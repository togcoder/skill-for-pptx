from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import csv

out = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts/headline.jpg')
font_path = 'segoeui.ttf'


def font(size):
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


def crop(path, box=None):
    im = Image.open(path).convert('RGB').resize((960, 540), Image.LANCZOS)
    return im.crop(box) if box else im


rows = []
# 1. chart
rows.append((
    'Chart: markers, gridlines, legend',
    crop('workspace/t059/pp/T028_report_pro/slide-05.png'),
    crop('workspace/t059/dc/T028_report_pro/slide-05.png'),
))
# 2. svg icons
box = (30, 150, 930, 500)
rows.append((
    'SVG icons: transparent PNG fallback drawn',
    crop('workspace/t059/pp/coffee_report_photos/slide-03.png', box),
    crop('workspace/t059/dc/coffee_report_photos/slide-03.png', box),
))
# 3. morph KPI
morph = list(csv.DictReader(open('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts/morph.csv', encoding='utf-8')))
row = next(r for r in morph if r['deck'] == 'vi_chuyen_doi_so' and r['slide'] == '3' and r['t'] == '0.5')
pp_frame = Path('workspace/morph/vi_chuyen_doi_so-s03-frames') / f"f-{int(row['pp_frame']) + 1:04d}.jpg"
dc_frame = Path('workspace/morph/vi_chuyen_doi_so-s03-dc/frame-t0.500.png')
box = (20, 40, 940, 470)
rows.append((
    'Morph t=0.50: entrance shapes hidden vs drawn',
    crop(pp_frame, box),
    crop(dc_frame, box),
))

pw, ph, label_w, gap = 600, 338, 330, 12
W = label_w + 2 * pw + 3 * gap
H = 50 + len(rows) * (ph + 34)
sheet = Image.new('RGB', (W, H), 'white')
dr = ImageDraw.Draw(sheet)
dr.text((gap, 12), 'T059 — DeckCraft vs PowerPoint: three fidelity breaks', fill=(20, 20, 20), font=font(22))
for i, (label, a, b) in enumerate(rows):
    y = 50 + i * (ph + 34)
    dr.multiline_text((gap, y + 6), label, fill=(30, 30, 30), font=font(13), spacing=4)
    sheet.paste(a.resize((pw, ph), Image.LANCZOS), (label_w, y))
    sheet.paste(b.resize((pw, ph), Image.LANCZOS), (label_w + pw + gap, y))
    dr.text((label_w, y + ph + 6), 'PowerPoint Slide.Export / CreateVideo', fill=(60, 60, 60), font=font(12))
    dr.text((label_w + pw + gap, y + ph + 6), 'DeckCraft render (not PowerPoint)', fill=(60, 60, 60), font=font(12))
sheet.save(out, 'JPEG', quality=84, optimize=True)
print(out, out.stat().st_size)
