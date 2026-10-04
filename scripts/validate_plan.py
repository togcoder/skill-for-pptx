#!/usr/bin/env python3
"""Validate the v0.1 motion-plan contract. No PPTX generation or playback claims."""
import argparse
import json
import math
from pathlib import Path
import re

KINDS = {"shape", "text", "image", "group", "chart", "video"}
ID = re.compile(r"^[a-z][a-z0-9-]{0,63}$")


def number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def validate(plan):
    errors = []
    if not isinstance(plan, dict):
        return ["plan: must be an object"]
    required = {"version", "brief", "canvas", "data_provenance", "objects", "states", "transitions"}
    for key in sorted(required - plan.keys()):
        errors.append(f"plan: missing {key}")
    if errors:
        return errors
    if plan["version"] != "0.1":
        errors.append("version: must be 0.1")
    if not isinstance(plan["brief"], str) or not plan["brief"].strip():
        errors.append("brief: must be nonempty text")
    canvas = plan["canvas"]
    if not isinstance(canvas, dict) or canvas.get("units") != "normalized":
        errors.append("canvas: must use normalized units")
    elif any(not number(canvas.get(k)) or canvas[k] <= 0 for k in ("width", "height")):
        errors.append("canvas: width and height must be positive finite numbers")
    if plan["data_provenance"] not in ("synthetic", "user-provided", "none"):
        errors.append("data_provenance: unsupported value")
    if any(not isinstance(plan[k], list) for k in ("objects", "states", "transitions")):
        return errors + ["objects, states and transitions must be arrays"]
    objects = {}
    names = set()
    for obj in plan["objects"]:
        if not isinstance(obj, dict):
            errors.append("object: must be an object")
            continue
        oid = obj.get("id")
        if not isinstance(oid, str) or not ID.fullmatch(oid):
            errors.append("object.id: invalid or missing")
            continue
        if oid in objects:
            errors.append(f"object {oid}: duplicate id")
        objects[oid] = obj
        if not isinstance(obj.get("kind"), str) or obj.get("kind") not in KINDS:
            errors.append(f"object {oid}: unsupported kind")
        if type(obj.get("persistent")) is not bool:
            errors.append(f"object {oid}: persistent must be boolean")
        name = obj.get("morph_name")
        if not isinstance(name, str) or not name.startswith("!!") or len(name) <= 2:
            errors.append(f"object {oid}: morph_name must start with !! and include a name")
        elif name in names:
            errors.append(f"object {oid}: duplicate morph_name {name}")
        else:
            names.add(name)
    if not objects:
        errors.append("objects: at least one is required")

    states = {}
    ordered_ids = []
    for state in plan["states"]:
        if not isinstance(state, dict) or not isinstance(state.get("id"), str) or not ID.fullmatch(state["id"]):
            errors.append("state.id: invalid or missing")
            continue
        sid = state["id"]
        if sid in states:
            errors.append(f"state {sid}: duplicate id")
        states[sid] = state
        ordered_ids.append(sid)
        if not isinstance(state.get("message"), str) or not state["message"].strip():
            errors.append(f"state {sid}: message is required")
        frames = state.get("objects")
        if not isinstance(frames, dict):
            errors.append(f"state {sid}: objects must be a mapping")
            continue
        for oid, frame in frames.items():
            where = f"state {sid}/{oid}"
            if oid not in objects:
                errors.append(f"{where}: unknown object")
            if not isinstance(frame, dict):
                errors.append(f"{where}: frame must be an object")
                continue
            keys = ("x", "y", "w", "h", "rotation_deg", "opacity")
            if any(not number(frame.get(k)) for k in keys):
                errors.append(f"{where}: geometry must contain finite numeric values")
                continue
            if frame["w"] <= 0 or frame["h"] <= 0:
                errors.append(f"{where}: dimensions must be positive")
            if not 0 <= frame["opacity"] <= 1:
                errors.append(f"{where}: opacity outside 0..1")
            outside = frame["x"] < 0 or frame["y"] < 0 or frame["x"] + frame["w"] > 1.000001 or frame["y"] + frame["h"] > 1.000001
            if type(frame.get("off_canvas", False)) is not bool:
                errors.append(f"{where}: off_canvas must be boolean")
            if outside and frame.get("off_canvas") is not True:
                errors.append(f"{where}: off-canvas geometry must be intentional")
        for oid, obj in objects.items():
            if obj.get("persistent") is True and oid not in frames:
                errors.append(f"state {sid}: persistent object {oid} is missing")
    if len(ordered_ids) < 2:
        errors.append("states: at least two are required")

    expected = list(zip(ordered_ids, ordered_ids[1:]))
    edges = []
    for trans in plan["transitions"]:
        if not isinstance(trans, dict):
            errors.append("transition: must be an object")
            continue
        src, dst = trans.get("from"), trans.get("to")
        if not isinstance(src, str) or not isinstance(dst, str):
            errors.append("transition: from and to must be state IDs")
            continue
        edges.append((src, dst))
        kind = trans.get("kind")
        if kind not in ("morph", "cut", "fade"):
            errors.append(f"transition {src}/{dst}: unsupported kind")
        duration = trans.get("duration_ms")
        if not number(duration) or duration < 0 or (kind != "cut" and duration == 0):
            errors.append(f"transition {src}/{dst}: invalid duration_ms")
        if kind == "cut" and duration != 0:
            errors.append(f"transition {src}/{dst}: cut duration must be zero")
        tracked = trans.get("track")
        if not isinstance(tracked, list) or any(not isinstance(v, str) for v in tracked):
            errors.append(f"transition {src}/{dst}: track must be an array of object IDs")
            continue
        if len(tracked) != len(set(tracked)):
            errors.append(f"transition {src}/{dst}: duplicate tracked object")
        if kind == "morph" and not tracked:
            errors.append(f"transition {src}/{dst}: morph needs tracked objects")
        for oid in tracked:
            if oid not in objects:
                errors.append(f"transition {src}/{dst}: unknown tracked object {oid}")
                continue
            if kind == "morph" and objects[oid].get("kind") in ("chart", "video"):
                errors.append(f"transition {src}/{dst}: {oid} cannot claim geometric morph in v0.1")
            for sid in (src, dst):
                frames = states.get(sid, {}).get("objects", {})
                if not isinstance(frames, dict) or oid not in frames:
                    errors.append(f"transition {src}/{dst}: {oid} absent from {sid}")
    if edges != expected:
        errors.append("transitions: must connect every consecutive state exactly once in order")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        errors = validate(json.loads(args.plan.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"valid": not errors, "errors": errors, "scope": "motion-plan-v0.1", "pptx_generated": False, "playback_verified": False}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
