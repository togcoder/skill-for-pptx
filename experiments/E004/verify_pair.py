"""Verify the frozen H003/E004 composition and allowed paired changes."""
import hashlib
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
baseline=json.loads((ROOT/'experiments/H003/plan.json').read_text())
candidate=json.loads((ROOT/'experiments/E004/plan.json').read_text())
pair_errors=[]
for key in ['brief','canvas','data_provenance','objects','transitions']:
    if baseline[key]!=candidate[key]: pair_errors.append('Changed '+key)
for a,b in zip(baseline['states'],candidate['states']):
    if a['id']!=b['id'] or a['message']!=b['message']:pair_errors.append('Changed state content')
    for key,f in a['objects'].items():
        g=b['objects'][key]
        allowed={'y'} if key.endswith(('-block','-label')) else set()
        for field,value in f.items():
            if field not in allowed and value!=g.get(field):pair_errors.append('Changed '+key+'.'+field)

results={}
for name,plan in [('H003',baseline),('E004',candidate)]:
    deck=ROOT/'output'/('PPTX_Motion_Lab_'+name+'.pptx')
    inventory=inspect(deck); errors=list(inventory['errors']); rows=[]
    if len(inventory['slides'])!=3:errors.append('Slide count')
    with ZipFile(deck) as z:
        for slide,state in zip(inventory['slides'],plan['states']):
            xml=E.fromstring(z.read(slide['part']))
            shapes=xml.findall('p:cSld/p:spTree/p:sp',NS)
            actual={s.find('p:nvSpPr/p:cNvPr',NS).get('name'):s for s in shapes}
            if len(shapes)!=8 or set(actual)!={o['morph_name'] for o in plan['objects']}:errors.append('Shape count/names')
            for obj in plan['objects']:
                s=actual.get(obj['morph_name'])
                if s is None:errors.append('Missing '+obj['id']);continue
                f=state['objects'][obj['id']]
                xf=s.find('p:spPr/a:xfrm',NS);off=xf.find('a:off',NS);ext=xf.find('a:ext',NS)
                actual_geom=[int(off.get('x')),int(off.get('y')),int(ext.get('cx')),int(ext.get('cy'))]
                expected=[f['x']*12192000,f['y']*6858000,f['w']*12192000,f['h']*6858000]
                if any(abs(x-y)>1 for x,y in zip(actual_geom,expected)):errors.append('Geometry '+obj['id'])
                texts=s.xpath('.//a:t/text()',namespaces=NS)
                # PowerPoint may encode a line break as separate paragraphs/runs.
                if ''.join(texts).replace('\n','')!=f.get('text',obj.get('text','')).replace('\n',''):errors.append('Text '+obj['id'])
                tx=s.find('p:nvSpPr/p:cNvSpPr',NS).get('txBox') in ('1','true')
                if tx!=(obj['kind']=='text'):errors.append('Textbox '+obj['id'])
                if s.find('p:spPr/a:prstGeom',NS).get('prst')!='rect':errors.append('Geometry type '+obj['id'])
            morph=xml.findall('.//m:morph',NS)
            if len(morph)!=(0 if slide['index']==1 else 1):errors.append('Morph count')
            if morph and (morph[0].get('option')!='byObject' or morph[0].getparent().get('{'+NS['d']+'}dur')!='1100'):errors.append('Morph duration/mode')
            if xml.findall('.//p:pic',NS):errors.append('Pictures present')
            if xml.findall('.//p:timing',NS):errors.append('Unexpected animation timing')
            rows.append(dict(slide=slide['index'],native_objects=len(shapes),textboxes=sum(s.find('p:nvSpPr/p:cNvSpPr',NS).get('txBox') in ('1','true') for s in shapes),morph_count=len(morph)))
    results[name]=dict(sha256=hashlib.sha256(deck.read_bytes()).hexdigest(),errors=errors,slides=rows,passed=not errors,powerpoint_playback_verified=False)
report=dict(pair_errors=pair_errors,decks=results,passed=not pair_errors and all(r['passed'] for r in results.values()))
print(json.dumps(report,indent=2))
raise SystemExit(not report['passed'])
