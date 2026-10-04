#!/usr/bin/env python3
"""Read exact PPTX evidence independently of the timing writer.

Restricted to flat native shapes and T006 M/L polylines. The layout-origin
coordinate model is diagnostic, not a PowerPoint emulator or playback proof.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E
from inspect_pptx import inspect

NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def polyline(value):
    tokens = value.split()
    points = []
    i = 0
    while i < len(tokens):
        command = tokens[i]
        if command == "E" and i == len(tokens)-1:
            return points
        if command not in ("M", "L") or i+2 >= len(tokens):
            raise ValueError("audit supports explicit M/L pairs ending with E only")
        if (not points and command != "M") or (points and command != "L"):
            raise ValueError("expected one M followed by L commands")
        point = [float(tokens[i+1]), float(tokens[i+2])]
        if not all(math.isfinite(v) for v in point):
            raise ValueError("nonfinite path")
        points.append(point)
        i += 3
    raise ValueError("missing path end")


def layout_anchor_error(encoded, intended, initial_center, canvas=(1280,720)):
    """Assume origin=layout offsets refer to the authored shape center.

    Explicit assumption: no implicit stage-to-stage position accumulation.
    Native PowerPoint must confirm this interpretation and fill semantics.
    """
    if len(encoded) != len(intended):
        raise ValueError("point count mismatch")
    return max(math.hypot((p[0]+initial_center[0]-q["x"])*canvas[0],
                          (p[1]+initial_center[1]-q["y"])*canvas[1])
               for p,q in zip(encoded,intended))


def audit(pptx, plan):
    pptx = Path(pptx)
    inventory = inspect(pptx)
    errors = list(inventory["errors"])
    slides = []
    objects = {o["id"]: o for o in plan["objects"]}
    if len(inventory["slides"]) != len(plan["slides"]):
        raise ValueError("slide count differs")
    with ZipFile(pptx) as z:
        crc = z.testzip()
        if crc:
            errors.append("CRC failure: "+crc)
        pres = E.fromstring(z.read("ppt/presentation.xml"))
        size = pres.find("p:sldSz",NS)
        cx,cy = int(size.get("cx")),int(size.get("cy"))
        for source, expected in zip(inventory["slides"],plan["slides"]):
            root = E.fromstring(z.read(source["part"]))
            shapes = {}
            for sp in root.findall("p:cSld/p:spTree/p:sp",NS):
                nv = sp.find("p:nvSpPr/p:cNvPr",NS)
                off = sp.find("p:spPr/a:xfrm/a:off",NS)
                ext = sp.find("p:spPr/a:xfrm/a:ext",NS)
                shapes[nv.get("name")] = {
                    "id":nv.get("id"),
                    "center":((int(off.get("x"))+int(ext.get("cx"))/2)/cx,
                              (int(off.get("y"))+int(ext.get("cy"))/2)/cy),
                    "text":"".join(sp.xpath(".//a:t/text()",namespaces=NS)),
                }
            wanted = {objects[oid]["morph_name"] for oid in expected["initial_objects"]}
            if set(shapes) != wanted:
                errors.append("native identity set differs")
            for oid,frame in expected["initial_objects"].items():
                obj = objects[oid]
                if shapes[obj["morph_name"]]["text"] != frame.get("text",obj.get("text","")):
                    errors.append("initial text differs: "+oid)
            actual = {}
            for tag,kind in (("animMotion","motion_path"),("animScale","scale"),("animRot","rotate")):
                for node in root.findall(".//p:"+tag,NS):
                    ctn = node.find("p:cBhvr/p:cTn",NS)
                    delay = int(ctn.find("p:stCondLst/p:cond",NS).get("delay"))
                    spid = node.find("p:cBhvr/p:tgtEl/p:spTgt",NS).get("spid")
                    key = (delay,kind,spid)
                    if key in actual:
                        errors.append("duplicate behavior key: "+str(key))
                    actual[key] = node
            stage_rows = []
            offset = 0
            used = set()
            for stage in expected["timeline"]:
                risks = []
                for effect in stage["effects"]:
                    oid = effect["target"]
                    shape = shapes[objects[oid]["morph_name"]]
                    key = (offset,effect["type"],shape["id"])
                    used.add(key)
                    if key not in actual:
                        errors.append("missing behavior: "+str(key))
                        continue
                    node = actual[key]
                    ctn = node.find("p:cBhvr/p:cTn",NS)
                    if int(ctn.get("dur")) != stage["duration_ms"]:
                        errors.append("duration differs: "+str(key))
                    if effect["type"] == "motion_path":
                        points = polyline(node.get("path"))
                        if len(points) != len(effect["points"]):
                            errors.append("path sample count differs: "+str(key))
                            continue
                        # Relative segment displacement is unambiguous even if
                        # the runtime origin/stacking semantics remain untested.
                        for i in range(1,len(points)):
                            for axis,k in enumerate(("x","y")):
                                delta = points[i][axis]-points[i-1][axis]
                                intended = effect["points"][i][k]-effect["points"][i-1][k]
                                if abs(delta-intended) > 1.1e-6:
                                    errors.append("path segment differs: "+str(key))
                        if node.get("origin") == "layout":
                            distance = layout_anchor_error(points,effect["points"],shape["center"])
                            if distance > 0.01:
                                risks.append({"target":oid,"max_coordinate_error_px":round(distance,6)})
                stage_rows.append({"id":stage["id"],"delay_ms":offset,
                                   "duration_ms":stage["duration_ms"],
                                   "effect_count":len(stage["effects"]),
                                   "layout_origin_model_mismatches":risks})
                offset += stage["duration_ms"]
            if set(actual) != used:
                errors.append("extra native behaviors")
            timing_ids = root.xpath(".//p:timing//p:cTn/@id",namespaces=NS)
            if len(timing_ids) != len(set(timing_ids)):
                errors.append("duplicate timing ids")
            slides.append({"part":source["part"],"native_objects":len(shapes),
                           "behavior_count":len(actual),"duration_ms":offset,
                           "click_groups":len(root.xpath(".//p:cTn[@nodeType='clickEffect']",namespaces=NS)),
                           "remove_fill_behaviors":len(root.xpath(".//p:cBhvr/p:cTn[@fill='remove']",namespaces=NS)),
                           "stages":stage_rows})
    return {"pptx_sha256":hashlib.sha256(pptx.read_bytes()).hexdigest(),
            "slide_count":len(slides),"structure_errors":errors,"slides":slides,
            "coordinate_model":"authored layout center + M/L coordinates; assumes no implicit accumulation",
            "risk_interpretation":"Conditional geometry diagnostic. Does not establish actual PowerPoint motion or fill behavior.",
            "powerpoint_playback_verified":False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx",type=Path)
    parser.add_argument("plan",type=Path)
    args = parser.parse_args()
    result = audit(args.pptx,json.loads(args.plan.read_text(encoding="utf-8")))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(bool(result["structure_errors"]))
