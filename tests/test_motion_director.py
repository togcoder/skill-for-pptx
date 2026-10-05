import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"tests"))

import pptx_animator as anim
import motion_director as md
from validate_director_plan import validate as validate_director

FIXTURE=ROOT/"tests"/"fixtures"/"report_deck.pptx"
H001=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"
NS=anim.NS
HAS_SOFFICE=bool(shutil.which("soffice")) and bool(shutil.which("montage"))


def slide_root(path,part):
    with ZipFile(path) as z:
        return E.fromstring(z.read(part))


def effect_ctns(root):
    return [c for c in root.iter(anim.q("cTn")) if c.get("presetClass")]


class CanonicalWriterTests(unittest.TestCase):
    def setUp(self):
        self.root=slide_root(FIXTURE,"ppt/slides/slide5.xml")

    def test_after_previous_opens_new_time_block_at_previous_end(self):
        clicks=[{"id":"c1","effects":[
            {"preset":"fade","spid":"3","trigger":"click","duration_ms":400},
            {"preset":"wipe-right","spid":"5","trigger":"after","duration_ms":300},
            {"preset":"fade","spid":"4","trigger":"with","delay_ms":100,"duration_ms":400},
            {"preset":"fade","spid":"6","trigger":"after","duration_ms":400},
        ]}]
        anim.apply_timeline(self.root,clicks)
        group=self.root.find(".//p:cTn[@nodeType='mainSeq']/p:childTnLst/p:par/p:cTn",NS)
        blocks=group.findall("p:childTnLst/p:par/p:cTn",NS)
        delays=[b.find("p:stCondLst/p:cond",NS).get("delay") for b in blocks]
        # block0: 0..400, block1 starts 400 and ends max(300, 100+400)=900
        self.assertEqual(delays,["0","400","900"])
        types=[c.get("nodeType") for c in effect_ctns(self.root)]
        self.assertEqual(types,["clickEffect","afterEffect","withEffect","afterEffect"])

    def test_entrance_sets_visibility_before_effect_and_exit_hides_at_end(self):
        clicks=[{"id":"c1","effects":[
            {"preset":"float-in","spid":"3","trigger":"click","duration_ms":600},
            {"preset":"fade-out","spid":"4","trigger":"after","duration_ms":400},
        ]}]
        anim.apply_timeline(self.root,clicks)
        entr,exit_=effect_ctns(self.root)
        self.assertEqual((entr.get("presetClass"),entr.get("presetID")),("entr","42"))
        first=entr.find("p:childTnLst/*",NS)
        self.assertEqual(E.QName(first).localname,"set")
        self.assertEqual(first.find("p:to/p:strVal",NS).get("val"),"visible")
        attrs=[a.text for a in entr.iter(anim.q("attrName"))]
        self.assertIn("ppt_y",attrs)
        last=exit_.findall("p:childTnLst/*",NS)[-1]
        self.assertEqual(last.find("p:to/p:strVal",NS).get("val"),"hidden")
        self.assertEqual(last.find(".//p:cond",NS).get("delay"),"399")

    def test_build_list_only_for_text_shapes_and_paragraph_builds(self):
        root=slide_root(FIXTURE,"ppt/slides/slide2.xml")
        clicks=[{"id":"c1","effects":[
            {"preset":"fade","spid":"3","paragraph":0,"trigger":"click","duration_ms":400,"beat":"b"},
            {"preset":"fade","spid":"3","paragraph":1,"trigger":"after","duration_ms":400,"beat":"b"},
        ]}]
        anim.apply_timeline(root,clicks)
        blds=root.findall(".//p:bldLst/p:bldP",NS)
        self.assertEqual([(b.get("spid"),b.get("grpId"),b.get("build")) for b in blds],[("3","0","p")])
        targets=[t.get("st") for t in root.iter(anim.q("pRg"))]
        self.assertEqual(sorted(set(targets)),["0","1"])
        connector_root=slide_root(FIXTURE,"ppt/slides/slide5.xml")
        anim.apply_timeline(connector_root,[{"id":"c","effects":[
            {"preset":"wipe-right","spid":"5","trigger":"click","duration_ms":300}]}])
        self.assertIsNone(connector_root.find(".//p:bldLst",NS))

    def test_rejects_nested_group_members_and_unknown_paragraphs(self):
        with self.assertRaises(ValueError):
            anim.apply_timeline(self.root,[{"id":"c","effects":[
                {"preset":"fade","spid":"999","trigger":"click","duration_ms":300}]}])
        with self.assertRaises(ValueError):
            anim.apply_timeline(self.root,[{"id":"c","effects":[
                {"preset":"fade","spid":"3","paragraph":7,"trigger":"click","duration_ms":300}]}])

    def test_auto_start_group_uses_on_begin(self):
        anim.apply_timeline(self.root,[{"id":"c","start":"auto","effects":[
            {"preset":"fade","spid":"3","trigger":"click","duration_ms":300}]}])
        conds=self.root.findall(".//p:cTn[@nodeType='mainSeq']/p:childTnLst/p:par/p:cTn/p:stCondLst/p:cond",NS)
        self.assertEqual(conds[1].get("evt"),"onBegin")
        self.assertEqual(effect_ctns(self.root)[0].get("nodeType"),"afterEffect")
        states,groups=anim.simulate_states(self.root)
        self.assertTrue(groups[0]["auto"])

    def test_extends_powerpoint_authored_timing_without_touching_it(self):
        root=slide_root(FIXTURE,"ppt/slides/slide6.xml")
        main=root.find(".//p:cTn[@nodeType='mainSeq']/p:childTnLst",NS)
        before=[E.tostring(p) for p in main.findall("p:par",NS)]
        receipt=anim.apply_timeline(root,[{"id":"c","effects":[
            {"preset":"fade","spid":"4","trigger":"click","duration_ms":500},
            {"preset":"pulse","spid":"3","trigger":"after","duration_ms":250}]}])
        after=[E.tostring(p) for p in main.findall("p:par",NS)]
        self.assertEqual(after[:2],before)
        self.assertEqual(len(after),3)
        self.assertEqual(receipt["existing_click_groups"],2)
        ids=[int(c.get("id")) for c in root.iter(anim.q("cTn"))]
        self.assertEqual(len(ids),len(set(ids)))
        new=effect_ctns(root)[-1]
        self.assertEqual(new.get("grpId"),"1")  # spid 3 already used grpId 0
        groups=anim.read_main_sequence(root)
        self.assertEqual([e["paragraph"] for e in groups[0]["effects"]],[0])
        with self.assertRaises(ValueError):
            anim.apply_timeline(root,[{"id":"x","start":"auto","effects":[
                {"preset":"fade","spid":"4","trigger":"click","duration_ms":100}]}])


class DirectorPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.td=Path(cls.tmp.name)
        cls.model=md.deck_model(FIXTURE)
        cls.plan=md.draft(cls.model,"Make the Q3 review presenter-paced")
        cls.out=cls.td/"out.pptx"
        cls.report=md.apply(FIXTURE,cls.plan,cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_model_resolves_placeholder_geometry_from_layout(self):
        body=next(o for o in self.model["slides"][1]["objects"] if o["name"]=="Content Placeholder 2")
        self.assertTrue(body["geometry_inherited"])
        self.assertGreater(body["geometry"]["h"],0.3)
        self.assertEqual(len(body["paragraphs"]),4)

    def test_draft_is_a_valid_director_plan_with_reasoned_clicks(self):
        self.assertEqual(validate_director(self.plan,self.model["inventory"]),[])
        planned={s["source_index"] for s in self.plan["slides"]}
        self.assertNotIn(1,planned)  # title slide static
        self.assertNotIn(6,planned)  # existing choreography preserved
        self.assertEqual(self.plan["script"]["source"],"speaker-notes")
        for s in self.plan["slides"]:
            for i,c in enumerate(s["click_beats"]):
                self.assertTrue(c["boundary_reason"])

    def test_output_preserves_source_and_passes_checks(self):
        self.assertTrue(self.report["ok"],self.report["problems"])
        changed={s["slide"] for s in self.report["slides"] if s["changed"]}
        self.assertEqual(changed,{2,3,4,5,7})
        with ZipFile(FIXTURE) as a, ZipFile(self.out) as b:
            for part in ("ppt/slides/slide1.xml","ppt/slides/slide6.xml","ppt/charts/chart1.xml"):
                self.assertEqual(a.read(part),b.read(part))

    def test_click_rhythm_matches_narrative(self):
        by={s["slide"]:s for s in self.report["slides"]}
        self.assertEqual(by[2]["click_groups"],4)   # one agenda point per click
        self.assertEqual(by[3]["click_groups"],3)   # one KPI card per click
        self.assertEqual(by[4]["click_groups"],2)   # data, then takeaway
        self.assertEqual(by[5]["click_groups"],5)   # notes walk steps, then result

    def test_simulated_states_start_hidden_and_end_fully_visible(self):
        root=slide_root(self.out,"ppt/slides/slide2.xml")
        states,_=anim.simulate_states(root)
        self.assertEqual(states[0]["hidden_paragraphs"],{("3",i) for i in range(4)})
        self.assertEqual(states[-1]["hidden_paragraphs"],set())
        root=slide_root(self.out,"ppt/slides/slide4.xml")
        chart=[c for c in effect_ctns(root) if c.find(".//a:chart",NS) is not None]
        self.assertEqual(len(chart),2)  # two series, sequential
        self.assertIsNotNone(root.find(".//p:bldGraphic/p:bldSub",NS))

    def test_v04_plan_runs_through_canonical_writer_sequentially(self):
        from test_generic_report_motion import generic_director
        from inspect_existing_deck import inspect_existing_deck
        plan=generic_director(inspect_existing_deck(H001))
        out=self.td/"h001.pptx"
        report=md.apply(H001,plan,out)
        self.assertTrue(report["ok"],report["problems"])
        root=slide_root(out,"ppt/slides/slide1.xml")
        group=root.find(".//p:cTn[@nodeType='mainSeq']/p:childTnLst/p:par/p:cTn",NS)
        delays=[int(b.find("p:stCondLst/p:cond",NS).get("delay")) for b in group.findall("p:childTnLst/p:par/p:cTn",NS)]
        self.assertEqual(len(delays),3)
        self.assertEqual(delays,sorted(delays))
        self.assertGreater(delays[1],0)

    def test_counters_hide_proxies_and_keep_source_text(self):
        plan=md.draft(self.model,counters=True)
        out=self.td/"counters.pptx"
        report=md.apply(FIXTURE,plan,out)
        self.assertTrue(report["ok"],report["problems"])
        counter=report["receipts"][[r["slide"] for r in report["receipts"]].index(3)]["counters"]
        self.assertEqual(len(counter),3)
        root=slide_root(out,"ppt/slides/slide3.xml")
        states,_=anim.simulate_states(root)
        proxies={c.get("id") for c in root.iter(anim.q("cNvPr")) if c.get("name","").startswith("__counter_")}
        self.assertTrue(proxies)
        self.assertTrue(proxies<=states[0]["hidden_objects"])
        self.assertTrue(proxies<=states[-1]["hidden_objects"])

    def test_extend_existing_timing_and_replace_requires_reason(self):
        plan=copy.deepcopy(self.plan)
        plan["slides"]=[{
            "source_index":6,"role":"evidence","objective":"Show the picture after the feedback points.",
            "beats":[{"id":"pic","purpose":"Reveal supporting picture.","operation":"reveal",
                      "targets":["Feedback Picture"],"reuse_existing":True,"same_slide":True,
                      "timing_intent":"on-click","effect":"zoom"}],
            "click_beats":[{"id":"c","purpose":"Picture.","motion_beats":["pic"],"stable_state":"All visible.",
                            "pause_after":"slide-complete","boundary_reason":"After the existing points."}],
            "components":[]}]
        out=self.td/"extend.pptx"
        report=md.apply(FIXTURE,plan,out)
        self.assertTrue(report["ok"],report["problems"])
        self.assertEqual(report["slides"][5]["click_groups"],3)
        plan["slides"][0]["existing_timing"]="replace"
        with self.assertRaises(ValueError):
            md.apply(FIXTURE,plan,self.td/"replace.pptx")

    def test_refuses_stale_plan_and_overwrite(self):
        plan=copy.deepcopy(self.plan)
        plan["source"]["pptx_sha256"]="0"*64
        with self.assertRaises(ValueError):
            md.apply(FIXTURE,plan,self.td/"stale.pptx")
        with self.assertRaises(ValueError):
            md.apply(FIXTURE,self.plan,self.out)

    def test_v05_validator_rejects_unknown_effect(self):
        plan=copy.deepcopy(self.plan)
        plan["slides"][0]["beats"][0]["effect"]="sparkle-explosion"
        errors=validate_director(plan,self.model["inventory"])
        self.assertTrue(any("unsupported effect" in e for e in errors))

    @unittest.skipUnless(HAS_SOFFICE,"LibreOffice Impress + ImageMagick not installed")
    def test_storyboard_and_libreoffice_crosscheck(self):
        from lo_timing_crosscheck import crosscheck
        sheets=md.storyboard(self.out,self.td/"sb",[4])
        self.assertEqual(len(sheets),1)
        result=crosscheck(self.out)
        slide4=next(s for s in result["slides"] if s["slide"]==4)
        begins=[e["block_begin"] for e in slide4["effects"]]
        self.assertEqual(begins[:2],["0s","0.8s"])
        self.assertTrue(all(e["preset_class"]=="entrance" for e in slide4["effects"]))


if __name__=="__main__":
    unittest.main()
