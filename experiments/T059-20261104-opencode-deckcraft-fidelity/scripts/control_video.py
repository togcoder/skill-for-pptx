from pathlib import Path
import sys
sys.path.insert(0, '.')
from scripts.deckcraft_fidelity import make_single_deck, create_video, extract_frames, detect_transition_start, load_frame, diff_map

src = 'workspace/decks/coffee_office_dynamic.pptx'
work = Path('workspace/control')
work.mkdir(parents=True, exist_ok=True)
for tag in ('a', 'b'):
    deck = work / f'control-{tag}-s04.pptx'
    video = work / f'control-{tag}-s04.mp4'
    make_single_deck(src, 4, deck)
    create_video(deck, video)
    extract_frames(video, work / f'control-{tag}-frames', fps=30)

a = sorted((work / 'control-a-frames').glob('*.jpg'))
b = sorted((work / 'control-b-frames').glob('*.jpg'))
sa = detect_transition_start(a, skip_s=0.5, threshold=0.2)
sb = detect_transition_start(b, skip_s=0.5, threshold=0.2)
a, b = a[sa:], b[sb:]
print('frames', len(a), len(b), 'starts', sa, sb)
import numpy as np
offsets, mins = [], []
for i in range(0, min(len(a), len(b)), 5):
    fa = load_frame(a[i])
    best = (999, 0)
    for off in range(-30, 31):
        j = i + off
        if 0 <= j < len(b):
            d = diff_map(fa, load_frame(b[j])).mean()
            if d < best[0]:
                best = (d, off)
    offsets.append(best[1]); mins.append(best[0])
    print(i, 'best', round(best[0], 2), 'offset', best[1])
print('median offset', np.median(offsets), 'median min diff', np.median(mins), 'max', max(mins))
