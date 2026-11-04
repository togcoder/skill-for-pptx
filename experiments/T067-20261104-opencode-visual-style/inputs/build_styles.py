#!/usr/bin/env python3
"""Build five style specimens with identical content (T067).

One content unit — a claim, one portrait, two facts — rendered five ways.
Every colour, type size, radius and duration comes from visual_style.py;
this file contains composition only.

Pipeline:
  1. python build_styles.py            -> artifacts/_base.pptx + effects manifest
  2. deckcraft-cli run ...             -> artifacts/_effects.pptx
  3. python build_styles.py --motion   -> artifacts/styles.pptx
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from lxml import etree
from PIL import ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_PATTERN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
import pptx_animator as anim  # noqa: E402
import visual_style as vs  # noqa: E402

ART = HERE.parent / "artifacts"
ASSETS = HERE / "assets"
BASE = ART / "_base.pptx"
EFFECTS = ART / "_effects.pptx"
FINAL = ART / "styles.pptx"
MANIFEST = ART / "deckcraft-effects.txt"

W, H = 960.0, 540.0
M = 56.0

# --------------------------------------------------------------------------- #
# Content — the same four strings on every slide
# --------------------------------------------------------------------------- #
EYEBROW = "LUẬN CƯƠNG 11 · 1845"
CLAIM_1 = "Không chỉ giải thích."
CLAIM_2 = "Mà cải tạo thế giới."
FACT_1_VALUE = "1845"
FACT_1_LABEL = "LUẬN CƯƠNG VỀ PHOIƠBẮC"
FACT_2_VALUE = "11"
FACT_2_LABEL = "LUẬN ĐIỂM, CÂU CUỐI LÀ MỆNH LỆNH"
CAPTION = "C. Mác · 1875"

FONT_FILES = {
    "palatino linotype": ["pala.ttf", "palab.ttf"],
    "arial": ["arial.ttf", "arialbd.ttf"],
    "segoe ui": ["segoeui.ttf", "segoeuib.ttf"],
    "segoe ui light": ["segoeuil.ttf", "segoeui.ttf"],
    "segoe ui semibold": ["seguisb.ttf", "segoeuib.ttf"],
    "segoe ui black": ["seguibl.ttf", "segoeuib.ttf"],
}

_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(family: str, size: float) -> ImageFont.FreeTypeFont | None:
    key = (family.lower(), round(size))
    if key not in _font_cache:
        for name in FONT_FILES.get(family.lower(), []):
            path = Path("C:/Windows/Fonts") / name
            if path.is_file():
                _font_cache[key] = ImageFont.truetype(str(path), max(1, round(size * 3)))
                break
        else:
            _font_cache[key] = None
    return _font_cache[key]


def width_pt(text: str, family: str, size: float, bold: bool = False) -> float:
    font = _font(family, size)
    if font is None:
        return len(text) * size * 0.55
    return font.getlength(text) / 3.0 * (1.02 if bold else 1.0)


def fit(text: str, family: str, max_w: float, start: float, floor: float = 18,
        bold: bool = False) -> float:
    size = start
    while size > floor and width_pt(text, family, size, bold) > max_w:
        size -= 1
    return size


# --------------------------------------------------------------------------- #
# Native drawing helpers
# --------------------------------------------------------------------------- #
def _rgb(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value.lstrip("#").upper())


def _sub(parent, tag, **attrs):
    el = etree.SubElement(parent, qn(tag))
    for k, v in attrs.items():
        el.set(k, str(v))
    return el


def set_fill_alpha(shape, opacity: float, target: str = "fill") -> None:
    """Add <a:alpha> to the solid/gradient/pattern stops of a shape's fill."""
    spPr = shape._element.spPr
    if target == "fill":
        nodes = spPr.findall(qn("a:solidFill") + "/" + qn("a:srgbClr"))
        nodes += spPr.findall(qn("a:gradFill") + "//" + qn("a:srgbClr"))
        nodes += spPr.findall(qn("a:pattFill") + "/" + qn("a:fgClr") + "/"
                              + qn("a:srgbClr"))
    else:
        nodes = spPr.findall(qn("a:ln") + "/" + qn("a:solidFill") + "/" + qn("a:srgbClr"))
    for node in nodes:
        for old in node.findall(qn("a:alpha")):
            node.remove(old)
        _sub(node, "a:alpha", val=int(round(opacity * 100000)))


def rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, radius=None,
         name=None, rotation=0.0, opacity=1.0, dash=None, shadow=None):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(kind, Pt(x), Pt(y), Pt(w), Pt(h))
    if radius:
        s.adjustments[0] = min(0.5, radius / max(1.0, min(w, h)))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = _rgb(fill)
        if opacity < 1.0:
            set_fill_alpha(s, opacity)
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = _rgb(line)
        s.line.width = Pt(lw)
        if dash:
            s.line.dash_style = dash
    s.rotation = rotation
    s.name = name or "shape"
    s.text_frame.word_wrap = False
    _strip_style(s)
    return s


def _strip_style(shape) -> None:
    """Remove <p:style> so no theme fill/effect leaks into a specimen."""
    el = shape._element
    for style in el.findall(qn("p:style")):
        el.remove(style)


def _insert_gradient(spPr, grad) -> None:
    """Insert gradFill in schema order: after geometry, before a:ln."""
    for tag in ("a:solidFill", "a:noFill", "a:gradFill"):
        for el in spPr.findall(qn(tag)):
            spPr.remove(el)
    spPr.insert_element_before(grad, "a:ln", "a:effectLst", "a:effectDag",
                               "a:scene3d", "a:sp3d", "a:extLst")


def grad_orb(slide, x, y, d, color, peak=0.45, name="orb"):
    """Radial gradient from `color` at `peak` alpha to transparent."""
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(x), Pt(y), Pt(d), Pt(d))
    grad = etree.Element(qn("a:gradFill"))
    grad.set("rotWithShape", "1")
    stops = etree.SubElement(grad, qn("a:gsLst"))
    for pos, alpha in ((0.0, peak), (0.45, peak * 0.40), (0.78, 0.0), (1.0, 0.0)):
        gs = _sub(stops, "a:gs", pos=int(pos * 100000))
        clr = _sub(gs, "a:srgbClr", val=color.lstrip("#").upper())
        _sub(clr, "a:alpha", val=int(alpha * 100000))
    path = _sub(grad, "a:path", path="circle")
    _sub(path, "a:fillToRect", l=0, t=0, r=100000, b=100000)
    _insert_gradient(s._element.spPr, grad)
    s.line.fill.background()
    s.name = name
    _strip_style(s)
    return s


def pattern_rect(slide, x, y, w, h, fg, bg, preset=MSO_PATTERN.PERCENT_20,
                 opacity=0.1, name="texture"):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Pt(x), Pt(y), Pt(w), Pt(h))
    s.line.fill.background()
    s.fill.patterned()
    s.fill.pattern = preset
    s.fill.fore_color.rgb = _rgb(fg)
    s.fill.back_color.rgb = _rgb(bg)
    set_fill_alpha(s, opacity)
    s.name = name
    _strip_style(s)
    return s


def text(slide, x, y, w, h, paras, name, anchor=MSO_ANCHOR.TOP,
         align=PP_ALIGN.LEFT, rotation=0.0, margins=(0, 0, 0, 0)):
    box = slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left, tf.margin_top, tf.margin_right, tf.margin_bottom = (
        Pt(margins[0]), Pt(margins[1]), Pt(margins[2]), Pt(margins[3]))
    tf.vertical_anchor = anchor
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = para.get("align", align)
        p.line_spacing = para.get("line_spacing", 1.0)
        p.space_before = Pt(para.get("space_before", 0))
        p.space_after = Pt(para.get("space_after", 0))
        for txt, color, opts in para["runs"]:
            r = p.add_run()
            r.text = txt
            f = r.font
            family = opts.get("family", para["family"])
            f.name = family
            f.size = Pt(opts.get("size", para["size"]))
            tracking = opts.get("tracking", para.get("tracking", 0.0))
            # a tracked label in a regular family is set bold, as the preset's
            # label weight asks; semibold/black families already carry weight
            infer_bold = (tracking >= 0.05
                          and not any(w in family.lower()
                                      for w in ("semibold", "black", "light")))
            f.bold = opts.get("bold", para.get("bold", infer_bold))
            f.italic = opts.get("italic", False)
            f.color.rgb = _rgb(color)
            if tracking:
                f._element.set("spc", str(int(round(tracking * f.size.pt * 100))))
    box.rotation = rotation
    box.name = name
    return box


def outline_run(run, color: str, width_pt: float, alpha: float = 1.0) -> None:
    """Native text outline only (no fill); part of the maximalist type language."""
    rPr = run.font._element
    for tag in ("a:solidFill", "a:noFill", "a:gradFill"):
        for el in rPr.findall(qn(tag)):
            rPr.remove(el)
    ln = etree.Element(qn("a:ln"))
    ln.set("w", str(int(round(width_pt * 12700))))
    sf = etree.SubElement(ln, qn("a:solidFill"))
    clr = etree.SubElement(sf, qn("a:srgbClr"))
    clr.set("val", color.lstrip("#").upper())
    etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    rPr.insert(0, ln)
    rPr.insert(1, etree.Element(qn("a:noFill")))


def pic(slide, path, x, y, w, h, name, line=None, lw=0, rotation=0.0):
    p = slide.shapes.add_picture(str(path), Pt(x), Pt(y), Pt(w), Pt(h))
    p.name = name
    p.rotation = rotation
    if line:
        p.line.color.rgb = _rgb(line)
        p.line.width = Pt(lw)
    return p


def picture_alpha(picture, opacity: float) -> None:
    """argb alpha (a:alphaModFix) on a picture; python-pptx has no API."""
    blip = picture._element.blipFill.blip
    node = etree.SubElement(blip, qn("a:alphaModFix"))
    node.set("amt", str(int(round(opacity * 100000))))


# --------------------------------------------------------------------------- #
# Shared text blocks
# --------------------------------------------------------------------------- #
def claim(slide, tk, x, y, w, gap, family_role="display", color=None,
          size_key="display", max_h=None, name_prefix="title"):
    """Two-line claim fitted to the column width; returns the bottom y."""
    family = tk["type"]["families"][family_role]
    color = color or tk["palette"]["text"]
    size = tk["type"]["sizes_pt"][size_key]
    s1 = fit(CLAIM_1, family, w, size)
    s2 = fit(CLAIM_2, family, w, size)
    size = min(s1, s2)
    lh = tk["type"]["line_height"]["display"]
    tracking = tk["type"]["tracking_em"]["display"]
    paras = [
        {"runs": [(CLAIM_1, color, {})], "size": size, "family": family,
         "line_spacing": lh, "tracking": tracking},
        {"runs": [(CLAIM_2, color, {})], "size": size, "family": family,
         "line_spacing": lh, "tracking": tracking, "space_before": gap},
    ]
    text(slide, x, y, w, size * lh * 2 + gap + 8, paras, f"{name_prefix}-claim")
    return y + size * lh * 2 + gap + 8


def eyebrow(slide, tk, x, y, color=None):
    text(slide, x, y, 340, 14,
         [{"runs": [(EYEBROW, color or tk["palette"]["accent"], {})],
           "size": tk["type"]["sizes_pt"]["label"],
           "family": tk["type"]["families"]["label"],
           "tracking": tk["type"]["tracking_em"]["label"]}], "eyebrow")


# --------------------------------------------------------------------------- #
# 1. editorial-crimson
# --------------------------------------------------------------------------- #
def build_editorial(slide, tk, fx):
    p = tk["palette"]
    rect(slide, 0, 0, W, H, p["canvas"], name="bg")
    rect(slide, 440, 0, 2, H, p["accent"], name="thread")
    slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(434), Pt(263), Pt(14), Pt(14)).fill.solid()
    dot = slide.shapes[-1]
    dot.fill.fore_color.rgb = _rgb(p["text"])
    dot.line.fill.background()
    dot.name = "thread-dot"
    _strip_style(dot)

    slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(468), Pt(42), Pt(440), Pt(440))
    disk = slide.shapes[-1]
    disk.fill.solid()
    disk.fill.fore_color.rgb = _rgb(p["surface_alt"])
    disk.line.fill.background()
    disk.name = "portrait-disk"
    _strip_style(disk)

    ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(456), Pt(30), Pt(464), Pt(464))
    ring.fill.background()
    ring.line.color.rgb = _rgb(p["accent"])
    ring.line.width = Pt(1.25)
    ring.name = "portrait-ring"
    _strip_style(ring)

    pic(slide, ASSETS / "marx-editorial.png", 488, 62, 400, 400, "portrait")

    eyebrow(slide, tk, M, 52)
    claim(slide, tk, M, 88, 360, 4)
    rect(slide, M, 252, 120, 3, p["accent"], name="rule")

    for i, (val, lab, xx) in enumerate((
            (FACT_1_VALUE, FACT_1_LABEL, M),
            (FACT_2_VALUE, FACT_2_LABEL, 248))):
        text(slide, xx, 286, 176, 48,
             [{"runs": [(val, p["accent_text"], {})],
               "size": tk["type"]["sizes_pt"]["title"],
               "family": tk["type"]["families"]["display"]}], f"fact-{i}-value")
        text(slide, xx, 338, 178, 44,
             [{"runs": [(lab, p["text_muted"], {})],
               "size": tk["type"]["sizes_pt"]["label"],
               "family": tk["type"]["families"]["label"],
               "tracking": tk["type"]["tracking_em"]["label"],
               "line_spacing": 1.25}], f"fact-{i}-label")
    text(slide, M, 496, 260, 14,
         [{"runs": [(CAPTION, p["text_muted"], {})],
           "size": tk["type"]["sizes_pt"]["micro"],
           "family": tk["type"]["families"]["body"]}], "caption")


# --------------------------------------------------------------------------- #
# 2. liquid-glass
# --------------------------------------------------------------------------- #
def build_glass(slide, tk, fx):
    p = tk["palette"]
    rect(slide, 0, 0, W, H, p["canvas"], name="bg")
    o1 = grad_orb(slide, -120, -180, 600, p["accent"], 0.62, "orb-1")
    o2 = grad_orb(slide, 600, -170, 560, p["accent_2"], 0.55, "orb-2")
    o3 = grad_orb(slide, 560, 300, 460, p["accent"], 0.26, "orb-3")
    fx += [{"shape": s.name, "softEdges": 70} for s in (o1, o2, o3)]

    pane = rect(slide, 512, 64, 400, 440, p["text"], line=p["text"],
                lw=tk["geometry"]["stroke_pt"], radius=tk["geometry"]["radius_pt"],
                name="pane", opacity=0.10)
    set_fill_alpha(pane, 0.10)
    set_fill_alpha(pane, 0.30, "line")
    fx.append({"shape": "pane", "shadowProps": {"color": p["ink"], "transparency": 0.55,
                                                "blur": 58, "dist": 20, "dir": 90}})
    spec = rect(slide, 536, 66, 352, 1.5, p["text"], name="pane-specular", opacity=0.75)
    fx.append({"shape": "pane-specular", "softEdges": 0})

    pic(slide, ASSETS / "marx-glass.png", 560, 88, 304, 380, "portrait")
    sheen = rect(slide, 560, 356, 304, 112, None, name="sheen", radius=18)
    grad = etree.Element(qn("a:gradFill"))
    grad.set("rotWithShape", "1")
    stops = etree.SubElement(grad, qn("a:gsLst"))
    for pos, a in ((0.0, 0.0), (1.0, 0.34)):
        gs = _sub(stops, "a:gs", pos=int(pos * 100000))
        clr = _sub(gs, "a:srgbClr", val=p["text"])
        _sub(clr, "a:alpha", val=int(a * 100000))
    _sub(grad, "a:lin", ang=5400000, scaled=0)
    _insert_gradient(sheen._element.spPr, grad)
    sheen.line.fill.background()
    sheen.name = "sheen"
    fx.append({"shape": "sheen", "softEdges": 24})

    text(slide, 560, 474, 240, 14,
         [{"runs": [(CAPTION, p["text_muted"], {})],
           "size": tk["type"]["sizes_pt"]["micro"],
           "family": tk["type"]["families"]["body"]}], "caption")

    eyebrow(slide, tk, M, 58)
    claim(slide, tk, M, 92, 410, 2)
    rect(slide, M, 244, 64, 2, p["accent"], name="rule")

    chips = [("chip-1", M, 176, FACT_1_VALUE, "LUẬN CƯƠNG RA ĐỜI"),
             ("chip-2", 248, 224, FACT_2_VALUE, "LUẬN ĐIỂM, CÂU CUỐI LÀ MỆNH LỆNH")]
    for name, x, w, val, lab in chips:
        c = rect(slide, x, 292, w, 100, p["text"], line=p["text"], lw=0.75,
                 radius=24, name=name, opacity=0.06)
        set_fill_alpha(c, 0.06)
        fx.append({"shape": name, "shadow": {"color": p["ink"], "blur": 30,
                                             "dist": 12, "dir": 90}})
        text(slide, x + 18, 306, w - 30, 34,
             [{"runs": [(val, p["text"], {})], "size": 27,
               "family": tk["type"]["families"]["display"]}], f"{name}-value")
        text(slide, x + 18, 344, w - 30, 34,
             [{"runs": [(lab, p["text_muted"], {})], "size": 9.5,
               "family": tk["type"]["families"]["label"],
               "tracking": 0.1, "line_spacing": 1.2}], f"{name}-label")
    text(slide, 852, 508, 60, 12,
         [{"runs": [("01 / 05", p["text_muted"], {})], "size": 9,
           "family": tk["type"]["families"]["label"]}], "folio", align=PP_ALIGN.RIGHT)


# --------------------------------------------------------------------------- #
# 3. clay-cartoon
# --------------------------------------------------------------------------- #
def build_clay(slide, tk, fx):
    p = tk["palette"]
    rect(slide, 0, 0, W, H, p["canvas"], name="bg")
    backdrop = slide.shapes.add_shape(MSO_SHAPE.OVAL, Pt(470), Pt(-70), Pt(520), Pt(520))
    backdrop.fill.solid()
    backdrop.fill.fore_color.rgb = _rgb(p["surface"])
    backdrop.line.fill.background()
    backdrop.name = "backdrop"
    _strip_style(backdrop)

    eyebrow_pill = rect(slide, M, 46, 202, 26, p["accent_3"], radius=13,
                        name="eyebrow-pill")
    text(slide, M + 14, 52, 180, 14,
         [{"runs": [(EYEBROW, p["ink"], {})], "size": 10,
           "family": tk["type"]["families"]["label"],
           "tracking": 0.12}], "eyebrow")
    fx.append({"shape": "eyebrow-pill", "threeD": {"camera": "orthographicFront", "bevelTop": "circle", "bevelTopW": 4, "bevelTopH": 3, "material": "matte", "lighting": "threePt"}})

    hi = rect(slide, 44, 150, 428, 50, p["accent_3"], radius=10, name="highlight",
              rotation=-1.5, opacity=0.9)
    fx.append({"shape": "highlight", "threeD": {"camera": "orthographicFront", "bevelTop": "circle", "bevelTopW": 4, "bevelTopH": 3, "material": "matte", "lighting": "threePt"}})

    family = tk["type"]["families"]["display"]
    size = min(fit(CLAIM_1, family, 440, 42), fit(CLAIM_2, family, 440, 42))
    text(slide, M, 86, 450, 54,
         [{"runs": [(CLAIM_1, p["ink"], {"size": size})], "family": family,
           "size": size, "line_spacing": 1.0, "tracking": -0.02}], "title-1")
    text(slide, M, 146, 460, 54,
         [{"runs": [(CLAIM_2, p["ink"], {"size": size})],
           "family": family, "size": size, "line_spacing": 1.0,
           "tracking": -0.02}], "title-2")

    # cream blob rim is baked into the PNG; the picture carries no rectangle border
    med = rect(slide, 556, 120, 316, 396, p["surface_alt"], radius=60,
               name="portrait-back", rotation=5)
    fx += [{"shape": "portrait-back", "softEdges": 0}]
    portrait = pic(slide, ASSETS / "marx-clay.png", 556, 92, 300, 375,
                   "portrait", rotation=3)
    fx.append({"shape": "portrait", "shadow": {"color": p["ink"], "blur": 26,
                                               "dist": 12, "dir": 100}})

    badge = rect(slide, 512, 56, 104, 104, p["accent"], radius=52, name="badge",
                 line=p["accent_text"], lw=4, rotation=-7)
    fx.append({"shape": "badge", "threeD": {"camera": "orthographicFront", "bevelTop": "circle",
                                             "bevelTopW": 4, "bevelTopH": 3,
                                             "material": "matte", "lighting": "threePt"},
               "shadowProps": {"color": p["ink"], "transparency": 0.6,
                               "blur": 14, "dist": 6, "dir": 90}})
    text(slide, 512, 56, 104, 104,
         [{"runs": [("C. MÁC", p["accent_text"], {})], "size": 13,
           "family": tk["type"]["families"]["label"], "tracking": 0.1}],
         "badge-text", align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, rotation=-7)

    tiles = [("tile-1", M, 250, p["surface"], p["ink"], p["text_muted"],
              FACT_1_VALUE, FACT_1_LABEL),
             ("tile-2", 322, 250, p["accent_2"], p["accent_text"], p["accent_text"],
              FACT_2_VALUE, FACT_2_LABEL)]
    for name, x, w, fill, vcol, lcol, val, lab in tiles:
        t = rect(slide, x, 330, w, 118, fill, radius=28, name=name)
        fx += [{"shape": name, "smooth": 92},
               {"shape": name, "threeD": {"camera": "orthographicFront", "bevelTop": "circle",
                                          "bevelTopW": 5, "bevelTopH": 3,
                                          "material": "matte", "lighting": "threePt"},
                "shadowProps": {"color": p["ink"], "transparency": 0.62,
                                "blur": 16, "dist": 7, "dir": 90}}]
        text(slide, x + 24, 346, w - 40, 40,
             [{"runs": [(val, vcol, {})], "size": 32, "family": family}],
             f"{name}-value")
        text(slide, x + 24, 392, w - 44, 42,
             [{"runs": [(lab, lcol, {})], "size": 10,
               "family": tk["type"]["families"]["label"], "tracking": 0.06,
               "line_spacing": 1.2}], f"{name}-label")
    text(slide, M, 496, 280, 14,
         [{"runs": [(CAPTION, p["text_muted"], {})],
           "size": tk["type"]["sizes_pt"]["micro"],
           "family": tk["type"]["families"]["body"]}], "caption")


# --------------------------------------------------------------------------- #
# 4. swiss-minimal
# --------------------------------------------------------------------------- #
def build_swiss(slide, tk, fx):
    p = tk["palette"]
    rect(slide, 0, 0, W, H, p["canvas"], name="bg")
    rect(slide, M, 96, 848, 0.75, p["text"], name="rule-top")
    rect(slide, M, 430, 848, 0.75, p["text"], name="rule-bottom")
    rect(slide, 660, 96, 0.75, 334, p["text"], name="rule-col")

    rect(slide, M, 62, 12, 12, p["accent"], name="accent-block")
    text(slide, 80, 60, 380, 14,
         [{"runs": [(EYEBROW, p["text"], {})],
           "size": tk["type"]["sizes_pt"]["label"],
           "family": tk["type"]["families"]["label"],
           "tracking": tk["type"]["tracking_em"]["label"]}], "eyebrow")

    family = tk["type"]["families"]["display"]
    size = min(fit(CLAIM_1, family, 560, tk["type"]["sizes_pt"]["display"], bold=True),
               fit(CLAIM_2, family, 560, tk["type"]["sizes_pt"]["display"], bold=True))
    text(slide, M, 118, 580, 60,
         [{"runs": [(CLAIM_1, p["text"], {"bold": True})], "size": size,
           "family": family, "line_spacing": 0.98,
           "tracking": tk["type"]["tracking_em"]["display"]}], "title-1")
    text(slide, M, 118 + size * 1.0, 580, 60,
         [{"runs": [(CLAIM_2, p["text"], {"bold": True})], "size": size,
           "family": family, "line_spacing": 0.98,
           "tracking": tk["type"]["tracking_em"]["display"]}], "title-2")

    pic(slide, ASSETS / "marx-swiss.png", 690, 112, 214, 214, "portrait")
    text(slide, 690, 334, 214, 30,
         [{"runs": [("C. Mác, 1875", p["text_muted"], {})], "size": 9,
           "family": tk["type"]["families"]["body"]}], "caption")

    rect(slide, M, 296, 360, 0.75, p["text"], name="rule-facts")
    for i, (val, lab, x) in enumerate(((FACT_1_VALUE, FACT_1_LABEL, M),
                                       (FACT_2_VALUE, FACT_2_LABEL, 250))):
        text(slide, x, 312, 190, 44,
             [{"runs": [(val, p["text"], {"bold": True})], "size": 36,
               "family": family}], f"fact-{i}-value")
        text(slide, x, 370, 180, 46,
             [{"runs": [(lab, p["text_muted"], {})], "size": 10,
               "family": tk["type"]["families"]["label"], "tracking": 0.12,
               "line_spacing": 1.25}], f"fact-{i}-label")
    text(slide, 760, 496, 144, 14,
         [{"runs": [("STYLE 04 / 05", p["text_muted"], {})], "size": 9,
           "family": tk["type"]["families"]["label"], "tracking": 0.12}],
         "folio", align=PP_ALIGN.RIGHT)


# --------------------------------------------------------------------------- #
# 5. maximalist-collage
# --------------------------------------------------------------------------- #
def build_collage(slide, tk, fx):
    p = tk["palette"]
    rect(slide, 0, 0, W, H, p["canvas"], name="bg")
    pattern_rect(slide, 0, 0, W, H, p["ink"], p["canvas"], opacity=0.09,
                 name="halftone")

    strip = rect(slide, -70, 40, 580, 64, p["accent"], name="strip", rotation=-6)
    text(slide, 8, 58, 460, 22,
         [{"runs": [(EYEBROW, p["accent_text"], {})], "size": 12,
           "family": tk["type"]["families"]["label"], "tracking": 0.22}],
         "eyebrow", rotation=-6)
    fx.append({"shape": "strip", "shadowProps": {"color": p["ink"], "transparency": 0.55,
                                               "blur": 3, "dist": 4, "dir": 45}})

    rect(slide, 40, 116, 424, 62, p["accent_3"], name="sticker-1", rotation=-3)
    text(slide, 56, 128, 400, 44,
         [{"runs": [(CLAIM_1, p["ink"], {"bold": True})], "size": 36,
           "family": tk["type"]["families"]["display"], "tracking": -0.01}],
         "title-1", rotation=-3)
    fx.append({"shape": "sticker-1", "shadowProps": {"color": p["ink"], "transparency": 0.5,
                                                 "blur": 3, "dist": 5, "dir": 45}})

    rect(slide, 46, 196, 470, 92, p["accent"], name="block-2", rotation=2)
    text(slide, 62, 214, 444, 62,
         [{"runs": [(CLAIM_2, p["accent_text"], {"bold": True})], "size": 36,
           "family": tk["type"]["families"]["display"], "tracking": -0.015}],
         "title-2", rotation=2)
    fx.append({"shape": "block-2", "shadowProps": {"color": p["ink"], "transparency": 0.5,
                                               "blur": 3, "dist": 5, "dir": 45}})

    # a ghost numeral fills the middle void and doubles the "11" fact as texture
    ghost = text(slide, 6, 298, 300, 116,
                 [{"runs": [("11", p["ink"], {"bold": True})], "size": 92,
                   "family": tk["type"]["families"]["display"], "line_spacing": 0.9}],
                 "ghost-numeral", anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT,
                 rotation=-7)
    outline_run(ghost.text_frame.paragraphs[0].runs[0], p["ink"], 1.75, 0.28)

    # a second, smaller print of the same plate: collage repetition, no new content
    stamp = pic(slide, ASSETS / "marx-collage.png", 330, 286, 128, 160,
                "portrait-stamp", rotation=7)
    picture_alpha(stamp, 0.55)
    rect(slide, 336, 282, 76, 15, p["surface"], name="stamp-tape",
         rotation=-10, opacity=0.55)

    pic(slide, ASSETS / "marx-collage.png", 650, 96, 252, 315, "portrait",
        line=p["ink"], lw=3, rotation=4)
    fx.append({"shape": "portrait", "shadowProps": {"color": p["ink"], "transparency": 0.45,
                                                "blur": 3, "dist": 6, "dir": 45}})
    tape = rect(slide, 672, 76, 128, 26, p["surface_alt"], name="tape",
                rotation=-17, opacity=0.62)
    fx.append({"shape": "tape", "shadowProps": {"color": p["ink"], "transparency": 0.65,
                                            "blur": 4, "dist": 2, "dir": 90}})

    badge = rect(slide, 806, 358, 100, 100, p["accent_2"], radius=50,
                 name="badge", line=p["accent_text"], lw=2, rotation=8)
    text(slide, 806, 386, 100, 44,
         [{"runs": [(FACT_2_VALUE, p["accent_text"], {"bold": True})], "size": 30,
           "family": tk["type"]["families"]["display"]}], "badge-value",
         align=PP_ALIGN.CENTER, rotation=8)
    text(slide, 806, 424, 100, 16,
         [{"runs": [("LUẬN ĐIỂM", p["accent_text"], {})], "size": 8,
           "family": tk["type"]["families"]["label"], "tracking": 0.1}],
         "badge-label", align=PP_ALIGN.CENTER, rotation=8)
    fx.append({"shape": "badge", "shadowProps": {"color": p["ink"], "transparency": 0.4,
                                             "blur": 3, "dist": 5, "dir": 45}})

    rect(slide, 38, 430, 372, 34, p["surface"], name="fact-strip-1", rotation=-2)
    text(slide, 50, 439, 350, 18,
         [{"runs": [(f"{FACT_1_VALUE} — {FACT_1_LABEL}", p["text"], {})],
           "size": 10, "family": tk["type"]["families"]["label"],
           "tracking": 0.08}], "fact-1", rotation=-2)
    rect(slide, 54, 474, 392, 34, p["surface_alt"], name="fact-strip-2", rotation=1.5)
    text(slide, 66, 483, 370, 18,
         [{"runs": [(f"{FACT_2_VALUE} — {FACT_2_LABEL}", p["text"], {})],
           "size": 10, "family": tk["type"]["families"]["label"],
           "tracking": 0.06}], "fact-2", rotation=1.5)
    for strip_name in ("fact-strip-1", "fact-strip-2"):
        fx.append({"shape": strip_name, "shadowProps": {"color": p["ink"], "transparency": 0.6,
                                                    "blur": 2, "dist": 3, "dir": 45}})


BUILDERS = {
    "editorial-crimson": build_editorial,
    "liquid-glass": build_glass,
    "clay-cartoon": build_clay,
    "swiss-minimal": build_swiss,
    "maximalist-collage": build_collage,
}


# --------------------------------------------------------------------------- #
# Motion: one plan per style, durations from the preset
# --------------------------------------------------------------------------- #
def add_motion(slide, style_id, tk, bounds):
    m = tk["motion"]
    def eff(name, verb, start="click", duration=None):
        return {"spid": str(bounds[name]), "preset": verb, "trigger": start,
                "duration_ms": duration or m["enter_ms"]}

    if style_id == "editorial-crimson":
        clicks = [
            {"id": "c1", "start": "click", "effects": [
                eff("eyebrow", "fade"), eff("title-claim", "wipe-up", "with",
                                            m["move_ms"])]},
            {"id": "c2", "start": "click", "effects": [
                eff("portrait", "zoom", "click", m["enter_ms"]),
                eff("portrait-ring", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [
                eff("rule", "wipe-left", "click", m["move_ms"]),
                eff("fact-0-value", "fade", "with"), eff("fact-0-label", "fade", "with"),
                eff("fact-1-value", "fade", "with"), eff("fact-1-label", "fade", "with")]},
        ]
    elif style_id == "liquid-glass":
        clicks = [
            {"id": "c1", "start": "click", "effects": [
                eff("pane", "fade", "click", m["enter_ms"]),
                eff("portrait", "fade", "with", m["move_ms"]),
                eff("sheen", "fade", "with", m["move_ms"])]},
            {"id": "c2", "start": "click", "effects": [
                eff("eyebrow", "fade", "click"), eff("title-claim", "float-in", "with",
                                                     m["move_ms"])]},
            {"id": "c3", "start": "click", "effects": [
                eff("chip-1", "float-in", "click", m["enter_ms"]),
                eff("chip-1-value", "fade", "with"), eff("chip-1-label", "fade", "with"),
                eff("chip-2", "float-in", "with", m["enter_ms"]),
                eff("chip-2-value", "fade", "with"), eff("chip-2-label", "fade", "with")]},
        ]
    elif style_id == "clay-cartoon":
        clicks = [
            {"id": "c1", "start": "click", "effects": [
                eff("eyebrow-pill", "zoom", "click", m["enter_ms"]),
                eff("title-1", "zoom", "with", m["enter_ms"]),
                eff("title-2", "zoom", "with", m["enter_ms"])]},
            {"id": "c2", "start": "click", "effects": [
                eff("portrait", "zoom", "click", m["enter_ms"]),
                eff("badge", "zoom", "with"), eff("badge-text", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [
                eff("tile-1", "zoom", "click", m["enter_ms"]),
                eff("tile-1-value", "fade", "with"), eff("tile-1-label", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [
                eff("tile-2", "zoom", "click", m["enter_ms"]),
                eff("tile-2-value", "fade", "with"), eff("tile-2-label", "fade", "with")]},
        ]
    elif style_id == "swiss-minimal":
        clicks = [
            {"id": "c1", "start": "click", "effects": [
                eff("title-1", "fade", "click"), eff("title-2", "fade", "with"),
                eff("rule-top", "wipe-left", "with", m["move_ms"])]},
            {"id": "c2", "start": "click", "effects": [
                eff("portrait", "fade", "click"), eff("caption", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [
                eff("fact-0-value", "fade", "click"), eff("fact-0-label", "fade", "with"),
                eff("fact-1-value", "fade", "with"), eff("fact-1-label", "fade", "with")]},
        ]
    else:  # maximalist-collage
        clicks = [
            {"id": "c1", "start": "click", "effects": [
                eff("strip", "wipe-left", "click", m["enter_ms"]),
                eff("title-1", "zoom", "with"), eff("title-2", "zoom", "with")]},
            {"id": "c2", "start": "click", "effects": [
                eff("portrait", "zoom", "click"), eff("tape", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [
                eff("badge", "zoom", "click"), eff("fact-1", "fade", "with"),
                eff("fact-2", "fade", "with")]},
        ]
    anim.apply_timeline(slide._element, clicks, mode="replace")


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_base() -> None:
    prs = Presentation()
    prs.slide_width, prs.slide_height = Pt(W), Pt(H)
    blank = prs.slide_layouts[6]
    manifest: list[dict] = []
    ids: dict[str, dict[str, int]] = {}
    for style_id, builder in BUILDERS.items():
        tk = vs.resolve(vs.get(style_id))
        slide = prs.slides.add_slide(blank)
        slide.name = style_id
        fx: list[dict] = []
        builder(slide, tk, fx)
        slide.notes_slide.notes_text_frame.text = (
            f"{tk['label_vi']} — {vs.get(style_id)['intent']} "
            f"Motion: {vs.get(style_id)['motion']['language']}, "
            f"{tk['motion']['enter_ms']} ms enters, {tk['motion']['morph_ms']} ms Morph. "
            f"Do: {'; '.join(vs.get(style_id)['do'][:3])}. "
            f"Don't: {'; '.join(vs.get(style_id)['dont'][:2])}.")
        ids[style_id] = {s.name: s.shape_id for s in slide.shapes}
        manifest.append({"style": style_id, "slide": len(prs.slides) - 1,
                         "effects": [dict(e, id=ids[style_id][e["shape"]])
                                     for e in fx]})
    ART.mkdir(parents=True, exist_ok=True)
    prs.save(str(BASE))
    (ART / "shape-ids.json").write_text(
        json.dumps(ids, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    for entry in manifest:
        lines.append(f'slide.go={{"index": {entry["slide"]}}}')
        for e in entry["effects"]:
            sid = e.pop("id")
            if "smooth" in e:
                lines.append(f'shape.smoothCorners={{"ids":[{sid}],'
                             f'"smoothing":{e.pop("smooth")}}}')
            if any(k in e for k in ("shadow", "shadowProps", "bevel", "softEdges",
                                    "glow", "glowProps", "threeD", "reflection",
                                    "reflectionProps")):
                params = {k: v for k, v in e.items() if k != "shape"}
                lines.append(f"shape.effects={json.dumps({'ids': [sid], **params})}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {BASE} ({BASE.stat().st_size} bytes), "
          f"{len(prs.slides)} slides, {len(lines)} DeckCraft commands")


def run_deckcraft() -> None:
    cli = Path(r"D:\artcraft\DeckCraft\deckcraft-cli.exe")
    if not cli.is_file():
        raise SystemExit("deckcraft-cli not found")
    cmd = [str(cli), "run", "--in", str(BASE), "--cmd-file", str(MANIFEST),
           "--save", str(EFFECTS)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise SystemExit(f"DeckCraft failed: {res.stderr}\n{res.stdout}")
    print(f"wrote {EFFECTS} ({EFFECTS.stat().st_size} bytes)")


def add_all_motion() -> None:
    prs = Presentation(str(EFFECTS))
    for idx, (style_id, slide) in enumerate(zip(BUILDERS, prs.slides)):
        tk = vs.resolve(vs.get(style_id))
        bounds = {s.name: s.shape_id for s in slide.shapes}
        add_motion(slide, style_id, tk, bounds)
    prs.save(str(FINAL))
    print(f"wrote {FINAL} ({FINAL.stat().st_size} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--motion", action="store_true")
    ap.add_argument("--skip-effects", action="store_true")
    ns = ap.parse_args()
    if ns.motion:
        add_all_motion()
        return 0
    build_base()
    if not ns.skip_effects:
        run_deckcraft()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
