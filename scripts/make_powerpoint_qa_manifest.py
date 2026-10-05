#!/usr/bin/env python3
"""Build a native-PowerPoint QA manifest for an exact PPTX artifact.

The manifest freezes the artifact hash and converts structural timing inventory
into expectations that a Windows PowerPoint COM probe can verify independently.
"""
import argparse
import hashlib
import json
from pathlib import Path

try:
    from .inspect_existing_deck import inspect_existing_deck
except ImportError:
    from inspect_existing_deck import inspect_existing_deck


def _sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(pptx):
    pptx=Path(pptx)
    inventory=inspect_existing_deck(pptx)
    if inventory.get("errors"):
        raise ValueError("Cannot build native QA manifest from invalid inventory: "+"; ".join(inventory["errors"]))

    slides=[]
    for slide in inventory["slides"]:
        timing=slide.get("timing_summary")
        if not timing:
            continue
        click_groups=timing.get("click_groups") or []
        target_names=[]
        for effect in timing.get("effects") or []:
            target=effect.get("target")
            if target and target.get("name") and target["name"] not in target_names:
                target_names.append(target["name"])

        expected_clicks=[]
        for group in click_groups:
            names=[]
            for target in group.get("targets") or []:
                if target and target.get("name") and target["name"] not in names:
                    names.append(target["name"])
            expected_clicks.append({
                "index":group["index"],
                "target_names":names,
                "effect_count":group.get("effect_count",0),
                "effect_types":group.get("effect_types") or [],
                "start_node_types":group.get("start_node_types") or [],
            })

        slides.append({
            "index":slide["index"],
            "title_candidate":slide.get("title_candidate"),
            "expected_click_count":len(click_groups),
            "structural_effect_count":timing.get("effect_count",0),
            "expected_target_names":target_names,
            "expected_clicks":expected_clicks,
            "has_transition":slide.get("has_transition",False),
        })

    return {
        "version":"0.1",
        "kind":"powerpoint-native-qa-manifest",
        "pptx_path_hint":pptx.name,
        "pptx_sha256":_sha256(pptx),
        "source_inventory_version":inventory.get("version"),
        "slide_count":len(inventory["slides"]),
        "animated_slide_count":len(slides),
        "slides":slides,
        "acceptance":{
            "require_exact_hash":True,
            "require_powerpoint_open":True,
            "require_slide_count_match":True,
            "require_click_count_match":True,
            "require_click_index_progression":True,
            "require_expected_targets_in_main_sequence":True,
            "visual_state_review_required":True,
        },
        "claim_boundary":{
            "native_application_parse_verified":False,
            "native_click_execution_verified":False,
            "visual_state_verified":False,
        },
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    manifest=build_manifest(args.pptx)
    data=json.dumps(manifest,ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(data+"\n",encoding="utf-8")
    else:
        print(data)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
