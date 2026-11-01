"""T038: Tests for PPTX Design Canon Tokens, Asymmetric & Bento Grids, Optical Balance & Critic Rules."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import design_critic as dc
import design_system as ds
import slide_forge as sf


class DesignCanonTokensTests(unittest.TestCase):
    """Verifies all quantitative design canon tokens loaded from design_system.json."""

    def test_chrome_tokens(self):
        chrome = ds.chrome()
        self.assertIn("slide_dimensions_pt", chrome)
        self.assertEqual(chrome["slide_dimensions_pt"]["w"], 960)
        self.assertEqual(chrome["slide_dimensions_pt"]["h"], 540)
        
        margins = chrome["safe_margins_pt"]
        self.assertEqual(margins["left"], 48)
        self.assertEqual(margins["right"], 48)
        self.assertEqual(margins["top"], 36)
        self.assertEqual(margins["bottom"], 36)

        logo = chrome["logo"]
        self.assertEqual(logo["anchor"], "top_right")
        self.assertLessEqual(logo["max_w_pt"], 72)
        self.assertLessEqual(logo["max_h_pt"], 24)
        self.assertIn("title", logo["hidden_layouts"])
        self.assertIn("closing", logo["hidden_layouts"])
        self.assertIn("duarte_break", logo["hidden_layouts"])

        prog = chrome["progress_bar"]
        self.assertEqual(prog["y_pt"], 537)
        self.assertEqual(prog["h_pt"], 3)

    def test_optical_icon_compensation_math(self):
        # Base size 32 pt
        sq = ds.optical_icon_compensation("square", 32)
        self.assertAlmostEqual(sq["width"], 32 * 0.88, places=2)
        self.assertAlmostEqual(sq["height"], 32 * 0.88, places=2)
        self.assertEqual(sq["dx"], 0.0)
        self.assertEqual(sq["dy"], 0.0)

        circ = ds.optical_icon_compensation("circle", 32)
        self.assertEqual(circ["width"], 32.0)
        self.assertEqual(circ["height"], 32.0)

        wide = ds.optical_icon_compensation("wide", 32)
        self.assertAlmostEqual(wide["width"], 32 * 1.08, places=2)
        self.assertAlmostEqual(wide["height"], 32 * 0.82, places=2)

        tri = ds.optical_icon_compensation("triangle", 32)
        self.assertAlmostEqual(tri["width"], 32 * 1.05, places=2)
        self.assertAlmostEqual(tri["height"], 32 * 1.05, places=2)
        # Apex compensation: shifted upward by -0.06 * 32 = -1.92 pt
        self.assertAlmostEqual(tri["dy"], -32 * 0.06, places=2)

        # Badge multiplier is 2.0x
        self.assertEqual(sq["badge_size"], 64.0)

    def test_bento_grid_coordinates_and_proportions(self):
        bento = ds.bento_grid_layout()
        hero = bento["hero"]
        tr = bento["top_right"]
        br1 = bento["bottom_right_1"]
        br2 = bento["bottom_right_2"]
        gutter = bento["gutter"]

        self.assertEqual(hero["x"], 48)
        self.assertEqual(hero["y"], 108)
        self.assertEqual(hero["w"], 496)
        self.assertEqual(hero["h"], 396)

        self.assertEqual(tr["x"], 564)
        self.assertEqual(tr["y"], 108)
        self.assertEqual(tr["w"], 348)
        self.assertEqual(tr["h"], 188)

        self.assertEqual(br1["x"], 564)
        self.assertEqual(br1["y"], 316)
        self.assertEqual(br1["w"], 164)
        self.assertEqual(br1["h"], 188)

        self.assertEqual(br2["x"], 748)
        self.assertEqual(br2["y"], 316)
        self.assertEqual(br2["w"], 164)
        self.assertEqual(br2["h"], 188)

        self.assertEqual(gutter, 20)
        
        # Verify horizontal layout sums: 48 (margin) + 496 (hero) + 20 (gutter) + 348 (right) + 48 (margin) = 960
        self.assertEqual(48 + hero["w"] + gutter + tr["w"] + 48, 960)
        # Verify right column split: 164 + 20 (gutter) + 164 = 348
        self.assertEqual(br1["w"] + gutter + br2["w"], tr["w"])
        # Verify vertical split: 188 + 20 (gutter) + 188 = 396
        self.assertEqual(tr["h"] + gutter + br1["h"], hero["h"])

    def test_asymmetric_golden_ratio_math(self):
        # Content box width is 864 pt, gutter is 20 pt -> active card width is 844 pt
        # Major card (61.8%): 522 pt, Minor card (38.2%): 322 pt
        asym = ds.asymmetric_golden_layout(reverse=False)
        maj = asym["major"]
        minor = asym["minor"]
        gutter = asym["gutter"]

        self.assertEqual(maj["w"], 522)
        self.assertEqual(minor["w"], 322)
        self.assertEqual(maj["w"] + gutter + minor["w"], 864)
        self.assertEqual(maj["x"], 48)
        self.assertEqual(minor["x"], 48 + 522 + 20)

        # Reversed orientation
        asym_rev = ds.asymmetric_golden_layout(reverse=True)
        self.assertEqual(asym_rev["minor"]["x"], 48)
        self.assertEqual(asym_rev["major"]["x"], 48 + 322 + 20)

    def test_duarte_break_calculation(self):
        self.assertEqual(ds.duarte_break_positions(4), [])
        self.assertEqual(ds.duarte_break_positions(5), [2, 3])
        self.assertEqual(ds.duarte_break_positions(10), [3, 7])
        self.assertEqual(ds.duarte_break_positions(15), [5, 10])

    def test_modular_scale_tokens(self):
        self.assertEqual(ds.modular_scale("caption"), 11)
        self.assertEqual(ds.modular_scale("body_sm"), 13)
        self.assertEqual(ds.modular_scale("body_base"), 14)
        self.assertEqual(ds.modular_scale("card_title"), 18)
        self.assertEqual(ds.modular_scale("section_sub"), 22)
        self.assertEqual(ds.modular_scale("slide_title"), 28)
        self.assertEqual(ds.modular_scale("hero_display"), 44)
        self.assertEqual(ds.modular_scale("kpi_stat"), 72)

    def test_background_layers_depth(self):
        layers = ds.background_layers()
        self.assertIn("z0_canvas", layers)
        self.assertIn("z1_ambient_glow", layers)
        self.assertIn("z2_surface_card", layers)
        self.assertEqual(layers["z1_ambient_glow"]["morph_id_prefix"], "!!")
        self.assertEqual(layers["z1_ambient_glow"]["max_orbs"], 2)


class SlideForgeCanonLayoutsTests(unittest.TestCase):
    """Verifies that Slide Forge compiles asymmetric, bento, and duarte_break layouts."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_build_asymmetric_slide(self):
        out = Path(self.tmp.name) / "asym.pptx"
        spec = {
            "title": "Asymmetric Deck",
            "theme": "midnight",
            "slides": [
                {
                    "layout": "asymmetric",
                    "title": "Market Disruption",
                    "kicker": "Deep Dive",
                    "major": {
                        "heading": "Primary Vector",
                        "text": "Autonomous intelligence bridges native desktop tools with deterministic constraints."
                    },
                    "minor": {
                        "heading": "Impact",
                        "kpi": "10x",
                        "text": "Speed to first draft."
                    }
                }
            ]
        }
        res = sf.build(spec, out)
        self.assertTrue(res["ok"], res.get("errors"))
        self.assertTrue(out.is_file())

        prs = Presentation(str(out))
        s0 = prs.slides[0]
        names = [sh.name for sh in s0.shapes]
        self.assertIn("Major Card", names)
        self.assertIn("Minor Card", names)
        self.assertIn("Major Heading", names)
        self.assertIn("Minor KPI", names)

    def test_build_bento_slide(self):
        out = Path(self.tmp.name) / "bento.pptx"
        spec = {
            "title": "Bento Deck",
            "theme": "paper",
            "slides": [
                {
                    "layout": "bento",
                    "title": "Multi-Tool Ecosystem",
                    "kicker": "Architecture",
                    "hero": {
                        "title": "Central Hub",
                        "text": "Coordinates ArtCraft bridges with universal contracts and dual-layer auditing."
                    },
                    "top_right": {
                        "title": "DeckCraft Engine",
                        "text": "Native Rust headless 1080p renderer."
                    },
                    "bottom_right_1": {
                        "kpi": "<1s",
                        "label": "Render latency"
                    },
                    "bottom_right_2": {
                        "kpi": "100%",
                        "label": "Audit pass rate"
                    }
                }
            ]
        }
        res = sf.build(spec, out)
        self.assertTrue(res["ok"], res.get("errors"))
        self.assertTrue(out.is_file())

        prs = Presentation(str(out))
        s0 = prs.slides[0]
        names = [sh.name for sh in s0.shapes]
        self.assertIn("Hero Card", names)
        self.assertIn("Top Right Card", names)
        self.assertIn("Bottom Right 1", names)
        self.assertIn("Bottom Right 2", names)
        self.assertIn("BR1 KPI", names)

    def test_build_duarte_break_slide(self):
        out = Path(self.tmp.name) / "duarte.pptx"
        spec = {
            "title": "Duarte Deck",
            "theme": "midnight",
            "slides": [
                {
                    "layout": "duarte_break",
                    "kpi": "99.8%",
                    "label": "Deterministic execution without human intervention."
                }
            ]
        }
        res = sf.build(spec, out)
        self.assertTrue(res["ok"], res.get("errors"))
        self.assertTrue(out.is_file())

        prs = Presentation(str(out))
        s0 = prs.slides[0]
        names = [sh.name for sh in s0.shapes]
        self.assertIn("Duarte KPI", names)
        self.assertIn("Duarte Statement", names)

    def test_chrome_injection_progress_bar_and_logo(self):
        out = Path(self.tmp.name) / "chrome_deck.pptx"
        spec = {
            "title": "Chrome Deck",
            "theme": "midnight",
            "chrome": True,
            "logo": "ARTCRAFT",
            "slides": [
                {"layout": "title", "title": "Cover Slide"},
                {"layout": "statement", "text": "Content Slide 1"},
                {"layout": "kpis", "title": "Metrics", "items": [{"value": "1", "label": "one"}]},
                {"layout": "closing", "title": "Closing Slide"}
            ]
        }
        res = sf.build(spec, out)
        self.assertTrue(res["ok"], res.get("errors"))

        prs = Presentation(str(out))
        # Slide 1 (title): progress bar and logo should be suppressed
        s1_names = [sh.name for sh in prs.slides[0].shapes]
        self.assertNotIn("!!progress-bar", s1_names)
        self.assertNotIn("Logo Watermark", s1_names)

        # Slide 3 (kpis - content): progress bar and logo should be present
        s3_names = [sh.name for sh in prs.slides[2].shapes]
        self.assertIn("!!progress-bar", s3_names)
        self.assertIn("Logo Watermark", s3_names)

        # Progress bar position should sit at bottom edge (y >= 7.4 in)
        pbar = next(sh for sh in prs.slides[2].shapes if sh.name == "!!progress-bar")
        self.assertGreaterEqual(pbar.top / 914400, 7.4)


class DesignCriticCanonRulesTests(unittest.TestCase):
    """Verifies that Design Critic validates canon rules (CHROME-SAFE, LAY-BENTO, OPT-ICON, DUA-BREAK)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_critic_validates_bento_and_chrome(self):
        out = Path(self.tmp.name) / "critic_deck.pptx"
        spec = {
            "title": "Test Deck",
            "theme": "midnight",
            "chrome": True,
            "logo": "ARTCRAFT",
            "slides": [
                {"layout": "title", "title": "Cover Slide"},
                {
                    "layout": "bento",
                    "title": "Bento Architecture",
                    "hero": {"title": "Hero", "text": "Core foundation."},
                    "top_right": {"title": "Sub", "text": "Right pillar."},
                    "bottom_right_1": {"kpi": "1", "label": "a"},
                    "bottom_right_2": {"kpi": "2", "label": "b"}
                },
                {"layout": "closing", "title": "Thank you"}
            ]
        }
        sf.build(spec, out)
        verdict = dc.critique(str(out))
        
        eval_codes = {ev[0] for ev in verdict.get("evaluations", [])}
        self.assertIn("CHROME-SAFE", eval_codes)
        self.assertIn("LAY-BENTO", eval_codes)


if __name__ == "__main__":
    unittest.main()
