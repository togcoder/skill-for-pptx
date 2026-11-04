---
name: deck-director
description: Direct a new deck before it is laid out — turn a topic, outline, document or chapter into a spoken script, a beat sheet of argument moves (hook, name, define, contrast, prove, mechanism, turn, land, ask), a shot list that fixes what is on screen at t=0 and after every click, and a style selection with the two policies a style cannot own (base state, image role) — then hand `deck.json` and `director.json` to slide-forge and pptx-motion-director. Use when the user asks for a deck about something (a lesson, a chapter, a report, a pitch, a talk), gives an outline or document to present, asks to "make it tell a story", or when a deck must argue, teach or persuade rather than simply list content. Do not use for a deck that already exists — use pptx-motion-director for that.
---

# Deck Director

> **Status: draft v0.1 (T067).** The contracts and the loop are usable today; the
> compiler `scripts/deck_director.py` does not exist yet. Until it does, follow
> *Compile by hand* below. Nothing here is wired into a product path.

You are the deck's director, not its typesetter. You decide **what the audience
must believe, see and feel at each moment** — then you write that down in files
that the builders obey. You never place a coordinate and never pick an animation
effect; if you are choosing a wipe, you are doing someone else's job and the deck
will show it.

`ROOT=<this skill dir>/../..`.

## Why this skill exists

Slide Forge compiles a *slide*. The Motion Director times a *click*. Neither owns
the thing between them: the argument, the beat, and what is in frame when the
presenter is still talking. A deck built without that layer is layout first and
motion last — the pictures arrive after the point they were meant to make, every
slide moves the same way, and no one can say why any click exists. That is not a
taste problem; it is a missing artifact. This skill is the artifact.

## Loop

0. **Brief.** Five fields, no deck yet:
   - `audience`, `minutes`, `room`;
   - `decision` — what the audience does after;
   - `one_sentence` — the sentence they should be able to repeat tomorrow;
   - `register` — `editorial_teaching | technical | executive | editorial_culture`.

   If `scripts/intent_decoder.py` exists, run it and store its `IntentBrief`
   under `brief.intent`; do not retype audience and cognitive budget by hand.
   **Gate:** if you cannot write `one_sentence` in one line, stop and ask — a deck
   without a spine cannot be directed, only decorated.

1. **Style.** Choose one preset (§Style) and record the two policies: `base_state`
   and `image_role`. **Gate:** a deck that changes preset after the first render
   re-runs the shot list, because image role and base state were chosen against the
   old one.

2. **Script.** Write the talk in the user's language, as Markdown with `## Slide N`
   and `[click]` cues (the `motion_script.py` format — do not invent a second one).
   Each scene opens with `claim:` in ≤25 words. Read it aloud once: cut every
   sentence that does not serve `one_sentence`. This file is a transcript of a
   talk, not a description of slides.

3. **Beats.** One beat per change in the audience's head — not per slide, not per
   bullet. For each: `job` (job table below), `claim`, `turn` (from → to),
   `evidence`, `carrier` (the object that embodies it), `attention` (what the eye
   hits first), and `clicks` — each click is a **stable state the presenter can
   talk over**, written as what the audience now knows, not as what the effect
   does.

   **Gate:** a beat whose `job` is `contrast` must be visible as two states at
   once; a beat whose `job` is `mechanism` must show the whole before walking the
   parts. A beat that cannot name a `carrier` is not a beat, it is a paragraph.

4. **Shots.** One shot per frame. Declare `base_state` **first** — the objects on
   screen at t=0 — then `state_after`, mapping each beat click to the objects that
   become visible. Objects carry a `role` (the layout is chosen from roles) and
   pictures carry an `asset` with `treatment`. **Gate:** an object appears exactly
   once across `base_state` and `state_after`; a shot whose base state has no text
   or picture is legal only for `job: hook`.

5. **Write `direction.json`** (`brief`, `style`, `script`, `beats`, `shots`) and
   run the contract checks in §Contracts. Fix the direction file, never the deck.

6. **Compile** to the two files the builders read (§Compile by hand until
   `deck_director.py` exists).

7. **Build.** `slide_forge build deck.json -o deck.pptx --plan director.json`
   (the `--plan` flag is the T067 proposal; until it lands, build with Forge and
   apply the plan with `motion_director.py apply`).

8. **Look.** Render and ask four questions, in this order:
   1. Does every pause slide read with no click? (section, quote, statement,
      closing)
   2. Is the thing the beat is about on screen before the words about it?
   3. Does each click change the argument, or only add a bullet?
   4. Does the deck move like one grammar — six figures, reused — or like a
      sampler of effects?

   Fix the direction file and rebuild. Do not fix the PPTX.

9. **Deliver** the `.pptx`, `direction.json`, the compiled `deck.json` /
   `director.json`, the ledger (§Ledger), and an honest rung
   (`$ROOT/docs/VERIFICATION.md`).

## Job table (why a beat exists)

| job | audience move | base state must carry | clicks | figure | never |
|---|---|---|---|---|---|
| `hook` | stop and look | the thing itself, or nothing if the reveal *is* the hook | 0–1 | `arrive` | a word-only title card |
| `name` | attach a word to a thing | the thing | 1 | `join` | the word before the thing |
| `define` | accept a definition | the term or its object | 1–2 | `build` | a definition before its subject |
| `contrast` | see A and B at once | nothing, or both grounds | 1–2 | `both` | A and B on separate clicks |
| `prove` | believe a number | axes, unit, context | 1–3 | `build` | the takeaway before the data |
| `mechanism` | understand how it works | the outline or the whole | 2–5 | `assemble` | a tour with no whole first |
| `turn` | change their mind | one sentence or one number | 0–1 | `clear` | chrome, cards, a second idea |
| `land` | remember the point | everything discussed | 1 | `clear` | a new object |
| `ask` | do something | the ask | 0 | `arrive` | motion at all |

Six figures: `arrive`, `join`, `build`, `both`, `assemble`, `clear`. They map to
recipes the Motion Director already has (`reveal`, `stagger-reveal`/`text-build`,
`swap`, `assemble` + `cycle`/`travel`/`spotlight`, `dim`/`exit`, `ken-burns` for a
carrier that must live without a click). Use the six; do not add a seventh
because a slide feels flat — a flat slide is a beat with no job.

**A tour is not a default.** Only `mechanism` beats walk parts one by one. A
five-part loop is not five clicks unless the script names each part.

## Base state policy

`poster_first` (default for editorial and cinematic presets): every content slide
carries at least one whole idea at t=0. The first click adds the *next* idea,
never the only idea. This is what makes a deck readable while the presenter
arrives, thinks, or is interrupted.

`build_first` (allowed for minimal and data presets): a slide may open on a frame —
axes, an outline, a question — and build. The frame must still be legible; "blank
until click 1" is not a frame. Pause layouts (section, statement, quote, closing)
are always `poster_first`, whatever the deck says.

## Style

A style says how things look; it cannot say when a thing must be on screen. This
skill selects a style and adds two policies — it does not define a second style
schema.

- **Preset ids** come from `VisualStyle/1`
  (`experiments/T067-20261104-opencode-visual-style/inputs/visual_style.py`,
  draft): `editorial-crimson`, `liquid-glass`, `clay-cartoon`, `swiss-minimal`,
  `maximalist-collage`. Resolve tokens with `visual_style.py tokens <preset>` and
  pass them to Forge; never type a hex, radius or duration yourself.
- **If `VisualStyle/1` is not available**, `style.preset` takes a Forge theme
  (`paper`, `office:Ion`, `{"seed": "#RRGGBB"}`) and the deck is reported as
  `style: forge_theme` — no style checks, no claims.

```json
"style": {
  "preset": "editorial-crimson",
  "base_state": "poster_first",
  "image_role": "evidence"
}
```

| field | values | decides |
|---|---|---|
| `base_state` | `poster_first` / `build_first` | whether a content slide must carry a whole idea at t=0, or may open on a legible frame |
| `image_role` | `evidence` / `atmosphere` / `punctuation` | what a picture is for: caption duty, whether it may be the only content of a `prove` beat, whether it must survive a click |

- **Numbers are not yours.** Margins, radii, gutters, type scale, durations,
  stagger and rhythm come from `knowledge/design_system.json` and the Office kit;
  the style preset is validated against the same bands.
- **Every image is treated before it is embedded:** crop to the role box, optional
  `rembg` cut-out, duotone, grade, mask; record `{source, licence, treatment, box,
  sha256}` in a manifest. A raw photo in a slide is a defect, not a shortcut. In
  the editorial presets the duotone stops are the style's `text` and `bg` — a rule,
  not a pair of hex values you like.
- An image declared `evidence` must be captioned or sourced; an image declared
  `atmosphere` may never be the only content of a `prove` beat.
- **The job → figure vocabulary is direction, not style.** A preset may tune how
  fast a figure runs; it may not decide that a contrast is shown as two states at
  once.

## Contracts

`direction.json` v0.1. Errors are codes; repair the direction, not the deck.

| code | check |
|---|---|
| `BRIEF-SPINE` | `one_sentence` present, ≤20 words |
| `SCRIPT-CLAIM-LONG` | every scene `claim` ≤25 words |
| `BEAT-JOB` | `job` in the nine |
| `BEAT-CLAIM` | claim is one sentence, ≤25 words |
| `BEAT-CARRIER` | `carrier` names an object in the beat's shot |
| `BEAT-CLICKS` | 0..6 clicks, unique ids, each with a `state` |
| `BEAT-TIME` | `seconds` present |
| `SHOT-BASE` | `base_state` names existing objects; non-empty except `job: hook` |
| `OBJECT-ORPHAN` / `OBJECT-TWICE` | every object in exactly one visibility state |
| `CLICK-UNMAPPED` | every beat click appears in `state_after`, in order |
| `LAYOUT-ROLE` | the layout can host the declared roles |
| `STYLE-UNKNOWN` | preset and enum values exist |
| `NAR-OFF-SPINE` | a beat that shares no term with `one_sentence` (override with a reason) |

## Compile by hand (until `deck_director.py` exists)

| `direction.json` | becomes | in |
|---|---|---|
| `shots[].layout` + objects by `role` + `text` | slide fields (`title`, `bullets`, `steps`, `chart`, …) | `deck.json` |
| `objects[role=anchor].asset` | `image` field (`{"file": …}` or `{"search": …}`) | `deck.json` |
| `shots[].base_state` | `base_state: ["Title", "Hero picture", …]` | `deck.json` (new field) |
| `beats[].clicks[].state` | `click_beats[].purpose` | `director.json` |
| `state_after[click]` | the click beat's `targets` (object names as Forge names them) | `director.json` |
| `beats[].job` + figure | `beats[].operation` / recipe | `director.json` |
| `script` | `script.md` for `motion_script.py --script`, and `click_beats[].narration` | both |

Object names must match what Forge writes (`Title`, `Hero picture`, `Card 1`,
`Step 2`, …). Run `motion_director.py inspect deck.pptx` after the first build and
correct the mapping; do not guess names.

## Ledger (what you report)

| fact | measure |
|---|---|
| clicks per slide | from the built deck's click groups |
| slides whose base state has no text or picture | count |
| carrier presence | clicks between the carrier's first appearance and slide end |
| pictures on the last click | count |
| distinct jobs / figures | counts |
| dead clicks | clicks that add nothing the beat's `state` promised |
| critic | `design_critic.py` **with** `--direction` once it exists |

## Never

- Never invent data, quotes or citations; label illustrative figures.
- Never exceed six clicks on a slide; three is usually a talk, six is a machine
  gun.
- Never animate a title inside a slide; titles move by Morph or not at all.
- Never let a beat exist for a layout you like. Choose the layout from the roles.
- Never write a purpose like "reveal the card" — that is the effect talking.
  Write what the audience now knows.
- Never deliver a deck whose `direction.json` you did not read back after the
  build. The build is the measurement.

## Evidence boundaries

A direction file is rung 0: a plan, not a deck. A built and rendered deck is rung
4–5 (PowerPoint opens/renders it; `CreateVideo` plays the clicks). Critic scores
are measurements of what they measure, never playback. Rung 6 — a human watching
every slide and click in the room — has not been reached by this lab, and this
skill cannot reach it.

## Not this skill

- An existing deck: `pptx-motion-director` (preserve by default).
- A one-slide fix or a re-theme: `slide-forge` directly.
- A document or a sheet: the `document-craft` / `sheet-craft` skills.
