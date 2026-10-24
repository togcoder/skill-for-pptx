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

import morph_studio as mstu
import motion_components as mc
import motion_director as md
import motion_engine as me
import pptx_animator as anim
from validate_director_plan import validate as validate_director

FX=ROOT/"tests"/"fixtures"
SHOWCASE=FX/"motion_showcase_deck.pptx"
REPORT=FX/"report_deck.pptx"
ESSAY=FX/"essay_outline_deck.pptx"
NS=anim.NS
HAS_PREVIEW=all(shutil.which(t) for t in ("soffice","pdftoppm","convert","montage"))


def names(pkg,part):
    return [p.get("name") for p in pkg.xml(part).iter(f"{{{anim.P}}}cNvPr")]


class PackageTests(unittest.TestCase):
    def test_duplicate_slide_copies_charts_and_drops_notes(self):
        pkg=mstu.Package(REPORT)
        order=pkg.slides()
        new=pkg.duplicate_slide(order[3],order[3],"probe")
        after=pkg.slides()
        self.assertEqual(after.index(new),4)
        root=pkg.xml(new)
        self.assertEqual(root.find("p:cSld",NS).get("name"),"__scene:probe")
        rels={r.get("Type").rsplit("/",1)[1]:r.get("Target") for r in pkg.rels(new)}
        self.assertNotIn("notesSlide",rels)
        src_chart=[r.get("Target") for r in pkg.rels(order[3]) if r.get("Type").endswith("/chart")][0]
        self.assertNotEqual(rels["chart"],src_chart)  # a part of its own
        self.assertIn(pkg.resolve(new,rels["chart"]),pkg.data)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"d.pptx"
            pkg.save(out)
            model=md.deck_model(out)
            self.assertEqual(len(model["slides"]),8)
            self.assertTrue(model["slides"][4]["scene"])


class TechniqueTests(unittest.TestCase):
    def test_continuity_pairs_titles_and_stages_off_slide(self):
        pkg=mstu.Package(SHOWCASE)
        order=pkg.slides()
        receipt=[]
        mstu.continuity(pkg,order[1],order[2],"byWord",receipt=receipt)
        mstu.continuity(pkg,order[2],order[3],receipt=receipt)
        t1=[n for n in names(pkg,order[1]) if n and n.startswith("!!m")]
        t3=[n for n in names(pkg,order[3]) if n and n.startswith("!!m")]
        self.assertTrue(t1 and t1[0] in t3)  # one title identity across three slides
        alt=pkg.xml(order[2]).find(f".//{{{anim.P159}}}morph")
        self.assertEqual(alt.get("option"),"byWord")
        staged=receipt[0]["staged"]
        self.assertTrue(staged)
        size=md.deck_model(SHOWCASE)["slide_size_emu"]
        self.assertEqual({st["on"] for st in staged},{order[1],order[2]})  # fly in and fly out
        for st in staged:
            other=order[2] if st["on"]==order[1] else order[1]
            node=next(n for n in mstu.shape_nodes(pkg.xml(st["on"])).values()
                      if n.find("./*/p:cNvPr",NS).get("name")==st["name"])
            x,y,w,h=mstu.box(mstu.xfrm_of(node))
            self.assertTrue(x+w<=0 or x>=size["width"] or y+h<=0 or y>=size["height"])
            self.assertIn(st["name"],names(pkg,other))

    def test_camera_zoom_frames_focus_and_scales_type(self):
        pkg=mstu.Package(SHOWCASE)
        order=pkg.slides()
        receipt=[]
        zoom,back=mstu.camera_zoom(pkg,order[5],"Quadrant Grow",fill=0.8,receipt=receipt,reason="t")
        root=pkg.xml(zoom)
        node=next(n for n in mstu.shape_nodes(root).values()
                  if n.find("./*/p:cNvPr",NS).get("name").endswith(
                      next(o for o in md.deck_model(SHOWCASE)["slides"][5]["objects"] if o["name"]=="Quadrant Grow")["id"]))
        x,y,w,h=mstu.box(mstu.xfrm_of(node))
        size=md.deck_model(SHOWCASE)["slide_size_emu"]
        self.assertAlmostEqual(h,size["height"]*0.8,delta=size["height"]*0.01)
        s=receipt[0]["scale"]
        sizes=[int(r.get("sz")) for r in node.iter(f"{{{anim.A}}}rPr") if r.get("sz")]
        self.assertTrue(sizes and all(abs(v-round(1800*s))<=1 for v in sizes))
        self.assertIsNotNone(pkg.xml(back).find(f".//{{{anim.P159}}}morph"))
        # Every object on the source and its zoom copy share one !! identity.
        self.assertEqual(sorted(n for n in names(pkg,order[5]) if n.startswith("!!")),
                         sorted(n for n in names(pkg,zoom) if n.startswith("!!")))

    def test_card_expand_and_pan(self):
        pkg=mstu.Package(REPORT)
        order=pkg.slides()
        new=mstu.card_expand(pkg,order[2],"KPI Card 1",reason="t")[0]
        kept=[n for n in names(pkg,new) if n]
        self.assertTrue(any(n.startswith("!!card") for n in kept))
        self.assertFalse(any("KPI Card 2" in n or n.endswith("-6") for n in kept if n.startswith("!!card")))
        pkg2=mstu.Package(REPORT)
        o2=pkg2.slides()
        added=mstu.pan(pkg2,o2[4],["Step 1","Step 2","Step 3"],reason="t")
        self.assertEqual(len(added),2)

    def test_card_expand_layout_and_exit_as_one_piece(self):
        pkg=mstu.Package(REPORT)
        order=pkg.slides()
        new=mstu.card_expand(pkg,order[2],"KPI Card 1",panel=(0.06,0.22,0.88,0.68),reason="t")[0]
        size=md.deck_model(REPORT)["slide_size_emu"]
        W,H=size["width"],size["height"]
        tree=[n.find("./*/p:cNvPr",NS).get("name") for n in mstu.shape_nodes(pkg.xml(new)).values()]
        self.assertTrue(all(n.startswith("!!card") for n in tree[-3:]))  # the growing card is on top
        boxes={n.find("./*/p:cNvPr",NS).get("name"):mstu.box(mstu.xfrm_of(n))
               for n in mstu.shape_nodes(pkg.xml(new)).values() if mstu.xfrm_of(n) is not None}
        card=boxes["!!card3-3"]
        self.assertEqual([round(v) for v in card],[round(0.06*W),round(0.22*H),round(0.88*W),round(0.68*H)])
        # Content keeps even margins: left offsets scale uniformly (not by the
        # wide horizontal stretch).
        src=md.deck_model(REPORT)["slides"][2]["objects"]
        g=lambda name:next(o["geometry"] for o in src if o["name"]==name)
        s=min(0.88/g("KPI Card 1")["w"],0.68/g("KPI Card 1")["h"])
        left=(boxes["!!card3-4"][0]-card[0])/W
        self.assertAlmostEqual(left,(g("KPI Value 1")["x"]-g("KPI Card 1")["x"])*s,places=3)
        for name in ("!!card3-4","!!card3-5"):
            b=boxes[name]
            self.assertTrue(card[0]<=b[0] and b[0]+b[2]<=card[0]+card[2]+1 and card[1]<=b[1]<=card[1]+card[3])
        # Leaving the panel: card, value and label fly off together.
        receipt=[]
        mstu.continuity(pkg,new,pkg.slides()[pkg.slides().index(new)+1],receipt=receipt)
        staged={st["source"]:st for st in receipt[0]["staged"]}
        self.assertEqual({staged[n]["side"] for n in ("!!card3-3","!!card3-4","!!card3-5")},{"bottom"})
        nxt=pkg.slides()[pkg.slides().index(new)+1]
        copies={n.find("./*/p:cNvPr",NS).get("name"):mstu.box(mstu.xfrm_of(n))
                for n in mstu.shape_nodes(pkg.xml(nxt)).values() if mstu.xfrm_of(n) is not None}
        shift={n:(copies[n][0]-boxes[n][0],copies[n][1]-boxes[n][1]) for n in ("!!card3-3","!!card3-4","!!card3-5")}
        self.assertEqual(len(set(shift.values())),1)

    def test_package_absolute_targets_and_selective_proposals(self):
        pkg=mstu.Package(REPORT)
        self.assertEqual(pkg.resolve("ppt/presentation.xml","/ppt/slides/slide1.xml"),"ppt/slides/slide1.xml")
        self.assertEqual(pkg.resolve("ppt/slides/slide1.xml","../media/image1.png"),"ppt/media/image1.png")
        plan=mstu.propose(md.deck_model(REPORT))
        # One idea per slide, about one per three slides: the headline KPI card
        # and the four-step row, not every card on the deck.
        self.assertEqual([(x["slide"],x["technique"]) for x in plan["suggestions"]],[(3,"card-expand"),(5,"pan")])
        self.assertEqual(plan["suggestions"][0]["card"],"KPI Card 1")

    def test_apply_plan_and_verify(self):
        plan=mstu.propose(md.deck_model(SHOWCASE))
        self.assertEqual([c["to_slide"] for c in plan["continuity"]],[2,3,4,5,6,7,8])
        self.assertTrue(any(s["technique"]=="camera-zoom" for s in plan["suggestions"]))
        plan["scenes"]=[{"slide":6,"technique":"camera-zoom","focus":"Quadrant Grow","reason":"explore Grow"}]
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"m.pptx"
            report=mstu.apply_plan(SHOWCASE,plan,out)
            self.assertTrue(report["ok"],report["problems"])
            self.assertEqual((report["output_slides"],report["scene_slides"]),(10,2))
            # The motion director leaves camera states alone.
            model=md.deck_model(out)
            draft=md.draft(model,style="cinematic")
            planned={s["source_index"] for s in draft["slides"]}
            scenes={s["index"] for s in model["slides"] if s["scene"]}
            self.assertFalse(planned&scenes)
            # A visible extra object would be rejected.
            pkg=mstu.Package(out)
            first=pkg.slides()[1]
            root=pkg.xml(first)
            node=copy.deepcopy(next(iter(mstu.shape_nodes(root).values())))
            node.find("./*/p:cNvPr",NS).set("id","999")
            node.find("./*/p:cNvPr",NS).set("name","Intruder")
            root.find("p:cSld/p:spTree",NS).append(node)
            pkg.put(first,root)
            bad=Path(td)/"bad.pptx"
            pkg.save(bad)
            self.assertFalse(mstu.verify_scenes(SHOWCASE,bad)["ok"])

    def test_scene_needs_reason(self):
        plan={"kind":"morph-scenes","scenes":[{"slide":6,"technique":"camera-zoom","focus":"Quadrant Grow"}]}
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                mstu.apply_plan(SHOWCASE,plan,Path(td)/"x.pptx")

    @unittest.skipUnless(HAS_PREVIEW,"LibreOffice Impress, poppler and ImageMagick required")
    def test_morph_preview(self):
        plan={"kind":"morph-scenes","continuity":[],"scenes":[{"slide":6,"technique":"camera-zoom",
                                                               "focus":"Quadrant Grow","reason":"t"}]}
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"m.pptx"
            mstu.apply_plan(SHOWCASE,plan,out)
            r=mstu.render_morph(out,7,Path(td)/"z.gif",steps=4)
            self.assertEqual(r["frames"],5)


class TextTrickTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=md.deck_model(REPORT)

    def plan_for(self,slide_index,beats,clicks,components=()):
        plan=md.draft(self.model)
        plan["slides"]=[{"source_index":slide_index,"role":"t","objective":"t","beats":beats,
                         "click_beats":clicks,"components":list(components)}]
        plan.pop("transitions",None)
        return plan

    def test_type_on_writes_letter_iteration(self):
        beat={"id":"t","purpose":"Typewriter the result.","operation":"reveal","targets":["Result"],
              "reuse_existing":True,"same_slide":True,"timing_intent":"on-click","effect":"type-on"}
        click=md._click("c","Type.",["t"],"Typed.","slide-complete","First.")
        plan=self.plan_for(5,[beat],[click])
        self.assertEqual(validate_director(plan,self.model["inventory"]),[])
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"o.pptx"
            report=md.apply(REPORT,plan,out)
            self.assertTrue(report["ok"],report["problems"])
            with ZipFile(out) as z:
                root=E.fromstring(z.read("ppt/slides/slide5.xml"))
        it=root.find(".//p:iterate",NS)
        self.assertEqual((it.get("type"),it.find("p:tmAbs",NS).get("val")),("lt","35"))
        groups,_=me.effects_from_slide(root)
        units=groups[0][0]["iterate"]["units"]
        self.assertEqual(units,len("Lead time fell from 9 days to 4 days.".replace(" ","")))
        self.assertEqual(me.group_duration(groups[0]),1+(units-1)*35)
        mid=me.state_at(me.initial_states(self.model["slides"][4]["objects"],groups),groups[0],300)
        rid=next(o["id"] for o in self.model["slides"][4]["objects"] if o["name"]=="Result")
        self.assertTrue(0<mid[rid]["text_frac"]<1)

    def test_rise_mask_matches_background_and_sits_above_text(self):
        comp=md._component("mask1","mask","hides the text before it rises","t",anchors=["Result"])
        beat={"id":"r","purpose":"Result rises from a line.","operation":"choreography","targets":["Result"],
              "reuse_existing":True,"same_slide":True,"timing_intent":"on-click","recipe":"rise",
              "motion_parameters":{"mask":"mask1","duration_ms":600}}
        click=md._click("c","Rise.",["r"],"Visible.","slide-complete","First.")
        plan=self.plan_for(5,[beat],[click],[comp])
        self.assertEqual(validate_director(plan,self.model["inventory"]),[])
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"o.pptx"
            report=md.apply(REPORT,plan,out)
            self.assertTrue(report["ok"],report["problems"])
            with ZipFile(out) as z:
                root=E.fromstring(z.read("ppt/slides/slide5.xml"))
            out_objects=md.deck_model(out)["slides"][4]["objects"]
        tree=[n.find("./*/p:cNvPr",NS).get("name") for n in root.find("p:cSld/p:spTree",NS)
              if n.find("./*/p:cNvPr",NS) is not None]
        self.assertEqual(tree.index("__gen_mask_mask1"),tree.index("Result")+1)
        mask=next(sp for sp in root.iter(f"{{{anim.P}}}sp")
                  if sp.find("p:nvSpPr/p:cNvPr",NS).get("name")=="__gen_mask_mask1")
        self.assertEqual(mask.find("p:spPr/a:solidFill/a:srgbClr",NS).get("val"),"FFFFFF")
        groups,_=me.effects_from_slide(root)
        states=me.advance(me.initial_states(out_objects,groups),groups[0])
        mask_id=root.find(".//p:cNvPr[@name='__gen_mask_mask1']",NS).get("id")
        self.assertFalse(states[mask_id]["visible"])  # mask is gone after the rise

    def test_rise_refuses_to_cover_other_objects(self):
        comp=md._component("mask1","mask","t","t",anchors=["Step 1"])
        beat={"id":"r","purpose":"Rise.","operation":"choreography","targets":["Step 1"],"reuse_existing":True,
              "same_slide":True,"timing_intent":"on-click","recipe":"rise","motion_parameters":{"mask":"mask1"}}
        click=md._click("c","Rise.",["r"],"Visible.","slide-complete","First.")
        plan=self.plan_for(5,[beat],[click],[comp])
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError) as cm:
                md.apply(REPORT,plan,Path(td)/"o.pptx")
        self.assertIn("would briefly cover",str(cm.exception))

    def test_rise_line_sits_under_the_text_lines(self):
        take=next(o for o in self.model["slides"][3]["objects"] if o["name"]=="Takeaway")
        x0,y0,x1,y1=me.text_block(take)
        g=take["geometry"]
        self.assertLess(y1,g["y"]+g["h"]*0.6)  # three 20 pt lines, not the whole box
        card=next(o for o in self.model["slides"][3]["objects"] if o["name"]=="Takeaway Card")
        self.assertEqual(me.text_block(card),(card["geometry"]["x"],card["geometry"]["y"],
                                              card["geometry"]["x"]+card["geometry"]["w"],
                                              card["geometry"]["y"]+card["geometry"]["h"]))
        plan=json.loads((ROOT/"experiments/T028-20261008-claude-morph-studio/report-director.json").read_text())
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"o.pptx"
            report=md.apply(REPORT,plan,out)
            self.assertTrue(report["ok"],report["problems"])
            slide=md.deck_model(out)["slides"][3]
            with ZipFile(out) as z:
                root=E.fromstring(z.read("ppt/slides/slide4.xml"))
        mask=next(o for o in slide["objects"] if o["name"]=="__gen_mask_mask4")["geometry"]
        self.assertTrue(y0<mask["y"]<g["y"]+g["h"])  # the line is inside the text box, under the lines
        self.assertGreaterEqual(mask["h"],y1-y0)    # tall enough to hide the text before it rises
        groups,_=me.effects_from_slide(root)
        tid=take["id"]
        click=next(gr for gr in groups if any(e["spid"]==tid for e in gr))
        states=me.initial_states(slide["objects"],groups)
        for gr in groups[:groups.index(click)]:
            states=me.advance(states,gr)
        start=me.state_at(states,click,int(me.group_duration(click))-650+5)  # the rise is the last 650 ms
        self.assertAlmostEqual(y0+start[tid]["dy"],mask["y"],delta=0.03)  # first line just under the line

    def test_cinematic_marks_conclusions_and_labels(self):
        plan=md.draft(self.model,style="cinematic")
        s5=next(s for s in plan["slides"] if s["source_index"]==5)
        self.assertIn("highlight",[c["generate"]["kind"] for c in s5["components"]])
        essay=md.deck_model(ESSAY)
        ep=md.draft(essay,style="cinematic")
        kinds=[c["generate"]["kind"] for s in ep["slides"] for c in s["components"]]
        self.assertGreaterEqual(kinds.count("underline"),4)
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/"o.pptx"
            r=md.apply(REPORT,plan,out)
            self.assertTrue(r["ok"],r["problems"])
            self.assertEqual(r["warnings"],[])
            with ZipFile(out) as z:
                root=E.fromstring(z.read("ppt/slides/slide5.xml"))
        tree=[n.find("./*/p:cNvPr",NS).get("name") for n in root.find("p:cSld/p:spTree",NS)
              if n.find("./*/p:cNvPr",NS) is not None]
        self.assertEqual(tree.index("Result"),tree.index(next(t for t in tree if t.startswith("__gen_highlight")))+1)


if __name__=="__main__":
    unittest.main()
