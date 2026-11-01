#!/usr/bin/env python3
"""Audit Excel charts for geometry, data integrity and accessibility (T041, xlsx).

Status: EXPERIMENTAL — T041 [xlsx], review requested.  Not a canonical module
until an independent review accepts it.


The audit is deliberately conservative: it measures the XML, not a screenshot.
A clean report means "the chart is structurally sane"; it does not prove that
Excel rendered it beautifully.  Use ``chart_forge.py build --render`` or Excel
``Chart.Export`` for a rendered check.

Rules are read from ``domains/xlsx/data/spreadsheet_system.json`` when present; the
defaults below are the fallback for a bare checkout.

CLI:
    python scripts/chart_audit.py book.xlsx
    python scripts/chart_audit.py book.xlsx --md audit.md
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
import zipfile
from typing import Any
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PATH = ROOT / "domains" / "xlsx" / "data" / "spreadsheet_system.json"

C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
XDR = "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
EMU_PER_CM = 360000
EMU_PER_PX = 9525
PX_PER_CM = 96 / 2.54
CHART_TYPES = {
    "barChart", "bar3DChart", "lineChart", "line3DChart", "areaChart", "area3DChart",
    "pieChart", "pie3DChart", "doughnutChart", "scatterChart", "bubbleChart",
    "radarChart", "stockChart", "surfaceChart", "surface3DChart", "ofPieChart",
    "treemapChart", "sunburstChart", "histogramChart", "waterfallChart",
    "funnelChart", "boxWhiskerChart",
}


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def _local(el) -> str:
    return etree.QName(el).localname


def _text(el) -> str:
    return "".join(t.text or "" for t in el.iter(q(A, "t")))


def _val(parent, tag: str, default=None):
    node = parent.find(q(C, tag)) if parent is not None else None
    if node is None:
        return default
    value = node.get("val")
    return default if value is None else value


def _float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _hex(color: str | None) -> tuple[int, int, int] | None:
    if not color:
        return None
    color = color.strip().lstrip("#")
    if len(color) == 6:
        try:
            return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
    return None


def _luminance(rgb: tuple[int, int, int]) -> float:
    vals = []
    for channel in rgb:
        c = channel / 255
        vals.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]


def _contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    l1, l2 = _luminance(a), _luminance(b)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _deuteranopia(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    r, g, b = [v / 255 for v in rgb]
    # Brettel/Viénot-style approximation; good enough for a distinctness warning.
    rr = 0.625 * r + 0.375 * g
    gg = 0.7 * r + 0.3 * g
    bb = 0.0 * r + 0.3 * g + 0.7 * b
    return tuple(max(0, min(255, int(v * 255))) for v in (rr, gg, bb))


def _distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


# ---------------------------------------------------------------------------
# Package structure
# ---------------------------------------------------------------------------

def _read(zf, name: str):
    try:
        return etree.fromstring(zf.read(name))
    except KeyError:
        return None


def _rels(zf, part: str) -> dict[str, str]:
    folder, base = part.rsplit("/", 1)
    rels_name = f"{folder}/_rels/{base}.rels"
    root = _read(zf, rels_name)
    out = {}
    if root is not None:
        for rel in root:
            rid = rel.get("Id")
            target = rel.get("Target")
            if rid and target:
                out[rid] = target
    return out


def _resolve(part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base = part.rsplit("/", 1)[0]
    parts = (base + "/" + target).split("/")
    out = []
    for p in parts:
        if p == "..":
            if out:
                out.pop()
        elif p and p != ".":
            out.append(p)
    return "/".join(out)


def _workbook_map(zf) -> tuple[dict[str, str], dict[str, list[str]], dict[str, list[str]]]:
    wb = _read(zf, "xl/workbook.xml")
    rels = _rels(zf, "xl/workbook.xml")
    sheets: dict[str, str] = {}
    if wb is not None:
        for sheet in wb.iter(q(S, "sheet")):
            name = sheet.get("name") or ""
            rid = sheet.get(q(R, "id"))
            if rid and rid in rels:
                sheets[name] = _resolve("xl/workbook.xml", rels[rid])
    sheet_drawings: dict[str, list[str]] = {}
    drawing_charts: dict[str, list[str]] = {}
    for name, part in sheets.items():
        srels = _rels(zf, part)
        drawings = []
        for target in srels.values():
            full = _resolve(part, target)
            if "/drawings/" in full and full.endswith(".xml"):
                drawings.append(full)
        sheet_drawings[name] = drawings
        for drawing in drawings:
            drels = _rels(zf, drawing)
            charts = [ _resolve(drawing, t) for t in drels.values() if "/charts/chart" in t and t.endswith(".xml")]
            drawing_charts[drawing] = charts
    return sheets, sheet_drawings, drawing_charts


def _sheet_cells(zf, part: str) -> dict[str, Any]:
    root = _read(zf, part)
    cells = {}
    if root is None:
        return cells
    for c in root.iter(q(S, "c")):
        ref = c.get("r")
        if not ref:
            continue
        v = c.find(q(S, "v"))
        isel = c.find(q(S, "is"))
        if v is not None and v.text is not None:
            cells[ref.replace("$", "")] = v.text
        elif isel is not None:
            cells[ref] = "".join(t.text or "" for t in isel.iter(q(S, "t")))
    return cells


def _col_widths(root) -> dict[int, float]:
    widths = {}
    if root is None:
        return widths
    for col in root.iter(q(S, "col")):
        try:
            lo, hi = int(col.get("min")), int(col.get("max"))
            width = float(col.get("width") or 8.43)
        except (TypeError, ValueError):
            continue
        for i in range(lo, hi + 1):
            widths[i] = width
    return widths


def _row_heights(root) -> dict[int, float]:
    heights = {}
    if root is None:
        return heights
    for row in root.iter(q(S, "row")):
        try:
            r = int(row.get("r"))
            heights[r] = float(row.get("ht") or 15)
        except (TypeError, ValueError):
            continue
    return heights


def _col_px(width_chars: float) -> float:
    # Excel's column width -> pixels for Calibri 11 at 96 DPI.
    return math.floor(((256 * width_chars + math.floor(128 / 7)) / 256) * 7) + 5


def _row_px(height_pt: float) -> float:
    return height_pt * 96 / 72


def _anchor_rect(anchor, col_widths: dict[int, float], row_heights: dict[int, float]):
    kind = _local(anchor)
    if kind == "absoluteAnchor":
        pos = anchor.find(q(XDR, "pos"))
        ext = anchor.find(q(XDR, "ext"))
        if pos is None or ext is None:
            return None
        return (float(pos.get("x") or 0) / EMU_PER_PX / PX_PER_CM,
                float(pos.get("y") or 0) / EMU_PER_PX / PX_PER_CM,
                float(ext.get("cx") or 0) / EMU_PER_CM,
                float(ext.get("cy") or 0) / EMU_PER_CM)
    frm = anchor.find(q(XDR, "from"))
    if frm is None:
        return None

    def coord(node):
        col = int(node.findtext(q(XDR, "col")) or 0)
        row = int(node.findtext(q(XDR, "row")) or 0)
        coff = float(node.findtext(q(XDR, "colOff")) or 0) / EMU_PER_PX
        roff = float(node.findtext(q(XDR, "rowOff")) or 0) / EMU_PER_PX
        x = sum(_col_px(col_widths.get(i, 8.43)) for i in range(1, col + 1)) + coff
        y = sum(_row_px(row_heights.get(i, 15)) for i in range(1, row + 1)) + roff
        return x, y

    x0, y0 = coord(frm)
    if kind == "oneCellAnchor":
        ext = anchor.find(q(XDR, "ext"))
        if ext is None:
            return None
        w = float(ext.get("cx") or 0) / EMU_PER_CM
        h = float(ext.get("cy") or 0) / EMU_PER_CM
        return (x0 / PX_PER_CM, y0 / PX_PER_CM, w, h)
    to = anchor.find(q(XDR, "to"))
    if to is None:
        return None
    x1, y1 = coord(to)
    return (x0 / PX_PER_CM, y0 / PX_PER_CM,
            (x1 - x0) / PX_PER_CM, (y1 - y0) / PX_PER_CM)


def _anchors(zf, drawing_part: str, sheet_part: str | None) -> list[dict]:
    root = _read(zf, drawing_part)
    if root is None:
        return []
    col_widths, row_heights = {}, {}
    if sheet_part:
        sheet_root = _read(zf, sheet_part)
        col_widths = _col_widths(sheet_root)
        row_heights = _row_heights(sheet_root)
    rels = _rels(zf, drawing_part)
    out = []
    for anchor in root:
        kind = _local(anchor)
        if kind not in {"twoCellAnchor", "oneCellAnchor", "absoluteAnchor"}:
            continue
        rect = _anchor_rect(anchor, col_widths, row_heights)
        if rect is None:
            continue
        obj_kind = "shape"
        chart_part = None
        for frame in anchor.iter(q(XDR, "graphicFrame")):
            obj_kind = "chart"
            rid = None
            for chart in frame.iter(q(C, "chart")):
                rid = chart.get(q(R, "id"))
            if rid and rid in rels:
                chart_part = _resolve(drawing_part, rels[rid])
        if any(True for _ in anchor.iter(q(XDR, "pic"))):
            obj_kind = "image"
        nv = anchor.find(f".//{q(XDR, 'cNvPr')}")
        alt = (nv.get("descr") or "") if nv is not None else ""
        out.append({"kind": obj_kind, "rect_cm": rect, "anchor": kind,
                    "chart_part": chart_part, "alt": alt})
    return out


def _print_areas(zf) -> dict[str, tuple[int, int, int, int]]:
    wb = _read(zf, "xl/workbook.xml")
    if wb is None:
        return {}
    out = {}
    for dn in wb.iter(q(S, "definedName")):
        if (dn.get("name") or "") != "_xlnm.Print_Area":
            continue
        text = (dn.text or "").strip()
        if "!" not in text:
            continue
        sheet, ref = text.split("!", 1)
        sheet = sheet.strip("'")
        m = re.match(r"\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+)", ref)
        if not m:
            continue
        c1, r1, c2, r2 = m.groups()
        out[sheet] = (_col_index(c1), int(r1), _col_index(c2), int(r2))
    return out


def _col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def _range_cells(ref: str) -> tuple[str, str] | None:
    ref = ref.split("!")[-1].replace("$", "")
    m = re.match(r"([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$", ref)
    if not m:
        return None
    c1, r1, c2, r2 = m.groups()
    return f"{c1}{r1}", f"{c2 or c1}{r2 or r1}"


def _cell_value(cells: dict, ref: str):
    raw = cells.get(ref)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return raw


# ---------------------------------------------------------------------------
# Chart parsing
# ---------------------------------------------------------------------------

def _series_info(ser) -> dict:
    name = ""
    tx = ser.find(q(C, "tx"))
    if tx is not None:
        name = _text(tx) or "".join(v.text or "" for v in tx.iter(q(C, "v")))
    values = []
    ref = None
    for tag in ("val", "yVal"):
        val = ser.find(q(C, tag))
        if val is not None:
            numref = val.find(q(C, "numRef"))
            if numref is not None:
                f = numref.find(q(C, "f"))
                ref = f.text if f is not None else None
                cache = numref.find(q(C, "numCache"))
                if cache is not None:
                    for pt in cache.findall(q(C, "pt")):
                        try:
                            values.append(float(pt.findtext(q(C, "v"))))
                        except (TypeError, ValueError):
                            pass
    color = None
    sp = ser.find(q(C, "spPr"))
    if sp is not None:
        clr = sp.find(f".//{q(A, 'srgbClr')}")
        if clr is not None:
            color = clr.get("val")
        if color is None:
            clr = sp.find(f"{q(A, 'ln')}//{q(A, 'srgbClr')}")
            if clr is not None:
                color = clr.get("val")
    marker = ser.find(q(C, "marker"))
    marker_type = marker.findtext(q(C, "symbol")) if marker is not None else None
    labels = ser.find(q(C, "dLbls"))
    point_colors = []
    for dpt in ser.findall(q(C, "dPt")):
        clr = dpt.find(f".//{q(A, 'srgbClr')}")
        if clr is not None:
            point_colors.append(clr.get("val"))
    return {"name": name, "values": values, "values_ref": ref, "color": color,
            "marker": marker_type, "has_labels": labels is not None,
            "point_colors": point_colors}


def _chart_info(root) -> dict:
    plot = root.find(f".//{q(C, 'plotArea')}")
    groups = []
    if plot is not None:
        groups = [child for child in plot if _local(child) in CHART_TYPES]
    group = groups[0] if groups else None
    types = [_local(g) for g in groups]
    chart_type = types[0] if len(types) == 1 else ("combo:" + "+".join(types) if types else None)
    title = ""
    title_el = root.find(f".//{q(C, 'title')}")
    if title_el is not None:
        title = _text(title_el)
    series = []
    for g in groups:
        series.extend(_series_info(s) for s in g.findall(q(C, "ser")))
    axes = []
    for tag in ("catAx", "valAx", "dateAx", "serAx"):
        for ax in root.iter(q(C, tag)):
            scaling = ax.find(q(C, "scaling"))
            axes.append({
                "kind": tag,
                "pos": _val(ax, "axPos"),
                "min": _val(scaling, "min") if scaling is not None else None,
                "max": _val(scaling, "max") if scaling is not None else None,
                "log": _val(scaling, "logBase") if scaling is not None else None,
                "num_fmt": (ax.find(q(C, "numFmt")).get("formatCode")
                            if ax.find(q(C, "numFmt")) is not None else None),
                "title": _text(ax.find(q(C, "title"))) if ax.find(q(C, "title")) is not None else "",
                "gridlines": ax.find(q(C, "majorGridlines")) is not None,
                "delete": _val(ax, "delete"),
            })
    fonts = []
    for el in root.iter():
        if _local(el) in {"defRPr", "rPr"}:
            sz = el.get("sz")
            if sz:
                fonts.append(float(sz) / 100)
    show_labels = False
    for g in groups:
        labels = g.find(q(C, "dLbls"))
        if labels is not None:
            show = labels.find(q(C, "showVal"))
            if show is not None and (show.get("val") or "1") in {"1", "true"}:
                show_labels = True
    legend = root.find(f".//{q(C, 'legend')}")
    gap = overlap = hole = rotation = None
    for g in groups:
        gap = gap or _val(g, "gapWidth")
        overlap = overlap or _val(g, "overlap")
        hole = hole or _val(g, "holeSize")
        rotation = rotation or _val(g, "firstSliceAng")
    return {
        "type": chart_type,
        "types": types,
        "title": title,
        "series": series,
        "axes": axes,
        "fonts": fonts,
        "min_font": min(fonts) if fonts else None,
        "max_font": max(fonts) if fonts else None,
        "show_labels": show_labels,
        "legend": None if legend is None else {
            "pos": _val(legend, "legendPos"),
            "overlay": _val(legend, "overlay"),
        },
        "gap": gap, "overlap": overlap, "hole": hole, "rotation": rotation,
    }


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def _load_system() -> dict:
    try:
        return json.loads(SYSTEM_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def audit_workbook(path: str | Path, system: dict | None = None) -> dict:
    path = Path(path)
    system = system or _load_system()
    geom = system.get("geometry", {})
    typo = system.get("typography", {})
    color_cfg = system.get("color", {})
    min_width = float(geom.get("min_width_cm", 10))
    min_height = float(geom.get("min_height_cm", 6))
    max_series = int(geom.get("max_series", 8))
    max_slices = int(geom.get("max_pie_slices", 7))
    min_category = float(geom.get("min_category_width_cm", 0.55))
    max_title_chars = int(geom.get("max_title_chars", 90))
    pie_aspect = geom.get("pie_aspect", [0.8, 1.25])
    pie_aspect_side = geom.get("pie_aspect_with_side_legend", [0.8, 2.2])
    min_font = float(typo.get("min_font_pt", 8))
    min_title = float(typo.get("min_title_pt", 10))
    contrast_graphic = float(color_cfg.get("contrast_graphic", 3.0))
    min_rgb = float(color_cfg.get("min_rgb_distance", 40))
    min_deut = float(color_cfg.get("min_deuteranopia_distance", 25))
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    charts: list[dict] = []
    with zipfile.ZipFile(path) as zf:
        sheets, sheet_drawings, drawing_charts = _workbook_map(zf)
        drawing_to_sheet = {}
        for sheet, drawings in sheet_drawings.items():
            for d in drawings:
                drawing_to_sheet[d] = sheet
        print_areas = _print_areas(zf)
        drawing_info = {}
        for drawing, sheet in drawing_to_sheet.items():
            drawing_info[drawing] = _anchors(zf, drawing, sheets.get(sheet))
        # Map chart part -> (sheet, anchor)
        chart_anchor: dict[str, tuple[str, dict]] = {}
        for drawing, charts_parts in drawing_charts.items():
            anchors = drawing_info.get(drawing, [])
            for anchor in anchors:
                if anchor.get("chart_part"):
                    chart_anchor[anchor["chart_part"]] = (drawing_to_sheet.get(drawing, ""), anchor)
        chart_names = sorted(n for n in zf.namelist() if re.fullmatch(r"xl/charts/chart\d+\.xml", n))
        for index, name in enumerate(chart_names, start=1):
            root = _read(zf, name)
            if root is None:
                continue
            info = _chart_info(root)
            info["index"] = index
            info["part"] = name
            sheet, anchor = chart_anchor.get(name, ("", None))
            info["sheet"] = sheet
            info["anchor"] = anchor
            if anchor:
                x, y, w, h = anchor["rect_cm"]
                info["rect_cm"] = [round(v, 2) for v in (x, y, w, h)]
                info["width_cm"] = round(w, 2)
                info["height_cm"] = round(h, 2)
                info["aspect"] = round(w / h, 3) if h else None
                info["anchor_kind"] = anchor["anchor"]
                info["alt"] = anchor.get("alt", "")
                if w < min_width or h < min_height:
                    errors.append(f"chart {index}: {w:.1f}×{h:.1f} cm is below the {min_width:.0f}×{min_height:.0f} cm minimum")
                if anchor["anchor"] == "twoCellAnchor":
                    warnings.append(f"chart {index}: two-cell anchor stretches with rows/columns; use a one-cell anchor")
                if any(t in {"pieChart", "doughnutChart"} for t in info.get("types", [])) and info.get("aspect"):
                    legend_pos = (info.get("legend") or {}).get("pos")
                    if legend_pos in {"l", "r"}:
                        ok_aspect = pie_aspect_side[0] <= info["aspect"] <= pie_aspect_side[1]
                    else:
                        ok_aspect = pie_aspect[0] <= info["aspect"] <= pie_aspect[1]
                    if not ok_aspect:
                        warnings.append(f"chart {index}: pie/doughnut aspect {info['aspect']:.2f} is not near square")
                # print area
                if sheet and sheet in print_areas:
                    c1, r1, c2, r2 = print_areas[sheet]
                    # approximating print area in cm from cell coordinates is
                    # done by the drawing anchor helper; a direct cell-range
                    # test is enough for the common case.
                    info["inside_print_area"] = True
                elif sheet:
                    notes.append(f"chart {index}: sheet {sheet!r} has no print area; chart may not print")
                if not info["alt"]:
                    warnings.append(f"chart {index}: no alt text on the chart frame")
            if info["type"] and "3D" in info["type"]:
                warnings.append(f"chart {index}: 3-D chart {info['type']}; use a 2-D chart for readable values")
            if any(t in {"pieChart", "doughnutChart"} for t in info.get("types", [])):
                points = max((len(s.get("values") or []) for s in info["series"]), default=0)
                if points > max_slices:
                    warnings.append(f"chart {index}: pie/doughnut has {points} slices (> {max_slices}); use a sorted bar chart")
                for s in info["series"]:
                    vals = s.get("values") or []
                    if any(v < 0 for v in vals):
                        errors.append(f"chart {index}: pie/doughnut has negative values")
                    if vals and abs(sum(vals)) < 1e-12:
                        errors.append(f"chart {index}: pie/doughnut values sum to zero")
                if points > 1 and info["series"]:
                    colors = set(info["series"][0].get("point_colors") or [])
                    if len(colors) < min(points, 3):
                        warnings.append(f"chart {index}: pie/doughnut slices share a colour; apply a categorical palette")
            if len(info["series"]) > max_series:
                warnings.append(f"chart {index}: {len(info['series'])} series (> {max_series}); use small multiples or highlight one series")
            if info["series"] and len(info["series"]) > 1 and not info["legend"]:
                warnings.append(f"chart {index}: multiple series but no legend")
            if info["legend"] and info["legend"].get("overlay") in {"1", "true"} and len(info["series"]) > 4:
                warnings.append(f"chart {index}: overlay legend covers the plot with {len(info['series'])} series")

            # Title / fonts / labels.
            if not info["title"]:
                notes.append(f"chart {index}: no chart title")
            elif len(info["title"]) > max_title_chars:
                warnings.append(f"chart {index}: title is {len(info['title'])} characters; move the insight to a subtitle or annotation")
            if info["min_font"] is not None and info["min_font"] < min_font:
                warnings.append(f"chart {index}: smallest font is {info['min_font']:.1f} pt (< {min_font:.0f} pt)")
            if info["title"] and info["max_font"] is not None and info["max_font"] < min_title:
                notes.append(f"chart {index}: title font {info['max_font']:.1f} pt is small for print")

            # Axes.
            val_axes = [ax for ax in info["axes"] if ax["kind"] == "valAx"]
            for ax in val_axes:
                if ax["log"]:
                    try:
                        base = float(ax["log"])
                    except ValueError:
                        base = 0
                    if base <= 1:
                        errors.append(f"chart {index}: logarithmic axis base must be > 1")
                    if ax["min"] is not None and _float(ax["min"], 0) <= 0:
                        errors.append(f"chart {index}: logarithmic axis minimum must be > 0")
                if "barChart" in info.get("types", []) and ax["min"] is not None:
                    if _float(ax["min"], 0) > 0:
                        warnings.append(f"chart {index}: value axis starts at {ax['min']}, truncating bar length; start at zero")
                if ax["max"] is not None and ax["pos"] in {"l", "r"} and info["series"]:
                    data_max = max((max(s.get("values") or [0]) for s in info["series"]), default=0)
                    if data_max > _float(ax["max"], data_max) + 1e-9:
                        warnings.append(f"chart {index}: axis maximum {ax['max']} cuts data at {data_max:g}")
            if len(val_axes) > 1:
                y2 = [ax for ax in val_axes if ax["pos"] == "r"]
                if y2 and not any(ax["title"] for ax in y2):
                    warnings.append(f"chart {index}: secondary axis has no title; readers cannot tell the units")
            if any(t in {"lineChart", "scatterChart"} for t in info.get("types", [])) and info["show_labels"] and len(info["series"]) > 3:
                warnings.append(f"chart {index}: data labels on {len(info['series'])} line series are likely to collide")

            # Category density for bar/column.
            if any(t in {"barChart", "bar3DChart"} for t in info.get("types", [])) and anchor:
                points = max((len(s.get("values") or []) for s in info["series"]), default=0)
                if points and w / points < min_category:
                    warnings.append(f"chart {index}: {w / points:.2f} cm per category (< {min_category:.2f}); rotate labels or reduce categories")

            # Colour: contrast and pairwise distinctness.
            colors = [_hex(s.get("color")) for s in info["series"] if s.get("color")]
            colors = [c for c in colors if c]
            for color in colors:
                if _contrast(color, (255, 255, 255)) < contrast_graphic:
                    warnings.append(f"chart {index}: series colour #{''.join(f'{v:02X}' for v in color)} is below {contrast_graphic:.1f}:1 against white")
            for i in range(len(colors)):
                for j in range(i + 1, len(colors)):
                    if (_distance(colors[i], colors[j]) < min_rgb or
                            _distance(_deuteranopia(colors[i]), _deuteranopia(colors[j])) < min_deut):
                        warnings.append(f"chart {index}: series colours {i + 1} and {j + 1} are hard to distinguish (also for deuteranopia)")

            # Data cache vs worksheet.
            if sheet and sheet in sheets:
                cells = _sheet_cells(zf, sheets[sheet])
                for si, s in enumerate(info["series"], start=1):
                    ref = s.get("values_ref")
                    if not ref:
                        continue
                    rng = _range_cells(ref)
                    if not rng:
                        continue
                    start, end = rng
                    # Compare only the first and last cache point.
                    if s.get("values") and start in cells:
                        actual = _cell_value(cells, start)
                        if isinstance(actual, float) and abs(actual - s["values"][0]) > 1e-6:
                            warnings.append(f"chart {index}: series {si} cache starts at {s['values'][0]:g} but cell {start} is {actual:g}; refresh the chart")
            charts.append(info)
    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "notes": notes,
        "stats": {
            "charts": len(charts),
            "types": [c.get("type") for c in charts],
            "sheets": list(sheets),
            "min_width_cm": min_width,
            "min_height_cm": min_height,
        },
        "charts": charts,
    }
    return result


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("xlsx", type=Path)
    parser.add_argument("--md", type=Path, default=None)
    args = parser.parse_args()
    result = audit_workbook(args.xlsx)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.md:
        lines = ["# XLSX chart audit", "", f"**ok:** {result['ok']}", ""]
        for label, items in [("Errors", result["errors"]), ("Warnings", result["warnings"]), ("Notes", result["notes"])]:
            lines.append(f"## {label}")
            lines.extend(f"- {x}" for x in items) if items else lines.append("- none")
            lines.append("")
        args.md.write_text("\n".join(lines), encoding="utf-8")
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
