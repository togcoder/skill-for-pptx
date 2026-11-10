# Domain: pptx (PowerPoint)

> **Entry point since T087: [`skills/pptx/SKILL.md`](../../skills/pptx/SKILL.md).** It is written guidance (D011); the modules below are its toolbox. `slide-forge`, `pptx-motion-director` and `deck-director` are older skills: use them only as the guide's section 9 says.

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

> Since T083 the owner of every script is recorded in `lab/capabilities.json`, and CI checks it. This table is a summary; when they disagree, the registry wins.
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

## State (2026-11-11)
- **Into a theme (T100, issue 83):** `glance` reports the faults a viewer sees at once from PowerPoint's own
  facts (drawn text bounds, drawn colours, the master's shapes) and boxes them on the slide; `shell` finds
  and strips the old shell where it lives (master, layouts, repeated shapes); `fit` scales a slide's content
  as one block into the theme's free area; `compare` pairs old and new at full size. Guide 13 defines the
  middle operation and the three checks before a deck is shown. Measured on four real decks; the real
  37-slide trial keeps every effect, video, number and picture and leaves 13 slides with listed faults.
  `glance` does not judge taste, and does not read text inside tables.
- **Motion eyes (T073):** `pptx_tools.py watch` runs PowerPoint's own slide show and writes one strip
  per slide: inside each Morph, the slide as it opens, after every click, inside long clicks; it names
  clicks that change nothing. Rung 5b on T069a, T090, the T087 demo and the real QCC deck; 16 of 16
  runs identical to the on-screen show. Guide 8 tells agents how to read the strips. Not yet tried by
  a small model.
- **Review follow-up (T099):** applied six concrete T096/T097 toolbox fixes: thousands-dot number parsing, clear PDF page errors, batched `sample` thumbnails, XML-safe table fill ordering, Pillow-safe image hashing, and linked-video extraction. Full suite 604 pass/10 skipped. `retable`'s palette semantics and the agent's click-by-click `watch` remain separate follow-ups; do not silently alter project colours.
- **Reusable components (T098):** `components`, `ungroup`, `component`, `place` extract a diagram frame / step bar / Gantt from a finished deck into a one-slide component (group flattening with child-space geometry, background exclusion, theme freeze, picture rel remap, trimmed bounds) and put it back on another slide. Real QCC deck: Ver3-4 slide 29 has 40 free shapes (no group) on a full-slide picture; 37 become `fishbone_ver34` and 64 become `fishbone_ver5`; `place` verified in PowerPoint 16.0 (rung 4). Animations stay with the source slide; charts/SmartArt/video are refused with the right alternative. Guide 12. Tests: `tests/test_components.py` (9).
- **Patchwork harmonisation (T094, guide 10):** DSH rehearsed T093's guide on the 10-slide patchwork
  deck and produced an 11-slide deck with 1 font family, 6 sizes, 6 text colours, flat charts,
  unstretched evidence photos, the 8-column table in an appendix, Fade on 2–11, **13 click groups /
  46 effects, 0 numbers lost**; PowerPoint 16.0 opens it and every effect resolves (rung 4). Review of
  the T093 tools: `research/reviews/T093-dsh-20261108.md`, **accept-with-fixes** — `numbers` compares
  value sets (necessary, not sufficient; demo given) and `inventory` cannot name theme fonts or count
  fills/backgrounds, which guide 10 step 4 needs. Twelve guide-10 wording gaps for the lead are listed
  in `experiments/T094-20261108-dsh-harmonize-patchwork/REPORT.md`; owner scoring pending.
- **Tests:** 556 run, 6 skipped, 100 % pass across all domains (after T066–T068).
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
- **Directed deck (T069a):** the real 10-slide chapter rebuilt as **14 slides, 9 clicks, 61 effects, 4 `byObject` Morphs** (1.2 s) and **17 shape lifecycles**. Four state pairs: answer cards → winning answer; two worldviews → dialectic; three parts → one whole; quotation → thesis. 0 empty base, 0 picture on the last click, 0 empty frame, 0 Morph/entrance conflict, max active view 45 words, five type sizes. PowerPoint 16.0 opens/renders 14 slides; COM reports EntryEffect 3954 on the four B slides. New experimental `scripts/deck_state_critic.py` fails T066 (58 gates) and passes T069a (0); `design_critic` 4.33 (narrative 4.92). No Morph playback capture; B states hand-authored on the T067 copy, not compiled by `deck_director.py`. `experiments/T069-20261104-opencode-directed-deck/REPORT.md`.
- **Narrative gate (T069b):** `design_critic.py` has a sixth `narrative` dimension: `NAR-BASE-STATE` (no blank `t=0`), `DEN-ACTIVE-WORDS` (≤45 active words), `NAR-LIFECYCLE` (multi-click slides need dim/exit), `NAR-ALIGN` (speaker notes carry matching `[T=0]`/`[CLICK]` cues). `deck_director.py` compiles native `notesSlide` cues, `exit` transitions and a two-pass `scaffold`/`check --pass-1` loop. Measured: T066 narrative 2.70, T068/T069 5.00; 12/12 tests; scaffolded deck 4.84. `experiments/T069-20261104-antigravity-narrative-critic/REPORT.md`.
- **Morph matching rules (T074):** 15-case matrix rendered by PowerPoint 16.0 (45 slides, 109.4 s video): `!!` is a name hint, not a type override (rect→ellipse cross-fades); an entrance on the destination blocks Morph; an off-slide destination is absent, not staged; different names of the same shape type still pair; group and 90° rotation pair; z-order can hide a morphing actor. `scripts/morph_studio.py audit` reports the three high-risk cases structurally; 2 tests, T069a clean. 11 rules + do/don't in `morph-rules.md`; `picture-diff`, charts/tables/SmartArt/3D/connectors/flips and >180° are open. `knowledge/morph_rules.json` is not written until review. `experiments/T074-20261105-opencode-morph-rules/REPORT.md`.
- **Motion fit (T091):** the owner's 2026-11-08 grades separate two "simple" decks. T087's 5-slide demo passed at **7/10** because the motion fit a classroom; T069a's four-Morph deck scored **6/10** as "gượng gạo", with the composition also named — and it passes `morph_studio audit` with 0 findings. Structural validity is not readability. Applied to `skills/pptx`: choose the motion level by room, pass a poster test on both Morph endpoints, and answer four forced-cut questions before adding motion. `experiments/T091-20261108-opencode-rung6-motion-law/REPORT.md`.
- **Deck Director compiler (T068):** `scripts/deck_director.py check|compile|ledger`, `lab/schemas/deck_direction.schema.json`, `slide_forge.py build --plan`. Two-pass direction (state machine and stage inventory, then spoken weave) with lifecycle `enter`/`dim`/`highlight`/`exit`; five hard laws as codes (`NAR-CODA-TRAP`, `NAR-KARAOKE`, `NAR-UNANCHORED`, `NAR-COLLISION`, `DEN-ACTIVE-VIEW`). Proof: 3 slides, QA 0 errors, critic 4.99, 6 lifecycles, 0 empty base, 7/7 unit tests; DeckCraft previews only (rung 2), no PowerPoint playback. `experiments/T068-20261104-antigravity-deck-director/REPORT.md`.
- **Deck direction (T067):** the owner's read of T066 — motion without *gu*, images last, generated before a script — is a pipeline property, not a deck accident. Layout is compiled first and `md.draft()` reads the finished file back; the plan's `script` is generated from slide titles; the critic has no narrative dimension and recognises titles only by placeholder. The lab's own reference deck reproduces the defects at 4.88/5.0 motion. T067 proved the repair on a copy: **51 → 27 clicks, 144 → 116 effects, 0 empty base, 0 pictures on the last click, 0 animated titles, ≤2 movers**, but **0 Morphs and 0 lifecycles**; removing all nine decorative Morphs was a reset, and T068 must restore **3–4 semantic state-pair Morphs**. Image law: one image is one block (face + ring + ground + caption) and enters on the naming sentence, never as a coda; identity images at `t=0`, evidence images on their beat. Style law: `VisualStyle/1` + 5 presets (`experiments/T067-20261104-opencode-visual-style/style-system.md`) defines geometry, material, depth, texture, image treatment, motion language and density, not palette + fonts. Draft layer: `skills/deck-director/SKILL.md` plus `direction.json` (brief → script → beats → shots → `base_state`). `deck_state_critic` is specified but not implemented; no human rung 6. Synthesis: `experiments/T067-20261104-opencode-deck-director/SYNTHESIS.md`.
- **Skill-built deck (T090):** a different model family (DeepSeek V4.1 Flash, DSH) built a 7-slide
  Triết học chương 1 short version by following `skills/pptx/` and `pptx_tools.py` only:
  **9 clicks, 28 entrance effects, one 1.4 s `byObject` Morph, 6 type sizes**, freshly drawn on a
  T066 identity; PowerPoint 16.0 build 17932 parses the Morph (`EntryEffect 3954`) and CreateVideo
  frames show it playing (rung 4/5). Two skill defects were measured: a Morph ghosts text that
  wraps differently on the two slides (identical explicit line breaks fix it), and the toolbox's
  entrance-only writer cannot satisfy `NAR-LIFECYCLE`. Eight guidance fixes are in the REPORT.
  Owner scoring pending. `experiments/T090-20261108-dsh-skill-triet-hoc/REPORT.md`.
- **Guidance patched (T092):** after T087 merged, the T090 cross-family review's guidance-only
  findings are applied: Morph text-wrap rule (identical line breaks on both slides), the
  `UNNAMED-PAIR` explanation for same-position titles, the decorative-glyph type rule, the t=0 check
  before motion, the speaker-notes `[T=0]`/`[CLICK n]` template, `DEN-WORDS`/`NAR-LIFECYCLE` limits,
  and D011 banners on the three legacy PPTX skills. R2 (dim/exit vs critic exemption) is left for
  the lead. No code changed. `experiments/T092-20261108-dsh-skill-guidance-fixes/REPORT.md`.
- **Existing decks (T093):** guide 10 tells an agent how to harmonise a colleague's patchwork deck
  without losing content: keep numbers, terms, titles, evidence photos and notes; change fonts,
  colours, layout, chart type and motion; triage each slide as keep / reshell / rebuild. Toolbox:
  `pptx_tools.py inventory|rechart|scale|unstretch|numbers`. Rehearsal on a synthetic QCC deck:
  5 fonts → 1, 14 sizes → 6, 0 numbers lost, all 36 effects resolve in PowerPoint (rung 4), owner
  grade pending; blind re-run by another family is T094.
  `experiments/T093-20261108-claude-harmonize-deck/REPORT.md`.
- **Guide 10 after the blind run (T094 → T095):** DSH reached the same system from the guide alone
  (1 family, 6 sizes, 0 numbers lost) but redrew the fishbone into another form and rewrote the
  author's notes. T095 makes a standard diagram's form and the author's notes content, forbids blank
  openings, and teaches `inventory` theme font names, fills and blank-opening detection, and `numbers`
  percent-vs-count and occurrence counts. Owner grades of both rehearsal decks pending.
  `experiments/T095-20261109-claude-guide10-fixes/REPORT.md`.
- **A reference document to follow (T096):** found on a real outside job (restyling a 20 x 11.25 in QCC
  theme after a 78-page printed report). Guide 2 now teaches following a sample's voice (charts, type,
  numbers, tables) without copying it; `pptx_tools.py sample` reads a PDF's real fonts (and whether this
  machine has them), sizes, text colours and fill colours. The small-text floor of `inventory` and
  `design_critic` `TYP-SMALL` now scales with slide height (27 pt on a 20 x 11.25 in slide).
  `experiments/T096-20261109-claude-sample-style-and-scaled-floor/REPORT.md`.

## Open questions / dissent
- **T067 job vocabulary.** The nine beat jobs (`hook`, `name`, `define`, `contrast`,
  `prove`, `mechanism`, `turn`, `land`, `ask`) and six figures are a reasoned
  taxonomy, not measured. Like T038's numbers, they need a reviewer to separate
  craft judgement from evidence. `narrative.presence_min_clicks = 1` is the only
  new number and the weakest one.

- **T038 numbers.** Several T038 values (golden 61.8 %, Duarte breaks at
  1/3 and 2/3, optical multipliers) are design lore. A reviewer should
  separate the ones that are measured from the ones that are judgement.
