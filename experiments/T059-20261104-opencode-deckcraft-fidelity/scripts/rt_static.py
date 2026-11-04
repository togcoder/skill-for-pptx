import sys
from pathlib import Path
sys.path.insert(0, '.')
from scripts.deckcraft_fidelity import powerpoint_export, compare_static

base = Path('workspace')
rows = []
for deck in sorted(base.glob('decks/*.pptx')):
    if '.static.' in deck.name or deck.stem == 'kind_probe':
        continue
    rt = base / 'rt' / f'{deck.stem}-roundtrip.pptx'
    if not rt.exists():
        continue
    pp_orig = base / 't059' / 'pp' / deck.stem
    pp_rt = base / 'rt_pp' / deck.stem
    if len(list(pp_rt.glob('slide-*.png'))) == 0:
        powerpoint_export(rt, pp_rt)
    s, _ = compare_static(deck, pp_orig, pp_rt)
    slides = [r for r in s if r['kind'] == '__slide__']
    print(deck.stem, 'slides', len(slides), 'mean', round(sum(float(r['mean_abs']) for r in slides) / len(slides), 4),
          'max', max(float(r['mean_abs']) for r in slides))
