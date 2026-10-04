# Click-Beat Choreography Policy

This document is a hard planning rule for presenter-paced motion inside one
PowerPoint slide.

## Core model

A slide is a **scene**. A scene contains one or more **click beats**. A click
beat contains one or more **stages**. A stage contains one or more **effects**.

`Slide -> Click Beat -> Stage -> Effects`

This distinction is mandatory:

- **slide boundary** = semantic scene change;
- **click-beat boundary** = presenter/audience pacing boundary inside the same scene;
- **stage boundary** = ordered automatic motion inside one click beat;
- **effects in one stage** = motions intended to happen together.

Packing many motions into one slide must never mean firing the entire slide from
the first click.

## PowerPoint timing meaning

Use the presenter model exposed by PowerPoint:

- `On Click`: start a new presenter-controlled beat;
- `With Previous`: start together with the previous effect/stage;
- `After Previous`: start automatically after the preceding effect/stage.

Microsoft documents these three start modes in the Animation Pane. Do not replace
an intended click boundary with a guessed delay. The model cannot know how long a
presenter will talk unless the script explicitly gives a timed narration.

## When to start a new click beat

Prefer a new click beat when at least one is true:

- the audience has reached a stable state worth explaining before more information
  appears;
- the next motion answers a new question or changes the audience's focus;
- exposing the next evidence early would weaken the narrative;
- the presenter likely needs an open-ended speaking pause;
- a comparison should be revealed only after the first side is understood;
- a drill-down should begin only after the overview has been discussed;
- the script/storyboard explicitly says "next", "then click", "after explaining",
  or otherwise marks a presenter-controlled reveal.

A beat boundary is about **attention and narration**, not about object identity.
Two beats may reuse exactly the same shapes and still require separate clicks.

## When motions belong in the same beat

Keep motions in one beat when they form one indivisible audience action:

- a focus move immediately followed by unfolding detail;
- an object moves while its label and connector follow;
- several objects rearrange as one comparison;
- a close/reassemble action immediately returns the audience to the overview;
- one visual preparation has no useful stable explanatory state before the next
  automatic transformation.

Within a beat:

- use the same stage / `With Previous` for concurrent changes;
- use a later stage / `After Previous` for automatic sequential changes;
- use a new click beat instead of a long delay when the pause belongs to the
  presenter rather than the animation.

## Stable-state test

Before merging two consecutive stages into one click beat, ask:

> If the animation stopped after the first stage, is that state meaningful enough
> that a presenter may want to talk about it for an unknown amount of time?

If yes, default to a new click beat.

Before splitting a beat, ask:

> Would requiring another click interrupt what the audience perceives as one
> continuous action?

If yes, keep the stages in one beat.

## T005/T006 benchmark reinterpretation

The old T006 packed candidate placed all six operations in one click group:

`burst -> orbit -> focus -> split -> reassemble -> restore`

That is now retained only as a negative/legacy pacing baseline.

The first T010 presenter-paced hypothesis is:

1. **Click 1 — Reveal:** `burst`, then hold for explanation.
2. **Click 2 — Relationship:** `orbit`, then hold.
3. **Click 3 — Drill down:** `focus -> split` automatically.
4. **Click 4 — Close detail:** `reassemble -> restore` automatically.

All four beats remain on **one PowerPoint slide** and reuse the same resource
set. This grouping is a benchmark hypothesis, not a universal recipe.

## Contract rules

For native-timeline v0.2:

- `timeline` remains the flat ordered list of stages for geometry/audit;
- `click_beats` partitions every timeline stage exactly once and in the same order;
- each beat has `id`, `purpose`, ordered `stages`, and optional
  `pause_after`;
- the first stage of every beat must use `trigger="on_click"`;
- later stages in the same beat use `with_previous` or `after_previous`;
- `on_click` may not appear in the middle of a declared beat.

The writer must emit separate click groups under PowerPoint's main sequence rather
than one click group with cumulative delays.

## Existing-deck rule

When reading a deck that already contains animation, recover click groups before
planning changes. Existing click boundaries are first-class choreography evidence.

Do not flatten an authored deck into a single delay-sorted list and then rebuild
it. Preserve its presenter rhythm unless a stronger explicit script justifies a
change.

## Evaluation

Record separately:

- slide count;
- click-beat count per slide;
- stages per beat;
- effects per stage;
- automatic chain depth;
- whether each beat ends at a meaningful stable state;
- whether any click interrupts a continuous action;
- whether any automatic reveal exposes information before the narrative needs it.

A high packing ratio with bad click rhythm is a failure.
