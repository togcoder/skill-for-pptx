# Existing-deck native timeline patch contract v0.5

This contract is the low-level bridge between a semantic motion-director plan and
an existing PPTX package.

It exists because real user decks do not have the experimental `!!` names used
by T005/T006 generated decks.

## Principle

Do not rename or rebuild source objects merely to animate them.

Target an existing object by the tuple:

- source slide index;
- native slide-local `cNvPr/@id`;
- native `cNvPr/@name`.

The ID is local to that slide. The name is an additional guard, not a global
identity.

## Root

- `version`: `"0.5"` for generic + chart + KPI patches; `"0.4"` remains counter-capable, `"0.3"` chart-capable, `"0.2"` click-beat, and `"0.1"` legacy one-click
- `kind`: `"existing-deck-timeline-patch"`
- `source_sha256`
- `slides`

The source hash must match the exact PPTX being patched.

## Slide patch

Each slide patch contains:

- `source_index`: one-based slide index;
- `stages`: ordered stage list;
- `click_beats`: required in v0.2+ and partitions stage IDs into presenter clicks.

v0.1–v0.4 currently patch only slides with **no existing `p:timing`**. T008 owns safe merge/continuation of pre-existing timing. Existing slide
transitions are preserved. Untargeted slide/package bytes must remain unchanged.

## Stage

- `id`
- `duration_ms`
- `trigger`: `on-click`, `with-previous`, or `after-previous`
- `effects`

For v0.1, the historical behavior remains one native click group with cumulative
delays.

For v0.2:

- every click beat's first stage is `on-click`;
- later stages in that click beat use `with-previous` or `after-previous`;
- click beats partition all stages in exact order;
- the writer emits one direct `mainSeq` click group per click beat;
- effect behavior delays remain zero unless a real animation delay is explicitly
  authored.

Do not use delays to approximate presenter speaking time.

## Target

Every effect contains:

`"target": {"source_id": "12", "source_name": "Revenue Card"}`

Both values must match the exact source slide. Do not rely on name alone.

## Effects

### motion_path

- `type="motion_path"`
- `points`: 2+ normalized slide coordinates

The points describe target-center positions and are converted to a relative
PowerPoint motion path.

### scale

- `type="scale"`
- `from_x`, `from_y`, `to_x`, `to_y`: positive scale factors

`1.0` means authored size, `1.2` means 120%.

### rotate

- `type="rotate"`
- `by_deg`: finite degree delta

### chart_entrance — v0.3

Targets must be an actual top-level chart graphicFrame in the source slide.

Required fields:

- `type="chart_entrance"`
- `target`
- `chart_type`
- `build`: `as-whole`, `series`, `category`, `series-elements`, or
  `category-elements`
- `series_count`
- `category_count` when the build needs categories
- `animate_background`
- optional `filter`; otherwise the writer chooses a conservative type-specific
  entrance filter
- optional `fanout_limit`, default 24

For a per-element build the writer expands one semantic effect into
`p:graphicEl/a:chart` sub-targets using `seriesIdx`, `categoryIdx`, and
`bldStep`.

The build list uses `p:bldGraphic`; non-whole builds contain
`p:bldSub/a:bldChart`. The writer records both requested and effective build
mode.

If fan-out exceeds the configured limit, the writer degrades granularity instead
of creating an unbounded number of animation behaviors. This is an execution
safety rule, not permission to change the chart's data.

### number_counter — v0.4

Targets must be an existing top-level text shape.

Required fields:

- `type="number_counter"`
- exact source `target`
- `from_value`, `to_value`
- `steps`: 2..30
- `decimal_places`: 0..8
- `prefix`, `suffix`
- `preserve_final_text`: exact source textbox text
- optional entrance/exit `filter`, default `fade`

The writer clones the source textbox for intermediate values, preserving its
shape geometry/style. Proxy IDs/names are new and unique. The original source
textbox is never rewritten.

Within one presenter click beat:

1. proxy values enter/exit automatically;
2. the untouched source textbox enters last;
3. the final state therefore uses the user's original object/value.

This is a synthesized stepped-text counter, not a claim of native PowerPoint
numeric interpolation.

### shape_entrance — v0.5

Use for ordinary non-chart source objects.

- `type="shape_entrance"`
- exact source `target`
- `filter`: one verified `p:animEffect` filter such as `fade` or directional
  `wipe(...)`

Charts are rejected on this path and must use `chart_entrance`.

A semantic reveal may compile to several `shape_entrance` stages inside one
presenter click. The first stage inherits the motion beat trigger; later stages
normally use `after-previous`.

## Preservation

The patcher must:

- reject source hash mismatch;
- reject unknown slide/object targets;
- reject duplicate stage IDs;
- reject invalid v0.2/v0.3 click-beat partitions or nested `on-click` stages;
- reject `chart_entrance` against non-chart source objects;
- record density-guard degradation for chart fan-out;
- reject counter source-text drift before cloning;
- preserve the original final KPI textbox and report all generated proxies;
- reject target slides that already have timing;
- preserve existing transitions;
- alter only the targeted slide XML parts;
- write atomically and refuse destination overwrite;
- report source/output hashes;
- keep PowerPoint playback status false until exact-file native QA.

Component creation is intentionally outside this low-level contract. T007 should
first create/insert a justified helper component, refresh the inventory, then
target the resulting native object.
