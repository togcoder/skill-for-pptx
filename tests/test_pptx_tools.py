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


if __name__ == "__main__":
    unittest.main()
