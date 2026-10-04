import copy
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile
from lxml import etree as E
from scripts.add_morph import patch, P, M, D
from test_plan_contract import fixture

R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'


def deck(path, order=('slide2.xml','slide3.xml','slide1.xml'), timing=False):
    with ZipFile(path,'w') as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        ids=''.join(f'<p:sldId id="{256+i}" r:id="r{i}"/>' for i in range(len(order)))
        z.writestr('ppt/presentation.xml',f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst>{ids}</p:sldIdLst></p:presentation>')
        rels=''.join(f'<Relationship Id="r{i}" Type="{R}/slide" Target="slides/{part}"/>' for i,part in enumerate(order))
        z.writestr('ppt/_rels/presentation.xml.rels',f'<Relationships xmlns="{REL}">{rels}</Relationships>')
        for i,part in enumerate(order):
            extra='<p:timing/>' if timing and i==len(order)-1 else ''
            z.writestr('ppt/slides/'+part,f'<p:sld xmlns:p="{P}"><p:cSld><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="!!orb"/></p:nvSpPr></p:sp></p:spTree></p:cSld>{extra}<p:extLst/></p:sld>')


def plan3():
    p=fixture();s=copy.deepcopy(p['states'][-1]);s['id']='last';p['states'].append(s)
    p['transitions'].append(dict(kind='morph',duration_ms=1800,**{'from':'end','to':'last'},track=['orb']))
    return p


class MorphPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
        self.src=self.d/'source.pptx';self.plan=self.d/'plan.json';self.out=self.d/'result.pptx'
        deck(self.src);self.plan.write_text(json.dumps(plan3()))
    def tearDown(self): self.tmp.cleanup()
    def test_slide_relationship_order_and_durations(self):
        patch(self.src,self.plan,self.out)
        with ZipFile(self.out) as z:
            for part,expected in [('slide2.xml',None),('slide3.xml','1000'),('slide1.xml','1800')]:
                root=E.fromstring(z.read('ppt/slides/'+part));morph=root.find(f'.//{{{M}}}morph')
                if expected is None: self.assertIsNone(morph)
                else:
                    self.assertIsNotNone(morph);self.assertEqual(morph.getparent().get(f'{{{D}}}dur'),expected)
                    self.assertEqual(root[-1].tag,f'{{{P}}}extLst')
    def test_mismatch_does_not_leave_partial_output(self):
        self.plan.write_text(json.dumps(fixture()))
        with self.assertRaises(ValueError): patch(self.src,self.plan,self.out)
        self.assertFalse(self.out.exists())
    def test_existing_animation_on_late_slide_is_preserved(self):
        deck(self.src,timing=True);before=self.src.read_bytes()
        with self.assertRaises(ValueError): patch(self.src,self.plan,self.out)
        self.assertFalse(self.out.exists());self.assertEqual(self.src.read_bytes(),before)
    def test_bad_identity_does_not_leave_output(self):
        p=plan3();p['objects'][0]['morph_name']='!!another';self.plan.write_text(json.dumps(p))
        with self.assertRaises(ValueError): patch(self.src,self.plan,self.out)
        self.assertFalse(self.out.exists())
    def test_destination_not_overwritten(self):
        self.out.write_bytes(b'keep')
        with self.assertRaises(ValueError): patch(self.src,self.plan,self.out)
        self.assertEqual(self.out.read_bytes(),b'keep')
    def test_fractional_duration_rejected_without_output(self):
        p=plan3();p['transitions'][0]['duration_ms']=1.5;self.plan.write_text(json.dumps(p))
        with self.assertRaises(ValueError): patch(self.src,self.plan,self.out)
        self.assertFalse(self.out.exists())
    def test_reapplying_to_animated_deck_rejected(self):
        patch(self.src,self.plan,self.out)
        with self.assertRaises(ValueError): patch(self.out,self.plan,self.d/'twice.pptx')
        self.assertFalse((self.d/'twice.pptx').exists())

if __name__=='__main__': unittest.main()
