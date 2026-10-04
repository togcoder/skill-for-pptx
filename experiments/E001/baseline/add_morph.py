#!/usr/bin/env python3
"""Add experimental Morph declarations to a fresh generated deck, never an existing animated deck."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E

P='http://schemas.openxmlformats.org/presentationml/2006/main'
MC='http://schemas.openxmlformats.org/markup-compatibility/2006'
M='http://schemas.microsoft.com/office/powerpoint/2015/09/main'
D='http://schemas.microsoft.com/office/powerpoint/2010/main'

def patch(source,plan_path,destination):
    if Path(destination).exists(): raise ValueError('Refuse to overwrite an output')
    plan=json.loads(Path(plan_path).read_text())
    with ZipFile(source) as src, ZipFile(destination,'w',ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data=src.read(item.filename)
            if item.filename.startswith('ppt/slides/slide') and item.filename.endswith('.xml'):
                index=int(item.filename.rsplit('slide',1)[1][:-4])-1
                old=E.fromstring(data)
                if old.find(f'{{{P}}}transition') is not None or old.find(f'{{{MC}}}AlternateContent') is not None:
                    raise ValueError('Input must be a fresh generated deck without transitions')
                if index>0:
                    tr=plan['transitions'][index-1]
                    if tr['kind']!='morph': raise ValueError('Only Morph is implemented')
                    ns=dict(old.nsmap);ns.update({'mc':MC,'p159':M,'p14':D})
                    root=E.Element(old.tag,nsmap=ns)
                    root.attrib.update(old.attrib)
                    root.extend(list(old))
                    alt=E.Element(f'{{{MC}}}AlternateContent')
                    choice=E.SubElement(alt,f'{{{MC}}}Choice',Requires='p159')
                    transition=E.SubElement(choice,f'{{{P}}}transition',spd='slow')
                    transition.set(f'{{{D}}}dur',str(int(tr['duration_ms'])))
                    E.SubElement(transition,f'{{{M}}}morph',option='byObject')
                    fallback=E.SubElement(alt,f'{{{MC}}}Fallback')
                    E.SubElement(E.SubElement(fallback,f'{{{P}}}transition',spd='slow'),f'{{{P}}}fade')
                    # Slide schema order: cSld, clrMapOvr, transition, timing, extLst.
                    children=list(root)
                    pos=next((i for i,x in enumerate(children) if x.tag in (f'{{{P}}}timing',f'{{{P}}}extLst')),len(children))
                    root.insert(pos,alt)
                    data=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
            dst.writestr(item,data)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source');ap.add_argument('plan');ap.add_argument('destination')
    a=ap.parse_args();patch(a.source,a.plan,a.destination)
    print('Experimental Morph structure written; native playback remains untested.')

