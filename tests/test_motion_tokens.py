"""T029: design-system easing fitted to PowerPoint accel/decel."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

import motion_engine as me
import motion_tokens as mt


class MotionTokenTests(unittest.TestCase):
    def test_powerpoint_progress_is_a_monotone_unit_curve(self):
        for a,d in ((0,0),(0.15,0.7),(0.35,0),(0,1),(1,0)):
            vals=[mt.ppt_progress(i/50,a,d) for i in range(51)]
            self.assertAlmostEqual(vals[0],0,places=6)
            self.assertAlmostEqual(vals[-1],1,places=6)
            self.assertTrue(all(b>=a_-1e-9 for a_,b in zip(vals,vals[1:])))

    def test_roles_reproduce_their_curves_closely(self):
        for role,token in mt.ROLES.items():
            a,d,err=mt.fit(mt.EASINGS[token][0])
            self.assertLessEqual(a+d,1.0)
            self.assertLess(err,0.1,role)

    def test_entrances_decelerate_and_exits_accelerate(self):
        a,d=mt.ease("enter")
        self.assertGreater(d,a)
        a,d=mt.ease("exit")
        self.assertGreater(a,d)
        self.assertEqual(me.EASE["standard"],mt.ease("standard"))

    def test_longer_journeys_take_longer_within_bounds(self):
        self.assertLess(mt.travel_ms(0.05),mt.travel_ms(0.6))
        self.assertEqual(mt.travel_ms(5),1200)


if __name__=="__main__":
    unittest.main()
