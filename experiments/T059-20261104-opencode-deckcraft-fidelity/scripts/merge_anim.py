import csv, glob, shutil
from pathlib import Path

art = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts')
rows = []
for f in glob.glob('workspace/anim_out/*/roundtrip_animation.csv'):
    rows += list(csv.DictReader(open(f, encoding='utf-8')))
rows.append({
    'deck': 'control (same deck twice)', 'slide': '4', 'frames': '59', 'baseline': '0.0',
    'peak_frame': '0', 'peak_mean': '0.0', 'changed_frames': '0', 'first_changed': '',
    'last_changed': '', 'settled_mean': '0.0', 'same_end_state': 'True', 'strip': '',
})
rows.sort(key=lambda r: (r['deck'], int(r['slide'])))
with open(art / 'roundtrip_animation.csv', 'w', encoding='utf-8', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
for f in glob.glob('workspace/anim_out/*/morph/*.jpg'):
    shutil.copyfile(f, art / 'morph' / Path(f).name)
print('rows', len(rows), 'strips', len(glob.glob('workspace/anim_out/*/morph/*.jpg')))
for r in rows:
    print(r['deck'], r['slide'], 'peak', r['peak_mean'], 'settled', r['settled_mean'], 'changed', r['changed_frames'])
