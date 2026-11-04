"""T063: Forge debt users see — type scale, counter stack, highlight, settle."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import design_critic as dc
import morph_studio as ms
import motion_components as mc
import motion_engine as me
import slide_forge as sf

EXAMPLES=ROOT/"examples"/"pptx"/"forge"


class TypeScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.built={}
        for path in sorted(EXAMPLES.glob("*.json")):
            out=Path(cls.tmp.name)/(path.stem+".pptx")
            verdict=sf.build(json.loads(path.read_text(encoding="utf-8")),out)
            assert verdict["ok"],(path.name,verdict["errors"])
            cls.built[path.stem]=out

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_example_uses_three_to_six_sizes_and_no_old_debt(self):
        for name,path in self.built.items():
            critique=dc.critique(path)
            codes={i["code"] for i in critique["issues"] if i["severity"]=="warn"}
            self.assertNotIn("TYP-SIZES",codes,name)
            self.assertNotIn("MOT-SETTLE",codes,name)
            self.assertTrue(3<=len(critique["deck"]["type_sizes"])<=6,
                            (name,critique["deck"]["type_sizes"]))

    def test_office_kit_type_scale_is_the_source(self):
        kit=next(k for k in json.loads(sf.KITS_PATH.read_text(encoding="utf-8"))["themes"]
                 if k["name"]=="Slice")
        scale=sf.deck_type_scale(kit,{"slides":[{"layout":"kpis"}]})
        self.assertEqual(scale["title"],int(kit["type_scale_pt"]["title"]))
        self.assertEqual(scale["subhead"],int(kit["type_scale_pt"]["body_l1"]))
        self.assertLessEqual(scale["small"],max(12,int(kit["type_scale_pt"]["body_l4"])))
        self.assertIn("display",scale)  # a KPI deck gets the design-system kpi_stat token

    def test_no_kpi_deck_does_not_add_display(self):
        spec={"slides":[{"layout":"section","title":"Only a section"}]}
        self.assertNotIn("display",sf.deck_type_scale(None,spec))


class CounterStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        spec={
            "theme":"paper",
            "motion":{"style":"modern","morph":False},
            "slides":[{"layout":"kpis","title":"Numbers","items":[
                {"value":"32%","label":"online orders"},{"value":"1.250","label":"new customers"}]}],
        }
        cls.out=Path(cls.tmp.name)/"kpi.pptx"
        cls.verdict=sf.build(spec,cls.out)
        with ZipFile(cls.out) as z:
            cls.root=E.fromstring(z.read("ppt/slides/slide1.xml"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def shapes(self):
        ns={"p":mc.P}
        return self.root.findall("p:cSld/p:spTree/p:sp",ns)

    def text(self,shape):
        return "".join(t.text or "" for t in shape.findall(".//a:t",{"a":mc.A}))

    def test_final_source_is_topmost_and_proxies_sit_below_it(self):
        shapes=self.shapes()
        source=next(s for s in shapes if s.find("p:nvSpPr/p:cNvPr",{"p":mc.P}).get("name")=="KPI value 1")
        sid=source.find("p:nvSpPr/p:cNvPr",{"p":mc.P}).get("id")
        proxies=[s for s in shapes if s.find("p:nvSpPr/p:cNvPr",{"p":mc.P}).get("name","").startswith(f"__counter_{sid}_")]
        self.assertTrue(proxies)
        stack=[s for s in shapes if s is source or s in proxies]
        self.assertIs(stack[-1],source)
        self.assertEqual(self.text(source),"32%")

    def test_source_is_painted_with_the_card_colour(self):
        source=next(s for s in self.shapes()
                    if s.find("p:nvSpPr/p:cNvPr",{"p":mc.P}).get("name")=="KPI value 1")
        fill=source.find("p:spPr/a:solidFill/a:srgbClr",{"p":mc.P,"a":mc.A})
        self.assertIsNotNone(fill)
        self.assertEqual(fill.get("val"),"FFFFFF")  # paper surface behind the KPI


class HighlightAlignmentTests(unittest.TestCase):
    def make(self,align):
        obj={"geometry":{"x":0.7,"y":5.5,"w":11.93,"h":0.8},"filled":False,"text_anchor":"ctr",
             "max_font_pt":28,"text":"Mỗi giai đoạn kéo dài một quý.",
             "paragraphs":[{"text":"Mỗi giai đoạn kéo dài một quý.","align":align,
                            "font":"Segoe UI","size_pt":28,"bold":True}]}
        return obj

    def test_marker_is_symmetric_under_centred_text(self):
        obj=self.make("ctr")
        tb=me.text_block(obj)
        g=mc.layout({"kind":"highlight"},[obj],{"objects":[obj]},16/9)
        self.assertAlmostEqual((g[0]+g[2]/2),((tb[0]+tb[2])/2),places=3)
        self.assertGreater(g[0],obj["geometry"]["x"]+1.0)  # not pinned to the box edge

    def test_marker_ends_at_right_aligned_text(self):
        obj=self.make("r")
        tb=me.text_block(obj)
        g=mc.layout({"kind":"highlight"},[obj],{"objects":[obj]},16/9)
        self.assertAlmostEqual(g[0]+g[2],tb[2]-0.004,places=3)
        self.assertGreater(g[0],obj["geometry"]["x"]+4.0)


class SettleTests(unittest.TestCase):
    def test_ken_burns_returns_to_the_authored_frame(self):
        obj={"id":"7","name":"Photo","token":"Photo","kind":"picture",
             "geometry":{"x":0.1,"y":0.1,"w":0.4,"h":0.4},"text":"","paragraphs":[]}
        states={obj["id"]:me.fresh_state()}
        effects=me.compile_choreography("ken-burns",[obj],states,{},"b1",
                                        {"duration_ms":6000,"scale":1.06,"pulse_stops":False})
        end=me.advance(states,effects)[obj["id"]]
        self.assertAlmostEqual(end["dx"],0.0)
        self.assertAlmostEqual(end["dy"],0.0)
        self.assertAlmostEqual(end["scale"],1.0)

    def test_token_is_authored_at_its_last_stop(self):
        token={"id":"1","name":"Marker","token":"Marker","kind":"shape",
               "geometry":{"x":0.785,"y":0.585,"w":0.03,"h":0.03},"text":"","paragraphs":[]}
        first={"id":"2","name":"Step 1","token":"Step 1","kind":"shape",
               "geometry":{"x":0.2,"y":0.5,"w":0.2,"h":0.2},"text":"","paragraphs":[]}
        last={"id":"3","name":"Step 2","token":"Step 2","kind":"shape",
              "geometry":{"x":0.7,"y":0.5,"w":0.2,"h":0.2},"text":"","paragraphs":[]}
        states={o["id"]:me.fresh_state() for o in (token,first,last)}
        effects=me.compile_choreography("travel",[token,first,last],states,{},"b1",
                                        {"author_at_last":True,"dwell_ms":0,"pulse_stops":False})
        end=me.advance(states,effects)[token["id"]]
        self.assertAlmostEqual(end["dx"],0.0)
        self.assertAlmostEqual(end["dy"],0.0)
        self.assertAlmostEqual(me.authored(token)["cx"],0.8)


if __name__=="__main__":
    unittest.main()
