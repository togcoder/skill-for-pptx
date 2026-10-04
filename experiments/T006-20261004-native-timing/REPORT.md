# T006 — Packed native timing writer

Date: 2026-10-04  
Branch: `work/T006-native-timing-writer-20261004`  
Base: `b2ef10df6ed463a8b26e8c999b6e0b237ed781cf`

## Problem

T005 represented a compound animation as many Morph slides. The user explicitly
requires the opposite architecture when the resources are shared: keep the
semantic scene on one slide and pack as many motions as PowerPoint can reliably
execute on that slide.

PR #4 established that policy and PR #6 added a 12-state -> 1-slide planning
compiler. T006 here tests the next missing layer: can the abstract packed
timeline be serialized into real PresentationML timing nodes without returning
to waypoint slides?

## Frozen hypothesis

For one semantic scene whose objects already exist, a single PowerPoint
`clickEffect` group can contain multiple motion/scale/rotation behaviors.
Cumulative behavior delays can serialize semantic stages while behaviors with
the same delay execute concurrently. Orbit samples remain points in one
`animMotion` path instead of slide boundaries.

This is a hypothesis about native playback until verified in Microsoft
PowerPoint. It is not promoted solely from schema/package checks.

## Implementation

### `scripts/add_timeline.py`

Research writer v0.1:

- maps stable semantic names such as `!!node-3-layer-1` to the slide-local
  numeric `spid`;
- requires the source shape identity set to match the timeline plan exactly;
- rejects a source slide that already contains `p:timing`;
- emits one `tmRoot`, one `mainSeq`, one click bucket and one packed
  `clickEffect` group per semantic slide;
- assigns a unique timing-node ID to every emitted behavior;
- schedules stages with cumulative delays;
- runs same-stage behaviors concurrently;
- serializes motion waypoints inside one relative `animMotion path`;
- emits `animScale` with explicit from/to percentages relative to the authored
  initial size;
- emits `animRot` using PowerPoint angle units;
- emits unique `bldP` pairs for each animated shape and packed group;
- patches the PPTX atomically and refuses to overwrite an existing destination;
- deliberately rejects `visibility` instead of guessing a playback-sensitive
  representation.

### End-to-end source pipeline

New files:

- `scripts/validate_timeline.py`
- `scripts/normalize_timeline_textboxes.py`
- `scripts/render_timeline.mjs`
- `scripts/run_timeline_experiment.sh`

The pipeline is:

`native-timeline-plan -> initial native slide(s) -> textbox normalization ->
add_timeline.py -> host finalizer`.

For the current radial-drilldown candidate the target remains **one semantic
slide**.

## Local package prototype

Before committing the production writer, a synthetic one-slide/two-shape PPTX
was patched with a two-stage compound timing group:

1. two motion paths at delay 0 ms;
2. one motion path plus one scale effect at delay 1000 ms.

Evidence:

| Check | Result |
|---|---|
| Source SHA-256 | `d85f4d19e83ba2fa824dfdbfc56e1228905faae8739fa1d0686af9452d72afbe` |
| Patched SHA-256 | `5a1517f1b25edd5ab5a143d0d07234d299afead4ed6d5335ee1b601204dffe1b` |
| ZIP CRC | pass |
| python-pptx reopen | 1 slide / 2 shapes |
| LibreOffice headless open/export | pass |
| Microsoft PowerPoint playback | **not tested** |

LibreOffice and python-pptx only establish lower-tier package/loadability
confidence. They are not a substitute for PowerPoint animation playback.

## Automated evidence

A temporary branch-only GitHub Actions workflow was used and removed before
integration.

### Run 1

Run ID: `37213165567`  
Job ID: `111468258362`

- full repository tests: **55 passed**
- includes T006 packing and timing-writer tests
- no failures/errors

### Run 2

Run ID: `37213501515`  
Job ID: `111469248904`

- `python -m py_compile scripts/*.py`: pass
- `python -m unittest discover -s tests -v`: **55 passed in 0.319 s**
- `node --check scripts/render_timeline.mjs`: pass
- `bash -n scripts/run_timeline_experiment.sh`: pass

The CI workflow was deliberately deleted afterward so this experiment does not
silently introduce permanent CI infrastructure.

## Structural test coverage added

`tests/test_timeline_writer.py` checks:

- multiple orbit/path points remain inside one motion behavior;
- one click group with cumulative stage delays;
- scale percentages are calculated relative to initial authored size;
- rotation uses 60,000ths of a degree;
- baseline + packed-group build-list entries are emitted per animated shape;
- timing-node IDs are unique;
- semantic-name/spid mismatches fail;
- unsupported visibility fails explicitly;
- duplicate timing IDs are detected by the structural inspector.

Existing packing tests still assert:

- T005 candidate: **12 legacy states -> 1 slide / 6 stages**;
- transfer: **10 legacy states -> 1 slide / 6 stages**;
- orbit waypoints become path points, not slides;
- focus can combine motion + scale on the same persistent resource.

## Source research

Primary mechanism claims are grounded in Microsoft Open XML / PowerPoint
documentation. Detailed URLs and interpretation are stored in:

- `research/claims/T006-single-slide-native-timeline.md`
- `research/claims/T006-timing-writer-evidence.md`

A public animation corpus was inspected as an empirical cross-check for
PowerPoint-authored timing-tree shapes and known silent-failure patterns. No
third-party source/runtime is vendored; the writer is independently implemented.

## What this experiment establishes

Established:

- the project no longer needs slide waypoints at the planning layer;
- a restricted native timing writer now exists;
- the same slide can structurally carry multiple packed stages and concurrent
  effects;
- current repository regressions remain green;
- a patched prototype remains a loadable PPTX package;
- the end-to-end Work-runtime source/finalization path is implemented in code.

Not established:

- that Microsoft PowerPoint accepts and plays this exact packed timing tree
  without repair;
- that cumulative delays inside one compound click group reproduce every
  `After Previous` behavior identically across PowerPoint versions;
- real perceived smoothness/easing;
- native editability of the exact final candidate in the PowerPoint animation
  pane;
- support for visibility/entrance/exit, arbitrary triggers, audio/video or 3D.

## Highest-value next experiment

Generate the full T005 candidate through the new pipeline:

```bash
python3 scripts/pack_timeline.py \
  experiments/T005-20261004-codex-choreography/candidate.intent.json \
  experiments/T006-20261004-native-timing/candidate.timeline.json

bash scripts/run_timeline_experiment.sh \
  experiments/T006-20261004-native-timing/candidate.timeline.json \
  build/T006-candidate \
  output/T006_packed_candidate.pptx
```

Then freeze the exact SHA-256 and open/play that exact file in a named Microsoft
PowerPoint version. Record repair warnings, one-click sequencing, each stage,
intermediate overlap, final pose and Animation Pane editability.

If native playback fails, do **not** fall back to waypoint slides immediately.
First compare the packed-delay tree with a more PowerPoint-authored
`afterEffect/withEffect` hierarchy while keeping one slide and the same
resource set.
