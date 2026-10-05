import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import motion_director as md
from render_identity import diff_rgb
from validate_director_plan import validate as validate_director

ESSAY=ROOT/"tests"/"fixtures"/"essay_outline_deck.pptx"
HAS_RENDER=bool(shutil.which("soffice")) and bool(shutil.which("pdftoppm"))


def clicks_by_slide(plan):
    return {s["source_index"]:s for s in plan["slides"]}


class TextBoxDeckDirectorTests(unittest.TestCase):
    """T022 regressions from the T009 water-report deck (text boxes only)."""

    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(ESSAY)
        cls.plan=md.draft(cls.model,"Làm bài thuyết trình rõ ràng, mạch lạc.")
        cls.by=clicks_by_slide(cls.plan)

    def targets(self,index):
        return [t for b in self.by[index]["beats"] for t in b["targets"]]

    def test_plan_is_valid(self):
        self.assertEqual(validate_director(self.plan,self.model["inventory"]),[])

    def test_text_only_title_slide_stays_static(self):
        self.assertNotIn(1,self.by)

    def test_implicit_titles_and_title_zone_are_not_animated(self):
        for s in self.model["slides"][1:]:
            title=md._implicit_title(s)
            self.assertIsNotNone(title)
            self.assertNotIn(title["token"],self.targets(s["index"]))
        self.assertNotIn("TextBox 2",self.targets(5))  # subheading under the title

    def test_label_stays_with_its_text_block(self):
        s2=self.by[2]
        self.assertEqual(len(s2["click_beats"]),2)
        self.assertEqual(s2["beats"][0]["targets"],["TextBox 2","TextBox 3"])
        self.assertEqual(len(self.by[5]["click_beats"]),2)

    def test_dense_paragraphs_get_their_own_click_without_content_change(self):
        s3=self.by[3]
        self.assertEqual(len(s3["click_beats"]),2)
        first=[b for b in s3["beats"] if b["id"] in s3["click_beats"][0]["motion_beats"]]
        self.assertEqual([b["operation"] for b in first],["reveal","text-build"])
        self.assertEqual(first[1]["paragraphs"],[0])
        second=[b for b in s3["beats"] if b["id"] in s3["click_beats"][1]["motion_beats"]]
        self.assertEqual(second[0]["paragraphs"],[2])
        self.assertTrue(s3["click_beats"][1]["boundary_reason"])
        self.assertEqual(len(self.by[4]["click_beats"]),2)

    def test_wrapped_heading_is_not_split_into_bullet_clicks(self):
        title_slide=self.model["slides"][0]
        wrapped=[o for o in title_slide["objects"] if len(o["paragraphs"])==2]
        self.assertTrue(wrapped)
        self.assertTrue(all(md._is_heading(o) for o in wrapped))

    def test_apply_preserves_deck(self):
        with tempfile.TemporaryDirectory() as td:
            report=md.apply(ESSAY,self.plan,Path(td)/"out.pptx")
        self.assertTrue(report["ok"],report["problems"])
        self.assertEqual(sum(s.get("click_groups",0) for s in report["slides"]),8)


class RenderIdentityTests(unittest.TestCase):
    def test_rgb_diff_catches_change_that_rgba_getbbox_misses(self):
        a=Image.new("RGBA",(10,10),(255,255,255,255))
        b=a.copy()
        b.putpixel((3,4),(254,255,255,255))
        self.assertIsNone(ImageChops.difference(a,b).getbbox())  # T009 method
        bbox,count=diff_rgb(a,b)
        self.assertEqual((bbox,count),((3,4,4,5),1))
        self.assertEqual(diff_rgb(a,a.copy()),(None,0))

    @unittest.skipUnless(HAS_RENDER,"LibreOffice Impress + pdftoppm not installed")
    def test_timing_only_output_renders_identically(self):
        from render_identity import compare
        plan=md.draft(md.deck_model(ESSAY))
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"out.pptx"
            md.apply(ESSAY,plan,out)
            result=compare(ESSAY,out,dpi=30)
        self.assertEqual(result["identical_slides"],5)


if __name__=="__main__":
    unittest.main()
