# T007 — Existing source-object timing patcher

Date: 2026-10-04  
Branch: `work/T007-source-object-patcher-20261004`

## Why this step matters

T006 generated decks rely on experimental `!!` semantic names. Real user
PowerPoint files will not.

To reach the product target in `docs/PRODUCT_TARGET.md`, native motion must be
applied directly to the objects already present in a user deck without requiring
the whole deck to be rebuilt or renamed.

## Implemented

### Existing-deck patch contract

`skills/pptx-motion/references/existing-deck-timeline-patch.md`

Targets each existing object by:

- one-based source slide index;
- native slide-local `cNvPr/@id`;
- native `cNvPr/@name`.

The plan also freezes the exact source PPTX SHA-256.

### Native source-object patcher

`scripts/patch_existing_timeline.py`

v0.1 supports:

- `motion_path`;
- `scale` by authored-size factors;
- `rotate`.

It:

- rejects source hash mismatch;
- verifies both native ID and name;
- uses one packed click group and cumulative stage delays;
- preserves slide transitions;
- refuses target slides with pre-existing `p:timing` instead of blindly merging;
- changes only targeted slide XML parts;
- writes atomically;
- never claims PowerPoint playback verification.

### Design fingerprint

The existing-deck intake now also extracts a deck design profile:

- font families;
- fill colors;
- line colors;
- text colors;
- preset geometries.

This is the first concrete basis for the user's requirement that newly generated
helper components remain inside the existing deck's visual framework.

## Failure retained

The first non-`!!` regression attempted to rename the first generic
`cNvPr` in the slide XML. That node belonged to slide-tree/container metadata,
not the first actual shape, so the expected source object was not renamed.

The fixture was corrected to target
`p:cSld/p:spTree/p:sp/p:nvSpPr/p:cNvPr`. No patcher rule was relaxed.

## Automated evidence

Temporary branch-only GitHub Actions workflow, removed before integration.

Final successful run:

- Run ID: `37214809106`
- Job ID: `111473050411`
- `python -m py_compile scripts/*.py`: pass
- `python -m unittest discover -s tests -v`: **73 tests passed in 0.485 s**

New source-patcher regressions establish:

1. an existing source object can receive native timing;
2. the untargeted second slide remains byte-identical;
3. a plain object name with no `!!` prefix can be patched;
4. wrong source SHA-256 fails;
5. wrong native object name fails;
6. an already-timed slide is not merged blindly;
7. the deck intake exposes a nonempty design fingerprint.

## Evidence boundary

This establishes package-preserving source-object targeting and structural timing
insertion.

It does **not** establish:

- actual Microsoft PowerPoint playback for the patched H001 sample;
- merging with arbitrary pre-existing animation trees;
- adding missing helper components yet;
- automatic director-plan -> low-level patch-plan translation;
- autonomous report-script quality.

## Next step

The highest-value next layer is the semantic bridge:

`director plan -> concrete source-object patch plan`

It should:

- take a validated T007 director plan;
- map semantic beats to supported native motion recipes;
- select existing source objects first;
- consult the design fingerprint before creating helper components;
- emit a low-level patch plan using native source IDs/names;
- request component synthesis only when a beat has a real resource gap.

A separate component-insertion path should then add native editable helper
objects, refresh the inventory/hash, and feed the resulting source back into the
source-object patcher.
