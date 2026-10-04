#!/usr/bin/env python3
"""Patch packed native animation onto existing PPTX source objects.

Unlike the T006 generated-deck writer, this patcher does not require !! semantic
names. It targets exact existing objects by slide-local cNvPr id + name and
preserves untargeted package parts byte-for-byte.
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
    from .add_timeline import (
        _q, _sub, _behavior_ctn, _path_data, _rotation_units,
        inspect_timing_root, ROOT_CTN_ID, MAIN_SEQ_ID, CLICK_BUCKET_ID,
        PACKED_GROUP_ID, FIRST_BEHAVIOR_ID,
    )
except ImportError:
    from inspect_pptx import inspect, P
    from add_timeline import (
        _q, _sub, _behavior_ctn, _path_data, _rotation_units,
        inspect_timing_root, ROOT_CTN_ID, MAIN_SEQ_ID, CLICK_BUCKET_ID,
        PACKED_GROUP_ID, FIRST_BEHAVIOR_ID,
    )

NS={"p":P}


def _target_key(target):
    if not isinstance(target,dict):
        raise ValueError("effect target must be an object")
    sid=target.get("source_id")
    name=target.get("source_name")
    if not isinstance(sid,str) or not sid.strip():
        raise ValueError("target.source_id must be nonempty text")
    if not isinstance(name,str) or not name:
        raise ValueError("target.source_name must be nonempty text")
    return sid,name


def validate_patch_plan(plan):
    errors=[]
    if not isinstance(plan,dict):
        return ["plan must be an object"]
    required={"version","kind","source_sha256","slides"}
    errors += [f"missing field: {k}" for k in sorted(required-plan.keys())]
    if errors:
        return errors
    if plan["version"]!="0.1":
        errors.append("version must be 0.1")
    if plan["kind"]!="existing-deck-timeline-patch":
        errors.append("kind must be existing-deck-timeline-patch")
    sha=plan["source_sha256"]
    if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha.lower()):
        errors.append("source_sha256 must be a 64-character hex digest")
    slides=plan["slides"]
    if not isinstance(slides,list) or not slides:
        errors.append("slides must be a nonempty list")
        return errors
    seen_slides=set()
    for slide in slides:
        if not isinstance(slide,dict):
            errors.append("slide patch must be an object")
            continue
        idx=slide.get("source_index")
        if type(idx) is not int or idx<1:
            errors.append("source_index must be a positive integer")
        elif idx in seen_slides:
            errors.append(f"duplicate source_index: {idx}")
        else:
            seen_slides.add(idx)
        stages=slide.get("stages")
        if not isinstance(stages,list) or not stages:
            errors.append(f"slide {idx}: stages must be nonempty")
            continue
        stage_ids=set()
        for i,stage in enumerate(stages):
            if not isinstance(stage,dict):
                errors.append(f"slide {idx}: stage must be an object")
                continue
            sid=stage.get("id")
            if not isinstance(sid,str) or not sid:
                errors.append(f"slide {idx}: stage id must be nonempty")
            elif sid in stage_ids:
                errors.append(f"slide {idx}: duplicate stage id {sid}")
            else:
                stage_ids.add(sid)
            expected="on-click" if i==0 else "after-previous"
            if stage.get("trigger")!=expected:
                errors.append(f"slide {idx}: stage {sid} trigger must be {expected}")
            duration=stage.get("duration_ms")
            if type(duration) is not int or duration<=0:
                errors.append(f"slide {idx}: stage {sid} duration_ms must be positive integer")
            effects=stage.get("effects")
            if not isinstance(effects,list) or not effects:
                errors.append(f"slide {idx}: stage {sid} effects must be nonempty")
                continue
            for effect in effects:
                if not isinstance(effect,dict):
                    errors.append(f"slide {idx}: effect must be an object")
                    continue
                try:
                    _target_key(effect.get("target"))
                except ValueError as exc:
                    errors.append(f"slide {idx}: {exc}")
                kind=effect.get("type")
                if kind=="motion_path":
                    points=effect.get("points")
                    if not isinstance(points,list) or len(points)<2:
                        errors.append(f"slide {idx}: motion_path needs >=2 points")
                    else:
                        for point in points:
                            if not isinstance(point,dict) or set(point)!={"x","y"}:
                                errors.append(f"slide {idx}: invalid motion point")
                                break
                            if any(type(point[k]) not in (int,float) or not math.isfinite(point[k]) for k in ("x","y")):
                                errors.append(f"slide {idx}: nonfinite motion point")
                                break
                elif kind=="scale":
                    for key in ("from_x","from_y","to_x","to_y"):
                        value=effect.get(key)
                        if type(value) not in (int,float) or not math.isfinite(value) or value<=0:
                            errors.append(f"slide {idx}: invalid scale {key}")
                elif kind=="rotate":
                    value=effect.get("by_deg")
                    if type(value) not in (int,float) or not math.isfinite(value):
                        errors.append(f"slide {idx}: invalid rotate by_deg")
                else:
                    errors.append(f"slide {idx}: unsupported effect type {kind}")
    return errors


def _shape_targets(root):
    result={}
    for props in root.findall(".//p:cNvPr",NS):
        sid=props.get("id")
        name=props.get("name")
        if sid is None or name is None:
            continue
        key=(sid,name)
        if key in result:
            raise ValueError(f"duplicate source object identity: {key}")
        result[key]=sid
    return result


def _scale_node(parent,effect,spid,behavior_id,duration_ms,delay_ms):
    scale=_sub(parent,"animScale")
    behavior=_sub(scale,"cBhvr")
    _behavior_ctn(behavior,behavior_id,duration_ms,delay_ms)
    target=_sub(behavior,"tgtEl")
    _sub(target,"spTgt",spid=spid)
    _sub(scale,"from",x=round(effect["from_x"]*100000),y=round(effect["from_y"]*100000))
    _sub(scale,"to",x=round(effect["to_x"]*100000),y=round(effect["to_y"]*100000))
    return scale


def _motion_node(parent,effect,spid,behavior_id,duration_ms,delay_ms):
    motion=_sub(parent,"animMotion",origin="layout",path=_path_data(effect["points"]),pathEditMode="relative")
    behavior=_sub(motion,"cBhvr")
    _behavior_ctn(behavior,behavior_id,duration_ms,delay_ms)
    target=_sub(behavior,"tgtEl")
    _sub(target,"spTgt",spid=spid)
    return motion


def _rotate_node(parent,effect,spid,behavior_id,duration_ms,delay_ms):
    rotate=_sub(parent,"animRot",by=_rotation_units(effect["by_deg"]))
    behavior=_sub(rotate,"cBhvr")
    _behavior_ctn(behavior,behavior_id,duration_ms,delay_ms)
    target=_sub(behavior,"tgtEl")
    _sub(target,"spTgt",spid=spid)
    names=_sub(behavior,"attrNameLst")
    name=_sub(names,"attrName")
    name.text="r"
    return rotate


def build_existing_timing(slide_patch,root):
    available=_shape_targets(root)
    stages=slide_patch["stages"]
    total_duration=sum(stage["duration_ms"] for stage in stages)

    timing=E.Element(_q("timing"))
    tn_list=_sub(timing,"tnLst")
    root_par=_sub(tn_list,"par")
    root_ctn=_sub(root_par,"cTn",id=ROOT_CTN_ID,dur="indefinite",restart="never",nodeType="tmRoot")
    root_children=_sub(root_ctn,"childTnLst")
    sequence=_sub(root_children,"seq",concurrent="1",nextAc="seek")
    seq_ctn=_sub(sequence,"cTn",id=MAIN_SEQ_ID,dur="indefinite",nodeType="mainSeq")
    main_children=_sub(seq_ctn,"childTnLst")
    click_bucket=_sub(main_children,"par")
    click_ctn=_sub(click_bucket,"cTn",id=CLICK_BUCKET_ID,fill="hold")
    start=_sub(click_ctn,"stCondLst")
    _sub(start,"cond",delay="indefinite")
    begin=_sub(start,"cond",evt="onBegin",delay="0")
    _sub(begin,"tn",val=MAIN_SEQ_ID)
    click_children=_sub(click_ctn,"childTnLst")
    packed=_sub(click_children,"par")
    packed_ctn=_sub(packed,"cTn",id=PACKED_GROUP_ID,dur=total_duration,fill="hold",nodeType="clickEffect",grpId=PACKED_GROUP_ID)
    packed_start=_sub(packed_ctn,"stCondLst")
    _sub(packed_start,"cond",delay="0")
    packed_children=_sub(packed_ctn,"childTnLst")

    behavior_id=FIRST_BEHAVIOR_ID
    delay=0
    animated={}
    receipts=[]
    for stage in stages:
        effect_receipts=[]
        for effect in stage["effects"]:
            key=_target_key(effect["target"])
            spid=available.get(key)
            if spid is None:
                raise ValueError(f"source object not found on slide {slide_patch['source_index']}: id={key[0]!r}, name={key[1]!r}")
            kind=effect["type"]
            if kind=="motion_path":
                _motion_node(packed_children,effect,spid,behavior_id,stage["duration_ms"],delay)
            elif kind=="scale":
                _scale_node(packed_children,effect,spid,behavior_id,stage["duration_ms"],delay)
            elif kind=="rotate":
                _rotate_node(packed_children,effect,spid,behavior_id,stage["duration_ms"],delay)
            else:
                raise ValueError(f"unsupported effect type: {kind}")
            animated[key]=spid
            effect_receipts.append({"type":kind,"source_id":key[0],"source_name":key[1],"behavior_id":behavior_id})
            behavior_id+=1
        receipts.append({"id":stage["id"],"delay_ms":delay,"duration_ms":stage["duration_ms"],"effects":effect_receipts})
        delay+=stage["duration_ms"]

    previous=_sub(sequence,"prevCondLst")
    cond=_sub(previous,"cond",evt="onPrev",delay="0")
    _sub(_sub(cond,"tgtEl"),"sldTgt")
    following=_sub(sequence,"nextCondLst")
    cond=_sub(following,"cond",evt="onNext",delay="0")
    _sub(_sub(cond,"tgtEl"),"sldTgt")

    build=_sub(timing,"bldLst")
    for key,spid in sorted(animated.items(),key=lambda item:(int(item[0][0]),item[0][1])):
        _sub(build,"bldP",spid=spid,grpId="0",animBg="1")
        _sub(build,"bldP",spid=spid,grpId=PACKED_GROUP_ID,animBg="1")

    return timing,{
        "total_duration_ms":total_duration,
        "behavior_count":behavior_id-FIRST_BEHAVIOR_ID,
        "animated_objects":[{"source_id":k[0],"source_name":k[1]} for k in animated],
        "stages":receipts,
    }


def patch_existing(source,plan_path,destination):
    source,plan_path,destination=map(Path,(source,plan_path,destination))
    if destination.exists():
        raise ValueError("Refuse to overwrite an output")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    errors=validate_patch_plan(plan)
    if errors:
        raise ValueError("Invalid existing-deck patch plan: "+"; ".join(errors))
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash!=plan["source_sha256"]:
        raise ValueError("Source SHA-256 does not match patch plan")

    inventory=inspect(source)
    if inventory["errors"]:
        raise ValueError("Invalid source package: "+"; ".join(inventory["errors"]))
    slides={slide["index"]:slide for slide in inventory["slides"]}
    parser=E.XMLParser(resolve_entities=False,no_network=True)
    updates={}
    receipts=[]

    with ZipFile(source) as src:
        for slide_patch in plan["slides"]:
            idx=slide_patch["source_index"]
            inv=slides.get(idx)
            if inv is None:
                raise ValueError(f"Unknown source slide: {idx}")
            part=inv["part"]
            root=E.fromstring(src.read(part),parser)
            if root.findall(".//p:timing",NS):
                raise ValueError(f"Slide {idx} already has native timing; merge is not implemented")
            timing,receipt=build_existing_timing(slide_patch,root)
            insert_at=next((i for i,child in enumerate(root) if child.tag==_q("extLst")),len(root))
            root.insert(insert_at,timing)
            check=inspect_timing_root(root)
            if check["errors"]:
                raise ValueError(f"Slide {idx} timing failed structural inspection: "+"; ".join(check["errors"]))
            updates[part]=E.tostring(root,encoding="UTF-8",xml_declaration=True,standalone=True)
            receipts.append({"slide":idx,"part":part,**receipt,"timing":check})

        destination.parent.mkdir(parents=True,exist_ok=True)
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent,suffix=".pptx",delete=False) as f:
                temporary=Path(f.name)
            with ZipFile(temporary,"w",ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(item,updates.get(item.filename,src.read(item.filename)))
            final=inspect(temporary)
            if final["errors"]:
                raise ValueError("Patched package failed inventory")
            os.link(temporary,destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    return {
        "source_sha256":source_hash,
        "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
        "patched_slides":[r["slide"] for r in receipts],
        "receipts":receipts,
        "powerpoint_playback_verified":False,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("plan")
    parser.add_argument("destination")
    args=parser.parse_args()
    print(json.dumps(patch_existing(args.source,args.plan,args.destination),indent=2))


if __name__=="__main__":
    main()
