#!/usr/bin/env python3
"""Declare timeline-plan text objects as native PowerPoint textboxes.

This is the timeline counterpart of normalize_textboxes.py. It only operates on
fresh flat native source decks whose shapes exactly match the semantic timeline
plan. It does not change timing because it is intended to run before add_timeline.
"""
import argparse
import hashlib
import json
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

A="http://schemas.openxmlformats.org/drawingml/2006/main"
NS={"p":P,"a":A}


def normalize(source,plan_path,destination):
    source,plan_path,destination=map(Path,(source,plan_path,destination))
    if destination.exists():
        raise ValueError("Refuse to overwrite an output")
    plan=json.loads(plan_path.read_text(encoding="utf-8"))
    errors=validate_timeline(plan)
    if errors:
        raise ValueError("Invalid timeline plan: "+"; ".join(errors))
    objects={o["id"]:o for o in plan["objects"]}
    for obj in objects.values():
        if (obj["kind"],obj.get("geometry")) not in {
            ("shape","rect"),("shape","ellipse"),("text","textbox")
        }:
            raise ValueError("Unsupported object representation")

    inventory=inspect(source)
    slides=inventory["slides"]
    if inventory["errors"] or len(slides)!=len(plan["slides"]):
        raise ValueError("Source package or slide count does not match timeline plan")
    if any(slide["timing_elements"] for slide in slides):
        raise ValueError("Timeline source must not already contain timing")

    updates,changes={},[]
    parser=E.XMLParser(resolve_entities=False,no_network=True)
    with ZipFile(source) as src:
        for inventory_slide,plan_slide in zip(slides,plan["slides"]):
            root=E.fromstring(src.read(inventory_slide["part"]),parser)
            shapes=root.findall("p:cSld/p:spTree/p:sp",NS)
            actual={}
            for shape in shapes:
                props=shape.find("p:nvSpPr/p:cNvPr",NS)
                if props is None or props.get("name") in actual:
                    raise ValueError("Missing or duplicate native shape name")
                actual[props.get("name")]=shape
            expected={objects[oid]["morph_name"] for oid in plan_slide["initial_objects"]}
            forced=set(inventory_slide["forced_morph_names"])
            if set(actual)!=expected or forced!=expected:
                raise ValueError("Native shape identities do not match timeline plan")

            changed=False
            for oid in plan_slide["initial_objects"]:
                obj=objects[oid]
                shape=actual[obj["morph_name"]]
                nv=shape.find("p:nvSpPr/p:cNvSpPr",NS)
                geom=shape.find("p:spPr/a:prstGeom",NS)
                wanted="rect" if obj["kind"]=="text" else obj["geometry"]
                if nv is None or geom is None or geom.get("prst")!=wanted:
                    raise ValueError("Unexpected native shape properties or geometry")
                flag=nv.get("txBox")
                if flag not in (None,"0","false","1","true"):
                    raise ValueError("Invalid txBox boolean")
                if obj["kind"]!="text":
                    if flag in ("1","true"):
                        raise ValueError("Planned carrier is already marked as a textbox")
                    continue
                if shape.find("p:txBody",NS) is None:
                    raise ValueError("Planned textbox has no native text body")
                if flag not in ("1","true"):
                    nv.set("txBox","1")
                    changes.append({
                        "slide":inventory_slide["index"],
                        "name":obj["morph_name"],
                        "attribute":"txBox","before":flag,"after":"1"
                    })
                    changed=True
            if changed:
                updates[inventory_slide["part"]]=E.tostring(
                    root,encoding="UTF-8",xml_declaration=True,standalone=True
                )

        destination.parent.mkdir(parents=True,exist_ok=True)
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent,suffix=".pptx",delete=False) as f:
                temporary=Path(f.name)
            with ZipFile(temporary,"w",ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(item,updates.get(item.filename,src.read(item.filename)))
            report=inspect(temporary)
            if report["errors"] or any(s["timing_elements"] for s in report["slides"]):
                raise ValueError("Normalized timeline package failed inventory")
            os.link(temporary,destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    return {
        "changed_textboxes":len(changes),
        "changes":changes,
        "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
        "powerpoint_playback_verified":False,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source");parser.add_argument("plan");parser.add_argument("destination")
    args=parser.parse_args()
    print(json.dumps(normalize(args.source,args.plan,args.destination),indent=2))
