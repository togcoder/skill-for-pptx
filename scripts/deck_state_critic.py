#!/usr/bin/env python3
"""Deck state critic (T069) — grade the deck the audience actually sees.

EXPERIMENTAL. Not wired into `design_critic.py` yet.

`design_critic.py` scores the final frame of each slide. This script scores the
*sequence of states*: what is readable at t=0, what enters on which click, and
whether an image/frame/title arrives after the sentence that gives it meaning.

Gates (fail):
  STATE-EMPTY-BASE          no text and no picture visible at t=0
  STATE-NO-CLAIM            no text >= 28 pt with >= 2 words visible at t=0
  STATE-TITLE-ANIMATED      the title enters on a click
  STATE-DECOR-BEFORE-IMAGE  a ring/disc/frame is visible before its picture
  STATE-IMAGE-CODA          a picture first appears in the last click group
  STATE-IMAGE-LAG           a picture first appears after the last text click
  MORPH-ENTRANCE-CONFLICT   a `!!`-named Morph object also has an entrance
  MORPH-NO-PAIR             a Morph transition with no shared `!!` name
  MOT-CLICKS                more than 6 click groups on a slide

Warnings:
  MOT-NO-LIFECYCLE          clicks exist but no object is ever dimmed/exited
  STATE-IMAGE-LED           no claim text at t=0 (allowed only with --allow-image-hook)
  MOT-CLICKS-SOFT           more than 4 click groups on a slide

Usage:
  python scripts/deck_state_critic.py deck.pptx [--json out.json] [--strict]
  python scripts/deck_state_critic.py old.pptx new.pptx

Exit code 0 when no fail gate fires; 1 otherwise (or when --strict and a warning
fires).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import design_critic as dc  # noqa: E402
import morph_studio as mstu  # noqa: E402
import motion_director as md  # noqa: E402

TITLE_TOKENS = {"title", "h1", "ctrtitle"}
FRAME_SUFFIXES = ("-ring", "-disc", "-frame", "-panel")


def _first_clicks(groups):
    """spid -> first click group index (1-based). Base state is absent."""
    first = {}
    for gi, group in enumerate(groups, 1):
        for effect in group["effects"]:
            spid = effect.get("spid")
            if spid:
                first.setdefault(spid, gi)
    return first


def _lifecycle_spids(groups):
    """Objects with an exit, emphasis or path effect (not only an entrance)."""
    seen = set()
    for group in groups:
        for effect in group["effects"]:
            if effect.get("cls") != "entr" and effect.get("spid"):
                seen.add(effect["spid"])
    return seen


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _morph(part_root):
    """Morph lives inside mc:AlternateContent/p159:morph, not direct p:transition."""
    for el in part_root.iter():
        if _local(el.tag) == "transition":
            for child in el.iter():
                if _local(child.tag) == "morph":
                    return child.get("option") or "byObject"
    return None


def _shared_morph_names(prev_names, names):
    return sorted(n for n in names if n.startswith("!!") and n in prev_names)


def critique(path: str, allow_image_hook: bool = False) -> dict:
    model = md.deck_model(path)
    pkg = mstu.Package(path)
    parts = pkg.slides()

    rows = []
    gates = []
    prev_morph_names: set[str] = set()
    deck_lifecycles = False
    morph_count = 0

    def gate(code, severity, slide, detail):
        gates.append({"code": code, "severity": severity,
                      "slide": slide, "detail": detail})

    for slide, part in zip(model["slides"], parts):
        root = pkg.xml(part)
        groups = dc.slide_timing(root)[0]
        clicks = len(groups)
        first = _first_clicks(groups)
        lifecycles = _lifecycle_spids(groups)
        deck_lifecycles = deck_lifecycles or bool(lifecycles)
        idx = slide["index"]

        objects = slide["objects"]
        pictures = [o for o in objects if o.get("image")]
        frames = [o for o in objects
                  if (o.get("name") or "").lower().endswith(FRAME_SUFFIXES)]
        texts = [o for o in objects if (o.get("text") or "").strip()]

        base_texts = [o for o in texts if o["id"] not in first]
        base_words = sum(len((o.get("text") or "").split()) for o in base_texts)
        base_claim = [o for o in base_texts
                      if (o.get("max_font_pt") or 0) >= 28
                      and len((o.get("text") or "").split()) >= 2]
        base_visual = [o for o in objects
                       if o["id"] not in first
                       and (o.get("image") or o.get("chart_summary"))]
        base_pictures = [o for o in base_visual if o.get("image")]

        if base_words == 0 and not base_visual:
            gate("STATE-EMPTY-BASE", "fail", idx,
                 "no text and no picture visible at t=0")

        if not base_claim:
            if base_pictures and allow_image_hook:
                gate("STATE-IMAGE-LED", "warn", idx,
                     "no claim text at t=0; image-led state allowed by flag")
            else:
                gate("STATE-NO-CLAIM", "fail", idx,
                     "no text >= 28 pt with >= 2 words at t=0 "
                     f"(base words={base_words})")

        for title in [o for o in texts
                      if (o.get("token") or "").lower() in TITLE_TOKENS
                      or (o.get("name") or "").lower() == "title"]:
            if first.get(title["id"]):
                gate("STATE-TITLE-ANIMATED", "fail", idx,
                     f"title '{title['name']}' enters on click {first[title['id']]}")

        for frame in frames:
            if first.get(frame["id"]):
                continue  # not visible at t=0, harmless
            stem = (frame.get("name") or "").lower()
            for suffix in FRAME_SUFFIXES:
                if stem.endswith(suffix):
                    stem = stem[: -len(suffix)]
                    break
            for pic in pictures:
                pname = (pic.get("name") or "").lower()
                if (pname == stem or pname.startswith(stem + "-")) and first.get(pic["id"]):
                    gate("STATE-DECOR-BEFORE-IMAGE", "fail", idx,
                         f"'{frame['name']}' visible at t=0, "
                         f"'{pic['name']}' enters click {first[pic['id']]}")

        last_text_click = max([0] + [first[o["id"]] for o in texts if o["id"] in first])
        for pic in pictures:
            fst = first.get(pic["id"], 0)
            if clicks and fst == clicks:
                gate("STATE-IMAGE-CODA", "fail", idx,
                     f"picture '{pic['name']}' first appears on the last click "
                     f"({fst}/{clicks})")
            elif fst > last_text_click:
                gate("STATE-IMAGE-LAG", "fail", idx,
                     f"picture '{pic['name']}' enters click {fst} after the last "
                     f"text click {last_text_click}")

        for obj in objects:
            if (obj.get("name") or "").startswith("!!") and first.get(obj["id"]):
                gate("MORPH-ENTRANCE-CONFLICT", "fail", idx,
                     f"Morph object '{obj['name']}' has an entrance on click "
                     f"{first[obj['id']]}")

        if clicks > 6:
            gate("MOT-CLICKS", "fail", idx, f"{clicks} click groups (> 6)")
        elif clicks > 4:
            gate("MOT-CLICKS-SOFT", "warn", idx, f"{clicks} click groups (> 4)")

        morph = _morph(root)
        names = {o.get("name") or "" for o in objects}
        if morph:
            morph_count += 1
            if prev_morph_names and not _shared_morph_names(prev_morph_names, names):
                gate("MORPH-NO-PAIR", "fail", idx,
                     f"Morph '{morph}' but no shared '!!' name with the previous slide")
        prev_morph_names = names

        rows.append({
            "slide": idx,
            "clicks": clicks,
            "effects": sum(len(g["effects"]) for g in groups),
            "base_words": base_words,
            "base_claim": bool(base_claim),
            "base_pictures": len(base_pictures),
            "words_per_view": [
                sum(len((o.get("text") or "").split()) for o in texts
                    if first.get(o["id"], 0) <= k)
                for k in range(clicks + 1)
            ],
            "pictures": {o["name"]: first.get(o["id"], 0) for o in pictures},
            "lifecycles": len(lifecycles),
            "morph": morph,
        })

    if not deck_lifecycles:
        gate("MOT-NO-LIFECYCLE", "warn", None,
             "no object is ever dimmed or exited; the deck only adds")

    fails = [g for g in gates if g["severity"] == "fail"]
    warns = [g for g in gates if g["severity"] == "warn"]
    return {
        "deck": Path(path).name,
        "sha256": _sha256(path),
        "slides": len(rows),
        "clicks": sum(r["clicks"] for r in rows),
        "effects": sum(r["effects"] for r in rows),
        "morphs": morph_count,
        "lifecycles": sum(r["lifecycles"] for r in rows),
        "gates": gates,
        "summary": {"fail": len(fails), "warn": len(warns)},
        "verdict": "fail" if fails else ("warn" if warns else "pass"),
        "rows": rows,
    }


def _sha256(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _print_text(report):
    print(f"{report['deck']}  sha={report['sha256']}")
    print(f"  slides={report['slides']} clicks={report['clicks']} "
          f"effects={report['effects']} morphs={report['morphs']} "
          f"lifecycles={report['lifecycles']} -> {report['verdict'].upper()}")
    for g in report["gates"]:
        where = f"slide {g['slide']}" if g["slide"] is not None else "deck"
        print(f"  [{g['severity'].upper():4}] {g['code']:26} {where}: {g['detail']}")
    print("  per slide: " + " ".join(
        f"{r['slide']}:{r['clicks']}c/{r['base_words']}w" for r in report["rows"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("decks", nargs="+")
    ap.add_argument("--json", help="write one report or a list to this path")
    ap.add_argument("--strict", action="store_true", help="warnings exit 1")
    ap.add_argument("--allow-image-hook", action="store_true",
                    help="allow an image-only t=0 state (downgrade to warning)")
    args = ap.parse_args(argv)

    reports = [critique(p, args.allow_image_hook) for p in args.decks]
    for report in reports:
        _print_text(report)
    if args.json:
        payload = reports[0] if len(reports) == 1 else reports
        Path(args.json).write_text(
            json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    failed = any(r["verdict"] == "fail" or (args.strict and r["verdict"] == "warn")
                 for r in reports)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
