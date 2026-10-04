#!/usr/bin/env python3
"""Create controlled motion-path origin/fill variants from one timed PPTX.

This is an experiment tool. It never modifies the production timing writer and
does not claim that any variant plays correctly in PowerPoint.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree as E

try:
    from .inspect_pptx import inspect, P
    from .pack_timeline import validate_timeline
except ImportError:
    from inspect_pptx import inspect, P
    from pack_timeline import validate_timeline

NS = {"p": P}
VARIANTS = (
    ("local-remove", "stage-local", "remove"),
    ("local-hold", "stage-local", "hold"),
    ("anchored-remove", "authored-layout", "remove"),
    ("anchored-hold", "authored-layout", "hold"),
)


def _format(value):
    if not math.isfinite(value):
        raise ValueError("nonfinite path coordinate")
    if abs(value) < 0.0000005:
        value = 0.0
    return f"{value:.6f}"


def _move_format(value):
    return "0" if abs(value) < 0.0000005 else _format(value)


def stage_local_path(points):
    start = points[0]
    parts = ["M", "0", "0"]
    for point in points[1:]:
        parts += ["L", _format(point["x"]-start["x"]), _format(point["y"]-start["y"])]
    return " ".join(parts+["E"])


def authored_layout_path(points, initial_center):
    parts = []
    for index,point in enumerate(points):
        formatter = _move_format if index == 0 else _format
        parts += ["M" if index == 0 else "L",
                  formatter(point["x"]-initial_center["x"]),
                  formatter(point["y"]-initial_center["y"])]
    return " ".join(parts+["E"])


def _shape_ids(root):
    result = {}
    for props in root.findall(".//p:cNvPr",NS):
        name = props.get("name")
        if name and name.startswith("!!"):
            result[name] = props.get("id")
    return result


def _rewrite(source, plan, basis, fill, destination):
    inventory = inspect(source)
    if inventory["errors"] or len(inventory["slides"]) != 1:
        raise ValueError("expected one valid source slide")
    slide_plan = plan["slides"][0]
    objects = {o["id"]:o for o in plan["objects"]}
    parser = E.XMLParser(resolve_entities=False,no_network=True)
    slide_part = inventory["slides"][0]["part"]
    with ZipFile(source) as src:
        root = E.fromstring(src.read(slide_part),parser)
        ids = _shape_ids(root)
        stage_by_delay = {}
        delay = 0
        for stage in slide_plan["timeline"]:
            stage_by_delay[delay] = stage
            delay += stage["duration_ms"]
        seen = []
        for motion in root.findall(".//p:animMotion",NS):
            behavior = motion.find("p:cBhvr",NS)
            ctn = behavior.find("p:cTn",NS)
            cond = ctn.find("p:stCondLst/p:cond",NS)
            spid = behavior.find("p:tgtEl/p:spTgt",NS).get("spid")
            delay_ms = int(cond.get("delay"))
            stage = stage_by_delay.get(delay_ms)
            if stage is None:
                raise ValueError(f"unexpected delay: {delay_ms}")
            effects = [e for e in stage["effects"] if
                       e["type"] == "motion_path" and
                       ids[objects[e["target"]]["morph_name"]] == spid]
            if len(effects) != 1:
                raise ValueError("motion effect mapping is not unique")
            effect = effects[0]
            frame = slide_plan["initial_objects"][effect["target"]]
            center = {"x":frame["x"]+frame["w"]/2,"y":frame["y"]+frame["h"]/2}
            path = (stage_local_path(effect["points"]) if basis == "stage-local"
                    else authored_layout_path(effect["points"],center))
            motion.set("path",path)
            ctn.set("fill",fill)
            seen.append({"stage":stage["id"],"delay_ms":delay_ms,
                         "duration_ms":int(ctn.get("dur")),"path":path,"fill":fill})
        if len(seen) != 2:
            raise ValueError(f"expected two motion behaviors, found {len(seen)}")
        replacement = E.tostring(root,encoding="UTF-8",xml_declaration=True,standalone=True)
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent,suffix=".pptx",delete=False) as handle:
            temporary = Path(handle.name)
        try:
            with ZipFile(temporary,"w",ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(item,replacement if item.filename == slide_part else src.read(item.filename))
            if inspect(temporary)["errors"]:
                raise ValueError("variant failed package inventory")
            os.link(temporary,destination)
        finally:
            temporary.unlink(missing_ok=True)
    return seen


def build_matrix(source, plan_path, output_dir):
    source,plan_path,output_dir = Path(source),Path(plan_path),Path(output_dir)
    if output_dir.exists():
        raise ValueError("use a fresh matrix directory")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    errors = validate_timeline(plan)
    if errors:
        raise ValueError("invalid plan: "+"; ".join(errors))
    output_dir.mkdir(parents=True)
    source_parts = {}
    with ZipFile(source) as z:
        source_parts = {item.filename:hashlib.sha256(z.read(item.filename)).hexdigest()
                        for item in z.infolist()}
    results = []
    for name,basis,fill in VARIANTS:
        destination = output_dir/f"{name}.pptx"
        receipts = _rewrite(source,plan,basis,fill,destination)
        with ZipFile(destination) as z:
            part_hashes = {item.filename:hashlib.sha256(z.read(item.filename)).hexdigest()
                           for item in z.infolist()}
        changed_parts = sorted(k for k in source_parts if source_parts[k] != part_hashes.get(k))
        results.append({"variant":name,"basis":basis,"fill":fill,
                        "candidate":str(destination),
                        "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
                        "changed_uncompressed_parts":changed_parts,
                        "behaviors":receipts})
    report = {"source":str(source),
              "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "variants":results,"powerpoint_playback_verified":False}
    (output_dir/"matrix-build.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path)
    parser.add_argument("plan",type=Path)
    parser.add_argument("output_dir",type=Path)
    args = parser.parse_args()
    print(json.dumps(build_matrix(args.source,args.plan,args.output_dir),indent=2))
