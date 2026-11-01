#!/usr/bin/env python3
"""Sheet Forge — a designed Excel dashboard from a semantic spec (T046, xlsx).

Status: EXPERIMENTAL — T046 [xlsx], review requested.

This module covers the workbook-level work that a chart-only tool misses:

* a typed data table and named ranges;
* cross-sheet formulas (`SUMIFS`, `COUNTIFS`, `AVERAGEIF`, `INDEX`/`MATCH`);
* a table with embedded images and a fixed row height;
* a native Gantt (stacked bar + date axis + invisible start series);
* a relationship matrix (conditional-format heatmap) and a node-link scatter;
* a designed dashboard (KPI cards, shared palette, fixed chart geometry, print);
* an optional native PivotTable via GridCraft, with a formula summary fallback;
* a `.bas` VBA module, injected only when the host enables trust access.

CLI:
    python scripts/sheet_forge.py build spec.json -o dashboard.xlsx
    python scripts/sheet_forge.py build spec.json -o dashboard.xlsx --render preview/
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import tempfile
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
CM_PER_INCH = 2.54
PALETTE = ["#1F4E79", "#2E75B6", "#548235", "#C55A11", "#7030A0", "#7F7F7F"]
CARD_FILLS = ["#EAF1F8", "#EAF4E7", "#FFF2E5", "#F3EDF7"]


def _date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def _cm_width(cm: float) -> float:
    return cm / CM_PER_INCH * 96 / 7.0


def _cm_height(cm: float) -> float:
    return cm / CM_PER_INCH * 72


def _add_table_sheet(wb, name: str, spec: dict, fmt_header, fmt_text, fmt_num):
    ws = wb.add_worksheet(name)
    headers = spec["headers"]
    rows = spec["rows"]
    formats = {k.lower(): v for k, v in (spec.get("formats") or {}).items()}
    col_formats = []
    for header in headers:
        pattern = formats.get(header.lower())
        col_formats.append(wb.add_format({"font_size": 9, "num_format": pattern,
                                          "border": 1, "border_color": "#D9D9D9"})
                           if pattern else fmt_num)
    ws.write_row(0, 0, headers, fmt_header)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            if isinstance(value, (dt.date, dt.datetime)):
                ws.write_datetime(r, c, value, wb.add_format({"num_format": "dd-mmm-yy"}))
            elif isinstance(value, (int, float)):
                ws.write_number(r, c, value, col_formats[c])
            else:
                ws.write_string(r, c, "" if value is None else str(value), fmt_text)
    ws.add_table(0, 0, len(rows), len(headers) - 1, {
        "style": spec.get("table_style", "Table Style Medium 2"),
        "columns": [{"header": h} for h in headers],
        "autofilter": True,
    })
    for col, width in (spec.get("widths") or {}).items():
        ws.set_column(col, width)
    ws.freeze_panes(spec.get("freeze", "A2"))
    if spec.get("print_area"):
        ws.print_area(spec["print_area"])
    ws.set_landscape()
    ws.fit_to_pages(1, 0)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
    return ws


def _add_formula_sheet(wb, spec: dict, fmt_header, fmt_text, fmt_num):
    ws = wb.add_worksheet("Model")
    last = int(spec.get("data_last_row", 61))
    rows = spec.get("data", {}).get("rows") or []
    ws.write_row(0, 0, ["Workstream", "Tasks", "Cost", "Benefit", "Avg progress"], fmt_header)
    for r, workstream in enumerate(spec["workstreams"], start=1):
        subset = [row for row in rows if len(row) > 7 and row[1] == workstream]
        count = len(subset)
        cost = sum(float(row[7]) for row in subset)
        benefit = sum(float(row[8]) for row in subset)
        avg = (sum(float(row[6]) for row in subset) / count) if count else 0
        ws.write_string(r, 0, workstream, fmt_text)
        ws.write_formula(r, 1, f'=COUNTIF(Data!$B$2:$B${last},A{r + 1})', fmt_num, count)
        ws.write_formula(r, 2, f'=SUMIF(Data!$B$2:$B${last},A{r + 1},Data!$H$2:$H${last})', fmt_num, cost)
        ws.write_formula(r, 3, f'=SUMIF(Data!$B$2:$B${last},A{r + 1},Data!$I$2:$I${last})', fmt_num, benefit)
        ws.write_formula(r, 4, f'=IFERROR(AVERAGEIF(Data!$B$2:$B${last},A{r + 1},Data!$G$2:$G${last}),0)',
                         fmt_num, avg)
    ws.write_formula(7, 0, f"=COUNTA(Data!$A$2:$A${last})", fmt_num, len(rows))
    top = max(rows, key=lambda row: float(row[7])) if rows else ["", "", ""]
    ws.write_formula(8, 0, f"=INDEX(Data!$C$2:$C${last},MATCH(MAX(Data!$H$2:$H${last}),Data!$H$2:$H${last},0))",
                     fmt_text, str(top[2]) if len(top) > 2 else "")
    ws.set_column("A:A", 18); ws.set_column("B:E", 14)
    wb.define_name("TaskCount", f"=COUNTA(Data!$A$2:$A${last})")
    wb.define_name("TotalCost", f"=SUM(Data!$H$2:$H${last})")
    wb.define_name("TotalBenefit", f"=SUM(Data!$I$2:$I${last})")
    ws.print_area("A1:E10")
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    return ws


def _add_team_sheet(wb, spec: dict, fmt_header, fmt_text):
    ws = wb.add_worksheet("Team")
    ws.write_row(0, 0, ["Photo", "Name", "Role", "Focus"], fmt_header)
    ws.set_column("A:A", 7); ws.set_column("B:B", 22); ws.set_column("C:C", 20); ws.set_column("D:D", 42)
    text = wb.add_format({"font_size": 9, "valign": "vcenter", "border": 1,
                          "border_color": "#D9D9D9"})
    for r, member in enumerate(spec["team"], start=1):
        ws.set_row(r, 32)
        path = Path(member["photo"])
        if path.is_file():
            ws.insert_image(r, 0, str(path), {
                "x_offset": 2, "y_offset": 2, "x_scale": 0.24, "y_scale": 0.24,
                "description": member.get("alt", member["name"]),
            })
        ws.write_string(r, 1, member["name"], text)
        ws.write_string(r, 2, member["role"], text)
        ws.write_string(r, 3, member["focus"], text)
    ws.add_table(0, 0, len(spec["team"]), 3, {
        "style": "Table Style Medium 2",
        "columns": [{"header": h} for h in ["Photo", "Name", "Role", "Focus"]],
        "autofilter": True,
    })
    ws.freeze_panes("A2")
    ws.print_area(0, 0, len(spec["team"]), 3)
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
    return ws


def _gantt_chart(wb, spec: dict):
    chart = wb.add_chart({"type": "bar", "subtype": "stacked"})
    chart.add_series({
        "name": "Start", "categories": f"=Gantt!$A$2:$A${len(spec['tasks']) + 1}",
        "values": f"=Gantt!$B$2:$B${len(spec['tasks']) + 1}",
        "fill": {"none": True}, "border": {"none": True},
    })
    chart.add_series({
        "name": "Duration", "categories": f"=Gantt!$A$2:$A${len(spec['tasks']) + 1}",
        "values": f"=Gantt!$C$2:$C${len(spec['tasks']) + 1}",
        "fill": {"color": PALETTE[0]}, "border": {"color": PALETTE[0]},
    })
    chart.set_title({"name": "Lịch trình chương trình", "name_font": {"size": 13, "bold": True}})
    chart.set_legend({"none": True})
    # Bar charts swap the axes internally: set_y_axis controls the vertical
    # category axis (task names), set_x_axis controls the horizontal value
    # axis (dates).  Excel has no date category axis here, so use an explicit
    # serial range + date number format.  The Start series is made transparent
    # by the build patch.
    starts = [_date(task["start"]) for task in spec["tasks"]]
    ends = [start + dt.timedelta(days=int(task["days"]) - 1)
            for start, task in zip(starts, spec["tasks"])]
    serial = lambda value: (value - dt.date(1899, 12, 30)).days
    chart.set_y_axis({"num_font": {"size": 8}})
    chart.set_x_axis({
        "min": serial(min(starts)) - 7, "max": serial(max(ends)) + 7,
        "major_unit": 30, "num_format": "mmm-yy", "num_font": {"size": 8},
        "major_gridlines": {"visible": True, "line": {"color": "#E6E6E6"}},
    })
    chart.set_size({"width": 680, "height": 320})
    chart.set_plotarea({"layout": {"x": 0.24, "y": 0.12, "width": 0.72, "height": 0.78}})
    return chart


def _add_gantt_sheet(wb, spec: dict, fmt_header, fmt_text, fmt_num):
    ws = wb.add_worksheet("Gantt")
    ws.write_row(0, 0, ["Task", "Start", "Days", "End", "Progress"], fmt_header)
    for r, task in enumerate(spec["tasks"], start=1):
        ws.write_string(r, 0, task["name"], fmt_text)
        ws.write_datetime(r, 1, _date(task["start"]), wb.add_format({"num_format": "dd-mmm-yy"}))
        ws.write_number(r, 2, int(task["days"]), fmt_num)
        ws.write_formula(r, 3, f"=B{r + 1}+C{r + 1}-1", wb.add_format({"num_format": "dd-mmm-yy"}))
        ws.write_number(r, 4, float(task.get("progress", 0)), wb.add_format({"num_format": "0%"}))
    ws.set_column("A:A", 34); ws.set_column("B:D", 13); ws.set_column("E:E", 10)
    ws.freeze_panes("A2")
    chart = _gantt_chart(wb, spec)
    ws.insert_chart("A13", chart, {"x_offset": 4, "y_offset": 6,
                                   "x_scale": 1.1, "y_scale": 1.0})
    ws.print_area("A1:L27")
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)
    return ws


def _add_relations_sheet(wb, spec: dict, fmt_header, fmt_text, fmt_num):
    """Nodes + edge list + a 6×6 relationship matrix, stacked for printing.

    The node-link scatter is intentionally absent: an experimental scatter
    (one series per edge) did not render all series consistently in Excel/Graph,
    so the matrix heatmap is the deliverable.  The edge coordinates stay on the
    sheet as provenance for a future native node-link attempt.
    """
    ws = wb.add_worksheet("Relations")
    nodes = spec["nodes"]
    edges = spec["edges"]
    ws.write_row(0, 0, ["Node", "X", "Y", "Group"], fmt_header)
    for r, node in enumerate(nodes, start=1):
        ws.write_string(r, 0, node["name"], fmt_text)
        ws.write_number(r, 1, node["x"], fmt_num)
        ws.write_number(r, 2, node["y"], fmt_num)
        ws.write_string(r, 3, node["group"], fmt_text)

    # Edge list as raw data, to the right and outside the print area.
    ws.write_row(0, 8, ["Edge", "From", "To", "X1", "Y1", "X2", "Y2", "Weight"], fmt_header)
    for r, edge in enumerate(edges, start=1):
        ws.write_string(r, 8, edge["name"], fmt_text)
        ws.write_string(r, 9, edge["from"], fmt_text)
        ws.write_string(r, 10, edge["to"], fmt_text)
        ws.write_number(r, 11, edge["x1"], fmt_num)
        ws.write_number(r, 12, edge["y1"], fmt_num)
        ws.write_number(r, 13, edge["x2"], fmt_num)
        ws.write_number(r, 14, edge["y2"], fmt_num)
        ws.write_number(r, 15, edge.get("weight", 1), fmt_num)

    # Relationship matrix below the node table.
    start = len(nodes) + 3
    ws.merge_range(start - 1, 0, start - 1, len(nodes), "Ma trận quan hệ (trọng số)",
                   wb.add_format({"bold": True, "font_size": 11, "font_color": "#1F4E79"}))
    ws.write(start, 0, "Từ \\ Đến", fmt_header)
    for c, node in enumerate(nodes, start=1):
        ws.write(start, c, node["name"], fmt_header)
    for r, a in enumerate(nodes, start=start + 1):
        ws.write(r, 0, a["name"], wb.add_format({"font_size": 9, "bold": True,
                                                 "border": 1, "border_color": "#D9D9D9"}))
        for c, b in enumerate(nodes, start=1):
            value = 0
            for edge in edges:
                if {edge["from"], edge["to"]} == {a["name"], b["name"]}:
                    value = edge.get("weight", 1)
            ws.write_number(r, c, value, wb.add_format({
                "font_size": 9, "num_format": "0", "align": "center",
                "border": 1, "border_color": "#FFFFFF"}))
    ws.conditional_format(start + 1, 1, start + len(nodes), len(nodes), {
        "type": "3_color_scale", "min_color": "#EAF1F8",
        "mid_color": "#9DC3E6", "max_color": "#1F4E79",
    })
    ws.set_column("A:A", 18); ws.set_column("B:G", 11)
    ws.set_column("I:I", 18); ws.set_column("J:P", 9)
    ws.print_area(0, 0, start + len(nodes), len(nodes))
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
    return ws


def _add_dashboard(wb, spec: dict, charts: dict, fmt_header, fmt_text):
    ws = wb.add_worksheet("Dashboard")
    ws.hide_gridlines(2)
    ws.set_column("A:N", 10)
    ws.set_row(0, 8)
    ws.merge_range("A2:N3", spec["title"], wb.add_format({
        "bold": True, "font_size": 22, "font_color": "#1F4E79", "valign": "vcenter"}))
    ws.merge_range("A4:N4", spec.get("subtitle", ""), wb.add_format({
        "font_size": 10, "font_color": "#595959", "valign": "vcenter"}))
    for i, kpi in enumerate(spec["kpis"][:4]):
        col = i * 3
        row = 6
        fill = kpi.get("fill", CARD_FILLS[i % len(CARD_FILLS)])
        ws.merge_range(row, col, row, col + 2, kpi["label"], wb.add_format({
            "bg_color": fill, "font_size": 9, "font_color": "#595959", "valign": "vcenter"}))
        value_fmt = wb.add_format({
            "bg_color": fill, "font_size": 20, "bold": True, "font_color": "#1F4E79",
            "valign": "vcenter", "align": "center", "num_format": kpi.get("format", "0")})
        ws.merge_range(row + 1, col, row + 1, col + 2, "", value_fmt)
        if kpi.get("formula"):
            ws.write_formula(row + 1, col, kpi["formula"], value_fmt,
                             kpi.get("cached", 0))
        else:
            ws.write_string(row + 1, col, kpi["value"], value_fmt)
        ws.merge_range(row + 2, col, row + 2, col + 2, kpi.get("delta", ""), wb.add_format({
            "bg_color": fill, "font_size": 9,
            "font_color": "#548235" if kpi.get("positive", True) else "#C00000"}))
    ws.insert_chart("A11", charts["gantt"], {"x_offset": 4, "y_offset": 4})
    ws.insert_chart("H26", charts["cost"], {"x_offset": 4, "y_offset": 4})
    # Relationship matrix (native conditional-format heatmap).
    nodes = spec["nodes"]
    edges = spec["edges"]
    ws.merge_range("A28:G28", "Ma trận quan hệ công việc", wb.add_format({
        "bold": True, "font_size": 12, "font_color": "#1F4E79"}))
    ws.write(28, 0, "Từ \\ Đến", wb.add_format({"bold": True, "font_size": 8,
                                                "bg_color": "#1F4E79", "font_color": "#FFFFFF"}))
    for c, node in enumerate(nodes, start=1):
        ws.write(28, c, node["name"], wb.add_format({"bold": True, "font_size": 8,
                                                     "bg_color": "#1F4E79", "font_color": "#FFFFFF"}))
    for r, a in enumerate(nodes, start=29):
        ws.write(r, 0, a["name"], wb.add_format({"font_size": 8, "bold": True}))
        for c, b in enumerate(nodes, start=1):
            value = 0
            for edge in edges:
                if {edge["from"], edge["to"]} == {a["name"], b["name"]}:
                    value = edge.get("weight", 1)
            ws.write_number(r, c, value, wb.add_format({"font_size": 8, "num_format": "0",
                                                        "border": 1, "border_color": "#FFFFFF"}))
    ws.conditional_format(29, 1, 29 + len(nodes) - 1, len(nodes), {
        "type": "3_color_scale", "min_color": "#EAF1F8",
        "mid_color": "#9DC3E6", "max_color": "#1F4E79",
    })
    ws.merge_range("A38:N38", "Nguồn: dữ liệu tổng hợp cho mục đích trình diễn.", wb.add_format({
        "font_size": 8, "italic": True, "font_color": "#7F7F7F"}))
    ws.print_area("A1:N39")
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.3, 0.3, 0.4, 0.4)
    return ws


def _add_cost_chart(wb, spec: dict):
    chart = wb.add_chart({"type": "column"})
    chart.add_series({
        "name": "Cost", "categories": "=Model!$A$2:$A$5", "values": "=Model!$C$2:$C$5",
        "fill": {"color": PALETTE[1]}, "data_labels": {"value": True, "num_format": "#,##0"},
    })
    chart.add_series({
        "name": "Benefit", "categories": "=Model!$A$2:$A$5", "values": "=Model!$D$2:$D$5",
        "fill": {"color": PALETTE[2]},
    })
    chart.set_title({"name": "Chi phí và lợi ích theo nhóm", "name_font": {"size": 13, "bold": True}})
    chart.set_legend({"position": "bottom", "font": {"size": 8}})
    chart.set_y_axis({"num_format": "#,##0", "num_font": {"size": 8},
                      "major_gridlines": {"visible": True, "line": {"color": "#E6E6E6"}}})
    chart.set_x_axis({"num_font": {"size": 8}})
    chart.set_size({"width": 500, "height": 280})
    return chart


def _gridcraft_cli():
    try:
        try:
            from .gridcraft_bridge import find_gridcraft_cli
        except ImportError:
            from gridcraft_bridge import find_gridcraft_cli
        return find_gridcraft_cli()
    except Exception:
        return None


def _gridcraft_pivot(path: Path, spec: dict, cli=None) -> bool:
    cli = cli or _gridcraft_cli()
    if not cli:
        return False
    steps = [
        {"command": "home.insertSheet", "params": {"name": "Pivot"}},
        {"command": "insert.pivotTable", "params": {
            "source": spec["pivot_source"],
            "destination": "Pivot!A3",
            "rows": spec["pivot_rows"],
            "columns": spec.get("pivot_columns", []),
            "values": spec["pivot_values"],
        }},
    ]
    with tempfile.TemporaryDirectory() as td:
        script = Path(td) / "pivot.jsonl"
        script.write_text("\n".join(json.dumps(s) for s in steps), encoding="utf-8")
        res = subprocess.run([str(cli), "run", "--in", str(path), "--script", str(script),
                              "--out", str(path)], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False)
        return res.returncode == 0


def _filter_summary(wb, spec: dict, fmt_header, fmt_text, fmt_num):
    """Formula summary on the Pivot sheet when GridCraft is unavailable."""
    ws = wb.add_worksheet("Pivot")
    ws.write_row(2, 0, ["Workstream", "Cost", "Tasks"], fmt_header)
    last = spec.get("data_last_row", 61)
    for i, workstream in enumerate(spec["workstreams"], start=3):
        ws.write_string(i, 0, workstream, fmt_text)
        ws.write_formula(i, 1, f'=SUMIF(Data!$B$2:$B${last},A{i + 1},Data!$H$2:$H${last})', fmt_num, 0)
        ws.write_formula(i, 2, f'=COUNTIF(Data!$B$2:$B${last},A{i + 1})', fmt_num, 0)
    ws.set_column("A:A", 20); ws.set_column("B:C", 14)
    ws.print_area(0, 0, 3 + len(spec["workstreams"]) - 1, 2)
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    return ws


def _add_lookups_sheet(wb, spec: dict, fmt_header, fmt_text):
    ws = wb.add_worksheet("Lookups")
    ws.write_row(0, 0, ["Workstream", "Owner", "Status", "Priority"], fmt_header)
    workstreams = spec.get("workstreams") or ["Dữ liệu", "Nền tảng", "Năng lực", "Trải nghiệm"]
    owners = [m["name"] for m in spec.get("team", [])] or ["Lan", "Minh", "Hà", "Tuấn"]
    statuses = ["On track", "At risk", "Blocked", "Done"]
    priorities = ["High", "Medium", "Low"]
    for i, value in enumerate(workstreams, start=1):
        ws.write_string(i, 0, value, fmt_text)
    for i, value in enumerate(owners, start=1):
        ws.write_string(i, 1, value, fmt_text)
    for i, value in enumerate(statuses, start=1):
        ws.write_string(i, 2, value, fmt_text)
    for i, value in enumerate(priorities, start=1):
        ws.write_string(i, 3, value, fmt_text)
    ws.set_column("A:D", 20)
    return ws


def _add_input_sheet(wb, spec: dict, fmt_header, fmt_text):
    """A visible, protected data-entry surface over the hidden Data sheet."""
    ws = wb.add_worksheet("Input")
    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 18)
    ws.set_column("C:D", 17)
    ws.set_column("E:E", 16)
    ws.set_column("F:G", 17)
    ws.set_column("H:H", 3)
    ws.set_row(0, 10)
    ws.merge_range("B2:G2", "NHẬP CÔNG VIỆC", wb.add_format({
        "bold": True, "font_size": 20, "font_color": "#FFFFFF", "bg_color": "#1F4E79",
        "valign": "vcenter", "align": "left"}))
    ws.set_row(1, 34)
    ws.merge_range("B3:G3", "Biểu mẫu ghi vào sheet Data (ẩn). Mỗi lần thêm một dòng; dashboard tự tính lại.",
                   wb.add_format({"font_size": 9, "font_color": "#595959", "valign": "vcenter"}))
    ws.merge_range("B5:G5", "THÔNG TIN CÔNG VIỆC", wb.add_format({
        "bold": True, "font_size": 10, "font_color": "#1F4E79", "bg_color": "#EAF1F8",
        "valign": "vcenter"}))
    label = wb.add_format({"bold": True, "font_size": 9, "font_color": "#404040",
                           "valign": "vcenter", "align": "right"})
    inp = wb.add_format({"locked": False, "font_size": 10, "bg_color": "#FFFFFF",
                         "border": 1, "border_color": "#BFBFBF", "valign": "vcenter"})
    auto = wb.add_format({"font_size": 10, "bg_color": "#F2F2F2", "border": 1,
                          "border_color": "#BFBFBF", "valign": "vcenter"})
    rows = [
        (6, "Workstream", "C6:D6", "Owner", "F6:G6", "C6", "=Lookups!$A$2:$A$5",
         "F6", "=Lookups!$B$2:$B$7"),
        (7, "Ngày bắt đầu", "C7:D7", "Số ngày", "F7:G7", None, None, None, None),
        (8, "Chi phí (triệu)", "C8:D8", "Lợi ích (triệu)", "F8:G8", None, None, None, None),
        (9, "Trạng thái", "C9:D9", "Ưu tiên", "F9:G9", "C9", "=Lookups!$C$2:$C$5",
         "F9", "=Lookups!$D$2:$D$4"),
    ]
    for row, l1, m1, l2, m2, s1, src1, s2, src2 in rows:
        ws.set_row(row - 1, 26)
        ws.write(row - 1, 1, l1, label)
        ws.merge_range(row - 1, 2, row - 1, 3, "", inp)
        ws.write(row - 1, 4, l2, label)
        ws.merge_range(row - 1, 5, row - 1, 6, "", inp)
        if src1:
            ws.data_validation(s1, {"validate": "list", "source": src1,
                                    "error_message": "Chọn từ danh sách."})
            ws.data_validation(s2, {"validate": "list", "source": src2,
                                    "error_message": "Chọn từ danh sách."})
    ws.write(9, 1, "Mã công việc", label)
    ws.merge_range("C10:D10", "", auto)
    ws.write_formula(9, 2, '=IF(COUNTA(Data!$A$2:$A$999)=0,"T001","T"&TEXT(COUNTA(Data!$A$2:$A$999)+1,"000"))', auto)
    ws.data_validation("C7", {"validate": "date", "criteria": "between",
                              "minimum": dt.date(2026, 1, 1), "maximum": dt.date(2027, 12, 31),
                              "error_title": "Ngày không hợp lệ",
                              "error_message": "Chọn ngày trong khoảng 2026-01-01 → 2027-12-31."})
    ws.data_validation("F7", {"validate": "integer", "criteria": "between", "minimum": 1,
                              "maximum": 365, "error_message": "Số ngày từ 1 đến 365."})
    for cell in ("C8", "F8"):
        ws.data_validation(cell, {"validate": "decimal", "criteria": ">=", "value": 0,
                                  "error_message": "Giá trị phải >= 0."})

    button = {"width": 132, "height": 30}
    ws.insert_button("B12", {**button, "caption": "Thêm bản ghi",
                             "macro": "DashboardTools.AddRecord"})
    ws.insert_button("D12", {**button, "caption": "Xóa biểu mẫu",
                             "macro": "DashboardTools.ClearForm"})
    ws.insert_button("F12", {**button, "caption": "Làm mới",
                             "macro": "DashboardTools.RefreshDashboard"})

    ws.merge_range("B14:G14", "QUY TẮC NHẬP", wb.add_format({
        "bold": True, "font_size": 10, "font_color": "#1F4E79", "bg_color": "#FFF2E5"}))
    notes = [
        "1. Chọn Workstream, Owner, Trạng thái, Ưu tiên từ danh sách — không gõ tay.",
        "2. Ngày bắt đầu theo ISO 8601 (YYYY-MM-DD); số ngày 1–365.",
        "3. Mã công việc tự sinh; không sửa ô xám.",
        "4. Nhấn “Thêm bản ghi” (nút hiển thị khi mở trong Excel) để ghi vào sheet Data (ẩn).",
        "5. Sheet này được bảo vệ; chỉ các ô trắng được nhập.",
    ]
    for i, note in enumerate(notes):
        ws.merge_range(14 + i, 1, 14 + i, 6, note, wb.add_format({
            "font_size": 9, "font_color": "#404040", "valign": "vcenter", "text_wrap": True}))
    ws.set_row(18, 8)
    ws.merge_range("B20:G20", "Sẵn sàng.", wb.add_format({
        "font_size": 9, "italic": True, "font_color": "#1F4E79", "bg_color": "#EAF1F8",
        "valign": "vcenter"}))
    ws.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})
    ws.print_area("B2:G20")
    ws.set_landscape()
    ws.fit_to_pages(1, 1)
    ws.set_margins(0.4, 0.4, 0.5, 0.5)
    ws.activate()
    ws.set_tab_color("#C55A11")
    return ws


def _apply_ux(wb, spec: dict) -> None:
    ux = spec.get("ux") or {}
    for name, cfg in (ux.get("sheets") or {}).items():
        ws = wb.get_worksheet_by_name(name)
        if ws is None:
            continue
        if cfg.get("very_hidden"):
            ws.very_hidden()
        elif cfg.get("hidden"):
            ws.hide()
        if cfg.get("tab_color"):
            ws.set_tab_color(cfg["tab_color"])
        if cfg.get("protect"):
            ws.protect("", {"select_locked_cells": True, "select_unlocked_cells": True})





def _normalize_workbook_view(path: str | Path) -> bool:
    """Make Dashboard the first visible tab while Input stays active.

    XlsxWriter's ``set_first_sheet`` counts differently from OOXML; rewriting
    ``firstSheet`` to the Dashboard index avoids an out-of-range/blank tab bar.
    """
    path = Path(path)
    if not path.is_file():
        return False
    with zipfile.ZipFile(path) as zin:
        members = {name: zin.read(name) for name in zin.namelist()}
    if "xl/workbook.xml" not in members:
        return False
    text = members["xl/workbook.xml"].decode("utf-8")
    names = re.findall(r'<sheet name="([^"]+)"', text)
    if "Dashboard" not in names:
        return False
    index = names.index("Dashboard")
    new = re.sub(r'firstSheet="\d+"', f'firstSheet="{index}"', text)
    if new == text:
        return False
    members["xl/workbook.xml"] = new.encode("utf-8")
    tmp = path.with_suffix(".view.xlsx")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, blob in members.items():
            zout.writestr(name, blob)
    tmp.replace(path)
    return True


def _ux_stats(path: str | Path) -> dict:
    """Rung-1 summary of the workbook UX layer, read back from the package."""
    path = Path(path)
    out = {"hidden": [], "very_hidden": [], "protected": [], "tab_colors": {},
           "merged_ranges": 0, "validations": 0, "buttons": [],
           "active_tab": None, "first_sheet": None, "sheets": 0}
    if not path.is_file():
        return out
    with zipfile.ZipFile(path) as zf:
        wb = zf.read("xl/workbook.xml").decode("utf-8")
        active = re.search(r'activeTab="(\d+)"', wb)
        first = re.search(r'firstSheet="(\d+)"', wb)
        out["active_tab"] = int(active.group(1)) if active else None
        out["first_sheet"] = int(first.group(1)) if first else None
        rels = zf.read("xl/_rels/workbook.xml.rels").decode("utf-8")
        targets = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
        for tag in re.findall(r'<sheet [^>]+/>', wb):
            name = re.search(r'name="([^"]+)"', tag)
            rid = re.search(r'r:id="([^"]+)"', tag)
            state = re.search(r'state="([^"]+)"', tag)
            if not name or not rid:
                continue
            out["sheets"] += 1
            name, rid = name.group(1), rid.group(1)
            if state:
                if state.group(1) == "hidden":
                    out["hidden"].append(name)
                elif state.group(1) == "veryHidden":
                    out["very_hidden"].append(name)
            target = targets.get(rid)
            if not target:
                continue
            part = "xl/" + target.lstrip("/").replace("xl/", "", 1)
            if part not in zf.namelist():
                continue
            xml = zf.read(part).decode("utf-8")
            out["merged_ranges"] += xml.count("<mergeCell ")
            out["validations"] += xml.count("<dataValidation ")
            if "<sheetProtection" in xml:
                out["protected"].append(name)
            color = re.search(r'<tabColor rgb="([0-9A-Fa-f]+)"', xml)
            if color:
                out["tab_colors"][name] = color.group(1)
        for name in zf.namelist():
            if name.startswith("xl/drawings/") and name.endswith(".vml"):
                vml = zf.read(name).decode("utf-8", errors="replace")
                out["buttons"].extend(re.findall(r"<x:FmlaMacro>([^<]+)</x:FmlaMacro>", vml))
    return out


def build_dashboard(spec_path: str | Path, out_path: str | Path, *, pivot: bool = True,
                    vba: bool = False) -> dict:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    # Relative asset paths in a spec resolve against the spec's own directory,
    # not the caller's working directory.
    base = Path(spec_path).resolve().parent
    for member in spec.get("team", []):
        photo = Path(member.get("photo", ""))
        if photo and not photo.is_absolute():
            member["photo"] = str((base / photo).resolve())
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Decide the pivot path before the workbook is written: if GridCraft is
    # absent, put a formula summary on the Pivot sheet in the same pass instead
    # of leaving it empty or rewriting (and destroying) the dashboard later.
    gridcraft = _gridcraft_cli() if pivot else None
    wb = xlsxwriter.Workbook(str(out_path), {"use_future_functions": True, "nan_inf_to_errors": True})
    fmt_header = wb.add_format({"bold": True, "bg_color": "#1F4E79", "font_color": "#FFFFFF",
                                "border": 1, "border_color": "#FFFFFF", "align": "left"})
    fmt_text = wb.add_format({"font_size": 9, "border": 1, "border_color": "#D9D9D9"})
    fmt_num = wb.add_format({"font_size": 9, "num_format": "#,##0", "border": 1, "border_color": "#D9D9D9"})
    _add_table_sheet(wb, "Data", spec["data"], fmt_header, fmt_text, fmt_num)
    _add_formula_sheet(wb, spec, fmt_header, fmt_text, fmt_num)
    _add_team_sheet(wb, spec, fmt_header, fmt_text)
    _add_gantt_sheet(wb, spec, fmt_header, fmt_text, fmt_num)
    _add_relations_sheet(wb, spec, fmt_header, fmt_text, fmt_num)
    cost_chart = _add_cost_chart(wb, spec)
    _add_dashboard(wb, spec, {"gantt": _gantt_chart(wb, spec), "cost": cost_chart},
                   fmt_header, fmt_text)
    if not pivot or not gridcraft:
        _filter_summary(wb, spec, fmt_header, fmt_text, fmt_num)
    if (spec.get("ux") or {}).get("input_form"):
        _add_lookups_sheet(wb, spec, fmt_header, fmt_text)
        input_ws = _add_input_sheet(wb, spec, fmt_header, fmt_text)
        dashboard = wb.get_worksheet_by_name("Dashboard")
        if dashboard is not None:
            dashboard.set_first_sheet()
        input_ws.activate()
    _apply_ux(wb, spec)
    wb.close()

    pivot_ok = _gridcraft_pivot(out_path, spec, gridcraft) if (pivot and gridcraft) else False

    # Fixed chart anchors: Dashboard charts must not stretch with row/column
    # changes.  The sizes are in the insertion order.
    # Fixed chart anchors and axis repair.  GridCraft's pivot round-trip can
    # drop axis scaling/number formats, so re-apply them after it has run.
    starts = [_date(task["start"]) for task in spec["tasks"]]
    ends = [start + dt.timedelta(days=int(task["days"]) - 1)
            for start, task in zip(starts, spec["tasks"])]
    serial = lambda value: (value - dt.date(1899, 12, 30)).days
    gantt_axis = {
        "min": serial(min(starts)) - 7, "max": serial(max(ends)) + 7,
        "major_unit": 30, "number_format": "mmm-yy",
        "gridlines": True, "gridline_color": "E6E6E6",
    }
    if out_path.is_file():
        patch_workbook(out_path, {
            "charts": [
                {"index": 1, "hide_series": ["Start"], "axes": {"value": gantt_axis}},
                {"index": 2, "hide_series": ["Start"], "axes": {"value": gantt_axis}},
                {"index": 3, "axes": {"value": {"number_format": "#,##0",
                                                "gridlines": True,
                                                "gridline_color": "E6E6E6"}}},
            ],
            "anchors": [{"sheet": "Dashboard", "anchor": {
                "mode": "one_cell",
                "sizes": [[18.0, 7.0], [13.2, 6.6]],
                "alts": ["Gantt chart", "Cost and benefit chart"],
            }}],
        }, out_path)

    _normalize_workbook_view(out_path)

    vba_info = None
    if vba:
        try:
            from .vba_forge import write_dashboard_module, inject_vba, normalize_button_macros
        except ImportError:
            from vba_forge import write_dashboard_module, inject_vba, normalize_button_macros
        bas = out_path.with_suffix(".bas")
        write_dashboard_module(bas)
        injected = inject_vba(out_path, bas)
        if injected:
            normalize_button_macros(injected)
        vba_info = {"bas": str(bas), "injected": injected}
    audit = audit_workbook(out_path)
    return {"ok": audit["ok"], "output": str(out_path), "bytes": out_path.stat().st_size,
            "pivot": pivot_ok, "vba": vba_info, "audit": audit,
            "ux": _ux_stats(out_path) if (spec.get("ux") or {}) else None}


def _render_excel(xlsx: Path, out_dir: Path) -> list[str]:
    try:
        import win32com.client as win32
    except Exception:
        return []
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    excel = wb = None
    try:
        excel = win32.DispatchEx("Excel.Application")
        excel.Visible = False; excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(xlsx.resolve()), False, True)
        paths = []
        for si in range(1, wb.Worksheets.Count + 1):
            ws = wb.Worksheets(si)
            if ws.Name != "Dashboard":
                continue
            for i in range(1, ws.ChartObjects().Count + 1):
                target = out_dir / f"dashboard-chart-{i}.png"
                ws.ChartObjects(i).Chart.Export(str(target), "PNG")
                paths.append(str(target))
        pdf = out_dir / "dashboard.pdf"
        ws.ExportAsFixedFormat(0, str(pdf))
        paths.append(str(pdf))
        return paths
    except Exception:
        return []
    finally:
        if wb is not None:
            try: wb.Close(False)
            except Exception: pass
        if excel is not None:
            try: excel.Quit()
            except Exception: pass


def main() -> None:
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("spec", type=Path)
    b.add_argument("-o", "--output", type=Path, required=True)
    b.add_argument("--no-pivot", action="store_true")
    b.add_argument("--vba", action="store_true")
    b.add_argument("--render", type=Path, default=None)
    args = p.parse_args()
    report = build_dashboard(args.spec, args.output, pivot=not args.no_pivot, vba=args.vba)
    if args.render:
        report["rendered"] = _render_excel(args.output, args.render)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
