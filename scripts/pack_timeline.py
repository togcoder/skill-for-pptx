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


def _initial_frame(frame):
    """Keep authored opening text even when it is a state-local override.

    Later phase-label changes remain outside this geometry-only backend.
    Dropping the initial override can leave a text object with no text body.
    """
    result = _geom(frame)
    if "text" in frame:
        result["text"] = frame["text"]
    return result


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
    if plan["version"] not in ("0.1", "0.2"):
        errors.append("version must be 0.1 or 0.2")
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
        beats = slide.get("click_beats")
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

        if plan["version"] == "0.2":
            if not isinstance(beats, list) or not beats:
                errors.append(f"{slide.get('id','slide')}: click_beats must be nonempty for v0.2")
            else:
                seen_beat_ids = set()
                flattened = []
                for beat in beats:
                    if not isinstance(beat, dict):
                        errors.append(f"{slide.get('id','slide')}: click beat must be an object")
                        continue
                    beat_id = beat.get("id")
                    if not isinstance(beat_id, str) or not beat_id:
                        errors.append(f"{slide.get('id','slide')}: click beat id must be nonempty")
                    elif beat_id in seen_beat_ids:
                        errors.append(f"{slide.get('id','slide')}: duplicate click beat id {beat_id}")
                    else:
                        seen_beat_ids.add(beat_id)
                    if not isinstance(beat.get("purpose"), str) or not beat["purpose"].strip():
                        errors.append(f"{slide.get('id','slide')}: click beat {beat_id} purpose must be nonempty")
                    beat_stages = beat.get("stages")
                    if not isinstance(beat_stages, list) or not beat_stages:
                        errors.append(f"{slide.get('id','slide')}: click beat {beat_id} stages must be nonempty")
                        continue
                    flattened.extend(beat_stages)
                    if beat_stages[0] not in stage_ids:
                        errors.append(f"{slide.get('id','slide')}: click beat {beat_id} starts with unknown stage")
                if flattened != stage_ids:
                    errors.append(f"{slide.get('id','slide')}: click_beats must partition timeline stages in order exactly once")

        beat_starts = set()
        if isinstance(beats, list):
            for beat in beats:
                if isinstance(beat, dict) and isinstance(beat.get("stages"), list) and beat["stages"]:
                    beat_starts.add(beat["stages"][0])

        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                errors.append("stage must be an object")
                continue
            trigger = stage.get("trigger")
            if trigger not in ("on_click", "with_previous", "after_previous"):
                errors.append(f"{stage.get('id','stage')}: unsupported trigger {trigger}")
            if plan["version"] == "0.2":
                should_click = stage.get("id") in beat_starts
                if should_click and trigger != "on_click":
                    errors.append(f"{stage.get('id','stage')}: first stage of a click beat must be on_click")
                if not should_click and trigger == "on_click":
                    errors.append(f"{stage.get('id','stage')}: on_click must start a declared click beat")
            elif i == 0 and trigger != "on_click":
                errors.append(f"{stage.get('id','stage')}: first legacy stage must be on_click")
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
            "trigger": "on_click",
            "duration_ms": 350 * intent["orbit_segments"],
            "effects": _orbit_effects(orbit_states, object_ids),
        },
        {
            "id": "focus",
            "operation": "focus",
            "trigger": "on_click",
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
            "trigger": "on_click",
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
        "version": "0.2",
        "kind": "native-timeline-plan",
        "brief": intent["prompt"],
        "canvas": legacy["canvas"],
        "data_provenance": legacy["data_provenance"],
        "objects": legacy["objects"],
        "slides": [{
            "id": "radial-drilldown",
            "message": "Packed radial drill-down sequence",
            "initial_objects": {oid: _initial_frame(state_by_id["core"]["objects"][oid]) for oid in object_ids},
            "timeline": stages,
            "click_beats": [
                {
                    "id": "beat-reveal",
                    "purpose": "Reveal the system structure, then hold so the presenter can explain the topology.",
                    "stages": ["burst"],
                    "pause_after": "presenter_explanation",
                },
                {
                    "id": "beat-orbit",
                    "purpose": "Show the relationship/orbit as a distinct presenter-controlled idea.",
                    "stages": ["orbit"],
                    "pause_after": "presenter_explanation",
                },
                {
                    "id": "beat-drill-down",
                    "purpose": "Move attention to the selected node and immediately unfold its internal layers as one continuous drill-down.",
                    "stages": ["focus", "split"],
                    "pause_after": "presenter_explanation",
                },
                {
                    "id": "beat-close-detail",
                    "purpose": "Close the detail view and return to the system context as one continuous resolution.",
                    "stages": ["reassemble", "restore"],
                    "pause_after": "slide_complete",
                },
            ],
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
                "click_beat_count": 4,
                "presenter_paced": True,
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
