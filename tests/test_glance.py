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


def faults(rows, image=None, slots=frozenset(), moving=frozenset(), chart_inks=None):
    image = image or Image.new("RGB", (960, 540), (246, 242, 234))
    found, unreadable = tools._glance_slide({"slide": 2, "shapes": rows}, SIZE, slots, moving, image, chart_inks)
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
