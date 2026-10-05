#!/usr/bin/env python3
"""RGB-aware static render comparison of two decks (T022).

Renders both decks with LibreOffice (PPTX -> PDF -> PNG via pdftoppm) and
compares every slide in RGB. The T009 comparison used
``ImageChops.difference(rgba_a, rgba_b).getbbox()``; for RGBA images Pillow's
getbbox() looks at the alpha band only, so colour changes on opaque pixels were
invisible. This tool converts to RGB first and reports changed-pixel counts.

A static render shows the authored (final) layout only. Equality means timing
did not alter layout; it says nothing about animation playback.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageChops


def _render(pptx,outdir,dpi):
    soffice=shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice or not shutil.which("pdftoppm"):
        raise RuntimeError("LibreOffice Impress and pdftoppm are required")
    outdir.mkdir(parents=True,exist_ok=True)
    src=outdir/"deck.pptx"
    shutil.copy(pptx,src)
    subprocess.run([soffice,"--headless","--convert-to","pdf","--outdir",str(outdir),str(src)],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=600)
    pdf=outdir/"deck.pdf"
    if not pdf.exists():
        raise RuntimeError(f"LibreOffice could not render {pptx}")
    subprocess.run(["pdftoppm","-r",str(dpi),"-png",str(pdf),str(outdir/"slide")],check=True,timeout=600)
    return sorted(outdir.glob("slide-*.png"))


def diff_rgb(a,b):
    """Return (bbox, changed_pixel_count) comparing two images in RGB."""
    a=a.convert("RGB")
    b=b.convert("RGB")
    if a.size!=b.size:
        return (0,0)+a.size,a.size[0]*a.size[1]
    diff=ImageChops.difference(a,b)
    r,g,b=diff.split()
    strongest=ImageChops.lighter(ImageChops.lighter(r,g),b)  # per-pixel max over bands
    return diff.getbbox(),a.size[0]*a.size[1]-strongest.histogram()[0]


def compare(source,output,dpi=50):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        pa=_render(source,td/"a",dpi)
        pb=_render(output,td/"b",dpi)
        slides=[]
        for i,(x,y) in enumerate(zip(pa,pb),1):
            bbox,count=diff_rgb(Image.open(x),Image.open(y))
            slides.append({"slide":i,"identical_rgb":bbox is None,"changed_pixels":count,"bbox":bbox})
        return {
            "method":"LibreOffice PDF -> pdftoppm PNG, RGB difference",
            "dpi":dpi,
            "source_pages":len(pa),
            "output_pages":len(pb),
            "identical_slides":sum(s["identical_rgb"] for s in slides),
            "slides":slides,
            "powerpoint_playback_verified":False,
        }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("output")
    ap.add_argument("--dpi",type=int,default=50)
    ap.add_argument("--json")
    args=ap.parse_args()
    result=compare(args.source,args.output,args.dpi)
    text=json.dumps(result,indent=2)
    if args.json:
        Path(args.json).write_text(text+"\n",encoding="utf-8")
    print(text)
    return 0 if result["identical_slides"]==len(result["slides"])==result["source_pages"]==result["output_pages"] else 1


if __name__=="__main__":
    raise SystemExit(main())
