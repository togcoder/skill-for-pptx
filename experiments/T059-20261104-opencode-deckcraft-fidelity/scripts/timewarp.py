from pathlib import Path
import numpy as np
from PIL import Image
import sys
sys.path.insert(0, '.')
from scripts.deckcraft_fidelity import detect_transition_start, load_frame, diff_map

deck = sys.argv[1]
a = sorted(Path(f'workspace/anim/anim-{deck}-original-s04-frames').glob('*.jpg'))
b = sorted(Path(f'workspace/anim/anim-{deck}-roundtrip-s04-frames').glob('*.jpg'))
sa = detect_transition_start(a, skip_s=0.5, threshold=0.2)
sb = detect_transition_start(b, skip_s=0.5, threshold=0.2)
a, b = a[sa:], b[sb:]
print('frames', len(a), len(b), 'starts', sa, sb)
offsets, mins = [], []
for i in range(0, min(len(a), len(b)), 3):
    fa = load_frame(a[i])
    best = (999, 0)
    for off in range(-45, 46):
        j = i + off
        if 0 <= j < len(b):
            d = diff_map(fa, load_frame(b[j])).mean()
            if d < best[0]:
                best = (d, off)
    offsets.append(best[1]); mins.append(best[0])
    print(i, 'best', round(best[0], 2), 'offset', best[1])
print('median offset', np.median(offsets), 'median min diff', np.median(mins), 'max min diff', max(mins))
