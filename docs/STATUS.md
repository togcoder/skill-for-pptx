> **Since T040 this page is the pptx domain's status.** Lab-wide state lives in
> `HANDOFF.md` and `domains/README.md`; how agents work is in `lab/PROTOCOL.md`.

# Status — current state (2026-11-03, after T055)

This page is rewritten, not appended. History is in [CHANGELOG.md](CHANGELOG.md),
task IDs in [research/tasks/INDEX.md](../research/tasks/INDEX.md), and the
evidence vocabulary in [VERIFICATION.md](VERIFICATION.md).

## Where the code is

- **`main`:** `f648ace`, T053 merged. 448 tests passed at that point.
- **`work/T054-opencode-vector-match`:** `b387146`, **review requested**.
  Comparison-first vector match + SolidCraft CSG blockout. Still axonometric.
- **`work/T055-opencode-pptx-3d`:** claim `64d6d47` plus the T055 work,
  **review requested**, stacked on T054. Native 3D product deck.
- **Current tree:** 469 tests OK, 8 skipped; `lab/tools/check_layout.py` passes.
- Merge order is T054 first; T055 reuses the T054 blockout and must be rebased
  on the accepted T054 state.

## Product paths

| Path | Entry point | For | Skill / command |
|---|---|---|---|
| Motion Director | `scripts/motion_director.py` (`inspect → draft → apply/auto → preview → verify → critique`) | Existing decks: script-driven click rhythm, compound and layered motion, preserving the source | `skills/pptx-motion-director`, `/animate-deck` |
| Morph Studio | `scripts/morph_studio.py` (`propose → apply → preview`) | Cross-slide Morph: `!!` continuity, fly-in staging, camera, card expand, pan | same skill |
| Slide Forge | `scripts/slide_forge.py` (`schema → build → qa → render`) | New decks from a semantic spec: layout, type, themes, assets, motion | `skills/slide-forge`, `/forge-deck` |
| Design system + critic | `knowledge/design_system.json`, `scripts/design_critic.py` | One set of numbers for generating and judging beauty and technique | `docs/DESIGN_SYSTEM.md` |
| Native 3D product deck (experimental) | `experiments/T055-20261103-opencode-pptx-3d/inputs/build_product_deck_v3.py` | Embedded GLB + native callouts + camera views; `Shapes.Add3DModel` | T055 report |

The north star is unchanged: an AI Motion Director for existing decks
([PRODUCT_TARGET.md](PRODUCT_TARGET.md)). Forge is the second entry mode, for
decks that do not exist yet. T055 is a third entry mode under review: a native
3D product explainer.

## Capability × evidence

The evidence ladder is defined in [VERIFICATION.md](VERIFICATION.md). Columns:

- **Struct**: structural checks.
- **Sim**: simulated preview.
- **LO**: LibreOffice reads the effects or renders the slides.
- **PPT-parse**: PowerPoint parsed the effects (EffectType or effect count).
- **PPT-render**: PowerPoint rendered the deck (PDF, PNG, CreateVideo).
- **Interactive**: played in a live slideshow with clicks.

| Capability | Struct | Sim | LO | PPT-parse | PPT-render | Interactive |
|---|---|---|---|---|---|---|
| Canonical timing writer, click groups, after-previous chains | ✓ (T019) | ✓ | ✓ | ✓ (T029: 122 effects) | ✓ (T025, T027) | – |
| Text builds, chart series builds, KPI counters | ✓ | ✓ | ✓ | partly | ✓ Forge decks (T025) | – |
| Compound recipes (assemble, spotlight, cycle, swap, travel, zoom-focus, rise) | ✓ (T023, T028) | ✓ | ✓ | ✓ (cinematic showcase, T029) | partly (T032: 3D carousel, cascade) | – |
| Layers: halo, rail, token, orbit ring, loops | ✓ (T024a) | ✓ | ✓ | ✓ (loops, T024b) | ✓ Ken Burns and float (T024b) | – |
| Library presets `ppt:<name>` (198) | ✓ | – | – | ✓ 7/7 EffectType (T027) | ✓ dynamic style (T027) | – |
| Morph continuity, `!!` chains, staging, scenes | ✓ (T028) | ✓ simulated Morph | Fade fallback only | – | Forge `!!orb` Morph rendered (T025) | – |
| Script layer: provided, paraphrased, generated scripts; notes | ✓ (T024a) | – | – | – | – | Presenter View not checked |
| Shape-click triggers | ✓ (T032) | – | – | – | CreateVideo cannot click | – |
| Design-system tokens in generators (easing, durations, contrast) | ✓ (T034) | ✓ (simulator uses PowerPoint easing) | ✓ frame metrics | – | – | – |
| Design critic | ✓ (T034) | – | ✓ frames match PowerPoint renders (Spearman 0.99) | – | ✓ reads PowerPoint render strips | – |
| **Native 3D: embedded GLB, Type-30 shape, camera/rotation persistence** | ✓ (T055: 10 tests) | – | – | ✓ (T055: 3 models, 3 slides) | ✓ (T055: PDF + PNG) | Rotation not played |
| **Native 3D: editable callouts, focus boxes, spec rows** | ✓ (T055) | – | – | ✓ (T055 audit) | ✓ (T055 PDF) | – |
| **Native 3D: Morph between camera views** | ✓ XML accepted (T055) | – | – | EntryEffect 3954 | not verified | – |

"–" means no evidence. The native interactive gate is still open: no deck has
been played click-by-click in a live PowerPoint session and reviewed by a human.

## T055 native 3D — what is actually proven

- `Shapes.Add3DModel` inserts an embedded GLB as shape **Type 30**.
- Camera, look-at, rotation and FOV survive save and reopen.
- Three slides, one model each, three embedded `model3d*.glb` copies.
- Source GLB is Y-up metres, 400 × 553 × 326 mm, 34 non-metallic material
  regions; the embedded copies are semantically identical.
- PowerPoint opens the exact file and exports a 252 KB PDF.
- Callouts, focus boxes and spec rows are native text/shapes, not raster.
- Limits: the model is a massing study; native lighting is fixed; metallic PBR
  renders white; `COLOR_0` is ignored when a material exists; Morph on the 3D
  camera is not visually verified.

## Experimental (not used by any product path)

`scripts/morph_playbook.py`, `scripts/cognitive_pacing.py` and
`scripts/interactive_triggers.py` came from Argon's T033 drop. Each writes
schema-invalid or wrong XML on real decks, so all three are quarantined. See
`experiments/T033-20261016-argon-research/REPORT.md`. T055's native 3D compiler
is also `EXPERIMENTAL` until reviewed.

## Open problems (ranked)

1. **T054/T055 review and merge order.** T054 is a prerequisite for T055.
   Review the native reopen evidence, the massing-study label, and the Morph
   negative result before either enters a product path.
2. **Native 3D gate.** Play the T055 deck in a live PowerPoint session: rotate
   the model, confirm the callouts stay editable, and check the PDF/PNG match
   the screen.
3. **Morph on a 3D camera.** The OOXML transition is accepted; visual
   interpolation is unverified. Do not claim it until a clean capture shows it.
4. **Product mesh.** Replace the T054 blockout with a beveled, detailed mesh
   and a 12-landmark constrained camera; then re-run the T055 compiler.
5. **Human calibration of the critic.** Hand-rank about 20 decks and report
   Spearman against the critic.
6. **Integration.** Merge the accepted research branches into `main` through a
   PR. The ID-suffix convention (T024a/b/c) is in the registry.
