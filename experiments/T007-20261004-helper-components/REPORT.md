# T007 — Style-donor helper component synthesis

Date: 2026-10-04

## Purpose

The user requires the Motion Director to create missing components when a report
beat cannot be expressed with existing resources, while staying inside the
existing deck's visual framework.

This experiment implements the first safe native strategy: **clone an existing
native shape as a style donor** instead of inventing new fonts/colors/layout
language.

## Implemented

### Contract

`skills/pptx-motion/references/helper-component-synthesis.md`

A helper component plan freezes:

- exact source PPTX SHA-256;
- source slide;
- donor native ID + name;
- new unique native name;
- narrative role;
- explicit rationale;
- data provenance;
- normalized geometry;
- text action: preserve / clear / replace.

### Writer

`scripts/insert_helper_components.py`

v0.1:

- supports native `p:sp` donors only;
- clones the donor subtree;
- allocates a new slide-local cNvPr ID;
- preserves donor fill/line/text styling and textbox representation;
- changes only identity, geometry and requested text;
- preserves all other package parts;
- refuses destination overwrite;
- requires re-inventory before animation.

This is intentionally conservative. It does not clone charts, pictures,
SmartArt, media or embeddings.

## Why this fits the product target

The deck intake already exposes a design fingerprint. The model can use that
profile to choose an appropriate donor, then clone the donor so the helper
inherits the deck's real style.

Pipeline:

`inventory -> director plan -> identify resource gap -> choose donor ->
insert helper -> re-inventory -> source-object timeline patch`

The source-object patcher then targets the new helper normally by native ID +
name and the refreshed source hash.

## Automated evidence

Temporary branch-only GitHub Actions workflow was removed after validation.

Final run:

- Run ID: `37215145147`
- Job ID: `111474013826`
- Python compile: pass
- Unit suite: **77 tests passed in 0.540 s**

New regressions prove:

- shape helper inherits the donor style;
- text helper inherits donor font/text color and can replace content;
- a new unique native ID is allocated;
- source slide shape count increases by exactly one;
- untouched slide bytes remain identical;
- source hash mismatch fails;
- missing donor fails.

## Evidence boundary

This proves native package/component insertion and style inheritance.

It does not prove:

- PowerPoint playback of an animation involving the new helper;
- automatic donor selection quality;
- automatic layout/collision avoidance for arbitrary decks;
- component synthesis for charts/images/SmartArt;
- autonomous report-script inference quality.

## Next experiment

Build the semantic bridge:

1. director plan identifies a narrative gap;
2. model chooses a donor using the design fingerprint;
3. generate helper component plan;
4. insert component;
5. re-inventory;
6. compile supported director beats into source-object timeline patch;
7. patch native timing;
8. verify preservation and exact-file PowerPoint playback.

The no-script condition should be tested on a real report where speaker notes and
animation instructions are absent from the planner context.
