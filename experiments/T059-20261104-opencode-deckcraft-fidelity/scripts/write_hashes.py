import hashlib
from pathlib import Path

lines = [
    '# T059 frozen decks (built from examples/pptx/forge or copied from T028 output)',
    '# sha256  bytes  file  source',
    '',
]
src = {
    'coffee_office_dynamic': 'examples/pptx/forge/coffee_office_dynamic.json',
    'coffee_report': 'examples/pptx/forge/coffee_report.json',
    'coffee_report_photos': 'examples/pptx/forge/coffee_report_photos.json',
    'vi_brand_seed': 'examples/pptx/forge/vi_brand_seed.json',
    'vi_chuyen_doi_so': 'examples/pptx/forge/vi_chuyen_doi_so.json',
    'T028_report_pro': 'experiments/T028-20261008-claude-morph-studio/output/T028_report_pro.pptx',
    'T028_showcase_pro': 'experiments/T028-20261008-claude-morph-studio/output/T028_showcase_pro.pptx',
    'kind_probe': 'workspace/build_kind_probe.py (synthetic)',
}
for f in sorted(Path('workspace/decks').glob('*.pptx')):
    if '.static.' in f.name:
        continue
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    lines.append(f'{h}  {f.stat().st_size:>8}  {f.name}  {src.get(f.stem, "?")}')
out = Path('experiments/T059-20261104-opencode-deckcraft-fidelity/inputs/deck_hashes.txt')
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
