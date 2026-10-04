# Existing-deck native timeline patch contract v0.2

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

- `version`: `"0.2"` for presenter-paced patches; `"0.1"` remains accepted as the legacy one-click baseline
- `kind`: `"existing-deck-timeline-patch"`
- `source_sha256`
- `slides`

The source hash must match the exact PPTX being patched.

## Slide patch

Each slide patch contains:

- `source_index`: one-based slide index;
- `stages`: ordered stage list;
- `click_beats`: required in v0.2 and partitions stage IDs into presenter clicks.

v0.1/v0.2 currently patch only slides with **no existing `p:timing`**. T008 owns safe merge/continuation of pre-existing timing. Existing slide
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

## Preservation

The patcher must:

- reject source hash mismatch;
- reject unknown slide/object targets;
- reject duplicate stage IDs;
- reject invalid v0.2 click-beat partitions or nested `on-click` stages;
- reject target slides that already have timing;
- preserve existing transitions;
- alter only the targeted slide XML parts;
- write atomically and refuse destination overwrite;
- report source/output hashes;
- keep PowerPoint playback status false until exact-file native QA.

Component creation is intentionally outside this low-level contract. T007 should
first create/insert a justified helper component, refresh the inventory, then
target the resulting native object.
