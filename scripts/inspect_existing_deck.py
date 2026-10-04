#!/usr/bin/env python3
"""Read an existing PPTX into a stable deck-intake JSON for motion planning.

This is a read-only package analyzer. It does not infer narrative or edit the
deck. Its job is to give the AI planner a faithful inventory before any motion
or component synthesis is attempted.
"""
import argparse
import hashlib
import json
import posixpath
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile

P="http://schemas.openxmlformats.org/presentationml/2006/main"
A="http://schemas.openxmlformats.org/drawingml/2006/main"
R="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL="http://schemas.openxmlformats.org/package/2006/relationships"
C="http://schemas.openxmlformats.org/drawingml/2006/chart"
DGM="http://schemas.openxmlformats.org/drawingml/2006/diagram"
NS={"p":P,"a":A,"r":R}
REL_NS={"rel":REL}

TYPE_BY_TAG={
    f"{{{P}}}sp":"shape",
    f"{{{P}}}pic":"picture",
    f"{{{P}}}graphicFrame":"graphic-frame",
    f"{{{P}}}cxnSp":"connector",
    f"{{{P}}}grpSp":"group",
}


def _safe_xml(data,name):
    if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
        raise ValueError(f"{name}: DTD/entity declarations are not supported")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"{name}: invalid XML: {exc}") from exc


def _resolve_part(base_part,target):
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_part),target))


def _relationships(package,part):
    rel_part=posixpath.join(
        posixpath.dirname(part),
        "_rels",
        posixpath.basename(part)+".rels",
    )
    if rel_part not in package.namelist():
        return []
    root=_safe_xml(package.read(rel_part),rel_part)
    out=[]
    for rel in root.findall(f"{{{REL}}}Relationship"):
        out.append({
            "id":rel.get("Id"),
            "type":rel.get("Type",""),
            "target":rel.get("Target",""),
            "target_mode":rel.get("TargetMode"),
            "resolved_target":None if rel.get("TargetMode")=="External" else _resolve_part(part,rel.get("Target","")),
        })
    return out


def _text(root):
    return "".join((node.text or "") for node in root.findall(".//a:t",NS)).strip()


def _cNvPr(node):
    props=node.find(".//p:cNvPr",NS)
    if props is None:
        return {"id":None,"name":None,"descr":None}
    return {
        "id":props.get("id"),
        "name":props.get("name"),
        "descr":props.get("descr"),
    }


def _xfrm(node):
    # Common locations for shapes/pictures/connectors and graphic frames.
    candidates=[
        node.find("p:spPr/a:xfrm",NS),
        node.find("p:spPr/a:xfrm",NS),
        node.find("p:xfrm",NS),
        node.find("p:grpSpPr/a:xfrm",NS),
    ]
    x=next((item for item in candidates if item is not None),None)
    if x is None:
        return None
    off=x.find("a:off",NS)
    ext=x.find("a:ext",NS)
    if off is None or ext is None:
        return None
    try:
        return {
            "x_emu":int(off.get("x")),
            "y_emu":int(off.get("y")),
            "cx_emu":int(ext.get("cx")),
            "cy_emu":int(ext.get("cy")),
            "rot":int(x.get("rot","0")),
        }
    except (TypeError,ValueError):
        return None


def _normalize_geometry(geom,width,height):
    if geom is None or not width or not height:
        return None
    return {
        "x":geom["x_emu"]/width,
        "y":geom["y_emu"]/height,
        "w":geom["cx_emu"]/width,
        "h":geom["cy_emu"]/height,
        "rotation_deg":geom["rot"]/60000,
    }


def _graphic_kind(node):
    data=node.find(".//a:graphicData",NS)
    if data is None:
        return "graphic"
    uri=data.get("uri","")
    if "chart" in uri:
        return "chart"
    if "table" in uri:
        return "table"
    if "diagram" in uri:
        return "diagram"
    return "graphic"


def _shape_inventory(root,width,height):
    tree=root.find("p:cSld/p:spTree",NS)
    if tree is None:
        return []
    out=[]
    z=0
    for node in list(tree):
        base=TYPE_BY_TAG.get(node.tag)
        if base is None:
            continue
        z+=1
        props=_cNvPr(node)
        kind=_graphic_kind(node) if base=="graphic-frame" else base
        geom=_xfrm(node)
        out.append({
            "z_index":z,
            "kind":kind,
            "id":props["id"],
            "name":props["name"],
            "descr":props["descr"],
            "text":_text(node) or None,
            "geometry":_normalize_geometry(geom,width,height),
            "geometry_emu":geom,
            "forced_semantic_name":props["name"] if (props["name"] or "").startswith("!!") else None,
        })
    return out


def _notes_text(package,slide_part,relationships):
    rel=next((r for r in relationships if r["type"].endswith("/notesSlide") and r["resolved_target"]),None)
    if rel is None or rel["resolved_target"] not in package.namelist():
        return None
    root=_safe_xml(package.read(rel["resolved_target"]),rel["resolved_target"])
    chunks=[]
    for shape in root.findall("p:cSld/p:spTree/p:sp",NS):
        text=_text(shape)
        if not text:
            continue
        placeholder=shape.find("p:nvSpPr/p:nvPr/p:ph",NS)
        ptype=placeholder.get("type") if placeholder is not None else None
        # Exclude slide image / slide number placeholders but preserve body notes.
        if ptype in ("sldImg","sldNum","hdr","ftr","dt"):
            continue
        chunks.append(text)
    joined="\n".join(chunks).strip()
    return joined or None


def _relationship_summary(relationships):
    out=[]
    for rel in relationships:
        rtype=rel["type"].rsplit("/",1)[-1] if "/" in rel["type"] else rel["type"]
        out.append({
            "id":rel["id"],
            "kind":rtype,
            "target":rel["resolved_target"] or rel["target"],
            "external":rel["target_mode"]=="External",
        })
    return out


def inspect_existing_deck(path):
    path=Path(path)
    report={
        "version":"0.1",
        "kind":"existing-deck-inventory",
        "source_file":path.name,
        "source_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "errors":[],
        "slide_size_emu":None,
        "slides":[],
        "package":{},
    }
    try:
        with ZipFile(path) as package:
            infos=package.infolist()
            names=package.namelist()
            dup=[name for name,count in Counter(names).items() if count>1]
            if dup:
                raise ValueError("Duplicate ZIP entries")
            bad=package.testzip()
            if bad:
                report["errors"].append(f"ZIP CRC error: {bad}")

            for required in ("ppt/presentation.xml","ppt/_rels/presentation.xml.rels"):
                if required not in names:
                    raise ValueError(f"Missing required part: {required}")

            presentation=_safe_xml(package.read("ppt/presentation.xml"),"ppt/presentation.xml")
            size=presentation.find(f"{{{P}}}sldSz")
            if size is not None:
                try:
                    width,height=int(size.get("cx")),int(size.get("cy"))
                    report["slide_size_emu"]={"width":width,"height":height}
                except (TypeError,ValueError):
                    width=height=None
            else:
                width=height=None

            rel_root=_safe_xml(package.read("ppt/_rels/presentation.xml.rels"),"ppt/_rels/presentation.xml.rels")
            rels={r.get("Id"):r for r in rel_root.findall(f"{{{REL}}}Relationship")}
            slide_nodes=presentation.findall(f"{{{P}}}sldIdLst/{{{P}}}sldId")
            for index,node in enumerate(slide_nodes,1):
                rid=node.get(f"{{{R}}}id")
                rel=rels.get(rid)
                if rel is None or not rel.get("Type","").endswith("/slide"):
                    report["errors"].append(f"slide {index}: invalid slide relationship {rid}")
                    continue
                part=_resolve_part("ppt/presentation.xml",rel.get("Target",""))
                if part not in names:
                    report["errors"].append(f"slide {index}: missing slide part {part}")
                    continue
                root=_safe_xml(package.read(part),part)
                relationships=_relationships(package,part)
                shapes=_shape_inventory(root,width,height)
                title=next((s["text"] for s in shapes if s["text"]),None)
                report["slides"].append({
                    "index":index,
                    "part":part,
                    "title_candidate":title,
                    "text":"\n".join(s["text"] for s in shapes if s["text"]) or None,
                    "speaker_notes":_notes_text(package,part,relationships),
                    "shape_count":len(shapes),
                    "shapes":shapes,
                    "relationships":_relationship_summary(relationships),
                    "has_transition":root.find(f".//{{{P}}}transition") is not None,
                    "has_timing":root.find(f".//{{{P}}}timing") is not None,
                    "layout_part":next((r["resolved_target"] for r in relationships if r["type"].endswith("/slideLayout")),None),
                })

            report["package"]={
                "file_count":len(infos),
                "has_theme":any(n.startswith("ppt/theme/") and n.endswith(".xml") for n in names),
                "has_media":any(n.startswith("ppt/media/") for n in names),
                "has_notes":any(n.startswith("ppt/notesSlides/") and n.endswith(".xml") for n in names),
                "has_charts":any(n.startswith("ppt/charts/") and n.endswith(".xml") for n in names),
                "has_embedded_objects":any(n.startswith("ppt/embeddings/") for n in names),
            }
    except (OSError,BadZipFile,ValueError) as exc:
        report["errors"].append(str(exc))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=inspect_existing_deck(args.pptx)
    data=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(data+"\n",encoding="utf-8")
    else:
        print(data)
    return 1 if report["errors"] else 0


if __name__=="__main__":
    raise SystemExit(main())
