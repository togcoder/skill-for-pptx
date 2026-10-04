#!/usr/bin/env python3
"""Compile Director v0.3 semantic data motion into patch-plan v0.4.

This bridge is intentionally strict: it only compiles slides whose complete
presenter click rhythm consists of supported data-motion beats. Mixed/unsupported
slides are blocked rather than partially compiled and silently changing click
semantics.
"""
import argparse
import json
from pathlib import Path

try:
    from .validate_director_plan import validate as validate_director
    from .chart_native_timing import concrete_chart_filter
except ImportError:
    from validate_director_plan import validate as validate_director
    from chart_native_timing import concrete_chart_filter


SUPPORTED_DATA_KINDS={"chart","number-counter"}


def _shape_tokens(shape):
    out=[]
    for key in ("name","forced_semantic_name","id"):
        value=shape.get(key)
        if isinstance(value,str) and value:
            out.append(value)
    return out


def _shape_index(inventory_slide):
    result={}
    for shape in inventory_slide.get("shapes",[]):
        for token in _shape_tokens(shape):
            if token in result and result[token] is not shape:
                raise ValueError(f"ambiguous source target token on slide {inventory_slide.get('index')}: {token!r}")
            result[token]=shape
    return result


def _resolve_single_target(beat,inventory_slide):
    targets=beat.get("targets")
    if not isinstance(targets,list) or len(targets)!=1:
        raise ValueError(f"beat {beat.get('id')} requires exactly one target for data-motion execution")
    by_token=_shape_index(inventory_slide)
    shape=by_token.get(targets[0])
    if shape is None:
        raise ValueError(f"beat {beat.get('id')} target is absent from inventory")
    sid=shape.get("id")
    name=shape.get("name")
    if not isinstance(sid,str) or not sid or not isinstance(name,str) or not name:
        raise ValueError(f"beat {beat.get('id')} target lacks stable source id/name")
    return shape,{"source_id":sid,"source_name":name}


def _chart_duration_ms(data_motion,shape):
    summary=shape.get("chart_summary") or {}
    build=data_motion.get("build")
    series=summary.get("series_count") or 1
    categories=summary.get("category_count") or 1
    if build=="series":
        units=series
    elif build=="category":
        units=categories
    elif build in ("series-elements","category-elements"):
        units=series*categories
    else:
        units=1
    return min(2200,max(700,600+min(units,24)*70))


def _counter_effect(data_motion,target,shape):
    if data_motion.get("implementation") not in ("stepped-text","odometer-proxy"):
        raise ValueError("unsupported Director counter implementation")
    raw=((shape.get("data_semantics") or {}).get("standalone_number") or {}).get("raw")
    if not isinstance(raw,str) or not raw:
        raise ValueError("counter target lacks standalone-number source text")

    requested=data_motion.get("implementation")
    effective="stepped-text"
    allow_fallback=data_motion.get("allow_fallback",True)
    if requested!="stepped-text" and not allow_fallback:
        raise ValueError("odometer-proxy requested with fallback disabled, but backend is not implemented")

    return {
        "type":"number_counter",
        "target":target,
        "from_value":data_motion["from_value"],
        "to_value":data_motion["to_value"],
        "steps":data_motion["steps"],
        "decimal_places":data_motion["decimal_places"],
        "prefix":data_motion.get("prefix",""),
        "suffix":data_motion.get("suffix",""),
        "preserve_final_text":raw,
        "filter":"fade",
        "_compile_metadata":{
            "requested_implementation":requested,
            "effective_implementation":effective,
            "fallback_used":requested!=effective,
            "fallback_reason":(
                "odometer-proxy backend is not implemented; stepped-text is the verified structural fallback"
                if requested!=effective else None
            ),
        },
    }


def _chart_effect(data_motion,target,shape):
    summary=shape.get("chart_summary") or {}
    return {
        "type":"chart_entrance",
        "target":target,
        "chart_type":data_motion["chart_type"],
        "build":data_motion["build"],
        "series_count":summary.get("series_count") or 1,
        "category_count":summary.get("category_count"),
        "animate_background":data_motion.get("animate_background",False),
        "filter":concrete_chart_filter(data_motion["chart_type"]),
        "fanout_limit":data_motion.get("fanout_limit",24),
    }


def _compile_slide(director_slide,inventory_slide):
    beat_by_id={beat["id"]:beat for beat in director_slide["beats"]}
    unsupported=[]
    for beat in director_slide["beats"]:
        dm=beat.get("data_motion")
        if not isinstance(dm,dict) or dm.get("kind") not in SUPPORTED_DATA_KINDS:
            unsupported.append(beat["id"])

    if unsupported:
        return None,{
            "source_index":director_slide["source_index"],
            "reason":"mixed-or-unsupported-motion",
            "unsupported_motion_beats":unsupported,
        }

    stages=[]
    stage_id_by_beat={}
    compile_metadata=[]
    for beat in director_slide["beats"]:
        shape,target=_resolve_single_target(beat,inventory_slide)
        dm=beat["data_motion"]
        stage_id=f"data-{beat['id']}"
        stage_id_by_beat[beat["id"]]=stage_id

        if dm["kind"]=="chart":
            if shape.get("kind")!="chart":
                raise ValueError(f"beat {beat['id']} chart data_motion targets non-chart")
            effect=_chart_effect(dm,target,shape)
            duration=_chart_duration_ms(dm,shape)
        elif dm["kind"]=="number-counter":
            if not ((shape.get("data_semantics") or {}).get("standalone_number")):
                raise ValueError(f"beat {beat['id']} number-counter target is not standalone numeric")
            effect=_counter_effect(dm,target,shape)
            duration=dm["duration_ms"]
            compile_metadata.append({
                "beat_id":beat["id"],
                **effect.pop("_compile_metadata"),
            })
        else:
            raise AssertionError(dm["kind"])

        stages.append({
            "id":stage_id,
            "duration_ms":duration,
            "trigger":beat["timing_intent"],
            "effects":[effect],
        })

    click_beats=[]
    for click in director_slide["click_beats"]:
        motion_ids=click["motion_beats"]
        stage_ids=[stage_id_by_beat[mid] for mid in motion_ids]
        click_beats.append({
            "id":click["id"],
            "stages":stage_ids,
        })

    return {
        "source_index":director_slide["source_index"],
        "stages":stages,
        "click_beats":click_beats,
    },compile_metadata


def compile_data_motion_patch(director_plan,inventory):
    errors=validate_director(director_plan,inventory)
    if errors:
        raise ValueError("Invalid director plan: "+"; ".join(errors))
    if director_plan.get("version")!="0.3":
        raise ValueError("semantic-to-execution compiler requires Director v0.3")

    inv_by_index={slide["index"]:slide for slide in inventory.get("slides",[])}
    patch_slides=[]
    blocked=[]
    compile_metadata=[]

    for director_slide in director_plan["slides"]:
        index=director_slide["source_index"]
        inv=inv_by_index.get(index)
        if inv is None:
            raise ValueError(f"source slide missing from inventory: {index}")
        patch_slide,meta=_compile_slide(director_slide,inv)
        if patch_slide is None:
            blocked.append(meta)
            continue
        patch_slides.append(patch_slide)
        compile_metadata.extend(meta)

    if not patch_slides:
        raise ValueError(
            "No slide can be compiled safely: every slide contains unsupported or mixed motion beats"
        )

    return {
        "version":"0.4",
        "kind":"existing-deck-timeline-patch",
        "source_sha256":director_plan["source"]["pptx_sha256"],
        "slides":patch_slides,
        "compile_metadata":{
            "source_director_version":director_plan["version"],
            "compiled_slide_count":len(patch_slides),
            "blocked_slides":blocked,
            "counter_fallbacks":compile_metadata,
            "partial_deck":bool(blocked),
        },
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("director_plan",type=Path)
    parser.add_argument("inventory",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    director=json.loads(args.director_plan.read_text(encoding="utf-8"))
    inventory=json.loads(args.inventory.read_text(encoding="utf-8"))
    patch=compile_data_motion_patch(director,inventory)
    text=json.dumps(patch,ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(text+"\n",encoding="utf-8")
    else:
        print(text)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
