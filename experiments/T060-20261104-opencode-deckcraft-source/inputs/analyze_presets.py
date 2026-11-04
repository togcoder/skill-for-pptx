#!/usr/bin/env python3
"""T060: compare the lab's PowerPoint preset table with DeckCraft's animation table.

Usage:
  python experiments/T060-.../inputs/analyze_presets.py --src workspace/deckcraft-src

Inputs:
  knowledge/powerpoint_presets.json      (PowerPoint-authored; 198 presets)
  <deckcraft-src>/crates/model/src/anim.rs (ANIMATIONS static)

Outputs (next to this script, unless --out):
  preset-coverage.csv       one row per lab preset: mapping, conflict, fidelity class
  preset-summary.json       counts used in REPORT.md
  table-conflicts.csv       DeckCraft entries whose (class, preset) names another
                            PowerPoint effect in the lab table
"""
import argparse
import collections
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLASS = {"entr": "Entrance", "exit": "Exit", "emph": "Emphasis", "path": "Path"}
CLASS_BACK = {v: k for k, v in CLASS.items()}

# How the DeckCraft evaluator (crates/anim/src/effects.rs) handles the effect id.
# exact: its own branch reproduces the PowerPoint mechanism.
# approximate: a visible but substituted mechanism (state in `why`).
# fallback: no branch: entrance/exit become an opacity fade, emphasis is a no-op.
EXACT = {
    "appear", "fade", "fly", "peek", "wipe", "zoom", "grow", "expand",
    "spinner", "bounce", "rise", "pulse", "colorPulse", "teeter", "spin",
    "growShrink", "desaturate", "darken", "lighten", "transparency", "complementaryColor",
}
# Exit ids evaluate as their entrance mirror (crates/anim/src/effects.rs, exit_base).
EXIT_BASE = {
    "disappear": "appear", "fadeOut": "fade", "flyOut": "fly", "floatOut": "float",
    "splitOut": "split", "wipeOut": "wipe", "shapeOut": "shape", "wheelOut": "wheel",
    "randomBarsOut": "randomBars", "shrinkTurn": "grow", "zoomOut": "zoom",
    "swivelOut": "swivel", "bounceOut": "bounce", "dissolveOut": "dissolve",
    "blindsOut": "blinds", "boxOut": "box", "checkerboardOut": "checkerboard",
    "diamondOut": "diamond", "peekOut": "peek", "stripsOut": "strips",
    "sinkDown": "rise", "spinnerOut": "spinner", "contract": "expand",
}
APPROX = {
    "blinds": "opacity fade, not blinds",
    "checkerboard": "opacity fade, not checkerboard",
    "randomBars": "opacity fade, not random bars",
    "wheel": "opacity fade, not spokes",
    "dissolve": "opacity fade, not pixel dissolve",
    "box": "centre rectangle clip, not a box outline",
    "circle": "centre rectangle clip, not a circle",
    "diamond": "centre rectangle clip, not a diamond",
    "shape": "centre rectangle clip, not the PowerPoint shape",
    "strips": "rectangle clip, not strips",
    "split": "centre clip; PowerPoint splits from the edges",
    "swivel": "axis scale; PowerPoint swivels in 3D",
    "wave": "shape offset/scale; PowerPoint waves text",
    "float": "offset + fade; also the preset id is Ascend's (42)",
    "swivel": "axis scale; also the preset id is Faded Swivel's (45)",
    "zoom": "scale + fade; also the preset id is Faded Zoom's (53)",
    "objectColor": "whole-shape tint, PowerPoint changes fill/line/font scope",
    "fillColor": "whole-shape tint, PowerPoint changes the fill",
    "lineColor": "whole-shape tint, PowerPoint changes the line",
    "fontColor": "whole-shape tint, PowerPoint changes the font",
    "underline": "shape scale, PowerPoint underlines text",
    "boldFlash": "shape scale + tint, PowerPoint bolds text",
    "colorPulse": "shape tint; PowerPoint pulses the fill",
}
# Our preset names that are a different effect from the DeckCraft label for the
# same preset id. Values are the PowerPoint name the id really has (our table).
ID_SHIFT = {
    ("Entrance", 42): "Ascend (DeckCraft calls id 42 Float In)",
    ("Exit", 42): "Ascend (DeckCraft calls id 42 Float Out)",
    ("Entrance", 53): "Faded Zoom (DeckCraft calls id 53 Zoom)",
    ("Exit", 53): "Faded Zoom (DeckCraft calls id 53 Zoom)",
    ("Entrance", 45): "Faded Swivel (DeckCraft calls id 45 Swivel)",
    ("Exit", 45): "Faded Swivel (DeckCraft calls id 45 Swivel)",
    ("Emphasis", 26): "Flash Bulb (DeckCraft calls id 26 Pulse)",
    ("Emphasis", 27): "Flicker (DeckCraft calls id 27 Color Pulse)",
}

# Our names that map to a DeckCraft id but whose PowerPoint id is absent from
# DeckCraft, so they fall back. Listed for the report's examples.
ABSENT_IDS = {
    ("Entrance", 23): "Zoom",
    ("Exit", 23): "Zoom",
    ("Entrance", 19): "Swivel",
    ("Exit", 19): "Swivel",
    ("Entrance", 30): "Float",
    ("Exit", 30): "Float",
}


def parse_animations(src: Path):
    text = (src / "crates/model/src/anim.rs").read_text(encoding="utf-8")
    start = text.index("pub static ANIMATIONS")
    end = text.index("pub fn animation_info", start)
    pat = re.compile(
        r'\(\s*"([^"]+)",\s*"([^"]+)",\s*AnimClass::(\w+),\s*(\d+),\s*(\d+),\s*&\[([^\]]*)\]',
        re.S,
    )
    return [
        {"id": m.group(1), "label": m.group(2), "class": m.group(3), "preset": int(m.group(4)), "default_ms": int(m.group(5))}
        for m in pat.finditer(text[start:end])
    ]


# PowerPoint/DeckCraft labels that name the same effect differently.
ALIASES = {
    frozenset(("appear-out", "disappear")),
    frozenset(("grow-shrink", "grow/shrink")),
    frozenset(("grow-and-turn-out", "shrink & turn")),
    frozenset(("rise-up-out", "sink down")),
    frozenset(("expand-out", "contract")),
    frozenset(("change-fill-color", "fill color")),
    frozenset(("change-line-color", "line color")),
    frozenset(("change-font-color", "font color")),
    frozenset(("brush-on-underline", "underline")),
}


def normalize(s: str):
    s = s.lower().replace("-", " ").replace("&", " and ")
    s = re.sub(r"\b(in|out|entrance|exit)\b", " ", s)
    return " ".join(s.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT / "workspace/deckcraft-src"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    args = ap.parse_args()
    src = Path(args.src)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    dc = parse_animations(src)
    index = {}
    for a in dc:
        index.setdefault((a["class"], a["preset"]), a)  # first match, as effect_for_preset

    lab = json.loads((ROOT / "knowledge/powerpoint_presets.json").read_text(encoding="utf-8"))["presets"]
    rows = []
    for p in lab:
        cls = CLASS[p["presetClass"]]
        key = (cls, p["presetID"])
        hit = index.get(key)
        effect = hit["id"] if hit else ""
        base = EXIT_BASE.get(effect, effect) if cls == "Exit" else effect
        if not hit:
            fidelity, why = "missing", "no DeckCraft animation with this class and preset id; fallback effect"
        elif cls == "Path":
            fidelity, why = "path", "motion runs; the file's animMotion path is used, else the preset geometry"
        elif base in APPROX:
            fidelity, why = "approximate", APPROX[base]
        elif base in EXACT:
            fidelity, why = "exact", "dedicated evaluator branch"
        else:
            fidelity, why = "fallback", "no evaluator branch (the id exists but plays as a fade or no-op)"
        shift = ID_SHIFT.get(key, "")
        if shift:
            fidelity, why = "id-shift", shift
        rows.append({
            "class": p["presetClass"], "name": p["name"], "preset_id": p["presetID"],
            "subtype": p["presetSubtype"], "deckcraft_effect": effect,
            "deckcraft_label": hit["label"] if hit else "",
            "fidelity": fidelity, "why": why,
        })

    with (out / "preset-coverage.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # DeckCraft entries whose same (class, id) has a different name in the lab table.
    # Path presets encode the subtype in the lab's name (path-up vs Lines/up), so they are
    # compared by behaviour in the fidelity table, not here.
    lab_by_key = {(CLASS[p["presetClass"]], p["presetID"]): p["name"] for p in lab}
    conflicts = []
    for a in dc:
        if a["class"] == "Path":
            continue
        key = (a["class"], a["preset"])
        lab_name = lab_by_key.get(key)
        if not lab_name:
            continue
        if frozenset((lab_name, a["label"].lower())) in ALIASES:
            continue
        if normalize(lab_name) != normalize(a["label"]):
            conflicts.append({
                "class": a["class"], "preset_id": a["preset"],
                "deckcraft_id": a["id"], "deckcraft_label": a["label"],
                "powerpoint_name_in_lab_table": lab_name,
            })
    with (out / "table-conflicts.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(conflicts[0]) if conflicts else
                          ["class", "preset_id", "deckcraft_id", "deckcraft_label", "powerpoint_name_in_lab_table"])
        w.writeheader()
        w.writerows(conflicts)

    by_class = collections.defaultdict(collections.Counter)
    for r in rows:
        by_class[r["class"]][r["fidelity"]] += 1
    summary = {
        "deckcraft_animations": len(dc),
        "deckcraft_by_class": dict(collections.Counter(a["class"] for a in dc)),
        "lab_presets": len(rows),
        "mapped_by_id": sum(1 for r in rows if r["deckcraft_effect"]),
        "mapped_pct": round(100 * sum(1 for r in rows if r["deckcraft_effect"]) / len(rows), 1),
        "fidelity_by_class": {k: dict(v) for k, v in by_class.items()},
        "fidelity_total": dict(collections.Counter(r["fidelity"] for r in rows)),
        "table_conflicts": len(conflicts),
    }
    (out / "preset-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("\nconflicts:")
    for c in conflicts:
        print(f"  {c['class']:9} {c['preset_id']:3} DeckCraft {c['deckcraft_id']:16} ({c['deckcraft_label']}) vs lab {c['powerpoint_name_in_lab_table']}")


if __name__ == "__main__":
    main()
