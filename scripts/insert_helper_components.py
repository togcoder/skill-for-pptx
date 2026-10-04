#!/usr/bin/env python3
"""Insert style-matched native helper shapes into an existing PPTX.

v0.1 clones an existing p:sp donor on the same slide, preserving its style and
PowerPoint-native representation while changing identity, geometry and optional
text. Re-inventory the output before adding animation.
"""
import argparse
import copy
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
    from .inspect_existing_deck import inspect_existing_deck
except ImportError:
    from inspect_pptx import inspect, P
    from inspect_existing_deck import inspect_existing_deck

A="http://schemas.openxmlformats.org/drawingml/2006/main"
NS={"p":P,"a":A}
PROVENANCE={"none","derived-from-source","synthetic-nondata","user-provided"}
TEXT_ACTIONS={"preserve","clear","replace"}


def validate_component_plan(plan):
    errors=[]
    if not isinstance(plan,dict):
        return ["plan must be an object"]
    required={"version","kind","source_sha256","components"}
    errors += [f"missing field: {k}" for k in sorted(required-plan.keys())]
    if errors:
        return errors
    if plan["version"]!="0.1":
        errors.append("version must be 0.1")
    if plan["kind"]!="existing-deck-helper-components":
        errors.append("kind must be existing-deck-helper-components")
    sha=plan["source_sha256"]
    if not isinstance(sha,str) or len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha.lower()):
        errors.append("source_sha256 must be a 64-character hex digest")
    components=plan["components"]
    if not isinstance(components,list) or not components:
        errors.append("components must be a nonempty list")
        return errors
    names=set()
    for comp in components:
        if not isinstance(comp,dict):
            errors.append("component must be an object")
            continue
        idx=comp.get("source_index")
        if type(idx) is not int or idx<1:
            errors.append("component.source_index must be positive integer")
        donor=comp.get("donor")
        if not isinstance(donor,dict) or not isinstance(donor.get("source_id"),str) or not isinstance(donor.get("source_name"),str):
            errors.append(f"slide {idx}: donor needs source_id and source_name text")
        name=comp.get("new_name")
        if not isinstance(name,str) or not name.strip():
            errors.append(f"slide {idx}: new_name must be nonempty")
        elif name in names:
            errors.append(f"duplicate new_name: {name}")
        else:
            names.add(name)
        for key in ("role","rationale"):
            if not isinstance(comp.get(key),str) or not comp[key].strip():
                errors.append(f"slide {idx}: {key} must be nonempty")
        if comp.get("data_provenance") not in PROVENANCE:
            errors.append(f"slide {idx}: unsupported data_provenance")
        geom=comp.get("geometry")
        if not isinstance(geom,dict):
            errors.append(f"slide {idx}: geometry must be an object")
        else:
            for key in ("x","y","w","h"):
                value=geom.get(key)
                if type(value) not in (int,float) or not math.isfinite(value):
                    errors.append(f"slide {idx}: geometry.{key} must be finite")
                elif key in ("w","h") and value<=0:
                    errors.append(f"slide {idx}: geometry.{key} must be positive")
            rot=geom.get("rotation_deg",0)
            if type(rot) not in (int,float) or not math.isfinite(rot):
                errors.append(f"slide {idx}: rotation_deg must be finite")
        action=comp.get("text_action")
        if action not in TEXT_ACTIONS:
            errors.append(f"slide {idx}: unsupported text_action")
        if action=="replace" and not isinstance(comp.get("text"),str):
            errors.append(f"slide {idx}: replace requires text")
    return errors


def _shape_identity(shape):
    props=shape.find("p:nvSpPr/p:cNvPr",NS)
    if props is None:
        return None
    return props.get("id"),props.get("name")


def _find_donor(root,target):
    tree=root.find("p:cSld/p:spTree",NS)
    if tree is None:
        raise ValueError("slide has no shape tree")
    key=(target["source_id"],target["source_name"])
    for shape in tree.findall("p:sp",NS):
        if _shape_identity(shape)==key:
            return tree,shape
    raise ValueError(f"donor shape not found: id={key[0]!r}, name={key[1]!r}")


def _next_shape_id(root):
    values=[]
    for props in root.findall(".//p:cNvPr",NS):
        raw=props.get("id")
        if raw is None:
            continue
        try:
            values.append(int(raw))
        except ValueError as exc:
            raise ValueError("nonnumeric cNvPr id in source slide") from exc
    return max(values,default=0)+1


def _set_geometry(shape,geom,slide_width,slide_height):
    xfrm=shape.find("p:spPr/a:xfrm",NS)
    if xfrm is None:
        raise ValueError("donor shape has no p:spPr/a:xfrm")
    off=xfrm.find("a:off",NS)
    ext=xfrm.find("a:ext",NS)
    if off is None or ext is None:
        raise ValueError("donor shape transform is incomplete")
    off.set("x",str(round(geom["x"]*slide_width)))
    off.set("y",str(round(geom["y"]*slide_height)))
    ext.set("cx",str(round(geom["w"]*slide_width)))
    ext.set("cy",str(round(geom["h"]*slide_height)))
    rot=round(geom.get("rotation_deg",0)*60000)
    if rot:
        xfrm.set("rot",str(rot))
    elif "rot" in xfrm.attrib:
        del xfrm.attrib["rot"]


def _apply_text(shape,action,text=None):
    runs=shape.findall(".//a:t",NS)
    if action=="preserve":
        return
    if not runs:
        if action=="clear":
            return
        raise ValueError("donor has no native text run for replacement")
    if action=="clear":
        for node in runs:
            node.text=""
        return
    runs[0].text=text
    for node in runs[1:]:
        node.text=""


def insert_helpers(source,plan_path,destination):
    source,plan_path,destination=map(Path,(source,plan_path,destination))
    if destination.exists():
        raise ValueError("Refuse to overwrite an output")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    errors=validate_component_plan(plan)
    if errors:
        raise ValueError("Invalid helper component plan: "+"; ".join(errors))
    source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash!=plan["source_sha256"]:
        raise ValueError("Source SHA-256 does not match component plan")

    deck=inspect_existing_deck(source)
    if deck["errors"]:
        raise ValueError("Invalid source deck: "+"; ".join(deck["errors"]))
    if deck["slide_size_emu"] is None:
        raise ValueError("Source slide size is unavailable")
    width=deck["slide_size_emu"]["width"]
    height=deck["slide_size_emu"]["height"]

    inventory=inspect(source)
    slides={slide["index"]:slide for slide in inventory["slides"]}
    grouped={}
    for comp in plan["components"]:
        grouped.setdefault(comp["source_index"],[]).append(comp)

    parser=E.XMLParser(resolve_entities=False,no_network=True)
    updates={}
    receipts=[]

    with ZipFile(source) as src:
        for idx,components in grouped.items():
            inv=slides.get(idx)
            if inv is None:
                raise ValueError(f"Unknown source slide: {idx}")
            root=E.fromstring(src.read(inv["part"]),parser)
            existing_names={p.get("name") for p in root.findall(".//p:cNvPr",NS)}
            next_id=_next_shape_id(root)
            for comp in components:
                if comp["new_name"] in existing_names:
                    raise ValueError(f"new_name already exists on slide {idx}: {comp['new_name']}")
                tree,donor=_find_donor(root,comp["donor"])
                clone=copy.deepcopy(donor)
                props=clone.find("p:nvSpPr/p:cNvPr",NS)
                props.set("id",str(next_id))
                props.set("name",comp["new_name"])
                if "descr" in props.attrib:
                    props.set("descr",comp["role"])
                _set_geometry(clone,comp["geometry"],width,height)
                _apply_text(clone,comp["text_action"],comp.get("text"))
                tree.append(clone)
                receipts.append({
                    "slide":idx,
                    "source_id":str(next_id),
                    "source_name":comp["new_name"],
                    "donor":comp["donor"],
                    "role":comp["role"],
                    "rationale":comp["rationale"],
                })
                existing_names.add(comp["new_name"])
                next_id+=1
            updates[inv["part"]]=E.tostring(root,encoding="UTF-8",xml_declaration=True,standalone=True)

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
                raise ValueError("Helper component package failed inventory")
            os.link(temporary,destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    return {
        "source_sha256":source_hash,
        "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
        "created_components":receipts,
        "requires_reinventory":True,
        "powerpoint_playback_verified":False,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("plan")
    parser.add_argument("destination")
    args=parser.parse_args()
    print(json.dumps(insert_helpers(args.source,args.plan,args.destination),indent=2))


if __name__=="__main__":
    main()
