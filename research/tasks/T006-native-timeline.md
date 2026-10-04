# T006 — Native timed paths, single-slide packing and choreography

Status: active implementation. Native planning compiler + restricted timing writer implemented; PowerPoint playback gate pending. Owner: current integrator/model. Check open PRs/claims before starting implementation work.

User priority: advanced effects from a short natural-language prompt that keep
all requested actions and constraints **while packing as many motions as possible
into one slide when they reuse the same resources**. Read
`docs/MOTION_PACKING.md` before implementation.

T005 proves restricted intent/geometry, but its state-per-slide Morph strategy
is now a legacy baseline. It requires many clicks and over-expands slide count.
The target architecture treats a slide as a scene/execution container, not a
motion frame.

## Frozen hypothesis

A native timed timeline can replace most or all T005 waypoint/state slides when
the same persistent objects are reused. Motion paths, rotation, scale, emphasis,
visibility, sequencing, delay, trigger and synchronization should be expressed
as tracks on the same slide where PowerPoint supports them.

The first T006 candidate must attempt this exact compression:

- semantic sequence: burst -> orbit -> focus -> split -> reassemble -> restore;
- same persistent object/resource set as T005 where practical;
- target: **1 PowerPoint slide** containing the full sequence;
- no extra slide merely for an orbit waypoint, intermediate pose, emphasis step,
  split step or restore step;
- if one slide is impossible, document the verified blocker and use the minimum
  slide count, with a reason for every boundary.

Orbit sampling may still exist internally for path construction or validation,
but samples must not become PowerPoint slides by default.

## Research requirements

Study authoritative OOXML/PowerPoint documentation and an actually viewed source
effect; log which media was observed and its rights. Work in an isolated
backend/experiment. Do not silently change the current Morph-only renderer or
allow `add_morph` to overwrite existing timing. Preserve all historical
baselines.

Define trigger, dependencies, duration, easing, target mapping and end state
explicitly. Separate unsupported visual demands from fallback choices. Prefer
native editable mechanisms. If a requested effect can share the same asset
instances, do not duplicate those assets merely to simplify implementation.

## Required metrics

Record for candidate and transfer:

- semantic scene count;
- final slide count;
- requested motion-event count;
- packed motion-event count per slide;
- resource-set changes;
- packing ratio = requested motion events / final slide count;
- each technical/semantic reason for a slide boundary.

Packing ratio is diagnostic only; do not merge unrelated scenes or sacrifice
readability/editability merely to increase it.

## Acceptance

1. Structural schema/parity checks pass.
2. Render every final slide and inspect static states.
3. Actual PowerPoint playback is captured against the exact file hash and named
   PowerPoint version before claiming native behavior.
4. Intermediate overlap, pauses, sequence/target fidelity and editability are
   assessed.
5. T005 compression is compared against its legacy multi-slide baseline.
6. A fresh compound prompt transfers the packing policy; it must not regress to
   one-motion/one-slide without a documented blocker.
7. A genuinely different multi-track effect is tested, not just different node
   counts.
8. Without native runtime, prepare code/fixtures/capture instructions and keep
   native acceptance pending; HTML/video simulations do not replace the gate.
9. A video fallback may be offered only with its lost editability clearly stated.

The guiding question for every slide boundary is: **what changed that requires a
new slide rather than another track on the current slide?**


## 2026-10-04 implementation checkpoint

Implemented on the T006 native-timing writer branch:

- `scripts/add_timeline.py`: restricted PresentationML timing writer for motion,
  scale and rotate;
- `scripts/validate_timeline.py`;
- `scripts/normalize_timeline_textboxes.py`;
- `scripts/render_timeline.mjs`;
- `scripts/run_timeline_experiment.sh`;
- `tests/test_timeline_writer.py`;
- experiment report at
  `experiments/T006-20261004-native-timing/REPORT.md`.

Branch-only GitHub CI ran 55 tests successfully and passed Python compile,
Node syntax and shell syntax checks. The temporary workflow was removed.

The acceptance gate remains unchanged: do not mark T006 complete until the full
one-slide candidate has a frozen hash and actual Microsoft PowerPoint playback
evidence. If the packed-delay scheduling differs in PowerPoint, keep one slide
and compare an authored-style afterEffect/withEffect timing hierarchy before
introducing any slide boundary.
