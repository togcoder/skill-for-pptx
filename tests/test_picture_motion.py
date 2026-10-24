"""T024: pictures keep moving (Ken Burns), accents draw in, idle loops."""
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import motion_director as md
import motion_engine as me
import pptx_animator as anim
from validate_director_plan import validate as validate_director

FIXTURE=ROOT/"tests"/"fixtures"/"picture_deck.pptx"
NS=anim.NS


def slide_root(path,n):
    with ZipFile(path) as z:
        return E.fromstring(z.read(f"ppt/slides/slide{n}.xml"))


def plan_ops(slide):
    return [(b["operation"],b.get("recipe") or b.get("effect"),b["targets"],b["timing_intent"]) for b in slide["beats"]]


class PictureDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(FIXTURE)
        cls.plan=md.draft(cls.model)
        cls.by={s["source_index"]:s for s in cls.plan["slides"]}

    def test_plan_is_valid(self):
        self.assertEqual(validate_director(self.plan,self.model["inventory"]),[])

    def test_title_slide_gets_automatic_intro_not_clicks(self):
        ops=plan_ops(self.by[1])
        self.assertEqual(ops[0],("stagger-reveal","wipe-right",["Accent bar"],"on-slide-start"))
        self.assertEqual(ops[1][:3],("choreography","ken-burns",["Backdrop"]))
        self.assertEqual(len(self.by[1]["click_beats"]),1)
        self.assertNotIn("Title",[t for b in self.by[1]["beats"] for t in b["targets"]])

    def test_content_picture_reveals_then_keeps_moving(self):
        ops=plan_ops(self.by[2])
        self.assertEqual(ops[0][3],"on-slide-start")  # underline draws in
        pic=[o for o in ops if o[2]==["Roastery photo"]]
        self.assertEqual([o[0] for o in pic],["reveal","choreography"])
        self.assertEqual(pic[1][1:],("ken-burns",["Roastery photo"],"after-previous"))

    def test_single_picture_slide_is_no_longer_static(self):
        self.assertEqual(plan_ops(self.by[3]),[("choreography","ken-burns",["Harvest photo"],"on-slide-start")])

    def test_subtle_style_keeps_pictures_alive_but_skips_accents(self):
        plan=md.draft(self.model,style="subtle")
        targets=[t for s in plan["slides"] for b in s["beats"] for t in b["targets"]]
        self.assertNotIn("Accent bar",targets)
        self.assertIn("Backdrop",targets)

    def test_picture_carried_by_morph_does_not_drift(self):
        showcase=md.deck_model(ROOT/"tests"/"fixtures"/"motion_showcase_deck.pptx")
        plan=md.draft(showcase)
        recipes=[(s["source_index"],b.get("recipe")) for s in plan["slides"] for b in s["beats"]]
        self.assertNotIn("ken-burns",[r for _,r in recipes])


class PictureApplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)/"out.pptx"
        cls.report=md.apply(FIXTURE,md.draft(md.deck_model(FIXTURE)),cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_applies_without_problems_or_warnings(self):
        self.assertTrue(self.report["ok"],self.report["problems"])
        self.assertEqual(self.report["warnings"],[])

    def test_backdrop_moves_and_scales_from_slide_start(self):
        root=slide_root(self.out,1)
        group=root.find(".//p:cTn[@nodeType='mainSeq']/p:childTnLst/p:par/p:cTn",NS)
        self.assertIsNotNone(group.find("p:stCondLst/p:cond[@evt='onBegin']",NS))
        self.assertIsNotNone(group.find(".//p:animMotion",NS))
        by=group.find(".//p:animScale/p:by",NS)
        self.assertEqual(by.get("x"),"106000")


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.model=md.deck_model(FIXTURE)
        self.slide=next(s for s in self.model["slides"] if s["index"]==2)
        self.photo=next(o for o in self.slide["objects"] if o["name"]=="Roastery photo")

    def loop_effects(self):
        states={o["id"]:me.fresh_state() for o in self.slide["objects"]}
        return me.compile_choreography("float",[self.photo],states,{},"b1",{"amplitude":0.01,"period_ms":2000})

    def test_float_writes_repeat_until_slide_end_and_round_trips(self):
        effects=self.loop_effects()
        effects[0]["trigger"]="click"
        root=slide_root(FIXTURE,2)
        anim.apply_timeline(root,[{"id":"c1","effects":effects}])
        ctn=root.find(".//p:cTn[@presetClass='path']",NS)
        self.assertEqual((ctn.get("repeatCount"),ctn.get("autoRev")),("indefinite","1"))
        group=me.effects_from_slide(root)[0][0]
        self.assertEqual(group[0]["loop"],{"repeat":"indefinite","auto_reverse":True})
        end=me.advance({self.photo["id"]:me.fresh_state()},group)[self.photo["id"]]
        self.assertAlmostEqual(end["dy"],0.0)  # one simulated cycle returns home

    def test_drifting_loop_is_rejected(self):
        eff={"preset":"path","spid":"2","trigger":"click","duration_ms":500,"loop":{"repeat":"indefinite"},
             "anchored":[{"x":0,"y":0},{"x":0,"y":-0.01}]}
        with self.assertRaises(ValueError):
            anim.validate_effect(eff)

    def test_later_click_cannot_move_a_looping_object(self):
        token=self.photo["name"]
        plan={"beats":[
            {"id":"f","operation":"choreography","recipe":"float","targets":[token],"timing_intent":"on-click"},
            {"id":"k","operation":"choreography","recipe":"ken-burns","targets":[token],"timing_intent":"on-click"}],
              "click_beats":[{"id":"c1","motion_beats":["f"]},{"id":"c2","motion_beats":["k"]}]}
        with self.assertRaisesRegex(ValueError,"already looping"):
            md.compile_slide(plan,self.slide)


if __name__=="__main__":
    unittest.main()
