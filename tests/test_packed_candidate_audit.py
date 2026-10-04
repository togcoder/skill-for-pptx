import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_packed_candidate import layout_anchor_error, polyline


class PackedAuditTests(unittest.TestCase):
    def test_distinguishes_stage_relative_from_layout_relative_coordinates(self):
        planned = [{"x":.4,"y":.25},{"x":.6,"y":.25}]
        # Second motion starts at .4, but the authored center was .2.
        self.assertAlmostEqual(layout_anchor_error(polyline("M 0 0 L .2 0 E"),planned,(.2,.25)),256)
        self.assertAlmostEqual(layout_anchor_error(polyline("M .2 0 L .4 0 E"),planned,(.2,.25)),0)

    def test_parser_rejects_unhandled_curve_and_nonfinite_coordinates(self):
        for value in ("M 0 0 C 0 0 1 1 2 2 E", "M 0 0 L nan 1 E", "M 0 0 L 1 1"):
            with self.assertRaises(ValueError):
                polyline(value)

    def test_point_count_mismatch_is_not_silently_truncated(self):
        with self.assertRaises(ValueError):
            layout_anchor_error([[0,0]],[{"x":0,"y":0},{"x":1,"y":1}],(0,0))
