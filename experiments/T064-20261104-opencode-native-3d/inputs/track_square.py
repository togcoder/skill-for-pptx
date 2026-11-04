#!/usr/bin/env python3
"""T064: track the amber Morph control square through the transition.

The square sits in the top band of the slide, outside the model crop. A real
Morph moves it; a fallback cross-fade shows it at both ends at once, which the
script reports as two amber blobs or an abnormally wide one.

Run:  python experiments/T064-.../inputs/track_square.py
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
TMP = EXP.parents[1] / "workspace" / "t064" / "frames" / "square"

BAND = (0, 40, 1920, 210)          # 1080p rows that hold the square only
AMBER = np.array([215, 154, 50], dtype=np.float32)
SAMPLES = [3.6, 4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0,
           5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.8, 6.0]


def grab(mp4: Path, t: float) -> np.ndarray:
    p = TMP / f"{mp4.stem}-{t:04.2f}.png"
    p.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4),
                    "-frames:v", "1", str(p)], check=True)
    rgb = np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)
    x0, y0, x1, y1 = BAND
    return rgb[y0:y1, x0:x1]


def blobs(band: np.ndarray) -> dict:
    d = np.abs(band - AMBER).sum(axis=2)
    mask = d < 90
    cols = np.where(mask.any(axis=0))[0]
    if len(cols) == 0:
        return {"blobs": 0, "span_px": 0, "center_px": None, "width_px": 0}
    # split on gaps wider than 40 px (a 120 px square is one blob)
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > 40:
            groups.append((start, prev))
            start = c
        prev = c
    groups.append((start, prev))
    total = int(mask.sum())
    return {
        "blobs": len(groups),
        "span_px": int(cols[-1] - cols[0]),
        "center_px": round(float(cols.mean()), 1),
        "width_px": int(groups[0][1] - groups[0][0]) if len(groups) == 1 else None,
        "group_widths": [int(b - a) for a, b in groups],
        "amber_px": total,
    }


def main() -> dict:
    report = {"band_1080p": BAND, "amber_rgb": AMBER.tolist(), "frames": {}}
    for key in ("morph", "fade", "shared"):
        mp4 = PREVIEW / f"camera-{key}.mp4"
        rows = []
        for t in SAMPLES:
            rows.append({"t": t, **blobs(grab(mp4, t))})
        report["frames"][key] = rows
    (PREVIEW / "square-track.json").write_text(json.dumps(report, indent=2),
                                               encoding="utf-8")
    for key, rows in report["frames"].items():
        print(key)
        for r in rows:
            print(f"  t={r['t']:.1f} blobs={r['blobs']} center={r['center_px']} "
                  f"width={r['width_px']} span={r['span_px']}")
    return report


if __name__ == "__main__":
    main()
