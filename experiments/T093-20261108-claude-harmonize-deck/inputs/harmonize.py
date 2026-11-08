"""T093: harmonise qcc-chap-va.pptx by following skills/pptx/guides/10 step by step.

Triage (step 3) is in ../REPORT.md. System (step 4): Segoe UI for both roles,
sizes 40 / 32 / 22 / 18 / 16 / 72, white background, ink 262626, main colour
1F4E79 (the deck's own blue, the most used colour), accent C55A11 (the deck's
own orange). Every text below is read from the original shapes or copied from
them word for word; nothing is typed from memory.
"""
import copy
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_tools as tools  # noqa: E402

EXP = Path(__file__).resolve().parents[1]
SRC = EXP / "artifacts" / "qcc-chap-va.pptx"
TMP = ROOT / "workspace" / "t093"
OUT = EXP / "artifacts" / "qcc-dong-bo.static.pptx"
TMP.mkdir(parents=True, exist_ok=True)

FONT = "Segoe UI"
INK, SOFT, MAIN, ACCENT = "262626", "6B6B6B", "1F4E79", "C55A11"
GREY, PANEL, ON_DARK = "C9C9C9", "EEF3F8", "BDD7EE"
W, H, M = 13.333, 7.5, 0.8

# ---- step 5 first: the three things only the toolbox can do (chain through files)
steps = [
    lambda a, b: tools.rechart(a, 3, "Bieu do loi", "line", b, color=MAIN, size=16, ink=INK),
    lambda a, b: tools.rechart(a, 5, "Bieu do tron", "bar", b, sort=True, accent="Que hàn ẩm",
                               color=ACCENT, size=16, ink=INK),
    lambda a, b: tools.unstretch(a, 8, "Anh truoc", b, box=True),  # evidence photos: keep every pixel
    lambda a, b: tools.unstretch(a, 8, "Anh sau", b, box=True),
]
cur = SRC
for n, step in enumerate(steps, 1):
    nxt = TMP / f"step{n}.pptx"
    step(str(cur), str(nxt))
    cur = nxt
# the fishbone: every shape but the title, as one block, below the title band
prs = Presentation(cur)
fish = [s.name for s in prs.slides[3].shapes if not s.is_placeholder]
low = tools.scale(str(cur), 4, fish, 0.68, str(TMP / "step5.pptx"), at=(1.75, 1.6))
print("fishbone smallest text after scale:", low, "pt")

prs = Presentation(TMP / "step5.pptx")
slides = list(prs.slides)


# ---- helpers ------------------------------------------------------------------------
def rgb(h):
    return RGBColor.from_string(h)


def remove(shape):
    shape._element.getparent().remove(shape._element)


def clear_motion(slide):
    timing = slide._element.find(qn("p:timing"))
    if timing is not None:
        slide._element.remove(timing)


def by_text(slide, start):
    found = [s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip().startswith(start)]
    assert len(found) == 1, (start, [s.text_frame.text[:30] for s in slide.shapes if s.has_text_frame])
    return found[0]


def text(slide, name, x, y, w, h, lines, size, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, heading=False, spacing=1.1):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    tf = box.text_frame
    tf.word_wrap, tf.auto_size, tf.vertical_anchor = True, MSO_AUTO_SIZE.NONE, anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate([lines] if isinstance(lines, str) else lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing = align, spacing
        r = p.add_run()
        r.text = line
        r.font.size, r.font.bold, r.font.color.rgb = Pt(size), bold, rgb(color)
        if heading:
            r.font.name = "+mj-lt"
    return box


def rect(slide, name, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE):
    r = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    r.name = name
    r.fill.solid()
    r.fill.fore_color.rgb = rgb(color)
    r.line.fill.background()
    r.shadow.inherit = False
    return r


def line(slide, name, x1, y1, x2, y2, color, pt):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb, c.line.width = rgb(color), Pt(pt)
    return c


def background(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(color)


def sentence(words):
    """Guide 4: no all-caps sentences. Same words, sentence case; one-letter names (B) and
    roman numerals (II) kept."""
    if not words.isupper():
        return words
    out = " ".join(w if len(w) == 1 or re.fullmatch("[IVX]+", w) else w.lower() for w in words.split())
    return out[0].upper() + out[1:]


def title(slide, words, takeaway=None):
    """Same place, size and colour on every content slide (guide 10, step 4.3)."""
    words = sentence(words)
    t = text(slide, "Tieu de", M, 0.5, W - 2 * M, 0.75, words, 32, MAIN, bold=True, heading=True)
    if takeaway:
        text(slide, "Thong diep", M, 1.25, W - 2 * M, 0.5, takeaway, 22, SOFT)
    return t


def old_title(slide):
    """The author's title text, from a placeholder or the top-most text box."""
    if slide.shapes.title is not None:
        shape = slide.shapes.title
    else:
        shape = min((s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()), key=lambda s: s.top)
    words = shape.text_frame.text.strip()
    remove(shape)
    return words


# ---- step 4: one system for the whole deck --------------------------------------------
tools.theme_fonts(prs, FONT, FONT)
for s in slides:
    tools.follow_theme(s._element)
    background(s, "FFFFFF")

# 1. Cover (Sửa vỏ) -------------------------------------------------------------------
s = slides[0]
clear_motion(s)
words = [by_text(s, start).text_frame.text.strip() for start in ("GIẢM", "Nhóm", "Dữ liệu")]
for shape in list(s.shapes):
    remove(shape)  # gear goes: decoration
background(s, MAIN)
text(s, "Tieu de", M, 2.2, 9.6, 1.8, sentence(words[0]), 40, "FFFFFF", bold=True, heading=True, anchor=MSO_ANCHOR.BOTTOM)
line(s, "Gach", M, 4.3, M + 1.4, 4.3, "F4B183", 3)
text(s, "Nhom", M, 4.55, 9.6, 0.6, words[1], 22, ON_DARK)
text(s, "Ghi chu", M, 6.6, 11, 0.4, words[2], 16, ON_DARK)

# 2. Why this topic (Làm lại: paragraph -> three points; the paragraph goes to the notes) ---
s = slides[1]
clear_motion(s)
para = by_text(s, "Trong 6 tháng").text_frame.text.strip()
heading = old_title(s)
remove(by_text(s, "Trong 6 tháng"))
s.notes_slide.notes_text_frame.text = para
title(s, heading)
points = (("4,1%", "Tỉ lệ lỗi hàn trung bình 6 tháng đầu năm, cao gấp đôi mục tiêu 2% của nhà máy"),
          ("Chi phí", "Tăng thời gian sửa chữa, chi phí vật tư và gây chậm giao hàng cho khách hàng"),
          ("2 lần", "Khách hàng phản hồi về chất lượng mối hàn trong quý II"))
col = (W - 2 * M - 2 * 0.5) / 3
for k, (big, small) in enumerate(points):
    x = M + k * (col + 0.5)
    text(s, f"So {k + 1}", x, 1.75, col, 0.8, big, 40, ACCENT, bold=True, heading=True)
    text(s, f"Y {k + 1}", x, 2.65, col, 1.6, small, 22, INK, spacing=1.15)
rect(s, "Nen muc tieu", M, 4.85, W - 2 * M, 1.45, PANEL)
text(s, "Muc tieu", M + 0.4, 4.85, W - 2 * M - 0.8, 1.45,
     "Mục tiêu: giảm tỉ lệ lỗi hàn tại dây chuyền B xuống dưới 2% trong vòng 3 tháng, "
     "đồng thời chuẩn hóa thao tác hàn để duy trì kết quả lâu dài", 22, MAIN, bold=True,
     anchor=MSO_ANCHOR.MIDDLE)

# 3. Current state (Sửa vỏ: 3D columns -> line against the target) -----------------------
s = slides[2]
heading = old_title(s)
title(s, heading, "Cả 6 tháng đều trên mục tiêu 2%, trung bình 4,1%")
chart = [x for x in s.shapes if x.name == "Bieu do loi"][0]
chart.left, chart.top, chart.width, chart.height = Inches(M), Inches(2.0), Inches(W - 2 * M), Inches(5.0)

# 4. Fishbone (Sửa vỏ: scaled above; restyle, keep its bone-by-bone animation) ----------
s = slides[3]
heading = old_title(s)
title(s, heading)
for shape in s.shapes:
    if shape.name == "Tieu de":
        continue
    if shape.shape_type == 9 or shape.name.startswith("Connector"):  # lines
        shape.line.color.rgb = rgb(SOFT)
        continue
    if not shape.has_text_frame or not shape.text_frame.text.strip():
        if shape.name.startswith("Right Arrow"):
            shape.fill.solid()
            shape.fill.fore_color.rgb = rgb(ACCENT)
        continue
    is_head = shape.name.startswith("Pentagon")
    is_cat = shape.text_frame.text.strip() in ("Con người", "Máy móc", "Phương pháp", "Vật liệu")
    if is_head:
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb(MAIN)
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(22 if is_head or is_cat else 18)
            r.font.bold = is_head or is_cat
            r.font.color.rgb = rgb("FFFFFF" if is_head else MAIN if is_cat else INK)
    if is_head:
        shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    elif not is_cat:  # causes: clear of the bone they hang on, wide enough for one line
        shape.left, shape.width = shape.left + Inches(0.3), Inches(3.2)
    if not is_head:
        shape.fill.solid()  # lines pass behind the words, not through them
        shape.fill.fore_color.rgb = rgb("FFFFFF")

# 5. Causes (Làm lại: 3D pie -> sorted bars, one accent) ------------------------------------
s = slides[4]
heading = old_title(s)
title(s, heading, "Que hàn ẩm chiếm nhiều nhất: 38% số lỗi")
chart = [x for x in s.shapes if x.name == "Bieu do tron"][0]
chart.left, chart.top, chart.width, chart.height = Inches(M), Inches(2.0), Inches(W - 2 * M), Inches(5.0)

# 6. Weekly table (Làm lại: one number + small line; the full table goes to an appendix) --
s = slides[5]
heading = table_heading = old_title(s)
table = [x for x in s.shapes if x.has_table][0]
rows = [[c.text for c in r.cells] for r in table.table.rows]
appendix = prs.slides.add_slide(prs.slide_layouts[6])
moved = copy.deepcopy(table._element)
appendix.shapes._spTree.append(moved)
remove(table)
title(s, heading)
weeks = [f"Tuần {r[0]}" for r in rows[1:]]
rates = [float(r[3].replace(",", ".")) for r in rows[1:]]
text(s, "So lon", M, 1.9, 4.4, 1.4, rows[-1][3] + "%", 72, ACCENT, bold=True, heading=True)
text(s, "Ghi so lon", M, 3.35, 4.2, 1.6,
     [f"tỉ lệ lỗi {weeks[-1].lower()}", f"từ {rows[1][3]}% ở {weeks[0].lower()}"], 22, INK, spacing=1.2)
text(s, "Nguon", M, 6.55, 6, 0.4, "Số liệu đầy đủ 6 tuần: phụ lục cuối bài", 16, SOFT)
tools.add_chart(s, "line", (Inches(5.6), Inches(1.8), Inches(W - M - 5.6), Inches(4.9)), weeks,
                [("Tỉ lệ lỗi (%)", rates)], "0.0", color=MAIN, size=16, ink=INK).name = "Duong tuan"

# 7. Steps (Làm lại: bullets -> steps on one axis) -------------------------------------------
s = slides[6]
clear_motion(s)
body = by_text(s, "• Bước 1")
steps_text = [p.text.split(":", 1)[1].strip() for p in body.text_frame.paragraphs if p.text.strip()]
heading = old_title(s)
remove(body)
title(s, heading)
n = len(steps_text)
gap = (W - 2 * M) / n
line(s, "Truc", M + gap / 2, 3.25, W - M - gap / 2, 3.25, GREY, 2)
for k, words in enumerate(steps_text, 1):
    cx = M + gap * (k - 0.5)
    dot = rect(s, f"Vong {k}", cx - 0.45, 2.8, 0.9, 0.9, MAIN, MSO_SHAPE.OVAL)
    tf = dot.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.text = str(k)
    run = tf.paragraphs[0].runs[0]
    run.font.size, run.font.bold, run.font.color.rgb = Pt(22), True, rgb("FFFFFF")
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    text(s, f"Buoc {k}", cx - gap / 2 + 0.1, 4.0, gap - 0.2, 2.2, words, 22, INK, align=PP_ALIGN.CENTER, spacing=1.15)

# 8. Before / after photos (Sửa vỏ: frames fixed to the photos, same size, one row) ----------
s = slides[7]
heading = old_title(s)
title(s, heading)
h_in = 4.2
for k, (pic_name, start) in enumerate((("Anh truoc", "TRƯỚC"), ("Anh sau", "Sau"))):
    pic = [x for x in s.shapes if x.name == pic_name][0]
    ratio = pic.width / pic.height
    pic.height = Inches(h_in)
    pic.width = int(Inches(h_in) * ratio)
    pic.left = Inches(M) if k == 0 else Inches(W - M) - pic.width
    pic.top = Inches(1.75)
    cap = by_text(s, start)
    words = cap.text_frame.text.strip()
    remove(cap)
    text(s, "Chu truoc" if k == 0 else "Chu sau", pic.left / 914400, 6.1, pic.width / 914400, 0.5,
         sentence(words), 22, MAIN, bold=True, heading=True)

# 9. Result (Làm lại: two big numbers, no star, no shouting) -----------------------------------
s = slides[8]
clear_motion(s)
before = by_text(s, "Trước").text_frame.text.strip()
after = by_text(s, "Sau").text_frame.text.strip()
goal = by_text(s, "ĐẠT").text_frame.text.replace("!", "").strip()
heading = old_title(s)
for shape in list(s.shapes):
    remove(shape)  # the star goes: decoration
title(s, heading)
for k, (label, value, color) in enumerate(((before.split(":")[0], before.split(":")[1].strip(), SOFT),
                                           (after.split(":")[0], after.split(":")[1].strip(), ACCENT))):
    x = M + k * 6.2
    text(s, "So truoc" if k == 0 else "So sau", x, 2.0, 5.2, 1.4, value, 72, color, bold=True, heading=True)
    text(s, "Nhan truoc" if k == 0 else "Nhan sau", x, 3.45, 5.2, 0.5, label, 22, SOFT)
arrow = rect(s, "Mui ten", 5.25, 2.45, 1.2, 0.6, GREY, MSO_SHAPE.RIGHT_ARROW)
text(s, "Dat muc tieu", M, 5.0, W - 2 * M, 0.7, sentence(goal), 32, MAIN, bold=True, heading=True)

# 10. Thanks (Sửa vỏ: same lid as the cover) ----------------------------------------------------
s = slides[9]
clear_motion(s)
words = by_text(s, "CẢM ƠN").text_frame.text.strip()
for shape in list(s.shapes):
    remove(shape)  # the smiley goes: decoration
background(s, MAIN)
text(s, "Tieu de", M, 2.2, 9.6, 1.8, sentence(words), 40, "FFFFFF", bold=True, heading=True,
     anchor=MSO_ANCHOR.BOTTOM)
line(s, "Gach", M, 4.3, M + 1.4, 4.3, "F4B183", 3)

# 11. Appendix: the full weekly table, restyled -----------------------------------------------
s = appendix
background(s, "FFFFFF")
title(s, "Phụ lục: " + table_heading.lower())
tbl = [x for x in s.shapes if x.has_table][0]
tbl.name = "Bang theo doi"
tbl.left, tbl.top, tbl.width = Inches(M), Inches(1.6), Inches(W - 2 * M)
tbl.table.first_row = True
widths = (0.9, 1.9, 1.2, 1.5, 1.4, 1.3, 1.5, 2.03)
for k, w in enumerate(widths):
    tbl.table.columns[k].width = Inches(w)
for r_no, row in enumerate(tbl.table.rows):
    row.height = Inches(0.62)
    for c_no, cell in enumerate(row.cells):
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(MAIN if r_no == 0 else "FFFFFF" if r_no % 2 else "F5F7FA")
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.RIGHT if c_no in (1, 2, 3) and r_no else PP_ALIGN.LEFT
            for run in p.runs:
                run.font.size = Pt(18 if r_no else 16)
                run.font.bold = r_no == 0 or (c_no == 3 and r_no == len(tbl.table.rows) - 1)
                run.font.color.rgb = rgb("FFFFFF" if r_no == 0 else INK)
tools.follow_theme(s._element)

prs.save(OUT)
print(OUT)
