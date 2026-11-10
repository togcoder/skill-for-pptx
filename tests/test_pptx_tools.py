"""T087: the guidance skill's toolbox writes clicks and transitions by shape name."""
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from pptx import Presentation
from pptx.oxml.ns import qn
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

    def test_inventory_names_numbers_repeated_on_many_slides(self):
        prs = Presentation()
        for k in range(5):
            box = prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_textbox(0, 0, Inches(6), Inches(1))
            box.text_frame.text = f"H422 step {k + 1}: 156,179 PPM" if k < 4 else "0 PPM in 2026"
        path = self.dir / "repeat.pptx"
        prs.save(path)
        report = tools.inventory(path)
        self.assertIn("156179 on 4 slides", report)
        self.assertNotIn("422 on", report)   # part of a code
        self.assertNotIn("2026 on", report)

    def test_key_numbers_keeps_thousands_dots_and_commas(self):
        self.assertEqual(tools._key_numbers("còn 1.200 sp và 1,200 sp"), {"1200"})
        self.assertEqual(tools._key_numbers("tỉ lệ 1.2%"), {"1.2%"})

    def test_inventory_reads_a_rebuilt_deck_with_video_old_transitions_and_lost_targets(self):
        from lxml import etree
        src, mid = self.dir / "v.pptx", self.dir / "v2.pptx"
        _deck(src)
        tools.apply_motion(src, {"clicks": {"1": [["Card A"]]}}, mid)
        prs = Presentation(mid)
        clip = self.dir / "clip.mp4"
        clip.write_bytes(b"\x00" * 64)
        prs.slides[1].shapes.add_movie(str(clip), 0, 0, Inches(4), Inches(3), mime_type="video/mp4")
        card = next(s for s in prs.slides[0].shapes if s.name == "Card A")
        card._element.getparent().remove(card._element)    # its click effect stays behind
        prs.slides[2]._element.append(etree.fromstring(
            '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:checker/></p:transition>'))
        prs.save(mid)
        report = tools.inventory(mid)                       # used to crash on the video
        self.assertIn("transitions: none x2, checker x1", report)
        self.assertIn("old-style transition 'checker'", report)
        self.assertIn("effects point to 1 shapes that are gone", report)

    @unittest.skipUnless(__import__("importlib").util.find_spec("fitz"), "PyMuPDF not installed")
    def test_sample_rejects_empty_pdf_and_bad_page(self):
        import fitz
        empty = self.dir / "empty.pdf"
        empty.write_bytes(b"not a real PDF")
        from unittest.mock import patch
        with patch("fitz.open", return_value=[]):
            with self.assertRaisesRegex(ValueError, "0 pages"):
                tools.sample(empty, self.dir / "empty-look")
        one = fitz.open()
        one.new_page()
        one_pdf = self.dir / "one.pdf"
        one.save(one_pdf)
        with self.assertRaisesRegex(ValueError, "has 1 pages"):
            tools.sample(one_pdf, self.dir / "one-look", [2])

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


class RebuildTests(unittest.TestCase):
    """T097: extract the original's media, then gate the rebuilt deck against it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        from PIL import Image
        self.photo = self.dir / "photo.png"
        Image.linear_gradient("L").resize((320, 200)).convert("RGB").save(self.photo)
        self.clip = self.dir / "clip.mp4"
        self.clip.write_bytes(b"\x00" * 64)
        prs = Presentation()
        one = prs.slides.add_slide(prs.slide_layouts[6])
        one.shapes.add_picture(str(self.photo), Inches(1), Inches(1), Inches(3)).name = "Teardown"
        one.shapes.add_movie(str(self.clip), 0, 0, prs.slide_width, prs.slide_height, mime_type="video/mp4")
        box = prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_textbox(0, 0, Inches(4), Inches(1))
        box.name, box.text_frame.text = "Card A", "Leak 38%"
        mid = self.dir / "mid.pptx"
        prs.save(mid)
        self.old = self.dir / "old.pptx"
        tools.apply_motion(mid, {"clicks": {"2": [["Card A"]]}}, self.old)
        self.map = {"1": {"old": [1], "group": "reskin"}, "2": {"old": [2], "group": "keep"}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_extract_writes_original_media_and_a_manifest(self):
        import json
        summary = tools.extract(self.old, self.dir / "x")
        self.assertIn("1 pictures and 1 videos", summary)
        manifest = json.loads((self.dir / "x" / "manifest.json").read_text(encoding="utf-8"))
        one, two = manifest["slide_list"]
        self.assertEqual({m["kind"] for m in one["media"]}, {"picture", "video"})
        self.assertTrue(all((self.dir / "x" / m["file"]).exists() for m in one["media"]))
        self.assertEqual((two["effects"], two["text"][0]["text"]), (1, "Leak 38%"))

    def test_check_passes_a_faithful_copy_and_fails_each_loss(self):
        gates, passed, _ = tools.check(self.old, self.old, self.map)
        self.assertEqual(passed, len(gates))
        from lxml import etree
        from PIL import Image
        prs = Presentation(self.old)
        one, two = prs.slides
        pic = next(s for s in one.shapes if s.name == "Teardown")
        pic.crop_left = 0.3                                   # evidence cut tighter
        video = next(s for s in one.shapes if s.name != "Teardown")
        video.width, video.height = video.width // 2, video.height // 2
        timing = two._element.find(qn("p:timing"))
        timing.getparent().remove(timing)                     # the keep slide loses its effect
        two.shapes[0].text_frame.text = "Leak"
        two._element.append(etree.fromstring(
            '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:checker/>'
            '</p:transition>'))
        bad = self.dir / "bad.pptx"
        prs.save(bad)
        failed = {name for ok, name, _ in tools.check(self.old, bad, self.map)[0] if not ok}
        self.assertEqual(failed, {"transitions", "videos fill the slide", "numbers kept", "pictures not cut",
                                  "keep slides keep their effects"})
        agreed = {**self.map, "1": {**self.map["1"], "video": "small"}}   # the user asked for a small video
        self.assertNotIn("videos fill the slide", {name for ok, name, _ in tools.check(self.old, bad, agreed)[0]
                                                   if not ok})
        resaved = self.dir / "photo.jpg"                       # the same photo saved again still counts
        Image.open(self.photo).resize((300, 188)).save(resaved, quality=80)
        prs = Presentation(self.old)
        pic = next(s for s in prs.slides[0].shapes if s.name == "Teardown")
        pic._element.getparent().remove(pic._element)
        prs.slides[0].shapes.add_picture(str(resaved), Inches(1), Inches(1), Inches(3))
        prs.save(bad)
        failed = {name for ok, name, _ in tools.check(self.old, bad, self.map)[0] if not ok}
        self.assertEqual(failed, set())

    def test_check_fails_a_map_that_leaves_a_slide_out(self):
        def failed(mapping):
            return {name for ok, name, _ in tools.check(self.old, self.old, mapping)[0] if not ok}
        one_row = {"1": self.map["1"]}
        self.assertEqual(failed(one_row), {"every slide accounted for"})            # old slide 2 is in no row
        self.assertEqual(failed({**one_row, "dropped": [2]}), set())               # left out on purpose
        self.assertEqual(failed({**self.map, "9": {"old": [2], "group": "keep"}}), {"every slide accounted for"})
        self.assertEqual(failed({**self.map, "2": {"old": [7], "group": "keep"}}), {"every slide accounted for"})


class TableAndCutoutTests(unittest.TestCase):
    """A native table restyled in place; a plain background taken off a picture."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_retable_keeps_text_and_merges_and_recolours_bars(self):
        from pptx.dml.color import RGBColor
        prs = Presentation()
        frame = prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_table(3, 3, 0, 0, Inches(6), Inches(2))
        frame.name = "Gantt"
        t = frame.table
        t.cell(0, 0).text, t.cell(1, 0).text = "Activity", "Teardown"
        t.cell(1, 0).merge(t.cell(2, 0))
        for r, c, colour in ((1, 1, "FFFF00"), (1, 2, "F8CBAD")):
            t.cell(r, c).fill.solid()
            t.cell(r, c).fill.fore_color.rgb = RGBColor.from_string(colour)
        src, out = self.dir / "t.pptx", self.dir / "t2.pptx"
        prs.save(src)
        self.assertEqual(tools.retable(src, 1, "Gantt", out, font="Arial", fill_map={"ffff00": "0062AC"}), (3, 3))
        t = Presentation(out).slides[0].shapes[0].table
        self.assertEqual((t.cell(1, 0).text, t.cell(1, 0).is_merge_origin), ("Teardown", True))
        fill = lambda r, c: t.cell(r, c)._tc.tcPr.find("a:solidFill/a:srgbClr", tools.NS).get("val")
        self.assertEqual((fill(0, 0), fill(1, 1), fill(1, 2)), ("0062AC", "0062AC", "FFFFFF"))
        pr = t.cell(1, 1)._tc.tcPr
        self.assertEqual([E_local(n) for n in pr][:5], ["lnL", "lnR", "lnT", "lnB", "solidFill"])  # schema order
        self.assertEqual(t.cell(0, 0).text_frame.paragraphs[0].runs[0].font.name, "Arial")

    def test_retable_keeps_diagonal_border_after_fill(self):
        from lxml import etree
        prs = Presentation()
        frame = prs.slides.add_slide(prs.slide_layouts[6]).shapes.add_table(1, 1, 0, 0, Inches(2), Inches(1))
        frame.name = "Table"
        tcPr = frame.table.cell(0, 0)._tc.get_or_add_tcPr()
        diagonal = etree.Element(qn("a:lnTlToBr"))
        tcPr.append(diagonal)
        src, out = self.dir / "diagonal.pptx", self.dir / "diagonal-out.pptx"
        prs.save(src)
        tools.retable(src, 1, "Table", out)
        pr = Presentation(out).slides[0].shapes[0].table.cell(0, 0)._tc.tcPr
        tags = [E_local(n) for n in pr]
        self.assertLess(tags.index("lnTlToBr"), tags.index("solidFill"))

    @unittest.skipUnless(__import__("importlib").util.find_spec("scipy"), "scipy not installed")
    def test_cutout_keeps_the_whole_subject_and_drops_the_background(self):
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (400, 240), (244, 237, 245))
        d = ImageDraw.Draw(im)
        d.line((10, 200, 390, 20), fill=(215, 205, 225), width=3)       # a faint sketch in the background
        d.ellipse((100, 60, 260, 200), fill=(30, 60, 210))                # the subject
        d.ellipse((150, 100, 180, 130), fill=(235, 235, 235))             # its pale eye, inside
        src, out = self.dir / "fish.png", self.dir / "cut.png"
        im.save(src)
        summary = tools.cutout(src, out)
        self.assertIn("kept 1 part", summary)
        a = Image.open(out).getchannel("A")
        self.assertEqual(a.getpixel((180, 180)), 255)   # body
        self.assertEqual(a.getpixel((165, 115)), 255)   # the eye stays
        self.assertEqual(a.getpixel((20, 20)), 0)       # background
        self.assertEqual(a.getpixel((200, 110)), 255)
        self.assertEqual(a.getpixel((330, 60)), 0)      # the sketch line is gone

    def test_replace_picture_keeps_id_and_place(self):
        from PIL import Image
        a, b = self.dir / "a.png", self.dir / "b.png"
        Image.new("RGB", (40, 20), (200, 0, 0)).save(a)
        Image.new("RGBA", (40, 20), (0, 0, 200, 128)).save(b)
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        pic = slide.shapes.add_picture(str(a), Inches(1), Inches(1), Inches(4))
        pic.name = "Fish frame"
        before = (pic.shape_id, pic.left, pic.width)
        tools.replace_picture(slide, "Fish frame", str(b))
        out = self.dir / "p.pptx"
        prs.save(out)
        pic = Presentation(out).slides[0].shapes[0]
        self.assertEqual((pic.shape_id, pic.left, pic.width), before)
        self.assertEqual(pic.image.ext, "png")
        self.assertEqual(pic.image.size, (40, 20))
        self.assertEqual(Image.open(__import__("io").BytesIO(pic.image.blob)).mode, "RGBA")


def E_local(node):
    from lxml import etree
    return etree.QName(node).localname



class WatchTest(unittest.TestCase):
    """T073: reading the pictures of a slide show. The show itself needs PowerPoint."""

    def _frame(self, *boxes):
        from PIL import Image, ImageDraw
        image = Image.new("RGB", (320, 180), (250, 250, 250))
        for box in boxes:
            ImageDraw.Draw(image).rectangle(box, fill=(180, 20, 20))
        return image

    def test_slide_box_beside_the_scrollbar(self):
        self.assertEqual(tools._slide_box(1422, 700, 22, 16 / 9), (78, 0, 1322, 700))  # bars left and right
        self.assertEqual(tools._slide_box(1482, 833, 21, 16 / 9), (0, 5, 1461, 827))   # bars above and below

    def test_a_click_is_dead_passing_or_a_change(self):
        empty, card = self._frame(), self._frame((40, 40, 120, 90))
        self.assertEqual(tools._read_step(empty, [(0.1, empty), (0.9, empty)])[0], "dead")
        kind, picture = tools._read_step(empty, [(0.1, empty), (0.4, card), (0.9, empty)])
        self.assertEqual(kind, "passing")
        self.assertIs(picture, card)
        kind, picture = tools._read_step(empty, [(0.1, empty), (0.4, card)])
        self.assertEqual(kind, "change")
        self.assertIs(picture, card)

    def test_report_names_the_wasted_click(self):
        lines = tools.watch_lines([{"slide": 2, "enter": "morph 1.2 s", "strip": "slide-02.jpg", "clicks": [
            {"click": 1, "kind": "change", "seconds": 0.4}, {"click": 2, "kind": "dead", "seconds": 0.0}]}])
        self.assertIn("morph 1.2 s, 2 clicks", lines[0])
        self.assertIn("NOTHING CHANGES", lines[2])

    @unittest.skipUnless(__import__("os").environ.get("PPTX_NATIVE") == "1", "set PPTX_NATIVE=1 on a desktop with PowerPoint")
    def test_watch_the_real_show(self):
        with tempfile.TemporaryDirectory() as tmp:
            deck, moving = Path(tmp) / "deck.pptx", Path(tmp) / "moving.pptx"
            _deck(deck)
            prs = Presentation(deck)
            prs.slides[2].shapes.add_textbox(Inches(1), Inches(4), Inches(2), Inches(1)).name = "Ghost"  # no text
            prs.save(deck)
            plan = {"transitions": {"2": "morph"}, "clicks": {"1": [["Card A"], ["Card B"]], "3": [["Ghost"]]}}
            tools.apply_motion(str(deck), plan, str(moving))
            report = tools.watch(str(moving), Path(tmp) / "watch")
            self.assertEqual([[c["kind"] for c in row["clicks"]] for row in report],
                             [["change", "change"], [], ["dead"]])
            self.assertTrue(report[1]["enter"].startswith("morph"))
            self.assertTrue(Path(report[0]["strip"]).exists())


if __name__ == "__main__":
    unittest.main()
