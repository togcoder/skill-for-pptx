#!/usr/bin/env python3
"""Declare planned native textboxes without changing their content or geometry.

Restricted to this project's flat rect/ellipse/textbox output. Does not validate
PowerPoint playback or convert arbitrary user shapes into textboxes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
try:
    from .inspect_pptx import inspect, P
    from .validate_plan import validate
except ImportError:
    from inspect_pptx import inspect, P
    from validate_plan import validate

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS = {'p': P, 'a': A}


def normalize(source, plan_path, destination):
    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise ValueError('Refuse to overwrite an output')
    plan = json.loads(Path(plan_path).read_text(encoding='utf-8'))
    errors = validate(plan)
    if errors:
        raise ValueError('Invalid plan: ' + '; '.join(errors))
    objects = {o['id']: o for o in plan['objects']}
    for obj in objects.values():
        if (obj['kind'], obj.get('geometry')) not in {
            ('shape', 'rect'), ('shape', 'ellipse'), ('text', 'textbox')
        }:
            raise ValueError('Unsupported object representation')
    inventory = inspect(source)
    slides = inventory['slides']
    if inventory['errors'] or len(slides) != len(plan['states']):
        raise ValueError('Source package or slide count does not match plan')
    if len({s['part'] for s in slides}) != len(slides):
        raise ValueError('A slide part is referenced more than once')
    updates, changes = {}, []
    parser = E.XMLParser(resolve_entities=False, no_network=True)
    with ZipFile(source) as src:
        # Validate every slide before publishing any output.
        for slide, state in zip(slides, plan['states']):
            root = E.fromstring(src.read(slide['part']), parser)
            shapes = root.findall('p:cSld/p:spTree/p:sp', NS)
            actual = {}
            for shape in shapes:
                props = shape.find('p:nvSpPr/p:cNvPr', NS)
                if props is None or props.get('name') in actual:
                    raise ValueError('Missing or duplicate native shape name')
                actual[props.get('name')] = shape
            expected = {objects[oid]['morph_name'] for oid in state['objects']}
            if set(actual) != expected or set(slide['forced_morph_names']) != expected:
                raise ValueError('Native shape identities do not match plan')
            changed = False
            for oid in state['objects']:
                obj = objects[oid]
                shape = actual[obj['morph_name']]
                nv = shape.find('p:nvSpPr/p:cNvSpPr', NS)
                geom = shape.find('p:spPr/a:prstGeom', NS)
                wanted = 'rect' if obj['kind'] == 'text' else obj['geometry']
                if nv is None or geom is None or geom.get('prst') != wanted:
                    raise ValueError('Unexpected native shape properties or geometry')
                flag = nv.get('txBox')
                if flag not in (None, '0', 'false', '1', 'true'):
                    raise ValueError('Invalid txBox boolean')
                if obj['kind'] != 'text':
                    if flag in ('1', 'true'):
                        raise ValueError('Planned carrier is already marked as a textbox')
                    continue
                if shape.find('p:txBody', NS) is None:
                    raise ValueError('Planned textbox has no native text body')
                if flag not in ('1', 'true'):
                    nv.set('txBox', '1')
                    changes.append({'slide': slide['index'], 'name': obj['morph_name'],
                                    'attribute': 'txBox', 'before': flag, 'after': '1'})
                    changed = True
            if changed:
                updates[slide['part']] = E.tostring(root, encoding='UTF-8', xml_declaration=True, standalone=True)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.pptx', delete=False) as f:
                temporary = Path(f.name)
            with ZipFile(temporary, 'w', ZIP_DEFLATED) as dst:
                for item in src.infolist():
                    dst.writestr(item, updates.get(item.filename, src.read(item.filename)))
            if inspect(temporary)['errors']:
                raise ValueError('Normalized package failed inventory')
            os.link(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return {'changed_textboxes': len(changes), 'changes': changes,
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'powerpoint_playback_verified': False}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source'); ap.add_argument('plan'); ap.add_argument('destination')
    args = ap.parse_args()
    print(json.dumps(normalize(args.source, args.plan, args.destination), indent=2))
