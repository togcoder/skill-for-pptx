"""Create the T052 chart specs and build them with Chart Forge (SheetCraft)."""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts" / "charts"


def write(name: str, spec: dict) -> Path:
    path = HERE / f"{name}.json"
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def meta(title: str) -> dict:
    return {"title": title, "sheet": "Data", "author": "T052", "company": "DocumentCraft"}


def line_training() -> dict:
    rows = []
    for epoch in range(1, 41):
        train = 0.06 + 0.86 * math.exp(-epoch / 8.5)
        val = 0.09 + 0.93 * math.exp(-epoch / 7.2) + (0.012 * max(0, epoch - 30))
        rows.append([epoch, round(train, 4), round(val, 4)])
    return {
        "meta": meta("Train / validation loss"),
        "data": {"headers": ["Epoch", "Train loss", "Validation loss"], "rows": rows,
                 "widths": {"A:A": 10, "B:C": 16}, "freeze": "A2"},
        "chart": {
            "type": "line", "subtype": "smooth", "title": "",
            "style": 10, "palette": ["#1F4E79", "#C55A11"],
            "position": {"cell": "E2", "width_cm": 15.6, "height_cm": 8.2},
            "categories_column": 0,
            "axes": {
                "x": {"title": "Epoch", "label_size": 9, "min": 0, "max": 40, "major_unit": 5},
                "y": {"title": "Loss", "min": 0, "max": 1.0, "major_unit": 0.2,
                      "number_format": "0.0", "gridlines": True, "label_size": 9},
            },
            "legend": {"position": "bottom", "size": 9},
            "series": [
                {"name": "Train loss", "column": 1, "color": "#1F4E79", "line_width": 2.2, "marker": "none"},
                {"name": "Validation loss", "column": 2, "color": "#C55A11", "line_width": 2.2, "marker": "none"},
            ],
        },
        "post": {"anchor": "one_cell", "plot_layout": {"x": 0.11, "y": 0.16, "w": 0.76, "h": 0.60}},
    }


def scatter_pr() -> dict:
    recall = [0.0, 0.08, 0.16, 0.24, 0.32, 0.40, 0.48, 0.56, 0.64, 0.72, 0.80, 0.88, 0.94, 1.0]
    precision = [1.0, 0.99, 0.985, 0.975, 0.965, 0.952, 0.936, 0.915, 0.888, 0.852, 0.805, 0.735, 0.62, 0.34]
    rows = [[r, p] for r, p in zip(recall, precision)]
    return {
        "meta": meta("Đường cong precision–recall"),
        "data": {"headers": ["Recall", "Precision"], "rows": rows, "widths": {"A:B": 12}},
        "chart": {
            "type": "scatter", "subtype": "smooth_markers", "title": "Đường cong precision–recall",
            "style": 10, "palette": ["#1F4E79"],
            "position": {"cell": "E2", "width_cm": 14.4, "height_cm": 8.0},
            "categories_column": 0,
            "axes": {
                "x": {"title": "Recall", "min": 0, "max": 1.0, "major_unit": 0.2,
                      "number_format": "0.0", "gridlines": True, "label_size": 9},
                "y": {"title": "Precision", "min": 0, "max": 1.0, "major_unit": 0.2,
                      "number_format": "0.0", "gridlines": True, "label_size": 9},
            },
            "legend": {"position": "none", "size": 9},
            "series": [{"name": "Ours", "column": 1, "color": "#1F4E79", "line_width": 2.4, "marker": "circle", "marker_size": 5}],
        },
        "post": {"anchor": "one_cell", "plot_layout": {"x": 0.12, "y": 0.15, "w": 0.72, "h": 0.62}},
    }


def bar_f1() -> dict:
    methods = ["Isolation Forest", "OCSVM", "LSTM-AE", "USAD", "OmniAnomaly", "Đề xuất"]
    f1 = [0.71, 0.68, 0.79, 0.84, 0.86, 0.89]
    rows = [[m, v] for m, v in zip(methods, f1)]
    return {
        "meta": meta("So sánh F1"),
        "data": {"headers": ["Phương pháp", "F1"], "rows": rows, "widths": {"A:A": 20, "B:B": 10}},
        "chart": {
            "type": "column", "title": "So sánh F1 trên bốn bộ dữ liệu",
            "style": 10, "palette": ["#1F4E79"],
            "position": {"cell": "E2", "width_cm": 14.8, "height_cm": 8.0},
            "categories_column": 0,
            "axes": {
                "x": {"title": "", "label_size": 9, "label_rotation": -20},
                "y": {"title": "F1", "min": 0, "max": 1.0, "major_unit": 0.2,
                      "number_format": "0.00", "gridlines": True, "label_size": 9},
            },
            "legend": {"position": "none", "size": 9},
            "series": [{"name": "F1", "column": 1, "color": "#1F4E79", "gap": 45,
                        "data_labels": {"show": True, "position": "outside_end", "size": 9,
                                        "number_format": "0.00"}}],
        },
        "post": {"anchor": "one_cell", "plot_layout": {"x": 0.10, "y": 0.16, "w": 0.78, "h": 0.58}},
    }


def bar_ablation() -> dict:
    variants = ["AE", "CNN-AE", "CNN-LSTM-AE", "+Attention", "+Mahalanobis", "Đầy đủ + QAT"]
    f1 = [0.78, 0.82, 0.85, 0.87, 0.885, 0.89]
    rows = [[v, f] for v, f in zip(variants, f1)]
    return {
        "meta": meta("Ablation"),
        "data": {"headers": ["Biến thể", "F1"], "rows": rows, "widths": {"A:A": 20, "B:B": 10}},
        "chart": {
            "type": "column", "title": "Đóng góp của từng thành phần",
            "style": 10, "palette": ["#2E75B6"],
            "position": {"cell": "E2", "width_cm": 14.8, "height_cm": 8.0},
            "categories_column": 0,
            "axes": {
                "x": {"title": "", "label_size": 8.5, "label_rotation": -25},
                "y": {"title": "F1", "min": 0.70, "max": 0.92, "major_unit": 0.04,
                      "number_format": "0.00", "gridlines": True, "label_size": 9},
            },
            "legend": {"position": "none", "size": 9},
            "series": [{"name": "F1", "column": 1, "color": "#2E75B6", "gap": 45,
                        "data_labels": {"show": True, "position": "outside_end", "size": 8.5,
                                        "number_format": "0.000"}}],
        },
        "post": {"anchor": "one_cell", "plot_layout": {"x": 0.10, "y": 0.16, "w": 0.78, "h": 0.58}},
    }


def bar_latency() -> dict:
    rows = [
        ["TinyAE (12K)", 9.2],
        ["CNN-AE (28K)", 12.4],
        ["LSTM-AE (41K)", 15.1],
        ["Đề xuất float32 (36K)", 18.4],
        ["Đề xuất int8 (36K)", 11.7],
    ]
    return {
        "meta": meta("Độ trễ suy luận"),
        "data": {"headers": ["Mô hình", "Độ trễ (ms)"], "rows": rows,
                 "widths": {"A:A": 24, "B:B": 14}},
        "chart": {
            "type": "column", "title": "Độ trễ suy luận trên STM32H747",
            "style": 10, "palette": ["#C55A11"],
            "position": {"cell": "E2", "width_cm": 14.8, "height_cm": 8.0},
            "categories_column": 0,
            "axes": {
                "x": {"title": "", "label_size": 8.5, "label_rotation": -22},
                "y": {"title": "Latency (ms)", "min": 0, "max": 22, "major_unit": 4,
                      "number_format": "0.0", "gridlines": True, "label_size": 9},
            },
            "legend": {"position": "none", "size": 9},
            "series": [{"name": "Độ trễ", "column": 1, "color": "#C55A11", "gap": 50,
                        "data_labels": {"show": True, "position": "outside_end", "size": 8.5,
                                        "number_format": "0.0"}}],
        },
        "post": {"anchor": "one_cell", "plot_layout": {"x": 0.10, "y": 0.16, "w": 0.78, "h": 0.58}},
    }


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    for name, spec in [
        ("training", line_training()),
        ("pr", scatter_pr()),
        ("f1", bar_f1()),
        ("ablation", bar_ablation()),
        ("latency", bar_latency()),
    ]:
        print(write(name, spec))


if __name__ == "__main__":
    main()
