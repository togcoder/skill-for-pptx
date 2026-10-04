#!/usr/bin/env python3
"""Pack the T005 radial-drilldown intent into one abstract native timeline slide.

This is a planning compiler, not a PowerPoint timing-XML writer. It reuses the
legacy geometry oracle, but converts waypoint states into effects/tracks so
waypoints are not PowerPoint slides. See references/native-timeline.md.
"""
import argparse
import json
import math
from pathlib import Path

from choreography import OPS, compile_intent

EPS = 1e-10
GEOM_KEYS = ("x", "y", "w", "h", "rotation_deg", "opacity")


def _geom(frame):
    return {k: frame[k] for k in GEOM_KEYS}


def _center(frame):
    return {
        "x": frame["x"] + frame["w"] / 2,
        "y": frame["y"] + frame["h"] / 2,
    }


def _different(a, b):
    return abs(a - b) > EPS


def _pair_effects(source, target, object_ids):
    effects = []
    for oid in object_ids:
        a = source["objects"][oid]
        b = target["objects"][oid]
        ca, cb = _center(a), _center(b)
        if _different(ca["x"], cb["x"]) or _different(ca["y"], cb["y"]):
            effects.append({
                "type": "motion_path",
                "target": oid,
                "path_kind": "polyline",
                "points": [ca, cb],
            })
        if _different(a["w"], b["w"]) or _different(a["h"], b["h"]):
            effects.append({
                "type": "scale",
                "target": oid,
                "from_w": a["w"],
                "from_h": a["h"],
                "to_w": b["w"],
                "to_h": b["h"],
            })
        if _different(a["rotation_deg"], b["rotation_deg"]):
            effects.append({
                "type": "rotate",
                "target": oid,
                "from_deg": a["rotation_deg"],
                "to_deg": b["rotation_deg"],
            })
    return effects


def _orbit_effects(states, object_ids):
    effects = []
    for oid in object_ids:
        points = [_center(s["objects"][oid]) for s in states]
        if any(_different(points[i]["x"], points[i+1]["x"]) or
               _different(points[i]["y"], points[i+1]["y"])
               for i in range(len(points)-1)):
            effects.append({
                "type": "motion_path",
                "target": oid,
                "path_kind": "polyline",
                "points": points,
            })
    return effects


def validate_timeline(plan):
    errors = []
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    required = {"version", "kind", "brief", "canvas", "data_provenance",
                "objects", "slides", "research_metadata"}
    errors += [f"missing field: {k}" for k in sorted(required - plan.keys())]
    if errors:
        return errors
    if plan["version"] != "0.1":
        errors.append("version must be 0.1")
    if plan["kind"] != "native-timeline-plan":
        errors.append("kind must be native-timeline-plan")
    if not isinstance(plan["objects"], list) or not plan["objects"]:
        errors.append("objects must be a nonempty list")
        return errors
    object_ids = [o.get("id") for o in plan["objects"] if isinstance(o, dict)]
    if len(object_ids) != len(plan["objects"]) or any(not isinstance(x, str) or not x for x in object_ids):
        errors.append("every object needs a nonempty id")
        return errors
    if len(object_ids) != len(set(object_ids)):
        errors.append("object ids must be unique")
    if not isinstance(plan["slides"], list) or not plan["slides"]:
        errors.append("slides must be a nonempty list")
        return errors

    for slide in plan["slides"]:
        if not isinstance(slide, dict):
            errors.append("slide must be an object")
            continue
        initial = slide.get("initial_objects")
        stages = slide.get("timeline")
        if not isinstance(initial, dict):
            errors.append(f"{slide.get('id','slide')}: initial_objects must be an object")
            continue
        missing = set(object_ids) - set(initial)
        if missing:
            errors.append(f"{slide.get('id','slide')}: missing initial objects: {sorted(missing)}")
        if not isinstance(stages, list) or not stages:
            errors.append(f"{slide.get('id','slide')}: timeline must be nonempty")
            continue
        stage_ids = [s.get("id") for s in stages if isinstance(s, dict)]
        if len(stage_ids) != len(set(stage_ids)):
            errors.append(f"{slide.get('id','slide')}: stage ids must be unique")
        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                errors.append("stage must be an object")
                continue
            trigger = stage.get("trigger")
            expected = "on_click" if i == 0 else "after_previous"
            if trigger != expected:
                errors.append(f"{stage.get('id','stage')}: trigger must be {expected}")
            duration = stage.get("duration_ms")
            if type(duration) is not int or duration <= 0:
                errors.append(f"{stage.get('id','stage')}: duration_ms must be positive integer")
            effects = stage.get("effects")
            if not isinstance(effects, list):
                errors.append(f"{stage.get('id','stage')}: effects must be a list")
                continue
            for effect in effects:
                if not isinstance(effect, dict):
                    errors.append("effect must be an object")
                    continue
                target = effect.get("target")
                if target not in object_ids:
                    errors.append(f"unknown effect target: {target}")
                    continue
                kind = effect.get("type")
                if kind == "motion_path":
                    points = effect.get("points")
                    if not isinstance(points, list) or len(points) < 2:
                        errors.append(f"{target}: motion path needs at least two points")
                    else:
                        for point in points:
                            if not isinstance(point, dict) or set(point) != {"x", "y"}:
                                errors.append(f"{target}: invalid motion point")
                                break
                            if any(type(point[k]) not in (int, float) or not math.isfinite(point[k]) for k in ("x", "y")):
                                errors.append(f"{target}: nonfinite motion point")
                                break
                elif kind == "scale":
                    for key in ("from_w", "from_h", "to_w", "to_h"):
                        value = effect.get(key)
                        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                            errors.append(f"{target}: invalid scale {key}")
                elif kind == "rotate":
                    for key in ("from_deg", "to_deg"):
                        value = effect.get(key)
                        if type(value) not in (int, float) or not math.isfinite(value):
                            errors.append(f"{target}: invalid rotation {key}")
                elif kind != "visibility":
                    errors.append(f"unsupported effect type: {kind}")

    meta = plan["research_metadata"].get("motion_packing", {})
    if meta.get("final_slide_count") != len(plan["slides"]):
        errors.append("motion_packing.final_slide_count mismatch")
    if plan["slides"]:
        stage_count = sum(len(s.get("timeline", [])) for s in plan["slides"])
        if meta.get("packed_motion_events") != stage_count:
            errors.append("motion_packing.packed_motion_events mismatch")
    return errors


def compile_packed_timeline(intent):
    legacy = compile_intent(intent)
    state_by_id = {s["id"]: s for s in legacy["states"]}
    object_ids = [o["id"] for o in legacy["objects"]]

    orbit_states = [state_by_id["burst"]] + [
        s for s in legacy["states"] if s["id"].startswith("orbit-")
    ]
    final_orbit = orbit_states[-1]

    stages = [
        {
            "id": "burst",
            "operation": "burst",
            "trigger": "on_click",
            "duration_ms": 1000,
            "effects": _pair_effects(state_by_id["core"], state_by_id["burst"], object_ids),
        },
        {
            "id": "orbit",
            "operation": "orbit",
            "trigger": "after_previous",
            "duration_ms": 350 * intent["orbit_segments"],
            "effects": _orbit_effects(orbit_states, object_ids),
        },
        {
            "id": "focus",
            "operation": "focus",
            "trigger": "after_previous",
            "duration_ms": 1000,
            "effects": _pair_effects(final_orbit, state_by_id["focus"], object_ids),
        },
        {
            "id": "split",
            "operation": "split",
            "trigger": "after_previous",
            "duration_ms": 1000,
            "effects": _pair_effects(state_by_id["focus"], state_by_id["split"], object_ids),
        },
        {
            "id": "reassemble",
            "operation": "reassemble",
            "trigger": "after_previous",
            "duration_ms": 1000,
            "effects": _pair_effects(state_by_id["split"], state_by_id["reassemble"], object_ids),
        },
        {
            "id": "restore",
            "operation": "restore",
            "trigger": "after_previous",
            "duration_ms": 1000,
            "effects": _pair_effects(state_by_id["reassemble"], state_by_id["restore"], object_ids),
        },
    ]

    plan = {
        "version": "0.1",
        "kind": "native-timeline-plan",
        "brief": intent["prompt"],
        "canvas": legacy["canvas"],
        "data_provenance": legacy["data_provenance"],
        "objects": legacy["objects"],
        "slides": [{
            "id": "radial-drilldown",
            "message": "Packed radial drill-down sequence",
            "initial_objects": {oid: _geom(state_by_id["core"]["objects"][oid]) for oid in object_ids},
            "timeline": stages,
            "expected_final_objects": {oid: _geom(state_by_id["restore"]["objects"][oid]) for oid in object_ids},
        }],
        "research_metadata": {
            "source_recipe": "radial-drilldown",
            "source_architecture": "legacy-state-per-slide-morph-baseline",
            "dynamic_phase_text": "not yet compiled; geometry/motion packing only",
            "motion_packing": {
                "policy": "resource-local-native-timeline",
                "semantic_scene_count": 1,
                "legacy_state_count": len(legacy["states"]),
                "final_slide_count": 1,
                "requested_motion_events": len(intent["operations"]),
                "packed_motion_events": len(stages),
                "packing_ratio": len(stages),
                "resource_set_changes": 0,
                "native_playback_verified": False,
            },
        },
    }
    errors = validate_timeline(plan)
    if errors:
        raise ValueError("; ".join(errors))
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intent", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    intent = json.loads(args.intent.read_text(encoding="utf-8"))
    plan = compile_packed_timeline(intent)
    with args.output.open("x", encoding="utf-8") as out:
        json.dump(plan, out, ensure_ascii=False, indent=2)
        out.write("\n")
    meta = plan["research_metadata"]["motion_packing"]
    print(json.dumps({
        "slides": meta["final_slide_count"],
        "legacy_states": meta["legacy_state_count"],
        "packed_motion_events": meta["packed_motion_events"],
        "playback_verified": False,
        "output": str(args.output),
    }))


if __name__ == "__main__":
    main()
