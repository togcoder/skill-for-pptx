"""Cross-check the triangle bound against the frozen continuous path diagnostic."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from cyclic_label_clearance import clearance
spec=importlib.util.spec_from_file_location('frozen_path',ROOT/'experiments/E003/path_diagnostic.py')
diag=importlib.util.module_from_spec(spec);spec.loader.exec_module(diag)


def plan(w,h,gap,d=420):
    slots=[(640-d,560),(640,560-gap),(640+d,560)]
    states=[]
    for n,order in enumerate([['b','a','c'],['c','b','a']]):
        frames={key:dict(x=(cx-w/2)/1280,y=(cy-h/2)/720,w=w/1280,h=h/720,rotation_deg=0)
                for key,(cx,cy) in zip(order,slots)}
        states.append(dict(id=str(n),objects=frames))
    return dict(states=states)


class ClearanceTests(unittest.TestCase):
    def test_prior_small_and_new_long_labels(self):
        for w,h,g,expected in [(200,64,200,True),(360,96,200,False),(360,96,300,True)]:
            with self.subTest(w=w,h=h,g=g):
                result=clearance(420,w,h,g)
                actual=diag.evaluate(plan(w,h,g),['a','b','c'])['overlapping_pairs']==0
                self.assertEqual(actual,expected)
                self.assertEqual(result['predicted_positive_area_overlap_free'],actual)
                self.assertFalse(result['native_playback_verified'])

    def test_near_boundary_without_float_edge_ambiguity(self):
        for gap,expected in [(251,False),(253,True)]:
            result=clearance(420,360,96,gap)
            self.assertEqual(result['minimum_vertical_gap_px'],252)
            self.assertEqual(diag.evaluate(plan(360,96,gap),['a','b','c'])['overlapping_pairs']==0,expected)
            self.assertEqual(result['predicted_positive_area_overlap_free'],expected)

    def test_diagonal_routes_too_wide(self):
        with self.assertRaises(ValueError):clearance(420,430,96,500)
        self.assertGreater(diag.evaluate(plan(430,96,500),['a','b','c'])['overlapping_pairs'],0)

    def test_invalid_dimensions(self):
        for invalid in [0,-1,float('nan'),float('inf'),True,'96']:
            with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                clearance(420,360,invalid,300)


if __name__=='__main__':unittest.main()
