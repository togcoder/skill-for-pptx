import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from layer_separation import make_plan, binding_metrics


class LayerRecipeTests(unittest.TestCase):
    def config(self,n=4):
        return dict(title='Test',subtitle='Synthetic',brief='Separate and reassemble.',
                    layers=[dict(id=f'layer-{i}',label=f'Part {i}',role='A distinct role') for i in range(n)])

    def test_supported_counts_close_and_keep_children_attached(self):
        for n in [3,4,5]:
            plan=make_plan(self.config(n))
            self.assertEqual(binding_metrics(plan)['violation_count'],0)
            for oid,a in plan['states'][0]['objects'].items():
                b=plan['states'][2]['objects'][oid]
                self.assertEqual({k:v for k,v in a.items() if k!='text'},
                                 {k:v for k,v in b.items() if k!='text'})
            for state in plan['states']:
                for f in state['objects'].values():
                    self.assertTrue(0<=f['x']<=1-f['w'] and 0<=f['y']<=1-f['h'])

    def test_detached_detail_detected(self):
        plan=make_plan(self.config())
        child=plan['research_metadata']['bindings'][0]['child']
        plan['states'][1]['objects'][child]['x']+=25/1280
        result=binding_metrics(plan)
        self.assertEqual(result['violation_count'],1)
        self.assertEqual(result['max_drift_px'],25)

    def test_unsafe_layout_inputs_rejected(self):
        for n in [2,6]:
            with self.assertRaises(ValueError):make_plan(self.config(n))
        for key,value in [('label','x'*25),('role','x'*39),('id','Invalid ID')]:
            c=self.config();c['layers'][0][key]=value
            with self.assertRaises(ValueError):make_plan(c)
        c=self.config();c['layers'][1]['id']=c['layers'][0]['id']
        with self.assertRaises(ValueError):make_plan(c)

    def test_generation_does_not_modify_input(self):
        c=self.config();before=copy.deepcopy(c)
        make_plan(c);self.assertEqual(c,before)

    def test_proxy_rejects_unsupported_rotation_or_scaling(self):
        for field,value in [('rotation_deg',30),('w',0.3)]:
            plan=make_plan(self.config())
            child=plan['research_metadata']['bindings'][0]['child']
            plan['states'][1]['objects'][child][field]=value
            with self.assertRaises(ValueError):binding_metrics(plan)


if __name__=='__main__':unittest.main()
