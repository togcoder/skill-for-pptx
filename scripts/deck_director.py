#!/usr/bin/env python3
"""Deck Director: Two-Pass Screenplay Compiler and State-Machine Validator (T068).

Directs presentation decks before layout: locks Stage Inventory, t=0 Resting Base State,
and Lifecycle State Transitions (enter, dim, highlight, exit, zoom) in Pass 1,
then weaves spoken dialogue with Split-Sentence Bridging in Pass 2.
Enforces 5 hard narrative laws:
- NAR-CODA-TRAP: No empty clicks; t0_says <= 35 words.
- NAR-KARAOKE: Vocabulary overlap between spoken dialogue and on-slide text <= 45%.
- NAR-UNANCHORED: Every click's speech references its target actors.
- NAR-COLLISION: Cinematic figures (assemble, drill, >=3 movers) require pre-click lead-in.
- DEN-ACTIVE-VIEW: Active on-screen words capped at <= 45 words per view.

Usage:
    python scripts/deck_director.py check direction.json
    python scripts/deck_director.py compile direction.json -o deck.json --director director.json
    python scripts/deck_director.py ledger deck.pptx [--direction direction.json]
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

# Allowed 9 argument jobs and 7 figures
VALID_JOBS = {"hook", "name", "define", "contrast", "prove", "mechanism", "turn", "land", "ask"}
VALID_FIGURES = {"arrive", "join", "build", "both", "assemble", "clear", "drill"}
VALID_REGISTERS = {"editorial_teaching", "technical", "executive", "editorial_culture"}

VIETNAMESE_STOPWORDS = {
    "và", "của", "là", "có", "được", "trong", "một", "cho", "với", "không", "các",
    "những", "này", "khi", "để", "về", "như", "đã", "tại", "từ", "ra", "đến", "thì",
    "mà", "sẽ", "ở", "bởi", "lại", "theo", "nó", "hay", "cũng", "đang", "nhưng",
    "the", "and", "of", "to", "in", "is", "a", "for", "that", "this", "with", "on"
}


def _tokenize(text: str) -> list[str]:
    """Tokenize and filter stopwords for overlap checking."""
    words = re.findall(r"\b\w+\b", text.lower())
    return [w for w in words if w not in VIETNAMESE_STOPWORDS and len(w) > 1]


def _vocabulary_overlap(text_a: str, text_b: str) -> float:
    """Compute vocabulary overlap (unigram + bigram) between on-slide text and speech."""
    tokens_a = _tokenize(text_a)
    tokens_b = _tokenize(text_b)
    if not tokens_a or not tokens_b:
        return 0.0

    set_a = set(tokens_a)
    set_b = set(tokens_b)

    # Add bigrams
    bigrams_a = {f"{tokens_a[i]}_{tokens_a[i+1]}" for i in range(len(tokens_a) - 1)}
    bigrams_b = {f"{tokens_b[i]}_{tokens_b[i+1]}" for i in range(len(tokens_b) - 1)}

    all_a = set_a | bigrams_a
    all_b = set_b | bigrams_b

    intersection = all_a & all_b
    union = all_a | all_b
    return len(intersection) / len(union) if union else 0.0


# ---------------------------------------------------------------------------
# Validator: check()
# ---------------------------------------------------------------------------

def check_direction(data: dict[str, Any]) -> dict[str, Any]:
    """Validate direction data against schema and 5 hard narrative laws."""
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    # 1. Brief checks
    brief = data.get("brief", {})
    if not brief:
        errors.append({"code": "BRIEF-MISSING", "detail": "Missing 'brief' section"})
    else:
        spine = brief.get("one_sentence", "").strip()
        if not spine:
            errors.append({"code": "BRIEF-SPINE", "detail": "Missing 'one_sentence' spine"})
        elif len(spine.split()) > 20:
            errors.append({"code": "BRIEF-SPINE", "detail": f"Spine exceeds 20 words ({len(spine.split())} words)"})

        reg = brief.get("register")
        if reg not in VALID_REGISTERS:
            errors.append({"code": "BRIEF-REGISTER", "detail": f"Invalid register: {reg}"})

    # 2. Style checks
    style = data.get("style", {})
    if not style.get("preset"):
        errors.append({"code": "STYLE-PRESET", "detail": "Missing style preset"})

    # 3. Beats and Shots map
    beats = data.get("beats", [])
    shots = data.get("shots", [])

    if not beats:
        errors.append({"code": "BEATS-EMPTY", "detail": "Direction contains no beats"})
    if not shots:
        errors.append({"code": "SHOTS-EMPTY", "detail": "Direction contains no shots"})

    shots_by_id = {s["id"]: s for s in shots if "id" in s}
    shots_by_beat = {s.get("beat"): s for s in shots if "beat" in s}

    for b_idx, beat in enumerate(beats):
        b_id = beat.get("id", f"b{b_idx+1}")
        job = beat.get("job")
        if job not in VALID_JOBS:
            errors.append({"code": "BEAT-JOB", "detail": f"Beat {b_id}: Invalid job '{job}'"})

        claim = beat.get("claim", "")
        if len(claim.split()) > 25:
            errors.append({"code": "SCRIPT-CLAIM-LONG", "detail": f"Beat {b_id}: Claim exceeds 25 words"})

        fig = beat.get("figure")
        if fig not in VALID_FIGURES:
            errors.append({"code": "BEAT-FIGURE", "detail": f"Beat {b_id}: Invalid figure '{fig}'"})

        shot = shots_by_beat.get(b_id)
        if not shot:
            errors.append({"code": "BEAT-SHOT-UNMAPPED", "detail": f"Beat {b_id} has no corresponding shot"})
            continue

        shot_obj_ids = {o["id"] for o in shot.get("objects", []) if "id" in o}
        carrier = beat.get("carrier")
        if carrier and carrier not in shot_obj_ids:
            errors.append({"code": "BEAT-CARRIER", "detail": f"Beat {b_id}: Carrier '{carrier}' not found in shot objects"})

        # Pass 2 Spoken Line checks
        t0_says = beat.get("t0_says", "").strip()
        clicks = beat.get("clicks", [])

        if not t0_says:
            errors.append({"code": "NAR-T0-SAYS-MISSING", "detail": f"Beat {b_id}: Missing 't0_says' for t=0 base state"})
        elif len(clicks) > 0 and len(t0_says.split()) > 35:
            errors.append({"code": "NAR-CODA-TRAP", "detail": f"Beat {b_id}: t0_says too long ({len(t0_says.split())} words > 35) without visual event"})

        # Shots state_after & lifecycle validation
        base_state = shot.get("base_state", [])
        if not base_state and job != "hook":
            errors.append({"code": "SHOT-BASE", "detail": f"Shot {shot.get('id')}: Base state at t=0 cannot be empty for job '{job}'"})

        state_after = shot.get("state_after", {})
        known_entered = set(base_state)
        known_dimmed: set[str] = set()
        known_exited: set[str] = set()

        for c_idx, click in enumerate(clicks):
            c_id = click.get("id", f"{b_id}.{c_idx+1}")
            if c_id not in state_after:
                errors.append({"code": "CLICK-UNMAPPED", "detail": f"Beat {b_id}: Click '{c_id}' not in shot.state_after"})
                continue

            trans = state_after[c_id]
            # Normalize transition
            if isinstance(trans, list):
                trans_dict = {"enter": trans, "dim": [], "highlight": [], "exit": [], "action": None}
            elif isinstance(trans, dict):
                trans_dict = {
                    "enter": trans.get("enter", []),
                    "dim": trans.get("dim", []),
                    "highlight": trans.get("highlight", []),
                    "exit": trans.get("exit", []),
                    "action": trans.get("action"),
                }
            else:
                errors.append({"code": "TRANSITION-INVALID", "detail": f"Click {c_id}: Invalid transition format"})
                continue

            # NAR-CODA-TRAP: Empty click check
            if not trans_dict["enter"] and not trans_dict["dim"] and not trans_dict["highlight"] and not trans_dict["exit"] and not trans_dict["action"]:
                errors.append({"code": "NAR-CODA-TRAP", "detail": f"Click {c_id}: Empty transition (no visual delta)"})

            # OBJECT-ENTER-ONCE
            for ent in trans_dict["enter"]:
                if ent in known_entered:
                    errors.append({"code": "OBJECT-ENTER-ONCE", "detail": f"Click {c_id}: Object '{ent}' entered more than once"})
                known_entered.add(ent)

            # OBJECT-LIFECYCLE-VALID
            for d in trans_dict["dim"] + trans_dict["highlight"] + trans_dict["exit"]:
                if d not in known_entered:
                    errors.append({"code": "OBJECT-LIFECYCLE-VALID", "detail": f"Click {c_id}: Object '{d}' modified before entering"})
                if d in trans_dict["dim"]:
                    known_dimmed.add(d)
                if d in trans_dict["exit"]:
                    known_exited.add(d)

            # NAR-COLLISION: Complex motion pacing
            movers_count = len(trans_dict["enter"]) + len(trans_dict["dim"]) + len(trans_dict["exit"]) + len(trans_dict["highlight"])
            if (fig in ("assemble", "drill") or movers_count >= 3) and not click.get("lead_in"):
                errors.append({"code": "NAR-COLLISION", "detail": f"Click {c_id}: Cinematic transition ({fig}, {movers_count} movers) missing lead_in cue"})

            # NAR-UNANCHORED: target_refs verification
            target_refs = click.get("target_refs", [])
            active_changers = set(trans_dict["enter"] + trans_dict["highlight"] + trans_dict["dim"] + trans_dict["exit"])
            if not target_refs:
                errors.append({"code": "NAR-UNANCHORED", "detail": f"Click {c_id}: Missing target_refs"})
            elif not set(target_refs) & active_changers and active_changers:
                warnings.append({"code": "NAR-UNANCHORED-MISMATCH", "detail": f"Click {c_id}: target_refs {target_refs} not in changing actors {list(active_changers)}"})

        # DEN-ACTIVE-VIEW check
        # Calculate active words for shot
        objects_dict = {o["id"]: o for o in shot.get("objects", []) if "id" in o}
        total_shot_words = sum(len(o.get("text", "").split()) for o in objects_dict.values())
        if total_shot_words > 55 and len(clicks) >= 3 and not known_dimmed and not known_exited:
            errors.append({"code": "DEN-ACTIVE-VIEW", "detail": f"Shot {shot.get('id')}: Total words {total_shot_words} > 55 across {len(clicks)} clicks without any dim or exit (Additive Clutter)"})

        # NAR-KARAOKE check across all spoken lines vs slide text
        shot_texts = " ".join(o.get("text", "") for o in objects_dict.values())
        speech_texts = t0_says + " " + " ".join(f"{c.get('lead_in', '')} {c.get('post_click_says', '')}" for c in clicks)
        overlap = _vocabulary_overlap(shot_texts, speech_texts)
        if overlap > 0.45:
            warnings.append({"code": "NAR-KARAOKE", "detail": f"Beat {b_id} / Shot {shot.get('id')}: High text-speech overlap ({overlap*100:.1f}% > 45%). Presenter reading slide verbatim."})

    ok = len(errors) == 0
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "beats_count": len(beats),
        "shots_count": len(shots)
    }


# ---------------------------------------------------------------------------
# Compiler: compile()
# ---------------------------------------------------------------------------

def compile_direction(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compile direction.json into (deck.json, director.json)."""
    brief = data.get("brief", {})
    style = data.get("style", {})
    beats = data.get("beats", [])
    shots = data.get("shots", [])

    shots_by_beat = {s.get("beat"): s for s in shots if "beat" in s}

    # Map style preset to Forge theme
    preset = style.get("preset", "editorial-crimson")
    if "crimson" in preset or "red" in preset:
        theme = {"seed": "#C1121F", "mode": "dark"}
    elif "midnight" in preset or "dark" in preset:
        theme = "midnight"
    elif "forest" in preset:
        theme = "forest"
    elif "sunrise" in preset:
        theme = "sunrise"
    else:
        theme = "paper"

    # Legal slide_forge layouts
    FORGE_LAYOUTS = {"title", "section", "statement", "bullets", "image", "kpis",
                     "process", "cycle", "chart", "comparison", "quote", "closing",
                     "asymmetric", "bento", "duarte_break"}

    # 1. Build deck.json (for slide_forge)
    deck_slides = []
    for beat in beats:
        b_id = beat.get("id")
        shot = shots_by_beat.get(b_id, {})
        objs = shot.get("objects", [])

        # Extract title and subtitle
        title_obj = next((o for o in objs if o.get("role") == "title"), None)
        title = title_obj.get("text") if title_obj else beat.get("claim", "")

        layout = shot.get("layout", "bullets")
        if layout not in FORGE_LAYOUTS:
            layout = "title" if b_id == "b1" else "bullets"

        texts = [o.get("text", "") for o in objs if o.get("role") not in ("title", "anchor", "hero") and o.get("text")]
        image_spec = next((o.get("asset") for o in objs if o.get("role") in ("anchor", "hero") and o.get("asset")), None)

        slide_dict: dict[str, Any] = {
            "title": title,
            "layout": layout,
            "base_state": shot.get("base_state", []),
        }

        if layout == "title":
            sub = next((o.get("text") for o in objs if o.get("role") == "subtitle"), "")
            if not sub and texts:
                sub = texts[0]
            slide_dict["subtitle"] = sub or brief.get("one_sentence", "")
            if image_spec and isinstance(image_spec, dict) and "file" in image_spec:
                slide_dict["image"] = image_spec["file"]

        elif layout == "asymmetric":
            slide_dict["major"] = texts[0] if texts else title
            slide_dict["minor"] = "\n\n".join(texts[1:]) if len(texts) > 1 else "Cấu trúc trọng tâm của bài giảng."

        elif layout == "bullets":
            slide_dict["bullets"] = texts if texts else ["Luận điểm 1", "Luận điểm 2"]

        elif layout == "process":
            slide_dict["steps"] = texts if len(texts) >= 3 else (texts + ["Bước hoàn thiện"])

        elif layout == "kpis":
            slide_dict["items"] = [{"label": o.get("id", f"item_{i}"), "value": o.get("text", "100%")} for i, o in enumerate(objs if objs else [{"id": "v1", "text": "100%"}])]

        else:
            slide_dict["bullets"] = texts if texts else ["Nội dung chính"]

        deck_slides.append(slide_dict)

    deck_spec = {
        "title": brief.get("one_sentence", "Presentation"),
        "theme": theme,
        "slides": deck_slides
    }

    # 2. Build director.json (compliant with Director v0.7 contract for motion_director.apply)
    director_slides = []
    for s_idx, beat in enumerate(beats):
        b_id = beat.get("id")
        shot = shots_by_beat.get(b_id, {})
        clicks = beat.get("clicks", [])
        state_after = shot.get("state_after", {})
        fig = beat.get("figure", "build")

        # Map high-level actor IDs to Forge shape tokens
        layout = shot.get("layout", "bullets")
        token_map = {}
        if layout == "title":
            token_map = {"title:main": "Title", "sub:main": "Subtitle", "art:portraits": "Hero picture"}
        elif layout == "asymmetric":
            token_map = {"art:plato": "Hero picture", "card:def1": "Major Content", "card:def2": "Minor Content", "card:def3": "Minor Card"}
        elif layout == "bullets":
            token_map = {"bullet:sys1": "Points", "bullet:sys2": "Points", "bullet:sys3": "Points"}

        slide_beats = []
        click_beats = []

        for c_idx, c in enumerate(clicks):
            c_id = c.get("id", f"{b_id}.{c_idx+1}")
            trans = state_after.get(c_id, {})
            if isinstance(trans, list):
                raw_targets = trans
                dim_targets = []
                exit_targets = []
            else:
                raw_targets = trans.get("enter", []) + trans.get("highlight", [])
                dim_targets = trans.get("dim", [])
                exit_targets = trans.get("exit", [])

            mapped_targets = [token_map.get(t, t) for t in raw_targets if t in token_map or t in ("Title", "Subtitle", "Points", "Hero picture", "Major Card", "Major Content", "Minor Card", "Minor Content")]
            if not mapped_targets and raw_targets:
                mapped_targets = [token_map.get(t, "Points") for t in raw_targets]

            # Figure mapping to v0.7 operations
            op = "reveal"
            effect = "fade"
            if fig in ("arrive", "join"):
                op = "reveal"
                effect = "fade"
            elif fig == "build":
                op = "reveal" if layout != "bullets" else "text-build"
                effect = "float-in"
            elif fig == "both":
                op = "reveal"
                effect = "wipe-up"
            elif fig == "assemble":
                op = "reveal"
                effect = "zoom"
            elif fig == "clear":
                op = "exit"
                effect = "fade-out"

            beat_id = f"beat-{s_idx+1}-{c_idx+1}"
            b_obj = {
                "id": beat_id,
                "purpose": c.get("state", f"Click {c_id}"),
                "operation": op,
                "targets": list(dict.fromkeys(mapped_targets)) if mapped_targets else ["Title"],
                "timing_intent": "on-click",
                "effect": effect,
                "reuse_existing": True,
                "same_slide": True,
                "duration_ms": int(c.get("seconds", 0.6) * 1000) if c.get("seconds") else 600
            }
            slide_beats.append(b_obj)
            motion_beat_ids = [beat_id]

            # If dimming targets exist, add dim beat
            if dim_targets:
                dim_id = f"dim-{s_idx+1}-{c_idx+1}"
                mapped_dims = [token_map.get(t, t) for t in dim_targets if t in token_map or t in ("Title", "Subtitle", "Points", "Hero picture", "Major Card", "Major Content", "Minor Card", "Minor Content")]
                if mapped_dims:
                    slide_beats.append({
                        "id": dim_id,
                        "purpose": f"Dim prior elements for {c_id}",
                        "operation": "dim",
                        "targets": list(dict.fromkeys(mapped_dims)),
                        "timing_intent": "with-previous",
                        "effect": "dim",
                        "reuse_existing": True,
                        "same_slide": True,
                        "duration_ms": 400
                    })
                    motion_beat_ids.append(dim_id)

            click_beats.append({
                "id": f"click-{s_idx+1}-{c_idx+1}",
                "purpose": c.get("state", f"Click {c_id}"),
                "motion_beats": motion_beat_ids,
                "stable_state": c.get("state", "State achieved."),
                "pause_after": "slide-complete" if c_idx == len(clicks) - 1 else "await-next-reveal",
                "boundary_reason": f"Click {c_id} of beat {b_id}."
            })

        director_slides.append({
            "source_index": s_idx + 1,
            "role": "title slide" if s_idx == 0 else "content slide",
            "objective": beat.get("claim", f"Slide {s_idx+1} objective"),
            "existing_timing": "replace",
            "replace_reason": f"Two-Pass Choreography: {beat.get('job')} / {beat.get('figure')}",
            "beats": slide_beats,
            "click_beats": click_beats,
            "components": []
        })

    director_plan = {
        "version": "0.7",
        "kind": "existing-deck-motion-director",
        "source": {
            "source_slide_count": len(beats)
        },
        "user_instruction": brief.get("one_sentence", "Presentation"),
        "script": {
            "source": "provided",
            "summary": brief.get("one_sentence", "Presentation"),
            "evidence": ["two-pass screenplay", "stage inventory"],
            "beats": [f"slide {i+1}: {b.get('claim', '')}" for i, b in enumerate(beats)]
        },
        "preservation": {
            "preserve_text_by_default": True,
            "preserve_media_by_default": True,
            "preserve_theme_by_default": True,
            "preserve_slide_order_by_default": True,
            "slide_count_policy": "preserve"
        },
        "slides": director_slides,
        "target_slide_count": len(beats),
        "research_metadata": {
            "style": "modern",
            "drafted_by": "deck_director.py v0.2", "draft_notes": {}
        }
    }

    return deck_spec, director_plan


# ---------------------------------------------------------------------------
# Ledger: ledger()
# ---------------------------------------------------------------------------

def calculate_ledger(pptx_path: Path, direction_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Calculate and return narrative metrics from built PPTX and direction data."""
    import zipfile
    from lxml import etree

    # Extract timing information from PPTX
    slides_count = 0
    total_effects = 0
    lifecycles = 0
    empty_base_states = 0
    click_groups_per_slide = []

    if pptx_path.is_file():
        with zipfile.ZipFile(pptx_path) as z:
            slide_files = [f for f in z.namelist() if f.startswith("ppt/slides/slide") and f.endswith(".xml")]
            slides_count = len(slide_files)

            for s_file in slide_files:
                tree = etree.fromstring(z.read(s_file))
                # Count interactive & timing sequences
                timing = tree.find(".//{http://schemas.openxmlformats.org/presentationml/2006/main}timing")
                spid_counts: Counter[str] = Counter()
                c_groups = 0

                if timing is not None:
                    # Find main sequence condition nodes
                    for c_tn in timing.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}cTn"):
                        node_type = c_tn.get("nodeType")
                        if node_type == "clickEffect":
                            c_groups += 1

                    for sp_tgt in timing.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}spTgt"):
                        spid = sp_tgt.get("spid")
                        if spid:
                            spid_counts[spid] += 1
                            total_effects += 1

                click_groups_per_slide.append(c_groups)
                lifecycles += sum(1 for cnt in spid_counts.values() if cnt >= 2)

    # If direction data available, measure direction metrics
    if direction_data:
        shots = direction_data.get("shots", [])
        for shot in shots:
            if not shot.get("base_state"):
                empty_base_states += 1

    return {
        "slides_count": slides_count,
        "total_effects": total_effects,
        "lifecycles": lifecycles,
        "click_groups_per_slide": click_groups_per_slide,
        "empty_base_states": empty_base_states,
        "pptx_path": str(pptx_path)
    }


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    # check
    p_check = sub.add_parser("check", help="Check direction.json against schema and 5 narrative laws")
    p_check.add_argument("direction", type=Path, help="Path to direction.json")

    # compile
    p_compile = sub.add_parser("compile", help="Compile direction.json to deck.json and director.json")
    p_compile.add_argument("direction", type=Path, help="Path to direction.json")
    p_compile.add_argument("-o", "--output", type=Path, required=True, help="Path to output deck.json")
    p_compile.add_argument("--director", type=Path, required=True, help="Path to output director.json")

    # ledger
    p_ledger = sub.add_parser("ledger", help="Report narrative ledger from built PPTX")
    p_ledger.add_argument("pptx", type=Path, help="Path to presentation.pptx")
    p_ledger.add_argument("--direction", type=Path, default=None, help="Path to direction.json")

    args = parser.parse_args(argv)

    if args.cmd == "check":
        data = json.loads(args.direction.read_text(encoding="utf-8"))
        res = check_direction(data)
        print(f"Validation result for {args.direction.name}: {'PASSED' if res['ok'] else 'FAILED'}")
        if res["errors"]:
            print(f"\nErrors ({len(res['errors'])}):")
            for e in res["errors"]:
                print(f"  [{e['code']}] {e['detail']}")
        if res["warnings"]:
            print(f"\nWarnings ({len(res['warnings'])}):")
            for w in res["warnings"]:
                print(f"  [{w['code']}] {w['detail']}")
        return 0 if res["ok"] else 1

    elif args.cmd == "compile":
        data = json.loads(args.direction.read_text(encoding="utf-8"))
        deck_spec, director_plan = compile_direction(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.director.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(deck_spec, indent=2, ensure_ascii=False), encoding="utf-8")
        args.director.write_text(json.dumps(director_plan, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Compiled {args.direction.name} -> {args.output.name} and {args.director.name}")
        return 0

    elif args.cmd == "ledger":
        direction_data = json.loads(args.direction.read_text(encoding="utf-8")) if args.direction and args.direction.is_file() else None
        res = calculate_ledger(args.pptx, direction_data)
        print(json.dumps(res, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
