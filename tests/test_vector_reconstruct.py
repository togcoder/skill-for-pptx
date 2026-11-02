"""T053 tests: projection, primitives and the semantic SVG contract."""
from __future__ import annotations

import math
import re
import unittest
import xml.etree.ElementTree as ET

from scripts.vector_reconstruct import (
    Projection,
    Scene,
    circle_points,
    convex_hull,
    rounded_rect_points,
)


def _bbox_from_path(d: str) -> tuple[float, float, float, float]:
    match = re.search(r'd="([^"]+)"', d)
    if match:
        d = match.group(1)
    numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
    xs = numbers[0::2]
    ys = numbers[1::2]
    return min(xs), min(ys), max(xs), max(ys)


class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.view = Projection(ox=400, oy=900, sx=4.6, sy=5.5, dx=-2.05, dy=-1.35)

    def test_projection_is_linear(self):
        x0, y0 = self.view.p(0, 0, 0)
        x1, y1 = self.view.p(10, 0, 0)
        self.assertAlmostEqual(x1 - x0, 46.0, places=4)
        self.assertAlmostEqual(y1 - y0, 0.0, places=4)
        x2, y2 = self.view.p(0, 10, 0)
        self.assertAlmostEqual(x2 - x0, 0.0, places=4)
        self.assertAlmostEqual(y2 - y0, -55.0, places=4)
        x3, y3 = self.view.p(0, 0, 10)
        self.assertAlmostEqual(x3 - x0, -20.5, places=4)
        self.assertAlmostEqual(y3 - y0, -13.5, places=4)

    def test_rounded_rect_has_four_corners(self):
        pts = rounded_rect_points(0, 0, 10, 6, 2)
        self.assertGreater(len(pts), 8)
        self.assertTrue(all(0 <= x <= 10 and 0 <= y <= 6 for x, y in pts))

    def test_circle_points_close(self):
        pts = circle_points(5, 5, 3, 32)
        self.assertEqual(len(pts), 32)
        self.assertAlmostEqual(pts[0][0], 8.0, places=4)
        self.assertAlmostEqual(pts[16][0], 2.0, places=4)

    def test_convex_hull_drops_inside_points(self):
        pts = [(0, 0), (10, 0), (10, 10), (0, 10), (5, 5)]
        hull = convex_hull(pts)
        self.assertEqual(len(hull), 4)
        self.assertNotIn((5.0, 5.0), hull)


class PrimitiveTests(unittest.TestCase):
    def setUp(self):
        self.scene = Scene(Projection(400, 900, 4.6, 5.5, -2.05, -1.35))
        self.scene.gradient("g", [(0, "#FFFFFF"), (1, "#000000")])

    def test_box_has_three_faces(self):
        faces = self.scene.box(0, 0, 0, 10, 10, 10, front="url(#g)",
                               side="#AAAAAA", top="#BBBBBB")
        self.assertEqual(len(faces), 3)
        for face in faces:
            self.assertIn("<path", face)
            self.assertTrue(face.endswith("/>") or face.endswith("</path>"))
        self.assertTrue(all("Z" in face for face in faces))

    def test_front_circle_is_round_on_screen(self):
        path = self.scene.front_circle(50, 60, 10, 0, "#FFFFFF")
        x0, y0, x1, y1 = _bbox_from_path(path)
        self.assertAlmostEqual(x1 - x0, y1 - y0, delta=1.5)

    def test_vertical_cylinder_has_side_and_top(self):
        parts = self.scene.cylinder_y(20, 30, 6, 0, 10, side="#AAAAAA", top="#BBBBBB")
        self.assertEqual(len(parts), 2)
        self.assertTrue(all("Z" in part for part in parts))

    def test_tube_draws_outline_plus_metal(self):
        parts = self.scene.tube([(0, 0, 0), (10, 10, 0)], 6, "#CCCCCC")
        self.assertGreaterEqual(len(parts), 2)
        self.assertTrue(any('stroke-width="6' in part for part in parts))

    def test_text_is_on_the_front_plane(self):
        text = self.scene.text_front(50, 80, 0, "QUICK", 3, "#B43A2E")
        self.assertIn(">QUICK</text>", text)
        self.assertIn("font-size=", text)


class DocumentTests(unittest.TestCase):
    def _scene(self) -> Scene:
        scene = Scene(Projection(400, 900, 4.6, 5.5, -2.05, -1.35),
                      width=1000, height=1000)
        scene.gradient("chrome", [(0, "#FFFFFF"), (1, "#999999")])
        scene.body.append('<g id="part">')
        scene.body.extend(scene.box(0, 0, 0, 10, 10, 10, front="url(#chrome)",
                                    side="#AAAAAA", top="#BBBBBB"))
        scene.body.append(scene.front_circle(5, 5, 2, -0.1, "#FFFFFF"))
        scene.body.append("</g>")
        return scene

    def test_svg_is_well_formed_and_has_no_raster(self):
        svg = self._scene().svg(title="Test part", desc="A box and a circle.",
                                metadata={"source": "synthetic", "license": "test"})
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("<title>Test part</title>", svg)
        self.assertNotIn("<image", svg)
        self.assertNotIn("base64", svg)
        self.assertIn('id="part"', svg)

    def test_scene_is_deterministic(self):
        first = self._scene().svg(title="A", desc="B", metadata={})
        second = self._scene().svg(title="A", desc="B", metadata={})
        self.assertEqual(first, second)

    def test_svg_has_a_paper_background(self):
        svg = self._scene().svg(title="A", desc="B", metadata={})
        self.assertIn('id="paper"', svg)
        self.assertIn("#F7F4EC", svg)


if __name__ == "__main__":
    unittest.main()
