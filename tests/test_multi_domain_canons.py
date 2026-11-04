#!/usr/bin/env python3
"""Unit tests for Multi-Domain Design Canons and ArtCraft Bridges (T042)."""
import math
from pathlib import Path
import unittest

from scripts.multi_domain_canons import (
    calculate_action_safe_box,
    calculate_bezier_circle_handle,
    calculate_concentric_fillet,
    calculate_dimension_offset_mm,
    calculate_ducking_attenuation,
    calculate_j_cut_frames,
    calculate_l_cut_frames,
    calculate_micro_bevel_radius,
    calculate_stroke_weight,
    calculate_three_point_lighting,
    calculate_title_safe_box,
    get_3d_canon,
    get_cad_canon,
    get_icon_optical_trim,
    get_iso_7200_title_block_spec,
    get_iso_line_weight,
    get_iso_sheet_dimensions,
    get_isometric_camera_angles,
    get_sound_canon,
    get_vector_canon,
    get_video_canon,
    is_in_vertical_9_16_dead_zone,
    snap_node_coordinate,
    validate_audio_mastering,
    validate_pbr_material,
    validate_video_pacing,
)

from scripts.filmcraft_bridge import find_filmcraft_cli, is_available as filmcraft_available
from scripts.solidcraft_bridge import find_solidcraft_cli, is_available as solidcraft_available
from scripts.cadcraft_bridge import find_cadcraft_cli, is_available as cadcraft_available
from scripts.soundcraft_bridge import find_soundcraft_cli, is_available as soundcraft_available


class VideoCanonTests(unittest.TestCase):
    def test_load_video_canon(self):
        canon = get_video_canon()
        self.assertEqual(canon["domain"], "video")
        self.assertIn("SMPTE RP 2046-2", canon["standards"])
        self.assertIn("landscape_16_9", canon["canvas"])

    def test_safe_margins_16_9(self):
        action = calculate_action_safe_box(1920, 1080, 3.5)
        self.assertEqual(action["x_min"], 67)
        self.assertEqual(action["y_min"], 38)
        self.assertEqual(action["x_max"], 1853)
        self.assertEqual(action["y_max"], 1042)
        self.assertEqual(action["width"], 1786)
        self.assertEqual(action["height"], 1004)

        title = calculate_title_safe_box(1920, 1080, 5.0)
        self.assertEqual(title["x_min"], 96)
        self.assertEqual(title["y_min"], 54)
        self.assertEqual(title["x_max"], 1824)
        self.assertEqual(title["y_max"], 1026)
        self.assertEqual(title["width"], 1728)
        self.assertEqual(title["height"], 972)

    def test_vertical_9_16_dead_zones(self):
        # Center of screen is safe
        in_dz, reason = is_in_vertical_9_16_dead_zone(540, 800)
        self.assertFalse(in_dz)
        self.assertIsNone(reason)

        # Top header
        in_dz, reason = is_in_vertical_9_16_dead_zone(540, 100)
        self.assertTrue(in_dz)
        self.assertEqual(reason, "top_ui_header")

        # Bottom caption
        in_dz, reason = is_in_vertical_9_16_dead_zone(540, 1600)
        self.assertTrue(in_dz)
        self.assertEqual(reason, "bottom_caption_audio")

        # Right action icons
        in_dz, reason = is_in_vertical_9_16_dead_zone(950, 1200)
        self.assertTrue(in_dz)
        self.assertEqual(reason, "right_action_rail")

    def test_video_pacing_and_cuts(self):
        ok, _ = validate_video_pacing(2.0, "promo")
        self.assertTrue(ok)
        ok, _ = validate_video_pacing(0.8, "promo")
        self.assertFalse(ok)
        ok, _ = validate_video_pacing(3.5, "promo")
        self.assertFalse(ok)

        j_min, j_max = calculate_j_cut_frames(30.0)
        self.assertEqual((j_min, j_max), (12, 24))

        l_min, l_max = calculate_l_cut_frames(30.0)
        self.assertEqual((l_min, l_max), (15, 30))

    def test_audio_mastering_validation(self):
        ok, issues = validate_audio_mastering(-14.2, -1.5, "web")
        self.assertTrue(ok)
        self.assertEqual(len(issues), 0)

        ok, issues = validate_audio_mastering(-11.0, -0.5, "web")
        self.assertFalse(ok)
        self.assertEqual(len(issues), 2)


class VectorCanonTests(unittest.TestCase):
    def test_load_vector_canon(self):
        canon = get_vector_canon()
        self.assertEqual(canon["domain"], "vector")
        self.assertEqual(canon["icon_grid_24"]["viewbox"], "0 0 24 24")

    def test_stroke_scaling_formula(self):
        # 16px -> 1.5px
        self.assertAlmostEqual(calculate_stroke_weight(16.0), 1.5, places=2)
        # 24px -> 2.0px
        self.assertAlmostEqual(calculate_stroke_weight(24.0), 2.0, places=2)
        # 32px -> 2.5px
        self.assertAlmostEqual(calculate_stroke_weight(32.0), 2.5, places=2)
        # 48px -> 3.25px
        self.assertAlmostEqual(calculate_stroke_weight(48.0), 3.25, places=2)

    def test_bezier_circle_handle(self):
        # For r = 10, handle should be 10 * 4/3 * (sqrt(2)-1) ~ 5.5228
        h = calculate_bezier_circle_handle(10.0)
        self.assertAlmostEqual(h, 5.5228475, places=4)

    def test_optical_trim_boxes(self):
        c = get_icon_optical_trim("circle")
        self.assertEqual(c["diameter"], 20)
        s = get_icon_optical_trim("square")
        self.assertEqual(s["width"], 18)
        self.assertEqual(s["height"], 18)

    def test_snap_node_coordinate(self):
        # Even stroke weight snaps to integer
        self.assertEqual(snap_node_coordinate(10.2, 2.0), 10.0)
        self.assertEqual(snap_node_coordinate(10.8, 2.0), 11.0)
        # Odd stroke weight snaps to half pixel
        self.assertEqual(snap_node_coordinate(10.2, 1.5), 10.5)


class Solid3DCanonTests(unittest.TestCase):
    def test_load_3d_canon(self):
        canon = get_3d_canon()
        self.assertEqual(canon["domain"], "3d")
        self.assertIn("no_sharp_edge_law", canon)

    def test_micro_bevel_radius(self):
        # Small part: 100 x 50 x 20 -> 0.005 * 20 = 0.1 -> clamped to 0.2
        r_small = calculate_micro_bevel_radius(100.0, 50.0, 20.0)
        self.assertEqual(r_small, 0.2)
        # Large part: 200 x 200 x 200 -> 0.005 * 200 = 1.0 -> clamped to 0.5
        r_large = calculate_micro_bevel_radius(200.0, 200.0, 200.0)
        self.assertEqual(r_large, 0.5)

    def test_concentric_fillet(self):
        # Outer = 4.0, Wall = 1.5 -> Inner = 2.5
        r_in = calculate_concentric_fillet(4.0, 1.5)
        self.assertEqual(r_in, 2.5)
        # Outer = 1.0, Wall = 0.8 -> Inner clamped to 0.5
        r_in_min = calculate_concentric_fillet(1.0, 0.8)
        self.assertEqual(r_in_min, 0.5)

    def test_isometric_elevation(self):
        angles = get_isometric_camera_angles()
        self.assertEqual(angles["azimuth_degrees"], 45.0)
        expected_elev = math.degrees(math.atan(1.0 / math.sqrt(2.0)))
        self.assertAlmostEqual(angles["elevation_degrees"], expected_elev, places=4)
        self.assertAlmostEqual(angles["elevation_degrees"], 35.264, places=2)

    def test_three_point_lighting(self):
        rig = calculate_three_point_lighting(100.0, "technical")
        self.assertEqual(rig["key_light"]["intensity"], 1.00)
        self.assertEqual(rig["fill_light"]["intensity"], 0.50)
        self.assertEqual(rig["key_light"]["distance_mm"], 350.0)

        hero_rig = calculate_three_point_lighting(100.0, "hero")
        self.assertEqual(hero_rig["fill_light"]["intensity"], 0.25)

    def test_pbr_material_validation(self):
        # Valid dielectric
        ok, _ = validate_pbr_material(0.0, 0.5, (120, 120, 120))
        self.assertTrue(ok)
        # Valid conductor
        ok, _ = validate_pbr_material(1.0, 0.1, (200, 200, 200))
        self.assertTrue(ok)
        # Invalid ambiguous metalness
        ok, issues = validate_pbr_material(0.5, 0.5)
        self.assertFalse(ok)
        self.assertTrue(any("Ambiguous metalness" in i for i in issues))
        # Invalid dark albedo
        ok, issues = validate_pbr_material(0.0, 0.5, (10, 10, 10))
        self.assertFalse(ok)
        self.assertTrue(any("too dark" in i for i in issues))


class CadIsoCanonTests(unittest.TestCase):
    def test_load_cad_canon(self):
        canon = get_cad_canon()
        self.assertEqual(canon["domain"], "cad")
        self.assertIn("sheet_sizes_mm", canon)

    def test_iso_sheet_dimensions(self):
        a3 = get_iso_sheet_dimensions("A3")
        self.assertEqual(a3["width"], 420)
        self.assertEqual(a3["height"], 297)
        self.assertEqual(a3["border_margin_left"], 20.0)
        self.assertEqual(a3["border_margin_other"], 10.0)

        a0 = get_iso_sheet_dimensions("A0")
        self.assertEqual(a0["width"], 1189)
        self.assertEqual(a0["height"], 841)
        self.assertEqual(a0["border_margin_left"], 20.0)
        self.assertEqual(a0["border_margin_other"], 20.0)

    def test_iso_line_weight_hierarchy(self):
        # A3 / A4 group (0.50mm group)
        self.assertEqual(get_iso_line_weight("VISIBLE_OUTLINE", "A3"), 0.50)
        self.assertEqual(get_iso_line_weight("HIDDEN_EDGE", "A3"), 0.25)
        self.assertEqual(get_iso_line_weight("CENTER_AXIS", "A3"), 0.18)
        self.assertEqual(get_iso_line_weight("DIMENSION_HATCH", "A3"), 0.18)
        self.assertEqual(get_iso_line_weight("PHANTOM_BOUNDARY", "A3"), 0.18)

        # A0 / A1 group (0.70mm group)
        self.assertEqual(get_iso_line_weight("VISIBLE_OUTLINE", "A0"), 0.70)
        self.assertEqual(get_iso_line_weight("HIDDEN_EDGE", "A0"), 0.35)
        self.assertEqual(get_iso_line_weight("CENTER_AXIS", "A0"), 0.25)

    def test_dimension_offsets(self):
        self.assertEqual(calculate_dimension_offset_mm(1), 10.0)
        self.assertEqual(calculate_dimension_offset_mm(2), 17.0)
        self.assertEqual(calculate_dimension_offset_mm(3), 24.0)

    def test_title_block_iso_7200(self):
        tb = get_iso_7200_title_block_spec()
        self.assertEqual(tb["width_mm"], 180.0)
        self.assertIn("drawing_number", tb["mandatory_fields"])


class SoundCanonTests(unittest.TestCase):
    def test_load_sound_canon(self):
        canon = get_sound_canon()
        self.assertEqual(canon["domain"], "sound")
        self.assertEqual(canon["sample_formats"]["default_sample_rate_hz"], 48000)

    def test_ducking_attenuation(self):
        ducked = calculate_ducking_attenuation(-16.0, -14.0)
        self.assertEqual(ducked, -30.0)


class ArtCraftBridgeDiscoveryTests(unittest.TestCase):
    def test_cli_binaries_discovery(self):
        # Verify that all 4 bridge runners can discover the ArtCraft CLI binaries on this host
        filmcraft = find_filmcraft_cli()
        if filmcraft is None:
            self.skipTest("ArtCraft CLIs are not installed on this host (CI runner)")
        self.assertTrue(filmcraft_available())
        self.assertTrue(filmcraft.is_file())

        solidcraft = find_solidcraft_cli()
        self.assertIsNotNone(solidcraft)
        self.assertTrue(solidcraft_available())
        self.assertTrue(solidcraft.is_file())

        cadcraft = find_cadcraft_cli()
        self.assertIsNotNone(cadcraft)
        self.assertTrue(cadcraft_available())
        self.assertTrue(cadcraft.is_file())

        soundcraft = find_soundcraft_cli()
        self.assertIsNotNone(soundcraft)
        self.assertTrue(soundcraft_available())
        self.assertTrue(soundcraft.is_file())


if __name__ == "__main__":
    unittest.main()
