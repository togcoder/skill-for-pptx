---
name: deck-director
description: Direct a new deck before it is laid out — turn a topic, outline, document or chapter into a spoken screenplay with Two-Pass Choreography (state machine and stage inventory first, natural voice weave second), a beat sheet of argument moves (hook, name, define, contrast, prove, mechanism, turn, land, ask), a shot list fixing base_state at t=0 and lifecycle state_after (enter, dim, highlight, exit, zoom) for every click, an image choreography that binds each picture to the sentence that names it, and a VisualStyle preset with the two policies a style cannot own (base state, image role) — then compile direction.json into deck.json and director.json for slide-forge and pptx-motion-director. Enforces five hard narrative laws (anti-Coda, anti-Karaoke, unanchored monologue, motion collision, active view cap) and the image rules (no coda image, no empty frame). Use when the user asks for a deck about something (a lesson, a chapter, a report, a pitch, a talk), gives an outline or document to present, asks to "make it tell a story", or when a deck must argue, teach or persuade rather than simply list content. Do not use for a deck that already exists — use pptx-motion-director for that.
---

# Deck Director

> **Status: v0.3 (T067 + T068 merge).** Two-pass compiler and validator live in
> `scripts/deck_director.py`; `slide_forge.py build --plan` consumes its output.
> The five narrative laws are implemented and unit-tested. The image rules and
> the `VisualStyle/1` presets are still research-grade (T067), not product canon.

You are the deck's director, not its typesetter. You decide **what the audience
must believe, see and feel at each moment** — then write that down in files the
builders obey. You never place a coordinate and never pick a raw animation
effect; if you are choosing a wipe, you are doing someone else's job and the deck
will show it.

`ROOT=<this skill dir>/../..`.

## Why this skill exists

Slide Forge compiles a *slide*. The Motion Director times a *click*. Neither owns
the thing between them: the argument, the beat, and what is in frame while the
presenter is still talking. A deck built without that layer is layout first and
motion last:

- pictures arrive after the point they were meant to make (Coda Trap);
- slides open on a blank or decorative-only stage at `t=0`;
- text accumulates into unreadable clutter (`lifecycles: 0`);
- the presenter reads word-for-word what is already on screen (Karaoke Effect);
- each picture is treated as an ornament appended last, not as a block of the
  argument.

That is not a taste problem; it is a missing architectural artifact. Deck
Director is that artifact: **Two-Pass Choreography** locks the visual state
machine before weaving the spoken line.

## Two-Pass Loop

### Pass 1: Architecture and State Machine (stage inventory, beats, shots)

0. **Brief.** Five fields:
   - `audience`, `minutes`, `room`;
   - `decision` — what the audience does after;
   - `one_sentence` — the repeatable spine (≤ 20 words);
   - `register` — `editorial_teaching | technical | executive | editorial_culture`.

   **Gate:** if you cannot write `one_sentence` in one line, stop and ask. A deck
   without a spine cannot be directed, only decorated.

1. **Style.** Choose one `VisualStyle/1` preset (see §Style) and record the two
   policies: `base_state` (`poster_first | build_first`) and `image_role`
   (`evidence | atmosphere | punctuation`).

   **Gate:** a deck that changes preset after the first render re-runs the shot
   list, because image role and base state were chosen against the old one.

2. **Beats (nine jobs).** One beat per cognitive shift in the audience's mind —
   not per slide, not per bullet. Each beat carries `job`, `claim` (≤ 25 words),
   `turn` (from → to), `evidence`, `carrier` (the object that embodies it),
   `attention` (what the eye hits first) and `figure`.

   **Gate:** a beat whose `job` is `contrast` must show two states at once; a
   beat whose `job` is `mechanism` must show the whole before walking the parts.
   A beat that cannot name a `carrier` is not a beat, it is a paragraph.

3. **Shots and stage inventory.**
   - Declare all `objects` with `id`, `role`, and optional `text`, `asset`, or
     `zoom_spec`.
   - Declare `base_state` **first** — the objects on screen at `t=0` (non-empty
     except `job: hook`).
   - Declare `state_after` for each click with full lifecycle control:
     `enter` (new objects), `dim` (de-emphasised), `highlight` (focused),
     `exit` (removed), and optional `action`.

   **Gate:** every object enters at most once (`OBJECT-ENTER-ONCE`); objects in
   `dim`/`exit` must have previously entered (`OBJECT-LIFECYCLE-VALID`).

### Pass 2: Natural Voice Weave (split-sentence bridging and deictic anchoring)

4. **Weave the spoken screenplay.**
   - **`t0_says`:** the opening spoken sentence delivered while the audience
     looks at `base_state` at `t=0`. Never leave `t=0` without voice or with a
     blank slide.
   - **`clicks[].lead_in`:** pre-click cue that provides momentum before the
     button press.
   - **`clicks[].post_click_says`:** spoken explanation after the click lands,
     explaining the new visual state and referencing the target object.
   - **Split-sentence bridging:** place the click at the pivot between cause and
     effect — *"In small clusters this runs smoothly… but when load scales 10×
     — [click] — this database node becomes a single point of failure."*
   - **Implicit deictic anchoring:** never say *"As you see on the left"*. Say
     *"When we strip this outer caching layer…"* matching the visual transition.

5. **Scaffold, validate and compile.**
   - **Scaffold a new draft:**
     ```powershell
     python scripts/deck_director.py scaffold -o direction.json --title "My Topic" --slides 3 --preset editorial-crimson
     ```
   - **Validate Pass 1 (Stage & State Machine only):**
     ```powershell
     python scripts/deck_director.py check direction.json --pass-1
     ```
   - **Validate Pass 2 (Full Screenplay & Speech Weave):**
     ```powershell
     python scripts/deck_director.py check direction.json
     ```
   - **Compile to Forge deck and Director plan (Speaker notes auto-compiled):**
     ```powershell
     python scripts/deck_director.py compile direction.json -o deck.json --director director.json
     ```

6. **Build and measure.**
   ```powershell
   python scripts/slide_forge.py build deck.json -o deck.pptx --plan director.json
   python scripts/design_critic.py deck.pptx
   python scripts/deck_director.py ledger deck.pptx --direction direction.json
   ```

7. **Look.** Render and ask four questions, in this order:
   1. Does every pause slide read with no click? (section, quote, statement,
      closing)
   2. Is the thing the beat is about on screen before the words about it?
   3. Does each click change the argument, or only add a bullet?
   4. Does the deck move like one grammar — six figures, reused — or like a
      sampler of effects?

   Fix the direction file and rebuild. Do not fix the PPTX.

8. **Deliver** the `.pptx`, `direction.json`, the compiled `deck.json` /
   `director.json`, the ledger, and an honest rung (`$ROOT/docs/VERIFICATION.md`).

## Five hard narrative laws (validator codes)

| Code | Law | Violation check |
|---|---|---|
| `NAR-CODA-TRAP` | Anti-late evidence | `state_after[k]` has no visual delta (empty click), or `t0_says` > 35 words without a visual event |
| `NAR-KARAOKE` | Anti-redundancy | Unigram + bigram vocabulary overlap between on-slide text and spoken line > 45 % |
| `NAR-UNANCHORED` | Spatial grounding | A click whose `post_click_says` does not reference any object in `target_refs` |
| `NAR-COLLISION` | Cognitive pacing | Cinematic motion (`assemble`, `drill`, or ≥ 3 movers) without a pre-click `lead_in` |
| `DEN-ACTIVE-VIEW` | Active clutter cap | Words in currently active (visible − dimmed − exited) objects > 45; a slide > 55 words with ≥ 3 clicks must contain `dim` or `exit` |

## Narrative Critic in `design_critic.py` (6th Dimension)

`scripts/design_critic.py` measures narrative technique on the native `.pptx` (both `p:timing` and `notesSlide` XML):

| Code | Dimension | Requirement |
|---|---|---|
| `NAR-BASE-STATE` | `narrative` | Slide must not open blank at t=0; must have >= 1 visual anchor or title. |
| `DEN-ACTIVE-WORDS` | `narrative` | Active on-screen words during any click state must stay <= 45 words. |
| `NAR-LIFECYCLE` | `narrative` | Slides with multi-click content must include >= 1 object lifecycle transition (dim or exit). Purely additive clutter fails. |
| `NAR-ALIGN` | `narrative` | Speaker notes must contain choreographed cues ([T=0] and [CLICK]) precisely matching slide click groups. |

## State gate (T069, experimental)

`deck_director.py check` validates the **plan**. It cannot see the built deck's
`t=0` or click sequence. Run the state critic on the file:

```powershell
python scripts/deck_state_critic.py deck.pptx
```

It fails a deck when a slide opens with no readable claim, a title enters on a
click, a ring/disc/caption is visible before its picture, a picture first
appears on the last click or after the last text click, a `!!` Morph object also
has an entrance, a Morph has no shared `!!` pair, or a slide has more than six
click groups. It warns when the deck only adds (no dim/exit lifecycle) or a
slide exceeds four clicks. Exit code 1 on a fail. The script is experimental;
its rules are the T066/T069 evidence, not product canon.

## Job and figure table

| job | audience move | base state must carry | clicks | figure | never |
|---|---|---|---|---|---|
| `hook` | stop and look | the thing itself, or nothing if the reveal *is* the hook | 0–1 | `arrive` | a word-only title card |
| `name` | attach a word to a thing | the thing | 1 | `join` | the word before the thing |
| `define` | accept a definition | the term or its object | 1–3 | `build` | a definition before its subject |
| `contrast` | see A and B at once | nothing, or both grounds | 1–2 | `both` | A and B on separate clicks |
| `prove` | believe a number | axes, unit, context | 1–3 | `arrive` | the takeaway before the data |
| `mechanism` | understand how it works | the outline or the whole | 2–4 | `assemble` / `drill` | a tour with no whole first |
| `turn` | change their mind | one sentence or one number | 1 | `clear` | chrome, cards, a second idea |
| `land` | remember the point | everything discussed | 0–1 | `arrive` | a new object |
| `ask` | do something | the ask | 0–1 | `arrive` | motion at all |

Six figures: `arrive`, `join`, `build`, `both`, `assemble`, `clear`. They map to
Motion Director recipes (`reveal`, `stagger-reveal`/`text-build`, `swap`,
`assemble` + `cycle`/`travel`/`spotlight`, `dim`/`exit`, `ken-burns` for a
carrier that must live without a click). Use the six; do not add a seventh
because a slide feels flat — a flat slide is a beat with no job.

**A tour is not a default.** Only `mechanism` beats walk parts one by one. A
five-part loop is not five clicks unless the script names each part.

## Base state policy

`poster_first` (default for editorial and cinematic presets): every content slide
carries at least one whole idea at `t=0`. The first click adds the *next* idea,
never the only idea. This is what makes a deck readable while the presenter
arrives, thinks, or is interrupted.

`build_first` (allowed for minimal and data presets): a slide may open on a frame
— axes, an outline, a question — and build. The frame must still be legible;
"blank until click 1" is not a frame. Pause layouts (section, statement, quote,
closing) are always `poster_first`, whatever the deck says.

**Corollary:** a title is part of the base plate, not an entrance. Titles move by
Morph or not at all. Never animate a title inside a slide.

## Image choreography

An image without a role is decoration — and decoration is what the T066 review
rejected. These rules decide **what an image is doing, when it appears, and in
what order**.

### Role chooses timing

| Role | Job | Timing |
|---|---|---|
| **Identity anchor** | tells the room who/what the slide is about before the first word | visible at `t=0`, no entrance |
| **Evidence** | proves or instantiates the claim being spoken | enters **on its naming beat** |
| **Scene** | sets period, place or mood; carries no claim | visible before the first sentence |
| **Transition** | carries the eye between slides (Morph) | present at the end of slide N and the start of N+1 |

- **One role per image, written down** in the beat sheet. If you cannot name the
  role in one word, the image has no job.
- **One image is one block.** The picture plus everything that exists only
  because of it — disc, ring, panel, caption, credit — is authored and animated
  as one unit. Never leave a frame, disc or caption on screen without its
  picture. Test: `empty_frame == 0`.
- **No image on the last click** unless the image *is* the conclusion. Test:
  delete the last click; if the slide still reads, the image was a coda. Coda
  images are forbidden.
- **The order of pictures is the order of the claim.** If the claim is a
  sequence, reveal in sequence order (1848 → 1867 → 1917), not cast order. If
  the slide ranks, reveal in rank order.
- **Grouping mirrors the sentence.** "Marx – Lenin" is one compound name → one
  group. "Marx and Engels laid the foundation; Lenin developed it" is 2 + 1 →
  a pair beat and a single beat.
- **One new image unit per click.** A group that is one referent may enter with
  a 60–150 ms stagger; two unrelated images in one click read as a contact
  sheet.
- **Same role, same size.** A portrait is 24–40 % of slide height in a group,
  40–60 % when it is the slide's subject. Above 60 % only when the image *is*
  the slide.
- **Crop for the face, not for the box.** Eyes in the upper third; cut at
  mid-chest; keep ≥ 0.25 in from the slide edge; a clean bust may overflow its
  disc at the bottom.
- **The last image beat must not be later than the last text beat**
  (`image_lag == 0` on every slide).
- **Every image is treated before it is embedded:** crop to the role box,
  optional `rembg` cut-out, duotone, grade, mask; record
  `{source, licence, treatment, box, sha256}` in a manifest. A raw photo in a
  slide is a defect, not a shortcut. In editorial presets the duotone stops are
  the style's `text` and `bg` — a rule, not a pair of hex values you like.
- An image declared `evidence` must be captioned or sourced; an image declared
  `atmosphere` may never be the only content of a `prove` beat.
- **Cut-outs are legal.** A transparent-background portrait is not the defect;
  a cut-out with no ground, no naming beat or no size discipline is.

## Style

A style says how things look; it cannot say when a thing must be on screen. This
skill selects a style and adds three policies (`base_state`, `image_role`, image
treatment) — it does not define a second style schema.

- **Preset ids** come from `VisualStyle/1`
  (`experiments/T067-20261104-opencode-visual-style/inputs/visual_style.py`,
  research-grade): `editorial-crimson`, `liquid-glass`, `clay-cartoon`,
  `swiss-minimal`, `maximalist-collage`. Resolve tokens with
  `visual_style.py tokens <preset>` and pass them to Forge; never type a hex,
  radius or duration yourself.
- **If `VisualStyle/1` is not available**, `style.preset` takes a Forge theme
  (`paper`, `office:Ion`, `{"seed": "#RRGGBB"}`) and the deck is reported as
  `style: forge_theme` — no style checks, no claims.
- A style is material + geometry + depth + texture + type + image treatment +
  motion language + density, not only palette and fonts. If a preset cannot
  specify those, it is a theme, not a style.

```json
"style": {
  "preset": "editorial-crimson",
  "base_state": "poster_first",
  "image_role": "evidence"
}
```

| field | values | decides |
|---|---|---|
| `base_state` | `poster_first` / `build_first` | whether a content slide must carry a whole idea at `t=0`, or may open on a legible frame |
| `image_role` | `evidence` / `atmosphere` / `punctuation` | what a picture is for: caption duty, whether it may be the only content of a `prove` beat, whether it must survive a click |

- **Numbers are not yours.** Margins, radii, gutters, type scale, durations,
  stagger and rhythm come from `knowledge/design_system.json` and the Office kit;
  the style preset is validated against the same bands.
- **The job → figure vocabulary is direction, not style.** A preset may tune how
  fast a figure runs; it may not decide that a contrast is shown as two states at
  once.

## Contracts

`direction.json` — errors are codes; repair the direction, not the deck.

| code | check |
|---|---|
| `BRIEF-MISSING` / `BRIEF-SPINE` | brief present; `one_sentence` present, ≤ 20 words |
| `BRIEF-REGISTER` | register in the four |
| `STYLE-PRESET` | preset present |
| `BEATS-EMPTY` / `SHOTS-EMPTY` | both non-empty |
| `BEAT-JOB` / `BEAT-FIGURE` | job and figure in their tables |
| `SCRIPT-CLAIM-LONG` | every beat `claim` ≤ 25 words |
| `BEAT-SHOT-UNMAPPED` | every beat has a shot |
| `BEAT-CARRIER` | `carrier` names an object in the beat's shot |
| `NAR-T0-SAYS-MISSING` | every beat has a `t0_says` |
| `SHOT-BASE` | `base_state` names existing objects; non-empty except `job: hook` |
| `OBJECT-ENTER-ONCE` / `OBJECT-LIFECYCLE-VALID` | each object enters once; `dim`/`exit` only after entry |
| `CLICK-UNMAPPED` | every beat click appears in `state_after`, in order |
| `NAR-CODA-TRAP` | no empty click; `t0_says` ≤ 35 words per click beat |
| `NAR-KARAOKE` | text/speech overlap ≤ 45 % |
| `NAR-UNANCHORED` | `post_click_says` references a target |
| `NAR-COLLISION` | cinematic figure or ≥ 3 movers has a `lead_in` |
| `DEN-ACTIVE-VIEW` | active words ≤ 45 |

## Compile mapping

| `direction.json` | becomes | in |
|---|---|---|
| `shots[].layout` + objects by `role` + `text` | slide fields (`title`, `bullets`, `steps`, `chart`, …) | `deck.json` |
| `objects[role=anchor].asset` | `image` field (`{"file": …}` or `{"search": …}`) | `deck.json` |
| `shots[].base_state` | `base_state: ["Title", "Hero picture", …]` | `deck.json` |
| `beats[].clicks[].state` | `click_beats[].purpose` | `director.json` |
| `state_after[click]` | the click beat's `targets` | `director.json` |
| `beats[].job` + figure | `beats[].operation` / recipe | `director.json` |
| spoken line | `script.md` for `motion_script.py --script`, and `click_beats[].narration` | both |

Object names must match what Forge writes (`Title`, `Hero picture`, `Card 1`,
`Step 2`, …). Run `motion_director.py inspect deck.pptx` after the first build
and correct the mapping; do not guess names.

## Ledger (what you report)

| fact | measure |
|---|---|
| clicks per slide | from the built deck's click groups |
| slides whose base state has no text or picture | count |
| carrier presence | clicks between the carrier's first appearance and slide end |
| pictures on the last click | count |
| empty frames / image lag | count / max clicks |
| distinct jobs / figures | counts |
| dead clicks | clicks that add nothing the beat's `state` promised |
| critic | `design_critic.py` **with** `--direction` once it exists |

## Never

- Never invent data, quotes or citations; label illustrative figures.
- Never exceed six clicks on a slide; three is usually a talk, six is a machine gun.
- Never animate a title inside a slide; titles move by Morph or not at all.
- Never let a beat exist for a layout you like. Choose the layout from the roles.
- Never write a purpose like "reveal the card" — that is the effect talking.
  Write what the audience now knows.
- Never reveal an image after the sentence that names it.
- Never deliver a deck whose `direction.json` you did not read back after the
  build. The build is the measurement.

## Evidence boundaries

A direction file is rung 0: a plan, not a deck. A built and rendered deck is rung
4–5 (PowerPoint opens/renders it; `CreateVideo` plays the clicks). Critic scores
are measurements of what they measure, never playback. Rung 6 — a human watching
every slide and click in the room — has not been reached by this lab, and this
skill cannot reach it.

`VisualStyle/1` is research-grade: five presets were built as specimens, but
liquid glass is an approximation (DrawingML has no backdrop blur), and clay rims
are baked into PNGs. Do not claim native fidelity you have not measured.

## Not this skill

- An existing deck: `pptx-motion-director` (preserve by default).
- A one-slide fix or a re-theme: `slide-forge` directly.
- A document or a sheet: the `document-craft` / `sheet-craft` skills.
