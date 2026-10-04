# T010 — Presenter-paced click-beat choreography

Date: 2026-10-05 Vietnam.

## User correction

The previous packed-timeline architecture solved the wrong half of the problem:
it kept many motions on one physical slide, but the first click launched the
entire sequence.

The desired behavior is presenter-paced choreography:

- identify which movements form one meaningful cluster;
- identify which movements share a slide but must wait for the **next click**;
- identify which movements happen concurrently;
- identify which movements automatically follow another movement.

The architecture is now:

`Slide -> Click Beat -> Stage -> Effects`

## Key distinction

- **Motion packing** decides whether resources/motions can stay on one slide.
- **Click-beat choreography** decides when the presenter allows the story to
  advance inside that slide.

These are separate planning decisions.

## PowerPoint semantics used

Microsoft Support documents:

- On Click: start when the presenter clicks;
- With Previous: start together with the previous effect;
- After Previous: start after the previous effect finishes;
- Delay is relative to that Start behavior.

Sources inspected 2026-10-05:

- https://support.microsoft.com/en-us/powerpoint/set-the-start-time-and-speed-of-an-animation-effect
- https://support.microsoft.com/en-us/powerpoint/apply-multiple-animation-effects-to-one-object
- https://support.microsoft.com/en-us/powerpoint/training/animate-text-or-objects

Empirical OpenXML cross-checks:

- lindexi authored-PPT timing analysis distinguishes several automatic animations
  wrapped under one click from separate main-sequence children for separate clicks:
  https://github.com/lindexi/lindexi.github.io/blob/0084be094c0177dcaa2de5bdbfee4ae00b5e3b8d/dotnet%20OpenXML%20PPT%20%E5%8A%A8%E7%94%BB%E6%A1%86%E6%9E%B6%E5%85%A5%E9%97%A8.md
- agentsea/nautilo groups `onClick` as a new click group while
  `withPrev`/`afterPrev` remain in the current group:
  https://github.com/agentsea/nautilo/blob/0f02e50472b09b96b18ae711412b4c36dd2a7b13/packages/office-slides/src/export/pptx/animation.ts

No external runtime code was vendored.

## Planning change

`scripts/pack_timeline.py` now emits native-timeline plan v0.2.

It preserves a flat `timeline` for geometry/audit and adds `click_beats`,
which must partition every stage exactly once and in order.

The T005/T006 regression is now:

| Click | Purpose | Stages |
|---|---|---|
| 1 | Reveal structure | burst |
| 2 | Show relationship | orbit |
| 3 | Drill into selected node | focus -> split |
| 4 | Close detail and restore context | reassemble -> restore |

This is one slide, not four slides.

The trigger sequence is:

`on_click, on_click, on_click, after_previous, on_click, after_previous`.

## Writer change

`scripts/add_timeline.py` is backward compatible:

- v0.1 with no `click_beats` keeps the legacy one-click cumulative-delay writer;
- v0.2 emits separate presenter click groups under `mainSeq`.

For v0.2:

- first stage of each beat -> `clickEffect`;
- later sequential stage -> `afterEffect`;
- later concurrent stage -> `withEffect`;
- effect behaviors inside a stage use zero delay;
- no cumulative delay is used to simulate presenter speech;
- each stage has a distinct build-list group ID.

The legacy one-click file remains valid as a negative pacing baseline.

## Existing-deck intake

`scripts/inspect_existing_deck.py` now recovers direct click-group structure
from `mainSeq` when available. The inventory exposes:

- click-group count;
- effects in each group;
- start-node types;
- source shape targets.

This lets the director preserve existing presenter rhythm instead of flattening
an authored deck into a delay-sorted effect list.

## Automated evidence

Temporary GitHub Actions:

- run 37234036106: initial click-beat writer/test set, 85 tests passed;
- run 37234224744: T005 integration regression added, **86 tests passed**;
- run 37234235795: receipt update included, **86 tests passed in 0.648 s**;
- `python -m py_compile scripts/*.py`: pass.

Integration regression proves, structurally:

- T005 candidate remains one slide;
- 82 encoded behaviors remain;
- click-beat count = 4;
- clickEffect stage count = 4;
- afterEffect stage count = 2;
- mainSeq contains four direct click-group wrappers.

## Planning heuristic

A stage should normally end a click beat when the resulting state is meaningful
enough that the presenter may speak for an unknown amount of time.

A stage should stay in the same beat when another click would interrupt what the
audience perceives as one continuous action.

Therefore presenter speech time is not encoded as a guessed delay.

## Evidence boundary

This experiment proves the plan schema, XML structure and regressions only.

It does **not** yet prove that Microsoft PowerPoint will execute exactly four
clicks with the intended after/with-previous semantics. T010 remains pending
until the exact v0.2 candidate is generated, hashed, opened in a named Microsoft
PowerPoint version, and each click is observed.

## Next experiment

1. Generate the exact v0.2 T005 candidate through the Work presentation pipeline.
2. Freeze SHA-256.
3. Inspect timing inventory and confirm four click groups.
4. Open the exact file in PowerPoint.
5. Record:
   - click 1 stages;
   - click 2 stages;
   - click 3 focus -> split;
   - click 4 reassemble -> restore;
   - Animation Pane ordering;
   - persistence/fill/path correctness.
6. Then transfer click-beat planning to an existing no-script report rather than
   hard-coding this four-beat recipe.
