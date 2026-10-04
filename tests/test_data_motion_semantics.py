import io
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from inspect_existing_deck import _chart_summary, _standalone_number_candidate
from data_motion_recipes import chart_motion_recipe, number_counter_recipe


class DataMotionSemanticTests(unittest.TestCase):
    def test_standalone_number_candidate_preserves_format(self):
        parsed=_standalone_number_candidate("$12,345.6%")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["numeric_value"],12345.6)
        self.assertEqual(parsed["prefix"],"$")
        self.assertEqual(parsed["suffix"],"%")

    def test_number_candidate_rejects_sentence_or_label(self):
        self.assertIsNone(_standalone_number_candidate("OEE 95%"))
        self.assertIsNone(_standalone_number_candidate("Target: 95"))

    def test_number_counter_recipe_uses_source_format(self):
        parsed=_standalone_number_candidate("98.5%")
        recipe=number_counter_recipe(parsed)
        self.assertEqual(recipe["semantic_kind"],"number-counter")
        self.assertEqual(recipe["recipe"],"count-up")
        self.assertEqual(recipe["to_value"],98.5)
        self.assertEqual(recipe["decimal_places"],1)
        self.assertEqual(recipe["suffix"],"%")
        self.assertTrue(recipe["requires_narrative_highlight"])

    def test_chart_summary_reads_column_chart(self):
        xml=b"""<?xml version="1.0" encoding="UTF-8"?>
<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
  <c:chart><c:plotArea><c:barChart>
    <c:barDir val="col"/><c:grouping val="clustered"/>
    <c:ser><c:cat><c:strRef><c:strCache>
      <c:pt idx="0"><c:v>A</c:v></c:pt><c:pt idx="1"><c:v>B</c:v></c:pt>
    </c:strCache></c:strRef></c:cat>
    <c:val><c:numRef><c:numCache>
      <c:pt idx="0"><c:v>10</c:v></c:pt><c:pt idx="1"><c:v>20</c:v></c:pt>
    </c:numCache></c:numRef></c:val></c:ser>
  </c:barChart></c:plotArea></c:chart>
</c:chartSpace>"""
        buf=io.BytesIO()
        with ZipFile(buf,"w") as z:
            z.writestr("ppt/charts/chart1.xml",xml)
        buf.seek(0)
        with ZipFile(buf) as z:
            summary=_chart_summary(z,"ppt/charts/chart1.xml")
        self.assertEqual(summary["primary_type"],"column")
        self.assertEqual(summary["series_count"],1)
        self.assertEqual(summary["category_count"],2)
        self.assertEqual(summary["point_count"],2)
        recipe=chart_motion_recipe(summary)
        self.assertEqual(recipe["recipe"],"baseline-grow")
        self.assertEqual(recipe["preferred_build"],"category-elements")
        self.assertFalse(recipe["animate_background"])

    def test_chart_recipe_differs_by_chart_semantics(self):
        line=chart_motion_recipe({"primary_type":"line","series_count":1})
        pie=chart_motion_recipe({"primary_type":"pie","series_count":1})
        scatter=chart_motion_recipe({"primary_type":"scatter","series_count":1})
        self.assertEqual(line["recipe"],"series-trace")
        self.assertEqual(pie["recipe"],"segment-sweep")
        self.assertEqual(scatter["recipe"],"point-build")
        self.assertEqual(pie["preferred_build"],"category-elements")
        self.assertEqual(scatter["preferred_build"],"series-elements")

    def test_unknown_chart_is_conservative(self):
        recipe=chart_motion_recipe({"primary_type":"waterfall","series_count":1})
        self.assertEqual(recipe["recipe"],"semantic-build")
        self.assertEqual(recipe["preferred_build"],"as-whole")


if __name__=="__main__":
    unittest.main()
