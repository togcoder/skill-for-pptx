"""Paired change: enlarge vertical slot separation, retain all other design settings."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=json.loads((HERE.parent/'H003/plan.json').read_text())
p['research_metadata']['experiment']='E004'
p['research_metadata']['paired_baseline']='H003'
p['research_metadata']['limitations']=['Only block and label y positions changed. Tuned comparison, not an unseen holdout.']
for state in p['states']:
    for key,f in state['objects'].items():
        if key.endswith(('-block','-label')):
            oldcy=(f['y']+f['h']/2)*720
            cy=260 if abs(oldcy-320)<1e-6 else 560
            f['y']=cy/720-f['h']/2
(HERE/'plan.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
