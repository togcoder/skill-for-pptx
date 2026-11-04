import csv, glob, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys

repo = Path('.')
out = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts')
(out / 'morph').mkdir(parents=True, exist_ok=True)

rows, hidden = [], []
for f in glob.glob('workspace/morph_out/*/morph.csv'):
    rows += list(csv.DictReader(open(f, encoding='utf-8')))
for f in glob.glob('workspace/morph_out/*/morph_hidden.csv'):
    hidden += list(csv.DictReader(open(f, encoding='utf-8')))
rows.sort(key=lambda r: (r['deck'], int(r['slide']), float(r['t'])))
hidden.sort(key=lambda r: (r['deck'], int(r['slide']), float(r['t']), int(r['spid'])))
for f in glob.glob('workspace/morph_out/*/morph/*.jpg'):
    shutil.copyfile(f, out / 'morph' / Path(f).name)

with open(out / 'morph.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
with open(out / 'morph_hidden.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(hidden[0].keys()))
    w.writeheader(); w.writerows(hidden)

print('morph rows', len(rows), 'hidden rows', len(hidden), 'strips', len(list((out / 'morph').glob('*.jpg'))))
print('decks', sorted(set(r['deck'] for r in rows)))

# headline per transition
print('\n== transition summary ==')
for key in sorted(set((r['deck'], r['slide']) for r in rows)):
    rs = [r for r in rows if (r['deck'], r['slide']) == key]
    means = [float(r['mean_abs']) for r in rs]
    p40 = [float(r['pct_gt40']) for r in rs]
    print(f"{key[0]:24s} s{key[1]:>2s} mean {sum(means)/len(means):6.2f} max {max(means):6.2f} p40 {sum(p40)/len(p40):5.2f}%")

print('\n== entrance-hidden states by opacity (t=0.25/0.5/0.75) ==')
for key in sorted(set((h['deck'], h['slide'], h['t']) for h in hidden)):
    hs = [h for h in hidden if (h['deck'], h['slide'], h['t']) == key]
    measurable = [h for h in hs if h['pp_alpha'] not in ('', None) and h['dc_alpha'] not in ('', None)]
    pp_hidden = sum(1 for h in measurable if float(h['pp_alpha']) < 0.15)
    dc_drawn = sum(1 for h in measurable if float(h['pp_alpha']) < 0.15 and float(h['dc_alpha']) > 0.25)
    both = sum(1 for h in measurable if float(h['pp_alpha']) < 0.15 and float(h['dc_alpha']) < 0.15)
    print(f"{key[0]:24s} s{key[1]:>2s} t={key[2]} measurable {len(measurable):2d} pp-hidden {pp_hidden:2d} dc-drawn-early {dc_drawn:2d} both-hidden {both:2d}")

# entrance-hidden evidence crop for vi slide 3 at t=0.5
try:
    deck, slide, t = 'vi_chuyen_doi_so', '3', '0.5'
    frame_dir = Path(f'workspace/morph/{deck}-s{int(slide):02d}-frames')
    dc_path = Path(f'workspace/morph/{deck}-s{int(slide):02d}-dc/frame-t0.500.png')
    pp_static = Path(f'workspace/t059/pp/{deck}/slide-{int(slide):02d}.png')
    # the matching video frame index from morph.csv
    row = next(r for r in rows if r['deck'] == deck and r['slide'] == slide and r['t'] == t)
    pp_frame = frame_dir / f"f-{int(row['pp_frame']) + 1:04d}.jpg"
    box = (48, 196, 912, 440)  # four KPI cards at 960x540
    def crop(p):
        im = Image.open(p).convert('RGB').resize((960, 540), Image.LANCZOS)
        return im.crop(box)
    panels = [('PowerPoint at t=0.50', crop(pp_frame)), ('DeckCraft render at t=0.50', crop(dc_path)),
              ('PowerPoint end state (Slide.Export)', crop(pp_static))]
    w, h = panels[0][1].size
    sheet = Image.new('RGB', (w, (h + 26) * 3 + 8), 'white')
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('segoeui.ttf', 16)
    except OSError:
        font = ImageFont.load_default()
    for i, (label, im) in enumerate(panels):
        y = i * (h + 26)
        dr.text((8, y + 4), label, fill=(20, 20, 20), font=font)
        sheet.paste(im, (0, y + 24))
    sheet.save(out / 'morph' / 'entrance-hidden-kpi.jpg', quality=86)
    print('wrote entrance-hidden-kpi.jpg')
except Exception as exc:
    print('entrance crop failed:', exc)
