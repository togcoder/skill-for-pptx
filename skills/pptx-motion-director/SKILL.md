---
name: pptx-motion-director
description: Add presenter-paced native PowerPoint animation — from simple builds to compound choreography (objects moving, assembling, cycling, swapping, zooming), motion layers (halo, rail, token, highlighter, rise-from-a-line) and professional cross-slide Morph (!! pairing, fly-ins, camera push-in, card expand) — to an existing .pptx deck while preserving its slides, text, layout and existing animation, then grade it against the shared design system. Use when the user gives a PowerPoint file and wants it animated, "brought to life", made cinematic or professional, builds/reveals added, bullets to appear one by one, a diagram walked through, charts or KPIs animated, Morph transitions, or a motion pass for presenting — even if they give only the file and a vague goal.
---

# PPTX Motion Director

You are the motion director. The user may give only a deck and a vague goal; do
not ask them to specify each animation. Read the deck, decide the story and the
click rhythm yourself, and deliver an editable PPTX with native PowerPoint
animation, a report, and an honest status.

Scripts live two levels above this file: `ROOT=<this skill dir>/../..`.

- **Required:** Python 3 + `lxml`.
- **Optional:**
  - LibreOffice Impress + poppler, for storyboards, previews and frame metrics;
  - `python-pptx` and Pillow.

## Workflow

0. **Script first.** Take the story from the strongest source available:
   1. the user's script (a file or pasted text);
   2. speaker notes;
   3. existing animation;
   4. your own script.

   A given script is saved as Markdown with `## Slide N` headings and
   `[click]` cues (`[nhấp]`, `[bấm]` and `>>` also work); then go to step 4b.
   Without one, run `python3 $ROOT/scripts/motion_script.py draft DECK.pptx -o script.md --style cinematic`.
   Then **rewrite every line into natural speech**: keep the cues and the
   words that name each resource, and add the points the story needs.
1. **Inspect.** Run `python3 $ROOT/scripts/motion_director.py inspect DECK.pptx`.
   Read titles, bullets (¶ = paragraph index), charts, numbers, notes, and
   objects already `ANIMATED`.
2. **Draft.** Run `python3 $ROOT/scripts/motion_director.py draft DECK.pptx -o director.json --style subtle|modern|bold|dynamic|cinematic [--goal "…"] [--no-morph] [--ambient]`.
   The draft is a starting point, not the answer.
3. **Direct.** Edit `director.json` with your judgement (rules below): what
   the audience sees first, what waits for the presenter, what lands as the
   conclusion.
4. **Apply.** Run `python3 $ROOT/scripts/motion_director.py apply DECK.pptx director.json -o OUT.pptx --storyboard storyboard/ --preview previews/`.

   4b. **Script-driven.** Run `… auto DECK.pptx -o OUT.pptx --script script.md --style cinematic [--fill-gaps] [--write-notes] --preview previews/`.
   The script decides *when* (each `[click]` line) and the director decides
   *how*:
   - A first mention reveals a resource; a later mention focuses it.
   - A line that names nothing new releases a tour.
   - If the script ends during a tour, a closing release click is added.
   - Paraphrased lines take the next resource in reading order.
   - `--fill-gaps` turns a line the slide cannot show into a callout in the
     deck's style.
   - `--write-notes` writes the narration into the speaker notes.
5. **Look.** Open the storyboard sheets, plus the GIF and sheet from
   `… preview OUT.pptx --slide N -o sN.gif --sheet sN.png`. Check order,
   collisions mid-move, empty starts and off-slide travel.
6. **Critique.** Every `apply` or `auto` report ends with a *Design critique*:
   source vs output scores against `knowledge/design_system.json`, plus open
   warnings in the form rule → measured → expected → fix. Fix the warnings
   that belong to motion (durations, easing, stagger, movers, clicks,
   helper contrast, settle). Report the warnings that belong to the source
   deck (its own text contrast or density) without editing the source unless
   asked. Run on any deck with
   `python3 $ROOT/scripts/motion_director.py critique OUT.pptx --md critique.md [--render lo]`.
7. **Morph** (optional, the professional finish): see *Morph Studio* below.
8. **Deliver** the PPTX, the `.report.md`, `.script.md` and `.critique.json`,
   and the evidence rung reached, e.g. "structurally checked and simulated;
   not yet played in PowerPoint" (`$ROOT/docs/VERIFICATION.md`).

One-shot path when speed beats craft:
`… auto DECK.pptx -o OUT.pptx --style cinematic --storyboard storyboard/`.

## The design system (beauty = technique)

`$ROOT/knowledge/design_system.json` holds the numbers the generators use and
the critic checks:

| Area | Values |
|---|---|
| Durations | entrance 250–700 ms; exit 200–500; emphasis 250–600; moves 400–1200 scaled with distance; Morph 1.0–1.6 s; ambient loop cycles ≥ 6 s; letter gap 20–60 ms |
| Easing | Moves slow in and out (Carbon-fitted accel/decel) |
| Stagger | 60–150 ms, only to show order |
| Rhythm | ≤ 4 independent movers per click; ≤ 6 clicks per slide; 3–10 effect kinds per deck |
| Contrast | WCAG text 4.5:1 (large text 3:1); helpers ≥ 3:1 |

Do not hard-code other numbers. When you deviate on purpose, say why in the
beat's `purpose`. Details: `$ROOT/docs/DESIGN_SYSTEM.md`.

## Direction rules

The story source ranks: explicit script > speaker notes > existing animation >
visible structure > inferred narrative. Never override a stronger source with
a prettier guess.

- **Preserve by default.** Slide count, order, text, geometry, theme and media
  stay. Existing animation is extended; replace it only with
  `"existing_timing":"replace"` and a `"replace_reason"` from the user's
  request.
- **A click is a presenter pause.** Start a new click when the audience should
  hold a meaningful state while the presenter talks. Use `with-previous` for
  things that belong together and `after-previous` for automatic
  continuation. Never fake speaking time with delays.
- **Don't animate everything, but never leave a picture frozen.**
  - Titles, footers, logos and badges stay still.
  - Large pictures get `ken-burns`.
  - Thin accent bars draw in at slide start.
  - A picture that continues by Morph stays where it was authored.
- **Idle motion is seasoning.** Use `float` on at most one or two accents,
  and never on an object a later click moves.
- **Data has meaning.** Charts use `data_motion` builds (series or category)
  chosen by chart type. Counters (`--counters`) add proxy shapes; use them
  only for a hero number, and say so.
- **Text-box decks.** The topmost short text is the title. A label reveals
  together with the block under it. Separate paragraphs (claim, rebuttal)
  get separate clicks.
- **Conclusions last.** Evidence first, then the takeaway on its own click.
  Secondary accents (highlighter, underline, rise) are for that click.
- **One motion language per deck.**
  - `subtle`: fade.
  - `modern`: float-in, wipe.
  - `bold`: zoom.
  - `dynamic`: PowerPoint presets real complex decks use.
  - `cinematic`: compound motion plus layers.

## Plan essentials (Director v0.7)

Each slide has `beats` (motion actions) and `click_beats` (presenter clicks
that partition the beats in order).

**Beat fields:**
- `id`, `purpose`, `operation`;
- `targets` (names or ids from inspect);
- `timing_intent`: `on-click`, `with-previous` or `after-previous`; the first
  beat may be `on-slide-start`;
- optional: `effect`, `duration_ms`, `layer` (`primary`, `secondary`,
  `ambient`), `trigger_shape`.

**Click beat fields:** `purpose`, `stable_state`, `pause_after`; from the
second click on, also `boundary_reason`. Optional `narration`.

| operation | use |
|---|---|
| `reveal` / `stagger-reveal` / `process-reveal` | appear together / one after another in one click |
| `text-build` | bullets by paragraph (`paragraphs: [0]`) |
| `focus` / `emphasize` | pulse (`effect: pulse`) |
| `dim` | fade others after discussing them |
| `exit` | remove (`fade-out`) |
| `move` / `rotate` | explicit points / degrees only; never guess geometry |
| `choreography` | compound recipes (below) |
| any + `data_motion` | chart build or KPI counter (`$ROOT/skills/pptx-motion/references/data-motion-recipes.md`) |

**Effects:**
- entrances: `appear`, `fade`, `float-in`, `zoom`, `wipe-*`, `type-on`
  (typewriter);
- exits: `fade-out`, `disappear`;
- emphasis: `pulse`, `spin`, `dim`;
- motion: `path`;
- `by: "word" | "letter"` on any entrance;
- any PowerPoint built-in as `ppt:<name>` (198 harvested presets, e.g.
  `ppt:faded-zoom`, `ppt:ascend`, `ppt:teeter`, `ppt:path-s-curve1`).

Real complex decks get their richness from object lifecycles (enter → move →
dim → exit), not from exotic presets.

The full v0.4 contract and its history are in
`$ROOT/skills/pptx-motion/references/existing-deck-director.md`. v0.5–v0.7
add choreography, transitions, layers, components and narration; the
validator (`validate_director_plan.py`) is the authority.

## Compound recipes (`"operation":"choreography"`)

Motion must explain, not decorate. If you cannot say what a movement means,
use a reveal. State (position, scale, rotation, opacity, visibility) carries
across clicks; `release` returns to the authored layout.

| recipe | targets | meaning / params |
|---|---|---|
| `assemble` / `disperse` | parts | Parts fly in to their places and arrive decelerating (`from`, `stagger_ms`, `overshoot` ≤ 0.08), or leave outward |
| `spotlight` / `release` | focus, others… | Focus grows, others dim (`scale`, `dim`, `halo`); one per click walks a diagram. `release` restores |
| `cycle` | ≥ 3 in order | Each moves to the next one's place (`steps`, `direction`) |
| `swap` | a, b | Exchange places on opposite arcs (re-ranking) |
| `travel` | token, stop… | Token moves to each stop; hop time scales with distance unless `duration_ms` is given. Stops pulse |
| `zoom-focus` | focus, others… | Focus moves and grows to `fill`, others exit; then `release` |
| `rise` | text | Text rises out of an invisible line; needs a `mask` component; refused if the mask would cover anything |
| `ken-burns` / `float` | pictures / accents | Slow push-in and drift / idle bob until slide end |
| `orbit`, `orbit-3d`, `wave`, `explode-layers`, `cascade-flow` | various | Revolve, 3D carousel, ripple, strata separation, token swarm (T024c). These are busy: check MOT-MOVERS |
| `breathe`, `drift`, `spin-loop`, `ripple` | ambient | `layer: "ambient"`, cycles ≥ 6 s |
| `tracks` | objects | Full keyframe control (below) |

**Keyframe keys:**
- `t` (ms);
- position: `x`/`y`, `dx`/`dy` or `to`;
- `curve`, `jump`, `scale`, `rotate`, `opacity`, `visible` with
  `enter`/`exit`;
- `ease`: `standard` (default), `enter`, `exit`, `expressive`, `linear`,
  `smooth`, `in`, `out`;
- `overshoot` ≤ 0.08, `anticipate` ≤ 0.05.

**Recipe options:**
- Virtual rigging carries labels sitting inside a shape (`"rigging": false`
  disables it).
- `"auto_avoid": true` curves paths around obstacles.
- `attach: {"Leader": ["Label"]}` makes a label follow its shape.
- A click beat with `trigger_shape` becomes a shape-click trigger
  (`interactiveSeq`; not verified natively).

**Blocking checks:**
- two overlapping moves of one object;
- a later click moving an object that is still looping;
- an after-previous effect queued behind a loop.

Warnings flag objects ending off-slide or newly covered. Read them; they are
usually real.

## Motion layers and generated components

- **Primary** is the meaning.
- **Secondary** reacts to it:
  - a `halo` follows each spotlight;
  - a `track-line` plus `token` runs under a walked process;
  - an `orbit-ring` sits behind a cycle;
  - `ripple`, `highlight` (a marker behind the conclusion, with opacity
    sized so the text keeps its contrast), `underline`, and a `mask` for
    `rise`.
- **Ambient** is slow background life.

Components (`components[].generate`) are named `__gen_<kind>_<id>`. They need
a role and rationale, and use the deck's font plus a deck colour that reaches
3:1 against the slide. Prefer an existing resource (the deck's own token) over
generating one. `--style cinematic` proposes these layers; `--ambient` adds
drifting backdrops.

## Morph Studio (cross-slide, professional finish)

```bash
python3 $ROOT/scripts/morph_studio.py propose OUT.pptx -o morph.json      # continuity + ≤ 1 scene idea per slide
# accept suggestions into "scenes" (each needs a reason); add "pairs" to force two shapes to morph
python3 $ROOT/scripts/morph_studio.py apply OUT.pptx morph.json -o FINAL.pptx
python3 $ROOT/scripts/morph_studio.py preview FINAL.pptx --slide N -o mN.gif --sheet mN.png
```

**Continuity:**
- pairs objects across slides with `!!` names, renaming whole chains;
- titles glide; the same picture or text travels;
- sets Morph to `byObject`, `byWord` or `byChar`;
- stages new and leaving objects off-slide so they fly, with cards moving as
  one piece.

**Scenes** add slides, each starting from the source's end state:
- `camera-zoom`: push in, pull back;
- `card-expand`: a card grows into a panel over its neighbours;
- `pan`: carousel.

Read `references/pro-techniques.md` (50 techniques) before choosing.

**Settle before Morph.** Morph starts from each slide's authored layout, not
from where animation left it. `apply` reports `unsettled` slides; end them on
the full picture, or accept the snap knowingly. The Morph preview is
simulated.

Experimental modules from T033 (`morph_playbook.py`, `cognitive_pacing.py`,
`interactive_triggers.py`) are **not** part of this workflow. Director plans
have no `pre_stage`/`post_stage` keys.

## Evidence boundaries

Name the rung reached (`$ROOT/docs/VERIFICATION.md`). The writer reproduces
the timing structure PowerPoint saves.

| What | Rung reached |
|---|---|
| Sequencing, paths, Grow/Shrink, Transparency, exits | LibreOffice reads them as intended |
| Many effects | PowerPoint 16.0 parsed them, and CreateVideo rendered Ken Burns, loops and Forge decks |
| Interactive click playback, Presenter View, shape triggers, Morph Studio `!!` chains and scenes | Not observed (Forge `!!orb` Morph was rendered, T025) |

GIFs and storyboards are simulations. Critic scores are measurements, not
playback. Never describe XML checks, previews, LibreOffice output or scores as
PowerPoint playback.
