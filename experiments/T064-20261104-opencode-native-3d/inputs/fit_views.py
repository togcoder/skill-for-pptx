#!/usr/bin/env python3
"""T064: is a transition frame one dimmed 3D render, or a mixture of two?

For each frame the script fits the best brightness scale s (least squares) to
every ladder camera render and reports the residual. A frame that is a single
3D render -- at any opacity -- fits one rung closely. A cross-fade (or any two
renders at once) fits no single rung, because two silhouettes cannot align.

The same test is run on the Fade control, whose middle frame is known to show
both views at once.

Run:  python experiments/T064-.../inputs/fit_views.py
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
TMP = EXP.parents[1] / "workspace" / "t064" / "frames" / "fit"

CROP = (150, 230, 800, 880)
XS = [round(-1.2 + 0.1 * i, 1) for i in range(25)]
SAMPLES = {
    "morph": [4.2, 4.4, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.0],
    "fade": [4.2, 4.4, 4.5, 4.6, 4.7, 4.8, 5.0],
    "shared": [4.2, 4.4, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.0],
    "modelonly": [4.2, 4.4, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 6.0],
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


def fit(frame: np.ndarray, view: np.ndarray) -> tuple[float, float]:
    """Best brightness scale and residual RMSE."""
    num = float((frame * view).sum())
    den = float((view * view).sum())
    s = num / den if den else 0.0
    res = float(np.sqrt(np.mean((frame - s * view) ** 2)))
    return s, res


def main() -> dict:
    ladder = {x: load(LADDER / f"cam-{x:+.1f}.png") for x in XS}
    report = {"crop_1080p": CROP, "ladder_cameras_x": XS, "frames": {}}
    for key, samples in SAMPLES.items():
        mp4 = PREVIEW / f"camera-{key}.mp4"
        rows = []
        for t in samples:
            f = grab(mp4, t)
            fits = {x: fit(f, ladder[x]) for x in XS}
            best = min(fits, key=lambda x: fits[x][1])
            rows.append({
                "t": t,
                "peak": round(float(f.max()), 1),
                "mean": round(float(f.mean()), 2),
                "best_camera_x": best,
                "scale": round(fits[best][0], 4),
                "residual": round(fits[best][1], 3),
                "residual_by_camera": {f"{x:+.1f}": round(fits[x][1], 3) for x in XS},
            })
        report["frames"][key] = rows
    (PREVIEW / "view-fit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    for key, rows in report["frames"].items():
        print(key)
        for r in rows:
            print(f"  t={r['t']:.1f} peak={r['peak']:5.1f} best_x={r['best_camera_x']:+.1f} "
                  f"scale={r['scale']:.3f} residual={r['residual']:6.2f}")
    return report


if __name__ == "__main__":
    main()
