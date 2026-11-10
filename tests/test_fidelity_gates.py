from pptx import Presentation
from pptx.util import Inches
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from PIL import Image
import sys, os, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import pptx_tools as tools


def _deck(path, rich=False):
    prs = Presentation()
    s = prs.slides.add_slide(prs.slide_layouts[5])
    if rich:
        img = os.path.join(tempfile.gettempdir(), "gate_source.png")
        Image.new("RGB", (40, 40), (10, 100, 200)).save(img)
        s.shapes.add_picture(img, Inches(1), Inches(1), Inches(1), Inches(1))
        s.shapes.add_table(2, 2, Inches(3), Inches(1), Inches(3), Inches(1))
        data = CategoryChartData()
        data.categories = ["A", "B"]
        data.add_series("S", (1, 2))
        s.shapes.add_chart(XL_CHART_TYPE.PIE, Inches(3), Inches(4), Inches(3), Inches(2), data)
    prs.save(path)


class FidelityGates(unittest.TestCase):
    def test_decimal_number_is_not_forced_to_thousands(self):
        a, b = tempfile.mktemp(suffix=".pptx"), tempfile.mktemp(suffix=".pptx")
        _deck(a)
        _deck(b)
        prs = Presentation(a)
        prs.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(3), Inches(1)).text_frame.text = "814.332"
        prs.save(a)
        prs = Presentation(b)
        prs.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(3), Inches(1)).text_frame.text = "814.332"
        prs.save(b)
        self.assertEqual(tools.missing_numbers(a, b), {})

    def test_rebuild_still_has_to_carry_source_pictures_charts_tables(self):
        a, b = tempfile.mktemp(suffix=".pptx"), tempfile.mktemp(suffix=".pptx")
        _deck(a, rich=True)
        _deck(b)
        gates, passed, _ = tools.check(a, b, {"1": {"old": [1], "group": "rebuild"}})
        failed = {name for ok, name, _ in gates if not ok}
        self.assertIn("source pictures on their slide", failed)
        self.assertIn("tables kept", failed)
        self.assertIn("charts kept", failed)


    def test_grouped_numbers_are_not_reported_lost_when_formatting_changes(self):
        src, same, less = (tempfile.mktemp(suffix=".pptx") for _ in range(3))
        _deck(src)
        prs = Presentation(src)
        box = prs.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(1))
        box.text_frame.text = "156.179 814.332"
        prs.save(src)
        _deck(same)
        prs = Presentation(same)
        box = prs.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(1))
        box.text_frame.text = "156179 814,332"      # same values, other separators
        prs.save(same)
        _deck(less)
        prs = Presentation(less)
        box = prs.slides[0].shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(1))
        box.text_frame.text = "156179"               # 814.332 is really gone
        prs.save(less)
        self.assertEqual(tools.missing_numbers(src, same), {})
        gone = [n for nums in tools.missing_numbers(src, less).values() for n in nums]
        self.assertEqual(gone, ["814.332"])


    def test_chart_data_is_compared_not_only_chart_type(self):
        from pptx.chart.data import CategoryChartData
        from pptx.enum.chart import XL_CHART_TYPE
        src, same, different = (tempfile.mktemp(suffix=".pptx") for _ in range(3))
        _deck(src, rich=True)
        _deck(same, rich=True)
        _deck(different, rich=True)
        prs = Presentation(src)
        prs.save(src)
        prs = Presentation(different)
        chart = next(sh for sh in prs.slides[0].shapes if getattr(sh, "has_chart", False))
        data = CategoryChartData()
        data.categories = ["A", "B"]
        data.add_series("S", (1, 99))          # invented value, same chart kind
        chart.chart.replace_data(data)
        prs.save(different)
        mapping = {"1": {"old": [1], "group": "reskin"}}
        failed = {name for ok, name, _ in tools.check(src, different, mapping)[0] if not ok}
        self.assertIn("chart data kept", failed)
        self.assertNotIn("charts kept", failed)      # type survived; values did not
        failed = {name for ok, name, _ in tools.check(src, same, mapping)[0] if not ok}
        self.assertNotIn("chart data kept", failed)


if __name__ == "__main__":
    unittest.main()
