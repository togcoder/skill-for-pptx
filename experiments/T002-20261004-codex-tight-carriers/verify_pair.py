"""Check T002 plan scope and both path-proxy classes; not native playback."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments/E003'))
from path_diagnostic import evaluate

baseline=json.loads((ROOT/'experiments/E004/plan.json').read_text())
candidate=json.loads(Path(__file__).with_name('plan.json').read_text())
errors=[]
for key in ['brief','canvas','data_provenance','objects','transitions']:
    if baseline[key]!=candidate[key]:errors.append('Changed '+key)
for a,b in zip(baseline['states'],candidate['states']):
    if a['id']!=b['id'] or a['message']!=b['message']:errors.append('Changed state content')
    for oid,f in a['objects'].items():
        g=b['objects'][oid]
        allowed={'x','y','w','h'} if oid.endswith('-block') else set()
        if set(f)!=set(g):errors.append('Changed frame fields '+oid)
        for field,value in f.items():
            if field not in allowed and value!=g[field]:errors.append('Changed '+oid+'.'+field)
label_ids=['community-label','transport-label','infrastructure-label']
carrier_ids=['community-block','transport-block','infrastructure-block']
results={}
for name,plan in [('E004',baseline),('T002',candidate)]:
    results[name]={'labels':evaluate(plan,label_ids),'carriers':evaluate(plan,carrier_ids)}
if results['E004']['labels']['overlapping_pairs']!=0:errors.append('Baseline label metric changed')
if results['E004']['carriers']['overlapping_pairs']!=6:errors.append('Baseline carrier metric changed')
if results['T002']['labels']['overlapping_pairs']!=0:errors.append('Candidate label target failed')
if results['T002']['carriers']['overlapping_pairs']!=0:errors.append('Candidate carrier target failed')
report={'scope':'plan-diff and continuous rectangle proxy; not native playback',
        'errors':errors,'results':results,'passed':not errors,'native_playback_verified':False}
print(json.dumps(report,indent=2))
raise SystemExit(not report['passed'])
