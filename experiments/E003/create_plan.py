import copy
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
plan=json.loads((root/'experiments/H002/plan.json').read_text())
modes=['read','relax','create']
orders=[['relax','read','create'],['create','relax','read'],['read','create','relax']]
slots=[(220,520,180),(640,320,360),(1060,520,180)]
for state,order in zip(plan['states'],orders):
    for mode,(cx,cy,diameter) in zip(order,slots):
        ring=state['objects'][mode+'-ring']
        ring.update(x=(cx-diameter/2)/1280,y=(cy-diameter/2)/720,w=diameter/1280,h=diameter/720)
        label=state['objects'][mode+'-label']
        label.update(x=cx/1280-label['w']/2,y=cy/720-label['h']/2)
plan.setdefault('research_metadata',{})['experiment']='E003'
plan['research_metadata']['route_assumption']='Three triangular slots, cyclic identity order. Linear label-box proxy only; PowerPoint playback pending.'
(root/'experiments/E003/plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
