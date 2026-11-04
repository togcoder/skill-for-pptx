# T067 — Skill audit: why the deck had motion but no *gu*

- **Task:** T067 [pptx] — audit `slide-forge` and `pptx-motion-director` against the
  owner's critique of T066, then propose the missing layer.
- **Date:** 2026-11-04. **Base:** `main` @ `7d3d9b8`.
- **Instruments:** the two skills, their scripts, `knowledge/design_system.json`,
  `design_critic.py`, the T066 report and the T057 lead review; plus a small
  read-only probe (`inputs/measure_narrative.py`) that measures the facts the
  critic never looks at, run on two decks.
- **Status:** audit + draft. No product path changed.

## 1. What the owner said, and what would prove him wrong

Four symptoms, one deck (T066, Chapter 1 of Marxist–Leninist philosophy):

| # | Owner's words (paraphrased) | What it claims |
|---|---|---|
| S1 | "motion has no *gu*" | the movement is not tasteful, i.e. not chosen; it is applied |
| S2 | "images appear last with no meaning" | the pictures are decoration: they arrive after the argument is over |
| S3 | "the deck was generated too fast, before a script existed" | the causal order was inverted: output, then story |
| S4 | "theme is palette + fonts, not a design style" | the deck has colours and typefaces but no visual argument |

These are not four complaints about one deck. They are one complaint about the
*tool*: **the pipeline has no place to put a decision, so no decision was made.**

Falsifiers for the diagnosis below — if any held, the skills would be sound and
T066 would be a one-off failure of its author:

- the two skills require a script or an argument artifact before layout;
- `slide_forge` accepts a script/beat file and passes it to motion;
- motion timing is derived from something other than the built geometry;
- `theme` can express image treatment, density or motion vocabulary;
- `design_critic` can distinguish "an image that means something" from "an image
  that fills a hole", or "a deliberate reveal" from "a slide that opens blank".

None of these holds. Sections 3–6 show the code.

## 2. Measurements

Two decks, same instrument. T066 is the owner's deck. `vi_chuyen_doi_so.json` is
the lab's own reference example, built on this branch with
`python scripts/slide_forge.py build examples/pptx/forge/vi_chuyen_doi_so.json`
— i.e. what the default pipeline produces when nobody interferes.

| Fact | T066 (hand-built) | Forge example (default pipeline) |
|---|---|---|
| Slides / click groups | 10 / **51** | 9 / **30** |
| Clicks per slide | 4–7 (mean 5.1) | 1–6 (mean 3.3) |
| Click groups that run automatically | **0** of 51 | 0 of 30 |
| Effects | 144 | 99 main-sequence |
| Object lifecycles (enter → dim/exit) | **0** | 26 |
| Slides whose base state has no text or image | **1, 3, 5** | **2 (section), 9 (closing)** |
| Pictures revealed on the *last* click | **4 of 4** (slide 1 ×3, slide 2 ×1) | **1 of 1** (cover) |
| Slides with an animated title | **9 of 10** | 2 of 9 |
| Critic: design / motion / rhythm / coherence / overall | 2.98 / **4.99** / 4.48 / 3.67 / 4.03 | 5.0 / **5.0** / 4.5 / 5.0 / **4.88** |
| Critic warnings | 3 (all type) | **0** |

The second column is the important one. The owner's deck is a hand-built
exception; the *reference deck of the default pipeline* scores 4.88 with zero
warnings and still has an empty section divider, an empty closing slide, and a
cover whose only picture waits for a click. The failure is structural, not
personal.

Definitions, so the table can be re-measured: *base state* = what is on screen at
t=0, i.e. text/picture objects with no entrance effect; *picture on the last
click* = the picture's first effect belongs to the final click group; *lifecycle*
= one object with two or more effects (`design_critic` already computes this and
never grades it — see F14).

## 3. Finding A — the skills assume layout first and motion last

**F1. `slide-forge` describes itself as a single pass, in that order.**
`skills/slide-forge/SKILL.md:8-10`: "you write a semantic spec, it does layout,
typography, art, motion and checks". The spec schema (`slide_forge.py:185-209`)
has `layout`, text fields, `image`, `notes` — and **no field for an argument, a
beat, a script or an intent**. The user's story cannot enter the compiler.

**F2. `build()` derives motion from the finished file.** `slide_forge.py:927-932`:

```python
b.build(spec, static)                       # layout + art, fully finished
model = md.deck_model(static)               # read the geometry back
plan  = md.draft(model, goal=spec.get("title",""), style=..., ...)
```

The only narrative input to the entire motion stage is the deck **title string**,
passed as `goal` and used for one line of metadata. Motion is a function of
geometry.

**F3. `draft_slide()` dispatches on layout, not on meaning.** `motion_director.py:586-620`
branches on `_units(slide)` — chart, cycle, labeled, bullets, pictures — that is,
on what the shapes *are*. Every consequence follows: a 5-item cycle automatically
earns a 5-click spotlight tour (`motion_director.py:664`), a title slide always
gets "accents and picture give the opening life", a section always gets its
kicker and title as two clicks. The 4-click section divider in the Forge example
is not a decision; it is a default.

**F4. T066 is the pure case.** `inputs/build_deck.py` is 524 lines: layout on
lines 164–385, then a comment on line 386 — `# ---- motion + Morph` — and 138
lines of effects for all ten slides. The portraits were placed while building the
cover and could only be animated afterwards, when the only remaining variable was
*which click*. Slide 1 puts them on click 4 of 4; slide 2 puts the Plato bust on
click 7 of 7. The owner's S2 is literally the consequence of authoring a set
first and pointing a camera at it later.

## 4. Finding B — there is no script and no beat sheet

**F5. A "script" exists in the plan, but it is generated from the deck.**
`motion_director.py:1008-1014`:

```python
"script": {
  "source": "speaker-notes" if has_notes else ("existing-timing" if has_existing else "inferred"),
  "summary": "Each slide reveals its content in reading order ...",
  "beats": [f"slide {s['index']}: {title[:60]}" for s in model["slides"]],
}
```

That is a list of slide titles with the word "slide" in front. It is written
*after* the deck exists, by the same function that writes the motion. The
validator (`validate_director_plan.py:171-188`) requires it to be a non-empty
list of non-empty strings. A contract that promises a script and a checker that
only counts the strings.

**F6. `pptx-motion-director`'s step 0 inverts its own priority list.**
`skills/pptx-motion-director/SKILL.md:22-32` ranks "the user's script" first, then
notes, then existing animation, then "your own script". But the fallback for *no*
script is `motion_script.py draft DECK.pptx` — a script written by reading the
deck (`motion_script.py:17-19`: "so a deck without any script still gets one").
The stronger source is therefore never allowed to be *absent*: every deck gets a
plausible-sounding script, and the ranking stops discriminating. T066 has **no
script file and no director plan at all** (`inputs/` holds cut-out scripts, a
524-line builder and a render script; there is no `script.md`, `deck.json` or
`director.json`).

**F7. The script can only say *when*, never *what*.** `motion_script.plan_from_script()`
aligns narration segments with resources that already exist on the slide and
reports "clicks with nothing to show"; `--fill-gaps` turns a gap into a generated
callout. If the script says "here is Marx, and only then his sentence", and the
slide has no Marx, the module cannot add him. The ceiling of script-driven
direction on the current architecture is a callout.

**Consequence.** No artifact states *what the audience must believe after this
click*. The only place such a sentence could live — `beats[].purpose` — is filled
by template text (`"Build the chart data in its reading order so each series lands
as the presenter explains it."`), and T066 bypassed the Director entirely, so its
51 clicks carry no purpose field at all.

## 5. Finding C — "theme" is a palette and a font pair

**F8. `slide_forge`'s theme is six colour roles plus two fonts.**
`slide_forge.py:54-60` (`THEMES`), `87-108` (`office_theme()`), and
`theme_engine.py` is not referenced by the skill or by `slide_forge`. Nothing in a
theme says what a picture is *for*, how much whitespace a slide may keep, whether
rules are hairlines or absent, or whether a deck argues in theses or in scenes.

**F9. A richer style vocabulary exists — orphaned.** `theme_engine.py:643-745`
already defines seven archetypes with `shape_style`, `corner_radius_pt`,
`border_weight_pt`, `modular_scale`, a font pair and a `background_recipe`
("COMPOSITE_TEXTURE_IMAGE", "PURE_SOLID", "TRANSLUCENT_PNG_OVERLAY"). It is T043
code, unreviewed, wired to nothing, and its schema is still called `theme`. So the
lab has two competing notions of style (six hex roles vs. seven archetypes) and
ships the weaker one.

**F10. Motion "style" is a preset table.** `motion_director.py:67-81`: five names,
each a map from object role to `(preset, duration)`. `cinematic` = more zoom;
`dynamic` = PowerPoint built-ins. There is no vocabulary of *figures* — nothing
that says "a contrast must be visible as two states at once" or "a mechanism
assembles and then runs". Choice of style cannot express a rhetorical intention,
so all five styles produce the same rhythm with different easing.

**F11. Images have no treatment contract.** `forge_assets.py` acquires licensed
photos; `photo_vector.py` turns a photo into an illustration; nothing owns
crop → mask → duotone → grade for a slide. T066 did it in a one-off
`inputs/02_prepare_assets.py` (rembg + two-stop duotone + circular mask) and the
result is the best part of the deck. That recipe is not in any skill, preset or
design-system entry, so the next deck cannot repeat it.

## 6. Finding D — what the critic cannot see

`design_critic.py` grades five dimensions: design, motion, rhythm, coherence,
technique (`design_critic.py:63-71`). It reads **only the PPTX**. The plan — the
only file where intent could live — is not an input (`critique(path, render=None,
xsd=None)`).

**F12. No narrative dimension.** There is no check for order (evidence before
claim), for whether the object a slide is *about* stays on screen, or for whether
a deck has more than one kind of argument. T066's 51 clicks are all additive
reveals with zero lifecycles — a slide can only ever grow — and nothing notices.

**F13. Title identity is placeholder-only.** `design_critic.py:564` and `:660`
decide "is this a title" with `o["placeholder"]["type"] in md.TITLE_TYPES`. Forge
and T066 build with plain text boxes named `Title`/`title`. So the `MOT-TITLE`
rule never fires: T066 animates its title on 9 of 10 slides, the Forge example on
2 of 9, and the critic reports nothing. (The rule is also graded `"note"`, the
weakest severity — `design_critic.py:687`.)

**F14. The lifecycle metric is computed and never graded.** `design_critic.py:794-799`
counts objects with two or more effects and returns `deck.lifecycles`. T066: **0**.
The number appears in the JSON and in no rule, no score.

**F15. Per-effect checks swamp the score.** The 456 checks on T066 are:
153 `MOT-DURATION`, 110 `COL-TEXT`, 110 `LAY-SAFE`, 51 `MOT-EFFECTS` — 93 % are
per-object micro-checks. The dimension score is `1 + 4·(good + 0.5·note)/n`
(`design_critic.py:780-790`), so 152 good duration checks outvote any structural
failure. Motion 4.99 on a deck with zero lifecycles, every title wiping, and four
pictures that never survive a click is not a measurement error; it is what the
formula is built to produce.

**F16. The bands whisper.** `ds.grade()` returns `note` between band and limit
(`design_system.py:42-48`). Words-per-slide band ends at 45, limit at 80. T066 has
74, 78 and 80 words on three slides — a wall of text by any human standard — and
all three are **notes**, half credit. Same for 7 clicks on one slide (band ≤ 6).
So the owner's "too dense" is detected, graded as a whisper, and scored as almost
fine.

**F17. Base state and per-view composition are unmeasured.** `LAY-DENSITY`,
`LAY-BALANCE`, `COL-COLOURFUL` need `--render`; `slide_forge.build()` calls
`critique(out)` with no render, so in the normal loop they never run (T066's
`critic.json` has `frames: 0`). Even with a render they measure the **settled
frame** — the end state — never the t=0 state or any intermediate stable state.
"Every slide opens on a blank frame" is invisible to every existing check.

## 7. What the audit says the rewrite must be

The four symptoms reduce to three mechanical causes, and they compose:

1. **No causal artifact.** The pipeline is spec → file → motion. A deck cannot be
   directed because direction (what to say, in what order, with what in frame) is
   never written down. Everything downstream can only describe the file.
2. **Intent is unrepresentable and unverified.** Where a purpose field exists it
   is auto-filled; where it is absent nothing complains; and the critic never
   reads the plan. "Gu" has no address in the schema, so it cannot be required,
   checked or improved.
3. **Style is a token list.** Palette and type came out well (the owner said so),
   but a style that stops there cannot decide image treatment, whitespace,
   argument shape or motion grammar — the four things that separate T066 from a
   designed deck.

A rewrite that only adds fields would reproduce the failure with more JSON. The
repair is a **layer that is written before layout and consumed by both existing
skills**, plus a critic that can read it. That is `DECK-DIRECTOR-SKILL-DRAFT.md`.

## 8. Also true, and must not be lost

- The palette, font choice, Vietnamese glyph check and asset licensing in T066
  are good. The style layer must keep them as the *base*, not replace them.
- Forge's `T063` type-scale work and the Director's lifecycle-rich output
  (26 lifecycles on the reference deck) are real assets; the new layer should
  feed them, not compete.
- The critic's numbers are honest measurements of what they measure. The problem
  is coverage and weighting, not arithmetic.
- One deck proves nothing on its own. The second column of §2 is why this is a
  tool finding: the reference deck of the default pipeline has the same defects
  and a better score.
