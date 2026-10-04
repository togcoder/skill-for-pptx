import copy
import unittest
from scripts.validate_plan import validate


def fixture():
    frame = dict(x=.1,y=.1,w=.2,h=.2,rotation_deg=0,opacity=1)
    return dict(version='0.1',brief='Move one object',canvas=dict(width=16,height=9,units='normalized'),
        data_provenance='none',objects=[dict(id='orb',kind='shape',persistent=True,morph_name='!!orb')],
        states=[dict(id='start',message='Start',objects={'orb':copy.deepcopy(frame)}),
                dict(id='end',message='End',objects={'orb':dict(frame,x=.6)})],
        transitions=[dict(kind='morph',duration_ms=1000,**{'from':'start','to':'end'},track=['orb'])])


class ContractTests(unittest.TestCase):
    def test_valid_plan(self): self.assertEqual(validate(fixture()),[])
    def test_missing_persistent_object(self):
        p=fixture();p['states'][1]['objects']={};self.assertTrue(validate(p))
    def test_duplicate_forced_name(self):
        p=fixture();p['objects'].append(dict(p['objects'][0],id='other'));self.assertTrue(validate(p))
    def test_nonfinite_geometry(self):
        p=fixture();p['states'][0]['objects']['orb']['x']=float('nan');self.assertTrue(validate(p))
    def test_unplanned_offcanvas(self):
        p=fixture();p['states'][0]['objects']['orb']['x']=-.2;self.assertTrue(validate(p))
    def test_explicit_offcanvas(self):
        p=fixture();p['states'][0]['objects']['orb'].update(x=-.2,off_canvas=True);self.assertEqual(validate(p),[])
    def test_bad_transition_order(self):
        p=fixture();p['transitions'][0]['to']='start';self.assertTrue(validate(p))
    def test_no_native_chart_morph_claim(self):
        p=fixture();p['objects'][0]['kind']='chart';self.assertTrue(validate(p))
    def test_invalid_kind_does_not_crash(self):
        p=fixture();p['objects'][0]['kind']=[];self.assertTrue(validate(p))
    def test_bool_is_not_dimension(self):
        p=fixture();p['canvas']['width']=True;self.assertTrue(validate(p))
    def test_zero_duration(self):
        p=fixture();p['transitions'][0]['duration_ms']=0;self.assertTrue(validate(p))
    def test_unknown_track(self):
        p=fixture();p['transitions'][0]['track']=['missing'];self.assertTrue(validate(p))


if __name__=='__main__': unittest.main()
