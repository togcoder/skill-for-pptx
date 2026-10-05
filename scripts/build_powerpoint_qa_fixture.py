#!/usr/bin/env python3
"""Build the composite T018 native-PowerPoint QA deck and manifest.

Fixture contents:
- slide 1: native line chart reveal, then KPI stepped counter (2 clicks);
- slide 2: generic focus pulse on an existing source object (1 click).

The base is a valid repository PPTX. The result is intended for PowerPoint COM
runtime QA, not as user/factory data.
"""
import argparse
import json
import tempfile
from pathlib import Path

try:
    from .make_data_motion_fixture import make_fixture
    from .inspect_existing_deck import inspect_existing_deck
    from .compile_director_patch import compile_director_patch
    from .patch_existing_timeline import patch_existing
    from .make_powerpoint_qa_manifest import build_manifest
except ImportError:
    from make_data_motion_fixture import make_fixture
    from inspect_existing_deck import inspect_existing_deck
    from compile_director_patch import compile_director_patch
    from patch_existing_timeline import patch_existing
    from make_powerpoint_qa_manifest import build_manifest


ROOT=Path(__file__).resolve().parents[1]
DEFAULT_BASE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


def _find_focus_target(slide):
    shapes=slide["shapes"]
    for shape in shapes:
        if isinstance(shape.get("text"),str) and "inspect" in shape["text"].lower():
            return shape
    for shape in shapes:
        if shape.get("kind") not in ("chart","group") and shape.get("name"):
            return shape
    raise ValueError("No suitable generic focus target found on slide 2")


def _director(inv):
    slide1=inv["slides"][0]
    chart=next(s for s in slide1["shapes"] if s.get("name")=="Trend Chart")
    kpi=next(s for s in slide1["shapes"] if s.get("name")=="Hero KPI")
    slide2=inv["slides"][1]
    focus=_find_focus_target(slide2)

    return {
        "version":"0.4",
        "kind":"existing-deck-motion-director",
        "source":{
            "pptx_sha256":inv["source_sha256"],
            "inventory_version":inv["version"],
            "source_slide_count":len(inv["slides"]),
        },
        "user_instruction":"Native QA fixture: chart, KPI counter, then generic focus.",
        "script":{
            "source":"provided",
            "summary":"Reveal data evidence and KPI on slide 1, then focus an existing object on slide 2.",
            "evidence":["T018 deterministic QA fixture specification."],
            "beats":["chart","kpi","focus"],
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
                "role":"data-motion-runtime-qa",
                "objective":"Exercise chart and KPI native timing with two presenter clicks.",
                "beats":[
                    {
                        "id":"chart",
                        "purpose":"Reveal the line chart by series.",
                        "operation":"chart-reveal",
                        "targets":[chart["name"]],
                        "reuse_existing":True,
                        "same_slide":True,
                        "timing_intent":"on-click",
                        "data_motion":{
                            "kind":"chart",
                            "chart_type":"line",
                            "recipe":"series-trace",
                            "build":"series",
                            "animate_background":False,
                            "rationale":"Line chart QA exercises native series build.",
                        },
                    },
                    {
                        "id":"kpi",
                        "purpose":"Count to the final KPI.",
                        "operation":"kpi-highlight",
                        "targets":[kpi["name"]],
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
                            "implementation":"stepped-text",
                            "rationale":"KPI QA exercises generated proxy timing and original final value.",
                        },
                    },
                ],
                "click_beats":[
                    {
                        "id":"click-chart",
                        "purpose":"Reveal chart evidence.",
                        "motion_beats":["chart"],
                        "stable_state":"Both chart series are visible.",
                        "pause_after":"presenter-explanation",
                        "boundary_reason":"First click starts slide evidence.",
                    },
                    {
                        "id":"click-kpi",
                        "purpose":"Land KPI conclusion.",
                        "motion_beats":["kpi"],
                        "stable_state":"Original 98.5% source KPI is visible.",
                        "pause_after":"slide-complete",
                        "boundary_reason":"KPI waits until chart evidence has been shown.",
                    },
                ],
                "components":[],
            },
            {
                "source_index":2,
                "role":"generic-motion-runtime-qa",
                "objective":"Exercise an in-place native focus pulse with one click.",
                "beats":[{
                    "id":"focus",
                    "purpose":"Pulse one existing source object and return to authored size.",
                    "operation":"focus",
                    "targets":[focus["name"]],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                }],
                "click_beats":[{
                    "id":"click-focus",
                    "purpose":"Run focus pulse.",
                    "motion_beats":["focus"],
                    "stable_state":"Object returns to authored size.",
                    "pause_after":"slide-complete",
                    "boundary_reason":"First click on slide 2 performs the focus QA.",
                }],
                "components":[],
            },
        ],
        "target_slide_count":len(inv["slides"]),
        "research_metadata":{"sources":[]},
    }


def build_qa_fixture(output,manifest_output,base=DEFAULT_BASE):
    output=Path(output)
    manifest_output=Path(manifest_output)
    base=Path(base)
    if output.exists() or manifest_output.exists():
        raise ValueError("Refuse to overwrite T018 QA outputs")
    output.parent.mkdir(parents=True,exist_ok=True)
    manifest_output.parent.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory(dir=output.parent) as td:
        td=Path(td)
        enriched=td/"enriched.pptx"
        make_fixture(base,enriched)
        inv=inspect_existing_deck(enriched)
        if inv["errors"]:
            raise ValueError("Enriched QA fixture inventory failed: "+"; ".join(inv["errors"]))
        director=_director(inv)
        patch=compile_director_patch(director,inv)
        patch_path=td/"patch.json"
        patch_path.write_text(json.dumps(patch,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        receipt=patch_existing(enriched,patch_path,output)

    manifest=build_manifest(output)
    manifest_output.write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"
    )
    return {
        "pptx":str(output),
        "manifest":str(manifest_output),
        "sha256":manifest["pptx_sha256"],
        "slide_count":manifest["slide_count"],
        "animated_slide_count":manifest["animated_slide_count"],
        "expected_click_counts":{
            str(slide["index"]):slide["expected_click_count"]
            for slide in manifest["slides"]
        },
        "patch_receipt":receipt,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base",type=Path,default=DEFAULT_BASE)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--manifest",type=Path,required=True)
    args=parser.parse_args()
    result=build_qa_fixture(args.output,args.manifest,args.base)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
