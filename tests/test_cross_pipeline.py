#!/usr/bin/env python3
"""Unit tests for Cross-Asset Pipeline Validator and Protocol Conformance (T044)."""
from pathlib import Path
import unittest
from PIL import Image

from scripts.cross_pipeline import (
    validate_audio_for_muxing,
    validate_chart_data_for_presentation,
    validate_image_for_embedding,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class CrossAssetPipelineTests(unittest.TestCase):
    def test_image_validation_hero_full_bleed(self):
        # 1. High-res 16:9 image
        im_16_9 = Image.new("RGB", (1920, 1080), color=(20, 30, 50))
        res = validate_image_for_embedding(im_16_9, slot_type="hero_full_bleed", canvas_mode="DARK_CANVAS")
        self.assertTrue(res["is_valid"])
        self.assertEqual(len(res["errors"]), 0)
        self.assertEqual(res["aspect_ratio"], 1.778)

        # 2. Low-res image failing minimum resolution
        im_small = Image.new("RGB", (300, 200), color=(20, 30, 50))
        res_small = validate_image_for_embedding(im_small, slot_type="hero_full_bleed")
        self.assertFalse(res_small["is_valid"])
        self.assertTrue(any("resolution" in e for e in res_small["errors"]))

        # 3. Square image generating aspect ratio warning for 16:9 slot
        im_square = Image.new("RGB", (1000, 1000), color=(20, 30, 50))
        res_sq = validate_image_for_embedding(im_square, slot_type="hero_full_bleed")
        self.assertTrue(res_sq["is_valid"])  # Valid resolution but warning on aspect ratio
        self.assertTrue(any("Aspect ratio" in w for w in res_sq["warnings"]))

    def test_image_validation_translucent_art_wash(self):
        # 1. RGB image without Alpha band must fail for translucent_art_wash
        im_rgb = Image.new("RGB", (800, 800), color=(255, 200, 220))
        res_rgb = validate_image_for_embedding(im_rgb, slot_type="translucent_art_wash")
        self.assertFalse(res_rgb["is_valid"])
        self.assertTrue(any("strictly requires an Alpha channel" in e for e in res_rgb["errors"]))

        # 2. RGBA image with translucent pixels must pass
        im_rgba = Image.new("RGBA", (800, 800), color=(255, 200, 220, 128))
        res_rgba = validate_image_for_embedding(im_rgba, slot_type="translucent_art_wash")
        self.assertTrue(res_rgba["is_valid"])
        self.assertTrue(res_rgba["has_alpha"])

    def test_audio_validation_ebu_r128(self):
        # 1. Compliant broadcast master
        res_ok = validate_audio_for_muxing(
            integrated_lufs=-14.0, true_peak_dbtp=-1.5, has_voiceover=True, bgm_ducking_db=-14.0
        )
        self.assertTrue(res_ok["is_valid"])
        self.assertEqual(len(res_ok["errors"]), 0)

        # 2. Clipping violation (True Peak > -1.0 dBTP)
        res_clip = validate_audio_for_muxing(
            integrated_lufs=-14.0, true_peak_dbtp=0.5
        )
        self.assertFalse(res_clip["is_valid"])
        self.assertTrue(any("True Peak" in e for e in res_clip["errors"]))

        # 3. Excessive Loudness penalty
        res_loud = validate_audio_for_muxing(
            integrated_lufs=-10.0, true_peak_dbtp=-2.0
        )
        self.assertFalse(res_loud["is_valid"])
        self.assertTrue(any("too loud" in e for e in res_loud["errors"]))

    def test_chart_data_validation(self):
        # 1. Valid multi-series data
        valid_series = [
            {"name": "Revenue", "values": [100.0, 120.0, 150.0]},
            {"name": "Cost", "values": [60.0, 70.0, 85.0]},
        ]
        res_chart = validate_chart_data_for_presentation(valid_series)
        self.assertTrue(res_chart["is_valid"])
        self.assertEqual(res_chart["series_count"], 2)
        self.assertEqual(res_chart["point_count"], 3)

        # 2. Series with NaN / null
        dirty_series = [
            {"name": "Revenue", "values": [100.0, None, 150.0]},
            {"name": "Cost", "values": [60.0, float('nan'), 85.0]},
        ]
        res_dirty = validate_chart_data_for_presentation(dirty_series)
        self.assertFalse(res_dirty["is_valid"])
        self.assertEqual(len(res_dirty["errors"]), 2)

    def test_all_five_lab_protocols_exist(self):
        proto_dir = REPO_ROOT / "lab" / "protocols"
        expected = [
            "00_intent_empathy_decoder.md",
            "01_capability_first_gate.md",
            "02_cross_delegation_dag.md",
            "03_redteam_critique_rubric.md",
            "04_cross_asset_pipeline.md",
        ]
        for p_name in expected:
            p_file = proto_dir / p_name
            self.assertTrue(p_file.is_file(), f"Missing required protocol file: {p_name}")
            content = p_file.read_text(encoding="utf-8")
            self.assertGreater(len(content), 100, f"Protocol {p_name} is too short or empty")


if __name__ == "__main__":
    unittest.main()
