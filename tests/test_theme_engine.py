#!/usr/bin/env python3
"""Unit tests for Dynamic Theme Engine and PPTX Reference Teardown (T043)."""
from pathlib import Path
import unittest

from scripts.theme_engine import (
    PPTXThemeExtractor,
    build_harmonized_image_prompt,
    classify_canvas_mode,
    delta_e_oklab,
    hex_to_rgb,
    oklab_to_oklch,
    oklab_to_rgb,
    oklch_to_oklab,
    relative_luminance,
    rgb_to_hex,
    rgb_to_oklab,
    synthesize_theme_from_need,
    wcag_contrast_ratio,
)

SAMPLE_DECKS_DIR = Path(r"C:\Users\COMPUTER\Desktop\QCC - SHARP Team\reference\sample_decks")


class ColorMathTests(unittest.TestCase):
    def test_hex_rgb_roundtrip(self):
        self.assertEqual(rgb_to_hex(255, 255, 255), "#FFFFFF")
        self.assertEqual(rgb_to_hex(11, 27, 61), "#0B1B3D")
        self.assertEqual(hex_to_rgb("#0B1B3D"), (11, 27, 61))

    def test_relative_luminance_and_contrast(self):
        white = (255, 255, 255)
        black = (0, 0, 0)
        navy = (11, 27, 61)
        self.assertAlmostEqual(relative_luminance(white), 1.0, places=3)
        self.assertAlmostEqual(relative_luminance(black), 0.0, places=3)
        self.assertGreater(relative_luminance(white), relative_luminance(navy))

        # White on black = 21.0
        self.assertAlmostEqual(wcag_contrast_ratio(white, black), 21.0, places=1)
        # White on Navy (#0B1B3D) should be > 13.0
        cr_navy = wcag_contrast_ratio(white, navy)
        self.assertGreater(cr_navy, 13.0)

    def test_oklab_oklch_roundtrip(self):
        rgb_orig = (59, 130, 246)  # #3B82F6
        L, a, b = rgb_to_oklab(rgb_orig)
        L2, C, H = oklab_to_oklch(L, a, b)
        L3, a3, b3 = oklch_to_oklab(L2, C, H)
        rgb_back = oklab_to_rgb(L3, a3, b3)

        self.assertAlmostEqual(L, L3, places=3)
        self.assertAlmostEqual(a, a3, places=3)
        self.assertAlmostEqual(b, b3, places=3)
        self.assertLessEqual(abs(rgb_orig[0] - rgb_back[0]), 1)
        self.assertLessEqual(abs(rgb_orig[1] - rgb_back[1]), 1)
        self.assertLessEqual(abs(rgb_orig[2] - rgb_back[2]), 1)

    def test_classify_canvas_mode(self):
        self.assertEqual(classify_canvas_mode("#0B1B3D"), "DARK_CANVAS")
        self.assertEqual(classify_canvas_mode("#000000"), "DARK_CANVAS")
        self.assertEqual(classify_canvas_mode("#F4F1E9"), "WARM_PAPER")
        self.assertEqual(classify_canvas_mode("#FFFFFF"), "LIGHT_CANVAS")


class PPTXReferenceTeardownTests(unittest.TestCase):
    @unittest.skipUnless(SAMPLE_DECKS_DIR.is_dir(), "Sample decks folder required")
    def test_teardown_blue_modern_pitch_deck(self):
        deck_path = SAMPLE_DECKS_DIR / "Blue Modern Business Pitch Deck Presentation.pptx"
        if not deck_path.is_file():
            self.skipTest(f"Missing sample file: {deck_path}")

        extractor = PPTXThemeExtractor(deck_path)
        spec = extractor.extract()

        self.assertEqual(spec["canvas_mode"], "DARK_CANVAS")
        self.assertEqual(spec["slide_count"], 10)

        # Check Palette: Canvas is deep dark, Text primary is white
        pal = spec["palette_60_30_10"]
        c_rgb = hex_to_rgb(pal["canvas_hex"])
        self.assertLess(relative_luminance(c_rgb), 0.15)
        self.assertIn(pal["text_primary_hex"], ("#FFFFFF", "#F8FAFC"))

        # Check Typography: Aileron detected and mammoth KPI >= 180pt
        typo = spec["typography"]
        self.assertIn("Aileron", typo["font_display"] + typo["font_body"])
        self.assertIsNotNone(typo["hero_kpi_pt"])
        self.assertGreaterEqual(typo["hero_kpi_pt"], 180.0)

        # Check Shape DNA: custGeom detected
        self.assertTrue(spec["shape_dna"]["has_cust_geom_mask"])

    @unittest.skipUnless(SAMPLE_DECKS_DIR.is_dir(), "Sample decks folder required")
    def test_teardown_webinar_keynote_presentation(self):
        deck_path = SAMPLE_DECKS_DIR / "Webinar Keynote Presentation.pptx"
        if not deck_path.is_file():
            self.skipTest(f"Missing sample file: {deck_path}")

        extractor = PPTXThemeExtractor(deck_path)
        spec = extractor.extract()

        self.assertEqual(spec["canvas_mode"], "WARM_PAPER")
        self.assertEqual(spec["slide_count"], 27)

        # Check Palette: Canvas in warm paper range, Text primary dark
        pal = spec["palette_60_30_10"]
        c_rgb = hex_to_rgb(pal["canvas_hex"])
        self.assertGreater(relative_luminance(c_rgb), 0.70)
        t_rgb = hex_to_rgb(pal["text_primary_hex"])
        self.assertLess(relative_luminance(t_rgb), 0.20)

        # Check Typography: TT Commons or TAN Mon Cheri detected
        typo = spec["typography"]
        combined_fonts = typo["font_display"] + " " + typo["font_body"]
        self.assertTrue("TT Commons" in combined_fonts or "TAN Mon Cheri" in combined_fonts)


class NeedBasedSynthesizerTests(unittest.TestCase):
    def test_synthesize_qcc_report(self):
        theme = synthesize_theme_from_need("Báo cáo QCC cải tiến chất lượng dây chuyền sản xuất")
        self.assertEqual(theme["archetype_id"], "INDUSTRIAL_QCC")
        self.assertEqual(theme["canvas_mode"], "LIGHT_CANVAS")
        pal = theme["palette_60_30_10"]
        self.assertGreaterEqual(pal["wcag_contrast_ratio"], 4.5)
        self.assertEqual(theme["shape_dna"]["shape_style"], "SHARP_CHAMFER")

    def test_synthesize_ai_pitch_deck(self):
        theme = synthesize_theme_from_need("Pitch deck gọi vốn AI startup công nghệ")
        self.assertEqual(theme["archetype_id"], "TECH_PITCH_DARK")
        self.assertEqual(theme["canvas_mode"], "DARK_CANVAS")
        pal = theme["palette_60_30_10"]
        self.assertGreaterEqual(pal["wcag_contrast_ratio"], 4.5)
        self.assertEqual(theme["typography"]["font_display"], "Aileron Bold")

    def test_synthesize_editorial_webinar(self):
        theme = synthesize_theme_from_need("Hội thảo văn hóa nội bộ và gắn kết nhân sự")
        self.assertEqual(theme["archetype_id"], "EDITORIAL_WARM_KEYNOTE")
        self.assertEqual(theme["canvas_mode"], "WARM_PAPER")
        pal = theme["palette_60_30_10"]
        self.assertGreaterEqual(pal["wcag_contrast_ratio"], 4.5)
        self.assertEqual(theme["shape_dna"]["shape_style"], "SOFT_ORGANIC_PILL")

    def test_dynamic_hue_override(self):
        # Rotate hue to emerald green (~140 degrees)
        theme = synthesize_theme_from_need("Pitch deck công nghệ tông màu xanh lục", custom_hue_deg=140.0)
        accent_hex = theme["palette_60_30_10"]["accent_primary_hex"]
        rgb = hex_to_rgb(accent_hex)
        L, a, b = rgb_to_oklab(rgb)
        _, _, H = oklab_to_oklch(L, a, b)
        # Check that accent hue is around 140 degrees (+- 15 degrees)
        self.assertAlmostEqual(H, 140.0, delta=15.0)


class ImagePromptHarmonizerTests(unittest.TestCase):
    def test_hero_full_bleed_dark_canvas(self):
        dark_theme = {"canvas_mode": "DARK_CANVAS", "palette_60_30_10": {"accent_primary_hex": "#3B82F6"}}
        res = build_harmonized_image_prompt("Server room with quantum computing core", dark_theme, "hero_full_bleed")

        self.assertEqual(res["aspect_ratio"], "16:9")
        self.assertEqual(res["lighting_kelvin"], 6500)
        self.assertIn("6500K", res["prompt"])
        self.assertIn("60% clean uncluttered negative space", res["prompt"])
        self.assertIn("#3B82F6", res["prompt"])

    def test_split_panel_warm_paper(self):
        warm_theme = {"canvas_mode": "WARM_PAPER", "palette_60_30_10": {"accent_primary_hex": "#FFD0E0"}}
        res = build_harmonized_image_prompt("Confident female team leader smiling", warm_theme, "split_vertical_panel")

        self.assertEqual(res["aspect_ratio"], "4:5")
        self.assertEqual(res["lighting_kelvin"], 3800)
        self.assertIn("3800K", res["prompt"])
        self.assertIn("Kodak Portra", res["prompt"])
        self.assertEqual(res["recommended_mask"], "soft_pill")


if __name__ == "__main__":
    unittest.main()
