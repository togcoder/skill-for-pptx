"""T051 tests: geometry, edge policy, detail budgets and SVG layers."""
from __future__ import annotations

import math
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.photo_vector import (
    BUDGETS,
    Edge,
    Segment,
    classify_edges,
    polyline_to_path,
    rdp,
)

try:
    import cv2
    import numpy as np
    HAVE_CV = True
except Exception:  # pragma: no cover
    HAVE_CV = False


def _edge(points, *, closed=False, area=0.0, grad=80.0, length=None):
    length = length if length is not None else sum(
        math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return Edge(list(points), length, closed, area, grad, 1.0,
                (min(xs), min(ys), max(xs), max(ys)))


class GeometryTests(unittest.TestCase):
    def test_rdp_keeps_endpoints_and_drops_collinear(self):
        pts = [(0, 0), (1, 0), (2, 0), (3, 0), (3, 3)]
        out = rdp(pts, 0.5)
        self.assertEqual(out[0], (0.0, 0.0))
        self.assertEqual(out[-1], (3.0, 3.0))
        self.assertNotIn((1.0, 0.0), out)
        self.assertLess(len(out), len(pts))

    def test_rdp_keeps_a_real_corner(self):
        pts = [(0, 0), (2, 0), (4, 0), (4, 4)]
        out = rdp(pts, 0.4)
        self.assertIn((4.0, 0.0), out)

    def test_polyline_path_is_closed_and_has_cubics(self):
        path = polyline_to_path([(0, 0), (10, 0), (10, 10), (0, 10)], closed=True)
        self.assertTrue(path.startswith("M "))
        self.assertTrue(path.endswith("Z"))
        self.assertIn("C ", path)

    def test_corner_is_preserved_geometrically(self):
        # A right angle must survive the Catmull-Rom conversion: the control
        # point at the corner collapses onto the vertex.
        path = polyline_to_path([(0, 0), (20, 0), (20, 20)], closed=False)
        self.assertIn("C 20 0", path.replace(",", " "))


class EdgePolicyTests(unittest.TestCase):
    def setUp(self):
        self.segment = Segment(mask=None, x=0, y=0, w=600, h=800, coverage=0.4)

    def test_budgets_are_monotonic(self):
        self.assertEqual(BUDGETS["silhouette"]["form"], 0)
        self.assertEqual(BUDGETS["silhouette"]["detail"], 0)
        self.assertLessEqual(BUDGETS["form"]["form"], BUDGETS["catalogue"]["form"])
        self.assertLessEqual(BUDGETS["form"]["detail"], BUDGETS["catalogue"]["detail"])
        self.assertGreater(BUDGETS["full"]["detail"], BUDGETS["catalogue"]["detail"])

    def test_long_coherent_edge_becomes_form(self):
        edge = _edge([(0, 400), (100, 400), (200, 400), (300, 400)], grad=120)
        classify_edges([edge], self.segment, "form", width_mm=120)
        self.assertEqual(edge.role, "form")

    def test_wiggly_reflection_is_removed(self):
        # Zig-zag with the same endpoints but a long, non-smooth path.
        pts = [(0, 400)] + [(20 + i * 5, 400 + (12 if i % 2 else -12)) for i in range(20)]
        pts.append((300, 400))
        edge = _edge(pts, grad=120)
        classify_edges([edge], self.segment, "catalogue", width_mm=120)
        self.assertEqual(edge.role, "removed")
        self.assertIn("reflection", edge.reason)

    def test_tiny_control_is_removed_by_scale(self):
        # A 6 px circle at 120 mm is ~1.1 mm: below the 1.5 mm floor.
        pts = [(100 + 3 * math.cos(t / 6 * 2 * math.pi),
                100 + 3 * math.sin(t / 6 * 2 * math.pi)) for t in range(7)]
        edge = _edge(pts, closed=True, area=28, grad=300)
        classify_edges([edge], self.segment, "catalogue", width_mm=120)
        self.assertEqual(edge.role, "removed")

    def test_detail_budget_is_a_cap(self):
        edges = []
        for i in range(60):
            x = 10 + (i % 10) * 40
            y = 20 + (i // 10) * 40
            edges.append(_edge([(x, y), (x + 30, y + 2)], grad=200))
        classify_edges(edges, self.segment, "catalogue", width_mm=120)
        details = [e for e in edges if e.role == "detail"]
        self.assertLessEqual(len(details), BUDGETS["catalogue"]["detail"])
        self.assertTrue(details)

    def test_silhouette_budget_keeps_no_edges(self):
        edge = _edge([(0, 400), (300, 400)], grad=200)
        classify_edges([edge], self.segment, "silhouette", width_mm=120)
        self.assertEqual(edge.role, "removed")


@unittest.skipUnless(HAVE_CV, "OpenCV not installed")
class EndToEndTests(unittest.TestCase):
    def _photo(self, path: Path) -> None:
        image = np.full((420, 320, 3), 210, np.uint8)
        cv2.rectangle(image, (55, 55), (265, 355), (30, 150, 210), -1)   # body
        cv2.rectangle(image, (55, 300), (265, 355), (20, 20, 20), -1)    # base
        cv2.rectangle(image, (155, 90), (240, 175), (210, 210, 210), -1)  # panel
        cv2.circle(image, (120, 180), 22, (40, 40, 40), -1)              # group
        cv2.circle(image, (120, 180), 14, (180, 180, 180), -1)           # control
        cv2.line(image, (60, 240), (260, 240), (10, 10, 10), 3)          # seam
        cv2.rectangle(image, (70, 320), (110, 340), (230, 230, 230), -1)  # label
        cv2.imwrite(str(path), image)

    def test_build_writes_layered_svg_and_metrics(self):
        from scripts.photo_vector import build_illustration

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            photo = tmp / 'product.png'
            self._photo(photo)
            out = tmp / 'product.svg'
            result = build_illustration(photo, out, level='catalogue', colors=5,
                                        width_mm=120, source='synthetic', license='test')
            self.assertTrue(out.is_file())
            root = ET.parse(out).getroot()
            tags = [el.tag for el in root]
            self.assertTrue(any(tag.endswith('g') for tag in tags))
            ids = {el.get('id') for el in root.iter() if el.get('id')}
            self.assertIn('silhouette-fill', ids)
            self.assertIn('form', ids)
            self.assertIn('detail', ids)
            self.assertIn('colour', ids)
            self.assertGreater(result['stats']['form_paths'], 0)
            self.assertLessEqual(result['counts']['detail'], BUDGETS['catalogue']['detail'])
            self.assertGreater(result['fidelity']['grabcut_iou'], 0.5)
            self.assertGreater(result['edges']['long_edge_coverage'], 0.1)

    def test_silhouette_level_has_no_colour_layer(self):
        from scripts.photo_vector import build_illustration

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            photo = tmp / 'product.png'
            self._photo(photo)
            out = tmp / 'silhouette.svg'
            result = build_illustration(photo, out, level='silhouette', colors=4)
            ids = {el.get('id') for el in ET.parse(out).getroot().iter() if el.get('id')}
            self.assertNotIn('colour', ids)
            self.assertEqual(result['counts']['form'], 0)
            self.assertEqual(result['counts']['detail'], 0)

    def test_line_style_has_no_colour_group(self):
        from scripts.photo_vector import build_illustration

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            photo = tmp / 'product.png'
            self._photo(photo)
            out = tmp / 'line.svg'
            result = build_illustration(photo, out, level='catalogue', colors=4,
                                        style='line')
            ids = {el.get('id') for el in ET.parse(out).getroot().iter() if el.get('id')}
            self.assertNotIn('colour', ids)
            self.assertEqual(result['stats']['colour_paths'], 0)
            self.assertIsNone(result['fidelity']['colour_delta_e76'])
            self.assertGreater(result['counts']['form'], 0)

    def test_svg_parses_and_has_accessibility_text(self):
        from scripts.photo_vector import build_illustration

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            photo = tmp / 'product.png'
            self._photo(photo)
            out = tmp / 'product.svg'
            build_illustration(photo, out, level='form', colors=4,
                               title='Test machine', source='synthetic', license='test')
            text = out.read_text(encoding='utf-8')
            self.assertIn('<title>Test machine</title>', text)
            self.assertIn('<desc>', text)
            self.assertIn('license', text)
            ET.fromstring(text)


if __name__ == '__main__':
    unittest.main()
