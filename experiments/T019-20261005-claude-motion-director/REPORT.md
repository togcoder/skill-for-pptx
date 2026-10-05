# T019 — PowerPoint-canonical timing and one-command Motion Director

## Frozen input

- Task: `research/tasks/T019-canonical-timing-motion-director.md`; claim
  `research/claims/T019-motion-director-20261005.md`.
- Date 2026-10-05; Claude Code cloud session; base commit in `base-commit.txt`.
- Owner brief (paraphrased): keep developing until the tool lets an AI produce
  the intended result — skill, plugin or anything — within a ~$20 budget.
- Hypotheses:
  1. The patch v0.2–v0.5 writer's click-beat tree does not sequence
     `after-previous` stages and lacks entrance visibility; a writer that copies
     PowerPoint's saved structure fixes both.
  2. Real decks need placeholder-geometry inheritance, paragraph builds, and
     extension of existing timing before an AI can direct them end to end.
- Baselines kept frozen: `scripts/patch_existing_timeline.py` and all earlier
  tests are unchanged. Validator change is additive (v0.5 gate only).

## Reproduction

Environment: Python 3.11.15, lxml 6.1.3, LibreOffice 24.2.7.2 (Impress installed
in the session with apt for this study), ImageMagick `montage`. No PowerPoint.

```bash
python3 scripts/make_report_fixture.py            # dev-only (python-pptx, Pillow)
python3 scripts/motion_director.py inspect tests/fixtures/report_deck.pptx > inspect-outline.txt
python3 scripts/motion_director.py auto tests/fixtures/report_deck.pptx \
    -o experiments/T019-20261005-claude-motion-director/report_deck_motion.pptx \
    --storyboard experiments/T019-20261005-claude-motion-director/storyboard
python3 scripts/lo_timing_crosscheck.py <deck> --output lo-crosscheck-*.json
python3 -m unittest discover -s tests -v
```

| File | SHA-256 |
|---|---|
| `tests/fixtures/report_deck.pptx` (source) | `7366f1382edd834d6cea1831d5ea4959232053ecc3bb55328fbf4eae5394b3d6` |
| `report_deck_motion.pptx` (auto output) | `b7f0e2f4be0d3e19e96f1274af210583c846fa182776f1ec9185bc2a6366ba11` |
| H001 + T017 plan via patch v0.5 writer (not kept) | `6c6458cce78d287650c1d069317a6699ea3d3b4caba4852e4ee0881946d636d0` |
| H001 + same plan via canonical writer (not kept) | `0b0b06965b7042af587bb5532f2279e12f67f7dde7dc1e27a8b036c8f3b2f879` |

The two H001 decks are reproducible from `tests/test_generic_report_motion.py`'s
`generic_director` plan; only their cross-check JSON is stored.

## Evidence

### Independent importer reading (LibreOffice PPTX → ODP)

Same H001 deck, same T017 Director v0.4 plan (slide 1: three-object stagger):

| Writer | node types | preset class | block begins | visibility sets |
|---|---|---|---|---|
| patch v0.5 (`lo-crosscheck-v05-writer-h001.json`) | on-click, after-previous, after-previous | none | 0s, 0s, 0s | 0 |
| canonical (`lo-crosscheck-canonical-h001.json`) | on-click, after-previous, after-previous | entrance | 0s, 0.32s, 0.64s | 1 each |

LibreOffice reads the old tree as three effects starting together; it reads the
new tree as a sequence. This supports hypothesis 1 for one independent SMIL
interpreter. It is not PowerPoint playback.

Report deck (`lo-crosscheck-report-deck.json`): every new effect is recognised as
an entrance preset (`ooo-entrance-ascend` = Float In, wipe, fade); chart series 2
begins at 0.8s; process steps begin 0.3s after their connectors; slide 6's
PowerPoint-authored groups are still read as two on-click fades.

### Package and preservation checks (`report_deck_motion.report.md`)

- 7 slides in, 7 out; no part added/removed; only slide XML parts 2, 3, 4, 5, 7
  changed; slides 1 and 6, chart, layouts, theme and media byte-identical.
- Every source object keeps id, name, text and resolved geometry.
- Every animation and build target exists; cTn ids unique; simulated final
  state shows every source object and paragraph.

### Click plan chosen autonomously (no animation instructions given)

| Slide | Evidence used | Result |
|---|---|---|
| 1 title | title layout | static |
| 2 agenda | 4 bullets | 4 clicks, one bullet each (Float In) |
| 3 KPIs | 3 cards with hero numbers, notes "Start… Then… Finally" | 3 clicks, card + value + label together |
| 4 chart | clustered column, 2 series; takeaway card | click 1 chart by series (wipe up); click 2 takeaway |
| 5 process | 4 similar steps + 3 connectors; notes "walk the four steps" | 4 step clicks (connector wipe → step) + result click; corner badge static |
| 6 existing | PowerPoint-authored paragraph fades | preserved untouched |
| 7 priorities | 3 bullets | 3 clicks |

Storyboard sheets for each changed slide are in `storyboard/` and were viewed:
each frame is a LibreOffice render of the simulated stable state after a click.
They confirm order, no overlaps, and that hidden bullets leave layout intact.
Known preview limitation: a chart series build is shown as a whole-chart reveal.

### Tests

`python3 -m unittest discover -s tests -v`: **167 tests pass** (150 earlier +
17 new in `tests/test_motion_director.py`, one of which needs LibreOffice and
ImageMagick and is skipped without them).

Native playback: null. Real-application editing: null.

## Comparison

Measured only. The patch v0.5 writer and the canonical writer were compared on
the identical H001 plan via the same importer. No subjective score is given
because no native motion was observed.

## Failures and decision

- First storyboard attempt failed: the container's LibreOffice lacked Impress
  ("source file could not be loaded" for every deck, including H001).
  Installing `libreoffice-impress` fixed it; the storyboard and cross-check
  remain optional tools and their test is skipped when absent.
- Fixture bug: setting only left/width on a python-pptx placeholder wrote a
  zero-height frame; fixed in the generator before freezing the fixture.
- Decision: keep the canonical writer as the product path
  (`scripts/motion_director.py`). Patch v0.1–v0.5 stay frozen for reproduction;
  new work should not build on their click-beat tree.
- Counter proxies are opt-in (`--counters`): stacked proxy text is visible in
  edit view and in PDF/print export of the final slide.

## Reusable lesson and handoff

- Lesson: in PowerPoint timing, sequence lives in the tree (time blocks with
  begin delays), not in `nodeType`. `nodeType` is a UI label.
- Lesson: entrance targets must carry `set style.visibility=visible`; that is
  what makes an object start hidden.
- Skill: `skills/pptx-motion-director/SKILL.md`; plugin manifest
  `.claude-plugin/`; command `commands/animate-deck.md`.
- Next step (unchanged gate): play `report_deck_motion.pptx` and the frozen T006
  hashes in Windows PowerPoint with `docs/POWERPOINT_NATIVE_HARNESS.md`; record
  whether bullets/cards start hidden and whether `after-previous` sequences.
- Claim status: completed for structural scope.
