#!/usr/bin/env python3
"""Photo → controlled vector illustration (T051, vector domain).

The problem is not "trace every edge".  A camera photo contains three kinds of
ink that a technical illustration must treat differently:

* **silhouette** — the outline of the object; always kept, simplified, heaviest;
* **form** — long boundaries between parts or planes; kept when long and
  coherent, drawn at a medium weight;
* **detail** — controls, seams, fasteners, reflections and texture; kept only
  inside a *detail budget*, drawn thin, otherwise removed.

The module implements that policy with measurable signals (contour length,
straightness, gradient support, closed-loop area) and a scale test: a detail
shorter than ~1.5 mm at the final print width is removed even if it is a real
edge, because the reader cannot see it.

Pipeline::

    photo → GrabCut mask → flat colour regions (k-means, merged)
          → Canny contours → classify silhouette/form/detail
          → RDP + corner-preserving Bézier → layered SVG

The output is a *first pass* plus a decision table, not an automatic
illustrator.  A human still chooses the level and corrects semantics.

CLI::

    python scripts/photo_vector.py build photo.jpg -o illustration.svg \
        --level catalogue --colors 5 --width-mm 120 --json metrics.json
    python scripts/photo_vector.py analyze photo.jpg --json edges.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

Point = tuple[float, float]

PAPER = "#F7F5F0"
INK = "#20242A"
LEVELS = ("silhouette", "form", "catalogue", "full")

# Budgets are deliberately explicit.  They are a design decision, not a
# property of the photo; the report records why each number was chosen.
BUDGETS = {
    "silhouette": {"form": 0, "detail": 0},
    "form": {"form": 30, "detail": 0},
    "catalogue": {"form": 34, "detail": 16},
    "full": {"form": 10_000, "detail": 10_000},
}


# ---------------------------------------------------------------------------
# Geometry (pure Python, unit-tested without OpenCV)
# ---------------------------------------------------------------------------

def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _point_line_distance(p: Point, a: Point, b: Point) -> float:
    if a == b:
        return _dist(p, a)
    x0, y0 = p
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    return abs(dx * (y1 - y0) - (x1 - x0) * dy) / math.hypot(dx, dy)


def rdp(points: Sequence[Point], epsilon: float) -> list[Point]:
    """Ramer–Douglas–Peucker simplification, iterative and deterministic."""
    pts = [(float(x), float(y)) for x, y in points]
    if len(pts) < 3 or epsilon <= 0:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        start, end = stack.pop()
        best = -1.0
        index = -1
        for i in range(start + 1, end):
            d = _point_line_distance(pts[i], pts[start], pts[end])
            if d > best:
                best, index = d, i
        if best > epsilon and index > 0:
            keep[index] = True
            stack.append((start, index))
            stack.append((index, end))
    return [p for p, k in zip(pts, keep) if k]


def _angle(a: Point, b: Point, c: Point) -> float:
    """Interior angle at *b* in degrees (180 = straight)."""
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    n1 = math.hypot(*v1)
    n2 = math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return 180.0
    cos = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
    return math.degrees(math.acos(cos))


def _fmt(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def polyline_to_path(points: Sequence[Point], *, closed: bool = False,
                     smooth: bool = True, corner_deg: float = 105.0) -> str:
    """Return an SVG path.

    Corners are preserved: at a sharp vertex both control points collapse onto
    the vertex, so the curve stops there instead of rounding the designer's
    intentional corner.  Elsewhere a Catmull–Rom → cubic conversion gives G1
    continuity without an extra fitting library.
    """
    pts = [(float(x), float(y)) for x, y in points]
    if not pts:
        return ""
    if len(pts) == 1:
        return f"M {_fmt(pts[0][0])} {_fmt(pts[0][1])}"
    if len(pts) == 2 or not smooth:
        d = [f"M {_fmt(pts[0][0])} {_fmt(pts[0][1])}"]
        d += [f"L {_fmt(x)} {_fmt(y)}" for x, y in pts[1:]]
        if closed:
            d.append("Z")
        return " ".join(d)

    n = len(pts)
    corners: set[int] = set()
    indices = range(n) if closed else range(1, n - 1)
    for i in indices:
        a = pts[(i - 1) % n] if closed else pts[i - 1]
        c = pts[(i + 1) % n] if closed else pts[i + 1]
        if _angle(a, pts[i], c) < corner_deg:
            corners.add(i)

    d = [f"M {_fmt(pts[0][0])} {_fmt(pts[0][1])}"]
    segments = n if closed else n - 1
    for i in range(segments):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p0 = pts[(i - 1) % n] if (closed or i > 0) else p1
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        if i in corners:
            c1 = p1
        else:
            c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        if (i + 1) % n in corners:
            c2 = p2
        else:
            c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(
            f"C {_fmt(c1[0])} {_fmt(c1[1])} {_fmt(c2[0])} {_fmt(c2[1])} "
            f"{_fmt(p2[0])} {_fmt(p2[1])}"
        )
    if closed:
        d.append("Z")
    return " ".join(d)


def _closed_area(points: Sequence[Point]) -> float:
    pts = list(points)
    if len(pts) < 3:
        return 0.0
    area = 0.0
    for i, (x1, y1) in enumerate(pts):
        x2, y2 = pts[(i + 1) % len(pts)]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def _bbox(points: Iterable[Point]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------------------
# Perception (OpenCV)
# ---------------------------------------------------------------------------

def _cv():
    try:
        import cv2  # noqa: PLC0415
        import numpy as np  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "OpenCV is required for photo_vector: pip install opencv-python-headless numpy"
        ) from exc
    # GrabCut and k-means use OpenCV's RNG.  Without a seed two builds of the
    # same photo choose different palettes and slightly different masks; the
    # five-budget study must be reproducible.
    cv2.setRNGSeed(0)
    cv2.setNumThreads(1)
    return cv2, np


@dataclass
class Segment:
    mask: Any
    x: int
    y: int
    w: int
    h: int
    coverage: float
    raw_mask: Any = None


def segment_product(bgr, *, iterations: int = 5, margin: float = 0.03) -> Segment:
    """GrabCut from a border rectangle, keep the largest component, fill holes."""
    cv2, np = _cv()
    h, w = bgr.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    rect = (int(w * margin), int(h * margin),
            int(w * (1 - 2 * margin)), int(h * (1 - 2 * margin)))
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(bgr, mask, rect, bgd, fgd, iterations, cv2.GC_INIT_WITH_RECT)
    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, kernel, iterations=2)
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel, iterations=1)
    contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("segmentation produced no object")
    main = max(contours, key=cv2.contourArea)
    solid = np.zeros_like(fg)
    cv2.drawContours(solid, [main], -1, 255, -1)
    raw = solid.copy()
    solid = _trim_ground_shadow(bgr, solid, cv2, np)
    contours, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    main = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(main)
    return Segment(solid, x, y, bw, bh, float(cv2.countNonZero(solid)) / (w * h),
                   raw_mask=raw)


def _trim_ground_shadow(bgr, mask, cv2, np):
    """Trim the shadow/reflection skirt below the darkest base line.

    Product photos on a table carry a soft shadow attached to the base.  GrabCut
    keeps it because it touches the object.  In a line illustration that skirt
    is not part of the machine: the silhouette stroke would wrap the shadow and
    read as a puddle.  For each column, the lowest *dark* pixel is the contact
    line; a narrow band below it is removed.  The rule only applies when dark
    pixels cover most columns and the removed area is small, so a light-bodied
    product is left alone.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w = mask.shape[:2]
    ys_all, xs_all = np.where(mask > 0)
    if len(ys_all) == 0:
        return mask
    y0, y1 = int(ys_all.min()), int(ys_all.max())
    scan_from = int(y0 + 0.80 * (y1 - y0))
    dark = (mask > 0) & (gray < 72)
    dark[:scan_from, :] = False
    columns = []
    for x in range(w):
        ys = np.where(dark[:, x])[0]
        columns.append(int(ys.max()) if len(ys) else None)
    known = [c for c in columns if c is not None]
    if len(known) < 0.55 * w:
        return mask
    # Fill gaps from the nearest known column.
    for x in range(w):
        if columns[x] is None:
            left = next((columns[i] for i in range(x, -1, -1) if columns[i] is not None), None)
            right = next((columns[i] for i in range(x, w) if columns[i] is not None), None)
            values = [v for v in (left, right) if v is not None]
            columns[x] = int(sum(values) / len(values)) if values else None
    out = mask.copy()
    removed = 0
    for x, limit in enumerate(columns):
        if limit is None:
            continue
        cut = limit + 3
        if cut < h:
            removed += int((out[cut:, x] > 0).sum())
            out[cut:, x] = 0
    if removed > 0.08 * cv2.countNonZero(mask):
        return mask
    kernel = np.ones((5, 5), np.uint8)
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel, iterations=1)
    return out


@dataclass
class Regions:
    labels: Any
    palette: list[str]
    palette_lab: list[tuple[float, float, float]]
    areas: list[int]


def _suppress_rim_highlights(labels, lab, mask, np, cv2, *, max_width: float = 18.0):
    """Merge thin bright rims into the dark body they sit on.

    A chrome object photographed on a table has a bright line along its lower
    silhouette.  Traced as a flat region, that line reads as a puddle under the
    machine.  A technical illustration keeps the silhouette stroke and the
    material fill, not the optical rim.  Only components that touch the
    silhouette, are thin (2·area/perimeter < 18 px) and are brighter than the
    adjacent body are merged; broad chrome faces are untouched.
    """
    boundary = cv2.subtract(mask, cv2.erode(mask, np.ones((13, 13), np.uint8)))
    ids = [int(i) for i in np.unique(labels) if i > 0]
    lum = {i: float(lab[labels == i, 0].mean()) for i in ids}
    for region in ids:
        if lum[region] < 150:
            continue
        count, components = cv2.connectedComponents((labels == region).astype(np.uint8))
        for component_id in range(1, count):
            component = components == component_id
            area = int(component.sum())
            if area < 48 or not np.any(component & (boundary > 0)):
                continue
            contours, _ = cv2.findContours(component.astype(np.uint8),
                                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            perimeter = sum(cv2.arcLength(c, True) for c in contours)
            width = 2.0 * area / perimeter if perimeter else 0.0
            if width >= max_width:
                continue
            ring = cv2.dilate(component.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            neighbours: dict[int, int] = {}
            for value in labels[ring & ~component]:
                value = int(value)
                if value > 0 and value != region and lum.get(value, 255) < 140:
                    neighbours[value] = neighbours.get(value, 0) + 1
            if neighbours:
                labels[component] = max(neighbours, key=neighbours.get)
    return labels


def _merge_small(labels, np, min_area: int, rounds: int = 3):
    """Absorb regions and small islands into their strongest neighbour.

    Two passes are needed for chrome: k-means first makes many thin bands, and
    a label can be large overall while a single connected island is tiny.  The
    component pass removes those islands before vectorisation, which is what
    keeps the SVG from turning into 300 wiggle paths.
    """
    labels = labels.copy()
    cv2, _ = _cv()
    for _ in range(rounds):
        ids, counts = np.unique(labels, return_counts=True)
        small = [int(i) for i, c in zip(ids, counts) if 0 < i and c < min_area]
        if not small:
            break
        for region in sorted(small, key=lambda r: int((labels == r).sum())):
            ys, xs = np.where(labels == region)
            if len(xs) == 0:
                continue
            neighbours: dict[int, int] = {}
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    yy = np.clip(ys + dy, 0, labels.shape[0] - 1)
                    xx = np.clip(xs + dx, 0, labels.shape[1] - 1)
                    for value in labels[yy, xx]:
                        value = int(value)
                        if value > 0 and value != region:
                            neighbours[value] = neighbours.get(value, 0) + 1
            if neighbours:
                labels[labels == region] = max(neighbours, key=neighbours.get)

    # Per-connected-component cleanup (the part region-only merging misses).
    for region in [int(i) for i in np.unique(labels) if i > 0]:
        component_count, component = cv2.connectedComponents(
            (labels == region).astype(np.uint8))
        for component_id in range(1, component_count):
            island = component == component_id
            if int(island.sum()) >= min_area:
                continue
            ys, xs = np.where(island)
            neighbours = {}
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    yy = np.clip(ys + dy, 0, labels.shape[0] - 1)
                    xx = np.clip(xs + dx, 0, labels.shape[1] - 1)
                    for value in labels[yy, xx]:
                        value = int(value)
                        if value > 0 and value != region:
                            neighbours[value] = neighbours.get(value, 0) + 1
            if neighbours:
                labels[island] = max(neighbours, key=neighbours.get)
    return labels


def quantize_regions(bgr, mask, *, colors: int = 5, min_ratio: float = 0.004,
                     chroma: float = 0.9) -> Regions:
    """Flat colour regions in Lab, small regions merged, palette slightly calmed."""
    cv2, np = _cv()
    # Smooth chrome micro-bands before clustering; otherwise every reflection
    # becomes its own colour island.
    smooth = cv2.bilateralFilter(bgr, 9, 45, 45)
    lab = cv2.cvtColor(smooth, cv2.COLOR_BGR2LAB)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        raise ValueError("empty mask")
    data = lab[ys, xs].astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
    _, labels_flat, centers = cv2.kmeans(
        data, colors, None, criteria, 4, cv2.KMEANS_PP_CENTERS)
    labels = np.zeros(mask.shape, np.int32)
    labels[ys, xs] = labels_flat.ravel() + 1
    # A 5x5 mode filter removes pixel-level salt before the component merge.
    # MedianBlur is safe here because the label count is tiny (~8).
    labels = cv2.medianBlur(labels.astype(np.uint8), 5).astype(np.int32)
    labels[mask == 0] = 0
    min_area = max(48, int(len(xs) * min_ratio))
    labels = _merge_small(labels, np, min_area)
    labels = _suppress_rim_highlights(labels, lab, mask, np, cv2)

    ids = [int(i) for i in np.unique(labels) if i > 0]
    palette: list[str] = []
    palette_lab: list[tuple[float, float, float]] = []
    areas: list[int] = []
    for region in ids:
        sel = labels == region
        mean_lab = lab[sel].mean(axis=0)
        l, a, b = (float(v) for v in mean_lab)
        # OpenCV 8-bit Lab stores L in 0..255, a/b offset by 128.
        a = 128.0 + (a - 128.0) * chroma
        b = 128.0 + (b - 128.0) * chroma
        l = max(16.0, min(245.0, l))
        palette_lab.append((l, a, b))
        bgr_mean = cv2.cvtColor(
            np.uint8([[[l, a, b]]]), cv2.COLOR_LAB2BGR)[0, 0]
        palette.append("#{:02X}{:02X}{:02X}".format(
            int(bgr_mean[2]), int(bgr_mean[1]), int(bgr_mean[0])))
        areas.append(int(sel.sum()))
    # Re-index 1..n and sort by area (large fills first).
    order = sorted(range(len(ids)), key=lambda i: areas[i], reverse=True)
    remap = {ids[old]: new + 1 for new, old in enumerate(order)}
    out = np.zeros_like(labels)
    for old, new in remap.items():
        out[labels == old] = new
    return Regions(out, [palette[i] for i in order],
                   [palette_lab[i] for i in order], [areas[i] for i in order])


@dataclass
class Edge:
    points: list[Point]
    length: float
    closed: bool
    area: float
    mean_grad: float
    straightness: float
    bbox: tuple[float, float, float, float]
    score: float = 0.0
    smoothness: float = 1.0
    wiggle: float = 0.0
    role: str = ""
    reason: str = ""
    simplified: list[Point] = field(default_factory=list)
    path: str = ""

    @property
    def diagonal(self) -> float:
        return math.hypot(self.bbox[2] - self.bbox[0], self.bbox[3] - self.bbox[1])


def _auto_canny(gray, mask, np, cv2) -> tuple[int, int]:
    values = gray[mask > 0]
    median = float(np.median(values)) if values.size else 128.0
    lower = int(max(12, 0.55 * median))
    upper = int(min(240, max(lower + 30, 1.45 * median)))
    return lower, upper


def _retraced_half(pts: list[Point]) -> list[Point] | None:
    """Return the forward half of a Canny contour that walks out and back.

    ``cv2.findContours`` traces a 1 px Canny ridge as a closed polygon: it goes
    from one end to the other and returns along the other side of the same
    ridge.  The endpoints look "closed", the enclosed area is ~0, and the path
    length is doubled.  Split at the farthest point and keep one half when the
    two halves nearly coincide; a true ring (opposite arcs far apart) is left
    closed.
    """
    n = len(pts)
    if n < 6:
        return None
    k = max(range(n), key=lambda i: _dist(pts[0], pts[i]))
    if k < 3 or n - k < 3:
        return None
    forward, backward = pts[:k + 1], pts[k:]
    fs = forward[:: max(1, len(forward) // 20)]
    bs = backward[:: max(1, len(backward) // 20)]
    if not fs or not bs:
        return None
    near = sum(min(_dist(p, q) for q in bs) for p in fs) / len(fs)
    balanced = abs(len(forward) - len(backward)) <= 0.40 * max(len(forward), len(backward))
    if near <= 5.0 and balanced:
        return forward if len(forward) >= len(backward) else list(reversed(backward))
    return None


def edge_candidates(bgr, mask, *, erode: int = 3) -> tuple[list[Edge], tuple[int, int]]:
    """Canny contours inside the object, with geometric and gradient features."""
    cv2, np = _cv()
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    smooth = cv2.bilateralFilter(gray, 7, 55, 55)
    gx = cv2.Scharr(smooth, cv2.CV_32F, 1, 0)
    gy = cv2.Scharr(smooth, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)
    lower, upper = _auto_canny(gray, mask, np, cv2)
    edges = cv2.Canny(smooth, lower, upper)
    inner = cv2.erode(mask, np.ones((erode * 2 + 1, erode * 2 + 1), np.uint8))
    edges = cv2.bitwise_and(edges, inner)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    h, w = gray.shape[:2]
    out: list[Edge] = []
    for contour in contours:
        pts = [(float(p[0][0]), float(p[0][1])) for p in contour]
        if len(pts) < 4:
            continue
        opened = _retraced_half(pts)
        if opened is not None:
            pts = opened
            closed = False
            length = _polyline_length(pts, closed=False)
            box = _bbox(pts)
            area = 0.0
            chord = _dist(pts[0], pts[-1])
            straightness = chord / length if length else 0.0
        else:
            length = _polyline_length(pts, closed=True)
            if length < 6.0:
                continue
            box = _bbox(pts)
            area = _closed_area(pts)
            closed = (_dist(pts[0], pts[-1]) <= 3.0 and length > 20
                      and min(box[2] - box[0], box[3] - box[1]) >= 4.0
                      and area >= 20.0)
            if not closed:
                area = 0.0
                length = _polyline_length(pts, closed=False)
            chord = _dist(pts[0], pts[-1])
            straightness = chord / length if length else 0.0
            if closed:
                straightness = min(1.0, 4.0 * math.pi * area / (length * length)) * 0.5
        if length < 6.0:
            continue
        sample = np.array([[int(round(x)), int(round(y))]
                           for x, y in pts[:: max(1, len(pts) // 24)]])
        sample[:, 0] = np.clip(sample[:, 0], 0, w - 1)
        sample[:, 1] = np.clip(sample[:, 1], 0, h - 1)
        mean_grad = float(mag[sample[:, 1], sample[:, 0]].mean())
        out.append(Edge(pts, length, closed, area, mean_grad, straightness, box))
    out = _dedupe_edges(out, (h, w), cv2, np)
    return out, (lower, upper)


def _dedupe_edges(edges: list[Edge], shape: tuple[int, int], cv2, np,
                  *, thickness: int = 3, coverage: float = 0.70) -> list[Edge]:
    """Drop Canny's second contour around the same ridge.

    Canny returns two nearly parallel contours for one edge (one on each side
    of the gradient ridge).  Traced literally, every real line becomes a
    double line and the "detail" budget fills with 20x2 px slivers.  Edges are
    visited longest-first; a candidate whose points are already >=70% covered
    by a kept stroke is the same edge and is dropped.  The kernel is small
    (3 px) so genuinely separate parallel features survive.
    """
    kept_mask = np.zeros(shape, np.uint8)
    kept: list[Edge] = []
    for edge in sorted(edges, key=lambda e: e.length, reverse=True):
        pts = edge.points
        step = max(1, len(pts) // 80)
        sample = pts[::step]
        hits = 0
        for x, y in sample:
            if kept_mask[int(round(y)), int(round(x))] > 0:
                hits += 1
        if sample and hits / len(sample) >= coverage:
            continue
        kept.append(edge)
        poly = np.array([[int(round(x)), int(round(y))] for x, y in pts], np.int32)
        cv2.polylines(kept_mask, [poly], False, 255, thickness)
    return kept


def _polyline_length(points: Sequence[Point], closed: bool = False) -> float:
    if len(points) < 2:
        return 0.0
    total = sum(_dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    if closed:
        total += _dist(points[-1], points[0])
    return total


def _wiggle(points: Sequence[Point], *, eps: float = 3.0,
            threshold: float = 12.0) -> float:
    """Excess turning per unit length after a 3 px simplification.

    A smooth part boundary turns gradually, so no vertex exceeds the 12° dead
    band.  A reflection or a scribble turns sharply many times; the excess is a
    stable signal that does not depend on how long the contour happens to be.
    """
    pts = rdp(points, eps)
    if len(pts) < 3:
        return 0.0
    excess = 0.0
    for i in range(1, len(pts) - 1):
        deviation = 180.0 - _angle(pts[i - 1], pts[i], pts[i + 1])
        if deviation > threshold:
            excess += deviation - threshold
    return excess / max(1.0, _polyline_length(pts))


def classify_edges(edges: list[Edge], segment: Segment, level: str,
                   *, width_mm: float = 120.0,
                   detail_max_strokes: int | None = None) -> list[Edge]:
    """Assign silhouette/form/detail/removed and a detail budget.

    Two measurements separate a structural edge from a reflection:

    * **smoothness** — arc length after RDP(2 px) divided by raw arc length.
      A long reflection wiggle loses 25–40% of its length under simplification;
      a part boundary keeps almost all of it.
    * **scale test** — at the final print width, a detail shorter than 1.5 mm
      cannot be read, so it is removed even when it is a real edge.

    Form is ranked by length × smoothness × contrast.  Detail is deliberately
    *not* the next-longest leftovers: it must be short, strong and either a
    closed control loop or a coherent short stroke.  This is what prevents
    "detail" from becoming a second pile of long reflection lines.
    """
    if level not in BUDGETS:
        raise ValueError(f"unknown level {level!r}; choose from {', '.join(LEVELS)}")
    diagonal = max(1.0, math.hypot(segment.w, segment.h))
    mm_per_px = width_mm / max(1.0, float(segment.w))
    min_detail_px = 1.5 / mm_per_px
    min_control_px = 3.0 / mm_per_px
    long_px = 0.055 * diagonal
    cap = BUDGETS[level]

    for edge in edges:
        simplified = rdp(edge.points, 2.0)
        simplified_length = _polyline_length(simplified, closed=edge.closed)
        edge.smoothness = min(1.0, simplified_length / max(1.0, edge.length))
        edge.wiggle = _wiggle(edge.points)
        length_norm = min(1.0, edge.length / (0.45 * diagonal))
        coherence = edge.smoothness
        if edge.closed:
            circularity = min(1.0, 4.0 * math.pi * edge.area / (edge.length ** 2))
            coherence = max(coherence, 0.45 + 0.55 * circularity)
        contrast = min(1.0, edge.mean_grad / 90.0)
        edge.score = ((length_norm ** 0.6) * (0.30 + 0.70 * coherence)
                      * (0.40 + 0.60 * contrast))

    scored = sorted(edges, key=lambda e: e.score, reverse=True)

    def bbox_diag(edge: Edge) -> float:
        return math.hypot(edge.bbox[2] - edge.bbox[0], edge.bbox[3] - edge.bbox[1])

    # 1. Form: long or a meaningful closed loop, and coherent after RDP.
    form_cap = int(cap["form"])
    for edge in scored:
        long = edge.length >= long_px
        loop = (edge.closed and 80.0 <= edge.area <= 0.06 * segment.w * segment.h
                and edge.length >= 18.0 and bbox_diag(edge) >= min_control_px)
        if not (long or loop):
            edge.role = "candidate"
            edge.reason = "short: below the form length floor"
            continue
        if edge.wiggle > 0.55 and not edge.closed:
            edge.role = "removed"
            edge.reason = "reflection: high turning rate"
            continue
        if form_cap <= 0:
            edge.role = "removed"
            edge.reason = "over the form budget"
            continue
        edge.role = "form"
        edge.reason = "closed loop" if loop else "long + coherent"
        form_cap -= 1

    # 2. Detail: short, strong, and either a *sized* closed control or a
    # coherent short stroke.  Canny makes a ~31 px ring around every dust dot;
    # scoring by circumference would fill the budget with those rings.  Score
    # closed controls by their bounding-box size instead.
    detail_cap = int(cap["detail"] if detail_max_strokes is None else detail_max_strokes)

    def detail_score(edge: Edge) -> float:
        size = bbox_diag(edge)
        size_factor = min(1.0, max(0.0, (size - 12.0) / 38.0))
        contrast = min(1.0, edge.mean_grad / 90.0)
        if edge.closed:
            shape = 0.40 + 0.60 * min(1.0, size / 55.0)
        else:
            shape = (0.50 * min(1.0, edge.length / 45.0)
                     + 0.30 * edge.smoothness + 0.20 * contrast)
        return 0.55 * shape + 0.45 * size_factor

    candidates = [e for e in scored if e.role == "candidate"]
    candidates.sort(key=detail_score, reverse=True)
    for edge in candidates:
        # The visible feature is the bbox for a loop and the length for an open
        # stroke; a 13 px ring is 2.4 mm at 120 mm and is not a control.
        feature_px = bbox_diag(edge) if edge.closed else edge.length
        visible = feature_px >= max(8.0, min_detail_px)
        strong = edge.mean_grad >= 26.0
        coherent = edge.closed or edge.smoothness >= 0.55
        if edge.closed and bbox_diag(edge) < max(8.0, min_control_px):
            edge.role = "removed"
            edge.reason = "below the 3 mm control floor"
            continue
        if edge.closed:
            perimeter = edge.length or 1.0
            circularity = min(1.0, 4.0 * math.pi * edge.area / (perimeter ** 2))
            if circularity < 0.28:
                edge.role = "removed"
                edge.reason = "decal/lettering: closed but not a control shape"
                continue
        if not visible:
            edge.role = "removed"
            edge.reason = "below the 1.5 mm scale floor"
            continue
        if not (strong and coherent):
            edge.role = "removed"
            edge.reason = "weak or broken: not a readable control"
            continue
        if detail_cap <= 0:
            edge.role = "removed"
            edge.reason = "over the detail budget"
            continue
        edge.role = "detail"
        edge.reason = "closed control loop" if edge.closed else "short structural detail"
        detail_cap -= 1

    return scored


def simplify_edges(edges: list[Edge], *, form_eps: float = 1.1,
                   detail_eps: float = 0.8) -> None:
    for edge in edges:
        if edge.role == "form":
            edge.simplified = rdp(edge.points, form_eps)
            edge.path = polyline_to_path(edge.simplified, closed=edge.closed,
                                         smooth=True, corner_deg=102)
        elif edge.role == "detail":
            edge.simplified = rdp(edge.points, detail_eps)
            edge.path = polyline_to_path(edge.simplified, closed=edge.closed,
                                         smooth=edge.closed,
                                         corner_deg=102 if edge.closed else 105)


def region_components(regions: Regions, *, eps: float = 1.2) -> list[tuple[float, str, str]]:
    """Return ``(component_area, colour, path)`` sorted large → small.

    Sorting by the *connected component* area, not the global label area, is
    what makes overpainting safe: a small island of a large label is still
    painted after a big island of a smaller label.  The dominant label (index
    1) is skipped because the silhouette fill already uses that colour.
    """
    cv2, np = _cv()
    out: list[tuple[float, str, str]] = []
    for index, colour in enumerate(regions.palette, start=1):
        if index == 1:
            continue
        mask = np.where(regions.labels == index, 255, 0).astype(np.uint8)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < 24:
                continue
            pts = [(float(p[0][0]), float(p[0][1])) for p in contour]
            simplified = rdp(pts, eps)
            if len(simplified) >= 3:
                d = polyline_to_path(simplified, closed=True, smooth=True,
                                     corner_deg=100)
                out.append((area, colour, d))
    out.sort(key=lambda item: item[0], reverse=True)
    return out


def silhouette_path(mask, *, eps: float = 1.2) -> tuple[str, list[Point]]:
    cv2, np = _cv()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("empty silhouette")
    contour = max(contours, key=cv2.contourArea)
    pts = [(float(p[0][0]), float(p[0][1])) for p in contour]
    simplified = rdp(pts, eps)
    return polyline_to_path(simplified, closed=True, smooth=True, corner_deg=100), simplified


# ---------------------------------------------------------------------------
# SVG assembly
# ---------------------------------------------------------------------------

def build_svg(*, width: int, height: int, mask, regions: Regions, edges: list[Edge],
              title: str, desc: str, metadata: dict, level: str,
              width_mm: float = 120.0, ground: bool = True,
              style: str = "colour") -> tuple[str, dict]:
    """Return (svg_text, stats).  Layers are ordered fill → colour → form → detail."""
    cv2, np = _cv()
    sil_d, sil_pts = silhouette_path(mask)
    object_h = max(1, int(_bbox(sil_pts)[3] - _bbox(sil_pts)[1]))
    # Line hierarchy: ratios of object height, then clamped so a small render
    # does not collapse to hairline soup.
    w_sil = max(2.2, min(5.0, object_h * 0.0048))
    w_form = max(1.25, min(2.6, object_h * 0.0026))
    w_detail = max(0.65, min(1.4, object_h * 0.00125))
    form = [e for e in edges if e.role == "form"]
    detail = [e for e in edges if e.role == "detail"]

    parts: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
        f"<title>{_escape(title)}</title>",
        f"<desc>{_escape(desc)}</desc>",
        "<metadata>" + _escape(json.dumps(metadata, ensure_ascii=False)) + "</metadata>",
        f'<rect id="paper" x="0" y="0" width="{width}" height="{height}" fill="{PAPER}"/>',
    ]
    if ground:
        x, y, bw, bh = _bbox(sil_pts)
        cy = y + bh + max(6.0, bh * 0.012)
        parts.append(
            f'<g id="ground" data-role="ground">'
            f'<ellipse cx="{_fmt((x + bw / 2))}" cy="{_fmt(cy)}" '
            f'rx="{_fmt(bw * 0.46)}" ry="{_fmt(max(4.0, bh * 0.012))}" '
            f'fill="#E6E2DA"/></g>'
        )
    if style == "colour":
        parts.append(
            f'<g id="silhouette-fill" data-role="silhouette-fill" fill="{regions.palette[0]}">'
            f'<path d="{sil_d}"/></g>'
        )
    else:
        # A line drawing keeps the paper as negative space; no flat fills.
        parts.append(
            f'<g id="silhouette-fill" data-role="silhouette-fill" fill="{PAPER}">'
            f'<path d="{sil_d}"/></g>'
        )
    colour_paths = 0
    colour_nodes = 0
    if level != "silhouette" and style == "colour":
        parts.append('<g id="colour" data-role="colour" stroke="none">')
        for _area, colour, d in region_components(regions):
            parts.append(f'<path d="{d}" fill="{colour}" fill-rule="evenodd" '
                         f'stroke="{colour}" stroke-width="0.45"/>')
            colour_paths += 1
            colour_nodes += d.count("C") + d.count("L") + 1
        parts.append("</g>")
    parts.append(
        f'<g id="form" data-role="form" fill="none" stroke="{INK}" '
        f'stroke-width="{_fmt(w_form)}" stroke-linecap="round" '
        f'stroke-linejoin="round">'
    )
    parts.append(f'<path d="{sil_d}" stroke-width="{_fmt(w_sil)}"/>')
    for edge in form:
        parts.append(f'<path d="{edge.path}"/>')
    parts.append("</g>")
    parts.append(
        f'<g id="detail" data-role="detail" fill="none" stroke="{INK}" '
        f'stroke-width="{_fmt(w_detail)}" stroke-linecap="round" '
        f'stroke-linejoin="round" opacity="0.92">'
    )
    for edge in detail:
        parts.append(f'<path d="{edge.path}"/>')
    parts.append("</g>")
    parts.append("</svg>")
    nodes = (len(sil_pts) + sum(len(e.simplified) for e in form)
             + sum(len(e.simplified) for e in detail) + colour_nodes)
    stats = {
        "level": level,
        "style": style,
        "form_paths": len(form),
        "detail_paths": len(detail),
        "colour_paths": colour_paths,
        "nodes": int(nodes),
        "stroke_length_px": round(sum(e.length for e in form + detail), 1),
        "stroke_weights_px": {"silhouette": round(w_sil, 2),
                              "form": round(w_form, 2),
                              "detail": round(w_detail, 2)},
        "smallest_detail_mm": round(
            min(((math.hypot(e.bbox[2] - e.bbox[0], e.bbox[3] - e.bbox[1])
                  if e.closed else e.length) for e in detail), default=0.0)
            * width_mm / max(1.0, float(_bbox(sil_pts)[2] - _bbox(sil_pts)[0])), 3),
        "viewBox": [0, 0, width, height],
    }
    return "\n".join(parts), stats


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def silhouette_iou(mask, sil_pts: Sequence[Point]) -> float:
    cv2, np = _cv()
    render = np.zeros_like(mask)
    poly = np.array([[int(round(x)), int(round(y))] for x, y in sil_pts], np.int32)
    cv2.fillPoly(render, [poly], 255)
    inter = float(cv2.countNonZero(cv2.bitwise_and(mask, render)))
    union = float(cv2.countNonZero(cv2.bitwise_or(mask, render)))
    return inter / union if union else 0.0


def colour_error(bgr, mask, regions: Regions) -> float:
    cv2, np = _cv()
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    pred = np.zeros_like(lab)
    for i, colour in enumerate(regions.palette, start=1):
        bgr_hex = colour.lstrip("#")
        r, g, b = (int(bgr_hex[i:i + 2], 16) for i in (0, 2, 4))
        pred[regions.labels == i] = cv2.cvtColor(
            np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2LAB)[0, 0]
    inner = cv2.erode(mask, np.ones((5, 5), np.uint8))
    sel = inner > 0
    if not sel.any():
        return 0.0
    diff = lab[sel] - pred[sel]
    # OpenCV 8-bit Lab: L in 0..255, a/b offset 128.  Scale to CIELAB units.
    dl = diff[:, 0] * (100.0 / 255.0)
    da = diff[:, 1]
    db = diff[:, 2]
    return float(np.sqrt(dl ** 2 + da ** 2 + db ** 2).mean())


def edge_metrics(bgr, mask, edges: list[Edge], sil_pts: Sequence[Point]) -> dict:
    cv2, np = _cv()
    h, w = mask.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    ref = cv2.Canny(gray, 30, 80)
    inner = cv2.erode(mask, np.ones((7, 7), np.uint8))
    ref = cv2.bitwise_and(ref, inner)
    kept = np.zeros((h, w), np.uint8)
    for edge in edges:
        if edge.role in {"form", "detail"}:
            points = edge.simplified or edge.points
            pts = np.array([[int(round(x)), int(round(y))] for x, y in points], np.int32)
            cv2.polylines(kept, [pts], False, 255, 1)

    def coverage(reference):
        ref_count = cv2.countNonZero(reference)
        if ref_count == 0:
            return 1.0
        near = cv2.dilate(kept, np.ones((5, 5), np.uint8))
        return float(cv2.countNonZero(cv2.bitwise_and(reference, near))) / ref_count

    # Long structural reference: Canny contours at least 55 px long.
    long_ref = np.zeros((h, w), np.uint8)
    contours, _ = cv2.findContours(ref, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        if cv2.arcLength(contour, False) >= 55:
            cv2.drawContours(long_ref, [contour], -1, 255, 1)
    kept_count = cv2.countNonZero(kept)
    ref_count = cv2.countNonZero(ref)
    return {
        "edge_coverage": round(coverage(ref), 3),
        "long_edge_coverage": round(coverage(long_ref), 3),
        "ink_ratio": round(kept_count / ref_count, 3) if ref_count else 0.0,
        "kept_pixels": int(kept_count),
        "reference_pixels": int(ref_count),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _load(path: str | Path):
    cv2, _ = _cv()
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"cannot read image: {path}")
    return image


def analyse_photo(photo: str | Path, *, colors: int = 5, max_side: int = 1200) -> dict:
    """Return the segmentation, palette, edge inventory and auto thresholds."""
    cv2, _ = _cv()
    bgr = _load(photo)
    h, w = bgr.shape[:2]
    if max(h, w) > max_side:
        scale = max_side / max(h, w)
        bgr = cv2.resize(bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    segment = segment_product(bgr)
    regions = quantize_regions(bgr, segment.mask, colors=colors)
    edges, (lo, hi) = edge_candidates(bgr, segment.mask)
    return {"bgr": bgr, "segment": segment, "regions": regions,
            "edges": edges, "canny": [lo, hi], "size": bgr.shape[:2]}


def build_illustration(photo: str | Path, out_svg: str | Path, *, level: str = "catalogue",
                       colors: int = 5, width_mm: float = 120.0, title: str = "",
                       source: str = "", license: str = "", ground: bool = True,
                       style: str = "colour", max_side: int = 1200) -> dict:
    """Build one SVG and return measured fidelity/complexity."""
    cv2, _ = _cv()
    data = analyse_photo(photo, colors=colors, max_side=max_side)
    bgr, segment, regions = data["bgr"], data["segment"], data["regions"]
    edges = classify_edges(data["edges"], segment, level, width_mm=width_mm)
    simplify_edges(edges)
    height, width = bgr.shape[:2]
    name = title or Path(photo).stem.replace("-", " ").replace("_", " ").title()
    metadata = {
        "generator": "photo_vector.py (T051)",
        "level": level,
        "style": style,
        "source": source or str(photo),
        "license": license,
        "colour_regions": len(regions.palette),
        "canny": data["canny"],
        "policy": "silhouette always; form by length/coherence; detail by budget and 1.5 mm scale test",
    }
    svg, stats = build_svg(
        width=width, height=height, mask=segment.mask, regions=regions, edges=edges,
        title=name, desc=(
            f"Vector illustration at '{level}' detail budget: "
            f"{stats_count(edges, 'form')} form strokes, "
            f"{stats_count(edges, 'detail')} detail strokes, "
            + (f"{len(regions.palette)} flat colour regions."
               if style == "colour" else "line style, no fills.")
        ),
        metadata=metadata, level=level, width_mm=width_mm, ground=ground, style=style)
    out_svg = Path(out_svg)
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text(svg, encoding="utf-8")
    result = {
        "svg": str(out_svg),
        "level": level,
        "style": style,
        "size_px": [width, height],
        "bbox": [segment.x, segment.y, segment.w, segment.h],
        "palette": regions.palette,
        "canny": data["canny"],
        "counts": {
            "form": stats_count(edges, "form"),
            "detail": stats_count(edges, "detail"),
            "removed": stats_count(edges, "removed"),
            "total_candidates": len(edges),
        },
        "reasons": _reason_counts(edges),
        "stats": stats,
        "fidelity": {
            # Agreement between the raw GrabCut mask and the delivered mask.
            # It is not ground truth: the difference is the trimmed shadow.
            "grabcut_iou": round(silhouette_iou(
                segment.raw_mask, _silhouette_points(segment.mask)), 4) if segment.raw_mask is not None else None,
            "colour_delta_e76": (round(colour_error(bgr, segment.mask, regions), 2)
                                 if style == "colour" and level != "silhouette" else None),
        },
        "edges": edge_metrics(bgr, segment.mask, edges, _silhouette_points(segment.mask)),
    }
    return result


def stats_count(edges: list[Edge], role: str) -> int:
    return sum(1 for e in edges if e.role == role)


def _reason_counts(edges: list[Edge]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for edge in edges:
        key = f"{edge.role}: {edge.reason or 'unspecified'}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _silhouette_points(mask) -> list[Point]:
    cv2, _ = _cv()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = max(contours, key=cv2.contourArea)
    pts = [(float(p[0][0]), float(p[0][1])) for p in contour]
    return rdp(pts, 1.2)


def main() -> None:
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build", help="Build one layered SVG")
    p.add_argument("photo", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    p.add_argument("--level", choices=LEVELS, default="catalogue")
    p.add_argument("--colors", type=int, default=5)
    p.add_argument("--width-mm", type=float, default=120.0)
    p.add_argument("--style", choices=("colour", "line"), default="colour")
    p.add_argument("--title", default="")
    p.add_argument("--source", default="")
    p.add_argument("--license", default="")
    p.add_argument("--no-ground", action="store_true")
    p.add_argument("--json", type=Path, default=None)
    p = sub.add_parser("analyze", help="Edge inventory without writing SVG")
    p.add_argument("photo", type=Path)
    p.add_argument("--colors", type=int, default=5)
    p.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()
    if args.cmd == "build":
        result = build_illustration(
            args.photo, args.output, level=args.level, colors=args.colors,
            width_mm=args.width_mm, title=args.title, source=args.source,
            license=args.license, ground=not args.no_ground, style=args.style)
    else:
        data = analyse_photo(args.photo, colors=args.colors)
        result = {
            "size_px": list(data["size"]),
            "bbox": [data["segment"].x, data["segment"].y,
                     data["segment"].w, data["segment"].h],
            "canny": data["canny"],
            "palette": data["regions"].palette,
            "edges": [{"length": round(e.length, 1), "closed": e.closed,
                       "area": round(e.area, 1), "grad": round(e.mean_grad, 1),
                       "straightness": round(e.straightness, 3)}
                      for e in sorted(data["edges"], key=lambda e: e.length, reverse=True)],
        }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
