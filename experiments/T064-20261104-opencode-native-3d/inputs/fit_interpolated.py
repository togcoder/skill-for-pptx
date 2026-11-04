#!/usr/bin/env python3
"""T064: fit each transition frame to an interpolated camera between ladder rungs.

For a frame f the script searches every adjacent pair of ladder renders
(L_i, L_i+1), a blend weight w in [0, 1] and a brightness scale s, minimising
|| f - s*((1-w)L_i + w L_i+1) ||. A genuine camera interpolation collapses to a
small residual with s ~ 1 and a smooth x(t); a cross-fade of two rasters can
only be explained by mixing the two *end* views, which this model rejects
because it never blends two cameras that are far apart.

Run:  python experiments/T064-.../inputs/fit_interpolated.py
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
PREVIEW = EXP / "preview"
LADDER = PREVIEW / "ladder"
TMP = EXP.parents[1] / "workspace" / "t064" / "frames" / "interp"

CROP = (150, 230, 800, 880)
XS = [round(-1.2 + 0.1 * i, 1) for i in range(25)]
SAMPLES = {
    "morph": [4.2, 4.4, 5.0, 5.2, 5.4, 5.6, 6.0],
    "fade": [4.4, 4.5, 4.6, 4.7, 5.0],
    "shared": [4.2, 4.4, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.0],
    "dup": [4.2, 4.4, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.0],
}


def crop(img: np.ndarray) -> np.ndarray:
    x0, y0, x1, y1 = CROP
    return img[y0:y1, x0:x1]


def load(path: Path) -> np.ndarray:
    return crop(np.asarray(Image.open(path).convert("RGB"), dtype=np.float32))


def grab(mp4: Path, t: float) -> np.ndarray:
    p = TMP / f"{mp4.stem}-{t:04.2f}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4),
                    "-frames:v", "1", str(p)], check=True)
    return load(p)


def fit_pair(frame: np.ndarray, a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    best = (0.0, 0.0, float("inf"))
    for w in np.linspace(0.0, 1.0, 21):
        model = (1.0 - w) * a + w * b
        den = float((model * model).sum())
        s = float((frame * model).sum()) / den if den else 0.0
        res = float(np.sqrt(np.mean((frame - s * model) ** 2)))
        if res < best[2]:
            best = (s, float(w), res)
    return best


def main() -> dict:
    ladder = {x: load(LADDER / f"cam-{x:+.1f}.png") for x in XS}
    report = {"crop_1080p": CROP, "ladder_step": 0.1, "frames": {}}
    for key, samples in SAMPLES.items():
        mp4 = PREVIEW / f"camera-{key}.mp4"
        rows = []
        for t in samples:
            f = grab(mp4, t)
            best = None
            for i in range(len(XS) - 1):
                s, w, res = fit_pair(f, ladder[XS[i]], ladder[XS[i + 1]])
                if best is None or res < best["residual"]:
                    best = {"camera_x": round(XS[i] + 0.1 * w, 3), "scale": round(s, 3),
                            "residual": round(res, 3), "between": [XS[i], XS[i + 1]]}
            rows.append({"t": t, **best})
        report["frames"][key] = rows
    (PREVIEW / "interpolated-fit.json").write_text(json.dumps(report, indent=2),
                                                    encoding="utf-8")
    for key, rows in report["frames"].items():
        print(key)
        for r in rows:
            print(f"  t={r['t']:.1f} camera_x={r['camera_x']:+.2f} "
                  f"scale={r['scale']:.3f} residual={r['residual']:6.2f}")
    return report


if __name__ == "__main__":
    main()
