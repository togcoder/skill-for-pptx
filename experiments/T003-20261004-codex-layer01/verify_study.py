"""Reproduce package/geometry evidence; visual ratings are reviewed separately."""
import copy
import json
from pathlib import Path
import sys
from verify_package import verify,ROOT
sys.path.insert(0,str(ROOT/'scripts'))
from layer_separation import binding_metrics
from validate_plan import validate

BASE=Path(__file__).resolve().parent
CASES={
    'ablation':('ablation-plan.json','T003_layer_ablation.pptx'),
    'candidate_v1':('plan.json','T003_layer_candidate.pptx'),
    'candidate_v2':('plan-v2.json','T003_layer_candidate_v2.pptx'),
    'transfer_v1':('transfer/plan.json','T003_transfer_v1.pptx'),
    'transfer_v2':('transfer/plan-v2.json','T003_transfer_v2.pptx'),
}
plans={k:json.loads((BASE/p).read_text()) for k,(p,_) in CASES.items()}
report={'cases':{},'comparison_errors':[],'native_playback_verified':False}
for name,plan in plans.items():
    validation=validate(plan)
    # validate() returns a list of contract errors.
    if validation:report['comparison_errors'].append(f'{name}: {validation}')
    first,last=plan['states'][0]['objects'],plan['states'][-1]['objects']
    closure=all({k:v for k,v in f.items() if k!='text'}==
                {k:v for k,v in last[oid].items() if k!='text'} for oid,f in first.items())
    rail=all(f==first[oid] for state in plan['states'] for oid,f in state['objects'].items() if oid.startswith('rail-'))
    carriers=[o['id'] for o in plan['objects'] if o['id'].startswith('layer-')]
    gaps=[(state['objects'][b]['y']-state['objects'][a]['y']-state['objects'][a]['h'])*720
          for state in plan['states'] for a,b in zip(carriers,carriers[1:])]
    package=verify(plan,ROOT/'output'/CASES[name][1])
    report['cases'][name]=dict(plan_errors=validation,assembly_closes=closure,fixed_rail=rail,
                               min_adjacent_carrier_gap_px=round(min(gaps),6),
                               binding=binding_metrics(plan),package=package)
    if not closure or not rail or min(gaps)<0 or not package['passed']:
        report['comparison_errors'].append(name+' objective failure')

# Reconstruct only the declared ablation change and compare the complete plan.
expected=copy.deepcopy(plans['candidate_v1'])
expected['research_metadata']['ablation']=True
for binding in expected['research_metadata']['bindings']:
    child=binding['child']
    expected['states'][1]['objects'][child]=copy.deepcopy(expected['states'][0]['objects'][child])
if expected!=plans['ablation']:report['comparison_errors'].append('Ablation changed more than detached children')

# Width-only repair; text, all other coordinates, styles and timing are frozen.
for a,b in [('candidate_v1','candidate_v2'),('transfer_v1','transfer_v2')]:
    expected=copy.deepcopy(plans[a])
    for state in expected['states']:
        for binding in expected['research_metadata']['bindings']:
            if binding['child'].endswith('-number'):
                state['objects'][binding['child']]['w']=60/1280
    if expected!=plans[b]:report['comparison_errors'].append(a+' width repair changed other fields')
report['passed']=not report['comparison_errors']
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(not report['passed'])
