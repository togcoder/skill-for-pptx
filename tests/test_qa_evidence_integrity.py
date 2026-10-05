import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from verify_powerpoint_qa import verify
from qa_evidence_cases import challenge_cases, positive_control


class QaEvidenceIntegrityTests(unittest.TestCase):
    def test_frozen_challenge_set(self):
        for name, manifest, evidence, expected_parse, expected_click in challenge_cases():
            with self.subTest(case=name):
                original = copy.deepcopy((manifest, evidence))
                claims = verify(manifest, evidence)["claims"]
                self.assertEqual(claims["native_application_parse_verified"], expected_parse)
                self.assertEqual(claims["native_click_execution_verified"], expected_click)
                self.assertEqual(claims["native_click_index_progression_verified"], expected_click)
                self.assertFalse(claims["animation_completion_verified"])
                self.assertFalse(claims["native_playback_verified"])
                self.assertFalse(claims["visual_state_verified"])
                self.assertEqual((manifest, evidence), original)

    def test_malformed_top_level_fails_without_crash(self):
        for manifest, evidence in [(None, None), ([], []), ({}, {}), (42, "error")]:
            with self.subTest(manifest=manifest):
                self.assertFalse(verify(manifest, evidence)["claims"]["native_click_execution_verified"])

    def test_capture_paths_do_not_prove_visual_playback(self):
        m, e = positive_control()
        e["slideshow"]["slides"][0]["clicks"][0]["capture"] = {"path": "nonexistent.png"}
        claims = verify(m, e)["claims"]
        self.assertEqual(claims["visual_capture_count"], 1)
        self.assertFalse(claims["visual_state_verified"])
        self.assertFalse(claims["native_playback_verified"])


if __name__ == "__main__":
    unittest.main()
