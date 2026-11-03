"""T054 3D blockout tests: depth structure, not a 2D sticker."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "T054-20261102-opencode-vector-match"


class BlockoutTests(unittest.TestCase):
    def setUp(self):
        self.script = json.loads((EXP / "artifacts" / "blockout.json").read_text(encoding="utf-8"))
        self.cmds = self.script["commands"]
        self.by_name = {}
        for c in self.cmds:
            p = c.get("params", {})
            name = p.get("body_name")
            if c["command"] in {"solid.box", "solid.cylinder"} and name:
                self.by_name[name] = c

    def test_bay_is_a_recess_not_a_flat_panel(self):
        cuts = [c for c in self.cmds if c["command"] == "solid.combine"
                and c["params"].get("operation") == "cut"
                and c["params"].get("target") == "upper_core"]
        self.assertEqual(len(cuts), 1)
        bay = self.by_name["bay_cut"]["params"]
        self.assertGreaterEqual(bay["width"], 120)   # depth into the body
        self.assertGreaterEqual(bay["height"], 200)
        # The bay is open at the front: y starts at -1, not 0.
        self.assertLessEqual(bay["corner"][1], 0)

    def test_top_housing_is_a_deep_box_with_a_soffit(self):
        top = self.by_name["top_housing"]["params"]
        self.assertGreaterEqual(top["height"], 70)
        self.assertGreaterEqual(top["width"], 250)
        self.assertGreaterEqual(top["length"], 300)
        self.assertEqual(self.by_name["top_chrome_left"]["params"]["length"], 152)

    def test_group_head_protrudes_into_the_bay(self):
        group = self.by_name["group_head"]["params"]
        self.assertEqual(group["base"][2], 270)
        self.assertEqual(group["height"], 60)
        self.assertEqual(group["radius"], 50)
        handle = self.by_name["portafilter_handle"]["params"]
        self.assertGreaterEqual(handle["height"], 120)
        self.assertGreaterEqual(handle["radius"], 13)

    def test_switch_plate_is_on_the_lower_front_left(self):
        plate = self.by_name["switch_plate"]["params"]
        self.assertEqual(plate["corner"][1], -4)      # protrudes from the front
        self.assertGreaterEqual(plate["corner"][2], 80)
        self.assertLessEqual(plate["corner"][0] + plate["length"], 160)

    def test_tray_is_cut_into_the_lower_body(self):
        cuts = [c for c in self.cmds if c["command"] == "solid.combine"
                and c["params"].get("operation") == "cut"
                and c["params"].get("target") == "lower_body"]
        self.assertEqual(len(cuts), 1)
        tray = self.by_name["tray_cut"]["params"]
        self.assertGreaterEqual(tray["height"], 25)
        self.assertGreaterEqual(tray["width"], 150)

    def test_3d_view_was_exported_as_vector(self):
        svg = EXP / "artifacts" / "blockout.svg"
        self.assertTrue(svg.exists())
        text = svg.read_text(encoding="utf-8")
        self.assertGreater(text.count("<polyline") + text.count("<path"), 800)
        self.assertNotIn("<image", text)
        self.assertTrue((EXP / "artifacts" / "blockout.dxf").exists())


if __name__ == "__main__":
    unittest.main()
