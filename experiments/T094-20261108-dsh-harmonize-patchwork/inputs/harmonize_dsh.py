#!/usr/bin/env python3
"""T094 - blind rehearsal of guide 10 on the T093 patchwork deck (DSH family).

Reads:  experiments/T093-20261108-claude-harmonize-deck/artifacts/qcc-chap-va.pptx
Writes: artifacts/qcc-dong-bo-dsh.static.pptx, artifacts/qcc-dong-bo-dsh.pptx,
        inputs/plan.json, preview/inventory-*.txt

Blind rule: this script never opens qcc-dong-bo*.pptx, harmonize.py, plan.json or the T093 REPORT.
Everything here comes from the original deck + skills/pptx/guides/10 + the toolbox.

usage: python experiments/T094-.../inputs/harmonize_dsh.py
"""
import copy
import json
import sys
import tempfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_tools as tools  # noqa: E402

TASK = ROOT / "experiments/T094-20261108-dsh-harmonize-patchwork"
SRC = ROOT / "experiments/T093-20261108-claude-harmonize-deck/artifacts/qcc-chap-va.pptx"
ART = TASK / "artifacts"
PREVIEW = TASK / "preview"
(ART).mkdir(parents=True, exist_ok=True)
PREVIEW.mkdir(parents=True, exist_ok=True)

PRIMARY = "1F4E79"
ACCENT = "C00000"
INK = "262626"
GREY = "A6A6A6"
PALE = "DCE6F1"
WHITE = "FFFFFF"
FONT = "Century Gothic"


def I(v):
    return Inches(v)


def rgb(h):
    return RGBColor.from_string(h)


def drop(shape):
    el = shape._element
    el.getparent().remove(el)


def find(slide, name):
    for sh in slide.shapes:
        if sh.name == name:
            return sh
    raise KeyError(f"{name} not on slide")


def set_text(shape, lines, size, color, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
             spacing=1.0, heading=False):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, line in enumerate(lines if isinstance(lines, list) else [lines]):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = align
        para.line_spacing = spacing
        run = para.add_run()
        run.text = line
        f = run.font
        f.size = Pt(size)
        f.bold = bold
        f.color.rgb = rgb(color)
        f.name = FONT
    return shape


def tbox(slide, name, x, y, w, h, lines, size, color=INK, bold=False, align="l", anchor="t", spacing=1.0,
         heading=False):
    sh = slide.shapes.add_textbox(I(x), I(y), I(w), I(h))
    sh.name = name
    align_map = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
    anchor_map = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}
    set_text(sh, lines, size, color, bold, align_map[align], anchor_map[anchor], spacing, heading)
    return sh


def rbox(slide, name, x, y, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, I(x), I(y), I(w), I(h))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb(fill)
    if line:
        sh.line.color.rgb = rgb(line)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def oval(slide, name, x, y, d, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, I(x), I(y), I(d), I(d))
    sh.name = name
    sh.fill.solid()
    sh.fill.fore_color.rgb = rgb(fill)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def connector(slide, name, x1, y1, x2, y2, color=INK, w=1.25):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, I(x1), I(y1), I(x2), I(y2))
    c.name = name
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(w)
    return c


def set_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)


def style_title(slide, text, size=32, color=PRIMARY, dark=False):
    sh = None
    for cand in slide.shapes:
        if cand.has_text_frame and cand.text_frame.text.strip():
            sh = cand
            break
    assert sh is not None, "slide without a text shape to use as title"
    sh.left, sh.top, sh.width, sh.height = I(0.6), I(0.35), I(12.1), I(0.85)
    set_text(sh, text, size, color, bold=True, heading=True)
    return sh


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ---------------------------------------------------------------- step A: toolbox passes
WORK = Path(tempfile.mkdtemp(prefix="t094-work-"))
tmp1 = WORK / "step1-line.pptx"
tmp2 = WORK / "step2-bar.pptx"
tmp3 = WORK / "step3-pic1.pptx"
tmp4 = WORK / "step4-pic2.pptx"
tools.rechart(SRC, 3, "Bieu do loi", "line", tmp1, color=PRIMARY, muted=GREY, font=FONT, size=14)
tools.rechart(tmp1, 5, "Bieu do tron", "bar", tmp2, sort=True, color=PRIMARY, accent="Que hàn ẩm",
              font=FONT, size=14)
tools.unstretch(tmp2, 8, "Anh truoc", tmp3, box=True)
tools.unstretch(tmp3, 8, "Anh sau", tmp4, box=True)
print("toolbox passes done")

# ---------------------------------------------------------------- step B: one system + rebuilds
prs = Presentation(str(tmp4))
tools.theme_fonts(prs, FONT, FONT)
for slide in prs.slides:
    tools.follow_theme(slide._element)

slides = list(prs.slides)
for _sl in slides[1:9]:
    set_bg(_sl, WHITE)
plan_clicks = {}
plan_trans = {"default": "fade", "1": "none"}

# ---------- 1 cover ----------
s = slides[0]
for sh in list(s.shapes):
    if not sh.has_text_frame and sh.shape_type != 17:
        drop(sh)  # gear
    elif sh.has_text_frame and "" == sh.text_frame.text.strip():
        drop(sh)
set_bg(s, PRIMARY)
title = s.shapes[0]
title.left, title.top, title.width, title.height = I(0.9), I(2.0), I(11.6), I(1.7)
set_text(title, "Giảm tỉ lệ lỗi hàn tại dây chuyền B", 44, WHITE, bold=True, heading=True, spacing=1.05)
sub = s.shapes[1]
sub.left, sub.top, sub.width, sub.height = I(0.9), I(3.85), I(11.6), I(0.5)
set_text(sub, "Nhóm QCC Ánh Dương — 2026", 20, PALE)
foot_note = s.shapes[2]
foot_note.left, foot_note.top, foot_note.width, foot_note.height = I(0.9), I(6.55), I(11.6), I(0.4)
set_text(foot_note, "Dữ liệu giả lập để diễn tập — không phải số liệu thật", 18, PALE)
notes(s, "[T=0] Chào mọi người, nhóm Ánh Dương xin trình bày đề tài QCC năm 2026.")
plan_clicks["1"] = []

# ---------- 2 reason (rebuild) ----------
s = slides[1]
style_title(s, "1. Lý do chọn đề tài")
for sh in list(s.shapes):
    if sh.name != "TextBox 1":
        drop(sh)
reasons = [
    ("Y 1", "6 tháng đầu năm: tỉ lệ lỗi hàn dây chuyền B trung bình 4,1% — cao gấp đôi mục tiêu 2% của nhà máy."),
    ("Y 2", "Lỗi hàn làm tăng thời gian sửa chữa, tăng chi phí vật tư và gây chậm giao hàng cho khách hàng."),
    ("Y 3", "Khách hàng đã có 2 lần phản hồi về chất lượng mối hàn trong quý II."),
]
for i, (name, line) in enumerate(reasons):
    y = 1.62 + i * 0.95
    rbox(s, f"Cham {i+1}", 0.62, y + 0.12, 0.09, 0.30, ACCENT)
    tbox(s, name, 0.92, y, 11.7, 0.75, line, 20, INK, spacing=1.15)
tbox(s, "Muc tieu nhan", 0.62, 4.95, 3.2, 0.5, "MỤC TIÊU", 18, ACCENT, bold=True, heading=True)
tbox(s, "Muc tieu text", 0.62, 5.4, 12.0, 0.9,
     "Giảm tỉ lệ lỗi hàn xuống dưới 2% trong vòng 3 tháng; chuẩn hóa thao tác hàn để duy trì kết quả lâu dài.",
     20, INK, spacing=1.2)
notes(s, "[T=0] Trong 6 tháng đầu năm, tỉ lệ lỗi hàn tại dây chuyền B luôn ở mức cao, trung bình khoảng "
         "4,1%, cao gấp đôi mục tiêu 2% của nhà máy.\n"
         "[CLICK 1] Lỗi hàn làm tăng thời gian sửa chữa, tăng chi phí vật tư và gây chậm giao hàng cho "
         "khách hàng. Ngoài ra, khách hàng đã có 2 lần phản hồi về chất lượng mối hàn trong quý II.\n"
         "[CLICK 2] Vì vậy nhóm chọn đề tài giảm tỉ lệ lỗi hàn tại dây chuyền B xuống dưới 2% trong vòng "
         "3 tháng, đồng thời chuẩn hóa thao tác hàn để duy trì kết quả lâu dài.\n"
         "Nguyên văn đoạn gốc: Trong 6 tháng đầu năm, tỉ lệ lỗi hàn tại dây chuyền B luôn ở mức cao, "
         "trung bình khoảng 4,1%, cao gấp đôi mục tiêu 2% của nhà máy. Lỗi hàn làm tăng thời gian sửa "
         "chữa, tăng chi phí vật tư và gây chậm giao hàng cho khách hàng. Ngoài ra, khách hàng đã có 2 "
         "lần phản hồi về chất lượng mối hàn trong quý II. Vì vậy nhóm chọn đề tài giảm tỉ lệ lỗi hàn "
         "tại dây chuyền B xuống dưới 2% trong vòng 3 tháng, đồng thời chuẩn hóa thao tác hàn để duy trì "
         "kết quả lâu dài.")
plan_clicks["2"] = [["Cham 1", "Y 1", "Cham 2", "Y 2", "Cham 3", "Y 3"],
                    ["Muc tieu nhan", "Muc tieu text"]]

# ---------- 3 current state (line chart from its own numbers) ----------
s = slides[2]
style_title(s, "Hiện trạng tỉ lệ lỗi hàn (%)")
chart = find(s, "Bieu do loi")
chart.left, chart.top, chart.width, chart.height = I(0.8), I(1.5), I(11.7), I(4.75)
tbox(s, "Thong diep 3", 0.8, 6.45, 11.7, 0.5, "Cả 6 tháng đều trên mục tiêu 2% — trung bình 4,1%.", 18,
     PRIMARY, bold=True)
notes(s, "[T=0] Tỉ lệ lỗi các tháng đều trên 3,8%, trung bình 4,1%.\n"
         "[CLICK 1] Cả 6 tháng đều trên mục tiêu 2% — trung bình 4,1%.")
plan_clicks["3"] = [["Thong diep 3"]]

# ---------- 4 fishbone (scaled 0.72 would leave 17,3 pt < 18, so re-lay it as vertical branches) ----------
s = slides[3]
style_title(s, "Phân tích nguyên nhân – Biểu đồ xương cá")
for sh in list(s.shapes):
    if sh.name != "Title 1":
        drop(sh)
connector(s, "Xuong song", 1.0, 6.2, 9.0, 6.2, INK, 2.5)
head = s.shapes.add_shape(MSO_SHAPE.PENTAGON, I(8.95), I(5.7), I(2.55), I(1.0))
head.name = "Ket qua xương cá"
head.fill.solid()
head.fill.fore_color.rgb = rgb(PRIMARY)
head.line.fill.background()
head.shadow.inherit = False
set_text(head, "Lỗi hàn 4,1%", 18, WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
groups = [
    ("Con nguoi", "Con người", ["Thợ mới chưa được đào tạo", "Thao tác không đồng nhất"]),
    ("May moc", "Máy móc", ["Đầu hàn mòn", "Dòng hàn dao động"]),
    ("Phuong phap", "Phương pháp", ["Chưa có tiêu chuẩn góc hàn", "Không kiểm tra đầu ca"]),
    ("Vat lieu", "Vật liệu", ["Que hàn ẩm", "Bề mặt phôi bẩn"]),
]
for i, (gname, label, causes) in enumerate(groups):
    cx = 1.95 + i * 2.15
    tbox(s, f"4M {gname}", cx - 1.05, 1.95, 2.1, 0.4, label, 20, PRIMARY, bold=True, align="c")
    for k, text in enumerate(causes):
        tbox(s, f"NN {gname} {k+1}", cx - 1.03, 2.55 + k * 0.9, 2.06, 0.85, "– " + text, 18, INK,
             align="c", spacing=1.15)
    connector(s, f"Xuong {gname}", cx + 0.35, 4.32, cx, 6.2, GREY, 1.75)
plan_clicks["4"] = [["4M Con nguoi", "NN Con nguoi 1", "NN Con nguoi 2"],
                    ["4M May moc", "NN May moc 1", "NN May moc 2"],
                    ["4M Phuong phap", "NN Phuong phap 1", "NN Phuong phap 2"],
                    ["4M Vat lieu", "NN Vat lieu 1", "NN Vat lieu 2"]]
notes(s, "[T=0] Nhóm dùng 4M để tìm nguyên nhân.\n"
         "[CLICK 1] Con người: thợ mới chưa được đào tạo; thao tác không đồng nhất.\n"
         "[CLICK 2] Máy móc: đầu hàn mòn; dòng hàn dao động.\n"
         "[CLICK 3] Phương pháp: chưa có tiêu chuẩn góc hàn; không kiểm tra đầu ca.\n"
         "[CLICK 4] Vật liệu: que hàn ẩm; bề mặt phôi bẩn. Mũi tên chỉ tới vấn đề lỗi hàn 4,1%.")

# ---------- 5 causes (bar sorted from its own numbers) ----------
s = slides[4]
style_title(s, "Tỉ lệ các nguyên nhân gây lỗi")
chart = find(s, "Bieu do tron")
chart.left, chart.top, chart.width, chart.height = I(0.8), I(1.5), I(11.7), I(4.75)
tbox(s, "Thong diep 5", 0.8, 6.45, 11.7, 0.5, "Que hàn ẩm là nguyên nhân lớn nhất: 38%.", 18, PRIMARY,
     bold=True)
notes(s, "[T=0] Que hàn ẩm chiếm nhiều nhất, 38%.\n"
         "[CLICK 1] Que hàn ẩm là nguyên nhân lớn nhất: 38%.")
plan_clicks["5"] = [["Thong diep 5"]]

# ---------- 6 tracking (big number + line from the table, table to appendix) ----------
s = slides[5]
style_title(s, "Kết quả theo dõi sau cải tiến")
table_shape = find(s, "Bang theo doi")
table_el = copy.deepcopy(table_shape._element)
weeks = []
rates = []
for row in list(table_shape.table.rows)[1:]:
    weeks.append(int(row.cells[0].text))
    rates.append(float(row.cells[3].text.replace(",", ".")))
drop(table_shape)
tbox(s, "So 6", 0.9, 1.55, 3.4, 1.1, "1,2%", 54, PRIMARY, bold=True)
tbox(s, "Nhan 6", 0.9, 2.75, 3.7, 1.0, ["tỉ lệ lỗi tuần 6", "từ 3,8% ở tuần 1"], 18, INK, spacing=1.3)
frame = tools.add_chart(s, "line", (I(4.7), I(1.45), I(7.95), I(4.7)),
                        [f"Tuần {w}" for w in weeks],
                        [("Tỉ lệ lỗi (%)", rates), ("Mục tiêu", [2] * len(rates))],
                        number_format="0.0", color=PRIMARY, muted=GREY, font=FONT, size=14, ink=INK)
frame.name = "Bieu do tuan"
tbox(s, "Thong diep 6", 0.9, 6.4, 12.0, 0.5,
     "Chuỗi 6 tuần đều giảm; tuần 6 còn 1,2% — dưới mục tiêu 2%.", 18, PRIMARY, bold=True)
notes(s, "[T=0] Sau 6 tuần tỉ lệ lỗi giảm từ 3,8% xuống 1,2%.\n"
         "[CLICK 1] Tuần 6 còn 1,2% — đã dưới mục tiêu 2%.\n"
         "[CLICK 2] Bảng đầy đủ 6 tuần nằm ở phụ lục.")
plan_clicks["6"] = [["So 6", "Nhan 6"], ["Bieu do tuan", "Thong diep 6"]]

# ---------- 7 steps as a process line ----------
s = slides[6]
style_title(s, "Các bước cải tiến đã thực hiện")
for sh in list(s.shapes):
    if sh.name != "TextBox 1":
        drop(sh)
steps = ["Sấy que hàn trước mỗi ca", "Thay đầu hàn theo lịch 2 tuần/lần",
         "Đào tạo lại thợ mới theo tiêu chuẩn", "Ban hành tiêu chuẩn góc hàn",
         "Kiểm tra đầu ca bằng phiếu kiểm"]
connector(s, "Truc quy trinh", 0.9, 3.95, 12.45, 3.95, GREY, 1.75)
xs = [1.65 + i * 2.4 for i in range(5)]
for i, (x, text) in enumerate(zip(xs, steps), 1):
    oval(s, f"Buoc {i} tron", x - 0.32, 3.65, 0.64, PRIMARY)
    tbox(s, f"Buoc {i} so", x - 0.32, 3.65, 0.64, 0.64, str(i), 20, WHITE, bold=True, align="c",
         anchor="m", heading=True)
    tbox(s, f"Buoc {i} nhan", x - 1.15, 4.45, 2.3, 1.0, text, 18, INK, align="c", spacing=1.15)
plan_clicks["7"] = [[f"Buoc {i} tron", f"Buoc {i} so", f"Buoc {i} nhan"] for i in range(1, 6)]
notes(s, "[T=0] Nhóm đã thực hiện 5 bước cải tiến.\n"
         "[CLICK 1] Bước 1: Sấy que hàn trước mỗi ca.\n"
         "[CLICK 2] Bước 2: Thay đầu hàn theo lịch 2 tuần/lần.\n"
         "[CLICK 3] Bước 3: Đào tạo lại thợ mới theo tiêu chuẩn.\n"
         "[CLICK 4] Bước 4: Ban hành tiêu chuẩn góc hàn.\n"
         "[CLICK 5] Bước 5: Kiểm tra đầu ca bằng phiếu kiểm.")

# ---------- 8 evidence photos (unstretched, same frame) ----------
s = slides[7]
style_title(s, "Hình ảnh trước và sau cải tiến")
before = find(s, "Anh truoc")
after = find(s, "Anh sau")
for pic in (before, after):
    pic.width, pic.height = I(5.6), I(4.2)
before.left, before.top = I(0.8), I(1.65)
after.left, after.top = I(6.95), I(1.65)
lab_before = find(s, "TextBox 4")
lab_before.name = "Nhan truoc"
lab_before.left, lab_before.top, lab_before.width, lab_before.height = I(0.8), I(6.0), I(5.6), I(0.45)
set_text(lab_before, "TRƯỚC", 20, ACCENT, bold=True, align=PP_ALIGN.CENTER, heading=True)
lab_after = find(s, "TextBox 5")
lab_after.name = "Nhan sau"
lab_after.left, lab_after.top, lab_after.width, lab_after.height = I(6.95), I(6.0), I(5.6), I(0.45)
set_text(lab_after, "SAU", 20, PRIMARY, bold=True, align=PP_ALIGN.CENTER, heading=True)
notes(s, "[T=0] Mối hàn trước có nhiều rỗ khí và bắn tóe.\n"
         "[CLICK 1] Sau cải tiến mối hàn đều.")
plan_clicks["8"] = [["Anh sau", "Nhan sau"]]

# ---------- 9 result (two big numbers, no star / no "!!!") ----------
s = slides[8]
style_title(s, "Kết quả đạt được")
for sh in list(s.shapes):
    if sh.name not in ("TextBox 1",):
        drop(sh)
tbox(s, "So truoc", 1.0, 1.95, 4.2, 1.1, "4,1%", 54, INK, bold=True, heading=True)
tbox(s, "Nhan so truoc", 1.0, 3.1, 4.2, 0.45, "Trước cải tiến", 20, GREY)
tbox(s, "Mui ten", 5.35, 2.0, 2.6, 0.8, "→", 44, PRIMARY, bold=True, align="c", heading=True)
tbox(s, "So sau", 7.9, 1.95, 4.2, 1.1, "1,2%", 54, PRIMARY, bold=True, heading=True)
tbox(s, "Nhan so sau", 7.9, 3.1, 4.2, 0.45, "Sau cải tiến", 20, PRIMARY)
tbox(s, "Ket luan", 1.0, 5.1, 11.3, 0.7, "Đạt mục tiêu dưới 2% — duy trì kết quả.", 20, ACCENT, bold=True)
notes(s, "[T=0] Trước cải tiến, tỉ lệ lỗi hàn là 4,1%.\n"
         "[CLICK 1] Sau cải tiến còn 1,2% — đạt mục tiêu dưới 2%.")
plan_clicks["9"] = [["So sau", "Nhan so sau", "Ket luan"]]

# ---------- 10 thanks (same style as cover) ----------
s = slides[9]
for sh in list(s.shapes):
    if sh.name != "TextBox 1":
        drop(sh)
set_bg(s, PRIMARY)
title = find(s, "TextBox 1")
title.left, title.top, title.width, title.height = I(0.9), I(2.7), I(11.6), I(1.2)
set_text(title, "Cảm ơn đã lắng nghe!", 44, WHITE, bold=True)
tbox(s, "Phu de cam on", 0.9, 4.1, 11.6, 0.5, "Nhóm QCC Ánh Dương — 2026", 20, PALE)
notes(s, "[T=0] Cảm ơn mọi người đã lắng nghe.")
plan_clicks["10"] = []

# ---------- 11 appendix (original table, kept whole) ----------
app = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(app, WHITE)
for ph in list(app.placeholders):
    drop(ph)
app.shapes._spTree.append(copy.deepcopy(table_el))
tbl = [sh for sh in app.shapes if sh.has_table][0]
tbl.name = "Bang phu luc"
tbl.left, tbl.top, tbl.width, tbl.height = I(0.45), I(1.35), I(12.4), I(4.9)
widths = [0.6, 1.75, 1.0, 1.3, 1.3, 1.3, 1.15, 4.0]
for i, w in enumerate(widths):
    tbl.table.columns[i].width = I(w)
for row in tbl.table.rows:
    row.height = I(0.5)
for r, row in enumerate(tbl.table.rows):
    for c, cell in enumerate(row.cells):
        cell.margin_left = cell.margin_right = I(0.03)
        cell.margin_top = cell.margin_bottom = I(0.02)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(PRIMARY if r == 0 else WHITE)
        for para in cell.text_frame.paragraphs:
            para.alignment = PP_ALIGN.RIGHT if (c in (0, 1, 2, 3) and r > 0) else PP_ALIGN.LEFT
            for run in para.runs:
                run.font.size = Pt(16)
                run.font.name = FONT
                run.font.bold = r == 0
                run.font.color.rgb = rgb(WHITE if r == 0 else INK)
        tcPr = cell._tc.get_or_add_tcPr()
        for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
            for old in tcPr.findall(qn(tag)):
                tcPr.remove(old)
        for tag, edge in (("a:lnT", True), ("a:lnB", True), ("a:lnL", False), ("a:lnR", False)):
            ln = etree.Element(qn(tag), w=str(Pt(0.75)) if edge else "0")
            if edge:
                fill = etree.SubElement(ln, qn("a:solidFill"))
                etree.SubElement(fill, qn("a:srgbClr"), val="C9C9C9")
            else:
                etree.SubElement(ln, qn("a:noFill"))
            tcPr.insert(0, ln)
tbox(app, "Tieu de phu luc", 0.55, 0.35, 12.1, 0.8, "Phụ lục: kết quả theo dõi sau cải tiến", 32, PRIMARY,
     bold=True, heading=True)
notes(app, "[T=0] Phụ lục: bảng đầy đủ 6 tuần để tra cứu.")
set_bg(slides[0], PRIMARY)

static = ART / "qcc-dong-bo-dsh.static.pptx"
prs.save(str(static))
print("static saved", static, "slides", len(prs.slides))

# ---------------------------------------------------------------- step C: motion (clean first, add after)
plan = {"transitions": plan_trans, "clicks": plan_clicks}
(TASK / "inputs" / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
out = ART / "qcc-dong-bo-dsh.pptx"
summary = tools.apply_motion(str(static), plan, str(out))
print("motion", json.dumps(summary, ensure_ascii=False))

# ---------------------------------------------------------------- step D: checks (rung 1)
lost = tools.missing_numbers(str(SRC), str(out))
print("numbers missing:", lost)
(PREVIEW / "inventory-original.txt").write_text(tools.inventory(str(SRC)), encoding="utf-8")
(PREVIEW / "inventory-after.txt").write_text(tools.inventory(str(out)), encoding="utf-8")
print("inventory written")
