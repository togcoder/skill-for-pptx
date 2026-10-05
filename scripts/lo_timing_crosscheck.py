#!/usr/bin/env python3
"""Cross-check PPTX timing through LibreOffice's independent PPTX importer.

Converts a PPTX to ODP headlessly and lists, per slide, every effect node as
LibreOffice understood it: node type (on-click / with-previous /
after-previous), preset class/id, the begin offset of the effect and of its
time block, and whether a visibility `set` exists.

This is a third-party reading of the timing tree. It catches sequencing and
preset-recognition defects; it is NOT PowerPoint playback evidence.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from zipfile import ZipFile

from lxml import etree as E

NS={
    "draw":"urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "anim":"urn:oasis:names:tc:opendocument:xmlns:animation:1.0",
    "pres":"urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
    "smil":"urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0",
}


def _q(prefix,name):
    return f"{{{NS[prefix]}}}{name}"


def crosscheck(pptx):
    soffice=shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("LibreOffice Impress is required")
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/"deck.pptx"
        shutil.copy(pptx,src)
        subprocess.run([soffice,"--headless","--convert-to","odp","--outdir",td,str(src)],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=300)
        odp=Path(td)/"deck.odp"
        if not odp.exists():
            raise RuntimeError("LibreOffice could not load the deck")
        root=E.fromstring(ZipFile(odp).read("content.xml"))
    slides=[]
    for index,page in enumerate(root.iter(_q("draw","page")),1):
        effects=[]
        for node in page.iter(_q("anim","par")):
            kind=node.get(_q("pres","node-type"))
            if kind in (None,"timing-root","main-sequence"):
                continue
            block=node.getparent()
            effects.append({
                "node_type":kind,
                "preset_class":node.get(_q("pres","preset-class")),
                "preset_id":node.get(_q("pres","preset-id")),
                "effect_begin":node.get(_q("smil","begin")),
                "block_begin":block.get(_q("smil","begin")) if block is not None else None,
                "visibility_sets":len(node.findall(f".//{_q('anim','set')}")),
            })
        if effects:
            slides.append({"slide":index,"effects":effects})
    return {"tool":"LibreOffice PPTX import -> ODP","pptx":str(pptx),"slides":slides,
            "powerpoint_playback_verified":False}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pptx")
    ap.add_argument("--output")
    args=ap.parse_args()
    result=json.dumps(crosscheck(args.pptx),indent=2)
    if args.output:
        Path(args.output).write_text(result+"\n",encoding="utf-8")
    print(result)


if __name__=="__main__":
    main()
