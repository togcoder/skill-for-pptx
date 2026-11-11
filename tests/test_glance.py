"""T100: the faults a viewer sees at once, and the middle operation that puts a deck into a theme."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pptx_tools as tools  # noqa: E402

SIZE = (960.0, 540.0)
WHITE, INK, RED = 0xFFFFFF, 0x33241D, 0x0000FF   # PowerPoint colours are BGR


def row(shape_id, name, box, kind=1, text=None, runs=None, layer="slide", depth=0, text_box=None):
    out = {"id": shape_id, "name": name, "type": kind, "layer": layer, "depth": depth, "box": list(box), "visible": True}
    if text:
        out["text"] = {"sample": text, "box": list(text_box or box), "runs": runs or [[len(text), 24.0, INK]]}
    return out


def faults(rows, image=None, slots=frozenset(), moving=frozenset(), chart_inks=None,
           chart_sizes=None, pic_shas=None, repeated_shas=None, text_notes=None):
    image = image or Image.new("RGB", (960, 540), (246, 242, 234))
    found, unreadable = tools._glance_slide(
        {"slide": 2, "shapes": rows}, SIZE, slots, moving, image,
        chart_inks=chart_inks, chart_sizes=chart_sizes, pic_shas=pic_shas,
        repeated_shas=repeated_shas, text_notes=text_notes,
    )
    return [kind for kind, _, _ in found], unreadable


class GlanceRules(unittest.TestCase):
    def test_a_clean_slide_has_no_fault(self):
        kinds, _ = faults([row(1, "Title", (60, 40, 600, 50), text="Why the joint leaks"),
                           row(2, "Photo", (60, 140, 400, 300), kind=13),
                           row(3, "Label", (80, 160, 200, 30), text="Glue gap")])   # a label on a photo is fine
        self.assertEqual(kinds, [])

    def test_two_titles_printed_over_each_other(self):
        kinds, _ = faults([row(1, "Old title", (60, 40, 600, 50), text="2.2 Analysis cause 2"),
                           row(2, "Title", (70, 44, 600, 50), text="Cause 2: the glue overflowed")])
        self.assertEqual(kinds, ["text on text"])

    def test_animated_text_that_swaps_in_place_is_not_a_fault(self):
        rows = [row(1, "State A", (60, 40, 600, 50), text="Before"), row(2, "State B", (60, 40, 600, 50), text="After")]
        self.assertEqual(faults(rows, moving={2})[0], [])

    def test_white_text_on_ivory_cannot_be_read_and_is_listed_for_new_ink(self):
        rows = [row(1, "Note", (60, 300, 500, 40), text="written for a dark panel", runs=[[24, 24.0, WHITE]])]
        kinds, unreadable = faults(rows)
        self.assertEqual((kinds, unreadable), (["cannot read"], [(1, "FFFFFF")]))
        dark = Image.new("RGB", (960, 540), (40, 50, 70))
        self.assertEqual(faults(rows, dark)[0], [])        # the same text on its dark panel is fine

    def test_a_minority_colour_nobody_can_read_is_found_too(self):
        rows = [row(1, "Note", (60, 300, 500, 40), text="dark words and a yellow one",
                    runs=[[20, 24.0, INK], [6, 24.0, 0x00FFFF]])]
        self.assertEqual(faults(rows)[1], [(1, "FFFF00")])

    def test_new_logo_on_the_masters_old_logo(self):
        kinds, _ = faults([row(1, "Logo", (800, 20, 130, 24), kind=13),
                           row(9, "Picture 35", (830, 14, 120, 22), kind=13, layer="master"),
                           row(10, "Panel", (0, 60, 960, 480), kind=13, layer="master")])   # a background is no twin
        self.assertEqual(kinds, ["picture on the master's picture"])

    def test_text_under_a_picture_is_hidden_and_the_shell_applied_twice_shows(self):
        kinds, _ = faults([row(1, "Body", (60, 200, 400, 120), text="The STB machine turns the part"),
                           row(2, "Video", (200, 0, 300, 540), kind=16),
                           row(3, "Logo", (800, 20, 130, 24), kind=13), row(4, "Logo", (800, 20, 130, 24), kind=13)])
        self.assertEqual(sorted(kinds), ["same picture twice", "text hidden"])

    def test_tiny_text_and_the_footer_that_may_be_small(self):
        small = [row(1, "Body", (60, 100, 700, 300), text="x" * 200, runs=[[200, 8.0, INK]]),
                 row(2, "Footer", (60, 510, 400, 16), text="QCC 2026 SHARP Team", runs=[[19, 8.0, INK]])]
        self.assertEqual(faults(small)[0], ["tiny text"])
        self.assertEqual(faults(small[1:])[0], [])

    def test_content_under_the_shell_and_a_title_too_long_for_its_box(self):
        bar = row(1, "!!step5", (60, 20, 200, 30), text="5 Analysis root cause", runs=[[21, 14.0, WHITE]])
        table = row(2, "Table 4", (40, 10, 880, 500), kind=19)
        dark = Image.new("RGB", (960, 540), (0, 98, 172))
        self.assertIn("content under the shell", faults([bar, table], dark, slots={(2, 1)})[0])
        title = row(3, "Title", (60, 90, 800, 40), text="A title of two lines", text_box=(60, 60, 800, 100))
        photo = row(4, "Photo", (60, 135, 400, 300), kind=13)
        self.assertIn("text spills", faults([title, photo])[0])

    def test_chart_text_written_for_the_old_ground(self):
        chart = row(5, "Chart 17", (100, 100, 600, 300), kind=3)
        kinds, unreadable = faults([chart], chart_inks={5: {"FFFFFF", "1D2433"}})
        self.assertEqual((kinds, unreadable), (["cannot read"], [(5, "FFFFFF")]))

    def test_slots_are_what_sits_in_the_same_place_on_many_slides(self):
        slides = [{"slide": n, "shapes": [row(1, "Title", (60, 40, 600, 50), text=f"Title {n}"),
                                          row(2, "Body", (60 + 40 * n, 150 + 30 * n, 300, 100), text="body")]}
                  for n in range(1, 7)]
        del slides[3]["shapes"][0]                       # one slide has no title
        keys, usual = tools._slots(slides, SIZE)
        self.assertEqual(keys, {(n, 1) for n in (1, 2, 3, 5, 6)})
        self.assertEqual([(label, sorted(on)) for label, _, on in usual], [("Title", [1, 2, 3, 5, 6])])

    def test_table_cells_unreadable_and_tiny_text_are_caught_and_reinkable(self):
        tbl_row = {
            "id": 7, "name": "Table 4", "type": 19, "layer": "slide", "depth": 0,
            "box": [60.0, 120.0, 600.0, 220.0], "visible": True,
            "table": {"cells": [
                {"sample": "White cell", "runs": [[10, 16.0, WHITE]], "box": [70.0, 140.0, 180.0, 20.0]},
                {"sample": "Tiny cell", "runs": [[12, 8.0, INK]], "box": [270.0, 200.0, 180.0, 20.0]},
            ]},
        }
        kinds, unreadable = faults([tbl_row])
        self.assertEqual(sorted(kinds), ["cannot read", "tiny text"])
        self.assertEqual(unreadable, [(7, "FFFFFF")])
        clean_tbl = {
            "id": 8, "name": "Table 5", "type": 19, "layer": "slide", "depth": 0,
            "box": [60.0, 120.0, 600.0, 220.0], "visible": True,
            "table": {"cells": [
                {"sample": "Dark cell", "runs": [[9, 14.0, INK]], "box": [70.0, 140.0, 180.0, 20.0]},
            ]},
        }
        self.assertEqual(faults([clean_tbl]), ([], []))

    def test_chart_small_text_and_micro_text_floor(self):
        chart = row(5, "Chart 1", (100, 100, 600, 300), kind=3)
        self.assertEqual(faults([chart], chart_sizes={5: [8.0, 18.0]})[0], ["tiny text"])
        self.assertEqual(faults([chart], chart_sizes={5: [14.0, 18.0]})[0], [])
        body = [row(1, "Hero", (60, 60, 700, 100), text="Big statement", runs=[[200, 28.0, INK]]),
                row(2, "Card", (60, 200, 300, 80), text="Dense micro copy", runs=[[16, 8.0, INK]])]
        self.assertEqual(faults(body)[0], ["tiny text"])

    def test_text_on_busy_photo_is_flagged_while_smooth_background_passes(self):
        busy = Image.new("RGB", (960, 540), (246, 242, 234))
        draw = ImageDraw.Draw(busy)
        palette = ((245, 245, 245), (140, 185, 235), (170, 95, 70))
        for idx, y in enumerate(range(140, 360, 4)):
            draw.line([(80, y), (460, y)], fill=palette[idx % 3], width=4)
        rows = [row(1, "Photo", (80, 140, 380, 220), kind=13),
                row(2, "Label", (120, 200, 240, 60), text="Machine step", runs=[[12, 16.0, INK]])]
        self.assertIn("text on picture", faults(rows, busy)[0])
        self.assertEqual(faults(rows)[0], [])

    def test_same_content_photo_repeated_across_cards_vs_deck_wide_mark(self):
        rows = [row(1, "PicA", (60, 140, 160, 120), kind=13),
                row(2, "PicB", (300, 140, 160, 120), kind=13)]
        shas = {1: "deadbeef0001:0:0:0:0", 2: "deadbeef0001:0:0:0:0"}
        self.assertEqual(faults(rows, pic_shas=shas)[0], ["same picture twice"])
        self.assertEqual(faults(rows, pic_shas=shas, repeated_shas={"deadbeef0001:0:0:0:0"})[0], [])
        tiny_icons = [row(1, "IconA", (60, 140, 30, 30), kind=13),
                      row(2, "IconB", (300, 140, 30, 30), kind=13)]
        self.assertEqual(faults(tiny_icons, pic_shas=shas)[0], [])

    def test_broken_pua_symbol_and_draft_meta_text(self):
        self.assertEqual(tools._pua_hits("\uf0e8 Next", "Wingdings"), [])
        self.assertEqual(tools._pua_hits("\uf0e8 Next", "Arial"), [("Arial", "U+F0E8")])
        rows = [row(1, "Arrow", (60, 120, 200, 40), text="\uf0e8 Next"),
                row(2, "Draft", (60, 220, 400, 40), text="Charts kept from slide 4 [TODO]")]
        notes = {1: {"pua": [("Arial", "U+F0E8")], "full": "\uf0e8 Next"},
                 2: {"pua": [], "full": "Charts kept from slide 4 [TODO]"}}
        self.assertEqual(sorted(faults(rows, text_notes=notes)[0]), ["broken symbol", "draft text"])


def old_deck(path):
    """A deck in an old shell: a dark panel on the master, a step bar on every slide, light text."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    for n in range(1, 5):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bar = slide.shapes.add_textbox(0, 0, Inches(11), Inches(0.6))
        bar.name, bar.text_frame.text = f"Bar {n}", f"{n}. Step {n}"
        body = slide.shapes.add_textbox(Inches(0.5), Inches(0.9 + 0.2 * n), Inches(12.5), Inches(6))
        body.name = "Body"
        run = body.text_frame.paragraphs[0].add_run()
        run.text, run.font.size, run.font.color.rgb = "Leak 38% of rejects", Pt(24), RGBColor(0xFF, 0xFF, 0xFF)
        red = body.text_frame.paragraphs[0].add_run()
        red.text, red.font.size, red.font.color.rgb = " NG", Pt(24), RGBColor(0xC0, 0x00, 0x00)
    panel = copy.deepcopy(prs.slides[0].shapes[0]._element)       # a shape of the master: the old panel
    panel.find(qn("p:nvSpPr")).find(qn("p:cNvPr")).set("name", "Rectangle 8")
    for words in panel.iter(qn("a:t")):
        words.text = ""
    prs.slide_master.shapes._spTree.append(panel)
    prs.save(path)


class IntoATheme(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.old = self.dir / "old.pptx"
        old_deck(self.old)

    def tearDown(self):
        self.tmp.cleanup()

    def test_shell_finds_the_master_and_what_repeats_and_strip_takes_it_off(self):
        listing = tools.shell(self.old)
        self.assertIn("m1  on the master", listing)
        self.assertIn("r1  on 4 slides (1-4)", listing)
        self.assertIn("differs per slide", listing)
        out = self.dir / "base.pptx"
        words, note = tools.unshell(self.old, out, ["m1", "r1"], background="F6F2EA")
        self.assertIn("removed 5 shapes", note)
        self.assertEqual(words[3], [{"part": "r1", "text": "3. Step 3"}])
        self.assertEqual(json.loads(out.with_suffix(".shell.json").read_text(encoding="utf-8"))["3"][0]["text"], "3. Step 3")
        prs = Presentation(out)
        self.assertEqual([len(s.shapes) for s in prs.slides], [1, 1, 1, 1])
        self.assertEqual(len(prs.slide_master.shapes) - sum(s.is_placeholder for s in prs.slide_master.shapes), 0)
        self.assertEqual(prs.slide_master._element.find(".//" + qn("a:srgbClr")).get("val"), "F6F2EA")
        with self.assertRaises(ValueError):
            tools.unshell(self.old, out, ["m9"])

    def test_fit_reclaims_whitespace_for_clamped_boxes_without_hitting_neighbors(self):
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        wide = slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(8.0), Inches(3.0))
        wide.name, wide.text_frame.text = "Notes", "Line one wraps onto a taller frame when squeezed"
        wide.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
        sibling = slide.shapes.add_textbox(Inches(9.0), Inches(1.0), Inches(12.0), Inches(3.0))
        sibling.name, sibling.text_frame.text = "Metric", "42%"
        sibling.text_frame.paragraphs[0].runs[0].font.size = Pt(28)
        tall = slide.shapes.add_table(3, 2, Inches(0.5), Inches(4.5), Inches(8.0), Inches(4.5))
        tall.name = "Grid"
        for r in range(3):
            for c in range(2):
                tall.table.cell(r, c).text = f"R{r}C{c}"
                tall.table.cell(r, c).text_frame.paragraphs[0].runs[0].font.size = Pt(14)
        src, out = self.dir / "clamp.pptx", self.dir / "clamp-fit.pptx"
        prs.save(src)
        into = (0.7, 2.0, 12.0, 4.8)
        done = tools.fit(src, out, into)
        factor = done[0][1]
        self.assertLess(factor, 0.7)
        fitted = Presentation(out).slides[0]
        notes = next(s for s in fitted.shapes if s.name == "Notes")
        metric = next(s for s in fitted.shapes if s.name == "Metric")
        grid = next(s for s in fitted.shapes if s.name == "Grid")
        # Clamped text (14 pt -> clamped to 12 pt) reclaims slack without hitting sibling or leaving `into`
        self.assertGreater(notes.width, round(Inches(8.0) * factor))
        self.assertLessEqual(notes.left + notes.width, metric.left - round(Inches(0.05)))
        self.assertGreater(grid.height, round(Inches(4.5) * factor))
        self.assertLessEqual(grid.top + grid.height, Inches(into[1] + into[3]) + 10)
        self.assertLessEqual(metric.left + metric.width, Inches(into[0] + into[2]) + 10)

    def test_inventory_and_pre_com_guard_catch_stacked_outEnd_and_pua(self):
        from lxml import etree
        from pptx.chart.data import CategoryChartData
        from pptx.enum.chart import XL_CHART_TYPE
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
        box.name = "Step"
        r = box.text_frame.paragraphs[0].add_run()
        r.text, r.font.name, r.font.size = "\uf0e8 Broken", "Arial", Pt(20)
        data = CategoryChartData()
        data.categories = ["A", "B"]
        data.add_series("S1", (10, 20))
        data.add_series("S2", (5, 10))
        ch = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_STACKED, Inches(1), Inches(2), Inches(5), Inches(3), data)
        ch.name = "BadStack"
        ch.chart.plots[0].has_data_labels = True
        dlbls = ch.chart._chartSpace.find(f".//{{{tools.C_NS}}}barChart/{{{tools.C_NS}}}dLbls")
        dlbls.insert(0, etree.Element(f"{{{tools.C_NS}}}dLblPos", val="outEnd"))
        broken = self.dir / "broken_stack.pptx"
        prs.save(broken)
        inv = tools.inventory(broken)
        self.assertIn("dLblPos='outEnd'", inv)
        self.assertIn("U+F0E8 in 'Arial'", inv)
        with self.assertRaisesRegex(ValueError, "dLblPos='outEnd'"):
            tools.glance(broken, self.dir / "broken-glance")

    @unittest.skipUnless(os.environ.get("PPTX_NATIVE") == "1", "set PPTX_NATIVE=1 on a desktop with PowerPoint")
    def test_glance_native_tables_charts_pua_dup_photos_and_partial_slides(self):
        from lxml import etree
        from pptx.chart.data import CategoryChartData
        from pptx.enum.chart import XL_CHART_TYPE
        img_plain = self.dir / "dup.png"
        im_p = Image.new("RGB", (240, 180), (40, 90, 160))
        ImageDraw.Draw(im_p).rectangle((40, 40, 200, 140), fill=(220, 170, 50))
        im_p.save(img_plain)
        img_busy = self.dir / "busy.png"
        im_b = Image.new("RGB", (400, 250), (255, 255, 255))
        draw_b = ImageDraw.Draw(im_b)
        for y in range(0, 250, 8):
            draw_b.rectangle((0, y, 400, y + 3), fill=(25, 25, 25))
        im_b.save(img_busy)
        prs = Presentation()
        prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        for n in range(1, 5):
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            slot = sl.shapes.add_textbox(Inches(0.6), Inches(0.25), Inches(8.0), Inches(0.55))
            slot.name = "Title"
            r = slot.text_frame.paragraphs[0].add_run()
            r.text, r.font.name, r.font.size = f"Slide {n}", "Arial", Pt(24)
            r.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)
        # Slide 2: native table (dark header OK + white-on-white cell + tiny 8pt cell), PUA, draft text, dup photo
        s2 = prs.slides[1]
        tbl = s2.shapes.add_table(2, 2, Inches(0.8), Inches(1.2), Inches(5.0), Inches(1.8)).table
        s2.shapes[-1].name = "Table 4"
        tbl.cell(0, 0).fill.solid(); tbl.cell(0, 0).fill.fore_color.rgb = RGBColor(0x00, 0x62, 0xAC)
        r0 = tbl.cell(0, 0).text_frame.paragraphs[0].add_run()
        r0.text, r0.font.size, r0.font.color.rgb = "Header OK", Pt(16), RGBColor(0xFF, 0xFF, 0xFF)
        tbl.cell(1, 0).fill.solid(); tbl.cell(1, 0).fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r1 = tbl.cell(1, 0).text_frame.paragraphs[0].add_run()
        r1.text, r1.font.size, r1.font.color.rgb = "White cell leak", Pt(16), RGBColor(0xFF, 0xFF, 0xFF)
        tbl.cell(1, 1).fill.solid(); tbl.cell(1, 1).fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r2 = tbl.cell(1, 1).text_frame.paragraphs[0].add_run()
        r2.text, r2.font.size, r2.font.color.rgb = "Micro 8pt note", Pt(8), RGBColor(0x1D, 0x24, 0x33)
        pua_box = s2.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(4.5), Inches(0.6))
        pua_box.name = "Arrow"
        rp = pua_box.text_frame.paragraphs[0].add_run()
        rp.text, rp.font.name, rp.font.size = "\uf0e8 Cause leads here", "Arial", Pt(18)
        rp.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)
        draft_box = s2.shapes.add_textbox(Inches(0.8), Inches(4.0), Inches(5.0), Inches(0.6))
        draft_box.name = "DraftNote"
        rd = draft_box.text_frame.paragraphs[0].add_run()
        rd.text, rd.font.name, rd.font.size = "Charts kept from old slide", "Arial", Pt(18)
        rd.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)
        s2.shapes.add_picture(str(img_plain), Inches(7.0), Inches(1.2), Inches(2.4)).name = "DupA"
        s2.shapes.add_picture(str(img_plain), Inches(9.8), Inches(1.2), Inches(2.4)).name = "DupB"
        # Slide 3: text on busy photo + chart tiny text
        s3 = prs.slides[2]
        s3.shapes.add_picture(str(img_busy), Inches(0.8), Inches(1.5), Inches(5.0), Inches(3.0)).name = "StripedPhoto"
        over = s3.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(4.0), Inches(1.2))
        over.name = "OnPhoto"
        ro = over.text_frame.paragraphs[0].add_run()
        ro.text, ro.font.name, ro.font.size = "Readable? No", "Arial", Pt(20)
        ro.font.color.rgb = RGBColor(0x1D, 0x24, 0x33)
        data = CategoryChartData()
        data.categories = ["X", "Y"]
        data.add_series("Rate", (10, 20))
        ch = s3.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(6.5), Inches(1.5), Inches(5.5), Inches(4.0), data)
        ch.name = "SmallChart"
        ch.chart.font.size = Pt(8)
        deck = self.dir / "native_guards.pptx"
        prs.save(deck)
        report = tools.glance(deck, self.dir / "g-partial", slides=[2, 3])
        self.assertEqual([r["slide"] for r in report], [2, 3])
        k2 = {k for k, _ in report[0]["faults"]}
        self.assertEqual(k2, {"cannot read", "tiny text", "broken symbol", "draft text", "same picture twice"})
        self.assertNotIn("missing", k2)
        k3 = {k for k, _ in report[1]["faults"]}
        self.assertIn("tiny text", k3)
        self.assertTrue("text on picture" in k3 or "cannot read" in k3)
        reinked = self.dir / "reinked.pptx"
        tools.reink(deck, reinked, report, "1D2433")
        t_after = next(sh.table for sh in Presentation(reinked).slides[1].shapes if sh.name == "Table 4")
        self.assertEqual(str(t_after.cell(0, 0).text_frame.paragraphs[0].runs[0].font.color.rgb), "FFFFFF")
        self.assertEqual(str(t_after.cell(1, 0).text_frame.paragraphs[0].runs[0].font.color.rgb), "1D2433")

    def test_fit_puts_the_content_in_the_free_area_and_keeps_text_readable(self):
        out = self.dir / "fit.pptx"
        done = tools.fit(self.old, out, (0.7, 2.2, 12.0, 4.8), skip={f"Bar {n}" for n in range(1, 5)})
        self.assertEqual([n for n, _, _ in done], [1, 2, 3, 4])
        self.assertTrue(all(factor < 1 for _, factor, _ in done))
        prs = Presentation(out)
        for slide in prs.slides:
            body = next(s for s in slide.shapes if s.name == "Body")
            self.assertGreaterEqual(body.top, Inches(2.19))
            self.assertLessEqual(body.top + body.height, Inches(7.01))
            self.assertGreaterEqual(body.text_frame.paragraphs[0].runs[0].font.size.pt, 12)   # never under the minimum

    def test_reink_changes_only_the_colour_nobody_could_read(self):
        out = self.dir / "ink.pptx"
        body = next(s for s in Presentation(self.old).slides[0].shapes if s.name == "Body")
        changed = tools.reink(self.old, out, [{"slide": 1, "unreadable": [(body.shape_id, "FFFFFF")]}], "1D2433")
        self.assertEqual(changed, 1)
        runs = next(s for s in Presentation(out).slides[0].shapes if s.name == "Body").text_frame.paragraphs[0].runs
        self.assertEqual([str(r.font.color.rgb) for r in runs], ["1D2433", "C00000"])

    @unittest.skipUnless(os.environ.get("PPTX_NATIVE") == "1", "set PPTX_NATIVE=1 on a desktop with PowerPoint")
    def test_glance_and_compare_in_real_powerpoint(self):
        report = tools.glance(self.old, self.dir / "glance")
        self.assertEqual([[k for k, _ in r["faults"]] for r in report], [["cannot read"]] * 4)   # white on white
        self.assertTrue(Path(report[0]["marked"]).exists())
        fixed = self.dir / "fixed.pptx"
        tools.reink(self.old, fixed, report, "1D2433")
        self.assertEqual([r["faults"] for r in tools.glance(fixed, self.dir / "glance2")], [[]] * 4)
        pairs = tools.compare(self.old, fixed, self.dir / "pairs")
        self.assertEqual([(n, olds) for n, olds, _ in pairs], [(n, [n]) for n in range(1, 5)])
        self.assertEqual(Image.open(pairs[0][2]).size, (1600, 1860))


if __name__ == "__main__":
    unittest.main()
