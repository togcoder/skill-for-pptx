"""Build the synthetic per-kind probe deck for T059.

Run from the repository root: ``python experiments/T059-.../scripts/build_kind_probe.py``.
Writes ``workspace/decks/kind_probe.pptx`` and ``workspace/kind_probe/probe_picture.png``.
"""
from pathlib import Path
from lxml import etree
from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

work = Path('workspace/kind_probe')
work.mkdir(parents=True, exist_ok=True)

# synthetic raster picture: four-colour blocks with a diagonal
img = Image.new('RGB', (400, 260), (232, 226, 215))
d = ImageDraw.Draw(img)
for i, c in enumerate([(15, 118, 110), (180, 83, 47), (244, 162, 97), (40, 54, 79)]):
    d.rectangle([0, i * 65, 400, (i + 1) * 65], fill=c)
d.line([0, 0, 400, 260], fill=(255, 255, 255), width=6)
pic = work / 'probe_picture.png'
img.save(pic)

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(5.625)
slide = prs.slides.add_slide(prs.slide_layouts[6])

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'


def label(text, x, y):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(2.2), Inches(0.25))
    box.text_frame.text = text
    for p in box.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(10)
            r.font.name = 'Segoe UI'
            r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)


def rect(x, y, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(2.1), Inches(1.15))
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor(*fill)
    sh.line.fill.background()
    sh.adjustments[0] = 0.08
    return sh


def effect(sh, xml):
    spPr = sh._element.spPr
    old = spPr.find(qn('a:effectLst'))
    if old is not None:
        spPr.remove(old)
    el = etree.fromstring(f'<a:effectLst xmlns:a="{A}">{xml}</a:effectLst>')
    spPr.append(el)


def gradient(sh):
    spPr = sh._element.spPr
    old = spPr.find(qn('a:solidFill'))
    if old is not None:
        spPr.remove(old)
    el = etree.fromstring(
        f'<a:gradFill xmlns:a="{A}" rotWithShape="1"><a:gsLst>'
        f'<a:gs pos="0"><a:srgbClr val="0F766E"/></a:gs>'
        f'<a:gs pos="50000"><a:srgbClr val="F4A261"/></a:gs>'
        f'<a:gs pos="100000"><a:srgbClr val="B4532F"/></a:gs>'
        f'</a:gsLst><a:lin ang="2700000" scaled="1"/></a:gradFill>')
    # insert before a:ln if present, else append
    ln = spPr.find(qn('a:ln'))
    if ln is not None:
        ln.addprevious(el)
    else:
        spPr.append(el)


# row 1
label('text (3 lines)', 0.35, 0.2)
tb = slide.shapes.add_textbox(Inches(0.35), Inches(0.45), Inches(2.1), Inches(1.15))
tf = tb.text_frame
tf.word_wrap = True
for i, line in enumerate(['Direct orders', 'rose 12% in Q3', 'across six markets']):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = line
    for r in p.runs:
        r.font.size = Pt(15 if i == 0 else 11)
        r.font.name = 'Segoe UI'
        r.font.bold = i == 0
        r.font.color.rgb = RGBColor(0x28, 0x36, 0x4F)

label('picture (raster)', 2.75, 0.2)
slide.shapes.add_picture(str(pic), Inches(2.75), Inches(0.45), Inches(2.1), Inches(1.15))

label('chart (bar, 2 series)', 5.15, 0.2)
cd = CategoryChartData()
cd.categories = ['Jul', 'Aug', 'Sep']
cd.add_series('2025', (320, 340, 360))
cd.add_series('2026', (410, 520, 640))
gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(5.15), Inches(0.45), Inches(4.4), Inches(2.4), cd)
ch = gf.chart
ch.has_legend = True
ch.has_title = False
ch.plots[0].has_data_labels = False

# row 2
label('gradient (3 stops)', 0.35, 2.7)
gradient(rect(0.35, 2.95, (15, 118, 110)))

label('effect: outer shadow', 2.75, 2.7)
effect(rect(2.75, 2.95, (15, 118, 110)),
       '<a:outerShdw blurRad="127000" dist="63500" dir="5400000" rotWithShape="0">'
       '<a:srgbClr val="000000"><a:alpha val="45000"/></a:srgbClr></a:outerShdw>')

label('effect: glow', 5.15, 2.7)
effect(rect(5.15, 2.95, (180, 83, 47)),
       '<a:glow rad="127000"><a:srgbClr val="F4A261"><a:alpha val="60000"/></a:srgbClr></a:glow>')

label('effect: soft edge + bevel', 7.55, 2.7)
effect(rect(7.55, 2.95, (40, 54, 79)),
       '<a:softEdge rad="63500"/><a:sp3d><a:bevelT w="63500" h="25400"/></a:sp3d>')

# row 3
label('effect: reflection', 0.35, 4.4)
effect(rect(0.35, 4.65, (244, 162, 97)),
       '<a:reflection blurRad="6350" stA="50000" endA="300" endPos="55000" dist="38100" '
       'dir="5400000" sy="-100000" algn="bl" rotWithShape="0"/>')

label('gradient (2 stops)', 2.75, 4.4)
grad2 = rect(2.75, 4.65, (15, 118, 110))
spPr = grad2._element.spPr
solid = spPr.find(qn('a:solidFill'))
if solid is not None:
    spPr.remove(solid)
ln = spPr.find(qn('a:ln'))
spPr.insert(list(spPr).index(ln) if ln is not None else len(spPr), etree.fromstring(
    f'<a:gradFill xmlns:a="{A}"><a:gsLst>'
    f'<a:gs pos="0"><a:srgbClr val="0F766E"/></a:gs>'
    f'<a:gs pos="100000"><a:srgbClr val="B4532F"/></a:gs>'
    f'</a:gsLst><a:lin ang="2700000" scaled="1"/></a:gradFill>'))

label('text: Segoe UI Semibold', 5.15, 4.4)
tb2 = slide.shapes.add_textbox(Inches(5.15), Inches(4.65), Inches(2.1), Inches(0.5))
tb2.text_frame.text = 'Semibold family'
for p in tb2.text_frame.paragraphs:
    for r in p.runs:
        r.font.size = Pt(16)
        r.font.name = 'Segoe UI Semibold'
        r.font.color.rgb = RGBColor(0x28, 0x36, 0x4F)

label('text: Segoe UI + bold', 7.55, 4.4)
tb3 = slide.shapes.add_textbox(Inches(7.55), Inches(4.65), Inches(2.1), Inches(0.5))
tb3.text_frame.text = 'Bold flag'
for p in tb3.text_frame.paragraphs:
    for r in p.runs:
        r.font.size = Pt(16)
        r.font.name = 'Segoe UI'
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x28, 0x36, 0x4F)

out = Path('workspace/decks/kind_probe.pptx')
prs.save(out)
print(out, out.stat().st_size)
