"""T034: one design system for beauty and technique.

Generators read knowledge/design_system.json; validators and the critic grade
against the same numbers. These tests hold the two sides together."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import design_critic as dc  # noqa: E402
import design_system as ds  # noqa: E402
import motion_components as mc  # noqa: E402
import motion_director as md  # noqa: E402
import motion_engine as me  # noqa: E402
import motion_tokens as mt  # noqa: E402
import pptx_animator as anim  # noqa: E402
from validate_director_plan import validate as validate_director  # noqa: E402

FX=ROOT/"tests"/"fixtures"
REPORT=FX/"report_deck.pptx"
NS=anim.NS


class DesignSystemTests(unittest.TestCase):
    def test_rules_cite_sources_and_bands_are_ordered(self):
        sys_=ds.load()
        for r in sys_["rules"]:
            self.assertTrue(r["evidence"] and r["checker"] and r["generators"],r["id"])
            for src in r["evidence"]:
                self.assertIn(src,sys_["sources"],f"{r['id']} cites unknown source {src}")
        for role,spec in sys_["motion"]["duration_ms"].items():
            lo,hi=spec["band"]
            llo,lhi=spec["limit"]
            self.assertTrue(llo<=lo<=spec["default"]<=hi<=lhi,role)

    def test_grades_easing_contrast_and_travel(self):
        self.assertEqual(ds.grade(500,ds.duration("enter")),"good")
        self.assertEqual(ds.grade(800,ds.duration("enter")),"note")
        self.assertEqual(ds.grade(1500,ds.duration("enter")),"warn")
        self.assertEqual(ds.easing("move"),mt.ease("standard"))
        self.assertEqual(ds.easing("ambient"),(0.0,0.0))
        self.assertAlmostEqual(ds.contrast("FFFFFF","000000"),21.0,places=2)
        self.assertEqual(ds.text_contrast_needed(18),3.0)
        self.assertEqual(ds.text_contrast_needed(14,bold=True),3.0)
        self.assertEqual(ds.text_contrast_needed(14),4.5)
        short,long_=ds.travel_ms(0.1),ds.travel_ms(0.8)
        self.assertLess(short,long_)
        lo,hi=ds.duration("move")["band"]
        self.assertTrue(lo<=short and long_<=hi)


class GeneratorTests(unittest.TestCase):
    """The generators obey the design system."""

    def test_assemble_arrives_decelerating_with_overshoot(self):
        # Regression: the Argon merge had reverted assemble to the legacy
        # "out" curve and dropped overshoot (T029 had "enter" + overshoot).
        model=md.deck_model(FX/"motion_showcase_deck.pptx")
        slide=model["slides"][1]
        stages=[o for o in slide["objects"] if o["name"].startswith("Stage ")]
        plan_effects=self._assemble_effects(slide,stages)
        paths=[e for e in plan_effects if e["preset"]=="path"]
        enter=mt.ease("enter")
        self.assertTrue(any(abs(e.get("decel",0)-enter[1])<1e-9 for e in paths))
        per=[sum(1 for e in paths if e["spid"]==o["id"]) for o in stages]
        self.assertTrue(all(n==2 for n in per),per)  # main move + follow-through settle

    def _assemble_effects(self,slide,stages):
        beat={"id":"a","purpose":"t","operation":"choreography","targets":[o["token"] for o in stages],
              "reuse_existing":True,"same_slide":True,"timing_intent":"on-click","recipe":"assemble",
              "motion_parameters":{"from":"center","overshoot":0.08,"duration_ms":700}}
        click=md._click("c","t",["a"],"t","slide-complete","First.")
        ps={"source_index":slide["index"],"role":"t","objective":"t","beats":[beat],"click_beats":[click],"components":[]}
        clicks=md.compile_slide(ps,slide,md.STYLES["cinematic"],[])
        return [e for c in clicks for e in c["effects"]]

    def test_validator_rejects_out_of_band_overshoot_and_stagger(self):
        model=md.deck_model(FX/"motion_showcase_deck.pptx")
        plan=md.draft(model,style="cinematic")
        s=next(x for x in plan["slides"] if any(b.get("recipe")=="assemble" for b in x["beats"]))
        b=next(b for b in s["beats"] if b.get("recipe")=="assemble")
        b["motion_parameters"]["overshoot"]=0.3
        b["motion_parameters"]["stagger_ms"]=900
        errors=validate_director(plan,model["inventory"])
        self.assertTrue(any("MOT-OVERSHOOT" in e for e in errors))
        self.assertTrue(any("MOT-STAGGER" in e for e in errors))

    def test_writer_and_simulator_share_powerpoint_easing(self):
        root=E.fromstring(zipfile.ZipFile(REPORT).read("ppt/slides/slide5.xml"))
        spid=next(iter(anim.top_level_objects(root)))
        anim.apply_timeline(root,[{"effects":[{"preset":"path","spid":spid,"trigger":"click","duration_ms":600,
                                               "anchored":[{"x":0.1,"y":0.1},{"x":0.5,"y":0.1}]}]}],mode="replace")
        ctn=root.find(".//p:cTn[@presetClass='path']",NS)
        a,d=ds.easing("move")
        self.assertEqual((ctn.get("accel"),ctn.get("decel")),(str(round(a*100000)),str(round(d*100000))))
        eff={"preset":"path","accel":0.0,"decel":0.9}
        self.assertAlmostEqual(me._ease(0.5,eff),mt.ppt_progress(0.5,0.0,0.9))
        self.assertEqual(me._ease(0.5,{"preset":"path","accel":0.0,"decel":0.0}),0.5)

    def test_travel_takes_longer_for_longer_hops(self):
        model=md.deck_model(FX/"motion_showcase_deck.pptx")
        slide=model["slides"][4]
        token=next(o for o in slide["objects"] if o["name"]=="Order token")
        steps=[o for o in slide["objects"] if o["name"].startswith("Step ")]
        beat={"id":"t","purpose":"t","operation":"choreography","targets":[token["token"]]+[o["token"] for o in steps],
              "reuse_existing":True,"same_slide":True,"timing_intent":"on-click","recipe":"travel",
              "motion_parameters":{"dwell_ms":0}}
        click=md._click("c","t",["t"],"t","slide-complete","First.")
        ps={"source_index":5,"role":"t","objective":"t","beats":[beat],"click_beats":[click],"components":[]}
        clicks=md.compile_slide(ps,slide,md.STYLES["cinematic"],[])
        paths=[e for e in clicks[0]["effects"] if e["preset"]=="path" and e["spid"]==token["id"]]
        centre=lambda o:(o["geometry"]["x"]+o["geometry"]["w"]/2,o["geometry"]["y"]+o["geometry"]["h"]/2)
        stops=[centre(token)]+[centre(o) for o in steps]
        expected=[ds.travel_ms(((b[0]-a[0])**2+(b[1]-a[1])**2)**0.5) for a,b in zip(stops,stops[1:])]
        self.assertEqual([e["duration_ms"] for e in paths],expected)
        self.assertGreater(len(set(expected)),1)  # hops of different length take different time

    def test_helpers_reach_graphic_contrast_on_any_background(self):
        # The most-used fill is a dark card surface on a dark slide: the old
        # deck_style painted helpers with it (1.2:1, invisible).
        model={"inventory":{"design_profile":{"fill_colors":[{"value":"1E293B"},{"value":"38BDF8"}],
                                              "text_colors":[],"font_families":[]}}}
        style=mc.deck_style(model,background="0F172A")
        self.assertGreaterEqual(ds.contrast(style["accent"],"0F172A"),3.0)
        self.assertEqual(style["accent"],"38BDF8")
        only_dark={"inventory":{"design_profile":{"fill_colors":[{"value":"1E293B"}],"text_colors":[],"font_families":[]}}}
        moved=mc.deck_style(only_dark,background="0F172A")["accent"]
        self.assertGreaterEqual(ds.contrast(moved,"0F172A"),3.0)
        self.assertEqual(mc.deck_style(model)["accent"],"1E293B")  # no background: old behaviour

    def test_highlighter_keeps_the_text_readable(self):
        color,alpha=mc.marker_tint(["0F9D8A"],"0F9D8A","FFFFFF",ds.text_contrast_needed(20,bold=True))
        blend="".join(f"{round(int(color[i:i+2],16)*alpha+255*(1-alpha)):02X}" for i in (0,2,4))
        self.assertGreaterEqual(ds.contrast("0F9D8A",blend),3.0)
        dark_text=mc.marker_tint(["0F9D8A"],"1F2A44","FFFFFF",4.5)
        self.assertEqual(dark_text,("0F9D8A",0.25))  # dark text keeps the full marker


class CriticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td=tempfile.TemporaryDirectory()
        cls.raw=dc.critique(REPORT)
        cls.out=Path(cls.td.name)/"cinematic.pptx"
        r=subprocess.run([sys.executable,str(ROOT/"scripts"/"motion_director.py"),"auto",str(REPORT),"-o",str(cls.out),
                          "--style","cinematic","--force"],capture_output=True,text=True)
        assert r.returncode==0,r.stderr
        cls.directed=dc.critique(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def codes(self,v,severity="warn"):
        return {i["code"] for i in v["issues"] if i["severity"]==severity}

    def test_plain_deck_is_flagged_static_and_monotone(self):
        self.assertTrue({"MOT-STATIC","MOT-VOCAB"}<=self.codes(self.raw))
        kpi=[i for i in self.raw["issues"] if i["code"]=="COL-TEXT" and i["slide"]==3]
        self.assertEqual({i["measured"] for i in kpi},{2.95})  # teal 44 pt numbers on a cream card
        self.assertLess(self.raw["scores"]["rhythm"],self.directed["scores"]["rhythm"])

    def test_director_output_passes_the_rules_it_generates_for(self):
        generated={"MOT-DURATION","MOT-EASING","MOT-STAGGER","MOT-AMBIENT","MOT-CLICKS","MOT-MOVERS",
                   "MOT-STATIC","MOT-VOCAB","COL-GRAPHIC","MOT-SETTLE"}
        self.assertFalse(self.codes(self.directed)&generated,self.directed["issues"])
        self.assertGreater(self.directed["deck"]["lifecycles"],0)
        report=self.out.with_suffix(".report.md").read_text(encoding="utf-8")
        self.assertIn("## Design critique (design system",report)
        self.assertTrue(self.out.with_suffix(".critique.json").is_file())

    def test_gestures_autorev_and_drifts_are_read_as_one_motion(self):
        root=E.fromstring(zipfile.ZipFile(self.out).read("ppt/slides/slide5.xml"))
        groups,_=dc.slide_timing(root)
        paths=[e for g in groups for e in g["effects"] if e["cls"]=="path"]
        self.assertTrue(paths and all(e["dur"]>=ds.duration("move")["limit"][0] for e in paths))
        pulse={"cls":"emph","pid":6,"dur":400,"repeat":None,"spatial":True}
        self.assertEqual(dc.role(pulse),"emphasis")
        drift={"cls":"path","pid":0,"dur":7000,"repeat":None,"spatial":True}
        self.assertEqual(dc.role(drift),"ambient")

    def test_a_linear_move_is_flagged_and_an_eased_one_is_not(self):
        with tempfile.TemporaryDirectory() as td:
            outs={}
            for name,ease in (("linear",{"accel":0.0,"decel":0.0}),("eased",{})):
                z=zipfile.ZipFile(REPORT)
                out=Path(td)/f"{name}.pptx"
                with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as w:
                    for item in z.infolist():
                        data=z.read(item.filename)
                        if item.filename=="ppt/slides/slide5.xml":
                            root=E.fromstring(data)
                            spid=next(k for k,n in anim.top_level_objects(root).items()
                                      if n.find("./*/p:cNvPr",NS).get("name")=="Step 1")
                            anim.apply_timeline(root,[{"effects":[dict({"preset":"path","spid":spid,"trigger":"click",
                                "duration_ms":600,"anchored":[{"x":0.1,"y":0.4},{"x":0.5,"y":0.4}]},**ease)]}],mode="replace")
                            data=E.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
                        w.writestr(item,data)
                outs[name]={i["code"] for i in dc.critique(out)["issues"] if i["severity"]=="warn"}
        self.assertIn("MOT-EASING",outs["linear"])
        self.assertNotIn("MOT-EASING",outs["eased"])

    def test_highlighter_does_not_hide_the_result(self):
        plan=json.loads((ROOT/"experiments/T028-20261008-claude-morph-studio/report-director.json").read_text())
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"o.pptx"
            self.assertTrue(md.apply(REPORT,plan,out)["ok"])
            v=dc.critique(out)
        self.assertFalse([i for i in v["issues"] if i["code"]=="COL-TEXT" and i["object"]=="Result"])

    def test_schema_check_and_markdown(self):
        text=dc.markdown(self.directed)
        self.assertIn("| design | motion | rhythm | coherence",text)
        xsd=Path("/mnt/skills/public/pptx/scripts/office/schemas/ISO-IEC29500-4_2016/pml.xsd")
        if xsd.is_file():
            v=dc.critique(self.out,xsd=xsd)
            self.assertNotIn("TEC-SCHEMA",self.codes(v))

    def test_quarantined_modules_stay_out_of_product_paths(self):
        product=["motion_director.py","motion_engine.py","pptx_animator.py","morph_studio.py","slide_forge.py",
                 "motion_components.py","motion_script.py","design_critic.py","forge_qa.py"]
        for name in product:
            text=(ROOT/"scripts"/name).read_text(encoding="utf-8")
            for bad in ("morph_playbook","cognitive_pacing","interactive_triggers"):
                self.assertNotRegex(text,rf"^\s*(import|from)\s+{bad}\b",f"{name} imports {bad}")
        for bad in ("morph_playbook","cognitive_pacing","interactive_triggers"):
            head=(ROOT/"scripts"/f"{bad}.py").read_text(encoding="utf-8")[:400]
            self.assertIn("EXPERIMENTAL",head)


if __name__=="__main__":
    unittest.main()
