from pathlib import Path
import json,zipfile,xml.etree.ElementTree as E,posixpath,hashlib
root=Path(__file__).resolve().parents[2]
plan=json.loads((root/'experiments/H002/plan.json').read_text())
pptx=root/'output/PPTX_Motion_Lab_H002.pptx'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','p159':'http://schemas.microsoft.com/office/powerpoint/2015/09/main'}
errors=[];slides=[]
with zipfile.ZipFile(pptx) as z:
    pres=E.fromstring(z.read('ppt/presentation.xml'))
    relations={x.get('Id'):x.get('Target') for x in E.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    targets=[relations[x.get('{'+ns['r']+'}id')] for x in pres.findall('p:sldIdLst/p:sldId',ns)]
    order=[posixpath.normpath(t.lstrip('/') if t.startswith('/') else posixpath.join('ppt',t)) for t in targets]
    if len(order)!=3:errors.append('slide count')
    for i,part in enumerate(order):
        s=E.fromstring(z.read(part)); shapes=s.findall('.//p:sp',ns)
        names=[x.find('p:nvSpPr/p:cNvPr',ns).get('name') for x in shapes]
        expect={o['morph_name'] for o in plan['objects'] if o['id'] in plan['states'][i]['objects']}
        if set(names)!=expect or len(names)!=len(expect):errors.append(f'slide {i+1}: names')
        counts={'textboxes':0,'native_nonempty_text_carriers':0,'ellipse':0,'rect':0,'pictures':len(s.findall('.//p:pic',ns))}
        geometry=[]
        for sh in shapes:
            istext=sh.find('p:nvSpPr/p:cNvSpPr',ns).get('txBox') in ('1','true')
            counts['textboxes']+=int(istext)
            counts['native_nonempty_text_carriers']+=int(bool(sh.findall('.//a:t',ns)))
            geom=sh.find('p:spPr/a:prstGeom',ns)
            if geom is not None and not istext: counts[geom.get('prst')]=counts.get(geom.get('prst'),0)+1
            name=sh.find('p:nvSpPr/p:cNvPr',ns).get('name')
            if name.endswith('-ring'):
                xfrm=sh.find('p:spPr/a:xfrm',ns);off=xfrm.find('a:off',ns);ext=xfrm.find('a:ext',ns)
                dims={k:int(v)/9525 for k,v in (dict(off.attrib)|dict(ext.attrib)).items()}
                f=plan['states'][i]['objects'][name[2:]]
                expected=[f['x']*1280,f['y']*720,f['w']*1280,f['h']*720]
                actual=[dims['x'],dims['y'],dims['cx'],dims['cy']]
                if any(abs(a-b)>0.01 for a,b in zip(actual,expected)):errors.append(f'slide {i+1}: {name} geometry')
                geometry.append(dict(name=name,pixels=dims))
        transitions=s.findall('.//p:transition',ns)
        morph=s.findall('.//p159:morph',ns)
        durations=[v for el in transitions for k,v in el.attrib.items() if k.endswith('dur')]
        if len(morph)!=(0 if i==0 else 1):errors.append(f'slide {i+1}: morph count')
        if i>0 and '1100' not in durations:errors.append(f'slide {i+1}: duration')
        if counts['textboxes']!=6 or counts['ellipse']!=4 or counts['rect']!=1 or len(shapes)!=11 or counts['pictures']!=0:errors.append(f'slide {i+1}: native types')
        txt=[x.text or '' for x in s.findall('.//a:t',ns)]
        slides.append(dict(index=i+1,part=part,shape_count=len(shapes),counts=counts,forced_name_count=len(names),morph_count=len(morph),duration_values=durations,ring_geometry=geometry,text=txt))
    media=[name for name in z.namelist() if name.startswith('ppt/media/')]
report=dict(experiment='H002',sha256=hashlib.sha256(pptx.read_bytes()).hexdigest(),errors=errors,slides=slides,media_parts=media,structure_checked=not errors,full_schema_validated=False,native_motion=None,powerpoint_playback_verified=False,real_application_editing=None)
(root/'build/h002/structure-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(errors=errors,sha256=report['sha256'],slides=[dict(index=s['index'],counts=s['counts'],morph_count=s['morph_count'],duration_values=s['duration_values']) for s in slides]),ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
