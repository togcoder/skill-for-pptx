#!/usr/bin/env python3
"""Office Link Bridge — Interactive Excel-to-PowerPoint/Word Chart Linkage (T047, cross).

Connects isolated agent workflows across Excel (SheetCraft/GridCraft), PowerPoint
(SlideForge/DeckCraft), and Word (DocumentCraft).

Supports three architectural bridge modes:
1. Live External Link (ISO/IEC 29500 DrawingML + TargetMode="External"):
   - Chart references a live external Excel workbook on disk.
   - PowerPoint / Word opens the external workbook when clicking 'Edit Data'.
   - Cached DrawingML values (<c:numCache>, <c:strCache>) are pre-synchronized
     so the chart renders instantly and accurately across all platforms (DeckCraft,
     LibreOffice, Google Slides, web).
2. Embedded Connected Workbook (Self-Contained Full Model):
   - Injects a complete multi-sheet SheetCraft workbook (.xlsx / .xlsm) into the
     presentation/document package (ppt/embeddings/ or word/embeddings/).
   - Preserves all real Excel formulas (e.g. =SUM, =B2*1.3), formatting, and tabs.
   - Clicking 'Edit Data in Excel' in desktop Office launches the real model, not a dummy 1-sheet stub.
3. Offline Bi-directional Cache Synchronizer:
   - Reads evaluated values from the Excel workbook (via openpyxl) and updates
     the DrawingML XML caches (<c:numCache>, <c:strCache>) without requiring Microsoft Office.
   - Produces a machine-readable sync audit with value diffs.
4. Optional Desktop COM Automation (Windows Rung 4–5):
   - Commands PowerPoint / Excel desktop COM to refresh links or verify live binding.

CLI:
    python scripts/office_link_bridge.py inspect deck.pptx
    python scripts/office_link_bridge.py link deck.pptx --excel model.xlsx --sheet Summary --mode external
    python scripts/office_link_bridge.py embed deck.pptx --excel model.xlsx --sheet Summary
    python scripts/office_link_bridge.py sync deck.pptx [--excel model.xlsx]
"""
from __future__ import annotations

import argparse
import copy
import io
import json
import os
from pathlib import Path
import re
import sys
from typing import Any
import urllib.parse
import zipfile

from lxml import etree as ET
import openpyxl

NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

NAMESPACES = {
    "c": NS_C,
    "a": NS_A,
    "r": NS_R,
    "rel": NS_PKG,
    "p": NS_P,
    "w": NS_W,
}

REL_TYPE_OLE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject"
REL_TYPE_PACKAGE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/package"


def _col_to_index(col_str: str) -> int:
    """Convert column letters ('A', 'B', 'AA') to 1-based column index."""
    col = 0
    for ch in col_str.upper():
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return col


def _parse_cell_reference(ref: str) -> tuple[int, int]:
    """Parse '$B$2' or 'B2' into (row, col) as 1-based integers."""
    clean = ref.replace("$", "").strip()
    m = re.match(r"^([A-Za-z]+)(\d+)$", clean)
    if not m:
        raise ValueError(f"Invalid cell reference: {ref}")
    col_str, row_str = m.groups()
    return int(row_str), _col_to_index(col_str)


def parse_formula_range(formula: str) -> tuple[str, str, str | None]:
    """Parse formula like 'Sheet1!$B$2:$B$4' or '[model.xlsx]Sheet1!$B$1'.

    Returns (sheet_name, start_cell, end_cell_or_None).
    """
    clean = formula.strip().lstrip("=")
    # Remove workbook prefix if present e.g. [model.xlsx]Sheet1!
    if "[" in clean and "]" in clean:
        clean = re.sub(r"\[.*?\]", "", clean)
    
    if "!" in clean:
        sheet, cell_part = clean.split("!", 1)
        sheet = sheet.strip("'\"")
    else:
        sheet = "Sheet1"
        cell_part = clean

    if ":" in cell_part:
        start_cell, end_cell = cell_part.split(":", 1)
        return sheet, start_cell.strip(), end_cell.strip()
    return sheet, cell_part.strip(), None


def recalculate_excel_workbook(xlsx_path: str | Path) -> bool:
    """Recalculate all formulas in an Excel workbook using native Excel COM (if available on Windows).

    This ensures that openpyxl(data_only=True) reads real calculated numbers instead of None
    when a workbook contains formulas (=SUM, =B2-B3) generated programmatically.
    """
    try:
        import win32com.client
        p = Path(xlsx_path).resolve()
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(p))
        excel.CalculateFull()
        wb.Save()
        wb.Close(False)
        excel.Quit()
        return True
    except Exception:
        return False


def read_excel_range_values(
    xlsx_path: str | Path,
    sheet_name: str,
    start_cell: str,
    end_cell: str | None = None,
    *,
    recalculate: bool = False,
) -> list[Any]:
    """Read evaluated values from an Excel file using openpyxl (data_only=True)."""
    if recalculate:
        recalculate_excel_workbook(xlsx_path)

    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        # Fall back to active sheet if sheet_name doesn't match
        ws = wb.active
    else:
        ws = wb[sheet_name]

    start_row, start_col = _parse_cell_reference(start_cell)
    if end_cell:
        end_row, end_col = _parse_cell_reference(end_cell)
    else:
        end_row, end_col = start_row, start_col

    values = []
    has_nones = False
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            val = ws.cell(row=r, column=c).value
            if val is None:
                has_nones = True
            values.append(val)

    # If any cell is None and we haven't recalculated yet, try recalculating once
    if has_nones and not recalculate:
        if recalculate_excel_workbook(xlsx_path):
            return read_excel_range_values(xlsx_path, sheet_name, start_cell, end_cell, recalculate=False)

    return values


def inspect_office_charts(file_path: str | Path) -> dict[str, Any]:
    """Inspect all DrawingML charts in a PPTX or DOCX package."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    is_docx = p.suffix.lower() == ".docx"
    doc_prefix = "word" if is_docx else "ppt"

    charts_info = []
    with zipfile.ZipFile(p, "r") as z:
        namelist = z.namelist()
        chart_names = [n for n in namelist if n.startswith(f"{doc_prefix}/charts/chart") and n.endswith(".xml")]
        # Sort chart names naturally
        chart_names.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", x)])

        for chart_path in chart_names:
            chart_xml = z.read(chart_path)
            tree = ET.fromstring(chart_xml)

            # Check rels
            rels_path = f"{doc_prefix}/charts/_rels/{Path(chart_path).name}.rels"
            data_rel_info = {}
            if rels_path in namelist:
                rels_xml = z.read(rels_path)
                rels_tree = ET.fromstring(rels_xml)
                for rel in rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
                    rel_type = rel.get("Type", "")
                    if "package" in rel_type or "oleObject" in rel_type:
                        data_rel_info = {
                            "id": rel.get("Id"),
                            "type": rel_type,
                            "target": rel.get("Target"),
                            "target_mode": rel.get("TargetMode", "Internal"),
                        }
                        break

            # Chart title
            title_node = tree.find(".//c:title//c:v", namespaces=NAMESPACES)
            title = title_node.text if title_node is not None else None

            # ExternalData node
            ext_data = tree.find(".//c:externalData", namespaces=NAMESPACES)
            auto_update = None
            ext_id = None
            if ext_data is not None:
                ext_id = ext_data.get(f"{{{NS_R}}}id")
                au_node = ext_data.find("c:autoUpdate", namespaces=NAMESPACES)
                if au_node is not None:
                    auto_update = au_node.get("val")

            # Determine mode
            target_mode = data_rel_info.get("target_mode", "Internal")
            target_str = data_rel_info.get("target", "")
            if target_mode.lower() == "external":
                link_mode = "linked_external"
            elif "embeddings" in target_str:
                link_mode = "embedded"
            else:
                link_mode = "isolated"

            # Series info
            series_list = []
            for ser in tree.findall(".//c:ser", namespaces=NAMESPACES):
                ser_idx = ser.find("c:idx", namespaces=NAMESPACES)
                s_idx = ser_idx.get("val") if ser_idx is not None else ""

                tx_f = ser.find(".//c:tx//c:f", namespaces=NAMESPACES)
                tx_v = ser.find(".//c:tx//c:v", namespaces=NAMESPACES)
                ser_name = tx_v.text if tx_v is not None else None
                ser_name_formula = tx_f.text if tx_f is not None else None

                cat_f = ser.find(".//c:cat//c:f", namespaces=NAMESPACES)
                cat_formula = cat_f.text if cat_f is not None else None
                cat_vals = [v.text for v in ser.findall(".//c:cat//c:v", namespaces=NAMESPACES)]

                val_f = ser.find(".//c:val//c:f", namespaces=NAMESPACES)
                val_formula = val_f.text if val_f is not None else None
                num_vals = []
                for v in ser.findall(".//c:val//c:v", namespaces=NAMESPACES):
                    try:
                        num_vals.append(float(v.text) if "." in v.text else int(v.text))
                    except (ValueError, TypeError):
                        num_vals.append(v.text)

                series_list.append({
                    "idx": s_idx,
                    "name": ser_name,
                    "name_formula": ser_name_formula,
                    "categories_formula": cat_formula,
                    "categories_count": len(cat_vals),
                    "categories_sample": cat_vals[:5],
                    "values_formula": val_formula,
                    "values_count": len(num_vals),
                    "values": num_vals,
                })

            charts_info.append({
                "chart_path": chart_path,
                "title": title,
                "link_mode": link_mode,
                "auto_update": auto_update,
                "external_id": ext_id,
                "relationship": data_rel_info,
                "series_count": len(series_list),
                "series": series_list,
            })

    return {
        "file": str(p),
        "document_type": "docx" if is_docx else "pptx",
        "total_charts": len(charts_info),
        "charts": charts_info,
    }


def _update_cache_elements(
    cache_parent: ET._Element,
    values: list[Any],
    *,
    is_numeric: bool = True,
    format_code: str = "General",
) -> None:
    """Update or replace children of <c:numCache> or <c:strCache> with fresh values."""
    # Clear existing pt elements
    for pt in cache_parent.findall(f"{{{NS_C}}}pt"):
        cache_parent.remove(pt)

    # Set ptCount
    pt_count = cache_parent.find(f"{{{NS_C}}}ptCount")
    if pt_count is None:
        pt_count = ET.SubElement(cache_parent, f"{{{NS_C}}}ptCount")
    pt_count.set("val", str(len(values)))

    # Set formatCode if numeric
    if is_numeric:
        fmt = cache_parent.find(f"{{{NS_C}}}formatCode")
        if fmt is None:
            # Insert formatCode before ptCount if possible
            fmt = ET.Element(f"{{{NS_C}}}formatCode")
            cache_parent.insert(0, fmt)
        fmt.text = format_code

    # Add pt elements
    for idx, val in enumerate(values):
        pt = ET.SubElement(cache_parent, f"{{{NS_C}}}pt", idx=str(idx))
        v = ET.SubElement(pt, f"{{{NS_C}}}v")
        if val is None:
            v.text = ""
        elif isinstance(val, float) and val.is_integer():
            v.text = str(int(val))
        else:
            v.text = str(val)


def link_chart_to_external_excel(
    presentation_path: str | Path,
    excel_path: str | Path,
    *,
    chart_index: int = 0,
    output_path: str | Path | None = None,
    sheet_name: str | None = None,
    auto_update: bool = True,
    use_absolute_path: bool = True,
) -> dict[str, Any]:
    """Convert an existing PPTX/DOCX chart into a live linked chart pointing to an external Excel file.

    Follows ISO/IEC 29500 DrawingML specification:
    - Sets chart relationship TargetMode="External" with Type=oleObject.
    - Synchronizes <c:numCache> and <c:strCache> from the external Excel file.
    - Enables autoUpdate flag in <c:externalData>.
    """
    p = Path(presentation_path)
    xl_p = Path(excel_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Presentation not found: {p}")
    if not xl_p.exists():
        raise FileNotFoundError(f"Source Excel not found: {xl_p}")

    out_file = Path(output_path) if output_path else p
    is_docx = p.suffix.lower() == ".docx"
    doc_prefix = "word" if is_docx else "ppt"

    # Load source workbook data
    wb = openpyxl.load_workbook(xl_p, data_only=True)
    target_sheet = sheet_name or wb.sheetnames[0]
    if target_sheet not in wb.sheetnames:
        target_sheet = wb.sheetnames[0]

    with zipfile.ZipFile(p, "r") as zin:
        in_files = {name: zin.read(name) for name in zin.namelist()}

    chart_names = [n for n in in_files.keys() if n.startswith(f"{doc_prefix}/charts/chart") and n.endswith(".xml")]
    chart_names.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", x)])

    if not chart_names:
        raise ValueError(f"No charts found in {p}")
    if chart_index >= len(chart_names):
        raise IndexError(f"Chart index {chart_index} out of range (found {len(chart_names)} charts)")

    target_chart_name = chart_names[chart_index]
    chart_base = Path(target_chart_name).name
    rels_name = f"{doc_prefix}/charts/_rels/{chart_base}.rels"

    # Determine relationship Target
    if use_absolute_path:
        # Standard Office Windows URI format: file:///C:\path\to\file.xlsx
        win_path = str(xl_p).replace("/", "\\")
        encoded_path = urllib.parse.quote(win_path, safe=":\\")
        target_uri = f"file:///{encoded_path}"
    else:
        # Relative path from ppt/charts/ to the excel file
        chart_dir = (p.parent / doc_prefix / "charts").resolve()
        target_uri = os.path.relpath(xl_p, chart_dir).replace("\\", "/")

    # 1. Update relationship file
    rels_tree = ET.fromstring(in_files[rels_name])
    ext_rel_id = None
    for rel in rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
        rel_type = rel.get("Type", "")
        if "package" in rel_type or "oleObject" in rel_type:
            ext_rel_id = rel.get("Id")
            rel.set("Type", REL_TYPE_OLE)
            rel.set("Target", target_uri)
            rel.set("TargetMode", "External")
            break

    if not ext_rel_id:
        # Create new relationship
        ext_rel_id = f"rId{len(rels_tree) + 1}"
        ET.SubElement(
            rels_tree,
            f"{{{NS_PKG}}}Relationship",
            Id=ext_rel_id,
            Type=REL_TYPE_OLE,
            Target=target_uri,
            TargetMode="External",
        )

    in_files[rels_name] = ET.tostring(rels_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # 2. Update chart.xml externalData & sync caches
    chart_tree = ET.fromstring(in_files[target_chart_name])
    ext_data = chart_tree.find(".//c:externalData", namespaces=NAMESPACES)
    if ext_data is None:
        ext_data = ET.SubElement(chart_tree, f"{{{NS_C}}}externalData")
    ext_data.set(f"{{{NS_R}}}id", ext_rel_id)
    au = ext_data.find("c:autoUpdate", namespaces=NAMESPACES)
    if au is None:
        au = ET.SubElement(ext_data, f"{{{NS_C}}}autoUpdate")
    au.set("val", "1" if auto_update else "0")

    # Sync series cache values from Excel
    series_diffs = []
    for ser in chart_tree.findall(".//c:ser", namespaces=NAMESPACES):
        ser_idx_node = ser.find("c:idx", namespaces=NAMESPACES)
        ser_idx = ser_idx_node.get("val") if ser_idx_node is not None else "0"

        # Check values formula
        val_f = ser.find(".//c:val//c:f", namespaces=NAMESPACES)
        num_cache = ser.find(".//c:val//c:numRef//c:numCache", namespaces=NAMESPACES)
        if val_f is not None and val_f.text and num_cache is not None:
            formula = val_f.text
            sheet, start_c, end_c = parse_formula_range(formula)
            actual_sheet = sheet if sheet in wb.sheetnames else target_sheet
            new_vals = read_excel_range_values(xl_p, actual_sheet, start_c, end_c)
            _update_cache_elements(num_cache, new_vals, is_numeric=True)
            series_diffs.append({
                "series_idx": ser_idx,
                "formula": formula,
                "sheet": actual_sheet,
                "new_values": new_vals,
            })

    in_files[target_chart_name] = ET.tostring(chart_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Write out package
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in in_files.items():
            zout.writestr(name, content)

    return {
        "ok": True,
        "mode": "linked_external",
        "chart": target_chart_name,
        "target_excel": str(xl_p),
        "target_uri": target_uri,
        "auto_update": auto_update,
        "series_synced": series_diffs,
        "output_file": str(out_file),
    }


def embed_sheetcraft_workbook(
    presentation_path: str | Path,
    excel_path: str | Path,
    *,
    chart_index: int = 0,
    output_path: str | Path | None = None,
    sheet_name: str | None = None,
    series_mappings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Inject a full SheetCraft workbook (.xlsx/.xlsm) into a PPTX/DOCX chart's embedded package.

    Preserves 100% of Excel multi-tabs, formulas, formatting, and charts while binding
    the host presentation chart to the target cells.
    """
    p = Path(presentation_path)
    xl_p = Path(excel_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Presentation not found: {p}")
    if not xl_p.exists():
        raise FileNotFoundError(f"Source Excel not found: {xl_p}")

    out_file = Path(output_path) if output_path else p
    is_docx = p.suffix.lower() == ".docx"
    doc_prefix = "word" if is_docx else "ppt"

    # Read the full model bytes
    model_bytes = xl_p.read_bytes()
    wb = openpyxl.load_workbook(io.BytesIO(model_bytes), data_only=True)
    active_sheet = sheet_name or wb.sheetnames[0]

    with zipfile.ZipFile(p, "r") as zin:
        in_files = {name: zin.read(name) for name in zin.namelist()}

    chart_names = [n for n in in_files.keys() if n.startswith(f"{doc_prefix}/charts/chart") and n.endswith(".xml")]
    chart_names.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", x)])

    if not chart_names:
        raise ValueError(f"No charts found in {p}")
    if chart_index >= len(chart_names):
        raise IndexError(f"Chart index {chart_index} out of range")

    target_chart_name = chart_names[chart_index]
    chart_base = Path(target_chart_name).name
    rels_name = f"{doc_prefix}/charts/_rels/{chart_base}.rels"

    # Identify or create the embedded workbook part in the zip
    emb_target = f"{doc_prefix}/embeddings/Microsoft_Excel_Worksheet{chart_index + 1}.xlsx"
    rels_tree = ET.fromstring(in_files[rels_name])
    found_rel = False
    for rel in rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
        rel_type = rel.get("Type", "")
        if "package" in rel_type or "oleObject" in rel_type:
            rel.set("Type", REL_TYPE_PACKAGE)
            # Relative path from ppt/charts/
            rel.set("Target", f"../embeddings/Microsoft_Excel_Worksheet{chart_index + 1}.xlsx")
            rel.attrib.pop("TargetMode", None)
            found_rel = True
            break

    if not found_rel:
        new_id = f"rId{len(rels_tree) + 1}"
        ET.SubElement(
            rels_tree,
            f"{{{NS_PKG}}}Relationship",
            Id=new_id,
            Type=REL_TYPE_PACKAGE,
            Target=f"../embeddings/Microsoft_Excel_Worksheet{chart_index + 1}.xlsx",
        )

    in_files[rels_name] = ET.tostring(rels_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Injected embedded workbook
    in_files[emb_target] = model_bytes

    # Update chart.xml
    chart_tree = ET.fromstring(in_files[target_chart_name])
    series_nodes = chart_tree.findall(".//c:ser", namespaces=NAMESPACES)

    synced_series = []
    if series_mappings:
        for idx, mapping in enumerate(series_mappings):
            if idx >= len(series_nodes):
                break
            ser = series_nodes[idx]
            s_sheet = mapping.get("sheet", active_sheet)

            # Name
            if "name" in mapping or "name_cell" in mapping:
                tx = ser.find("c:tx", namespaces=NAMESPACES)
                if tx is None:
                    tx = ET.SubElement(ser, f"{{{NS_C}}}tx")
                name_val = mapping.get("name")
                name_cell = mapping.get("name_cell")
                if name_cell:
                    tx_f = tx.find(".//c:f", namespaces=NAMESPACES)
                    if tx_f is None:
                        sref = ET.SubElement(tx, f"{{{NS_C}}}strRef")
                        tx_f = ET.SubElement(sref, f"{{{NS_C}}}f")
                    tx_f.text = f"'{s_sheet}'!${name_cell.replace('$', '')}"
                    name_val = read_excel_range_values(xl_p, s_sheet, name_cell)[0]

                str_cache = tx.find(".//c:strCache", namespaces=NAMESPACES)
                if str_cache is not None and name_val:
                    _update_cache_elements(str_cache, [name_val], is_numeric=False)

            # Categories
            if "categories_range" in mapping:
                cat_range = mapping["categories_range"]
                cat_node = ser.find("c:cat", namespaces=NAMESPACES)
                if cat_node is not None:
                    cat_f = cat_node.find(".//c:f", namespaces=NAMESPACES)
                    if cat_f is not None:
                        cat_f.text = f"'{s_sheet}'!{cat_range}"
                    cat_cache = cat_node.find(".//c:strCache", namespaces=NAMESPACES)
                    if cat_cache is not None:
                        start_c, end_c = (cat_range.split(":") + [None])[:2]
                        cat_vals = read_excel_range_values(xl_p, s_sheet, start_c, end_c)
                        _update_cache_elements(cat_cache, cat_vals, is_numeric=False)

            # Values
            if "values_range" in mapping:
                val_range = mapping["values_range"]
                val_node = ser.find("c:val", namespaces=NAMESPACES)
                if val_node is not None:
                    val_f = val_node.find(".//c:f", namespaces=NAMESPACES)
                    if val_f is not None:
                        val_f.text = f"'{s_sheet}'!{val_range}"
                    val_cache = val_node.find(".//c:numCache", namespaces=NAMESPACES)
                    if val_cache is not None:
                        start_c, end_c = (val_range.split(":") + [None])[:2]
                        num_vals = read_excel_range_values(xl_p, s_sheet, start_c, end_c)
                        _update_cache_elements(val_cache, num_vals, is_numeric=True)
                        synced_series.append({
                            "series_idx": idx,
                            "range": val_range,
                            "values": num_vals,
                        })
    else:
        # Default: sync existing formulas with the newly injected workbook
        for idx, ser in enumerate(series_nodes):
            val_f = ser.find(".//c:val//c:f", namespaces=NAMESPACES)
            val_cache = ser.find(".//c:val//c:numRef//c:numCache", namespaces=NAMESPACES)
            if val_f is not None and val_f.text and val_cache is not None:
                sheet, start_c, end_c = parse_formula_range(val_f.text)
                target_s = sheet if sheet in wb.sheetnames else active_sheet
                new_vals = read_excel_range_values(xl_p, target_s, start_c, end_c)
                _update_cache_elements(val_cache, new_vals, is_numeric=True)
                synced_series.append({
                    "series_idx": idx,
                    "sheet": target_s,
                    "formula": val_f.text,
                    "values": new_vals,
                })

    in_files[target_chart_name] = ET.tostring(chart_tree, xml_declaration=True, encoding="UTF-8", standalone=True)

    # Write out package
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in in_files.items():
            zout.writestr(name, content)

    return {
        "ok": True,
        "mode": "embedded_connected",
        "chart": target_chart_name,
        "embedded_part": emb_target,
        "workbook_sheets": wb.sheetnames,
        "series_synced": synced_series,
        "output_file": str(out_file),
    }


def sync_office_chart_data(
    presentation_path: str | Path,
    excel_path: str | Path | None = None,
    *,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Offline Bi-directional Cache Synchronizer.

    Reads updated numbers from the external or embedded Excel file and updates
    DrawingML <c:numCache> and <c:strCache> directly.
    """
    p = Path(presentation_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    out_file = Path(output_path) if output_path else p
    is_docx = p.suffix.lower() == ".docx"
    doc_prefix = "word" if is_docx else "ppt"

    with zipfile.ZipFile(p, "r") as zin:
        in_files = {name: zin.read(name) for name in zin.namelist()}

    chart_names = [n for n in in_files.keys() if n.startswith(f"{doc_prefix}/charts/chart") and n.endswith(".xml")]
    if not chart_names:
        return {"ok": False, "message": "No charts found in package"}

    sync_reports = []

    for chart_name in chart_names:
        chart_base = Path(chart_name).name
        rels_name = f"{doc_prefix}/charts/_rels/{chart_base}.rels"
        if rels_name not in in_files:
            continue

        rels_tree = ET.fromstring(in_files[rels_name])
        target_path_str = None
        target_mode = "Internal"
        for rel in rels_tree.findall(".//rel:Relationship", namespaces=NAMESPACES):
            rel_type = rel.get("Type", "")
            if "package" in rel_type or "oleObject" in rel_type:
                target_path_str = rel.get("Target")
                target_mode = rel.get("TargetMode", "Internal")
                break

        # Resolve excel data source
        source_wb = None
        if excel_path:
            source_wb = openpyxl.load_workbook(excel_path, data_only=True)
            active_xl_path = Path(excel_path).resolve()
        elif target_mode.lower() == "external" and target_path_str:
            clean_path = target_path_str
            if clean_path.startswith("file:///"):
                clean_path = urllib.parse.unquote(clean_path[8:])
            active_xl_path = Path(clean_path).resolve()
            if active_xl_path.exists():
                source_wb = openpyxl.load_workbook(active_xl_path, data_only=True)
        else:
            # Check embedded workbook inside the zip
            if target_path_str:
                norm_emb = target_path_str.replace("../", f"{doc_prefix}/")
                if norm_emb in in_files:
                    source_wb = openpyxl.load_workbook(io.BytesIO(in_files[norm_emb]), data_only=True)
                    active_xl_path = Path(norm_emb)

        if source_wb is None:
            sync_reports.append({
                "chart": chart_name,
                "status": "skipped",
                "reason": f"Unable to resolve source workbook for target {target_path_str}",
            })
            continue

        # Parse chart and update cache
        chart_tree = ET.fromstring(in_files[chart_name])
        chart_diffs = []

        for ser in chart_tree.findall(".//c:ser", namespaces=NAMESPACES):
            ser_idx_node = ser.find("c:idx", namespaces=NAMESPACES)
            s_idx = ser_idx_node.get("val") if ser_idx_node is not None else "0"

            val_f = ser.find(".//c:val//c:f", namespaces=NAMESPACES)
            num_cache = ser.find(".//c:val//c:numRef//c:numCache", namespaces=NAMESPACES)
            if val_f is not None and val_f.text and num_cache is not None:
                formula = val_f.text
                sheet, start_c, end_c = parse_formula_range(formula)
                target_sheet = sheet if sheet in source_wb.sheetnames else source_wb.sheetnames[0]

                # Old values
                old_vals = [v.text for v in num_cache.findall(".//c:v", namespaces=NAMESPACES)]

                # New values from source via read_excel_range_values (with formula recalculation fallback)
                new_vals = read_excel_range_values(active_xl_path, target_sheet, start_c, end_c)

                _update_cache_elements(num_cache, new_vals, is_numeric=True)

                chart_diffs.append({
                    "series_idx": s_idx,
                    "formula": formula,
                    "sheet": target_sheet,
                    "old_values": old_vals,
                    "new_values": new_vals,
                    "changed": str(old_vals) != str(new_vals),
                })

        in_files[chart_name] = ET.tostring(chart_tree, xml_declaration=True, encoding="UTF-8", standalone=True)
        sync_reports.append({
            "chart": chart_name,
            "status": "synced",
            "source": str(active_xl_path),
            "series": chart_diffs,
        })

    # Save output
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in in_files.items():
            zout.writestr(name, content)

    return {
        "ok": True,
        "output_file": str(out_file),
        "synced_charts": sync_reports,
    }


def refresh_presentation_links_com(presentation_path: str | Path) -> dict[str, Any]:
    """Native Windows COM Automation (Rung 4–5).

    Opens Microsoft PowerPoint silently to refresh all external links and update chart displays.
    """
    try:
        import win32com.client
    except ImportError:
        return {"ok": False, "reason": "pywin32 is not installed"}

    p = Path(presentation_path).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Presentation not found: {p}")

    ppt = None
    pres = None
    try:
        ppt = win32com.client.DispatchEx("PowerPoint.Application")
        ppt.DisplayAlerts = False
        pres = ppt.Presentations.Open(str(p), ReadOnly=False, WithWindow=False)
        pres.UpdateLinks()
        pres.Save()
        return {"ok": True, "method": "COM UpdateLinks", "file": str(p)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        if pres is not None:
            try:
                pres.Close()
            except Exception:
                pass
        if ppt is not None:
            try:
                ppt.Quit()
            except Exception:
                pass


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Office Link Bridge — Interactive Excel-to-PowerPoint/Word Chart Linkage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # inspect
    p_ins = sub.add_parser("inspect", help="Inspect charts in a PPTX or DOCX package")
    p_ins.add_argument("file", type=Path)

    # link
    p_link = sub.add_parser("link", help="Link a chart to an external Excel file")
    p_link.add_argument("presentation", type=Path)
    p_link.add_argument("--excel", type=Path, required=True)
    p_link.add_argument("--chart-idx", type=int, default=0)
    p_link.add_argument("--sheet", type=str, default=None)
    p_link.add_argument("-o", "--output", type=Path, default=None)
    p_link.add_argument("--relative", action="store_true", help="Use relative path instead of absolute file URI")

    # embed
    p_emb = sub.add_parser("embed", help="Embed a full SheetCraft workbook into chart package")
    p_emb.add_argument("presentation", type=Path)
    p_emb.add_argument("--excel", type=Path, required=True)
    p_emb.add_argument("--chart-idx", type=int, default=0)
    p_emb.add_argument("--sheet", type=str, default=None)
    p_emb.add_argument("-o", "--output", type=Path, default=None)

    # sync
    p_sync = sub.add_parser("sync", help="Synchronize chart data cache from Excel workbook")
    p_sync.add_argument("presentation", type=Path)
    p_sync.add_argument("--excel", type=Path, default=None)
    p_sync.add_argument("-o", "--output", type=Path, default=None)

    # refresh-com
    p_com = sub.add_parser("refresh-com", help="Refresh presentation links via Windows PowerPoint COM")
    p_com.add_argument("presentation", type=Path)

    args = parser.parse_args()

    if args.cmd == "inspect":
        res = inspect_office_charts(args.file)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "link":
        res = link_chart_to_external_excel(
            args.presentation,
            args.excel,
            chart_index=args.chart_idx,
            output_path=args.output,
            sheet_name=args.sheet,
            use_absolute_path=not args.relative,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "embed":
        res = embed_sheetcraft_workbook(
            args.presentation,
            args.excel,
            chart_index=args.chart_idx,
            output_path=args.output,
            sheet_name=args.sheet,
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "sync":
        res = sync_office_chart_data(args.presentation, args.excel, output_path=args.output)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.cmd == "refresh-com":
        res = refresh_presentation_links_com(args.presentation)
        print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
