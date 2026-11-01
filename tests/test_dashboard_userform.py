"""T050 tests: dashboard composition and VBA UserForm contract."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.dashboard_forge import audit_dashboard, build_dashboard
from scripts.userform_forge import FORM_CODE, MODULE_CODE, _rgb


def _spec(tmp: Path) -> Path:
    rows = []
    for i in range(8):
        rows.append([f"T{i+1:03d}", ["Dữ liệu", "Nền tảng"][i % 2], "Lan",
                     "2026-01-05", "2026-01-20", 10 + i, 0.25,
                     100 + i * 10, 150 + i * 12,
                     ["On track", "At risk"][i % 2], "High"])
    spec = {
        "title": "Dashboard mini",
        "subtitle": "4 chart · 12 column grid",
        "data": {"headers": ["Task ID", "Workstream", "Owner", "Start", "End", "Days",
                             "Progress", "Cost", "Benefit", "Status", "Priority"],
                 "rows": rows},
        "trend": [[f"T{m}", 100 + m * 5, 150 + m * 6] for m in range(1, 7)],
        "model": [{"name": "Dữ liệu", "cost": 120, "benefit": 200, "tasks": 4},
                  {"name": "Nền tảng", "cost": 80, "benefit": 140, "tasks": 4}],
        "status_counts": [["On track", 4], ["At risk", 4], ["Blocked", 0], ["Done", 0]],
        "kpis": [
            {"label": "Tasks", "value": "8", "delta": "+2", "fill": "#EAF1F8"},
            {"label": "Cost", "value": "1.080", "delta": "budget", "fill": "#EAF4E7"},
            {"label": "Benefit", "value": "1.600", "delta": "ROI", "fill": "#FFF2E5"},
            {"label": "Risk", "value": "4", "delta": "at risk", "fill": "#FCE4D6",
             "positive": False},
        ],
    }
    path = tmp / "dashboard.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class DashboardTests(unittest.TestCase):
    def test_dashboard_has_four_native_charts_and_hidden_data(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "dash.xlsx"
            report = build_dashboard(_spec(tmp), out)
            self.assertTrue(report["ok"], report["audit"])
            self.assertEqual(report["audit"]["stats"]["charts"], 4)
            with zipfile.ZipFile(out) as zf:
                book = zf.read("xl/workbook.xml").decode("utf-8")
                self.assertIn('state="hidden"', book)
                self.assertEqual(book.count("<sheet "), 4)
                vml = [n for n in zf.namelist() if n.endswith(".vml")]
                self.assertTrue(vml)
                text = "\n".join(zf.read(n).decode("utf-8", errors="replace") for n in vml)
                for macro in ("FormTools.ShowEntryForm", "FormTools.FilterRisk",
                              "FormTools.FilterAll"):
                    self.assertIn(macro, text)

    def test_userform_code_contract(self):
        for token in ("Private Sub UserForm_Initialize",
                      "Private Sub btnSave_Click", "Private Sub btnClear_Click",
                      "Private Sub btnCancel_Click", "Private Sub ClearForm",
                      "Me.cboWorkstream", "Me.txtStart", "Me.lblStatus",
                      "ThisWorkbook.Worksheets(\"Data\")",
                      "ws.Cells(nextRow, 1).Value = nextId",
                      "CDate(Me.txtStart.Value) + days - 1"):
            self.assertIn(token, FORM_CODE)
        for token in ("Public Sub ShowEntryForm", "frmEntry.Show",
                      "Public Sub FilterRisk", "Public Sub FilterAll"):
            self.assertIn(token, MODULE_CODE)
        self.assertEqual(_rgb("#1F4E79"), 0x794E1F)

    def test_audit_catches_missing_hidden_state(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            out = tmp / "dash.xlsx"
            build_dashboard(_spec(tmp), out)
            # The audit is structural; a normal build is clean.
            self.assertTrue(audit_dashboard(out)["ok"])


if __name__ == "__main__":
    unittest.main()
