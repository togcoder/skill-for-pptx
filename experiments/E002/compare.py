#!/usr/bin/env python3
"""Measure package and static-pixel deltas; no motion evaluation."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from PIL import Image

root = Path(__file__).resolve().parents[2]
folder = root / 'experiments/E002'
old = root / 'output/PPTX_Motion_Lab_H001.pptx'
new = root / 'output/PPTX_Motion_Lab_E002.pptx'
rows = []
for i in (1, 2):
    a = Image.open(root / f'experiments/H001/final-render/slide-{i}.png').convert('RGBA')
    b = Image.open(folder / f'final-render/slide-{i}.png').convert('RGBA')
    if a.size != b.size:
        raise ValueError('Different render dimensions')
    changed = sum(a.getpixel((x, y)) != b.getpixel((x, y))
                  for y in range(a.height) for x in range(a.width))
    rows.append({'slide': i, 'size': list(b.size), 'changed_pixels': changed,
                 'total_pixels': b.width * b.height, 'identical': changed == 0})
ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
changed_parts, exact_others, slide_semantic_same = [], True, True
with ZipFile(old) as a, ZipFile(new) as b:
    assert a.namelist() == b.namelist()
    for name in a.namelist():
        ab, bb = a.read(name), b.read(name)
        if ab == bb:
            continue
        changed_parts.append(name)
        if not (name.startswith('ppt/slides/slide') and name.endswith('.xml')):
            exact_others = False
            continue
        ar, br = E.fromstring(ab), E.fromstring(bb)
        for sh in br.findall('p:cSld/p:spTree/p:sp', ns):
            nv = sh.find('p:nvSpPr/p:cNvSpPr', ns)
            if nv.get('txBox') == '1':
                del nv.attrib['txBox']
        slide_semantic_same &= E.tostring(ar, method='c14n') == E.tostring(br, method='c14n')
hash_of = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((root / 'experiments/H001/plan-package-comparison.json').read_text())
candidate = json.loads((folder / 'h001-candidate-check.json').read_text())
report = {
    'baseline_sha256': hash_of(old), 'candidate_sha256': hash_of(new),
    'static_pixel_comparison': rows, 'changed_parts': changed_parts,
    'all_non_slide_parts_byte_identical': exact_others,
    'slide_xml_equal_after_removing_added_txBox': slide_semantic_same,
    'h001_checker_sha256': hash_of(root / 'experiments/H001/verify_package.py'),
    'h001_rubric_sha256': hash_of(root / 'experiments/H001/rubric.json'),
    'baseline_failed_checks': len(baseline['failures']),
    'candidate_failed_checks': len(candidate['failures']),
    'total_frozen_checks': len(candidate['checks']),
    'powerpoint_playback_verified': False,
}
print(json.dumps(report, indent=2))
