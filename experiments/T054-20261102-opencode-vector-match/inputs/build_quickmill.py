"""T054 semantic 2.5D reconstruction of the Quick Mill Omre.

The T053 scene was a boxy first pass.  This build is driven by the photo/vector
comparison: the photo's body is 0.80 as wide as it is tall, the group-head centre
is at 0.275 of the body height, the tray top at 0.520, the lower panel at 0.618,
and the base top at 0.843.  The projection and Dimensions below encode those
fractions.  The top panel is chrome, the badge is an oval, the group head is a
chrome block with a vertical basket and an angled black handle, and the tray is a
deep box rather than a shelf.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.vector_reconstruct import Projection, Scene  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"


@dataclass(frozen=True)
class Dimensions:
    x0: float = 10.0
    width: float = 80.0
    z0: float = 0.0
    depth: float = 60.0
    base_h: float = 18.5
    lower_h: float = 26.6
    tray_h: float = 11.5
    tower_h: float = 55.6
    top_h: float = 5.8
    black_band_h: float = 19.7
    tray_front: float = -8.0
    tray_depth: float = 42.0
    group_r: float = 9.5
    portafilter_r: float = 7.5
    group_center_frac: float = 0.806

    @property
    def x1(self) -> float:
        return self.x0 + self.width

    @property
    def z1(self) -> float:
        return self.z0 + self.depth

    @property
    def lower_top(self) -> float:
        return self.base_h + self.lower_h

    @property
    def tray_top(self) -> float:
        return self.lower_top + self.tray_h

    @property
    def tower_top(self) -> float:
        return self.tray_top + self.tower_h

    @property
    def top_top(self) -> float:
        return self.tower_top + self.top_h

    @property
    def black_bottom(self) -> float:
        return self.tower_top - self.black_band_h

    @property
    def cx(self) -> float:
        return self.x0 + self.width / 2.0

    @property
    def group_y(self) -> float:
        return self.tray_top + (self.black_bottom - self.tray_top) * self.group_center_frac


def group(scene: Scene, name: str, items: list[str]) -> None:
    scene.body.append(f'<g id="{name}">')
    scene.body.extend(items)
    scene.body.append("</g>")


def side_dot(scene: Scene, x: float, y: float, z: float, r: float,
             fill: str, stroke: str | None = None, sw: float = 0.0,
             opacity: float | None = None) -> str:
    points = [scene.projection.p(x, y + r * math.cos(2 * math.pi * i / 32),
                                z + r * math.sin(2 * math.pi * i / 32))
              for i in range(32)]
    d = "M " + " L ".join(f"{px:.2f} {py:.2f}" for px, py in points) + " Z"
    return scene.path(d, fill=fill, stroke=stroke, sw=sw, opacity=opacity)


def build(dims: Dimensions | None = None) -> str:
    d = dims or Dimensions()
    view = Projection(ox=223, oy=940, sx=7.0, sy=6.95, dx=-2.42, dy=-0.9)
    s = Scene(view, width=1000, height=1000)

    chrome_front = s.gradient("chromeFront", [(0, "#F0EDE3"), (0.42, "#D2CFC4"), (1, "#A6A39A")])
    chrome_side = s.gradient("chromeSide", [(0, "#C9C6BC"), (1, "#8C8A82")])
    chrome_top = s.gradient("chromeTop", [(0, "#FCFAF2"), (1, "#D8D6CD")])
    chrome_edge = s.gradient("chromeEdge", [(0, "#B8B5AC"), (1, "#7E7C74")])
    yellow_side = s.gradient("yellowSide", [(0, "#E8B72D"), (1, "#B47B12")])
    yellow_top = s.gradient("yellowTop", [(0, "#F8D15A"), (1, "#D8A122")])
    black_front = s.gradient("blackFront", [(0, "#303337"), (1, "#191B1E")])
    black_side = s.gradient("blackSide", [(0, "#222528"), (1, "#0F1113")])
    black_top = s.gradient("blackTop", [(0, "#3D4045"), (1, "#25282C")])
    cream = "#EDE4CF"
    red = "#B43A2E"

    # Floor shadow, in object coordinates.
    group(s, "shadow", [s.disc_y(d.cx, d.z0 + d.depth / 2, d.width * 0.60,
                                 d.depth * 0.34, -0.1, "#E7E1D4", opacity=0.85)])

    # Feet: dark rear, brass front.
    feet = []
    for x, z in ((d.x0 + 12, d.z1 - 12), (d.x1 - 12, d.z1 - 12)):
        feet.extend(s.cylinder_y(x, z, 3.0, -4, 0, side="#2A2C2E", top="#4A4C4E", sw=1.1))
    for x, z in ((d.x0 + 12, d.z0 + 12), (d.x1 - 12, d.z0 + 12)):
        feet.extend(s.cylinder_y(x, z, 3.0, -4, 0, side="#A67C1A", top="#D0A63C", sw=1.1))
    group(s, "feet", feet)

    # Base plinth, with a chrome lip on the front and the left side.
    base = s.box(d.x0 - 2, 0, d.z0 - 2, d.x1 + 2, d.base_h, d.z1 + 2,
                 front=black_front, side=black_side, top=black_top, sw=2.2)
    base.append(s.face([(d.x0 - 2, d.base_h - 1.4, d.z0 - 2.05),
                        (d.x1 + 2, d.base_h - 1.4, d.z0 - 2.05),
                        (d.x1 + 2, d.base_h - 0.2, d.z0 - 2.05),
                        (d.x0 - 2, d.base_h - 0.2, d.z0 - 2.05)],
                       fill=chrome_side, stroke=None, sw=0))
    base.append(s.face([(d.x0 - 2.05, d.base_h - 1.4, d.z0 - 2),
                        (d.x0 - 2.05, d.base_h - 1.4, d.z1 + 2),
                        (d.x0 - 2.05, d.base_h - 0.2, d.z1 + 2),
                        (d.x0 - 2.05, d.base_h - 0.2, d.z0 - 2)],
                       fill=chrome_side, stroke=None, sw=0))
    group(s, "base", base)

    # Lower body: chrome front, yellow side, dark top under the tray.
    lower = s.box(d.x0, d.base_h, d.z0, d.x1, d.lower_top, d.z1,
                  front=chrome_front, side=yellow_side, top="#5A5A55", sw=2.0)
    group(s, "lower-body", lower)

    # Tower front: chrome below the black band; the side is one yellow sheet.
    tower = [
        s.face([(d.x0, d.tray_top, d.z0), (d.x1, d.tray_top, d.z0),
                (d.x1, d.black_bottom, d.z0), (d.x0, d.black_bottom, d.z0)],
               fill=chrome_front, sw=2.0),
        s.face([(d.x0, d.black_bottom, d.z0), (d.x1, d.black_bottom, d.z0),
                (d.x1, d.tower_top, d.z0), (d.x0, d.tower_top, d.z0)],
               fill=black_front, sw=2.0),
        s.face([(d.x0, d.tower_top, d.z0), (d.x1, d.tower_top, d.z0),
                (d.x1, d.tower_top, d.z1), (d.x0, d.tower_top, d.z1)],
               fill="#2A2D31", sw=2.0),
        s.face([(d.x0, d.black_bottom - 0.5, d.z0 - 0.1),
                (d.x1, d.black_bottom - 0.5, d.z0 - 0.1),
                (d.x1, d.black_bottom + 0.2, d.z0 - 0.1),
                (d.x0, d.black_bottom + 0.2, d.z0 - 0.1)],
               fill=chrome_side, stroke=None, sw=0),
    ]
    group(s, "tower", tower)

    # Chrome top panel overhangs the black band; the top is not black.
    top = s.box(d.x0 - 0.3, d.tower_top, d.z0 - 0.8, d.x1 + 0.3, d.top_top, d.z1,
                front=chrome_front, side=chrome_edge, top=chrome_top, sw=2.0)
    top.append(s.face([(d.x0 - 0.3, d.tower_top, d.z0 - 0.85),
                       (d.x1 + 0.3, d.tower_top, d.z0 - 0.85),
                       (d.x1 + 0.3, d.tower_top + 0.7, d.z0 - 0.85),
                       (d.x0 - 0.3, d.tower_top + 0.7, d.z0 - 0.85)],
                      fill=black_side, stroke=None, sw=0))
    group(s, "top-panel", top)

    # A shallow cup-warmer recess and one rear rail, not four heavy bars.
    top_detail = [s.face([(d.x0 + 6, d.top_top + 0.04, d.z0 + 8),
                          (d.x1 - 6, d.top_top + 0.04, d.z0 + 8),
                          (d.x1 - 6, d.top_top + 0.04, d.z1 - 11),
                          (d.x0 + 6, d.top_top + 0.04, d.z1 - 11)],
                         fill="none", stroke=chrome_side, sw=1.0)]
    top_detail.extend(s.box(d.x0 + 8, d.top_top, d.z1 - 12, d.x1 - 8,
                            d.top_top + 1.4, d.z1 - 10,
                            front=chrome_front, side=chrome_side, top=chrome_top, sw=0.9))
    group(s, "top-detail", top_detail)

    # Drip tray: a deep black box with a fine grid and a chrome front lip.
    tray = s.box(d.x0, d.lower_top, d.tray_front, d.x1, d.tray_top,
                 d.tray_front + d.tray_depth,
                 front=black_front, side=black_side, top="#15171A", sw=1.8)
    grid = []
    for i in range(12):
        z = d.tray_front + 2 + i * 3.2
        grid.append(s.face([(d.x0 + 3, d.tray_top + 0.2, z),
                            (d.x1 - 3, d.tray_top + 0.2, z),
                            (d.x1 - 3, d.tray_top + 0.2, z + 1.2),
                            (d.x0 + 3, d.tray_top + 0.2, z + 1.2)],
                           fill="#34383D", stroke=None, sw=0))
    for x in range(int(d.x0 + 6), int(d.x1 - 4), 6):
        grid.append(s.face([(x, d.tray_top + 0.25, d.tray_front + 1),
                            (x + 1.1, d.tray_top + 0.25, d.tray_front + 1),
                            (x + 1.1, d.tray_top + 0.25, d.tray_front + d.tray_depth - 4),
                            (x, d.tray_top + 0.25, d.tray_front + d.tray_depth - 4)],
                           fill="#34383D", stroke=None, sw=0))
    tray += grid
    tray.append(s.face([(d.x0, d.lower_top + 0.3, d.tray_front - 0.1),
                        (d.x1, d.lower_top + 0.3, d.tray_front - 0.1),
                        (d.x1, d.lower_top + 2.6, d.tray_front - 0.1),
                        (d.x0, d.lower_top + 2.6, d.tray_front - 0.1)],
                       fill=chrome_front, sw=1.2))
    tray.append(s.face([(d.x0, d.tray_top - 0.8, d.tray_front - 0.12),
                        (d.x1, d.tray_top - 0.8, d.tray_front - 0.12),
                        (d.x1, d.tray_top, d.tray_front - 0.12),
                        (d.x0, d.tray_top, d.tray_front - 0.12)],
                       fill=chrome_side, stroke=None, sw=0))
    group(s, "drip-tray", tray)

    # One yellow side sheet from base to top, with two screw holes and a joint.
    side = s.face([(d.x0, d.base_h, d.z0), (d.x0, d.base_h, d.z1),
                   (d.x0, d.tower_top, d.z1), (d.x0, d.tower_top, d.z0)],
                  fill=yellow_side, sw=2.0)
    seam = side_dot(s, d.x0 - 0.03, d.lower_top, d.z0 + 24, 0.55, "#8A6410", opacity=0.55)
    screws = [
        side_dot(s, d.x0 - 0.04, 108.0, d.z0 + 22, 1.15, "#7A5A0E"),
        side_dot(s, d.x0 - 0.04, 33.0, d.z0 + 22, 1.15, "#7A5A0E"),
        side_dot(s, d.x0 - 0.05, 108.4, d.z0 + 21.5, 0.45, "#C99A2E"),
        side_dot(s, d.x0 - 0.05, 33.4, d.z0 + 21.5, 0.45, "#C99A2E"),
    ]
    group(s, "side-panel", [side, seam, *screws])

    # Steam wand: drawn before the portafilter so the handle sits in front.
    gx = d.x0 + d.width * 0.61
    gz = d.z0 - 5.0
    gy = d.group_y
    wx = d.x0 + d.width * 0.78
    wand = [s.front_circle(wx, gy + 1.0, 3.0, d.z0 - 0.2, chrome_side, sw=0.8),
            s.front_circle(wx, gy + 1.0, 1.7, d.z0 - 0.35, "#2A2C2E", sw=0.6)]
    wand += s.tube([(wx, gy + 1.0, d.z0 - 0.4),
                    (d.x0 + d.width * 0.88, gy - 12.0, d.z0 - 1.5),
                    (d.x0 + d.width * 0.93, gy - 25.0, d.z0 - 2.5),
                    (d.x0 + d.width * 0.95, gy - 30.0, d.z0 - 2.8)], 13.0,
                   chrome_front, highlight="#FFFFFF", sw=0.7)
    wand += s.tube([(d.x0 + d.width * 0.95, gy - 28.0, d.z0 - 2.8),
                    (d.x0 + d.width * 0.96, gy - 32.0, d.z0 - 2.9)], 16.0,
                   "#1B1D20", sw=1.0)
    group(s, "steam-wand", wand)

    # Portafilter: a larger chrome basket, a chrome collar, a thick straight
    # black handle angled down/right, in front of the wand.
    portafilter = [
        s.cylinder_y(gx, gz, d.portafilter_r + 0.8, gy - 16.4, gy - 15.4,
                     side="#1E2022", top="#1E2022", sw=0.7)[0],
        s.cylinder_y(gx, gz, d.portafilter_r + 0.6, gy - 15.4, gy - 10.0,
                     side="#B8B6AD", top=chrome_top, sw=1.0)[0],
        s.cylinder_y(gx, gz, d.portafilter_r + 1.0, gy - 10.6, gy - 9.4,
                     side=chrome_side, top=chrome_top, sw=0.8)[0],
    ]
    portafilter.append(s.cylinder_y(gx, gz, d.portafilter_r + 1.3, gy - 13.4, gy - 12.2,
                                    side=chrome_side, top=chrome_top, sw=0.8)[0])
    handle = s.tube([(gx, gy - 13.0, gz - 3.0),
                     (gx + 10, gy - 15.0, gz - 14),
                     (gx + 21, gy - 18.0, gz - 28),
                     (gx + 24.5, gy - 19.0, gz - 33)], 52.0,
                    "#17191C", highlight="#4A4D51", sw=1.0)
    handle.append(s.front_circle(gx + 24.5, gy - 19.0, 2.3, gz - 33.2,
                                 "#101214", sw=0.7))
    portafilter.append(s.front_rounded(gx - 3.4, gy - 14.6, gx - 1.2, gy - 10.6, 0.6,
                                      gz - d.portafilter_r - 1.3, "#FFFFFF", stroke=None,
                                      sw=0, opacity=0.18))
    portafilter += handle
    group(s, "portafilter", portafilter)

    # Group head: a compact chrome overhang over a visible vertical cylinder,
    # with a dark gasket and a round collar.  It is not a white cube.
    group_head = [
        s.front_ellipse(gx, gy - 17, 17, 2.4, d.z0 - 0.1, "#000000",
                        stroke=None, sw=0, opacity=0.13),
        s.cylinder_y(gx, gz, d.group_r + 0.8, gy - 11.4, gy - 10.0,
                     side="#6F7274", top="#6F7274", sw=0.7)[0],
        s.cylinder_y(gx, gz, d.group_r + 0.4, gy - 10.0, gy + 1.6,
                     side=chrome_side, top=chrome_top, sw=1.1)[0],
        s.disc_y(gx, gz, d.group_r, d.group_r, gy - 11.5, "#1E2022"),
    ]
    group_head += s.box(gx - 13, gy + 0.4, d.z0 - 7, gx + 13, gy + 8.0, d.z0,
                        front=chrome_front, side=chrome_edge, top=chrome_top, sw=1.3)
    group_head.append(s.front_rounded(gx - 13, gy + 0.4, gx + 13, gy + 8.0, 1.3,
                                      d.z0 - 7.05, chrome_front, sw=1.0))
    group_head.append(s.front_rounded(gx - 4.2, gy - 9.2, gx - 1.6, gy + 0.8, 0.7,
                                      gz - d.group_r - 0.2, "#FFFFFF", stroke=None,
                                      sw=0, opacity=0.20))
    group_head.append(s.front_rounded(gx + 2.2, gy - 9.2, gx + 4.2, gy + 0.8, 0.7,
                                      gz - d.group_r - 0.2, "#6E7174", stroke=None,
                                      sw=0, opacity=0.16))
    group_head.append(s.face([(gx - 13, gy + 0.4, d.z0 - 7.1),
                              (gx + 13, gy + 0.4, d.z0 - 7.1),
                              (gx + 13, gy + 1.8, d.z0 - 7.1),
                              (gx - 13, gy + 1.8, d.z0 - 7.1)],
                             fill=black_side, stroke=None, sw=0, opacity=0.45))
    group(s, "group-head", group_head)

    # Two smaller yellow knobs on a chrome top.
    knobs = []
    for fx in (0.30, 0.59):
        x = d.x0 + d.width * fx
        z = d.z0 + d.depth * 0.30
        knobs.extend(s.cylinder_y(x, z, 4.2, d.top_top - 0.8, d.top_top,
                                  side="#1B1D20", top="#34373A", sw=0.9))
        knobs.extend(s.cylinder_y(x, z, 3.5, d.top_top, d.top_top + 7.4,
                                  side=yellow_side, top=yellow_top, sw=1.2))
    group(s, "top-knobs", knobs)

    # Oval badge: QUICK / MOL / OMRE, live type (not traced).
    bx = d.x0 + d.width * 0.704
    by = 103.0
    badge = [s.front_ellipse(bx, by, 7.8, 9.6, d.z0 - 0.2, cream, sw=1.2)]
    badge.append(s.front_ellipse(bx, by, 6.9, 8.7, d.z0 - 0.3, "none",
                                 stroke=red, sw=0.9))
    badge.append(s.text_front(bx, by + 1.7, d.z0 - 0.4, "QUICK", 2.55, red,
                              weight="700", letter_spacing=0.02))
    badge.append(s.text_front(bx, by - 1.7, d.z0 - 0.4, "MOL", 1.1, red,
                              weight="700", letter_spacing=0.12))
    badge.append(s.text_front(bx, by - 4.4, d.z0 - 0.4, "OMRE", 0.52, red,
                              weight="400", letter_spacing=0.08))
    group(s, "badge", badge)

    # Lower switch plate at the left, red jewel, right-side steam valve.
    px0, px1 = d.x0 + 11, d.x0 + 33
    py0, py1 = d.base_h + 3.6, d.base_h + 23.0
    controls = [s.front_rounded(px0, py0, px1, py1, 2.0, d.z0 - 0.4, "#202225", sw=1.2)]
    for i, x in enumerate((px0 + 2.0, px0 + 8.2, px0 + 14.4)):
        controls.append(s.front_rounded(x, py0 + 5.4, x + 5.0, py1 - 5.4, 0.8,
                                        d.z0 - 0.5, cream, sw=0.8))
        controls.append(s.front_rounded(x + 2.0, py0 + 7.0, x + 3.0, py1 - 7.0, 0.4,
                                        d.z0 - 0.6, "#8E8775", sw=0.5))
        controls.append(s.text_front(x + 2.5, py1 - 2.0, d.z0 - 0.6,
                                     ("SPENTO", "FERMO", "CAFFE")[i], 0.86,
                                     "#D8D2C2", weight="400", letter_spacing=0.01))
    lx = d.x0 + d.width * 0.48
    controls.append(s.front_circle(lx, py0 + 9.0, 1.8, d.z0 - 0.5, "#B5322A", sw=0.8))
    controls.append(s.front_circle(lx - 0.5, py0 + 9.5, 0.55, d.z0 - 0.6, "#F2B2A8", sw=None))
    controls += s.cylinder_z(d.x0 + d.width * 0.90, 30.0, d.z0 - 5.0, d.z0 - 1.0,
                             1.7, 1.5, side=chrome_side, cap=chrome_top, sw=0.7)
    controls.append(s.front_circle(d.x0 + d.width * 0.90, 30.0, 0.9, d.z0 - 5.1,
                                   "#1B1D20", sw=0.5))
    group(s, "controls", controls)

    # Designed chrome bands on the lower front.
    highlights = [
        s.face([(d.x0 + 6, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 26, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 22, d.base_h + 5, d.z0 - 0.1),
                (d.x0 + 3, d.base_h + 5, d.z0 - 0.1)],
               fill="#FFFFFF", stroke=None, sw=0, opacity=0.22),
        s.face([(d.x0 + 55, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 68, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 64, d.base_h + 5, d.z0 - 0.1),
                (d.x0 + 51, d.base_h + 5, d.z0 - 0.1)],
               fill="#6E7174", stroke=None, sw=0, opacity=0.12),
    ]
    group(s, "highlights", highlights)

    metadata = {
        "generator": "vector_reconstruct.py / build_quickmill.py (T054)",
        "source": "Wikimedia Commons: File:Quick Mill Omre Espresso Machine.jpg",
        "license": "CC0",
        "method": "semantic 2.5D reconstruction matched to photo landmarks; no edge trace",
        "projection": "axonometric x-right/y-up/z-back-left",
        "comparison_fractions": {
            "aspect_w_over_h": 0.80,
            "black_bottom": 0.216,
            "group_centre": 0.275,
            "tray_top": 0.520,
            "lower_top": 0.618,
            "base_top": 0.843,
        },
        "dimensions": {
            "width": d.width, "depth": d.depth, "base_h": d.base_h,
            "lower_h": d.lower_h, "tray_h": d.tray_h, "tower_h": d.tower_h,
            "top_h": d.top_h, "black_band_h": d.black_band_h,
        },
    }
    return s.svg(
        title="Quick Mill Omre — T054 landmark-matched reconstruction",
        desc=("A 2.5D product illustration rebuilt against the source photo's "
              "landmark fractions: chrome top, oval badge, chrome group head with "
              "an angled portafilter and a deep drip tray."),
        metadata=metadata)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    out = ART / "quickmill-t054.svg"
    out.write_text(build(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
