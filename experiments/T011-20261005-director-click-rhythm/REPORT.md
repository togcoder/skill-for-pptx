# T011 — Director click rhythm and existing-deck execution

Date: 2026-10-05 Vietnam.

## Why T011 exists

T010 fixed the low-level timing architecture, but an autonomous Motion Director
could still produce a flat list of motion actions and leave click grouping to the
writer.

That is too late.

Presenter rhythm is a narrative decision. The AI must decide the click structure
while understanding the report, before authoring OOXML.

## Semantic hierarchy

The director layer now uses:

`Deck Narrative -> Slide Objective -> Click Beat -> Motion Beat -> Effects`

This is compatible with T010's execution hierarchy:

`Slide -> Click Beat -> Stage -> Effects`

A motion beat is an audience-facing action. It is **not automatically a click**.
Several motion beats can be inside one click, and two actions on the same object
can require different clicks if the presenter should pause between them.

## Director contract v0.2

`existing-deck-motion-director` v0.2 adds per-slide `click_beats`.

Each click beat records:

- `purpose`;
- ordered `motion_beats`;
- `stable_state`;
- `pause_after`;
- `boundary_reason` from click 2 onward.

Validation requires:

- exact ordered partition of all motion beats;
- first motion beat of each click uses `on-click`;
- later beats in that click may use `with-previous` or `after-previous`;
- no nested `on-click`;
- each later click has a narrative boundary reason.

Legacy v0.1 remains accepted only for historical flat-beat plans.

## Existing-deck execution v0.2

`existing-deck-timeline-patch` now also supports v0.2 click beats for a source
slide that has no native timing yet.

It emits multiple direct click groups under `mainSeq` while preserving:

- the original slide count;
- exact source object ID + name targeting;
- source hash guard;
- untouched package/slide parts;
- one physical slide for all same-scene motion.

v0.1 remains the legacy one-click cumulative-delay baseline.

T008 still owns safe merge/continuation when the source slide already has native
timing.

## No-script benchmark change

T009 now scores:

- click-boundary quality;
- stable-state quality;
- continuity quality;
- premature-reveal count.

A no-script plan fails if it:

- merely animates z-order;
- collapses the whole slide into one autoplay chain;
- or creates one click for every individual motion without narrative reason.

## Automated evidence

Temporary GitHub Actions run:

- run ID: 37234829380
- Python 3.12
- `python -m py_compile scripts/*.py`: pass
- `python -m unittest discover -s tests -v`: **92 tests passed in 0.449 s**

New coverage proves:

1. valid director v0.2 click rhythm passes;
2. incomplete click partition fails;
3. nested on-click inside one click beat fails;
4. a second presenter click without boundary reason fails;
5. existing-deck patch v0.2 can place two presenter click groups on one existing
   source slide;
6. read-back inventory reports two click groups;
7. the second group contains a click-started stage plus an after-previous stage;
8. v0.1 existing-deck patch behavior remains covered.

## Evidence boundary

This is semantic-contract + OOXML-structure evidence.

Actual Microsoft PowerPoint playback remains unverified. Do not claim that
structural read-back proves presenter click behavior.

## Next research

The next high-value experiment is not another hard-coded radial recipe.

Use a real report slide and compare:

- bad one-click autoplay choreography;
- bad one-click-per-motion choreography;
- AI-inferred narrative click rhythm.

Keep the same source resources and slide count. Human review should judge whether
click boundaries align with meaningful explanation states. Then run exact-file
PowerPoint playback.
