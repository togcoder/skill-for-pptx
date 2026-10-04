#!/usr/bin/env python3
"""Read-only PPTX inventory. This is NOT a full OOXML validator or player."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import xml.etree.ElementTree as ET
import zipfile

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
MORPH = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"


def inspect(path):
    report = {"file": str(path), "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(), "scope": "package-inventory-v0.1", "errors": [], "slides": [], "playback_verified": False, "full_schema_validated": False}
    with zipfile.ZipFile(path) as package:
        infos = package.infolist()
        if len(infos) > 20000 or sum(i.file_size for i in infos) > 512 * 1024 * 1024:
            raise ValueError("Package exceeds this research inspector's size budget")
        names = package.namelist()
        duplicate_entries = [n for n, count in Counter(names).items() if count > 1]
        if duplicate_entries:
            raise ValueError("Duplicate ZIP entries")
        bad = package.testzip()
        if bad:
            report["errors"].append(f"ZIP CRC error: {bad}")
        xml = {}
        for name in names:
            if name.endswith((".xml", ".rels")):
                try:
                    data = package.read(name)
                    if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
                        raise ValueError("DTD/entity declarations are not supported")
                    xml[name] = ET.fromstring(data)
                except (ET.ParseError, ValueError) as exc:
                    report["errors"].append(f"{name}: {exc}")
        required = ("[Content_Types].xml", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels")
        if any(n not in xml for n in required):
            report["errors"].append("Missing or unreadable required package part")
            return report
        rels = {}
        for rel in xml["ppt/_rels/presentation.xml.rels"].findall(f"{{{REL}}}Relationship"):
            rid = rel.get("Id")
            if rid in rels:
                report["errors"].append(f"Duplicate presentation relationship: {rid}")
            rels[rid] = rel
        slide_nodes = xml["ppt/presentation.xml"].findall(f"{{{P}}}sldIdLst/{{{P}}}sldId")
        if not slide_nodes:
            report["errors"].append("No ordered slides in presentation")
        for index, node in enumerate(slide_nodes, 1):
            rid = node.get(f"{{{R}}}id")
            rel = rels.get(rid)
            if rel is None or rel.get("TargetMode") == "External" or not rel.get("Type", "").endswith("/slide"):
                report["errors"].append(f"slide {index}: missing or invalid relationship {rid}")
                continue
            target = rel.get("Target", "")
            part = posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join("ppt", target))
            if part not in xml:
                report["errors"].append(f"slide {index}: unreadable target {part}")
                continue
            root = xml[part]
            shape_props = root.findall(f".//{{{P}}}cNvPr")
            ids = [n.get("id") for n in shape_props]
            if len(ids) != len(set(ids)):
                report["errors"].append(f"slide {index}: duplicate local shape IDs")
            forced = [n.get("name", "") for n in shape_props if n.get("name", "").startswith("!!")]
            if len(forced) != len(set(forced)):
                report["errors"].append(f"slide {index}: duplicate forced Morph names")
            for element in root.iter():
                if element.tag.split("}")[-1] == "morph" and element.tag != f"{{{MORPH}}}morph":
                    report["errors"].append(f"slide {index}: unexpected Morph namespace")
            morph = root.findall(f".//{{{MORPH}}}morph")
            report["slides"].append({"index": index, "part": part, "forced_morph_names": forced, "morph_elements": len(morph), "morph_options": [m.get("option") for m in morph], "timing_elements": len(root.findall(f".//{{{P}}}timing"))})
    report["note"] = "Inventory checks only. Open and play this exact file in PowerPoint before claiming compatibility or motion correctness."
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()
    try:
        report = inspect(args.pptx)
    except (OSError, zipfile.BadZipFile, ValueError, RuntimeError) as exc:
        report = {"errors": [str(exc)], "playback_verified": False}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

