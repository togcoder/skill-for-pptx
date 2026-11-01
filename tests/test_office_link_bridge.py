import io
import os
from pathlib import Path
import tempfile
import unittest
import zipfile

from lxml import etree as ET
import openpyxl

from scripts.office_link_bridge import (
    parse_formula_range,
    read_excel_range_values,
    inspect_office_charts,
    link_chart_to_external_excel,
    embed_sheetcraft_workbook,
    sync_office_chart_data,
    refresh_presentation_links_com,
)


class TestOfficeLinkBridge(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir = Path(self.temp_dir.name)
        self.sample_pptx = Path(__file__).resolve().parents[1] / "build" / "forge" / "coffee_report.pptx"

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_sample_excel(self) -> Path:
        xl_path = self.dir / "sample_model.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Financials"
        ws["A1"] = "Period"
        ws["B1"] = "2025"
        ws["C1"] = "2026"

        ws["A2"] = "Jul"
        ws["B2"] = 400
        ws["C2"] = 550

        ws["A3"] = "Aug"
        ws["B3"] = 450
        ws["C3"] = 620

        ws["A4"] = "Sep"
        ws["B4"] = 500
        ws["C4"] = 710

        # Add a second sheet to verify multi-sheet preservation
        ws2 = wb.create_sheet(title="Formulas")
        ws2["A1"] = "Growth"
        ws2["B1"] = "=(Financials!C4-Financials!B4)/Financials!B4"

        wb.save(xl_path)
        return xl_path

    def test_parse_formula_range(self):
        sheet, start, end = parse_formula_range("Sheet1!$B$2:$B$4")
        self.assertEqual(sheet, "Sheet1")
        self.assertEqual(start, "$B$2")
        self.assertEqual(end, "$B$4")

        sheet, start, end = parse_formula_range("'Financials Summary'!A1")
        self.assertEqual(sheet, "Financials Summary")
        self.assertEqual(start, "A1")
        self.assertIsNone(end)

        sheet, start, end = parse_formula_range("[model.xlsx]Data!$C$5:$C$10")
        self.assertEqual(sheet, "Data")
        self.assertEqual(start, "$C$5")
        self.assertEqual(end, "$C$10")

    def test_read_excel_range_values(self):
        xl_path = self._create_sample_excel()
        vals = read_excel_range_values(xl_path, "Financials", "B2", "B4")
        self.assertEqual(vals, [400, 450, 500])

        single = read_excel_range_values(xl_path, "Financials", "A1")
        self.assertEqual(single, ["Period"])

    def test_inspect_office_charts(self):
        if not self.sample_pptx.exists():
            self.skipTest(f"{self.sample_pptx} does not exist")
        res = inspect_office_charts(self.sample_pptx)
        self.assertEqual(res["document_type"], "pptx")
        self.assertGreaterEqual(res["total_charts"], 1)
        chart0 = res["charts"][0]
        self.assertEqual(chart0["link_mode"], "embedded")
        self.assertEqual(chart0["series_count"], 2)

    def test_link_chart_to_external_excel(self):
        if not self.sample_pptx.exists():
            self.skipTest(f"{self.sample_pptx} does not exist")
        xl_path = self._create_sample_excel()
        out_pptx = self.dir / "linked_output.pptx"

        res = link_chart_to_external_excel(
            self.sample_pptx,
            xl_path,
            chart_index=0,
            output_path=out_pptx,
            sheet_name="Financials",
            auto_update=True,
        )
        self.assertTrue(res["ok"])
        self.assertEqual(res["mode"], "linked_external")
        self.assertTrue(out_pptx.exists())

        # Inspect modified file
        inspect_res = inspect_office_charts(out_pptx)
        c0 = inspect_res["charts"][0]
        self.assertEqual(c0["link_mode"], "linked_external")
        self.assertEqual(c0["auto_update"], "1")
        self.assertTrue(c0["relationship"]["target"].startswith("file:///"))
        self.assertEqual(c0["relationship"]["target_mode"], "External")

    def test_embed_sheetcraft_workbook(self):
        if not self.sample_pptx.exists():
            self.skipTest(f"{self.sample_pptx} does not exist")
        xl_path = self._create_sample_excel()
        out_pptx = self.dir / "embedded_output.pptx"

        res = embed_sheetcraft_workbook(
            self.sample_pptx,
            xl_path,
            chart_index=0,
            output_path=out_pptx,
            sheet_name="Financials",
        )
        self.assertTrue(res["ok"])
        self.assertEqual(res["mode"], "embedded_connected")
        self.assertIn("Financials", res["workbook_sheets"])
        self.assertIn("Formulas", res["workbook_sheets"])

        # Check embedded part inside zip
        with zipfile.ZipFile(out_pptx, "r") as z:
            emb_bytes = z.read(res["embedded_part"])
            wb = openpyxl.load_workbook(io.BytesIO(emb_bytes))
            self.assertEqual(wb.sheetnames, ["Financials", "Formulas"])
            self.assertEqual(wb["Formulas"]["A1"].value, "Growth")

    def test_sync_chart_data(self):
        if not self.sample_pptx.exists():
            self.skipTest(f"{self.sample_pptx} does not exist")
        xl_path = self._create_sample_excel()
        linked_pptx = self.dir / "linked_for_sync.pptx"

        # 1. Create linked deck
        link_chart_to_external_excel(
            self.sample_pptx,
            xl_path,
            chart_index=0,
            output_path=linked_pptx,
            sheet_name="Financials",
        )

        # 2. Modify Excel values
        wb = openpyxl.load_workbook(xl_path)
        ws = wb["Financials"]
        ws["B2"] = 999
        ws["B3"] = 888
        ws["B4"] = 777
        wb.save(xl_path)

        # 3. Run sync
        synced_pptx = self.dir / "synced_output.pptx"
        sync_res = sync_office_chart_data(linked_pptx, excel_path=xl_path, output_path=synced_pptx)
        self.assertTrue(sync_res["ok"])

        # 4. Verify updated values inside chart cache
        inspect_res = inspect_office_charts(synced_pptx)
        c0 = inspect_res["charts"][0]
        # Series 0 (2025) should now have values [999, 888, 777]
        self.assertEqual(c0["series"][0]["values"], [999, 888, 777])


if __name__ == "__main__":
    unittest.main()
