# T007 — Existing Deck Motion Director

Status: active product-layer research. Owner: unassigned after initial scaffold.

Read `docs/PRODUCT_TARGET.md` and `docs/MOTION_PACKING.md` first.

## Goal

Accept an existing PPTX and produce a motion-directed version of the same deck.
If a choreography/report script exists, follow it. If no script exists, infer
the report sequence and create a script before authoring motion. Create missing
components only when required by that script and keep them inside the existing
visual framework.

## Frozen product rules

1. Existing PPTX is the source of truth.
2. Preserve source slide count/order by default.
3. Preserve user content/resources by default.
4. Explicit script > notes > inferred narrative > researched narrative.
5. Do not animate every object just because it exists.
6. Missing components require a narrative role and design-system fit.
7. Same-resource motions stay on the same slide whenever feasible.
8. Never invent unsupported report data.
9. Native PowerPoint playback remains an exact-file acceptance gate.

## Research path

### T007-A — Deck intake/inventory

Build a reusable read-only extractor for:

- slide order/size;
- shapes and z-order;
- native names and numeric IDs;
- text;
- normalized geometry;
- pictures/media relationships;
- chart/table indicators;
- existing timing/transitions;
- speaker notes where available;
- master/layout/theme references where useful.

The output should be stable JSON suitable for an AI planner.

### T007-B — Motion-director contract

Define an intermediate plan containing:

- source PPTX hash;
- script source and confidence;
- deck narrative summary;
- per-slide semantic role;
- per-slide ordered motion beats;
- resource reuse mapping;
- missing components and why they are necessary;
- preservation constraints;
- target slide count;
- animation timeline requirements.

### T007-C — Script generation

Test three cases:

1. explicit user script;
2. speaker notes / obvious report structure;
3. no script and ambiguous structure.

For case 3, the AI must first form a report sequence. External research is
allowed only when appropriate and must remain separate from user-provided data.

### T007-D — Component synthesis

Generate only missing native components. Evaluate:

- visual-system match;
- whether an existing resource could have been reused;
- editability;
- data provenance;
- whether the component improves narrative clarity.

### T007-E — Existing-deck patching

Apply T006 timeline primitives to existing slide objects rather than recreating
the entire deck. Use stable source object identity and guard against destructive
changes.

## First acceptance milestone

Given a real existing 3–10 slide report with no animation:

- inventory the deck;
- infer a report script when none is supplied;
- select one slide with at least three existing resources;
- produce a motion plan that reuses those resources;
- create at most one justified helper component;
- keep the slide count unchanged;
- inject native timing;
- verify preservation of untouched content;
- play the exact file in PowerPoint and capture evidence.

## Non-goals for the first milestone

- arbitrary redesign of the whole deck;
- replacing all existing objects with generated artwork;
- one-motion/one-slide;
- video-only fallback presented as native PPTX;
- unsupported factual enrichment.


## 2026-10-04 source-object patching checkpoint

Implemented:

- `scripts/patch_existing_timeline.py`
- `skills/pptx-motion/references/existing-deck-timeline-patch.md`
- design fingerprint in `scripts/inspect_existing_deck.py`
- regressions in `tests/test_existing_deck_timeline_patch.py`

Final temporary CI run `37214809106`: 73 tests pass.

This removes the generated-deck `!!` naming requirement for animation targets.
Real source objects are guarded by source slide index + native ID + native name
and the exact source PPTX hash.

Next: build the semantic bridge from validated director beats to this concrete
patch plan. If a required helper component does not exist, synthesize it as a
native editable object using the inventory design fingerprint, refresh the
inventory/hash, then target it normally. Do not bypass this by rebuilding the
whole slide.
