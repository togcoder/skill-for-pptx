import hashlib
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from inspect_existing_deck import inspect_existing_deck

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


class ExistingDeckInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=inspect_existing_deck(SOURCE)

    def test_h001_inventory_reads_source_without_errors(self):
        self.assertEqual(self.report["errors"],[])
        self.assertEqual(self.report["source_sha256"],hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(len(self.report["slides"]),2)
        self.assertEqual([s["index"] for s in self.report["slides"]],[1,2])

    def test_inventory_preserves_semantic_names_and_order(self):
        for slide in self.report["slides"]:
            self.assertEqual(slide["shape_count"],12)
            forced=[s["forced_semantic_name"] for s in slide["shapes"] if s["forced_semantic_name"]]
            self.assertEqual(len(forced),12)
            self.assertEqual(len(forced),len(set(forced)))
            self.assertEqual([s["z_index"] for s in slide["shapes"]],list(range(1,13)))

    def test_geometry_is_normalized(self):
        for slide in self.report["slides"]:
            for shape in slide["shapes"]:
                geom=shape["geometry"]
                self.assertIsNotNone(geom)
                self.assertGreater(geom["w"],0)
                self.assertGreater(geom["h"],0)

    def test_existing_motion_is_detected(self):
        self.assertFalse(self.report["slides"][0]["has_transition"])
        self.assertTrue(self.report["slides"][1]["has_transition"])

    def test_transition_summary_exposes_existing_transition(self):
        first,second=self.report["slides"]
        self.assertIsNone(first["transition_summary"])
        self.assertIsNotNone(second["transition_summary"])
        variants=second["transition_summary"]["variants"]
        names={name for variant in variants for name in variant["descendants"]}
        self.assertTrue("morph" in names or "fade" in names)

    def test_speaker_notes_are_detected_when_present(self):
        notes=[slide["speaker_notes"] for slide in self.report["slides"] if slide["speaker_notes"]]
        self.assertTrue(notes)
        self.assertTrue(any("Collect" in note and "Inspect" in note for note in notes))

    def test_design_fingerprint_is_exposed(self):
        profile=self.report["design_profile"]
        self.assertTrue(profile["fill_colors"])
        self.assertTrue(profile["geometry_presets"])
        self.assertTrue(any(shape["style"] for slide in self.report["slides"] for shape in slide["shapes"]))

    def test_package_capabilities_are_exposed(self):
        self.assertTrue(self.report["package"]["has_theme"])
        self.assertTrue(self.report["slide_size_emu"]["width"]>0)
        self.assertTrue(self.report["slide_size_emu"]["height"]>0)


if __name__=="__main__":
    unittest.main()
