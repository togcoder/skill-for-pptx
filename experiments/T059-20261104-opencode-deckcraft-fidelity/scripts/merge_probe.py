import csv, shutil
from pathlib import Path

art = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/artifacts')
probe = Path('workspace/probe_out2')
for name, key in (('fidelity.csv', ('deck', 'slide', 'kind')), ('fidelity_objects.csv', ('deck', 'slide', 'z'))):
    main = [r for r in csv.DictReader(open(art / name, encoding='utf-8')) if r['deck'] != 'kind_probe']
    extra = list(csv.DictReader(open(probe / name, encoding='utf-8')))
    rows = main + extra
    rows.sort(key=lambda r: (r['deck'], int(r['slide']), r.get('kind', r.get('z'))))
    with open(art / name, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(name, len(main), '+', len(extra), '=', len(rows))
for f in (probe / 'static').glob('*.jpg'):
    shutil.copyfile(f, art / 'static' / f.name)
for f in (probe / 'diffs').glob('*.jpg'):
    shutil.copyfile(f, art / 'diffs' / f.name)
print('copied probe images')
