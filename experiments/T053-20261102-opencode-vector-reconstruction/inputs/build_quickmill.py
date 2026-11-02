"""Semantic 2.5D reconstruction of the Quick Mill Omre (T053).

The photo is a reference for proportions, materials and camera.  Every visible
face here is a box, cylinder, plate or control in object coordinates; no Canny
edge, no trace, no raster underlay.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.vector_reconstruct import (  # noqa: E402
    INK, PAPER, Projection, Scene, _n,
)

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"


def group(scene: Scene, name: str, items: list[str]) -> None:
    scene.body.append(f'<g id="{name}">')
    scene.body.extend(items)
    scene.body.append("</g>")


def build() -> str:
    view = Projection(ox=400, oy=900, sx=4.6, sy=5.5, dx=-2.05, dy=-1.35)
    s = Scene(view, width=1000, height=1000)

    chrome_front = s.gradient("chromeFront", [(0, "#ECE9E0"), (0.45, "#CFCCC2"), (1, "#A8A59B")])
    chrome_side = s.gradient("chromeSide", [(0, "#C4C1B7"), (1, "#8E8C84")])
    chrome_top = s.gradient("chromeTop", [(0, "#FAF8F0"), (1, "#D6D4CB")])
    yellow_front = s.gradient("yellowFront", [(0, "#F0C03A"), (1, "#CE971C")])
    yellow_side = s.gradient("yellowSide", [(0, "#E0AE2E"), (1, "#B47E14")])
    yellow_top = s.gradient("yellowTop", [(0, "#F6CD55"), (1, "#D8A122")])
    black_front = s.gradient("blackFront", [(0, "#2E3135"), (1, "#1A1C1F")])
    black_side = s.gradient("blackSide", [(0, "#202327"), (1, "#101214")])
    black_top = s.gradient("blackTop", [(0, "#3A3D42"), (1, "#24272B")])
    cream = "#EDE4CF"
    red = "#B43A2E"

    # Shadow: a designed floor ellipse, not a traced cast shadow.
    s.body.append('<g id="shadow">'
                  '<ellipse cx="500" cy="902" rx="280" ry="36" fill="#E7E1D4" opacity="0.85"/>'
                  '</g>')

    # Feet (back pair first, then front pair).
    feet = []
    for x, z in ((16, 56), (84, 56)):
        feet.extend(s.cylinder_y(x, z, 3.2, -4, 0, side="#2A2C2E", top="#4A4C4E", sw=1.2))
    for x, z in ((16, 14), (84, 14)):
        feet.extend(s.cylinder_y(x, z, 3.2, -4, 0, side="#A67C1A", top="#D0A63C", sw=1.2))
    group(s, "feet", feet)

    # Base plinth.
    base = s.box(-2, 0, -2, 102, 7, 72, front=black_front, side=black_side,
                 top=black_top, sw=2.4)
    base.append(s.face([(-2, 6.2, -2.05), (102, 6.2, -2.05), (102, 7, -2.05), (-2, 7, -2.05)],
                       fill=chrome_side, stroke=None, sw=0))
    group(s, "base", base)

    # Lower body: yellow side, chrome front, dark top.
    lower = s.box(3, 7, 0, 97, 42, 69, front=chrome_front, side=yellow_side,
                  top="#5A5A55", sw=2.2)
    group(s, "lower-body", lower)

    # Tower: yellow side, chrome lower front, black upper front, dark top.
    tower_top = s.face([(3, 92, 0), (97, 92, 0), (97, 92, 69), (3, 92, 69)],
                       fill="#2A2D31", sw=2.2)
    tower_lower = s.face([(3, 42, 0), (97, 42, 0), (97, 78, 0), (3, 78, 0)],
                         fill=chrome_front, sw=2.2)
    tower_upper = s.face([(3, 78, 0), (97, 78, 0), (97, 92, 0), (3, 92, 0)],
                         fill=black_front, sw=2.2)
    tower_trim = [
        s.face([(3, 77.4, -0.1), (97, 77.4, -0.1), (97, 78.4, -0.1), (3, 78.4, -0.1)],
               fill=chrome_side, stroke=None, sw=0),
        s.face([(3, 91.6, -0.1), (97, 91.6, -0.1), (97, 92, -0.1), (3, 92, -0.1)],
               fill=chrome_side, stroke=None, sw=0, opacity=0.7),
    ]
    group(s, "tower", [tower_top, tower_lower, tower_upper] + tower_trim)

    # Top panel.
    top = s.box(4, 92, 8, 96, 96, 71, front=black_front, side=black_side,
                top=black_top, sw=2.4)
    top.append(s.face([(4, 92, 8), (96, 92, 8), (96, 93, 8), (4, 93, 8)],
                      fill=chrome_side, stroke=None, sw=0, opacity=0.55))
    group(s, "top-panel", top)

    # Cup-warmer rails: four chrome bars on the top face.
    rails = []
    for z in (36, 44, 52, 60):
        rails.extend(s.box(12, 96, z - 1.1, 88, 98.2, z + 1.1,
                           front=chrome_front, side=chrome_side, top=chrome_top, sw=1.1))
    group(s, "cup-rails", rails)

    # Drip tray: black body, grid on top, chrome front lip.
    tray = s.box(3, 42, -6, 97, 47, 40, front=black_front, side=black_side,
                 top="#15171A", sw=2.0)
    grid = []
    for z in (-2, 1.5, 5, 8.5, 12, 15.5, 19, 22.5, 26, 29.5, 33, 36.5):
        grid.append(s.face([(7, 47.2, z), (93, 47.2, z), (88, 47.2, z + 1.4),
                            (7, 47.2, z + 1.4)], fill="#0B0D0F", stroke=None, sw=0))
    for x in range(12, 90, 8):
        grid.append(s.face([(x, 47.25, -3), (x + 1.3, 47.25, -3),
                            (x + 1.3, 47.25, 38), (x, 47.25, 38)],
                           fill="#0B0D0F", stroke=None, sw=0))
    tray += grid
    tray.append(s.face([(3, 42.2, -6.1), (97, 42.2, -6.1), (97, 44.4, -6.1), (3, 44.4, -6.1)],
                       fill=chrome_front, sw=1.4))
    group(s, "drip-tray", tray)

    # One yellow side panel, drawn after the tray so the side is not cut by
    # the tray's black edge.  The seam at y=42 is a designed joint, not a step.
    side_panel = [
        s.face([(3, 7, 0), (3, 7, 69), (3, 92, 69), (3, 92, 0)],
               fill=yellow_side, sw=2.2),
    ]
    group(s, "side-panel", side_panel)

    # Group head: a chrome block with a round collar and a black portafilter.
    group_head = [
        s.front_ellipse(50, 55.5, 12, 2.2, -0.1, "#000000", stroke=None, sw=0, opacity=0.14),
    ]
    group_head += s.cylinder_z(50, 61, 0, -11, 12.5, 11.8,
                               side=chrome_side, cap=chrome_front, sw=1.6)
    group_head.append(s.front_circle(50, 61, 12.2, -11.1, "none", stroke="#7C7E80", sw=2.4))
    group_head.append(s.front_circle(50, 61, 9.4, -11.2, "#1E2022", sw=1.4))
    group(s, "group-head", group_head)

    portafilter = s.cylinder_z(50, 61, -11.2, -14.5, 8.2, 7.8,
                               side=chrome_side, cap=chrome_top, sw=1.2)
    portafilter += s.cylinder_z(50, 61, -14.5, -52, 5.6, 4.8,
                                side=black_side, cap="#24272A", sw=1.4)
    group(s, "portafilter", portafilter)

    # Steam wand: a designed tube on the right, with a black grip.
    wand = s.tube([(82, 65, 0), (86, 50, 2), (90, 31, 4)], 11.0,
                  chrome_front, highlight="#FFFFFF", sw=0.8)
    wand += s.tube([(89.5, 35, 4), (90.2, 30, 4.2)], 15.0, "#1B1D20", sw=1.5)
    wand.append(s.front_circle(82, 66, 4.0, 0.2, chrome_side, sw=1.0))
    wand.append(s.front_circle(82, 66, 3.0, -0.2, "#2A2C2E", sw=1.0))
    group(s, "steam-wand", wand)

    # Top knobs: black base ring + yellow cylinder.
    knobs = []
    for x in (28, 64):
        knobs.extend(s.cylinder_y(x, 24, 7.4, 94.8, 96, side="#1B1D20", top="#34373A", sw=1.2))
        knobs.extend(s.cylinder_y(x, 24, 6.4, 96, 106, side=yellow_side, top=yellow_top, sw=1.6))
    group(s, "top-knobs", knobs)

    # Badge: cream disc, red ring, vector lettering (not traced).
    badge = [s.front_circle(72, 85, 8.6, -0.2, cream, sw=1.6)]
    badge.append(s.front_circle(72, 85, 7.3, -0.3, "none", stroke=red, sw=1.1))
    badge.append(s.text_front(72, 85.4, -0.4, "QUICK", 3.25, red,
                              weight="700", letter_spacing=0.05))
    badge.append(s.text_front(72, 82.2, -0.4, "MOL", 1.35, red, weight="700",
                              letter_spacing=0.18))
    group(s, "badge", badge)

    # Switch plate and red light on the lower front.
    controls = [s.front_rounded(24, 13, 56, 35, 2.4, -0.4, "#202225", sw=1.4)]
    for i, x in enumerate((28.5, 37.5, 46.5)):
        controls.append(s.front_rounded(x, 17, x + 5.5, 30, 1.0, -0.5, cream, sw=1.0))
        controls.append(s.front_rounded(x + 2.1, 19.5, x + 3.4, 27.5, 0.5, -0.6,
                                        "#8E8775", sw=0.6))
        label = ("SPENTO", "FEENO", "CAFFE")[i]
        controls.append(s.text_front(x + 2.75, 32.6, -0.6, label, 1.15,
                                     "#D8D2C2", weight="400", letter_spacing=0.02))
    controls.append(s.front_circle(64, 22, 2.2, -0.5, "#B5322A", sw=1.0))
    controls.append(s.front_circle(63.4, 22.6, 0.7, -0.6, "#F2B2A8", sw=None))
    group(s, "controls", controls)

    # Designed chrome bands on the front face, projected from object space.
    highlights = [
        s.face([(12, 40, -0.1), (35, 40, -0.1), (30, 12, -0.1), (8, 12, -0.1)],
               fill="#FFFFFF", stroke=None, sw=0, opacity=0.16),
        s.face([(70, 40, -0.1), (83, 40, -0.1), (77, 12, -0.1), (64, 12, -0.1)],
               fill="#6E7174", stroke=None, sw=0, opacity=0.08),
    ]
    group(s, "highlights", highlights)

    metadata = {
        "generator": "vector_reconstruct.py / build_quickmill.py (T053)",
        "source": "Wikimedia Commons: File:Quick Mill Omre Espresso Machine.jpg",
        "license": "CC0",
        "method": "semantic 2.5D reconstruction: boxes, cylinders, plates and controls; no edge trace",
        "projection": "axonometric x-right/y-up/z-back-left",
    }
    return s.svg(
        title="Quick Mill Omre — semantic vector reconstruction",
        desc=("A clean 2.5D product illustration reconstructed from boxes, cylinders, "
              "plates and controls. The photo supplied proportions and materials, not line work."),
        metadata=metadata)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    svg = build()
    out = ART / "quickmill-reconstruction.svg"
    out.write_text(svg, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
