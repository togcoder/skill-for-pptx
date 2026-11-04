# Image audit — T066 “Triết học Mác – Lênin, Chương 1”

- **Task:** T067 [pptx], image choreography.
- **Object:** `experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx`
  (read-only; 10 slides, 144 effects, Morph on 2–10).
- **Measured with:** `inputs/audit_images.py` (shape geometry + `pptx_animator.read_main_sequence`),
  `inputs/measure_choreography.py` (beat metrics), PowerPoint 16.0 COM
  (`probe_variants.ps1` for the variants; T066 was parsed by the same reader).
- **States:** `preview/states/t066-*.png`, reconstructed from the deck's own
  timing tree and exported by PowerPoint (`inputs/render_states.py`). Rung 4:
  the pixels are PowerPoint's, the *order* is the timing model — this is not a
  slideshow-playback claim.
- **Raw data:** `artifacts/image-audit.json`, `artifacts/image-beat-metrics.json`.

## 1. What is on the deck

| # | Image | Place | Size (in) | % slide height | Entry click | Notes |
|---|---|---|---|---|---|---|
| 1 | `!!marx` | cover, top right | 2.90 × 2.90 | 38.7 | **4 / 4** | zoom 700 ms |
| 2 | `!!engels` | cover, right edge | 2.25 × 2.25 | 30.0 | **4 / 4** | zoom 600 ms |
| 3 | `!!lenin` | cover, bottom right | 2.75 × 2.75 | 36.7 | **4 / 4** | zoom 600 ms |
| 4 | `plato` | slide 2, right third | 3.75 × 4.55 | **60.7** | **7 / 7** | float-in 700 ms |
| 5 | `!!marx` | slide 7, col 1 | 2.30 × 2.30 | 30.7 | 2 / 5 | zoom 700 ms |
| 6 | `!!engels` | slide 7, col 2 | 2.30 × 2.30 | 30.7 | 3 / 5 | zoom 700 ms |
| 7 | `!!lenin` | slide 7, col 3 | 2.30 × 2.30 | 30.7 | 4 / 5 | zoom 700 ms |

PowerPoint crop on every picture is `0,0,0,0`: the circular mask is baked into
the PNG (`inputs/02_prepare_assets.py`), so “crop” here means the disc mask and
the asset framing, not a PowerPoint crop rectangle.

## 2. The measurements that matter

From `image-beat-metrics.json`:

| Slide | Clicks | first image vs first text | last image after last text | images on the last (coda) click | clicks with an empty frame |
|---|---|---|---|---|---|
| 1 cover | 4 | **+3** | **+1** | **3 of 3** | 4 states / 12 frame-instances |
| 2 “Triết học là gì?” | 7 | **+7** | **+1** | **1 of 1** | 7 states / 7 instances |
| 7 “Một dòng chảy” | 5 | +2 | 0 | 0 | 4 states / 9 instances |

- `first image vs first text = +3` means the cover's text starts three clicks
  before any face exists.
- `last image after last text = +1` means every image lands after the last
  verbal beat: the pictures are a coda.
- `empty frame` counts states in which a ring/disc is visible while its picture
  is hidden. On the cover this is every state before click 4; on slide 2 it is
  every state before click 7.

## 3. Slide by slide

### Slide 1 — cover

- **Role intended:** identity anchor. The chapter is *about* these three; the
  title is their name.
- **Role performed:** decoration, coda. The three faces are the last click.
- **What the audience sees at t = 0** (`preview/states/t066-s1-c0.png`): a red
  field, a dark panel, and **three empty gold rings**. No text, no faces.
- **What it sees after three clicks** (`t066-s1-c3.png`): kicker, title,
  subtitle, footer — and still three empty rings. The whole verbal argument is
  on screen before the first face.
- **Spoken line that names them:** none. The notes say “Ba chân dung không phải
  để tôn thờ; họ là ba mốc…” — “ba chân dung”, no names. The title names **Mác**
  and **Lênin**; **Ăngghen is named nowhere on the cover and nowhere in its
  notes**. One of three faces is never given a word.
- **Size/crop:** 2.90 / 2.25 / 2.75 in. The 0.65 in spread has no meaning: it
  implies Marx > Lenin > Engels, which the content does not claim. Engels's
  disc ends at x = 13.30 in, 0.03 in from the slide edge — no safe margin.
- **Position vs claim:** the dark panel on the right is a correct “identity
  field”; the composition says “these three matter”. The timing says “they are
  an afterthought”. Position and timing disagree.
- **Verdict:** the worst instance in the deck — see §5.

### Slide 2 — “Triết học là gì?”

- **Role intended:** scene / mood. A Greek philosopher bust to place the
  question in a tradition.
- **Role performed:** decoration that contradicts its own caption.
- **What the audience sees at t = 0** (`preview/states/t066-s2-c0.png`): a
  **giant empty red disc** (60.7 % of the slide height, 34 % of its width) with
  the caption **“Tượng triết gia Hy Lạp · CC0”** already on screen. The slide
  labels an empty circle as a statue for six clicks.
- **Entry:** click **7 of 7**, after the definition, the second definition and
  all three function labels. The largest image in the deck arrives after the
  argument is over.
- **Spoken line:** none. The notes discuss the definition and the three labels;
  the statue is never mentioned.
- **Truthfulness:** the object is an Epidauros philosopher type, not Plato
  (T066's own REPORT §Negative 3). The caption is honest; the deck still uses it
  as if it were evidence for “philosophy”.
- **Size/crop:** 3.75 × 4.55 — larger than any portrait of the three thinkers
  the chapter is named after. The size claims importance the image does not
  carry. The bust deliberately overflows the disc at the bottom (0.23 in), which
  is a good cut-out gesture; it is wasted by the timing.
- **Position vs claim:** the disc owns the right third while the claim is a
  two-sentence definition on the left. The image is a co-equal, but says
  nothing. Either give it a sentence (the tradition before Marx) or remove it.
- **Verdict:** the clearest proof that the defect is systemic: the deck's
  largest image, with a visible caption, arrives last.

### Slide 7 — “Một dòng chảy”

- **Role intended:** evidence — three people, three dates, one project.
- **Entry:** one portrait per click (2, 3, 4), which is the right *grain*. The
  problem is the order and the axis, not the grain.
- **Measured contradiction:** the portraits are in **person order**
  (Marx 2.15 in, Engels 6.60, Lenin 11.05) while the timeline is in **work
  order** (1848 dot at 2.20, 1867 at 6.40, 1917 at 10.90). The stop at 2.20
  labelled **1848** sits under the portrait captioned **“Tư bản · 1867”**; the
  stop at 6.40 labelled **1867** sits under **“Tuyên ngôn · 1848”**. The two
  rows cross.
- **Reading order:** the captions read 1867 → 1848 → 1917, a non-monotonic
  sequence in the direction of reading, under a title that says “one flow”.
- **The spine arrives last** (click 5), after the three items it is supposed to
  organise. The audience sees three portraits, then a line that re-orders them.
- **Spoken line:** the notes say “Mác và Ăngghen đặt nền lý luận; Lênin phát
  triển…” — a **2 + 1** argument. The layout is **1 + 1 + 1** (three equal
  columns, equal size, equal spacing). The image grouping contradicts the
  spoken grouping.
- **Size:** 2.30 in each, equal — correct for peers, wrong for a 2 + 1 claim.
- **Verdict:** the images are timely but *misordered*; the slide's claim is an
  order, and the pictures do not follow it.

## 4. Findings

**F1 — The frame outlives the picture.** Gold rings and the red disc are
separate shapes with no entrance. They are visible from t = 0; the picture
inside arrives at the last click. The slide shows an empty frame and, on slide
2, a caption for an absent object. This is the mechanical cause of the owner's
“ảnh hiện lên cuối cùng”.

**F2 — No image has a line.** No click in T066 has a script line that names an
image. The notes are prose paragraphs without click cues; the build script
assigns effects by shape name, not by sentence. An image that no sentence names
can only be decoration, whenever it appears.

**F3 — All cover images are on the last click.** 3 of 3, at click 4 of 4. The
cover spends its entire verbal budget before showing who it is about.

**F4 — The largest image is the last one.** Plato at 60.7 % height, click 7/7,
with no spoken line and a caption that admits it is a generic philosopher.

**F5 — Order is cast order, not argument order.** Slide 7 reads Marx → Engels →
Lenin while the claim reads 1848 → 1867 → 1917. One adjacent inversion (1867
before 1848) in the reading direction.

**F6 — Grouping is flat where the argument is 2 + 1.** Three equal columns for
“two founders, then the one who turned theory into revolution”.

**F7 — Size varies without meaning.** Cover 2.90 / 2.25 / 2.75; slide 2's bust
larger than every portrait of the chapter's own subject.

**F8 — No safe margin at the edge.** Engels's disc ends 0.03 in from the slide
edge.

## 5. The worst defect

**The cover: the deck's identity is revealed on the last click, inside frames
that were already on screen.**

It is the worst because it is the first impression, it affects all three
images, and it is visible without any interpretation: `t066-s1-c0.png` is three
empty gold rings on a red field. The room sees the frame, waits three clicks,
and gets the face after the title has finished speaking. The picture is not
late by accident of duration; it is late by design — the build puts the
portraits in their own click group, after the subtitle.

Slide 2 is the same defect with a harder proof (a caption on an empty disc), and
slide 7 is the same root cause expressed as order rather than lateness: in both
cases the image is treated as a layer added after the text, not as the thing the
text is about.

## 6. What the fix has to change

1. **One image = one unit**: face + rim + field (+ caption). No frame without
   its picture, at any click.
2. **A role decides the beat**: an identity anchor is present at t = 0; an
   evidence image enters on the line that names it; no image enters after its
   last naming line.
3. **The order of the pictures is the order of the argument**, not the cast
   list; if the claim is a sequence, the sequence is the reveal order.
4. **The grouping of the pictures is the grouping of the argument** (pair vs
   individual).
5. **Write the line first.** If no sentence names the image, the image has no
   click.

The full ruleset is `image-rules.md`; the two variants that test rules 2–4 are
`artifacts/T067-variant-A-cover-flow.pptx` and
`artifacts/T067-variant-B-cover-flow.pptx`.
