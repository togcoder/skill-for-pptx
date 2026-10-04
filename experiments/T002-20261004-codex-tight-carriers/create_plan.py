"""Derive the frozen T002 candidate from E004 by changing carrier frames only."""
import copy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
baseline=json.loads((ROOT/'experiments/E004/plan.json').read_text())
candidate=copy.deepcopy(baseline)

for state in candidate['states']:
    for prefix in ('community','transport','infrastructure'):
        block=state['objects'][prefix+'-block']
        label=state['objects'][prefix+'-label']
        focused=round(block['w']*1280)==480
        width,height=(404,112) if focused else (372,104)
        block.update(x=label['x']-(width-360)/2/1280,
                     y=label['y']-(height-96)/2/720,
                     w=width/1280,h=height/720)

candidate['brief']=baseline['brief']
candidate.setdefault('research_metadata',{})['experiment']='T002-20261004-codex-tight-carriers'
candidate['research_metadata']['baseline']='experiments/E004/plan.json'
candidate['research_metadata']['change']='Carrier frames only: focus 404x112 px, context 372x104 px, centered on unchanged labels.'
candidate['research_metadata']['native_playback_verified']=False

output=Path(__file__).with_name('plan.json')
with output.open('x') as handle:
    json.dump(candidate,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
