"""T093 rehearsal input: a deliberately patchwork QCC deck, as if three colleagues
had each made a few slides. Every number is synthetic (made up for the rehearsal)
and the cover says so. The two "photos" are drawn here with Pillow.

What is wrong on purpose (the harmonising agent should find it with
`pptx_tools.py inventory` and its own eyes):
- five fonts, a dozen sizes, a different title place and colour on each slide;
- a 3D column chart and a 3D pie with default Office colours;
- a long paragraph, a dense 8-column table, a bullet list that is really a process;
- a fishbone drawn too big (off the slide, over the title), animated part by part;
- two stretched photos with different frames;
- bounce, spin, fly-in, teeter and five different transitions.
"""
import random
import sys
from pathlib import Path

from lxml import etree as E
from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import pptx_animator as anim  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "artifacts" / "qcc-chap-va.pptx"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def text(s, x, y, w, h, lines, font, size, color="000000", bold=False, align=None, shadow=False):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate([lines] if isinstance(lines, str) else lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align:
            p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.name, r.font.size, r.font.bold = font, Pt(size), bold
        r.font.color.rgb = RGBColor.from_string(color)
        if shadow:
            rpr = r._r.get_or_add_rPr()
            eff = E.SubElement(rpr, qn("a:effectLst"))
            sh = E.SubElement(eff, qn("a:outerShdw"), blurRad="38100", dist="38100", dir="2700000", algn="tl")
            E.SubElement(E.SubElement(sh, qn("a:srgbClr"), val="000000"), qn("a:alpha"), val="60000")
            # effectLst must come after the fill in rPr
            rpr.remove(eff)
            rpr.insert(list(rpr).index(rpr.find(qn("a:solidFill"))) + 1, eff)
    return box


def bg(s, hex_):
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = RGBColor.from_string(hex_)


def transition(s, xml):
    s._element.append(E.fromstring(f'<p:transition xmlns:p="{anim.P}" spd="slow">{xml}</p:transition>'))


def clicks(s, groups, chain="after", ms=900):
    """groups: list of clicks; each click is a list of (shape, preset[, extra])."""
    out = []
    for n, group in enumerate(groups, 1):
        effects = []
        for k, item in enumerate(group):
            shape, preset = item[0], item[1]
            eff = {"preset": preset, "spid": str(shape.shape_id), "trigger": "click" if k == 0 else chain,
                   "duration_ms": ms}
            if len(item) > 2:
                eff.update(item[2])
            effects.append(eff)
        out.append({"id": f"c{n}", "start": "click", "effects": effects})
    anim.apply_timeline(s._element, out)


def notes(s, line):
    s.notes_slide.notes_text_frame.text = line


def make_3d(chart, pie=False):
    """python-pptx writes only flat charts; turn one into the 3D look people paste in."""
    cs = chart._chartSpace
    plot = cs.find(f".//{{{C}}}plotArea")
    flat = plot.find(f"{{{C}}}{'pieChart' if pie else 'barChart'}")
    flat.tag = f"{{{C}}}{'pie3DChart' if pie else 'bar3DChart'}"
    for drop in ("overlap", "firstSliceAng"):
        for n in flat.findall(f"{{{C}}}{drop}"):
            flat.remove(n)
    if not pie:
        flat.find(f"{{{C}}}axId").addprevious(E.Element(f"{{{C}}}shape", val="box"))
    view = E.fromstring(f'<c:view3D xmlns:c="{C}"><c:rotX val="{30 if pie else 15}"/>'
                        f'<c:rotY val="{0 if pie else 20}"/><c:rAngAx val="{0 if pie else 1}"/></c:view3D>')
    if not pie:
        view.find(f"{{{C}}}rAngAx").addprevious(E.Element(f"{{{C}}}depthPercent", val="100"))
    plot.addprevious(view)


def weld_photo(path, good, seed):
    """A plain drawing of a weld seam on steel: smooth (after) or rough with spatter (before)."""
    rnd = random.Random(seed)
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), (122, 128, 134))
    d = ImageDraw.Draw(img)
    for _ in range(9000):  # brushed steel
        x, y = rnd.randrange(w), rnd.randrange(h)
        g = rnd.randrange(100, 160)
        d.line([(x, y), (x + rnd.randrange(20, 80), y)], fill=(g, g + 4, g + 9))
    cy = h // 2
    for x in range(80, w - 80, 14):  # bead ripples
        jitter = 0 if good else rnd.randrange(-22, 22)
        r = 46 if good else rnd.randrange(30, 60)
        shade = 182 if good else rnd.randrange(120, 190)
        d.ellipse([x - r, cy - r + jitter, x + r, cy + r + jitter], fill=(shade, shade - 12, shade - 30),
                  outline=(90, 80, 70))
    if not good:
        for _ in range(70):  # spatter and pores
            x, y = rnd.randrange(60, w - 60), cy + rnd.choice([-1, 1]) * rnd.randrange(70, 300)
            r = rnd.randrange(3, 11)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(70, 62, 55))
        for _ in range(12):
            x, y = rnd.randrange(150, w - 150), cy + rnd.randrange(-25, 25)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(35, 30, 28))
    img.filter(ImageFilter.GaussianBlur(1.2)).save(path, quality=88)


# 1. Cover --------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
bg(s, "2E75B6")
t1 = text(s, 1.0, 2.0, 11.3, 1.6, "GIẢM TỈ LỆ LỖI HÀN TẠI DÂY CHUYỀN B", "Times New Roman", 44, "FFC000",
          bold=True, align=PP_ALIGN.CENTER, shadow=True)
t2 = text(s, 1.0, 3.8, 11.3, 0.8, "Nhóm QCC Ánh Dương – 2026", "Arial", 24, "FFFFFF", align=PP_ALIGN.CENTER)
t3 = text(s, 1.0, 6.6, 11.3, 0.5, "Dữ liệu giả lập để diễn tập – không phải số liệu thật", "Arial", 12, "DDEBF7",
          align=PP_ALIGN.CENTER)
gear = s.shapes.add_shape(MSO_SHAPE.GEAR_9, Inches(11.2), Inches(0.4), Inches(1.6), Inches(1.6))
gear.fill.solid()
gear.fill.fore_color.rgb = RGBColor(0xFF, 0xC0, 0x00)
clicks(s, [[(t1, "ppt:bounce")], [(t2, "ppt:fly")], [(gear, "spin", {"by_deg": 360})]])
transition(s, '<p:split orient="vert" dir="out"/>')
notes(s, "Chào mọi người, nhóm Ánh Dương xin trình bày đề tài QCC năm 2026.")

# 2. Why this topic: one long paragraph --------------------------------------------
s = prs.slides.add_slide(BLANK)
title = text(s, 0.3, 0.2, 9, 0.9, "1. Lý do chọn đề tài", "Arial", 32, "00B050", bold=True)
para = text(s, 0.6, 1.4, 12.0, 5.2,
            "Trong 6 tháng đầu năm, tỉ lệ lỗi hàn tại dây chuyền B luôn ở mức cao, trung bình khoảng 4,1%, "
            "cao gấp đôi mục tiêu 2% của nhà máy. Lỗi hàn làm tăng thời gian sửa chữa, tăng chi phí vật tư và "
            "gây chậm giao hàng cho khách hàng. Ngoài ra, khách hàng đã có 2 lần phản hồi về chất lượng mối hàn "
            "trong quý II. Vì vậy nhóm chọn đề tài giảm tỉ lệ lỗi hàn tại dây chuyền B xuống dưới 2% trong vòng "
            "3 tháng, đồng thời chuẩn hóa thao tác hàn để duy trì kết quả lâu dài.", "Calibri", 20, "000000")
clicks(s, [[(title, "ppt:fly")], [(para, "ppt:fly")]])
transition(s, '<p:push dir="u"/>')

# 3. Current state: 3D column chart ------------------------------------------------
s = prs.slides.add_slide(BLANK)
bg(s, "F2F2F2")
text(s, 2.0, 0.3, 9.3, 0.9, "HIỆN TRẠNG TỈ LỆ LỖI HÀN (%)", "Times New Roman", 30, "1F4E79", bold=True,
     align=PP_ALIGN.CENTER)
data = CategoryChartData(number_format="0.0")
data.categories = ["T1", "T2", "T3", "T4", "T5", "T6"]
data.add_series("Tỉ lệ lỗi", (3.8, 4.2, 4.5, 3.9, 4.3, 3.9))
data.add_series("Mục tiêu", (2, 2, 2, 2, 2, 2))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(1.2), Inches(1.3), Inches(10.9), Inches(5.8), data)
gf.name = "Bieu do loi"
gf.chart.has_legend = True
gf.chart.legend.position = XL_LEGEND_POSITION.BOTTOM
gf.chart.plots[0].has_data_labels = True
make_3d(gf.chart)
transition(s, '<p:cover dir="l"/>')
notes(s, "Tỉ lệ lỗi các tháng đều trên 3,8%, trung bình 4,1%.")

# 4. Fishbone: too big, animated bone by bone --------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only
s.shapes.title.text = "Phân tích nguyên nhân – Biểu đồ xương cá"
spine = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(-0.4), Inches(4.3), Inches(11.0), Inches(4.3))
spine.line.width, spine.line.color.rgb = Pt(4.5), RGBColor(0x40, 0x40, 0x40)
head = s.shapes.add_shape(MSO_SHAPE.PENTAGON, Inches(11.0), Inches(3.5), Inches(2.9), Inches(1.6))
head.fill.solid()
head.fill.fore_color.rgb = RGBColor(0xC0, 0x00, 0x00)
head.text_frame.text = "Lỗi hàn 4,1%"
head.text_frame.paragraphs[0].runs[0].font.size = Pt(26)
head.text_frame.paragraphs[0].runs[0].font.bold = True
bones = (("Con người", ("Thợ mới chưa được đào tạo", "Thao tác không đồng nhất"), 0.6, True),
         ("Máy móc", ("Đầu hàn mòn", "Dòng hàn dao động"), 5.6, True),
         ("Phương pháp", ("Chưa có tiêu chuẩn góc hàn", "Không kiểm tra đầu ca"), 0.6, False),
         ("Vật liệu", ("Que hàn ẩm", "Bề mặt phôi bẩn"), 5.6, False))
groups = [[(head, "appear")]]
for label, causes, x, top in bones:
    y_end = 1.0 if top else 7.6
    bone = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x + 1.4), Inches(y_end), Inches(x + 3.2), Inches(4.3))
    bone.line.width, bone.line.color.rgb = Pt(3), RGBColor(0x40, 0x40, 0x40)
    cat = text(s, x, (0.35 if top else 7.65), 3.6, 0.6, label, "Tahoma", 26, "C00000", bold=True)
    c1 = text(s, x + 2.0, (1.5 if top else 5.2), 3.6, 0.6, causes[0], "Tahoma", 24, "000000")
    c2 = text(s, x + 2.4, (2.6 if top else 6.3), 3.6, 0.6, causes[1], "Tahoma", 24, "000000")
    groups.append([(bone, "wipe-down" if top else "wipe-up"), (cat, "fade"), (c1, "fade"), (c2, "fade")])
arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(0.2), Inches(3.95), Inches(1.0), Inches(0.7))
arrow.fill.solid()
arrow.fill.fore_color.rgb = RGBColor(0xFF, 0xC0, 0x00)
groups.append([(arrow, "path", {"points": [{"x": 0, "y": 0}, {"x": 0.72, "y": 0}], "duration_ms": 2000})])
clicks(s, groups, chain="with", ms=500)
transition(s, '<p:wipe dir="r"/>')
notes(s, "Nhóm dùng 4M để tìm nguyên nhân. Mũi tên vàng chạy dọc xương sống tới vấn đề.")

# 5. Causes: 3D pie ----------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
text(s, 0.5, 0.4, 7, 0.8, "Tỉ lệ các nguyên nhân gây lỗi", "Calibri", 34, "7030A0", bold=True)
data = CategoryChartData(number_format='0"%"')
data.categories = ["Que hàn ẩm", "Đầu hàn mòn", "Thợ mới chưa đào tạo", "Bề mặt phôi bẩn", "Khác"]
data.add_series("Tỉ lệ", (38, 24, 16, 12, 10))
gf = s.shapes.add_chart(XL_CHART_TYPE.PIE, Inches(2.2), Inches(1.3), Inches(8.9), Inches(5.9), data)
gf.name = "Bieu do tron"
gf.chart.has_legend = True
gf.chart.legend.position = XL_LEGEND_POSITION.RIGHT
gf.chart.plots[0].has_data_labels = True
make_3d(gf.chart, pie=True)
transition(s, '<p:zoom/>')
notes(s, "Que hàn ẩm chiếm nhiều nhất, 38%.")

# 6. Dense table -------------------------------------------------------------------
s = prs.slides.add_slide(prs.slide_layouts[5])
s.shapes.title.text = "Kết quả theo dõi sau cải tiến"
rows = (("Tuần", "Sản lượng (mối)", "Mối lỗi", "Tỉ lệ lỗi (%)", "Que hàn", "Đầu hàn", "Thợ", "Ghi chú"),
        ("1", "5.000", "190", "3,8", "Đã sấy", "Cũ", "Chưa ĐT", "Bắt đầu"),
        ("2", "5.000", "150", "3,0", "Đã sấy", "Cũ", "Chưa ĐT", ""),
        ("3", "5.000", "120", "2,4", "Đã sấy", "Mới", "Đang ĐT", "Thay đầu hàn"),
        ("4", "5.000", "90", "1,8", "Đã sấy", "Mới", "Đã ĐT", ""),
        ("5", "5.000", "75", "1,5", "Đã sấy", "Mới", "Đã ĐT", ""),
        ("6", "5.000", "60", "1,2", "Đã sấy", "Mới", "Đã ĐT", "Đạt mục tiêu"))
tb = s.shapes.add_table(len(rows), len(rows[0]), Inches(0.4), Inches(1.6), Inches(12.5), Inches(4.6))
tb.name = "Bang theo doi"
for r, row in enumerate(rows):
    for c, v in enumerate(row):
        cell = tb.table.cell(r, c)
        cell.text = v
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                run.font.size, run.font.name = Pt(13), "Arial"
transition(s, '<p:push dir="l"/>')
notes(s, "Sau 6 tuần tỉ lệ lỗi giảm từ 3,8% xuống 1,2%.")

# 7. A process written as bullets ---------------------------------------------------
s = prs.slides.add_slide(BLANK)
title = text(s, 0.5, 0.3, 12, 0.9, "Các bước cải tiến đã thực hiện", "Times New Roman", 36, "C55A11", bold=True)
steps = ("Sấy que hàn trước mỗi ca", "Thay đầu hàn theo lịch 2 tuần/lần", "Đào tạo lại thợ mới theo tiêu chuẩn",
         "Ban hành tiêu chuẩn góc hàn", "Kiểm tra đầu ca bằng phiếu kiểm")
body = text(s, 1.0, 1.6, 11, 5, [f"• Bước {i}: {v}" for i, v in enumerate(steps, 1)], "Arial", 22, "262626")
clicks(s, [[(title, "teeter")], [(body, "ppt:bounce")]])
transition(s, '<p:split orient="horz" dir="in"/>')

# 8. Before / after photos, stretched --------------------------------------------------
s = prs.slides.add_slide(BLANK)
text(s, 3, 0.25, 7.3, 0.8, "Hình ảnh trước và sau cải tiến", "Calibri", 32, "000000", bold=True,
     align=PP_ALIGN.CENTER)
for name, good, seed in (("truoc", False, 3), ("sau", True, 5)):
    weld_photo(HERE / f"weld-{name}.jpg", good, seed)
p1 = s.shapes.add_picture(str(HERE / "weld-truoc.jpg"), Inches(0.5), Inches(1.6), Inches(6.6), Inches(3.3))
p1.name = "Anh truoc"
p2 = s.shapes.add_picture(str(HERE / "weld-sau.jpg"), Inches(7.6), Inches(1.3), Inches(4.4), Inches(5.0))
p2.name = "Anh sau"
text(s, 2.8, 5.2, 2, 0.6, "TRƯỚC", "Arial", 24, "C00000", bold=True)
text(s, 9.0, 6.4, 2, 0.6, "Sau", "Times New Roman", 20, "00B050")
transition(s, '<p:cover dir="u"/>')
notes(s, "Mối hàn trước có nhiều rỗ khí và bắn tóe; sau cải tiến mối hàn đều.")

# 9. Result, loud ------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
bg(s, "FFF2CC")
text(s, 0.5, 0.3, 12, 0.9, "KẾT QUẢ ĐẠT ĐƯỢC", "Arial", 36, "000000", bold=True)
before = text(s, 1.0, 2.0, 5, 1.2, "Trước: 4,1%", "Arial", 48, "C00000", bold=True, shadow=True)
after = text(s, 7.0, 2.0, 5, 1.2, "Sau: 1,2%", "Arial", 48, "00B050", bold=True, shadow=True)
star = s.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, Inches(5.6), Inches(4.1), Inches(2.0), Inches(2.0))
star.fill.solid()
star.fill.fore_color.rgb = RGBColor(0xFF, 0xC0, 0x00)
goal = text(s, 1.0, 6.1, 11.3, 0.9, "ĐẠT MỤC TIÊU DƯỚI 2% !!!", "Tahoma", 40, "FF0000", bold=True,
            align=PP_ALIGN.CENTER, shadow=True)
clicks(s, [[(before, "ppt:fly")], [(after, "ppt:fly")], [(star, "spin", {"by_deg": 720})], [(goal, "teeter")]])
transition(s, '<p:zoom dir="in"/>')

# 10. Thanks --------------------------------------------------------------------------------
s = prs.slides.add_slide(BLANK)
bg(s, "2E75B6")
thanks = text(s, 1.0, 2.6, 11.3, 1.4, "CẢM ƠN ĐÃ LẮNG NGHE!", "Tahoma", 54, "FFFFFF", bold=True,
              align=PP_ALIGN.CENTER, shadow=True)
smile = s.shapes.add_shape(MSO_SHAPE.SMILEY_FACE, Inches(5.9), Inches(4.4), Inches(1.5), Inches(1.5))
smile.fill.solid()
smile.fill.fore_color.rgb = RGBColor(0xFF, 0xC0, 0x00)
clicks(s, [[(thanks, "ppt:bounce")], [(smile, "spin", {"by_deg": 360})]])
transition(s, '<p:split orient="vert" dir="in"/>')

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(OUT)
