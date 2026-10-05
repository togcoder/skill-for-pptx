# T023 — Compound motion engine for existing decks

## Frozen input

- Owner request (2026-10-05): after T019/T022, take a large step into complex
  motion so the project is ready to operate.
- Claude Code cloud session. Branch `claude/blissful-pasteur-gmll59`. The base
  commit is in `base-commit.txt` (T022 on top of main 09ba641).
- Coordination: Codex claimed T021 ("compound motion and reasoning audit",
  draft PR #24). Only the claim was pushed, with no code. T023 keeps to the
  existing-deck Director path (files `motion_engine.py`, `motion_preview.py`,
  `motion_director.py`) and does not touch the T021 branch. T021 can consume
  the engine API or replace parts of it after review.
- Hypothesis: compound choreography on existing objects can be expressed as
  keyframe tracks and compiled into ordinary native PowerPoint effects with
  exact delays, while state is carried across clicks. Examples: assemble, walk
  a cycle with spotlight, swap, travel, zoom-in, and Morph between slides. A
  simulator using the same semantics can then preview and check the result
  before any PowerPoint is available.

## What was built

| Layer | File | Content |
|---|---|---|
| Writer | `pptx_animator.py` | `grow` (Grow/Shrink with a `by` ratio), layout-anchored motion paths with cubic Bézier curves, per-effect accel/decel, Transparency in PowerPoint's set→animEffect order, Morph transition with a Fade fallback (`mc:AlternateContent`) |
| Engine | `motion_engine.py` | keyframe tracks → effects; recipes `assemble`, `disperse`, `spotlight`, `release`, `cycle`, `swap`, `travel`, `zoom-focus`; state simulation; XML → effects reader for any deck; conflict check; occlusion and off-slide checks |
| Director | `motion_director.py` | Director v0.6 `choreography` beats and deck-level `transitions`; state carried through existing timing and earlier clicks; plan-based initial visibility; detection of cycle and hub diagrams; `cinematic` style; Morph detection with continuity (a continuing object is not re-entered); `preview` command; graceful "nothing to add" |
| Preview | `motion_preview.py` | samples the timeline, writes frame slides into one temporary deck, renders it once with LibreOffice, then builds a GIF and a key-state sheet |
| Validator | `validate_director_plan.py` | v0.6 recipe and target-count rules, keyframe keys, transition reasons; charts may be moved or dimmed by choreography but never built by it |

## Reproduction

Python 3.11.15, lxml 6.1.3, LibreOffice 24.2.7.2 Impress, poppler, ImageMagick 6. No PowerPoint.

```bash
python3 scripts/make_motion_fixture.py                      # dev-only (python-pptx, Pillow)
python3 scripts/motion_director.py draft tests/fixtures/motion_showcase_deck.pptx -o auto-cinematic-plan.json --style cinematic
python3 scripts/motion_director.py apply tests/fixtures/motion_showcase_deck.pptx directed-plan.json -o output/T023_showcase_directed.pptx
python3 scripts/motion_director.py preview output/T023_showcase_directed.pptx --slide N -o preview/slide-0N.gif --sheet preview/slide-0N.png
python3 scripts/lo_timing_crosscheck.py output/T023_showcase_directed.pptx --output lo-crosscheck-directed.json
python3 scripts/render_identity.py tests/fixtures/motion_showcase_deck.pptx output/T023_showcase_directed.pptx
```

| File | SHA-256 |
|---|---|
| `tests/fixtures/motion_showcase_deck.pptx` | `536575cc74cedb9682a978c669650a495cf23209c802beb6844701a760723522` |
| `output/T023_showcase_directed.pptx` | `0c589e41d065384860152a68a79170fc8d73e1dcee99b56c0792f0faf4904b6a` |
| `output/T023_showcase_auto_cinematic.pptx` | `435fd9f5ddce8983b4a0353667bbda224f97abaa19031450b0ef536108e3946b` |

## Evidence

### Autonomous draft (`--style cinematic`, no instructions)

- Slide 2 (PDCA around a hub) is detected as a cycle; reading order is
  measured in true slide proportions. The plan is: hub + `assemble` from the
  centre, then `spotlight` on Plan → Do → Check → Act (one click each), then
  `release`. That is 6 clicks.
- Slide 3 (hub + 6 partners): `assemble` only. Above 5 members a tour would
  tire the audience.
- Slide 6 (2×2 matrix) is also detected as radial: assemble + spotlight tour.
- Slide 7→8: the same picture moves and shrinks, so a Morph is proposed. The
  picture is not re-entered on slide 8, and slide 7 (a picture alone) stays
  static.

### AI-directed plan (`directed-plan.json`, edited from the draft)

| Slide | Choreography | Meaning |
|---|---|---|
| 2 | assemble → spotlight ×4 → release | walk the improvement cycle |
| 3 | assemble; then raw `tracks`: Cafés and Grocers curve closer and grow | shift to direct channels |
| 4 | three reveals → `swap` Sustainability ↔ Cost on opposite arcs | priorities re-ranked |
| 5 | steps + token appear → `travel` token to each step, one click per stop, the stop pulses | follow one order |
| 6 | assemble → `zoom-focus` Grow (others exit) → `release` | drill into one quadrant |
| 8 | Morph in; bullets one per click | the roastery photo carries over |

The first version of this plan raised two warnings from the engine: "'Partner
Cafés' now covers 'Platform'" and "'Quadrant Grow' now covers 'Title 1'". Both
were real. The plan was fixed with a smaller offset and a zoom centre below the
title (new `x`/`y` parameters), and the final report has 0 warnings and passes
structural checks.

### Independent importer (`lo-crosscheck-directed.json`)

LibreOffice recognises every new effect class: `motion-path` (24),
`ooo-emphasis-grow-and-shrink` (16), `ooo-emphasis-transparency` (12),
`ooo-exit-fade-out` (3), and the entrance presets including fade-in-and-zoom.
On slide 5 the stop pulses begin at 0.7 s, inside the travel click. Chained
travel paths continue: each path's `M` point equals the previous path's end
(for example `M 0.116253 -0.12 C …`).

### Simulated preview (`preview/`)

GIFs and key-state sheets for slides 2–6 were viewed. They show the PDCA
spotlight tour, the curved channel shift, the swap, the token journey and the
zoom-in and release. The swap's mid-frames show the two bars passing over
"Speed". This is acceptable for a re-ranking, and the effect would not be
visible in click end states. The preview simulates the engine's semantics; it
is not PowerPoint playback.

### Preservation and statics

`render_identity.py` gives 8/8 slides RGB-identical to the source, so timing
and transitions did not change the authored layout. Only slide XML parts
changed.

### Operational smoke test

`auto` was run with `modern` and `cinematic` on every PPTX in the repository:
27 decks, including old Morph-state decks and fully animated decks.

- Before fixes, fully animated decks crashed ("slides must be nonempty").
  `auto` now reports "Nothing to add" and writes no file.
- Before fixes, Morph-state decks (T005, 12 slides) received 88 entrance
  clicks, which re-entered objects that should glide in by Morph. Objects
  shared with the previous slide are now kept static whenever a Morph
  (existing or new) brings the slide in.
- Every other deck passes structural checks with 0 warnings.

### Tests

`tests/test_compound_motion.py` adds 14 tests: anchored chaining and
continuity, compounding scale and rotation, cycle end positions, spotlight →
zoom → release restore, conflict and layout checks, writer XML,
XML-reader round trip, cycle and Morph detection, directed apply, validator
rules, a blocking conflict, and preview. The full suite has **190 tests**, all
passing.

Native playback: null.

## Limitations and decision

- **Native semantics are assumed, not observed.** Chained paths assume
  layout-anchored offsets with hold (the T006 "anchored-hold" hypothesis).
  Grow/Shrink `by` is assumed to compound, and a later Transparency is assumed
  to override an earlier one. If PowerPoint behaves otherwise, the fix is
  local to `anchored_path_string`, the `grow` ratio, or the `dim` restore.
- **Radial detection is approximate.** It requires self-contained shapes with
  text inside. Labels drawn as separate objects are not detected, because
  tracks would separate them from their shapes. Group-aware tracks are future
  work.
- **No transient occlusion check.** Overlap is checked only at stable states;
  the GIF is the tool for mid-motion overlap.
- **Morph matching is left to PowerPoint.** Objects are not renamed with `!!`,
  so names stay preserved.

Decision: the engine becomes part of the product path (the skill now
documents v0.6). Earlier writers stay frozen.

## Next

1. On Windows PowerPoint, play `output/T023_showcase_directed.pptx`. For each
   click, compare against `preview/*.png` and record whether chained paths
   continue (anchored hypothesis), whether Grow compounds, whether Transparency
   restores, whether Morph glides the photo, and any repair prompt.
2. Add group-aware tracks (move a shape together with its separate label).
3. Add a transient collision sampler to `verify` if the GIF review proves
   insufficient.
