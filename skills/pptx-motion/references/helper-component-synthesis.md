# Existing-deck helper component synthesis v0.1

Use this only after an existing-deck director plan proves that a narrative beat
cannot be expressed well with existing resources.

## Goal

Create a small native editable helper component **inside the deck's existing
visual framework**.

v0.1 uses style-donor cloning rather than inventing a new style system.

## Why donor cloning

A source `p:sp` already carries real PowerPoint styling:

- fill;
- line;
- text properties;
- geometry behavior;
- textbox declaration;
- theme bindings.

Cloning that object and changing only identity, geometry and optional text gives
a stronger visual-system match than selecting arbitrary new colors/fonts.

## Root

- `version="0.1"`
- `kind="existing-deck-helper-components"`
- `source_sha256`
- `components`

## Component

Required:

- `source_index`: one-based slide index;
- `donor`: `{"source_id":"...","source_name":"..."}`;
- `new_name`: unique native shape name;
- `role`: narrative role;
- `rationale`: why existing resources are insufficient;
- `data_provenance`: `none`, `derived-from-source`,
  `synthetic-nondata`, or `user-provided`;
- `geometry`: normalized x/y/w/h and optional rotation_deg;
- `text_action`: `preserve`, `clear`, or `replace`;
- `text`: required only for `replace`.

## Constraints

v0.1 only clones a native `p:sp` on the same slide.

Do not use this path to duplicate charts, pictures, SmartArt, media or embedded
objects.

The patcher must:

- freeze exact source hash;
- match donor by local ID + name;
- allocate a new unique local shape ID;
- preserve donor style subtree;
- change only identity, geometry and requested text;
- preserve all other package parts byte-for-byte;
- refuse destination overwrite;
- return a new hash;
- require re-inventory before timing is authored.

## Design choice

The AI should prefer a donor with the closest semantic/visual role:

- focus frame -> existing card/frame;
- temporary label -> existing label/textbox;
- connector-like helper -> existing simple line/block donor where appropriate.

The inventory `design_profile` is evidence for donor selection, but v0.1 does
not automatically choose a donor. That remains a model decision.

After insertion:

1. rerun `inspect_existing_deck.py`;
2. use the new source hash;
3. target the helper by its new native ID + name;
4. apply `patch_existing_timeline.py`.

This keeps component synthesis and animation as explicit, reviewable steps.
