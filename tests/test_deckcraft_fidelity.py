#!/usr/bin/env python3
"""Tests for the DeckCraft fidelity harness (T059) — EXPERIMENTAL.

Pure functions are tested without PowerPoint or DeckCraft. The fallback test
mocks both renderers, so it also runs on hosts without either.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches
from lxml import etree

from scripts.deckcraft_fidelity import (
    FRAME_H,
    FRAME_W,
    detect_transition_start,
    diff_map,
    region_metrics,
    render_frames_with_fallback,
    shape_kinds,
    timing_inventory,
    visibility_label,
    _alpha_estimate,
)

A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def _png(path: Path, colour=(200, 200, 200)) -> Path:
    Image.new("RGB", (FRAME_W, FRAME_H), colour).save(path)
    return path


class RegionTests(unittest.TestCase):
    def test_mean_and_thresholds(self):
        a = np.zeros((10, 10, 3), dtype=np.uint8)
        b = a.copy()
        b[:5, :, 0] = 60
        m = region_metrics(diff_map(a, b))
        self.assertEqual(m["pixels"], 100)
        self.assertAlmostEqual(m["mean_abs"], 30.0, places=3)
        self.assertAlmostEqual(m["pct_gt40"], 50.0, places=3)
        self.assertAlmostEqual(m["pct_gt10"], 50.0, places=3)
        self.assertEqual(m["max_abs"], 60)

    def test_empty_mask(self):
        m = region_metrics(np.zeros((4, 4), dtype=np.uint8), np.zeros((4, 4), dtype=bool))
        self.assertEqual(m["pixels"], 0)
        self.assertIsNone(m["mean_abs"])


class ShapeKindTests(unittest.TestCase):
    def test_text_chart_picture_gradient_effects(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            pic = td / "p.png"
            Image.new("RGB", (80, 60), (120, 30, 30)).save(pic)
            prs = Presentation()
            prs.slide_width, prs.slide_height = Inches(10), Inches(5.625)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            text = slide.shapes.add_textbox(Inches(0.2), Inches(0.2), Inches(2), Inches(0.5))
            text.text_frame.text = "Hello"
            picture = slide.shapes.add_picture(str(pic), Inches(0.2), Inches(1), Inches(1), Inches(0.75))
            cd = CategoryChartData()
            cd.categories = ["a", "b"]
            cd.add_series("s", (1, 2))
            chart = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(3), Inches(1),
                                           Inches(4), Inches(2.5), cd)
            grad = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.2), Inches(3), Inches(2), Inches(1))
            spPr = grad._element.spPr
            solid = spPr.find(f"{{{A}}}solidFill")
            if solid is not None:
                spPr.remove(solid)
            spPr.append(etree.fromstring(
                f'<a:gradFill xmlns:a="{A}"><a:gsLst>'
                f'<a:gs pos="0"><a:srgbClr val="FF0000"/></a:gs>'
                f'<a:gs pos="100000"><a:srgbClr val="0000FF"/></a:gs>'
                f'</a:gsLst><a:lin ang="0"/></a:gradFill>'))
            shadow = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3), Inches(3), Inches(2), Inches(1))
            shadow._element.spPr.append(etree.fromstring(
                f'<a:effectLst xmlns:a="{A}"><a:outerShdw blurRad="63500" dist="38100" dir="5400000"/>'
                f'</a:effectLst>'))
            self.assertIn("text", shape_kinds(text))
            self.assertIn("picture", shape_kinds(picture))
            self.assertIn("chart", shape_kinds(chart))
            self.assertIn("gradient", shape_kinds(grad))
            self.assertIn("effects", shape_kinds(shadow))


class TimingTests(unittest.TestCase):
    def test_inventory_reads_effects_from_a_real_deck(self):
        sample = Path(__file__).resolve().parents[0] / "fixtures" / "report_deck.pptx"
        if not sample.is_file():
            self.skipTest("fixture missing")
        inv = timing_inventory(sample, 5)
        self.assertGreater(inv["total_ctn"], 0)
        self.assertTrue(inv["effects"])
        self.assertTrue(any(e.get("preset") for e in inv["effects"]))

    def test_missing_timing_is_empty(self):
        sample = Path(__file__).resolve().parents[0] / "fixtures" / "report_deck.pptx"
        if not sample.is_file():
            self.skipTest("fixture missing")
        inv = timing_inventory(sample, 0)
        self.assertEqual(inv["effects"], [])


class VisibilityTests(unittest.TestCase):
    def test_final_and_previous(self):
        prev = np.zeros((100, 100, 3), dtype=np.uint8)
        final = np.full((100, 100, 3), 200, dtype=np.uint8)
        self.assertEqual(visibility_label(final, prev, final, [10, 10, 50, 50])[0], "final")
        self.assertEqual(visibility_label(prev, prev, final, [10, 10, 50, 50])[0], "previous")

    def test_alpha_estimate(self):
        prev = np.zeros((100, 100, 3), dtype=np.uint8)
        final = np.full((100, 100, 3), 200, dtype=np.uint8)
        frame = np.full((100, 100, 3), 100, dtype=np.uint8)
        self.assertAlmostEqual(_alpha_estimate(frame, prev, final, [0, 0, 100, 100]), 0.5, places=2)


class TransitionTests(unittest.TestCase):
    def test_detects_first_changed_frame(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            frames = []
            for i in range(12):
                if i < 6:
                    colour = (240, 240, 240)
                else:
                    v = max(10, 240 - (i - 5) * 40)
                    colour = (v, v, v)
                p = td / f"f-{i:04d}.png"
                Image.new("RGB", (FRAME_W, FRAME_H), colour).save(p)
                frames.append(p)
            self.assertEqual(detect_transition_start(frames, fps=10, skip_s=0.2, threshold=0.12), 6)


class FallbackTests(unittest.TestCase):
    def test_powerpoint_path_labels_powerpoint(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            out = td / "frames"

            def fake_pp(pptx, out_dir):
                out_dir.mkdir(parents=True, exist_ok=True)
                return [_png(out_dir / "slide-01.png")]

            with mock.patch("scripts.deckcraft_fidelity.powerpoint_export", side_effect=fake_pp):
                result = render_frames_with_fallback(td / "deck.pptx", out)
            self.assertEqual(result["renderer"], "powerpoint")
            self.assertEqual(result["label"], "PowerPoint Slide.Export")
            self.assertEqual(result["evidence_rung"], 5)

    def test_fallback_is_never_labelled_powerpoint(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            out = td / "frames"

            def fake_dc(pptx, out_dir, scale=2):
                out_dir.mkdir(parents=True, exist_ok=True)
                return [_png(out_dir / "slide-01.png")]

            with mock.patch("scripts.deckcraft_fidelity.powerpoint_export",
                            side_effect=RuntimeError("no PowerPoint")), \
                 mock.patch("scripts.deckcraft_fidelity.deckcraft_render", side_effect=fake_dc):
                result = render_frames_with_fallback(td / "deck.pptx", out)
            self.assertEqual(result["renderer"], "deckcraft")
            self.assertIn("not PowerPoint", result["label"])
            self.assertNotIn("PowerPoint Slide.Export", result["label"])
            self.assertEqual(result["evidence_rung"], 2)
            self.assertIsNone(result["video"])
            self.assertTrue(result["note"])


if __name__ == "__main__":
    unittest.main()
