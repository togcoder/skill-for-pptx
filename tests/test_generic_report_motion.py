import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from generic_motion_recipes import generic_motion_recipe, focus_scale
from inspect_existing_deck import inspect_existing_deck
from compile_director_patch import compile_director_patch
from patch_existing_timeline import patch_existing, validate_patch_plan

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


def generic_director(inv):
    names=[[s["name"] for s in slide["shapes"] if s["name"]] for slide in inv["slides"]]
    return {
        "version":"0.4",
        "kind":"existing-deck-motion-director",
        "source":{
            "pptx_sha256":inv["source_sha256"],
            "inventory_version":inv["version"],
            "source_slide_count":len(inv["slides"]),
        },
        "user_instruction":"Reveal the process, then emphasize Inspect.",
        "script":{
            "source":"speaker-notes",
            "summary":"Reveal the process overview, then focus Inspect.",
            "evidence":["Speaker notes and source slide order."],
            "beats":["overview","focus"],
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
                "objective":"Audience understands the first three process resources in sequence.",
                "beats":[{
                    "id":"reveal-process",
                    "purpose":"Reveal existing process resources in source order.",
                    "operation":"stagger-reveal",
                    "targets":names[0][:3],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                }],
                "click_beats":[{
                    "id":"click-process",
                    "purpose":"Reveal the process overview.",
                    "motion_beats":["reveal-process"],
                    "stable_state":"The first process resources are visible.",
                    "pause_after":"slide-complete",
                    "boundary_reason":"First click opens the process.",
                }],
                "components":[],
            },
            {
                "source_index":2,
                "role":"focus",
                "objective":"Audience understands which source object is the current focus.",
                "beats":[{
                    "id":"focus-inspect",
                    "purpose":"Pulse one existing source object in place without changing layout.",
                    "operation":"focus",
                    "targets":[names[1][1]],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                }],
                "click_beats":[{
                    "id":"click-focus",
                    "purpose":"Emphasize the focused source resource.",
                    "motion_beats":["focus-inspect"],
                    "stable_state":"The focus pulse returns the object to authored size.",
                    "pause_after":"slide-complete",
                    "boundary_reason":"First click on this slide performs the focus.",
                }],
                "components":[],
            },
        ],
        "target_slide_count":len(inv["slides"]),
        "research_metadata":{"sources":[]},
    }


class GenericReportMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory=inspect_existing_deck(SOURCE)

    def test_reveal_and_focus_recipes_are_distinct(self):
        slide=self.inventory["slides"][0]
        shapes=slide["shapes"][:2]
        reveal=generic_motion_recipe("stagger-reveal",shapes)
        self.assertEqual(reveal["kind"],"reveal")
        self.assertGreater(reveal["stagger_ms"],0)
        focus=generic_motion_recipe("focus",[shapes[0]])
        self.assertEqual(focus["kind"],"focus-pulse")
        self.assertGreater(focus["scale"],1.0)

    def test_focus_scale_respects_slide_edges(self):
        edge={"geometry":{"x":0.0,"y":0.0,"w":0.5,"h":0.5}}
        center={"geometry":{"x":0.3,"y":0.3,"w":0.2,"h":0.2}}
        self.assertLessEqual(focus_scale(edge),focus_scale(center))
        self.assertGreaterEqual(focus_scale(edge),1.02)
        self.assertLessEqual(focus_scale(center),1.08)

    def test_compiler_expands_one_semantic_beat_to_multiple_stages(self):
        plan=generic_director(self.inventory)
        patch=compile_director_patch(plan,self.inventory)
        self.assertEqual(patch["version"],"0.5")
        self.assertFalse(patch["compile_metadata"]["partial_deck"])
        slide1,slide2=patch["slides"]
        self.assertEqual(len(slide1["click_beats"]),1)
        self.assertEqual(len(slide1["click_beats"][0]["stages"]),3)
        self.assertEqual(
            [s["trigger"] for s in slide1["stages"]],
            ["on-click","after-previous","after-previous"],
        )
        self.assertTrue(all(s["effects"][0]["type"]=="shape_entrance" for s in slide1["stages"]))
        self.assertEqual(len(slide2["click_beats"][0]["stages"]),2)
        self.assertEqual([s["effects"][0]["type"] for s in slide2["stages"]],["scale","scale"])
        self.assertEqual([s["trigger"] for s in slide2["stages"]],["on-click","after-previous"])
        self.assertEqual(validate_patch_plan(patch),[])

    def test_real_h001_package_patches_generic_motion_without_slide_inflation(self):
        plan=generic_director(self.inventory)
        patch=compile_director_patch(plan,self.inventory)
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            patch_path=td/"patch.json"
            output=td/"out.pptx"
            patch_path.write_text(json.dumps(patch),encoding="utf-8")
            receipt=patch_existing(SOURCE,patch_path,output)
            self.assertEqual(receipt["patched_slides"],[1,2])
            self.assertEqual(receipt["click_beat_count"],2)
            out=inspect_existing_deck(output)
            self.assertEqual(out["errors"],[])
            self.assertEqual(len(out["slides"]),len(self.inventory["slides"]))
            self.assertEqual(out["slides"][0]["timing_summary"]["click_group_count"],1)
            self.assertEqual(out["slides"][1]["timing_summary"]["click_group_count"],1)
            self.assertEqual(out["slides"][0]["timing_summary"]["effect_count"],3)
            self.assertEqual(out["slides"][1]["timing_summary"]["effect_count"],2)
            self.assertIsNotNone(out["slides"][1]["transition_summary"])
            # Generic motion must not rewrite existing text or geometry.
            for src_slide,out_slide in zip(self.inventory["slides"],out["slides"]):
                src_by={(s["id"],s["name"]):s for s in src_slide["shapes"]}
                out_by={(s["id"],s["name"]):s for s in out_slide["shapes"]}
                for key,src_shape in src_by.items():
                    self.assertIn(key,out_by)
                    self.assertEqual(out_by[key]["text"],src_shape["text"])
                    self.assertEqual(out_by[key]["geometry"],src_shape["geometry"])

    def test_move_requires_explicit_path_and_compiles_when_present(self):
        plan=generic_director(self.inventory)
        beat=plan["slides"][1]["beats"][0]
        beat["operation"]="move"
        shape=next(s for s in self.inventory["slides"][1]["shapes"] if s["name"]==beat["targets"][0])
        g=shape["geometry"]
        start={"x":g["x"]+g["w"]/2,"y":g["y"]+g["h"]/2}
        beat["motion_parameters"]={
            "points":[start,{"x":start["x"]+0.01,"y":start["y"]}],
            "duration_ms":500,
        }
        patch=compile_director_patch(plan,self.inventory)
        effect=patch["slides"][1]["stages"][0]["effects"][0]
        self.assertEqual(effect["type"],"motion_path")

    def test_unknown_operation_blocks_slide_not_partial_motion(self):
        plan=generic_director(self.inventory)
        plan["slides"][0]["beats"][0]["operation"]="unknown-fancy-effect"
        patch=compile_director_patch(plan,self.inventory)
        self.assertTrue(patch["compile_metadata"]["partial_deck"])
        self.assertEqual(patch["compile_metadata"]["compiled_slide_count"],1)
        self.assertEqual(patch["compile_metadata"]["blocked_slides"][0]["source_index"],1)


if __name__=="__main__":
    unittest.main()
