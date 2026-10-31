# T035 — DeckCraft Native Bridge and Skill-for-Design Foundation

## Frozen input

- **Request.** On 2026-10-31, the project owner requested to advance the repository directly into a comprehensive **Skill for Design** suite, with PPTX motion as the pioneering branch, integrating native tools and pushing progress directly to GitHub.
- **Base.** Research tip `claude/blissful-pasteur-gmll59` @ `ba2fe8b` (T034 design system + documentation standardization).
- **Environment.** Windows 10/11 x64, Python 3.12 (miniconda3), ArtCraft Suite (`D:\artcraft\DeckCraft\deckcraft-cli.exe` v0.13.1).
- **Previous Bottleneck.** As recorded in `HANDOFF.md` item 1 and `docs/STATUS.md`, native rendering verification (Rung 5/6) previously required manual PowerPoint execution or LibreOffice. Without a visual render loop, agents could not independently inspect what they produced offline.

## What was built

### 1. DeckCraft Native Bridge (`scripts/deckcraft_bridge.py`)
- Discovers `deckcraft-cli.exe` in `D:\artcraft\DeckCraft`, default locations, or system PATH.
- Headless slide rendering (`render_slides`): converts `.pptx` or `.deckcraft` slides directly to Full HD (1920x1080) PNGs in under 1 second.
- Inspection (`inspect_deck`): extracts structural JSON tree without launching a GUI.
- Format conversion (`convert_presentation`): round-trips between PPTX, DeckCraft, PDF, and outline Markdown.

### 2. Native Verification in Design Critic (`scripts/design_critic.py`)
- Extended `--render` parameter to support native DeckCraft rendering:
  ```bash
  python scripts/design_critic.py deck.pptx --render deckcraft
  # or
  python scripts/design_critic.py deck.pptx --render dc
  ```
- Instantaneous visual feedback loop: Design Critic automatically triggers DeckCraft, generates PNG frames, and computes `background_share`, `balance_offset`, and Hasler-Suesstrunk `colourfulness` against `knowledge/design_system.json`.

### 3. Test Coverage (`tests/test_deckcraft_bridge.py`)
- Added 3 unit tests verifying binary detection, multi-slide rendering, and single-slide rendering.
- Test suite expanded from 289 to **292 tests, all passing (0 failures, 4 skipped)**:
  ```text
  Ran 292 tests in 14.384s
  OK (skipped=4)
  ```

### 4. Verification Evidence
Tested on `experiments/T019-20261005-claude-motion-director/report_deck_motion.pptx`:
- Rendered 7 slides to 1920x1080 PNGs in **0.87 seconds**.
- Full Design Critic verdict computed in **2.1 seconds** (Score: Overall 4.77, Motion 4.88, Rhythm 5.0).
- Proves native offline visual inspection without Microsoft Office or LibreOffice.

## Skill for Design Architecture

The project maintains full backward compatibility for all existing PPTX Motion Lab tools (`motion_director.py`, `slide_forge.py`, `morph_studio.py`, `design_critic.py`) while establishing the multi-craft foundation:

```text
skill-for-pptx (evolving to Skill for Design)
├── shared/
│   ├── design_system.json       # Core design tokens (Carbon, Material, WCAG 2.2)
│   └── critic/                  # Aesthetic & technical grading engine
├── domains/
│   ├── pptx/                    # [PIONEER] Motion Director, Morph Studio, Slide Forge
│   │   └── bridges/deckcraft    # DeckCraft native headless engine
│   ├── docs/                    # WordCraft document engine (roadmap)
│   ├── sheets/                  # GridCraft spreadsheet engine (roadmap)
│   └── vector/                  # VectorCraft illustration engine (roadmap)
```

## Next steps

1. Update `docs/STATUS.md` and `HANDOFF.md` to document the native DeckCraft capability and new test baseline (292 tests).
2. Wire DeckCraft render directly into `slide_forge.py` and `motion_director.py` preview generation.
3. Address remaining critic findings (MOT-SETTLE and Forge type scale).
