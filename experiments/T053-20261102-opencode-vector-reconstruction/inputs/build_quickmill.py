"""Semantic 2.5D reconstruction of the Quick Mill Omre (T053).

The photo is a reference for proportions, materials and camera.  Every visible
face here is a box, cylinder, plate or control in object coordinates; no Canny
edge, no trace, no raster underlay.

The major dimensions live in ``Dimensions`` so changing one value moves the
dependent parts.  That is the difference between a reconstruction and a trace.
"""
from __future__ import annotations

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
    x0: float = 3
    width: float = 94
    z0: float = 0
    depth: float = 69
    base_h: float = 7
    lower_h: float = 35
    tray_h: float = 5
    tower_h: float = 45
    top_h: float = 4
    tray_front: float = -6
    tray_depth: float = 46
    group_r: float = 8.5
    portafilter_r: float = 7.5

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
    def cx(self) -> float:
        return self.x0 + self.width / 2.0

    @property
    def group_y(self) -> float:
        return self.tray_top + 14.0


def group(scene: Scene, name: str, items: list[str]) -> None:
    scene.body.append(f'<g id="{name}">')
    scene.body.extend(items)
    scene.body.append("</g>")


def build(dims: Dimensions | None = None) -> str:
    d = dims or Dimensions()
    view = Projection(ox=400, oy=900, sx=4.6, sy=5.5, dx=-2.05, dy=-1.35)
    s = Scene(view, width=1000, height=1000)

    chrome_front = s.gradient("chromeFront", [(0, "#ECE9E0"), (0.45, "#CFCCC2"), (1, "#A8A59B")])
    chrome_side = s.gradient("chromeSide", [(0, "#C4C1B7"), (1, "#8E8C84")])
    chrome_top = s.gradient("chromeTop", [(0, "#FAF8F0"), (1, "#D6D4CB")])
    yellow_side = s.gradient("yellowSide", [(0, "#E0AE2E"), (1, "#B47E14")])
    yellow_top = s.gradient("yellowTop", [(0, "#F6CD55"), (1, "#D8A122")])
    black_front = s.gradient("blackFront", [(0, "#2E3135"), (1, "#1A1C1F")])
    black_side = s.gradient("blackSide", [(0, "#202327"), (1, "#101214")])
    black_top = s.gradient("blackTop", [(0, "#3A3D42"), (1, "#24272B")])
    cream = "#EDE4CF"
    red = "#B43A2E"

    # Designed floor shadow, in object coordinates.
    group(s, "shadow", [s.disc_y(d.cx, d.z0 + d.depth / 2, d.width * 0.62,
                                 d.depth * 0.35, -0.1, "#E7E1D4", opacity=0.85)])

    # Feet: dark rear, brass front.
    feet = []
    for x, z in ((d.x0 + 13, d.z1 - 13), (d.x1 - 13, d.z1 - 13)):
        feet.extend(s.cylinder_y(x, z, 3.2, -4, 0, side="#2A2C2E", top="#4A4C4E", sw=1.2))
    for x, z in ((d.x0 + 13, d.z0 + 13), (d.x1 - 13, d.z0 + 13)):
        feet.extend(s.cylinder_y(x, z, 3.2, -4, 0, side="#A67C1A", top="#D0A63C", sw=1.2))
    group(s, "feet", feet)

    # Base plinth with a chrome lip.
    base = s.box(d.x0 - 2, 0, d.z0 - 2, d.x1 + 2, d.base_h, d.z1 + 2,
                 front=black_front, side=black_side, top=black_top, sw=2.4)
    base.append(s.face([(d.x0 - 2, d.base_h - 0.8, d.z0 - 2.05),
                        (d.x1 + 2, d.base_h - 0.8, d.z0 - 2.05),
                        (d.x1 + 2, d.base_h, d.z0 - 2.05),
                        (d.x0 - 2, d.base_h, d.z0 - 2.05)],
                       fill=chrome_side, stroke=None, sw=0))
    group(s, "base", base)

    # Lower body: yellow side, chrome front, dark top.
    lower = s.box(d.x0, d.base_h, d.z0, d.x1, d.lower_top, d.z1,
                  front=chrome_front, side=yellow_side, top="#5A5A55", sw=2.2)
    group(s, "lower-body", lower)

    # Tower starts above the tray: the tray no longer pierces the front wall.
    split = d.tower_top - 14.0
    tower = [
        s.face([(d.x0, d.tray_top, d.z0), (d.x1, d.tray_top, d.z0),
                (d.x1, split, d.z0), (d.x0, split, d.z0)],
               fill=chrome_front, sw=2.2),
        s.face([(d.x0, split, d.z0), (d.x1, split, d.z0),
                (d.x1, d.tower_top, d.z0), (d.x0, d.tower_top, d.z0)],
               fill=black_front, sw=2.2),
        s.face([(d.x0, d.tower_top, d.z0), (d.x1, d.tower_top, d.z0),
                (d.x1, d.tower_top, d.z1), (d.x0, d.tower_top, d.z1)],
               fill="#2A2D31", sw=2.2),
        s.face([(d.x0, split - 0.6, d.z0 - 0.1), (d.x1, split - 0.6, d.z0 - 0.1),
                (d.x1, split + 0.4, d.z0 - 0.1), (d.x0, split + 0.4, d.z0 - 0.1)],
               fill=chrome_side, stroke=None, sw=0),
    ]
    group(s, "tower", tower)

    # Top panel overhangs the tower by 1 unit on each side and 2 at the front.
    top = s.box(d.x0 - 1, d.tower_top, d.z0 - 2, d.x1 + 1, d.top_top, d.z1,
                front=black_front, side=black_side, top=black_top, sw=2.4)
    top.append(s.face([(d.x0 - 1, d.tower_top, d.z0 - 2), (d.x1 + 1, d.tower_top, d.z0 - 2),
                       (d.x1 + 1, d.tower_top + 0.8, d.z0 - 2),
                       (d.x0 - 1, d.tower_top + 0.8, d.z0 - 2)],
                      fill=chrome_side, stroke=None, sw=0, opacity=0.6))
    group(s, "top-panel", top)

    # Cup-warmer rails, behind the knobs.
    rails = []
    for frac in (0.52, 0.64, 0.76, 0.88):
        z = d.z0 + d.depth * frac
        rails.extend(s.box(d.x0 + 9, d.top_top, z - 1.1, d.x1 - 9, d.top_top + 2.2, z + 1.1,
                           front=chrome_front, side=chrome_side, top=chrome_top, sw=1.1))
    group(s, "cup-rails", rails)

    # Drip tray: black body, repeated slot pattern, chrome lip.
    tray = s.box(d.x0, d.lower_top, d.tray_front, d.x1, d.tray_top,
                 d.tray_front + d.tray_depth,
                 front=black_front, side=black_side, top="#15171A", sw=2.0)
    grid = []
    for i in range(12):
        z = d.tray_front + 2 + i * 3.5
        grid.append(s.face([(d.x0 + 4, d.tray_top + 0.2, z),
                            (d.x1 - 4, d.tray_top + 0.2, z),
                            (d.x1 - 4, d.tray_top + 0.2, z + 1.4),
                            (d.x0 + 4, d.tray_top + 0.2, z + 1.4)],
                           fill="#0B0D0F", stroke=None, sw=0))
    for x in range(int(d.x0 + 8), int(d.x1 - 6), 8):
        grid.append(s.face([(x, d.tray_top + 0.25, d.tray_front + 1),
                            (x + 1.3, d.tray_top + 0.25, d.tray_front + 1),
                            (x + 1.3, d.tray_top + 0.25, d.tray_front + d.tray_depth - 4),
                            (x, d.tray_top + 0.25, d.tray_front + d.tray_depth - 4)],
                           fill="#0B0D0F", stroke=None, sw=0))
    tray += grid
    tray.append(s.face([(d.x0, d.lower_top + 0.2, d.tray_front - 0.1),
                        (d.x1, d.lower_top + 0.2, d.tray_front - 0.1),
                        (d.x1, d.lower_top + 2.4, d.tray_front - 0.1),
                        (d.x0, d.lower_top + 2.4, d.tray_front - 0.1)],
                       fill=chrome_front, sw=1.4))
    group(s, "drip-tray", tray)

    # One continuous yellow side panel; drawn after the tray so the tray does
    # not cut the panel in half.
    group(s, "side-panel", [s.face(
        [(d.x0, d.base_h, d.z0), (d.x0, d.base_h, d.z1),
         (d.x0, d.tower_top, d.z1), (d.x0, d.tower_top, d.z0)],
        fill=yellow_side, sw=2.2)])

    # Portafilter is lower than the group housing, so it is painted first.
    gx = d.cx
    gz = d.z0 - 6.0
    gy = d.group_y
    portafilter = [
        s.cylinder_y(gx, gz, d.portafilter_r + 0.2, gy - 9.4, gy - 8.4,
                     side="#1E2022", top="#1E2022", sw=0.8)[0],
        s.cylinder_y(gx, gz, d.portafilter_r, gy - 8.4, gy + 1.0,
                     side="#B8B6AD", top=chrome_top, sw=1.4)[0],
        s.cylinder_y(gx, gz, d.portafilter_r + 0.5, gy + 0.6, gy + 1.2,
                     side=chrome_side, top=chrome_top, sw=1.0)[0],
    ]
    portafilter += s.cylinder_z(gx, gy - 4.0, gz - d.portafilter_r + 1.5, d.z0 - 42,
                                4.4, 3.8, side=black_side, cap="#24272A", sw=1.4)
    group(s, "portafilter", portafilter)

    # Rectangular group housing.  It is drawn after the basket, so its bottom
    # face covers the basket top; no top ellipse peeks out.
    group_head = [
        s.front_ellipse(gx, gy - 11, 18, 3.0, d.z0 - 0.1, "#000000",
                        stroke=None, sw=0, opacity=0.14),
    ]
    group_head += s.box(gx - 16, gy + 1.0, d.z0 - 10, gx + 16, gy + 9.0, d.z0,
                        front=chrome_front, side=chrome_side, top=chrome_top, sw=1.8)
    group_head.append(s.face([(gx - 16, gy + 1.0, d.z0 - 10.1),
                              (gx + 16, gy + 1.0, d.z0 - 10.1),
                              (gx + 16, gy + 2.2, d.z0 - 10.1),
                              (gx - 16, gy + 2.2, d.z0 - 10.1)],
                             fill=chrome_side, stroke=None, sw=0))
    group(s, "group-head", group_head)

    # Steam wand: bracket first, then the tube; z stays in front of the face.
    wand = [s.front_circle(d.x0 + d.width * 0.84, gy + 4, 4.0, d.z0 - 0.2,
                           chrome_side, sw=1.0),
            s.front_circle(d.x0 + d.width * 0.84, gy + 4, 3.0, d.z0 - 0.4,
                           "#2A2C2E", sw=1.0)]
    wand += s.tube([(d.x0 + d.width * 0.84, gy + 4, d.z0 - 0.5),
                    (d.x0 + d.width * 0.90, gy - 11, d.z0 - 2),
                    (d.x0 + d.width * 0.94, gy - 30, d.z0 - 3)], 11.0,
                   chrome_front, highlight="#FFFFFF", sw=0.8)
    wand += s.tube([(d.x0 + d.width * 0.94, gy - 26, d.z0 - 3),
                    (d.x0 + d.width * 0.95, gy - 31, d.z0 - 3.2)], 15.0,
                   "#1B1D20", sw=1.5)
    group(s, "steam-wand", wand)

    # Top knobs: black base ring + yellow cylinder.
    knobs = []
    for fx in (0.27, 0.67):
        x = d.x0 + d.width * fx
        z = d.z0 + d.depth * 0.35
        knobs.extend(s.cylinder_y(x, z, 7.4, d.top_top - 1.2, d.top_top,
                                  side="#1B1D20", top="#34373A", sw=1.2))
        knobs.extend(s.cylinder_y(x, z, 6.4, d.top_top, d.top_top + 10,
                                  side=yellow_side, top=yellow_top, sw=1.6))
    group(s, "top-knobs", knobs)

    # Badge: cream disc, red ring, vector lettering (not traced).
    bx = d.x0 + d.width * 0.73
    by = d.tower_top - 7
    badge = [s.front_circle(bx, by, 8.6, d.z0 - 0.2, cream, sw=1.6)]
    badge.append(s.front_circle(bx, by, 7.3, d.z0 - 0.3, "none", stroke=red, sw=1.1))
    badge.append(s.text_front(bx, by + 0.4, d.z0 - 0.4, "QUICK", 3.1, red,
                              weight="700", letter_spacing=0.03))
    badge.append(s.text_front(bx, by - 2.8, d.z0 - 0.4, "MILL", 1.2, red,
                              weight="700", letter_spacing=0.16))
    group(s, "badge", badge)

    # Switch plate, three rockers, labels and red light.
    px0, px1 = d.x0 + 21, d.x0 + 53
    py0, py1 = d.base_h + 6, d.base_h + 28
    controls = [s.front_rounded(px0, py0, px1, py1, 2.4, d.z0 - 0.4, "#202225", sw=1.4)]
    for i, x in enumerate((px0 + 4.5, px0 + 13.5, px0 + 22.5)):
        controls.append(s.front_rounded(x, py0 + 4, x + 5.5, py1 - 5, 1.0,
                                        d.z0 - 0.5, cream, sw=1.0))
        controls.append(s.front_rounded(x + 2.1, py0 + 6.5, x + 3.4, py1 - 7.5, 0.5,
                                        d.z0 - 0.6, "#8E8775", sw=0.6))
        controls.append(s.text_front(x + 2.75, py1 - 2.4, d.z0 - 0.6,
                                     ("SPENTO", "FERMO", "CAFFE")[i], 1.1,
                                     "#D8D2C2", weight="400", letter_spacing=0.02))
    lx = d.x0 + d.width * 0.65
    controls.append(s.front_circle(lx, py0 + 9, 2.2, d.z0 - 0.5, "#B5322A", sw=1.0))
    controls.append(s.front_circle(lx - 0.6, py0 + 9.6, 0.7, d.z0 - 0.6, "#F2B2A8", sw=None))
    group(s, "controls", controls)

    # Designed chrome bands on the front face, in object coordinates.
    highlights = [
        s.face([(d.x0 + 9, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 32, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 27, d.base_h + 5, d.z0 - 0.1),
                (d.x0 + 5, d.base_h + 5, d.z0 - 0.1)],
               fill="#FFFFFF", stroke=None, sw=0, opacity=0.16),
        s.face([(d.x0 + 67, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 80, d.lower_top - 2, d.z0 - 0.1),
                (d.x0 + 74, d.base_h + 5, d.z0 - 0.1),
                (d.x0 + 61, d.base_h + 5, d.z0 - 0.1)],
               fill="#6E7174", stroke=None, sw=0, opacity=0.08),
    ]
    group(s, "highlights", highlights)

    metadata = {
        "generator": "vector_reconstruct.py / build_quickmill.py (T053)",
        "source": "Wikimedia Commons: File:Quick Mill Omre Espresso Machine.jpg",
        "license": "CC0",
        "method": "semantic 2.5D reconstruction: boxes, cylinders, plates and controls; no edge trace",
        "projection": "axonometric x-right/y-up/z-back-left",
        "dimensions": {
            "width": d.width, "depth": d.depth, "base_h": d.base_h,
            "lower_h": d.lower_h, "tray_h": d.tray_h, "tower_h": d.tower_h,
            "top_h": d.top_h,
        },
    }
    return s.svg(
        title="Quick Mill Omre — semantic vector reconstruction",
        desc=("A clean 2.5D product illustration reconstructed from boxes, cylinders, "
              "plates and controls. The photo supplied proportions and materials, not line work."),
        metadata=metadata)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    out = ART / "quickmill-reconstruction.svg"
    out.write_text(build(), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
