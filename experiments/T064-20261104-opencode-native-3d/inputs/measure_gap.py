#!/usr/bin/env python3
"""T064: exact length of the blank gap in variant A, frame by frame.

Variant A (one `Add3DModel` embed per slide) does not move the camera during
Morph: the outgoing model dims out, the frame returns to the background, then
the incoming model dims in. This measures that gap at 30 fps instead of
sampling it coarsely.

Run:  python experiments/T064-.../inputs/measure_gap.py
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
MP4 = PREVIEW / "camera-morph.mp4"
TMP = EXP.parents[1] / "workspace" / "t064" / "frames" / "gap"
BOX = (150, 230, 800, 880)      # model area at 1080p
BACKGROUND_PEAK = 40            # the stage's own peak is 34


def main() -> dict:
    rows = []
    for i in range(120, 170):   # 4.00 s .. 5.63 s at 30 fps
        t = i / 30
        p = TMP / f"{i:04d}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", str(MP4),
                        "-frames:v", "1", str(p)], check=True)
        img = np.asarray(Image.open(p).convert("RGB"), dtype=np.float32)
        x0, y0, x1, y1 = BOX
        crop = img[y0:y1, x0:x1]
        rows.append({"frame": i, "t": round(t, 3), "peak": int(crop.max()),
                     "mean": round(float(crop.mean()), 2)})
    blank = [r for r in rows if r["peak"] <= BACKGROUND_PEAK]
    info = {"mp4": str(MP4), "box_1080p": BOX, "background_peak": BACKGROUND_PEAK,
            "sampled_frames": len(rows), "blank_frames": len(blank),
            "blank_seconds": round(len(blank) / 30, 3),
            "first_blank_frame": blank[0]["frame"] if blank else None,
            "last_blank_frame": blank[-1]["frame"] if blank else None,
            "table": rows}
    (PREVIEW / "variantA-gap.json").write_text(json.dumps(info, indent=2),
                                               encoding="utf-8")
    print(json.dumps({k: info[k] for k in ("blank_frames", "blank_seconds",
                                           "first_blank_frame", "last_blank_frame")},
                     indent=2))
    return info


if __name__ == "__main__":
    main()
