# T020 — Continue the Motion Director (handoff from T019)

Status: queued. Not claimed. Built on T019 (merged to main).

## Where things stand

Product entry point: `scripts/motion_director.py`
(`inspect → draft → apply → storyboard / verify`), writer
`scripts/pptx_animator.py`, skill `skills/pptx-motion-director/SKILL.md`,
plugin `.claude-plugin/` + `commands/animate-deck.md`.
Evidence: `experiments/T019-20261005-claude-motion-director/REPORT.md`.

Proven: structure, preservation, simulated click states, LibreOffice reads the
sequencing/presets as intended. **Not proven: PowerPoint playback.**
Patch v0.2–v0.5 writer is frozen and known-defective (after-previous runs
concurrently); do not build on it.

Read first: AGENTS.md, HANDOFF.md (T019 section), the T019 report,
`skills/pptx-motion-director/SKILL.md`, `docs/CLICK_BEAT_CHOREOGRAPHY.md`.
Run `python3 -m unittest discover -s tests -v` (190 pass at T023).

## Work items — pick by environment, in priority order

### A. Native PowerPoint gate (needs Windows + PowerPoint) — highest value

Also play the T023 compound-motion showcase
`experiments/T023-20261005-claude-compound-motion/output/T023_showcase_directed.pptx`
against `preview/slide-0N.png` (anchored chained paths, Grow compounding,
Transparency restore, Morph glide), and the T009 deck candidates from T022:
`experiments/T022-20261005-claude-t009-recompile/output/*.pptx`.

1. Open `experiments/T019-20261005-claude-motion-director/report_deck_motion.pptx`
   (sha256 `b7f0e2f4…6ba11`) using `docs/POWERPOINT_NATIVE_HARNESS.md`.
2. Record per slide: repair prompt yes/no; Animation Pane shows named effects
   (Float In, Wipe, Fade) not "Custom"; bullets/cards hidden before their click;
   `after-previous` steps play in sequence; chart builds series by series with
   axes visible; slide 6 original fades still work, then the appended picture.
3. Save the file once in PowerPoint and diff the timing XML against ours —
   any normalisation PowerPoint applies is the next writer fix.
4. Only then set native playback verified, per effect that was observed.

### B. Director quality (Python only)

Progress (T022): text-box-only decks fixed (implicit titles, label–body pairing,
paragraph clicks) with `tests/fixtures/essay_outline_deck.pptx`. Still open:
tables, SmartArt, image-heavy and two-column comparison decks, 4:3 decks.

1. Build 3+ new synthetic fixtures unlike `tests/fixtures/report_deck.pptx`:
   table-heavy, image-heavy, two-column comparison, SmartArt/diagram, Vietnamese
   text, a 16:10/4:3 deck, groups used as content. Run `auto`, view storyboards,
   log every wrong decision before changing heuristics (`draft_slide`,
   `_units`). Keep the T019 fixture results as regression.
2. Independent transfer test: give a fresh agent only the skill + a new deck +
   one-line goal; record whether it refines the draft sensibly. Do not leak
   expected answers.
3. Gaps known at T019: tables (row-by-row reveal not supported), SmartArt
   (`bldDgm`), comparison layouts (left vs right as separate clicks),
   storyboard shows chart series builds as whole-chart reveal, counters clutter
   edit/PDF view (find a cleaner native approach or keep opt-in).

### C. Packaging

1. Test plugin install in Claude Code (`/plugin marketplace add`,
   `/plugin install pptx-motion@togcoder-pptx`, `/animate-deck`) and fix the
   manifest if needed. Repo is private: installer needs GitHub access.
2. Consider bundling only `scripts/` + skill for a lighter install; do not
   publish a release without the owner's approval.

## Acceptance

- New evidence in a new experiment folder (`T020-<date>-<agent>-…`), never
  overwriting T019 outputs.
- Every heuristic change has a failing fixture first and a regression test.
- Tests pass; STATUS.md updated; playback claims only from observed PowerPoint.
