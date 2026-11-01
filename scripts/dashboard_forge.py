"""Compose a readable dashboard from many charts (T050, xlsx).

Status: EXPERIMENTAL — T050.  This is a composition prototype, not a second
canonical workbook builder.  It uses a 12-column grid, a KPI strip, four native
charts, a hidden data/model layer and form-control buttons.  The goal is to
test *composition* rules that the T046 dashboard did not have:

* one grid (A:L, 12 columns), every card/chart snapped to it;
* one reading order: title -> KPI -> trend/composition -> comparison/status;
* one palette: navy/blue for the primary series, orange for attention, grey for
  context;
* native charts only, with a source line and a print area that fits one A4
  landscape page;
* hidden Data/Model/Trend sheets; the dashboard is the only visible sheet.

CLI:
    python scripts/dashboard_forge.py build spec.json -o dashboard.xlsx
    python scripts/dashboard_forge.py inspect dashboard.xlsx
"""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

try:
    import xlsxwriter
except ImportError as exc:  # pragma: no cover
    raise SystemExit("xlsxwriter is required: pip install xlsxwriter") from exc

NAVY = "#1F4E79"
BLUE = "#2E75B6"
LIGHT = "#9DC3E6"
ORANGE = "#C55A11"
GREEN = "#548235"
GREY = "#7F7F7F"
PALE = "#EAF1F8"


def _fmt(wb, **kw):
    base = {"font_name": "Calibri", "font_size": 10, "font_color": "#1A1A1A"}
    base.update(kw)
    return wb.add_format(base)


def _sheet(wb, name: str, *, hidden: bool = False, very_hidden: bool = False):
    ws = wb.add_worksheet(name)
    if very_hidden:
        ws.very_hidden()
    elif hidden:
        ws.hide()
    return ws


def _data_sheet(wb, spec: dict, fmt_header, fmt_text, fmt_num) -> None:
    ws = _sheet(wb, "Data", hidden=True)
    headers = spec["data"]["headers"]
    ws.write_row(0, 0, headers, fmt_header)
    for r, row in enumerate(spec["data"]["rows"], start=1):
        for c, value in enumerate(row):
            if isinstance(value, (int, float)):
                ws.write_number(r, c, value, fmt_num)
            else:
                ws.write_string(r, c, str(value), fmt_text)
    ws.set_column("A:A", 10)
    ws.set_column("B:B", 18)
    ws.set_column("C:C", 18)
    ws.set_column("D:E", 12)
    ws.set_column("F:F", 8)
    ws.set_column("G:G", 10)
    ws.set_column("H:I", 12)
    ws.set_column("J:K", 11)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, len(spec["data"]["rows"]), len(headers) - 1)
    ws.print_area(0, 0, len(spec["data"]["rows"]), len(headers) - 1)


def _trend_sheet(wb, spec: dict, fmt_header, fmt_text, fmt_num) -> None:
    ws = _sheet(wb, "Trend", hidden=True)
    ws.write_row(0, 0, ["Tháng", "Chi phí", "Lợi ích"], fmt_header)
    for r, (month, cost, benefit) in enumerate(spec["trend"], start=1):
        ws.write_string(r, 0, month, fmt_text)
        ws.write_number(r, 1, cost, fmt_num)
        ws.write_number(r, 2, benefit, fmt_num)
    ws.set_column("A:C", 12)


def _model_sheet(wb, spec: dict, fmt_header, fmt_text, fmt_num) -> None:
    ws = _sheet(wb, "Model", hidden=True)
    ws.write_row(0, 0, ["Nhóm", "Chi phí", "Lợi ích", "Công việc"], fmt_header)
    for r, row in enumerate(spec["model"], start=1):
        ws.write_string(r, 0, row["name"], fmt_text)
        ws.write_number(r, 1, row["cost"], fmt_num)
        ws.write_number(r, 2, row["benefit"], fmt_num)
        ws.write_number(r, 3, row["tasks"], fmt_num)
    ws.set_column("A:A", 20)
    ws.set_column("B:D", 12)


def _chart(wb, kind: str, title: str, *, width: int = 600, height: int = 290):
    chart = wb.add_chart({"type": kind})
    chart.set_title({"name": title, "name_font": {"size": 13, "bold": True, "color": "#10243A"}})
    chart.set_legend({"position": "bottom", "font": {"size": 8}})
    chart.set_size({"width": width, "height": height})
    chart.set_chartarea({"border": {"color": "#D6DEE8"}, "fill": {"color": "#FFFFFF"}})
    chart.set_plotarea({"fill": {"color": "#FFFFFF"}})
    return chart


def _trend_chart(wb):
    chart = _chart(wb, "line", "Chi phí và lợi ích theo tháng", width=540, height=250)
    chart.add_series({
        "name": "Chi phí", "categories": "=Trend!$A$2:$A$13", "values": "=Trend!$B$2:$B$13",
        "line": {"color": NAVY, "width": 2.4}, "marker": {"type": "circle", "size": 5,
                                                          "fill": {"color": NAVY},
                                                          "border": {"color": NAVY}},
    })
    chart.add_series({
        "name": "Lợi ích", "categories": "=Trend!$A$2:$A$13", "values": "=Trend!$C$2:$C$13",
        "line": {"color": ORANGE, "width": 2.4}, "marker": {"type": "circle", "size": 5,
                                                             "fill": {"color": ORANGE},
                                                             "border": {"color": ORANGE}},
    })
    chart.set_y_axis({"num_format": "#,##0", "num_font": {"size": 8},
                      "major_gridlines": {"visible": True, "line": {"color": "#E6E6E6"}}})
    chart.set_x_axis({"num_font": {"size": 8}})
    return chart


def _composition_chart(wb):
    chart = _chart(wb, "column", "Chi phí theo nhóm", width=390, height=250)
    chart.add_series({
        "name": "Chi phí", "categories": "=Model!$A$2:$A$5", "values": "=Model!$B$2:$B$5",
        "fill": {"color": NAVY}, "gap": 55,
        "data_labels": {"value": True, "num_format": "#,##0", "font": {"size": 8}},
    })
    chart.set_y_axis({"num_format": "#,##0", "num_font": {"size": 8},
                      "major_gridlines": {"visible": True, "line": {"color": "#E6E6E6"}}})
    chart.set_x_axis({"num_font": {"size": 8}, "label_position": "low"})
    chart.set_legend({"none": True})
    return chart


def _comparison_chart(wb):
    chart = _chart(wb, "bar", "Chi phí và lợi ích theo nhóm", width=540, height=250)
    chart.add_series({
        "name": "Chi phí", "categories": "=Model!$A$2:$A$5", "values": "=Model!$B$2:$B$5",
        "fill": {"color": LIGHT},
    })
    chart.add_series({
        "name": "Lợi ích", "categories": "=Model!$A$2:$A$5", "values": "=Model!$C$2:$C$5",
        "fill": {"color": GREEN},
    })
    chart.set_x_axis({"num_format": "#,##0", "num_font": {"size": 8},
                      "major_gridlines": {"visible": True, "line": {"color": "#E6E6E6"}}})
    chart.set_y_axis({"num_font": {"size": 8}})
    return chart


def _status_chart(wb, spec):
    chart = _chart(wb, "doughnut", "Trạng thái công việc", width=380, height=250)
    chart.add_series({
        "name": "Trạng thái", "categories": "=Dashboard!$A$41:$A$44",
        "values": "=Dashboard!$B$41:$B$44",
        "points": [{"fill": {"color": GREEN}}, {"fill": {"color": ORANGE}},
                   {"fill": {"color": "#C00000"}}, {"fill": {"color": BLUE}}],
        "data_labels": {"value": True, "font": {"size": 8, "bold": True}},
    })
    chart.set_hole_size(55)
    chart.set_legend({"position": "right", "font": {"size": 7}})
    return chart


def _dashboard_sheet(wb, spec: dict, charts: dict, fmt_title, fmt_sub, fmt_card, fmt_value,
                     fmt_delta, fmt_section, fmt_text, fmt_num):
    ws = wb.add_worksheet("Dashboard")
    ws.hide_gridlines(2)
    ws.set_column("A:L", 10.5)
    for row, height in {0: 12, 1: 28, 2: 8, 3: 6, 4: 18, 5: 30, 6: 16,
                        7: 6, 8: 14, 9: 14, 10: 15, 11: 15, 12: 15, 13: 15, 14: 15,
                        15: 15, 16: 15, 17: 15, 18: 15, 19: 15, 20: 15, 21: 15,
                        22: 6, 23: 14, 24: 15, 25: 15, 26: 15, 27: 15, 28: 15,
                        29: 15, 30: 15, 31: 15, 32: 15, 33: 15, 34: 15, 35: 15,
                        36: 15, 37: 6}.items():
        ws.set_row(row, height)
    ws.merge_range("A1:L2", spec["title"], fmt_title)
    ws.merge_range("A3:H3", spec.get("subtitle", ""), fmt_sub)
    # KPI cards: four cards, each 3 columns.
    for i, kpi in enumerate(spec["kpis"][:4]):
        c = i * 3
        fill = kpi.get("fill", PALE)
        card = wb.add_format({"bg_color": fill, "border": 1, "border_color": "#D6DEE8"})
        label = wb.add_format({"bg_color": fill, "font_size": 9, "font_color": "#595959",
                               "valign": "vcenter", "border": 1, "border_color": "#D6DEE8"})
        value = wb.add_format({"bg_color": fill, "font_size": 22, "bold": True,
                               "font_color": NAVY, "align": "center", "valign": "vcenter",
                               "border": 1, "border_color": "#D6DEE8"})
        delta = wb.add_format({"bg_color": fill, "font_size": 9,
                               "font_color": GREEN if kpi.get("positive", True) else "#C00000",
                               "border": 1, "border_color": "#D6DEE8"})
        ws.merge_range(4, c, 4, c + 2, kpi["label"], label)
        ws.merge_range(5, c, 5, c + 2, kpi["value"], value)
        ws.merge_range(6, c, 6, c + 2, kpi.get("delta", ""), delta)
    # Section labels + charts.
    ws.merge_range("A9:G9", "XU HƯỚNG", fmt_section)
    ws.merge_range("H9:L9", "CƠ CẤU", fmt_section)
    ws.insert_chart("A10", charts["trend"], {"x_offset": 2, "y_offset": 2})
    ws.insert_chart("H10", charts["composition"], {"x_offset": 2, "y_offset": 2})
    ws.merge_range("A24:G24", "SO SÁNH", fmt_section)
    ws.merge_range("H24:L24", "TRẠNG THÁI", fmt_section)
    ws.insert_chart("A25", charts["comparison"], {"x_offset": 2, "y_offset": 2})
    ws.insert_chart("H25", charts["status"], {"x_offset": 2, "y_offset": 2})
    # Hidden helper table for the doughnut (kept on the dashboard so the chart
    # has a stable range; the rows are outside the print area).
    ws.write_row(39, 0, ["Trạng thái", "Số việc"], fmt_section)
    for r, (label, value) in enumerate(spec["status_counts"], start=40):
        ws.write_string(r, 0, label, fmt_text)
        ws.write_number(r, 1, value, fmt_num)
    # Footer + filter buttons.
    ws.merge_range("A38:I38", "Nguồn: dữ liệu tổng hợp cho mục đích trình diễn. "
                              "Biểu đồ native Excel; bảng dữ liệu được ẩn.", fmt_sub)
    ws.insert_button("J38", {"caption": "Nhập liệu", "macro": "FormTools.ShowEntryForm",
                             "width": 78, "height": 24})
    ws.insert_button("K38", {"caption": "Rủi ro", "macro": "FormTools.FilterRisk",
                             "width": 60, "height": 24})
    ws.insert_button("L38", {"caption": "Tất cả", "macro": "FormTools.FilterAll",
                             "width": 60, "height": 24})
    ws.print_area("A1:L39")
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.25, 0.25, 0.35, 0.35)
    ws.set_tab_color(NAVY)
    ws.activate()
    return ws


def build_dashboard(spec_path: str | Path, out_path: str | Path) -> dict:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    out_path = Path(out_path)
    wb = xlsxwriter.Workbook(str(out_path), {"nan_inf_to_errors": True})
    fmt_header = _fmt(wb, bold=True, font_color="#FFFFFF", bg_color=NAVY, border=1,
                      border_color="#FFFFFF", align="center", valign="vcenter")
    fmt_text = _fmt(wb, border=1, border_color="#D6DEE8", valign="vcenter")
    fmt_num = _fmt(wb, num_format="#,##0", border=1, border_color="#D6DEE8",
                   align="right", valign="vcenter")
    fmt_title = _fmt(wb, bold=True, font_size=22, font_color=NAVY, valign="vcenter")
    fmt_sub = _fmt(wb, font_size=9, font_color="#595959", valign="vcenter")
    fmt_section = _fmt(wb, bold=True, font_size=10, font_color=NAVY,
                       bg_color="#EAF1F8", valign="vcenter")
    fmt_card = _fmt(wb, bg_color=PALE)
    fmt_value = _fmt(wb, bg_color=PALE)
    fmt_delta = _fmt(wb, bg_color=PALE)
    _data_sheet(wb, spec, fmt_header, fmt_text, fmt_num)
    _trend_sheet(wb, spec, fmt_header, fmt_text, fmt_num)
    _model_sheet(wb, spec, fmt_header, fmt_text, fmt_num)
    charts = {
        "trend": _trend_chart(wb),
        "composition": _composition_chart(wb),
        "comparison": _comparison_chart(wb),
        "status": _status_chart(wb, spec),
    }
    _dashboard_sheet(wb, spec, charts, fmt_title, fmt_sub, fmt_card, fmt_value, fmt_delta,
                     fmt_section, fmt_text, fmt_num)
    wb.close()
    audit = audit_dashboard(out_path)
    return {"ok": audit["ok"], "output": str(out_path), "bytes": out_path.stat().st_size,
            "audit": audit}


def audit_dashboard(path: str | Path) -> dict:
    """Structural audit of the visible dashboard and the hidden layer."""
    path = Path(path)
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict[str, Any] = {}
    with zipfile.ZipFile(path) as zf:
        book = zf.read("xl/workbook.xml").decode("utf-8")
        names = [n for n in zf.namelist() if n.startswith("xl/charts/chart") and n.endswith(".xml")]
        stats["charts"] = len(names)
        stats["sheets"] = book.count("<sheet ")
        if 'state="hidden"' not in book:
            errors.append("data sheet is not hidden")
        if 'tabColor rgb="FF1F4E79"' not in zf.read("xl/worksheets/sheet4.xml").decode("utf-8"):
            warnings.append("dashboard tab colour missing")
        for name in names:
            xml = zf.read(name).decode("utf-8")
            if "<c:title>" not in xml:
                warnings.append(f"{name}: no chart title")
            if xml.count("<c:ser>") > 1 and "<c:legend>" not in xml:
                warnings.append(f"{name}: multi-series chart without legend")
    stats["ok"] = not errors
    return {"ok": not errors, "errors": errors, "warnings": warnings, "stats": stats}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("spec", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p = sub.add_parser("inspect")
    p.add_argument("xlsx", type=Path)
    args = parser.parse_args()
    if args.cmd == "build":
        print(json.dumps(build_dashboard(args.spec, args.output), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(audit_dashboard(args.xlsx), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
