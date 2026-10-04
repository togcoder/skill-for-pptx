#!/usr/bin/env python3
"""Generate a restricted native 2D layer-separation plan (no PPTX playback)."""
import argparse
import copy
import json
from pathlib import Path
import re

W, H = 1280, 720
PALETTE = ['#54E7FF', '#BAFA64', '#FFBC70', '#C59EFF', '#FF7FA8']


def frame(x, y, w, h):
    return dict(x=x/W, y=y/H, w=w/W, h=h/H, rotation_deg=0, opacity=1)


def make_plan(config, *, ablate_binding=False):
    """3–5 equal-height layers; flat objects, stable IDs, translation only.

    Input: title, subtitle, brief, layers=[{id,label,role}], optional references.
    Length budgets are preflight bounds, not a substitute for inspecting text.
    """
    unknown = set(config) - {'title', 'subtitle', 'brief', 'layers', 'references'}
    if unknown:
        raise ValueError(f'Unsupported config fields: {sorted(unknown)}')
    for key, limit in [('title', 26), ('subtitle', 70), ('brief', 1500)]:
        value = config.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f'{key} must be nonempty text, at most {limit} characters')
    layers = config.get('layers')
    if not isinstance(layers, list) or not 3 <= len(layers) <= 5:
        raise ValueError('This layout supports 3–5 layers')
    ids = set()
    for layer in layers:
        if not isinstance(layer, dict) or set(layer) != {'id', 'label', 'role'}:
            raise ValueError('Each layer needs exactly id, label, role')
        lid = layer['id']
        if not isinstance(lid, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', lid) or lid in ids:
            raise ValueError('Layer IDs must be unique lower-case semantic identifiers')
        ids.add(lid)
        for key, limit in [('label', 24), ('role', 38)]:
            value = layer[key]
            if not isinstance(value, str) or not value.strip() or len(value) > limit or '\n' in value:
                raise ValueError(f'Layer {key} must fit one line ({limit} characters maximum)')
    refs = config.get('references', [])
    if not isinstance(refs, list) or any(not isinstance(r, dict) or not isinstance(r.get('url'), str) or not r['url'].startswith(('https://', 'http://')) for r in refs):
        raise ValueError('references must contain URL records')

    objects, fixed, bindings = [], {}, []

    def add(oid, geometry, f, *, fill='none', stroke='none', text=None, size=24, color='#F7F4FA', bold=True):
        obj = dict(id=oid, kind='text' if geometry == 'textbox' else 'shape',
                   persistent=True, morph_name='!!'+oid, geometry=geometry,
                   fill=fill, stroke=stroke, stroke_width=1.5 if stroke != 'none' else 0)
        if text is not None:
            obj.update(text=text, font_size=size, text_color=color, bold=bold)
        objects.append(obj)
        fixed[oid] = f

    add('eyebrow', 'textbox', frame(90, 28, 1100, 24), text='PPTX MOTION LAB  /  LAYER STUDY', size=16, color='#AAA2B8', bold=False)
    add('title', 'textbox', frame(90, 66, 1100, 65), text=config['title'], size=52)
    add('subtitle', 'textbox', frame(90, 135, 1100, 38), text=config['subtitle'], size=24, color='#C9C1D4', bold=False)
    add('divider', 'rect', frame(726, 202, 2, 406), fill='#393240')
    add('scene', 'textbox', frame(100, 627, 575, 37), text='01 / TỔNG THỂ', size=23, color='#E9E3F0')
    add('footer', 'textbox', frame(755, 632, 460, 30), text='Sơ đồ minh họa • dữ liệu giả định', size=17, color='#AAA2B8', bold=False)

    n = len(layers)
    compact_top = 390 - ((n-1)*56+52)/2
    spread_top = 390 - ((n-1)*88+52)/2
    for i, layer in enumerate(layers):
        lid, color = layer['id'], PALETTE[i]
        x, y = 124+i*7, compact_top+i*56
        carrier = f'layer-{lid}'
        add(carrier, 'rect', frame(x,y,520,52), fill='#24212C', stroke=color)
        # Children are flattened native shapes, positioned in carrier-local coordinates.
        for suffix, geom, dx, dy, width, height, kwargs in [
            ('number','textbox',14,10,42,32,dict(text=f'{i+1:02}',size=23,color=color)),
            ('trace','rect',78,25,310,2,dict(fill=color)),
            ('node','ellipse',382,16,20,20,dict(fill=color)),
            ('end','rect',438,14,57,24,dict(fill=color)),
        ]:
            child = f'{lid}-{suffix}'
            add(child,geom,frame(x+dx,y+dy,width,height),**kwargs)
            bindings.append(dict(parent=carrier,child=child,offset_px=[dx,dy]))
        ry = spread_top+i*88
        add(f'rail-{lid}-number','textbox',frame(751,ry+8,46,35),text=f'{i+1:02}',size=22,color=color)
        add(f'rail-{lid}-label','textbox',frame(809,ry-1,390,35),text=layer['label'],size=26,color=color)
        add(f'rail-{lid}-role','textbox',frame(809,ry+34,390,27),text=layer['role'],size=19,color='#D4CCDF',bold=False)

    states=[]
    for sid, caption in [('assembled','01 / TỔNG THỂ'),('separated','02 / TÁCH LỚP'),('reassembled','03 / GHÉP LẠI')]:
        frames=copy.deepcopy(fixed)
        frames['scene']['text']=caption
        if sid == 'separated':
            for i, layer in enumerate(layers):
                carrier=f"layer-{layer['id']}"
                frames[carrier]['y']=(spread_top+i*88)/H
            if not ablate_binding:
                for binding in bindings:
                    parent=frames[binding['parent']]
                    child=frames[binding['child']]
                    child['x']=parent['x']+binding['offset_px'][0]/W
                    child['y']=parent['y']+binding['offset_px'][1]/H
        states.append(dict(id=sid,message=caption+'. '+config['brief'],objects=frames))
    persistent=[o['id'] for o in objects]
    return dict(version='0.1',brief=config['brief'],canvas=dict(width=16,height=9,units='normalized'),
                data_provenance='synthetic',objects=objects,states=states,
                transitions=[dict(**{'from':a,'to':b},kind='morph',duration_ms=1100,track=persistent)
                             for a,b in [('assembled','separated'),('separated','reassembled')]],
                research_metadata=dict(recipe='layer-separation-2d-v1',bindings=bindings,
                    references=refs,ablation=ablate_binding,layer_count=n,
                    native_playback_verified=False,
                    assumptions='Constant size, zero rotation, synchronous translation. Fixed explanation rail. No native group or 3D extrusion.'))


def binding_metrics(plan):
    """Endpoint relative offsets; invariance also holds under linear translation."""
    violations=[]
    maximum=0.0
    for state in plan['states']:
        for binding in plan['research_metadata']['bindings']:
            parent=state['objects'][binding['parent']]
            child=state['objects'][binding['child']]
            dx=(child['x']-parent['x'])*W-binding['offset_px'][0]
            dy=(child['y']-parent['y'])*H-binding['offset_px'][1]
            drift=(dx*dx+dy*dy)**0.5
            maximum=max(maximum,drift)
            if drift>1e-6:
                violations.append(dict(state=state['id'],child=binding['child'],drift_px=round(drift,6)))
    return dict(checked_child_states=len(plan['states'])*len(plan['research_metadata']['bindings']),
                violation_count=len(violations),max_drift_px=round(maximum,6),violations=violations,
                scope='Endpoint offsets plus synchronous linear translation implication, not native playback')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--ablate-binding',action='store_true',help='Constructed fault case for research only')
    args=parser.parse_args()
    plan=make_plan(json.loads(args.config.read_text()),ablate_binding=args.ablate_binding)
    with args.output.open('x') as handle:
        json.dump(plan,handle,ensure_ascii=False,indent=2)
        handle.write('\n')
