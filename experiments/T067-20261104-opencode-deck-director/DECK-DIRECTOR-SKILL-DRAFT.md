# T067 — Deck direction and visual style: proposed layer, contracts, diff list

- **Status:** draft for review. No code merged, no product path touched.
- **Companion skill draft:** `skills/deck-director/SKILL.md`.
- **Audit that motivates it:** `skill-audit.md` (same folder).
- **One sentence:** today the lab can lay out a slide and time a click; it has no
  artifact that says *what the audience must believe, see and feel at each
  moment*. This layer is that artifact, and it is written **before** layout.

## 1. The pipeline, inverted

```
brief ──► SCRIPT ──► BEAT SHEET ──► SHOT LIST ──► MOTION PLAN ──► BUILD ──► CRITIC
         (speech)    (argument)      (frames)      (timing)                  (with direction)
```

Today:

```
spec ──► layout+art ──► (read the file back) ──► effects ──► QA
```

Three properties of the new order matter more than the boxes:

1. **Each stage has a file.** A decision that is not in a file did not happen.
2. **Each stage constrains the next.** The beat sheet decides which objects exist;
   the shot list decides what is visible at t=0; the motion plan may only animate
   the difference between two declared states. No stage may add content that the
   previous stage did not ask for.
3. **The critic reads the direction file as well as the deck.** Intent becomes
   checkable, so "no *gu*" becomes a number someone can fail.

Why a new skill rather than two more fields in Forge: the decision "the portrait
must be on screen before the name" cannot be expressed in a layout spec, because
the layout spec has no concept of *before*. It needs a layer that owns time and
argument, and hands finished frames to the layout engine.

## 2. The four artifacts

All four live in the task folder, UTF-8, JSON except the script. `direction.json`
is the umbrella file: it holds `brief`, `style`, `script`, `beats`, `shots` and is
the only file the compiler reads.

### 2.1 Brief (5 fields, reuses T037)

T037's `intent_decoder.py` + `lab/schemas/intent_brief.schema.json` already define
audience, cognitive budget, viewing context and design canon — and are referenced
by no skill. Do not duplicate them: `deck-director` calls `intent_decoder.decode()`
when present and stores the result under `brief.intent`, adding only the two
things IntentBrief lacks:

```json
"brief": {
  "intent_id": "INT-20261104-001",
  "audience": "sinh viên năm 1, giảng đường 200 chỗ",
  "minutes": 18,
  "decision": "hiểu vì sao chương 1 đứng trước mọi chương sau",
  "one_sentence": "Triết học không phải môn phụ; nó là khung mà mọi khoa học khác mặc định.",
  "register": "editorial_teaching"
}
```

`one_sentence` is the deck's spine. Every beat must serve it or be cut; a beat
that cannot be tied to it is `NAR-OFF-SPINE`.

### 2.2 Script

Reuse `motion_script.py`'s existing Markdown format — `## Slide N`, `[click]` cues,
`[nhấp]`/`[bấm]`/`>>`. No second syntax. One addition: each scene opens with a
`claim:` line, because narration without a claim is prose.

```markdown
## Slide 2 — Triết học là gì?
claim: Triết học là hệ thống tri thức chung nhất, và nó có trước mọi khoa học cụ thể.
[click] Ai cũng đã từng triết học mà không gọi tên nó.
[click] Giáo trình định nghĩa nó bằng ba tầng: tự nhiên, xã hội, tư duy.
```

`scene.claim` is what the audience must be able to repeat; `scene.narration` is
what the presenter says. The compiler refuses a scene whose claim is longer than
25 words (it is a thesis, not a paragraph) — `SCRIPT-CLAIM-LONG`.

### 2.3 Beat sheet

One beat = one change in the audience's head. This is the layer T066 lacked.

```json
{
  "id": "b2",
  "scene": "s2",
  "job": "define",
  "claim": "Triết học là hệ thống tri thức chung nhất.",
  "turn": {"from": "một môn học phải học", "to": "cái khung mọi khoa học dựa vào"},
  "evidence": ["Giáo trình tr. 12"],
  "carrier": "art:plato",
  "attention": "mặt tượng trước, định nghĩa sau",
  "clicks": [
    {"id": "b2.1", "state": "Bức tượng và câu hỏi, chưa có định nghĩa", "says": "Ai cũng đã từng triết học mà không biết."},
    {"id": "b2.2", "state": "Định nghĩa hiện thành ba tầng", "says": "Giáo trình định nghĩa nó bằng ba tầng."}
  ],
  "seconds": 90
}
```

Rules the compiler enforces:

| Rule | Meaning | Error code |
|---|---|---|
| `job` ∈ 9 values (§3) | the beat has a rhetorical job | `BEAT-JOB` |
| `claim` ≤ 25 words, one sentence | it is a thesis | `BEAT-CLAIM` |
| `carrier` names an object in its shot | the meaning has a body | `BEAT-CARRIER` |
| `clicks` 0..6, ids unique | presenter rhythm | `BEAT-CLICKS` |
| every click has a `state` that names what is new | a click is a stable state | `BEAT-STATE` |
| `seconds` present | the deck has a duration | `BEAT-TIME` |

A beat with `clicks: []` is legal and means "this idea is not revealed; it is
simply there while the presenter speaks". That is how pause slides stop being
empty.

### 2.4 Shot list

One shot = one frame. It is the join between argument and layout, and it is where
the owner's S2 is fixed: **the shot declares the base state first.**

```json
{
  "id": "sh2",
  "beat": "b2",
  "layout": "asymmetric",
  "objects": [
    {"id": "art:plato",   "role": "anchor",   "kind": "picture",
     "asset": {"file": "inputs/assets/plato.png", "treatment": "cutout_duotone", "crop": "circle"}},
    {"id": "text:q",      "role": "title",    "kind": "text", "text": "Triết học là gì?"},
    {"id": "text:def",    "role": "evidence", "kind": "text", "text": "Hệ thống tri thức chung nhất về tự nhiên, xã hội và tư duy."},
    {"id": "text:src",    "role": "source",   "kind": "text", "text": "Giáo trình, tr. 12"}
  ],
  "base_state": ["art:plato", "text:q"],
  "state_after": {"b2.1": [], "b2.2": ["text:def", "text:src"]},
  "notes": "Tượng ở lại suốt beat; định nghĩa không được che mặt."
}
```

Contract:

- `base_state` ∪ all `state_after` values = every object, exactly once
  (`OBJECT-ORPHAN`, `OBJECT-TWICE`);
- `state_after` keys are the beat's click ids, in order (`CLICK-UNMAPPED`);
- `role` ∈ {`kicker`,`title`,`statement`,`evidence`,`number`,`label`,`anchor`,
  `support`,`source`,`quote`,`author`,`ask`,`chrome`} — layout is chosen from the
  role set, not the other way round;
- `asset.treatment` comes from the style preset (§4), not from the author's mood;
- a shot may declare `layout` explicitly; otherwise the compiler picks the layout
  whose required roles match the object roles (`LAYOUT-ROLE`).

This is the single most important inversion in the proposal. Forge today decides
the layout first, places the picture in whatever slot is left, and the Director
then has no choice but to reveal it late. Here the shot says "the bust is in the
base state", so the layout must be built around a picture that is already there,
and the Director must *not* animate it.

### 2.5 Compiled outputs (what the existing skills already understand)

```
direction.json ──deck_director.py compile──► deck.json      (slide-forge spec)
                                           └► director.json  (motion-director plan)
```

- **`deck.json`** — today's Forge spec plus two fields: `beat` on each slide and
  `base_state` (object names) on each slide. `style` is passed through as a preset
  name. Nothing else changes, so `slide_forge.py schema` stays valid.
- **`director.json`** — today's Director plan v0.7 plus, on each beat: `job`
  (from the beat), `figure` (from §3), `narration` (from the script), `carrier`.
  `click_beats[].purpose` is copied from `beat.clicks[].state` — a sentence about
  the audience, not about the effect. `stable_state` is redefined as *what the room
  reads*, not *what is visible*.

### 2.6 Where it plugs in — the code seam that already exists

`slide_forge.build()` already ends with `md.apply(static, plan, out, force=True)`.
`apply` accepts a plan. Forge simply never offers one:

```python
# scripts/slide_forge.py:918
def build(spec, out, work=None, plan=None):        # <- one new parameter
    ...
    plan = plan or md.draft(model, goal=spec.get("title",""), ...)
    report = md.apply(static, plan, out, force=True)
```

That is the whole wiring for "Forge can be directed". The rest is the compiler
that turns a shot list into `deck.json` + `director.json`, and one Builder rule:
**objects listed in `base_state` get no entrance effect** (the plan simply does
not target them; the Director needs no new capability).

CLI surface for the next task:

```
deck_director.py check    direction.json                  # contracts + jobs + roles
deck_director.py compile  direction.json -o build/        # deck.json + director.json
deck_director.py ledger   OUT.pptx --direction direction.json   # narrative checks
```

## 3. The job → figure table (this is the "*gu*")

Nine jobs, six motion figures. A job is *why* the audience changes; a figure is
*how* the change is shown. The vocabulary is small on purpose: a deck should feel
like one grammar, and grammar is repetition with meaning.

| job | audience move | base state must carry | typical clicks | figure | forbidden |
|---|---|---|---|---|---|
| `hook` | stop and look | the thing itself (image, number, object) | 0–1 | `arrive` | a title card with no object |
| `name` | attach a word to a thing | the thing | 1 | `join` | the word before the thing |
| `define` | accept a definition | the term or its object | 1–2 | `build` | a definition revealed before its subject |
| `contrast` | see A and B at once | nothing, or both grounds | 1–2 | `both` | two separate clicks for A and B |
| `prove` | believe a number | axes / context / unit | 1–3 | `build` | the takeaway before the data |
| `mechanism` | understand how it works | the outline or the whole | 2–5 | `assemble` | a tour of parts with no whole first |
| `turn` | change their mind | one sentence or one number | 0–1 | `clear` | chrome, cards, a second idea |
| `land` | remember the point | everything discussed | 1 | `clear` | a new object introduced here |
| `ask` | do something | the ask | 0 | `arrive` | motion at all |

Figure definitions (all already implementable with existing Director recipes):

- `arrive` — one object enters; nothing else moves. (`reveal`, one target)
- `join` — a label attaches to an object already on screen, `with-previous`.
- `build` — ordered accumulation of one class of object; stagger 60–150 ms.
- `both` — two groups enter together, or `swap` places.
- `assemble` — parts converge (`choreography: assemble`), then the system runs
  (`cycle`/`travel`/`spotlight`) only if the job is `mechanism`.
- `clear` — `dim` others, one object stays (`land`), or full-frame statement with
  chrome off (`turn`).

Three consequences, each checkable:

1. **A cycle no longer earns a tour by existing.** Only `mechanism` beats may
   walk the parts. (Today: any ≤5-item cycle gets 5 extra clicks —
   `motion_director.py:664`.)
2. **A contrast may not be built in two clicks.** If A and B are in separate
   clicks, the audience cannot compare; the first is gone from attention before
   the second arrives (Mayer's temporal contiguity). `both` is required.
3. **A picture that carries the beat must be in the base state or survive one
   click.** This is the rule the owner's S2 needs; see `NAR-PRESENCE` (§5).

## 4. The visual style layer

**This section defers to a sibling stream.** The same task (T067) has a second
stream building `VisualStyle/1` — `experiments/T067-20261104-opencode-visual-style/inputs/visual_style.py`
— whose schema is already richer than what I would invent here: roles for colour,
type, geometry, material, depth, texture, image, motion and density; five presets
(`editorial-crimson`, `liquid-glass`, `clay-cartoon`, `swiss-minimal`,
`maximalist-collage`); a resolver that turns a preset into build tokens; and a
`check` command that audits a `.pptx` against its declared preset. That is the
implementation. Building a second preset list in this document would reproduce the
exact defect the audit names (F9: two competing style schemas), so this layer adds
only the **policies a style does not own** and points at theirs for everything
else.

### 4.1 What Deck Director takes from the style

`direction.json` carries `style: {"preset": "<VisualStyle id>", "overrides": {...}}`.
The compiler asks `visual_style.tokens(preset)` for resolved tokens and passes them
to Forge; it never reads a hex value directly. If `VisualStyle/1` has not landed,
the same field holds a Forge theme name (`paper`, `office:Ion`, `{"seed": ...}`)
and the deck gets no style checks — reported, not hidden.

### 4.2 The two policies Deck Director adds

A style says how things look; it cannot say *when a thing must be on screen*. Two
fields, both policy, no numbers:

```json
"style": {
  "preset": "editorial-crimson",
  "base_state": "poster_first",
  "image_role": "evidence"
}
```

| field | values | what it decides |
|---|---|---|
| `base_state` | `poster_first` / `build_first` | whether a content slide must carry a whole idea at t=0, or may open on a legible frame and build. Pause layouts (section, statement, quote, closing) are always `poster_first`. |
| `image_role` | `evidence` / `atmosphere` / `punctuation` | what a picture is *for*, which decides caption duty, whether it may be the only content on a `prove` beat, and whether it must survive a click (`NAR-PRESENCE`). |

These are the two decisions T066 got wrong and no palette could have fixed.

### 4.3 Image treatment

The style's `image` role should own the treatment pipeline, and T066's recipe is
the reference implementation for the editorial presets: `rembg` cut-out, two-stop
duotone whose stops are the style's `text` and `bg`, circular or silhouette mask,
crop to the object's box. Per `AGENTS.md` no raw asset is embedded, and every
treated asset carries `{source, licence, treatment, box, sha256}` in a manifest.
`forge_assets.py` acquires, `photo_vector.py` illustrates, and treatment belongs
with the style system, not with the deck compiler. Until that exists the skill
instructs the agent to run the steps and record the manifest — which is what T066
did by hand.

### 4.4 What the direction layer keeps for itself

The **job → figure vocabulary** (§3) is not a style token. A style may tune rates
and easing; it may not decide that a contrast is shown as two states at once — that
is an argument decision. The split is:

- style → `how it looks and how fast`;
- direction → `what must be true at each moment`.

### 4.5 Discipline

Every number still comes from `knowledge/design_system.json` by reference. The
style system validates its presets against the same bands (`VisualStyle/1` reads
`enter_ms`, `move_ms`, `stagger_ms`, `body_pt`, `words`, `sizes` from it). The only
new numeric value in the whole proposal is `narrative.presence_min_clicks = 1`
(§5), and it is flagged for review.


## 5. Critic additions

New dimension `narrative`; all rules read the **direction file** when supplied, and
degrade to deck-only heuristics otherwise. Measurements use the timing tree
already parsed by `design_critic.slide_timing()`; no new renderer.

| rule | dimension | measurement | band / expectation | fixes |
|---|---|---|---|---|
| `NAR-BASE-STATE` | narrative | content objects visible at t=0 | ≥1; a `hook` beat with an empty base is a note, not a warn | shot `base_state` |
| `NAR-PRESENCE` | narrative | clicks between the carrier's first appearance and slide end | ≥1, or in base state | beat `carrier`, shot order |
| `NAR-ORDER` | narrative | first click of `evidence` vs first click of `statement` | evidence ≤ statement | beat `clicks` |
| `NAR-JOB-MIX` | narrative | distinct jobs in a ≥5-slide deck | ≥3, and ≥1 of `turn`/`land` | beats |
| `NAR-ORPHAN` | narrative | slides with no shot / shots with no slide | 0 | compiler |
| `NAR-OFF-SPINE` | narrative | beats whose claim does not share a term with `brief.one_sentence` | 0 by default, override allowed with reason | beats |
| `MOT-LIFECYCLE` | rhythm | objects with ≥2 effects (already computed) | ≥1 in a ≥6-slide deck | plan |
| `MOT-FIGURE-REPEAT` | motion | share of slides whose (role→preset) signature is identical | ≤0.6 | plan |
| `DEN-VIEW` | design | max words in any single stable state | same band as density (≤45) | beats/shots |
| `TYP-TITLE-ID` | coherence | decks where no title is identified | 0 | title detection |
| `PLAN-PURPOSE` | narrative | click beats with a purpose; share of the most repeated purpose | 100 %, template share <0.5 | plan |
| `PLAN-DRIFT` | technique | declared clicks vs actual click groups | equal | compiler |

Two structural changes to the critic, not just new rules:

1. **Title identity.** A title is a placeholder **or** a declared `role:"title"` **or**
   a text box named `title`/`h1` **or** the largest text at ≥1.5× body. This is a
   bug fix: `design_critic.py:564,660` currently recognise placeholders only, so
   Forge and T066 decks escape `MOT-TITLE` and `TYP-RATIO`.
2. **Score by rule, then by dimension.** Average *rules* (one grade per rule per
   deck), not the 153 per-effect checks. `TYP-SIZES` and `MOT-DURATION` should not
   have the same weight in a dimension score. Report both counts
   (`checks`, `rules`) so the inflation stays visible.

Severity changes: `MOT-TITLE` from note → warn; `DEN-WORDS` stays as is (changing
the band needs evidence), but `DEN-VIEW` is added with the same band so a slide
that never shows more than its limit passes while a wall does not.

## 6. Concrete diff list

### 6.1 `skills/slide-forge/SKILL.md`

**Remove**
- `:17-19` the "Story first" step. It is advice with no artifact, and it lets the
  agent believe the story is handled. Replace with the direction step: run
  `deck-director` and build from its `deck.json` (§2).
- `:20-22` "Choose the layout from what the content *is*" as the decision
  procedure. The table stays; it becomes a lookup keyed by beat job.
- `:122-128` the motion-style bullet list framed as a choice of taste. Keep the
  names as compatibility presets; state that the figure vocabulary comes from
  `style.motion.figures`.
- `:42-45` "Deliver ... one line per slide (layout and what moves)" → add the beat
  id and the base state, because those are the two things a reviewer needs.

**Add**
- Step 0: "Direction. If the user gave a topic, an outline or a document rather
  than a finished argument, run `deck-director` first; build from the `deck.json`
  it emits. Building a topic directly is a layout-led build: allowed, reported as
  `direction_source: "none"`, and it may not claim narrative quality."
- A `base_state` row in the slide-spec table: "objects visible at t=0; listed
  objects get no entrance effect".
- A `beat` field on each slide (traceability).
- QA codes: `BASE_STATE_EMPTY`, `CARRIER_LAST_CLICK`, `CLICK_UNMAPPED`,
  `OBJECT_ORPHAN`, `STYLE_UNKNOWN`.
- A pointer to the style presets (§4.1) and the two policies (`base_state`,
  `image_role`) that the deck spec must carry.

**Rename**
- `motion.style` → `motion.preset` in prose and schema (`style` kept as an alias,
  deprecated in the docs). It is an effect preset table, not a style.

### 6.2 `skills/pptx-motion-director/SKILL.md`

**Remove**
- `:69-70` "One-shot path when speed beats craft". Delete the framing; it
  advertises exactly the failure the owner hit. Replace with: "`auto` is for a
  deck that already exists. On a new deck, an inferred plan is a fallback and is
  labelled `script.source: inferred`; it is not a delivery."
- `:30-32` the instruction to draft a script from the deck as the normal path.
  Keep the command for legacy decks, mark it `legacy`.
- The auto-tour of any cycle (`motion_director.py:664`): a tour now requires
  `job: mechanism` or an explicit sequence cue in the notes.

**Add**
- Step 0 "Direction first": read `direction.json`; the script is the transcript
  of the beats, not a description of the slides. If absent, say so in the report.
- The job → figure table (§3) as the motion grammar.
- Beat fields `job`, `figure`, `narration`, `carrier`.
- Validator rules `PLAN-PURPOSE`, `PLAN-FIGURE`.
- A rule that every `click_beats[].purpose` must be a sentence the presenter could
  say, and no two clicks on a slide may share it.

**Rename**
- "Script first" → "Direction first; the script is its transcript". The ranking
  (script > notes > existing timing > inferred) stays, but the *fallback* is now
  labelled as a downgrade instead of silently satisfying the contract.

### 6.3 `scripts/design_critic.py`

**Remove**
- Placeholder-only title identification (`:564`, `:660`).
- Per-effect averaging as the dimension score (`:780-790`).
- `MOT-TITLE` as `note` (`:687`).

**Add**
- `critique(path, render=None, xsd=None, direction=None)`.
- The `narrative` dimension and rules in §5.
- `MOT-LIFECYCLE` (grade the `lifecycles` count it already computes, `:794-799`).
- `MOT-FIGURE-REPEAT`, `DEN-VIEW`, `TYP-TITLE-ID`.

**Change**
- Return `partial: true` when no render was supplied, and make the skill say it:
  today `slide_forge` calls `critique(out)` with no frames, so the three frame
  rules never run on any Forge build.

### 6.4 `knowledge/design_system.json` (data, needs review)

**Add**
- `narrative`: `jobs` (the nine), `figures` (six, each naming the Director recipe),
  `presence_min_clicks: 1` (**new value, needs a source or a review decision**),
  `job_mix` band.
- `style`: the two policies (`base_state`, `image_role`) and their enums. Preset
  definitions live in `VisualStyle/1` (§4), not here; no duplicated numbers.
- `rules`: one entry per new check with `generator` and `checker`, the same shape
  as the existing 20.

### 6.5 New files (next task, not this one)

- `scripts/deck_director.py` — `check`, `compile`, `ledger` (about 300 lines; it
  is a validator plus two writers, no layout and no XML).
- `scripts/image_treatment.py` — crop/mask/duotone/grade + manifest (§4.3), or the
  same step inside `VisualStyle/1` if that stream owns it.
- `lab/schemas/deck_direction.schema.json`.
- Tests: compile a two-slide direction and assert `base_state` objects have no
  entrance effect; ledger catches a carrier on the last click.

## 7. Worked example — T066 slide 1 and 2, directed

Prediction only (rung 0); the falsifier is building it.

**Slide 1, cover.** Current: 4 clicks; kicker, title, subtitle, portraits each on
their own click; the three portraits arrive at click 4 of 4 and the slide ends.
Under the layer: `job: hook`, `carrier: art:marx|engels|lenin`,
`base_state: [portraits, kicker]`, `clicks: [title, subtitle]`. Result: the faces
are the first thing on screen; title and subtitle land over them; 2 clicks instead
of 4; carrier presence 2 clicks instead of 0.

**Slide 2, "Triết học là gì?".** Current: 7 clicks, 74 words at the end, the
Plato bust on click 7. Under the layer: `job: define`, `carrier: art:plato`,
`base_state: [plato, question, source]`, `clicks: [definition, three layers]`;
the "three functions" become a second shot (`job: mechanism`) if they need their
own beat. Prediction: 7 → 3 clicks, carrier presence 0 → 3, max view words
74 → ~40.

**What the critic would say.** Before: design 2.98 / motion 4.99 / narrative
absent. After (predicted): `NAR-PRESENCE` 0 violations, `NAR-BASE-STATE` 0, clicks
51 → ~24, `MOT-FIGURE-REPEAT` passes, `PLAN-PURPOSE` 100 %. If the predicted
numbers do not appear, the layer is wrong and the report must say so.

**A parallel stream already built it.** While this document was being written, a
second T067 stream in the same task folder produced
`motion/artifacts/T066-deck-directed.pptx` (uncommitted at the time of writing).
Measured by me with the same probe:

| fact | T066 | directed rebuild | prediction |
|---|---|---|---|
| click groups | 51 | **27** | ~24 |
| slides with an empty base state | 1, 3, 5 | **none** | none |
| pictures on the last click | 4 of 4 | **0** | 0 |
| titles animated inside a slide | 9 of 10 | **0** | 0 |
| object lifecycles | 0 | **0** | not targeted |
| widest view (words) | 80 | **80** | not targeted |

So the three defects the layer targets moved, and the two it does not target did
not. That is the shape of a real effect rather than a rescore. It is also not a
triumph: a 27-click deck still has 2.7 clicks per slide, and slide 10 still asks
the room to read 80 words. The rebuild is the other stream's artifact; I did not
build or review it, and it must be reported by them.

## 8. Compatibility and migration

- **Existing decks:** `pptx-motion-director` keeps its current path. A deck the
  user already has cannot be re-authored, so the script stays `speaker-notes` or
  `inferred`, and the new checks report `NAR-*` only when a direction file is
  supplied. No regression for the 5 Forge examples.
- **Forge without direction:** builds exactly as today, plus
  `direction_source:"none"` in the verdict and a single deck-level note
  `NAR-NO-DIRECTION`. No new error.
- **`motion.style`:** accepted forever as an alias; docs call it a preset.
- **Schema version:** `direction.json` 0.1; `deck.json` stays `forge-0.2` with
  optional fields; `director.json` 0.8 (0.7 + `job`/`figure`/`narration`).

## 9. Risks and what would make this fail

1. **Ceremony.** Four files before one slide is a lot. Mitigation: the minimum
   viable path is one file (`direction.json`) with `brief.one_sentence`, three
   beats and three shots; the compiler fills the rest. If the layer cannot pay for
   itself on a 6-slide deck, it is wrong.
2. **Job theatre.** An agent can label every beat `define` and satisfy the schema.
   `NAR-JOB-MIX` and `NAR-OFF-SPINE` are the counters; neither is strong. The
   honest check is the owner's eye, rung 6.
3. **New numbers without sources.** Only `presence_min_clicks` is new, and it is
   called out. If review rejects it, use 0 and rely on `NAR-BASE-STATE` alone.
4. **Three style vocabularies.** `theme_engine.ARCHETYPES` (T043), the five
   `VisualStyle/1` presets (sibling T067 stream) and Forge's `THEMES` exist at once.
   This document defers to `VisualStyle/1` and treats Forge's themes as the
   fallback; the merge is a review decision, and until it happens no deck may claim
   more than one of them.
5. **A directed deck can still be dull.** This layer fixes order and presence, not
   taste in type or colour. The owner's "gu" is only partly mechanisable; the rest
   is the eye test this lab has not reached (rung 6).
