#!/usr/bin/env python3
"""Experimental Morph insertion with plan, order and identity gates. Not a player."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
try:
    from .inspect_pptx import inspect
    from .validate_plan import validate
except ImportError:
    from inspect_pptx import inspect
    from validate_plan import validate

P='http://schemas.openxmlformats.org/presentationml/2006/main'
MC='http://schemas.openxmlformats.org/markup-compatibility/2006'
M='http://schemas.microsoft.com/office/powerpoint/2015/09/main'
D='http://schemas.microsoft.com/office/powerpoint/2010/main'


def patch(source, plan_path, destination):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise ValueError('Refuse to overwrite an output')
    plan=json.loads(Path(plan_path).read_text(encoding='utf-8'))
    errors=validate(plan)
    if errors:
        raise ValueError('Invalid plan: '+'; '.join(errors))
    for tr in plan['transitions']:
        if tr['kind']!='morph':
            raise ValueError('Only Morph is implemented')
        if type(tr['duration_ms']) is not int or not 1<=tr['duration_ms']<=4294967295:
            raise ValueError('Morph duration must be a positive unsigned integer in milliseconds')
    inventory=inspect(source)
    if inventory['errors']:
        raise ValueError('Invalid source package: '+'; '.join(inventory['errors']))
    slides=inventory['slides']
    if len(slides)!=len(plan['states']):
        raise ValueError('Slide count differs from plan')
    parts=[x['part'] for x in slides]
    if len(parts)!=len(set(parts)):
        raise ValueError('A slide part is referenced more than once')
    objects={x['id']:x for x in plan['objects']}
    parser=E.XMLParser(resolve_entities=False,no_network=True)
    updates={}
    with ZipFile(source) as src:
        for index, (slide,state) in enumerate(zip(slides,plan['states'])):
            expected={objects[oid]['morph_name'] for oid in state['objects']}
            if set(slide['forced_morph_names'])!=expected:
                raise ValueError(f'Slide {index+1}: names differ from planned object identities')
            old=E.fromstring(src.read(slide['part']),parser)
            if old.findall(f'.//{{{P}}}transition') or old.findall(f'.//{{{P}}}timing'):
                raise ValueError('Source must be fresh, without existing transitions or timing')
            if index==0:
                continue
            ns=dict(old.nsmap)
            for prefix,uri in [('mc',MC),('p159',M),('p14',D)]:
                if prefix in ns and ns[prefix]!=uri:
                    raise ValueError(f'Namespace prefix conflict: {prefix}')
                ns[prefix]=uri
            root=E.Element(old.tag,nsmap=ns)
            root.attrib.update(old.attrib)
            root.text=old.text
            root.extend(list(old))
            alt=E.Element(f'{{{MC}}}AlternateContent')
            choice=E.SubElement(alt,f'{{{MC}}}Choice',Requires='p159 p14')
            transition=E.SubElement(choice,f'{{{P}}}transition',spd='slow')
            transition.set(f'{{{D}}}dur',str(plan['transitions'][index-1]['duration_ms']))
            E.SubElement(transition,f'{{{M}}}morph',option='byObject')
            fallback=E.SubElement(alt,f'{{{MC}}}Fallback')
            E.SubElement(E.SubElement(fallback,f'{{{P}}}transition',spd='slow'),f'{{{P}}}fade')
            pos=next((i for i,x in enumerate(root) if x.tag in (f'{{{P}}}timing',f'{{{P}}}extLst')),len(root))
            root.insert(pos,alt)
            updates[slide['part']]=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
        destination.parent.mkdir(parents=True,exist_ok=True)
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent,suffix='.pptx',delete=False) as f:
                temporary=Path(f.name)
            with ZipFile(temporary,'w',ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(item,updates.get(item.filename,src.read(item.filename)))
            report=inspect(temporary)
            if report['errors']:
                raise ValueError('Patched package failed inventory')
            os.link(temporary,destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return {'slides':len(slides),'morph_transitions':len(updates),
            'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'powerpoint_playback_verified':False}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source');ap.add_argument('plan');ap.add_argument('destination')
    a=ap.parse_args()
    print(json.dumps(patch(a.source,a.plan,a.destination),indent=2))
