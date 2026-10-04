# Existing-deck director contract v0.1

Use this contract after `scripts/inspect_existing_deck.py` and before adding
motion to an existing PPTX.

The director plan is a semantic plan. It does not contain raw PresentationML.

## Root

Required fields:

- `version`: `"0.1"`
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
- `inferred`
- `researched`

Priority is defined in `docs/PRODUCT_TARGET.md`. A lower-priority source may
not silently override a higher-priority source.

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
- `beats`: ordered motion beats;
- `components`: generated helper components, possibly empty.

### Motion beat

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

## Output responsibilities

A model that executes this plan must produce:

1. an edited PPTX;
2. a preservation report comparing source and output;
3. a motion report listing reused resources, generated components and timing;
4. PowerPoint playback evidence before setting native playback to verified.

The plan is not the final artifact.
