#!/usr/bin/env python3
"""Build the T066 Chapter 1 deck — native shapes, cut-out portraits, Morph."""
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
ASSETS = HERE / "assets"
OUT = HERE.parent / "artifacts" / "T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx"

W, H = 13.333, 7.5
RED = RGBColor(0xC1, 0x12, 0x1F)
DEEP = RGBColor(0x7A, 0x0C, 0x14)
INK = RGBColor(0x1A, 0x05, 0x08)
CREAM = RGBColor(0xF7, 0xF1, 0xE8)
GOLD = RGBColor(0xE8, 0xB0, 0x4B)
GOLD_TEXT = RGBColor(0xFF, 0xD9, 0x8A)
PINK = RGBColor(0xF2, 0xC9, 0xC9)
MUTED = RGBColor(0xE7, 0xC9, 0xC4)

HEAD = "Palatino Linotype"
BODY = "Arial"

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


def c(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


def bg(slide, color: RGBColor):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.name = "!!bg"
    return s


def rect(slide, x, y, w, h, fill=None, line=None, lw=1.0, radius=None, name=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius is not None else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
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
    if radius is not None:
        try:
            s.adjustments[0] = radius
        except Exception:
            pass
    if name:
        s.name = name
    return s


def circle(slide, x, y, d, fill=None, line=None, lw=1.2, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
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
       italic=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0,
       after=0, name=None, spc=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(lines, str):
        lines = lines.split("\n")
    else:
        lines = [part for line in lines for part in line.split("\n")]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_before = Pt(0)
        p.space_after = Pt(after)
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


def pic(slide, filename, x, y, w, h, name=None):
    box = slide.shapes.add_picture(str(ASSETS / filename), Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        box.name = name
    return box


def line(slide, x1, y1, x2, y2, color, width=1.0, dash=None, name=None):
    s = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    s.line.color.rgb = color
    s.line.width = Pt(width)
    if dash is not None:
        s.line.dash_style = dash
    if name:
        s.name = name
    return s


def thread(slide, x, y, w, h, horizontal=False):
    """The continuous gold thread; same names on every slide for Morph."""
    rect(slide, x, y, w, h, fill=GOLD, name="!!thread")
    if horizontal:
        circle(slide, x + w - 0.09, y - 0.075, 0.15, fill=CREAM, name="!!dot")
    else:
        circle(slide, x - 0.06, y - 0.06, 0.15, fill=CREAM, name="!!dot")


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def new_slide(color=RED):
    slide = prs.slides.add_slide(BLANK)
    bg(slide, color)
    return slide


# ---------------------------------------------------------------- 1 cover
s = new_slide(RED)
# a deeper vertical field behind the portraits
rect(s, 8.55, 0, W - 8.55, H, fill=DEEP, name="!!panel")
tb(s, 0.85, 0.62, 6.8, 0.4, "CHƯƠNG 1  ·  KHÁI LUẬN", size=10.5, color=GOLD_TEXT, bold=True, spc=1.6, name="kicker")
tb(s, 0.78, 1.35, 7.5, 2.5, ["TRIẾT HỌC", "MÁC – LÊNIN"], size=63, font=HEAD, color=CREAM, bold=True,
   spacing=0.92, name="title")
rect(s, 0.85, 4.38, 1.55, 0.045, fill=GOLD, name="rule")
tb(s, 0.85, 4.68, 6.8, 0.9, ["Từ thế giới quan", "đến phương pháp luận"], size=21, color=CREAM,
   spacing=1.02, name="subtitle")
tb(s, 0.85, 6.55, 6.8, 0.4, "Giáo trình Triết học Mác – Lênin  ·  Chương 1", size=9.5, color=CREAM, name="caption")
# portraits, overlapping like a constellation
for f, x, y, d, nm in [
    ("marx-circle.png", 8.95, 0.55, 2.9, "!!marx"),
    ("engels-circle.png", 11.05, 2.25, 2.25, "!!engels"),
    ("lenin-circle.png", 9.15, 3.95, 2.75, "!!lenin"),
]:
    circle(s, x - 0.06, y - 0.06, d + 0.12, fill=None, line=GOLD, lw=1.1, name=nm + "-ring")
    pic(s, f, x, y, d, d, name=nm)
thread(s, 8.38, 0.7, 0.035, 6.1)
notes(s, "Mở đầu: Chương 1 đặt câu hỏi nền tảng — triết học là gì, và triết học Mác – Lênin trả lời câu hỏi đó từ đâu? Ba chân dung không phải để tôn thờ; họ là ba mốc của một lý luận gắn với thực tiễn.")

# ---------------------------------------------------------------- 2 what is philosophy
s = new_slide(CREAM)
tb(s, 0.85, 0.62, 6.0, 0.35, "CÂU HỎI MỞ", size=10.5, color=RED, bold=True, spc=1.5, name="kicker")
tb(s, 0.8, 1.05, 6.4, 2.3, ["Triết học", "là gì?"], size=52, font=HEAD, color=RED, bold=True,
   spacing=0.94, name="title")
tb(s, 0.85, 3.45, 6.25, 1.1, "Một hệ thống tri thức lý luận chung nhất về thế giới và vị trí của con người trong thế giới ấy.", size=17, color=INK, spacing=1.12, name="def1")
tb(s, 0.85, 4.65, 6.25, 0.9, "Khoa học về những quy luật chung nhất của tự nhiên, xã hội và tư duy.", size=15, color=DEEP, spacing=1.12, name="def2")
# three labels
labels = [
    ("01", "THẾ GIỚI QUAN", "cách nhìn tổng thể"),
    ("02", "PHƯƠNG PHÁP LUẬN", "cách hành động"),
    ("03", "LOGIC BIỆN CHỨNG", "cách tư duy"),
]
for i, (n, head, sub) in enumerate(labels):
    x = 0.85 + i * 1.95
    rect(s, x, 5.55, 1.75, 0.035, fill=RED, name=f"l{i}-rule")
    tb(s, x, 5.7, 0.4, 0.32, n, size=9.5, color=RED, bold=True, name=f"l{i}-n")
    tb(s, x, 5.98, 1.78, 0.35, head, size=9, color=INK, bold=True, name=f"l{i}-h")
    tb(s, x, 6.28, 1.78, 0.35, sub, size=8.5, color=DEEP, name=f"l{i}-s")
# Plato on the right, dark red on cream
circle(s, 8.55, 1.35, 4.55, fill=RED, name="plato-disc")
pic(s, "plato-full.png", 8.95, 1.58, 3.75, 4.55, name="plato")
tb(s, 8.95, 6.35, 3.85, 0.35, "Tượng triết gia Hy Lạp · CC0", size=8.0, color=DEEP, align=PP_ALIGN.RIGHT, name="plato-cap")
thread(s, 0.85, 7.05, 11.7, 0.035, horizontal=True)
notes(s, "Định nghĩa không phải để học thuộc. Ba nhãn ở dưới là ba việc triết học làm: cho ta một thế giới quan, một phương pháp luận, và một logic để không tự lừa mình.")

# ---------------------------------------------------------------- 3 basic question
s = new_slide(RED)
tb(s, 0.85, 0.62, 8.0, 0.35, "VẤN ĐỀ CƠ BẢN", size=10.5, color=GOLD_TEXT, bold=True, spc=1.6, name="kicker")
tb(s, 0.8, 1.05, 9.5, 1.5, ["VẬT CHẤT", "HAY Ý THỨC?"], size=40, font=HEAD, color=CREAM, bold=True,
   spacing=0.94, name="title")
# two cards
rect(s, 0.85, 2.75, 4.75, 3.15, fill=DEEP, radius=0.04, name="left")
tb(s, 1.15, 3.0, 4.2, 0.7, "VẬT CHẤT", size=32, font=HEAD, color=CREAM, bold=True, name="left-title")
tb(s, 1.15, 3.85, 4.1, 1.2, ["Cái có trước.", "Quyết định ý thức."], size=16, color=PINK, spacing=1.12, name="left-body")
tb(s, 1.15, 5.25, 4.1, 0.4, "BẢN THỂ LUẬN", size=9, color=GOLD, bold=True, spc=1.2, name="left-foot")
rect(s, 7.25, 2.75, 4.75, 3.15, fill=CREAM, radius=0.04, name="right")
tb(s, 7.55, 3.0, 4.2, 0.7, "Ý THỨC", size=32, font=HEAD, color=RED, bold=True, name="right-title")
tb(s, 7.55, 3.85, 4.1, 1.2, ["Cái có sau.", "Phản ánh vật chất."], size=16, color=DEEP, spacing=1.12, name="right-body")
tb(s, 7.55, 5.25, 4.1, 0.4, "NHẬN THỨC LUẬN", size=9, color=RED, bold=True, spc=1.2, name="right-foot")
# the question mark between them
tb(s, 5.88, 3.25, 1.25, 1.4, "?", size=92, font=HEAD, color=GOLD, bold=True, align=PP_ALIGN.CENTER, name="qmark")
line(s, 5.95, 4.7, 6.95, 4.7, GOLD, 1.4, name="qline")
tb(s, 5.8, 4.9, 1.35, 0.5, "CÁI NÀO TRƯỚC?", size=8.0, color=GOLD_TEXT, bold=True, align=PP_ALIGN.CENTER, name="qcap")
thread(s, 12.6, 0.7, 0.035, 5.9)
notes(s, "Đây là câu hỏi nền tảng, không phải câu hỏi triết học duy nhất. Hai mặt của nó: bản thể luận (cái nào có trước) và nhận thức luận (con người có nhận thức được thế giới không).")

# ---------------------------------------------------------------- 4 dialectics / metaphysics
s = new_slide(CREAM)
tb(s, 0.85, 0.62, 6.5, 0.35, "HAI CÁCH NHÌN", size=10.5, color=RED, bold=True, spc=1.5, name="kicker")
tb(s, 0.8, 1.0, 8.0, 1.4, ["BIỆN CHỨNG", "HAY SIÊU HÌNH?"], size=38, font=HEAD, color=RED, bold=True,
   spacing=0.96, name="title")
# visual: a gold circular arrow vs a straight line
circle(s, 0.95, 2.55, 3.35, fill=None, line=RED, lw=3.0, name="dialectic-circle")
circle(s, 1.75, 3.35, 1.75, fill=GOLD, name="dialectic-core")
arrow = s.shapes.add_shape(MSO_SHAPE.CIRCULAR_ARROW, Inches(1.5), Inches(3.12), Inches(1.55), Inches(1.55))
arrow.fill.solid(); arrow.fill.fore_color.rgb = RED
arrow.line.fill.background(); arrow.name = "dialectic-arrow"
tb(s, 0.95, 5.95, 3.4, 0.4, "LIÊN HỆ · VẬN ĐỘNG · MÂU THUẪN", size=8.0, color=DEEP, bold=True, spc=0.8, name="dialectic-foot")
line(s, 8.35, 3.55, 11.55, 3.55, DEEP, 2.2, name="straight-line")
for x in (8.35, 9.95, 11.55):
    circle(s, x - 0.08, 3.47, 0.16, fill=DEEP, name=f"straight-dot-{x}")
tb(s, 8.35, 3.95, 3.3, 0.8, ["TÁCH RỜI", "BẤT BIẾN"], size=15, color=DEEP, bold=True, spacing=1.0, name="straight-label")
# two cards
rect(s, 0.85, 5.2, 5.6, 1.05, fill=RED, name="dialectic-card")
tb(s, 1.1, 5.35, 5.1, 0.35, "BIỆN CHỨNG", size=12, color=CREAM, bold=True, spc=1.2, name="dialectic-name")
tb(s, 1.1, 5.68, 5.1, 0.45, "Sự vật trong liên hệ, vận động, phát triển.", size=10.5, color=CREAM, name="dialectic-desc")
rect(s, 7.25, 5.2, 5.25, 1.05, fill=None, line=DEEP, lw=1.0, name="meta-card")
tb(s, 7.5, 5.35, 4.8, 0.35, "SIÊU HÌNH", size=12, color=DEEP, bold=True, spc=1.2, name="meta-name")
tb(s, 7.5, 5.68, 4.8, 0.45, "Sự vật cô lập, tĩnh tại, phiến diện.", size=10.5, color=DEEP, name="meta-desc")
thread(s, 0.85, 7.05, 11.65, 0.035, horizontal=True)
notes(s, "Biện chứng không phải 'mọi thứ đều thay đổi' một cách mơ hồ. Nó là cách xem xét trong chỉnh thể, có mâu thuẫn, có chuyển hóa. Siêu hình là cách xem xét tách rời, thường tiện cho kỹ thuật nhưng sai khi nhìn xã hội.")

# ---------------------------------------------------------------- 5 conditions
s = new_slide(RED)
tb(s, 0.85, 0.62, 8.0, 0.35, "BỐI CẢNH", size=10.5, color=GOLD_TEXT, bold=True, spc=1.6, name="kicker")
tb(s, 0.8, 1.0, 10.5, 1.2, "ĐIỀU KIỆN RA ĐỜI", size=40, font=HEAD, color=CREAM, bold=True, name="title")
tb(s, 0.85, 1.95, 8.0, 0.4, "Những năm 1840 · Tây Âu", size=13, color=GOLD_TEXT, name="sub")
cards = [
    ("KINH TẾ – XÃ HỘI", ["CNTB phát triển mạnh.", "Giai cấp vô sản xuất hiện."], DEEP, CREAM, PINK),
    ("KHOA HỌC TỰ NHIÊN", ["Tế bào · Bảo toàn năng lượng · Tiến hóa."], CREAM, RED, DEEP),
    ("TƯ TƯỞNG", ["Hegel · Feuerbach", "· XHCN không tưởng."], DEEP, CREAM, PINK),
]
for i, (head, body, fill, ink, body_color) in enumerate(cards):
    x = 0.85 + i * 4.08
    rect(s, x, 2.65, 3.75, 3.15, fill=fill, radius=0.04, name=f"card{i}")
    tb(s, x + 0.25, 2.9, 3.25, 0.5, f"0{i+1}", size=11, color=GOLD if fill == DEEP else RED, bold=True, name=f"card{i}-n")
    tb(s, x + 0.25, 3.25, 3.25, 0.8, head, size=14, color=ink, bold=True, spacing=0.98, name=f"card{i}-h")
    tb(s, x + 0.25, 3.95, 3.2, 1.45, body, size=12, color=body_color, spacing=1.12, name=f"card{i}-b")
# timeline
line(s, 0.85, 6.55, 12.35, 6.55, GOLD, 1.2, name="timeline")
circle(s, 0.95, 6.47, 0.16, fill=CREAM, name="timeline-dot")
tb(s, 1.2, 6.72, 3.5, 0.35, "1848 · Tuyên ngôn Đảng Cộng sản", size=9, color=CREAM, name="timeline-text")
thread(s, 0.45, 0.8, 0.035, 5.2)
notes(s, "Ba điều kiện không tách rời: một nền kinh tế đặt ra vấn đề, một nền khoa học đổi cách nhìn, một dòng tư tưởng để phê phán và kế thừa. Mác và Ăngghen không sáng tạo từ hư không.")

# ---------------------------------------------------------------- 6 three parts
s = new_slide(CREAM)
tb(s, 0.85, 0.62, 6.0, 0.35, "CẤU TRÚC", size=10.5, color=RED, bold=True, spc=1.5, name="kicker")
tb(s, 0.8, 1.0, 10.5, 1.25, "BA BỘ PHẬN", size=40, font=HEAD, color=RED, bold=True, name="title")
tb(s, 0.85, 1.95, 8.0, 0.45, "Cấu thành triết học Mác – Lênin", size=13, color=DEEP, name="sub")
parts = [
    ("01", "TRIẾT HỌC", "Duy vật biện chứng\nvà duy vật lịch sử", RED, CREAM),
    ("02", "KINH TẾ\nCHÍNH TRỊ", "Học thuyết về\nphương thức sản xuất", DEEP, CREAM),
    ("03", "CHỦ NGHĨA XÃ HỘI\nKHOA HỌC", "Con đường\nvà lực lượng cách mạng", GOLD, INK),
]
for i, (n, head, body, fill, ink) in enumerate(parts):
    x = 0.85 + i * 4.1
    rect(s, x, 2.65, 3.65, 2.65, fill=fill, radius=0.04, name=f"part{i}")
    tb(s, x + 0.25, 2.85, 0.8, 0.35, n, size=10, color=CREAM if fill != GOLD else INK, bold=True, name=f"part{i}-n")
    tb(s, x + 0.25, 3.2, 3.15, 0.9, head, size=15, color=ink, bold=True, spacing=0.95, name=f"part{i}-h")
    tb(s, x + 0.25, 4.4, 3.1, 0.65, body, size=10.5, color=ink, spacing=1.1, name=f"part{i}-b")
# connector arrows
line(s, 4.5, 3.95, 4.95, 3.95, GOLD, 1.5, name="arrow1")
line(s, 8.6, 3.95, 9.05, 3.95, GOLD, 1.5, name="arrow2")
tb(s, 0.85, 5.65, 11.7, 0.6, "Một chỉnh thể: triết học là nền tảng phương pháp; kinh tế chính trị là giải phẫu xã hội; CNXH khoa học là mục tiêu và con đường.", size=12, color=DEEP, name="note")
thread(s, 0.85, 7.05, 11.65, 0.035, horizontal=True)
notes(s, "Ba bộ phận không phải ba môn học rời. Triết học cho phương pháp; kinh tế chính trị chỉ ra quan hệ sản xuất; CNXH khoa học nói về con đường. Thiếu một cái, hệ thống mất tính nhất quán.")

# ---------------------------------------------------------------- 7 timeline of thinkers
s = new_slide(RED)
tb(s, 0.85, 0.62, 8.0, 0.35, "BA MỐC", size=10.5, color=GOLD_TEXT, bold=True, spc=1.6, name="kicker")
tb(s, 0.8, 1.0, 10.5, 1.1, "MỘT DÒNG CHẢY", size=40, font=HEAD, color=CREAM, bold=True, name="title")
tb(s, 0.85, 1.9, 8.0, 0.4, "Từ lý luận đến cách mạng", size=13, color=GOLD_TEXT, name="sub")
# portraits
for f, x, y, d, nm, date, name, desc in [
    ("marx-circle.png", 1.0, 2.35, 2.3, "!!marx", "1818 – 1883", "C. MÁC", "Tư bản · 1867"),
    ("engels-circle.png", 5.45, 2.35, 2.3, "!!engels", "1820 – 1895", "PH. ĂNGGHEN", "Tuyên ngôn · 1848"),
    ("lenin-circle.png", 9.9, 2.35, 2.3, "!!lenin", "1870 – 1924", "V.I. LÊNIN", "Cách mạng · 1917"),
]:
    circle(s, x - 0.05, y - 0.05, d + 0.1, fill=None, line=GOLD, lw=1.0, name=nm + "-ring")
    pic(s, f, x, y, d, d, name=nm)
    tb(s, x - 0.2, y + d + 0.1, d + 0.4, 0.3, date, size=8.5, color=GOLD_TEXT, align=PP_ALIGN.CENTER, name=nm + "-date")
    tb(s, x - 0.2, y + d + 0.38, d + 0.4, 0.35, name, size=11, color=CREAM, bold=True, align=PP_ALIGN.CENTER, name=nm + "-name")
    tb(s, x - 0.2, y + d + 0.66, d + 0.4, 0.3, desc, size=8, color=CREAM, align=PP_ALIGN.CENTER, name=nm + "-desc")
# timeline
line(s, 0.85, 6.35, 12.45, 6.35, GOLD, 1.2, name="timeline")
for x, label in [(2.2, "1848"), (6.4, "1867"), (10.9, "1917")]:
    circle(s, x - 0.07, 6.28, 0.14, fill=CREAM, name=f"tl-{label}")
    tb(s, x - 0.3, 6.55, 0.6, 0.3, label, size=8, color=GOLD_TEXT, align=PP_ALIGN.CENTER, name=f"tl-{label}-t")
thread(s, 0.45, 0.8, 0.035, 5.0)
notes(s, "Ba người, ba thời điểm, một dự án. Mác và Ăngghen đặt nền lý luận; Lênin phát triển trong điều kiện đế quốc chủ nghĩa và cách mạng vô sản. Đừng biến họ thành ba biểu tượng tách rời khỏi lịch sử.")

# ---------------------------------------------------------------- 8 functions
s = new_slide(CREAM)
tb(s, 0.85, 0.62, 8.0, 0.35, "CÔNG CỤ", size=10.5, color=RED, bold=True, spc=1.5, name="kicker")
tb(s, 0.8, 1.0, 11.0, 1.1, "ĐỐI TƯỢNG & CHỨC NĂNG", size=36, font=HEAD, color=RED, bold=True, name="title")
tiles = [
    ("01", "THẾ GIỚI QUAN", "Nhìn thế giới như một chỉnh thể\ncó quy luật.", RED),
    ("02", "PHƯƠNG PHÁP LUẬN", "Cách đặt vấn đề, cách hành động\ntrong thực tiễn.", DEEP),
    ("03", "CHỨC NĂNG XÃ HỘI", "Phê phán cái lỗi thời;\nmở đường cho cái mới.", RED),
    ("04", "KHOA HỌC", "Không đứng trên khoa học;\nlà phương pháp của khoa học.", DEEP),
]
for i, (n, head, body, ink) in enumerate(tiles):
    x = 0.85 + (i % 2) * 5.95
    y = 2.35 + (i // 2) * 2.3
    rect(s, x, y, 5.45, 1.95, fill=None, line=ink, lw=1.0, name=f"tile{i}")
    tb(s, x + 0.22, y + 0.18, 0.5, 0.3, n, size=9, color=ink, bold=True, name=f"tile{i}-n")
    tb(s, x + 0.75, y + 0.16, 4.4, 0.35, head, size=13, color=ink, bold=True, spc=0.6, name=f"tile{i}-h")
    tb(s, x + 0.75, y + 0.65, 4.4, 0.85, body, size=10.5, color=DEEP, spacing=1.12, name=f"tile{i}-b")
thread(s, 0.85, 7.05, 11.7, 0.035, horizontal=True)
notes(s, "Chức năng không phải 'ứng dụng triết học vào mọi thứ'. Đó là bốn cách kiểm tra: cách nhìn, cách làm, cách phê phán, và quan hệ với khoa học. Một bài nói tốt phải chỉ ra chỗ nào dùng cái nào.")

# ---------------------------------------------------------------- 9 quote
s = new_slide(DEEP)
tb(s, 0.85, 0.62, 8.0, 0.35, "LUẬN CƯƠNG", size=10.5, color=GOLD_TEXT, bold=True, spc=1.6, name="kicker")
tb(s, 1.0, 0.95, 2.0, 1.5, "“", size=180, font=BODY, color=GOLD, bold=True, name="quote-mark")
quote_lines = [
    "Các nhà triết học chỉ giải thích",
    "thế giới bằng nhiều cách khác nhau;",
    "vấn đề là cải tạo thế giới.",
]
for i, qline in enumerate(quote_lines):
    tb(s, 2.2, 1.75 + i * 1.05, 9.6, 0.95, qline, size=33, font=HEAD, color=CREAM, bold=False,
       spacing=1.0, name=f"quote{i}")
line(s, 2.05, 5.25, 6.75, 5.25, GOLD, 1.2, name="quote-rule")
tb(s, 2.05, 5.5, 8.5, 0.4, "C. Mác · Luận cương về Phoiơbắc, 1845", size=12, color=GOLD, name="author")
thread(s, 0.85, 7.05, 11.7, 0.035, horizontal=True)
notes(s, "Câu này thường bị trích như một khẩu hiệu. Cần đọc nó trong lập trường duy vật thực tiễn: lý luận không phải để chiêm ngưỡng mà để chỉ ra hành động có thể kiểm chứng. Đây là cầu nối sang phần vận dụng.")

# ---------------------------------------------------------------- 10 close
s = new_slide(CREAM)
tb(s, 0.85, 0.62, 8.0, 0.35, "KẾT", size=10.5, color=RED, bold=True, spc=1.5, name="kicker")
tb(s, 0.8, 1.0, 10.5, 1.1, "MANG THEO", size=40, font=HEAD, color=RED, bold=True, name="title")
takeaways = [
    ("01", "Câu hỏi nền tảng", "Cái nào có trước: vật chất hay ý thức?"),
    ("02", "Cách nhìn biện chứng", "Sự vật trong liên hệ, vận động, mâu thuẫn."),
    ("03", "Lý luận gắn thực tiễn", "Giải thích thế giới để cải tạo thế giới."),
]
for i, (n, head, body) in enumerate(takeaways):
    y = 2.35 + i * 1.15
    tb(s, 0.85, y, 0.55, 0.35, n, size=9, color=RED, bold=True, name=f"take{i}-n")
    tb(s, 1.45, y - 0.03, 4.0, 0.4, head, size=14, color=INK, bold=True, name=f"take{i}-h")
    tb(s, 5.55, y - 0.02, 6.5, 0.45, body, size=11.5, color=DEEP, name=f"take{i}-b")
    line(s, 0.85, y + 0.48, 11.95, y + 0.48, PINK, 0.8, name=f"take{i}-line")
tb(s, 0.85, 6.05, 11.5, 0.55, "Học triết học là học cách đặt câu hỏi đúng.", size=22, font=HEAD, color=RED, bold=True, italic=True, name="closing")
tb(s, 0.85, 6.75, 11.9, 0.5, "Ảnh: Wikimedia Commons — Marx/Engels/Lenin (Public Domain), tượng triết gia Hy Lạp (CC0). Nội dung: Giáo trình Triết học Mác – Lênin, Chương 1.", size=8.0, color=DEEP, name="credits")
thread(s, 0.85, 7.15, 11.7, 0.03, horizontal=True)
notes(s, "Ba điều mang theo, không phải ba định nghĩa. Kết bằng câu hỏi: trong ba cách nhìn này, cách nào bạn đang thiếu nhất khi phân tích một vấn đề thật?")

# ---------------------------------------------------------------- motion + Morph
mapping = []
for idx, slide in enumerate(prs.slides, 1):
    ids = {sh.name: str(sh.shape_id) for sh in slide.shapes if sh.name}
    mapping.append((idx, ids))

# Effect helper
E = lambda name, preset, trigger="click", **kw: {"spid": ids[name], "preset": preset, "trigger": trigger,
                                                "duration_ms": kw.pop("dur", 500), **kw}

for idx, slide in enumerate(prs.slides, 1):
    ids = mapping[idx - 1][1]
    def eff(name, preset, trigger="click", **kw):
        return {"spid": ids[name], "preset": preset, "trigger": trigger,
                "duration_ms": kw.pop("dur", 500), **kw}

    clicks = []
    if idx == 1:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("kicker", "fade", "click", dur=450)]},
            {"id": "c2", "start": "click", "effects": [
                eff("title", "wipe-up", "click", dur=700),
                eff("rule", "wipe-left", "with", dur=700),
            ]},
            {"id": "c3", "start": "click", "effects": [
                eff("subtitle", "fade", "click", dur=700),
                eff("caption", "fade", "with", dur=600),
                eff("!!thread", "wipe-down", "with", dur=700),
                eff("!!dot", "zoom", "with", dur=500),
            ]},
            {"id": "c4", "start": "click", "effects": [
                eff("!!marx", "zoom", "click", dur=700),
                eff("!!engels", "zoom", "after", dur=600),
                eff("!!lenin", "zoom", "after", dur=600),
            ]},
        ]
    elif idx == 2:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("kicker", "fade", "click", dur=400)]},
            {"id": "c2", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700)]},
            {"id": "c3", "start": "click", "effects": [
                eff("def1", "fade", "click", dur=700), eff("def2", "fade", "after", dur=700)]},
            {"id": "c4", "start": "click", "effects": [
                eff("l0-rule", "wipe-left", "click", dur=400), eff("l0-n", "fade", "with"),
                eff("l0-h", "fade", "with"), eff("l0-s", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [
                eff("l1-rule", "wipe-left", "click", dur=400), eff("l1-n", "fade", "with"),
                eff("l1-h", "fade", "with"), eff("l1-s", "fade", "with")]},
            {"id": "c6", "start": "click", "effects": [
                eff("l2-rule", "wipe-left", "click", dur=400), eff("l2-n", "fade", "with"),
                eff("l2-h", "fade", "with"), eff("l2-s", "fade", "with")]},
            {"id": "c7", "start": "click", "effects": [eff("plato", "float-in", "click", dur=700)]},
        ]
    elif idx == 3:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("kicker", "fade", "click", dur=400)]},
            {"id": "c2", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700)]},
            {"id": "c3", "start": "click", "effects": [
                eff("left", "wipe-up", "click", dur=700), eff("left-title", "fade", "with"),
                eff("left-body", "fade", "with"), eff("left-foot", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [
                eff("right", "wipe-down", "click", dur=700), eff("right-title", "fade", "with"),
                eff("right-body", "fade", "with"), eff("right-foot", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [
                eff("qmark", "zoom", "click", dur=600), eff("qline", "wipe-left", "with", dur=500),
                eff("qcap", "fade", "with")]},
        ]
    elif idx == 4:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700)]},
            {"id": "c2", "start": "click", "effects": [
                eff("dialectic-circle", "zoom", "click", dur=700), eff("dialectic-core", "zoom", "with", dur=700),
                eff("dialectic-arrow", "pulse", "with", dur=600)]},
            {"id": "c3", "start": "click", "effects": [
                eff("dialectic-card", "wipe-up", "click", dur=600), eff("dialectic-name", "fade", "with"),
                eff("dialectic-desc", "fade", "with"), eff("dialectic-foot", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [
                eff("straight-line", "wipe-left", "click", dur=700), eff("straight-label", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [
                eff("meta-card", "wipe-up", "click", dur=600), eff("meta-name", "fade", "with"),
                eff("meta-desc", "fade", "with")]},
        ]
    elif idx == 5:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("kicker", "fade", "click", dur=400)]},
            {"id": "c2", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700), eff("sub", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [eff("card0", "float-in", "click", dur=700), eff("card0-n", "fade", "with"), eff("card0-h", "fade", "with"), eff("card0-b", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [eff("card1", "float-in", "click", dur=700), eff("card1-n", "fade", "with"), eff("card1-h", "fade", "with"), eff("card1-b", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [eff("card2", "float-in", "click", dur=700), eff("card2-n", "fade", "with"), eff("card2-h", "fade", "with"), eff("card2-b", "fade", "with")]},
            {"id": "c6", "start": "click", "effects": [eff("timeline", "wipe-left", "click", dur=700), eff("timeline-dot", "zoom", "with"), eff("timeline-text", "fade", "with")]},
        ]
    elif idx == 6:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700), eff("sub", "fade", "with")]},
            {"id": "c2", "start": "click", "effects": [eff("part0", "zoom", "click", dur=700), eff("part0-n", "fade", "with"), eff("part0-h", "fade", "with"), eff("part0-b", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [eff("part1", "zoom", "click", dur=700), eff("part1-n", "fade", "with"), eff("part1-h", "fade", "with"), eff("part1-b", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [eff("part2", "zoom", "click", dur=700), eff("part2-n", "fade", "with"), eff("part2-h", "fade", "with"), eff("part2-b", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [eff("arrow1", "wipe-left", "click", dur=500), eff("arrow2", "wipe-left", "with", dur=500), eff("note", "fade", "with")]},
        ]
    elif idx == 7:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700), eff("sub", "fade", "with")]},
            {"id": "c2", "start": "click", "effects": [eff("!!marx", "zoom", "click", dur=700), eff("!!marx-date", "fade", "with"), eff("!!marx-name", "fade", "with"), eff("!!marx-desc", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [eff("!!engels", "zoom", "click", dur=700), eff("!!engels-date", "fade", "with"), eff("!!engels-name", "fade", "with"), eff("!!engels-desc", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [eff("!!lenin", "zoom", "click", dur=700), eff("!!lenin-date", "fade", "with"), eff("!!lenin-name", "fade", "with"), eff("!!lenin-desc", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [eff("timeline", "wipe-left", "click", dur=700), eff("tl-1848", "zoom", "with"), eff("tl-1867", "zoom", "after"), eff("tl-1917", "zoom", "after")]},
        ]
    elif idx == 8:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700)]},
            {"id": "c2", "start": "click", "effects": [eff("tile0", "wipe-up", "click", dur=600), eff("tile0-n", "fade", "with"), eff("tile0-h", "fade", "with"), eff("tile0-b", "fade", "with")]},
            {"id": "c3", "start": "click", "effects": [eff("tile1", "wipe-up", "click", dur=600), eff("tile1-n", "fade", "with"), eff("tile1-h", "fade", "with"), eff("tile1-b", "fade", "with")]},
            {"id": "c4", "start": "click", "effects": [eff("tile2", "wipe-up", "click", dur=600), eff("tile2-n", "fade", "with"), eff("tile2-h", "fade", "with"), eff("tile2-b", "fade", "with")]},
            {"id": "c5", "start": "click", "effects": [eff("tile3", "wipe-up", "click", dur=600), eff("tile3-n", "fade", "with"), eff("tile3-h", "fade", "with"), eff("tile3-b", "fade", "with")]},
        ]
    elif idx == 9:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("quote-mark", "zoom", "click", dur=700)]},
            {"id": "c2", "start": "click", "effects": [eff("quote0", "wipe-up", "click", dur=700)]},
            {"id": "c3", "start": "click", "effects": [eff("quote1", "wipe-up", "click", dur=700)]},
            {"id": "c4", "start": "click", "effects": [eff("quote2", "wipe-up", "click", dur=700), eff("quote-rule", "wipe-left", "with", dur=600), eff("author", "fade", "with")]},
        ]
    elif idx == 10:
        clicks = [
            {"id": "c1", "start": "click", "effects": [eff("title", "wipe-up", "click", dur=700)]},
            {"id": "c2", "start": "click", "effects": [eff("take0-n", "fade", "click"), eff("take0-h", "fade", "with"), eff("take0-b", "fade", "with"), eff("take0-line", "wipe-left", "with")]},
            {"id": "c3", "start": "click", "effects": [eff("take1-n", "fade", "click"), eff("take1-h", "fade", "with"), eff("take1-b", "fade", "with"), eff("take1-line", "wipe-left", "with")]},
            {"id": "c4", "start": "click", "effects": [eff("take2-n", "fade", "click"), eff("take2-h", "fade", "with"), eff("take2-b", "fade", "with"), eff("take2-line", "wipe-left", "with")]},
            {"id": "c5", "start": "click", "effects": [eff("closing", "zoom", "click", dur=700), eff("credits", "fade", "with")]},
        ]

    if clicks:
        anim.apply_timeline(slide._element, clicks, mode="replace")
    if idx > 1:
        anim.add_morph_transition(slide._element, 1500)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print("wrote", OUT, "slides", len(prs.slides), "bytes", OUT.stat().st_size)