# Changelog — research log, newest first

This is the chronological record each task wrote when it finished. It used to
be `docs/STATUS.md`; since T034 the current state lives in
[STATUS.md](STATUS.md), and this file is append-only history. The entries are
kept verbatim: older ones mention test counts, versions and "next steps" that
were true at the time. Task IDs and their branches are listed in
[research/tasks/INDEX.md](../research/tasks/INDEX.md).

## T074 [pptx] Morph matching rules, verified by experiment matrix — 2026-11-05

- **Why.** T069a's four Morphs worked, but the rules that made them work were
  implicit. The owner's F8 ("Morph seems very hard") needs a measured rulebook,
  not another hand-built deck.
- **Matrix.** 15 two-slide cases (45 slides) rendered by PowerPoint 16.0 at
  720p/30 fps. Video **109.4 s** for 45×2 s slides because 15 Morphs add 1.2 s
  each.
- **Result.** Headline rule **M-02**: `!!` is a name hint, not a type override —
  rect→ellipse with the same `!!track` is **two blobs**, a cross-fade.
  **M-07**: an entrance on the destination blocks the Morph. **M-08**: an
  off-slide B object is absent, not staged. `diff-name` still pairs, so names
  are not required for simple same-type shapes.
- **Audit.** `scripts/morph_studio.py audit` reports `MORPH-TYPE-MISMATCH`,
  `MORPH-ENTRANCE`, `MORPH-OFFSLIDE` and `MORPH-UNNAMED-PAIR`; on the matrix it
  finds exactly the three planted errors, on T069a it is clean. Two structural
  tests; full suite **566 pass**.
- **Deliverables.** `morph-rules.md` (11 rules + do/don't),
  `artifacts/matrix-final.json`, 15 evidence frames, 45-slide matrix deck.
  `picture-diff` is explicitly **not measured**; charts/tables/SmartArt/3D/
  connectors/flips/rotation >180° are open. No `knowledge/morph_rules.json` yet
  (needs review).
  `experiments/T074-20261105-opencode-morph-rules/REPORT.md`.

## T084 [cross] Green CI — 2026-11-04

- **Test dependencies.** CI now installs `python-docx`, `openpyxl`, `numpy` and
  `pytest`; seven test modules failed to import without them.
- **Host-only tests skip on CI.** The PowerPoint COM games suite and ArtCraft CLI
  discovery skip when the tool is absent. The online photo example in
  `test_forge_debt` skips when Openverse cannot be reached.
- **Logo box fit (`slide_forge`).** The chrome logo box is sized from the measured
  text instead of a fixed 1.3 in, so a wider fallback font no longer breaks the word.

## T083 [cross] Coordination layer: registry, binding decisions, claim/board/check — 2026-11-04

- **Why.** The owner: skills grow in parallel across agents, so "the last
  version" is not final; agents and humans need a better channel so they stop
  stepping on each other. The rules already existed in `lab/standards/MERGE.md`
  but nothing checked them.
- **Built.**
  - `lab/capabilities.json`: 19 capabilities; every one of the 103 scripts has
    one owner and one role.
  - `lab/DECISIONS.md`: D001–D008.
  - `lab/tools/coord.py`:
    - `claim` reserves the ID against main and every open branch, then
      creates the branch and worktree, pushes and prints the briefing;
    - `board` shows active branches, collisions, a dirty shared checkout and
      open owner items;
    - `check` covers registry coverage, single-writer files and product →
      experimental imports.
  - `check_layout.py` runs the checks in CI (full fetch).
  - 8 tests.
  - `research/feedback/questions.md` is the agent → owner channel.
  - AGENTS/PROTOCOL changes: claim with the tool; agents no longer edit
    HANDOFF/ROADMAP (D006).
- **Found on day one.** Three live collisions:
  - T054 × T055 on `HANDOFF.md`, the svg card, the vector-craft skill and two
    tests;
  - both against T070 on `HANDOFF.md`;
  - an uncommitted `deck_director.py` in the shared checkout.

  There are also four product modules importing experimental bridges.
- **Owner questions.**
  - Q1: branch protection.
  - Q2: GitHub Issues as a two-way channel.
  - Q3: whether the configured `a12-hub` MCP server is meant to be the hub.

## T078 [pptx] Script track: diagnosis, method and the first gold script — 2026-11-04

- **Why.** The owner pushed back on T070: motion thinking is driven by the
  script, the agents' script skill is weak, and weak models may not manage
  this part. T070 had treated the script as an input the agent "just writes".
- **Diagnosis.**
  - The deck-director skill teaches a form and prohibitions, not a way to think.
  - It has no gold example.
  - The T069a script starts from the textbook outline and restates
    definitions.
  - There is no bridge from sentences to motion.
  - Scripts are never read as text before building.
- **Method.** Direction lives in `docs/SCRIPT_TRACK.md`:
  - a table of what a weak model can and cannot do;
  - a 6-step method (ask, intent, shifts, scene sheet, verb → motion,
    read-aloud and approval);
  - a library of 8 narrative frames;
  - an 18-row verb → motion table (hypotheses);
  - a division of labour: a strong model or the owner approves scripts as
    text.
- **Gold script.** `experiments/T078-…/gold-script-triet-hoc-ch1.md`: 13 scenes for
  the T066/T069a deck. It opens with two proverbs, uses a persistent lens
  metaphor as the Morph actor, and derives motion from verbs: gather, tip,
  flip, merge, become, pan through time, swap weight. It is compared with
  T069a.
- **Reserved.** T079 weak-model experiment, T080 verb-table validation, T081
  `script-writer` skill, T082 gold scripts 2–5. Next free ID T083. The ROADMAP
  principle 2 and architecture now put the script first.

## T070 [cross] Lead synthesis of T001–T069, critique and PPTX roadmap — 2026-11-04

- **Why.** The owner saw a lot of activity but no clearly better deck, noticed
  that mixing feedback and new requests in one session confused the agents,
  and found Morph hard. They asked the lead to synthesise all research,
  criticise it and set the path.
- **Synthesis.** Six phases (timing language, existing-deck director, new
  decks and knowledge, breadth, gates, story direction). Rung-5 assets: canonical
  timing writer and presets, picture motion, print-safe count-ups, live trigger
  clicks (T058), one interaction writer (T061), 3D camera Morph with a shared
  model part (T064), native part-addressable art (T062).
- **Critique.**
  - The critic is saturated: T068/T069b decks with empty cards, a clipped
    title and scaffold text score 4.99, and T066's "tasteless" motion scores
    4.99.
  - The best deck (T066) is a 524-line bespoke script, so taste never reaches
    the product.
  - `deck_director.py` maps actors by substring and invents content ("100%",
    "Bước hoàn thiện").
  - Names outrun evidence.
  - Same-family reviews, 12 tasks in a day and a duplicate ID (T069a/b).
  - Morph is hard because the lab thinks per slide instead of per scene, and
    its matching rules are scattered.
- **Roadmap.** New living `docs/ROADMAP.md`: six principles (owner's eye is
  the ground truth; intelligence goes into tools; Morph is a scene-compiler
  output; taste becomes verified recipes; one source of truth per capability;
  never invent). Stage 1 reserved: T071 golden benchmark + A/B page, T072
  visual defect gates, T073 fast motion viewer, T074 Morph rulebook. Stage 2
  reserved: T075 scene compiler, T076 ten Morph moves, T077 Director emits
  scenes. Next free ID T078.
- **Process.** New owner feedback ledger `research/feedback/` (seeded with
  F1–F8); one brief per agent session; builder and critic from different
  model families; at most three open pptx tasks. `HANDOFF.md` rewritten.

## T069b [pptx] Narrative Critic, speaker notes compiler and two-pass scaffold — 2026-11-04

- **Why.** `deck_director.py` could compile a screenplay, but `design_critic.py`
  could not see whether the deck's spoken cues, `t=0` and lifecycles agreed.
  The end-to-end loop stopped at the build.
- **Added.** A sixth `narrative` dimension in `design_critic.py`
  (`NAR-BASE-STATE`, `DEN-ACTIVE-WORDS`, `NAR-LIFECYCLE`, `NAR-ALIGN`), a
  speaker-notes compiler that writes `[T=0]`/`[CLICK]` cues into native
  `notesSlide` parts, `exit` lifecycles in the compiler, and a two-pass
  `scaffold` / `check --pass-1` workflow.
- **Measured.** 12/12 unit tests; T066 narrative **2.70** vs T068/T069 **5.00**;
  T069 scaffolded deck overall **4.84**, 4 lifecycles, 0 empty base, all active
  views ≤ 45 words, notes aligned. Review requested (Argon).
  `experiments/T069-20261104-antigravity-narrative-critic/REPORT.md`.

## T069a [pptx] Directed deck: four semantic Morphs, image blocks, state critic — 2026-11-04

- **Why.** T067 removed all nine decorative Morphs and fixed the base states;
  T068 built a direction compiler but proved it on three slides. Neither produced
  one artifact where motion, images and the script agree on the real chapter.
- **State pairs.** Four B states were added and joined by a 1.2 s `byObject`
  Morph: two answer cards → the winning answer; two worldviews → the dialectic
  one; three parts → one whole; quotation → thesis. Each pair shares 7–16
  `!!` names; no background or thread Morph.
- **Measured.** 14 slides, **9 click groups, 61 effects, 4 Morphs, 17 shape
  lifecycles**; 0 empty base states, 0 pictures on the last click, 0 empty
  frames, 0 Morph/entrance conflicts; max active view **45 words**; five type
  sizes. PowerPoint 16.0 opens 14 slides + 14 PNG + 14-page PDF, 0 repair; COM
  reports EntryEffect **3954** (Morph) at 1.2 s on slides 4/6/9/13.
- **Critic.** New experimental `scripts/deck_state_critic.py` grades `t=0` and
  every click. It **fails T066** with 58 gates (51 fail) and **passes T069a**
  with 0 gates. `design_critic.py` (with T069b's narrative dimension) gives
  T069a **4.33** (design 3.99, motion 5.0, rhythm 3.42, coherence 4.33,
  narrative 4.92).
- **Images.** Cover portraits and Plato are present at `t=0`; the timeline was
  re-ordered to Engels 1848 → Marx 1867 → Lenin 1917 so the dots sit under the
  work each face carries (T066 had 1848 under Marx).
- **Limits.** Morph interpolation was not captured frame-by-frame; 14 slides
  instead of 10; B states hand-authored on the T067 copy, not compiled by
  `deck_director.py`; no human rung 6.
  `experiments/T069-20261104-opencode-directed-deck/REPORT.md`.

## T068 [pptx] Deck Director compiler: Two-Pass screenplay, lifecycle state machine, five narrative laws — 2026-11-04

- **Why.** T067 named the missing artifact; T068 made it executable. The
  failure was an inverted pipeline: conversational prose was written before the
  spatial-temporal state machine existed.
- **Two passes.** Pass 1 locks stage inventory, `t=0` base state and lifecycle
  transitions (`enter`, `dim`, `highlight`, `exit`); Pass 2 weaves the spoken
  line with split-sentence bridging at causality pivots and implicit deictic
  anchoring.
- **Implemented.** `scripts/deck_director.py` validates, compiles and reports a
  ledger; `lab/schemas/deck_direction.schema.json` is the canonical schema;
  `slide_forge.py build --plan` consumes `director.json`.
- **Five laws (validator codes).** `NAR-CODA-TRAP` (no empty click; `t0_says`
  ≤ 35 words), `NAR-KARAOKE` (text/speech overlap ≤ 45 %), `NAR-UNANCHORED`
  (`post_click_says` must reference a target), `NAR-COLLISION` (cinematic figure
  or ≥ 3 movers needs a `lead_in`), `DEN-ACTIVE-VIEW` (≤ 45 active words).
- **Measured.** 3-slide directed build, QA 0 errors, critic 4.99/5.0, **6 object
  lifecycles**, **0 empty base states**; 7/7 unit tests. Previews are DeckCraft
  renders (rung 2), not PowerPoint playback.
- **Limits.** 3 slides is a proof, not a deck; complex custom layouts still need
  `inspect` tokens read back; `drill` zoom falls back to hyperlinks outside
  PowerPoint/DeckCraft; no human rung 6.
  `experiments/T068-20261104-antigravity-deck-director/REPORT.md`.

## T067 [pptx] Synthesis: direction before layout, state before effect — 2026-11-04

- **Why.** Four parallel streams audited the owner's critique of T066. The
  umbrella finding is that T066 did not lack effects; it lacked direction. No
  artifact said what the audience must see or believe at each moment, so layout
  finished first and motion only picked a click index.
- **Base state.** 3 slides opened with no readable claim, 9/10 titles were
  click-gated, 4/4 pictures arrived on the last click, and 51 clicks contained
  0 object lifecycles. The directed copy reaches 27 beats, 116 effects, a
  readable `t=0`, no picture on the last click and at most two movers.
- **Images.** One image is one block (face + ring + ground + caption) and enters
  on the sentence that names it, never after the last sentence. Identity images
  sit at `t=0`; evidence images enter on their naming beat; a coda image is
  banned. A wins the cover, B wins the argument slide.
- **Style.** `VisualStyle/1` plus five presets replaces "theme = palette +
  fonts" with geometry, material, depth, texture, image treatment, motion
  language and density; 5/5 specimens built native.
- **Motion.** Removing all nine decorative Morphs was a reset, not the target.
  The target is 3–4 semantic state-pair Morphs, each continuing one object or
  idea; no background/thread Morph.
- **Direction artefact.** `brief → script → beat sheet → shot list → motion
  plan`, where every shot declares `base_state` before `state_after`. Draft
  skill: `skills/deck-director/SKILL.md` (not wired).
- **Still missing.** `deck_state_critic` is specified but not implemented; no
  combined deck yet; no human review (rung 6). T068 is the directed build.
  `experiments/T067-20261104-opencode-deck-director/SYNTHESIS.md`.

## T067 [pptx] Visual style system — 2026-11-04

- **Why.** The owner asked for style, not only background and type: cartoon,
  liquid glass, clay, minimal, maximalist. The `theme` object had palette,
  fonts and layout only, so two decks could share a palette and still feel like
  different products.
- **Schema.** `VisualStyle/1` (`inputs/visual_style.py`): 9 colour roles; 3 type
  roles with a 5-step scale; geometry (sharp/rounded/blob/diagonal/mixed);
  material (flat/paper/glass/clay/collage/chrome); depth (flat/layered/2.5D/3D);
  texture (none/grain/halftone/paper/pattern); image treatment + mask + grade +
  area cap; motion language with five durations; density. The resolver emits build
  tokens; a linter audits a PPTX against its declared preset (palette, fonts,
  native share, raster share, effect vocabulary).
- **Presets.** `editorial-crimson` (T066), `liquid-glass`, `clay-cartoon`,
  `swiss-minimal`, `maximalist-collage`; all five validate, all five built as
  native specimens with one content unit (claim + portrait + two facts).
- **Measured.** 631,684 B, 5 slides, 165 words, 4–6 type sizes, native share
  90.0–94.7 %, raster 8.8–30.9 %, 49 native effects with durations exactly
  0.25/0.26/0.30/0.42/0.62/0.90 s; PowerPoint COM opens in 152 ms, PDF 5 pages.
- **Hardest native style.** Liquid glass: no backdrop blur, blend mode or
  refraction in DrawingML; the pane is an illusion of alpha + rim + specular +
  shadow. Clay is second (custGeom squircle + matte `sp3d` per object).
- **Finding.** A `gradFill` appended after `a:ln` is ignored and PowerPoint falls
  back to the theme fill; inserting it before the outline makes per-stop alpha
  work. Radial gradients ring at the ellipse unless alpha reaches 0 by ~78 % of
  radius. Both reproduced and documented.
- **Limits.** No human eye (rung 6); no Morph in the specimen; easing is
  plan-level, not frame-verified; clay rims are baked into the PNG; Swiss
  title/body 3.0 is outside the band. No product path changed.
  `experiments/T067-20261104-opencode-visual-style/style-system.md`.

## T067 [pptx] Image choreography (parallel stream) — 2026-11-04

- **Why.** The owner's first complaint about T066 was the image order: the
  portraits arrive last and mean nothing. This stream audited all seven image
  placements and wrote the timing law the deck was missing.
- **Audit.** Cover: 3/3 portraits on click 4/4, with three empty gold rings
  visible from t=0. Slide 2: the largest image in the deck (60.7 % of slide
  height) on click 7/7, while its red disc **and its “statue” credit** are on
  screen for six clicks. Slide 7: portraits 2–4, timeline 5, and the 1848 dot
  sits under the portrait captioned “Tư bản · 1867”. `image-audit.md`.
- **Rules.** 25 rules in five groups: role → legal beat (anchor at t=0,
  evidence on its naming beat, never after), one image focus, order = argument,
  grouping = argument, size/crop/cut-out, naming sentence. Two machine checks
  (`empty_frame_states`, `image_lag`). `image-rules.md`.
- **Variants.** Same layout, one variable: A = anchors at t=0; B = each image on
  its naming beat. Built on T066's assets; 2 slides each, 19/37 native effects;
  32 click states rendered by PowerPoint COM. A wins the cover, B wins the
  argument slide; the recommendation is A-cover + B-body.
- **Limits.** State renders are reconstructed, not played; no human eye; the
  variants are excerpts; the Plato fix is proposed but not built.
  `REPORT-image-choreography.md`.

## T067 [pptx] Skill audit and deck-direction draft — 2026-11-04

- **Why.** The owner judged T066: crop, palette and fonts good; motion has no
  *gu*; images appear last with no meaning; the deck was generated before a script
  existed. The brief was to find the cause in the skills, research it, and rewrite
  if necessary.
- **Audit.** Four root causes, each traced to code: (1) no causal artifact — Forge
  compiles layout first and passes only the deck title to `md.draft()`, so motion
  is a function of geometry; (2) intent is unrepresentable — the plan's `script`
  block is generated from slide titles and the validator only counts the strings;
  (3) style is a token list — `THEMES` + two fonts, while `theme_engine`'s seven
  archetypes sit orphaned; (4) the critic has no narrative dimension, identifies
  titles by placeholder only, and averages 153 per-effect checks so structure cannot
  move the score.
- **Control deck.** The lab's own reference example (`vi_chuyen_doi_so.json`, built
  by the default pipeline) scores 5.0 design / 5.0 motion / 4.88 overall with zero
  warnings and still opens its section and closing slides blank, and reveals its
  only picture on the cover's last click.
- **Measured.** T066: 51 click groups, 0 lifecycles, 9/10 titles animated, 4/4
  pictures on the last click, three slides with no base state. Probe and JSONs in
  `experiments/T067-20261104-opencode-deck-director/artifacts/measurements/`.
- **Proposal (draft only).** A `deck-director` layer: brief → script → beat sheet
  (9 jobs) → shot list (`base_state` first, `state_after` per click) → motion plan
  → build; `direction.json` compiles to `deck.json` + `director.json`; Forge needs
  one `plan` parameter and already has the `md.apply` seam. A style layer with
  palette/type, grain, image treatment and six motion figures. Critic additions:
  `narrative` dimension, `MOT-LIFECYCLE`, `MOT-FIGURE-REPEAT`, `DEN-VIEW`,
  `PLAN-DRIFT`, and rule-level scoring.
- **Limits.** No human eye and no PowerPoint render of either probe deck; the
  post-fix numbers are one measured parallel rebuild (51 → 27 clicks, no empty
  base state) plus untested predictions; the job vocabulary is a reasoned
  taxonomy, not measured; no compiler exists.
- **Status.** EXPERIMENTAL; review requested. Report:
  `experiments/T067-20261104-opencode-deck-director/REPORT.md`; skill draft
  `skills/deck-director/SKILL.md`.

## T066 [pptx] Triết học Mác – Lênin, Chương 1: native red editorial deck — 2026-11-04

- **Why.** The owner asked for a real Chapter 1 deck, not a template demo:
  vivid red, cut-out historical images from the internet, and complex motion.
- **Deck.** 10 native slides, 16:9, crimson/cream/gold identity; Palatino
  display + Arial body; four Wikimedia images background-removed with `rembg`,
  duotoned and circular-masked. 144 main-sequence effects, 51 click groups,
  nine 1.5 s Morph transitions (`!!thread` / `!!dot` continuity), speaker notes.
- **Evidence.** PowerPoint 16.0 opens the exact file, 10 slides, no repair;
  10 PNGs at 1920×1080; PDF 10 pages; `CreateVideo` 74 s (14 s teaser);
  `design_critic` overall 4.03 (motion 4.99, rhythm 4.48, design 2.98).
- **Limits.** Critic flags 21 type sizes and 10–12 pt card body / 8–9 pt
  captions; no human rung 6; cut-out edge artefacts on Engels/Marx; content is
  a summary, not a full textbook reproduction.
- **Status.** EXPERIMENTAL; review requested. Report:
  `experiments/T066-20261104-opencode-triet-hoc-ch1/REPORT.md`.

## T065 [cross] Lab hygiene: encoding repair, duplicate-ID and size checks — 2026-11-04

- **Why.** The first file every agent reads was corrupt (T057, finding 3), five
  task IDs had been used twice, and pptx code had reached `main` without PR or
  review. T065 makes the machine-checkable part checkable.
- **Encoding.** `docs/CHANGELOG.md` (812 markers, 161 lines),
  `domains/README.md`, `experiments/T045-…/REPORT.md`,
  `experiments/T046-…/REPORT.md` and `research/claims/T050-…md` were UTF-8 read
  through `cp1258`/`cp1252`. Repair: exact line restore from the pre-damage blob
  (`459852d^`, `318f748`) for 71 lines, then a byte-shape decoder for the rest —
  1 862 sequences on the base blobs, 0 left. Damage entered on 2026-11-01 in
  `459852d`, `bc7a071` and the PR #42 merge `f7185ae`.
- **Rule.** `lab/tools/check_layout.py` now fails on Markdown that is not UTF-8,
  starts with a BOM, carries C0/C1 controls, contains the markers (quoted lines
  opt out with `<!-- allow-mojibake -->`), or repeats a task ID in
  `research/tasks/INDEX.md`. It **warns** on committed files over 2 MB or tasks
  over 10 MB; 0 warnings today. Git LFS is an open owner decision
  (`lab/standards/OUTPUTS.md`).
- **Tests.** The 12 errors on a `cp1258` machine came from 12 `read_text()` calls
  without `encoding="utf-8"`. Suite: **476 tests OK, 8 skipped**, with and without
  `PYTHONUTF8=1`. New `tests/test_lab_hygiene.py` (15) covers the rules and the
  false-positive cases. CI gained `PYTHONUTF8=1`: new `.github/workflows/tests.yml`
  (ubuntu + windows) and the native-QA workflow.
- **Rules written.** pptx product paths change only through a PR with a review
  (`domains/pptx/DOMAIN.md`, pointer in `lab/standards/MERGE.md`); text is UTF-8
  without BOM and code passes `encoding="utf-8"` (`docs/ENVIRONMENT.md`).
- **Left open.** JSON artifacts of T039/T041/T045/T047/T051–T053 still carry
  damage and 4 are not UTF-8; they are hash-referenced, so a follow-up must
  re-extract, not text-edit. `HANDOFF.md`/`docs/STATUS.md` wait for the
  integrator after T058–T064. New workflow not yet run (no push from T065).
- **Report.** `experiments/T065-20261104-opencode-hygiene/REPORT.md`.

## T061 [pptx] One canonical interaction writer — 2026-11-04

- **Why.** `interactiveSeq` was written by three modules
  (`interactive_triggers.py`, `advanced_interactivity.py`,
  `slide_navigator.py`); `pptx_animator.py` owned none of it, so the T049
  root-cause fixes lived in one module and never reached the others.
- **What moved.** The writer (sequence shell, trigger conditions, click-step
  timing, hyperlink conflict, ID allocation) now lives in `pptx_animator.py`
  under "Interactive triggers, hyperlink conflicts, semantic actions". The
  three modules are thin callers; `interactive_triggers.py` keeps only the T033
  plan vocabulary. `advanced_interactivity.compile_one_slide_games_suite` is
  unchanged (PowerPoint COM writes its own timing).
- **T049 findings ported.** The interactiveSeq `cTn` carries its own onClick
  `stCondLst` and `endSync`; the click step runs at `delay="0"`; one `p:seq`
  per trigger shape; a trigger shape's click hyperlink is stripped, and adding
  a hyperlink to a trigger shape is reported as a conflict.
- **Byte evidence.** Both T048b decks rebuild to 43 identical zip members
  (`docProps/*` excluded). The T049 artifact is unchanged
  (`f91531f8…`) and still parses to 8 sequences (4 + 4).
  `build_canonical_interactive_seq` is byte-identical (`d1f76b7b…`).
- **PowerPoint.** COM 16.0 reads the canonical subtree as 1 interactive
  sequence, trigger "Inspect Button", target "Detail Panel", effect 48,
  0.5 s. The pre-T061 shape parses identically, so a parse count cannot prove
  the delay fix; T058's click harness must.
- **Tests.** 476 run, 8 skipped, OK (15 new in
  `tests/test_interaction_writer.py`). `lab/tools/check_layout.py` OK.
- **Report.** `experiments/T061-20261104-opencode-interaction-writer/REPORT.md`.

## T063 [pptx] Forge debt that users see — 2026-11-04

- **Why.** T057 named four defects a Forge user sees: count-up proxies stack in
  print/PDF/Morph, the highlight marker ignores horizontal alignment, decks
  carry 13–15 type sizes, and every cinematic deck trips MOT-SETTLE.
- **Fixed.** Count-up proxies now sit below an opaque final-value source (the
  container colour), so print/PDF/static Morph show one value while PowerPoint
  still counts up. Highlight geometry reads paragraph alignment and measures
  the real font. Type sizes come from the Office kit `type_scale_pt`
  (3–6 sizes; `kpi_stat` display token only when a KPI exists). Ken Burns
  releases to the authored frame before Morph; generated process tokens are
  authored at their last stop (T034 author-at-destination).
- **Evidence.** All five example decks: no TYP-SIZES or MOT-SETTLE warning,
  sizes 13–15 → 6, overall 4.36–4.53 → 4.70–4.88. PowerPoint PDF, PNG and
  CreateVideo frames inspected (rung 5); DeckCraft Morph frame used only as a
  static second reader (rung 4). 470 tests pass, 8 skipped.
- **Report.** `experiments/T063-20261104-opencode-forge-debt/REPORT.md`.

## T062 [pptx] Native asset factory: DeckCraft shapes vs SVG vs GLB — 2026-11-04

- **Why.** T057 asked whether DeckCraft's Merge/Freeform/Effects commands can
  give an agent **native, part-editable PowerPoint art**, instead of a picture
  or a 3D model that the Director cannot touch.
- **Built.** One 20-part device mockup compiled three ways from one part
  table: 228 DeckCraft commands → 25 named native shapes; the same parts as
  one SVG picture; the same parts as one extruded GLB. Evidence is PowerPoint
  COM at rung 4/5 plus pixel diffs, not simulation.
- **Result.** Native wins where it matters: 20/20 art parts addressable by
  name, 21 animations on 20 movers vs 0/20 and 0 for both alternatives, 25 KB
  vs 102 KB/224 KB, and 0.23 % renderer disagreement with DeckCraft. The
  falsifier half-fired: names survive `convert`, but a merge re-ids its result
  and DeckCraft silently accepts animation on the dead id (19/21 reached
  PowerPoint on the first build). Cost: 228 commands, no SVG import, and the
  art's own micro-text trips `design_critic.py`.
- **Deliverable.** `{"native_art": …}` Forge spec proposal + compiler with
  coded skips (`SKIP_NATIVE_ART_PLATFORM`, `SKIP_NATIVE_ART_NO_DECKCRAFT`);
  EXPERIMENTAL, not wired into `slide_forge.py`.
- **Report.** `experiments/T062-20261104-opencode-asset-factory/REPORT.md`.

## T060 [pptx] DeckCraft source study: in-slide animation frames — 2026-11-04

- **Why.** T057 found DeckCraft has no in-slide animation renderer and proposed
  a source study: find the timing-tree player, estimate
  `render-animation --slide N --click K --t ms`, and test the Forge `dynamic`
  deck against PowerPoint CreateVideo.
- **Source.** `storytold/deckcraft` @ `23ac4f7` (0.15.0, MIT/Apache-2.0). The
  player is `deckcraft-anim` (pure Rust): `Timeline` builds click steps and
  per-shape `AnimState`; `ShowState` adds navigation; `effects.rs` evaluates
  entrance/exit/emphasis/path; `render_slide` already accepts a per-shape state
  closure. No CLI animation command exists at HEAD.
- **Prototype.** A 151-line patch adds `render::shape_state` and
  `deckcraft-cli render-animation ... [--plan]`; it builds and renders the
  Forge deck. 98 `deckcraft-anim` tests and 20 CLI tests pass.
- **Fidelity.** 118/118 effects match PowerPoint's trigger; 106/106 finite
  durations match; 37/37 step counts; 29/37 step durations exact and 6 explained
  by after-previous chains. Path probe within 10 px at 1280. Preset coverage:
  102/198 map (51.5%), but at most 67/198 (33.8%) are exact/path; 96 missing, 27
  approximated, 8 identity-shifted. A probe found behaviour-level
  `repeatCount` is dropped (3.000 s PowerPoint vs 1.000 s DeckCraft).
- **Status.** Experiment only; no upstream push/PR. Patch plan in the report.
- **Report.** `experiments/T060-20261104-opencode-deckcraft-source/REPORT.md`.

## T058 [pptx] Interactive slide-show harness — 2026-11-04

- **Why.** T057 found that every interactive claim stopped at rung 4: nobody
  had clicked a shape trigger in a live show. `GotoClick` does not fire
  `interactiveSeq`.
- **Module.** `scripts/interactive_show_harness.py` starts a windowed show,
  finds the `PPTFrameClass` window by PowerPoint PID, becomes per-monitor DPI
  aware, places the window in the work area, calibrates slide→screen mapping
  against `Slide.Export`, sends `SetCursorPos`/`mouse_event` clicks, waits for
  stable frames and asserts pixel change inside the target box.
- **Evidence.** 5 runs / 25 steps, all passing on the T049 one-slide games and
  the T048b hub (9/9 edges including `lastslideviewed` 5→3). T049 cover clicks:
  100 % of the target box changed, 97.8 % of changed pixels inside the box.
  `GotoClick(1)` on the same deck: index 0→0, 0.000 % pixels. With a main
  sequence added, `GotoClick(1)` moves the index 0→1 but renders nothing
  (0.000 %). COM `GetClickCount/Index` stay 0 after a successful trigger click.
  Rung 5b; rung 6 still needs human review of the captures.
- **Defects found.** `interactive_triggers.apply_interactive_triggers` (T032)
  writes a file PowerPoint 16.0 refuses to open (`0x80004005`).
  `pptx_animator._interactive_sequence` omits `p:stCondLst`, so its trigger
  effect runs at slide load. Both were pre-T061; after merging T061, the rebuilt
  fixtures open and contain `stCondLst`/`onClick`.
- **Tests.** `tests/test_interactive_show_harness.py`: 36 tests (2 skipped; a
  native integration test is opt-in with `T058_NATIVE=1`).
- Report: `experiments/T058-20261104-opencode-interactive-harness/REPORT.md`.

## T064 [pptx] Review and decoupling of T055, Morph between two 3D camera views — 2026-11-04

- **Why.** T055 (native 3D product deck) was stacked on the unmerged T054
  branch, and its Morph question ("does the camera interpolate?") was open at
  rung 4. T064 was asked to decouple it, review it and answer the Morph
  question with `CreateVideo` frames.
- **Dependency.** One file: `make_product_glb.py` read the T054 worktree at an
  absolute path. The blockout is now a frozen input (`inputs/blockout.json`,
  SHA-256 `86bf30f8…cd389b`); the rebuilt GLB is byte-identical
  (`fd252d7c…f959143`), so no T055 evidence changed. The five T055 commits are
  rebased onto `ac5b45e` without the five T054 commits.
- **Review.** `accept-with-fixes`, findings R1–R10 in
  `research/reviews/T055-opencode-20261104.md`. R1 (dependency) and R5
  (absolute evidence paths) fixed in the rebase; R2 was a `CreateVideo`
  argument-order bug that had produced a 52 × 28 clip, not a PowerPoint limit.
- **Morph.** Two probe decks, a Fade control, a 25-rung camera ladder and a
  moving control square, rendered by PowerPoint at 1920 × 1080. Morph
  **does** interpolate the `am3d:camera` when both slides share one `model3d`
  part (camera x −1.0 → +1.2 over 1.7 s at constant brightness); with one
  `Add3DModel` embed per slide (T055's construction) the model fades out, is
  blank for 0.40 s and fades in at the new view. Duplicating the slide before
  changing the camera produces the shared part.
- **Evidence.** Rung 5 (CreateVideo frames) for the Morph claims; rung 4 for
  the package and camera parse; rung 6 missing. Report:
  `experiments/T064-20261104-opencode-native-3d/REPORT.md`.
- **Integration.** Merged by the integrator with T064; T055 stays
  EXPERIMENTAL with R3/R4/R6/R7/R8 open. HANDOFF and STATUS updated where the
  T055 merge order was stated.

## T059 [pptx] DeckCraft as second renderer: static, Morph and round-trip fidelity — 2026-11-04

- **Why.** T057 asked whether DeckCraft 0.13.1 can stand in for PowerPoint when
  PowerPoint is absent, and where it stops. This task measured it on 67 slides
  (five Forge decks, the two T028 pro decks) plus a synthetic per-kind probe,
  against PowerPoint `Slide.Export` and `CreateVideo`.
- **Static.** Whole-slide mean 0.5–1.5/255, `>40` 0.24–0.89%. Raster pictures
  (0.50), theme effects (1.06), vector shapes (0.83) and text (1.54) are close;
  charts break (13.1 weighted, 5.3–12.7% `>40`: markers, gridlines, legend,
  plot area); SVG icons are absent because DeckCraft draws the transparent PNG
  fallback (49.0, 28.4% `>40`); 3-stop gradients lose the middle stop
  (14.2, 6.1%); soft edges/bevels differ (8.6). The design critic is
  insensitive to all of it: score delta ≤0.01, far below the 0.2 falsifier.
- **Morph.** `render-transition` is not a proxy for PowerPoint Morph. On the
  Forge KPI transition PowerPoint hides 36/36 entrance shapes at t=0.25/0.5/0.75
  while DeckCraft draws 29/35/35; the T028 camera morph differs by 64.3 mean /
  40% `>40` even with zero entrance effects. Falsifier 2 triggered.
- **Round trip.** `convert` rewrites `p:cTn` 2641→2492, `p:anim` 338→245,
  `p:animEffect` 356→300, `p:graphicEl` 24→0 and drops all 5 SVG blips.
  PowerPoint parses the same effect list and transitions on 67/67 slides but
  149 fewer behaviours. Ascend/RiseUp `ppt_x` drops are identity (video diff
  0.0); Transparency is redundant; GrowAndTurn loses its rotation (2.4 peak);
  chart build targets are lost, so the round-trip chart runs 0.4–0.8 s ahead
  (14.3 peak, 13 frames >5). Not a safe last writer.
- **Wiring.** Proposed `slide_forge.render(..., renderer="auto")` fallback with
  `renderer`/`frame_source`/`label="DeckCraft render (not PowerPoint)"`/
  `evidence_rung=2`; implemented and unit-tested in
  `scripts/deckcraft_fidelity.py`, not wired into the product path.
- **Tests.** 471 run, 8 skipped, OK. Artifacts: 68 per-slide diffs, 8 contact
  sheets, 20 Morph strips, 5 playback strips, 11 CSV tables (5.7 MB).

## T057 [cross] Lead review, DeckCraft evaluation and next programme — 2026-11-04

- **Why.** After 22 tasks in four days (T035–T056) the owner asked Claude to
  act as lead: judge the state, name the difficulties and set the next
  research directions, and answer whether DeckCraft makes PPTX asset creation
  easier for an AI.
- **Findings.** 461 tests pass. The pptx core has not changed since T038 and
  the T034 problems (type scale, MOT-SETTLE, native interactive gate) are
  open. Five task IDs were used twice; pptx features reached `main` without
  PR or review; every review is by one agent (Argon); `HANDOFF.md` was
  mojibake and pointed at T047 as the next ID; three modules write
  `interactiveSeq` separately.
- **DeckCraft 0.13.1.** Static renders match PowerPoint closely (0.1–2.1% of
  pixels differ by >40; charts differ most); Morph frames in 0.19 s but their
  fidelity is unproven; no in-slide animation renderer; `convert` rewrites
  some timing nodes. Its 330 commands (also over MCP) add Merge Shapes,
  freeform curves, shape effects, background removal and SmartArt that
  python-pptx cannot do: useful for native PPTX assets, not for motion QA.
  Open source (MIT/Apache-2.0), so an animation-frame renderer is a research
  option (T060).
- **Programme.** Reserved briefs T058–T065 (harness, DeckCraft fidelity,
  DeckCraft source study, one interaction writer, native asset factory, Forge
  debt, T055 3D, lab hygiene), each with a builder and a critic from a
  different model family. Breadth domains frozen for one cycle.
- **Rewritten.** `HANDOFF.md` (clean UTF-8, Vietnamese) and `docs/STATUS.md`.

## T056 [vector] Part-based isometric product illustration (`iso-vector-craft`) — 2026-11-03

- **Why.** T053 proved that a product drawing must be a model, not a trace, but
  the result still read as a diagram. T056 adds the missing method: a measured
  part inventory, one camera chosen per product, four-tone materials and a
  written painter's order. The owner accepted the Technics V3 result and asked
  for the method on `main`.
- **Skill.** `skills/iso-vector-craft/SKILL.md`: 30–60 named parts, 1 unit = 1 mm,
  azimuth/elevation rules, 4–6 materials, detail budget, failure modes and a
  checklist. The MIT **Anatomy** kit (commit `1482e84`) is vendored with
  `LICENSE`/`ATTRIBUTION.md`; `kit/product-svg.mjs` bakes the light palette into
  literal values, adds `<title>/<desc>` and pins a real font.
- **Examples.** Technics SL-1200: 518 paths, 12 part groups, plinth 54, Ø330
  platter, Ø300 record, Ø100 label, Ø96 arm well. Gale Silver Monitor: 79
  paths front / 114 rear. Rolleiflex TLR: 217 paths, kept as a labelled hard
  subject stress test, not a showcase.
- **Evidence.** resvg renders for every artifact; VectorCraft `info` 0 warnings
  and all fonts exact; `tests/test_iso_vector_skill.py` (13 tests) checks XML,
  no raster/external refs, baked palette, path counts, 12 Technics part groups
  and the MIT attribution. Progression sheet keeps V1 (411 paths, 98-unit
  plinth, 18°) as the negative result; V2 (463, 54 units, 24°) is the silhouette
  win.
- **Status.** EXPERIMENTAL; owner approved the direction; Argon review
  `accept-with-fixes` (round 2) after the gimbal order, relative anchors,
  generic rules and DOM contract fixes; merged to `main` as a skill (not a
  canonical replacement for T053).
- Report: `experiments/T056-20261103-opencode-iso-vector/REPORT.md`.

## T053 [vector] Semantic 2.5D reconstruction (supersedes T051) — 2026-11-02

- **Why.** The owner rejected T051: Canny edges are a trace, not a
  reconstruction. T053 models the machine in object coordinates and draws the
  parts, instead of extracting pixel lines.
- **Module.** `scripts/vector_reconstruct.py`: axonometric projection, box,
  front rounded rect/circle, vertical/horizontal cylinder, tube, gradients and
  an SVG scene with semantic groups.
- **Scene.** `build_quickmill.py`: 14 parts / 16 groups, 101 primitive paths,
  5 live text elements, 1000 × 1000; one light, painter's order, no raster.
- **Evidence.** VectorCraft `info`: 16 groups, 102 paths, 5 types, 0 warnings;
  before/after sheet shows the T051 trace next to the reconstruction.
- **Tests.** `tests/test_vector_reconstruct.py` (16 tests); full suite 448
  tests OK (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T053, round 3);
  merged to main (PR #50).
- Report: `experiments/T053-20261102-opencode-vector-reconstruction/REPORT.md`.

## T051 [vector] Photo-to-vector line hierarchy and detail budget — 2026-11-02

- **Pipeline.** `scripts/photo_vector.py` segments a product photo (GrabCut,
  shadow trim), flattens 5 material tones, extracts/dedupes Canny edges, and
  classifies them as silhouette, form, detail or removed with recorded reasons.
- **Policy.** Form: length ≥ 5.5% of the object diagonal and turning ≤ 0.55°/px.
  Detail: short + strong, closed controls ≥ 3 mm and circularity ≥ 0.28; 1.5 mm
  scale floor. The full trace is kept as the strawman.
- **Result.** Line style: 34 form + 16 detail, 1,437 nodes, 0 fills, GrabCut IoU
  0.959, VectorCraft 0 warnings. Colour style: 15 fills, ΔE76 10.56. Full-line strawman:
  58 + 133, 2,268 (colour 3,178) nodes, visibly scribbled.
- **Evidence.** Four budget SVGs + line + full-line, VectorCraft renders, photo-vs-vector,
  layer stack, budget sheet, `levels.json`/`line.json`; 18 new tests.
- **Tests.** `tests/test_photo_vector.py` (18 tests); full suite 422 tests OK
  (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T051, round 2);
  merged to main (PR #49).
- Report: `experiments/T051-20261102-opencode-photo-vector/REPORT.md`.
## T052 [docx] Configurable standard profiles + Vietnamese scientific report — 2026-11-02

- **Profile layer.** `domains/docx/data/standard_profiles.json` adds four
  sourced profiles: `hust-datn-2017`, `vnu-uet-kl-2024`, `iso-7144-thesis` and
  `annual-report-gri`, with page, typography, numbering, caption position,
  front-matter order, reference position and page limits.
- **Merge.** `scripts/docx_profiles.py` merges profile defaults under the spec
  (explicit spec wins) and `document_forge --profile` applies them. The same
  content spec builds a HUST report (34 body pages, 48 total) and a VNU-UET
  report (35 body pages, 45 total).
- **Conformance.** `check_docx()` measures A4, margins, body/table font, size,
  line spacing, first-line indent, heading depth/numbering, chapter captions
  and position, page number, front-matter order, references/citations, abstract
  length, body pages and equations. Both builds pass (23/23 and 24/24).
- **Chapter numbering.** `STYLEREF "Heading 1" \s` + `SEQ ... \s 1` for
  figures, tables and equations; `Chapter Unnumbered` standalone style for
  `Mở đầu` so it does not shift the Heading 1 counter.
- **Report content.** 59 headings (max H3), 23/22 tables, 7 figures, 9 native
  equations, 12 references, 13 citation fields, thesis cover, declaration,
  task, abstract, abbreviations, lists, appendices.
- **Cross-asset.** SVG architecture/window diagrams via VectorCraft; training,
  PR, F1, ablation and latency charts via Chart Forge (SheetCraft).
- **Audit.** Both builds: 0 errors, 0 warnings with profile-aware margin floor;
  204 fields, 88 bookmarks, `vi-VN`; Word refreshed fields and exported 48/45
  pages.
- **Tests.** `tests/test_docx_profiles.py` (7 tests); full suite 411 tests OK
  (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T052, round 2); merged to main (306f5f2).
- Report: `experiments/T052-20261102-opencode-scientific-report/REPORT.md`.

## T050 [xlsx] VBA UserForm + composed dashboard — 2026-11-02

- **UserForm.** `scripts/userform_forge.py` injects a real `frmEntry` (22
  controls: 8 labels, 4 combo boxes, 4 text boxes, 3 buttons, title/hint/status)
  and a `FormTools` module into an `.xlsm`; `btnSave_Click` validates and appends
  to the hidden Data sheet.
- **Dashboard.** `scripts/dashboard_forge.py` composes a 12-column A4 landscape
  dashboard: 4 KPI cards, 4 native charts (line/column/bar/doughnut), hidden
  Data/Trend/Model, 3 filter/form buttons, one-page print area.
- **Evidence.** Excel opened the exact XLSM: 4 sheets (3 hidden), 4 charts,
  3 buttons, 22 form controls; Dashboard exported as **1 page**; form code has
  `btnSave_Click`/`ClearForm`/`nextId`. Macro execution remains blocked by host
  policy; the form was not shown end-to-end.
- **Tests.** `tests/test_dashboard_userform.py` (3 tests); full suite 407 tests
  OK (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T050, round 2); merged to main (90695a9).
- Report: `experiments/T050-20261102-opencode-userform-dashboard/REPORT.md`.

## T048 [xlsx] Workbook UX: hidden data, VBA input, tab colour, merges — 2026-11-01

- **UX layer.** `sheet_forge` accepts a `ux` block: per-sheet `hidden` /
  `very_hidden`, `tab_color`, `protect`, and `input_form`.
- **Input form.** A visible Input sheet with 18 merged layout ranges, 8 data
  validations, auto Task ID, inline status and 3 macro buttons.
- **Hidden data.** Data/Model/Team/Gantt/Relations hidden; Pivot/Lookups
  veryHidden; only Dashboard/Input visible. Tab colours set.
- **Protection.** Input and Dashboard protected; input cells unlocked.
- **VBA.** `AddRecord`/`ClearForm`/`RefreshDashboard`/`SetStatus`; button
  macros rewritten to `[0]!DashboardTools.*` after SaveAs.
- **Evidence.** Excel opened XLSX/XLSM; 3 buttons, 8 validations, 2 protections,
  5 hidden + 2 veryHidden; Input and Dashboard 1-page PDFs; module present in
  `.xlsm`. Macro execution blocked by host policy — not claimed.
- **Limits.** Hidden ≠ secure; merged cells layout-only; no UserForm/audit
  log/undo; form validation is type/list only.
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T048, round 2); awaiting owner merge.
- Report: `experiments/T048-20261101-opencode-workbook-ux/REPORT.md`.

## T047 [docx] Standards-controlled annual/ESG report — 2026-11-01

- **Standards profile.** `domains/docx/data/report_standard.json` declares ISO
  7144:1986 (structure), ISO 2145 (numbering), ISO 690:2021 (references), ISO
  80000-1/8601-1 (units/dates), WCAG 2.2, GRI 1/2/3/305, with 10 controls and
  evidence. The report prints the control matrix before the TOC.
- **Front matter order.** `front_matter.order: "iso7144"` renders abstract →
  preface → TOC → lists; references move after appendices and use an
  unnumbered Heading 1 so the running header still works.
- **Content depth.** 25 pages, 37 tables, 5 equations (2 numbered), 4 figures,
  10 material topics, 5 stakeholder groups, Scope 1/2/3, a 37-row GRI content
  index, data appendix, glossary and 11 references.
- **Cross-asset.** Camera illustration authored as SVG, rasterised by
  VectorCraft, trimmed/graded/composited by Pillow; revenue and emissions charts
  built by Chart Forge (SheetCraft), exported by Excel, embedded with source and
  alt text.
- **Parser.** `word_math` now accepts escaped punctuation and the LaTeX control
  space (`\%`, `\&`, `\ `), covered by tests.
- **Evidence.** Word opened the exact DOCX, refreshed fields and saved; 25-page
  PDF inspected; audit clean: 101 fields, 89 bookmarks, 37 tables, 4 figures,
  5 equations, `vi-VN`; full suite 395 tests OK.
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T047, round 2); awaiting owner merge.
- Report: `experiments/T047-20261101-opencode-standards-report/REPORT.md`.

## T046 [xlsx] Advanced workbook and dashboard — 2026-11-01

- **Sheet Forge.** `scripts/sheet_forge.py` composes a 7-sheet programme
  workbook from a semantic spec: typed data table, cross-sheet model
  (`SUMIFS`/`COUNTIFS`/`AVERAGEIF`/`INDEX`+`MATCH`, named ranges), image table,
  native Gantt, relationship matrix, PivotTable and a designed dashboard.
- **Image table.** Pictures are inserted in cells with alt text and a fixed row
  height; the `Team` sheet prints A1:D7 on one page.
- **Gantt.** Stacked bar, transparent start series (`<a:noFill/>`),
  date-formatted value axis with explicit serial min/max (bar charts have no
  date category axis), reversed categories; inserted on the Gantt sheet and on
  the dashboard.
- **Relationship view.** Matrix heatmap with a 3-colour scale; the node-link
  scatter was tested and rejected (one series per edge does not scale, and the
  experimental build did not render every series consistently) and is recorded
  as a negative result.
- **Pivot.** Native PivotTable built by GridCraft `insert.pivotTable`; Excel
  reads `PivotTable1` over `Data!R1C1:R61C11`. Without GridCraft a `SUMIF`/
  `COUNTIF` summary is written to the `Pivot` sheet in the first pass.
- **VBA.** `scripts/vba_forge.py` writes a `DashboardTools` `.bas` (with a
  worksheet guard) and injects it into an `.xlsm` only when Excel trusts the
  VBA project object model.
- **Dashboard.** 4 formula-driven KPI cards, 2 fixed one-cell-anchored charts,
  matrix, one source note; print area 29.21 × 20.39 cm (≈93% A4), Excel export
  one page. Audit clean (3 charts, 0 errors/0 warnings/0 notes).
- **Evidence.** Excel opened the exact XLSX/XLSM, recalculated formulas, read
  the pivot and exported 5 sheets; `tests/test_sheet_craft_advanced.py` (5
  tests); full suite 385 tests OK with `PYTHONUTF8=1`.
- **Review fixes (Argon).** Gantt `Start` transparency + value-axis min/max/date
  format; re-apply axes after GridCraft's pivot round-trip; KPI formulas; pivot
  fallback on the Pivot sheet; VBA worksheet guard; dashboard/Gantt print areas
  reduced to ~93% A4; hidden-series/`gantt` audit detection; negative-result
  reasoning corrected. Argon **approve T046** (round 2).
- **Status.** EXPERIMENTAL; review accepted; awaiting owner merge.
- Report: `experiments/T046-20261101-opencode-advanced-xlsx/REPORT.md`.

## T045 [docx] Advanced report craft — side-by-side media, equations, rich tables — 2026-11-01

- **Native equations.** `scripts/word_math.py` parses a strict LaTeX subset into
  OMML (`m:oMath`): fractions, scripts, roots, sums/integrals, delimiters,
  accents, Greek letters and common operators. Unsupported constructs raise an
  explicit error. Equation numbering uses `SEQ Equation`.
- **Side-by-side media.** `figure_text` emits a borderless two-cell table with
  an inline picture and a text column, caption below; no floating anchors.
- **Rich tables.** `table.advanced` supports multiple header rows, `colspan`/
  `rowspan`, explicit merges, per-cell alignment/vertical alignment, fills,
  row heights, cell margins and image cells.
- **Callouts / KPI strip / cover hero.** Shaded single-cell callouts, a
  borderless label/value strip, and a full-text-width inline cover image.
- **Cross-craft.** Cover and icons are SVG rasterised by VectorCraft
  (`convert --scale 1`), then accepted by the DOCX audit/render.
- **Audit depth (review fix).** `audit_docx` counts equations/equation numbers,
  merged cells, images in cells and languages; validates `gridSpan` vs
  `tblGrid`, orphan `vMerge`, image width vs `tcW`, OMML empty/one-sided parts
  and alt text; `docDefaults` + styles carry `vi-VN`.
- **Evidence.** 11-page Word PDF inspected; audit clean (20 fields, 15
  bookmarks, 6 tables, 6 drawings, 2 equations/1 numbered, 5 merged cells,
  5 images in cells); `tests/test_document_advanced.py` (5 tests) + T039 tests;
  full suite 385 tests OK with `PYTHONUTF8=1`. Argon **approve T045** (round 2).
- **Status.** EXPERIMENTAL; review accepted; awaiting owner merge.
- Report: `experiments/T045-20261101-opencode-advanced-docx/REPORT.md`.

## T044 Multi-Asset Pipeline Protocol, User Experience Maximization & Local Autonomy Charter — 2026-11-01

- **Official Owner Mandate Codification (togcoder).** Integrated official directive on cross-domain agentic skill development:
  - Skills do not produce single isolated files; they orchestrate compound assets across multiple target applications.
  - Elevate user experience to the peak: deeply decode user intent to achieve first-pass satisfaction ("đúng ý ngay từ lượt đầu"), eliminating tedious regeneration.
  - Mandate cross-asset pre-processing pipelines: edit/crop/mask images before slide/doc embedding; normalize audio (EBU R128) before video muxing; validate structured data before chart rendering.
  - Authorize full local operational autonomy: agents working locally have complete freedom to download fonts, models, and install code libraries, provided workspaces remain tidy in git-ignored `workspace/` and transient files are deleted.
- **Protocol 04 Added (`lab/protocols/04_cross_asset_pipeline.md`):** Formally codified the 3 canonical pre-processing pipelines (Visual/Raster, Audio/Motion, Data/Chart), the First-Pass Excellence law, and the Local Autonomy & Cleanliness Law.
- **Core Governance Updates:**
  - `AGENTS.md`: Added First-Pass Intent Fulfillment, Cross-Asset Pre-processing Pipeline, and Local Autonomy & Cleanliness Law to Rules for Every Agent.
  - `lab/CHARTER.md`: Added Goals 4 & 5 (First-Pass Fulfillment, Cross-Asset Orchestration) and principles on pre-processing before embedding and local autonomy.
  - `lab/PROTOCOL.md`: Added cross-asset pipeline step and local resource freedom to the agent research lifecycle.
  - `README.md`: Upgraded the lab introduction to reflect the Cross-Domain Agentic AI Lab vision.
  - `domains/cross/DOMAIN.md`: Updated scope, code table, and rules with Protocol 04.
- **Cross-Pipeline Validator (`scripts/cross_pipeline.py`):**
  - `validate_image_for_embedding`: Verifies aspect ratios (16:9, 4:5, 1:1), minimum resolutions, alpha channels for art washes, and canvas mode luminance harmony.
  - `validate_audio_for_muxing`: Verifies EBU R128 loudness (-14.0 LUFS), True Peak safety ceiling (<= -1.0 dBTP), and BGM auto-ducking attenuation.
  - `validate_chart_data_for_presentation`: Verifies zero-error numerical integrity (no NaNs, nulls, division-by-zero) and Miller 7+-2 cognitive density.
- **Tests.** Added `tests/test_cross_pipeline.py` (5 unit tests). Full lab test suite passes **359 tests 100% (skipped=4)**; `lab/tools/check_layout.py` reports `layout OK`.

## T043 Dynamic Theme Engine: Need-Based Synthesizer, Reference Teardown, Composite Backgrounds & AI Image Harmonizer — 2026-11-01

- **Argon Strategic Consultation (game25072003 / yep).** In response to owner directive that themes are infinite and must be driven by user need and reference decks, collaborated with Gemini 4 Argon (`gemini-argon`) on `chat_id: 2:53675cab70c50cda` to formulate the Dynamic Theme Engine architecture:
  - Adversarial review rejected raw `<a:srgbClr>` counting in favor of Area-Weighted Clustering and `<a:schemeClr>` resolution.
  - Perceptual color math in pure Python (sRGB <-> Linear <-> OKLab <-> OKLCH, Relative Luminance Y, WCAG 2.1 contrast ratio).
- **Composite Background & Translucency Architecture (Addressing User Feedback):**
  - Addressed critical design reality: professional decks NEVER rely on flat single-color (`đơn sắc`) fills.
  - Proved via Pillow alpha histogram on user's sample decks: `Webinar Keynote Presentation.pptx` media assets `image1.png` and `image6.png` feature 60.9% to 64.9% translucent pixels ($1 \le \alpha \le 254$), overlaying a warm ecru canvas (`#F4F1E9`) to create soft organic pastel tone variations.
  - Proved shape alpha in `Blue Modern Business Pitch Deck Presentation.pptx`: explicit OOXML `<a:alpha val="36863"/>` (36.86% opacity) for frosted glass containers over a 2362x1575 composite image texture.
  - Integrated 4-layer Composite Background Recipe into `scripts/theme_engine.py`: Layer 0 Canvas Base Tone, Layer 1 Atmosphere/Translucent PNG Washes, Layer 2 Tint Washes/Glassmorphism Cards, Layer 3 Foreground Typography.
- **Core Engine Module (`scripts/theme_engine.py`):**
  - `PPTXThemeExtractor`: Reverse-engineers any PPTX reference file. Weighting: Backgrounds ($A = 	ext{slide\_area} 	imes 1.0$), Shapes ($A = 	ext{cx} 	imes 	ext{cy}$), Text ($W = 	ext{len} 	imes 	ext{size}^2 	imes 12700^2$), Full-slide background sampling via Pillow. Agglomerative clustering in OKLab ($\Delta E < 0.035$). Computes Salience Score for Accent: $	ext{Score} = C 	imes 2.5 + \Delta E 	imes 1.5 + \ln(1 + 	ext{ratio})$. Extracts typography hierarchy, detects mammoth Hero KPIs (e.g. 202pt), and geometric modular scale ($r = (S_{	ext{h1}} / S_{	ext{body}})^{1/3}$). Extracts `background_recipe` with translucency ratios and shape alphas.
  - `classify_canvas_mode`: Distinguishes `DARK_CANVAS` ($Y < 0.18$), `WARM_PAPER` ($0.72 \le Y \le 0.96, 0.010 \le C \le 0.060, 50^\circ \le H \le 110^\circ$), `LIGHT_CANVAS` ($Y \ge 0.72$), and `MID_TONE_CANVAS`.
  - `synthesize_theme_from_need`: Synthesizes complete ThemeSpecs from user topic/intent strings across 5 foundational archetypes (`INDUSTRIAL_QCC`, `TECH_PITCH_DARK`, `EDITORIAL_WARM_KEYNOTE`, `EXECUTIVE_STRATEGY`, `SUSTAINABLE_BIO`). Supports Dynamic Hue Override (rotates Hue in OKLCH while strictly preserving Lightness and Chroma) and assigns layered background recipes.
  - `build_harmonized_image_prompt`: Prompt builder guaranteeing visual harmony between generated AI images and the slide theme (6500K cool studio for Dark Canvas, 3800K soft morning window light for Warm Paper, 5500K high-key for Light Canvas). Slot framing: 16:9 hero full-bleed (60% negative space for typography), 16:9 atmospheric backdrop texture, 4:5 split/angled mask, 1:1 isolated translucent art wash on white background for alpha-mask conversion, 1:1 isometric bento.
- **Tests.** Added `tests/test_theme_engine.py` (14 unit tests). Verified native teardown of user's `Blue Modern Business Pitch Deck` (`DARK_CANVAS`, `#01152B`, `Aileron`, 202pt KPI, 36.86% shape alpha) and `Webinar Keynote Presentation` (`WARM_PAPER`, `#F4F1E9`, `TT Commons Pro` + `TAN Mon Cheri`, pastel accents, >60% translucent PNG overlays). Full suite passes **354 tests 100% (skipped=4)**; `lab/tools/check_layout.py` reports `layout OK`.

## T042 Multi-Domain Design Canons: Video, Vector/SVG, 3D/Solid, CAD & Audio — 2026-11-01

- **Argon Multi-Domain Consultation.** Partnered with Gemini 4 Argon (\gemini-argon\) to establish mathematical formulas, geometric tokens, and handoff contracts across all specialized ArtCraft domains (\D:\\artcraft\).
- **5 Formal Domain Canons (\knowledge/\):**
  - \knowledge/video_canon.json\: SMPTE RP 2046-2 / EBU R95 safe areas (Action Safe 3.5%, Title Safe 5.0%), 9:16 vertical dead zones (top 220px, bottom 440px, right action rail), ASL shot duration, J-cut (12-24 frames lead) and L-cut (15-30 frames trail) asynchrony, and EBU R128 audio mastering (-14.0 LUFS, True Peak <= -1.0 dBTP, sidechain ducking -14 dB).
  - \knowledge/vector_canon.json\: W3C SVG 2.0, 24x24 icon grid (20x20 live area), optical trim boxes (Circle d=20, Square 18x18, Landscape 20x16, Portrait 16x20), non-linear stroke scaling formula W(S) = W0 * (S/S0)^0.75, and Bezier 90-degree circle handle ratio kappa ~ 0.55228.
  - \knowledge/3d_solid_canon.json\: Metric scale (1 unit = 1.0 mm, Y-up glTF), No-Sharp-Edge Law (micro-bevel R = 0.005 * min(W,H,D) bounded in [0.2, 0.5] mm), concentric fillets, True Isometric camera (45-deg azimuth, elevation arctan(1/sqrt(2)) ~ 35.264-deg), 3-point studio lighting (Key 1.0, Fill 2:1/4:1, Rim 1.0), and PBR material albedo clamp with strict prohibition on ambiguous metalness M in [0.2, 0.8].
  - \knowledge/cad_iso_canon.json\: ISO 5457 sheet dimensions (A4 to A0) with 20.0mm left margin, ISO 128 line weight hierarchy (0.50mm group: 0.50, 0.25, 0.18mm), ISO 129 dimensioning geometry (10mm 1st tier, 7mm 2nd tier, 1.0mm origin offset, 2.0mm overshoot, 3:1 closed filled arrows), and ISO 7200 title block (180.0mm width).
  - \knowledge/sound_canon.json\: SoundCraft mastering targets (EBU R128, ITU BS.1770-4, 48kHz 24-bit PCM, stem dynamic ranges, auto-ducking attack/hold/release envelopes).
- **Multi-Domain Evaluator & Calculators (\scripts/multi_domain_canons.py\).** Implemented pure Python token accessors, geometric calculators, and pre-flight validation rules for all 5 domains.
- **4 Native ArtCraft Bridges (\scripts/\):**
  - \scripts/filmcraft_bridge.py\: Headless runner for \FilmCraft\\filmcraft-cli.exe\ (probe, render frame, export, inspect).
  - \scripts/solidcraft_bridge.py\: Headless runner for \SolidCraft\\solidcraft-cli.exe\ (eval, snapshot, render, icon export).
  - \scripts/cadcraft_bridge.py\: Headless runner for \CADCraft\\cadcraft-cli.exe\ (info, convert DXF/DWG/SVG/PNG/PDF, sample generator).
  - \scripts/soundcraft_bridge.py\: Headless runner for \SoundCraft\\soundcraft-cli.exe\ (info, convert, normalize, resample).
- **Domain Cards Registered (\domains/\):** Created \domains/video/DOMAIN.md\, \domains/3d/DOMAIN.md\, \domains/cad/DOMAIN.md\; updated \domains/svg/DOMAIN.md\ and \domains/README.md\.
- **Verification Evidence Artifacts (\experiments/T042-20261101-antigravity-multi-domain-canons/artifacts/\):**
  - \cad_sample_bracket.svg\ (99 KB) & \cad_sample_bracket.png\ (115 KB) via \cadcraft-cli.exe sample\.
  - \solidcraft_icon.png\ (21 KB) via \solidcraft-cli.exe icon\.
- **Tests.** Added \	ests/test_multi_domain_canons.py\ (24 unit tests). All **340 tests pass 100% (skipped=4)**; \lab/tools/check_layout.py\ reports \layout OK\.

## T041 [xlsx] SheetCraft — controlled standard DrawingML charts — 2026-11-01

- **Chart Forge.** `scripts/chart_forge.py` builds a workbook/chart from
  `domains/xlsx/schemas/chart_spec.schema.json`: column/bar, line, area, pie,
  doughnut, scatter, bubble, radar, stock and combo; axes, labels, legend,
  markers, trendlines, number formats and print area.
- **Chart patch.** `scripts/chart_patch.py` edits existing chart OOXML:
  title/legend/axes/bar gap/data labels/series style/manual plot layout and
  converts `xdr:twoCellAnchor` to a fixed `xdr:oneCellAnchor`.
- **Chart audit.** `scripts/chart_audit.py` measures geometry, zero baseline,
  log scaling, category density, labels, legend, contrast/deuteranopia, pie
  slices, 3-D, fonts, series count, print area, alt text and the chart cache.
- **Evidence.** Three synthetic fixtures (combo secondary axis, doughnut,
  scatter + trendline) pass the audit with no errors/warnings; Excel opened the
  exact files and exported the charts; GridCraft PDF rendered them but dropped
  Vietnamese diacritics. Waterfall/treemap/histogram/box/funnel remain raw-OOXML
  recipes, not generated.
- **Review fixes (Argon).** Combo series/axis mapping, manualLayout/`a:ln` child
  order, print-area geometry, full cache comparison with worksheet fallback,
  Excel-first `--render`, and `gridcraft_bridge` use instead of a hard-coded
  `D:\artcraft` path.
- **Tests.** `tests/test_sheet_craft.py` (10 tests) covers build/audit, combo
  second-series patch, per-axis max, print-area rejection, stale cache,
  manualLayout order, small chart, doughnut palette and schema. Full suite:
  326 tests OK with `PYTHONUTF8=1`.
- **Status.** EXPERIMENTAL; review requested. One task = one domain; the
  document half is T039 [docx].
- Report: `experiments/T041-20261101-opencode-sheet-craft/REPORT.md`.

## T039 [docx] DocumentCraft — professional Word canon and real fields — 2026-11-01

- **Standards research.** Mapped the binding hierarchy (law/contract/template →
  ISO 7144/2145/690/7200/8601/80000 → institutional rules), marked ISO 5966 as
  withdrawn, and recorded the sources/statuses in
  `domains/docx/data/document_system.json`.
- **Document Forge.** `scripts/document_forge.py` builds a DOCX from
  `domains/docx/schemas/document_spec.schema.json`: cover, unnumbered front
  matter, linked multilevel headings, `TOC` field, standard `TOC \c` lists of
  figures/tables updated through `TablesOfFigures`, `SEQ` captions,
  `STYLEREF`/`SECTIONPAGES` headers/footers, inline images with alt text, fixed
  table grids with repeating headers, references and appendix A/A.1.
- **Word field kit.** `scripts/word_field_kit.py` writes/audits fields,
  bookmarks and captions; `scripts/document_audit.py` is the standalone audit.
- **Evidence.** Structural audit clean (29 fields, 22 bookmarks, 3 tables, 2
  figures, no errors/warnings); Word refreshed the exact file (including
  `TablesOfFigures`) and exported a 12-page PDF; pages inspected. WordCraft was
  a fallback (physical TOC page numbers, dropped `descr`, Vietnamese PDF font
  clipping). No PDF/UA, PDF/A or human edit/print yet.
- **Tests.** `tests/test_document_craft.py` (6 tests) covers fields/bookmarks,
  broken targets, broken bookmarkEnd, table width, en-US language and optional
  WordCraft refresh. Full suite: 322 tests OK with `PYTHONUTF8=1`.
- **Review fixes (Argon).** Standard `TOC \c` lists updated via
  `TablesOfFigures`; bookmarkEnd balance and per-section width checks; spec
  language instead of hard-coded `vi-VN`; `SECTIONPAGES` for the restarted body.
- **Status.** EXPERIMENTAL; review requested. One task = one domain; the
  spreadsheet half is T041 [xlsx].
- Report: `experiments/T039-20261101-opencode-office-canon/REPORT.md`.

## T040 multi-domain lab restructure — 2026-11-01

The repository is now organised as a multi-domain design lab:

- `lab/` holds the charter, the agent protocol, and the research, review,
  merge and outputs standards. The shared protocols, schemas, registry and
  templates moved there.
- `domains/` has a card per domain (pptx, docx, xlsx, svg, cross), each with
  its own thesis, canon, code status and evidence ladder.
- `research/reviews/` holds peer critiques.
- `workspace/` is for scratch and is git-ignored. `output/` is frozen.
- `lab/tools/check_layout.py` and its test keep outputs out of the root.
- `AGENTS.md` and `HANDOFF.md` were rewritten lab-wide.

No design research was done. Report:
experiments/T040-20261101-claude-lab-restructure/REPORT.md.

## T038 PPTX Design Canon Tokens, Asymmetric & Bento Grids, Optical Balance & Critic Rules — 2026-11-01

- **Argon Dissection & Design Canon Foundations.** Partnered with Gemini 4 Argon (`gemini-argon`) to dissect and codify high-craft mathematical formulas into `knowledge/design_system.json` (v1.1.0):
  - *Deck Chrome Bounds:* Slide $960 \times 540\text{ pt}$, safe margins $48/36\text{ pt}$, logo watermark ($w \le 72, h \le 24$, $y=20\text{ pt}$ top-right, suppressed on cover/divider/closing/break slides), section breadcrumbs ($10\text{ pt}$ uppercase tracked font), and progress tracker ($y=537, h=3\text{ pt}$ along bottom edge).
  - *Optical Icon Balance:* Equalizes perceived mass across geometric shapes (Square $0.88\times$, Circle $1.0\times$, Wide $1.08\times/0.82\times$, Triangle $1.05\times$ with $+0.06\times$ apex upward shift, Badge $2.0\times$).
  - *3-Layer Background Depth:* Z0 Base Canvas (135° Deep Slate `#0B0F19` $\rightarrow$ `#111827` or Light Alabaster `#F8FAFC` $\rightarrow$ `#EDF2F7`), Z1 Ambient Radial Glow Orbs (blurred $120-160\text{ pt}$, opacity $0.12-0.18$, morph-linked via `!!` prefix), Z2 Surface Cards (glassmorphism opacity $65-75\%$, top-lit border, corner radius $8-12\text{ pt}$, inner padding $20-28\text{ pt}$).
  - *Content Layout Canons:* Symmetric grids (2-col $422\text{ pt}$, 3-col $274\text{ pt}$, 4-col $204\text{ pt}$), Asymmetric Golden Ratio (Major $522\text{ pt}$ / $61.8\%$, Minor $322\text{ pt}$ / $38.2\%$), and Bento Grid (Hero $496 \times 396\text{ pt}$ [7/12 width], Top-Right $348 \times 188\text{ pt}$, and 2 Bottom-Right split cards $164 \times 188\text{ pt}$).
  - *Nancy Duarte Pattern Breaks:* Automatic pacing triggers for decks of $\ge 5$ slides near $1/3$ and $2/3$ milestones ($\ge 70\%$ negative space, single bold statement $36-44\text{ pt}$ or mammoth KPI $72-96\text{ pt}$, chrome suppressed) to eliminate cognitive fatigue.
  - *Color & Typography:* 60-30-10 surface area bounds, Modular Scale token table (caption $11\text{ pt}$, body_base $14\text{ pt}$, card_title $18\text{ pt}$, slide_title $28\text{ pt}$, hero $44\text{ pt}$, kpi_stat $72\text{ pt}$).
- **Programmatic Helpers (`scripts/design_system.py`).** Added `chrome()`, `optical_icon_compensation()`, `bento_grid_layout()`, `asymmetric_golden_layout()`, `duarte_break_positions()`, `modular_scale()`, and `background_layers()`.
- **Slide Forge Compilation (`scripts/slide_forge.py`).** Added `asymmetric`, `bento`, and `duarte_break` layout compilers, automatic deck chrome injection, and optical icon balancing.
- **Design Critic Rules (`scripts/design_critic.py`).** Implemented and registered `CHROME-SAFE`, `OPT-ICON`, `LAY-BENTO`, and `DUA-BREAK` rules; returns detailed `evaluations` audit log.
- **Tests.** Added `tests/test_pptx_design_canon.py` (12 unit tests). Total project test suite expanded to **318 tests, 100% passing (0 failures, 4 skipped)** in 14.90s.

## T037 Multi-Craft Native Bridges & Intent-Empathy Decoder — 2026-11-01

- **Multi-Craft Bridges.** Built `scripts/wordcraft_bridge.py`, `scripts/gridcraft_bridge.py`,
  and `scripts/vectorcraft_bridge.py`. Connects natively to `wordcraft-cli.exe`, `gridcraft-cli.exe`,
  and `vectorcraft-cli.exe` in `D:\artcraft`. Provides headless document/sheet/vector inspection,
  page rendering, formula evaluation, and cross-format conversion.
- **Intent & Empathy Decoder Engine (`scripts/intent_decoder.py`).** Implemented Protocol 00:
  parses raw prompts into 5-dimensional `IntentBrief` documents matching `schemas/intent_brief.schema.json`
  (Audience Persona, Cognitive Budget, Viewing Context, Canonical System, Craft Routing).
- **Tests.** Added `tests/test_craft_bridges.py` and `tests/test_intent_decoder.py`. Test suite
  expanded from 296 to **302 tests, all passing (0 failures, 4 skipped)** in 8.69s.

## T036 Universal ArtCraft Hub, Multi-Agent Protocols & Intent Schemas — 2026-11-01

- **Argon Architecture Consultation.** Consulted Gemini 4 Argon (`gemini-argon`) on multi-agent
  governance, identifying 4 architectural traps: unbounded mesh chat (solved by DAG contracts),
  LLM python bias (solved by 3-tier capability escalation gate), blind code review (solved by
  render-before-review), and lack of empathy (solved by 5-dimensional intent briefs).
- **Universal ArtCraft Discovery & Hub.** Built `scripts/sync_artcraft_capabilities.py` and
  `scripts/artcraft_hub.py`. Automatically catalogs all 13 tools in `D:\artcraft`, generates
  `registry/artcraft_capabilities.json` (hash `21eaaf51d6891acf`) and `registry/capability_gaps_backlog.md`.
- **Human Intent & Empathy Schema.** Created `schemas/intent_brief.schema.json` modeling 5 dimensions:
  Audience Persona, Cognitive Budget (Miller/Hick, Z/F pattern), Viewing Context, Canonical System
  (Swiss Grid, Dieter Rams, Tufte, IBM Carbon, Material 3), and Craft Routing.
- **Cross-Delegation & Critique Contracts.** Created `schemas/handoff_contract.schema.json`
  (enforcing max 2 iteration loops) and `schemas/critique_report.schema.json` (100-point dual-layer audit).
- **Foundation Protocols.** Established `protocols/00_intent_empathy_decoder.md`, `01_capability_first_gate.md`,
  `02_cross_delegation_dag.md`, and `03_redteam_critique_rubric.md`.
- **Validation & Tests.** Created `scripts/validate_handoff.py` and `tests/test_artcraft_hub.py`.
  Test suite expanded from 292 to **296 tests, all passing (0 failures, 4 skipped)** in 8.64s.

## T035 DeckCraft native bridge + Skill-for-Design evolution — 2026-10-31

- **Native rendering bridge (`scripts/deckcraft_bridge.py`).** Discovers `deckcraft-cli.exe`
  from the ArtCraft suite (`D:\artcraft\DeckCraft`). Headlessly renders slides to Full HD
  (1920x1080) PNGs in < 1s, inspects presentation JSON, and converts formats without
  requiring Microsoft Office or LibreOffice.
- **Critic integration.** `scripts/design_critic.py` now supports `--render deckcraft` (or `--render dc`),
  enabling instantaneous offline visual metrics extraction (background share, balance offset,
  colourfulness). Tested on `report_deck_motion.pptx` in 2.1s with 100% success.
- **Tests.** Added `tests/test_deckcraft_bridge.py`. Test suite expanded from 289 to 292 tests,
  all passing (0 failures, 4 skipped).
- **Skill-for-Design roadmap.** Established the architectural blueprint to evolve `skill-for-pptx`
  into the comprehensive Skill for Design suite with PPTX as pioneer.

## T034 design system + documentation standardised — 2026-10-19

Beauty and technique now share one source,
`knowledge/design_system.json` (see `docs/DESIGN_SYSTEM.md`):

- **Shared numbers.** Duration bands per role, easing roles fitted to
  PowerPoint, stagger, overshoot, rhythm limits, WCAG contrast, type scale,
  density and layout, with 18 rules and their evidence.
- **Generators read it.** Arrivals ease in, and the assemble regression from
  the Argon merge is undone. Overshoot is clamped. Travel time scales with
  distance. The default path easing is no longer 50/50. The simulator uses
  PowerPoint's accel/decel curve. Helpers take a deck colour that reaches
  3:1 against the background. The highlighter tint keeps text contrast. One
  contrast function, with WCAG large text at 18 pt.
- **Checkers grade against it.** These are the validator, `forge_qa` and the
  new `scripts/design_critic.py`. The critic resolves inherited sizes and
  colours, alpha tints and gesture segments, measures settled frames
  (LibreOffice or PowerPoint) and checks the schema. `forge_critique.py`
  (T031) now delegates to it.
- **Wiring.** Director reports, Forge verdicts and Morph Studio reports
  include the critique.
- **Evidence.** In a before/after run (36 director runs, one critic),
  generator-controlled warnings fell from 14 to 6. The invisible helpers on
  brand themes (1.14:1) became 5.33:1. LibreOffice frame metrics match
  PowerPoint's (background share: median difference 0.022, Spearman 0.99).
- **Quarantine.** The T033 modules are labelled experimental and kept out of
  product paths.
- **Documentation.** Documents were reorganised: STATUS (current state),
  CHANGELOG (this log), VERIFICATION, DESIGN_SYSTEM, ARCHITECTURE and the
  task registry. Superseded documents moved to `docs/archive/`.

289 tests pass. Report:
experiments/T034-20261019-claude-design-system/REPORT.md.

## T033 Argon second drop: morph twins, triggers, pacing — 2026-10-16

The owner integrated three Argon answers:

- `morph_playbook.py`: `!!` twin staging, extract_objects, homotopy;
- `interactive_triggers.py`;
- `cognitive_pacing.py`.

No report was written at the time. The T034 audit found that none of them is
wired into a product path, and that each one writes schema-invalid or wrong
XML on real decks. All three are quarantined as experimental. Report
(written in T034): experiments/T033-20261016-argon-research/REPORT.md.

## T031 measurable critique (WIP) — 2026-10-08

`scripts/forge_critique.py` scored PPTEval-style dimensions (content, design,
coherence) plus motion from measurements. It was a single WIP commit with no
tests or wiring and no report. T034 folded its checks into `design_critic.py`.

## T032 Argon (Gemini) research drop evaluated and integrated — 2026-10-15

Argon worked offline on the old main and reused ID T024. Its drop is preserved
verbatim on `import/argon-t024-20261014` and merged here. **Adopted:**

- virtual rigging with follow-through;
- the orbit, orbit-3d, wave, explode-layers and cascade-flow recipes;
- poly-segment paths;
- auto-arc collision avoidance;
- bounceEnd;
- shape-click triggers;
- two engine bug fixes;
- the Pillow-only preview fallback.

**Corrected:** `color` (wrote Change Line Color, now Change Fill Color) and
`teeter` (wrote Blast, now PowerPoint's Teeter). Its loop keys are normalised
into `loop:{}`.

**Quarantined:** the import-breaking "PHASE 2-4" block, now in
`scripts/morph_playbook.py`, experimental. 265 tests pass, 48/48 decks apply,
and PowerPoint 16.0 renders the 3D carousel and the cascade.
Report: experiments/T032-20261015-claude-argon-integration/REPORT.md.

## T030 brand palette from one colour + highlight fix — 2026-10-08

`scripts/brand_palette.py` builds a whole Forge theme from one brand colour
(`"theme": {"seed": "#DA251D", "mode": "light|dark", "harmony": 150}`). It
works in OKLCH (Ottosson) and picks colours by contrast target, the way Adobe
Leonardo does. The brand hue is kept, and its lightness moves only as far as
WCAG AA requires; the raw colour still paints the decoration. A test holds 47
seeds × 2 modes to AA on bg and surface.

The PowerPoint render of a Vietnamese brand deck showed the T028 highlight
marker above a centred, wrapped takeaway. The marker now uses the
anchor-aware `text_block` and covers wrapped blocks; a regression test was
added and the re-render was checked. 256 tests pass.

## T029 motion tokens — 2026-10-08

Carbon and Material 3 easing curves (Apache-2.0) are fitted to PowerPoint's
accel/decel. Carbon fits within 1.5–8%; Material's emphasized curves are
18–44% off with one behaviour.

The keyframe default moves from the symmetric 0.5/0.5 to Carbon standard
(0.15/0.70). Assemble and rise now enter with a deceleration, and disperse
exits with an acceleration. PowerPoint 16.0 parsed all 122 effects of a
cinematic showcase deck. 251 tests pass. See `knowledge/README.md`.

## Integration 2026-10-08 — both lines merged

Two sessions worked in parallel, and both used the ID **T024**. Experiment
folders keep their names:

- `T024-20261005-claude-layers-script` (cloud): motion layers and the script layer.
- `T024-20261007-claude-picture-motion` (desktop): Ken Burns and the accent intro.

Use T029+ for new work. Loops are unified on the cloud representation
`loop: {repeat, auto_reverse}`. The desktop `float` recipe is now an alias of
`drift` straight up. Recipes `ken-burns`, `ppt:<name>` effects, Slide Forge,
assets and the knowledge base sit next to Morph Studio, the script layer and
layers. Natively verified so far: PowerPoint CreateVideo renders (T024
picture, T025, T027) and EffectType recognition of library presets. The
cloud work (T024 layers, T028) has simulated previews only.

## T028 Morph Studio + professional text tricks — 2026-10-08

Goal: the polish seen in motion-design tutorials. `scripts/morph_studio.py`
adds cross-slide Morph to a directed deck. **Continuity** pairs titles,
identical pictures and text, and existing names via `!!`, and renames along
the whole chain. It stages new and leaving objects off-slide so they fly;
contained objects travel with their card. **Scenes** each need a reason and
start from the source's end state: `camera-zoom` (push-in and pull-back, type
scaled like a lens), `card-expand` (over its neighbours, even margins) and
`pan`. `verify_scenes` keeps originals intact (only `!!` renames and
off-slide copies). The `unsettled` check lists slides whose animation ends
away from the authored layout before a Morph. The script layer adds a closing
release click when a script stops mid-tour.

Text tricks: `type-on` and `by: word/letter` (`p:iterate`), `rise` from an
invisible line (the mask sits under the last estimated text line, in the
container or background colour, and is refused if it would cover anything),
`highlight` and `underline` sweeps (added by cinematic). The catalog
`skills/pptx-motion-director/references/pro-techniques.md` lists 50
techniques with when and how.

Evidence: report deck (7→8 slides) and showcase deck (8→10 slides) with
simulated previews. LibreOffice reads every Morph slide's fallback as Fade.
Five defects were found by looking at the previews and fixed with tests.
Smoke test: 34/34 repository decks pass
propose → apply with every suggestion accepted. **219 tests pass.** PowerPoint playback is pending; the native gate is in
T020 §A.

Report: experiments/T028-20261008-claude-morph-studio/REPORT.md.

## T027 design + complex-motion knowledge — 2026-10-07

- PowerPoint authored all 198 built-in effects. They are now writable as
  `ppt:<name>` (verified 7/7 by native EffectType).
- 11 Microsoft designer themes became Forge `office:<Name>` themes, AA in light and dark.
- 797 licensed Zenodo10K decks were scanned XML-only over HTTP Range. 93% of
  real effects are entrances, and complexity lives in object lifecycles.
- New `dynamic` motion style. See `knowledge/README.md` and
  experiments/T027-20261007-claude-design-motion-corpus/REPORT.md.

## T026 Forge online assets — 2026-10-07

Forge now finds licensed photos (Openverse CC0/BY/BY-SA, or Pexels with a
key) and open-source icons (Iconify: Lucide/Tabler/Phosphor) by itself.
Contact sheets let the agent pick photos by eye. Icons are inserted as native
SVG. Attribution goes on an automatic credits slide, in the notes and in the
verdict. Example deck rendered by PowerPoint 16.0.
Report: experiments/T026-20261007-claude-forge-assets/REPORT.md.

## T025 Slide Forge — agent-facing deck compiler — 2026-10-07

New product path for *new* decks: `scripts/slide_forge.py` (schema → build →
qa → render). An agent writes a semantic spec with 12 layouts. Forge handles
layout, measured type, art, Director motion (KPI count-up, chart builds,
process, cycle tour, Ken Burns, accent draw-ins, Morph orbs) and coded QA.
Two example decks (EN and VI) pass QA and were rendered by PowerPoint 16.0.
The renders found wrap and mid-word-break defects that QA now catches.
Skill: `skills/slide-forge/SKILL.md`; command `/forge-deck`.
Report: experiments/T025-20261007-claude-slide-forge/REPORT.md.

## T024 picture motion + motion-graphic intro — 2026-10-07

Prompt-made decks animated only their text: the draft heuristic skipped small
pictures, kept single-picture and title slides static, and gave other pictures
a one-off entrance. Now large pictures get `ken-burns` (slow Grow/Shrink +
drift; on slide start for backdrops and picture-only slides, after the reveal
for content pictures), thin accent bars/lines draw in at slide start, and a new
`float` recipe loops until the slide ends (`repeatCount`/`autoRev` support in
the writer, reader and simulator). Morph-carried pictures stay still.
**202 tests pass.** First native evidence in this repo: PowerPoint 16.0 parsed
the effects and its own `CreateVideo` render shows the picture push-in and the
loop (pixel-measured). Interactive click playback is still pending.

Report: experiments/T024-20261007-claude-picture-motion/REPORT.md.
## T024 motion layers + script layer — 2026-10-05

Motion now has three layers. **Primary** is the meaning. **Secondary** covers
a halo following each spotlight, a rail plus progress token under walked
processes, an orbit ring behind cycles, ripple, overshoot/anticipate, and
labels that follow their shapes (`attach`). **Ambient** covers native loops:
breathe, drift and spin-loop, repeating indefinitely or until the next click.
Helper shapes come from `scripts/motion_components.py` in the deck's accent and
font. The draft reuses the deck's own token when one exists. Director v0.7 adds
`layer` and `components[].generate`.

Script layer (`scripts/motion_script.py`): the script says *when*, the
director's choreography says *how*. It covers a provided script, notes, or a
generated full script (`motion_script.py draft`). First mention reveals, a
later mention focuses, a line that names nothing new releases a tour, and
paraphrased cued lines take the next resource in order. Gaps are reported and
`--fill-gaps` turns them into callouts. Every run writes `OUT.script.md`;
`--write-notes` puts the narration in speaker notes. Verified on an English
human-style script and a Vietnamese paraphrase.

**205 tests pass.** Smoke test passes on all repository decks. Native playback
is pending.

Report: experiments/T024-20261005-claude-layers-script/REPORT.md.
## Argon (Gemini) "T024" virtual rigging, poly-segment paths, auto-arc collision solver & interactiveSeq — 2026-10-14

Resolved the three compound-motion limitations identified in T023 and incorporated architectural lessons from an open-source review (`hugohe3/ppt-master`, `JimLiu/baoyu-design`, `scanny/python-pptx#942`, and the Open XML SDK SMIL specification):

1. **Group-aware virtual rigging (`detect_virtual_rigs`, `expand_rig_tracks` in `scripts/motion_engine.py`)**: shapes with separate floating text labels or badges sitting inside them now automatically carry those followers along in geometric lockstep (position, scale, rotation, opacity, visibility) without mutating `<p:spTree>`. `scripts/motion_director.py` (`_radial_group`) now detects and animates cycle/hub diagrams with separate text labels instead of rejecting them.
2. **Mid-flight trajectory collision detection & auto-arc avoidance (`transient_warnings`, `resolve_trajectory_collisions`)**: samples intermediate instants `(0.2, 0.35, 0.5, 0.65, 0.8)` of each click group to flag mid-motion collisions/occlusions, and automatically bends straight trajectories into obstacle-clearing cubic Bezier arcs when `auto_avoid=True`.
3. **Poly-segment motion paths (`poly_path=True`, `via=True`) & new recipes (`orbit`, `wave`)**: compiles multi-waypoint curves and 360-degree 4-quadrant orbits into a single `<p:animMotion>` element (`M ... C ... C ... E`), eliminating multi-stage path handoff seams.
4. **Canonical writer extensions (`scripts/pptx_animator.py`)**: added native `color` (`p:animClr`), `teeter` (`p:animRot`), `repeat` (`repeatCount`), `auto_reverse` (`autoRev`), `bounce_end` (`p14:bounceEnd`), shape-triggered `interactiveSeq` (`trigger_shape` / `trigger_spid`), and `empty_placeholders()` inspection/stripping for Morph transitions.
5. **Cross-platform resilience (`scripts/check_environment.py`, `scripts/motion_preview.py`)**: fixed `PermissionError` when probing `/root/.codex/...` as a non-root user and added a pure-Python `Pillow` fallback for animated GIFs and storyboard contact sheets when ImageMagick (`convert`/`montage`) is absent.

**198/198 tests pass (0 skipped).** `render_identity.py` confirms 4/4 slides RGB-identical on the T024 showcase; `lo_timing_crosscheck.py` confirms LibreOffice imports all new effects cleanly. Native PowerPoint playback remains pending: play `experiments/T024-20261014-gemini-complex-motion-rigging/output/T024_complex_motion_directed.pptx` against `preview/slide-0N.png`.

Report: `experiments/T024-20261014-gemini-complex-motion-rigging/REPORT.md`.

## T023 compound motion engine — 2026-10-05

Existing decks can now receive compound choreography, not only builds.
`scripts/motion_engine.py` compiles keyframe tracks and recipes (assemble,
disperse, spotlight, release, cycle, swap, travel, zoom-focus, raw tracks) into
native motion paths, Grow/Shrink, Spin, Transparency and entrance/exit effects
with exact delays. Position, scale, rotation, opacity and visibility carry
across clicks. Director v0.6 adds `choreography` beats and Morph `transitions`.

The draft detects cycle/hub diagrams (assemble, then a spotlight tour, then
release) and Morph continuity (a shared picture or text that moves). It keeps
continuing objects static. `preview` renders a simulated GIF plus a key-state
sheet of any slide (reading the timing XML back). `verify` rejects overlapping
moves of one object and warns about new occlusion or off-slide states. Those
warnings caught two real mistakes in the hand-directed showcase.

LibreOffice recognises the new motion-path, grow-and-shrink, transparency and
exit effects. Smoke test: `auto` on 27 repository decks passes, after fixing a
crash on fully animated decks and 88 bogus re-entries on Morph-state decks.
**190 tests pass.** Native playback is pending: play
`experiments/T023-20261005-claude-compound-motion/output/T023_showcase_directed.pptx`
against its preview sheets.

Report: experiments/T023-20261005-claude-compound-motion/REPORT.md.

## T022 T009 recompile + text-box deck direction — 2026-10-05

Continued Codex's T009 arm C (PR #22, which its review held back from merging).
The plan, unchanged, was recompiled through T019 on a timing-stripped
reconstruction (0 inventory differences over 31 shapes). In LibreOffice's
reading, the T009 candidate has 21 effects with 0 presets and all stages at
0s; R1 has 21/21 presets, with staged reveals at 0s/0.32s. A paragraph-click
variant (R2, 19 clicks) separates claims from rebuttals without content edits.

The T019 autonomous draft failed on this text-box-only deck: 40 clicks
(titles animated, wrapped titles split, labels separated). Implicit-title,
title-zone and label-body pairing rules bring it to 18 clicks. That matches
Codex's grouping on slides 2 and 10 and differs only by keeping slide 1 static.

`scripts/render_identity.py` compares renders in RGB. A negative control shows
the T009 RGBA `getbbox()` method misses real changes. R1, R2 and auto2 render
10/10 identical. **176 tests pass.** Native playback is still pending: play the
two PPTX files in `experiments/T022-20261005-claude-t009-recompile/output/`.

Report: experiments/T022-20261005-claude-t009-recompile/REPORT.md.

## T019 canonical timing + one-command Motion Director — 2026-10-05

Product path now exists end to end: `scripts/motion_director.py`
`inspect → draft → apply → storyboard/verify`, packaged as skill
`skills/pptx-motion-director/` and Claude Code plugin (`.claude-plugin/`,
`/animate-deck`). Input can be only a PPTX + vague goal.

Found and fixed a writer defect: patch v0.2–v0.5 put all stages of a click in
one `p:par` at delay 0, so `after-previous` ran concurrently, and entrances had
no `set style.visibility`. LibreOffice's importer reads the old H001 tree as
three effects at 0s with no preset; the new `scripts/pptx_animator.py` tree as
0s/0.32s/0.64s Float/Fade entrances. Existing timing is now extended (appended,
original nodes byte-equal) instead of rejected.

Synthetic real-world fixture `tests/fixtures/report_deck.pptx` (placeholders,
bullets, KPI cards, chart, process, picture, group, notes, PowerPoint-authored
animation): autonomous draft gives 4/3/2/5/3 clicks on slides 2/3/4/5/7, keeps
title and existing-animation slides untouched; preservation checks pass.
**167 tests pass.** PowerPoint playback still pending — play
`experiments/T019-20261005-claude-motion-director/report_deck_motion.pptx`.

Report: experiments/T019-20261005-claude-motion-director/REPORT.md.
Next task: research/tasks/T020-motion-director-continuation.md.

## T018 native QA evidence integrity — 2026-10-05

Reviewed the unfinished T018 harness from a00ea03 on a separate branch (PR #21).
Frozen synthetic evidence cases found 18 false click passes and one crash in
26 cases. The corrected verifier gives 26/26 expected decisions, zero false
passes and zero crashes. **150 tests pass**, plus Python compile and PowerShell
syntax parse in GitHub Actions run 37248823323.

Exact-artifact manifest, Windows COM probe, composite fixture builder and manual
workflow are now documented in docs/POWERPOINT_NATIVE_HARNESS.md. No native
workflow was dispatched and no new PPTX artifact was delivered in this study.
Raw probe results are provisional; matching click indices do not prove animation
completion. Native playback and visual-state claims remain false.

Next: run the four frozen T006 hashes on an actual Windows PowerPoint desktop,
then chart/KPI/focus capture. Do not repeat the matrix or expand effects to avoid
the native gate. Report: experiments/T018-20261005-qa-evidence-review/REPORT.md.

## T017 generic report motion — 2026-10-05

Generic existing-deck semantics now bridge to native timing for reveal, staggered
reveal, process reveal, focus/emphasis, explicit move and explicit rotate.

Director v0.4 + `scripts/compile_director_patch.py` expand one semantic beat to
multiple automatic stages while preserving click groups. Patch v0.5 adds generic
`shape_entrance` and rejects charts on that path.

H001 real-deck transfer passes: 3-stage reveal in one click on slide 1, 2-stage
focus pulse in one click on slide 2, no slide inflation, source text/geometry
preserved and existing transition retained.

CI run 37239720520: **140/140 tests pass** + Python compile.

PowerPoint runtime remains the decisive missing gate.

Task: `research/tasks/T017-generic-report-motion.md`.
Report: `experiments/T017-20261005-generic-report-motion/REPORT.md`.

## T016 real-package data motion — 2026-10-05

T012–T015 now pass a real PPTX package integration, not only isolated XML.

A fixture derived from the valid H001 deck adds a native two-series/four-category
line chart plus `98.5%` KPI, then executes:

`inventory -> Director v0.3 -> compiler -> patch v0.4 -> output inventory`.

First CI exposed a genuine inventory gap: inline ChartML `strLit/numLit` points
were not counted. Parser fixed; regression added.

Final run 37239255072: **130/130 tests pass** + Python compile.

Package audit confirms two presenter clicks, source KPI preservation, native
chart build read-back, unchanged slide count, and byte-identical untargeted
slide/chart/relationship parts.

PowerPoint runtime playback remains pending.

Task: `research/tasks/T016-real-package-data-motion.md`.
Report: `experiments/T016-20261005-real-package-data-motion/REPORT.md`.

## T015 Director → execution compiler — 2026-10-05

The manual bridge between Director v0.3 and patch v0.4 is removed for complete
data-motion slides.

`scripts/compile_data_motion_patch.py` compiles chart/KPI semantic beats into
`chart_entrance` / `number_counter`, resolves exact source targets and
preserves Director click grouping.

Safety: mixed/unsupported slides are blocked instead of partially compiled.
Odometer → stepped-text fallback is explicit and can be disabled.

Final CI run 37238859486: **126/126 tests pass** + Python compile. Integration
regression preserves two presenter clicks across Director → patch → timing
read-back.

PowerPoint playback remains pending.

Task: `research/tasks/T015-director-to-execution.md`.
Report: `experiments/T015-20261005-director-to-execution/REPORT.md`.

## T014 KPI counter execution — 2026-10-05

T012 hero-metric counters now have a structural v0.4 execution path.

`number_counter` clones the exact source KPI textbox for intermediate values,
preserves style/geometry, sequences proxy entrance/exit inside one presenter
click beat, and reveals the untouched source textbox last.

Counter interpolation preserves prefix/suffix/decimal/grouping and rejects
source-text drift. The source final value is never rewritten.

CI run 37238539416: **120/120 tests pass** + Python compile.

Critical runtime gate remains: exact PowerPoint playback must prove that generated
entrance effects hide source/proxy shapes until scheduled and that only one value
is visible at a time.

Task: `research/tasks/T014-kpi-counter-execution.md`.
Report: `experiments/T014-20261005-kpi-counter-execution/REPORT.md`.

## T013 native chart execution — 2026-10-05

T012 semantic chart recipes now have a structural native execution path.

`existing-deck-timeline-patch` v0.3 supports `chart_entrance` on exact
existing chart graphicFrames and emits:

- chart sub-targets via `p:graphicEl/a:chart`;
- `seriesIdx/categoryIdx/bldStep`;
- `p:bldGraphic/p:bldSub/a:bldChart`;
- chart-type-specific conservative entrance filters;
- density guard with requested/effective build receipt.

Default fan-out limit is 24; excessive point-level builds degrade to series or
whole-chart rather than creating hundreds of effects.

CI run 37238145782: **112/112 tests pass** + Python compile. Structural read-back
confirms chart build mode and sub-target indices.

PowerPoint playback is still pending; this is not a native-playback claim.

Task: `research/tasks/T013-native-chart-execution.md`.
Report: `experiments/T013-20261005-native-chart-execution/REPORT.md`.

## T012 semantic data motion — 2026-10-05

User added a new product requirement: charts need type-specific animation, and
standalone hero metrics need dedicated number counting.

Inventory now recognizes classic ChartML subtype/dimensions and standalone
numeric candidates. `scripts/data_motion_recipes.py` maps chart semantics to
distinct defaults (baseline-grow, series-trace, segment-sweep, point-build,
etc.) and emits source-preserving KPI counter recipes.

Director v0.3 requires chart-targeting beats to declare type-specific data motion.
Hero KPI counter plans must preserve the exact source numeric value and format.
Data motion remains subordinate to T010/T011 click-beat rhythm.

CI run 37236839744: **103/103 tests pass** + Python compile.

This is semantic/structural evidence only. Native chart build and counter
playback remain pending.

Reference: `skills/pptx-motion/references/data-motion-recipes.md`.
Report: `experiments/T012-20261005-data-motion-recipes/REPORT.md`.

## T011 director click rhythm — 2026-10-05

T010 established click groups in the timing writer. T011 moves that decision
upstream into the AI Director.

Canonical semantic hierarchy:

`Deck Narrative -> Slide Objective -> Click Beat -> Motion Beat -> Effects`

Director v0.2 requires each click beat to record audience purpose, stable state,
pause type, and (after the first click) a narrative boundary reason. It rejects
flat/ambiguous grouping, nested `on-click`, and incomplete beat partitions.

Existing-deck patch v0.2 now preserves the same click grouping on a fresh
unanimated source slide, so multi-click pacing no longer requires multiple
slides.

CI run 37234829380: **92/92 tests pass** + Python compile. A regression patches a
real existing-deck fixture to two click groups and reads the groups back through
the deck inspector.

T009 no-script benchmark now explicitly penalizes whole-slide autoplay,
one-click-per-motion overfragmentation and premature reveals.

Report: `experiments/T011-20261005-director-click-rhythm/REPORT.md`.

## T010 presenter-paced click beats — 2026-10-05

User corrected the packed-motion target: one physical slide may contain many
motions **and many presenter clicks**. Packing and pacing are now separate.

Canonical rule: `docs/CLICK_BEAT_CHOREOGRAPHY.md`.
Task: `research/tasks/T010-click-beat-choreography.md`.

Native timeline v0.2 now models:

`Slide -> Click Beat -> Stage -> Effects`

T005 benchmark remains **1 slide / 82 behaviors**, but is repartitioned from the
legacy one-click chain into **4 click beats**:

1. burst;
2. orbit;
3. focus -> split;
4. reassemble -> restore.

`scripts/add_timeline.py` keeps v0.1 one-click behavior for historical
reproducibility and uses multiple `mainSeq` click groups for v0.2. The
existing-deck inspector also exposes click-group structure so authored presenter
rhythm can be preserved.

CI evidence: run 37234235795 — **86/86 tests pass**, Python compile pass.
Integration regression locks 4 clickEffect stages, 2 afterEffect stages and
82 behaviors on one slide. Native PowerPoint playback is still pending, so this
is structural evidence only.

Report: `experiments/T010-20261005-click-beat-choreography/REPORT.md`.

Cập nhật ngày 04/10/2026, giờ Việt Nam. Phiên bản nguồn nghiên cứu v0.7 (thêm T005 compound intent).

## T006 controlled motion semantics matrix — 2026-10-04 20:08 UTC

PR #12 prepares four exact one-slide files that differ only by stage-local vs
authored-layout motion paths and fill=remove vs fill=hold. Every file has two
900 ms motion behaviors in one click group. Four finalizers pass with no layout
warnings; all static renders were viewed and are pixel-identical. Exact audit
finds no uncontrolled package/XML difference. **83 tests pass.**

No PowerPoint runtime was available, so there is no winning native variant and
the production writer/source skill remain unchanged. Highest-value next action:
run all four exact hashes using
experiments/T006-20261004-motion-semantics-matrix/playback-checklist.json.
Only then revise path anchoring/fill and rebuild the full packed candidate.

## T006 full packed candidate — 2026-10-04 19:16 UTC / 05-10 Vietnam

Built `output/T006_packed_candidate.pptx`: **1 slide, 31 native objects, 6 stages,
82 encoded behaviors, 7,100 ms planned duration**. Exact SHA-256:
`41c4fb7865ea587e0d426fccf4de2c82fc1db731147a92a4fba28926b0e52094`.

Full pipeline initially failed because packing dropped state-local opening text.
Preserving initial text fixes the abort; the exact final file passes finalization
and its sole static render was viewed. **79 tests pass.** Failed raw artifact,
plans, receipt, hashes and full report are in
`experiments/T006-20261004-packed-validation/` (PR #11).

Independent audit found **47 path-origin mismatches under the authored-layout
coordinate model**, with maximum 543.766 px. This is a conditional geometry
diagnostic, not observed playback. All 82 behaviors currently use fill=remove.
Keep the evidence; do not promote native compatibility. Next: exact-file playback
and a PowerPoint-authored two-stage path fixture to resolve origin/fill/trigger
semantics. Do not rebuild this same candidate without a new hypothesis.
T007/T008 autonomy work remains as below; source skill is still research v0.7.

## T007 autonomy + existing-motion continuation

The product target is now explicit at the stronger autonomy level requested by
the user: **PPTX + optional high-level goal is enough input**. The model should
not require object-by-object animation instructions. It must discover/use a
script, infer one when absent, research reporting structure only when necessary,
reuse deck resources, synthesize only justified missing components, and return
the same report motion-directed.

Existing native animation is now first-class source evidence. Script priority is:
provided script → speaker notes → existing timing/choreography → visible
narrative → inferred narrative → researched narrative. Existing timing must be
preserved/extended by default rather than rejected or deleted.

`inspect_existing_deck.py` now exposes transition and timing choreography:
effect types, source targets, durations, start conditions, numeric delays,
build groups and an order hint with an explicit structural-evidence boundary.

Branch CI run 37215400829: **75/75 tests pass** plus Python compile. New tasks:
`T008-existing-motion-continuation.md` and
`T009-autonomous-no-script-benchmark.md`.

Report: `experiments/T007-20261004-autonomy-existing-motion/REPORT.md`.

## Product destination — T007 Existing Deck Motion Director

Người dùng đã mở rộng đích đến: hệ thống phải nhận **file PPTX có sẵn** và tự
đạo diễn chuyển động. Nếu có script/storyboard thì bám script. Nếu không có,
ưu tiên speaker notes, sau đó tự phân tích trình tự báo cáo; chỉ nghiên cứu ngoài
khi cần và phù hợp. Nếu narrative thiếu component thì tự tạo helper component
trong đúng visual framework của deck, không sinh decoration vô cớ.

Tài liệu chuẩn: `docs/PRODUCT_TARGET.md`.
Task: `research/tasks/T007-existing-deck-motion-director.md`.

Scaffold hiện có:
- `scripts/inspect_existing_deck.py`: source-hash + slide/object/text/geometry/
  relationships/timing/transition/notes/theme/media inventory;
- `skills/pptx-motion/references/existing-deck-director.md`: director contract;
- `scripts/validate_director_plan.py`: buộc script source, source grounding,
  preserve slide count, target resource validity và justification cho component;
- final branch CI run `37214340363`: **67/67 tests pass**, `py_compile` pass.

Report: `experiments/T007-20261004-existing-deck-director/REPORT.md`. Phần còn
pending: inference trên deck thật không có script, synthesis component theo design
system, director-beat → T006 timeline adapter, và patch/playback exact-file.

Default mới: preserve source slide count/order/content; resource cũ được reuse
trước; same-resource motion phải pack trong slide; generated component chỉ lấp
narrative gap.

### T007 source-object patcher checkpoint

Đã thêm `scripts/patch_existing_timeline.py` và
`existing-deck-timeline-patch.md`: object deck thật được target bằng source
slide + native `cNvPr id` + name, không cần `!!`. Patcher kiểm source SHA-256,
chỉ sửa slide được chọn, giữ slide khác byte-identical, preserve transition và
từ chối merge timing cũ mù quáng.

Deck intake cũng đã có `design_profile` gồm font/fill/line/text-color/geometry
frequency để làm basis khi sau này phải sinh helper component.

Final temporary CI run `37214809106`: **73/73 tests pass** + `py_compile`
pass. Report: `experiments/T007-20261004-source-object-patcher/REPORT.md`.

Phần còn thiếu cho product path: director beat → concrete patch-plan compiler;
native helper-component insertion + re-inventory; no-script narrative test trên
deck thật; exact-file PowerPoint playback.

## T006 native timing writer — đã có backend cấu trúc, playback còn pending

T006 đã tiến từ planning sang writer native hạn chế. `scripts/pack_timeline.py`
vẫn nén T005 candidate 12 legacy states thành 1 semantic slide/6 stage và
transfer 10→1. `scripts/add_timeline.py` hiện ghi `p:timing` cho motion path,
scale và rotate trên cùng slide: waypoint nằm trong path, các stage dùng delay
tích lũy và các effect cùng stage chạy song song trong một packed click group.

Đường dựng end-to-end mới:
`validate_timeline.py -> render_timeline.mjs -> normalize_timeline_textboxes.py
-> add_timeline.py -> host finalizer`, gọi bằng
`scripts/run_timeline_experiment.sh`.

Bằng chứng tự động: GitHub Actions branch-only run 37213501515 đạt
`py_compile`, **55 unit tests**, `node --check` renderer và `bash -n` runner.
Workflow tạm đã xóa sau kiểm tra. Prototype 1 slide/2 shape sau patch vẫn pass ZIP
CRC, mở lại bằng python-pptx và LibreOffice export PDF. Đây là bằng chứng package,
**không phải playback PowerPoint**.

Report: `experiments/T006-20261004-native-timing/REPORT.md`.
Native playback/editability exact-file vẫn pending; M1 chưa đạt.

## Chỉ thị mới — resource-local motion packing

Người dùng yêu cầu đổi kiến trúc: không coi mỗi chuyển động/state là một slide.
Khi các action dùng chung resource set và cùng semantic scene, ưu tiên gom tối đa
vào một native slide timeline. Tài liệu chuẩn: `docs/MOTION_PACKING.md`.

T005 12-state Morph giữ nguyên làm baseline lịch sử. Nó không còn là mẫu kiến
trúc mục tiêu. T006 phải cố gắng tái hiện burst → orbit → focus → split →
reassemble → restore trong 1 slide với nhiều track/timing/trigger native; nếu
PowerPoint/backend buộc tách, ghi blocker và dùng số slide tối thiểu. Các model
sau phải đọc rule này trước khi thiết kế choreography.

## Kết quả mới nhất — T005

Ưu tiên mới của người dùng là hiệu ứng phức tạp từ một câu lệnh ngắn, giữ đúng ý định. PR #3 và `experiments/T005-20261004-codex-choreography/REPORT.md` có compiler intent nghiêm ngặt cho chuỗi bung nút, xoay vòng, phóng đối tượng, tách lớp, ghép lại và trở về. AI diễn giải prompt; compiler chỉ nhận dữ liệu có cấu trúc, không phải NLP tổng quát.

Hai PPTX native: candidate 12 trạng thái/31 đối tượng, transfer 10 trạng thái/22 đối tượng. 7 nhóm kiểm tra geometry và package parity đều đạt trên mỗi file. Đã xem riêng đủ 22 ảnh cuối. 41 unit tests đạt. Đối chứng cố ý bỏ waypoint cho sai lệch bán kính tuyến tính 65,608 px; candidate còn 1,916 px. Không coi số này là độ mượt phát thực tế.

Lỗi có ích: tổng góc xoay đúng vẫn có thể che waypoint sai; đã giữ test đột biến và sửa kiểm tra từng waypoint/ràng buộc nhãn. Agent mới tạo bài học tập 8 nút, ngược chiều 60°, nút 6, 3 lớp; parent xuất file. Agent đã đọc brief do AGENTS yêu cầu nên không gọi đây là kiểm thử mù hoàn toàn.

Giới hạn quan trọng: vẫn là 2D Morph theo từng lần bấm, một recipe hạn chế, hình học còn đơn giản; chưa có bằng chứng hiệu ứng ấn tượng hoặc playback PowerPoint. Không phải skill hoàn chỉnh hiểu mọi ý tưởng phức tạp, chưa cài personal skill. Bước tiếp ưu tiên T006 native timeline/path và T001 playback exact-hash; giữ nguyên T005 làm đối chứng.

File: `output/T005_compound_candidate.pptx` SHA-256 `05ddf33c89725dbb66083f5130c549d59d9aa291893321a34cc68c6cf9e9cf58`; `output/T005_compound_transfer.pptx` SHA-256 `e87d37db4a76f51c56dac893bade9c2966960cbc6bfc869ebb5bceb3d8cb5e16`.

## Kết quả mới nhất — T002

PR #2, `experiments/T002-20261004-codex-tight-carriers/REPORT.md` giữ E004 bất biến và chỉ siết carrier quanh label. Trong cùng proxy tuyến tính, label giữ 0/6 cặp chồng và carrier giảm 6/6→0/6. Candidate có 3 slide, 8 đối tượng native/slide, 5 textbox/slide, 2 Morph 1100 ms; 3/3 ảnh cuối đã xem và 34 tests đạt. SHA-256 `c41f2289bfd662f2642ea611b119d8aeaf35678425cba4cf4b7ffe0640922186`.

Tradeoff: focus emphasis tĩnh chủ quan giảm 4/5→3/5; creative vẫn 2/5. Đây là sửa rủi ro geometry, không chứng minh motion đẹp hoặc playback đúng. Native motion/editing null. Nguồn v0.6 chưa cài personal skill. Bước tiếp: exact-hash PowerPoint playback so E004/T002, hoặc T004 portable backend; T002 tiếp theo phải có giả thuyết mới về emphasis/z-order.

## Kết quả mới nhất — T003

Đọc `experiments/T003-20261004-codex-layer01/REPORT.md` trước khi tiếp tục. Nhánh `work/T003-codex-20261004`, PR #1 có generator 3–5 lớp, nguồn và rubric đã đóng băng, hai chủ đề (QUANTA 5 lớp; học trực tuyến 4 lớp), 5 PPTX giữ cả thất bại và 15 ảnh cuối đã xem. Native parity đạt trên cả 5 file; repo có 34 tests đạt. Backend cũ và các baseline E001–E004/H001–H003 giữ nguyên.

Phép đo fixture ràng buộc: 16/60 child-state lệch → 0/60, max 64 → 0 px; đây là lỗi cố ý để thử quy tắc, không phải benchmark độc lập. Lỗi số thật được phát hiện bằng render: ô 42 px làm hai chữ số xuống dòng. Chỉ mở rộng thành 60 px, số lỗi quan sát QUANTA 15→0 và bài mới 12→0. Bài mới do agent ngữ cảnh riêng lập plan; parent xuất PPTX và sửa, không gọi là benchmark tự hành end-to-end. Bản nên dùng: `output/T003_layer_candidate_v2.pptx`, `output/T003_transfer_v2.pptx`.

T003 mới đạt phần recipe 2D và transfer cấu trúc/ảnh tĩnh. Chỉ đọc tutorial nguồn, chưa xem choreography nguồn; không tái hiện 3D extrusion. Native playback, sửa thật trong PowerPoint, M1 vẫn pending; điểm motion/editing null. Điểm sáng tạo tĩnh 3/5 là chủ quan, không phải đạt mục tiêu chuyển động ấn tượng. Nguồn v0.5 chưa cài thành personal skill.

Bước có giá trị tiếp: T001 phát exact-hash hai file v2; hoặc phần tiếp T003 xem animation nguồn thực rồi lập giả thuyết choreography mới; hoặc T002 xử lý carrier crossing cũ. Claim đầu tiên đã xong phạm vi nghiên cứu này; kiểm tra nhánh/PR mới nhất trước khi nhận phần tiếp, không lặp v1/v2.

## Trạng thái thực tế

M0 đã có bộ thực thi thử nghiệm và bằng chứng cấu trúc/bố cục E001, H001. M1 chưa đạt vì thiếu phát thử PowerPoint. Đây là nhánh dựng mẫu và kiểm tra phần mềm trong lúc chờ cổng native; không hạ tiêu chuẩn nghiệm thu M1. Nguồn skill là bản nghiên cứu trong dự án, chưa cài vào tài khoản.

Repo chính đã xác minh: `https://github.com/togcoder/skill-for-pptx`, private, owner `togcoder`, quyền push. Chủ repo tạo README khởi tạo ngày 04/10/2026. Bản handoff nhập snapshot v0.4 cùng nguồn, demo và bằng chứng vào repo này; lịch sử cũ nguyên vẹn tại `archive/pre-github-v0.4.bundle`. Đọc `HANDOFF.md`, `docs/COLLABORATION.md` và các nhánh/PR trước khi nhận việc. Không dùng tên dự kiến `pptx-motion-lab` làm repo GitHub nữa.

## Đã hoàn tất

1. Khôi phục scaffold từ phiên trước, giữ snapshot gốc. Phát hiện nguồn SKILL.md còn template TODO và đường dựng chưa hoàn tất.
2. Hoàn thiện đường dựng hạn chế bằng artifact-tool, kế hoạch JSON, chèn Morph và kiểm tra file cuối.
3. Dựng E001 ba cảnh với 13 đối tượng native mỗi slide; hai khai báo Morph 1.200 ms. Render và xem toàn bộ file cuối.
4. Sửa bộ chèn Morph: đọc đúng thứ tự slide, kiểm tra số cảnh và tên, bảo vệ file có timing, từ chối duration lẻ, không để lại file dở và không ghi đè.
5. Cùng bộ 7 lỗi mục tiêu: baseline 1/7, candidate 7/7. Toàn bộ 19 unit tests hiện có pass. Không coi đó là điểm chất lượng chuyển động hay benchmark độc lập.
6. Viết nguồn skill v0.2 cùng hợp đồng, công thức, rubric và hướng dẫn thực thi có thể gọi lại.
7. Dùng một agent với ngữ cảnh tối thiểu để áp dụng skill vào H001: hai cảnh Collect/Inspect/Decide, phóng lớn Inspect và giữ bối cảnh hai bên. Đã tạo PPTX và xem hai slide cuối. Không tiết lộ đáp án/chẩn đoán E001 cho agent đó.
8. H001 phát hiện nguồn tham khảo E001 bị gắn cứng trong speaker notes; đã sửa renderer để dùng nguồn thực sự trong kế hoạch.
9. H001 cũng phát hiện planned textbox xuất thành native shape có p:txBody nhưng không có txBox=1. Giữ kiểm tra nghiêm ngặt thất bại, ghi ranh giới trong skill; không sửa rubric để che lỗi.
10. E002 sửa đúng 14 khai báo textbox của H001 theo kế hoạch. Bộ kiểm tra H001 giữ nguyên: từ 14 lỗi còn 0 lỗi, 93/93 kiểm tra đạt. Chỉ hai slide XML thay đổi bởi txBox; mọi phần khác giữ nguyên byte. Hai ảnh cuối giống H001 từng pixel. 25 unit tests đạt. Nguồn skill/bộ dựng đã dùng bước chuẩn hóa này.

11. H002 đã hoàn tất từ đề độc lập về đèn ORBIT: 3 slide, 11 đối tượng native mỗi slide, 6 textbox/slide đúng khai báo, 2 Morph 1.100 ms. Agent và parent đã xem đủ ảnh cuối. Agent không đọc plan/artifact cũ, nhưng được thu gọn phần việc sau giai đoạn đọc hướng dẫn; không coi đây là benchmark tự hành có đo thời gian.
12. H002 lộ nguy cơ nhãn gặp nhau khi đổi chỗ đối ứng. E003 giữ baseline và cùng phép đo hình học tuyến tính liên tục: từ 2 cặp nhãn có khoảng chồng xuống 0 trên 6 cặp/chuyển cảnh. Chỉ đổi bố trí/đường đi thành chu kỳ qua ba đỉnh tam giác; giữ 3 slide, chữ, loại/kích thước đối tượng và thời lượng. File cuối đạt cấu trúc, render/xem đủ 3 slide. Đây là cải thiện trong mô hình giả định, chưa phải playback PowerPoint.

13. H003 thử đề mới với ba nhãn tiếng Việt dài 360×96 px. Giữ rubric và chẩn đoán E003: 4/6 cặp nhãn có khoảng chồng theo mô hình. E004 chỉ đổi y của khối/nhãn, tăng khoảng cách hai tầng từ 200 lên 300 px, số cặp nhãn chồng về 0. Cả hai vẫn 6/6 cặp khối có khoảng chồng. File cuối có 3×8 đối tượng native, 5 textbox/slide và hai Morph 1.100 ms; kiểm tra và xem đủ 6 ảnh cuối.
14. Bổ sung scripts/cyclic_label_clearance.py với ngưỡng H >= 3*d*h/(2*d-w) cho ba nhãn đều, ba vị trí đối xứng, nội suy đồng bộ tuyến tính; có miền áp dụng rõ. Bốn test mới đối chiếu chẩn đoán cũ, tổng 29 unit tests đạt. Đã cập nhật nguồn skill với bài học và giữ lỗi plan/preflight ban đầu.

Tại mốc bàn giao v0.4 chưa có claim nghiên cứu mới; T003 sau đó được nhận tại PR #1 như mục mới nhất phía trên. Luôn kiểm tra nhánh và PR mở để biết công việc đang chạy. Nguồn skill bổ sung công thức cyclic focus và phân biệt số trạng thái với số chuyển cảnh. Read của H002/E003 mở ở tư thế lớn; không có đoạn phóng lớn riêng trên slide đầu.

## Bằng chứng cần đọc

- `experiments/E001/REPORT.md`, `scores.json`, `regression-comparison.json`, `validation.json`, `final-renders/`.
- `experiments/H001/`: kế hoạch độc lập, rubric, báo cáo và bằng chứng file cuối.
- `experiments/E002/REPORT.md`, `comparison.json`: sửa textbox, giữ baseline và tiêu chí H001; `output/PPTX_Motion_Lab_E002.pptx`.
- `experiments/H002/`: đề, plan, rubric, qa và bản sao bằng chứng tại `evidence/`.
- `experiments/E003/REPORT.md`: H002 và E003, chẩn đoán đường đi, kiểm tra cấu trúc và điểm tĩnh chủ quan. Native motion/editability vẫn null; không tính điểm tổng.
- `experiments/E004/REPORT.md`, `package-comparison.json`, `unit-tests.txt`, `scores.json`, các `path-diagnostic.json` và `carrier-paths.json` H003/E004; `output/PPTX_Motion_Lab_E004.pptx`.
- `research/skill-source-validation.json`: kiểm tra nguồn thử nghiệm, không phải chứng nhận cài đặt skill.
- `docs/POWERPOINT_QA.md`: yêu cầu bằng chứng native.

PPTX E001: `output/PPTX_Motion_Lab_E001.pptx`. SHA-256: b3b4e28c14f00bc4fe05d6a71400752819413661e1280eb92301b4a6305e7c37.
PPTX H001: `output/PPTX_Motion_Lab_H001.pptx`; dùng hash trong bằng chứng H001.

Điểm E001: đáp ứng đề 4/5, cấu trúc chỉnh sửa 4/5, định danh 4/5, dễ đọc tĩnh 4/5, bố cục sáng tạo tĩnh 3/5. Đây là nhận xét không mù của người làm. Chuyển động chưa chấm, không có điểm tổng.

## Việc tiếp theo theo giá trị

1. Hai đường ưu tiên: (a) dùng `output/T006_packed_candidate.pptx` đã freeze hash trong báo cáo packed-validation để kiểm playback PowerPoint và đối chiếu fixture hai chặng về origin/fill/trigger; (b) T007 lấy một deck thật 3–10 slide, inventory → script/infer → motion-direct một slide bằng resource có sẵn, tối đa một helper component, không đổi slide count. Không dựng lại candidate cũ nếu chưa có giả thuyết mới. Không quay lại waypoint slides nếu playback lỗi; sửa trong cùng slide và giữ baseline. T001/native exact-hash vẫn là cổng nghiệm thu; M1 pending.
2. Nếu chưa có PowerPoint, không lặp ma trận origin/fill vừa tạo. Chọn T007/T008 hoặc chuẩn bị một fixture native khác chỉ khi có biến số mới rõ ràng. Không gọi mô phỏng là playback hoặc tăng số đối tượng là tăng chất lượng hiệu ứng.
3. Chia phần việc theo task trong `research/tasks/`. Nhận claim/nhánh riêng trước khi làm để tránh trùng. Skill và renderer hiện vẫn phụ thuộc môi trường Work như `docs/ENVIRONMENT.md`.
4. Chuẩn bị công cụ thu bằng chứng trên PowerPoint Windows khi phù hợp, không giả lập kết quả. Benchmark 18 lượt chưa thực hiện.

## Khôi phục và lưu tiếp

GitHub `togcoder/skill-for-pptx` là nguồn làm việc chính. Clone/fetch main mới nhất, kiểm tra nhánh/PR và đọc HANDOFF.md. Đọc docs/RECOVERY.md để tra lịch sử trước khi nhập GitHub. Bundle và các checkpoint cloud cũ là snapshot phục hồi lịch sử; không ghi chúng đè lên repo mới hơn. Code và kết quả đã gắn GitHub được commit/push về đúng repo, không tạo bản sao code mới song song trong Library.
