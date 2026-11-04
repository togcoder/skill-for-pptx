#!/usr/bin/env python3
"""T060: compare DeckCraft's Timeline step durations with PowerPoint's own MainSequence.

Reads the PPTX with the built deckcraft-cli (`render-animation --plan`), groups the
PowerPoint `native_sequence.json` effects into click steps (a `on click` effect starts
a step; with/after previous join it), and writes step-durations.csv.

Usage:
  python .../inputs/compare_steps.py --cli workspace/deckcraft-src/target/debug/deckcraft-cli.exe \
      --pptx workspace/coffee_dynamic.pptx \
      --native workspace/ppt_render/native_sequence.json
"""
import argparse
import csv
import json
import math
import re
import subprocess
from pathlib import Path


def deckcraft_plan(cli, pptx, slides):
    plans = []
    for i in range(slides):
        r = subprocess.run([cli, "render-animation", pptx, "--slide", str(i), "--plan"],
                           capture_output=True, text=True, check=False)
        if r.returncode != 0:
            raise SystemExit(r.stderr)
        steps = []
        for line in r.stdout.splitlines():
            m = re.match(r"\s+step (\d+): (auto|click)\s+(\d+)ms, (\d+) effects", line)
            if m:
                steps.append({"step": int(m.group(1)), "kind": m.group(2),
                              "ms": int(m.group(3)), "effects": int(m.group(4))})
        plans.append(steps)
    return plans


def powerpoint_steps(native):
    groups = []
    cur = []
    for e in native["effects"]:
        if e["trigger"] == 1 and cur:
            groups.append(cur)
            cur = []
        cur.append(e)
    if cur:
        groups.append(cur)
    steps = []
    for g in groups:
        dur = max((e["delay_s"] + (0 if not math.isfinite(e["duration_s"]) else e["duration_s"])) for e in g)
        steps.append({"ms": round(dur * 1000), "effects": len(g)})
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cli", required=True)
    ap.add_argument("--pptx", required=True)
    ap.add_argument("--native", required=True)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "step-durations.csv"))
    args = ap.parse_args()
    native = json.loads(Path(args.native).read_text(encoding="utf-8-sig"))
    plans = deckcraft_plan(args.cli, args.pptx, len(native["slides"]))
    rows = []
    for i, slide in enumerate(native["slides"]):
        psteps = powerpoint_steps(slide)
        dsteps = plans[i]
        if len(psteps) != len(dsteps):
            rows.append({"slide": i, "step": "-", "deckcraft_ms": "", "powerpoint_ms": "",
                         "delta_ms": "", "deckcraft_effects": "", "powerpoint_effects": "",
                         "note": f"step count differs: {len(dsteps)} vs {len(psteps)}"})
            continue
        for k, (d, p) in enumerate(zip(dsteps, psteps)):
            rows.append({"slide": i, "step": k, "deckcraft_ms": d["ms"], "powerpoint_ms": p["ms"],
                         "delta_ms": d["ms"] - p["ms"], "deckcraft_effects": d["effects"],
                         "powerpoint_effects": p["effects"], "note": ""})
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    bad = [r for r in rows if r["delta_ms"] not in ("", 0)]
    print(f"{len(rows)} steps, {len(bad)} with |delta| > 0 ms, max |delta| "
          f"{max((abs(int(r['delta_ms'])) for r in rows if r['delta_ms'] != ''), default=0)} ms")
    for r in bad:
        print(r)


if __name__ == "__main__":
    main()
