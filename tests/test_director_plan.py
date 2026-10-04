import copy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from inspect_existing_deck import inspect_existing_deck
from validate_director_plan import validate
from data_motion_recipes import chart_motion_recipe, number_counter_recipe

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


class DirectorPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory=inspect_existing_deck(SOURCE)

    def plan(self):
        inv=self.inventory
        names=[[s["name"] for s in slide["shapes"] if s["name"]] for slide in inv["slides"]]
        return {
            "version":"0.1",
            "kind":"existing-deck-motion-director",
            "source":{
                "pptx_sha256":inv["source_sha256"],
                "inventory_version":inv["version"],
                "source_slide_count":len(inv["slides"]),
            },
            "user_instruction":"Add meaningful native motion without changing the report structure.",
            "script":{
                "source":"speaker-notes",
                "summary":"Introduce the process, then focus attention on Inspect while preserving context.",
                "evidence":["Speaker notes and existing slide order."],
                "beats":["overview","focus-inspect"],
            },
            "preservation":{
                "preserve_text_by_default":True,
                "preserve_media_by_default":True,
                "preserve_theme_by_default":True,
                "preserve_slide_order_by_default":True,
                "slide_count_policy":"preserve",
            },
            "slides":[
                {
                    "source_index":1,
                    "role":"process overview",
                    "objective":"Audience understands Collect -> Inspect -> Decide.",
                    "beats":[{
                        "id":"reveal-process",
                        "purpose":"Reveal the existing process in reading order.",
                        "operation":"stagger-reveal",
                        "targets":names[0][:3],
                        "reuse_existing":True,
                        "same_slide":True,
                        "timing_intent":"on-click",
                    }],
                    "components":[],
                },
                {
                    "source_index":2,
                    "role":"focus",
                    "objective":"Audience understands why Inspect is the current focus.",
                    "beats":[{
                        "id":"focus-inspect",
                        "purpose":"Move attention to the existing Inspect block without removing context.",
                        "operation":"focus",
                        "targets":[names[1][1]],
                        "reuse_existing":True,
                        "same_slide":True,
                        "timing_intent":"on-click",
                    }],
                    "components":[],
                },
            ],
            "target_slide_count":2,
            "research_metadata":{"sources":[]},
        }

    def test_valid_plan_is_grounded_in_inventory(self):
        self.assertEqual(validate(self.plan(),self.inventory),[])

    def plan_v2(self):
        plan=copy.deepcopy(self.plan())
        plan["version"]="0.2"
        for slide in plan["slides"]:
            beat_ids=[beat["id"] for beat in slide["beats"]]
            slide["click_beats"]=[{
                "id":f"click-{slide['source_index']}-1",
                "purpose":slide["objective"],
                "motion_beats":beat_ids,
                "stable_state":"The audience can hold and discuss the slide objective before continuing.",
                "pause_after":"slide-complete",
                "boundary_reason":"First click starts this slide's presenter-controlled reveal.",
            }]
        return plan

    def test_valid_v2_plan_has_click_rhythm(self):
        self.assertEqual(validate(self.plan_v2(),self.inventory),[])

    def test_v2_requires_click_beat_partition(self):
        bad=self.plan_v2()
        bad["slides"][0]["click_beats"][0]["motion_beats"]=[]
        self.assertTrue(any("motion_beats must be nonempty" in x for x in validate(bad,self.inventory)))

    def test_v2_rejects_nested_on_click_inside_one_presenter_beat(self):
        bad=self.plan_v2()
        slide=bad["slides"][0]
        second=copy.deepcopy(slide["beats"][0])
        second["id"]="second-motion"
        second["purpose"]="Second motion that should not open another click inside the same group."
        second["timing_intent"]="on-click"
        slide["beats"].append(second)
        slide["click_beats"][0]["motion_beats"].append("second-motion")
        self.assertTrue(any("nested on-click" in x for x in validate(bad,self.inventory)))

    def test_v2_second_click_requires_boundary_reason(self):
        bad=self.plan_v2()
        slide=bad["slides"][0]
        second=copy.deepcopy(slide["beats"][0])
        second["id"]="second-motion"
        second["purpose"]="Reveal a second narrative idea."
        second["timing_intent"]="on-click"
        slide["beats"].append(second)
        slide["click_beats"]=[
            {
                "id":"click-1",
                "purpose":"Reveal first idea.",
                "motion_beats":["reveal-process"],
                "stable_state":"First idea is visible and explainable.",
                "pause_after":"presenter-explanation",
                "boundary_reason":"First click opens the slide.",
            },
            {
                "id":"click-2",
                "purpose":"Reveal second idea.",
                "motion_beats":["second-motion"],
                "stable_state":"Second idea is now visible.",
                "pause_after":"slide-complete",
                "boundary_reason":"",
            },
        ]
        self.assertTrue(any("requires boundary_reason" in x for x in validate(bad,self.inventory)))

    def data_inventory(self):
        inv=copy.deepcopy(self.inventory)
        inv["slides"][0]["shapes"].extend([
            {
                "id":"900",
                "name":"Trend Chart",
                "forced_semantic_name":None,
                "kind":"chart",
                "text":None,
                "chart_summary":{
                    "primary_type":"line",
                    "chart_types":["line"],
                    "series_count":2,
                    "category_count":4,
                    "point_count":4,
                },
                "data_semantics":{"standalone_number":None},
            },
            {
                "id":"901",
                "name":"Hero KPI",
                "forced_semantic_name":None,
                "kind":"shape",
                "text":"98.5%",
                "chart_summary":None,
                "data_semantics":{
                    "standalone_number":{
                        "raw":"98.5%",
                        "numeric_value":98.5,
                        "prefix":"",
                        "suffix":"%",
                        "integer_like":False,
                        "counter_candidate":True,
                    }
                },
            },
        ])
        return inv

    def plan_v3_with_data_motion(self):
        inv=self.data_inventory()
        plan=copy.deepcopy(self.plan_v2())
        plan["version"]="0.3"
        plan["source"]["pptx_sha256"]=inv["source_sha256"]
        chart_rec=chart_motion_recipe(inv["slides"][0]["shapes"][-2]["chart_summary"])
        number_sem=inv["slides"][0]["shapes"][-1]["data_semantics"]["standalone_number"]
        counter=number_counter_recipe(number_sem)
        slide=plan["slides"][0]
        slide["beats"].extend([
            {
                "id":"reveal-trend",
                "purpose":"Reveal the existing trend chart according to its line-chart semantics.",
                "operation":"chart-reveal",
                "targets":["Trend Chart"],
                "reuse_existing":True,
                "same_slide":True,
                "timing_intent":"on-click",
                "data_motion":{
                    "kind":"chart",
                    "chart_type":"line",
                    "recipe":chart_rec["recipe"],
                    "build":chart_rec["preferred_build"],
                    "animate_background":False,
                    "rationale":chart_rec["reason"],
                },
            },
            {
                "id":"highlight-kpi",
                "purpose":"Make the hero KPI numerically salient after the trend is understood.",
                "operation":"kpi-highlight",
                "targets":["Hero KPI"],
                "reuse_existing":True,
                "same_slide":True,
                "timing_intent":"on-click",
                "data_motion":{
                    "kind":"number-counter",
                    "recipe":counter["recipe"],
                    "from_value":counter["from_value"],
                    "to_value":counter["to_value"],
                    "duration_ms":counter["duration_ms"],
                    "steps":counter["steps"],
                    "prefix":counter["prefix"],
                    "suffix":counter["suffix"],
                    "decimal_places":counter["decimal_places"],
                    "implementation":counter["preferred_implementation"],
                    "rationale":"This is the hero metric named by the slide objective and deserves numeric emphasis.",
                },
            },
        ])
        slide["click_beats"]=[
            {
                "id":"click-process",
                "purpose":"Reveal the process overview.",
                "motion_beats":["reveal-process"],
                "stable_state":"The process is visible.",
                "pause_after":"presenter-explanation",
                "boundary_reason":"First reveal establishes context.",
            },
            {
                "id":"click-trend",
                "purpose":"Reveal the trend evidence.",
                "motion_beats":["reveal-trend"],
                "stable_state":"The trend is visible and can be discussed.",
                "pause_after":"presenter-explanation",
                "boundary_reason":"Trend evidence should wait until the process context has been explained.",
            },
            {
                "id":"click-kpi",
                "purpose":"Highlight the final KPI.",
                "motion_beats":["highlight-kpi"],
                "stable_state":"The final 98.5% KPI is visible.",
                "pause_after":"slide-complete",
                "boundary_reason":"The KPI should land after the trend has been understood.",
            },
        ]
        return plan,inv

    def test_valid_v3_data_motion_plan(self):
        plan,inv=self.plan_v3_with_data_motion()
        self.assertEqual(validate(plan,inv),[])

    def test_v3_chart_target_requires_chart_data_motion(self):
        plan,inv=self.plan_v3_with_data_motion()
        del plan["slides"][0]["beats"][1]["data_motion"]
        self.assertTrue(any("targeting chart requires data_motion" in x for x in validate(plan,inv)))

    def test_v3_chart_wrong_recipe_needs_override_reason(self):
        plan,inv=self.plan_v3_with_data_motion()
        plan["slides"][0]["beats"][1]["data_motion"]["recipe"]="segment-sweep"
        self.assertTrue(any("differs from recommended" in x for x in validate(plan,inv)))
        plan["slides"][0]["beats"][1]["data_motion"]["override_reason"]="The script explicitly requests a nonstandard segment metaphor."
        self.assertEqual(validate(plan,inv),[])

    def test_v3_hero_number_requires_counter(self):
        plan,inv=self.plan_v3_with_data_motion()
        del plan["slides"][0]["beats"][2]["data_motion"]
        self.assertTrue(any("highlighted standalone number requires counter" in x for x in validate(plan,inv)))

    def test_v3_counter_cannot_change_source_value(self):
        plan,inv=self.plan_v3_with_data_motion()
        plan["slides"][0]["beats"][2]["data_motion"]["to_value"]=99.9
        self.assertTrue(any("to_value does not match source number" in x for x in validate(plan,inv)))

    def test_source_hash_mismatch_fails(self):
        bad=self.plan();bad["source"]["pptx_sha256"]="0"*64
        self.assertIn("source.pptx_sha256 does not match inventory",validate(bad,self.inventory))

    def test_unknown_target_fails(self):
        bad=self.plan();bad["slides"][0]["beats"][0]["targets"]=["not-in-slide"]
        self.assertTrue(any("unknown targets" in x for x in validate(bad,self.inventory)))

    def test_existing_timing_is_valid_script_source(self):
        plan=self.plan();plan["script"]["source"]="existing-timing"
        plan["script"]["evidence"]=["Existing slide timing targets and order."]
        self.assertEqual(validate(plan,self.inventory),[])

    def test_researched_script_requires_sources(self):
        bad=self.plan();bad["script"]["source"]="researched"
        self.assertIn("researched script requires research_metadata.sources",validate(bad,self.inventory))

    def test_component_requires_narrative_rationale(self):
        bad=self.plan()
        bad["slides"][0]["components"]=[{
            "id":"glow","role":"emphasis","rationale":"đẹp hơn",
            "native_kind":"shape","style_basis":"existing card radius",
            "data_provenance":"synthetic-nondata",
        }]
        self.assertTrue(any("decorative-only rationale" in x for x in validate(bad,self.inventory)))

    def test_preserve_policy_forbids_slide_inflation(self):
        bad=self.plan();bad["target_slide_count"]=3
        self.assertIn("target_slide_count must equal source when slide_count_policy=preserve",validate(bad,self.inventory))


if __name__=="__main__":
    unittest.main()
