"""T087 demo: a 5-slide deck built by following skills/pptx step by step.

Static deck only; motion is written afterwards by pptx_tools.py from plan.json.
Content is factual (no invented figures). Portraits: Wikimedia Commons, public
domain, prepared in T066 (see experiments/T066-…/inputs/SOURCES.md).
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "experiments/T066-20261104-opencode-triet-hoc-ch1/inputs/assets"
OUT = Path(__file__).resolve().parents[1] / "artifacts" / "demo-triet-hoc.static.pptx"

RED, DEEP, CREAM = RGBColor(0xC1, 0x12, 0x1F), RGBColor(0x7A, 0x0C, 0x14), RGBColor(0xF7, 0xF1, 0xE8)
GOLD, INK, SOFT = RGBColor(0xE8, 0xB0, 0x4B), RGBColor(0x2A, 0x14, 0x14), RGBColor(0x6B, 0x55, 0x52)
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


def rect(s, name, x, y, w, h, color, shape=MSO_SHAPE.RECTANGLE):
    r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    r.name = name
    r.fill.solid()
    r.fill.fore_color.rgb = color
    r.line.fill.background()
    r.shadow.inherit = False
    return r


def line(s, name, x1, y1, x2, y2, color, pt):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.name = name
    c.line.color.rgb = color
    c.line.width = Pt(pt)
    return c


def portrait(s, who, x, y, d):
    p = s.shapes.add_picture(str(ASSETS / f"{who}-circle.png"), Inches(x), Inches(y), Inches(d), Inches(d))
    p.name = f"!!{who}"
    return p


# 1. Cover: title left, the three portraits clustered on a deeper panel (they travel on to slide 2).
s = slide(RED)
rect(s, "Panel", 8.15, 0, W - 8.15, H, DEEP)
text(s, "Eyebrow", M, 1.45, 6.5, 0.4, "CHƯƠNG 1 · KHÁI LUẬN", 14, GOLD, bold=True, tracking=300)
text(s, "Tieu de", M, 1.95, 7.2, 2.6, ["TRIẾT HỌC", "MÁC – LÊNIN"], 60, CREAM, HEAD, bold=True, spacing=1.0)
line(s, "Gach vang", M, 4.55, M + 1.3, 4.55, GOLD, 3)
text(s, "Phu de", M, 4.85, 6.6, 1.0, "Từ thế giới quan đến phương pháp luận", 22, CREAM)
portrait(s, "marx", 8.75, 0.75, 2.75)
portrait(s, "engels", 10.45, 2.55, 2.35)
portrait(s, "lenin", 8.85, 4.35, 2.55)

# 2. Timeline: the same portraits land in a row on one axis; each landmark is one click.
s = slide(CREAM)
text(s, "Eyebrow", M, 0.6, 8, 0.4, "BA MỐC", 14, RED, bold=True, tracking=300)
text(s, "Tieu de", M, 1.05, 11.5, 0.9, "Một dòng chảy: từ lý luận đến cách mạng", 36, RED, HEAD, bold=True)
centers = (2.75, 6.67, 10.58)
line(s, "Truc", M, 4.55, W - M, 4.55, DEEP, 1.5)
facts = (("marx", "1848", "C. Mác", "Tuyên ngôn của Đảng Cộng sản, viết cùng Ph. Ăngghen"),
         ("engels", "1878", "Ph. Ăngghen", "Chống Đuy-rinh: trình bày có hệ thống triết học mácxít"),
         ("lenin", "1909", "V. I. Lênin", "Chủ nghĩa duy vật và chủ nghĩa kinh nghiệm phê phán"))
for cx, (who, year, name, work) in zip(centers, facts):
    portrait(s, who, cx - 1.05, 2.05, 2.1)
    rect(s, f"Moc {year}", cx - 0.11, 4.44, 0.22, 0.22, RED, MSO_SHAPE.OVAL)
    text(s, f"Nam {year}", cx - 1.8, 4.85, 3.6, 0.55, year, 26, RED, HEAD, bold=True, align=PP_ALIGN.CENTER)
    text(s, f"Ghi {year}", cx - 1.8, 5.45, 3.6, 1.4, [name, work], 18, INK, align=PP_ALIGN.CENTER, spacing=1.15)

# 3. The basic question: two answers side by side, then the chosen stance.
s = slide(DEEP)
text(s, "Eyebrow", M, 0.6, 9, 0.4, "VẤN ĐỀ CƠ BẢN CỦA TRIẾT HỌC", 14, GOLD, bold=True, tracking=300)
text(s, "Tieu de", M, 1.05, 11.7, 0.9, "Vật chất hay ý thức: cái nào có trước?", 36, CREAM, HEAD, bold=True)
line(s, "Duong chia", W / 2, 2.35, W / 2, 5.25, PINK, 1)
text(s, "Duy vat", M, 2.35, 5.2, 0.6, "Chủ nghĩa duy vật", 26, CREAM, HEAD, bold=True)
text(s, "Duy vat y", M, 3.1, 5.2, 1.6, "Vật chất có trước, quyết định ý thức.", 22, PINK)
text(s, "Duy tam", W / 2 + 0.5, 2.35, 5.2, 0.6, "Chủ nghĩa duy tâm", 26, CREAM, HEAD, bold=True)
text(s, "Duy tam y", W / 2 + 0.5, 3.1, 5.2, 1.6, "Ý thức có trước, sinh ra và quyết định vật chất.", 22, PINK)
line(s, "Gach chon", M, 4.3, M + 2.2, 4.3, GOLD, 4)
text(s, "Ket luan", M, 5.6, 11.7, 1.0,
     "Triết học Mác – Lênin đứng trên lập trường duy vật biện chứng.", 26, GOLD, HEAD, bold=True)

# 4. Quote: one sentence, nothing else competes.
s = slide(RED)
text(s, "Ngoac kep", M, 1.55, 1.5, 1.5, "“", 120, GOLD, HEAD, bold=True)
text(s, "Trich dan", 2.0, 2.4, 10.2, 2.6,
     ["Các nhà triết học đã chỉ giải thích thế giới bằng nhiều cách khác nhau;",
      "song vấn đề là cải tạo thế giới."], 36, CREAM, HEAD, spacing=1.2)
line(s, "Gach vang", 2.0, 5.05, 3.2, 5.05, GOLD, 3)
text(s, "Nguon", 2.0, 5.25, 9, 0.5, "C. Mác · Luận cương về Phoiơbắc, 1845", 14, PINK)

# 5. What to take away: three rows, one per click.
s = slide(CREAM)
text(s, "Eyebrow", M, 0.6, 8, 0.4, "KẾT", 14, RED, bold=True, tracking=300)
text(s, "Tieu de", M, 1.05, 11.5, 0.9, "Ba điều mang theo", 36, RED, HEAD, bold=True)
s.shapes[-1].top = Inches(1.05)
rows = (("Câu hỏi nền tảng", "Giữa vật chất và ý thức, cái nào có trước, cái nào quyết định?"),
        ("Cách nhìn biện chứng", "Sự vật luôn liên hệ với nhau, vận động và phát triển."),
        ("Lý luận gắn với thực tiễn", "Giải thích thế giới là để cải tạo nó."))
for i, (head, body) in enumerate(rows):
    y = 2.3 + i * 1.45
    text(s, f"So {i + 1}", M, y, 1.0, 0.7, f"0{i + 1}", 26, RED, HEAD, bold=True)
    text(s, f"Y {i + 1}", M + 1.2, y, 10.3, 1.2, [head, body], 22, INK, spacing=1.2)
    s.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
    s.shapes[-1].text_frame.paragraphs[0].runs[0].font.size = Pt(26)
line(s, "Duong cuoi", M, 6.55, W - M, 6.55, PINK, 1)
text(s, "Nguon anh", M, 6.7, 11, 0.4, "Ảnh chân dung: Wikimedia Commons, phạm vi công cộng.", 14, SOFT)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(OUT)
