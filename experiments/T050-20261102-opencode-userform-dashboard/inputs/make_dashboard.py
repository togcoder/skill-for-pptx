"""Build the T050 dashboard spec and the VBA UserForm fixture."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "artifacts"


def build() -> dict:
    workstreams = ["Dữ liệu", "Nền tảng", "Năng lực", "Trải nghiệm"]
    owners = ["Lan Nguyễn", "Minh Trần", "Hà Phạm", "Tuấn Lê", "Mai Vũ", "Khánh Đỗ"]
    statuses = ["On track", "On track", "At risk", "Done", "On track", "Blocked"]
    rows = []
    start0 = dt.date(2026, 1, 5)
    for i in range(24):
        start = start0 + dt.timedelta(days=(i * 11) % 250)
        days = 5 + (i * 3) % 25
        rows.append([
            f"T{i + 1:03d}", workstreams[i % 4], owners[i % 6],
            start.isoformat(), (start + dt.timedelta(days=days)).isoformat(),
            days, round(0.1 + (i % 9) * 0.1, 2), 40 + (i * 17) % 240,
            80 + (i * 23) % 300, statuses[i % 6],
            ["High", "Medium", "Low"][i % 3],
        ])
    trend = []
    for m in range(1, 13):
        trend.append([f"T{m}", 120 + (m - 1) * 18, 180 + (m - 1) * 24])
    model = []
    for name in workstreams:
        subset = [r for r in rows if r[1] == name]
        model.append({
            "name": name,
            "cost": sum(r[7] for r in subset),
            "benefit": sum(r[8] for r in subset),
            "tasks": len(subset),
        })
    counts = {s: sum(1 for r in rows if r[9] == s) for s in ["On track", "At risk", "Blocked", "Done"]}
    status_counts = [[s, counts[s]] for s in ["On track", "At risk", "Blocked", "Done"]]
    total_cost = sum(r[7] for r in rows)
    total_benefit = sum(r[8] for r in rows)
    risk = counts["At risk"] + counts["Blocked"]
    return {
        "title": "Điều hành chương trình chuyển đổi số 2026",
        "subtitle": "24 công việc · 4 nhóm · dữ liệu ẩn · biểu đồ native · một trang A4 ngang",
        "data": {
            "headers": ["Task ID", "Workstream", "Owner", "Start", "End", "Days", "Progress",
                        "Cost", "Benefit", "Status", "Priority"],
            "rows": rows,
        },
        "trend": trend,
        "model": model,
        "status_counts": status_counts,
        "kpis": [
            {"label": "Công việc", "value": "24", "formula": "=SUM(Data!$L$2:$L$200)",
             "cached": len(rows), "delta": "4 nhóm · 6 người",
             "fill": "#EAF1F8", "positive": True},
            {"label": "Chi phí", "value": f"{total_cost} tr", "formula": "=SUM(Model!$B$2:$B$5)",
             "cached": total_cost, "num_format": '#,##0" tr"', "delta": "tổng 4 nhóm",
             "fill": "#EAF4E7", "positive": True},
            {"label": "Lợi ích", "value": f"{total_benefit} tr", "formula": "=SUM(Model!$C$2:$C$5)",
             "cached": total_benefit, "num_format": '#,##0" tr"', "delta": f"ROI {total_benefit / total_cost:.2f}×",
             "fill": "#FFF2E5", "positive": True},
            {"label": "Rủi ro", "value": str(risk),
             "formula": '=COUNTIFS(Data!$J$2:$J$200,"At risk",Data!$L$2:$L$200,1)',
             "cached": counts['At risk'], "delta": f"{counts['At risk']} at risk · {counts['Blocked']} blocked",
             "fill": "#FCE4D6", "positive": False},
        ],
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    path = HERE / "dashboard_spec.json"
    path.write_text(json.dumps(build(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
