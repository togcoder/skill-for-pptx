#!/usr/bin/env python3
"""Chart Forge — build a controlled Excel chart from a semantic spec (T041, xlsx).

Status: EXPERIMENTAL — T041 [xlsx], review requested.  Not a canonical module
until an independent review accepts it.


The chart is written with xlsxwriter for workbook/data/styles, then patched at
the OOXML level for properties xlsxwriter does not expose (legend overlay,
doughnut hole, pie rotation, one-cell anchors).  Every chart is audited by
``chart_audit.py`` before it is called done.

Why a spec instead of ad-hoc code:
  * axes, units, number formats, labels, markers and series colours are data;
  * the same spec can be replayed and diffed;
  * geometry is explicit (cm, cell, manual plot layout), so charts do not
    stretch when a column width changes;
  * unsupported properties fail with a named error instead of a broken chart.

CLI:
    python scripts/chart_forge.py build spec.json -o chart.xlsx
    python scripts/chart_forge.py build spec.json -o chart.xlsx --render preview/
    python scripts/chart_forge.py inspect chart.xlsx
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

try:
    import xlsxwriter
except ImportError as exc:  # pragma: no cover
    raise SystemExit("xlsxwriter is required: pip install XlsxWriter") from exc

try:
    from .chart_patch import patch_workbook
    from .chart_audit import audit_workbook
except ImportError:
    from chart_patch import patch_workbook
    from chart_audit import audit_workbook

PX_PER_CM = 37.7952755906
EMU_PER_CM = 360000


def _col_letter(index: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    out = ""
    n = index + 1
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def _col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch.upper()) - 64
    return n - 1


def _range(sheet: str, col: int, first_row: int, last_row: int) -> str:
    letter = _col_letter(col)
    return f"={sheet}!${letter}${first_row}:${letter}${last_row}"


def _num(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _chart_subtype(kind: str, subtype: str | None) -> str | None:
    if not subtype:
        return None
    table = {
        "column": {"clustered": None, "stacked": "stacked", "percent_stacked": "percent_stacked"},
        "bar": {"clustered": None, "stacked": "stacked", "percent_stacked": "percent_stacked"},
        "line": {"straight": "straight", "markers": "straight_with_markers",
                 "smooth": "smooth", "smooth_markers": "smooth_with_markers"},
        "area": {"standard": None, "stacked": "stacked", "percent_stacked": "percent_stacked"},
        "scatter": {"markers": "straight_with_markers", "smooth": "smooth",
                    "smooth_markers": "smooth_with_markers", "straight": "straight"},
        "radar": {"standard": None, "markers": "with_markers", "filled": "filled"},
    }
    return table.get(kind, {}).get(subtype, subtype)


def _axis_options(cfg: dict, *, is_x: bool = False) -> dict:
    out: dict[str, Any] = {}
    if cfg.get("title"):
        out["name"] = cfg["title"]
    if cfg.get("title_size"):
        out["name_font"] = {"size": _num(cfg["title_size"], 10), "bold": False, "color": "#404040"}
    if cfg.get("min") is not None:
        out["min"] = _num(cfg["min"])
    if cfg.get("max") is not None:
        out["max"] = _num(cfg["max"])
    if cfg.get("major_unit") is not None:
        out["major_unit"] = _num(cfg["major_unit"])
    if cfg.get("minor_unit") is not None:
        out["minor_unit"] = _num(cfg["minor_unit"])
    if cfg.get("log_base"):
        out["log_base"] = int(cfg["log_base"])
    if cfg.get("number_format"):
        out["num_format"] = cfg["number_format"]
    if cfg.get("gridlines") is not None:
        out["major_gridlines"] = {
            "visible": bool(cfg["gridlines"]),
            "line": {"color": cfg.get("gridline_color", "#D9D9D9"),
                     "width": _num(cfg.get("gridline_width"), 0.5)},
        }
    font = {}
    if cfg.get("label_size"):
        font["size"] = _num(cfg["label_size"], 9)
    if cfg.get("label_rotation") is not None:
        font["rotation"] = cfg["label_rotation"]
    if cfg.get("label_color"):
        font["color"] = cfg["label_color"]
    if font:
        out["num_font"] = font
    if cfg.get("reverse"):
        out["reverse"] = True
    if cfg.get("visible") is False:
        out["visible"] = False
    if cfg.get("tick_label_position"):
        out["label_position"] = cfg["tick_label_position"]
    if cfg.get("date_axis"):
        out["date_axis"] = True
    if cfg.get("major_unit_type"):
        out["major_unit_type"] = cfg["major_unit_type"]
    if cfg.get("crossing"):
        out["crossing"] = cfg["crossing"]
    if cfg.get("position_axis"):
        out["position_axis"] = cfg["position_axis"]
    if cfg.get("display_units"):
        out["display_units"] = cfg["display_units"]
        out["display_units_visible"] = True
    if is_x and cfg.get("label_align"):
        out["label_align"] = cfg["label_align"]
    return out


def _series_options(series: dict, sheet: str, headers: list, nrows: int, categories_col: int,
                    palette: list[str], index: int) -> dict:
    col = series.get("column")
    if col is None:
        col = index + 1
    col = int(col)
    values = series.get("values") or _range(sheet, col, 2, nrows + 1)
    categories = series.get("categories") or _range(sheet, categories_col, 2, nrows + 1)
    name = series.get("name")
    if not name and col < len(headers):
        name = headers[col]
    out: dict[str, Any] = {
        "name": f"={sheet}!${_col_letter(col)}$1" if name else None,
        "categories": categories,
        "values": values,
    }
    if not out["name"]:
        out.pop("name")
    color = series.get("color") or (palette[index % len(palette)] if palette else None)
    kind = series.get("type", "")
    if kind == "scatter":
        # In a scatter chart xlsxwriter's `categories` are the numeric X
        # values, not text labels.  Default to the first numeric column (B),
        # while `values` stays the Y column (C).
        x_col = int(series.get("x_column", 1))
        out["categories"] = _range(sheet, x_col, 2, nrows + 1)
    if kind in {"line", "scatter", "radar"}:
        if color:
            out["line"] = {"color": color, "width": _num(series.get("line_width"), 2.25)}
        if series.get("dash_type"):
            out.setdefault("line", {})["dash_type"] = series["dash_type"]
    else:
        if color:
            out["fill"] = {"color": color}
            out["border"] = {"color": series.get("border_color", color)}
    if series.get("marker"):
        out["marker"] = {
            "type": series["marker"],
            "size": int(series.get("marker_size", 6)),
            "fill": {"color": series.get("marker_color", color or "#1F4E79")},
            "border": {"color": series.get("marker_border", color or "#1F4E79")},
        }
    elif kind in {"line", "scatter"} and series.get("marker", True) is not False:
        out["marker"] = {"type": "circle", "size": 5,
                         "fill": {"color": color or "#1F4E79"},
                         "border": {"color": color or "#1F4E79"}}
    if series.get("data_labels") is not None:
        out["data_labels"] = _label_options(series["data_labels"])
    if series.get("trendline"):
        out["trendline"] = _trendline_options(series["trendline"])
    if series.get("y2_axis") or series.get("axis") == "secondary":
        out["y2_axis"] = True
    if series.get("gap") is not None:
        out["gap"] = int(series["gap"])
    if series.get("overlap") is not None:
        out["overlap"] = int(series["overlap"])
    if kind in {"pie", "doughnut"} and palette:
        out["points"] = [{"fill": {"color": palette[i % len(palette)]}} for i in range(nrows)]
    if series.get("points"):
        out["points"] = series["points"]
    return out


def _label_options(cfg: dict) -> dict:
    out: dict[str, Any] = {}
    percent = bool(cfg.get("show_percent"))
    for key, target in [("show", "value"), ("show_value", "value"), ("show_category", "category"),
                        ("show_series", "series_name"), ("show_percent", "percentage"),
                        ("show_legend_key", "legend_key"), ("show_bubble_size", "bubble_size")]:
        if cfg.get(key) is not None:
            out[target] = bool(cfg[key])
    # "show: true" is shorthand for the value.  When the caller asks for
    # percentages, don't also print the raw value unless they asked explicitly.
    if percent and not cfg.get("show_value"):
        out["value"] = False
        out["percentage"] = True
    if cfg.get("position"):
        out["position"] = cfg["position"]
    if cfg.get("number_format"):
        out["num_format"] = cfg["number_format"]
    if cfg.get("separator"):
        out["separator"] = cfg["separator"]
    font = {}
    if cfg.get("size"):
        font["size"] = _num(cfg["size"], 8)
    if cfg.get("bold"):
        font["bold"] = True
    if cfg.get("color"):
        font["color"] = cfg["color"]
    if font:
        out["font"] = font
    if cfg.get("leader_lines") is not None:
        out["leader_lines"] = bool(cfg["leader_lines"])
    return out


def _trendline_options(cfg: dict) -> dict:
    out = {"type": cfg.get("type", "linear")}
    for key in ["order", "period", "forward", "backward", "intercept", "name"]:
        if cfg.get(key) is not None:
            out[key] = cfg[key]
    if cfg.get("display_equation"):
        out["display_equation"] = True
    if cfg.get("display_r_squared"):
        out["display_r_squared"] = True
    return out


def build_chart(spec_path: str | Path, out_path: str | Path) -> dict:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    meta = spec.get("meta", {})
    data = spec.get("data", {})
    chart_spec = spec.get("chart", {})
    headers = data.get("headers") or []
    rows = data.get("rows") or []
    if not headers or not rows:
        raise ValueError("data.headers and data.rows are required")
    if any(len(row) != len(headers) for row in rows):
        raise ValueError("every data row must have the same length as headers")
    sheet = meta.get("sheet") or "Data"
    nrows = len(rows)
    categories_col = int(chart_spec.get("categories_column", 0))
    palette = chart_spec.get("palette") or ["#1F4E79", "#ED7D31", "#A5A5A5", "#FFC000",
                                             "#5B9BD5", "#70AD47", "#264478", "#9E480E"]
    series_specs = chart_spec.get("series") or []
    if not series_specs:
        series_specs = [{"column": i} for i in range(1, len(headers))
                        if any(isinstance(r[i], (int, float)) for r in rows)]

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(out_path), {"nan_inf_to_errors": True})
    workbook.set_properties({
        "title": meta.get("title", ""),
        "subject": meta.get("subject", ""),
        "author": meta.get("author", ""),
        "company": meta.get("company", ""),
        "comments": "Generated by Chart Forge (T041)",
    })
    worksheet = workbook.add_worksheet(sheet)
    header_fmt = workbook.add_format({"bold": True, "bg_color": "#F2F2F2", "border": 1,
                                      "border_color": "#BFBFBF", "align": "left"})
    for c_index, header in enumerate(headers):
        worksheet.write(0, c_index, header, header_fmt)
    data_fmt = workbook.add_format({"num_format": "#,##0.00", "align": "right"})
    text_fmt = workbook.add_format({"align": "left"})
    for r_index, row in enumerate(rows, start=1):
        for c_index, value in enumerate(row):
            if isinstance(value, (int, float)):
                worksheet.write_number(r_index, c_index, value, data_fmt)
            else:
                worksheet.write_string(r_index, c_index, "" if value is None else str(value), text_fmt)
    for key, width in (data.get("widths") or {}).items():
        worksheet.set_column(key, width)
    if data.get("freeze"):
        worksheet.freeze_panes(data["freeze"])
    if data.get("table"):
        worksheet.add_table(0, 0, nrows, len(headers) - 1,
                            {"style": data.get("table_style", "Table Style Medium 2"),
                             "columns": [{"header": h} for h in headers]})

    kind = (chart_spec.get("type") or "column").lower()
    subtype = _chart_subtype(kind, chart_spec.get("subtype"))
    title = chart_spec.get("title") or meta.get("title") or ""
    position = chart_spec.get("position") or {}
    width_cm = _num(position.get("width_cm"), 16.0)
    height_cm = _num(position.get("height_cm"), 9.0)
    cell = position.get("cell", "E2")

    # Group series by (type, axis) so a combo can hold several groups.
    groups: list[dict] = []
    for i, series in enumerate(series_specs):
        stype = (series.get("type") or kind).lower()
        if stype == "combo":
            stype = "column"
        axis = "secondary" if (series.get("axis") == "secondary" or series.get("y2_axis")) else "primary"
        key = (stype, axis)
        group = next((g for g in groups if g["key"] == key), None)
        if group is None:
            group = {"key": key, "type": stype, "axis": axis, "series": []}
            groups.append(group)
        group["series"].append((i, series))

    charts = []
    for gi, group in enumerate(groups):
        ctype = group["type"]
        csub = _chart_subtype(ctype, chart_spec.get("subtype") if len(groups) == 1 else None)
        chart = workbook.add_chart({"type": ctype, "subtype": csub} if csub else {"type": ctype})
        for i, series in group["series"]:
            opts = _series_options(series, sheet, headers, nrows, categories_col, palette, i)
            chart.add_series(opts)
        charts.append((group, chart))

    primary = charts[0][1]
    for group, chart in charts[1:]:
        primary.combine(chart)

    if chart_spec.get("style"):
        primary.set_style(int(chart_spec["style"]))
    if title:
        primary.set_title({"name": title, "name_font": {
            "size": _num(chart_spec.get("title_size"), 14), "bold": True,
            "color": chart_spec.get("title_color", "#1A1A1A")}, "overlay": False})
    axes = chart_spec.get("axes") or {}
    if axes.get("x"):
        primary.set_x_axis(_axis_options(axes["x"], is_x=True))
    if axes.get("y"):
        primary.set_y_axis(_axis_options(axes["y"]))
    if axes.get("y2"):
        # xlsxwriter binds the secondary axis to the combined chart, not to the
        # primary chart object; setting it on the primary leaves Excel's default
        # 0..max scale, which flattens the secondary series.
        secondary = charts[1][1] if len(charts) > 1 else primary
        secondary.set_y2_axis(_axis_options(axes["y2"]))
    if chart_spec.get("legend") is not None:
        legend = chart_spec["legend"]
        if isinstance(legend, str):
            legend = {"position": legend}
        if legend.get("none"):
            primary.set_legend({"none": True})
        else:
            opts = {"position": legend.get("position", "bottom")}
            if legend.get("size"):
                opts["font"] = {"size": _num(legend["size"], 9),
                                "color": legend.get("color", "#404040")}
            primary.set_legend(opts)
    primary.set_size({"width": int(round(width_cm * PX_PER_CM)),
                      "height": int(round(height_cm * PX_PER_CM))})
    layout = chart_spec.get("plot_layout") or {"x": 0.12, "y": 0.16, "width": 0.74, "height": 0.62}
    primary.set_plotarea({"layout": layout, "border": {"color": "#D9D9D9"},
                          "fill": {"color": "#FFFFFF"}})
    primary.set_chartarea({"border": {"none": True}, "fill": {"color": "#FFFFFF"}})
    if chart_spec.get("data_table"):
        primary.set_table({"show_keys": bool(chart_spec["data_table"].get("keys", True))})
    if chart_spec.get("disp_blanks"):
        primary.show_blanks_as(chart_spec["disp_blanks"])
    insert_opts = {}
    if position.get("offset_cm"):
        insert_opts["x_offset"] = int(_num(position["offset_cm"], 0) * PX_PER_CM)
        insert_opts["y_offset"] = int(_num(position["offset_cm"], 0) * PX_PER_CM)
    worksheet.insert_chart(cell, primary, insert_opts)
    # Include the chart in the print area.  Without this, Excel prints the data
    # table and silently clips the chart, one of the common "broken chart"
    # reports.  The explicit data.print_area overrides the computed box.
    if data.get("print_area"):
        worksheet.print_area(data["print_area"])
    else:
        m = re.match(r"([A-Z]+)(\d+)", cell)
        if m:
            chart_col = _col_index(m.group(1)) + int(math.ceil(width_cm * PX_PER_CM / 64)) + 1
            chart_row = int(m.group(2)) + int(math.ceil(height_cm * PX_PER_CM / 20)) + 1
            worksheet.print_area(0, 0, max(nrows + 1, chart_row), max(len(headers) - 1, chart_col))
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 1)
    workbook.close()

    # Post-patch: xlsxwriter has no legend overlay / doughnut hole / pie
    # rotation, and a two-cell anchor lets a chart distort when cells resize.
    post = spec.get("post") or {}
    chart_patch = {"index": 1}
    for key in ["legend", "doughnut_hole", "pie_rotation", "plot_layout",
                "rounded_corners", "plot_vis_only", "disp_blanks", "data_labels",
                "series", "bar"]:
        if key in post:
            chart_patch[key] = post[key]
    # Trendline equation labels are auto-positioned at the top-left by Excel and
    # collide with the y-axis title.  Move them into the plot's free corner.
    series_patches: list[dict] = [{} for _ in series_specs]
    for i, series in enumerate(series_specs):
        if series.get("trendline_label_layout"):
            series_patches[i]["trendline_label_layout"] = series["trendline_label_layout"]
    for i, extra in enumerate(post.get("series") or []):
        if i < len(series_patches):
            series_patches[i].update(extra)
    if any(series_patches):
        chart_patch["series"] = series_patches
    if chart_spec.get("data_labels") and "data_labels" not in chart_patch:
        chart_patch["data_labels"] = chart_spec["data_labels"]
    anchor_mode = post.get("anchor", "one_cell")
    patch = {
        "charts": [chart_patch],
        "anchors": [{"drawing": 1, "anchor": {
            "mode": anchor_mode,
            "width_cm": width_cm,
            "height_cm": height_cm,
            "alt": chart_spec.get("alt") or title,
        }}],
    }
    patch_result = patch_workbook(out_path, patch, out_path)
    audit = audit_workbook(out_path)
    return {
        "ok": audit["ok"],
        "output": str(out_path),
        "bytes": out_path.stat().st_size,
        "spec": str(spec_path),
        "chart_type": kind,
        "series": len(series_specs),
        "size_cm": [width_cm, height_cm],
        "patch": patch_result,
        "audit": audit,
    }


def inspect_chart(path: str | Path) -> dict:
    from chart_audit import audit_workbook
    return audit_workbook(path)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("spec", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--report", type=Path, default=None)
    p.add_argument("--render", type=Path, default=None)
    p = sub.add_parser("inspect")
    p.add_argument("xlsx", type=Path)
    args = parser.parse_args()
    if args.cmd == "build":
        report = build_chart(args.spec, args.output)
        if args.render:
            report["rendered"] = _render_any(args.output, args.render)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        raise SystemExit(0 if report["ok"] else 1)
    else:
        print(json.dumps(inspect_chart(args.xlsx), indent=2, ensure_ascii=False))


def _render_any(xlsx: Path, out_dir: Path) -> list[str]:
    """Prefer native Excel chart export (rung 4–5), then GridCraft (rung 3)."""
    paths = _render_excel(xlsx, out_dir)
    if paths:
        return paths
    return _render_gridcraft(xlsx, out_dir)


def _render_excel(xlsx: Path, out_dir: Path) -> list[str]:
    """Export every ChartObject with Excel's own renderer."""
    try:
        import win32com.client as win32
    except Exception:
        return []
    # Excel's Export resolves a relative path against its own working dir, not
    # the shell's; resolve before handing it over.
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    excel = None
    wb = None
    try:
        excel = win32.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(xlsx.resolve()), False, True)
        paths = []
        for si in range(1, wb.Worksheets.Count + 1):
            sheet = wb.Worksheets(si)
            count = sheet.ChartObjects().Count
            for i in range(1, count + 1):
                target = out_dir / f"chart-{si}-{i}.png"
                sheet.ChartObjects(i).Chart.Export(str(target), "PNG")
                paths.append(str(target))
        return paths
    except Exception:
        return []
    finally:
        if wb is not None:
            try:
                wb.Close(False)
            except Exception:
                pass
        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass


def _render_gridcraft(xlsx: Path, out_dir: Path) -> list[str]:
    """Render workbook to PDF via GridCraft, then PDF pages to PNG."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        try:
            from .gridcraft_bridge import find_gridcraft_cli, convert_sheet
        except ImportError:
            from gridcraft_bridge import find_gridcraft_cli, convert_sheet
        if not find_gridcraft_cli():
            return []
        pdf = out_dir / "workbook.pdf"
        convert_sheet(xlsx, pdf)
    except Exception:
        return []
    try:
        import fitz
        paths = []
        with fitz.open(pdf) as doc:
            for i, page in enumerate(doc, start=1):
                target = out_dir / f"page-{i:02d}.png"
                page.get_pixmap(dpi=150).save(target)
                paths.append(str(target))
        return paths
    except Exception:
        return []


if __name__ == "__main__":
    main()
