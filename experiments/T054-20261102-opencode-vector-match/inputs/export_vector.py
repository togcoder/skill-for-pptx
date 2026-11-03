#!/usr/bin/env python3
"""Export the 3D blockout's current view as DXF (3D -> vector, no trace)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ART = EXP / "artifacts"
SC = Path(r"D:\artcraft\SolidCraft\solidcraft-cli.exe")
CAD = Path(r"D:\artcraft\CADCraft\cadcraft-cli.exe")

cam = {"target": [190, 150, 300], "yaw": 0.45, "pitch": 0.17,
       "distance": 2200, "fov": 0.35}

script = json.loads((ART / "blockout.json").read_text(encoding="utf-8"))
script["commands"] += [
    {"command": "view.apply", "params": {"camera": cam}},
    {"command": "file.export_view_dxf", "params": {
        "camera": cam, "hidden": "omit", "tolerance": 0.05,
        "path": str(ART / "blockout.dxf")}},
]
export = ART / "blockout_export.json"
export.write_text(json.dumps(script, indent=2), encoding="utf-8")
print(export)

res = subprocess.run([str(SC), "run", str(export)], capture_output=True, text=True,
                     encoding="utf-8")
print(res.stdout.strip()[-1000:])
if res.returncode:
    print(res.stderr.strip()[-1000:])

dxf = ART / "blockout.dxf"
print("dxf", dxf.exists(), dxf.stat().st_size if dxf.exists() else 0)
if dxf.exists():
    out = ART / "blockout.svg"
    r = subprocess.run([str(CAD), "convert", str(dxf), str(out)], capture_output=True,
                       text=True, encoding="utf-8")
    print(r.stdout.strip()[-600:])
    if r.returncode:
        print(r.stderr.strip()[-600:])
    print("svg", out.exists(), out.stat().st_size if out.exists() else 0)
