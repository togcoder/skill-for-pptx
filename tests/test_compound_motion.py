import copy
import json
import math
import shutil
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

SHOWCASE=ROOT/"tests"/"fixtures"/"motion_showcase_deck.pptx"
DIRECTED=ROOT/"tests"/"fixtures"/"motion_showcase_director.json"
NS=anim.NS
HAS_PREVIEW=all(shutil.which(t) for t in ("soffice","pdftoppm","convert","montage"))


def slide_root(path,part):
    with ZipFile(path) as z:
        return E.fromstring(z.read(part))


def centre(obj,state):
    a=me.authored(obj)
    return (a["cx"]+state["dx"],a["cy"]+state["dy"])


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(SHOWCASE)
        cls.s5=cls.model["slides"][4]
        cls.by={o["name"]:o for o in cls.s5["objects"]}
        cls.tok={o["name"]:o for o in cls.s5["objects"]}

    def states(self,slide):
        return {o["id"]:me.fresh_state() for o in slide["objects"]}

    def test_chained_paths_are_anchored_and_continuous(self):
        st=self.states(self.s5)
        token=self.by["Order token"]
        first=me.compile_choreography("travel",[token,self.by["Step Order"]],st,self.tok,"a",{"pulse_stops":False})
        st=me.advance(st,first)
        second=me.compile_choreography("travel",[token,self.by["Step Roast"]],st,self.tok,"b",{"pulse_stops":False})
        p1,p2=first[0]["anchored"],second[0]["anchored"]
        self.assertEqual((p1[0]["x"],p1[0]["y"]),(0,0))
        self.assertAlmostEqual(p2[0]["x"],p1[-1]["x"])
        self.assertAlmostEqual(p2[0]["y"],p1[-1]["y"])
        st=me.advance(st,second)
        self.assertAlmostEqual(centre(token,st[token["id"]])[0],me.authored(self.by["Step Roast"])["cx"],places=6)

    def test_scale_and_rotation_compound_from_current_state(self):
        obj=self.by["Step Pack"]
        st=self.states(self.s5)
        e1=me.compile_track({"keyframes":[{"t":0},{"t":500,"scale":1.2,"rotate":90}]},obj,self.tok,st[obj["id"]],"x")
        st=me.advance(st,e1)
        e2=me.compile_track({"keyframes":[{"t":0},{"t":500,"scale":1.0,"rotate":0}]},obj,self.tok,st[obj["id"]],"y")
        grow=[e for e in e2 if e["preset"]=="grow"][0]
        spin=[e for e in e2 if e["preset"]=="spin"][0]
        self.assertAlmostEqual(grow["ratio"],1/1.2)
        self.assertAlmostEqual(spin["by_deg"],-90)
        st=me.advance(st,e2)
        self.assertAlmostEqual(st[obj["id"]]["scale"],1.0)
        self.assertAlmostEqual(st[obj["id"]]["rot"],0.0)

    def test_cycle_moves_each_object_to_its_neighbour(self):
        s2=self.model["slides"][1]
        stages=[o for o in s2["objects"] if o["name"].startswith("Stage")]
        tok={o["name"]:o for o in s2["objects"]}
        st=self.states(s2)
        effects=me.compile_choreography("cycle",stages,st,tok,"c",{"duration_ms":800})
        self.assertTrue(all(e["preset"]=="path" and "c1" in e["anchored"][-1] for e in effects))
        end=me.advance(st,effects)
        for i,o in enumerate(stages):
            nxt=me.authored(stages[(i+1)%len(stages)])
            x,y=centre(o,end[o["id"]])
            self.assertAlmostEqual(x,nxt["cx"],places=6)
            self.assertAlmostEqual(y,nxt["cy"],places=6)

    def test_spotlight_release_and_zoom_focus_restore(self):
        s6=self.model["slides"][5]
        quads=[o for o in s6["objects"] if o["name"].startswith("Quadrant")]
        tok={o["name"]:o for o in s6["objects"]}
        st=self.states(s6)
        st=me.advance(st,me.compile_choreography("spotlight",quads,st,tok,"s"))
        self.assertGreater(st[quads[0]["id"]]["scale"],1.0)
        self.assertTrue(all(st[o["id"]]["opacity"]<0.5 for o in quads[1:]))
        st=me.advance(st,me.compile_choreography("zoom-focus",quads,st,tok,"z",{"y":0.6}))
        self.assertTrue(all(not st[o["id"]]["visible"] for o in quads[1:]))
        st=me.advance(st,me.compile_choreography("release",quads,st,tok,"r"))
        for o in quads:
            s=st[o["id"]]
            self.assertTrue(s["visible"])
            self.assertAlmostEqual(s["scale"],1.0)
            self.assertAlmostEqual(s["opacity"],1.0)
            self.assertAlmostEqual(s["dx"],0.0)

    def test_overlapping_moves_of_one_object_are_rejected(self):
        obj=self.by["Step Order"]
        st=self.states(self.s5)
        a=me.compile_track({"keyframes":[{"t":0},{"t":800,"dx":0.1}]},obj,self.tok,st[obj["id"]],"a")
        b=me.compile_track({"keyframes":[{"t":0},{"t":800,"dy":0.1}]},obj,self.tok,st[obj["id"]],"b")
        for e in a+b:
            e["trigger"]="with"
        self.assertTrue(me.conflicts(a+b))

    def test_layout_warnings_find_new_occlusion_and_off_slide(self):
        s4=self.model["slides"][3]
        cost,speed=[o for o in s4["objects"] if o["name"] in ("Priority Cost","Priority Speed")]
        st=self.states(s4)
        st[cost["id"]]["dy"]=me.authored(speed)["cy"]-me.authored(cost)["cy"]
        warnings=me.layout_warnings(s4["objects"],st,"t")
        self.assertTrue(any("covers" in w for w in warnings))
        st[cost["id"]]["dy"]=0.9
        self.assertTrue(any("outside" in w for w in me.layout_warnings(s4["objects"],st,"t")))

    def test_writer_emits_grow_ratio_curved_anchored_path_and_easing(self):
        root=slide_root(SHOWCASE,"ppt/slides/slide5.xml")
        anim.apply_timeline(root,[{"id":"c","effects":[
            {"preset":"path","spid":"7","trigger":"click","duration_ms":700,"accel":0.0,"decel":0.6,
             "anchored":[{"x":0,"y":0},{"x":0.1,"y":-0.1,"c1":{"x":0.03,"y":-0.12},"c2":{"x":0.07,"y":-0.12}}]},
            {"preset":"grow","spid":"3","trigger":"with","delay_ms":700,"duration_ms":300,"ratio":1.25}]}])
        motion=root.find(".//p:animMotion",NS)
        self.assertTrue(motion.get("path").startswith("M 0 0 C "))
        self.assertIsNone(motion.get("ptsTypes"))
        ctn=[c for c in root.iter(anim.q("cTn")) if c.get("presetClass")=="path"][0]
        self.assertEqual((ctn.get("accel"),ctn.get("decel")),(None,"60000"))
        self.assertEqual(root.find(".//p:animScale/p:by",NS).get("x"),"125000")

    def test_xml_reader_round_trips_compiled_schedule(self):
        plan=json.loads(DIRECTED.read_text())
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"o.pptx"
            md.apply(SHOWCASE,plan,out)
            root=slide_root(out,"ppt/slides/slide5.xml")
        groups,autos=me.effects_from_slide(root)
        self.assertEqual(len(groups),5)
        paths=[e for g in groups for e in g if e["preset"]=="path"]
        self.assertEqual(len(paths),4)
        for a,b in zip(paths,paths[1:]):
            self.assertAlmostEqual(a["anchored"][-1]["x"],b["anchored"][0]["x"],places=5)


class DirectorCompoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(SHOWCASE)
        cls.auto=md.draft(cls.model,style="cinematic")
        cls.by={s["source_index"]:s for s in cls.auto["slides"]}
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)/"directed.pptx"
        cls.report=md.apply(SHOWCASE,json.loads(DIRECTED.read_text()),cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_auto_draft_detects_cycle_and_walks_it(self):
        s2=self.by[2]
        recipes=[b.get("recipe") for b in s2["beats"]]
        self.assertEqual(recipes,[None,"assemble","spotlight","spotlight","spotlight","spotlight","release"])
        order=[b["targets"][0] for b in s2["beats"] if b.get("recipe")=="spotlight"]
        self.assertEqual(order,["Stage Plan","Stage Do","Stage Check","Stage Act"])
        self.assertEqual(len(s2["click_beats"]),6)
        self.assertEqual(len(self.by[3]["click_beats"]),1)  # six partners: assemble only

    def test_auto_draft_adds_morph_and_keeps_continuing_object_static(self):
        self.assertEqual([t["slide"] for t in self.auto["transitions"]],[8])
        self.assertNotIn(7,self.by)
        targets=[t for b in self.by[8]["beats"] for t in b["targets"]]
        self.assertNotIn("Roastery photo",targets)
        self.assertEqual(validate_director(self.auto,self.model["inventory"]),[])

    def test_directed_plan_applies_cleanly(self):
        self.assertTrue(self.report["ok"],self.report["problems"])
        self.assertEqual(self.report["warnings"],[])
        by={s["slide"]:s for s in self.report["slides"]}
        self.assertEqual([by[i].get("click_groups") for i in (2,3,4,5,6,8)],[6,2,4,5,3,3])
        self.assertEqual(by[8]["transition"],"morph")
        root=slide_root(self.out,"ppt/slides/slide8.xml")
        self.assertIsNotNone(root.find(f".//{{{anim.MC}}}Fallback/p:transition/p:fade",NS))
        children=[E.QName(c).localname for c in root]
        self.assertLess(children.index("AlternateContent"),children.index("timing"))

    def test_validator_checks_recipes_and_transitions(self):
        plan=json.loads(DIRECTED.read_text())
        bad=copy.deepcopy(plan)
        swap=[b for s in bad["slides"] for b in s["beats"] if b.get("recipe")=="swap"][0]
        swap["targets"]=swap["targets"][:1]
        self.assertTrue(any("needs 2" in e for e in validate_director(bad,self.model["inventory"])))
        bad=copy.deepcopy(plan)
        bad["transitions"]=[{"slide":8,"kind":"morph","reason":""}]
        self.assertTrue(any("reason" in e for e in validate_director(bad,self.model["inventory"])))
        bad["version"]="0.5"
        self.assertTrue(any("v0.6" in e for e in validate_director(bad,self.model["inventory"])))

    def test_conflicting_choreography_blocks_the_slide(self):
        plan=json.loads(DIRECTED.read_text())
        s4=[s for s in plan["slides"] if s["source_index"]==4][0]
        s4["beats"].append({"id":"clash","purpose":"Second move on the same object.","operation":"choreography",
                            "targets":["Priority Cost"],"reuse_existing":True,"same_slide":True,
                            "timing_intent":"with-previous","recipe":"tracks",
                            "tracks":[{"target":"Priority Cost","keyframes":[{"t":0},{"t":600,"dx":0.05}]}]})
        s4["click_beats"][-1]["motion_beats"].append("clash")
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError) as cm:
                md.apply(SHOWCASE,plan,Path(td)/"x.pptx")
        self.assertIn("overlapping pos",str(cm.exception))

    @unittest.skipUnless(HAS_PREVIEW,"LibreOffice Impress, poppler and ImageMagick required")
    def test_preview_renders_every_sample(self):
        from motion_preview import render_slide_motion
        with tempfile.TemporaryDirectory() as td:
            r=render_slide_motion(self.out,4,Path(td)/"s4.gif",fps=4,sheet=Path(td)/"s4.png")
            self.assertTrue(Path(r["gif"]).exists())
            self.assertGreater(r["frames"],r["click_groups"])


if __name__=="__main__":
    unittest.main()
