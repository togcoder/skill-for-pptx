import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import motion_components as mc
import motion_director as md
import motion_engine as me
import motion_script as ms
import pptx_animator as anim
from validate_director_plan import validate as validate_director

FX=ROOT/"tests"/"fixtures"
SHOWCASE=FX/"motion_showcase_deck.pptx"
REPORT=FX/"report_deck.pptx"
ESSAY=FX/"essay_outline_deck.pptx"
NS=anim.NS


def slide_root(path,part):
    with ZipFile(path) as z:
        return E.fromstring(z.read(part))


def fresh(slide):
    return {o["id"]:me.fresh_state() for o in slide["objects"]}


class LoopWriterTests(unittest.TestCase):
    def test_loop_attributes_and_until_next_click(self):
        root=slide_root(SHOWCASE,"ppt/slides/slide2.xml")
        anim.apply_timeline(root,[{"id":"c","effects":[
            {"preset":"grow","spid":"3","trigger":"click","duration_ms":800,"ratio":1.04,
             "loop":{"repeat":"indefinite","auto_reverse":True}},
            {"preset":"spin","spid":"4","trigger":"with","duration_ms":20000,"by_deg":360,
             "loop":{"repeat":"until-next-click"}},
            {"preset":"path","spid":"5","trigger":"with","duration_ms":500,
             "anchored":[{"x":0,"y":0},{"x":0.01,"y":0}],"loop":{"repeat":3,"auto_reverse":True}},
            {"preset":"fade","spid":"6","trigger":"after","duration_ms":300}]}])
        ctns=[c for c in root.iter(anim.q("cTn")) if c.get("presetClass")]
        self.assertEqual((ctns[0].get("repeatCount"),ctns[0].get("autoRev")),("indefinite","1"))
        self.assertEqual(ctns[1].get("repeatCount"),"indefinite")
        self.assertEqual(ctns[1].find("p:endCondLst/p:cond",NS).get("evt"),"onNext")
        self.assertEqual(ctns[2].get("repeatCount"),"3000")
        # The after-previous block waits one loop cycle, not forever.
        blocks=root.findall(".//p:cTn[@nodeType='mainSeq']/p:childTnLst/p:par/p:cTn/p:childTnLst/p:par/p:cTn",NS)
        self.assertEqual(blocks[1].find("p:stCondLst/p:cond",NS).get("delay"),"20000")
        groups,_=me.effects_from_slide(root)
        loops=[e.get("loop") for e in groups[0]]
        self.assertEqual(loops[:3],[{"repeat":"indefinite","auto_reverse":True},
                                    {"repeat":"until-next-click","auto_reverse":False},
                                    {"repeat":3,"auto_reverse":True}])

    def test_simulated_loop_moves_then_rests(self):
        eff={"preset":"grow","spid":"1","trigger":"click","duration_ms":1000,"ratio":1.1,
             "loop":{"repeat":"indefinite","auto_reverse":True}}
        st={"1":me.fresh_state()}
        mid=me.state_at(st,[eff],1000)["1"]["scale"]
        self.assertAlmostEqual(mid,1.1,places=3)
        self.assertAlmostEqual(me.advance(st,[eff])["1"]["scale"],1.0)


class EngineLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(SHOWCASE)
        cls.s2=cls.model["slides"][1]
        cls.tok={o["name"]:o for o in cls.s2["objects"]}

    def test_overshoot_and_anticipate_end_on_target(self):
        a=self.tok["Stage Plan"]
        st=fresh(self.s2)
        effects=me.compile_track({"keyframes":[{"t":0},{"t":1000,"dx":0.1,"overshoot":0.1,"anticipate":0.05}]},
                                 a,self.tok,st[a["id"]],"x")
        paths=[e for e in effects if e["preset"]=="path"]
        self.assertEqual(len(paths),3)
        self.assertLess(paths[0]["anchored"][-1]["x"],0)          # wind-up backwards
        self.assertGreater(paths[1]["anchored"][-1]["x"],0.1)      # overshoot
        self.assertAlmostEqual(paths[2]["anchored"][-1]["x"],0.1)  # settle
        self.assertEqual(sum(e["duration_ms"] for e in paths),1000)

    def test_followers_track_their_leader(self):
        plan_obj,label=self.tok["Stage Plan"],self.tok["Hub"]
        st=fresh(self.s2)
        effects=me.compile_choreography("tracks",[plan_obj],st,self.tok,"b",
            {"attach":{"Stage Plan":["Hub"]}},
            [{"target":plan_obj,"keyframes":[{"t":0},{"t":600,"dx":0.05,"dy":0.02,"scale":1.2}]}])
        end=me.advance(st,effects)
        lead,follow=end[plan_obj["id"]],end[label["id"]]
        la,fa=me.authored(plan_obj),me.authored(label)
        # Relative offset scales with the leader.
        rel0=(fa["cx"]-la["cx"],fa["cy"]-la["cy"])
        rel1=((fa["cx"]+follow["dx"])-(la["cx"]+lead["dx"]),(fa["cy"]+follow["dy"])-(la["cy"]+lead["dy"]))
        self.assertAlmostEqual(rel1[0],rel0[0]*1.2,places=6)
        self.assertAlmostEqual(rel1[1],rel0[1]*1.2,places=6)
        self.assertAlmostEqual(follow["scale"],1.2)

    def test_ambient_recipes_loop(self):
        st=fresh(self.s2)
        objs=[self.tok["Hub"]]
        for recipe in ("breathe","drift","spin-loop"):
            effects=me.compile_choreography(recipe,objs,st,self.tok,"a",{})
            self.assertTrue(all(e.get("loop") for e in effects),recipe)
        ripple=me.compile_choreography("ripple",[self.tok["Stage Plan"],self.tok["Stage Do"]],st,self.tok,"r",{})
        self.assertEqual([e["delay_ms"] for e in ripple],[0,120])


class ComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(SHOWCASE)

    def test_insert_components_in_deck_style(self):
        s2=self.model["slides"][1]
        root=slide_root(SHOWCASE,s2["part"])
        size=self.model["slide_size_emu"]
        style=mc.deck_style(self.model)
        self.assertEqual(style["accent"],"0F9D8A")
        created=mc.insert(root,s2,[
            {"id":"ring","kind":"orbit-ring","anchors":["Stage Plan","Stage Do","Stage Check","Stage Act"]},
            {"id":"halo","kind":"halo","anchors":["Stage Plan"]},
            {"id":"note","kind":"callout","text":"85% of pilots hit target"},
            {"id":"b1","kind":"badge","anchors":["Stage Do"],"text":"2"},
            {"id":"arr","kind":"arrow","anchors":["Stage Plan","Stage Do"]},
            {"id":"frame","kind":"highlight-frame","anchors":["Hub"]}],style,size["width"],size["height"])
        names=[c["name"] for c in created]
        self.assertEqual(names[0],"__gen_orbit-ring_ring")
        tree=root.find("p:cSld/p:spTree",NS)
        order=[c.find("./*/p:cNvPr",NS).get("name") for c in tree if c.find("./*/p:cNvPr",NS) is not None]
        self.assertLess(order.index("__gen_orbit-ring_ring"),order.index("Title 1"))  # background behind
        self.assertGreater(order.index("__gen_callout_note"),order.index("Stage Act"))  # foreground on top
        ring=created[0]["geometry"]
        aspect=size["width"]/size["height"]
        r=ring["h"]/2
        cx,cy=ring["x"]+ring["w"]/2,ring["y"]+ring["h"]/2
        for name in ("Stage Plan","Stage Do"):
            o=next(o for o in s2["objects"] if o["name"]==name)
            ox,oy=me.authored(o)["cx"],me.authored(o)["cy"]
            self.assertAlmostEqual(math.hypot((ox-cx)*aspect,oy-cy),r,places=2)
        self.assertEqual(root.find(".//p:cxnSp//a:tailEnd",NS).get("type"),"triangle")

    def test_cinematic_draft_layers(self):
        plan=md.draft(self.model,style="cinematic")
        self.assertEqual(validate_director(plan,self.model["inventory"]),[])
        by={s["source_index"]:s for s in plan["slides"]}
        self.assertEqual({c["id"] for c in by[2]["components"]},{"orbit","halo"})
        layers={b.get("layer") for b in by[2]["beats"]}
        self.assertTrue({"secondary","ambient"}<=layers)
        self.assertEqual([c["id"] for c in by[6]["components"]],["halo"])  # 2x2 matrix: tour halo, no orbit ring
        # Existing token on the order journey is reused, nothing generated.
        self.assertTrue(all(b.get("recipe")!="travel" or b["targets"][0]=="Order token" for b in by[5]["beats"]))
        report_model=md.deck_model(REPORT)
        rp=md.draft(report_model,style="cinematic")
        s5=next(s for s in rp["slides"] if s["source_index"]==5)
        # T028: the takeaway also gets a highlighter sweep; the rail moves above
        # the steps because the band below is taken by the result line.
        self.assertEqual({c["id"] for c in s5["components"]},{"track","token","marker3"})
        track=next(c for c in s5["components"] if c["id"]=="track")
        self.assertLess(track["generate"]["offset_y"],0)
        with tempfile.TemporaryDirectory() as td:
            report=md.apply(REPORT,rp,Path(td)/"o.pptx")
        self.assertTrue(report["ok"],report["problems"])
        self.assertEqual(report["warnings"],[])
        s5r=next(s for s in report["slides"] if s["slide"]==5)
        self.assertEqual(sorted(s5r["generated"]),["__gen_highlight_marker3","__gen_token_token","__gen_track-line_track"])

    def test_loop_guard_blocks_later_motion_on_looping_property(self):
        plan=md.draft(self.model,style="cinematic")
        s2=next(s for s in plan["slides"] if s["source_index"]==2)
        s2["beats"].append({"id":"bad","purpose":"Grow the ring later.","operation":"choreography","targets":["orbit"],
                            "reuse_existing":True,"same_slide":True,"timing_intent":"with-previous","recipe":"tracks",
                            "tracks":[{"target":"orbit","keyframes":[{"t":0},{"t":400,"rotate":30}]}]})
        s2["click_beats"][-1]["motion_beats"].append("bad")
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError) as cm:
                md.apply(SHOWCASE,plan,Path(td)/"x.pptx")
        self.assertIn("already looping",str(cm.exception))

    def test_validator_layer_rules(self):
        plan=md.draft(self.model,style="cinematic")
        s2=next(s for s in plan["slides"] if s["source_index"]==2)
        spin=next(b for b in s2["beats"] if b.get("recipe")=="spin-loop")
        spin["layer"]="primary"
        self.assertTrue(any("ambient" in e for e in validate_director(plan,self.model["inventory"])))


class ScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.showcase=md.deck_model(SHOWCASE)

    def test_parse_cues_headings_and_intro(self):
        secs=ms.parse_script("## Slide 2: Cycle\nIntro line.\n[click] First.\nmore of first\n\n[nhấp] Hai.\n"
                             "Trang 3: Thân bài\nPara one.\n\nPara two.\n# Market quadrants\n>> Grow.")
        self.assertEqual([s["slide"] for s in secs],[2,3,None])
        self.assertEqual(secs[0]["intro"],"Intro line.")
        self.assertEqual([x["text"] for x in secs[0]["segments"]],["First. more of first","Hai."])
        self.assertEqual([x["cue"] for x in secs[1]["segments"]],[False,False])
        self.assertEqual(ms.match_sections(secs,self.showcase)[6]["title"],"Market quadrants")

    def test_generated_script_round_trips_to_same_rhythm(self):
        model=md.deck_model(REPORT)
        draft=md.draft(model,style="cinematic")
        text=ms.script_from_plan(model,draft)
        plan,report=ms.plan_from_script(model,text,style="cinematic")
        self.assertEqual(validate_director(plan,model["inventory"]),[])
        want={s["source_index"]:len(s["click_beats"]) for s in draft["slides"]}
        got={s["source_index"]:len(s["click_beats"]) for s in plan["slides"]}
        self.assertEqual(got,want)
        self.assertTrue(all(c.get("narration") for s in plan["slides"] for c in s["click_beats"]))

    def test_human_script_drives_the_cycle_tour(self):
        plan,report=ms.plan_from_script(self.showcase,(FX/"showcase_script.md").read_text(),style="cinematic")
        self.assertEqual(validate_director(plan,self.showcase["inventory"]),[])
        s2=next(s for s in plan["slides"] if s["source_index"]==2)
        beats={b["id"]:b for b in s2["beats"]}
        per_click=[[beats[m] for m in c["motion_beats"]] for c in s2["click_beats"]]
        focus=[next((b["targets"][0] for b in bs if b.get("recipe")=="spotlight"),None) for bs in per_click]
        self.assertEqual(focus,[None,"Stage Plan","Stage Do","Stage Check","Stage Act",None])
        self.assertTrue(any(b.get("recipe")=="release" for b in per_click[5]))
        self.assertTrue(s2["click_beats"][5]["narration"].startswith("And then the cycle"))
        self.assertEqual(s2["intro_narration"],"This is how we improve every quarter.")
        gaps=report[2]["gaps"]
        self.assertEqual([g["values"] for g in gaps if g["kind"]=="number-not-on-slide"],[["85"]])
        s6=next(s for s in plan["slides"] if s["source_index"]==6)
        b6={b["id"]:b for b in s6["beats"]}
        last=[b6[m] for m in s6["click_beats"][-2]["motion_beats"]]
        self.assertEqual(next(b for b in last if b.get("recipe")=="spotlight")["targets"][0],"Quadrant Explore")
        # The script ends mid-tour: an unscripted closing click settles the
        # slide (release + halo out) so nothing snaps back at the next slide.
        settle=[b6[m] for m in s6["click_beats"][-1]["motion_beats"]]
        self.assertEqual({b.get("recipe") or b["operation"] for b in settle},{"release","exit"})
        self.assertEqual(s6["click_beats"][-1]["narration"],"")
        self.assertIn("settle-click-without-line",[g["kind"] for g in report[6]["gaps"]])

    def test_vietnamese_paraphrase_and_gap_callout(self):
        model=md.deck_model(ESSAY)
        plan,report=ms.plan_from_script(model,(FX/"essay_script_vi.md").read_text(),fill_gaps=True)
        self.assertEqual(validate_director(plan,model["inventory"]),[])
        by={s["source_index"]:s for s in plan["slides"]}
        self.assertEqual(len(by[2]["click_beats"]),2)
        first=[b for b in by[2]["beats"] if b["id"] in by[2]["click_beats"][0]["motion_beats"]]
        self.assertEqual(first[0]["targets"],["TextBox 2","TextBox 3"])
        callouts=[c for c in by[3]["components"] if c["generate"]["kind"]=="callout"]
        self.assertEqual(len(callouts),1)
        self.assertIn("5",callouts[0]["generate"]["text"])
        self.assertTrue(any(g["kind"]=="placed-by-order" for g in report[4]["gaps"]))
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"vi.pptx"
            result=md.apply(ESSAY,plan,out)
            self.assertTrue(result["ok"],result["problems"])
            notes=ms.write_notes(out,plan,out)
            # python-pptx decks without a notes master: skipped, never broken.
            self.assertEqual(notes["notes_written"],[])
            self.assertEqual(sorted(notes["skipped_no_notes_master"]),[2,3,4])
            self.assertTrue(md.verify(ESSAY,out,allow_notes=True)["ok"])

    def test_notes_are_appended_or_created(self):
        plan,_=ms.plan_from_script(self.showcase,(FX/"showcase_script.md").read_text(),style="cinematic")
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"n.pptx"
            md.apply(SHOWCASE,plan,out)
            notes=ms.write_notes(out,plan,out)
            self.assertEqual(sorted(notes["notes_written"]),[2,5,6])
            self.assertEqual(len(notes["notes_slides_created"]),1)  # slide 6 had no notes
            check=md.verify(SHOWCASE,out,allow_notes=True)
            self.assertTrue(check["ok"],check["problems"])
            self.assertFalse(md.verify(SHOWCASE,out)["ok"])  # notes changes need explicit allowance
            after=md.deck_model(out)
            self.assertTrue(after["slides"][5]["notes"].startswith("[Motion script]"))
            self.assertIn("Introduce the cycle",after["slides"][1]["notes"])  # original notes kept

    def test_unexpected_new_objects_still_fail_verify(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"x.pptx"
            plan=md.draft(self.showcase,style="cinematic")
            md.apply(SHOWCASE,plan,out)
            data={}
            with ZipFile(out) as z:
                for n in z.namelist():
                    data[n]=z.read(n)
            part="ppt/slides/slide2.xml"
            data[part]=data[part].replace(b'name="__gen_halo_halo"',b'name="Mystery"')
            bad=Path(td)/"bad.pptx"
            from zipfile import ZIP_DEFLATED
            with ZipFile(bad,"w",ZIP_DEFLATED) as z:
                for n,d in data.items():
                    z.writestr(n,d)
            self.assertTrue(any("unexpected new objects" in p for p in md.verify(SHOWCASE,bad)["problems"]))


if __name__=="__main__":
    unittest.main()


class HighlightPlacementTests(unittest.TestCase):
    """T030: PowerPoint render showed the marker above a centred, wrapped takeaway."""

    def test_marker_sits_on_centred_wrapped_text(self):
        import motion_components as mc
        takeaway={"geometry":{"x":0.66,"y":0.29,"w":0.29,"h":0.39},"text_anchor":"ctr","max_font_pt":30,
                  "text":"Kênh trực tuyến tăng gấp 2,5 lần trong sáu tháng.",
                  "paragraphs":[{"text":"Kênh trực tuyến tăng gấp 2,5 lần trong sáu tháng."}]}
        x,y,w,h=mc.layout({"kind":"highlight"},[takeaway],{"objects":[takeaway]},16/9)
        g=takeaway["geometry"]
        self.assertGreater(y,g["y"]+0.05)           # not glued to the box top
        self.assertLess(abs((y+h/2)-(g["y"]+g["h"]/2)),0.03)  # centred like the text
        self.assertGreater(h,0.1)                    # covers the wrapped lines

    def test_single_top_line_marker_unchanged_in_spirit(self):
        import motion_components as mc
        label={"geometry":{"x":0.1,"y":0.2,"w":0.6,"h":0.2},"text_anchor":"t","max_font_pt":24,
               "text":"Short takeaway","paragraphs":[{"text":"Short takeaway"}]}
        x,y,w,h=mc.layout({"kind":"highlight"},[label],{"objects":[label]},16/9)
        self.assertLess(y,0.22)
        self.assertLess(w,0.3)
