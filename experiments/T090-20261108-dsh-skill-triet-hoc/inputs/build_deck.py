"""T090 — Triết học Mác – Lênin, Chương 1 (bản ngắn 7 slide).

Built by following ``skills/pptx/`` (D011): a static deck first, then motion from
``plan.json`` with ``pptx_tools.py motion``. The written source is
``inputs/script.md`` (condensed from the T078 gold script); content is the
textbook summary already used in T066, no invented figures.

Static deck only. Run:
    python scripts/pptx_tools.py motion artifacts/T090-triet-hoc-ch1.static.pptx \
        inputs/plan.json -o artifacts/T090-triet-hoc-ch1.pptx

Images: red duotone circle cut-outs from T066 (Wikimedia Commons, public
domain; see experiments/T066-.../inputs/SOURCES.md).
"""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "experiments/T066-20261104-opencode-triet-hoc-ch1/inputs/assets"
OUT = Path(__file__).resolve().parents[1] / "artifacts" / "T090-triet-hoc-ch1.static.pptx"

RED = RGBColor(0xC1, 0x12, 0x1F)
DEEP = RGBColor(0x7A, 0x0C, 0x14)
CREAM = RGBColor(0xF7, 0xF1, 0xE8)
GOLD = RGBColor(0xE8, 0xB0, 0x4B)
INK = RGBColor(0x2A, 0x14, 0x14)
PINK = RGBColor(0xF2, 0xD7, 0xD3)
HEAD, BODY = "Palatino Linotype", "Arial"
W, H, M = 13.333, 7.5, 0.8

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)


def slide(bg):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    return s


def text(s, name, x, y, w, h, lines, size, color, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         spacing=1.1, anchor=MSO_ANCHOR.TOP, tracking=0):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    tf = box.text_frame
    tf.word_wrap, tf.auto_size, tf.vertical_anchor = True, MSO_AUTO_SIZE.NONE, anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate([lines] if isinstance(lines, str) else lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.line_spacing = align, spacing
        r = p.add_run()
        r.text = line
        f = r.font
        f.name, f.size, f.bold, f.color.rgb = font, Pt(size), bold, color
        if tracking:
            r._r.get_or_add_rPr().set("spc", str(tracking))
    return box


def rect(s, name, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE, border=None, border_pt=1.0):
    r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    r.name = name
    r.fill.solid()
    r.fill.fore_color.rgb = color
    if border is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = border
        r.line.width = Pt(border_pt)
    r.shadow.inherit = False
    return r


def line(s, name, x1, y1, x2, y2, color, pt):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = color
    c.line.width = Pt(pt)
    return c


def arrow(s, name, x, y, w, color):
    """Thin connector arrow, pointing right; wipe reveals it like a direction."""
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x + w), Inches(y))
    c.name = name
    c.line.color.rgb = color
    c.line.width = Pt(2.5)
    tail = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"))
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return c


def dot(s, name, x, y, d, color):
    return rect(s, name, x, y, d, d, color, shape=MSO_SHAPE.OVAL)


def portrait(s, name, x, y, d):
    files = {"Chan dung Mac": "marx-circle.png", "Chan dung Engels": "engels-circle.png",
             "Chan dung Lenin": "lenin-circle.png"}
    p = s.shapes.add_picture(str(ASSETS / files[name]), Inches(x), Inches(y), Inches(d), Inches(d))
    p.name = name
    return p


def title_block(s, eyebrow, title, fg, eyebrow_color):
    """The one repeated identity: eyebrow, title in the same place, thin gold rule."""
    text(s, "Eyebrow", M, 0.62, 9.0, 0.35, eyebrow, 14, eyebrow_color, bold=True, tracking=300)
    text(s, "Tieu de", M, 1.05, 11.7, 0.7, title, 32, fg, HEAD, bold=True)
    line(s, "Gach tieu de", M, 1.9, M + 1.3, 1.9, GOLD, 2)


def notes(s, body):
    s.notes_slide.notes_text_frame.text = body


# ---------------------------------------------------------------- 1. Bìa
s = slide(RED)
rect(s, "Nen phai", 8.2, 0, W - 8.2, H, DEEP)
line(s, "Duong vang", 7.95, 0.85, 7.95, 6.65, GOLD, 2)
dot(s, "Diem vang", 7.86, 0.76, 0.18, GOLD)
text(s, "Eyebrow", M, 1.3, 7.0, 0.4, "CHƯƠNG 1 · KHÁI LUẬN VỀ TRIẾT HỌC", 14, CREAM,
     bold=True, tracking=300)
text(s, "Tieu de", M, 1.75, 7.1, 2.6, ["TRIẾT HỌC", "MÁC – LÊNIN"], 64, CREAM, HEAD,
     bold=True, spacing=1.0)
line(s, "Gach vang", M, 4.55, M + 1.3, 4.55, GOLD, 3)
text(s, "Phu de", M, 4.85, 6.8, 1.1, "Từ thế giới quan đến phương pháp luận", 24, CREAM)
text(s, "Chan trang", M, 6.75, 7.4, 0.4, "Giáo trình Triết học Mác – Lênin · Chương 1", 14, PINK)
portrait(s, "Chan dung Mac", 8.75, 0.75, 2.75)
portrait(s, "Chan dung Engels", 10.45, 2.55, 2.35)
portrait(s, "Chan dung Lenin", 8.85, 4.35, 2.55)
notes(s, "[T=0] Chương 1 — Khái luận về triết học và triết học Mác – Lênin. Ba người ở bên phải là "
         "ba tác giả của học thuyết chúng ta sẽ đọc trong học kỳ này: C. Mác, Ph. Ăngghen, V. I. Lênin.")

# ---------------------------------------------------------------- 2. Hai niềm tin
s = slide(CREAM)
title_block(s, "MỞ ĐẦU", "Hai niềm tin, một câu hỏi", RED, RED)
text(s, "!!cau1", M, 2.5, 11.7, 1.1, "“Có công mài sắt, có ngày nên kim.”", 44, DEEP, HEAD,
     bold=True, spacing=1.05)
text(s, "!!cau2", M, 3.85, 11.7, 1.5, ["“Sống chết có mệnh,", "giàu sang do trời.”"], 44, DEEP, HEAD,
     bold=True, spacing=1.05)
text(s, "Ket luan", M, 5.9, 11.7, 0.7, "Dù bạn chọn câu nào, bạn vừa trả lời một câu hỏi triết học.",
     24, INK)
notes(s, "[T=0] Hai câu này chắc ai cũng từng nghe. Một câu nói cố gắng sẽ đổi được; câu kia nói mọi "
         "thứ do trời định. Bạn tin câu nào hơn?\n[CLICK 1] Dù bạn chọn câu nào, bạn vừa trả lời một câu "
         "hỏi triết học.")

# ---------------------------------------------------------------- 3. Vấn đề cơ bản
s = slide(DEEP)
title_block(s, "VẤN ĐỀ CƠ BẢN CỦA TRIẾT HỌC", "Vật chất hay ý thức: cái nào có trước?", CREAM, PINK)
line(s, "Duong chia", 6.67, 2.25, 6.67, 5.05, PINK, 1)
text(s, "Chu de vat chat", M, 2.25, 5.4, 0.45, "VẬT CHẤT CÓ TRƯỚC", 18, GOLD, bold=True, tracking=200)
text(s, "!!cau1", M, 2.8, 5.5, 1.5, "“Có công mài sắt, có ngày nên kim.”", 24, CREAM, HEAD)
text(s, "Nhan duy vat", M, 4.5, 5.2, 0.65, "DUY VẬT", 32, GOLD, bold=True, tracking=200)
text(s, "Chu de y thuc", 6.9, 2.25, 5.5, 0.45, "Ý THỨC CÓ TRƯỚC", 18, GOLD, bold=True, tracking=200)
text(s, "!!cau2", 6.9, 2.8, 5.6, 1.5, ["“Sống chết có mệnh,", "giàu sang do trời.”"], 24, CREAM, HEAD)
text(s, "Nhan duy tam", 6.9, 4.5, 5.2, 0.65, "DUY TÂM", 32, GOLD, bold=True, tracking=200)
line(s, "Gach chon", M, 5.35, M + 2.2, 5.35, GOLD, 3)
text(s, "Ket luan", M, 5.55, 11.7, 0.9, "Triết học Mác – Lênin đứng trên lập trường duy vật biện chứng.",
     24, GOLD, HEAD, bold=True)
notes(s, "[T=0] Câu hỏi nền của mọi triết học: giữa vật chất và ý thức, cái nào có trước, cái nào quyết "
         "định? Hai câu tục ngữ ban nãy đã trả lời hộ bạn.\n[CLICK 1] Ai cho vật chất có trước, người đó "
         "đứng về phía duy vật; ai cho ý thức có trước, người đó đứng về phía duy tâm.\n[CLICK 2] Triết "
         "học Mác – Lênin chọn chủ nghĩa duy vật, và chọn thêm phép biện chứng: duy vật biện chứng.")

# ---------------------------------------------------------------- 4. Bốn trạng thái
s = slide(CREAM)
title_block(s, "HAI CÁCH NHÌN", "Bốn trạng thái rời, hay một dòng chảy?", RED, RED)
centers = (1.9, 5.078, 8.256, 11.434)
for i, (name, label) in enumerate((("Hat", "Hạt"), ("Mam", "Mầm"),
                                   ("Cay", "Cây"), ("Bong", "Bông"))):
    text(s, f"Trang thai {name}", centers[i] - 1.1, 2.85, 2.2, 1.0, label, 44, RED, HEAD,
         bold=True, align=PP_ALIGN.CENTER)
for i in range(3):
    arrow(s, f"Mui ten {i + 1}", centers[i] + 1.18, 3.22,
          centers[i + 1] - centers[i] - 2.36, DEEP)
text(s, "Cach nhin A", M, 4.95, 11.7, 0.5, "Siêu hình: thấy từng trạng thái đứng riêng.", 24, INK)
text(s, "Ket luan", M, 5.85, 11.7, 0.7, "Biện chứng: thấy chúng trong liên hệ và vận động.",
     24, RED, HEAD, bold=True)
notes(s, "[T=0] Trả lời xong câu hỏi gốc, còn chuyện ta nhìn sự vật thế nào. Cách nhìn siêu hình thấy "
         "từng trạng thái đứng riêng: hạt là hạt, cây là cây.\n[CLICK 1] Cách nhìn biện chứng thấy chúng "
         "trong liên hệ và vận động: hạt mất đi để thành cây, cây lại cho ra hạt mới.")

# ---------------------------------------------------------------- 5. Ba nguồn, ba bộ phận
s = slide(DEEP)
title_block(s, "LÊNIN TÓM GỌN", "Ba nguồn gốc, ba bộ phận", CREAM, PINK)
rows = (("Triết học cổ điển Đức", "Triết học Mác – Lênin"),
        ("Kinh tế chính trị cổ điển Anh", "Kinh tế chính trị Mác – Lênin"),
        ("Chủ nghĩa xã hội không tưởng Pháp", "Chủ nghĩa xã hội khoa học"))
for i, (src, part) in enumerate(rows):
    y = 2.22 + i * 1.28
    text(s, f"Nguon {i + 1}", M, y + 0.08, 5.0, 0.8, src, 18, CREAM)
    arrow(s, f"Mui ten {i + 1}", 6.15, y + 0.25, 0.7, GOLD)
    text(s, f"Bo phan {i + 1}", 7.15, y, 5.4, 0.9, part, 24, GOLD, HEAD, bold=True)
text(s, "Ket luan", M, 6.15, 11.7, 1.0, ["Ba bộ phận, một chỉnh thể;",
                                         "triết học là nền móng phương pháp cho hai bộ phận kia."], 24, PINK)
notes(s, "[T=0] Lênin tóm gọn điều này trong một câu: ba nguồn gốc, ba bộ phận cấu thành. Triết học cổ "
         "điển Đức trở thành triết học Mác – Lênin; kinh tế chính trị cổ điển Anh trở thành kinh tế "
         "chính trị Mác – Lênin; chủ nghĩa xã hội không tưởng Pháp trở thành chủ nghĩa xã hội khoa học."
         "\n[CLICK 1] Ba bộ phận, một chỉnh thể — và triết học là nền móng phương pháp cho hai bộ phận kia.")

# ---------------------------------------------------------------- 6. Ba mốc
s = slide(RED)
title_block(s, "TỪ TRANG SÁCH ĐẾN ĐỜI SỐNG", "Ba mốc, một dòng chảy", CREAM, CREAM)
line(s, "Truc", M, 4.62, W - M, 4.62, CREAM, 1.5)
cx = (3.1, 6.67, 10.24)

portrait(s, "Chan dung Mac", cx[0] - 1.6, 2.0, 1.55)
portrait(s, "Chan dung Engels", cx[0] - 0.05, 2.05, 1.45)
dot(s, "Moc 1848", cx[0] - 0.11, 4.51, 0.22, GOLD)
text(s, "Nam 1848", cx[0] - 1.7, 4.85, 3.4, 0.55, "1848", 32, GOLD, HEAD, bold=True, align=PP_ALIGN.CENTER)
text(s, "Viec 1848", cx[0] - 1.7, 5.5, 3.4, 1.3, ["Mác · Ăngghen", "Tuyên ngôn của", "Đảng Cộng sản"],
     18, CREAM, align=PP_ALIGN.CENTER, spacing=1.15)

rect(s, "Sach", cx[1] - 0.8, 2.3, 1.6, 1.9, DEEP, border=GOLD, border_pt=1.5)
line(s, "Sach ghim", cx[1] - 0.66, 2.5, cx[1] - 0.66, 4.0, GOLD, 1.5)
text(s, "Sach chu", cx[1] - 0.5, 2.8, 1.2, 1.0, ["TƯ BẢN", "Tập I"], 14, GOLD, bold=True,
     align=PP_ALIGN.CENTER, spacing=1.1)
dot(s, "Moc 1867", cx[1] - 0.11, 4.51, 0.22, GOLD)
text(s, "Nam 1867", cx[1] - 1.7, 4.85, 3.4, 0.55, "1867", 32, GOLD, HEAD, bold=True, align=PP_ALIGN.CENTER)
text(s, "Viec 1867", cx[1] - 1.7, 5.5, 3.4, 1.2, ["C. Mác", "Tư bản, tập I"], 18, CREAM,
     align=PP_ALIGN.CENTER, spacing=1.15)

portrait(s, "Chan dung Lenin", cx[2] - 1.0, 2.0, 2.0)
dot(s, "Moc 1917", cx[2] - 0.11, 4.51, 0.22, GOLD)
text(s, "Nam 1917", cx[2] - 1.7, 4.85, 3.4, 0.55, "1917", 32, GOLD, HEAD, bold=True, align=PP_ALIGN.CENTER)
text(s, "Viec 1917", cx[2] - 1.7, 5.5, 3.4, 1.2, ["V. I. Lênin", "Cách mạng Tháng Mười"], 18, CREAM,
     align=PP_ALIGN.CENTER, spacing=1.15)
notes(s, "[T=0] Lý luận ấy không đứng yên trên trang sách.\n[CLICK 1] 1848, Mác và Ăngghen viết Tuyên "
         "ngôn của Đảng Cộng sản.\n[CLICK 2] 1867, Mác công bố tập I bộ Tư bản.\n[CLICK 3] 1917, Lênin "
         "đưa lý luận thành Cách mạng Tháng Mười.")

# ---------------------------------------------------------------- 7. Câu chốt
s = slide(DEEP)
text(s, "Ngoac kep", M, 1.35, 1.5, 1.0, "“", 64, GOLD, HEAD, bold=True)
text(s, "Trich dan 1", 1.9, 2.3, 10.9, 1.7, ["Các nhà triết học đã chỉ giải thích",
                                             "thế giới bằng nhiều cách khác nhau;"],
     44, CREAM, HEAD, spacing=1.15)
text(s, "Trich dan 2", 1.9, 4.55, 10.9, 0.9, "song vấn đề là cải tạo thế giới.", 44, GOLD, HEAD, bold=True)
line(s, "Gach vang", 1.9, 6.1, 3.4, 6.1, GOLD, 3)
text(s, "Nguon", 1.9, 6.3, 9.0, 0.4, "C. Mác · Luận cương về Phoiơbắc, 1845", 14, PINK)
notes(s, "[T=0] Năm 1845, Mác viết một câu sau này được khắc trên mộ ông: \"Các nhà triết học đã chỉ "
         "giải thích thế giới bằng nhiều cách khác nhau,\n[CLICK 1] song vấn đề là cải tạo thế giới.\"")

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(OUT.name)
