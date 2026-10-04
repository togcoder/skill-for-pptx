# T007 — Existing Deck Motion Director scaffold

Date: 2026-10-04  
Branch: `work/T007-existing-deck-motion-director-20261004`

## User destination

The user expanded the product target beyond prompt-to-animation generation.

The target is an AI Motion Director that accepts an existing PPTX and:

- understands the report and existing visual resources;
- follows an existing script/storyboard when one exists;
- otherwise uses speaker notes, then infers the report sequence, and may research
  an appropriate reporting structure when needed and permitted;
- creates a motion script before animation;
- reuses existing slide resources by default;
- creates helper components only for genuine narrative gaps and inside the
  existing deck's design language;
- preserves slide count/order/content by default;
- packs shared-resource motion into the same slide;
- returns an editable PPTX with exact-file PowerPoint playback evidence before
  claiming native compatibility.

The canonical product statement is `docs/PRODUCT_TARGET.md`.

## Implemented in this experiment

### 1. Read-only existing-deck intake

`scripts/inspect_existing_deck.py` produces stable JSON with:

- source SHA-256;
- ordered slides and slide size;
- shapes and z-order;
- native shape names and local IDs;
- text;
- normalized and EMU geometry;
- picture / chart / table / diagram indicators;
- slide relationships;
- existing transition/timing detection;
- speaker notes when present;
- layout references;
- package-level theme/media/notes/chart/embedding presence.

The analyzer is read-only and does not infer the story.

A useful failure was retained during development: the first detector looked only
for direct-child `p:transition` and missed Morph transitions inside
`mc:AlternateContent`. CI exposed this. The detector now searches descendants
and the regression is locked.

### 2. Motion-director plan contract

`skills/pptx-motion/references/existing-deck-director.md` defines:

- source deck hash grounding;
- script source priority;
- deck-level narrative summary and beats;
- per-slide role/objective;
- per-slide motion beats;
- resource reuse targets;
- generated components and mandatory narrative rationale;
- source preservation policy;
- slide-count policy;
- research-source disclosure.

### 3. Plan validator

`scripts/validate_director_plan.py` validates a director plan against the exact
inventory.

It rejects:

- wrong source hash;
- wrong inventory version or source slide count;
- unsupported script source;
- researched script with no research sources;
- unknown slide/object targets;
- duplicate beat/component IDs;
- generated components without role/rationale/style basis/provenance;
- decorative-only rationales such as "đẹp hơn" / "ấn tượng hơn";
- same-slide violations in v0.1;
- unsupported timing intents;
- slide-count inflation when policy is preserve;
- explicit slide-count change without documented reasons.

### 4. Future-model routing

Updated:

- `AGENTS.md`
- `HANDOFF.md`
- `docs/STATUS.md`
- `skills/pptx-motion/SKILL.md`

Future models are now required to read `docs/PRODUCT_TARGET.md` and treat the
existing-deck director as the product destination, while Morph/T005/T006 remain
supporting research/backends.

## Automated evidence

A temporary branch-only GitHub Actions workflow was used and removed afterward.

Final successful run:

- Run ID: `37214340363`
- Job ID: `111471698106`
- `python -m py_compile scripts/*.py`: pass
- `python -m unittest discover -s tests -v`: **67 tests passed in 0.353 s**

New tests cover:

- H001 deck intake without package errors;
- ordered slides;
- exact semantic-name inventory;
- z-order;
- normalized geometry;
- transition detection through AlternateContent;
- real H001 speaker notes;
- source grounding for director plans;
- researched-script evidence requirement;
- unknown-target rejection;
- helper-component rationale requirement;
- preserve-slide-count invariant.

The temporary CI workflow was deleted before integration.

## What is established

Established:

- the product destination is explicit and persistent in the repo;
- the system can inventory an existing PPTX before editing;
- speaker notes and existing motion can be surfaced as planning evidence;
- the director-plan schema forces script provenance and preservation constraints;
- generated components cannot be justified by aesthetics alone;
- plan targets can be checked against actual source objects;
- existing slide count is protected by default.

Not yet established:

- autonomous high-quality narrative inference on a real no-script deck;
- external research selection quality;
- automatic component synthesis matching arbitrary corporate design systems;
- conversion of arbitrary director beats into T006 timing primitives;
- preservation-safe patching of arbitrary third-party decks;
- exact-file PowerPoint playback for T006/T007 output.

## Next experiment

Use a real existing 3–10 slide report **without a motion script**.

1. inventory the deck;
2. hide/remove notes from the planner context for the no-script condition;
3. make the model infer the report sequence and produce a director plan;
4. compare the inferred sequence with a human review;
5. choose one slide with at least three reusable resources;
6. create at most one justified helper component;
7. translate supported beats to the T006 one-slide timeline backend;
8. preserve slide count and untouched content;
9. freeze output SHA-256;
10. open/play the exact file in Microsoft PowerPoint.

A second arm should supply an explicit script to the same deck. Compare whether
the model correctly follows the explicit script instead of overriding it with
its inferred story.
