#!/usr/bin/env python3
"""Semantic 2.5D vector reconstruction (T053, vector domain).

T051 traced Canny edges.  That is not a reconstruction: it reproduces the
camera's noise, not the object.  This module is the missing layer.

The scene is described in **object coordinates** (x = width, y = height,
z = depth).  A fixed axonometric projection maps it to the page.  Parts are
boxes, cylinders, plates and controls; the photo supplies proportions and
colours, never line work.  Faces are painted front/side/top with a lighting
convention, and only the visible outlines are stroked.

CLI::

    python scripts/vector_reconstruct.py demo -o demo.svg
    python scripts/vector_reconstruct.py inspect scene.svg

The Quick Mill scene lives in the experiment inputs; this module is the
reusable primitive/scene layer.
"""
from __future__ import annotations

import argparse
import json
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

Point2 = tuple[float, float]
Point3 = tuple[float, float, float]

INK = "#1C1F23"
PAPER = "#F7F4EC"


def _n(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _pts(points: Iterable[Point2]) -> str:
    return " ".join(f"{_n(x)},{_n(y)}" for x, y in points)


@dataclass(frozen=True)
class Projection:
    """Axonometric projection: x right, y up, z back-left-up."""

    ox: float
    oy: float
    sx: float
    sy: float
    dx: float
    dy: float

    def p(self, x: float, y: float, z: float) -> Point2:
        return (self.ox + x * self.sx + z * self.dx,
                self.oy - y * self.sy + z * self.dy)

    def poly(self, points: Sequence[Point3]) -> list[Point2]:
        return [self.p(*point) for point in points]


def rounded_rect_points(x0: float, y0: float, x1: float, y1: float,
                        radius: float, steps: int = 6) -> list[Point2]:
    """Rounded rectangle in a local 2-D plane (y up)."""
    r = max(0.0, min(radius, (x1 - x0) / 2.0, (y1 - y0) / 2.0))
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out: list[Point2] = []
    corners = [
        (x1 - r, y0 + r, -90, 0),   # bottom-right
        (x1 - r, y1 - r, 0, 90),    # top-right
        (x0 + r, y1 - r, 90, 180),  # top-left
        (x0 + r, y0 + r, 180, 270), # bottom-left
    ]
    for cx, cy, a0, a1 in corners:
        for i in range(steps + 1):
            angle = math.radians(a0 + (a1 - a0) * i / steps)
            out.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return out


def circle_points(cx: float, cy: float, r: float, steps: int = 48) -> list[Point2]:
    return [(cx + r * math.cos(2 * math.pi * i / steps),
             cy + r * math.sin(2 * math.pi * i / steps)) for i in range(steps)]


def convex_hull(points: Sequence[Point2]) -> list[Point2]:
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in points))
    if len(pts) <= 2:
        return list(pts)
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


@dataclass
class Scene:
    projection: Projection
    width: int = 1200
    height: int = 1200
    defs: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)

    # -- primitives ------------------------------------------------------
    def gradient(self, name: str, stops: Sequence[tuple[float, str]],
                 x1: float = 0, y1: float = 0, x2: float = 0, y2: float = 1) -> str:
        parts = [f'<linearGradient id="{name}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">']
        for offset, colour in stops:
            parts.append(f'<stop offset="{_n(offset)}" stop-color="{colour}"/>')
        parts.append("</linearGradient>")
        self.defs.append("".join(parts))
        return f"url(#{name})"

    def path(self, d: str, fill: str = "none", stroke: str | None = INK,
             sw: float = 2.0, opacity: float | None = None,
             extra: str = "") -> str:
        attrs = [f'd="{d}"', f'fill="{fill}"']
        if stroke:
            attrs += [f'stroke="{stroke}"', f'stroke-width="{_n(sw or 0)}"',
                      'stroke-linejoin="round"', 'stroke-linecap="round"']
        if opacity is not None:
            attrs.append(f'opacity="{_n(opacity)}"')
        if extra:
            attrs.append(extra)
        return f"<path {' '.join(attrs)}/>"

    def face(self, points: Sequence[Point3], fill: str, stroke: str | None = INK,
             sw: float = 2.0, opacity: float | None = None) -> str:
        screen = self.projection.poly(points)
        d = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in screen) + " Z"
        return self.path(d, fill=fill, stroke=stroke, sw=sw, opacity=opacity)

    # -- box: left side, top, front -------------------------------------
    def box(self, x0: float, y0: float, z0: float, x1: float, y1: float, z1: float,
            *, front: str, side: str, top: str, stroke: str | None = INK,
            sw: float = 2.0, opacity: float | None = None) -> list[str]:
        out = [
            self.face([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)],
                      fill=side, stroke=stroke, sw=sw, opacity=opacity),
            self.face([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
                      fill=top, stroke=stroke, sw=sw, opacity=opacity),
            self.face([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
                      fill=front, stroke=stroke, sw=sw, opacity=opacity),
        ]
        return out

    def add_box(self, *args, **kwargs) -> None:
        self.body.extend(self.box(*args, **kwargs))

    # -- front-plane rounded rect ---------------------------------------
    def front_rounded(self, x0: float, y0: float, x1: float, y1: float, radius: float,
                      z: float, fill: str, stroke: str | None = INK, sw: float = 1.6,
                      opacity: float | None = None) -> str:
        local = rounded_rect_points(x0, y0, x1, y1, radius)
        screen = [self.projection.p(x, y, z) for x, y in local]
        d = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in screen) + " Z"
        return self.path(d, fill=fill, stroke=stroke, sw=sw, opacity=opacity)

    def front_ellipse(self, cx: float, cy: float, rx: float, ry: float, z: float,
                      fill: str, stroke: str | None = INK, sw: float = 1.6,
                      opacity: float | None = None) -> str:
        local = circle_points(cx, cy, 1.0, 64)
        screen = [self.projection.p(cx + (x - cx) * rx, cy + (y - cy) * ry, z)
                  for x, y in local]
        d = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in screen) + " Z"
        return self.path(d, fill=fill, stroke=stroke, sw=sw, opacity=opacity)

    def front_circle(self, cx: float, cy: float, r: float, z: float,
                     fill: str, stroke: str | None = INK, sw: float = 1.6,
                     opacity: float | None = None) -> str:
        # Compensate the vertical stretch so the screen ellipse is a circle.
        ry = r * self.projection.sx / self.projection.sy
        return self.front_ellipse(cx, cy, r, ry, z, fill=fill, stroke=stroke,
                                  sw=sw, opacity=opacity)

    def disc_y(self, cx: float, cz: float, rx: float, rz: float, y: float,
               fill: str, opacity: float | None = None) -> str:
        """A filled ellipse on a horizontal plane, projected."""
        local = circle_points(0, 0, 1.0, 64)
        screen = [self.projection.p(cx + x * rx, y, cz + z * rz)
                  for x, z in local]
        d = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in screen) + " Z"
        return self.path(d, fill=fill, stroke=None, sw=0, opacity=opacity)

    # -- vertical cylinder (knobs, feet) --------------------------------
    def cylinder_y(self, cx: float, cz: float, r: float, y0: float, y1: float,
                   *, side: str, top: str, stroke: str | None = INK,
                   sw: float = 1.6) -> list[str]:
        bottom_pts = [self.projection.p(cx + dx, y0, cz + dz)
                      for dx, dz in circle_points(0, 0, r, 40)]
        top_pts = [self.projection.p(cx + dx, y1, cz + dz)
                   for dx, dz in circle_points(0, 0, r, 40)]
        hull = convex_hull(bottom_pts + top_pts)
        d_side = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in hull) + " Z"
        d_top = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in top_pts) + " Z"
        return [self.path(d_side, fill=side, stroke=stroke, sw=sw),
                self.path(d_top, fill=top, stroke=stroke, sw=sw)]

    # -- horizontal cylinder along z (portafilter) ----------------------
    def cylinder_z(self, cx: float, cy: float, z0: float, z1: float,
                   r0: float, r1: float, *, side: str, cap: str,
                   stroke: str | None = INK, sw: float = 1.6) -> list[str]:
        ky = self.projection.sx / self.projection.sy
        a = [self.projection.p(cx + dx, cy + dy * ky, z0)
             for dx, dy in circle_points(0, 0, r0, 40)]
        b = [self.projection.p(cx + dx, cy + dy * ky, z1)
             for dx, dy in circle_points(0, 0, r1, 40)]
        hull = convex_hull(a + b)
        d_side = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in hull) + " Z"
        d_cap = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in b) + " Z"
        return [self.path(d_side, fill=side, stroke=stroke, sw=sw),
                self.path(d_cap, fill=cap, stroke=stroke, sw=sw)]

    # -- screen-space tube (steam wand) ---------------------------------
    def tube(self, points: Sequence[tuple[float, float, float]], width: float,
             colour: str, *, highlight: str | None = None,
             stroke: str = INK, sw: float = 1.2) -> list[str]:
        screen = [self.projection.p(*p) for p in points]
        d = "M " + " L ".join(f"{_n(x)} {_n(y)}" for x, y in screen)
        out = [f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{_n(width + sw)}" '
               'stroke-linecap="round" stroke-linejoin="round"/>',
               f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{_n(width)}" '
               'stroke-linecap="round" stroke-linejoin="round"/>']
        if highlight:
            out.append(f'<path d="{d}" fill="none" stroke="{highlight}" '
                       f'stroke-width="{_n(max(1.0, width * 0.28))}" '
                       'stroke-linecap="round" opacity="0.75" '
                       f'transform="translate(-1.2 -1.2)"/>')
        return out

    def text_front(self, cx: float, cy: float, z: float, text: str, size: float,
                   fill: str, *, weight: str = "700", anchor: str = "middle",
                   family: str = "Arial, Helvetica, sans-serif",
                   letter_spacing: float = 0.0) -> str:
        x, y = self.projection.p(cx, cy, z)
        return (f'<text x="{_n(x)}" y="{_n(y)}" text-anchor="{anchor}" '
                f'dominant-baseline="middle" font-family="{family}" '
                f'font-size="{_n(size * self.projection.sx)}" font-weight="{weight}" '
                f'letter-spacing="{_n(letter_spacing * self.projection.sx)}" '
                f'fill="{fill}">{_escape(text)}</text>')

    # -- document -------------------------------------------------------
    def svg(self, *, title: str, desc: str, metadata: dict) -> str:
        head = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{self.height}" viewBox="0 0 {self.width} {self.height}" role="img">',
            f"<title>{_escape(title)}</title>",
            f"<desc>{_escape(desc)}</desc>",
            "<metadata>" + _escape(json.dumps(metadata, ensure_ascii=False)) + "</metadata>",
            "<defs>" + "".join(self.defs) + "</defs>",
            f'<rect id="paper" x="0" y="0" width="{self.width}" height="{self.height}" fill="{PAPER}"/>',
        ]
        return "\n".join(head + self.body + ["</svg>"])


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def inspect_svg(path: str | Path) -> dict:
    root = ET.parse(path).getroot()
    groups = [el.get("id") for el in root.iter() if el.tag.endswith("g") and el.get("id")]
    paths = sum(1 for el in root.iter() if el.tag.endswith("path"))
    texts = sum(1 for el in root.iter() if el.tag.endswith("text"))
    return {"ok": True, "viewBox": root.get("viewBox"), "groups": groups,
            "paths": paths, "texts": texts}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspect")
    p.add_argument("svg", type=Path)
    p = sub.add_parser("demo", help="Write a small primitive demo SVG")
    p.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "demo":
        scene = Scene(Projection(120, 260, 4.0, 4.0, -1.4, -1.0), width=420, height=300)
        scene.gradient("demo", [(0, "#EDE4CF"), (1, "#B9B5A8")])
        scene.body.extend(scene.box(10, 0, 0, 50, 40, 30, front="url(#demo)",
                                    side="#8F8C82", top="#F2EFE6"))
        scene.body.extend(scene.cylinder_y(30, 15, 7, 40, 52, side="#C8921C",
                                           top="#F0C24A"))
        scene.body.append(scene.front_circle(30, 20, 8, -0.1, "#EDE4CF"))
        scene.body.append(scene.text_front(30, 20, -0.2, "DEMO", 4, "#B43A2E"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(scene.svg(title="Demo", desc="Primitive demo",
                                         metadata={"source": "generated"}),
                               encoding="utf-8")
        print(args.output)
        return
    print(json.dumps(inspect_svg(args.svg), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
