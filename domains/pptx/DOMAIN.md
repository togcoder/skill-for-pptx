# Domain: pptx (PowerPoint)

## Scope
- **Existing decks:** motion direction that preserves the source. Script →
  click rhythm → compound and layered motion → Morph.
- **New decks:** Slide Forge, which builds from a spec, with layout,
  typography, themes and assets.
- North star: `docs/PRODUCT_TARGET.md`.

## Thesis
A deck is presented. Motion must follow the presenter's narrative (one idea
per click). Design numbers are shared by the generators and the critic
(`docs/DESIGN_SYSTEM.md`).

## Native canon and sources
- OOXML PresentationML timing (ECMA-376/ISO 29500).
- The 198 PowerPoint presets (`knowledge/powerpoint_presets.json`) and Office
  designer themes.
- Perception and design-system sources: `docs/SOURCES.md`.

## Code (canonical)
| Area | Modules |
|---|---|
| Director | `motion_director.py`, `motion_engine.py`, `pptx_animator.py`, `motion_components.py`, `motion_script.py`, `motion_preview.py`, `validate_director_plan.py` |
| Morph | `morph_studio.py` |
| New decks | `slide_forge.py`, `forge_qa.py`, `forge_assets.py` |
| Design | `design_system.py` + `knowledge/design_system.json`, `design_critic.py`, `motion_tokens.py`, `brand_palette.py` |
| Native | `powerpoint_render.ps1`, `powerpoint_native_probe.ps1`, `verify_powerpoint_qa.py`, `lo_timing_crosscheck.py` |
| Bridge | `deckcraft_bridge.py` (T035; ArtCraft DeckCraft renderer; Windows only; not yet reviewed) |
| Navigation | `slide_navigator.py` (T048; Non-linear branching, Hub & Spoke, auxiliary popup return via last_viewed, Custom Show Show-and-Return, kiosk mode, mini-game state machine) |

**Experimental** (quarantined, kept out of product paths):
`morph_playbook.py`, `cognitive_pacing.py`, `interactive_triggers.py` (T033).

**Frozen:** the E001–T018 research paths (`docs/ARCHITECTURE.md`).

## Docs
In `docs/`:
- `STATUS.md`
- `DESIGN_SYSTEM.md`
- `VERIFICATION.md` (the pptx evidence ladder)
- `ARCHITECTURE.md`
- `CLICK_BEAT_CHOREOGRAPHY.md`
- `MOTION_PACKING.md`
- `POWERPOINT_NATIVE_HARNESS.md`

Skills: `skills/pptx-motion-director`, `skills/slide-forge`.

## Domain rules
- **Inventory first.** For an existing deck, inventory the source before
  planning edits.
- **Story-source priority:** explicit script > speaker notes > existing
  native choreography > visible narrative > inferred narrative > researched
  narrative.
- **Preserve by default.** Existing timing is a source resource: preserve or
  extend it. Keep slide count, order and content unless the user asks
  otherwise. Generated components need a narrative role and must fit the
  design system.
- **Identity.** Preserve semantic object identity across states. Never treat
  slide-local shape IDs as global identity.
- **Compound motion.** Read `docs/MOTION_PACKING.md` and
  `docs/CLICK_BEAT_CHOREOGRAPHY.md` first. Start a new click at a meaningful
  stable state, use `with-previous` for concurrent motion and
  `after-previous` only for continuation within a beat. Never turn speech
  time into a guessed delay.
- **Design numbers.** New thresholds go into `knowledge/design_system.json`
  with sources. Run `design_critic.py` on outputs.
- **Non-Linear Navigation Law (T048):** Decks with branching narrative (Hub & Spoke, auxiliary popups, mini-games) must provide dynamic return actions (`lastslideviewed`), and must lock blank slide clicks (`advClick="0"`) or enable Kiosk mode (`p:kiosk`) to prevent accidental slide skips.
- **Advanced Interactivity Law (T049):** For auxiliary drill-downs, detail dialogs, and multi-perspective views, agents MUST prefer In-Slide Lightbox Modals and In-Slide Tabbed Switchers (via native `<p:cTn nodeType="interactiveSeq">`) over creating duplicate slides. In-slide triggers preserve visual context, eliminate disruptive screen cuts, and keep the presentation compact. Tactile sound effects (`<a:snd>` in `<a:hlinkClick>`/`<a:hlinkHover>`) and Morph transitions (`p14:morph`) should be integrated for high-polish interactivity.

## State (2026-11-03)
- **Tests:** 469 run, OK, 8 skipped; `lab/tools/check_layout.py` passes.
- **Native 3D (T055):** `Shapes.Add3DModel` + embedded GLB + editable callouts.
  3-slide deck, one Type-30 model per slide, three embedded `model3d*.glb`,
  cameras/rotation/FOV preserved after save/reopen, PDF export. Source GLB is
  Y-up metres, 400 × 553 × 326 mm, 34 non-metallic material regions. Report:
  `experiments/T055-20261103-opencode-pptx-3d/REPORT.md`; branch
  `work/T055-opencode-pptx-3d`; **review requested**, stacked on T054.
- **Navigation & Interactivity:** T048 added Slide Navigator (`slide_navigator.py`) establishing full non-linear branching, dynamic return paths, custom shows with return, and mini-game state machine compilation. T049 added Advanced Presentation Interactivity (`advanced_interactivity.py`) establishing native in-slide lightbox modals, multi-tab switchers, pure-Python synthetic sound FX (click/chime/buzz), hover actions, and twin-morph visual flow.
- **Evidence:** Rungs 0–5 established across PPTX, DOCX, XLSX, and Cross. PowerPoint 16.0 COM verified.
- **3D limits:** native lighting is fixed (black horizontal faces render grey);
  metallic PBR renders as a white mirror; `COLOR_0` is ignored when a material
  exists; Morph on the 3D camera is not visually verified. The T055 model is a
  massing study, not final product fidelity.

## Open questions / dissent
- **T038 numbers.** Several T038 values (golden 61.8 %, Duarte breaks at
  1/3 and 2/3, optical multipliers) are design lore. A reviewer should
  separate the ones that are measured from the ones that are judgement.
