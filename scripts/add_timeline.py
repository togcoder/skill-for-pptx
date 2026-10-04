#!/usr/bin/env python3
"""Inject a packed native animation timeline into fresh PPTX slide XML.

Research backend for T006/T010. It supports motion-path, scale and rotate
behaviors from native-timeline-plan. It does not prove PowerPoint playback: the
exact output still requires native PowerPoint QA.

v0.1 plans retain the historical one-click packed writer for reproducibility.
v0.2 plans use presenter-paced click beats: multiple click groups can live on
one slide, while stages inside a beat use clickEffect / withEffect / afterEffect
semantics. Intermediate waypoints stay inside animMotion path data and never
become PowerPoint slides.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from lxml import etree as E

try:
    from .inspect_pptx import inspect, P
    from .pack_timeline import validate_timeline
except ImportError:
    from inspect_pptx import inspect, P
    from pack_timeline import validate_timeline

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P, "a": A}
ROOT_CTN_ID = 1
MAIN_SEQ_ID = 2
CLICK_BUCKET_ID = 3
PACKED_GROUP_ID = 4
FIRST_BEHAVIOR_ID = 10


def _q(tag):
    return f"{{{P}}}{tag}"


def _sub(parent, tag, **attrs):
    return E.SubElement(parent, _q(tag), **{k: str(v) for k, v in attrs.items()})


def _path_data(points):
    """Convert normalized absolute centers into a slide-relative polyline."""
    if not isinstance(points, list) or len(points) < 2:
        raise ValueError("motion path needs at least two points")
    start = points[0]
    if set(start) != {"x", "y"}:
        raise ValueError("invalid motion path start point")
    parts = ["M 0 0"]
    for point in points[1:]:
        if set(point) != {"x", "y"}:
            raise ValueError("invalid motion path point")
        dx = point["x"] - start["x"]
        dy = point["y"] - start["y"]
        if not all(type(v) in (int, float) and math.isfinite(v) for v in (dx, dy)):
            raise ValueError("nonfinite motion path point")
        parts.append(f"L {dx:.6f} {dy:.6f}")
    parts.append("E")
    return " ".join(parts)


def _percent(value, base):
    if type(value) not in (int, float) or type(base) not in (int, float):
        raise ValueError("scale values must be numeric")
    if not math.isfinite(value) or not math.isfinite(base) or value <= 0 or base <= 0:
        raise ValueError("scale values must be finite and positive")
    result = round(value / base * 100000)
    if result <= 0:
        raise ValueError("scale percentage underflow")
    return str(result)


def _rotation_units(degrees):
    if type(degrees) not in (int, float) or not math.isfinite(degrees):
        raise ValueError("rotation delta must be finite")
    value = round(degrees * 60000)
    if not -2147483554 <= value <= 2147483554:
        raise ValueError("rotation exceeds PowerPoint integer range")
    return str(value)


def _shape_map(root):
    """Map forced semantic names to numeric slide-local shape IDs."""
    result = {}
    for props in root.findall(".//p:cNvPr", NS):
        name = props.get("name", "")
        if not name.startswith("!!"):
            continue
        if name in result:
            raise ValueError(f"duplicate forced shape name: {name}")
        raw = props.get("id")
        if raw is None:
            raise ValueError(f"missing shape id: {name}")
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"nonnumeric shape id: {name}") from exc
        if value <= 0:
            raise ValueError(f"invalid shape id: {name}")
        result[name] = str(value)
    return result


def _behavior_ctn(parent, behavior_id, duration_ms, delay_ms):
    ctn = _sub(
        parent,
        "cTn",
        id=behavior_id,
        dur=duration_ms,
        fill="remove",
        nodeType="withEffect",
    )
    conditions = _sub(ctn, "stCondLst")
    _sub(conditions, "cond", delay=delay_ms)
    return ctn


def _motion_node(parent, effect, spid, behavior_id, duration_ms, delay_ms):
    motion = _sub(
        parent,
        "animMotion",
        origin="layout",
        path=_path_data(effect["points"]),
        pathEditMode="relative",
    )
    behavior = _sub(motion, "cBhvr")
    _behavior_ctn(behavior, behavior_id, duration_ms, delay_ms)
    target = _sub(behavior, "tgtEl")
    _sub(target, "spTgt", spid=spid)
    return motion


def _scale_node(parent, effect, initial, spid, behavior_id, duration_ms, delay_ms):
    scale = _sub(parent, "animScale")
    behavior = _sub(scale, "cBhvr")
    _behavior_ctn(behavior, behavior_id, duration_ms, delay_ms)
    target = _sub(behavior, "tgtEl")
    _sub(target, "spTgt", spid=spid)
    _sub(
        scale,
        "from",
        x=_percent(effect["from_w"], initial["w"]),
        y=_percent(effect["from_h"], initial["h"]),
    )
    _sub(
        scale,
        "to",
        x=_percent(effect["to_w"], initial["w"]),
        y=_percent(effect["to_h"], initial["h"]),
    )
    return scale


def _rotate_node(parent, effect, spid, behavior_id, duration_ms, delay_ms):
    rotate = _sub(
        parent,
        "animRot",
        by=_rotation_units(effect["to_deg"] - effect["from_deg"]),
    )
    behavior = _sub(rotate, "cBhvr")
    _behavior_ctn(behavior, behavior_id, duration_ms, delay_ms)
    target = _sub(behavior, "tgtEl")
    _sub(target, "spTgt", spid=spid)
    names = _sub(behavior, "attrNameLst")
    name = _sub(names, "attrName")
    name.text = "r"
    return rotate


def _build_legacy_timing(slide_plan, objects, forced_name_to_spid):
    """Build one PresentationML timing tree for a packed semantic slide."""
    initial = slide_plan["initial_objects"]
    stages = slide_plan["timeline"]
    if not stages:
        raise ValueError("timeline must not be empty")

    expected_names = {objects[oid]["morph_name"] for oid in initial}
    if set(forced_name_to_spid) != expected_names:
        missing = sorted(expected_names - set(forced_name_to_spid))
        extra = sorted(set(forced_name_to_spid) - expected_names)
        raise ValueError(f"source shape identities differ from timeline plan; missing={missing}, extra={extra}")

    total_duration = sum(stage["duration_ms"] for stage in stages)
    timing = E.Element(_q("timing"))
    tn_list = _sub(timing, "tnLst")

    root_par = _sub(tn_list, "par")
    root_ctn = _sub(
        root_par,
        "cTn",
        id=ROOT_CTN_ID,
        dur="indefinite",
        restart="never",
        nodeType="tmRoot",
    )
    root_children = _sub(root_ctn, "childTnLst")

    sequence = _sub(root_children, "seq", concurrent="1", nextAc="seek")
    seq_ctn = _sub(
        sequence,
        "cTn",
        id=MAIN_SEQ_ID,
        dur="indefinite",
        nodeType="mainSeq",
    )
    main_children = _sub(seq_ctn, "childTnLst")

    click_bucket = _sub(main_children, "par")
    click_bucket_ctn = _sub(click_bucket, "cTn", id=CLICK_BUCKET_ID, fill="hold")
    start_conditions = _sub(click_bucket_ctn, "stCondLst")
    _sub(start_conditions, "cond", delay="indefinite")
    on_begin = _sub(start_conditions, "cond", evt="onBegin", delay="0")
    _sub(on_begin, "tn", val=MAIN_SEQ_ID)
    click_bucket_children = _sub(click_bucket_ctn, "childTnLst")

    packed_par = _sub(click_bucket_children, "par")
    packed_ctn = _sub(
        packed_par,
        "cTn",
        id=PACKED_GROUP_ID,
        dur=total_duration,
        fill="hold",
        nodeType="clickEffect",
        grpId=PACKED_GROUP_ID,
    )
    packed_start = _sub(packed_ctn, "stCondLst")
    _sub(packed_start, "cond", delay="0")
    packed_children = _sub(packed_ctn, "childTnLst")

    animated = set()
    behavior_id = FIRST_BEHAVIOR_ID
    delay_ms = 0
    stage_receipts = []

    for stage in stages:
        effect_receipts = []
        for effect in stage["effects"]:
            oid = effect["target"]
            if oid not in initial:
                raise ValueError(f"effect targets object absent from initial slide: {oid}")
            name = objects[oid]["morph_name"]
            spid = forced_name_to_spid[name]
            kind = effect["type"]
            if kind == "motion_path":
                _motion_node(
                    packed_children,
                    effect,
                    spid,
                    behavior_id,
                    stage["duration_ms"],
                    delay_ms,
                )
            elif kind == "scale":
                _scale_node(
                    packed_children,
                    effect,
                    initial[oid],
                    spid,
                    behavior_id,
                    stage["duration_ms"],
                    delay_ms,
                )
            elif kind == "rotate":
                _rotate_node(
                    packed_children,
                    effect,
                    spid,
                    behavior_id,
                    stage["duration_ms"],
                    delay_ms,
                )
            elif kind == "visibility":
                raise ValueError("visibility timing is not implemented in T006 writer v0.1")
            else:
                raise ValueError(f"unsupported timeline effect: {kind}")
            animated.add(oid)
            effect_receipts.append(
                {"type": kind, "target": oid, "spid": spid, "behavior_id": behavior_id}
            )
            behavior_id += 1

        stage_receipts.append(
            {
                "id": stage["id"],
                "operation": stage["operation"],
                "delay_ms": delay_ms,
                "duration_ms": stage["duration_ms"],
                "effects": effect_receipts,
            }
        )
        delay_ms += stage["duration_ms"]

    previous = _sub(sequence, "prevCondLst")
    cond = _sub(previous, "cond", evt="onPrev", delay="0")
    _sub(_sub(cond, "tgtEl"), "sldTgt")

    following = _sub(sequence, "nextCondLst")
    cond = _sub(following, "cond", evt="onNext", delay="0")
    _sub(_sub(cond, "tgtEl"), "sldTgt")

    build_list = _sub(timing, "bldLst")
    for oid in sorted(animated):
        spid = forced_name_to_spid[objects[oid]["morph_name"]]
        _sub(build_list, "bldP", spid=spid, grpId="0", animBg="1")
        _sub(build_list, "bldP", spid=spid, grpId=PACKED_GROUP_ID, animBg="1")

    return timing, {
        "total_duration_ms": total_duration,
        "behavior_count": behavior_id - FIRST_BEHAVIOR_ID,
        "animated_objects": sorted(animated),
        "stage_receipts": stage_receipts,
    }



TRIGGER_NODE_TYPE = {
    "on_click": "clickEffect",
    "with_previous": "withEffect",
    "after_previous": "afterEffect",
}


def _resolved_click_beats(slide_plan):
    stages = slide_plan.get("timeline", [])
    stage_by_id = {stage["id"]: stage for stage in stages}
    beats = slide_plan.get("click_beats")
    if not beats:
        return [{
            "id": "legacy-packed-beat",
            "purpose": "Legacy single-click packed sequence.",
            "pause_after": "slide_complete",
            "stages": stages,
        }]
    resolved = []
    for beat in beats:
        resolved.append({
            "id": beat["id"],
            "purpose": beat["purpose"],
            "pause_after": beat.get("pause_after"),
            "stages": [stage_by_id[stage_id] for stage_id in beat["stages"]],
        })
    return resolved


def _build_click_beat_timing(slide_plan, objects, forced_name_to_spid):
    """Build presenter-paced click groups while keeping all beats on one slide."""
    initial = slide_plan["initial_objects"]
    beats = _resolved_click_beats(slide_plan)
    if not beats:
        raise ValueError("click_beats must not be empty")

    expected_names = {objects[oid]["morph_name"] for oid in initial}
    if set(forced_name_to_spid) != expected_names:
        missing = sorted(expected_names - set(forced_name_to_spid))
        extra = sorted(set(forced_name_to_spid) - expected_names)
        raise ValueError(
            f"source shape identities differ from timeline plan; missing={missing}, extra={extra}"
        )

    timing = E.Element(_q("timing"))
    tn_list = _sub(timing, "tnLst")
    root_par = _sub(tn_list, "par")
    root_ctn = _sub(
        root_par,
        "cTn",
        id=ROOT_CTN_ID,
        dur="indefinite",
        restart="never",
        nodeType="tmRoot",
    )
    root_children = _sub(root_ctn, "childTnLst")
    sequence = _sub(root_children, "seq", concurrent="1", nextAc="seek")
    seq_ctn = _sub(
        sequence,
        "cTn",
        id=MAIN_SEQ_ID,
        dur="indefinite",
        nodeType="mainSeq",
    )
    main_children = _sub(seq_ctn, "childTnLst")

    next_id = 3
    animated = set()
    stage_build_pairs = set()
    beat_receipts = []
    total_stage_duration = 0
    behavior_count = 0

    for beat_index, beat in enumerate(beats, 1):
        outer_id = next_id
        next_id += 1
        inner_id = next_id
        next_id += 1

        outer_par = _sub(main_children, "par")
        outer_ctn = _sub(outer_par, "cTn", id=outer_id, fill="hold")
        outer_start = _sub(outer_ctn, "stCondLst")
        _sub(outer_start, "cond", delay="indefinite")
        outer_children = _sub(outer_ctn, "childTnLst")

        inner_par = _sub(outer_children, "par")
        inner_ctn = _sub(inner_par, "cTn", id=inner_id, fill="hold")
        inner_start = _sub(inner_ctn, "stCondLst")
        _sub(inner_start, "cond", delay="0")
        beat_children = _sub(inner_ctn, "childTnLst")

        stage_receipts = []
        for stage_index, stage in enumerate(beat["stages"]):
            trigger = stage["trigger"]
            node_type = TRIGGER_NODE_TYPE.get(trigger)
            if node_type is None:
                raise ValueError(f"unsupported stage trigger: {trigger}")
            if stage_index == 0 and trigger != "on_click":
                raise ValueError(f"click beat {beat['id']} must start with on_click")
            if stage_index > 0 and trigger == "on_click":
                raise ValueError(f"nested on_click stage in click beat {beat['id']}")

            stage_group_id = next_id
            next_id += 1
            stage_par = _sub(beat_children, "par")
            stage_ctn = _sub(
                stage_par,
                "cTn",
                id=stage_group_id,
                dur=stage["duration_ms"],
                fill="hold",
                nodeType=node_type,
                grpId=stage_group_id,
            )
            stage_start = _sub(stage_ctn, "stCondLst")
            _sub(stage_start, "cond", delay="0")
            stage_children = _sub(stage_ctn, "childTnLst")

            effect_receipts = []
            stage_targets = set()
            for effect in stage["effects"]:
                oid = effect["target"]
                if oid not in initial:
                    raise ValueError(
                        f"effect targets object absent from initial slide: {oid}"
                    )
                name = objects[oid]["morph_name"]
                spid = forced_name_to_spid[name]
                behavior_id = next_id
                next_id += 1
                kind = effect["type"]
                if kind == "motion_path":
                    _motion_node(
                        stage_children,
                        effect,
                        spid,
                        behavior_id,
                        stage["duration_ms"],
                        0,
                    )
                elif kind == "scale":
                    _scale_node(
                        stage_children,
                        effect,
                        initial[oid],
                        spid,
                        behavior_id,
                        stage["duration_ms"],
                        0,
                    )
                elif kind == "rotate":
                    _rotate_node(
                        stage_children,
                        effect,
                        spid,
                        behavior_id,
                        stage["duration_ms"],
                        0,
                    )
                elif kind == "visibility":
                    raise ValueError(
                        "visibility timing is not implemented in T010 writer v0.2"
                    )
                else:
                    raise ValueError(f"unsupported timeline effect: {kind}")

                animated.add(oid)
                stage_targets.add(spid)
                behavior_count += 1
                effect_receipts.append({
                    "type": kind,
                    "target": oid,
                    "spid": spid,
                    "behavior_id": behavior_id,
                })

            for spid in stage_targets:
                stage_build_pairs.add((spid, str(stage_group_id)))

            total_stage_duration += stage["duration_ms"]
            stage_receipts.append({
                "id": stage["id"],
                "operation": stage["operation"],
                "trigger": trigger,
                "node_type": node_type,
                "group_id": stage_group_id,
                "duration_ms": stage["duration_ms"],
                "effects": effect_receipts,
            })

        beat_receipts.append({
            "index": beat_index,
            "id": beat["id"],
            "purpose": beat["purpose"],
            "pause_after": beat.get("pause_after"),
            "outer_time_node_id": outer_id,
            "inner_time_node_id": inner_id,
            "stages": stage_receipts,
        })

    previous = _sub(sequence, "prevCondLst")
    cond = _sub(previous, "cond", evt="onPrev", delay="0")
    _sub(_sub(cond, "tgtEl"), "sldTgt")
    following = _sub(sequence, "nextCondLst")
    cond = _sub(following, "cond", evt="onNext", delay="0")
    _sub(_sub(cond, "tgtEl"), "sldTgt")

    build_list = _sub(timing, "bldLst")
    animated_spids = sorted(
        {forced_name_to_spid[objects[oid]["morph_name"]] for oid in animated},
        key=int,
    )
    for spid in animated_spids:
        _sub(build_list, "bldP", spid=spid, grpId="0", animBg="1")
    for spid, group_id in sorted(stage_build_pairs, key=lambda item: (int(item[0]), int(item[1]))):
        _sub(build_list, "bldP", spid=spid, grpId=group_id, animBg="1")

    return timing, {
        "writer_mode": "presenter-paced-click-beats",
        "click_beat_count": len(beats),
        "total_stage_duration_ms": total_stage_duration,
        "behavior_count": behavior_count,
        "animated_objects": sorted(animated),
        "click_beats": beat_receipts,
    }


def build_timing(slide_plan, objects, forced_name_to_spid):
    """Dispatch legacy one-click or v0.2 presenter-paced click-beat timing."""
    if slide_plan.get("click_beats"):
        return _build_click_beat_timing(slide_plan, objects, forced_name_to_spid)
    timing, receipt = _build_legacy_timing(slide_plan, objects, forced_name_to_spid)
    receipt = {"writer_mode": "legacy-one-click-packed", "click_beat_count": 1, **receipt}
    return timing, receipt


def inspect_timing_root(root):
    """Structural checks for the exact subset this writer emits."""
    errors = []
    timings = root.findall("p:timing", NS)
    if len(timings) != 1:
        return {"errors": [f"expected exactly one timing element, found {len(timings)}"]}

    timing = timings[0]
    root_children = timing.findall("p:tnLst/*", NS)
    if len(root_children) != 1 or root_children[0].tag != _q("par"):
        errors.append("tnLst must contain exactly one root par for PowerPoint")

    ctn_ids = [node.get("id") for node in timing.findall(".//p:cTn", NS) if node.get("id")]
    if len(ctn_ids) != len(set(ctn_ids)):
        errors.append("duplicate cTn IDs")

    shape_ids = {node.get("id") for node in root.findall(".//p:cNvPr", NS) if node.get("id")}
    targets = [node.get("spid") for node in timing.findall(".//p:spTgt", NS)]
    missing = sorted({spid for spid in targets if spid not in shape_ids})
    if missing:
        errors.append(f"timing targets missing slide shapes: {missing}")

    build_targets = [node.get("spid") for node in timing.findall("p:bldLst/p:bldP", NS)]
    missing_build = sorted({spid for spid in build_targets if spid not in shape_ids})
    if missing_build:
        errors.append(f"build list targets missing slide shapes: {missing_build}")

    return {
        "errors": errors,
        "ctn_ids": ctn_ids,
        "target_spids": targets,
        "motion_count": len(timing.findall(".//p:animMotion", NS)),
        "scale_count": len(timing.findall(".//p:animScale", NS)),
        "rotate_count": len(timing.findall(".//p:animRot", NS)),
        "build_entries": len(timing.findall("p:bldLst/p:bldP", NS)),
    }


def patch(source, plan_path, destination):
    source, plan_path, destination = map(Path, (source, plan_path, destination))
    if destination.exists():
        raise ValueError("Refuse to overwrite an output")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors = validate_timeline(plan)
    if errors:
        raise ValueError("Invalid timeline plan: " + "; ".join(errors))
    objects = {obj["id"]: obj for obj in plan["objects"]}

    inventory = inspect(source)
    if inventory["errors"]:
        raise ValueError("Invalid source package: " + "; ".join(inventory["errors"]))
    if len(inventory["slides"]) != len(plan["slides"]):
        raise ValueError("Slide count differs from timeline plan")
    if any(slide["timing_elements"] for slide in inventory["slides"]):
        raise ValueError("Source must be fresh, without existing timing")

    parser = E.XMLParser(resolve_entities=False, no_network=True)
    updates = {}
    receipts = []

    with ZipFile(source) as src:
        for inventory_slide, plan_slide in zip(inventory["slides"], plan["slides"]):
            part = inventory_slide["part"]
            root = E.fromstring(src.read(part), parser)
            name_map = _shape_map(root)
            timing, receipt = build_timing(plan_slide, objects, name_map)

            insert_at = next(
                (i for i, child in enumerate(root) if child.tag == _q("extLst")),
                len(root),
            )
            root.insert(insert_at, timing)
            timing_report = inspect_timing_root(root)
            if timing_report["errors"]:
                raise ValueError(
                    f"Slide {inventory_slide['index']} timing failed structural inspection: "
                    + "; ".join(timing_report["errors"])
                )
            updates[part] = E.tostring(
                root, encoding="UTF-8", xml_declaration=True, standalone=True
            )
            receipts.append(
                {
                    "slide": inventory_slide["index"],
                    "part": part,
                    **receipt,
                    "timing": timing_report,
                }
            )

        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=destination.parent, suffix=".pptx", delete=False
            ) as handle:
                temporary = Path(handle.name)
            with ZipFile(temporary, "w", ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(
                        item,
                        updates.get(item.filename, src.read(item.filename)),
                    )

            final_inventory = inspect(temporary)
            if final_inventory["errors"]:
                raise ValueError("Patched package failed inventory")
            if [s["timing_elements"] for s in final_inventory["slides"]] != [1] * len(plan["slides"]):
                raise ValueError("Patched package timing count mismatch")
            os.link(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    return {
        "slides": len(plan["slides"]),
        "packed_timing_groups": len(receipts),
        "receipts": receipts,
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "full_schema_validated": False,
        "powerpoint_playback_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("plan")
    parser.add_argument("destination")
    args = parser.parse_args()
    print(json.dumps(patch(args.source, args.plan, args.destination), indent=2))


if __name__ == "__main__":
    main()
