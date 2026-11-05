"""T074: scan the video and classify Morph matching without fixed timestamps.

The video is 109.4 s for 45 slides because every Morph adds its 1.2 s to the
2 s advance. Fixed per-slide times drift; this scanner follows each case colour
from its A state through the transition to B.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/T074-20261105-opencode-morph-rules"
MP4 = EXP / "preview/morph-matrix.mp4"
SCAN = ROOT / "workspace/T074/scan"
TMP = ROOT / "workspace/T074/frames2"
TMP.mkdir(parents=True, exist_ok=True)

CASES = [
    "same-bang", "same-name", "diff-name", "rect-ellipse", "text-same",
    "text-diff", "picture-same", "picture-diff", "group-same", "rotate90",
    "entrance", "byword", "bychar", "zorder", "offslide",
]
PALETTE = [
    (215, 154, 50), (220, 80, 70), (80, 170, 220), (120, 200, 120),
    (200, 120, 220), (240, 200, 80), (90, 200, 190), (240, 140, 180),
    (170, 170, 240), (230, 120, 60), (140, 220, 90), (100, 180, 240),
    (230, 90, 140), (180, 140, 80), (120, 210, 170),
]
A_CENTER, B_CENTER = 60.0, 252.0  # 320 px wide scan


def blobs(mask: np.ndarray) -> dict:
    cols = np.where(mask.any(axis=0))[0]
    if len(cols) == 0:
        return {"blobs": 0, "center": None, "width": 0, "pixels": 0}
    groups, start, prev = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - prev > 10:
            groups.append((start, prev))
            start = c
        prev = c
    groups.append((start, prev))
    return {"blobs": len(groups), "center": round(float(cols.mean()), 1),
            "width": int(groups[0][1] - groups[0][0]) if len(groups) == 1 else None,
            "group_widths": [int(b - a) for a, b in groups],
            "pixels": int(mask.sum())}


def main():
    files = sorted(SCAN.glob("*.png"))
    frames = [np.asarray(Image.open(p).convert("RGB"), dtype=np.int16) for p in files]
    palette = np.array(PALETTE, dtype=np.int16)
    index_frames = []
    for f in frames:
        d = np.abs(f[:, :, None, :] - palette[None, None, :, :]).sum(axis=3)
        idx = d.argmin(axis=2).astype(np.uint8)
        idx[d.min(axis=2) > 140] = 255
        index_frames.append(idx)
    rows, mids = [], []
    cursor = 0
    for case_i, (case, colour) in enumerate(zip(CASES, PALETTE)):
        masks = [ix == case_i for ix in index_frames]
        counts = [int(m.sum()) for m in masks]
        present = [i for i, n in enumerate(counts) if n > 3]
        intervals, cur = [], [present[0]] if present else []
        for i in present[1:]:
            if i - cur[-1] <= 10:
                cur.append(i)
            else:
                intervals.append(cur); cur = [i]
        if cur:
            intervals.append(cur)
        if not intervals:
            rows.append({"case": case, "verdict": "absent", "interval": None})
            continue
        seq = next((iv for iv in intervals if iv[0] >= cursor), None)
        if seq is None:
            seq = max(intervals, key=len)
        cursor = seq[-1] + 5
        centers = [masks[i].mean(axis=0).nonzero()[0].mean() if counts[i] else None for i in seq]
        valid = [c for c in centers if c is not None]
        start_c = float(np.median(valid[:5]))
        end_c = float(np.median(valid[-5:]))
        target = (start_c + end_c) / 2
        mid_i = min(seq, key=lambda i: abs((centers[seq.index(i)] or 0) - target))
        mid = blobs(masks[mid_i])
        if end_c - start_c < 15:
            verdict = "static/no-match"
        elif mid["blobs"] == 1 and mid["center"] is not None and start_c + 12 < mid["center"] < end_c - 12:
            verdict = "continuous"
        elif mid["blobs"] > 1:
            verdict = "two-blobs"
        else:
            verdict = "endpoint"
        if counts[seq[-1]] < 3:
            verdict = "missing-at-end"
        rows.append({"case": case, "verdict": verdict, "frames": [seq[0], seq[-1]],
                     "start_center": round(start_c, 1), "end_center": round(end_c, 1),
                     "mid_frame": mid_i, "mid": mid})
        # full-resolution mid frame for the contact sheet
        t = mid_i / 10
        p = TMP / f"{case}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}",
                        "-i", str(MP4), "-frames:v", "1", str(p)], check=True)
        mids.append((case, verdict, p))
        print(f"{case:14} {verdict:16} start={start_c:6.1f} end={end_c:6.1f} mid={mid}")

    (EXP / "artifacts/matrix.json").write_text(
        json.dumps({"scan_fps": 10, "a_center_px": A_CENTER, "b_center_px": B_CENTER,
                    "rows": rows}, indent=1), encoding="utf-8")

    thumb_w, thumb_h = 320, 180
    cols = 3
    sheet = Image.new("RGB", (cols * thumb_w, 5 * (thumb_h + 30)), "#111111")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
    for k, (case, verdict, path) in enumerate(mids):
        im = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        x, y = (k % cols) * thumb_w, (k // cols) * (thumb_h + 30)
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + thumb_h + 4), f"{case}: {verdict}",
                  fill="#7CFC98" if verdict == "continuous" else "#FFD400", font=font)
    out = EXP / "preview/matrix-midframes.png"
    sheet.save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
