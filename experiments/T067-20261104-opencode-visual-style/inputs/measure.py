#!/usr/bin/env python3
"""Measure the style specimens: static structure + PowerPoint COM timings."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
PPTX = ART / "styles.pptx"
PREVIEW = HERE.parent / "preview"
COM = ART / "com.json"
STYLES = ["editorial-crimson", "liquid-glass", "clay-cartoon",
          "swiss-minimal", "maximalist-collage"]


def words(prs) -> int:
    total = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                total += len(re.findall(r"\S+", shape.text_frame.text))
    return total


def contact_sheet() -> None:
    from PIL import Image, ImageDraw, ImageFont
    shots = sorted(PREVIEW.glob("slide-*.png"))
    if not shots:
        return
    tw, th, gap, label = 560, 315, 18, 26
    cols = 3
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * gap,
                             rows * (th + label) + (rows + 1) * gap), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    for i, shot in enumerate(shots):
        im = Image.open(shot).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = gap + (i % cols) * (tw + gap)
        y = gap + (i // cols) * (th + label + gap)
        sheet.paste(im, (x, y))
        draw.text((x + 2, y + th + 5), f"{STYLES[i]}  ·  {shot.name}", font=font,
                  fill=(230, 230, 235))
    sheet.save(PREVIEW / "all-styles.png", optimize=True)


def main() -> int:
    prs = Presentation(str(PPTX))
    slides = []
    for idx, slide in enumerate(prs.slides):
        sizes: set[float] = set()
        fonts: set[str] = set()
        text_shapes = picture_shapes = custgeom = effect_lists = sp3d = 0
        gradient = pattern = soft_edges = 0
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                picture_shapes += 1
            if shape.has_text_frame and shape.text_frame.text.strip():
                text_shapes += 1
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size:
                            sizes.add(round(run.font.size.pt, 1))
                        if run.font.name:
                            fonts.add(run.font.name)
            if shape._element.find(".//" + qn("a:custGeom")) is not None:
                custgeom += 1
            if shape._element.find(".//" + qn("a:effectLst")) is not None:
                effect_lists += 1
            if shape._element.find(".//" + qn("a:sp3d")) is not None:
                sp3d += 1
            if shape._element.find(".//" + qn("a:gradFill")) is not None:
                gradient += 1
            if shape._element.find(".//" + qn("a:pattFill")) is not None:
                pattern += 1
            if shape._element.find(".//" + qn("a:softEdge")) is not None:
                soft_edges += 1
        shapes = len(slide.shapes)
        slides.append({
            "index": idx + 1,
            "style": STYLES[idx],
            "shapes": shapes,
            "pictures": picture_shapes,
            "text_shapes": text_shapes,
            "native_share": round((shapes - picture_shapes) / shapes, 3),
            "words": sum(len(re.findall(r"\S+", s.text_frame.text))
                         for s in slide.shapes if s.has_text_frame),
            "type_sizes": sorted(sizes, reverse=True),
            "type_size_count": len(sizes),
            "fonts": sorted(fonts),
            "custgeom": custgeom,
            "effect_lists": effect_lists,
            "sp3d": sp3d,
            "gradient_fills": gradient,
            "pattern_fills": pattern,
            "soft_edges": soft_edges,
        })

    pdf = PREVIEW / "styles.pdf"
    pages = None
    if pdf.is_file():
        from pypdf import PdfReader
        pages = len(PdfReader(str(pdf)).pages)

    report = {
        "file": PPTX.name,
        "bytes": PPTX.stat().st_size,
        "sha256": hashlib.sha256(PPTX.read_bytes()).hexdigest(),
        "slides": len(prs.slides),
        "words": words(prs),
        "zoom": "16:9 960x540 pt",
        "pdf_pages": pages,
        "pdf_bytes": pdf.stat().st_size if pdf.is_file() else None,
        "previews": sorted(p.name for p in PREVIEW.glob("slide-*.png")),
        "per_slide": slides,
    }
    if COM.is_file():
        report["powerpoint"] = json.loads(COM.read_text(encoding="utf-8"))
    (ART / "measure.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("file", "bytes", "slides", "words",
                                             "pdf_pages", "pdf_bytes")},
                     ensure_ascii=False, indent=2))
    print(f"wrote {ART / 'measure.json'}")
    contact_sheet()
    return 0


if __name__ == "__main__":
    sys.exit(main())
