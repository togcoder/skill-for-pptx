# Task registry

This file is the one place to take a task ID. Before starting, add a row with
status `claimed`, using the next free ID (**T035**). Push the row before you do
expensive work. IDs are never reused. T024 was taken three times in parallel,
so those rows carry a suffix. The experiment folders keep the names they were
created with.

Statuses:

- **main**: merged to `main`.
- **tip**: on the research tip `claude/blissful-pasteur-gmll59` (= `work/T033-…` + T034), not yet in `main`.
- **partial**: some of the task's scope is done.
- **open**: not started, or nobody owns it.
- **experimental**: kept for reference; no product path uses it.
- **superseded**: replaced by a later task.

Git author names do not identify agents reliably. Commits T006–T018 show
`togcoder` (Codex runs), and T025–T033 show a placeholder author name from the
owner's machine. The "Agent" column comes from claims and reports.

| ID | Title | Agent | Branch / PR | Status | Evidence |
|---|---|---|---|---|---|
| E001–E004, H001–H003 | Baseline motion experiments and hypotheses | Codex | early main | main (frozen baselines) | `experiments/E00*/`, `experiments/H00*/` |
| T001 | Native PowerPoint playback gate | — | — | open; superseded by T020 §A and the T034 next steps | — |
| T002 | Tight carrier paths | Codex | PR #2 | main | `experiments/T002-20261004-codex-tight-carriers/REPORT.md` |
| T003 | New motion recipe: layer separation | Codex | PR #1 | partial | `experiments/T003-20261004-codex-layer01/REPORT.md` |
| T004 | Portable backend | — | — | open | — |
| T005 | Intent choreography | Codex | — | partial | `experiments/T005-20261004-codex-choreography/` |
| T006 | Native timeline: semantics matrix, writer, packing | Codex | PR #12 and others | main (writer frozen; superseded by T019) | `experiments/T006-*/` |
| T007 | Existing-deck motion director scaffold | Codex | `work/T007-*` | main (product layer superseded by T019); `work/T007-helper-component-synthesis-20261004` unmerged | `experiments/T007-*/` |
| T008 | Continue existing motion | — | — | superseded: T019 extends existing timing | — |
| T009 | Autonomous no-script benchmark | Codex | `work/T009-codex-no-script-20261005` (PR #22, held back) | partial; recompiled in T022 | `experiments/T022-…/REPORT.md` |
| T010 | Click-beat choreography | Codex | main | main | `experiments/T010-20261005-click-beat-choreography/` |
| T011 | Director click rhythm | Codex | main | main | `experiments/T011-20261005-director-click-rhythm/` |
| T012 | Data-motion recipes | Codex | main | main | `experiments/T012-…/` |
| T013 | Native chart execution | Codex | main | main (native pending) | `experiments/T013-…/` |
| T014 | KPI counter execution | Codex | main | main (native pending) | `experiments/T014-…/` |
| T015 | Director to execution | Codex | main | main | `experiments/T015-…/` |
| T016 | Real-package data motion | Codex | main | main | `experiments/T016-…/` |
| T017 | Generic report motion | Codex | main | main | `experiments/T017-…/` |
| T018 | Native PowerPoint QA evidence review | Codex | PR #21 | main | `experiments/T018-20261005-qa-evidence-review/REPORT.md` |
| T019 | Canonical timing writer + Motion Director | Claude (cloud) | PR #23 | main | `experiments/T019-20261005-claude-motion-director/REPORT.md` |
| T020 | Motion Director continuation (native gate, fixtures, packaging) | — | — | open | `research/tasks/T020-motion-director-continuation.md` |
| T021 | Compound motion (Codex) | Codex | `work/T021-codex-compound-motion-20261005` (PR #24, claim only) | open: no code; overlapped by T023 | — |
| T022 | Recompile Codex T009 + text-box decks | Claude (cloud) | PR #25 | main | `experiments/T022-20261005-claude-t009-recompile/REPORT.md` |
| T023 | Compound motion engine, Director v0.6 | Claude (cloud) | PR #25 | main | `experiments/T023-20261005-claude-compound-motion/REPORT.md` |
| T024a | Motion layers + script layer | Claude (cloud) | `claude/blissful-pasteur-gmll59` | tip | `experiments/T024-20261005-claude-layers-script/REPORT.md` |
| T024b | Picture motion (Ken Burns) + accent intro | Claude (desktop) | `work/T024-claude-picture-motion-graphics` | tip | `experiments/T024-20261007-claude-picture-motion/REPORT.md` |
| T024c | Argon (Gemini) complex motion rigging | Argon | `import/argon-t024-20261014` | tip (evaluated in T032) | `experiments/T024-20261014-gemini-complex-motion-rigging/REPORT.md` |
| T025 | Slide Forge (new decks) | Claude (desktop) | `work/T024-claude-picture-motion-graphics` | tip | `experiments/T025-20261007-claude-slide-forge/REPORT.md` |
| T026 | Forge online assets | Claude (desktop) | `work/T026-claude-forge-assets` | tip | `experiments/T026-20261007-claude-forge-assets/REPORT.md` |
| T027 | Design + motion knowledge base, 198 presets | Claude (desktop) | `work/T027-claude-design-motion-corpus` | tip | `experiments/T027-20261007-claude-design-motion-corpus/REPORT.md`, `knowledge/README.md` |
| T028 | Morph Studio + pro text tricks | Claude (cloud) | `claude/blissful-pasteur-gmll59` | tip | `experiments/T028-20261008-claude-morph-studio/REPORT.md` |
| — | Integration of both lines | Claude | `integrate/20261008` (867e355) | tip | `docs/CHANGELOG.md` |
| T029 | Motion tokens (Carbon/Material → accel/decel) | Claude (desktop) | `work/T029-claude-motion-tokens` | tip (no report; see CHANGELOG, `knowledge/README.md`) | `scripts/motion_tokens.py` |
| T030 | Brand palette from one colour (OKLCH) | Claude (desktop) | `work/T030-claude-brand-palette` | tip (no report; see CHANGELOG) | `scripts/brand_palette.py` |
| T031 | Measurable critique (WIP) | Claude (desktop) | `work/T031-claude-critique` | superseded by T034 `design_critic.py` | `docs/CHANGELOG.md` |
| T032 | Evaluate + integrate Argon's T024c | Claude (desktop) | `work/T032-claude-argon-integration` | tip | `experiments/T032-20261015-claude-argon-integration/REPORT.md` |
| T033 | Argon second drop: morph twins, triggers, pacing | owner + Argon | `work/T033-argon-morph-staging` | experimental (quarantined in T034) | `experiments/T033-20261016-argon-research/REPORT.md` |
| T034 | Design system (beauty ↔ technique) + documentation standardised | Claude (cloud) | `claude/blissful-pasteur-gmll59` | tip | `experiments/T034-20261019-claude-design-system/REPORT.md` |
| T035 | *next free ID* | | | | |
