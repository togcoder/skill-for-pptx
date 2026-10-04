import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from choreography import compile_intent, validate_intent
from validate_plan import validate
EXPERIMENT=ROOT/"experiments/T005-20261004-codex-choreography"
spec=importlib.util.spec_from_file_location("intent_checks",EXPERIMENT/"verify_intent.py")
checks=importlib.util.module_from_spec(spec);spec.loader.exec_module(checks)


class ChoreographyTests(unittest.TestCase):
    def config(self):return json.loads((EXPERIMENT/"candidate.intent.json").read_text())

    def test_candidate_semantics_and_plan(self):
        c=self.config();p=compile_intent(c)
        self.assertEqual(validate(p),[])
        self.assertTrue(checks.check(c,p)["passed"])
        self.assertEqual(len(p["states"]),12)
        self.assertEqual(len(p["objects"]),31)

    def test_geometry_mutations_are_detected(self):
        c=self.config();p=compile_intent(c)
        for sid,oid,key,value in [("orbit-2","label-1","x",0.1),("focus","node-3-layer-1","w",0.1),
                                   ("restore","label-4","x",0.2),("split","label-3","rotation_deg",15)]:
            bad=copy.deepcopy(p);bad["states"][next(i for i,s in enumerate(bad["states"]) if s["id"]==sid)]["objects"][oid][key]=value
            self.assertFalse(checks.check(c,bad)["passed"])

    def test_unknown_unsupported_and_invalid_rejected(self):
        for k,v in [("timeline",True),("recipe","fluid"),("node_count",True),("focus_node",13),
                    ("orbit_degrees",float("nan")),("orbit_segments",0),("direction","left"),
                    ("keep_labels_upright",False),("operations",["split","orbit"]),
                    ("title","x"*46),("assumptions",[]),("layer_count",6)]:
            c=self.config();c[k]=v
            with self.assertRaises(ValueError):compile_intent(c)

    def test_boundaries_and_reverse_full_orbit(self):
        for n in [6,12]:
            for layers in [3,5]:
                c=self.config();c.update(node_count=n,focus_node=n,layer_count=layers,
                    direction="counterclockwise",orbit_degrees=360,orbit_segments=24)
                p=compile_intent(c)
                self.assertEqual(validate(p),[])
                self.assertTrue(checks.check(c,p)["passed"])

    def test_deterministic_nonmutating(self):
        c=self.config();saved=copy.deepcopy(c)
        self.assertEqual(compile_intent(c),compile_intent(c));self.assertEqual(c,saved)

    def test_full_revolution_cannot_collapse_to_same_endpoint(self):
        c=self.config();c.update(orbit_degrees=360,orbit_segments=1)
        with self.assertRaises(ValueError):compile_intent(c)

    def test_waypoints_reduce_proxy_error(self):
        c=self.config();fine=checks.check(c,compile_intent(c))
        c["orbit_segments"]=1;coarse=checks.check(c,compile_intent(c))
        self.assertLess(fine["orbit_linear_proxy"]["max_radial_deviation_px"],2)
        self.assertGreater(coarse["orbit_linear_proxy"]["max_radial_deviation_px"],65)


if __name__=="__main__":unittest.main()
