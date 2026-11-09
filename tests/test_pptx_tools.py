"""T087: the guidance skill's toolbox writes clicks and transitions by shape name."""
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pptx_tools as tools  # noqa: E402


def _deck(path):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    for names in (["Title", "Card A", "Card B"], ["!!hero", "Caption"], ["Quote"]):
        slide = prs.slides.add_slide(blank)
        for k, name in enumerate(names):
            box = slide.shapes.add_textbox(Inches(1 + 3 * k), Inches(1), Inches(2.5), Inches(1))
            box.name = name
            box.text_frame.text = name
    prs.save(path)


def _xml(path, n):
    with ZipFile(path) as z:
        return z.read(f"ppt/slides/slide{n}.xml").decode("utf-8")


class MotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / "in.pptx"
        self.out = Path(self.tmp.name) / "out.pptx"
        _deck(self.src)

    def tearDown(self):
        self.tmp.cleanup()

    def test_plan_writes_clicks_morph_and_fade(self):
        plan = {"transitions": {"default": "none", "2": "morph", "3": "fade"},
                "clicks": {"1": [["Card A", "Card B:rise"]], "2": [["Caption"]]}}
        summary = tools.apply_motion(self.src, plan, self.out)
        self.assertEqual(summary["morph"], [2])
        self.assertEqual(summary["fade"], [3])
        self.assertEqual(summary["clicks"], {1: 1, 2: 1})
        s1, s2, s3 = (_xml(self.out, n) for n in (1, 2, 3))
        self.assertIn('presetID="10"', s1)          # fade
        self.assertIn('presetID="42"', s1)          # rise = float-in
        self.assertIn("p159:morph", s2)
        self.assertIn("<p:fade/>", s3)
        self.assertNotIn("p:timing", s3)            # nothing animated on slide 3

    def test_rerun_replaces_transition_instead_of_stacking(self):
        tools.apply_motion(self.src, {"transitions": {"2": "morph"}}, self.out)
        again = Path(self.tmp.name) / "again.pptx"
        tools.apply_motion(self.out, {"transitions": {"2": "fade"}}, again)
        s2 = _xml(again, 2)
        self.assertNotIn("p159:morph", s2)
        self.assertEqual(s2.count("<p:transition"), 1)

    def test_unknown_name_lists_the_real_names(self):
        with self.assertRaises(ValueError) as cm:
            tools.apply_motion(self.src, {"clicks": {"1": [["Subtitle"]]}}, self.out)
        self.assertIn("Card A", str(cm.exception))

    def test_morph_actor_cannot_have_an_entrance(self):
        plan = {"transitions": {"2": "morph"}, "clicks": {"2": [["!!hero"]]}}
        with self.assertRaises(ValueError) as cm:
            tools.apply_motion(self.src, plan, self.out)
        self.assertIn("Morph", str(cm.exception))


def _messy(path, img):
    """One slide each: a 3D chart, a stretched picture, two animated shapes with a path."""
    from PIL import Image
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.util import Pt
    import pptx_animator as anim
    Image.new("RGB", (400, 300), (90, 90, 90)).save(img)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    s = prs.slides.add_slide(blank)
    data = CategoryChartData(number_format="0.0")
    data.categories = ["A", "B", "C"]
    data.add_series("Rate", (3.8, 4.5, 2.0))
    data.add_series("Goal", (2, 2, 2))
    chart = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1), Inches(1), Inches(8), Inches(5), data)
    chart.name = "Chart"
    bar = chart.chart._chartSpace.find(f".//{{{tools.C_NS}}}barChart")
    bar.tag = f"{{{tools.C_NS}}}bar3DChart"
    anim.apply_timeline(s._element, [{"id": "c1", "start": "click", "effects": [
        {"preset": "fade", "spid": str(chart.shape_id), "trigger": "click", "duration_ms": 500}]}])
    s = prs.slides.add_slide(blank)
    pic = s.shapes.add_picture(str(img), Inches(1), Inches(1), Inches(6), Inches(3))  # photo is 4:3
    pic.name = "Photo"
    s = prs.slides.add_slide(blank)
    a = s.shapes.add_textbox(Inches(2), Inches(2), Inches(4), Inches(1))
    a.name, a.text_frame.text = "Big", "Label 24"
    a.text_frame.paragraphs[0].runs[0].font.size = Pt(24)
    b = s.shapes.add_textbox(Inches(10), Inches(4), Inches(4), Inches(1))  # runs off the slide
    b.name, b.text_frame.text = "Plain", "inherits its size"
    anim.apply_timeline(s._element, [{"id": "c1", "start": "click", "effects": [
        {"preset": "path", "spid": str(b.shape_id), "trigger": "click", "duration_ms": 800,
         "points": [{"x": 0, "y": 0}, {"x": 0.4, "y": 0}]}]}])
    prs.save(path)


class ExistingDeckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.src, self.out = d / "in.pptx", d / "out.pptx"
        _messy(self.src, d / "photo.png")

    def tearDown(self):
        self.tmp.cleanup()

    def test_inventory_names_what_the_eye_cannot_measure(self):
        report = tools.inventory(self.src)
        self.assertIn("bar3DChart  <- 3D: rechart", report)
        self.assertIn("'Photo' stretched 50% wider", report)
        self.assertIn("'Plain' runs 0.67 in off the slide", report)

    def test_rechart_keeps_identity_numbers_and_animation(self):
        before = Presentation(self.src).slides[0].shapes[0].shape_id
        info = tools.rechart(self.src, 1, "Chart", "line", self.out)
        self.assertEqual(info["categories"], ["A", "B", "C"])
        shape = Presentation(self.out).slides[0].shapes[0]
        self.assertEqual((shape.shape_id, shape.name), (before, "Chart"))
        self.assertEqual(tools._plot_kinds(shape.chart), ["lineChart"])
        self.assertEqual(list(shape.chart.plots[0].series[0].values), [3.8, 4.5, 2.0])
        self.assertIn(f'spid="{before}"', _xml(self.out, 1))  # its click still points at it
        with ZipFile(self.out) as z:  # the old 3D chart part is gone
            self.assertEqual(len([n for n in z.namelist() if n.startswith("ppt/charts/chart")]), 1)

    def test_scale_shrinks_text_strokes_and_inner_paths_and_keeps_ids(self):
        low = tools.scale(self.src, 3, ["Big", "Plain"], 0.5, self.out, at=(1, 1))
        s = Presentation(self.out).slides[2]
        big, plain = s.shapes
        self.assertEqual((big.left, big.top, big.width), (Inches(1), Inches(1), Inches(2)))
        self.assertEqual(plain.left, Inches(5))  # 8 in to the right of Big, halved
        self.assertEqual(big.text_frame.paragraphs[0].runs[0].font.size.pt, 12)
        self.assertEqual(plain.text_frame.paragraphs[0].runs[0].font.size.pt, 9)  # 18 pt inherited
        self.assertEqual(low, 9)
        self.assertIn('path="M 0 0 L 0.2 0 E"', _xml(self.out, 3))

    def test_unstretch_crops_or_refits_the_frame(self):
        tools.unstretch(self.src, 2, "Photo", self.out)
        self.assertAlmostEqual(tools._stretch(Presentation(self.out).slides[1].shapes[0]), 1, places=3)
        tools.unstretch(self.src, 2, "Photo", self.out, box=True)
        pic = Presentation(self.out).slides[1].shapes[0]
        self.assertEqual((round(pic.width / 914400, 2), pic.crop_top), (4.0, 0))

    def test_numbers_reports_what_the_new_deck_lost(self):
        tools.rechart(self.src, 1, "Chart", "column", self.out)
        self.assertEqual(tools.missing_numbers(self.src, self.out), {})
        prs = Presentation(self.out)
        sp = prs.slides[0].shapes[0]._element
        sp.getparent().remove(sp)
        prs.save(self.out)
        self.assertEqual(tools.missing_numbers(self.src, self.out), {1: ["2", "3.8", "4.5"]})

    # T095: what T094's review and the owner found
    def test_inventory_names_theme_fonts_counts_fills_and_flags_a_blank_opening(self):
        prs = Presentation(self.src)
        tools.theme_fonts(prs, "Segoe UI", "Segoe UI")
        for slide in prs.slides:
            tools.follow_theme(slide._element)
        prs.slides[1].background.fill.solid()
        prs.slides[1].background.fill.fore_color.rgb = tools.RGBColor.from_string("1F4E79")
        prs.save(self.out)
        report = tools.inventory(self.out)
        self.assertIn("fonts (1): Segoe UI", report)
        self.assertIn("1F4E79 (background) x1", report)
        slide1 = report.split("slide 2:")[0]  # the chart enters on the first click: nothing at the start
        self.assertIn("opens with only the title visible", slide1)

    def test_numbers_tells_a_percentage_from_a_count_and_counts_occurrences(self):
        def deck(path, *texts):
            prs = Presentation()
            for words in texts:
                prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_textbox(0, 0, Inches(4), Inches(1)).text_frame.text = words
            prs.save(path)
        a, b = Path(self.tmp.name) / "a.pptx", Path(self.tmp.name) / "b.pptx"
        deck(a, "Tỉ lệ 4,1%, mục tiêu 2%", "Đạt 2%")
        deck(b, "Tỉ lệ 4,1% và 2 lần phản hồi", "Đạt 2%")
        self.assertEqual(tools.missing_numbers(a, b), {})  # "2%" is still on slide 2 ...
        self.assertEqual(tools.fewer_numbers(a, b), {"2%": (2, 1)})  # ... but once, not twice

    def test_unstretch_respects_an_existing_crop(self):
        prs = Presentation(self.src)
        pic = prs.slides[1].shapes[0]
        pic.crop_left = 0.1  # visible 360 x 300 in a 6 x 3 frame
        prs.save(self.out)
        tools.unstretch(self.out, 2, "Photo", self.out)
        pic = Presentation(self.out).slides[1].shapes[0]
        self.assertAlmostEqual(tools._stretch(pic), 1, places=3)
        self.assertAlmostEqual(pic.crop_left, 0.1, places=3)


class SizeAndSampleTests(unittest.TestCase):
    """T096: what the QCC v6 restyle found."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _deck(self, width, height, pt):
        from pptx.util import Pt
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(width), Inches(height)
        box = prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_textbox(Inches(1), Inches(1), Inches(6), Inches(1))
        box.name, box.text_frame.text = "Body", "Glue does not cover the joint fully"
        box.text_frame.paragraphs[0].runs[0].font.size = Pt(pt)
        path = self.dir / f"{width}x{height}.pptx"
        prs.save(path)
        return path

    def test_small_text_floor_follows_the_slide_height(self):
        self.assertNotIn("text under", tools.inventory(self._deck(13.333, 7.5, 20)))
        big = tools.inventory(self._deck(20, 11.25, 20))  # 20 pt here reads like 13 pt on a 7.5 in slide
        self.assertIn("text floor 27 pt", big)
        self.assertIn("text under 27 pt in 'Body' (20 pt)", big)

    def test_critic_grades_body_size_for_the_slide_height(self):
        import design_critic as dc
        def small(path):
            return {i["detail"] for i in dc.critique(path)["issues"] if i["code"] == "TYP-SMALL"}
        self.assertEqual(small(self._deck(13.333, 7.5, 20)), set())
        self.assertTrue(small(self._deck(20, 11.25, 20)))

    @unittest.skipUnless(__import__("importlib").util.find_spec("fitz"), "PyMuPDF not installed")
    def test_sample_reads_fonts_sizes_and_colours_of_a_pdf(self):
        import fitz
        doc = fitz.open()
        page = doc.new_page(width=842, height=595)  # A4 landscape
        page.insert_text((72, 100), "Highlights 2026", fontname="helv", fontsize=24, color=(0, 0.4, 0.8))
        page.insert_text((72, 140), "Body text of the report", fontname="helv", fontsize=9, color=(0.2, 0.2, 0.2))
        page.draw_rect(fitz.Rect(72, 200, 372, 400), color=None, fill=(1, 0, 0))
        pdf = self.dir / "report.pdf"
        doc.save(pdf)
        report = tools.sample(pdf, self.dir / "look", [1])
        self.assertIn("297 x 210 mm (landscape)", report)
        self.assertIn("Helvetica 100%", report)
        self.assertIn("0066CC", report)                        # title colour
        self.assertIn("filled shapes by area: FF0000 100%", report)
        self.assertIn("24.0", report)
        self.assertTrue((self.dir / "look" / "sheet1.jpg").exists())
        self.assertTrue((self.dir / "look" / "page1.png").exists())


if __name__ == "__main__":
    unittest.main()
