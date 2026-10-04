import copy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from inspect_existing_deck import inspect_existing_deck
from validate_director_plan import validate

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
