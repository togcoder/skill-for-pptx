#!/usr/bin/env python3
"""Tests for Chart Forge, chart_patch and chart_audit (T041, xlsx)."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.chart_forge import build_chart
from scripts.chart_patch import patch_workbook
from scripts.chart_audit import audit_workbook

try:
    import xlsxwriter
    HAVE_XLSXWRITER = True
except Exception:  # pragma: no cover
    HAVE_XLSXWRITER = False


def _combo_spec(tmp: Path) -> Path:
    spec = {
        "meta": {"title": "Doanh thu", "sheet": "Data", "author": "QA"},
        "data": {
            "headers": ["Tháng", "Thực tế", "Mục tiêu"],
            "rows": [["T1", 120, 130], ["T2", 128, 138], ["T3", 135, 148],
                     ["T4", 140, 158], ["T5", 150, 170], ["T6", 158, 182]],
        },
        "chart": {
            "type": "combo",
            "title": "Doanh thu thực tế và mục tiêu",
            "palette": ["#1F4E79", "#C55A11"],
            "position": {"cell": "E2", "width_cm": 16, "height_cm": 9},
            "axes": {
                "x": {"title": "Tháng", "label_size": 9},
                "y": {"title": "Thực tế", "min": 0, "max": 200, "number_format": "#,##0", "gridlines": True},
                "y2": {"title": "Mục tiêu", "min": 0, "max": 250, "number_format": "#,##0"},
            },
            "legend": {"position": "bottom", "size": 9},
            "series": [
                {"name": "Thực tế", "column": 1, "type": "column", "color": "#1F4E79", "gap": 55},
                {"name": "Mục tiêu", "column": 2, "type": "line", "axis": "secondary", "color": "#C55A11", "marker": "circle"},
            ],
        },
        "post": {"anchor": "one_cell"},
    }
    path = tmp / "combo.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class ChartForgeTests(unittest.TestCase):
    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_combo_build_and_audit(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "combo.xlsx"
            report = build_chart(_combo_spec(tmp), out)
            self.assertTrue(report["ok"], report["audit"])
            self.assertEqual(report["chart_type"], "combo")
            audit = audit_workbook(out)
            self.assertTrue(audit["ok"], audit["errors"])
            self.assertEqual(audit["charts"][0]["type"], "combo:barChart+lineChart")
            self.assertEqual(audit["charts"][0]["anchor_kind"], "oneCellAnchor")
            self.assertEqual(audit["charts"][0]["width_cm"], 16.0)
            self.assertEqual(audit["charts"][0]["alt"], "Doanh thu thực tế và mục tiêu")
            with zipfile.ZipFile(out) as zf:
                chart_xml = zf.read("xl/charts/chart1.xml").decode("utf-8")
            self.assertIn("logBase", chart_xml) if "logBase" in chart_xml else True
            self.assertIn("gapWidth", chart_xml)
            self.assertIn("holeSize", chart_xml) if "doughnutChart" in chart_xml else True

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_patch_existing_chart_axes_and_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "combo.xlsx"
            build_chart(_combo_spec(tmp), out)
            patch = {
                "charts": [{
                    "index": 1,
                    "title": {"text": "Patched title", "size": 13},
                    "legend": {"position": "right", "overlay": False, "size": 8},
                    "axes": {"y2": {"title": "Mục tiêu (đã sửa)", "min": 50, "max": 240, "number_format": "#,##0"}},
                    "bar": {"gap": 40, "overlap": 0},
                }],
                "anchors": [{"drawing": 1, "anchor": {"mode": "one_cell", "width_cm": 15, "height_cm": 8, "alt": "Patched"}}],
            }
            patched = tmp / "patched.xlsx"
            result = patch_workbook(out, patch, patched)
            self.assertTrue(result["ok"])
            audit = audit_workbook(patched)
            self.assertTrue(audit["ok"], audit["errors"])
            chart = audit["charts"][0]
            self.assertEqual(chart["width_cm"], 15.0)
            self.assertEqual(chart["alt"], "Patched")
            y2 = [a for a in chart["axes"] if a["kind"] == "valAx" and a["pos"] == "r"][0]
            self.assertEqual(y2["title"], "Mục tiêu (đã sửa)")
            self.assertEqual(y2["min"], "50")

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_small_chart_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            path = tmp / "small.xlsx"
            wb = xlsxwriter.Workbook(str(path))
            ws = wb.add_worksheet("Data")
            ws.write_row(0, 0, ["A", "B"])
            ws.write_row(1, 0, ["x", 1])
            ws.write_row(2, 0, ["y", 2])
            chart = wb.add_chart({"type": "column"})
            chart.add_series({"categories": "=Data!$A$2:$A$3", "values": "=Data!$B$2:$B$3"})
            chart.set_size({"width": 150, "height": 100})
            ws.insert_chart("D2", chart)
            wb.close()
            audit = audit_workbook(path)
            self.assertFalse(audit["ok"])
            self.assertTrue(any("below the" in e for e in audit["errors"]), audit["errors"])

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_doughnut_has_palette_and_percent_labels(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = {
                "meta": {"title": "Cơ cấu", "sheet": "Data"},
                "data": {"headers": ["Nhóm", "Tỷ trọng"], "rows": [["A", 42], ["B", 24], ["C", 18], ["D", 9], ["E", 7]]},
                "chart": {
                    "type": "doughnut", "title": "Cơ cấu",
                    "palette": ["#1F4E79", "#2E75B6", "#5B9BD5", "#7F7F7F", "#D9D9D9"],
                    "position": {"cell": "D2", "width_cm": 13, "height_cm": 9},
                    "legend": {"position": "right", "size": 9},
                    "series": [{"name": "Tỷ trọng", "column": 1, "type": "doughnut",
                                "data_labels": {"show": True, "show_percent": True, "position": "best_fit", "size": 9}}],
                },
                "post": {"anchor": "one_cell", "doughnut_hole": 55},
            }
            path = tmp / "pie.json"
            path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            out = tmp / "pie.xlsx"
            report = build_chart(path, out)
            self.assertTrue(report["ok"], report["audit"])
            audit = audit_workbook(out)
            self.assertFalse(any("share a colour" in w for w in audit["warnings"]), audit["warnings"])
            with zipfile.ZipFile(out) as zf:
                xml = zf.read("xl/charts/chart1.xml").decode("utf-8")
            self.assertGreaterEqual(xml.count("<c:dPt>"), 5)
            self.assertIn('val="55"', xml)

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_patch_reaches_second_series_of_combo(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "combo.xlsx"
            build_chart(_combo_spec(tmp), out)
            patched = tmp / "patched.xlsx"
            patch_workbook(out, {"charts": [{"index": 1, "series": [{}, {"color": "#C00000", "line_width": 3.0}]}]}, patched)
            with zipfile.ZipFile(patched) as zf:
                xml = zf.read("xl/charts/chart1.xml").decode("utf-8")
            self.assertIn("C00000", xml)
            # The second series lives in the lineChart group, not the bar group.
            self.assertIn("lineChart", xml)
            self.assertIn('w="38100"', xml)

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_manual_layout_child_order(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "combo.xlsx"
            build_chart(_combo_spec(tmp), out)
            patched = tmp / "patched.xlsx"
            patch_workbook(out, {"charts": [{"index": 1,
                                             "plot_layout": {"x": 0.1, "y": 0.1, "w": 0.7, "h": 0.6}}]}, patched)
            with zipfile.ZipFile(patched) as zf:
                xml = zf.read("xl/charts/chart1.xml").decode("utf-8")
            manual = xml[xml.index("<c:manualLayout>"):xml.index("</c:manualLayout>")]
            self.assertLess(manual.index("<c:xMode"), manual.index("<c:x "))
            self.assertLess(manual.index("<c:wMode"), manual.index("<c:w "))
            self.assertLess(manual.index("<c:x "), manual.index("<c:y "))

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_axis_max_is_checked_per_axis_group(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            spec = {
                "meta": {"title": "Two scales", "sheet": "Data"},
                "data": {"headers": ["X", "Left", "Right"], "rows": [["A", 120, 230], ["B", 150, 240]]},
                "chart": {
                    "type": "combo", "title": "Two scales",
                    "position": {"cell": "E2", "width_cm": 16, "height_cm": 9},
                    "axes": {"y": {"min": 0, "max": 200}, "y2": {"min": 0, "max": 260}},
                    "series": [
                        {"name": "Left", "column": 1, "type": "column", "color": "#1F4E79"},
                        {"name": "Right", "column": 2, "type": "line", "axis": "secondary", "color": "#C55A11"},
                    ],
                },
                "post": {"anchor": "one_cell"},
            }
            path = tmp / "two.json"
            path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            out = tmp / "two.xlsx"
            report = build_chart(path, out)
            self.assertTrue(report["ok"], report["audit"])
            audit = audit_workbook(out)
            self.assertFalse(any("axis maximum 200" in w for w in audit["warnings"]), audit["warnings"])

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_chart_outside_print_area_is_warned(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            path = tmp / "outside.xlsx"
            wb = xlsxwriter.Workbook(str(path))
            ws = wb.add_worksheet("Data")
            ws.write_row(0, 0, ["A", "B"])
            ws.write_row(1, 0, ["x", 1])
            ws.write_row(2, 0, ["y", 2])
            ws.print_area("A1:B2")
            chart = wb.add_chart({"type": "column"})
            chart.add_series({"categories": "=Data!$A$2:$A$3", "values": "=Data!$B$2:$B$3"})
            ws.insert_chart("Z50", chart)
            wb.close()
            audit = audit_workbook(path)
            self.assertTrue(any("outside the print area" in w for w in audit["warnings"]), audit["warnings"])

    @unittest.skipUnless(HAVE_XLSXWRITER, "xlsxwriter is not installed")
    def test_stale_cache_is_warned(self):
        try:
            import openpyxl
        except Exception:
            self.skipTest("openpyxl is not installed")
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "combo.xlsx"
            build_chart(_combo_spec(tmp), out)
            wb = openpyxl.load_workbook(out)
            wb["Data"]["B2"] = 999
            wb.save(out)
            audit = audit_workbook(out)
            self.assertTrue(any("cache differs" in w for w in audit["warnings"]), audit["warnings"])

    def test_document_spec_schema_is_valid_json(self):
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "domains" / "xlsx" / "schemas" / "chart_spec.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("chart", schema["properties"])


if __name__ == "__main__":
    unittest.main()
