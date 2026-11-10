"""T089: the tool defaults must do nothing, not the wrong thing.

Each test here failed on the code before T089:

- a KPI whose value is 0 stopped the build (empty counter stack);
- card titles in asymmetric/bento shrank to 14 pt even when short;
- Forge drew two decorative ``!!orb`` circles on every slide and turned Morph
  on by default;
- a word given as ``logo`` was drawn as a text watermark;
- a cover made of text boxes was split into several click groups;
- any object that moved between slides caused a Morph, including decoration
  and objects present on every slide;
- a deck font missing on this machine was reported as overflowing text.
"""
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import forge_qa
import motion_director as md
import slide_forge as sf


def shapes(path):
    return [sh for slide in Presentation(str(path)).slides for sh in slide.shapes]


def run_sizes(path,names):
    out={}
    for sh in shapes(path):
        if sh.name in names and sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        out.setdefault(sh.name,set()).add(r.font.size.pt)
    return out


def obj(oid,name,text,x,kind="shape",image=None,filled=False,placeholder=None):
    return {"id":oid,"name":name,"kind":kind,"text":text,"image":image,"filled":filled,
            "placeholder":placeholder,"geometry":{"x":x,"y":0.1,"w":0.2,"h":0.2}}


class ForgeDefaultsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.dir=Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self,spec,name="deck.pptx"):
        out=self.dir/name
        verdict=sf.build(spec,out)
        return out,verdict

    def test_kpi_zero_builds_instead_of_stopping(self):
        spec={"title":"KPI không","slides":[
            {"layout":"title","title":"Bìa","subtitle":"Phụ đề"},
            {"layout":"kpis","title":"Kết quả","items":[{"value":"0","label":"ca bệnh"}]}]}
        out,verdict=self.build(spec)
        self.assertTrue(verdict["ok"],verdict.get("errors"))
        self.assertEqual([s.name for s in shapes(out) if s.name.startswith("__counter_")],[])

    def test_short_card_titles_keep_their_size(self):
        spec={"title":"Cards","slides":[
            {"layout":"asymmetric","title":"Bất đối xứng",
             "major":{"heading":"Việc lớn","text":"Nội dung lớn."},
             "minor":{"heading":"Việc nhỏ","text":"Nội dung nhỏ."}},
            {"layout":"bento","title":"Bento",
             "hero":{"title":"Hero","text":"Nội dung hero."},
             "top_right":{"title":"Góc phải","text":"Nội dung phải."},
             "bottom_right_1":{"kpi":"12","label":"nhãn"},
             "bottom_right_2":{"kpi":"8","label":"nhãn"}}]}
        out,verdict=self.build(spec,"cards.pptx")
        sizes=run_sizes(out,{"Major Heading","Minor Heading","Hero Title","TopRight Title"})
        for name in ("Major Heading","Minor Heading","Hero Title","TopRight Title"):
            self.assertGreaterEqual(max(sizes[name]),18,f"{name} is {sizes[name]}")
        shrunk={w["object"] for w in verdict["warnings"] if w["code"]=="TEXT_SHRUNK"}
        self.assertEqual(shrunk & set(sizes),set())

    def test_no_decoration_and_no_morph_by_default(self):
        spec={"title":"Plain","slides":[
            {"layout":"statement","title":"Một câu","text":"Nội dung."},
            {"layout":"statement","title":"Câu hai","text":"Nội dung."}]}
        out,verdict=self.build(spec,"plain.pptx")
        self.assertEqual([s.name for s in shapes(out) if s.name.startswith("!!")],[])
        self.assertEqual(verdict["metrics"]["morph_transitions"],0)

    def test_explicit_morph_still_moves_a_content_picture(self):
        png=self.dir/"shared.png"
        Image.new("RGB",(64,64),"#005577").save(png)
        spec={"title":"Morph","motion":{"morph":True},"slides":[
            {"layout":"title","title":"Bìa","image":str(png)},
            {"layout":"image","title":"Nội dung","image":str(png)}]}
        out,verdict=self.build(spec,"morph.pptx")
        self.assertTrue(verdict["ok"],verdict.get("errors"))
        self.assertGreaterEqual(verdict["metrics"]["morph_transitions"],1)

    def test_logo_word_is_not_drawn_but_a_logo_image_is(self):
        spec={"title":"Logo","logo":"ACME","slides":[
            {"layout":"bullets","title":"Một","bullets":["a","b"]}]}
        out,verdict=self.build(spec,"word.pptx")
        self.assertEqual([s.name for s in shapes(out) if "logo" in s.name.lower()],[])
        self.assertIn("LOGO_SKIPPED",{w["code"] for w in verdict["warnings"]})

        png=self.dir/"mark.png"
        Image.new("RGB",(64,64),"#AA0000").save(png)
        spec["logo"]=str(png)
        out,verdict=self.build(spec,"image.pptx")
        pictures=[s for s in shapes(out) if s.shape_type==13]
        self.assertTrue(pictures,"the logo image is placed on the slide")
        self.assertNotIn("LOGO_SKIPPED",{w["code"] for w in verdict["warnings"]})


class DirectorDefaultsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.dir=Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def cover_deck(self):
        prs=Presentation()
        prs.slide_width=Inches(13.333)
        prs.slide_height=Inches(7.5)
        blank=prs.slide_layouts[6]
        cover=prs.slides.add_slide(blank)
        for text,y in (("KICKER",1.2),("Tên bài giảng",1.6),("Phụ đề bài giảng",2.4),
                       ("Người trình bày",3.0),("2026",3.4)):
            box=cover.shapes.add_textbox(Inches(0.8),Inches(y),Inches(6),Inches(0.4))
            box.text_frame.text=text
        cover.shapes.add_shape(1,Inches(0.8),Inches(4.0),Inches(4),Inches(0.05))
        body=prs.slides.add_slide(blank)
        box=body.shapes.add_textbox(Inches(0.8),Inches(1),Inches(8),Inches(3))
        box.text_frame.text="Nội dung chính của bài."
        path=self.dir/"cover.pptx"
        prs.save(path)
        return path

    def test_cover_is_one_automatic_group_not_several_clicks(self):
        plan=md.draft(md.deck_model(self.cover_deck()),style="modern",morph=False)
        first=next(s for s in plan["slides"] if s["source_index"]==1)
        self.assertEqual(len(first["click_beats"]),1)
        beat=next(b for b in first["beats"] if b["id"]==first["click_beats"][0]["motion_beats"][0])
        self.assertEqual(beat["timing_intent"],"on-slide-start")

    def test_decoration_alone_does_not_cause_a_morph(self):
        model={"slides":[
            {"index":1,"has_transition":False,"objects":[obj("1","!!orb-1",None,0.1),obj("2","Title","A",0.4)]},
            {"index":2,"has_transition":False,"objects":[obj("1","!!orb-1",None,0.7),obj("3","Title","B",0.4)]}]}
        self.assertEqual(md.detect_morph_pairs(model),[])

    def test_object_on_every_slide_does_not_cause_a_morph(self):
        model={"slides":[
            {"index":i,"has_transition":False,"objects":[obj("9","Section label","QCC",0.1+i*0.2)]}
            for i in (1,2,3)]}
        self.assertEqual(md.detect_morph_pairs(model),[])

    def test_a_content_object_that_moves_still_causes_a_morph(self):
        model={"slides":[
            {"index":1,"has_transition":False,"objects":[obj("1","Portrait","A",0.1)]},
            {"index":2,"has_transition":False,"objects":[obj("1","Portrait","A",0.7)]}]}
        morphs=md.detect_morph_pairs(model)
        self.assertEqual(len(morphs),1)
        self.assertEqual(morphs[0]["slide"],2)


class QaFontTests(unittest.TestCase):
    def test_missing_font_is_a_note_not_an_overflow(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path=Path(tmp.name)/"font.pptx"
        prs=Presentation()
        prs.slide_width=Inches(13.333)
        prs.slide_height=Inches(7.5)
        slide=prs.slides.add_slide(prs.slide_layouts[6])
        box=slide.shapes.add_textbox(Inches(1),Inches(1),Inches(2.0),Inches(0.5))
        box.text_frame.word_wrap=True
        run=box.text_frame.paragraphs[0].add_run()
        run.text="A sentence that is far too long for this narrow box"
        run.font.name="NoSuchFontXYZ"
        run.font.size=Pt(24)
        prs.save(path)
        verdict=forge_qa.qa(path)
        codes={e["code"] for e in verdict["errors"]}
        self.assertNotIn("TEXT_OVERFLOW",codes)
        notes={w["code"]:w for w in verdict["warnings"]}
        self.assertIn("FONT_MISSING",notes)
        self.assertIn("approximate",notes["FONT_MISSING"]["detail"])


if __name__=="__main__":
    unittest.main()
