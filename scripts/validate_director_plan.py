#!/usr/bin/env python3
"""Validate an existing-deck motion-director plan against a deck inventory."""
import argparse
import json
from pathlib import Path

SCRIPT_SOURCES={"provided","speaker-notes","inferred","researched"}
TIMING={"on-click","with-previous","after-previous"}
COMPONENT_KINDS={"shape","text","connector","derived-visual"}
PROVENANCE={"none","derived-from-source","synthetic-nondata","user-provided"}


def validate(plan,inventory):
    errors=[]
    if not isinstance(plan,dict):
        return ["plan must be an object"]
    required={"version","kind","source","user_instruction","script","preservation",
              "slides","target_slide_count","research_metadata"}
    errors += [f"missing field: {k}" for k in sorted(required-plan.keys())]
    if errors:
        return errors
    if plan["version"]!="0.1":
        errors.append("version must be 0.1")
    if plan["kind"]!="existing-deck-motion-director":
        errors.append("kind must be existing-deck-motion-director")

    source=plan["source"]
    if not isinstance(source,dict):
        errors.append("source must be an object")
    else:
        if source.get("pptx_sha256")!=inventory.get("source_sha256"):
            errors.append("source.pptx_sha256 does not match inventory")
        if source.get("inventory_version")!=inventory.get("version"):
            errors.append("source.inventory_version does not match inventory")
        if source.get("source_slide_count")!=len(inventory.get("slides",[])):
            errors.append("source.source_slide_count does not match inventory")

    script=plan["script"]
    if not isinstance(script,dict):
        errors.append("script must be an object")
    else:
        if script.get("source") not in SCRIPT_SOURCES:
            errors.append("unsupported script.source")
        if not isinstance(script.get("summary"),str) or not script["summary"].strip():
            errors.append("script.summary must be nonempty")
        evidence=script.get("evidence")
        if not isinstance(evidence,list) or not evidence or any(not isinstance(x,str) or not x.strip() for x in evidence):
            errors.append("script.evidence must be a nonempty text list")
        beats=script.get("beats")
        if not isinstance(beats,list) or not beats:
            errors.append("script.beats must be nonempty")
        if script.get("source")=="researched":
            sources=plan.get("research_metadata",{}).get("sources")
            if not isinstance(sources,list) or not sources:
                errors.append("researched script requires research_metadata.sources")

    preservation=plan["preservation"]
    if not isinstance(preservation,dict):
        errors.append("preservation must be an object")
    else:
        for key in ("preserve_text_by_default","preserve_media_by_default",
                    "preserve_theme_by_default","preserve_slide_order_by_default"):
            if type(preservation.get(key)) is not bool:
                errors.append(f"preservation.{key} must be boolean")
        policy=preservation.get("slide_count_policy")
        if policy not in ("preserve","explicit-change"):
            errors.append("unsupported preservation.slide_count_policy")
        elif policy=="preserve" and plan["target_slide_count"]!=len(inventory.get("slides",[])):
            errors.append("target_slide_count must equal source when slide_count_policy=preserve")

    inv_slides={s["index"]:s for s in inventory.get("slides",[])}
    plans=plan["slides"]
    if not isinstance(plans,list) or not plans:
        errors.append("slides must be nonempty")
        return errors

    seen=set()
    for slide in plans:
        if not isinstance(slide,dict):
            errors.append("slide plan must be an object")
            continue
        idx=slide.get("source_index")
        if idx in seen:
            errors.append(f"duplicate source_index: {idx}")
        seen.add(idx)
        inv=inv_slides.get(idx)
        if inv is None:
            errors.append(f"unknown source slide: {idx}")
            continue
        for key in ("role","objective"):
            if not isinstance(slide.get(key),str) or not slide[key].strip():
                errors.append(f"slide {idx}: {key} must be nonempty")

        components=slide.get("components")
        if not isinstance(components,list):
            errors.append(f"slide {idx}: components must be a list")
            components=[]
        component_ids=set()
        for comp in components:
            if not isinstance(comp,dict):
                errors.append(f"slide {idx}: component must be an object")
                continue
            cid=comp.get("id")
            if not isinstance(cid,str) or not cid:
                errors.append(f"slide {idx}: component id must be nonempty")
                continue
            if cid in component_ids:
                errors.append(f"slide {idx}: duplicate component id {cid}")
            component_ids.add(cid)
            if comp.get("native_kind") not in COMPONENT_KINDS:
                errors.append(f"slide {idx}: unsupported component kind {comp.get('native_kind')}")
            if comp.get("data_provenance") not in PROVENANCE:
                errors.append(f"slide {idx}: unsupported component provenance {comp.get('data_provenance')}")
            for key in ("role","rationale","style_basis"):
                if not isinstance(comp.get(key),str) or not comp[key].strip():
                    errors.append(f"slide {idx}: component {cid} missing {key}")
            rationale=(comp.get("rationale") or "").lower()
            if rationale.strip() in ("make it beautiful","make it impressive","đẹp hơn","ấn tượng hơn"):
                errors.append(f"slide {idx}: component {cid} has decorative-only rationale")

        source_targets=set()
        for shape in inv.get("shapes",[]):
            for value in (shape.get("name"),shape.get("forced_semantic_name"),shape.get("id")):
                if isinstance(value,str) and value:
                    source_targets.add(value)

        beats=slide.get("beats")
        if not isinstance(beats,list) or not beats:
            errors.append(f"slide {idx}: beats must be nonempty")
            continue
        beat_ids=set()
        for beat in beats:
            if not isinstance(beat,dict):
                errors.append(f"slide {idx}: beat must be an object")
                continue
            bid=beat.get("id")
            if not isinstance(bid,str) or not bid:
                errors.append(f"slide {idx}: beat id must be nonempty")
            elif bid in beat_ids:
                errors.append(f"slide {idx}: duplicate beat id {bid}")
            else:
                beat_ids.add(bid)
            if not isinstance(beat.get("purpose"),str) or not beat["purpose"].strip():
                errors.append(f"slide {idx}: beat {bid} missing purpose")
            if not isinstance(beat.get("operation"),str) or not beat["operation"].strip():
                errors.append(f"slide {idx}: beat {bid} missing operation")
            if beat.get("same_slide") is not True:
                errors.append(f"slide {idx}: beat {bid} must stay on same slide in v0.1")
            if type(beat.get("reuse_existing")) is not bool:
                errors.append(f"slide {idx}: beat {bid} reuse_existing must be boolean")
            if beat.get("timing_intent") not in TIMING:
                errors.append(f"slide {idx}: beat {bid} has unsupported timing_intent")
            targets=beat.get("targets")
            if not isinstance(targets,list) or not targets:
                errors.append(f"slide {idx}: beat {bid} targets must be nonempty")
            else:
                allowed=source_targets|component_ids
                missing=[target for target in targets if target not in allowed]
                if missing:
                    errors.append(f"slide {idx}: beat {bid} unknown targets {missing}")

    if preservation.get("slide_count_policy")=="explicit-change":
        changes=plan.get("research_metadata",{}).get("slide_count_changes")
        if not isinstance(changes,list) or not changes:
            errors.append("explicit slide-count change requires research_metadata.slide_count_changes")
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan",type=Path)
    parser.add_argument("inventory",type=Path)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text(encoding="utf-8"))
    inventory=json.loads(args.inventory.read_text(encoding="utf-8"))
    errors=validate(plan,inventory)
    print(json.dumps({"valid":not errors,"errors":errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0


if __name__=="__main__":
    raise SystemExit(main())
