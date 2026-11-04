# T067 [pptx] — Skill audit and deck-direction draft

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), subagent of the owner's
  session.
- **Date:** 2026-11-04. **Base:** `main` @ `7d3d9b8`. **Branch:**
  `work/T067-opencode-deck-director`.
- **Request:** the owner judged T066: good crop/theme/font, but motion has no
  *gu*, images appear last with no meaning, and the deck was generated before a
  script existed. Find the weaknesses, solve them through the skills, research,
  and rewrite the skill if necessary.
- **Status:** audit + draft. No product path changed, no code merged, no INDEX
  edit. Review requested.

## Frame

**Question.** Why did a deck with 144 native effects, 51 click groups, nine Morph
transitions and a 4.99 motion score read as *tasteless* to the person it was made
for — and which part of the skill/toolchain produced that?

**Hypothesis.** The symptoms are not four defects of one deck but one property of
the pipeline: it has **no artifact for direction**. Layout is compiled first, the
motion planner reads the finished geometry back, and intent exists nowhere except
as prose in a skill and as auto-generated template strings in the plan. A deck
built that way can be technically rich and still have no reason for any single
click.

**Falsifiers** (if any held, the skills would be sound and T066 a one-off):

- the skills require a script or argument artifact before layout;
- `slide_forge` accepts a script/beat file and passes it to motion;
- motion timing is derived from something other than the built geometry;
- `theme` can express image treatment, density or motion vocabulary;
- `design_critic` distinguishes a meaningful image from a filler, or a deliberate
  reveal from a slide that opens blank.

**Domain lens.** PowerPoint-native: OOXML timing as the ground truth (`p:timing`,
click groups, `p:spTgt`), the lab's own design system as the only source of
numbers, and the deck as a *presented* object (one idea per click, evidence before
takeaway). The argument vocabulary I propose leans on sources the lab already
cites — Mayer (segmenting, signaling, coherence) and Duarte (pattern break) from
`knowledge/design_system.json` — not on new literature.

**Deliberately not imported.** No film-theory shot grammar, no "storytelling"
framework with a hero's journey, no new aesthetic numbers. A deck is not a film:
the presenter is the sound track and can stop at any state, which is the property
the whole proposal is built around.

## Method

1. Read both skills, `slide_forge.py`, `motion_director.py`, `motion_script.py`,
   `validate_director_plan.py`, `theme_engine.py`, `design_critic.py`,
   `design_system.py`, `knowledge/design_system.json`.
2. Read the T066 report, its `inputs/build_deck.py` (524 lines), its
   `artifacts/critic.json`, and the T057 lead review.
3. Built a probe (`inputs/measure_narrative.py`) that reads a deck's timing tree
   and computes the facts the critic does not check: base state, words visible at
   t=0 and per click, the click index at which each picture appears, whether a
   title moves, object lifecycles.
4. Ran it on T066 and on the lab's reference example
   `examples/pptx/forge/vi_chuyen_doi_so.json`, built on this branch with the
   default pipeline (`slide_forge.py build`, no direction).
5. Used the second deck as the control: if the reference deck of the default
   pipeline has the same defects, the cause is the tool, not the author.

```powershell
python experiments/T067-20261104-opencode-deck-director/inputs/measure_narrative.py `
  experiments/T066-.../artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx
python scripts/slide_forge.py build examples/pptx/forge/vi_chuyen_doi_so.json -o workspace/forge_probe.pptx
python experiments/T067-.../inputs/measure_narrative.py workspace/forge_probe.pptx
```

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| Forge cannot receive a story | `slide_forge.py:185-209` schema has no script/beat/intent field; `build()` (`:927-932`) passes only `spec["title"]` as `goal` | 1 |
| Motion is a function of geometry | `build()` builds the static deck, then `md.deck_model()` + `md.draft()` read it back | 1 |
| The "script" in the plan is generated from the deck | `motion_director.py:1008-1014` builds `beats` as `f"slide N: {title}"`; validator only requires non-empty strings (`validate_director_plan.py:182-184`) | 1 |
| T066 had no script at all | its `inputs/` holds cut-out scripts, a 524-line builder and a render script; no `script.md`, `deck.json` or `director.json` | 1 |
| T066 applied motion last | `build_deck.py:164-385` layout, `:386` `# ---- motion + Morph`, `:396-520` effects for all slides | 1 |
| T066's pictures arrive last | 4 of 4 pictures first appear in the final click group of their slide (cover ×3 at 4/4, Plato at 7/7) | 1 |
| The reference deck has the same defect | 1 of 1 picture on the last click (cover); section (2) and closing (9) open with no text or picture at all | 1 |
| Titles move inside slides | T066: 9 of 10 slides; Forge example: 2 of 9 | 1 |
| No object lifecycles in T066 | `deck.lifecycles = 0`; every object ever added is never dimmed or removed | 1 |
| The score is insensitive to this | T066 motion **4.99** with 0 lifecycles and 9/10 animated titles; Forge example **5.0** design / **5.0** motion / 4.88 overall, **0 warnings**, with two blank-base pause slides | 1 |
| The motion dimension is 93 % micro-checks | 153 `MOT-DURATION`, 110 `COL-TEXT`, 110 `LAY-SAFE`, 51 `MOT-EFFECTS` of 456 checks | 1 |
| `MOT-TITLE` cannot fire on lab decks | `design_critic.py:564,660` identify titles by placeholder type only; Forge/T066 use plain text boxes | 1 |
| Frame rules never run in the normal loop | `slide_forge.build()` calls `critique(out)` with no render; T066's `critic.json` has `frames: 0` | 1 |
| Density is whispered | band ≤45, limit ≤80 (`design_system.json`); T066's 74/78/80-word slides are all `note` (half credit) | 1 |
| A style vocabulary exists but is orphaned | `theme_engine.py:643-745` has 7 archetypes with shape/radius/grain; no skill or module references it | 1 |
| T066 did image treatment by hand | `inputs/02_prepare_assets.py`: rembg + two-stop duotone + circular mask; not in any skill, preset or design-system entry | 1 |
| T066 renders and plays | PowerPoint 16.0 opens 10 slides, 10 PNGs, 10-page PDF, 74 s CreateVideo | 4–5 (T066) |
| A directed rebuild moves the three targeted defects | parallel T067 stream's `motion/artifacts/T066-deck-directed.pptx`, measured by me with the same probe: 51 → **27** clicks, empty base **none**, pictures on the last click **0**, titles animated **0**; lifecycles still 0, widest view still 80 words | 1 (their artifact, my measurement) |

Instruments and raw measurements are committed:
`artifacts/measurements/t066_metrics.json`,
`forge_example_metrics.json`, `t066_critic_summary.json`,
`t066_check_histogram.json`, `forge_example_verdict.json`.

The audit is `skill-audit.md`; the proposal is `DECK-DIRECTOR-SKILL-DRAFT.md`;
the skill draft is `skills/deck-director/SKILL.md`.

## What the proposal is, in three lines

1. **A direction artifact written before layout** — brief → script → beat sheet
   (9 jobs) → shot list (`base_state` first, then `state_after` per click) →
   motion plan → build. `direction.json` compiles to `deck.json` + `director.json`;
   Forge already accepts a plan at `md.apply`, it just never offers one.
2. **A style layer that does not duplicate the one being built** — a sibling T067
   stream is writing `VisualStyle/1` (nine roles, five presets, a resolver and a
   deck check). This report defers to it and adds only the two policies a style
   cannot own: `base_state` (poster-first vs build-first) and `image_role`, plus the
   job→figure vocabulary, which is argument, not style. Numbers come from
   `design_system.json` by reference; the only new value is
   `presence_min_clicks = 1`, flagged for review.
3. **A critic that can see it** — `narrative` dimension (`NAR-BASE-STATE`,
   `NAR-PRESENCE`, `NAR-ORDER`, `NAR-JOB-MIX`, `NAR-ORPHAN`, `NAR-OFF-SPINE`),
   `MOT-LIFECYCLE`, `MOT-FIGURE-REPEAT`, `DEN-VIEW`, `PLAN-DRIFT`,
   `PLAN-PURPOSE`, plus two fixes: real title identity and rule-level scoring
   instead of per-effect averaging.

## Positive results

- The owner's four complaints are each traceable to a specific line of code, and
  the *same* defects appear in the lab's own reference deck. This is a tool
  finding, not a judgement on one agent's deck.
- A seam already exists for the fix: `md.apply(static, plan, out)` accepts a plan;
  Forge needs one parameter to stop drafting its own.
- The parts the owner liked (palette, fonts, crop, duotone) are already a coherent
  recipe. Promoting T066's image pipeline to a preset is the cheapest quality win
  available, and it needs no new invention.
- The critic's arithmetic is sound; the problem is coverage (5 dimensions, no
  narrative) and weighting (per-effect averaging), both fixable without a new
  renderer.

## Negative results and limits

1. **No human eye.** The whole audit is rung 1: code reading plus timing-tree
   measurement. I did not open either deck in PowerPoint, did not watch the 74 s
   video, and did not render a frame. "The cover is empty at t=0" is a structural
   fact from XML, not a viewed frame; how bad it looks depends on the room.
2. **The reference deck was built, not reviewed.** `vi_chuyen_doi_so.json` is a
   demo with synthetic data. It is a fair control for *pipeline behaviour*, not for
   design quality.
3. **The post-fix numbers are half measured, half predicted.** A parallel T067
   stream built a directed deck in the shared task folder; measured with this
   audit's probe it reaches 27 clicks (predicted ~24), no empty base state, no
   picture on the last click and no animated titles — but still 0 lifecycles and
   an 80-word widest view. I measured their artifact but did not build or review
   it, and the parts the layer does not target did not improve.
4. **The job vocabulary is design lore until tested.** Nine jobs and six figures
   are a reasoned taxonomy, not a measured one. They need the same scrutiny T038's
   numbers got (T057, open questions): separate what is measured from what is
   judgement. `presence_min_clicks = 1` is the one new number and is the weakest
   link.
5. **`NAR-OFF-SPINE` is lexical.** Token overlap between a beat and `one_sentence`
   is a weak proxy for relevance and will produce both false passes and false
   failures. It should stay a note, not a warn.
6. **Ceremony risk is real.** Four artifacts before one slide can slow a small
   deck more than it helps. The mitigation is a one-file minimum path, but it is
   untested.
7. **No implementation.** No compiler, no schema file, no test. The skill draft is
   executable by hand only.
8. **Three style vocabularies still exist.** `theme_engine.ARCHETYPES` (T043),
   Forge's `THEMES`, and `VisualStyle/1` from the sibling T067 stream. The proposal
   defers to `VisualStyle/1` and uses Forge themes as the fallback, but the merge
   is a review decision and cannot be done here.
9. **Coordination.** This worktree contains a second T067 stream: an untracked
   `experiments/T067-20261104-opencode-visual-style/` (style system) and, inside
   the shared task folder, its directed rebuild, variants, renders and build
   scripts. I did not write to those files and will not commit them; §4 of the
   draft records the interface, and §7 records the one artifact I measured. The
   shared folder is therefore a merge point for two streams, not a clean
   deliverable.
10. **T066's own report already saw part of this** ("images are assets, not
    backgrounds"; critic flags density). The audit's contribution is the mechanism:
    *why* the images still arrived last despite the intent, and why the critic
    scored it 4.99.

## Next

1. **T068 (builder): `scripts/deck_director.py`** — `check`, `compile`, `ledger`;
   ~300 lines; no layout, no XML. Acceptance: a 3-slide direction compiles to a
   Forge spec whose `base_state` objects carry no entrance effect, and the ledger
   reports carrier presence from the built deck.
2. **T068b: `image_treatment.py`** — crop / rembg / duotone / grade / mask +
   manifest, promoting T066's `02_prepare_assets.py` into a reusable tool with a
   licence record.
3. **T069 (critic):** title identity fix, rule-level scoring, `narrative`
   dimension, `--direction` input. Product path, so PR + review by another model
   family.
4. **T070 (proof):** verify the parallel stream's directed rebuild independently
   (rung 5: PowerPoint render + CreateVideo), then close what the layer does not
   touch — object lifecycles, the 80-word slide, image treatment manifest — and
   run the owner's eye test, the only rung 6.
5. **Design-system data:** add `narrative` and `style` sections with sources; a
   reviewer must decide `presence_min_clicks` or reject it.

## Review response

Pending. The reviewer should try the falsifiers in `skill-audit.md` §1 against the
code, not against this report, and should check one claim I could not: whether an
empty base state actually reads as bad in a room.
