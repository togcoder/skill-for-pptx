#!/usr/bin/env python3
"""T054 3D CSG blockout of the Quick Mill Omre (Z-up, millimetres).

The key correction from Argon: the upper front is not a flat split.  The black
badge panel is the *back wall of a recessed brewing bay*; the chrome left tower
stands in front of it, the black top housing overhangs with a soffit, and the
group head/portafilter project into the bay.  This script emits a SolidCraft
command script and a camera snapshot, so the depth can be checked as geometry,
not as 2D decoration.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
PREVIEW = EXP / "preview"
SC = Path(r"D:\artcraft\SolidCraft\solidcraft-cli.exe")

# mm, Z up, front at y=0, back at y=300
W, D = 380.0, 300.0
BASE_H, LOWER_H = 70.0, 140.0
BAY_Z0, BAY_Z1 = 210.0, 420.0
TOP_H = 80.0
PLATE_H = 15.0
TOWER_W = 152.0
BAY_BACK = 120.0
TRAY_Z = 180.0


def box(name, x0, y0, z0, x1, y1, z1):
    return {"command": "solid.box", "params": {
        "length": x1 - x0, "width": y1 - y0, "height": z1 - z0,
        "corner": [x0, y0, z0], "body_name": name,
    }}


def cyl(name, cx, cy, z0, z1, r):
    return {"command": "solid.cylinder", "params": {
        "radius": r, "height": z1 - z0, "base": [cx, cy, z0],
        "axis": "Z", "body_name": name,
    }}


def cyl_axis(name, base, axis, length, r):
    return {"command": "solid.cylinder", "params": {
        "radius": r, "height": length, "base": base,
        "axis": axis, "body_name": name,
    }}


def appearance(name, color, body=None, faces=None):
    if faces:
        # Face-level assignment: body + faces, not bodies (bodies is body-level).
        p = {"body": body, "faces": faces, "color": color}
    else:
        p = {"bodies": [body] if body else [], "color": color}
    return {"command": "appearance.assign", "params": p}


def build_script() -> dict:
    cmds = []
    # Base, lower body, upper core.
    cmds.append(box("base", -10, -10, 0, W + 10, D + 10, BASE_H))
    cmds.append(box("lower_body", 0, 0, BASE_H, W, D, BASE_H + LOWER_H))
    cmds.append(box("upper_core", 0, 0, BAY_Z0, W, D, BAY_Z1))

    # Cut the brewing bay: right 60%, front 120 mm, between the tray and the top.
    cmds.append(box("bay_cut", TOWER_W, -1, BAY_Z0, W + 1, BAY_BACK, BAY_Z1 + 1))
    cmds.append({"command": "solid.combine", "params": {
        "target": "upper_core", "tools": ["bay_cut"], "operation": "cut",
    }})

    # Cut the drip-tray recess into the lower body, add a dark grate and rim.
    cmds.append(box("tray_cut", 20, 20, TRAY_Z, W - 20, D - 40, BAY_Z0 + 1))
    cmds.append({"command": "solid.combine", "params": {
        "target": "lower_body", "tools": ["tray_cut"], "operation": "cut",
    }})
    cmds.append(box("tray_grate", 20, 20, TRAY_Z, W - 20, D - 40, TRAY_Z + 5))
    cmds.append(box("tray_front_lip", 20, -2, BAY_Z0 - 22, W - 20, 20, BAY_Z0 - 6))

    # Deep black top housing + thin chrome top plate.
    cmds.append(box("top_housing", 0, 0, BAY_Z1, W, D, BAY_Z1 + TOP_H))
    # A separate 2 mm chrome fascia on the left 40% of the black housing:
    # this is the face split, not a face-colour assignment on the whole front.
    cmds.append(box("top_chrome_left", 0, -2, BAY_Z1, TOWER_W, 0, BAY_Z1 + TOP_H))
    cmds.append(box("chrome_top", -5, -10, BAY_Z1 + TOP_H, W + 5, D + 10,
                    BAY_Z1 + TOP_H + PLATE_H))

    # Group housing hangs from the top into the bay; vertical group + basket.
    cmds.append(box("group_housing", 216, 40, 330, 316, BAY_BACK, BAY_Z1))
    cmds.append(cyl("group_head", 266, 80, 270, 330, 50))
    cmds.append(cyl("group_collar", 266, 80, 258, 270, 55))
    cmds.append(cyl("basket", 266, 80, 244, 258, 44))
    cmds.append(cyl_axis("portafilter_handle", [266, 80, 292],
                         [0.70, -0.42, -0.45], 130, 16))
    cmds.append(cyl_axis("steam_wand", [345, 60, 332], [0.0, -0.55, -0.84],
                         120, 4))
    cmds.append(cyl_axis("steam_grip", [345, 6, 205], [0.0, -0.2, -0.98],
                         38, 7))

    # Knobs: yellow cylinders on the chrome top.
    cmds.append(cyl("knob_l", 120, 80, BAY_Z1 + TOP_H + PLATE_H,
                    BAY_Z1 + TOP_H + PLATE_H + 38, 26))
    cmds.append(cyl("knob_r", 240, 80, BAY_Z1 + TOP_H + PLATE_H,
                    BAY_Z1 + TOP_H + PLATE_H + 38, 26))

    # Badge on the *recessed* back wall, switch plate on the lower front-left,
    # red light and the right-hand steam valve.
    cmds.append(cyl_axis("badge", [280, -2, 460], [0.0, 1.0, 0.0], 4, 44))
    cmds.append(box("switch_plate", 28, -4, 90, 148, 0, 172))
    for i, x in enumerate((42, 72, 102)):
        cmds.append(box(f"switch_{i+1}", x, -7, 104, x + 18, -3, 154))
    cmds.append(cyl_axis("red_light", [182, -4, 128], [0.0, 1.0, 0.0], 4, 9))
    cmds.append(cyl_axis("steam_valve", [342, -6, 128], [0.0, 1.0, 0.0], 16, 10))

    # Appearances: body colours first, then the face colours that matter.
    cmds += [
        appearance("base", "#17191C", "base"),
        appearance("lower", "#C9C6BC", "lower_body"),
        appearance("core", "#C9C6BC", "upper_core"),
        appearance("top", "#16181B", "top_housing"),
        appearance("top_chrome", "#C9C6BC", "top_chrome_left"),
        appearance("chrome_top", "#E8E6DE", "chrome_top"),
        appearance("group", "#B8B6AD", "group_head"),
        appearance("collar", "#9E9C93", "group_collar"),
        appearance("basket", "#8E8C84", "basket"),
        appearance("handle", "#111315", "portafilter_handle"),
        appearance("wand", "#E8E6DE", "steam_wand"),
        appearance("grip", "#111315", "steam_grip"),
        appearance("knobs", "#D9A21B", "knob_l"),
        appearance("knobs_r", "#D9A21B", "knob_r"),
        appearance("badge", "#EDE4CF", "badge"),
        appearance("switch_plate", "#1B1D20", "switch_plate"),
        appearance("grate", "#0C0E10", "tray_grate"),
        appearance("lip", "#C9C6BC", "tray_front_lip"),
    ]
    for i in range(1, 4):
        cmds.append(appearance(f"switch_{i}", "#EDE4CF", f"switch_{i}"))
    cmds.append(appearance("red", "#B5322A", "red_light"))
    cmds.append(appearance("valve", "#C9C6BC", "steam_valve"))

    # Left side yellow faces: lower body and upper core at x=0.
    cmds.append(appearance("lower_left", "#E0AE2E", "lower_body",
                           faces=[[0, 150, 140]]))
    cmds.append(appearance("core_left", "#E0AE2E", "upper_core",
                           faces=[[0, 150, 320]]))
    # Recessed back wall is black, not chrome: y=120, right of the tower.
    cmds.append(appearance("bay_back", "#16181B", "upper_core",
                           faces=[[266, BAY_BACK, 320]]))
    cmds.append(appearance("top_left_side", "#E0AE2E", "top_housing",
                           faces=[[0, 150, 460]]))
    # The top housing soffit is black; the top plate stays chrome.

    return {"commands": cmds}


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    script = build_script()
    path = ART / "blockout.json"
    path.write_text(json.dumps(script, indent=2), encoding="utf-8")
    print(path)

    cam = {"target": [190, 150, 300], "yaw": 0.45, "pitch": 0.17,
           "distance": 2200, "fov": 0.35}
    out = PREVIEW / "blockout.png"
    cmd = [str(SC), "snapshot", str(path), "--out", str(out),
           "--width", "1280", "--height", "1512", "--camera", json.dumps(cam),
           "--no-grid", "--no-axes"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout.strip())
    if res.returncode:
        print(res.stderr.strip())


if __name__ == "__main__":
    main()
