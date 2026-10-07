---
name: slide-forge
description: Build a finished, motion-directed PowerPoint deck from a topic, brief, outline or document — native editable shapes, measured text fitting, on-theme art, chart/KPI/process/cycle choreography, Ken Burns pictures, accent motion graphics and Morph between slides — then self-check it with machine-readable QA and a real PowerPoint render. Use whenever the user wants a new presentation, slides or a deck (not just animation for a deck they already have), especially when they expect it polished, animated or "presenter-ready".
---

# Slide Forge

You are the deck author and the art director. Forge is the compiler: you write
a semantic spec, it does layout, typography, art, motion and checks. You never
place coordinates or pick animation effects by hand.

`ROOT=<this skill dir>/../..`. Needs Python 3 with `python-pptx`, `lxml` and
`Pillow`. The render step needs Windows with desktop PowerPoint and `ffmpeg`.

## Loop

1. **Story first.** Before writing JSON, decide the deck's argument: opening
   state, problem, evidence, comparison, conclusion and action. One idea per
   slide. Put the evidence before the takeaway.
2. **Spec.** Run `python3 $ROOT/scripts/slide_forge.py schema`, then write
   `deck.json`. Choose the layout from what the content *is* (table below),
   not from variety for its own sake.
3. **Build.** Run `python3 $ROOT/scripts/slide_forge.py build deck.json -o deck.pptx`.
   It prints a JSON verdict.
4. **Repair.** For each entry in `errors`, apply its `fix` to the spec, never to
   the PPTX, and rebuild. Read `warnings`: `TEXT_SHRUNK` means the copy is long
   for the layout. Tighten the words instead of accepting tiny type. Stop when
   `ok` is true.
5. **Look.** If PowerPoint is available, run
   `python3 $ROOT/scripts/slide_forge.py render deck.pptx -d render/` and read
   every `render/slide-NN.png` strip (6 frames across the slide's motion).
   Check:
   - Hierarchy reads at a glance.
   - Nothing wraps badly or collides mid-motion.
   - Every slide has life.
   - The deck feels like one design.
   Fix the spec and rebuild.
6. **Deliver.** Give the PPTX path, one line per slide (layout and what moves),
   the generated-art list and an honest status. "Rendered by PowerPoint
   CreateVideo" is true only after step 5. Interactive click playback is not
   verified.

## Choosing layouts

| Content | Layout | Motion you get |
|---|---|---|
| Opening | `title` (+`image` or generated art) | accent draws in, picture Ken Burns |
| Chapter break | `section` | accent draws in |
| One big claim | `statement` | bar draws, claim lands |
| 2–6 short points (+ picture) | `bullets` | one point per click; picture reveals then drifts |
| A picture that is the message | `image` | Ken Burns from slide start |
| 1–4 headline numbers | `kpis` | cards one per click, numbers count up |
| Numbers over categories/time | `chart` (+`takeaway`) | series build, then the takeaway |
| 3–6 ordered steps | `process` | steps and arrows; sequence words in `notes` give one click per step |
| 3–6 stages that loop | `cycle` (+`center`) | parts assemble, spotlight tour, release |
| A vs B | `comparison` | one side per click |
| Voice of a customer/expert | `quote` | quote then attribution |
| Ending / ask | `closing` | title, accent, subtitle |

## Writing rules

- **Words:**
  - Titles ≤ 8 words.
  - Bullets ≤ 12 words each, never full paragraphs.
  - KPI values short (`48%`, `1,200 t`, `2.1 days`), with the label carrying the meaning.
- **Notes:** speaker notes drive rhythm. "First…, then…, finally…" (or
  "đầu tiên…, sau đó…, cuối cùng…") makes a process advance one step per
  click.
- **Pictures:**
  - Use real files the user supplied or you are allowed to use.
  - `{"generate": "..."}` makes abstract on-theme art, never a stand-in for a
    factual photo. Say it is generated.
- **Data:** never invent figures. With no data, use layouts that don't need it
  or label the data as illustrative, the way the examples do.
- **Theme:** `midnight`, `paper`, `forest` and `sunrise` pass WCAG AA for every
  text role. A custom theme object must keep `text`/`muted`/`accent` ≥ 4.5:1
  on `bg` and `surface`; QA enforces it.
- **Motion styles:**
  - `modern` is the default.
  - `cinematic` uses bolder zooms and float-ins.
  - `subtle` keeps pictures alive but leaves accents still.
  - `motion.morph` (default true) glides two background orbs between slides. Turn it off for very formal decks.

## QA codes

| Code | Severity | Meaning / fix |
|---|---|---|
| `TEXT_OVERFLOW`, `WORD_BREAK` | error | copy does not fit, or a word is wider than its box: shorten |
| `TEXT_COLLISION`, `OFF_SLIDE` | error | geometry problem: usually too much content for the layout |
| `LOW_CONTRAST` | error | custom colours too weak |
| `MOTION_APPLY` | error | the Director could not compile a slide; report it |
| `TEXT_SHRUNK`, `TYPE_TOO_SMALL` | warning | dense copy |
| `PICTURE_FROZEN`, `MOTION_NONE` | warning | a slide or picture without motion |
| `MOTION_WARNING` | warning | a stable state looks off (occlusion/off-slide): check the render |

`forge_qa.py` also works on any PPTX: `slide_forge.py qa deck.pptx`.

## Existing decks

For a deck the user already has, use the `pptx-motion-director` skill. Forge
is for new decks. Its output is still a normal PPTX, so the Director can refine it later.
