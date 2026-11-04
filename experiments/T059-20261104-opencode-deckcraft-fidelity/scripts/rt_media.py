import csv, os
from pathlib import Path
from pptx import Presentation
from pptx.oxml.ns import qn

rows = []
for f in sorted(Path('workspace/decks').glob('*.pptx')):
    if '.static.' in f.name or f.stem == 'kind_probe':
        continue
    rt = Path('workspace/rt') / f'{f.stem}-roundtrip.pptx'
    if not rt.exists():
        continue
    for label, path in (('original', f), ('roundtrip', rt)):
        p = Presentation(str(path))
        counts = {'slides': len(p.slides), 'shapes': 0, 'pictures': 0, 'svg_blips': 0, 'charts': 0, 'groups': 0}
        for s in p.slides:
            for sh in s.shapes:
                counts['shapes'] += 1
                if getattr(sh, 'has_chart', False):
                    counts['charts'] += 1
                if sh.shape_type == 13:
                    counts['pictures'] += 1
                if sh._element.tag == qn('p:grpSp'):
                    counts['groups'] += 1
                counts['svg_blips'] += len(sh._element.findall(
                    './/{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip'))
        rows.append({'deck': f.stem, 'source': label, 'width_pt': round(p.slide_width / 12700),
                     'height_pt': round(p.slide_height / 12700), **counts})

out = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts/roundtrip_media.csv')
with open(out, 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
for r in rows:
    print(r)
