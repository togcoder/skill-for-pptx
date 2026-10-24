# T034 — One design system for beauty and technique; documentation standardised

## Frozen input

- **Request.** On 2026-10-19 the owner asked to standardise the
  documentation to the latest research, to research consolidation further,
  and to unify aesthetics and technique.
- **Base.** The research tip `work/T033-argon-morph-staging` @ `d57f4a1`
  (`base-commit.txt`) is 18 commits ahead of `main` (`bb82c70`). It contains
  integrate/20261008 (T024 layers + T028 + T024-picture…T027), T029 tokens,
  T030 palette, T031 critique (WIP), the Argon import, T032 and T033. The
  branch `claude/blissful-pasteur-gmll59` was fast-forwarded to it; no other
  branch was modified.
- **Environment.** Claude Code cloud session: Python 3.11.15, lxml 6.1.3,
  Pillow, LibreOffice 24.2.7.2, poppler. No PowerPoint.
- **Network.** arXiv and most university hosts are blocked by the sandbox
  network policy. Papers were read through search-engine summaries and
  abstract pages; the sources table marks what was not read in full.

### Hypotheses

1. The aesthetic rules (craft catalog, tokens, knowledge base, palette,
   critique) and the technical generators disagree in measurable ways. Those
   disagreements produce visible defects that no existing check reports.
2. If generators and checkers read one machine-readable design system:
   - the critic can grade any deck against the same numbers the generators
     use;
   - "generator output passes the critic" becomes testable;
   - fixing a generator shows up as fewer findings on the same inputs.
3. Computed metrics (not an LLM judge) are a sound basis, following recent
   benchmarks.

## Audits (three read-only agents, then verified)

| Audit | Main findings | Verified here |
|---|---|---|
| T033 code (`morph_playbook`, `cognitive_pacing`, `interactive_triggers`) | None is wired into a product path. All three write schema-invalid or wrong XML on real decks: `customDur`, `p:by/p:pt`, a second `solidFill`, a misplaced `alphaModFix`. Other defects: Morph chains broken by one-sided renames, dangling picture rels, deleted hyperlinks, global stagger counter, constants without sources. The tests are circular. | The `customDur` schema failure was reproduced against ISO 29500 `pml.xsd`; the director output for the same slide validates. Full report: `experiments/T033-20261016-argon-research/REPORT.md` |
| Aesthetics stack (T027 to T031) | Five easing systems. The assemble regression came from the Argon merge (T029's `enter` + overshoot replaced by the legacy `out`). `deck_style` paints helpers with the card surface, which makes them invisible on dark and brand themes. The simulator used smoothstep, so previews ignored tokens. Three contrast functions, and a 24 pt large-text threshold. Durations disagree across the catalog, styles, recipes and pacing; `travel_ms` was unused. The T031 critique was unwired, untested, and had placeholder/vocabulary bugs. | All reproduced; the fixes are below |
| Documentation | 7 different test counts. `main` is 18 commits behind, and no document says so. HANDOFF/STATUS were append-only logs with 37 sections; T029–T033 had no reports. The director skill claims `pre_stage/post_stage`, which nothing reads. The ID T024 was used three times. Harness docs say "COM not run" although CreateVideo was used. | Spot-checked; acted on in the documentation rewrite |

## What was built

| Area | Change |
|---|---|
| Design system | `knowledge/design_system.json`: bands and limits for motion, rhythm, type, colour, density and layout; 18 rules with evidence, generators and checkers; sources. `scripts/design_system.py` loader. Doc: `docs/DESIGN_SYSTEM.md` |
| Generators read it | **Engine:** assemble arrives with `enter` easing and restored overshoot; explode uses `standard`; overshoot ≤ 0.08 and anticipate ≤ 0.05 are clamped; recipe default comes from `default_ms("move")`; travel hops take `travel_ms(distance)` when the plan gives no duration. **Writer:** default path easing is the `move` role (0.15/0.70, was 0.5/0.5). **Reader:** a missing accel/decel attribute is read as 0, as PowerPoint plays it. **Simulator:** uses PowerPoint's own accel/decel progress (`ppt_progress`) instead of smoothstep. **Director:** chart steps are clamped to the enter band; the ring reveal uses the band maximum; the token journey no longer fixes 650 ms. **Components:** `deck_style(model, background)` picks the most-used deck colour that reaches 3:1, or moves its lightness in OKLCH (`brand_palette`); highlighter tint and opacity are chosen so the text under it keeps WCAG contrast (`marker_tint`). **Contrast:** `forge_qa`, `slide_forge` and `brand_palette` all use `design_system.contrast`; large text follows WCAG 2.2 (≥ 18 pt, or 14 pt bold) |
| Validator | Rejects overshoot/anticipate and `stagger_ms` outside the limits (MOT-OVERSHOOT, MOT-STAGGER) |
| Critic | `scripts/design_critic.py`, with dimensions design, motion, rhythm, coherence and technique. It resolves inherited sizes, colours (theme, colour map, placeholders, master styles, lumMod/lumOff), alpha tints and the background behind each object. It reads click groups and blocks and merges one gesture's segments (move + overshoot settle), doubles `autoRev`, and treats long one-shot drifts as ambient. Optional checks: frame metrics from LibreOffice or PowerPoint renders, choosing the settled frame of a strip; ISO 29500 schema validation. `forge_critique.py` (T031) delegates to it |
| Product wiring | `motion_director.py apply/auto` adds a *Design critique* section (source vs output) and writes `OUTPUT.critique.json`; new `motion_director.py critique`. `slide_forge.py build` verdict gains `critique`. `morph_studio.py apply` report gains `critique` |
| Quarantine | `morph_playbook.py`, `cognitive_pacing.py` and `interactive_triggers.py` get EXPERIMENTAL headers that name the canonical module; a test keeps product paths from importing them |
| Tests | `tests/test_design_system.py` (15 tests): system integrity, generator obedience, the assemble regression, the helper-contrast regression, the highlighter, writer/simulator easing, travel time, critic behaviour, director-output agreement, schema, quarantine. One T019 expectation was updated (chart step 0.8 → 0.7 s) |

## Reproduction

```bash
git worktree add --detach /tmp/base d57f4a1        # arm "base"
python3 experiments/T034-20261019-claude-design-system/run_eval.py /tmp/base /tmp/t034-eval
python3 -m unittest discover -s tests              # 289 tests
python3 scripts/design_critic.py tests/fixtures/report_deck.pptx --md critique.md
```

Inputs:

- the 4 repository fixtures;
- 5 synthetic Forge decks (`inputs/spec_*.json`), each built with Forge's
  static stage and themed `midnight`, `paper`, `office:Facet`, brand seed
  `#E8B100` light and brand seed `#DA251D` dark.

Each input was directed by both arms in the `modern` and `cinematic` styles
(36 runs). Every output was graded by the current critic. Results:
`results.json`, `results.md`.

### Files

The same Forge deck (brand seed `#DA251D`, dark theme, cinematic style) is
directed by both arms:

| File | SHA-256 |
|---|---|
| `output/before_dark_brand_cinematic.pptx` (base arm) | `26b96d880e2aa928ce594c4d5347cbf537faaeeed8c055cf0b4042382d9ae50f` |
| `output/T034_dark_brand_cinematic.pptx` (T034 arm) | `f8ce4bbf9f305a9a5239e69a78129aa84bf39e49bc04049c87d2b33d75401c01` |

## Evidence

### Same inputs, two generator versions, one critic (`results.md`)

- **Warnings.** Generator-controlled warnings fall from **14 to 6**.
  - The 8 removed are all COL-GRAPHIC: on both brand-colour themes the old
    helpers were painted `2E1916` on `1D0C0A` (1.14:1).
  - With T034 they use the brand red `F74739` at 5.33:1
    (`preview/before-after-helpers.png`, and the full sheets
    `before-/after-dark-brand-*.png`).
- **Remaining 6.**
  - Five are MOT-SETTLE on Forge cinematic decks: a token journey ends parked
    before Forge's Morph orbs. This is pre-existing, flagged since T028, and
    left open (see Next).
  - One is the essay deck in `modern` style: a single effect kind
    (MOT-VOCAB), plus long paragraphs (DEN-WORDS, which is content, not the
    generator).
- **Scores.** Overall rises slightly or stays equal on every input; none
  falls.

### Generator–critic agreement (tests)

- Four fixtures × five styles: `auto` output has **no warnings** on the
  rules the director generates for. Only notes remain: busy assemble clicks
  of 9–14 effects with 5–6 movers in the showcase, and chart steps before
  their duration was clamped.
- The highlighter on "Result" (T028 report deck) was teal at 25 % under teal
  text, which brought contrast down to 2.53:1. The marker is now sized to
  10 %, and contrast stays at ≥ 3:1.

### Landscape (existing decks, `results.md`)

| Deck | Overall | Main findings |
|---|---|---|
| Report fixture, raw | 4.01 | Rhythm 3.0. MOT-STATIC: 3 of 4 content slides still. MOT-VOCAB: 1 kind. KPI numbers 0F9D8A on F4EFE6 at 2.95:1 (44 pt, needs 3:1) |
| Showcase fixture, raw | 3.17 | Rhythm 1.0 (static) |
| T019 / T028 director outputs | 4.80–4.81 | The KPI contrast inherited from the fixture; the token-settle note |
| T022 Codex T009 candidate | 4.33 | 9 slides over 45 words |
| T024 Argon complex showcase | 3.72 | 38 text-contrast failures (cyan on blue 2.13:1); up to 34 objects moving at once (MOT-MOVERS) and up to 78 effects in a click; body 11 pt, smallest 9 pt |
| T025 Forge EN / VI | 4.63 / 4.64 | 15 / 13 type sizes (Forge ignores the Office type scale it advertises); Ken Burns pictures before Morph |

### Render calibration (PowerPoint 16.0 vs LibreOffice 24.2, same 10-slide Forge deck)

Settled-frame metrics agree closely enough to measure layout without
PowerPoint:

| Metric | Median difference | Max difference | Spearman |
|---|---|---|---|
| Background share | 0.022 | 0.036 | 0.99 |
| Balance | 0.014 | 0.077 | 0.88 |
| Colourfulness | 0.9 | 10.8 | 0.92 |

The first PowerPoint read was wrong for slides 1–3. A render strip's last
frame is the Morph transition into the next slide, and the picker took it.
The picker now takes the frame with the most content.

### Checks

- 289 tests pass (274 before, plus 15 new).
- `validate_director_plan` passes on both T028 plans.
- The director output for the report deck validates against ISO 29500 PML.

PowerPoint playback: not run. Native playback: null.

## Limitations

- **No PowerPoint.** The cloud session has no PowerPoint. Timing, easing and
  Morph have not been observed, so the design-system bands are checked on
  structure and simulation only.
- **Judgement bands.** Several bands are judgement calls anchored to Carbon
  and Material tokens, WCAG, corpus statistics and perception studies. They
  are not optima from a user study, and the scores are not human ratings.
- **Text measurement.** Text colour behind gradients and pictures is not
  resolved (those checks are skipped). Word counts over-count Vietnamese
  (syllables).
- **Secondary sources.** Several cited studies were read from secondary
  summaries because the sandbox blocks their hosts.

## Next

1. **MOT-SETTLE fix by "authoring at the destination".** A generated token
   rests at its last stop in the XML and travels *from* the first stop, so
   the slide's end state is its authored layout. Morph then has nothing to
   snap. Apply this to Forge decks with Morph orbs.
2. **Forge type scale.** Read `type_scale_pt` from the Office kits, and limit
   generated sizes to the design-system band (TYP-SIZES).
3. **Native gate.** On Windows, play `T028_*_pro.pptx` and a Forge cinematic
   deck. Record easing, autoRev pulses, the visibility of helpers in dark
   theme, and settle behaviour.
4. **Human calibration.** Rank 20 decks by hand. Compare with the critic
   (Spearman), as SlidesGen-Bench does.
