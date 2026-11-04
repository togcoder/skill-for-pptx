# T067 — motion audit of T066 (before) and the directed copy (after)

- **Source:** `experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx`
  (`f4478f0e…`, 2 016 432 bytes).
- **Directed copy:** `experiments/T067-20261104-opencode-deck-director/motion/artifacts/T066-deck-directed.pptx`
  (`00c34c4c…`, 2 014 494 bytes).
- **Environment:** Windows 11, PowerPoint **16.0 build 17932**, Python 3.13,
  python-pptx, lxml, Pillow, pywin32.
- **Evidence rung:** **4** for the file/COM counts, **5** for the stable-state
  renders. No human review: rung 6 is not reached.
- **Trim note (2026-11-04):** the individual before/after frames were removed to
  keep the T067 experiment under the 10 MB cap. The frames cited below are kept
  in two contact sheets: `motion/evidence-sheet.png` (five before/after
  base-state pairs) and `motion/slide4-states.png` (all click states of slide
  4). Frame filenames are retained as labels inside those sheets.

## 1. How the audit was measured

Three independent readings of the same file:

1. `experiments/T067-20261104-opencode-deck-director/inputs/measure_narrative.py`
   — base words, picture click, title animation, lifecycles.
2. `workspace/T067/audit_timing.py` — per click: effects, animated targets,
   peak simultaneous movers, static decorations, title/picture first click.
   (`workspace/` is scratch and not committed; the numbers are reproduced in
   the tables below.)
3. PowerPoint COM: `motion/com_verify.py` opens the exact file, reads
   `TimeLine.MainSequence.Count`, `SlideShowTransition.EntryEffect` and
   `Duration`; `motion/capture_states.py` drives `View.Next()` and captures the
   settled frames. `GotoClick` advanced the click index but did not repaint, so
   the captures use `View.Next()`; that matches T058's finding.

`measure_narrative.py` counts words in text objects that are visible at t=0
(objects with no entrance effect). It does not judge whether the visible text
is a title, a date or decoration; the shape-level audit does that.

## 2. Before: the 10 slides

| # | Clicks | Effects | Base words | Title first click | Picture first click | Peak animated targets | Static decoration visible at t=0 |
|---:|---:|---:|---:|---|---|---:|---|
| 1 | 4 | 10 | **0** | 2 | 4 (all three) | 4 | three empty gold rings |
| 2 | 7 | 17 | 7 | 2 | **7 (last)** | 4 | red disc, caption, thread/dot |
| 3 | 5 | 13 | **0** | 2 | — | 4 | thread/dot |
| 4 | 5 | 13 | 3 | 1 | — | 4 | kicker, **arc**, **three dots**, thread/dot |
| 5 | 6 | 18 | **0** | 2 | — | 4 | thread/dot |
| 6 | 5 | 17 | 2 | 1 | — | 4 | kicker, thread/dot |
| 7 | 5 | 18 | 5 | 1 | 2 / 3 / 4 | 4 | kicker, **three empty rings + 1848/1867/1917**, thread/dot |
| 8 | 5 | 17 | 2 | 1 | — | 4 | kicker, thread/dot |
| 9 | 4 | 6 | 2 | no title shape | quote lines at 2/3/4 | 3 | kicker, thread/dot |
| 10 | 5 | 15 | 1 | 1 | — | 4 | kicker, thread/dot |

Totals: **51 click groups, 144 effects, 9 Morph transitions (1.5 s)**.
`measure_narrative.py`: **3 empty base slides** (1, 3, 5), **4 pictures on the
last click** (the three portraits on slide 1 and Plato on slide 2), **9 of 10
slides with an animated title**, **0 object lifecycles**.

### 2.1 Defect (a) — decoration is visible before the title/claim

The shape-level reason is always one of two:

- the shape has **no entrance effect**, so PowerPoint shows it at t=0;
- the shape has only an **emphasis** effect (e.g. `pulse`), which does not hide
  it at t=0.

The owner's slide-4 frame is exactly this:

- `kicker` — static, visible at t=0;
- `dialectic-arrow` — only a `pulse` emphasis at click 2, so visible at t=0;
- `straight-dot-8.35/9.95/11.55` — static, visible at t=0;
- `title` — `wipe-up` entrance at click 1, hidden at t=0;
- `dialectic-circle`, `dialectic-core` — `zoom` at click 2, hidden;
- `dialectic-card` / `meta-card` — at clicks 3/5, hidden.

Frame: `motion/before/s04-00-base.png`. The same pattern produces:

| Slide | Base frame | What the audience sees before the first click |
|---:|---|---|
| 1 | `before/s01-00-base.png` | red field + three **empty rings**; no title, no faces |
| 2 | `before/s02-00-base.png` | a **red disc** + a caption; no title, no Plato |
| 4 | `before/s04-00-base.png` | kicker + red arc + **three dots**; no title |
| 7 | `before/s07-00-base.png` | kicker + **three empty rings + three dates**; no title, no faces |
| 9 | `before/s09-00-base.png` | a deep-red field with only “LUẬN CƯƠNG” and a rule; no quote |

Slides 3, 5, 6, 8 and 10 have 0–2 base words, usually only the kicker; their
titles are click-gated too.

### 2.2 Defect (b) — an image arrives last without a spoken beat

| Slide | Image | First click | Last click? | Spoken beat in the notes? |
|---:|---|---:|---|---|
| 1 | `!!marx`, `!!engels`, `!!lenin` | 4 | **yes** (4/4) | The notes mention “ba chân dung”, but the visual arrives as one final cluster after the subtitle and the thread; it is a reveal, not an argument. |
| 2 | `plato` | 7 | **yes** (7/7) | The notes never mention the bust; it is a closing decoration. |
| 7 | `!!marx`, `!!engels`, `!!lenin` | 2 / 3 / 4 | no (timeline is 5) | Each portrait arrives with its name and dates, so the image-last rule is **not** the defect here; the empty base is. |

The worst case is slide 2: the viewer looks at a red disc for six clicks, then
Plato appears at the end. The image is the largest object on the slide and it
has no narrative job until after the argument is over.

### 2.3 Defect (c) — more than two movers at once

Peak **animated targets** per click group (entrances + emphasis, not counting
instant `appear`):

| Slide | Peak | The burst |
|---:|---:|---|
| 1 | 4 | click 3: subtitle + caption + thread + dot |
| 2 | 4 | clicks 4/5/6: rule + number + heading + sub-label |
| 3 | 4 | clicks 3/4: card + title + body + foot |
| 4 | 4 | click 3: card + name + desc + foot |
| 5 | 4 | each card: panel + number + heading + body |
| 6 | 4 | each part: panel + number + heading + body |
| 7 | 4 | each portrait: image + date + name + desc |
| 8 | 4 | each tile: panel + number + heading + body |
| 9 | 3 | click 4: quote line + rule + author |
| 10 | 4 | each row: number + heading + body + line |

This is the “4 movers” pattern the owner saw as busy. The design system allows
up to 4, but the owner's direction is stricter: **max 2**, and the deck should
read as one gesture, not four simultaneous fades.

### 2.4 Defect (d) — a Morph with no semantic continuity

Nine Morphs, 1.5 s each, on slides 2–10. COM: `EntryEffect = 3954` on 2–10.
The only objects that exist on both sides of every transition are the
background, the margin rule and the dot. The titles, cards, images and labels
are different objects with different meanings. On arrival, the destination's
title/claim is usually still hidden by its own entrance effect, so the Morph
has no visible target to continue into.

| Transition | Shared objects | Idea continuation? | Verdict |
|---|---|---|---|
| 1 → 2 | bg, rule, dot | chapter title → question; no image survives | drop |
| 2 → 3 | bg, rule, dot | definition → basic question; Plato disappears | drop |
| 3 → 4 | bg, rule, dot | two sides → two methods; same binary shape, different content | drop (false equivalence) |
| 4 → 5 | bg, rule, dot | method → history; no object | drop |
| 5 → 6 | bg, rule, dot | three conditions → three parts; same count, different meaning | drop (false equivalence) |
| 6 → 7 | bg, rule, dot | three parts → three people; theory is not the people | drop (false equivalence) |
| 7 → 8 | bg, rule, dot | three people → four functions; no | drop |
| 8 → 9 | bg, rule, dot | four functions → a quotation; no | drop |
| 9 → 10 | bg, rule, dot | the quote's “cải tạo thế giới” recurs in takeaway 03, but as a different object and hidden at entry | drop |

**0 of 9 kept.** Full table and reasons: `beat-sheet.md`, section 5.

### 2.5 Defect (e) — a click that exists only because a shape exists

| Slide / click | Shape(s) | Why the click is empty |
|---|---|---|
| 4 / click 3 | `dialectic-foot` | It is revealed at the same click as `dialectic-card`, but the card is opaque and sits on top of it. The audience never sees it. |
| 1 / click 3 | `!!thread`, `!!dot` | The gold thread and dot are decoration; they enter after the subtitle, before any content that needs them. |
| 2 / click 7 | `plato` | No spoken beat names the bust; the click exists because the picture exists. |
| 9 / clicks 1–4 | quote mark, then each line | The quote is the claim; building it line by line makes the first three states unreadable. |
| 10 / click 5 | `credits` | The source credit appears with the closing line; it could be static. |

The directed copy removes the `dialectic-foot` shape (it was dead weight under
the card), makes the credits static, keeps the thread/rule static as the
page gutter (and removes the `!!` Morph convention), and puts the quote on the
base plate.

## 3. After: the 10 slides

| # | Beats | Effects | Base words | Title | Picture | Peak movers |
|---:|---:|---:|---:|---|---|---:|
| 1 | 1 auto | 3 | 28 | static | all static | 1 |
| 2 | 3 | 14 | 14 | static | static | 1 |
| 3 | 3 | 11 | 9 | static | — | 1 |
| 4 | 3 | 11 | 8 | static | — | 1 |
| 5 | 4 | 15 | 12 | static | — | 1 |
| 6 | 2 | 15 | 12 | static | — | **2** |
| 7 | 4 | 16 | 11 | static | all static | 1 |
| 8 | 2 | 16 | 7 | static | — | **2** |
| 9 | 1 | 2 | 24 | no title; quote static | — | 1 |
| 10 | 4 | 13 | 27 | static | — | 1 |

Totals: **27 beats (26 presenter clicks + 1 auto ring build), 116 effects,
0 Morph, 9 Fade (0.35 s)**. No empty base slide; no title entrance; no picture
on a click; peak movers **2** (slide 6's two connectors and slide 8's paired
tile rows). The critic's spatial-mover count is lower because fades are not
spatial; the audit counts all animated targets.

## 4. The 4.99 motion score was measuring activity, not direction

The T066 critic gave motion **4.99** and rhythm **4.48** while the owner read
the deck as tasteless. The critic checks duration bands, easing, stagger,
effect kinds and counts; it does not check whether the first frame is readable,
whether a picture has a narrative job, or whether a Morph continues an object.
That is why the audit uses a second instrument (`measure_narrative.py`) and
PowerPoint's own frames. The directed copy scores **4.94** motion and **4.02**
overall — slightly lower, because it is quieter. The owner's judgement is the
gate, not the score.

## 5. Negative results / limits

- **No human review.** Rung 5 only: COM opened, played and captured the file.
- **No projector/room.** The type sizes and the 250 ms sequences were judged on
  a 1920×1080 capture, not in a room.
- **Lifecycles remain 0.** Every effect is an entrance; no object is moved,
  dimmed or exited after it appears. This is deliberate (the argument is
  additive), but it is a real limit against the skill's “object lifecycles”
  advice. A future pass could dim the three rows on slide 10 after the closing
  line, but that would hide the takeaways the audience may still want.
- **The critic still warns MOT-STAGGER on slides 2 and 7** (250 ms between
  three underlines / three dates). These are ordinal sequences the presenter
  speaks (“01, 02, 03”; “1848, 1867, 1917”), not a simultaneous group. We keep
  the 250 ms beat and report the warning instead of compressing it to 150 ms.
- **Capture artefacts.** The windowed captures include PowerPoint's title bar
  and scrollbar; the fullscreen slide-4 captures are clean except for the
  show toolbar on the *before* frame. The stable-state captures were taken
  from the direction build; the final rebuild changed two effect durations
  (200 → 250 ms; the two connectors now start together) and the zip metadata,
  not any stable frame. The static finals were re-exported from the final hash
  (`00c34c4c…`).
- **Content issue not fixed.** The T066 card says “liên hệ, vận động, phát
  triển”; the notes say “liên hệ, vận động, mâu thuẫn”. The directed copy keeps
  the card text; this is a content proofread item, not a motion fix.
