import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from lxml import etree as E
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'scripts'))
from inspect_pptx import inspect

plan=json.loads((root/'experiments/E003/plan.json').read_text())
baseline=json.loads((root/'experiments/H002/plan.json').read_text())
deck=root/'output/PPTX_Motion_Lab_E003.pptx'
inventory=inspect(deck)
errors=list(inventory['errors']); rows=[]
if plan['objects']!=baseline['objects'] or plan['transitions']!=baseline['transitions']:
    errors.append('Objects or durations changed from baseline')
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','m':'http://schemas.microsoft.com/office/powerpoint/2015/09/main','d':'http://schemas.microsoft.com/office/powerpoint/2010/main'}
with ZipFile(deck) as z:
    if len(inventory['slides'])!=3: errors.append('Wrong slide count')
    for slide,state in zip(inventory['slides'],plan['states']):
        s=E.fromstring(z.read(slide['part']))
        shapes=s.findall('p:cSld/p:spTree/p:sp',ns)
        actual={x.find('p:nvSpPr/p:cNvPr',ns).get('name'):x for x in shapes}
        if len(actual)!=11 or len(shapes)!=11: errors.append('Wrong shape count')
        for obj in plan['objects']:
            sh=actual.get(obj['morph_name'])
            if sh is None: errors.append('Missing '+obj['id']); continue
            f=state['objects'][obj['id']]
            xf=sh.find('p:spPr/a:xfrm',ns);off=xf.find('a:off',ns);ext=xf.find('a:ext',ns)
            a=[int(off.get('x')),int(off.get('y')),int(ext.get('cx')),int(ext.get('cy'))]
            b=[f['x']*12192000,f['y']*6858000,f['w']*12192000,f['h']*6858000]
            if any(abs(x-y)>1 for x,y in zip(a,b)):errors.append('Geometry '+obj['id'])
            text=''.join(sh.xpath('.//a:t/text()',namespaces=ns))
            if text!=f.get('text',obj.get('text','')):errors.append('Text '+obj['id'])
            tx=sh.find('p:nvSpPr/p:cNvSpPr',ns).get('txBox') in ('1','true')
            if tx!=(obj['kind']=='text'):errors.append('Type '+obj['id'])
            expected_geom='rect' if obj['kind']=='text' else obj['geometry']
            if sh.find('p:spPr/a:prstGeom',ns).get('prst')!=expected_geom:errors.append('Shape '+obj['id'])
        morph=s.findall('.//m:morph',ns)
        if len(morph)!=(0 if slide['index']==1 else 1):errors.append('Morph count')
        if morph and (morph[0].get('option')!='byObject' or morph[0].getparent().get('{'+ns['d']+'}dur')!='1100'):errors.append('Morph mode or duration')
        if s.findall('.//p:pic',ns):errors.append('Pictures present')
        rows.append({'slide':slide['index'],'native_objects':len(shapes),'textboxes':sum(x.find('p:nvSpPr/p:cNvSpPr',ns).get('txBox') in ('1','true') for x in shapes),'morph_count':len(morph)})
report={'candidate_sha256':hashlib.sha256(deck.read_bytes()).hexdigest(),'errors':errors,'passed':not errors,'slides':rows,'powerpoint_playback_verified':False}
print(json.dumps(report,indent=2))
raise SystemExit(bool(errors))
