# Image choreography rules

For decks built or directed in the PPTX domain. These rules decide **what an
image is doing on a slide, when it appears, and in what order** — not how it
looks once it is there. They are written from the T066 audit
(`image-audit.md`) and tested by the two variants in `artifacts/`.

Status: **proposal**, not canon. The numbers marked *(proposal)* are judgements
from the T066 evidence and need a review before they enter
`knowledge/design_system.json`. The durations, stagger and mover limits marked
*(design system)* come from `knowledge/design_system.json`.

## 0. Terms

- **Image unit** — the picture plus everything that only exists because of it:
  the disc/panel it sits in, the ring, the caption, the credit. A unit is
  authored, grouped and animated as one object.
- **Naming beat** — the click whose spoken line names the image or its referent
  (“1848 — Tuyên ngôn, Mác và Ăngghen” names both faces).
- **Entry click** — the click at which the image becomes visible for the first
  time. Not the click at which it is mentioned again.
- **Image beat** — the click that changes which image the audience is looking
  at.

## 1. Give every image one role

An image without a role is decoration, and decoration is what the owner
rejected. Four roles cover the decks in this lab:

| Role | Job | Timing law |
|---|---|---|
| **Identity anchor** | tells the room who/what the slide is about before the first word | **visible at t = 0**, no entrance |
| **Evidence** | proves or instantiates the claim being spoken | enters **on its naming beat** |
| **Scene** | sets period, place or mood; carries no claim | visible **before the first sentence**; may enter at t = 0 with the field |
| **Transition** | carries the eye between slides (Morph) | present at the end of slide N and the start of N+1 |

Rules:

- **R1 — One role per image, written down.** Record it in the beat sheet next
  to the click. If you cannot name the role in one word, the image has no job.
- **R2 — The role chooses the timing, not the build order.** A portrait is not
  “an entrance at the end” because the builder appends pictures last.
- **R3 — A scene image must earn its size.** If it is larger than the
  evidence, it is claiming to be evidence. T066's Plato bust is 60.7 % of the
  slide height and proves nothing.

## 2. Timing: before, on, or never after

The three positions are not equivalent:

- **Anchor — before the naming beat.** Legal and strong for identity. The
  audience sees the face, then hears the name; the name lands on something.
- **Evidence — on the naming beat.** The only legal position for proof. The
  image and the word arrive in the same presenter pause (one click), even if
  the image's own entrance is delayed 100–300 ms inside that click.
- **Coda — after the last naming beat.** **Forbidden.** If the image arrives
  after the sentence that gives it meaning, the audience has already moved on;
  the picture can only decorate.

Rules:

- **R4 — No image on the last click of a slide** unless the image *is* the
  conclusion (a final reveal that changes the claim). Test: delete the last
  click. If the slide still reads, the image was a coda.
- **R5 — An image enters at most one click after its naming line, and only if
  the line is still being spoken.** In practice: same click.
- **R6 — The last image beat must not be later than the last text beat.** This
  is the `image_lag` metric in `measure_choreography.py`; it must be 0 for
  every slide. T066: 1 on the cover, 1 on slide 2, 0 on slide 7.
- **R7 — A click must leave a stable image state.** A pulse that returns to the
  same size leaves the audience with no visible answer to their click. If the
  click is a “walk”, leave a marker (a work label, a lit stop, a focus ring) so
  the rest state shows where the walk has arrived. T066's timeline is the
  positive case: each stop is a stable state.
- **R8 — Anchor images stay still.** An identity anchor may have no entrance
  and no Ken Burns; the title's motion is the life of the slide. Never let a
  slow drift pull the eye off the words that are arriving.

## 3. One image focus at a time

- **R9 — One new image unit per click.** A group that is *one* referent (a
  compound name, a pair that acts together) counts as one unit and may enter
  with a 60–150 ms stagger *(design system)*. Two unrelated images in one click
  split attention and read as a contact sheet.
- **R10 — Grouping mirrors the sentence.** “Mác – Lênin” is one compound name →
  one group. “Mác và Ăngghen đặt nền; Lênin phát triển” is 2 + 1 → a pair beat
  and a single beat. T066's slide 7 says 2 + 1 in the notes and shows 1 + 1 + 1
  on the slide; that is the whole defect in one line.
- **R11 — Never leave a frame, disc, panel or caption without its picture.**
  The frame is part of the unit and enters with it. This is the “empty frame”
  metric; it must be 0. T066: 4 states / 12 instances on the cover, 7 / 7 on
  slide 2.
- **R12 — The field arrives with its occupant.** A dark panel that exists to
  hold a portrait is not a background; it is the portrait's stage. If it is on
  screen before the portrait, the slide shows an empty stage. In variant B the
  panel fades in with Lenin; in A it is part of the t = 0 composition.

## 4. Order is the argument

- **R13 — The order of the pictures is the order of the claim.** If the slide
  says “một dòng chảy”, the reveal order is the flow (1848 → 1867 → 1917), not
  the cast list (Mác → Ăngghen → Lênin). If the slide ranks, reveal in rank
  order. Cast order is legal only when the claim *is* cast order.
- **R14 — When the claim is a sequence, the spine comes first or with the first
  item — never last.** A line that organises three things cannot arrive after
  the three things; the audience has already built an order without it. T066's
  slide 7 draws the timeline at click 5, after all three portraits.
- **R15 — Do not put two orders on one slide without labelling the axes.** If
  the people are in one order and the works in another, give each its own axis
  and its own labels, and do not let a dot sit under a face as if it pointed at
  it. T066: the 1848 dot sits under the portrait captioned “Tư bản · 1867”.

## 5. Size, crop, and the cut-out

- **R16 — Same role, same size.** Different diameters inside one group imply a
  hierarchy the content must support. T066's cover uses 2.90 / 2.25 / 2.75 in
  with no reason.
- **R17 — A portrait is 24–40 % of slide height in a group; 40–60 % when it is
  the slide's subject; above 60 % only when the image *is* the slide.**
  *(proposal; T066's portraits are 30–39 %, the Plato bust 60.7 % on a text-led
  slide.)*
- **R18 — Crop for the face, not for the box.** Eyes in the upper third; cut at
  mid-chest, never through the chin or the eyes; a bust may overflow its disc
  at the bottom when the silhouette is clean (T066's Plato does this well).
- **R19 — Keep 0.25 in of safe margin** *(proposal)* between a cut-out and the
  slide edge; projectors overscan. T066's Engels ends 0.03 in from the edge.
- **R20 — A cut-out without a background needs a field and a rim.** Transparent
  PNGs are not “free”: place them on a solid field (disc, panel, band) or give
  them a 1–2 pt rim, and keep ≥ 3:1 graphic contrast between the cut-out's
  dominant tone and that field *(design system: graphic contrast)*. Never drop a
  cut-out on a photograph or a same-value gradient; the silhouette disappears.
- **R21 — Gaze into the content, not off the slide.** A face looking off the
  right edge pulls the eye out of the deck. Turn the crop or the position so the
  gaze lands on the title, the text, or the viewer.

## 6. Words: the naming sentence

- **R22 — No image without a sentence that names it.** The sentence may be on
  the slide (a caption, a label) or in the notes at that click. If neither
  names it, the image has no beat and should be removed.
- **R23 — A credit is not a name.** “Tượng triết gia Hy Lạp · CC0” is a credit;
  it tells the audience where the file came from, not what it is doing on the
  slide. T066's empty disc carries exactly this credit for six clicks.
- **R24 — Pair a portrait with its own date.** Three legal patterns:
  (a) face + lifespan, and the works on a separate spine (no false 1:1);
  (b) face + one work, when that person is the author;
  (c) face + a biographical date (birth, death, a life event).
  Never put a work date under a face that did not write it; never put a
  co-authored work under one of its two authors as if it were solo.
- **R25 — Write the beat sheet before the build.** One line per click, with the
  image name in the line. The build reads the beat sheet; it does not invent
  entrances from shape order. Template:

  ```markdown
  ## Slide 7 — Một dòng chảy
  [click] Một dòng chảy: 1848, 1867, 1917.        → spine draws
  [click] 1848 — Tuyên ngôn, của Mác và Ăngghen.  → pair enters (one unit)
  [click] 1867 — Tư bản.                          → 1867 stop; no new face
  [click] 1917 — Cách mạng Tháng Mười, Lênin.     → Lenin + his panel
  ```

## 7. Two tests before delivery

1. **Empty-frame test.** Step the slide click by click and ask, at every state:
   “is any frame, disc, panel or caption visible without its picture?” If yes,
   the unit is split. Automated: `measure_choreography.py` →
   `empty_frame_states` must be 0.
2. **Coda test.** Delete the last click. If the slide still makes sense, the
   last image was a coda. Automated: `image_lag` must be 0 and `coda_images`
   must be empty.

Both are cheap to compute from the timing tree and catch the T066 defect
without opening PowerPoint. They are necessary, not sufficient: they cannot see
whether the order follows the argument — that is R13–R15 and needs the beat
sheet.

## 8. Failure catalogue (T066 → rule)

| Symptom in T066 | Measurement | Rule |
|---|---|---|
| three portraits on click 4/4 | `image_lag = 1`, 3 coda images | R4, R6 |
| empty gold rings for four states | 4 states / 12 instances | R11 |
| empty red disc + “statue” credit for six clicks | 7 states / 7 instances | R11, R23 |
| Plato, the largest image, arrives last | 60.7 % height, click 7/7 | R3, R4 |
| slide 7: 1867 under 1848 | column 2.15 caption 1867 vs dot 2.20 label 1848 | R13, R15 |
| slide 7: three equal columns for a 2 + 1 claim | equal 2.30 in, equal spacing | R10 |
| cover sizes 2.90 / 2.25 / 2.75 | no semantic difference | R16 |
| Engels at 0.03 in from the edge | x + w = 13.30 of 13.333 | R19 |
