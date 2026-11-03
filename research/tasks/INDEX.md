# Task registry

Since T040: every new title starts with its domain in brackets: `[pptx]`, `[docx]`, `[xlsx]`, `[svg]` or `[cross]` (see `domains/README.md`). Lifecycle: `lab/PROTOCOL.md`. A row may carry `review requested` / `reviewed: <verdict>`.

This file is the one place to take a task ID. Before starting, add a row with
status `claimed`, using the next free ID (**T056**). Push the row before you do
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
| T025 | Slide Forge (new decks) | Claude (desktop) | `work/T026-claude-forge-assets` | tip (no report; see `scripts/slide_forge.py`, CHANGELOG) | `scripts/slide_forge.py` |
| T026 | Slide Forge assets | Claude (desktop) | `work/T026-claude-forge-assets` | tip (no report; see CHANGELOG) | `assets/` |
| T027 | Motion corpus scan | Claude (cloud) | `work/T027-claude-design-motion-corpus` | tip | `experiments/T027-20261008-claude-motion-corpus/REPORT.md` |
| T028 | Morph Studio + intro text tricks | Claude (cloud) | `claude/blissful-pasteur-gmll59` | tip | `experiments/T028-20261008-claude-morph-studio/REPORT.md` |
| — | Integration of both lines | Claude | `integrate/20261008` (867e355) | tip | `docs/CHANGELOG.md` |
| T029 | Motion tokens (Carbon/Material → accel/decel) | Claude (desktop) | `work/T029-claude-motion-tokens` | tip (no report; see CHANGELOG, `knowledge/README.md`) | `scripts/motion_tokens.py` |
| T030 | Brand palette from one colour (OKLCH) | Claude (desktop) | `work/T030-claude-brand-palette` | tip (no report; see CHANGELOG) | `scripts/brand_palette.py` |
| T031 | Measurable critique (WIP) | Claude (desktop) | `work/T031-claude-critique` | superseded by T034 `design_critic.py` | `docs/CHANGELOG.md` |
| T032 | Evaluate + integrate Argon's T024c | Claude (desktop) | `work/T032-claude-argon-integration` | tip | `experiments/T032-20261015-claude-argon-integration/REPORT.md` |
| T033 | Argon second drop: morph twins, triggers, pacing | owner + Argon | `work/T033-argon-morph-staging` | experimental (quarantined in T034) | `experiments/T033-20261016-argon-research/REPORT.md` |
| T034 | Design system (beauty ↔ technique) + documentation standardised | Claude (cloud) | `claude/blissful-pasteur-gmll59` | tip | `experiments/T034-20261019-claude-design-system/REPORT.md` |
| T035 | DeckCraft native bridge & Skill-for-Design evolution | Antigravity | `work/T035-deckcraft-bridge` | tip | `experiments/T035-20261031-deckcraft-bridge/REPORT.md` |
| T036 | Skill-for-Design Foundation: Universal ArtCraft Hub, Multi-Agent Protocols & Intent Schemas | Antigravity + Argon | `work/T036-skill-for-design-core` | tip | `experiments/T036-20261101-skill-for-design-core/REPORT.md` |
| T037 | Multi-Craft Bridges (WordCraft, GridCraft, VectorCraft) & Intent Decoder | Antigravity | `work/T037-multi-craft-bridges` | tip | `experiments/T037-20261101-multi-craft-bridges/REPORT.md` |
| T038 | PPTX Design Canon Tokens, Asymmetric & Bento Grids, Optical Balance & Critic Rules | Antigravity + Argon | `work/T038-pptx-design-canon-tokens` | tip | `experiments/T038-20261101-pptx-design-canon-tokens/REPORT.md` |
| T039 | [docx] DocumentCraft: professional Word canon, real fields, tables/images and linked appendices | OpenCode (DeepSeek V4.1 Flash) | `work/T039-opencode-docx` | review requested | `experiments/T039-20261101-opencode-office-canon/REPORT.md` |
| T040 | Multi-domain lab restructure: domains, agent protocol, research/review/merge standards | Claude (cloud) | `claude/blissful-pasteur-gmll59` | tip | `experiments/T040-20261101-claude-lab-restructure/REPORT.md` |
| T041 | [xlsx] SheetCraft: full Excel chart control, combo/secondary axis, geometry, palette, cache and print audit | OpenCode (DeepSeek V4.1 Flash) | `work/T041-opencode-xlsx` | review requested | `experiments/T041-20261101-opencode-sheet-craft/REPORT.md` |
| T042 | [cross] Multi-Domain Design Canons: Video, Vector/SVG, 3D/Solid, CAD & Audio | Antigravity + Argon | `work/T042-multi-domain-design-canons` | tip (review requested) | `experiments/T042-20261101-antigravity-multi-domain-canons/REPORT.md` |
| T043 | [pptx] Dynamic Theme Engine: Need-Based Synthesizer, Reference Teardown & AI Image Visual Harmonizer | Antigravity + Argon | `work/T043-dynamic-theme-engine` | tip (review requested) | `experiments/T043-20261101-antigravity-dynamic-theme-engine/REPORT.md` |
| T044 | [cross] Multi-Asset Pipeline Protocol, User Experience Maximization & Local Autonomy Charter | Antigravity | `work/T044-cross-asset-pipeline-and-autonomy` | tip (review requested) | `experiments/T044-20261101-antigravity-cross-asset-pipeline/REPORT.md` |
| T045 | [docx] Advanced report craft: side-by-side media, OMML equations, merged-header tables, image cells and cover assets | OpenCode (DeepSeek V4.1 Flash) | `work/T045-opencode-advanced-docx` | main | `experiments/T045-20261101-opencode-advanced-docx/REPORT.md` |
| T046 | [xlsx] Advanced workbook: image tables, Gantt, relationship matrix, cross-sheet formulas, pivot, VBA and dashboard design | OpenCode (DeepSeek V4.1 Flash) | `work/T046-opencode-advanced-xlsx` | main | `experiments/T046-20261101-opencode-advanced-xlsx/REPORT.md` |
| T047 | [cross] Office Link Bridge: Interactive Excel-to-PowerPoint/Word Linked Charts & Embedded Workbook Sync | Antigravity | `work/T047-cross-office-link-bridge` | main | `experiments/T047-20261101-antigravity-office-link-bridge/REPORT.md` |
| T047b | [docx] Standards-controlled annual/ESG report: ISO 7144/2145/690/80000 + GRI content, conformance sheet and richer narrative | OpenCode (DeepSeek V4.1 Flash) | `work/T047-opencode-standards-report` | main | `experiments/T047-20261101-opencode-standards-report/REPORT.md` |
| T048 | [xlsx] Workbook UX: hidden data sheets, VBA data-entry form, tab colour, merged-cell rules and sheet protection | OpenCode (DeepSeek V4.1 Flash) | `work/T048-opencode-workbook-ux` | main | `experiments/T048-20261101-opencode-workbook-ux/REPORT.md` |
| T048b | [pptx] Non-Linear Slide Navigation: Interactive Branching, Return Paths, Kiosk Mode & Mini-Game State Machine | Antigravity | `work/T048-interactive-slide-branching` | main | `experiments/T048-20261101-antigravity-slide-branching/REPORT.md` |
| T049 | [pptx] 1-Slide Native Interactive Mini-Games: Mystery Chests & Quiz Battle | Antigravity | `work/T049-advanced-presentation-interactivity` | main | `experiments/T049-20261101-antigravity-advanced-interactivity/REPORT.md` |
| T050 | [xlsx] VBA UserForm data entry + composed dashboard (grid, chart selection, interaction, visual quality) | OpenCode (DeepSeek V4.1 Flash) | `work/T050-opencode-userform-dashboard` | main | `experiments/T050-20261102-opencode-userform-dashboard/REPORT.md` |
| T051 | [vector] Photo-to-vector line hierarchy: what to keep, simplify or remove for a controlled technical illustration | OpenCode (DeepSeek V4.1 Flash) | `work/T051-opencode-photo-vector` | main | `experiments/T051-20261102-opencode-photo-vector/REPORT.md` |
| T052 | [docx] Configurable standard profiles + Vietnamese university scientific report (declaration, chapters, equations, references) | OpenCode (DeepSeek V4.1 Flash) | `work/T052-opencode-scientific-report` | main | `experiments/T052-20261102-opencode-scientific-report/REPORT.md` |
| T053 | [vector] Semantic product reconstruction: parametric 2.5D vector illustration from a photo (supersedes the T051 edge trace) | OpenCode (DeepSeek V4.1 Flash) | `work/T053-opencode-vector-reconstruction` | main | `experiments/T053-20261102-opencode-vector-reconstruction/REPORT.md` |
| T054 | [vector] Comparative match to the source photo: silhouette/proportion, chrome top, group head/portafilter and tray; photo-vector overlay as acceptance test | OpenCode (DeepSeek V4.1 Flash) | `work/T054-opencode-vector-match` | review requested | `experiments/T054-20261102-opencode-vector-match/REPORT.md` |
| T055 | [pptx] Native 3D product explainer: semantic scene → embedded GLB + native callouts + camera views + Morph, verified in PowerPoint | OpenCode (DeepSeek V4.1 Flash) | `work/T055-opencode-pptx-3d` | claimed | `experiments/T055-20261103-opencode-pptx-3d/REPORT.md` |
| T056 | *next free ID* | | | | |
