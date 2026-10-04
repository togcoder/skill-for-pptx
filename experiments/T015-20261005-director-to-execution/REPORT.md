# T015 — Semantic Director to native execution bridge

Date: 2026-10-05 Vietnam.

## Problem closed

Before T015, the repo had:

- semantic chart/KPI decisions in Director v0.3;
- native chart execution in T013;
- native stepped-text KPI execution in T014;

but a model still had to manually author the low-level patch JSON between those
layers.

T015 removes that manual gap for complete data-motion slides.

## Flow

`Inventory -> Director v0.3 -> compile_data_motion_patch -> patch v0.4 -> timing`

Chart semantic beat:

- resolves exact chart source ID/name;
- uses inventory series/category dimensions;
- becomes `chart_entrance`;
- keeps chart type/build/background policy;
- chooses a conservative concrete entrance filter.

KPI semantic beat:

- resolves exact source number shape;
- becomes `number_counter`;
- preserves the source final text;
- carries duration/steps/format;
- explicitly falls back from preferred odometer proxy to the implemented
  stepped-text backend unless fallback is forbidden.

## Presenter rhythm

Director `click_beats.motion_beats` are converted to patch
`click_beats.stages` without merging click boundaries.

The integration fixture contains:

- Click 1: line chart trend;
- Click 2: 98.5% KPI counter.

Timing read-back still exposes two direct presenter click groups.

## Partial compilation policy

T015 deliberately refuses to partially compile a slide containing unsupported
generic motion.

Reason: removing a non-data beat could turn an `after-previous` data beat into a
new click or expose evidence too early. That would violate T010/T011.

Unsupported/mixed slides are blocked instead.

## Test failure retained as a lesson

Initial integration test assumed `build_entries[0]` was `bldGraphic`.

Once chart and counter coexisted, the valid build list also contained KPI/proxy
`bldP` entries, so position was not a semantic identifier.

The test—not production code—was wrong. It was repaired to locate the chart
build by `type=="bldGraphic"` and `spid=="7"`.

This becomes a reusable rule: **never infer build semantics from bldLst order
when heterogeneous object types coexist**.

## Automated evidence

Final temporary GitHub Actions run 37238859486:

- Python compile pass;
- **126 tests passed in 0.339 s**.

## Remaining gate

No exact Microsoft PowerPoint playback has been observed. Structural integration
does not prove runtime chart/counter behavior.

The next decisive evidence is a real PPTX containing both a chart and KPI,
compiled by this bridge, frozen by SHA-256 and played in PowerPoint while
recording click behavior and Animation Pane order.
