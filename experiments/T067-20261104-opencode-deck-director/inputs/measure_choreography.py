#!/usr/bin/env python3
"""Measure image beat alignment on T066 and on the two variants.

Definitions (used in image-rules.md):
  image_lead   clicks between the first image entrance and the first text
               entrance on the same slide (negative = images first).
  image_lag    click groups after the last text entrance in which any image
               still enters (0 = no image arrives after the words).
  coda_images  images whose entrance is later than every text entrance.
  empty_frame_clicks  clicks in which a frame/disc/caption is visible while
               its picture is not (measured from the authored shape tree).
  images_per_click    image entrances per click group.

Frames are matched to their picture by an explicit map, because T066 names them
(e.g. !!marx-ring -> !!marx, plato-disc -> plato, !!panel -> the portraits on
that slide). The variants group each frame with its picture, so the map is only
needed for T066.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts import pptx_animator as anim  # noqa: E402

HERE = Path(__file__).resolve().parent
EXP = HERE.parent

DECKS = [
    ("T066", ROOT / "experiments" / "T066-20261104-opencode-triet-hoc-ch1"
     / "artifacts" / "T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx", None),
    ("A", EXP / "artifacts" / "T067-variant-A-cover-flow.pptx", None),
    ("B", EXP / "artifacts" / "T067-variant-B-cover-flow.pptx", None),
]

FRAME_TO_PIC = {
    "!!marx-ring": "!!marx", "!!engels-ring": "!!engels",
    "!!lenin-ring": "!!lenin", "plato-disc": "plato",
}


def is_picture(shape):
    if shape.shape_type == 13:
        return True
    # a grouped portrait (face + rim) is one image unit
    if shape.shape_type == 6:
        return any(c.shape_type == 13 for c in shape.shapes)
    return False


def main():
    out = []
    for label, path, _ in DECKS:
        prs = Presentation(str(path))
        for idx, slide in enumerate(prs.slides, 1):
            if label == "T066" and idx not in (1, 2, 7):
                continue
            groups = anim.read_main_sequence(slide._element)
            shapes = {str(s.shape_id): s for s in slide.shapes}
            pic_ids = {sid for sid, s in shapes.items() if is_picture(s)}
            text_ids = {sid for sid, s in shapes.items()
                        if s.has_text_frame and any(p.text.strip()
                                                    for p in s.text_frame.paragraphs)}
            first = {}
            for g_i, g in enumerate(groups, 1):
                for e in g["effects"]:
                    if e["visibility"] == "visible":
                        first.setdefault(e["spid"], g_i)
            image_first = {sid: first.get(sid, 0) for sid in pic_ids}
            text_first = {sid: first.get(sid, 0) for sid in text_ids}
            if not image_first:
                continue
            per_click = [0] * (len(groups) + 1)
            for sid, c in image_first.items():
                per_click[c] += 1
            last_text = max(text_first.values()) if text_first else 0
            coda = sorted(sid for sid, c in image_first.items() if c > last_text)
            # empty frame: frame visible at click k, its picture not visible yet
            states, _ = anim.simulate_states(slide._element)
            empty_states = 0
            empty_instances = 0
            for st in states:
                hidden = st["hidden_objects"]
                here = 0
                for frame, pic in FRAME_TO_PIC.items():
                    f_id = next((sid for sid, s in shapes.items()
                                 if s.name == frame), None)
                    p_id = next((sid for sid, s in shapes.items()
                                 if s.name == pic), None)
                    if f_id is None or p_id is None:
                        continue
                    if f_id not in hidden and p_id in hidden:
                        here += 1
                empty_instances += here
                empty_states += 1 if here else 0
            names = lambda ids: [shapes[i].name for i in ids]
            out.append({
                "deck": label, "slide": idx, "clicks": len(groups),
                "image_lead": min(image_first.values()) - (min(text_first.values()) if text_first else 0),
                "image_lag": max(0, max(image_first.values()) - last_text),
                "coda_images": names(coda),
                "empty_frame_states": empty_states,
                "empty_frame_instances": empty_instances,
                "images_per_click": per_click[1:],
                "image_entry_clicks": sorted(image_first.values()),
            })
    path = EXP / "artifacts" / "image-beat-metrics.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
    for r in out:
        print(f"{r['deck']} s{r['slide']}  clicks={r['clicks']} "
              f"lead={r['image_lead']:+d} lag={r['image_lag']} "
              f"coda={r['coda_images']} empty={r['empty_frame_states']}/{r['empty_frame_instances']} "
              f"per_click={r['images_per_click']}")


if __name__ == "__main__":
    main()
