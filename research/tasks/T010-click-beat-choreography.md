# T010 — Presenter-paced Click-Beat Choreography

Status: active research.

Read:

- `docs/PRODUCT_TARGET.md`
- `docs/MOTION_PACKING.md`
- `docs/CLICK_BEAT_CHOREOGRAPHY.md`
- `skills/pptx-motion/references/native-timeline.md`

## Problem

T006 proved that many motions can be packed into one slide, but its first native
writer placed the full sequence in one click group with cumulative delays. That
caused the first click to launch the entire choreography.

The product needs presenter rhythm, not merely slide compression.

## Hypothesis

A native slide can preserve resource-local packing while exposing multiple
presenter-controlled click beats. Each beat can then contain concurrent and
automatic sequential stages.

The planning model is:

`slide -> click beat -> stage -> effects`

## First candidate

Reuse the exact T005/T006 radial-drilldown sequence and resource set.

Expected structure:

- 1 slide;
- 4 click beats;
- 6 semantic stages;
- beat 1: burst;
- beat 2: orbit;
- beat 3: focus -> split;
- beat 4: reassemble -> restore.

No waypoint slide is allowed.

## Writer acceptance

The v0.2 writer must:

1. keep v0.1 one-click output reproducible as a legacy baseline;
2. emit multiple direct click groups under `mainSeq` for v0.2;
3. map beat-first stages to `clickEffect`;
4. map within-beat concurrent stages to `withEffect`;
5. map within-beat sequential stages to `afterEffect`;
6. give every timing node a unique ID;
7. keep build-list references valid;
8. keep all effect behavior delays at zero unless an actual animation delay is
   explicitly part of the script;
9. never use cumulative wall-clock delay to simulate presenter speech.

## Intake acceptance

The existing-deck inspector must expose click-group structure when it can recover
it from `mainSeq`, including target objects and start-node types.

## Narrative acceptance

For a no-script deck, the AI must justify each click boundary by audience meaning,
not merely animation convenience.

At minimum test:

- one overview -> detail slide;
- one comparison slide;
- one process/cause-effect slide.

Human review asks:

- Does each click reveal one coherent idea?
- Does the slide stop at useful explanatory states?
- Is any next reveal exposed too early?
- Does an extra click break a continuous action?

## Evidence boundary

Structural XML and unit tests do not prove native behavior. Exact-file PowerPoint
playback must record:

- how many clicks are required;
- which stages fire per click;
- whether same-beat effects synchronize;
- whether after-previous stages wait for prior motion to finish;
- whether final state persists;
- whether Animation Pane ordering matches the plan.

Do not mark T010 complete until this playback gate passes.
