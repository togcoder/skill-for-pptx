#!/usr/bin/env python3
"""T060: inventory the Forge `dynamic` deck's timing tree and map every effect to DeckCraft.

Usage:
  python experiments/T060-.../inputs/inspect_dynamic_deck.py \
      --pptx workspace/coffee_dynamic.pptx \
      --coverage experiments/T060-.../inputs/preset-coverage.csv

Writes dynamic-deck-inventory.json and dynamic-deck-inventory.md next to this script.
"""
import argparse
import collections
import csv
import json
import re
import zipfile
from pathlib import Path

from lxml import etree

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"p": P}
ROOT = Path(__file__).resolve().parents[3]


def u32(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def max_dur(ctn):
    vals = [u32(c.get("dur")) for c in ctn.iter(f"{{{P}}}cTn")]
    vals = [v for v in vals if v is not None and v > 1]
    return max(vals) if vals else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", required=True)
    ap.add_argument("--coverage", default=str(Path(__file__).resolve().parent / "preset-coverage.csv"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    args = ap.parse_args()
    out = Path(args.out)
    coverage = {}
    with open(args.coverage, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            coverage[(r["class"], int(r["preset_id"]))] = r

    z = zipfile.ZipFile(args.pptx)
    slides = []
    for name in sorted((n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                       key=lambda s: int(re.search(r"(\d+)", s).group(1))):
        root = etree.fromstring(z.read(name))
        effects = []
        for c in root.iter(f"{{{P}}}cTn"):
            if c.get("presetID") is None:
                continue
            cls = c.get("presetClass", "entr")
            pid = u32(c.get("presetID")) or 0
            sub = u32(c.get("presetSubtype")) or 0
            node = c.get("nodeType", "")
            cov = coverage.get((cls, pid), {})
            if cls == "path" and pid == 0:
                cov = {"name": "custom-path", "deckcraft_effect": "customPath", "fidelity": "path"}
            st = c.find(f"{{{P}}}stCondLst/{{{P}}}cond")
            effects.append({
                "class": cls, "preset_id": pid, "subtype": sub, "node_type": node,
                "duration_ms": max_dur(c),
                "delay_ms": u32(st.get("delay") if st is not None else 0) or 0,
                "auto_rev": c.get("autoRev") == "1",
                "repeat": c.get("repeatCount", ""),
                "lab_name": cov.get("name", ""),
                "deckcraft_effect": cov.get("deckcraft_effect", ""),
                "fidelity": cov.get("fidelity", ""),
            })
        click = sum(1 for e in effects if e["node_type"] == "clickEffect")
        auto_first = bool(effects) and effects[0]["node_type"] != "clickEffect"
        slides.append({
            "file": name,
            "effects": len(effects),
            "click_steps": click,
            "auto_first": auto_first,
            "main_steps": click + (1 if auto_first else 0),
            "by_preset": dict(collections.Counter(f'{e["class"]}:{e["preset_id"]}' for e in effects)),
            "items": effects,
        })

    result = {"pptx": args.pptx, "slides": slides}
    (out / "dynamic-deck-inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    distinct = collections.Counter()
    fidelity = collections.Counter()
    for s in slides:
        for e in s["items"]:
            distinct[(e["class"], e["preset_id"], e["lab_name"], e["deckcraft_effect"], e["fidelity"])] += 1
            fidelity[e["fidelity"]] += 1
    lines = ["# Forge `coffee_office_dynamic.json` - timing tree inventory", "",
             f"Deck: `{args.pptx}`", "",
             "| Slide | Effects | Click steps | Auto first | Main steps |",
             "|---|---|---|---|---|"]
    for i, s in enumerate(slides, 1):
        lines.append(f"| {i} | {s['effects']} | {s['click_steps']} | {s['auto_first']} | {s['main_steps']} |")
    lines += ["", "## Distinct presets used", "",
              "| Class:id | Lab name | DeckCraft effect | Fidelity | Effects |",
              "|---|---|---|---|---|"]
    for (cls, pid, lab, dc, fid), n in sorted(distinct.items()):
        lines.append(f"| {cls}:{pid} | {lab} | {dc} | {fid} | {n} |")
    lines += ["", f"Effect fidelity counts: {dict(fidelity)}", ""]
    (out / "dynamic-deck-inventory.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(json.dumps({f"{k[0]}:{k[1]}": v for k, v in sorted(distinct.items())}, indent=2))


if __name__ == "__main__":
    main()
