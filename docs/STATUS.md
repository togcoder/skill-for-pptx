# Status — current state (2026-10-19, after T034)

This page is rewritten, not appended. History is in [CHANGELOG.md](CHANGELOG.md),
task IDs in [research/tasks/INDEX.md](../research/tasks/INDEX.md), and the
evidence vocabulary in [VERIFICATION.md](VERIFICATION.md).

## Where the code is

- **Research tip:** `claude/blissful-pasteur-gmll59`. That is `work/T033-argon-morph-staging` plus T034.
  It holds everything through T034. **289 tests pass** (`python3 -m unittest discover -s tests`).
- **`main` is behind** at `bb82c70` (T022/T023, PR #25). Merging the research tip into `main` is
  the owner's decision: open a PR from the tip, don't push to `main` directly.
- **Unmerged side branches** that are not part of the tip:
  - `work/T021-codex-compound-motion-20261005`: a claim only, no code.
  - `work/T009-codex-no-script-20261005`: PR #22, held back. T022 recompiled it.
  - `work/T007-helper-component-synthesis-20261004`.

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

1. **Native gate.** Play the T028 pro decks, a Forge cinematic deck and the
   T034 dark-brand decks in PowerPoint. Record easing, autoRev pulses, the
   visibility of helpers, Morph pairing and z-order, and settle behaviour.
2. **MOT-SETTLE on Forge decks.** A token journey ends away from its authored
   place before Forge's Morph orbs. Proposed fix: author the token at its
   destination and travel from the start.
3. **Forge type scale.** Forge uses 13–15 type sizes per deck; the design
   system band is 3–6. It should read the Office kit `type_scale_pt`.
4. **Human calibration of the critic.** Hand-rank about 20 decks and report
   Spearman against the critic.
5. **Integration.** Merge the research tip into `main` through a PR. The
   ID-suffix convention (T024a/b/c) is now in the registry.
