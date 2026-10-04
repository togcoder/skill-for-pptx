import sys
import unittest
from pathlib import Path

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from counter_component import counter_values, insert_counter_stack
from patch_existing_timeline import build_existing_timing, validate_patch_plan
from inspect_existing_deck import _timing_inventory, A, P

NS={"p":P,"a":A}


def number_slide_root(text="98.5%"):
    xml=f"""<p:sld xmlns:p="{P}" xmlns:a="{A}">
      <p:cSld><p:spTree>
        <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
        <p:grpSpPr/>
        <p:sp>
          <p:nvSpPr><p:cNvPr id="7" name="Hero KPI"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
          <p:spPr>
            <a:xfrm><a:off x="100" y="200"/><a:ext cx="300" cy="100"/></a:xfrm>
            <a:solidFill><a:srgbClr val="112233"/></a:solidFill>
          </p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p>
            <a:r><a:rPr lang="en-US" sz="3200" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{text}</a:t></a:r>
          </a:p></p:txBody>
        </p:sp>
      </p:spTree></p:cSld>
    </p:sld>"""
    return E.fromstring(xml.encode())


def counter_effect():
    return {
        "type":"number_counter",
        "target":{"source_id":"7","source_name":"Hero KPI"},
        "from_value":0,
        "to_value":98.5,
        "steps":7,
        "decimal_places":1,
        "prefix":"",
        "suffix":"%",
        "preserve_final_text":"98.5%",
        "filter":"fade",
    }


def counter_plan():
    return {
        "version":"0.4",
        "kind":"existing-deck-timeline-patch",
        "source_sha256":"0"*64,
        "slides":[{
            "source_index":1,
            "stages":[{
                "id":"count-kpi",
                "duration_ms":1200,
                "trigger":"on-click",
                "effects":[counter_effect()],
            }],
            "click_beats":[{"id":"beat-kpi","stages":["count-kpi"]}],
        }],
    }


class KpiCounterExecutionTests(unittest.TestCase):
    def test_counter_values_are_ordered_and_preserve_format(self):
        values=counter_values(0,98.5,7,1,suffix="%",source_text="98.5%")
        self.assertGreaterEqual(len(values),4)
        self.assertEqual(values[0],"0.0%")
        self.assertNotIn("98.5%",values)
        nums=[float(v[:-1]) for v in values]
        self.assertEqual(nums,sorted(nums))

    def test_counter_values_preserve_grouping_and_currency(self):
        values=counter_values(0,12345,6,0,prefix="$",source_text="$12,345")
        self.assertTrue(all(v.startswith("$") for v in values))
        self.assertTrue(any("," in v for v in values if len(v)>4))
        self.assertNotIn("$12,345",values)

    def test_counter_stack_clones_source_style_but_not_source_text(self):
        root=number_slide_root()
        effect=counter_effect()
        component=insert_counter_stack(root,effect)
        tree=root.find("p:cSld/p:spTree",NS)
        shapes=tree.findall("p:sp",NS)
        self.assertEqual(component["proxy_count"],len(shapes)-1)
        source=next(s for s in shapes if s.find("p:nvSpPr/p:cNvPr",NS).get("id")=="7")
        source_text="".join(t.text or "" for t in source.findall(".//a:t",NS))
        self.assertEqual(source_text,"98.5%")
        source_xfrm=E.tostring(source.find("p:spPr/a:xfrm",NS))
        source_fill=E.tostring(source.find("p:spPr/a:solidFill",NS))
        ids=set()
        for proxy in component["proxies"]:
            node=next(s for s in shapes if s.find("p:nvSpPr/p:cNvPr",NS).get("id")==proxy["source_id"])
            props=node.find("p:nvSpPr/p:cNvPr",NS)
            ids.add(props.get("id"))
            self.assertTrue(props.get("name").startswith("__counter_7_"))
            self.assertEqual(E.tostring(node.find("p:spPr/a:xfrm",NS)),source_xfrm)
            self.assertEqual(E.tostring(node.find("p:spPr/a:solidFill",NS)),source_fill)
        self.assertEqual(len(ids),component["proxy_count"])
        # Topmost edit-view proxy is the first counter value.
        top=shapes[-1]
        top_text="".join(t.text or "" for t in top.findall(".//a:t",NS))
        self.assertEqual(top_text,component["proxies"][0]["text"])

    def test_v04_counter_plan_validates(self):
        self.assertEqual(validate_patch_plan(counter_plan()),[])

    def test_counter_requires_v04(self):
        plan=counter_plan()
        plan["version"]="0.3"
        self.assertTrue(any("requires patch plan v0.4" in e for e in validate_patch_plan(plan)))

    def test_counter_rejects_final_text_drift(self):
        root=number_slide_root("97.0%")
        with self.assertRaisesRegex(ValueError,"counter source text changed"):
            build_existing_timing(counter_plan()["slides"][0],root)

    def test_counter_writer_generates_proxies_and_final_source_reveal(self):
        root=number_slide_root()
        slide=counter_plan()["slides"][0]
        timing,receipt=build_existing_timing(slide,root)
        self.assertEqual(receipt["writer_mode"],"presenter-paced-click-beats")
        self.assertEqual(receipt["click_beat_count"],1)
        self.assertEqual(len(receipt["generated_components"]),1)
        component=receipt["generated_components"][0]
        proxy_count=component["proxy_count"]
        self.assertGreater(proxy_count,0)
        # two effects per proxy (enter/exit) plus final source entrance
        self.assertEqual(receipt["behavior_count"],proxy_count*2+1)
        effects=timing.findall(".//p:animEffect",NS)
        self.assertEqual(len(effects),proxy_count*2+1)
        transitions=[e.get("transition") for e in effects]
        self.assertEqual(transitions.count("in"),proxy_count+1)
        self.assertEqual(transitions.count("out"),proxy_count)
        last=effects[-1].find(".//p:spTgt",NS)
        self.assertEqual(last.get("spid"),"7")
        self.assertEqual(effects[-1].get("transition"),"in")

    def test_counter_readback_keeps_one_presenter_click(self):
        root=number_slide_root()
        timing,receipt=build_existing_timing(counter_plan()["slides"][0],root)
        root.append(timing)
        shapes=[]
        for sp in root.findall("p:cSld/p:spTree/p:sp",NS):
            props=sp.find("p:nvSpPr/p:cNvPr",NS)
            text="".join(t.text or "" for t in sp.findall(".//a:t",NS))
            shapes.append({"id":props.get("id"),"name":props.get("name"),"text":text,"kind":"shape"})
        summary=_timing_inventory(root,shapes)
        self.assertEqual(summary["click_group_count"],1)
        self.assertEqual(summary["effect_count"],receipt["behavior_count"])
        self.assertEqual(summary["effects"][-1]["target_spid"],"7")
        build_spids={x["spid"] for x in summary["build_entries"]}
        self.assertIn("7",build_spids)
        for proxy in receipt["generated_components"][0]["proxies"]:
            self.assertIn(proxy["source_id"],build_spids)


if __name__=="__main__":
    unittest.main()
