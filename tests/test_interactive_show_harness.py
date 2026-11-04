"""Tests for the T058 interactive slide-show harness (pure/offline parts).

The Windows desktop and PowerPoint COM paths are covered by an opt-in
integration test (``T058_NATIVE=1``); these tests exercise the geometry,
pixel-diff, calibration, planning and assertion logic without opening
PowerPoint.
"""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

if sys.platform != "win32":  # pragma: no cover - the harness is Windows-only
    raise unittest.SkipTest("interactive_show_harness is Windows-only")

from scripts import interactive_show_harness as h


def _solid(size, color):
    return Image.new("RGB", size, color)


class RectTests(unittest.TestCase):
    def test_geometry_helpers(self):
        r = h.Rect(10, 20, 110, 220)
        self.assertEqual(r.width, 100)
        self.assertEqual(r.height, 200)
        self.assertEqual(r.center, (60, 120))
        self.assertTrue(r.contains_point(10, 20))
        self.assertTrue(r.contains_point(110, 220))
        self.assertFalse(r.contains_point(110.1, 100))
        self.assertTrue(r.contains_rect(h.Rect(20, 30, 100, 200)))
        self.assertFalse(r.contains_rect(h.Rect(20, 30, 120, 200)))
        self.assertEqual(r.inset(10), h.Rect(20, 30, 100, 210))

    def test_union(self):
        a = h.Rect(0, 0, 10, 10)
        b = h.Rect(20, 20, 30, 30)
        self.assertEqual(a.union(b), h.Rect(0, 0, 30, 30))
        self.assertEqual(h.union_of_boxes([a, b]), h.Rect(0, 0, 30, 30))
        self.assertIsNone(h.union_of_boxes([]))


class MappingTests(unittest.TestCase):
    def test_exact_aspect_fills_client(self):
        client = h.Rect(100, 50, 1700, 950)
        m = h.predict_mapping(client, 960, 540)
        self.assertAlmostEqual(m.scale, 1600 / 960, places=6)
        self.assertEqual(m.content, client)

    def test_wider_client_is_height_limited_and_centred(self):
        client = h.Rect(0, 0, 1422, 700)
        m = h.predict_mapping(client, 960, 540)
        self.assertAlmostEqual(m.scale, 700 / 540, places=6)
        self.assertAlmostEqual(m.content.width, 960 * 700 / 540, places=4)
        self.assertAlmostEqual(m.content.left, (1422 - m.content.width) / 2, places=4)
        self.assertAlmostEqual(m.content.top, 0.0, places=4)

    def test_reserve_right_shifts_the_centre(self):
        client = h.Rect(0, 0, 1422, 700)
        full = h.predict_mapping(client, 960, 540)
        reserved = h.predict_mapping(client, 960, 540, reserve_right_px=22)
        self.assertAlmostEqual(full.content.left - reserved.content.left, 11.0, places=4)

    def test_taller_client_is_width_limited(self):
        client = h.Rect(0, 0, 800, 900)
        m = h.predict_mapping(client, 960, 540)
        self.assertAlmostEqual(m.scale, 800 / 960, places=6)
        self.assertAlmostEqual(m.content.height, 540 * 800 / 960, places=4)
        self.assertAlmostEqual(m.content.top, (900 - m.content.height) / 2, places=4)

    def test_point_and_box(self):
        m = h.SlideMapping(960, 540, 2.0, h.Rect(100, 50, 2020, 1130))
        self.assertEqual(m.point(0, 0), (100, 50))
        self.assertEqual(m.point(100, 50), (300, 150))
        self.assertEqual(m.box(0, 0, 10, 20), h.Rect(100, 50, 120, 90))

    def test_shift_keeps_scale(self):
        m = h.SlideMapping(960, 540, 2.0, h.Rect(100, 50, 2020, 1130))
        s = m.shifted(5, -7)
        self.assertEqual(s.scale, 2.0)
        self.assertEqual(s.content, h.Rect(105, 43, 2025, 1123))

    def test_empty_slide_rejected(self):
        with self.assertRaises(h.MappingError):
            h.predict_mapping(h.Rect(0, 0, 100, 100), 0, 540)


class DiffTests(unittest.TestCase):
    def test_no_change(self):
        a = _solid((100, 80), (10, 20, 30))
        st = h.diff_stats(a, a.copy())
        self.assertEqual(st["pct_changed"], 0.0)
        self.assertIsNone(st["changed_bbox"])

    def test_change_inside_box(self):
        a = _solid((100, 80), (0, 0, 0))
        b = a.copy()
        ImageDraw.Draw(b).rectangle((20, 10, 39, 29), fill=(255, 255, 255))
        st = h.diff_stats(a, b)
        self.assertAlmostEqual(st["pct_changed"], 400 / 8000 * 100, places=2)
        self.assertEqual(st["changed_bbox"], [20, 10, 40, 30])

    def test_crop_box_offsets_bbox(self):
        a = _solid((100, 80), (0, 0, 0))
        b = a.copy()
        ImageDraw.Draw(b).rectangle((60, 40, 69, 49), fill=(255, 0, 0))
        st = h.diff_stats(a, b, h.Rect(50, 30, 80, 60))
        self.assertEqual(st["changed_bbox"], [60, 40, 70, 50])
        self.assertAlmostEqual(st["pct_changed"], 100 / (30 * 30) * 100, places=2)

    def test_threshold_ignores_small_deltas(self):
        a = _solid((20, 20), (100, 100, 100))
        b = _solid((20, 20), (120, 120, 120))
        self.assertEqual(h.diff_stats(a, b, threshold=24)["pct_changed"], 0.0)
        self.assertGreater(h.diff_stats(a, b, threshold=12)["pct_changed"], 0.0)

    def test_compare_frames_share_inside(self):
        a = _solid((100, 100), (0, 0, 0))
        b = a.copy()
        ImageDraw.Draw(b).rectangle((10, 10, 29, 29), fill=(255, 255, 255))
        cmp = h.compare_frames(a, b, h.Rect(0, 0, 40, 40))
        self.assertEqual(cmp["inside"]["pct_changed"], 25.0)
        self.assertGreater(cmp["share_inside"], 0.99)

    def test_compare_frames_detects_outside_change(self):
        a = _solid((100, 100), (0, 0, 0))
        b = a.copy()
        ImageDraw.Draw(b).rectangle((80, 80, 99, 99), fill=(255, 255, 255))
        cmp = h.compare_frames(a, b, h.Rect(0, 0, 40, 40))
        self.assertEqual(cmp["inside"]["pct_changed"], 0.0)
        self.assertEqual(cmp["share_inside"], 0.0)
        self.assertGreater(cmp["outside"]["pct_changed"], 0.0)


class CalibrationTests(unittest.TestCase):
    @staticmethod
    def _scene(shift_x=0, shift_y=0):
        export = Image.new("RGB", (320, 180), (245, 245, 245))
        d = ImageDraw.Draw(export)
        d.rectangle((20, 20, 150, 120), fill=(20, 90, 200))
        d.rectangle((180, 40, 300, 160), fill=(220, 60, 40))
        d.text((40, 140), "calibration", fill=(0, 0, 0))
        client = Image.new("RGB", (300, 220), (0, 0, 0))
        patch = export.resize((160, 90), Image.LANCZOS)
        client.paste(patch, (50 + shift_x, 30 + shift_y))
        mapping = h.SlideMapping(960, 540, 1 / 6, h.Rect(50, 30, 210, 120))
        return client, export, mapping, h.Rect(0, 0, 300, 220)

    def test_already_aligned(self):
        client, export, mapping, rect = self._scene()
        res = h.calibrate_mapping(client, export, mapping, rect, max_shift=16)
        self.assertEqual(res["shift_px"], [0, 0])
        self.assertLess(res["mae"], 1.0)

    def test_recovers_known_shift(self):
        client, export, mapping, rect = self._scene(7, -5)
        res = h.calibrate_mapping(client, export, mapping, rect, max_shift=16)
        self.assertEqual(res["shift_px"], [7, -5])
        self.assertLess(res["mae"], 1.0)
        self.assertFalse(res["search_boundary"])

    def test_reports_search_boundary(self):
        client, export, mapping, rect = self._scene(20, 0)
        res = h.calibrate_mapping(client, export, mapping, rect, max_shift=8)
        self.assertTrue(res["search_boundary"])


class EvaluationTests(unittest.TestCase):
    @staticmethod
    def _comparison(inside_pct, outside_pct, share):
        return {
            "whole": {"pct_changed": inside_pct + outside_pct, "changed_px": 1,
                      "area_px": 1, "changed_bbox": None},
            "inside": {"pct_changed": inside_pct, "changed_px": 1, "area_px": 1,
                       "changed_bbox": [1, 1, 2, 2]},
            "outside": {"pct_changed": outside_pct},
            "share_inside": share,
        }

    def test_pixel_change_pass(self):
        ok, why = h._evaluate({"kind": "pixel_change", "min_pct": 2.0},
                              self._comparison(20.0, 0.5, 0.9), None)
        self.assertTrue(ok, why)

    def test_pixel_change_fails_on_low_inside(self):
        ok, why = h._evaluate({"kind": "pixel_change", "min_pct": 2.0},
                              self._comparison(0.1, 0.0, 1.0), None)
        self.assertFalse(ok)
        self.assertIn("inside", why)

    def test_pixel_change_fails_on_low_share(self):
        ok, why = h._evaluate({"kind": "pixel_change", "min_pct": 2.0, "min_share": 0.6},
                              self._comparison(20.0, 30.0, 0.2), None)
        self.assertFalse(ok)
        self.assertIn("share_inside", why)

    def test_noop(self):
        ok, _ = h._evaluate({"kind": "noop", "max_pct": 0.2},
                            self._comparison(0.0, 0.0, 0.0), None)
        self.assertTrue(ok)
        ok, _ = h._evaluate({"kind": "noop", "max_pct": 0.2},
                            self._comparison(0.0, 3.0, 0.0), None)
        self.assertFalse(ok)


class WindowClassTests(unittest.TestCase):
    def test_fullscreen_screen_class(self):
        self.assertTrue(h.is_show_window("screenClass", "anything"))

    def test_windowed_show_title(self):
        self.assertTrue(h.is_show_window(
            "PPTFrameClass", "PowerPoint Slide Show - [deck.pptx [Read-Only]]:2 - PowerPoint Preview"))

    def test_editor_window_is_not_a_show(self):
        self.assertFalse(h.is_show_window(
            "PPTFrameClass", "deck.pptx [Read-Only]:1 - PowerPoint Preview"))

    def test_unrelated_window(self):
        self.assertFalse(h.is_show_window("Chrome_WidgetWin_1", "PowerPoint Slide Show - x"))


class StableWaitTests(unittest.TestCase):
    def test_settles_after_two_identical_frames(self):
        frames = [_solid((20, 20), (0, 0, 0))]
        state = {"i": 0}

        def capture():
            i = state["i"]
            state["i"] += 1
            if i == 0:
                return _solid((20, 20), (0, 0, 0))
            if i == 1:
                return _solid((20, 20), (100, 0, 0))
            return _solid((20, 20), (200, 0, 0))

        res = h.wait_until_stable(capture, timeout_s=2.0, interval_s=0.01, need=2)
        self.assertTrue(res["settled"])
        self.assertEqual(res["frame"].getpixel((0, 0)), (200, 0, 0))

    def test_timeout_is_reported(self):
        state = {"i": 0}

        def capture():
            state["i"] += 1
            v = state["i"] % 2 * 255
            return _solid((10, 10), (v, 0, 0))

        res = h.wait_until_stable(capture, timeout_s=0.15, interval_s=0.01, need=2)
        self.assertFalse(res["settled"])
        self.assertTrue(res["series"])


class PlanTests(unittest.TestCase):
    def test_relative_deck_is_resolved_against_the_plan(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "deck.pptx").write_bytes(b"not really")
            plan_path = d / "plan.json"
            plan_path.write_text(json.dumps({
                "deck": "deck.pptx",
                "steps": [{"action": "goto_slide", "slide": 1}],
            }), encoding="utf-8")
            plan = h._load_plan(plan_path)
            self.assertEqual(Path(plan["deck"]), (d / "deck.pptx").resolve())

    def test_unknown_action_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "plan.json"
            p.write_text(json.dumps({"deck": "x.pptx",
                                     "steps": [{"action": "teleport"}]}), encoding="utf-8")
            with self.assertRaises(h.HarnessError):
                h._load_plan(p)

    def test_click_without_shape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "plan.json"
            p.write_text(json.dumps({"deck": "x.pptx",
                                     "steps": [{"action": "click_shape"}]}), encoding="utf-8")
            with self.assertRaises(h.HarnessError):
                h._load_plan(p)

    def test_empty_steps_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "plan.json"
            p.write_text(json.dumps({"deck": "x.pptx", "steps": []}), encoding="utf-8")
            with self.assertRaises(h.HarnessError):
                h._load_plan(p)


class DesktopTests(unittest.TestCase):
    def test_capability_record_shape(self):
        cap = h.desktop_capability()
        for key in ("pid", "session_id", "window_station", "desktop",
                    "input_desktop_openable", "interactive_desktop", "foreground"):
            self.assertIn(key, cap)
        self.assertIsInstance(cap["interactive_desktop"], bool)

    def test_enumerate_windows_returns_records(self):
        wins = h.enumerate_windows()
        self.assertIsInstance(wins, list)
        if wins:
            for key in ("hwnd", "class", "title", "pid", "rect", "visible"):
                self.assertIn(key, wins[0])

    def test_require_interactive_desktop_raises_when_unavailable(self):
        cap = h.desktop_capability()
        if cap["interactive_desktop"]:
            self.skipTest("this shell has an interactive desktop")
        with self.assertRaises(h.NoInteractiveDesktop):
            h.require_interactive_desktop()


@unittest.skipUnless(os.environ.get("T058_NATIVE") == "1",
                     "set T058_NATIVE=1 to drive PowerPoint")
class NativeIntegrationTests(unittest.TestCase):
    """Opt-in: opens a real windowed show and clicks one trigger."""

    def test_trigger_pixels_change(self):
        root = Path(__file__).resolve().parents[1]
        deck = (root / "experiments" / "T049-20261101-antigravity-advanced-interactivity"
                / "artifacts" / "one_slide_games_suite.pptx")
        if not deck.is_file():
            self.skipTest("T049 deck missing")
        h.enable_dpi_awareness()
        session = h.ShowSession(deck)
        try:
            session.start()
            client = h.client_rect(session.hwnd)
            before = h.capture_rect(client)
            info = session.shape_info(1, "Cover_1")
            mapping = h.predict_mapping(client, session.info["slide_width_pt"],
                                        session.info["slide_height_pt"])
            x, y = mapping.point(info["left_pt"] + info["width_pt"] / 2,
                                 info["top_pt"] + info["height_pt"] / 2)
            h.click_at(x, y)
            time.sleep(3.0)
            after = h.capture_rect(client)
            target = mapping.box(info["left_pt"], info["top_pt"],
                                 info["width_pt"], info["height_pt"])
            local = h.Rect(target.left - client.left, target.top - client.top,
                           target.right - client.left, target.bottom - client.top)
            cmp = h.compare_frames(before, after, local)
            self.assertGreater(cmp["inside"]["pct_changed"], 1.0)
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
