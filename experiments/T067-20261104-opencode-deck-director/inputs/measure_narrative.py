#!/usr/bin/env python3
"""T067 audit probe: the narrative/temporal facts design_critic.py does not check.

For each deck, per slide:
  base_words          words visible at t=0 (no entrance effect)
  base_objects        text/picture objects visible at t=0
  words_per_view      words visible after each click (cumulative)
  max_view_words      the largest state an audience ever reads
  slide_words         all words on the slide (what DEN-WORDS measures)
  carrier_click       click index at which each picture appears (0 = base state)
  title_animated      an object named like a title with an in-slide entrance
  lifecycles          objects with >= 2 effects
  click_purposes      purpose strings found in the deck (always 0: they live in plan JSON)

Read-only. Run from the repo root:  python workspace/t067_metrics.py DECK.pptx [...]
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve()
while ROOT.parent != ROOT and not (ROOT / "scripts" / "motion_director.py").is_file():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

import design_critic as dc  # noqa: E402
import morph_studio as mstu  # noqa: E402
import motion_director as md  # noqa: E402

TITLE_NAMES = {"title", "h1", "ctrtitle"}


def metrics(path):
    model = md.deck_model(path)
    pkg = mstu.Package(path)
    rows = []
    for slide, part in zip(model["slides"], pkg.slides()):
        groups = dc.slide_timing(pkg.xml(part))[0]
        first_click = {}
        for gi, g in enumerate(groups, 1):
            for e in g["effects"]:
                first_click.setdefault(e["spid"], gi)
        words = lambda o: len((o.get("text") or "").split())
        content = [o for o in slide["objects"]
                   if (o.get("text") or "").strip() or o.get("image")]
        base = [o for o in content if o["id"] not in first_click]
        base_words = sum(words(o) for o in base)
        # words visible after each click: base + every object whose first effect is <= k
        per_view = []
        for k in range(len(groups) + 1):
            vis = [o for o in content if first_click.get(o["id"], 0) <= k]
            per_view.append(sum(words(o) for o in vis))
        titles = [o for o in slide["objects"]
                  if (o["name"] or "").lower() in TITLE_NAMES
                  or (o.get("placeholder") or {}).get("type") in md.TITLE_TYPES]
        per = Counter(e["spid"] for g in groups for e in g["effects"] if e["spid"])
        rows.append({
            "slide": slide["index"],
            "clicks": len(groups),
            "base_objects": len(base),
            "base_words": base_words,
            "slide_words": sum(words(o) for o in content),
            "max_view_words": max(per_view),
            "words_per_view": per_view,
            "pictures": {o["name"]: first_click.get(o["id"], 0)
                         for o in slide["objects"] if o.get("image")},
            "titles_animated": [t["name"] for t in titles if t["id"] in first_click],
            "lifecycles": sum(1 for n in per.values() if n >= 2),
            "effects": sum(len(g["effects"]) for g in groups),
        })
    return {
        "deck": Path(path).name,
        "slides": len(rows),
        "clicks": sum(r["clicks"] for r in rows),
        "clicks_per_slide": [r["clicks"] for r in rows],
        "empty_base_slides": [r["slide"] for r in rows if r["base_words"] == 0 and r["clicks"] > 0],
        "pictures_on_last_click": [{"slide": r["slide"], "picture": n}
                                   for r in rows for n, c in r["pictures"].items()
                                   if c == r["clicks"] and c > 0],
        "titles_animated_slides": [r["slide"] for r in rows if r["titles_animated"]],
        "lifecycles": sum(r["lifecycles"] for r in rows),
        "effects": sum(r["effects"] for r in rows),
        "max_view_words": max((r["max_view_words"] for r in rows), default=0),
        "slide_words": sum(r["slide_words"] for r in rows),
        "rows": rows,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    print(json.dumps([metrics(p) for p in sys.argv[1:]], indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
