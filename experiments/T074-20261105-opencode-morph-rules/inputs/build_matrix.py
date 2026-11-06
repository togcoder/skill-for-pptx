"""T074: build a 15-pair Morph matrix deck (two slides per case).

Each pair is: A (source) → B (Morph 1.2 s) → separator (cut). The separator
prevents a Morph chain between cases. A unique colour per case makes the object
trackable in the video frames.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import pptx_animator as anim  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import PP_ALIGN  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

EXP = ROOT / "experiments/T074-20261105-opencode-morph-rules"
ART = EXP / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

CASES = [
    # id, kind, option, name_a, name_b, text_a, text_b, extra
    ("same-bang", "rect", "byObject", "!!track", "!!track", "", "", {}),
    ("same-name", "rect", "byObject", "track", "track", "", "", {}),
    ("diff-name", "rect", "byObject", "trackA", "trackB", "", "", {}),
    ("rect-ellipse", "rect-ellipse", "byObject", "!!track", "!!track", "", "", {}),
    ("text-same", "text", "byObject", "!!track", "!!track", "MORPH", "MORPH", {}),
    ("text-diff", "text", "byObject", "!!track", "!!track", "MORPH", "CHANGE", {}),
    ("picture-same", "picture", "byObject", "!!track", "!!track", "amber", "amber", {}),
    ("picture-diff", "picture", "byObject", "!!track", "!!track", "amber", "red", {}),
    ("group-same", "group", "byObject", "!!track", "!!track", "", "", {}),
    ("rotate90", "rect", "byObject", "!!track", "!!track", "", "", {"rotate": 90}),
    ("entrance", "rect", "byObject", "!!track", "!!track", "", "", {"entrance": True}),
    ("byword", "text", "byWord", "!!track", "!!track", "MORPH RULES", "MORPH RULES", {}),
    ("bychar", "text", "byChar", "!!track", "!!track", "MORPH", "MORPH", {}),
    ("zorder", "rect", "byObject", "!!track", "!!track", "", "", {"zorder": True}),
    ("offslide", "rect", "byObject", "!!track", "!!track", "", "", {"offslide": True}),
]

PALETTE = [
    (215, 154, 50), (220, 80, 70), (80, 170, 220), (120, 200, 120),
    (200, 120, 220), (240, 200, 80), (90, 200, 190), (240, 140, 180),
    (170, 170, 240), (230, 120, 60), (140, 220, 90), (100, 180, 240),
    (230, 90, 140), (180, 140, 80), (120, 210, 170),
]
AMBER = RGBColor(0xD7, 0x9A, 0x32)
BG = RGBColor(0x1E, 0x1E, 0x1E)


def set_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG


def add_rect(slide, name, color, x, y, w=2.0, h=2.0, shape=MSO_SHAPE.RECTANGLE):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.color.rgb = RGBColor(0xF7, 0xF1, 0xE8)
    sh.line.width = Pt(1.5)
    return sh


def add_text(slide, name, color, text, x, y, w=4.0, h=1.5, size=48):
    sh = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = name
    tf = sh.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = color
    run.font.name = "Arial"
    return sh


def add_group(slide, name, color, x, y):
    group = slide.shapes.add_group_shape()
    group.name = name
    a = group.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(1.4), Inches(1.4))
    a.fill.solid(); a.fill.fore_color.rgb = color
    a.line.color.rgb = RGBColor(0xF7, 0xF1, 0xE8)
    b = group.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), Inches(0.8), Inches(1.0), Inches(1.0))
    b.fill.solid(); b.fill.fore_color.rgb = color
    b.line.color.rgb = RGBColor(0xF7, 0xF1, 0xE8)
    group.left = Inches(x)
    group.top = Inches(y)
    return group


def add_track(slide, kind, name, color, x, text, extra):
    if kind == "rect":
        return add_rect(slide, name, color, x, 2.8, 2.0, 2.0)
    if kind == "ellipse":
        return add_rect(slide, name, color, x, 2.8, 2.0, 2.0, MSO_SHAPE.OVAL)
    if kind == "text":
        return add_text(slide, name, color, text or "MORPH", x, 3.0)
    if kind == "group":
        return add_group(slide, name, color, x, 2.9)
    if kind == "picture":
        path = ensure_png(text or "amber", color)
        pic = slide.shapes.add_picture(str(path), Inches(x), Inches(2.8),
                                       Inches(2.0), Inches(2.0))
        pic.name = name
        return pic
    raise ValueError(kind)


def ensure_png(key, color):
    path = ART / "assets" / f"{key}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        im = Image.new("RGB", (240, 240), tuple(color))
        d = ImageDraw.Draw(im)
        d.rectangle((12, 12, 228, 228), outline=(247, 241, 232), width=6)
        d.text((70, 105), key.upper(), fill=(30, 30, 30))
        im.save(path)
    return path


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for i, (cid, kind, option, name_a, name_b, text_a, text_b, extra) in enumerate(CASES):
        color = RGBColor(*PALETTE[i])
        a = prs.slides.add_slide(blank); set_bg(a)
        add_text(a, "case-label", RGBColor(0x88, 0x88, 0x88), cid, 0.5, 0.4, 6, 0.5, 18)
        a_obj = add_track(a, "rect" if kind == "rect-ellipse" else kind,
                          name_a, color, 1.5, text_a, extra)
        if extra.get("zorder"):
            add_rect(a, "foreground", RGBColor(0x44, 0x44, 0x44), 1.3, 2.6, 2.4, 2.4)

        b = prs.slides.add_slide(blank); set_bg(b)
        add_text(b, "case-label", RGBColor(0x88, 0x88, 0x88), cid, 0.5, 0.4, 6, 0.5, 18)
        bx = 9.5 if not extra.get("offslide") else 14.5
        b_obj = add_track(b, "ellipse" if kind == "rect-ellipse" else kind,
                          name_b, color, bx, text_b, extra)
        if extra.get("zorder"):
            add_rect(b, "foreground", RGBColor(0x44, 0x44, 0x44), 9.3, 2.6, 2.4, 2.4)
        if extra.get("rotate"):
            b_obj.rotation = extra["rotate"]

        alt = anim.add_morph_transition(b._element, 1200)
        morph = alt.find(".//{http://schemas.microsoft.com/office/powerpoint/2015/09/main}morph")
        morph.set("option", option)

        if extra.get("entrance"):
            anim.apply_timeline(b._element, [{
                "id": f"{cid}.entrance", "start": "click",
                "effects": [{"preset": "fade", "trigger": "click",
                             "duration_ms": 400, "spid": str(b_obj.shape_id)}],
            }], mode="replace")

        sep = prs.slides.add_slide(blank); set_bg(sep)
        add_text(sep, "case-label", RGBColor(0x66, 0x66, 0x66),
                 f"{cid} / separator", 0.5, 0.4, 8, 0.5, 18)
    out = ART / "morph-matrix.pptx"
    prs.save(out)
    print("wrote", out, out.stat().st_size, "bytes,", len(prs.slides), "slides")


if __name__ == "__main__":
    build()
