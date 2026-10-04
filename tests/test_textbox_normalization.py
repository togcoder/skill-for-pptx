import copy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from lxml import etree as E
from scripts.normalize_textboxes import normalize, NS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'output/PPTX_Motion_Lab_H001.pptx'
PLAN = ROOT / 'experiments/H001/plan.json'


def rewrite(source, destination, change):
    with ZipFile(source) as src, ZipFile(destination, 'w') as dst:
        for item in src.infolist():
            dst.writestr(item, change(item.filename, src.read(item.filename)))


class TextboxNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.out = self.work / 'out.pptx'

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_attribute_only_change_preserves_animation_and_other_parts(self):
        report = normalize(SOURCE, PLAN, self.out)
        self.assertEqual(report['changed_textboxes'], 14)
        with ZipFile(SOURCE) as old, ZipFile(self.out) as new:
            self.assertEqual(old.namelist(), new.namelist())
            for name in old.namelist():
                a, b = old.read(name), new.read(name)
                if a == b:
                    continue
                self.assertRegex(name, r'^ppt/slides/slide\d+\.xml$')
                before, after = E.fromstring(a), E.fromstring(b)
                for shape in after.findall('p:cSld/p:spTree/p:sp', NS):
                    nv = shape.find('p:nvSpPr/p:cNvSpPr', NS)
                    if nv.get('txBox') == '1':
                        del nv.attrib['txBox']
                self.assertEqual(E.tostring(before, method='c14n'), E.tostring(after, method='c14n'))

    def test_text_in_carrier_is_not_reclassified(self):
        plan = json.loads(PLAN.read_text())
        obj = next(o for o in plan['objects'] if o['kind'] == 'text')
        obj.update(kind='shape', geometry='rect')
        changed_plan = self.work / 'plan.json'
        changed_plan.write_text(json.dumps(plan))
        report = normalize(SOURCE, changed_plan, self.out)
        self.assertEqual(report['changed_textboxes'], 12)
        self.assertNotIn(obj['morph_name'], {c['name'] for c in report['changes']})

    def test_invalid_late_slide_leaves_no_partial_output(self):
        broken = self.work / 'broken.pptx'
        def change(name, data):
            if name == 'ppt/slides/slide2.xml':
                root = E.fromstring(data)
                shape = next(s for s in root.findall('p:cSld/p:spTree/p:sp', NS)
                             if s.find('p:txBody', NS) is not None)
                shape.remove(shape.find('p:txBody', NS))
                return E.tostring(root)
            return data
        rewrite(SOURCE, broken, change)
        with self.assertRaisesRegex(ValueError, 'no native text body'):
            normalize(broken, PLAN, self.out)
        self.assertFalse(self.out.exists())

    def test_identity_mismatch_rejected(self):
        plan = json.loads(PLAN.read_text())
        plan['objects'][0]['morph_name'] = '!!wrong'
        altered = self.work / 'plan.json'
        altered.write_text(json.dumps(plan))
        with self.assertRaisesRegex(ValueError, 'identities'):
            normalize(SOURCE, altered, self.out)
        self.assertFalse(self.out.exists())

    def test_idempotence_preserves_all_part_bytes(self):
        normalize(SOURCE, PLAN, self.out)
        again = self.work / 'again.pptx'
        self.assertEqual(normalize(self.out, PLAN, again)['changed_textboxes'], 0)
        with ZipFile(self.out) as a, ZipFile(again) as b:
            self.assertTrue(all(a.read(n) == b.read(n) for n in a.namelist()))

    def test_destination_is_not_overwritten(self):
        self.out.write_bytes(b'keep')
        with self.assertRaises(ValueError):
            normalize(SOURCE, PLAN, self.out)
        self.assertEqual(self.out.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()
