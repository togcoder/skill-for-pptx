---
name: pptx-motion-director
description: Add presenter-paced native PowerPoint animation — from simple builds to compound choreography (objects moving, assembling, cycling, swapping, zooming, Morph between slides) — to an existing .pptx deck while preserving its slides, text, layout and existing animation. Use when the user gives a PowerPoint file and wants it animated, "brought to life", made cinematic, builds/reveals added, bullets to appear one by one, a diagram walked through, charts or KPIs animated, or a motion pass for presenting — even if they give only the file and a vague goal.
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
2. **Draft** — `python3 $ROOT/scripts/motion_director.py draft DECK.pptx -o director.json [--style subtle|modern|bold|cinematic] [--goal "..."] [--no-morph]`
   The heuristic draft is a starting point, not the answer.
3. **Direct** — edit `director.json` with your judgement (rules below). This is
   where the value is: decide what the audience should see first, what waits for
   the presenter, and what lands as the conclusion.
4. **Apply** — `python3 $ROOT/scripts/motion_director.py apply DECK.pptx director.json -o OUT.pptx --storyboard storyboard/`
   It validates the plan, writes PowerPoint-canonical timing, re-reads the
   output and prints a per-click storyboard. Fix any reported problem.
5. **Look** — open the `storyboard/slide-NN.png` contact sheets (one frame per
   stable click state). For any slide with movement, render the motion:
   `python3 $ROOT/scripts/motion_director.py preview OUT.pptx --slide N -o sN.gif --sheet sN.png`
   (or `apply ... --preview previews/`). Read the sheet PNG; it shows every
   click's end state, and the GIF shows the motion between them. Check order,
   collisions mid-move, empty starts and off-slide travel. Iterate.
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

## Compound motion (Director v0.6)

Use when the slide's structure *means* something that motion can show: a cycle
turns, an ecosystem assembles around its hub, a ranking changes, an order
travels through a process, a quadrant is drilled into, a picture carries on to
the next slide. Motion must explain, not decorate; if you cannot say what the
movement means, use a reveal.

Beat: `"operation":"choreography"`, `"recipe"`, `"targets"` (names from
inspect), optional `"motion_parameters"`. State (position, scale, rotation,
transparency, visibility) carries across clicks, so later beats continue from
where earlier ones left off; `release` returns everything to the authored layout.

| recipe | targets | meaning / params |
|---|---|---|
| `assemble` | parts | parts fly in to their places, staggered. `from`: center (of the parts) · slide-center · below/above/left/right · outward; `stagger_ms`, `duration_ms` |
| `disperse` | parts | the reverse: parts leave outward and fade |
| `spotlight` | focus, others… | focus grows (`scale` 1.15), others dim (`dim` 0.35); `toward_center` 0..1. Chain one per click to walk a diagram |
| `release` | objects | restore authored position/size/rotation/opacity; re-enter hidden ones |
| `cycle` | ≥3 in order | every object moves to the next one's place along the circle; `steps`, `direction` forward/back |
| `swap` | a, b | exchange places on opposite arcs (`arc` 0.25) — re-ranking, before/after |
| `travel` | token, stop… | token moves to each stop (`arc`, `offset_y`, `dwell_ms`), stops pulse; one beat per click walks a journey |
| `zoom-focus` | focus, others… | focus moves to (`x`,`y`, default 0.5) and grows to `fill` of the slide; others exit. Follow with `release` |
| `tracks` | objects | full control: `"tracks":[{"target":"Name","keyframes":[{"t":0},{"t":800,"dx":0.1,"dy":-0.05,"scale":1.2,"rotate":15,"curve":0.2,"ease":"smooth"}]}]` |

Keyframe keys: `t` (ms from beat start); position `x`/`y` (slide fractions of
the object's centre), `dx`/`dy` (offset from its authored place) or `to`
(another object's name); `curve` (bulge, + = left of travel), `jump`; `scale`
and `rotate` absolute vs authored; `opacity` 0..1; `visible` with
`enter`/`exit` preset; `ease` linear|smooth|in|out.

Deck-level `"transitions":[{"slide":8,"kind":"morph","reason":"…"}]` adds a
Morph (Fade fallback) where a shared object (same picture, same text or same
`!!` name) moves between slides; do not also animate that object's entrance.
`draft` proposes these automatically and detects cycle/hub diagrams.

Checks that will stop or warn you: two moves/scales/spins of one object
overlapping in time (blocking), an object ending off-slide or newly covering
another at a stable state (warning). Read and fix warnings; they are usually
real.

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
effects and an independent importer (LibreOffice) reads the sequencing,
motion paths, Grow/Shrink, Transparency and exits as intended, but nothing
here has played in PowerPoint. Chained paths assume PowerPoint's
layout-anchored path semantics (T006 hypothesis); GIF previews simulate that
assumption. Storyboard frames are
static renders of simulated stable states (chart builds show as whole charts).
Never describe XML checks, storyboards or LibreOffice output as PowerPoint
playback. Native verification: `$ROOT/docs/POWERPOINT_NATIVE_HARNESS.md`.
