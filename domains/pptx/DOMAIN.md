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
| Interaction | `pptx_animator.py` — the **one** writer for `interactiveSeq`, trigger conditions and click-hyperlink conflicts (T061); `slide_navigator.py` (T048; non-linear branching, `last_viewed` return, custom shows, kiosk, navigation graph) |

**Experimental** (quarantined, kept out of product paths):
`morph_playbook.py`, `cognitive_pacing.py`, `interactive_triggers.py` (T033;
since T061 a thin compatibility shim over `pptx_animator.apply_interactive_actions`,
no XML of its own). `advanced_interactivity.py` (T049) keeps the PowerPoint COM
1-slide game builder and WAV synthesis; its timing builder/parser delegate to
`pptx_animator`. `interactive_show_harness.py` (T058; Windows interactive
desktop only, EXPERIMENTAL until reviewed).

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

Skills: `skills/pptx-motion-director`, `skills/slide-forge`, and (draft,
unwired) `skills/deck-director`.

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
- **Product paths change only through a pull request with a review (T065).**
  - The pptx product paths are `motion_director.py`, `motion_engine.py`,
    `pptx_animator.py`, `morph_studio.py`, `slide_forge.py`,
    `design_critic.py`, `slide_navigator.py`, `advanced_interactivity.py`,
    `interactive_triggers.py`, `theme_engine.py` and the design-system data in
    `knowledge/design_system.json`.
  - A commit that changes one of them goes to a `work/T…` branch, opens a PR,
    and waits for an accepted review in `research/reviews/` from an agent of a
    different model family (`lab/standards/REVIEW.md`).
  - Committing such a change straight to `main` is a process defect: the
    CHANGELOG entry must name the PR, and the reviewer re-reads the diff, not
    the REPORT alone. This rule exists because T043, T047, T048b and T049
    reached `main` unreviewed (T057 review, finding 3).
- **3D Camera Morph Law (T064):** A Morph between two camera views of one
  `am3d:model3d` animates the camera **only if every slide references the same
  model part**. Insert the model once, duplicate the slide, then change
  `Shape.Model3D` on the copy. One `Shapes.Add3DModel` per slide creates
  separate `ppt/media/model3dN.glb` parts and Morph degrades to a fade-out/
  fade-in with a 0.40 s blank. Verified at rung 5, PowerPoint 16.0 build 17932;
  see `experiments/T064-20261104-opencode-native-3d/REPORT.md`.

## State (2026-11-04)
- **Tests:** 556 run, 8 skipped, 100 % pass across all domains (after T061 + T063 + T062 + T058 + T064 + T059).
- **Forge (T063):** type sizes come from the Office kit `type_scale_pt` (3–6 per deck); count-up stacks are print/PDF/Morph-safe (final value topmost and opaque, proxies below); highlight markers follow centred/right-aligned text; Ken Burns ends on the authored frame and generated process tokens use T034's author-at-destination fix. All five example decks have no `TYP-SIZES` or `MOT-SETTLE` warning.
- **Navigation & Interactivity:** T048 added Slide Navigator (`slide_navigator.py`) establishing full non-linear branching, dynamic return paths, custom shows with return, and mini-game state machine compilation. T049 added Advanced Presentation Interactivity (`advanced_interactivity.py`) establishing native in-slide lightbox modals, multi-tab switchers, pure-Python synthetic sound FX (click/chime/buzz), hover actions, and twin-morph visual flow. **T061** consolidated every `interactiveSeq`/trigger/hyperlink writer into `pptx_animator.py`; T048b/T049 artifacts rebuild byte-identically (T048) or are unchanged and parse to the same counts (T049).
- **Interactive playback (T058):** `scripts/interactive_show_harness.py` drives a windowed show with Win32 input and asserts pixels. T049 slide 1/2 and the T048b hub reach **rung 5b** (COM-driven, machine-asserted, not human-reviewed): cover clicks 100 % of the target box, hub 9/9 edges including `lastslideviewed` 5→3. `GotoClick` is useless for triggers (0.000 %); on a main sequence it moves the index without rendering. T058's two pre-T061 defects (T032 writer rejected; missing `stCondLst`) were fixed by T061 and re-tested on `main`.
- **Native illustration (T062):** DeckCraft commands compile a named, part-editable asset (20/20 parts addressable, 21 animations) where SVG and GLB give one object each. The `{"native_art": …}` Forge field and its compiler are EXPERIMENTAL in `experiments/T062-*/inputs/`, not wired into `slide_forge.py`. Merge Shapes re-ids its result and DeckCraft accepts animation on a dead id, so compilers must re-inspect; `design_critic.py` needs an `art-*` exemption before native art scores honestly.
- **DeckCraft (T060):** the timing-tree player exists in `deckcraft-anim` (Rust: `Timeline`, `ShowState`, effect evaluation) but has no headless command. A local 151-line prototype adds `render-animation --slide N --click K --t ms` and renders main-sequence frames. Coverage is the limit: 102/198 lab presets map, at most 67/198 exact/path, behaviour-level repeat is dropped.
- **DeckCraft fidelity (T059):** static frames are close for design critique (critic delta ≤0.01) but break on charts (13.1 mean, 5–13 % `>40`), SVG icons (missing; transparent fallback), 3-stop gradients and soft edges/bevels. `render-transition` is not PowerPoint Morph (entrance shapes drawn; camera morph not interpolated). `convert` rewrites chart build targets, GrowAndTurn rotation and SVG blips; it is not a safe last writer. Use DeckCraft as a pre-Director asset tool or a labelled static fallback (`DeckCraft render`, rung 2), never PowerPoint.
- **Native 3D (T055, rebased by T064):** `Shapes.Add3DModel` + embedded GLB + editable callouts. 3-slide deck, one Type-30 model per slide, three embedded `model3d*.glb`, cameras/rotation/FOV preserved after save/reopen, PDF export. Source GLB is Y-up metres, 400 × 553 × 326 mm, 34 non-metallic material regions. The blockout is frozen in `inputs/blockout.json`, so T055 no longer depends on T054. Review `accept-with-fixes`: `research/reviews/T055-opencode-20261104.md`.
- **Morph over a 3D camera (T064):** verified at rung 5 with CreateVideo frames. Morph interpolates `am3d:camera` only when consecutive slides share one `model3d` part; with one `Add3DModel` embed per slide it fades the model out and in (0.40 s blank) and never moves the camera. Authoring rule: insert the model once, duplicate the slide, then change the camera.
- **3D limits:** native lighting is fixed (black horizontal faces render grey); metallic PBR renders as a white mirror; `COLOR_0` is ignored when a material exists. The T055 model is a massing study, not final product fidelity.
- **Evidence:** Rungs 0–5b established across PPTX, DOCX, XLSX and Cross; PowerPoint 16.0 COM is used for parse/render/click checks. T059 measured DeckCraft against PowerPoint at rung 4/5; T062 used COM at rung 4/5; T063 inspected PDF/PNG/CreateVideo frames (rung 5); T064 used CreateVideo frames for 3D camera Morph (rung 5). Rung 6 (a human reviewing every click/frame) has not been reached; the T057 audit retired the earlier "rungs 0–5 / COM verified" wording.
- **Deck direction (T067, draft):** the owner's read of T066 — motion without *gu*, images last, generated before a script — is a pipeline property, not a deck accident. Layout is compiled first and `md.draft()` reads the finished file back; the plan's `script` is generated from slide titles; the critic has no narrative dimension and recognises titles only by placeholder. The lab's own reference deck reproduces the defects at 4.88/5.0 motion. Draft layer: `skills/deck-director/SKILL.md` plus `direction.json` (brief → script → beats → shots → `base_state`). No code merged; compiler and critic changes are T068–T069.

## Open questions / dissent
- **T067 job vocabulary.** The nine beat jobs (`hook`, `name`, `define`, `contrast`,
  `prove`, `mechanism`, `turn`, `land`, `ask`) and six figures are a reasoned
  taxonomy, not measured. Like T038's numbers, they need a reviewer to separate
  craft judgement from evidence. `narrative.presence_min_clicks = 1` is the only
  new number and the weakest one.

- **T038 numbers.** Several T038 values (golden 61.8 %, Duarte breaks at
  1/3 and 2/3, optical multipliers) are design lore. A reviewer should
  separate the ones that are measured from the ones that are judgement.
