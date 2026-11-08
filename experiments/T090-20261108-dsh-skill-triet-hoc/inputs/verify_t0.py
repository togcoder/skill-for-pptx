"""T090 structural self-check (rung 1): what is on screen at t=0 for each slide,
and does every Morph actor survive between its two slides?

The skill's self-check asks "what is left when the slide opens, and can it be
read alone?" -- ``look`` exports the fully built slide, so this script answers
that from the package: a shape is visible at t=0 unless a click plan reveals it.

    python inputs/verify_t0.py artifacts/T090-triet-hoc-ch1.pptx inputs/plan.json -o artifacts/t0_check.json
"""
import argparse
import json
from pathlib import Path

from pptx import Presentation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("plan")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    clicks = {int(k): v for k, v in (plan.get("clicks") or {}).items()}
    transitions = {str(k): v for k, v in (plan.get("transitions") or {}).items()}
    prs = Presentation(args.deck)
    report = {"slides": [], "problems": []}
    for i, slide in enumerate(prs.slides, 1):
        names = [s.name for s in slide.shapes]
        revealed = {item.partition(":")[0] for group in clicks.get(i, []) for item in group}
        visible = [n for n in names if n not in revealed]
        text_words = 0
        quote_at_t0 = False
        for s in slide.shapes:
            if s.name not in visible or not s.has_text_frame:
                continue
            text_words += sum(len(p.text.split()) for p in s.text_frame.paragraphs)
            if s.text_frame.text.lstrip().startswith("“"):
                quote_at_t0 = True
        report["slides"].append({
            "index": i,
            "transition": transitions.get(str(i), transitions.get("default")),
            "clicks": len(clicks.get(i, [])),
            "visible_at_t0": visible,
            "words_at_t0": text_words,
        })
        if i == 1 and clicks.get(1):
            report["problems"].append("cover has clicks")
        # A slide with no title is accepted only when it is a quote slide (slide role
        # "Trích dẫn", guide 3): the quotation itself is the heading.
        if i > 1 and not any(n in visible for n in ("Tieu de", "Tieu de lon")) and not quote_at_t0:
            report["problems"].append(f"slide {i}: no title visible at t=0")
        if text_words == 0 and i > 1:
            report["problems"].append(f"slide {i}: no words at t=0")

    # Morph actors: named !! on both slides, and not revealed by a click on the destination.
    for i in range(1, len(prs.slides)):
        prev, cur = list(prs.slides)[i - 1], list(prs.slides)[i]
        if transitions.get(str(i + 1)) != "morph":
            continue
        prev_actors = {s.name for s in prev.shapes if s.name.startswith("!!")}
        cur_actors = {s.name for s in cur.shapes if s.name.startswith("!!")}
        cur_revealed = {item.partition(":")[0] for group in clicks.get(i + 1, []) for item in group}
        report["morph"] = {
            "pair": [i, i + 1],
            "actors_in_both": sorted(prev_actors & cur_actors),
            "actors_missing_destination": sorted(prev_actors - cur_actors),
            "destination_actors_with_entrance": sorted(cur_actors & cur_revealed),
        }
        if prev_actors - cur_actors:
            report["problems"].append("morph actor missing on destination")
        if cur_actors & cur_revealed:
            report["problems"].append("morph actor has a click entrance on destination")
    report["ok"] = not report["problems"]
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
