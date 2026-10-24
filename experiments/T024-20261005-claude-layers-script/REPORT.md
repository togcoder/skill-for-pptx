# T024 — Motion layers and the script layer

## Frozen input

- Owner request (2026-10-05, after the T022/T023 merge, PR #25). The owner
  wanted more complex motion with secondary and background effects on top of
  the main effect. The owner also wanted stronger script writing in three
  cases: following the user's request, following an existing presentation
  script, and writing a full script when the user supplies too little.
- Claude Code cloud session. The branch `claude/blissful-pasteur-gmll59` was
  restarted from main `bb82c70` (see `base-commit.txt`).
- Codex T021 (PR #24) still has only its claim; nothing here touches it.
- Hypotheses:
  1. Secondary and ambient motion can be built from native effects. Loops are
     repeatCount with autoRev and "until next click". Helper shapes are
     generated in the deck's own style. Neither should break primary motion
     or preservation.
  2. A script can drive the timing of the director's own choreography: the
     script says *when*, the draft says *how*. This works for verbatim,
     paraphrased (Vietnamese) and missing scripts.

## What was built

| Area | File | Content |
|---|---|---|
| Loops | `pptx_animator.py` | `loop` on effects: `repeatCount` (indefinite or N×1000), `autoRev`, "until next click" via `endCondLst` onNext; an after-previous block waits one cycle, never forever |
| Layers | `motion_engine.py` | ambient recipes `breathe`, `drift`, `spin-loop`; secondary `ripple`; spotlight `halo` follower; `attach` followers (a separate label follows and scales with its shape); `overshoot` and `anticipate` keyframes; loops simulated as moving, then at rest for stable states; XML reader understands loops |
| Components | `motion_components.py` (new) | `halo`, `orbit-ring`, `track-line`, `backdrop` (inserted behind all source shapes) and `token`, `callout`, `badge`, `highlight-frame`, `arrow` (on top); deck accent colour and font; named `__gen_<kind>_<id>` with a description |
| Director v0.7 | `motion_director.py`, `validate_director_plan.py` | `layer` (primary, secondary, ambient); generated components inserted before compile; guard blocking motion on a property that is already looping; cinematic draft adds orbit ring + slow spin + halo tour for loops (not for 2×2 grids), rail + token for walked processes (reusing an existing token when the deck has one), `--ambient` backdrops with drift; first-slide title rule narrowed (≤4 texts) |
| Script | `motion_script.py` (new) | parser (slide headings by number or title, `[click]`/`[nhấp]`/`[bấm]`/`>>` cues, intro text); weighted, accent-insensitive alignment (rare words weigh more, two-way overlap for long paragraphs, short labels keep stopwords); draft click bundles retimed by the script (first mention reveals, later mention focuses, a line naming nothing new releases a tour, paraphrased cued lines take the next bundle in reading order); gaps (missing numbers, clicks with no visual) and `--fill-gaps` callouts; complete script generation (`draft`); presenter script `OUT.script.md`; `--write-notes` appends `[Motion script]` and `[Click n]` to notes, creating notes slides from the notes master |
| CLI | `motion_director.py` | `auto --script`, `--fill-gaps`, `--write-notes`, `--ambient`; `verify(allow_notes=True)` |

## Reproduction

Python 3.11.15, lxml 6.1.3, LibreOffice 24.2.7.2 Impress, poppler, ImageMagick 6. No PowerPoint.

```bash
python3 scripts/motion_director.py auto tests/fixtures/motion_showcase_deck.pptx -o output/T024_showcase_scripted.pptx \
  --script tests/fixtures/showcase_script.md --style cinematic --fill-gaps --write-notes
python3 scripts/motion_director.py auto tests/fixtures/report_deck.pptx -o output/T024_report_cinematic_ambient.pptx \
  --style cinematic --ambient --write-notes
python3 scripts/motion_director.py auto tests/fixtures/essay_outline_deck.pptx -o output/T024_essay_vi_scripted.pptx \
  --script tests/fixtures/essay_script_vi.md --fill-gaps --style cinematic
python3 scripts/motion_script.py draft tests/fixtures/report_deck.pptx -o report_generated_script.md --style cinematic
python3 scripts/motion_director.py preview <output> --slide N -o preview/<name>-sN.gif --sheet preview/<name>-sN.png
```

| File | SHA-256 |
|---|---|
| `output/T024_showcase_scripted.pptx` | `81a932f9f56420e3d4b422409c32cb4f8efbbfe38f11ced9dde0260ab21dbb09` |
| `output/T024_report_cinematic_ambient.pptx` | `2e8d4e4d9ec61e1700fa1ca0f2238f3d263d8f4373a175658dab975b6d13cbab` |
| `output/T024_essay_vi_scripted.pptx` | `f0261ec5e284cf0f52bb94ef7f99d7684c175160733d78c953cd794c3c534664` |

## Evidence

### Script-driven showcase (`showcase_script.md`, written like a human presenter)

The script for slide 2 introduces the cycle, then says Plan, Do, Check, Act,
then "And then the cycle starts again". The plan follows it exactly:

- assemble with the orbit ring and its slow spin;
- a spotlight with halo on Plan, then Do, Check and Act;
- release plus the halo fading out on the last line.

The 85% the script mentions is reported as a number that is not on the slide.

Slide 5 reuses the deck's own "Order token": one stop per line, and "Pack and
deliver" moves two stops in a single click.

Slide 6 spotlights the quadrant the line names first ("Explore"). The 2×2
grid gets a halo tour but no orbit ring.

Notes were written for slides 2, 5 and 6. Slide 6 had no notes, so a notes
slide was created from the master; the original notes on the other slides are
kept above `[Motion script]`.

### Vietnamese paraphrase (`essay_script_vi.md`)

| Slide | Result |
|---|---|
| 2 | Two alternatives on two clicks, label and text together |
| 3 | Claim paragraph, then counter-paragraph. The new fact "giảm tới 5 độ" is not on the slide, so it becomes a generated callout (`--fill-gaps`, provenance user-provided) |
| 4 | A fully paraphrased line takes the next paragraph by order (`placed-by-order`) |

Before the weighted scoring this deck produced three wrong callouts and a
merged click. Those were caught by inspection and fixed, and the fix is
covered by tests.

### Generated full script

`report_generated_script.md` is a complete click-by-click script drafted from
the deck in its language, written for an AI to rewrite. Feeding it back
(`script plan`) reproduces the draft's click rhythm exactly: 4/3/2/5/3 clicks
on slides 2/3/4/5/7 (unit test).

### Layers in the previews (`preview/*.png`, `*.gif`; simulated)

- Showcase slide 2: dashed orbit ring behind the cycle, halo gliding from
  stage to stage, dimmed stages restored at the end.
- Report slide 5 (cinematic + ambient): drifting backdrops start with the
  slide (auto group); a rail is laid; the token travels with overshoot to each
  step as it appears; the result line follows.

### Independent importer (`lo-*.json`)

LibreOffice loads all three outputs.

| Output | Emphasis | Motion paths | Entrances | Exits |
|---|---|---|---|---|
| Showcase | 35 | 28 | 16 | 1 |
| Report | 4 | 18 | 32 | 0 |

### Checks

- `verify` passes on every output; with `allow_notes` it passes after notes
  are written.
- Unexpected new objects (any name other than `__gen_`/`__counter_`) still
  fail verification.
- The loop guard blocks a later rotation of the spinning ring.

The following bugs were found during the run and fixed:

- verify mistook generated shapes for counter proxies;
- an unused halo was added on slides without a tour;
- the preview sampled a 40-second loop in full, because the XML reader
  ignored `repeatCount`;
- "Do" was dropped as a stopword;
- the release landed on the same click as the last spotlight;
- a token was duplicated when the deck already had one;
- callouts overflowed their text;
- text-only first slides were treated as title slides too broadly.

### Smoke and tests

`auto --style cinematic --ambient` was run on every repository deck. All pass,
with 0 warnings. Morph-state decks animate only their first state; later
states continue by Morph.

**205 tests pass**: 190 earlier plus 15 in `tests/test_layers_and_script.py`.

Native playback: null.

## Limitations

- **PowerPoint semantics are still unobserved.** This now also covers
  `repeatCount`/`autoRev`/`endCondLst` for loops and how a halo's gradient
  renders.
- **Alignment is lexical.** It uses weighted tokens, not meaning. Heavy
  paraphrase falls back to reading order, and a line that is cued but empty
  needs `--fill-gaps` or it only adds narration.
- **Notes need a notes master.** Decks without one, such as python-pptx
  defaults, skip notes; the result reports which slides were skipped.
- **Generated components appear in static views.** They show in edit view
  and in PDF export, as the halo does at its first anchor.
- **Some recipes are never proposed by the draft.** The script layer retimes
  draft bundles only, so `swap` and `zoom-focus` must be authored in the
  director plan.

## Next

1. Native gate: play `output/T024_showcase_scripted.pptx` and compare with
   `preview/*.png`. Check loop playback, halo glide and travel overshoot.
   Open Presenter View to confirm the notes.
2. Add a semantic matcher (LLM-assisted alignment) behind the lexical one,
   keeping the lexical result as a check.
3. Let scripts request recipes explicitly, e.g. `[click: swap A B]`.
