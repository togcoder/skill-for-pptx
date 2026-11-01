"""Advanced Sheet Forge tests: image table, Gantt, matrix, dashboard, VBA.

EXPERIMENTAL — T043 [xlsx].  These tests inspect the OOXML package, not a
running Excel; the Excel COM open/render is recorded in the task report.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.chart_patch import _sheet_drawing_index
from scripts.sheet_forge import build_dashboard
from scripts.vba_forge import MODULE, write_dashboard_module

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:  # pragma: no cover
    HAVE_PIL = False


def _avatar(path: Path) -> Path:
    if HAVE_PIL:
        Image.new("RGB", (96, 96), "#1F4E79").save(path)
    else:  # 1×1 PNG fallback
        path.write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="))
    return path


def _spec(tmp: Path) -> Path:
    photo = _avatar(tmp / "avatar.png")
    rows = []
    for i in range(8):
        rows.append([f"T{i + 1:03d}", ["Dữ liệu", "Nền tảng"][i % 2], "Lan",
                     "2026-01-05", "2026-01-20", 10 + i, 0.25 + i * 0.05,
                     100 + i * 10, 150 + i * 12,
                     ["On track", "At risk"][i % 2], "High"])
    spec = {
        "title": "Mini dashboard",
        "subtitle": "8 tasks",
        "workstreams": ["Dữ liệu", "Nền tảng"],
        "data_last_row": 9,
        "data": {"headers": ["Task ID", "Workstream", "Owner", "Start", "End", "Days",
                             "Progress", "Cost", "Benefit", "Status", "Priority"],
                 "rows": rows, "print_area": "A1:K9",
                 "formats": {"Progress": "0%"}},
        "tasks": [
            {"name": "Khảo sát", "start": "2026-01-05", "days": 12, "progress": 0.3},
            {"name": "Chuẩn hoá", "start": "2026-01-20", "days": 18, "progress": 0.5},
            {"name": "Kiểm thử", "start": "2026-02-10", "days": 9, "progress": 0.7},
        ],
        "team": [{"name": "Lan Nguyễn", "role": "Lead", "focus": "Lộ trình",
                  "photo": str(photo), "alt": "Ảnh Lan"}],
        "nodes": [{"name": "Data", "x": 1, "y": 8, "group": "Core"},
                  {"name": "Platform", "x": 5, "y": 9, "group": "Core"},
                  {"name": "People", "x": 3, "y": 4, "group": "Enable"}],
        "edges": [{"name": "Data→Platform", "from": "Data", "to": "Platform",
                   "x1": 1, "y1": 8, "x2": 5, "y2": 9, "weight": 3},
                  {"name": "Data→People", "from": "Data", "to": "People",
                   "x1": 1, "y1": 8, "x2": 3, "y2": 4, "weight": 2}],
        "kpis": [{"label": "Tasks", "value": "8", "delta": "+2", "fill": "#EAF1F8"}],
        "pivot_source": "Data!A1:K9",
        "pivot_rows": ["Workstream"],
        "pivot_values": [{"field": "Cost", "func": "sum"}],
    }
    path = tmp / "spec.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class SheetForgeAdvancedTests(unittest.TestCase):
    def test_workbook_package_has_the_advanced_features(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "mini.xlsx"
            report = build_dashboard(_spec(tmp), out, pivot=False)
            self.assertTrue(report["ok"], report["audit"])
            self.assertTrue(out.is_file())
            with zipfile.ZipFile(out) as zf:
                names = set(zf.namelist())
                book = zf.read("xl/workbook.xml").decode("utf-8")
                for sheet in ("Data", "Model", "Team", "Gantt", "Relations", "Dashboard"):
                    self.assertIn(f'name="{sheet}"', book)
                model = zf.read("xl/worksheets/sheet2.xml").decode("utf-8")
                self.assertIn("SUMIF(", model)
                self.assertIn("COUNTIF(", model)
                self.assertIn("AVERAGEIF(", model)
                self.assertIn("INDEX(", model)
                styles = zf.read("xl/styles.xml").decode("utf-8")
                self.assertIn('formatCode="0%"', styles)
                charts = [n for n in names if n.startswith("xl/charts/chart")]
                self.assertEqual(len(charts), 3)  # Gantt sheet + dashboard Gantt + cost
                blunt = "".join(zf.read(n).decode("utf-8") for n in charts)
                self.assertIn("barChart", blunt)
                self.assertIn("dateAx", blunt)

    def test_image_table_and_matrix_are_native(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "mini.xlsx"
            report = build_dashboard(_spec(tmp), out, pivot=False)
            self.assertTrue(report["ok"], report["audit"])
            with zipfile.ZipFile(out) as zf:
                members = {n: zf.read(n) for n in zf.namelist()}
                pics = sum(blob.count(b"<xdr:pic>") for name, blob in members.items()
                           if name.startswith("xl/drawings/drawing"))
                self.assertEqual(pics, 1)  # one team photo
                image_rels = [name for name, blob in members.items()
                              if name.endswith(".rels") and b"/image" in blob]
                self.assertTrue(image_rels)
                cfgs = [name for name, blob in members.items()
                        if name.startswith("xl/worksheets/sheet") and
                        b"colorScale" in blob]
                self.assertTrue(cfgs, "relationship matrix needs a colour scale")

    def test_dashboard_has_fixed_chart_anchors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "mini.xlsx"
            report = build_dashboard(_spec(tmp), out, pivot=False)
            self.assertTrue(report["ok"], report["audit"])
            with zipfile.ZipFile(out) as zf:
                members = {n: zf.read(n) for n in zf.namelist()}
                dashboard = zf.read("xl/worksheets/sheet6.xml").decode("utf-8")
                self.assertIn("mergeCell", dashboard)
                self.assertIn('ref="A2:N3"', dashboard)
                drawing = _sheet_drawing_index(members)["Dashboard"]
                xml = zf.read(f"xl/drawings/drawing{drawing}.xml").decode("utf-8")
                self.assertEqual(xml.count("<xdr:oneCellAnchor>"), 2)
                self.assertIn("Gantt chart", xml)
                self.assertIn("Cost and benefit chart", xml)

    def test_vba_module_is_a_labelled_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "dash.bas"
            write_dashboard_module(path)
            text = path.read_text(encoding="utf-8")
            self.assertIn('Attribute VB_Name = "DashboardTools"', text)
            self.assertIn("Sub RefreshDashboard()", text)
            self.assertIn("Sub FilterAtRisk()", text)
            self.assertIn("Option Explicit", text)
            self.assertEqual(text, MODULE)


if __name__ == "__main__":
    unittest.main()
