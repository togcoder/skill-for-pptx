"""T069 builder: turn the T067 directed copy into a state-pair deck.

Adds four B-states (3B, 4B, 6B, 9B) reached by native Morph, strips the
sequential clicks that the Morph makes redundant, and leaves one dim lifecycle.

Run from the T069 worktree:
  python experiments/T069-20261104-opencode-directed-deck/inputs/build_directed_deck.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import morph_studio as mstu  # noqa: E402
import pptx_animator as anim  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import PP_ALIGN  # noqa: E402
from pptx.oxml.ns import qn  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402

BASE = ROOT / "experiments/T069-20261104-opencode-directed-deck"
SRC = BASE / "inputs/T066-deck-directed.pptx"
TMP = BASE / "artifacts/.build-tmp.pptx"
OUT = BASE / "artifacts/T069-directed-morph.pptx"

BG = "C1121F"
DARK = "7A0C14"
CREAM = "F7F1E8"
PINK = "F2C9C9"
GOLD = "E8B04B"
LIGHT_GOLD = "FFD98A"
PALATINO = "Palatino Linotype"
SANS = "Arial"

# source slides whose timing is replaced by a poster base state
STRIP = [1, 3, 4, 6, 9]
# insertion order matters: later slides first, so earlier indices remain stable
DUPLICATE = [9, 6, 4, 3]


def set_box(shape, x, y, w, h):
    shape.left = Inches(x)
    shape.top = Inches(y)
    shape.width = Inches(w)
    shape.height = Inches(h)


def set_text(shape, text, size, color, bold=False, font=SANS, align=PP_ALIGN.LEFT,
             italic=False, spacing=1.0):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.name = font
        run.font.color.rgb = RGBColor.from_string(color)


def add_alpha(srgb, alpha):
    for old in srgb.findall(qn("a:alpha")):
        srgb.remove(old)
    node = srgb.makeelement(qn("a:alpha"), {"val": str(int(alpha * 100000))})
    srgb.append(node)


def set_fill(shape, color, alpha=None):
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(color)
    if alpha is not None:
        srgb = shape.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
        add_alpha(srgb, alpha)


def no_fill(shape):
    shape.fill.background()


def dim(shape, alpha=0.28):
    """Lower fill and text contrast without changing geometry (Morph still pairs)."""
    try:
        if shape.fill.type is not None and shape.fill.type != 5:
            srgb = shape.fill._xPr.find(qn("a:solidFill"))
            if srgb is not None:
                clr = srgb.find(qn("a:srgbClr"))
                if clr is not None:
                    add_alpha(clr, alpha)
    except Exception:
        pass
    if shape.has_text_frame:
        for p in shape.text_frame.paragraphs:
            for run in p.runs:
                rPr = run._r.get_or_add_rPr()
                fill = rPr.find(qn("a:solidFill"))
                if fill is not None:
                    clr = fill.find(qn("a:srgbClr"))
                    if clr is not None:
                        add_alpha(clr, max(alpha, 0.45))


def by_name(slide, name):
    for shape in slide.shapes:
        if shape.name == name:
            return shape
    raise KeyError(f"{name} not on slide")


def rename_pair(slides, mapping):
    for slide in slides:
        for old, new in mapping.items():
            by_name(slide, old).name = new


def remove(slide, name):
    shape = by_name(slide, name)
    shape._element.getparent().remove(shape._element)


def add_text(slide, x, y, w, h, text, size, color, bold=False, font=SANS,
             align=PP_ALIGN.LEFT, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    set_text(box, text, size, color, bold=bold, font=font, align=align, italic=italic)
    return box


def add_ring(slide, x, y, w, h, color=GOLD, width=1.5):
    ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    no_fill(ring)
    ring.line.color.rgb = RGBColor.from_string(color)
    ring.line.width = Pt(width)
    return ring


def strip_timing(pkg, part):
    root = pkg.xml(part)
    timing = root.find(f"{{{mstu.P}}}timing")
    if timing is not None:
        root.remove(timing)
    pkg.put(part, root)


# ---------------------------------------------------------------------------
# 1. Duplicate the B states (after stripping timing so the whole poster copies)

pkg = mstu.Package(str(SRC))
parts = pkg.slides()
for idx in STRIP:
    strip_timing(pkg, parts[idx - 1])

parts = pkg.slides()
for idx in DUPLICATE:
    pkg.duplicate_slide(parts[idx - 1], parts[idx - 1],
                        f"T069 state-pair B for slide {idx}")
pkg.save(str(TMP))

# ---------------------------------------------------------------------------
# 2. Transform the B states

prs = Presentation(str(TMP))
# order: 1,2,3,3B,4,4B,5,6,6B,7,8,9,9B,10
s3, s3b = prs.slides[2], prs.slides[3]
s4, s4b = prs.slides[4], prs.slides[5]
s6, s6b = prs.slides[7], prs.slides[8]
s9, s9b = prs.slides[11], prs.slides[12]

# --- 4 base: keep both views legible, give the circle room above the cards --
set_box(by_name(s4, "dialectic-circle"), 1.10, 2.45, 3.10, 3.10)
set_box(by_name(s4, "dialectic-core"), 1.85, 3.20, 1.50, 1.50)
set_box(by_name(s4, "dialectic-arrow"), 1.55, 2.90, 1.65, 1.65)
for name, y in [("dialectic-card", 5.45), ("dialectic-name", 5.58),
                ("dialectic-desc", 5.90), ("meta-card", 5.45),
                ("meta-name", 5.58), ("meta-desc", 5.90)]:
    sh = by_name(s4, name)
    sh.top = Inches(y)

# --- 3B: matter wins -------------------------------------------------------
rename_pair([s3, s3b], {
    "title": "!!m3-title", "kicker": "!!m3-kicker",
    "left": "!!m3-left", "left-title": "!!m3-left-title",
    "left-body": "!!m3-left-body", "left-foot": "!!m3-left-foot",
    "right": "!!m3-right", "right-title": "!!m3-right-title",
    "right-body": "!!m3-right-body", "right-foot": "!!m3-right-foot",
    "qmark": "!!m3-qmark", "qline": "!!m3-qline", "qcap": "!!m3-qcap",
})
set_text(by_name(s3b, "!!m3-title"), "VẬT CHẤT\nQUYẾT ĐỊNH", 34, CREAM, bold=True, font=PALATINO)
set_text(by_name(s3b, "!!m3-kicker"), "CÂU TRẢ LỜI", 11, LIGHT_GOLD, bold=True)
# winner: cream card, red type
left = by_name(s3b, "!!m3-left")
set_box(left, 0.85, 2.35, 5.95, 3.75)
set_fill(left, CREAM)
set_text(by_name(s3b, "!!m3-left-title"), "VẬT CHẤT", 30, BG, bold=True, font=PALATINO)
set_text(by_name(s3b, "!!m3-left-body"), "Cái có trước.\nQuyết định.", 16, DARK, font=SANS)
set_text(by_name(s3b, "!!m3-left-foot"), "BẢN THỂ LUẬN", 10, BG, bold=True)
# loser: dark card, dim type
right = by_name(s3b, "!!m3-right")
set_box(right, 8.05, 2.95, 4.05, 2.75)
set_fill(right, DARK)
set_text(by_name(s3b, "!!m3-right-title"), "Ý THỨC", 18, PINK, bold=True, font=PALATINO)
set_text(by_name(s3b, "!!m3-right-body"), "Cái có sau.\nPhản ánh.", 10.5, PINK, font=SANS)
set_text(by_name(s3b, "!!m3-right-foot"), "NHẬN THỨC LUẬN", 8, LIGHT_GOLD, bold=True)
set_box(by_name(s3b, "!!m3-right-title"), 8.3, 3.1, 3.4, 0.4)
set_box(by_name(s3b, "!!m3-right-body"), 8.3, 3.6, 3.4, 0.75)
set_box(by_name(s3b, "!!m3-right-foot"), 8.3, 5.05, 3.4, 0.3)
dim(by_name(s3b, "!!m3-right"), 0.30)
# the question mark becomes a check
set_text(by_name(s3b, "!!m3-qmark"), "✓", 46, LIGHT_GOLD, bold=True, font=PALATINO,
         align=PP_ALIGN.CENTER)
set_box(by_name(s3b, "!!m3-qmark"), 6.95, 2.15, 0.95, 0.95)
qline = by_name(s3b, "!!m3-qline")
set_box(qline, 6.85, 3.15, 1.15, 0)
qline.line.color.rgb = RGBColor.from_string(GOLD)
set_text(by_name(s3b, "!!m3-qcap"), "ĐÚNG", 9.5, LIGHT_GOLD, bold=True,
         align=PP_ALIGN.CENTER)
set_box(by_name(s3b, "!!m3-qcap"), 6.85, 3.35, 0.9, 0.3)
add_text(s3b, 0.85, 6.45, 11.7, 0.4,
         "Ý thức phản ánh thế giới vật chất.",
         12, LIGHT_GOLD, italic=True)

# --- 4B: the dialectic view wins ------------------------------------------
rename_pair([s4, s4b], {
    "title": "!!m4-title", "kicker": "!!m4-kicker",
    "dialectic-circle": "!!m4-circle", "dialectic-core": "!!m4-core",
    "dialectic-arrow": "!!m4-arrow", "dialectic-card": "!!m4-card",
    "dialectic-name": "!!m4-name", "dialectic-desc": "!!m4-desc",
    "straight-line": "!!m4-line", "straight-label": "!!m4-label",
    "straight-dot-8.35": "!!m4-dot0", "straight-dot-9.95": "!!m4-dot1",
    "straight-dot-11.55": "!!m4-dot2",
    "meta-card": "!!m4-meta", "meta-name": "!!m4-meta-name",
    "meta-desc": "!!m4-meta-desc",
})
set_text(by_name(s4b, "!!m4-title"), "BIỆN CHỨNG", 40, BG, bold=True, font=PALATINO)
set_text(by_name(s4b, "!!m4-kicker"), "CÁCH NHÌN ĐÚNG", 11, DARK, bold=True)
set_box(by_name(s4b, "!!m4-circle"), 0.95, 2.50, 3.90, 3.90)
set_box(by_name(s4b, "!!m4-core"), 2.25, 3.55, 1.35, 1.35)
set_box(by_name(s4b, "!!m4-arrow"), 1.85, 3.15, 1.60, 1.60)
card = by_name(s4b, "!!m4-card")
set_box(card, 4.95, 3.00, 7.55, 1.05)
set_fill(card, BG)
set_text(by_name(s4b, "!!m4-name"), "BIỆN CHỨNG", 17, CREAM, bold=True, font=PALATINO)
set_text(by_name(s4b, "!!m4-desc"), "Sự vật trong liên hệ, vận động, phát triển.", 11.5, CREAM)
set_box(by_name(s4b, "!!m4-name"), 5.20, 3.12, 4.2, 0.35)
set_box(by_name(s4b, "!!m4-desc"), 5.20, 3.50, 7.0, 0.35)
# the losing view becomes a small, quiet inset
set_box(by_name(s4b, "!!m4-line"), 9.35, 2.45, 2.30, 0)
for i, name in enumerate(["!!m4-dot0", "!!m4-dot1", "!!m4-dot2"]):
    set_box(by_name(s4b, name), 9.35 + i * 1.0, 2.37, 0.16, 0.16)
set_text(by_name(s4b, "!!m4-label"), "TÁCH RỜI / BẤT BIẾN", 8, DARK, bold=True)
set_box(by_name(s4b, "!!m4-label"), 9.25, 2.65, 2.7, 0.35)
set_box(by_name(s4b, "!!m4-meta"), 4.95, 5.85, 7.55, 0.95)
set_text(by_name(s4b, "!!m4-meta-name"), "SIÊU HÌNH", 13, DARK, bold=True, font=PALATINO)
set_text(by_name(s4b, "!!m4-meta-desc"), "Cô lập, tĩnh tại, phiến diện.", 9.5, DARK)
set_box(by_name(s4b, "!!m4-meta-name"), 5.20, 5.95, 4.2, 0.35)
set_box(by_name(s4b, "!!m4-meta-desc"), 5.20, 6.30, 7.0, 0.35)
for name in ["!!m4-line", "!!m4-dot0", "!!m4-dot1", "!!m4-dot2",
             "!!m4-label", "!!m4-meta", "!!m4-meta-name", "!!m4-meta-desc"]:
    dim(by_name(s4b, name), 0.25)

# --- 6B: three parts become one whole -------------------------------------
rename_pair([s6, s6b], {
    "title": "!!m6-title", "kicker": "!!m6-kicker", "sub": "!!m6-sub",
    "part0": "!!m6-p0", "part0-n": "!!m6-p0n", "part0-h": "!!m6-p0h", "part0-b": "!!m6-p0b",
    "part1": "!!m6-p1", "part1-n": "!!m6-p1n", "part1-h": "!!m6-p1h", "part1-b": "!!m6-p1b",
    "part2": "!!m6-p2", "part2-n": "!!m6-p2n", "part2-h": "!!m6-p2h", "part2-b": "!!m6-p2b",
    "note": "!!m6-note", "arrow1": "!!m6-a1", "arrow2": "!!m6-a2",
})
set_text(by_name(s6b, "!!m6-title"), "MỘT CHỈNH THỂ", 40, BG, bold=True, font=PALATINO)
set_text(by_name(s6b, "!!m6-kicker"), "CẤU TRÚC", 11, BG, bold=True)
for slide in (s6, s6b):
    set_text(by_name(slide, "!!m6-sub"), "Một học thuyết", 13, DARK)
    set_text(by_name(slide, "!!m6-p0b"), "Duy vật biện chứng,\nduy vật lịch sử", 11, CREAM)
    set_text(by_name(slide, "!!m6-p1b"), "Phương thức sản xuất", 11, PINK)
    set_text(by_name(slide, "!!m6-p2h"), "CNXH KHOA HỌC", 15, DARK, bold=True, font=PALATINO)
    set_text(by_name(slide, "!!m6-p2b"), "Con đường cách mạng", 11, DARK)
    remove(slide, "!!m6-note")
# triangle: two on top, one below
set_box(by_name(s6b, "!!m6-p0"), 0.85, 2.30, 3.55, 1.95)
set_box(by_name(s6b, "!!m6-p0n"), 1.07, 2.48, 0.8, 0.35)
set_box(by_name(s6b, "!!m6-p0h"), 1.07, 2.83, 3.1, 0.85)
set_box(by_name(s6b, "!!m6-p0b"), 1.07, 3.70, 3.05, 0.5)
set_box(by_name(s6b, "!!m6-p2"), 8.95, 2.30, 3.55, 1.95)
set_box(by_name(s6b, "!!m6-p2n"), 9.17, 2.48, 0.8, 0.35)
set_box(by_name(s6b, "!!m6-p2h"), 9.17, 2.83, 3.1, 0.85)
set_box(by_name(s6b, "!!m6-p2b"), 9.17, 3.70, 3.05, 0.5)
set_box(by_name(s6b, "!!m6-p1"), 4.90, 4.55, 3.55, 1.75)
set_box(by_name(s6b, "!!m6-p1n"), 5.12, 4.73, 0.8, 0.35)
set_box(by_name(s6b, "!!m6-p1h"), 5.12, 5.08, 3.1, 0.75)
set_box(by_name(s6b, "!!m6-p1b"), 5.12, 5.82, 3.05, 0.4)
# a single ring in the middle names the whole
add_ring(s6b, 4.65, 2.55, 2.6, 1.55, color=BG, width=1.25)
add_text(s6b, 4.75, 2.80, 2.4, 1.0, "MỘT\nCHỈNH THỂ", 17, BG, bold=True,
         font=PALATINO, align=PP_ALIGN.CENTER)
remove(s6b, "!!m6-a1")
remove(s6b, "!!m6-a2")

# --- 9B: the thesis lands --------------------------------------------------
rename_pair([s9, s9b], {
    "quote-mark": "!!m9-mark", "quote0": "!!m9-q0", "quote1": "!!m9-q1",
    "quote2": "!!m9-q2", "quote-rule": "!!m9-rule", "author": "!!m9-author",
    "kicker": "!!m9-kicker",
})
set_text(by_name(s9b, "!!m9-kicker"), "HÀNH ĐỘNG", 11, GOLD, bold=True)
set_box(by_name(s9b, "!!m9-mark"), 0.85, 0.85, 1.0, 1.0)
set_text(by_name(s9b, "!!m9-mark"), "“", 60, GOLD, bold=True, font=PALATINO)
set_text(by_name(s9b, "!!m9-q0"), "Các nhà triết học chỉ giải thích", 13, PINK, italic=True)
set_text(by_name(s9b, "!!m9-q1"), "thế giới bằng nhiều cách khác nhau;", 13, PINK, italic=True)
set_text(by_name(s9b, "!!m9-q2"), "vấn đề là cải tạo thế giới.", 13, PINK, italic=True)
for name, y in [("!!m9-q0", 1.05), ("!!m9-q1", 1.42), ("!!m9-q2", 1.79)]:
    set_box(by_name(s9b, name), 1.95, y, 8.6, 0.4)
set_box(by_name(s9b, "!!m9-rule"), 1.95, 2.45, 4.0, 0)
set_box(by_name(s9b, "!!m9-author"), 1.95, 2.62, 8.4, 0.35)
set_text(by_name(s9b, "!!m9-author"), "C. Mác · 1845", 9, GOLD)
add_text(s9b, 0.95, 3.55, 11.4, 1.9, "CẢI TẠO\nTHẾ GIỚI", 54, CREAM, bold=True,
         font=PALATINO)
add_text(s9b, 1.0, 5.85, 11.3, 0.5, "Giải thích để cải tạo.",
         16, LIGHT_GOLD, italic=True)

# --- 8 base: four functions, one line each --------------------------------
s8 = prs.slides[10]
for name, text in [
    ("tile0-b", "Nhìn thế giới có quy luật."),
    ("tile1-b", "Cách đặt vấn đề, hành động."),
    ("tile2-b", "Phê phán cái lỗi thời."),
    ("tile3-b", "Phương pháp của khoa học."),
]:
    set_text(by_name(s8, name), text, 11, DARK)

# --- 7 timeline: portraits and dates in the order of the works -------------
s7 = prs.slides[9]
marx_ring = by_name(s7, "marx-ring").left
engels_ring = by_name(s7, "engels-ring").left
delta = engels_ring - marx_ring
for name in ["marx-ring", "marx", "marx-date", "marx-name", "marx-desc"]:
    sh = by_name(s7, name)
    sh.left = sh.left + delta
for name in ["engels-ring", "engels", "engels-date", "engels-name", "engels-desc"]:
    sh = by_name(s7, name)
    sh.left = sh.left - delta
# timeline dots under the work each portrait carries (1848 Engels, 1867 Marx, 1917 Lenin)
for name, center in [("tl-1848", 2.20), ("tl-1867", 6.60), ("tl-1917", 11.05)]:
    by_name(s7, name).left = Inches(center - 0.07)
for name, center in [("tl-1848-t", 2.20), ("tl-1867-t", 6.60), ("tl-1917-t", 11.05)]:
    by_name(s7, name).left = Inches(center - 0.30)

# --- 10 closing: one short line per take ----------------------------------
s10 = prs.slides[13]
for name, text in [
    ("take0-b", "Vật chất hay ý thức?"),
    ("take1-b", "Liên hệ, vận động, mâu thuẫn."),
    ("take2-b", "Giải thích để cải tạo."),
]:
    set_text(by_name(s10, name), text, 11, DARK)
set_text(by_name(s10, "closing"), "Học cách đặt câu hỏi đúng.", 26, BG, italic=True,
         font=PALATINO)
set_text(by_name(s10, "credits"), "Wikimedia · CC0", 8, DARK)

# --- one type scale: 9 / 12 / 16 / 24 / 36 / 54 pt -------------------------
def snap_size(pt: float) -> int:
    if pt <= 13:
        return 12
    if pt <= 20:
        return 16
    if pt <= 30:
        return 24
    if pt <= 48:
        return 36
    return 54


for slide in prs.slides:
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                if run.font.size is not None:
                    run.font.size = Pt(snap_size(run.font.size.pt))

prs.save(str(TMP))

# ---------------------------------------------------------------------------
# 3. Morph transitions on the B slides + one lifecycle dim on slide 11 (orig 8)

pkg = mstu.Package(str(TMP))
parts = pkg.slides()

# closing summary: all three takes + thesis are readable at t=0
strip_timing(pkg, parts[13])

# timeline slide: names/dates are the poster; one click draws the order
root = pkg.xml(parts[9])
ids = {}
for spid, node in anim.top_level_objects(root).items():
    prop = node.find("./*/" + qn("p:cNvPr"))
    if prop is not None:
        ids[prop.get("name")] = spid
names = ["timeline", "tl-1848", "tl-1848-t", "tl-1867", "tl-1867-t",
         "tl-1917", "tl-1917-t"]
clicks = [{
    "id": "t069.timeline",
    "start": "click",
    "effects": [
        {"preset": "fade", "trigger": "click" if i == 0 else "with",
         "duration_ms": 350, "spid": ids[name]}
        for i, name in enumerate(names)
    ],
}]
anim.apply_timeline(root, clicks, mode="replace")
pkg.put(parts[9], root)

# functions slide: four tiles are the poster; one click dims the first three
root = pkg.xml(parts[10])
ids = {}
for spid, node in anim.top_level_objects(root).items():
    prop = node.find("./*/" + qn("p:cNvPr"))
    if prop is not None:
        ids[prop.get("name")] = spid
clicks = [{
    "id": "t069.focus-science",
    "start": "click",
    "effects": [
        {"preset": "dim", "trigger": "click" if i == 0 else "with",
         "duration_ms": 400, "spid": ids[name], "opacity": 0.32}
        for i, name in enumerate(["tile0", "tile1", "tile2"])
    ],
}]
anim.apply_timeline(root, clicks, mode="replace")
pkg.put(parts[10], root)

for idx in [4, 6, 9, 13]:
    root = pkg.xml(parts[idx - 1])
    for tr in root.findall(f"{{{anim.P}}}transition"):
        root.remove(tr)
    for alt in root.findall(f"{{{anim.MC}}}AlternateContent"):
        if alt.find(f".//{{{anim.P}}}transition") is not None:
            root.remove(alt)
    mstu._set_transition(root, "byObject", 1200)
    pkg.put(parts[idx - 1], root)

pkg.save(str(OUT))
print("wrote", OUT, OUT.stat().st_size, "bytes")
