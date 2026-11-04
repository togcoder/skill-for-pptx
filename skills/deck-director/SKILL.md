---
name: deck-director
description: Direct a new deck before it is laid out — turn a topic, outline, document or chapter into a spoken screenplay with Two-Pass Choreography (State Machine & Stage Inventory first, Natural Voice Weave second), a beat sheet of argument moves (hook, name, define, contrast, prove, mechanism, turn, land, ask), a shot list fixing base_state at t=0 and lifecycle state_after (enter, dim, highlight, exit, zoom) for every click — then compile direction.json into deck.json and director.json for slide-forge and pptx-motion-director. Enforces 5 hard narrative laws (anti-Coda trap, anti-Karaoke redundancy, unanchored monologue prevention, motion collision avoidance, active view word cap <= 45).
---

# Deck Director

> **Status: v0.2 (T068).** Canonical two-pass screenplay compiler and validator
> implemented in `scripts/deck_director.py`. Wired into `slide_forge.py build --plan`.

You are the deck's director, not its typesetter. You decide **what the audience
must believe, see and feel at each moment** — then you write that down in files
that the builders obey. You never place a coordinate and never pick a raw animation
effect; if you are choosing a wipe, you are doing someone else's job and the deck
will show it.

`ROOT=<this skill dir>/../..`.

## Why this skill exists

Slide Forge compiles a *slide*. The Motion Director times a *click*. Neither owns
the thing between them: the argument, the beat, and what is in frame when the
presenter is still talking. A deck built without that layer is layout first and
motion last — the pictures arrive after the point they were meant to make (Coda Trap),
slides open on blank white screens at $t=0$, text accumulates into unreadable 80-word
clutter (`lifecycles: 0`), and the presenter reads word-for-word what is already on
screen (Karaoke Effect).

That is not a taste problem; it is a missing architectural artifact. Deck Director
provides that artifact: **Two-Pass Choreography** that locks the visual state machine
before weaving spoken dialogue.

## Two-Pass Loop

### Pass 1: Architecture & State Machine (Stage Inventory, Beats & Shots)

0. **Brief.** Five fields:
   - `audience`, `minutes`, `room`;
   - `decision` — what the audience does after;
   - `one_sentence` — the repeatable spine ($\le 20$ words);
   - `register` — `editorial_teaching | technical | executive | editorial_culture`.
   **Gate:** if you cannot write `one_sentence` in one line, stop and ask.

1. **Style.** Choose one preset (§Style) and record: `base_state` (`poster_first | build_first`)
   and `image_role` (`evidence | atmosphere | punctuation`).

2. **Beats (9 Jobs).** One beat per cognitive shift in the audience's mind:
   `job`, `claim` ($\le 25$ words), `carrier` (the object id that embodies it),
   `attention` (initial focus), and `figure` (`arrive | join | build | both | assemble | clear | drill`).
   **Gate:** a beat whose `job` is `contrast` must show two states at once; a beat
   whose `job` is `mechanism` must show the whole before walking the parts.

3. **Shots & Stage Inventory.**
   - Declare all `objects` with `id`, `role`, and optional `text`, `asset`, or `zoom_spec`.
   - Declare `base_state` **first** — objects on screen at $t=0$ (non-empty except `job: hook`).
   - Declare `state_after` for each click with **full lifecycle control**:
     `enter` (new objects), `dim` (de-emphasized objects), `highlight` (focused objects),
     `exit` (removed objects), and optional `action`.
   **Gate:** Every object enters at most once (`OBJECT-ENTER-ONCE`). Objects in `dim`/`exit`
   must have previously entered (`OBJECT-LIFECYCLE-VALID`).

### Pass 2: Natural Voice Weave (Split-Sentence Bridging & Deictic Anchoring)

4. **Weave Spoken Screenplay:**
   - **`t0_says`:** The opening spoken sentence delivered while audience looks at `base_state`
     at $t=0$ (before the first click). Never leave $t=0$ without voice or with a blank slide.
   - **`clicks[].lead_in`:** Pre-click cue sentence providing momentum before the button press.
   - **`clicks[].post_click_says`:** Spoken explanation delivered after the click lands,
     explaining the new visual state and referencing the target object.
   - **Split-Sentence Bridging:** Place the `[click]` at the pivot between cause and effect:
     *"In small clusters, this pipeline runs smoothly... but the moment load scales 10x — `[click]` — this central database node becomes an immediate single point of failure."*
   - **Implicit Deictic Anchoring:** Never say *"As you see on the left"*. Say *"When we strip this outer caching layer..."* matching the visual transition.

5. **Validate & Compile:**
   ```powershell
   python scripts/deck_director.py check direction.json
   python scripts/deck_director.py compile direction.json -o deck.json --director director.json
   ```

6. **Build & Measure:**
   ```powershell
   python scripts/slide_forge.py build deck.json -o deck.pptx --plan director.json
   python scripts/deck_director.py ledger deck.pptx --direction direction.json
   ```

## Five Hard Narrative Laws (Validator Codes)

| Code | Law | Violation Check |
|---|---|---|
| `NAR-CODA-TRAP` | Anti-Late Evidence | `state_after[k]` has no changes (empty click), or `t0_says` > 35 words without visual event |
| `NAR-KARAOKE` | Anti-Redundancy | Vocabulary overlap (unigram + bigram) between on-slide text and spoken lines > 45% |
| `NAR-UNANCHORED` | Spatial Grounding | A click beat whose `post_click_says` does not reference any object in `target_refs` |
| `NAR-COLLISION` | Cognitive Pacing | Cinematic motion (`assemble`, `drill`, or $\ge 3$ movers) without pre-click `lead_in` |
| `DEN-ACTIVE-VIEW` | Active Clutter Cap | Total words of currently active (visible - dimmed - exited) objects > 45 words. Slides with > 55 words and $\ge 3$ clicks must contain `dim` or `exit` |

## Job & Figure Table

| job | cognitive intent | base state | clicks | figure | rule |
|---|---|---|---|---|---|
| `hook` | stop and look | image/provocation or empty | 0–1 | `arrive` | never word-only card |
| `name` | attach label to entity | the entity | 1 | `join` | entity appears before name |
| `define` | unpack meaning into parts | entity + prompt | 1–3 | `build` | definitions stay under active cap |
| `contrast` | clash two realities | reality A | 1–2 | `both` | both states visible side-by-side |
| `prove` | substantiate with data | context / setup | 1–2 | `arrive` | evidence appears ON naming beat |
| `mechanism` | walk causality or drill | whole system | 2–4 | `assemble` / `drill` | dim previous steps as next lights up |
| `turn` | pivot argument | status quo | 1 | `clear` | old assumption dimmed/exited |
| `land` | deliver conclusion | core thesis | 0–1 | `arrive` | no new arguments introduced |
| `ask` | prompt next action | call to action | 0–1 | `arrive` | single unambiguous next step |

## Non-Linear & Interactive Zoom Integration (`drill`)

When `figure` is `drill`:
- The object role is `"zoom"`.
- It defines `zoom_spec`: `{"kind": "slide"|"section"|"summary", "slides": [N], "returnToZoom": true}`.
- DeckCraft 0.15.0 compiles this natively via `insert.zoom`.
- Verification confirms hyperlinks via `deckcraft-cli run --cmd slide.actions`.
