"""Read-only plan/package parity for this study, not schema or playback QA."""
import argparse
import json
import sys
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from inspect_pptx import inspect
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm':'http://schemas.microsoft.com/office/powerpoint/2015/09/main',
    'd':'http://schemas.microsoft.com/office/powerpoint/2010/main'}


def verify(plan,deck):
    inventory=inspect(deck)
    errors=list(inventory['errors'])
    rows=[]
    if len(inventory['slides'])!=len(plan['states']):errors.append('Slide count')
    with ZipFile(deck) as z:
        for slide,state in zip(inventory['slides'],plan['states']):
            xml=E.fromstring(z.read(slide['part']))
            shapes=xml.findall('p:cSld/p:spTree/p:sp',NS)
            actual={s.find('p:nvSpPr/p:cNvPr',NS).get('name'):s for s in shapes}
            if len(shapes)!=len(plan['objects']) or set(actual)!={o['morph_name'] for o in plan['objects']}:
                errors.append('Shape count/names')
            for obj in plan['objects']:
                s=actual.get(obj['morph_name'])
                if s is None:errors.append('Missing '+obj['id']);continue
                f=state['objects'][obj['id']]
                xf=s.find('p:spPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
                geom=[int(off.get('x')),int(off.get('y')),int(ext.get('cx')),int(ext.get('cy'))]
                expected=[f['x']*12192000,f['y']*6858000,f['w']*12192000,f['h']*6858000]
                if any(abs(x-y)>1 for x,y in zip(geom,expected)):errors.append('Geometry '+obj['id'])
                if int(xf.get('rot','0'))!=round(f['rotation_deg']*60000):errors.append('Rotation '+obj['id'])
                text=''.join(s.xpath('.//a:t/text()',namespaces=NS)).replace('\n','')
                if text!=f.get('text',obj.get('text','')).replace('\n',''):errors.append('Text '+obj['id'])
                tx=s.find('p:nvSpPr/p:cNvSpPr',NS).get('txBox') in ('1','true')
                if tx!=(obj['kind']=='text'):errors.append('Textbox '+obj['id'])
                kind='rect' if obj['geometry']=='textbox' else obj['geometry']
                if s.find('p:spPr/a:prstGeom',NS).get('prst')!=kind:errors.append('Type '+obj['id'])
            morph=xml.findall('.//m:morph',NS)
            if len(morph)!=(0 if slide['index']==1 else 1):errors.append('Morph count')
            if morph:
                duration=str(plan['transitions'][slide['index']-2]['duration_ms'])
                if morph[0].get('option')!='byObject' or morph[0].getparent().get('{'+NS['d']+'}dur')!=duration:
                    errors.append('Morph duration/mode')
            if xml.findall('.//p:pic',NS):errors.append('Pictures present')
            if xml.findall('.//p:timing',NS):errors.append('Unexpected animation timing')
            rows.append(dict(slide=slide['index'],native_objects=len(shapes),
                             textboxes=sum(s.find('p:nvSpPr/p:cNvSpPr',NS).get('txBox') in ('1','true') for s in shapes),
                             morph_count=len(morph)))
    return dict(sha256=inventory['sha256'],errors=errors,slides=rows,passed=not errors,
                full_schema_validated=False,powerpoint_playback_verified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path);parser.add_argument('deck',type=Path)
    args=parser.parse_args()
    report=verify(json.loads(args.plan.read_text()),args.deck)
    print(json.dumps(report,indent=2))
    raise SystemExit(not report['passed'])
