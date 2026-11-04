import csv, collections, statistics, hashlib
from pathlib import Path

art = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts')
rows = list(csv.DictReader(open(art / 'fidelity.csv', encoding='utf-8')))
objs = list(csv.DictReader(open(art / 'fidelity_objects.csv', encoding='utf-8')))

print('## Deck table')
print('| Deck | Slides | Mean | Max slide | Mean >40 | Max >40 | Worst slide |')
print('|---|---:|---:|---:|---:|---:|---|')
for deck in sorted(set(r['deck'] for r in rows)):
    rs = [r for r in rows if r['deck'] == deck and r['kind'] == '__slide__']
    means = [float(r['mean_abs']) for r in rs]
    p40 = [float(r['pct_gt40']) for r in rs]
    worst = max(rs, key=lambda r: float(r['mean_abs']))
    print(f"| {deck} | {len(rs)} | {statistics.mean(means):.3f} | {max(means):.3f} | {statistics.mean(p40):.3f}% | {max(p40):.3f}% | s{worst['slide']} |")

print('\n## Kind table')
print('| Kind | Rows | Decks | Pixel share | Weighted mean | Weighted >40 | Max row mean |')
print('|---|---:|---:|---:|---:|---:|---:|')
kinds = collections.defaultdict(list)
for r in rows:
    if r['kind'] != '__slide__':
        kinds[r['kind']].append(r)
for kind, rs in sorted(kinds.items()):
    px = sum(int(r['pixels']) for r in rs)
    if not px:
        continue
    wm = sum(float(r['mean_abs']) * int(r['pixels']) for r in rs) / px
    wp = sum(float(r['pct_gt40']) * int(r['pixels']) for r in rs) / px
    share = sum(float(r['pixel_share']) for r in rs) / len(rs)
    print(f"| {kind} | {len(rs)} | {len(set(r['deck'] for r in rs))} | {share:.1f}% | {wm:.3f} | {wp:.3f}% | {max(float(r['mean_abs']) for r in rs):.3f} |")

print('\n## Chart rows')
print('| Deck | Slide | Mean | >40 | Pixels |')
print('|---|---:|---:|---:|---:|')
for r in rows:
    if r['kind'] == 'chart':
        print(f"| {r['deck']} | {r['slide']} | {r['mean_abs']} | {r['pct_gt40']}% | {r['pixels']} |")

print('\n## Picture rows')
print('| Deck | Slide | Kind | Mean | >40 | Worst object |')
print('|---|---:|---|---:|---:|---|')
for r in rows:
    if r['kind'] in ('picture', 'picture-svg'):
        print(f"| {r['deck']} | {r['slide']} | {r['kind']} | {r['mean_abs']} | {r['pct_gt40']}% | {r['worst_object']} |")

print('\n## Text by deck')
print('| Deck | Text rows | Weighted mean | Weighted >40 | Worst text object |')
print('|---|---:|---:|---:|---|')
for deck in sorted(set(r['deck'] for r in rows)):
    rs = [r for r in rows if r['deck'] == deck and r['kind'] == 'text']
    px = sum(int(r['pixels']) for r in rs)
    wm = sum(float(r['mean_abs']) * int(r['pixels']) for r in rs) / px
    wp = sum(float(r['pct_gt40']) * int(r['pixels']) for r in rs) / px
    worst = max(rs, key=lambda r: float(r['mean_abs']))
    print(f"| {deck} | {len(rs)} | {wm:.3f} | {wp:.3f}% | {worst['worst_object']} ({worst['worst_object_mean']}) |")

print('\n## Critic parity')
crit = list(csv.DictReader(open(art / 'critic_parity.csv', encoding='utf-8')))
print('| Deck | Design | Motion | Rhythm | Coherence | Overall |')
print('|---|---:|---:|---:|---:|---:|')
for deck in sorted(set(r['deck'] for r in crit)):
    rs = {r['dimension']: r for r in crit if r['deck'] == deck}
    cells = []
    for d in ('design', 'motion', 'rhythm', 'coherence', 'overall'):
        r = rs.get(d)
        cells.append(f"{float(r['delta']):+.2f}" if r and r["delta"] not in ("", None) else "-")
    print(f"| {deck} | " + ' | '.join(cells) + ' |')

print('\n## Morph')
morph = list(csv.DictReader(open(art / 'morph.csv', encoding='utf-8')))
hidden = list(csv.DictReader(open(art / 'morph_hidden.csv', encoding='utf-8')))
print('| Deck | Slide | Mean | Max | Mean >40 | PP hidden shapes (t=.75) | DC drawn early (t=.75) |')
print('|---|---:|---:|---:|---:|---:|---:|')
for deck in sorted(set(r['deck'] for r in morph)):
    for slide in sorted(set(int(r['slide']) for r in morph if r['deck'] == deck)):
        rs = [r for r in morph if r['deck'] == deck and int(r['slide']) == slide]
        means = [float(r['mean_abs']) for r in rs]
        p40 = [float(r['pct_gt40']) for r in rs]
        hs = [h for h in hidden if h['deck'] == deck and int(h['slide']) == slide and h['t'] == '0.75'
              and h['pp_alpha'] not in ('', None) and h['dc_alpha'] not in ('', None)]
        pp_hidden = sum(1 for h in hs if float(h['pp_alpha']) < 0.15)
        dc_drawn = sum(1 for h in hs if float(h['pp_alpha']) < 0.15 and float(h['dc_alpha']) > 0.25)
        print(f"| {deck} | {slide} | {statistics.mean(means):.2f} | {max(means):.2f} | {statistics.mean(p40):.2f}% | {pp_hidden}/{len(hs)} | {dc_drawn}/{len(hs)} |")

print('\n## Roundtrip node deltas')
rt = list(csv.DictReader(open(art / 'roundtrip.csv', encoding='utf-8')))
agg = collections.defaultdict(lambda: [0, 0, 0])
for r in rt:
    if r['node'] == 'transition':
        continue
    agg[r['node']][0] += int(r['original'] or 0)
    agg[r['node']][1] += int(r['roundtrip'] or 0)
    if int(r['delta'] or 0):
        agg[r['node']][2] += 1
print('| Node | Original | Round trip | Delta | Slides changed |')
print('|---|---:|---:|---:|---:|')
for node, (a, b, c) in sorted(agg.items()):
    print(f"| p:{node} | {a} | {b} | {b-a:+d} | {c} |")

print('\n## Roundtrip effects')
eff = list(csv.DictReader(open(art / 'roundtrip_effects.csv', encoding='utf-8')))
cat = collections.Counter()
for r in eff:
    cat[(r['status'], r['class'], r['preset'], r['props'], r['children'])] += int(r['count'])
for k, n in cat.most_common(12):
    print(n, k)

print('\n## PowerPoint parse')
pp = list(csv.DictReader(open(art / 'roundtrip_pp.csv', encoding='utf-8')))
print('| Deck | Slides | Effect count same | Behaviors lost | Transitions same |')
print('|---|---:|---:|---:|---:|')
for deck in sorted(set(r['deck'] for r in pp)):
    rs = [r for r in pp if r['deck'] == deck]
    print(f"| {deck} | {len(rs)} | {sum(1 for r in rs if r['effects_original']==r['effects_roundtrip'])} | {sum(int(r['behaviors_lost']) for r in rs)} | {sum(1 for r in rs if r['transition_equal']=='True')} |")

print('\n## Deck hashes')
for f in sorted(Path('workspace/decks').glob('*.pptx')):
    if '.static.' in f.name:
        continue
    print(f"{f.name:28s} {hashlib.sha256(f.read_bytes()).hexdigest()[:16]} {f.stat().st_size}")
