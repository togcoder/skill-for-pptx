# Architecture (after T034)

Python 3 + lxml throughout. Optional tools:

- python-pptx and Pillow for Forge and the fixtures;
- LibreOffice Impress, poppler and ImageMagick for renders and previews;
- Windows with PowerPoint for native renders.

The scripts sit in `scripts/`, data in `knowledge/`, and the skills in
`skills/` wrap the CLIs for agents.

```
                     knowledge/design_system.json  ◄── design_system.py (loader)
                     (tokens, rules, sources)           motion_tokens.py (easing fits)
                              │ read by everyone below
 ┌──────────────── existing deck ────────────────┐   ┌──────── new deck ────────┐
 │ motion_director.py  inspect → deck_model      │   │ slide_forge.py           │
 │   draft (heuristics, styles, cinematic)       │   │  spec → layout, type,    │
 │   motion_script.py  (script ↔ plan, notes)    │   │  themes (office kits,    │
 │   validate_director_plan.py (contract v0.7)   │   │  brand_palette), assets  │
 │   compile: motion_engine.py (recipes,         │   │  (forge_assets) → static │
 │     keyframes, layers, rigging) +             │   │  deck → motion_director  │
 │     motion_components.py (generated helpers)  │   │  → forge_qa              │
 │   write: pptx_animator.py (canonical timing,  │   └──────────┬───────────────┘
 │     presets incl. ppt:<198>, Morph)           │              │
 │   verify (preservation, overlaps, occlusion)  │              │
 └──────────────┬────────────────────────────────┘              │
                ▼                                               │
 morph_studio.py  propose → continuity (!! chains, staging),    │
                  scenes (camera-zoom, card-expand, pan) →      │
                  verify_scenes, settle_report                  │
                ▼                                               ▼
           design_critic.py  ── grades every output against the design system
                │                (motion_director report, Forge verdict, Morph report)
                ▼
   previews: motion_preview.py (simulated GIF/sheets), morph_studio preview,
   lo_timing_crosscheck.py (LibreOffice), powerpoint_render.ps1 (PowerPoint)
```

## Modules

| Module | Role | Since |
|---|---|---|
| `motion_director.py` | Product entry for existing decks. Commands: `inspect`, `draft`, `apply`, `auto`, `preview`, `storyboard`, `verify` and `critique`. Holds the deck model and the draft heuristics | T019, T022–T024, T028, T034 |
| `motion_script.py` | Parses scripts (`[click]`/`[nhấp]`), aligns them to resources, retimes the draft, drafts a full script, writes speaker notes | T024a |
| `validate_director_plan.py` | Director plan contract v0.7, including design-system limits | T019–T034 |
| `motion_engine.py` | Keyframe tracks and recipes compiled to effects: assemble, spotlight, cycle, swap, travel, zoom-focus, rise, ken-burns, orbit(-3d), wave, explode-layers, cascade-flow, ambient. Also rigging, state simulation and the XML reader | T023, T024a–c, T028, T034 |
| `motion_components.py` | Generated helpers (halo, ring, rail, token, mask, highlight, underline, callout and others) in deck colours that reach WCAG contrast | T024a, T028, T034 |
| `pptx_animator.py` | Writer, reader and simulator for PowerPoint-canonical timing. Covers presets plus the `ppt:` library, loops, iterate, triggers and Morph transitions | T019+ |
| `motion_preview.py` | Simulated GIFs and key-state sheets (LibreOffice render of simulated states) | T023 |
| `morph_studio.py` | Cross-slide Morph: continuity, staging, scenes, verification, settle report, simulated Morph preview | T028 |
| `slide_forge.py`, `forge_qa.py`, `forge_assets.py` | New-deck compiler, coded QA, licensed photos and icons | T025–T026 |
| `design_system.py`, `knowledge/design_system.json` | The shared tokens and rules | T034 |
| `design_critic.py` | Measured verdict on beauty and technique (JSON and Markdown); `forge_critique.py` is a compatibility alias | T034 (T031) |
| `motion_tokens.py`, `brand_palette.py` | Easing fitted to accel/decel; OKLCH theme from one colour | T029, T030 |
| `deck_dna.py`, `corpus_scan.py`, `knowledge_build.py`, `phrase_scan.py`, `extract_presets.py`, `office_design_dna.py` | Build the knowledge base (`knowledge/README.md`) | T027 |
| `lo_timing_crosscheck.py`, `render_identity.py`, `powerpoint_render.ps1`, `powerpoint_native_probe.ps1`, `verify_powerpoint_qa.py` | Verification ladder rungs 3–6 (`docs/VERIFICATION.md`) | T018–T025 |
| `data_motion_recipes.py`, `chart_native_timing.py`, `counter_component.py` | Chart builds and KPI counters | T012–T016 |

## Experimental and frozen

- **Experimental, quarantined in T034:** `morph_playbook.py`,
  `cognitive_pacing.py` and `interactive_triggers.py`. No product path
  imports them, and a test enforces this.
- **Frozen research paths:**
  - the E001 Work-runtime builder: `run_experiment.sh`, `render_plan.mjs`,
    `validate_plan.py`;
  - the T006 packed-timeline writer: `pack_timeline.py`, `add_timeline.py`,
    `validate_timeline.py`;
  - the v0.2–v0.5 patch writers: `patch_existing_timeline.py`,
    `compile_director_patch.py`.

  They are kept so earlier experiments can be reproduced. The patch writers
  are known to be defective, because after-previous steps run concurrently.
  Do not build on any of these paths.

## Contracts

- **Director plan v0.7:** layers, generated components and narration. The
  essentials are in `skills/pptx-motion-director/SKILL.md`. The full v0.4
  contract is in `skills/pptx-motion/references/existing-deck-director.md`
  (historical); later versions are additive.
- **Morph plan** (`kind: "morph-scenes"`): continuity and scenes; see
  `morph_studio.py propose`.
- **Forge spec:** `slide_forge.py schema`.
- **Design system:** `knowledge/design_system.json` (version 1.0.0).
