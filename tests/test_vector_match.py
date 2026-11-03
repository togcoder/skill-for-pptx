"""T054 tests: the landmark fractions and the semantic SVG contract."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENE = (ROOT / "experiments" / "T054-20261102-opencode-vector-match"
         / "inputs" / "build_quickmill.py")


def _load_scene():
    spec = importlib.util.spec_from_file_location("t054_scene", SCENE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["t054_scene"] = module
    spec.loader.exec_module(module)
    return module


class LandmarkTests(unittest.TestCase):
    def setUp(self):
        self.mod = _load_scene()
        self.d = self.mod.Dimensions()

    def test_landmarks_match_the_photo_fractions(self):
        h = self.d.top_top
        self.assertAlmostEqual((h - self.d.black_bottom) / h, 0.216, delta=0.01)
        self.assertAlmostEqual((h - self.d.group_y) / h, 0.275, delta=0.01)
        self.assertAlmostEqual((h - self.d.tray_top) / h, 0.520, delta=0.01)
        self.assertAlmostEqual((h - self.d.lower_top) / h, 0.618, delta=0.01)
        self.assertAlmostEqual((h - self.d.base_h) / h, 0.843, delta=0.01)

    def test_body_aspect_is_close_to_the_photo(self):
        # Object width/height; the projected width adds the side depth, so
        # this is a sanity check on the vertical rebalance, not the projection.
        self.assertAlmostEqual(self.d.width / self.d.top_top, 0.678, delta=0.03)

    def test_front_split_matches_the_photo(self):
        # Photo: front face 390..930, chrome/black seam at 600 -> 0.389.
        self.assertAlmostEqual(self.d.front_split_frac, 0.40, delta=0.02)
        split_x = self.d.x0 + self.d.width * self.d.front_split_frac
        # The switch plate ends at the split, directly below the chrome panel.
        self.assertAlmostEqual(split_x, 42.0, delta=0.5)

    def test_scene_is_parametric(self):
        base = self.mod.build()
        narrow = self.mod.build(self.mod.Dimensions(width=74))
        self.assertNotEqual(base, narrow)
        self.assertEqual(base.count('<g id="'), 16)
        self.assertGreaterEqual(base.count("<path"), 100)
        self.assertNotIn("<image", base)
        self.assertEqual(base, self.mod.build())

    def test_legend_groups_are_semantic(self):
        svg = self.mod.build()
        for name in ("top-panel", "group-head", "portafilter", "drip-tray", "badge"):
            self.assertIn(f'id="{name}"', svg)


if __name__ == "__main__":
    unittest.main()
