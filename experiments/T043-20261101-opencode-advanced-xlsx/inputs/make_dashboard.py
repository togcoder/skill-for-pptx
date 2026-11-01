"""Generate the T043 synthetic programme workbook spec and avatar images."""
from __future__ import annotations

import datetime as dt
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
random.seed(43)


def avatar(name: str, color: str, idx: int) -> str:
    path = HERE / f"avatar-{idx}.png"
    img = Image.new("RGB", (160, 160), color)
    draw = ImageDraw.Draw(img)
    initials = "".join(p[0] for p in name.split()[:2]).upper()
    draw.ellipse((18, 18, 142, 142), fill="#FFFFFF")
    draw.text((48, 52), initials, fill=color)
    img.save(path)
    return str(path)


def make() -> Path:
    workstreams = ["Dữ liệu", "Nền tảng", "Năng lực", "Trải nghiệm"]
    owners = ["Lan", "Minh", "Hà", "Tuấn", "Mai", "Khánh"]
    statuses = ["On track", "At risk", "Blocked", "Done"]
    headers = ["Task ID", "Workstream", "Owner", "Start", "End", "Days", "Progress",
               "Cost", "Benefit", "Status", "Priority"]
    rows = []
    start0 = dt.date(2026, 1, 5)
    for i in range(60):
        ws = workstreams[i % 4]
        start = start0 + dt.timedelta(days=(i * 6) % 250)
        days = 5 + (i * 3) % 25
        end = start + dt.timedelta(days=days)
        cost = 40 + (i * 17) % 240
        benefit = int(cost * (1.1 + (i % 5) * 0.25))
        progress = min(1.0, 0.15 + (i % 9) * 0.09)
        status = statuses[i % 4]
        rows.append([f"T{i + 1:03d}", ws, owners[i % len(owners)], start.isoformat(),
                     end.isoformat(), days, round(progress, 2), cost, benefit, status,
                     ["High", "Medium", "Low"][i % 3]])
    tasks = []
    for i, name in enumerate(["Khảo sát hiện trạng", "Chuẩn hoá dữ liệu chủ", "Tích hợp nguồn",
                              "Kiểm thử chất lượng", "Đào tạo người dùng", "Dashboard điều hành",
                              "Tự động hoá báo cáo", "Đánh giá tác động", "Mở rộng phạm vi",
                              "Chuyển giao vận hành"]):
        tasks.append({"name": name, "start": (start0 + dt.timedelta(days=i * 18)).isoformat(),
                      "days": 12 + (i % 4) * 5, "progress": round(0.2 + i * 0.07, 2)})
    team = []
    colors = ["#1F4E79", "#2E75B6", "#548235", "#C55A11", "#7030A0", "#7F7F7F"]
    for i, (name, role, focus) in enumerate([
        ("Lan Nguyễn", "Programme lead", "Điều phối lộ trình và quyết định"),
        ("Minh Trần", "Data lead", "Chuẩn dữ liệu chủ và chất lượng"),
        ("Hà Phạm", "Platform lead", "Tích hợp, API và vận hành"),
        ("Tuấn Lê", "Analytics lead", "Mô hình, KPI và dashboard"),
        ("Mai Vũ", "Change lead", "Đào tạo và tiếp nhận"),
        ("Khánh Đỗ", "PMO", "Kế hoạch, rủi ro và báo cáo"),
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
        {"name": "Process→Customer", "from": "Process", "to": "Customer", "x1": 7, "y1": 3, "x2": 10, "y2": 2, "weight": 1},
    ]
    spec = {
        "title": "Điều hành chương trình chuyển đổi số 2026",
        "subtitle": "Danh mục 60 công việc · 4 nhóm · cập nhật 01/11/2026",
        "workstreams": workstreams,
        "data_last_row": 61,
        "data": {
            "headers": headers, "rows": rows, "freeze": "C2",
            "print_area": "A1:K61",
            "formats": {"Progress": "0%"},
            "widths": {"A:A": 10, "B:B": 16, "C:C": 12, "D:E": 13, "F:F": 8,
                       "G:G": 10, "H:I": 12, "J:J": 12, "K:K": 9},
        },
        "tasks": tasks,
        "team": team,
        "nodes": nodes,
        "edges": edges,
        "kpis": [
            {"label": "Công việc", "value": "60", "delta": "+12 trong quý", "fill": "#EAF1F8", "positive": True},
            {"label": "Ngân sách", "value": "8,4 tỷ", "delta": "72% đã phân bổ", "fill": "#EAF4E7", "positive": True},
            {"label": "Lợi ích", "value": "12,1 tỷ", "delta": "1,44× chi phí", "fill": "#FFF2E5", "positive": True},
            {"label": "Rủi ro", "value": "3", "delta": "1 đang theo dõi", "fill": "#F3EDF7", "positive": False},
        ],
        "pivot_source": "Data!A1:K61",
        "pivot_rows": ["Workstream"],
        "pivot_columns": ["Status"],
        "pivot_values": [{"field": "Cost", "func": "sum"}],
    }
    path = HERE / "dashboard_spec.json"
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    print(make())
