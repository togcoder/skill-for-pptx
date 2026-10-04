#!/usr/bin/env python3
"""Compile Director v0.4 semantic motion into existing-deck patch v0.5.

Supported families:
- T012/T015 chart and KPI data motion;
- reveal / stagger-reveal / process-reveal;
- focus / emphasize as an in-place scale pulse;
- move with explicit path points;
- rotate with explicit degrees.

Unknown operations block the whole slide instead of being silently dropped.
"""
import argparse
import json
from pathlib import Path

try:
    from .validate_director_plan import validate as validate_director
    from .compile_data_motion_patch import (
        _chart_effect, _chart_duration_ms, _counter_effect, _shape_index,
    )
    from .generic_motion_recipes import generic_motion_recipe, SUPPORTED_GENERIC_OPERATIONS
except ImportError:
    from validate_director_plan import validate as validate_director
    from compile_data_motion_patch import (
        _chart_effect, _chart_duration_ms, _counter_effect, _shape_index,
    )
    from generic_motion_recipes import generic_motion_recipe, SUPPORTED_GENERIC_OPERATIONS


def _source_target(token,inventory_slide):
    shape=_shape_index(inventory_slide).get(token)
    if shape is None:
        raise ValueError(f"target {token!r} is not a source object; component execution is not implemented")
    sid=shape.get("id")
    name=shape.get("name")
    if not isinstance(sid,str) or not sid or not isinstance(name,str) or not name:
        raise ValueError(f"target {token!r} lacks stable source id/name")
    return shape,{"source_id":sid,"source_name":name}


def _data_stages(beat,inventory_slide):
    dm=beat["data_motion"]
    if len(beat["targets"])!=1:
        raise ValueError(f"data-motion beat {beat['id']} requires one target")
    shape,target=_source_target(beat["targets"][0],inventory_slide)

    if dm["kind"]=="chart":
        effect=_chart_effect(dm,target,shape)
        duration=_chart_duration_ms(dm,shape)
        metadata=[]
    elif dm["kind"]=="number-counter":
        effect=_counter_effect(dm,target,shape)
        duration=dm["duration_ms"]
        metadata=[{"beat_id":beat["id"],**effect.pop("_compile_metadata")}]
    else:
        raise ValueError(f"unsupported data_motion kind {dm.get('kind')}")

    return [{
        "id":f"motion-{beat['id']}",
        "duration_ms":duration,
        "trigger":beat["timing_intent"],
        "effects":[effect],
    }],metadata


def _generic_stages(beat,inventory_slide):
    shapes=[]
    targets=[]
    for token in beat["targets"]:
        shape,target=_source_target(token,inventory_slide)
        shapes.append(shape)
        targets.append(target)

    recipe=generic_motion_recipe(
        beat["operation"],shapes,beat.get("motion_parameters")
    )
    if recipe is None:
        raise ValueError(f"unsupported generic operation {beat['operation']}")

    first_trigger=beat["timing_intent"]
    stages=[]

    if recipe["kind"]=="reveal":
        for i,(target,filter_name) in enumerate(zip(targets,recipe["filters"])):
            stages.append({
                "id":f"motion-{beat['id']}-{i+1}",
                "duration_ms":recipe["duration_ms"],
                "trigger":first_trigger if i==0 else "after-previous",
                "effects":[{
                    "type":"shape_entrance",
                    "target":target,
                    "filter":filter_name,
                }],
            })
    elif recipe["kind"]=="focus-pulse":
        target=targets[0]
        scale=recipe["scale"]
        stages=[
            {
                "id":f"motion-{beat['id']}-up",
                "duration_ms":recipe["up_duration_ms"],
                "trigger":first_trigger,
                "effects":[{
                    "type":"scale","target":target,
                    "from_x":1.0,"from_y":1.0,"to_x":scale,"to_y":scale,
                }],
            },
            {
                "id":f"motion-{beat['id']}-down",
                "duration_ms":recipe["down_duration_ms"],
                "trigger":"after-previous",
                "effects":[{
                    "type":"scale","target":target,
                    "from_x":scale,"from_y":scale,"to_x":1.0,"to_y":1.0,
                }],
            },
        ]
    elif recipe["kind"]=="motion-path":
        stages=[{
            "id":f"motion-{beat['id']}",
            "duration_ms":recipe["duration_ms"],
            "trigger":first_trigger,
            "effects":[{
                "type":"motion_path","target":targets[0],"points":recipe["points"],
            }],
        }]
    elif recipe["kind"]=="rotate":
        stages=[{
            "id":f"motion-{beat['id']}",
            "duration_ms":recipe["duration_ms"],
            "trigger":first_trigger,
            "effects":[{
                "type":"rotate","target":targets[0],"by_deg":recipe["by_deg"],
            }],
        }]
    else:
        raise AssertionError(recipe["kind"])

    return stages,[{
        "beat_id":beat["id"],
        "operation":beat["operation"],
        "recipe":recipe,
    }]


def _compile_slide(slide,inventory_slide):
    stage_ids_by_beat={}
    stages=[]
    metadata=[]
    unsupported=[]

    for beat in slide["beats"]:
        try:
            if isinstance(beat.get("data_motion"),dict):
                beat_stages,meta=_data_stages(beat,inventory_slide)
            elif beat.get("operation") in SUPPORTED_GENERIC_OPERATIONS:
                beat_stages,meta=_generic_stages(beat,inventory_slide)
            else:
                unsupported.append(beat["id"])
                continue
        except ValueError as exc:
            unsupported.append(beat["id"])
            metadata.append({"beat_id":beat["id"],"blocked_reason":str(exc)})
            continue

        stage_ids_by_beat[beat["id"]]=[stage["id"] for stage in beat_stages]
        stages.extend(beat_stages)
        metadata.extend(meta)

    if unsupported:
        return None,{
            "source_index":slide["source_index"],
            "reason":"unsupported-or-unresolved-motion",
            "unsupported_motion_beats":unsupported,
            "details":metadata,
        }

    click_beats=[]
    for click in slide["click_beats"]:
        stage_ids=[]
        for motion_id in click["motion_beats"]:
            stage_ids.extend(stage_ids_by_beat[motion_id])
        click_beats.append({"id":click["id"],"stages":stage_ids})

    return {
        "source_index":slide["source_index"],
        "stages":stages,
        "click_beats":click_beats,
    },metadata


def compile_director_patch(director_plan,inventory):
    errors=validate_director(director_plan,inventory)
    if errors:
        raise ValueError("Invalid director plan: "+"; ".join(errors))
    if director_plan.get("version")!="0.4":
        raise ValueError("generic semantic compiler requires Director v0.4")

    inv_by_index={slide["index"]:slide for slide in inventory.get("slides",[])}
    patch_slides=[]
    blocked=[]
    metadata=[]

    for slide in director_plan["slides"]:
        inv=inv_by_index.get(slide["source_index"])
        if inv is None:
            raise ValueError(f"source slide missing: {slide['source_index']}")
        patch_slide,meta=_compile_slide(slide,inv)
        if patch_slide is None:
            blocked.append(meta)
        else:
            patch_slides.append(patch_slide)
            metadata.extend(meta)

    if not patch_slides:
        raise ValueError("No slide can be compiled safely")

    return {
        "version":"0.5",
        "kind":"existing-deck-timeline-patch",
        "source_sha256":director_plan["source"]["pptx_sha256"],
        "slides":patch_slides,
        "compile_metadata":{
            "source_director_version":"0.4",
            "compiled_slide_count":len(patch_slides),
            "blocked_slides":blocked,
            "partial_deck":bool(blocked),
            "motion_recipes":metadata,
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
    patch=compile_director_patch(director,inventory)
    result=json.dumps(patch,ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(result+"\n",encoding="utf-8")
    else:
        print(result)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
