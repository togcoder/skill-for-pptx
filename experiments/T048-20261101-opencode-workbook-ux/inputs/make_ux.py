"""Build the T048 workbook UX spec: hidden data, visible Input form, VBA."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "artifacts"


def avatar(name: str, color: str, i: int) -> str:
    path = HERE / f"avatar-{i}.png"
    img = Image.new("RGB", (120, 120), color)
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 104, 104), fill="#FFFFFF")
    d.text((38, 40), "".join(p[0] for p in name.split()[:2]).upper(), fill=color)
    img.save(path)
    return str(path)


def build() -> dict:
    workstreams = ["Dữ liệu", "Nền tảng", "Năng lực", "Trải nghiệm"]
    owners = ["Lan Nguyễn", "Minh Trần", "Hà Phạm", "Tuấn Lê", "Mai Vũ", "Khánh Đỗ"]
    statuses = ["On track", "At risk", "Blocked", "Done"]
    headers = ["Task ID", "Workstream", "Owner", "Start", "End", "Days", "Progress",
               "Cost", "Benefit", "Status", "Priority"]
    rows = []
    start0 = dt.date(2026, 1, 5)
    for i in range(24):
        start = start0 + dt.timedelta(days=(i * 11) % 250)
        days = 5 + (i * 3) % 25
        rows.append([f"T{i + 1:03d}", workstreams[i % 4], owners[i % 6],
                     start.isoformat(), (start + dt.timedelta(days=days)).isoformat(),
                     days, round(0.1 + (i % 9) * 0.1, 2), 40 + (i * 17) % 240,
                     80 + (i * 23) % 300, statuses[i % 4],
                     ["High", "Medium", "Low"][i % 3]])
    tasks = [
        {"name": "Khảo sát hiện trạng", "start": "2026-01-05", "days": 12},
        {"name": "Chuẩn hoá dữ liệu", "start": "2026-01-26", "days": 18},
        {"name": "Tích hợp nguồn", "start": "2026-02-16", "days": 21},
        {"name": "Kiểm thử chất lượng", "start": "2026-03-16", "days": 15},
        {"name": "Đào tạo người dùng", "start": "2026-04-13", "days": 12},
        {"name": "Dashboard điều hành", "start": "2026-05-04", "days": 24},
    ]
    team = []
    colors = ["#1F4E79", "#2E75B6", "#548235", "#C55A11"]
    for i, (name, role, focus) in enumerate([
        ("Lan Nguyễn", "Programme lead", "Điều phối lộ trình"),
        ("Minh Trần", "Data lead", "Chuẩn dữ liệu chủ"),
        ("Hà Phạm", "Platform lead", "Tích hợp và vận hành"),
        ("Tuấn Lê", "Analytics lead", "KPI và dashboard"),
    ]):
        team.append({"name": name, "role": role, "focus": focus,
                     "photo": avatar(name, colors[i], i), "alt": f"Ảnh {name}"})
    nodes = [
        {"name": "Data", "x": 1, "y": 8, "group": "Core"},
        {"name": "Platform", "x": 5, "y": 9, "group": "Core"},
        {"name": "Analytics", "x": 9, "y": 7, "group": "Core"},
        {"name": "People", "x": 3, "y": 4, "group": "Enable"},
        {"name": "Process", "x": 7, "y": 3, "group": "Enable"},
        {"name": "Customer", "x": 10, "y": 2, "group": "Outcome"},
    ]
    edges = [
        {"name": "Data→Platform", "from": "Data", "to": "Platform", "x1": 1, "y1": 8, "x2": 5, "y2": 9, "weight": 3},
        {"name": "Platform→Analytics", "from": "Platform", "to": "Analytics", "x1": 5, "y1": 9, "x2": 9, "y2": 7, "weight": 3},
        {"name": "Data→People", "from": "Data", "to": "People", "x1": 1, "y1": 8, "x2": 3, "y2": 4, "weight": 2},
        {"name": "People→Process", "from": "People", "to": "Process", "x1": 3, "y1": 4, "x2": 7, "y2": 3, "weight": 2},
        {"name": "Analytics→Customer", "from": "Analytics", "to": "Customer", "x1": 9, "y1": 7, "x2": 10, "y2": 2, "weight": 2},
    ]
    total_cost = sum(r[7] for r in rows)
    total_benefit = sum(r[8] for r in rows)
    spec = {
        "title": "Điều hành chương trình chuyển đổi số 2026",
        "subtitle": "24 công việc · nhập liệu qua biểu mẫu · dữ liệu ẩn",
        "workstreams": workstreams,
        "data_last_row": 30,
        "data": {"headers": headers, "rows": rows, "freeze": "C2",
                 "print_area": "A1:K30", "formats": {"Progress": "0%"},
                 "widths": {"A:A": 10, "B:B": 16, "C:C": 18, "D:E": 13, "F:F": 8,
                            "G:G": 10, "H:I": 12, "J:J": 12, "K:K": 9}},
        "tasks": tasks,
        "team": team,
        "nodes": nodes,
        "edges": edges,
        "kpis": [
            {"label": "Công việc", "formula": "=TaskCount", "format": "0", "cached": len(rows),
             "delta": "+24 trong danh mục", "fill": "#EAF1F8", "positive": True},
            {"label": "Chi phí", "formula": '=SUBSTITUTE(TEXT(TotalCost/1000,"0.00"),".",",")&" tỷ"',
             "format": "General", "cached": f"{total_cost/1000:.2f}".replace(".", ",") + " tỷ",
             "delta": "tổng danh mục", "fill": "#EAF4E7", "positive": True},
            {"label": "Lợi ích", "formula": '=SUBSTITUTE(TEXT(TotalBenefit/1000,"0.0"),".",",")&" tỷ"',
             "format": "General", "cached": f"{total_benefit/1000:.1f}".replace(".", ",") + " tỷ",
             "delta": "tổng danh mục", "fill": "#FFF2E5", "positive": True},
            {"label": "Rủi ro", "formula": '=COUNTIF(Data!$J$2:$J$30,"At risk")', "format": "0", "cached": 6,
             "delta": "trong 24 công việc", "fill": "#F3EDF7", "positive": False},
        ],
        "pivot_source": "Data!A1:K30",
        "pivot_rows": ["Workstream"],
        "pivot_values": [{"field": "Cost", "func": "sum"}],
        "ux": {
            "input_form": True,
            "sheets": {
                "Data": {"hidden": True, "tab_color": "7F7F7F"},
                "Pivot": {"very_hidden": True, "tab_color": "7F7F7F"},
                "Model": {"hidden": True, "tab_color": "7F7F7F"},
                "Team": {"hidden": True, "tab_color": "7F7F7F"},
                "Gantt": {"hidden": True, "tab_color": "7F7F7F"},
                "Relations": {"hidden": True, "tab_color": "7F7F7F"},
                "Lookups": {"very_hidden": True, "tab_color": "7F7F7F"},
                "Dashboard": {"tab_color": "1F4E79", "protect": True},
                "Input": {"tab_color": "C55A11"},
            },
        },
    }
    return spec


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    path = HERE / "workbook_ux_spec.json"
    path.write_text(json.dumps(build(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
