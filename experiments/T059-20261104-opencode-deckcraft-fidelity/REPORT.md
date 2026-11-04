# T059 [pptx] — DeckCraft as second renderer: static, Morph and round-trip fidelity vs PowerPoint

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), builder. Critic per T057: Claude.
- **Date:** 2026-11-04. **Base:** `main` @ `ac5b45e`.
- **Branch:** `work/T059-opencode-deckcraft-fidelity`.
- **Environment:** Windows 11 x64; Python 3.13.5; python-pptx 1.0.2;
  Pillow 13.0.0; numpy 2.2.6; pywin32; Microsoft PowerPoint 16.0 build 17932
  (COM); DeckCraft CLI 0.13.1 (`D:\artcraft\DeckCraft\deckcraft-cli.exe`);
  ffmpeg/ffprobe 8.1.1.
- **Deliverables:** `artifacts/fidelity.csv`, `fidelity_objects.csv`,
  `critic_parity.csv`, `critic_frames.csv`, `morph.csv`, `morph_hidden.csv`,
  `roundtrip.csv`, `roundtrip_effects.csv`, `roundtrip_pp.csv`,
  `roundtrip_media.csv`, `roundtrip_animation.csv`,
  `frame_source_example.json`; per-slide JPEGs in
  `artifacts/diffs/`; deck contact sheets in `artifacts/static/`; Morph and
  animation strips in `artifacts/morph/`; headline in `artifacts/headline.jpg`.
  Commands: `inputs/commands.md`. Hashes: `inputs/deck_hashes.txt`. Wiring:
  `inputs/wiring-proposal.md`.

## Frame

**Question.** For the lab's own decks, where can DeckCraft 0.13.1 stand in for
PowerPoint — as the renderer behind `slide_forge.render` and
`design_critic` — and where can it not?

**Hypotheses and falsifiers.**

1. *Static:* DeckCraft static frames are close enough for design critique.
   Falsifier: the per-slide diff exceeds the critic's sensitivity, so critic
   scores differ by more than 0.2.
2. *Morph:* `render-transition` frames match PowerPoint `CreateVideo` frames
   at the same normalised time, including entrance-hidden shapes. Falsifier:
   the frames disagree.
3. *Round trip:* `convert` preserves the timing semantics, and PowerPoint
   still plays the deck the same way. Falsifier: PowerPoint's parsed effects
   or the played frames change.

**Domain lens.** PowerPoint's native model: OOXML PresentationML timing,
`Slide.Export` for static state, `CreateVideo` for playback,
`Slide.TimeLine.MainSequence` and `Effect.Behaviors` for what PowerPoint
parsed, and `design_critic.py` for the design-system judgement. DeckCraft is
tested *in the receiving domain*, not accepted because it is another ArtCraft
tool.

**Transfers.** DeckCraft is the cross-craft slide renderer named in
`lab/standards/RESEARCH.md`. Nothing here becomes a shared "universal" layer:
the matrix is PPTX-only, and every DeckCraft result is marked with its own
evidence rung. The only product-path idea (the render fallback) is proposed,
not wired.

## Frozen input

**Decks.** Five Forge specs from `examples/pptx/forge/`, built at the base
commit, plus the two T028 "pro" decks, plus one synthetic per-kind probe:

| Deck | Slides | Source | SHA-256 (first 16) |
|---|---:|---|---|
| `coffee_report` | 10 | Forge `coffee_report.json` | `4283926297c992fd` |
| `coffee_office_dynamic` | 10 | Forge `coffee_office_dynamic.json` | `6a6329e20326893b` |
| `coffee_report_photos` | 11 | Forge `coffee_report_photos.json` | `00110e27a0991244` |
| `vi_chuyen_doi_so` | 9 | Forge `vi_chuyen_doi_so.json` | `5dbd8465c40f36f9` |
| `vi_brand_seed` | 9 | Forge `vi_brand_seed.json` | `d6e7bba8f6cbcb78` |
| `T028_report_pro` | 8 | T028 output (Morph + director) | `6debf60a709189f6` |
| `T028_showcase_pro` | 10 | T028 output (Morph showcase) | `8d09f0e7b5f7b060` |
| `kind_probe` | 1 | synthetic, 22 objects | `cb5d99b2c9a34155` |

67 corpus slides, 68 measured frames. The probe is labelled separately: it is
a controlled test of gradient/effects/text cases the corpus does not contain,
not a user deck. Full hashes: `inputs/deck_hashes.txt`.

**What I could not access.** No automated live slide-show click harness (T058);
`CreateVideo` was the only PowerPoint playback channel. The comparison is
rung 3–5, never rung 6: no human watched the decks. LibreOffice was not used
as a third renderer in this task.

## Method

**Static.** PowerPoint `Slide.Export(path, "PNG", 1920, 1080)` vs
`deckcraft-cli render FILE --all --scale 2`. Both are resized to 960×540
(Lanczos) and compared per pixel on the maximum RGB channel difference. Metrics:
`mean_abs` (0–255), `pct_gt10`, `pct_gt40` (share of pixels above 40). This is
stricter on colour than T057's luminance method; T057 reported 0.2–2.8 mean
per slide, this run's per-deck means are 0.5–1.5, with chart slides up to 8.2.

**Object kinds.** Every top-level shape is classified from its XML:
`chart` (`c:chart`), `picture` (raster `p:pic`), `picture-svg` (`asvg:svgBlip`),
`gradient` (`a:gradFill`), `effects` (a non-empty `a:effectLst`),
`effects-theme` (`a:effectRef idx>0`), `text` (non-empty text frame), `group`,
`vector` (anything else). A shape may carry several kinds; per-kind rows may
therefore count its pixels more than once. Pixels are attributed to the
topmost shape whose bounding box contains them (rectangle approximation, not a
geometry mask); group interiors stay in the group box. `fidelity_objects.csv`
also reports each object.

**Critic parity.** `design_critic.critique(deck, render=<PowerPoint dir>)`
vs `critique(deck, render="deckcraft")`, same code, same design system. Scores
are compared per dimension.

**Morph.** For a transition into slide N, a copy keeps only slides N−1 and N;
slide N−1's timing and incoming transition are removed, so the transition
start is deterministic. `CreateVideo(..., UseTimings=true, 2 s,
1920×1080, 30 fps)` is recorded, frames are extracted at 30 fps, and the first
changed frame is detected. `t = 0.25/0.5/0.75` of the XML transition duration
(1500 ms for all these Morph slides) selects the PowerPoint frames. DeckCraft
frames come from `render-transition FILE --slide N-1 --t 0.25,0.5,0.75`.
Alignment is within one 30 fps frame (33 ms).

**Entrance-hidden shapes.** Shapes with an entrance effect
(`p:cTn presetClass="entr"`, 36 on the Forge KPI slide) are measured at each t:
per-pixel opacity relative to the previous and final PowerPoint exports is
estimated as `(frame − prev)/(final − prev)`; the median over pixels where the
previous and final states differ by >30 is reported as `pp_alpha`/`dc_alpha`.
`alpha < 0.15` is hidden; `alpha > 0.25` is drawn. This is a measurement, not a
visual judgement.

**Round trip.** `deckcraft-cli convert IN OUT.pptx`. The timing inventory
counts `p:cTn`, `p:par`, `p:seq`, `p:cond`, `p:graphicEl`, the behaviour tags
(`p:anim`, `p:animEffect`, `p:animMotion`, `p:animRot`, `p:animScale`, `p:set`,
`p:cmd`), and each effect's class/preset/node/duration/delay/props/children.
PowerPoint then parses both files (`MainSequence.Count`, effect type,
duration, trigger, repeat, behaviour count) — rung 4. Playback compares
one-slide videos with a leading blank slide, aligned on target appearance;
a same-file control gives 0.0, so the capture is deterministic.

## Evidence

### 1. Static matrix — the renderer is close on ordinary slides

| Deck | Slides | Mean | Max slide | Mean >40 | Max >40 | Worst slide |
|---|---:|---:|---:|---:|---:|---|
| `vi_chuyen_doi_so` | 9 | 1.063 | 3.703 | 0.630% | 2.276% | s4 chart |
| `vi_brand_seed` | 9 | 1.116 | 3.897 | 0.659% | 2.333% | s4 chart |
| `coffee_report` | 10 | 1.331 | 5.851 | 0.719% | 3.419% | s4 chart |
| `coffee_office_dynamic` | 10 | 1.270 | 6.155 | 0.714% | 3.427% | s4 chart |
| `coffee_report_photos` | 11 | 1.514 | 5.851 | 0.800% | 3.419% | s4 chart |
| `T028_report_pro` | 8 | 1.422 | 8.221 | 0.887% | 5.064% | s5 chart |
| `T028_showcase_pro` | 10 | 0.514 | 1.435 | 0.240% | 0.454% | s6 gradient |
| `kind_probe` | 1 | 10.206 | 10.206 | 5.801% | 5.801% | s1 (synthetic) |

The corpus mean is **0.5–1.5 / 255**; `>40` is **0.24–0.89%**. For the six
decks with charts, the worst slide is the chart slide; the exception is
`T028_showcase_pro`, whose worst slide is a gradient halo (1.435). The probe is
deliberately adversarial and is not part of the corpus mean. Rung: PowerPoint
side 5, DeckCraft side 2, comparison 3. See
`artifacts/static/*-contact.jpg` and `artifacts/headline.jpg`.

### 2. Per object kind — the matrix headline

Weighted by pixels over all rows:

| Kind | Rows | Decks | Pixel share | Weighted mean | Weighted >40 | Verdict |
|---|---:|---:|---:|---:|---:|---|
| text | 68 | 8 | 36.4% | **1.54** | 1.01% | near; weight/antialias differs |
| picture (raster) | 12 | 8 | 32.7% | **0.50** | 0.01% | match |
| picture-svg | 2 | 1 | 0.9% | **49.04** | 28.41% | **break** (icons missing) |
| chart | 7 | 7 | 36.2% | **15.31** | 9.22% | **break** |
| gradient | 3 | 2 | 8.7% | **7.02** | 1.09% | near; 3-stop mid missing |
| effects (explicit) | 1 | 1 | 16.6% | **2.61** | 0.67% | near; soft edge/bevel differ |
| effects-theme | 61 | 8 | 13.2% | **1.06** | 0.26% | match |
| vector | 55 | 7 | 7.6% | **0.83** | 0.04% | match |
| group | 1 | 1 | 1.0% | **3.68** | 2.72% | one group with a tiny logo |

Chart weighted mean falls to **13.1** if the synthetic probe is excluded.
Rows are in `fidelity.csv`; object detail in `fidelity_objects.csv`.

**Text.** 68 rows, weighted 1.54, `>40` 1.0%. The difference is visible as
weight and line spacing, not missing content. The probe is consistent with a
font-family resolution gap: the same phrase set in `Segoe UI Semibold` gives
3.55 mean / 2.8% `>40`, while `Segoe UI` with the bold flag gives 2.23 / 1.9%.
Forge asks for the family, not the bold flag. Vietnamese diacritics and text
colour match. Rung 3.

**Picture.** All raster pictures match: weighted 0.50, `>40` 0.01%; the worst
raster row is 2.85 on one Forge photo with a crop. The two `picture-svg` rows
are the exception: 41.02 and 60.23 mean, 24.7%/33.5% `>40`. DeckCraft draws
the **transparent PNG fallback** instead of the SVG blip; PowerPoint draws the
SVG. The icons are simply absent in the DeckCraft contact sheet
(`artifacts/diffs/coffee_report_photos-slide-03.jpg`,
`headline.jpg` middle row).

This is partly a **Forge defect**: `slide_forge.py::Builder.icon` writes
`Image.new("RGBA", (256,256), (0,0,0,0))` as the fallback (line 464). Any
renderer without SVG support sees nothing; PowerPoint hides the problem. Fix
the fallback before blaming the renderer. Rung 4 (PowerPoint) vs 2 (DeckCraft).

**Chart.** The largest systematic break. Six corpus charts: 8.12, 8.60,
13.47, 13.47, 14.42, 20.44 mean; `>40` 5.3–12.7%. The probe's default chart is
45.13 / 27.4%. Visible differences: no line markers, no horizontal gridlines,
legend marker/layout, larger plot area, axis-label placement, different series
colour mapping in the Forge chart. Chart data, categories and series names are
correct. This is a renderer limitation, not a data error. Rung 3.

**Gradient.** Three rows. The T028 soft halos are close in area but differ in
interpolation: 5.25 and 4.86 mean, `>40` 0.76%/0.02%. The probe isolates the
cause: a 2-stop gradient is 9.02 mean / 0% `>40` (endpoints match, midpoint
interpolation differs), while a 3-stop gradient is 14.21 / 6.1% — the middle
orange stop is missing and DeckCraft goes teal→brown. Rung 3.

**Effects.** The probe tests explicit `a:effectLst` on four cards: outer shadow
0.72, glow 0.44, soft edge + bevel 8.63, reflection 0.29 (reflection is partly
clipped below the slide, so its number is not conclusive). DeckCraft handles
shadows and glows; soft edges/bevels are visibly sharper/different. Weighted
explicit-effects mean 2.61. `effects-theme` (the default card shadow carried
by `p:style`) is 1.06. Rung 3.

**Group.** One T028 group contains a small logo that differs; the 3.68 is
dominated by that few-pixel object, not by layout.

### 3. Critic parity — falsifier 1 not triggered

`design_critic` scores, DeckCraft frames minus PowerPoint frames:

| Deck | Design | Motion | Rhythm | Coherence | Overall |
|---|---:|---:|---:|---:|---:|
| `T028_report_pro` | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| `T028_showcase_pro` | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| `coffee_office_dynamic` | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| `coffee_report` | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| `coffee_report_photos` | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| `vi_brand_seed` | +0.01 | +0.00 | +0.00 | +0.00 | +0.01 |
| `vi_chuyen_doi_so` | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |

Maximum absolute delta is **+0.01**, far below the +0.2 falsifier. The three
frame checks are global (background share, balance, colourfulness), so chart
markers or a missing icon cannot move them across a grade band. The largest
single frame-metric delta is balance on a sparse section slide (+0.153), still
inside its band. This is good news for using DeckCraft frames as a critic
fallback, and bad news for using the critic as a renderer regression test:
**the critic is not sensitive enough to catch the chart/SVG/Morph breaks.**
Rung 3 (measurement), not 5.

### 4. Morph frames — falsifier 2 triggered, hard

Twenty transitions, 20 strips. Per-transition mean (across t = 0.25/0.5/0.75)
and `>40`:

| Deck | Slide | Mean | Max | Mean >40 | Entrance shapes hidden in PP | Drawn early by DC |
|---|---:|---:|---:|---:|---:|---:|
| `T028_report_pro` | 2 | 5.81 | 5.81 | 2.88% | 0/1 | 0/1 |
| `T028_report_pro` | 4 | 7.96 | 9.04 | 2.05% | 0/0 | 0/0 |
| `T028_report_pro` | 6 | **27.76** | 34.43 | 19.41% | 7/8 | 7/8 |
| `T028_showcase_pro` | 2 | 18.51 | 27.48 | 10.47% | 7/7 | 7/7 |
| `T028_showcase_pro` | 7 | **64.34** | 78.40 | 40.01% | 0/0 | 0/0 |
| `T028_showcase_pro` | 10 | 21.72 | 27.56 | 9.02% | 0/0 | 0/0 |
| `coffee_office_dynamic` | 4 | 21.15 | 24.24 | 12.33% | 3/3 | 2/3 |
| `coffee_report` | 4 | 20.91 | 23.56 | 12.07% | 3/3 | 2/3 |
| `coffee_report_photos` | 3 | 16.38 | 17.06 | 6.54% | 6/33 | 4/33 |
| `coffee_report_photos` | 5 | 20.16 | 24.70 | 10.57% | 1/5 | 1/5 |
| `coffee_report_photos` | 10 | 7.36 | 8.24 | 2.79% | 2/3 | 1/3 |
| `vi_brand_seed` | 3 | 12.58 | 13.88 | 3.88% | 36/36 | 35/36 |
| `vi_chuyen_doi_so` | 2 | 29.39 | 46.37 | 28.84% | 2/4 | 1/4 |
| `vi_chuyen_doi_so` | 3 | 12.24 | 13.46 | 3.69% | **36/36** | **35/36** |
| `vi_chuyen_doi_so` | 4 | 12.51 | 13.45 | 4.56% | 1/4 | 1/4 |
| `vi_chuyen_doi_so` | 5 | 17.27 | 18.44 | 11.27% | 3/6 | 1/6 |
| `vi_chuyen_doi_so` | 6 | 13.47 | 16.32 | 4.67% | 1/6 | 1/6 |
| `vi_chuyen_doi_so` | 7 | 21.90 | 28.00 | 15.19% | 0/1 | 0/1 |
| `vi_chuyen_doi_so` | 8 | 9.12 | 9.97 | 3.65% | 3/3 | 2/3 |
| `vi_chuyen_doi_so` | 9 | 9.36 | 10.84 | 3.04% | 2/3 | 1/3 |

"Hidden in PP" and "drawn early by DC" are counts of entrance shapes whose
median opacity is <0.15 in PowerPoint and >0.25 in DeckCraft at t = 0.75.

Two distinct failures:

**4a. Entrance-hidden shapes.** Forge puts every content shape on an
entrance effect. During Morph, PowerPoint hides those shapes until their
effect fires; DeckCraft appears to draw both slides' static end states and
cross-fade them. On `vi_chuyen_doi_so` s3 (KPI), 36/36 entrance shapes are
hidden in PowerPoint at all three t; DeckCraft draws 29/36 at t=0.25 and
35/36 at t=0.5/0.75. `artifacts/morph/entrance-hidden-kpi.jpg` shows PowerPoint at
t=0.50 with only a faint title and no KPI content, while DeckCraft shows the
full KPI card row.
The same pattern appears on `vi_brand_seed` s3 (36/36 → 35/36) and the other
Forge slides. This is exactly the T057 observation, now measured. Rung 5 on
the PowerPoint side, 2 on DeckCraft.

**4b. Morph is not shape interpolation.** `T028_showcase_pro` s7 is a camera
morph with **zero** entrance effects, so 4a cannot explain it. The frames still
differ by 64.34 mean / 40.0% `>40`: at t=0.25 PowerPoint has begun the
camera move into the "Grow" card while DeckCraft still shows the quadrant
layout; by t=0.75 PowerPoint is nearly final (`pp_vs_final` 16.7) while
DeckCraft is still far (`dc_vs_final` 62.8). The frames are consistent with a
cross-fade of static slides; DeckCraft does not match shapes by name or
interpolate their geometry. Rung 5 vs 2.

**Falsifier 2 is triggered.** `render-transition` frames are not a proxy for
PowerPoint Morph. The strips are in `artifacts/morph/`; the numeric rows are in
`morph.csv` and `morph_hidden.csv`.

### 5. Round trip — same effect list, not the same play

**5a. Timing nodes rewritten.** Over 7 decks / 67 slides:

| Node | Original | Round trip | Delta | Slides changed |
|---|---:|---:|---:|---:|
| `p:cTn` | 2641 | 2492 | **−149** | 36 |
| `p:anim` | 338 | 245 | **−93** | 33 |
| `p:animEffect` | 356 | 300 | **−56** | 5 |
| `p:cond` | 1831 | 1827 | **−4** | 2 |
| `p:graphicEl` | 24 | 0 | **−24** | 6 (every chart slide) |
| `p:animMotion` | 57 | 57 | 0 | 0 |
| `p:animRot` | 1 | 1 | 0 | 0 |
| `p:animScale` | 54 | 54 | 0 | 0 |
| `p:set` | 578 | 578 | 0 | 0 |
| `p:par` / `p:seq` | 1200 / 57 | 1200 / 57 | 0 | 0 |

The exact effect rewrites (`roundtrip_effects.csv`):

| Class / preset | Effects | Lost | Consequence |
|---|---:|---|---|
| `entr` 42 Ascend | 83 | `ppt_x` (property anim) | from/to are both `#ppt_x`: identity, **no visual change** |
| `entr` 37 RiseUp | 4 | `ppt_x` (identity) + delayed `ppt_y` segment on the two quote slides | second half of the rise lost; layout unchanged |
| `emph` 9 Transparency | 56 | `animEffect` (`filter=image`) | redundant with the retained `set` to 0.5: no visible change |
| `entr` 31 GrowAndTurn | 2 | `style.rotation` (90°→0) | **rotation lost**; small visible change |
| chart build | 24 `graphicEl` | `a:chart bldStep` targets | **series build timing changes**; visible |
| `entr` 42/37 | 87 `ppt_x` | identity property anim | one behaviour less per effect in PowerPoint |

**5b. What PowerPoint parses.** All 67 slides keep the same main-sequence
effect count, effect type, duration, trigger and repeat; all transitions keep
the same entry effect and duration (3954 / 1.5 s for Morph). Behaviour count
drops by **149**: 145 are the property/emphasis behaviours in the table above,
plus 4 on the two `coffee_office_dynamic` quote slides, where the delayed
second `ppt_y` segment of RiseUp and its `p:cond` also disappear (PowerPoint
5 → 3 behaviours for Quote and Author). PowerPoint therefore sees the same
list of effects but fewer internal property behaviours. Rung 4.

Static end state after `convert` is unchanged: mean 0.0 for 6 decks; the photo
deck differs by 0.08 mean / 0.47 max on slides 3 and 8 because **`convert`
drops all 5 SVG blips** (`roundtrip_media.csv`: 5 → 0). A later PowerPoint
shows the raster fallback. Rung 4/5.

**5c. Does PowerPoint play it the same?** One-slide videos, original vs round
trip, aligned on target appearance. A same-file control is 0.0, so the capture
is deterministic.

| Deck / slide | Rewrite exercised | Peak mean | Frames >5 | Settled mean | Verdict |
|---|---|---:|---:|---:|---|
| control (same file twice) | none | 0.00 | 0 | 0.00 | capture is deterministic |
| `vi_chuyen_doi_so` s7 | Ascend `ppt_x` drop | 0.00 | 0 | 0.00 | identical |
| `coffee_report` s7 | Transparency `animEffect` drop | 1.58 | 0 | 0.13 | visually identical |
| `coffee_office_dynamic` s3 | GrowAndTurn rotation drop | 2.37 | 0 | 1.34 | minor visible difference |
| `coffee_office_dynamic` s4 | chart `graphicEl` + rotation | **14.31** | **13** | 1.85 | **chart build runs ahead** |

On the chart slide the round-trip chart build is ahead of the original by up
to 23 frames (0.77 s); fixed-index frames differ by up to 14.3 mean and 13
frames exceed 5. The cause is visible in the XML: `<p:spTgt spid="6"><p:graphicEl>
<a:chart seriesIdx="0" .../></p:graphicEl></p:spTgt>` becomes
`<p:spTgt spid="6"/>`. PowerPoint can no longer bind each effect to a series
build step, so the 2025/2026 series no longer enter in the authored order.
Rung 5.

**Verdict.** `convert` is **not** a safe last writer for a deck whose timing we
authored. It preserves the effect list, transitions and static end state, but
it rewrites chart build targets, drops one rotation behavior, and destroys SVG
icons. Use DeckCraft before the Motion Director, never after it.
`artifacts/morph/roundtrip-anim-*.jpg` show the original/round-trip/diff frames.

### 6. Wiring proposal

`inputs/wiring-proposal.md` proposes, but does not wire:

- `slide_forge.render(..., renderer="auto")`: keep the PowerPoint path first;
  on failure (`no PowerPoint` or `no ffmpeg`), render static frames with
  DeckCraft, set `renderer="deckcraft"`, `frame_source="deckcraft"`,
  `label="DeckCraft render (not PowerPoint)"`, `evidence_rung=2`, `video=None`.
  Never set a `powerpoint` key on the fallback.
- `design_critic`: record `frame_source` in the verdict; `--render deckcraft`
  becomes labelled rung 2; a frame directory can carry `frame_source.json`.
- Do **not** auto-enable frames in `slide_forge.build()`: they add no motion
  evidence and would slow every build.

The contract is implemented in `render_frames_with_fallback()` and unit-tested
(`tests/test_deckcraft_fidelity.py::FallbackTests`). Example:
`artifacts/frame_source_example.json` — `renderer=deckcraft`,
`label="DeckCraft render (not PowerPoint)"`, `evidence_rung=2`, 9 frames.

### 7. Evidence rungs

| Claim | Rung |
|---|---|
| DeckCraft static image differs from PowerPoint by the stated pixels | 3 (PowerPoint side 5, DeckCraft side 2) |
| Critic score delta ≤0.01 | 3 (measurement of two renders) |
| `render-transition` frames differ from `CreateVideo` frames | 3 (PowerPoint side 5, DeckCraft side 2) |
| PowerPoint hides the 36 entrance shapes during Morph | 5 |
| DeckCraft draws 35/36 of them | 2 |
| `convert` rewrites the listed nodes | 1 (file structure) |
| PowerPoint parses the same effect list / fewer behaviours | 4 |
| PowerPoint plays the chart build differently / Ascend identically | 5 |
| `convert` drops 5 SVG blips and 24 chart build targets | 1 (file structure) + 4 (PowerPoint shows the changed static result) |
| DeckCraft frame fallback can be labelled safely | 0/1 (design + unit test), not wired |

## Negative results and limitations

- **Rung 6 not attempted.** No human watched the decks. "Matches" means a
  pixel/model measurement, not an eye test.
- **The static mean is dominated by text antialiasing.** A low whole-slide
  mean can hide a missing icon (0.9% of pixels) or a wrong chart. The per-kind
  table and the object CSV are the useful signal; the whole-slide mean is not
  a quality score.
- **Object attribution is rectangular.** A shape's box may include background
  or another shape behind it; groups are not flattened. Per-kind numbers are
  comparative, not exact.
- **The probe is synthetic.** It was built to expose gradient/effects/text
  cases the corpus lacks; its default chart style exaggerates the chart gap.
  It is labelled `kind_probe` and excluded from the corpus mean.
- **Morph alignment is ±1 frame (33 ms).** The first changed frame is used;
  `CreateVideo` auto-advances click effects and the Forge decks put every
  content shape on an entrance effect, which is why PowerPoint's Morph frames
  are nearly empty. A deck with content visible before Morph may look closer;
  the T028 camera case (no entrance effects) still breaks.
- **The count-up defect contaminates the KPI crop.** Forge draws all count-up
  frames in the static end state (T057 defect 1), so the KPI numbers look
  garbled in both renderers. The Morph conclusion uses shape presence
  (`pp_alpha`/`dc_alpha`), not the legibility of the numbers; the hidden-shape
  count remains valid.
- **`convert` may rewrite more than measured.** SmartArt, 3D models, video and
  audio were not in this corpus. The matrix covers the lab's decks, not the
  whole OOXML surface.
- **Playback was sampled, not exhaustive.** Four slides plus a control; 30 fps
  can miss sub-frame differences. The same-file control rules out capture
  noise, not encoder smoothing.
- **Critic stability is not renderer fidelity.** A +0.01 score delta says the
  critic is insensitive to the breaks, not that DeckCraft is faithful.
- **DeckCraft 0.13.1 only.** A later build may fix SVG, chart or gradient
  support; rerun the matrix before changing the verdict.

## Next

1. **T060 (source study):** expose `render-animation --slide N --click K --t ms`.
   Until that exists, no DeckCraft frame can verify in-slide motion; the lab
   still needs `CreateVideo`.
2. **T062 (asset factory):** use DeckCraft for native shapes/effects, but keep
   the DeckCraft file as the working copy and save the final PPTX with
   python-pptx/our writer. Do not `convert` a timed deck back.
3. **T063 (Forge debt):** rasterise the SVG fallback in
   `slide_forge.py::Builder.icon` (cairosvg/resvg or a solid-glyph PNG) so
   non-SVG readers show the icons; add a DeckCraft render check to the Forge
   acceptance. Also fix the count-up static state (T057 defect 1) before
   judging Morph frames.
4. **T061 (one writer):** add the round-trip table as an acceptance test:
   chart `graphicEl` 24→24, GrowAndTurn rotation present, SVG blips 5→5.
5. **Upstream feedback (through the owner):** DeckCraft needs SVG blips,
   `a:chart bldStep` targets, 3-stop gradients, soft edges/bevels and
   `Segoe UI Semibold` family resolution. A `render-animation` command would
   close the largest verification gap.
6. **Regression gate:** rerun `inputs/commands.md` on each DeckCraft upgrade;
   fail the matrix if chart mean >5, SVG mean >20, text mean >3, or critic
   delta >0.2.

## Review response

Not reviewed yet. Per T057 this task is built by OpenCode and reviewed by
Claude; the review should try the falsifiers itself (critic parity, a Morph
strip, a round-trip video) before accepting the matrix.
