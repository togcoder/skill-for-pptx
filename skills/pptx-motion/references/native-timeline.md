# Native timeline contract v0.2

This contract is the first executable planning layer for T006. It is intentionally
separate from the legacy Morph plan contract.

## Goal

Represent many motions on the same PowerPoint slide when they reuse the same
resources. A slide is a scene/execution container. Timeline stages are not slides.

Microsoft documents that slide animations are time-based and stored in the
slide's timing tree, that motion paths target objects on the current slide, and
that multiple animation effects can be applied to one object with start modes
such as On Click, With Previous, and After Previous.

Primary sources inspected 2026-10-04:

- https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation
- https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/498c3cfa-652c-49b3-a82c-33fd94468af8
- https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/894705b6-9655-49e3-a6c6-54600f99f7f4
- https://support.microsoft.com/en-us/powerpoint/apply-multiple-animation-effects-to-one-object
- https://support.microsoft.com/en-us/powerpoint/add-a-motion-path-animation-effect

These sources establish mechanism availability, not that this repository already
authors valid native timing XML. Real PowerPoint playback remains a separate gate.

## Root

UTF-8 JSON:

- `version`: `"0.1"`
- `kind`: `"native-timeline-plan"`
- `brief`: verbatim user intent
- `canvas`: same normalized 16:9 convention as the Morph plan
- `data_provenance`: `none`, `synthetic`, or `user-provided`
- `objects`: semantic object definitions with stable IDs
- `slides`: semantic scenes
- `research_metadata`: packing/evidence metadata

## Slide

Each slide contains:

- `id`
- `message`
- `initial_objects`: object geometry at slide entry
- `timeline`: ordered stage list

Every object referenced by an effect must exist in `objects` and
`initial_objects` for that slide. Reusing an object across stages must not
create a new semantic ID.

## Stage

A stage is an ordered motion event inside one slide:

- `id`
- `operation`: semantic operation such as `burst`, `orbit`, `focus`
- `trigger`: `on_click`, `with_previous`, or `after_previous`
- `duration_ms`: positive integer
- `effects`: one or more effects

v0.1 used only one `on_click` stage and chained the rest automatically. That is
now a legacy pacing baseline.

v0.2 adds `click_beats` at slide level. Each click beat partitions one or more
timeline stages:

- first stage of a beat: `on_click`;
- concurrent continuation: `with_previous`;
- automatic serial continuation: `after_previous`.

Every timeline stage appears in exactly one beat and in the same order. The
writer must not replace beat boundaries with cumulative delays.

## Effect

v0.1 planning effects:

### motion_path

- `type`: `"motion_path"`
- `target`: object ID
- `points`: 2+ normalized center points, in execution order
- `path_kind`: `"polyline"` for the first implementation

Intermediate orbit samples are points in this list, **not slides**.

### scale

- `type`: `"scale"`
- `target`
- `from_w`, `from_h`, `to_w`, `to_h`: positive normalized sizes

This can run concurrently with a motion path on the same target during a stage.

### rotate

- `type`: `"rotate"`
- `target`
- `from_deg`, `to_deg`

### visibility

Reserved for the native backend. Use only when the resource already exists on
the slide and visibility, entrance, or exit is the intended behavior. Do not use
it to hide a resource-set change.

## Packing metadata

Record at minimum:

- `semantic_scene_count`
- `legacy_state_count` when comparing a Morph baseline
- `final_slide_count`
- `requested_motion_events`
- `packed_motion_events`
- `packing_ratio`
- `resource_set_changes`
- `native_playback_verified`

The first T006 target for radial drill-down is one semantic scene, one slide,
six requested/packed operations, zero resource-set changes, and native playback
unverified until exact-hash PowerPoint evidence exists.

## Current writer v0.1 / v0.2

`scripts/add_timeline.py` maps the contract to restricted PresentationML timing
for `motion_path`, `scale`, and `rotate`.

- v0.1 is retained as the historical one-click cumulative-delay writer.
- v0.2 emits multiple presenter click groups under `mainSeq`.
- each beat-first stage uses `clickEffect`;
- later stages use `withEffect` or `afterEffect`;
- effect behavior delays are zero unless a real animation delay is explicitly
  planned.

Both versions keep stages inside the same slide instead of manufacturing
waypoint slides.

The writer maps stable semantic `!!` names to local PowerPoint shape IDs,
requires exact identity parity, emits unique timing-node IDs and build-list
pairs, refuses pre-existing timing, and patches atomically. `visibility` is
deliberately rejected in v0.1.

This scheduling model is still experimental. Structural/package checks and
LibreOffice loadability do not establish that PowerPoint will preserve every
delay/trigger exactly. If playback differs, compare a PowerPoint-authored
afterEffect/withEffect hierarchy before considering extra slides.

## Boundary

This contract and writer do not by themselves prove faithful native animation.
The exact final PPTX must pass package checks and then be opened and played in a
named Microsoft PowerPoint version against its frozen hash. Until that gate,
`native_playback_verified` stays false.
