#!/usr/bin/env python3
"""Measure every picture in the T066 deck: geometry, crop, first entry click.

Reads the frozen T066 artifact read-only and prints a JSON audit used by
image-audit.md. No PPTX is modified.

    python experiments/T067-20261104-opencode-deck-director/inputs/audit_images.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import pptx_animator as anim  # noqa: E402

DECK = (ROOT / "experiments" / "T066-20261104-opencode-triet-hoc-ch1"
        / "artifacts" / "T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx")
OUT = Path(__file__).resolve().parent.parent / "artifacts" / "image-audit.json"
SLIDE_W, SLIDE_H = 13.333, 7.5


def inches(emu):
    return round(Emu(emu).inches, 3)


def text_of(shape):
    if not shape.has_text_frame:
        return ""
    return " / ".join(p.text for p in shape.text_frame.paragraphs if p.text.strip())


def main():
    prs = Presentation(str(DECK))
    audit = {"deck": DECK.name, "slide_size_in": [SLIDE_W, SLIDE_H], "slides": []}

    for idx, slide in enumerate(prs.slides, 1):
        groups = anim.read_main_sequence(slide._element)
        states, _ = anim.simulate_states(slide._element)
        start_hidden = states[0]["hidden_objects"]
        ids = {str(sh.shape_id): sh for sh in slide.shapes}

        # first entry record per shape
        entry = {}
        for g_i, group in enumerate(groups, 1):
            for e in group["effects"]:
                if e["visibility"] == "visible":
                    entry.setdefault(e["spid"], {
                        "click": g_i, "node_type": e["node_type"],
                        "preset_id": e["preset_id"], "class": e["class"],
                        "duration_ms": e["duration_ms"],
                        "delay_ms": e["delay_ms"],
                        "with_in_group": sum(1 for x in group["effects"]
                                             if x["visibility"] == "visible"),
                    })

        text_shapes = [sh for sh in slide.shapes if sh.has_text_frame and text_of(sh)]
        pics = []
        for sh in slide.shapes:
            if sh.shape_type != 13:  # PICTURE
                continue
            cx = inches(sh.left) + inches(sh.width) / 2
            cy = inches(sh.top) + inches(sh.height) / 2
            near = sorted(
                ({"text": text_of(t)[:64],
                  "dx_in": round(inches(t.left) + inches(t.width) / 2 - cx, 2),
                  "dy_in": round(inches(t.top) + inches(t.height) / 2 - cy, 2)}
                 for t in text_shapes),
                key=lambda d: abs(d["dx_in"]) + abs(d["dy_in"]))[:3]
            e = entry.get(str(sh.shape_id))
            pics.append({
                "name": sh.name,
                "x_in": inches(sh.left), "y_in": inches(sh.top),
                "w_in": inches(sh.width), "h_in": inches(sh.height),
                "height_pct_of_slide": round(inches(sh.height) / SLIDE_H * 100, 1),
                "crop_lrtb": [round(v, 3) for v in (sh.crop_left, sh.crop_right,
                                                     sh.crop_top, sh.crop_bottom)],
                "entry_click": e["click"] if e else None,
                "entry_nodes_in_click": e["with_in_group"] if e else None,
                "entry_preset": e["preset_id"] if e else None,
                "entry_ms": e["duration_ms"] if e else None,
                "hidden_at_start": str(sh.shape_id) in start_hidden,
                "nearest_text": near,
            })

        # timeline anchors and captions (slide 7 comparison)
        anchors = []
        if idx == 7:
            for sh in slide.shapes:
                if sh.name.startswith("tl-") or sh.name.endswith("-date") \
                        or sh.name.endswith("-desc") or sh.name.endswith("-name"):
                    anchors.append({"name": sh.name,
                                    "x_center": round(inches(sh.left) + inches(sh.width) / 2, 2),
                                    "text": text_of(sh)})

        audit["slides"].append({
            "index": idx,
            "shapes": len(slide.shapes),
            "click_groups": len(groups),
            "images": pics,
            **({"timeline_anchors": anchors} if anchors else {}),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT)
    for s in audit["slides"]:
        if not s["images"]:
            continue
        print(f"\nslide {s['index']}  clicks={s['click_groups']}")
        for p in s["images"]:
            print(f"  {p['name']:<12} {p['w_in']}x{p['h_in']}in "
                  f"({p['height_pct_of_slide']}%h) crop={p['crop_lrtb']} "
                  f"entry=click {p['entry_click']} +{p['entry_ms']}ms "
                  f"hidden_at_start={p['hidden_at_start']} "
                  f"near={p['nearest_text'][0]['text'][:30]!r}")


if __name__ == "__main__":
    main()
