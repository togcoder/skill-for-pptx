#!/usr/bin/env python3
"""T064: read the exported videos frame by frame and decide fade vs camera move.

Method
------
For every sampled instant of the transition, compare the frame with
  (a) the end state of slide 1 (REF1),
  (b) the end state of slide 2 (REF2),
  (c) the least-squares cross-fade  (1-a)*REF1 + a*REF2.
A cross-fade leaves almost no residual against (c) and a large residual against
both end states. An interpolated camera leaves a large residual against (c) --
two silhouettes cannot both be right -- while still matching neither end state.

Run:  python experiments/T064-.../inputs/analyze_video.py
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
FRAMES = EXP.parents[1] / "workspace" / "t064" / "frames" / "analyze"

# 2 slides x 4 s, morph duration 2000 ms, fade about 1000 ms.
DECKS = {
    "morph": {"mp4": PREVIEW / "camera-morph.mp4",
              "ref1": 3.0, "ref2": 9.0, "samples": [3.6, 3.9, 4.0, 4.2, 4.4,
                                                     4.6, 4.8, 5.0, 5.2, 5.4,
                                                     5.6, 5.8, 6.0, 6.2, 6.6, 7.0]},
    "fade": {"mp4": PREVIEW / "camera-fade.mp4",
             "ref1": 3.0, "ref2": 8.0, "samples": [3.6, 3.9, 4.0, 4.2, 4.4,
                                                   4.6, 4.8, 5.0, 5.2, 5.4,
                                                   5.6, 5.8, 6.0, 6.2, 6.6, 7.0]},
}
BOX = (170, 240, 760, 860)   # model area at 1080p, left half of the slide


def grab(mp4: Path, t: float, out: Path) -> np.ndarray:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4),
         "-frames:v", "1", str(out)], check=True)
    return np.asarray(Image.open(out).convert("RGB"), dtype=np.float32)


def region(img: np.ndarray) -> np.ndarray:
    x0, y0, x1, y1 = BOX
    return img[y0:y1, x0:x1]


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def best_alpha(f: np.ndarray, r1: np.ndarray, r2: np.ndarray) -> tuple[float, float]:
    d = (r2 - r1).ravel()
    y = (f - r1).ravel()
    denom = float(d @ d)
    a = 0.0 if denom == 0 else float(np.clip((y @ d) / denom, 0.0, 1.0))
    blend = r1 + a * (r2 - r1)
    return a, rmse(f, blend)


def verdict(rows: list[dict]) -> str:
    """Name what the transition did, from the frame table alone."""
    ends = [r for r in rows if r["match"] in ("end1", "end2")]
    mid = [r for r in rows if r["t"] not in ("3.6", "3.9", "4.0")]
    if all(r["match"] in ("end1", "end2", "blend") for r in rows):
        return "cross-fade: every frame is an end state or their blend"
    if mid and max(r["ghost_pixels_gt30"] for r in mid) > 0.25:
        return ("neither end state nor a cross-fade: two silhouettes are never "
                "superimposed, the model leaves the stage instead")
    return "no single camera explains the mid frames"


def main() -> dict:
    report = {"box_1080p": BOX, "decks": {}}
    for key, cfg in DECKS.items():
        if not cfg["mp4"].exists():
            raise SystemExit(f"missing {cfg['mp4']}; run create_video.py first")
        ref1 = region(grab(cfg["mp4"], cfg["ref1"], FRAMES / f"{key}-ref1.png"))
        ref2 = region(grab(cfg["mp4"], cfg["ref2"], FRAMES / f"{key}-ref2.png"))
        rows = []
        for t in cfg["samples"]:
            png = FRAMES / f"{key}-{t:04.1f}.png"
            frame = region(grab(cfg["mp4"], t, png))
            a, r_blend = best_alpha(frame, ref1, ref2)
            r1, r2 = rmse(frame, ref1), rmse(frame, ref2)
            ghost = float(np.mean(np.abs(frame - (ref1 + a * (ref2 - ref1))) > 30))
            rows.append({"t": t, "alpha": round(a, 4),
                         "rmse_end1": round(r1, 3), "rmse_end2": round(r2, 3),
                         "rmse_blend": round(r_blend, 3),
                         "ghost_pixels_gt30": round(ghost, 4),
                         "match": "end1" if r1 < 2 else ("end2" if r2 < 2 else
                                  ("blend" if r_blend < max(2.0, min(r1, r2) * 0.5)
                                   else "neither"))})
        report["decks"][key] = {
            "mp4": str(cfg["mp4"]),
            "ref1_t": cfg["ref1"], "ref2_t": cfg["ref2"],
            "frames": rows,
            "verdict": verdict(rows),
        }
    (PREVIEW / "video-analysis.json").write_text(json.dumps(report, indent=2),
                                                 encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
