"""T048 workbook UX tests: hidden sheets, form, validation, colours, VBA."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.sheet_forge import build_dashboard
from scripts.vba_forge import MODULE


def _spec(tmp: Path) -> Path:
    rows = []
    for i in range(8):
        rows.append([f"T{i + 1:03d}", ["Dữ liệu", "Nền tảng"][i % 2], "Lan",
                     "2026-01-05", "2026-01-20", 10 + i, 0.25,
                     100 + i * 10, 150 + i * 12,
                     ["On track", "At risk"][i % 2], "High"])
    spec = {
        "title": "UX mini", "subtitle": "hidden data", "workstreams": ["Dữ liệu", "Nền tảng"],
        "data_last_row": 12,
        "data": {"headers": ["Task ID", "Workstream", "Owner", "Start", "End", "Days",
                             "Progress", "Cost", "Benefit", "Status", "Priority"],
                 "rows": rows, "formats": {"Progress": "0%"}},
        "tasks": [{"name": "A", "start": "2026-01-05", "days": 10},
                  {"name": "B", "start": "2026-01-20", "days": 12}],
        "team": [{"name": "Lan", "role": "Lead", "focus": "Data", "photo": ""},
                 {"name": "Minh", "role": "Data", "focus": "Model", "photo": ""}],
        "nodes": [{"name": "Data", "x": 1, "y": 2, "group": "Core"},
                  {"name": "Platform", "x": 2, "y": 3, "group": "Core"}],
        "edges": [{"name": "D→P", "from": "Data", "to": "Platform",
                   "x1": 1, "y1": 2, "x2": 2, "y2": 3, "weight": 2}],
        "kpis": [{"label": "Tasks", "formula": "=TaskCount", "cached": 8, "format": "0",
                  "delta": "+2", "fill": "#EAF1F8"}],
        "pivot_source": "Data!A1:K12", "pivot_rows": ["Workstream"],
        "pivot_values": [{"field": "Cost", "func": "sum"}],
        "ux": {"input_form": True, "sheets": {
            "Data": {"hidden": True, "tab_color": "7F7F7F"},
            "Pivot": {"very_hidden": True},
            "Lookups": {"very_hidden": True},
            "Dashboard": {"tab_color": "1F4E79", "protect": True},
            "Input": {"tab_color": "C55A11"},
        }},
    }
    path = tmp / "ux.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class WorkbookUxTests(unittest.TestCase):
    def test_hidden_colours_form_validation_protection_buttons(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "ux.xlsx"
            report = build_dashboard(_spec(tmp), out, pivot=False)
            self.assertTrue(report["ok"], report["audit"])
            ux = report["ux"]
            self.assertEqual(ux["hidden"], ["Data"])
            self.assertEqual(ux["very_hidden"], ["Pivot", "Lookups"])
            self.assertEqual(ux["active_tab"], 8)
            self.assertEqual(ux["first_sheet"], 5)
            self.assertIn("Input", ux["protected"])
            self.assertIn("Dashboard", ux["protected"])
            self.assertEqual(ux["validations"], 8)
            self.assertGreaterEqual(ux["merged_ranges"], 18)
            self.assertEqual(len(ux["buttons"]), 3)
            self.assertTrue(all("DashboardTools." in b for b in ux["buttons"]))
            with zipfile.ZipFile(out) as zf:
                input_xml = zf.read("xl/worksheets/sheet9.xml").decode("utf-8")
                self.assertIn("<sheetProtection", input_xml)
                self.assertIn('rgb="FFC55A11"', input_xml)
                self.assertIn("<mergeCell", input_xml)
                self.assertGreaterEqual(input_xml.count("<dataValidation "), 6)
                book = zf.read("xl/workbook.xml").decode("utf-8")
                self.assertIn('firstSheet="5"', book)
                self.assertIn('activeTab="8"', book)
                model = zf.read("xl/worksheets/sheet2.xml").decode("utf-8")
                self.assertIn("$A$12", model)  # data_last_row, not hard-coded 61

    def test_vba_contract_and_form_addresses(self):
        text = MODULE
        for token in ("Public Sub AddRecord()", "Public Sub ClearForm()",
                      "Public Sub RefreshDashboard()", "Private Sub SetStatus",
                      "WorksheetExists", "Option Explicit", "Unprotect",
                      "wsData.Cells(nextRow, 1).Value = nextId",
                      "CDate(startDate) + CLng(days) - 1", 'Range("B20")'):
            self.assertIn(token, text)
        for cell in ('"C6"', '"F6"', '"C7"', '"F7"', '"C8"', '"F8"', '"C9"', '"F9"'):
            self.assertIn(cell, text)


if __name__ == "__main__":
    unittest.main()
