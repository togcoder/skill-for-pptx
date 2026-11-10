# T089 [pptx] — Harmful defaults: Forge, Director and the font check

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash).
- **Date:** 2026-11-10. **Branch:** `work/T089-opencode-harmful-defaults`.
- **Status:** code change in product paths (`scripts/slide_forge.py`,
  `scripts/motion_director.py`, `scripts/forge_qa.py`,
  `scripts/data_motion_recipes.py`) plus one guide note. **Review requested**
  from Claude (different model family) before merge.
- **Addresses:** the T089 brief in `docs/ROADMAP.md`; F5/F8 (the owner sees
  decoration and Morph that nobody asked for); D011 (guidance first, code only
  for what words cannot do).

## Open first

`experiments/T089-20261110-opencode-harmful-defaults/artifacts/qcc-theme.pptx`
— 7 slides, built from the QCC-style spec in `inputs/qcc-theme.json`.
`preview/sheet.jpg` is the same deck as one contact sheet, rendered by
PowerPoint.

What to look for when flipping through it:

1. **The cover** should start by itself once and then wait. It should not ask
   for four or six clicks to assemble the title.
2. **Slide 4 (bento)** has a card whose number is **0**. It should simply read
   "0"; the build should not stop.
3. **Slide 5 (KPI row)** also starts with 0. The three values reveal as text,
   not as count-up stacks.
4. **Card titles** (slides 3 and 4) should be readable sizes — 28 pt and 20 pt —
   not squeezed to 14 pt.
5. **No circles in the corners** of any slide, no `!!` decoration anywhere,
   no text logo stamped top-right, and **no Morph** between slides. This deck
   has no object that travels, so it gets none.
6. The word `QCC` is passed as `logo` on purpose. It is skipped with a note
   ("not an image file") instead of being drawn as a watermark.

The deck is a defaults acceptance test, not a design showcase. Its composition
still has the weaknesses named under **Limits** below.

## Frame

**Question.** Which decisions do the old tools still make on the designer's
behalf, and how do we make the default "do nothing" instead of "do the wrong
thing"?

**Hypothesis.** The owner's "motion is forced" is not only a directing problem.
Part of it is manufactured upstream: Forge adds decoration and turns Morph on,
the Director reads that decoration as continuity, and the cover is split into
clicks because the cover detector does not recognise a text-box cover. Fix the
source, and the Director's output gets quieter without a new directing rule.

**Falsifiers.**

- The seven defects are not reproducible on current `main`.
- A fix makes legitimate motion disappear (a real travelling object no longer
  gets a Morph; a real logo image is dropped).
- The fixes only move the defect (e.g. the KPI 0 build succeeds but the slide
  is empty or the number is missing).
- The full suite still passes only because the old tests encoded the defect.

## Frozen input

The defect list is the T089 brief (owner's read of the QCC theme build). The
reproduction ran on `main` at claim time; the QCC-style acceptance spec is
`inputs/qcc-theme.json` (synthetic data, no customer content).

Environment: Windows, Python 3.13.5, python-pptx 1.0.2, Pillow 13.0.0,
lxml 6.1.1, Microsoft PowerPoint 16.0 build 17932.20130.

| Artifact | SHA-256 |
|---|---|
| `artifacts/qcc-theme.pptx` | `9C1E321DED0A280E8CD2383E1E01B7CEABEA8B9DD0723265E2F3835CE5673EC3` |
| `artifacts/qcc-theme.static.pptx` | `DC171B100C2EA279B7B0BA3FF7F7C6AF20DE5076686AFA0ABA02664131AA1052` |

## Method

1. Reproduce every defect on the unmodified code before touching it
   (`workspace/repro.py`, scratch; results quoted below).
2. Write `tests/test_harmful_defaults.py` first, one test per defect, and run the
   first nine against the old code: eight failed. The ninth ("a content object
   still causes a Morph") passed by design, so a fix could not silence all
   Morphs; a tenth test for the explicit `morph: true` path was added after the
   fix.
3. Fix each defect at its source, not at the acceptance deck.
4. Re-run the new tests, then the full suite.
5. Rebuild the QCC-style spec and inspect the result with `pptx_tools.py
   inventory` and PowerPoint's own render (`pptx_tools.py look`).
6. Update the one guide paragraph that taught the old defaults.

## Findings

### 1. A KPI of 0 stopped the build

**Before:** `ValueError: counter produced no intermediate proxy values`.
`number_counter_recipe` accepted `0` as a counter target; the proxy stack then
had no values between start and end.

**Fix:** `scripts/data_motion_recipes.py` returns `None` when the target is 0.
The number reveals as ordinary text. No counter stack, no empty animation.
**Test:** build succeeds and no `__counter_` shape exists.

### 2. Card titles were squeezed to 14 pt

**Before:** `Major Heading`, `Minor Heading`, `Hero Title` and `TopRight Title`
were all 14 pt on short text, with four `TEXT_SHRUNK` warnings. The asymmetric
and bento layouts used `label`/`subhead` in a 0.4–0.45 in box, so the fitter
walked down the scale.

**Fix:** the type scale gains a `card` level snapped from the design system's
`tokens_pt.card_title` (18 pt). Card titles use it, and their boxes grew from
0.4–0.45 in to 0.5–0.62 in. In this deck the snap lands on 20 pt; hero/major
titles keep 28 pt. **Test:** every card title is at least 18 pt and none of
those objects carries `TEXT_SHRUNK`.

### 3. Decoration and Morph were on by default

**Before:** every slide got two `!!orb-1/!!orb-2` circles, and `motion.morph`
defaulted to `true`, so a plain two-slide deck had one Morph between
decoration.

**Fix:** `Builder` defaults `morph` to `false`, and `background()` no longer
draws orbs. The schema text says what `morph: true` now means: add Morph only
where a content object travels. **Test:** no `!!` shapes and zero Morph
transitions by default; a separate test with an explicit shared picture still
gets a Morph.

### 4. A word passed as `logo` became a text watermark

**Before:** `logo: "ACME"` produced a `Logo Watermark` text shape on every
content slide.

**Fix:** `_logo_image()` accepts only a real image file. A word is skipped once
with a `LOGO_SKIPPED` note; the heading no longer reserves logo space for it.
**Test:** a word produces no logo shape and one note; a PNG is placed as a
picture (`shape_type == 13`).

### 5. The cover was split into clicks

**Before:** a cover made of kicker, title, subtitle, presenter, date and a rule
was treated as a content slide: 4 click groups in the reproduction (the owner
saw 6 on a richer cover). The title assembled click by click.

**Fix:** `_is_text_title_slide` now recognises a cover by what it lacks — no
chart/table, no filled card holding body copy or a number — instead of
requiring at most four text boxes. A date outside a card no longer disqualifies
it. **Test:** the cover gets exactly one click group and its first beat is
`on-slide-start`.

### 6. Decoration caused a Morph on every transition

**Before:** `shared_objects` treated a moving `!!orb` as continuity, and any
object present on every slide could trigger a Morph.

**Fix:** `shared_objects(prev, cur, ignore=)` separates "rides along" from
"justifies the cut". Decoration and chrome placeholders never justify it;
`_ubiquitous_names` removes names present on every slide. A two-slide deck is
exempt from the ubiquitous rule so a cover portrait can still travel into
slide 2. **Tests:** decoration alone → 0 Morph; an object on every slide → 0
Morph; a content object that moves → 1 Morph.

### 7. A missing font was reported as overflowing text

**Before:** a deck in a font this machine does not have produced
`TEXT_OVERFLOW`, because the fallback width estimate was treated as measured
fact.

**Fix:** `forge_qa.qa` checks `text_metrics.font_path(family)` first. Without
the file it emits one `FONT_MISSING` warning per family ("measurements are
approximate") and does not claim overflow. Forge's own text fitter makes the
same distinction: a missing font is a note, not an error. **Test:** the deck
gets `FONT_MISSING` and no `TEXT_OVERFLOW`.

## Evidence

Reproduction before the fix (scratch run, 2026-11-10):

| Defect | Observed before |
|---|---|
| KPI 0 | build raised `ValueError` |
| card titles | 14/14/14/14 pt, four `TEXT_SHRUNK` |
| decoration | 2 `!!orb` per slide, 1 Morph on a 2-slide deck |
| word logo | `Logo Watermark` text shape |
| cover | 4 click groups |
| Morph reason | orb-only model → Morph |
| missing font | `TEXT_OVERFLOW` error |

After the fix:

| Check | Result |
|---|---|
| new regression tests | **10/10 pass** (8 of the first 9 failed before the fix; the ninth guards a real Morph) |
| full suite | **600 run, 10 skipped, OK** |
| acceptance build | ok, 0 errors, 1 intended `LOGO_SKIPPED` note |
| slides / effects / motion coverage | 7 / 92 / 1.0 |
| Morph transitions | 0 (no travelling content object) |
| decoration / word logo shapes | none / none |
| card title sizes | Major 28, Minor 20, Hero 28, TopRight 20 |
| cover | 1 click group, first beat `on-slide-start` |
| type sizes | 5 (14, 20, 24, 28, 44) |
| PowerPoint render | 7 PNGs + contact sheet (`preview/`) |

The acceptance deck's `0` values appear as text on slides 4 and 5; no counter
stack was created.

## Limits / negative results

- **Composition is still Forge's weak point.** `pptx_tools.py inventory` flags
  slides 2, 3, 6 and 7 as "opens with only the title visible", and the bento
  and asymmetric cards hold large empty areas (slide 4 is the clearest case).
  T089 fixes the defaults; it does not make Forge a good composer. This is
  exactly the T095 rule catching Forge, and it needs its own task.
- **The Director can still open a content slide with only its title.** The
  cover fix is specific to slide 1. T095's rule remains the check for the rest.
- **No owner score yet.** The deck was rendered and inspected, but the
  quality measure is the owner's eye (D001). Rung 4 for parsing/rendering;
  rung 6 pending.
- **The explicit `morph: true` path is structurally tested, not played back.**
  The test asserts a Morph transition exists for a shared picture; no
  PowerPoint video capture was made for that two-slide case.
- **Decoration can still ride a Morph.** If a content object justifies the
  cut, a `!!` shape that also travels is included in `continuing_ids`. That is
  intentional (the decoration is not the reason), but it means a user-authored
  `!!` shape can still move.
- **The logo note is a warning, not an error.** A deck that passes a word as a
  logo still builds; it just has no logo. That is the chosen default (skip,
  say so) rather than guessing a mark.

## Follow-ups (out of T089)

1. **Forge's `t=0` frame.** Show the frame — labels, cards, axes — before the
   first click, and reduce empty card area in bento/asymmetric. Consumes the
   T095 rule "no slide may open with only its title".
2. **Director cover heuristic elsewhere.** Decide whether a section divider is
   allowed to open with only its title (currently flagged).
3. **Owner grades** for T090, T093, T094, T095 and this acceptance deck.

## Files changed

| File | Change |
|---|---|
| `scripts/slide_forge.py` | `morph` default false; orbs removed; `card` type level; card-title boxes; logo image-only + note; missing-font note |
| `scripts/motion_director.py` | cover detector; `shared_objects(ignore=)`; `_ubiquitous_names`; Morph reason excludes decoration/chrome |
| `scripts/forge_qa.py` | `FONT_MISSING` before any overflow verdict |
| `scripts/data_motion_recipes.py` | counter target 0 returns no recipe |
| `skills/pptx/guides/9-do-nghe.md` | old-tool paragraph now describes the fixed defaults |
| `tests/test_harmful_defaults.py` | 10 new regression tests |
| `tests/test_slide_forge.py` | example deck expects 0 Morph (it has no travelling object) |
| `tests/test_pptx_design_canon.py` | chrome test uses a real logo image |
| `examples/pptx/forge/coffee_report.json` | no `morph: true` (no real continuity) |
