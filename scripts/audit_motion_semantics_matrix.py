#!/usr/bin/env python3
"""Verify that final motion-semantics PPTX variants differ only as intended."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

try:
    from .inspect_pptx import inspect, P
except ImportError:
    from inspect_pptx import inspect, P

NS={"p":P}
EXPECTED={
    "local-remove": ("remove",["M 0 0 L 0.250000 0.000000 E"]*2),
    "local-hold": ("hold",["M 0 0 L 0.250000 0.000000 E"]*2),
    "anchored-remove": ("remove",[
        "M 0 0 L 0.250000 0.000000 E",
        "M 0.250000 0 L 0.500000 0.000000 E",
    ]),
    "anchored-hold": ("hold",[
        "M 0 0 L 0.250000 0.000000 E",
        "M 0.250000 0 L 0.500000 0.000000 E",
    ]),
}


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _normalized_slide(data):
    root=E.fromstring(data)
    for node in root.findall(".//p:animMotion",NS):
        node.set("path","__PATH_VARIANT__")
        node.find("p:cBhvr/p:cTn",NS).set("fill","__FILL_VARIANT__")
    return E.tostring(root,method="c14n")


def audit(files):
    findings=[]
    result={}
    baseline_parts=None
    baseline_normalized=None
    for name,path in files.items():
        path=Path(path)
        inventory=inspect(path)
        if inventory["errors"] or len(inventory["slides"])!=1:
            findings.append(f"{name}: package inventory failed")
            continue
        with ZipFile(path) as z:
            crc=z.testzip()
            if crc:
                findings.append(f"{name}: CRC failure {crc}")
            parts={item.filename:z.read(item.filename) for item in z.infolist()}
        slide_part=inventory["slides"][0]["part"]
        root=E.fromstring(parts[slide_part])
        motions=root.findall(".//p:animMotion",NS)
        rows=[]
        for node in motions:
            ctn=node.find("p:cBhvr/p:cTn",NS)
            rows.append({
                "path":node.get("path"),
                "fill":ctn.get("fill"),
                "origin":node.get("origin"),
                "path_edit_mode":node.get("pathEditMode"),
                "delay_ms":int(ctn.find("p:stCondLst/p:cond",NS).get("delay")),
                "duration_ms":int(ctn.get("dur")),
                "target_spid":node.find("p:cBhvr/p:tgtEl/p:spTgt",NS).get("spid"),
            })
        rows.sort(key=lambda row:row["delay_ms"])
        expected_fill,expected_paths=EXPECTED[name]
        if [row["path"] for row in rows]!=expected_paths:
            findings.append(f"{name}: paths differ from frozen matrix")
        if [row["fill"] for row in rows]!=[expected_fill,expected_fill]:
            findings.append(f"{name}: fill differs from frozen matrix")
        if [row["delay_ms"] for row in rows]!=[0,900]:
            findings.append(f"{name}: delays differ")
        if [row["duration_ms"] for row in rows]!=[900,900]:
            findings.append(f"{name}: durations differ")
        if any(row["origin"]!="layout" or row["path_edit_mode"]!="relative" for row in rows):
            findings.append(f"{name}: origin/pathEditMode differs")
        if len({row["target_spid"] for row in rows})!=1:
            findings.append(f"{name}: stages do not target one object")
        click_groups=len(root.findall(".//p:cTn[@nodeType='clickEffect']",NS))
        if len(rows)!=2 or click_groups!=1:
            findings.append(f"{name}: expected two motions and one click group")
        non_slide={part:_sha(data) for part,data in parts.items() if part!=slide_part}
        normalized=_normalized_slide(parts[slide_part])
        if baseline_parts is None:
            baseline_parts=non_slide
            baseline_normalized=normalized
        else:
            if non_slide!=baseline_parts:
                findings.append(f"{name}: non-slide package parts differ")
            if normalized!=baseline_normalized:
                findings.append(f"{name}: slide differs beyond path/fill attributes")
        result[name]={"path":str(path),"sha256":_sha(path.read_bytes()),
                      "slide_part":slide_part,"motion_count":len(rows),
                      "click_group_count":click_groups,"behaviors":rows,
                      "powerpoint_playback_verified":False}
    return {"findings":findings,"variants":result,
            "normalization":"Only p:animMotion@path and its p:cBhvr/p:cTn@fill replaced before canonical comparison.",
            "evidence_boundary":"Package and timing comparison only; no native playback.",
            "powerpoint_playback_verified":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory",type=Path)
    args=parser.parse_args()
    files={name:args.directory/("T006_motion_semantics_"+name.replace("-","_")+".pptx")
           for name in EXPECTED}
    report=audit(files)
    print(json.dumps(report,indent=2))
    raise SystemExit(bool(report["findings"]))
