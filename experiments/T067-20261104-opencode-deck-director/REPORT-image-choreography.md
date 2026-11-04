# T067 [pptx] — Image choreography: when a picture earns its click

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), builder for T067.
- **Date:** 2026-11-04. **Branch:** `work/T067-opencode-deck-director` (base
  `7d3d9b8`). **Scope:** `experiments/T067-20261104-opencode-deck-director/**`.
- **Trigger:** owner critique of T066 — *“Sắp xếp hình ảnh rất đáng quan tâm.
  Ảnh vĩ nhân hiện lên cuối cùng — nó mang ý nghĩa gì? Không. Phải làm rõ kịch
  bản.”*
- **Status:** experimental rules + tested variants; review requested. No product
  path, no skill, no design-system data changed.
- **Folder note:** this is the image-choreography stream's report. The task-wide
  skill audit is `REPORT.md` in the same folder (another stream); the style
  system is `experiments/T067-20261104-opencode-visual-style/`. Nothing in those
  files was edited.

## Frame

- **Question.** T066 uses seven image placements as decoration with arbitrary
  timing. Under what rule does a picture *mean* something, and which of two
  timing laws reads better — images present before the words, or images entering
  on the sentence that names them?
- **Hypothesis.** The defect is not “late” in the abstract; it is **entering
  after the last sentence that gives the image meaning**, inside a frame that
  was already visible. Two laws should cover the deck: identity anchors at
  t = 0, evidence on its naming beat. The cover should read better with the
  first law; the sequence slide with the second.
- **Falsifiers.**
  - the audit finds no systematic timing defect, only taste;
  - empty frames do not change the reading;
  - A's empty opening reads better than B's build (or the reverse) on both
    slides;
  - the image order cannot be made to follow the claim without breaking the
    layout;
  - PowerPoint cannot open or play the variants;
  - the rules do not predict which variant wins.

## Frozen input

- **Deck:** `experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/
  T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx`, sha256
  `f4478f0edc9829c664caac4a16aa4f7710ef57843b4493a7c3f46886d3ed244d`
  (read-only).
- **Images:** T066's prepared assets, read-only from
  `T066-.../inputs/assets/`: `marx-circle.png`, `engels-circle.png`,
  `lenin-circle.png` (700 × 700, circular cream disc + duotone, Wikimedia
  Commons PD). The variant files embed them; the branch does not copy them.
- **Design numbers:** `knowledge/design_system.json` — entrance 250–700 ms,
  stagger 60–150 ms, ≤ 4 independent movers per click. Image-specific numbers
  in `image-rules.md` are marked *proposal*.
- **Environment:** Windows 11, PowerPoint 16.0 build 17932, Python 3.13,
  python-pptx, Pillow, lxml.
- **Not available:** a human panel; a projector; a full 10-slide rebuild; a
  Plato-specific asset.

## Method

```powershell
# 1. audit every picture in T066 (geometry, crop, entry click, nearest text)
python experiments/T067-20261104-opencode-deck-director/inputs/audit_images.py

# 2. beat metrics (image lead/lag, coda, empty frames)
python experiments/T067-20261104-opencode-deck-director/inputs/measure_choreography.py

# 3. build the two variants (same layout, one variable: timing)
python experiments/T067-20261104-opencode-deck-director/inputs/build_variants.py

# 4. render every stable click state with PowerPoint COM, then contact sheets
python experiments/T067-20261104-opencode-deck-director/inputs/render_states.py
python experiments/T067-20261104-opencode-deck-director/inputs/make_sheets.py

# 5. native parse (effect + trigger counts) and final static render + PDF
powershell -File .../inputs/probe_variants.ps1 -Pptx ... -Out ...
powershell -File .../T066.../inputs/render.ps1 -Pptx ... -OutDir ...
```

1. **Audit.** Every picture measured in the T066 timing tree: entry click,
   duration, frame shapes, crop, distance to the nearest text, and the spoken
   line (notes) that names it. Result: `image-audit.md`.
2. **Rules.** Four roles (identity anchor, evidence, scene, transition) and the
   three legal positions relative to the naming beat (before / on / never
   after), plus order, grouping, size, crop and cut-out rules. Result:
   `image-rules.md`.
3. **Variants.** Two 2-slide excerpts (cover + “Một dòng chảy”), **same
   geometry, same assets, same type**. The only variable is when the images
   appear:
   - **A** — anchors visible at t = 0; the title animates over them; the work
     labels build one per click.
   - **B** — title first; the spine draws; the founders enter on “1848”, the
     1867 stop arrives alone, Lenin enters on “1917”.
   Both correct T066's structural defects identically, so they cannot explain a
   reading difference: each portrait is one atomic group (face + rim), the flow
   slide separates the people axis (portrait + lifespan) from the work axis
   (date + work + author on the spine), and the 2 + 1 argument becomes the
   composition (pair on the red field, Lenin in the deep panel). No Morph: the
   two slides are not adjacent in the real deck, and continuity is a separate
   variable.
4. **Render.** 32 stable states reconstructed from each deck's own timing tree
   (`simulate_states`) and exported by PowerPoint at 1920 × 1080; nine key
   states are committed at 1280 × 720, and all 32 appear in the contact sheets;
   final slides and PDFs rendered natively. Rung 4: the pixels are PowerPoint's,
   the order is the timing model — **not** a slideshow-playback claim.
5. **Compare.** Two measured proxies (empty-frame states, coda images) plus an
   author read of every state. No human panel.

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| T066's images are a coda | cover: `image_lag=1`, 3/3 images on click 4/4; slide 2: 1/1 on click 7/7 | 4 (timing tree + 12 state renders) |
| T066 shows empty picture frames | cover 4 states / 12 instances; slide 2 7 / 7 (disc **and** its caption) | 4 |
| T066's flow slide contradicts itself | 1848 dot at x=2.20 under portrait caption “Tư bản · 1867” at x=2.15; 1867 dot at x=6.40 under “Tuyên ngôn · 1848” at x=6.60 | 4 (measured shape positions) |
| Variants are native and editable | PowerPoint 16.0 opens both; `Slides.Count=2`; A 19 effects (7 + 12), B 37 (12 + 25); clicks 3 + 4 and 3 + 5 | 4 |
| Variants have no empty frames and no coda | `empty_frame_states=0`, `coda_images=[]`, `image_lag=0` on both slides of both files | 1 (computed from the timing tree) |
| Variants render | 32 state PNGs + 4 final PNGs + 2 PDFs exported by PowerPoint | 4 |
| A vs B reading | author read of the 32 states (`preview/sheets/`) | not a rung; no human panel |
| Human review | **not reached** | — |

## The comparison

Measured:

| | Cover clicks | Cover first image | Flow clicks | Flow first image | Empty-frame states | Coda images |
|---|---|---|---|---|---|---|
| T066 | 4 | click 4 (3 faces) | 5 | click 2 | 4 and 7 | 3 and 1 |
| **A** | 3 | **t = 0** (3 faces) | 4 | **t = 0** (3 faces) | 0 | 0 |
| **B** | 3 | click 2 (3 faces) | 5 | click 3 (2 faces) | 0 | 0 |

Read (author, from `preview/sheets/sheet-*.png`):

**Cover — A wins.**
`A-s1-c0` is a finished poster: three faces, the panel, the plate
“C. MÁC · PH. ĂNGGHEN · V.I. LÊNIN”. The title then lands into the left field
and the cover is complete. The audience entering the room already knows who the
chapter is about, and every later word lands on a face.
`B-s1-c0` is an empty red field with a dark panel; `B-s1-c1` is an empty field
with a kicker. B's gain is real — the faces arrive in the same click as
“MÁC – LÊNIN”, so the word and the image are one event (`B-s1-c2`) — but the
title already *is* the name, so the image closes no informational gap. The price
is two dead frames at the start of the deck. A cover is a place, not a
sequence.

**Flow — B wins.**
The slide's claim is an order (“một dòng chảy”). In B the click order *is* that
order: spine (`B-s2-c2`), 1848 + the pair (`c3`), 1867 alone (`c4`), 1917 +
Lenin + his field (`c5`). The 1867 click adding no new face is the best beat in
either variant: it says “the same people carry the theory forward” without a
word. Each click leaves a stable, different picture.
A shows the conclusion first: all three faces, all three dates, the spine at
t = 0 (`A-s2-c0`), then the title, then the three work labels. It is a better
*handout* and a worse *lecture*: the audience can read the whole argument before
the presenter opens their mouth, and the image reveal carries no information —
the faces never participate in the build. A's t = 0 is also slightly
unbalanced: the title band is empty above a fully populated lower two-thirds.

**Verdict.** The two laws are not rivals; they are cast by role.
**A wins the cover, B wins the argument slide.** As a deck rule, B's law
generalises (every content slide has a sentence to land on); A's law applies
only where the image *is* the identity of the slide. The recommended deck uses
**A on the cover and B on every argument slide**. If one file must be shown, show
B: it demonstrates the fix on the harder slide, and its cover still reaches the
same final frame — one click later.

## Negative results and limitations

1. **A's flow images are inert.** At t = 0 the whole cast is present; the
   clicks only add work labels. If the presenter skips the last three clicks,
   nothing is lost — a sign the image layer is not carrying the argument. That
   is A's cost, and the reason it loses the flow.
2. **B opens on nothing.** `B-s1-c0` and `B-s2-c0` are a red field (and a dark
   panel on the cover). If the presenter speaks before the first click, the room
   looks at an empty stage. A cover should probably not use B.
3. **B costs one more click** on the flow (5 vs 4). It buys four distinct
   states instead of one plus three annotations.
4. **The variants are excerpts.** Two slides, no Morph, no deck rhythm, no
   transition into/out of the slides. Continuity and cross-slide pacing are
   untested.
5. **State renders are reconstructed, not played.** `simulate_states` models
   visibility only; entrances are shown at their end state, pulses are invisible
   in a still. The A/B difference in *entry order* is exact; the feel of the
   motion is not verified. Interactive playback was not observed.
6. **A structural fix was needed to make the comparison honest.** Each portrait
   is now a group (face + rim). T066's separate rings are why the cover shows
   empty frames; grouping removes the failure mode by construction. This is a
   change to the artifact, not only to the timing — it is identical in A and B,
   so it cannot explain the A/B result, but it does mean the variants are not
   pure timing diffs of T066.
7. **The flow layout was rebuilt**, not just re-timed: 2 + 1 grouping, a
   people/work axis split, and a spine that names its authors. This is the
   argument fix; the A/B difference is still only timing. The cost is that the
   variant slide no longer matches T066's geometry.
8. **The Plato fix is proposed, not built.** The variants cover only the cover
   and slide 7. Slide 2 needs either removal or a scene line and a unit that
   includes the disc and the credit.
9. **Small type inherited.** The spine's work labels are 8.5 pt, below the
   design system's 11 pt caption token; the deck's type pass (T066 §Negative 1)
   still applies.
10. **No human review.** The “reads better” verdict is one author's read of
    stills. Rung 6 is not reached; a room test could reverse the cover verdict.

## Next

1. **Apply the law to the real 10-slide deck:** A-cover, B-flow, and slide 2
   rebuilt as one unit (disc + bust + credit) with a scene line — or the bust
   removed.
2. **Code the two checks** (`empty_frame_states`, `image_lag`) into
   `design_critic.py` or `forge_qa.py`; both are cheap to compute from
   `p:timing`. Product path → branch + review.
3. **Human review** of the two variants on a projector; record whether A's
   cover still wins when the deck is opened live, and whether B's empty first
   frame is acceptable in a lecture room.
4. **Beat-sheet template** (R25) into `pptx-motion-director`; the tool should
   refuse an image with no line. Product path → review.
5. **Decide the Plato asset:** a Plato-specific bust, or keep the Epidauros
   philosopher as a labelled scene image at 30–40 % height.

## Artifacts

- `image-audit.md` — every T066 image: role, click, line, size/crop, position
  vs claim, findings, worst defect.
- `image-rules.md` — 25 rules, the beat-sheet template, two tests, failure
  catalogue.
- `artifacts/T067-variant-A-cover-flow.pptx` — 2 slides, 19 effects.
- `artifacts/T067-variant-B-cover-flow.pptx` — 2 slides, 37 effects.
- `preview/final-A/`, `preview/final-B/` — PowerPoint PNG + PDF.
- `preview/states/` — nine key PowerPoint state renders at 1280 × 720.
- `preview/sheets/` — contact sheets for all 32 states, incl. the T066 evidence
  sheets.
- `artifacts/image-audit.json`, `image-beat-metrics.json`, `probe-A/B.json`.
- `inputs/` — audit, metrics, builder, state renderer, sheets, probes.

## Review response

Pending. The first review should test the verdict, not the files: does the
cover read better with the faces present at t = 0, and does the flow read better
when each portrait lands on its date? If both answers are “yes”, the rules hold;
if not, the role table is wrong and should be rewritten before the deck is.
