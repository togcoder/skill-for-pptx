# Existing-deck director contract v0.4

Use this contract after `scripts/inspect_existing_deck.py` and before adding
motion to an existing PPTX.

## Source package baseline

Run the host package-integrity validator before editing and retain the source
findings. A final candidate must not inherit a defect silently or misreport an
inherited defect as a motion failure.

If, and only if, the source findings are stale `[Content_Types].xml` overrides
for ZIP members that do not exist, keep the original source for inventory and
hash-bound patching, then repair the patched candidate copy with
`scripts/repair_stale_content_types.py` before finalization. Record the original
source hash, pre-repair candidate hash, repair receipt and repaired hash
separately. The utility may change only
`[Content_Types].xml`; it is not a repair for missing relationships, layouts,
masters or media. Plan and preservation evidence remain grounded in the
original source inventory.

The director plan is a semantic plan. It does not contain raw PresentationML.

## Root

Required fields:

- `version`: `"0.4"` for generic + data semantic motion plans; `"0.3"` remains the data-motion baseline, `"0.2"` click-rhythm, and `"0.1"` legacy flat-beat
- `kind`: `"existing-deck-motion-director"`
- `source`
- `user_instruction`
- `script`
- `preservation`
- `slides`
- `target_slide_count`
- `research_metadata`

## Source

`source`:

- `pptx_sha256`
- `inventory_version`
- `source_slide_count`

The source hash must match the inventory used to make the plan.

## Script

`script.source` is exactly one of:

- `provided`
- `speaker-notes`
- `existing-timing`
- `inferred`
- `researched`

Priority is defined in `docs/PRODUCT_TARGET.md`. A lower-priority source may
not silently override a higher-priority source. `existing-timing` means the
deck's current native animation/transition sequence is primary planning evidence;
preserve it unless the plan contains an explicit justified override.

`script` also includes:

- `summary`: concise report/story sequence;
- `evidence`: nonempty list describing what grounded the script;
- `beats`: deck-level ordered narrative beats.

When source is `researched`, `research_metadata.sources` must be nonempty.
Research may establish reporting structure or public facts, but must not invent
or overwrite user data.

## Preservation

Required booleans:

- `preserve_text_by_default`
- `preserve_media_by_default`
- `preserve_theme_by_default`
- `preserve_slide_order_by_default`

`slide_count_policy` must be `"preserve"` or `"explicit-change"`.

Default is preserve.

## Slide plans

Each entry has:

- `source_index`: one-based source slide index;
- `role`: semantic role in the report;
- `objective`: what the audience should understand after the slide;
- `beats`: ordered motion/action beats;
- `click_beats`: presenter-controlled groups that partition the motion beats;
- `components`: generated helper components, possibly empty.

### Motion beat

A motion beat is an action, not necessarily a presenter click.

Each beat requires:

- `id`
- `purpose`
- `operation`
- `targets`: list of source object names/semantic IDs
- `reuse_existing`: boolean
- `same_slide`: must be true for v0.1
- `timing_intent`: `on-click`, `with-previous`, or `after-previous`

A target must exist in the source slide inventory unless it names a component
created on that slide.

Do not use a beat whose only purpose is decorative motion.

### Data motion

v0.3 treats charts and highlighted standalone KPI numbers as semantic resources,
not generic shapes.

A motion beat that targets a chart must contain `data_motion`:

- `kind="chart"`;
- `chart_type`: copied from the source inventory;
- `recipe`: type-specific semantic recipe;
- `build`: `as-whole`, `series`, `category`, `series-elements`, or
  `category-elements`;
- `animate_background`: boolean, default false unless the narrative needs axes /
  grid / legend to enter too;
- `rationale`: why this recipe fits the chart's meaning;
- optional `override_reason` when intentionally departing from the type-specific
  recommendation.

Read [data-motion-recipes.md](data-motion-recipes.md) and use
`scripts/data_motion_recipes.py`.

A standalone numeric shape is only a **counter candidate**. Do not count page
numbers, dates, table cells, axis labels, or every numeric label merely because
they are numeric.

When the Director chooses a standalone number as a hero metric / KPI highlight,
its motion beat must contain `data_motion`:

- `kind="number-counter"`;
- `recipe="count-up"` or `"count-down"`;
- `from_value`, `to_value`;
- `duration_ms`, `steps`;
- `prefix`, `suffix`, `decimal_places`;
- `implementation`: `odometer-proxy` or `stepped-text`;
- `rationale`: why this number deserves a counter instead of ordinary emphasis.

The final visible text must remain exactly the source metric text unless the user
explicitly requested a data/content change.

Chart animation or number counting never creates its own click automatically.
It belongs to the click beat chosen by the narrative Director.

### Generic report motion — v0.4

Ordinary source objects use a deliberately small semantic vocabulary before
expanding to low-level timing:

- `reveal`: one or more objects appear together/in order;
- `stagger-reveal` / `process-reveal`: ordered targets appear automatically
  inside one presenter click;
- `focus` / `emphasize`: one source object pulses in place via scale-up then
  scale-down;
- `move`: one source object follows explicit `motion_parameters.points`;
- `rotate`: one source object rotates by explicit
  `motion_parameters.by_deg`.

Read `scripts/generic_motion_recipes.py`.

Rules:

- chart targets still require chart `data_motion`; generic reveal is not a
  backdoor to treat charts as plain shapes;
- focus/emphasize/move/rotate require exactly one target;
- reveal/process operations preserve the supplied target order;
- move and rotate never guess destination/angle in the low-level compiler;
- one semantic beat may expand to multiple automatic stages while preserving one
  presenter click;
- generic motion must not introduce helper components unless the Director plan
  separately justifies them.

### Click beat

For v0.2 every slide also requires `click_beats`. A click beat is the unit of
presenter pacing and contains one or more motion-beat IDs.

Each click beat requires:

- `id`
- `purpose`: the audience idea advanced by this click;
- `motion_beats`: ordered IDs from the slide's `beats`;
- `stable_state`: why the state after this click is meaningful to hold;
- `pause_after`: one of `presenter-explanation`, `await-next-reveal`,
  `slide-complete`, or `none`;
- `boundary_reason`: required from the second click onward; explain why this
  content must wait for a new presenter click instead of automatically following.

Rules:

- click beats partition every motion beat exactly once and preserve beat order;
- the first motion beat inside each click beat must use `on-click`;
- later motion beats in that click beat use `with-previous` or
  `after-previous`;
- a presenter speaking pause is a click boundary, not an animation delay;
- if a state has no useful audience meaning, do not create a click merely because
  authoring it is convenient.

Use the stable-state test from `docs/CLICK_BEAT_CHOREOGRAPHY.md`.

### Generated component

Each component requires:

- `id`
- `role`
- `rationale`
- `native_kind`: `shape`, `text`, `connector`, or `derived-visual`
- `style_basis`: how it matches the existing deck;
- `data_provenance`: one of:
  - `none`
  - `derived-from-source`
  - `synthetic-nondata`
  - `user-provided`

A component is invalid if its rationale says only that it makes the slide more
beautiful or more impressive. It must fill a narrative/interaction role.

## Slide-count rule

`target_slide_count` must equal the source slide count when
`slide_count_policy="preserve"`.

If slide count changes, each added/removed slide must have an explicit semantic
reason in `research_metadata.slide_count_changes`. Animation convenience is not
a valid reason.

## Autonomy and existing-motion rules

The model may receive no animation script. It must still create a defensible
report sequence from deck evidence and may research the reporting pattern when
needed and allowed.

If the inventory reports existing native timing, the plan must not assume a
fresh slide. Current animation is a source resource to understand and continue.
Destructive replacement requires an explicit reason.

## Output responsibilities

A model that executes this plan must produce:

1. an edited PPTX;
2. a preservation report comparing source and output;
3. a motion report listing reused resources, generated components and timing;
4. PowerPoint playback evidence before setting native playback to verified.

The plan is not the final artifact.
