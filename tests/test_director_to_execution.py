import copy
import sys
import unittest
from pathlib import Path

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from compile_data_motion_patch import compile_data_motion_patch
from patch_existing_timeline import build_existing_timing, validate_patch_plan
from inspect_existing_deck import _timing_inventory, A, P

C="http://schemas.openxmlformats.org/drawingml/2006/chart"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS={"p":P,"a":A}


def inventory():
    return {
        "version":"0.1",
        "kind":"existing-deck-inventory",
        "source_sha256":"a"*64,
        "slides":[{
            "index":1,
            "shapes":[
                {
                    "id":"7","name":"Trend Chart","forced_semantic_name":None,
                    "kind":"chart","text":None,
                    "chart_summary":{
                        "primary_type":"line","chart_types":["line"],
                        "series_count":2,"category_count":4,"point_count":4,
                    },
                    "data_semantics":{"standalone_number":None},
                },
                {
                    "id":"8","name":"Hero KPI","forced_semantic_name":None,
                    "kind":"shape","text":"98.5%",
                    "chart_summary":None,
                    "data_semantics":{"standalone_number":{
                        "raw":"98.5%","numeric_value":98.5,"prefix":"","suffix":"%",
                        "integer_like":False,"counter_candidate":True,
                    }},
                },
            ],
        }],
    }


def director_plan():
    return {
        "version":"0.3",
        "kind":"existing-deck-motion-director",
        "source":{
            "pptx_sha256":"a"*64,
            "inventory_version":"0.1",
            "source_slide_count":1,
        },
        "user_instruction":"Reveal the trend, then land the KPI.",
        "script":{
            "source":"inferred",
            "summary":"Show trend evidence, then the final KPI.",
            "evidence":["Visible chart and standalone KPI."],
            "beats":["trend","kpi"],
        },
        "preservation":{
            "preserve_text_by_default":True,
            "preserve_media_by_default":True,
            "preserve_theme_by_default":True,
            "preserve_slide_order_by_default":True,
            "slide_count_policy":"preserve",
        },
        "slides":[{
            "source_index":1,
            "role":"evidence-to-result",
            "objective":"Audience sees the trend before the KPI lands.",
            "beats":[
                {
                    "id":"trend",
                    "purpose":"Reveal the line trend.",
                    "operation":"chart-reveal",
                    "targets":["Trend Chart"],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                    "data_motion":{
                        "kind":"chart",
                        "chart_type":"line",
                        "recipe":"series-trace",
                        "build":"series",
                        "animate_background":False,
                        "rationale":"Line chart communicates ordered progression.",
                    },
                },
                {
                    "id":"kpi",
                    "purpose":"Land the final KPI after the trend is understood.",
                    "operation":"kpi-highlight",
                    "targets":["Hero KPI"],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                    "data_motion":{
                        "kind":"number-counter",
                        "recipe":"count-up",
                        "from_value":0,
                        "to_value":98.5,
                        "duration_ms":1200,
                        "steps":7,
                        "prefix":"",
                        "suffix":"%",
                        "decimal_places":1,
                        "implementation":"odometer-proxy",
                        "rationale":"The KPI is the slide conclusion.",
                    },
                },
            ],
            "click_beats":[
                {
                    "id":"click-trend",
                    "purpose":"Reveal trend evidence.",
                    "motion_beats":["trend"],
                    "stable_state":"Trend is fully visible.",
                    "pause_after":"presenter-explanation",
                    "boundary_reason":"First click establishes evidence.",
                },
                {
                    "id":"click-kpi",
                    "purpose":"Reveal KPI conclusion.",
                    "motion_beats":["kpi"],
                    "stable_state":"98.5% is visible as the final state.",
                    "pause_after":"slide-complete",
                    "boundary_reason":"KPI waits until the trend has been explained.",
                },
            ],
            "components":[],
        }],
        "target_slide_count":1,
        "research_metadata":{"sources":[]},
    }


def slide_root():
    xml=f"""<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:c="{C}" xmlns:r="{R}">
      <p:cSld><p:spTree>
        <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
        <p:grpSpPr/>
        <p:graphicFrame>
          <p:nvGraphicFramePr><p:cNvPr id="7" name="Trend Chart"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr>
          <p:xfrm><a:off x="100" y="100"/><a:ext cx="500" cy="300"/></p:xfrm>
          <a:graphic><a:graphicData uri="{C}"><c:chart r:id="rId5"/></a:graphicData></a:graphic>
        </p:graphicFrame>
        <p:sp>
          <p:nvSpPr><p:cNvPr id="8" name="Hero KPI"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
          <p:spPr><a:xfrm><a:off x="700" y="100"/><a:ext cx="250" cy="100"/></a:xfrm></p:spPr>
          <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr sz="3200" b="1"/><a:t>98.5%</a:t></a:r></a:p></p:txBody>
        </p:sp>
      </p:spTree></p:cSld>
    </p:sld>"""
    return E.fromstring(xml.encode())


class DirectorToExecutionTests(unittest.TestCase):
    def test_compiler_outputs_v04_patch_and_preserves_clicks(self):
        patch=compile_data_motion_patch(director_plan(),inventory())
        self.assertEqual(patch["version"],"0.4")
        self.assertEqual(patch["compile_metadata"]["compiled_slide_count"],1)
        self.assertFalse(patch["compile_metadata"]["partial_deck"])
        slide=patch["slides"][0]
        self.assertEqual([b["stages"] for b in slide["click_beats"]],[["data-trend"],["data-kpi"]])
        self.assertEqual(slide["stages"][0]["effects"][0]["type"],"chart_entrance")
        self.assertEqual(slide["stages"][1]["effects"][0]["type"],"number_counter")
        self.assertEqual(validate_patch_plan(patch),[])

    def test_odometer_request_uses_explicit_structural_fallback_metadata(self):
        patch=compile_data_motion_patch(director_plan(),inventory())
        fallbacks=patch["compile_metadata"]["counter_fallbacks"]
        self.assertEqual(len(fallbacks),1)
        self.assertEqual(fallbacks[0]["requested_implementation"],"odometer-proxy")
        self.assertEqual(fallbacks[0]["effective_implementation"],"stepped-text")
        self.assertTrue(fallbacks[0]["fallback_used"])

    def test_fallback_can_be_forbidden(self):
        plan=director_plan()
        plan["slides"][0]["beats"][1]["data_motion"]["allow_fallback"]=False
        with self.assertRaisesRegex(ValueError,"fallback disabled"):
            compile_data_motion_patch(plan,inventory())

    def test_mixed_motion_slide_is_blocked_instead_of_partially_compiled(self):
        plan=director_plan()
        generic={
            "id":"generic-focus",
            "purpose":"Unsupported generic focus.",
            "operation":"focus",
            "targets":["Hero KPI"],
            "reuse_existing":True,
            "same_slide":True,
            "timing_intent":"after-previous",
        }
        plan["slides"][0]["beats"].append(generic)
        plan["slides"][0]["click_beats"][1]["motion_beats"].append("generic-focus")
        with self.assertRaisesRegex(ValueError,"No slide can be compiled safely"):
            compile_data_motion_patch(plan,inventory())

    def test_semantic_to_timing_integration_keeps_two_presenter_clicks(self):
        patch=compile_data_motion_patch(director_plan(),inventory())
        root=slide_root()
        timing,receipt=build_existing_timing(patch["slides"][0],root)
        self.assertEqual(receipt["click_beat_count"],2)
        self.assertEqual(len(receipt["chart_builds"]),1)
        self.assertEqual(len(receipt["generated_components"]),1)
        root.append(timing)

        shapes=[]
        for node in root.find("p:cSld/p:spTree",NS):
            props=node.find(".//p:cNvPr",NS)
            if props is None:
                continue
            text="".join(t.text or "" for t in node.findall(".//a:t",NS)).strip() or None
            kind="chart" if node.tag.endswith("graphicFrame") else "shape"
            shapes.append({"id":props.get("id"),"name":props.get("name"),"text":text,"kind":kind})

        summary=_timing_inventory(root,shapes)
        self.assertEqual(summary["click_group_count"],2)
        chart_build=next(
            entry for entry in summary["build_entries"]
            if entry["type"]=="bldGraphic" and entry["spid"]=="7"
        )
        self.assertEqual(chart_build["build"],"series")
        # Two chart series plus counter proxy entrance/exits + final KPI entrance.
        self.assertGreater(summary["effect_count"],3)
        self.assertEqual(summary["click_groups"][0]["target_spids"],["7"])
        self.assertIn("8",summary["click_groups"][1]["target_spids"])

    def test_chart_duration_scales_but_is_bounded(self):
        patch=compile_data_motion_patch(director_plan(),inventory())
        dur=patch["slides"][0]["stages"][0]["duration_ms"]
        self.assertGreaterEqual(dur,700)
        self.assertLessEqual(dur,2200)


if __name__=="__main__":
    unittest.main()
