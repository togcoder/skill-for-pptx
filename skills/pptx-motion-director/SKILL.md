---
name: pptx-motion-director
description: Add presenter-paced native PowerPoint animation to an existing .pptx deck while preserving its slides, text, layout and existing animation. Use when the user gives a PowerPoint file and wants it animated, "brought to life", builds/reveals added, bullets to appear one by one, charts or KPIs to animate, or a motion pass for presenting — even if they give only the file and a vague goal.
---

# PPTX Motion Director

You are the motion director. The user may give only a deck and a vague goal; do
not ask them to specify each animation. Read the deck, decide the story and the
click rhythm yourself, and deliver an editable PPTX with native PowerPoint
animation plus a short report.

Scripts live in the repository root two levels above this file:
`ROOT=<this skill dir>/../..`. Requirement: Python 3 with `lxml`
(`pip install lxml`). Optional for visual QA: LibreOffice Impress + ImageMagick.

## Workflow

1. **Inspect** — `python3 $ROOT/scripts/motion_director.py inspect DECK.pptx`
   Read every slide: titles, bullets (¶ = paragraph index), charts, numbers,
   speaker notes, and objects already marked `ANIMATED`.
2. **Draft** — `python3 $ROOT/scripts/motion_director.py draft DECK.pptx -o director.json [--style subtle|modern|bold] [--goal "..."]`
   The heuristic draft is a starting point, not the answer.
3. **Direct** — edit `director.json` with your judgement (rules below). This is
   where the value is: decide what the audience should see first, what waits for
   the presenter, and what lands as the conclusion.
4. **Apply** — `python3 $ROOT/scripts/motion_director.py apply DECK.pptx director.json -o OUT.pptx --storyboard storyboard/`
   It validates the plan, writes PowerPoint-canonical timing, re-reads the
   output and prints a per-click storyboard. Fix any reported problem.
5. **Look** — open the `storyboard/slide-NN.png` contact sheets (one frame per
   stable click state) and check order, overlaps and empty starts. Iterate.
6. **Deliver** — the PPTX, the `.report.md`, and an honest status line:
   "structurally checked and simulated; not yet played in PowerPoint".

One-shot path when the user wants speed over craft:
`python3 $ROOT/scripts/motion_director.py auto DECK.pptx -o OUT.pptx --storyboard storyboard/`

## Direction rules

Source of the story, strongest first: the user's explicit script > speaker
notes > the deck's existing animation > visible structure (titles, order,
diagrams) > your inferred narrative. Never override a stronger source with a
prettier guess.

- **Preserve by default.** Slide count, order, text, geometry, theme and media
  stay as they are. Existing animation is extended (new clicks are appended
  after it); replace only with `"existing_timing":"replace"` plus a
  `"replace_reason"` grounded in the user's request.
- **A click is a presenter pause.** Start a new click beat when the audience
  should hold a meaningful state while the presenter talks (each bullet, each
  KPI card, each process step the notes walk through, the takeaway after a
  chart). Use `with-previous` for things that belong together and
  `after-previous` for automatic continuation. Never fake speaking time with
  delays. Keep it humane: usually ≤ 6 clicks per slide.
- **Don't animate everything.** Titles, footers, logos, decoration and small
  badges stay static. A title slide usually stays static.
- **Data has meaning.** Charts use `data_motion` builds (series/category) chosen
  by chart type; never a generic reveal. Counters (`--counters`) add hidden
  proxy text shapes, which clutter edit view and PDF export — use only for a
  true hero number and say so.
- **Text-box decks.** Many decks have no placeholders. The topmost short text
  is the title and stays static. A label ("Cách 1: …") reveals together with
  the text block under it. Each separate paragraph of a dense body (claim, then
  rebuttal) gets its own click. Never split a wrapped heading.
- **Conclusions last.** Evidence (chart/process) first, then the takeaway on its
  own click.
- **One motion language per deck.** Pick a style and stay consistent:
  `subtle` (fade), `modern` (float-in, wipe connectors), `bold` (zoom).

## Director plan (v0.5) essentials

Each slide entry has `beats` (motion actions) and `click_beats` (presenter
clicks that partition the beats in order). Beat fields: `id`, `purpose`,
`operation`, `targets` (object names or ids from inspect), `timing_intent`
(`on-click` | `with-previous` | `after-previous`; the very first beat may be
`on-slide-start` to play automatically), optional `effect`, `duration_ms`.

| operation | use | notes |
|---|---|---|
| `reveal` | objects appear together | e.g. card + its texts |
| `stagger-reveal` / `process-reveal` | objects appear one after another in one click | target order = order |
| `text-build` | bullets by paragraph | `paragraphs: [0]`; sub-levels follow their parent |
| `focus` / `emphasize` | pulse one object | `effect: pulse` |
| `dim` | fade others to 35% after discussing them | `motion_parameters.opacity` |
| `exit` | remove an object | `effect: fade-out` |
| `move` / `rotate` | explicit path points / degrees only | never guess geometry |
| any + `data_motion` | chart build or KPI counter | see `references/data-motion-recipes.md` |

Effects: `appear fade float-in zoom wipe-up wipe-down wipe-left wipe-right`
(entrances), `fade-out disappear` (exits), `pulse spin dim` (emphasis), `path`.

Click beats need `purpose`, `stable_state`, `pause_after`, and from the second
click on a `boundary_reason`. Full contract:
`$ROOT/skills/pptx-motion/references/existing-deck-director.md`.

## Evidence boundaries

The writer reproduces the timing structure PowerPoint saves for its built-in
effects and an independent importer (LibreOffice) reads the sequencing as
intended, but nothing here has played in PowerPoint. Storyboard frames are
static renders of simulated stable states (chart builds show as whole charts).
Never describe XML checks, storyboards or LibreOffice output as PowerPoint
playback. Native verification: `$ROOT/docs/POWERPOINT_NATIVE_HARNESS.md`.
