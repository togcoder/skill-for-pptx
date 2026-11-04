#!/usr/bin/env python3
"""Build the T067 image-choreography variants (cover + "Một dòng chảy").

Two files, same layout, one variable: WHEN the images appear.

  A  identity anchors present at t=0; the title animates over them.
  B  the title lands first; each image enters on the beat that names it.

The layout is T066's art direction (same palette, type, circle assets) with
three corrections that are identical in both variants, so they cannot explain
a difference in reading:
  1. a portrait is one atomic unit (gold ring + face), never an empty ring
     waiting for its picture;
  2. the "flow" slide separates the people axis (portrait + lifespan) from the
     work axis (date + work + author on the spine), so the rows cannot
     contradict each other;
  3. the 2+1 argument of the speaker notes (two founders, then Lenin) becomes
     the composition: a pair on the red field, one figure in the deep panel.

Run:  python experiments/T067-.../inputs/build_variants.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import pptx_animator as anim  # noqa: E402

HERE = Path(__file__).resolve().parent
T066_ASSETS = (ROOT / "experiments" / "T066-20261104-opencode-triet-hoc-ch1"
               / "inputs" / "assets")
OUT_DIR = HERE.parent / "artifacts"

W, H = 13.333, 7.5
RED = RGBColor(0xC1, 0x12, 0x1F)
DEEP = RGBColor(0x7A, 0x0C, 0x14)
INK = RGBColor(0x1A, 0x05, 0x08)
CREAM = RGBColor(0xF7, 0xF1, 0xE8)
GOLD = RGBColor(0xE8, 0xB0, 0x4B)
GOLD_TEXT = RGBColor(0xFF, 0xD9, 0x8A)
PINK = RGBColor(0xF2, 0xC9, 0xC9)
HEAD = "Palatino Linotype"
BODY = "Arial"

# ---------------------------------------------------------------- primitives


def bg(slide, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0,
                               prs.slide_width, prs.slide_height)
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.name = "!!bg"
    return s


def rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                               Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    if name:
        s.name = name
    return s


def circle(slide, x, y, d, fill=None, line=None, lw=1.2, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y),
                               Inches(d), Inches(d))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    if name:
        s.name = name
    return s


def tb(slide, x, y, w, h, lines, size=18, font=BODY, color=CREAM, bold=False,
       italic=False, align=PP_ALIGN.LEFT, spacing=1.0, name=None, spc=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    if isinstance(lines, str):
        lines = lines.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_before = Pt(0)
        p.space_after = Pt(0)
        r = p.add_run()
        r.text = line
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        if spc:
            r.font._element.set("spc", str(int(spc * 100)))
    if name:
        box.name = name
    return box


def line(slide, x1, y1, x2, y2, color, width=1.0, name=None):
    s = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1),
                                   Inches(y1), Inches(x2), Inches(y2))
    s.line.color.rgb = color
    s.line.width = Pt(width)
    if name:
        s.name = name
    return s


def thread(slide, x, y, w, h, horizontal=False):
    rect(slide, x, y, w, h, fill=GOLD, name="!!thread")
    if horizontal:
        circle(slide, x + w - 0.075, y - 0.06, 0.14, fill=CREAM, name="!!dot")
    else:
        circle(slide, x - 0.055, y - 0.06, 0.14, fill=CREAM, name="!!dot")


def portrait(slide, filename, x, y, d, name, ring_lw=1.1):
    """One image = face + rim, grouped so a frame can never outlive its picture."""
    ring = circle(slide, x - 0.055, y - 0.055, d + 0.11, fill=None,
                  line=GOLD, lw=ring_lw)
    pic = slide.shapes.add_picture(str(T066_ASSETS / filename), Inches(x),
                                   Inches(y), Inches(d), Inches(d))
    pic.name = name + "-pic"
    group = slide.shapes.add_group_shape([ring, pic])
    group.name = name
    return group


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def new_slide(color=RED):
    slide = prs.slides.add_slide(BLANK)
    bg(slide, color)
    return slide


# ---------------------------------------------------------------- slides


def cover(variant):
    s = new_slide(RED)
    rect(s, 8.55, 0, W - 8.55, H, fill=DEEP, name="!!panel")
    tb(s, 0.85, 0.62, 6.8, 0.4, "CHƯƠNG 1  ·  KHÁI LUẬN", size=10.5,
       color=GOLD_TEXT, bold=True, spc=1.6, name="kicker")
    tb(s, 0.78, 1.35, 7.5, 2.5, ["TRIẾT HỌC", "MÁC – LÊNIN"], size=63,
       font=HEAD, color=CREAM, bold=True, spacing=0.92, name="title")
    rect(s, 0.85, 4.38, 1.55, 0.045, fill=GOLD, name="rule")
    tb(s, 0.85, 4.68, 6.8, 0.9, ["Từ thế giới quan",
                                 "đến phương pháp luận"], size=21,
       color=CREAM, spacing=1.02, name="subtitle")
    tb(s, 0.85, 6.55, 6.8, 0.4,
       "Giáo trình Triết học Mác – Lênin  ·  Chương 1", size=9.5,
       color=CREAM, name="caption")

    # one atomic unit per person, named identically on every slide
    portrait(s, "marx-circle.png", 8.95, 0.55, 2.9, "!!marx")
    portrait(s, "engels-circle.png", 11.05, 2.25, 2.25, "!!engels")
    portrait(s, "lenin-circle.png", 9.15, 3.95, 2.75, "!!lenin")
    # the sentence that gives the three faces their names
    tb(s, 8.95, 6.98, 4.15, 0.3, "C. MÁC  ·  PH. ĂNGGHEN  ·  V.I. LÊNIN",
       size=9, color=GOLD_TEXT, bold=True, align=PP_ALIGN.RIGHT,
       name="portrait-plate", spc=1.2)
    thread(s, 8.38, 0.7, 0.035, 6.1)

    notes(s, "\n".join([
        "MỞ ĐẦU — ba chân dung đã ở trên màn hình khi khán giả bước vào: "
        "Mác, Ăngghen, Lênin. Không phải để tôn thờ; họ là ba mốc của một lý "
        "luận gắn với thực tiễn.",
        "[click 1] Chương 1 đặt câu hỏi nền tảng: triết học là gì?",
        "[click 2] Và triết học Mác – Lênin trả lời câu hỏi đó từ đâu? "
        "Tiêu đề này là tên của ba người đang đứng bên phải.",
        "[click 3] Từ thế giới quan đến phương pháp luận — đó là đường đi của "
        "cả chương.",
    ]))
    return s


def flow(variant):
    s = new_slide(RED)
    rect(s, 8.55, 0, W - 8.55, H, fill=DEEP, name="!!panel")
    tb(s, 0.85, 0.62, 8.0, 0.35, "BA MỐC", size=10.5, color=GOLD_TEXT,
       bold=True, spc=1.6, name="kicker")
    tb(s, 0.8, 1.0, 10.5, 1.1, "MỘT DÒNG CHẢY", size=40, font=HEAD,
       color=CREAM, bold=True, name="title")
    tb(s, 0.85, 1.9, 8.0, 0.4, "Từ lý luận đến cách mạng", size=13,
       color=GOLD_TEXT, name="sub")

    # people axis: portrait + lifespan only; works live on the spine
    tb(s, 1.55, 2.55, 6.0, 0.3, "HAI NGƯỜI ĐẶT NỀN · 1848 – 1895", size=9,
       color=GOLD_TEXT, bold=True, spc=1.4, name="founders-label")
    portrait(s, "marx-circle.png", 1.55, 2.95, 2.75, "!!marx")
    portrait(s, "engels-circle.png", 4.45, 2.95, 2.75, "!!engels")
    tb(s, 1.35, 5.83, 3.15, 0.3, "C. MÁC", size=11, color=CREAM, bold=True,
       align=PP_ALIGN.CENTER, name="!!marx-name")
    tb(s, 1.35, 6.11, 3.15, 0.25, "1818 – 1883", size=8.5, color=GOLD_TEXT,
       align=PP_ALIGN.CENTER, name="!!marx-date")
    tb(s, 4.25, 5.83, 3.15, 0.3, "PH. ĂNGGHEN", size=11, color=CREAM,
       bold=True, align=PP_ALIGN.CENTER, name="!!engels-name")
    tb(s, 4.25, 6.11, 3.15, 0.25, "1820 – 1895", size=8.5, color=GOLD_TEXT,
       align=PP_ALIGN.CENTER, name="!!engels-date")

    # the third act gets its own field, as on the cover
    tb(s, 8.85, 2.55, 4.1, 0.3, "NGƯỜI CHUYỂN THÀNH CÁCH MẠNG", size=9,
       color=GOLD_TEXT, bold=True, spc=1.4, name="lenin-label")
    portrait(s, "lenin-circle.png", 9.56, 2.95, 2.75, "!!lenin")
    tb(s, 9.36, 5.83, 3.15, 0.3, "V.I. LÊNIN", size=11, color=CREAM,
       bold=True, align=PP_ALIGN.CENTER, name="!!lenin-name")
    tb(s, 9.36, 6.11, 3.15, 0.25, "1870 – 1924", size=8.5, color=GOLD_TEXT,
       align=PP_ALIGN.CENTER, name="!!lenin-date")

    # work axis: the claim, drawn as one spine; each stop names its author
    line(s, 0.85, 6.65, 12.45, 6.65, GOLD, 1.2, name="timeline")
    for x, date, work in [(2.2, "1848", "Tuyên ngôn · Mác – Ăngghen"),
                          (6.4, "1867", "Tư bản · Mác"),
                          (10.9, "1917", "Cách mạng · Lênin")]:
        circle(s, x - 0.08, 6.57, 0.16, fill=CREAM, name=f"stop-{date}")
        tb(s, x - 1.2, 6.8, 2.4, 0.26, date, size=9.5, color=GOLD_TEXT,
           bold=True, align=PP_ALIGN.CENTER, name=f"stop-{date}-date")
        tb(s, x - 1.2, 7.04, 2.4, 0.24, work, size=8.5, color=CREAM,
           align=PP_ALIGN.CENTER, name=f"stop-{date}-work")
    thread(s, 0.45, 0.8, 0.035, 5.2)

    notes(s, "\n".join([
        "MỘT DÒNG CHẢY — không phải ba chân dung ngang hàng, mà hai người đặt "
        "nền và một người chuyển lý luận thành cách mạng.",
        "[click 1] Ba mốc: 1848, 1867, 1917.",
        "[click 2] Trước hết là cái trục — một dòng chảy từ lý luận đến cách "
        "mạng, không phải ba mẩu rời.",
        "[click 3] 1848: Tuyên ngôn Đảng Cộng sản, của Mác và Ăngghen. Hai "
        "chân dung này là hai người đặt nền.",
        "[click 4] 1867: bộ Tư bản. Vẫn chính những con người đó; lý luận đi "
        "tiếp, không cần gương mặt mới.",
        "[click 5] 1917: Cách mạng Tháng Mười. Lênin — người chuyển lý luận "
        "thành hành động trong một thời đại khác.",
    ]))
    return s


# ---------------------------------------------------------------- timing


def ids_of(slide):
    return {sh.name: str(sh.shape_id) for sh in slide.shapes if sh.name}


def build(variant):
    deck = Presentation()
    deck.slide_width = Inches(W)
    deck.slide_height = Inches(H)
    global prs, BLANK
    prs, BLANK = deck, deck.slide_layouts[6]

    s1, s2 = cover(variant), flow(variant)
    for idx, slide in enumerate((s1, s2), 1):
        ids = ids_of(slide)

        def eff(name, preset, trigger="click", dur=500, delay=0):
            return {"spid": ids[name], "preset": preset, "trigger": trigger,
                    "duration_ms": dur, "delay_ms": delay}

        if idx == 1 and variant == "A":
            clicks = [
                {"id": "c1", "start": "click", "effects": [eff("kicker", "fade", dur=400)]},
                {"id": "c2", "start": "click", "effects": [
                    eff("title", "wipe-up", dur=700),
                    eff("rule", "wipe-left", "with", dur=700)]},
                {"id": "c3", "start": "click", "effects": [
                    eff("subtitle", "fade", dur=600),
                    eff("caption", "fade", "with", dur=500),
                    eff("!!thread", "wipe-down", "with", dur=700),
                    eff("!!dot", "zoom", "with", dur=500)]},
            ]
        elif idx == 1 and variant == "B":
            clicks = [
                {"id": "c1", "start": "click", "effects": [eff("kicker", "fade", dur=400)]},
                {"id": "c2", "start": "click", "effects": [
                    eff("title", "wipe-up", dur=700),
                    eff("rule", "wipe-left", "with", dur=700),
                    eff("!!panel", "fade", "with", dur=600, delay=350),
                    eff("!!marx", "zoom", "with", dur=650, delay=350),
                    eff("!!engels", "zoom", "with", dur=650, delay=470),
                    eff("!!lenin", "zoom", "with", dur=650, delay=590),
                    eff("portrait-plate", "fade", "with", dur=450, delay=650)]},
                {"id": "c3", "start": "click", "effects": [
                    eff("subtitle", "fade", dur=600),
                    eff("caption", "fade", "with", dur=500),
                    eff("!!thread", "wipe-down", "with", dur=700),
                    eff("!!dot", "zoom", "with", dur=500)]},
            ]
        elif idx == 2 and variant == "A":
            clicks = [
                {"id": "c1", "start": "click", "effects": [
                    eff("kicker", "fade", dur=400),
                    eff("title", "wipe-up", "with", dur=700),
                    eff("sub", "fade", "with", dur=600)]},
                {"id": "c2", "start": "click", "effects": [
                    eff("stop-1848-work", "fade", dur=450),
                    eff("stop-1848", "pulse", "with", dur=450),
                    eff("stop-1848-date", "pulse", "with", dur=450)]},
                {"id": "c3", "start": "click", "effects": [
                    eff("stop-1867-work", "fade", dur=450),
                    eff("stop-1867", "pulse", "with", dur=450),
                    eff("stop-1867-date", "pulse", "with", dur=450)]},
                {"id": "c4", "start": "click", "effects": [
                    eff("stop-1917-work", "fade", dur=450),
                    eff("stop-1917", "pulse", "with", dur=450),
                    eff("stop-1917-date", "pulse", "with", dur=450)]},
            ]
        else:  # flow, B
            clicks = [
                {"id": "c1", "start": "click", "effects": [
                    eff("kicker", "fade", dur=400),
                    eff("title", "wipe-up", "with", dur=700),
                    eff("sub", "fade", "with", dur=600)]},
                {"id": "c2", "start": "click", "effects": [
                    eff("timeline", "wipe-left", dur=700)]},
                {"id": "c3", "start": "click", "effects": [
                    eff("stop-1848", "zoom", dur=450),
                    eff("stop-1848-date", "fade", "with", dur=400),
                    eff("stop-1848-work", "fade", "with", dur=400),
                    eff("!!marx", "zoom", "with", dur=650, delay=100),
                    eff("!!engels", "zoom", "with", dur=650, delay=220),
                    eff("founders-label", "fade", "with", dur=450, delay=160),
                    eff("!!marx-name", "fade", "with", dur=400, delay=300),
                    eff("!!marx-date", "fade", "with", dur=400, delay=300),
                    eff("!!engels-name", "fade", "with", dur=400, delay=300),
                    eff("!!engels-date", "fade", "with", dur=400, delay=300)]},
                {"id": "c4", "start": "click", "effects": [
                    eff("stop-1867", "zoom", dur=450),
                    eff("stop-1867-date", "fade", "with", dur=400),
                    eff("stop-1867-work", "fade", "with", dur=400)]},
                {"id": "c5", "start": "click", "effects": [
                    eff("!!panel", "fade", dur=600),
                    eff("stop-1917", "zoom", "with", dur=450),
                    eff("stop-1917-date", "fade", "with", dur=400),
                    eff("stop-1917-work", "fade", "with", dur=400),
                    eff("!!lenin", "zoom", "with", dur=650, delay=150),
                    eff("lenin-label", "fade", "with", dur=450, delay=200),
                    eff("!!lenin-name", "fade", "with", dur=400, delay=340),
                    eff("!!lenin-date", "fade", "with", dur=400, delay=340)]},
            ]

        anim.apply_timeline(slide._element, clicks, mode="replace")

    out = OUT_DIR / f"T067-variant-{variant}-cover-flow.pptx"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    deck.save(str(out))
    print("wrote", out, "slides", len(deck.slides), "bytes", out.stat().st_size)
    return out


if __name__ == "__main__":
    for v in ("A", "B"):
        build(v)
