> **Since T040 this page is the pptx domain's status.** Lab-wide state lives in
> `HANDOFF.md` and `domains/README.md`; how agents work is in `lab/PROTOCOL.md`.

# Status — current state (2026-11-04, after T057)

This page is rewritten, not appended. History is in [CHANGELOG.md](CHANGELOG.md),
task IDs in [research/tasks/INDEX.md](../research/tasks/INDEX.md), and the
evidence vocabulary in [VERIFICATION.md](VERIFICATION.md). The lead review and
the reserved next tasks (T058–T065) are in
[T057](../experiments/T057-20261104-claude-leader-review/REPORT.md).

## Where the code is

- Everything through T056, plus T057, is on `main`. **461 tests pass**
  (`python -m unittest discover -s tests`, 4 skipped).
- **Unmerged:**
  - `work/T054-opencode-vector-match` (vector).
  - `work/T055-opencode-pptx-3d` (native 3D deck): **no longer stacked on
    T054.** T064 froze the blockout as an input artifact and rebased the task
    onto `main`; review verdict `accept-with-fixes`.
  - `work/T064-opencode-native-3d`: the T055 review, the rebase and the Morph
    camera evidence; not merged.
  - The Codex T009/T021 branches are historical.
- **pptx modules added since T034:**
  - `theme_engine.py` (T043): not wired into Forge.
  - `slide_navigator.py` (T048b) and `advanced_interactivity.py` (T049): no
    review, and nothing has been played in a live slide show.
  - `deckcraft_bridge.py` (T035): renders through DeckCraft.

## Product paths

| Path | Entry point | For | Skill / command |
|---|---|---|---|
| Motion Director | `scripts/motion_director.py` (`inspect → draft → apply/auto → preview → verify → critique`) | Existing decks: script-driven click rhythm, compound and layered motion, preserving the source | `skills/pptx-motion-director`, `/animate-deck` |
| Morph Studio | `scripts/morph_studio.py` (`propose → apply → preview`) | Cross-slide Morph: `!!` continuity, fly-in staging, camera, card expand, pan | same skill |
| Slide Forge | `scripts/slide_forge.py` (`schema → build → qa → render`) | New decks from a semantic spec: layout, type, themes, assets, motion | `skills/slide-forge`, `/forge-deck` |
| Design system + critic | `knowledge/design_system.json`, `scripts/design_critic.py` | One set of numbers for generating and judging beauty and technique | `docs/DESIGN_SYSTEM.md` |

The north star is unchanged: an AI Motion Director for existing decks
([PRODUCT_TARGET.md](PRODUCT_TARGET.md)). Forge is the second entry mode, for
decks that do not exist yet.

## Capability × evidence

The evidence ladder is defined in [VERIFICATION.md](VERIFICATION.md). Columns:

- **Struct**: structural checks.
- **Sim**: simulated preview.
- **LO**: LibreOffice reads the effects or renders the slides.
- **PPT-parse**: PowerPoint parsed the effects (EffectType or effect count).
- **PPT-render**: PowerPoint rendered the deck with CreateVideo, which advances clicks automatically.
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

"–" means no evidence. Nothing has been played interactively in PowerPoint. That
is the open native gate: [T020 §A](../research/tasks/T020-motion-director-continuation.md)
and [T034 "Next"](../experiments/T034-20261019-claude-design-system/REPORT.md).

## Experimental (not used by any product path)

`scripts/morph_playbook.py`, `scripts/cognitive_pacing.py` and
`scripts/interactive_triggers.py` came from Argon's T033 drop. Each writes
schema-invalid or wrong XML on real decks, so all three are quarantined. See
`experiments/T033-20261016-argon-research/REPORT.md`. Older research paths
from E001–T018 (the Work-runtime builder, the patch writers v0.2–v0.5) are
frozen for reproducibility. Do not build on them.

## Open problems (ranked)

Briefs, owners and critics are in T057.

1. **Native interactive gate (T058).**
   - Nothing interactive has been clicked in a live slide show. This covers
     the T032 triggers and the T048b/T049 games and hubs.
   - Build an automated click harness, or write a manual protocol.
2. **One interaction writer (T061).** Three modules write `interactiveSeq`.
3. **Forge debt (T063).**
   - Count-up frames are stacked in the static, print and Morph views.
   - The highlight marker is misaligned for centred text.
   - A deck uses 13 type sizes (the band is 3–6).
   - MOT-SETTLE.
4. **DeckCraft (T059, T060, T062).**
   - Measure its fidelity as a second renderer.
   - Find out whether its source can render in-slide animation frames.
   - Use its shape commands for native assets.
5. **Native 3D (T064).** Decouple T055 from T054, then test Morph between
   camera views.
6. **Human calibration of the critic.** Hand-rank about 20 decks.
