import csv, glob, collections
from pathlib import Path

out = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts')
rows, effects, pp = [], [], []
for f in glob.glob('workspace/rt_out/*/roundtrip.csv'):
    rows += list(csv.DictReader(open(f, encoding='utf-8')))
for f in glob.glob('workspace/rt_out/*/roundtrip_effects.csv'):
    effects += list(csv.DictReader(open(f, encoding='utf-8')))
for f in glob.glob('workspace/rt_out/*/roundtrip_pp.csv'):
    pp += list(csv.DictReader(open(f, encoding='utf-8')))
rows.sort(key=lambda r: (r['deck'], int(r['slide']), r['node']))
effects.sort(key=lambda r: (r['deck'], int(r['slide']), r['status'], int(r['spid'] or 0)))
pp.sort(key=lambda r: (r['deck'], int(r['slide'])))
for name, data in (('roundtrip.csv', rows), ('roundtrip_effects.csv', effects), ('roundtrip_pp.csv', pp)):
    with open(out / name, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
        w.writeheader(); w.writerows(data)
    print(name, len(data))

print('\n== node changes ==')
agg = collections.defaultdict(lambda: [0, 0, 0])
for r in rows:
    if r['node'] in ('transition',):
        continue
    agg[r['node']][0] += int(r['original'] or 0)
    agg[r['node']][1] += int(r['roundtrip'] or 0)
    if int(r['delta'] or 0):
        agg[r['node']][2] += 1
for node, (a, b, changed) in sorted(agg.items()):
    if a != b:
        print(f"{node:12s} orig {a:5d} rt {b:5d} delta {b-a:+5d} slides-changed {changed}")

print('\n== effect rewrites ==')
for status in ('lost', 'added'):
    print(status)
    c = collections.Counter()
    for r in effects:
        if r['status'] == status:
            c[(r['class'], r['preset'], r['node'], r['props'], r['children'])] += int(r['count'])
    for k, n in c.most_common():
        print('  ', n, k)

print('\n== PowerPoint parse ==')
for r in pp:
    if int(r['lost'] or 0) or int(r['added'] or 0) or int(r['behaviors_lost'] or 0) or r['transition_equal'] != 'True':
        print(f"{r['deck']:24s} s{r['slide']:>2s} fx {r['effects_original']}->{r['effects_roundtrip']} lost {r['lost']} added {r['added']} beh {r['behaviors_original']}->{r['behaviors_roundtrip']} tr {r['transition_original']}->{r['transition_roundtrip']}")
