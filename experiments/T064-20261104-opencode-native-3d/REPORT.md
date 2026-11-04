# T064 [pptx] — Review and decoupling of T055 native 3D, and Morph between two camera views

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash), subagent of the T058–T065
  programme. **Date:** 2026-11-04.
- **Branch:** `work/T064-opencode-native-3d`, base `main` @ `ac5b45e`.
- **Brief:** `experiments/T057-20261104-claude-leader-review/REPORT.md`,
  section "T064".
- **Deliverables:** this report; `REBASE.md` (dependency map, rebase plan and
  execution); `research/reviews/T055-opencode-20261104.md` (the REVIEW.md
  critique of T055, findings R1–R10); the probe scripts in `inputs/`; the
  frames in `preview/`.

## Frame

**Question 1 — dependency.** Which T054 commits and files does
`work/T055-opencode-pptx-3d` actually need, and can T055 be rebased onto `main`
without changing any of its evidence?

- Hypothesis: the only real dependency is the `blockout.json` geometry read by
  `make_product_glb.py`; the GLB is an input artifact, not a child of T054.
- Falsified if: T055 imports T054 code, shares a module or test fixture, or the
  GLB cannot be reproduced from a frozen copy of the blockout (in which case
  the deck and its evidence would have to be rebuilt).

**Question 2 — Morph.** Does PowerPoint Morph between two camera views of the
same 3D model play, at rung 5 (`CreateVideo`, frames reported)?

- Hypothesis: Morph interpolates the `am3d:camera`, so the transition shows one
  model sweeping from view A to view B.
- Falsifiers: (a) the model cross-fades and the camera never moves; (b) the
  transition is silently replaced by Fade; (c) the model is absent during the
  transition.

**Domain lens.** PowerPoint native 3D: `am3d:model3d`, `am3d:camera`,
`p159:morph`, `Presentation.CreateVideo`, COM `Shape.Model3D`. The design canon
is the pptx card (`domains/pptx/DOMAIN.md`): native, editable output, motion
follows the narrative, preserve object identity.

**Transfers.** From the vector domain: T054's SolidCraft CSG blockout, used as
a mesh source only. From the DeckCraft study (T057): nothing here — DeckCraft
does not render in-slide 3D. No other-domain idea is imported untested.

## Frozen input

| Item | Value |
|---|---|
| Request | T057 brief, T064 row: rebase T055 off T054, review it, test Morph between camera views |
| Base | `main` @ `ac5b45e` ("T058-T065: claim the next research programme") |
| T055 as reviewed | branch head `addd340`, rebased here as `49cfeee…6a60036` |
| GLB under test | `inputs/quickmill-blockout.glb`, 56,544 B, SHA-256 `fd252d7c6e2470b9809766d9dcba0bbd546c8169209b7426ea6ceb363f959143` (byte copy of the T055 artifact) |
| Blockout (frozen) | `inputs/T054-blockout.json`, 12,357 B, SHA-256 `86bf30f8fe649a261c8aeb0ee0cc359c0b3e16d6a2bed86126de371342cd389b`, from T054 `b387146` |
| Environment | Windows 10/11 x64; PowerPoint 16.0 build **17932** (COM); Python 3.13.5; pywin32; trimesh 5.2.0; Pillow; numpy; PyMuPDF; ffmpeg 8.1.1 |
| Could not access | a live slide-show session with a human (rung 6); the T058 click harness; a second 3D model to test generality |

## Method

Run from the repository root, in this order. Every script is deterministic and
writes its own evidence JSON.

```powershell
$env:PYTHONUTF8=1

# 1. the two-view probe: same GLB, same shape name, cameras A and B
python experiments/T064-20261104-opencode-native-3d/inputs/build_camera_morph.py

# 2. Morph on slide 2 (scripts/add_morph.py structure) + a Fade control deck
python experiments/T064-20261104-opencode-native-3d/inputs/patch_transitions.py

# 3. variants that isolate what Morph matches
python experiments/T064-20261104-opencode-native-3d/inputs/shared_media_variant.py   # one GLB + one raster
python experiments/T064-20261104-opencode-native-3d/inputs/shared_model_only.py       # one GLB, two rasters
python experiments/T064-20261104-opencode-native-3d/inputs/duplicate_slide_probe.py   # duplicate-slide authoring path

# 4. rung 5: PowerPoint's own renderer, 1920x1080, 30 fps
python experiments/T064-20261104-opencode-native-3d/inputs/create_video.py

# 5. read the video: contact sheets, camera ladder, fits, control-square track
python experiments/T064-20261104-opencode-native-3d/inputs/camera_ladder.py
python experiments/T064-20261104-opencode-native-3d/inputs/make_sheets.py
python experiments/T064-20261104-opencode-native-3d/inputs/fit_views.py
python experiments/T064-20261104-opencode-native-3d/inputs/fit_interpolated.py
python experiments/T064-20261104-opencode-native-3d/inputs/track_square.py
python experiments/T064-20261104-opencode-native-3d/inputs/measure_gap.py

# 6. keep the committed evidence portable (no absolute worktree paths)
python experiments/T064-20261104-opencode-native-3d/inputs/normalize_evidence.py

# 7. the review of T055 (commands in the review file)
python -m unittest tests.test_product_deck_3d -v
python -m unittest discover -s tests
python lab/tools/check_layout.py
```

**How frames are read.** Three independent measurements, so no conclusion rests
on one metric:

1. **Contact sheet** (`preview/transition-sheet-*.png`): one cell per 0.1 s,
   cropped to the model. A fade shows two silhouettes in one cell; a camera
   move shows one.
2. **Camera ladder fit** (`preview/interpolated-fit.json`): 25 static slides of
   the same model, camera x from −1.2 to +1.2 in 0.1 steps, exported at
   1920 × 1080. Every video frame is fitted to a brightness scale `s` and a
   blend weight `w` between adjacent rungs, so a frame that is one dimmed render
   is explained with `s ≈ 1` (or a low `s` when it fades) and a small residual,
   while a cross-fade cannot be explained by any single camera.
3. **Control square** (`preview/square-track.json`): an amber 60 × 60 pt shape
   named `ProbeSquare` on both slides, at x = 300 pt on slide 1 and x = 860 pt
   on slide 2, in a band above the model. If Morph is really playing, one square
   travels; if the transition were a fallback, two squares would cross-fade.

## Evidence

### 1. Dependency and rebase (rung 1)

| Fact | Measurement |
|---|---|
| Hard dependency on T054 | one file, one line: `make_product_glb.py:33` absolute path to the T054 worktree |
| T054 commits in the T055 branch | 5 (`2c6e089`, `dac65c3`, `26759ac`, `d1feb1f`, `b387146`) |
| T055 commits rebased | 5 (`64d6d47`→`49cfeee`, `e71e0aa`→`bc7b3e9`, `1a309d5`→`9dd7b62`, `ec5bf8f`→`bdbcec5`, `addd340`→`6a60036`) |
| GLB rebuilt from `inputs/blockout.json` | 56,544 B, SHA-256 `fd252d7c…f959143` — **byte-identical**, so no deck, PDF, audit or test changed |
| T054 files left in the branch | none |
| T055 tests after the rebase | 10 tests, OK |
| Full suite after the rebase | 471 tests, 8 skipped, 0 failures (`PYTHONUTF8=1`) |

Detail and the conflict policy: `REBASE.md`. The verdict on T055:
`accept-with-fixes` (`research/reviews/T055-opencode-20261104.md`), with R1
(dependency) and R5 (absolute evidence paths) fixed by this rebase and R2
(CreateVideo argument order) corrected and re-measured here.

**Answer to question 1:** T055 needed exactly one T054 *file*, not the T054
*task*. After freezing that file, T055 is independent and can merge before,
after or without T054.

**Review of T055 — findings.** Full text and commands:
`research/reviews/T055-opencode-20261104.md`. Verdict `accept-with-fixes`.

| # | Severity | Finding | State |
|---|---|---|---|
| R1 | blocking | `make_product_glb.py` read the T054 worktree at an absolute path; the task could not build elsewhere | **fixed here** (frozen `inputs/blockout.json`, byte-identical GLB) |
| R2 | major | `CreateVideo(path, 3, 3, 30, 85)` set the height to 30 px; the "52 × 28 clip" negative result was a bug, not a PowerPoint limit | **fixed here** and re-measured at 1920 × 1080 |
| R3 | major | the claim says "named camera views and Morph"; the deck has one camera and no transition | author |
| R4 | major | 911 KB of unverified Morph decks committed as artifacts | author (delete) |
| R5 | major | evidence JSON stored machine-absolute paths | **fixed here** (`normalize_evidence.py`) |
| R6 | minor | the deck camera `z = 2.10` is not study view B `z = 2.50` | author |
| R7 | minor | the PDF test asserts only `size > 100 000` | author |
| R8 | minor | claim scope names scripts that do not exist | author |
| R9 | minor | lighting observations are prose, not tests; pin the PowerPoint build | author |
| R10 | process | reviewer and author are the same model family | owner |

### 2. The probe decks (rung 1/4)

| Deck | Slides | Model parts | Transition on slide 2 | `EntryEffect` |
|---|---|---|---|---|
| `camera-morph-base.pptx` | 2 | 2 (`model3d1`, `model3d2`) | none | 0 / 0 |
| `camera-morph.pptx` (variant A) | 2 | 2 | `p159:morph`, `p14:dur=2000`, fade fallback | 0 / **3954** |
| `camera-fade.pptx` (control) | 2 | 2 | plain `p:fade` | 0 / **3849** |
| `camera-morph-shared.pptx` (B) | 2 | **1** (`model3d1`) | `p159:morph` | 0 / **3954** |
| `camera-morph-modelonly.pptx` (C) | 2 | **1** (`model3d1`) | `p159:morph` | 0 / **3954** |
| `camera-morph-duplicated.pptx` (D) | 2 | **1** | `p159:morph` | 0 / **3954** |

Camera A `(-1.20, 0.45, 2.20)`, camera B `(1.20, 0.45, 2.20)`, look-at
`(0, 0.28, 0)`, model rotation `(6, 0, 0)`, FOV 40 on both slides. Everything
else on the slide is identical. `EntryEffect` 3954 is PowerPoint's Morph, 3849
its Fade: the two decks are parsed differently, so the Morph XML is live and
not being dropped.

### 3. Rung 5: PowerPoint's own video (1920 × 1080)

| Deck | CreateVideo status | Resolution | Duration | MP4 |
|---|---|---|---|---|
| variant A (Morph) | 3 (done) | 1920 × 1080 | 10.10 s | 1,144,545 B |
| fade control | 3 (done) | 1920 × 1080 | 9.11 s | 961,039 B |
| variant B (one model part, one raster) | 3 (done) | 1920 × 1080 | 10.10 s | 1,416,493 B |
| variant C (one model part, two rasters) | 3 (done) | 1920 × 1080 | 10.10 s | 1,416,493 B |
| variant D (duplicate slide) | 3 (done) | 1920 × 1080 | 10.10 s | 1,152,677 B |

The video files stay local (`*.mp4` is git-ignored); the frames and the
measurements are committed.

**Control: is Morph actually playing?** Yes. In both the Morph video and the
Fade video the amber square is present, but only the Morph video shows it
*moving*:

| t (s) | Morph: square blobs / centre x (px) | Fade: blobs / centre x |
|---|---|---|
| 4.0 | 1 / 659.5 | 1 / 659.5 |
| 4.2 | 1 / 747.0 | 1 / 659.5 |
| 4.4 | 1 / 935.0 | 0 / — (both at 50 %, below threshold) |
| 4.6 | 1 / 1146.0 | 0 / — |
| 4.8 | 1 / 1337.0 | 1 / 1779.5 |
| 5.0 | 1 / 1493.0 | 1 / 1779.5 |
| 5.8 | 1 / 1770.0 | 1 / 1779.5 |

One square, monotone travel, ~1.7 s: Morph runs. In the Fade control the square
never travels; it is at one end or the other.

### 4. The 3D model during the transition — three outcomes

| Deck | Model present? | Camera x(t) | Brightness scale | Residual to best camera fit |
|---|---|---|---|---|
| **Variant A** (T055's structure: one embed per slide) | fades: `s` 0.79 → 0.34 → **12 frames at background, 13 under peak 40/255 (0.43 s)** → 0.32 → 0.99 | fixed at −1.19 while fading out, fixed at +1.19 while fading in | 0.34 … 0.99 | 3.3 → 10.4 (dimming), 1.6 at the end |
| **Fade control** | both views at once (ghosting) | jumps A → B | ≈ 1 | **22–32** at mid-transition — no single camera explains it |
| **Variant B/C/D** (one shared model part) | continuous, never dims | **−1.01 → −0.61 → +0.59 → +0.72 → +0.84 → +0.93 → +1.01 → +1.08 → +1.12 → +1.16 → +1.19 → +1.20** | **0.995–0.996** | 5.6–14.9 (mid-move), 1.99 at rest |

The camera positions in variant A are the two end values and nothing in
between; the brightness scale is the animated quantity. That is a fade of a
static render, not a camera move. In variants B, C and D the brightness never
changes and the camera position advances monotonically across 1.7 s: that is
the camera interpolating. The three variants differ only in how the shared part
is produced — XML rels with one raster (B), XML rels with two rasters (C), or
PowerPoint's own duplicate-slide (D) — and their frame fits are identical to
three decimals.

`preview/transition-sheet-shared.png` is the visual proof: one model at
intermediate angles (yellow left face rotating out of view, bay coming to the
front), no double silhouette. `preview/transition-sheet-fade.png` is the
control: two models ghosted over each other at 4.4–4.8 s.
`preview/transition-sheet-morph.png` is variant A: the model dims out, four
blank frames, then dims in at the other camera.

**What makes the difference.** Not the GLB bytes — `model3d1.glb` and
`model3d2.glb` are the same size and the same model. It is **part identity**:
variant B points slide 2 at slide 1's `ppt/media/model3d1.glb`; variant C leaves
each slide its own raster but shares the model part, and its frames are
identical to B's. So the `am3d:raster` preview image is irrelevant, and the
model part is what Morph matches.

**The authoring recipe that produces it** (variant D, `duplicate_slide_probe.py`):
insert the model once, **duplicate the slide**, then change the camera on the
copy. PowerPoint keeps one `ppt/media/model3d1.glb` and writes one raster per
camera; Morph then sweeps the camera. Building each slide with its own
`Shapes.Add3DModel` (what T055 did) creates two model parts, and Morph degrades
to the fade.

**Answer to question 2:** Morph between two camera views of the same 3D model
does play — with one shared `model3d` part, rung 5, frames in
`preview/transition-sheet-shared.png`. With one embedded copy per slide it
falls back to a fade-out/fade-in with a 0.40 s blank gap, which confirms the
brief's falsifier *for that construction only*.

### 5. Claims and rungs

| Claim | Evidence | Rung |
|---|---|---|
| T055 needs one T054 file, not the T054 task | dependency inventory; rebuild reproduces the GLB hash | 1 |
| The rebase changes no T055 evidence | identical GLB SHA-256; 10 tests OK; full suite OK | 1 |
| PowerPoint parses `p159:morph` in these decks | `EntryEffect` 3954 vs 3849 for `p:fade` | 4 |
| Morph plays in PowerPoint's renderer | control square travels 659→1779 px, one blob, no ghosting | 5 |
| Morph does **not** move the camera when each slide owns a model part | camera x stays at the end values; brightness ramps 0.34→0.99; 13 frames under peak 40/255 | 5 |
| Fade (control) is a cross-dissolve, not a dip | residual 22–32 to any single camera at mid-transition | 5 |
| Morph **does** move the camera when the slides share one model part | camera x −1.01→+1.20 monotone; brightness 0.995 constant | 5 |
| Duplicating a slide then editing the camera produces the shared part | package: 1 `model3d1.glb`, 2 rasters; same frame fits | 4/5 |
| The `am3d:raster` preview is not what Morph matches | variant C (distinct rasters, shared model) identical to B | 4/5 |
| T055's native 3D claims (Type 30, camera persistence, embedded GLB, editable callouts, PDF) | see the review; reproduced here | 4/5 |
| Human approval of the result | not obtained | 6 (missing) |

### 6. Files

| File | Bytes | SHA-256 |
|---|---:|---|
| `inputs/quickmill-blockout.glb` | 56,544 | `fd252d7c6e2470b9809766d9dcba0bbd546c8169209b7426ea6ceb363f959143` |
| `inputs/T054-blockout.json` | 12,357 | `86bf30f8fe649a261c8aeb0ee0cc359c0b3e16d6a2bed86126de371342cd389b` |
| `artifacts/camera-morph-base.pptx` | 464,725 | `46fac2f03213796681be331266f207c9ed5706478daeecf9656a5a9148327ff1` |
| `artifacts/camera-morph.pptx` | 462,374 | `4ba96f1bdaadf99958b77a7fba5b9728497efb7a2414ae9813bc376f0ff941a3` |
| `artifacts/camera-fade.pptx` | 462,307 | `92095a5f89891cc69aca03321d9fd753d74e401b498b6658628eacf678f80207` |
| `artifacts/camera-morph-shared.pptx` | 253,313 | `c38c243efbc7850eac3825e6e5f727a52f721d604281d93aafd4ffef99ecd175` |
| `artifacts/camera-morph-modelonly.pptx` | 462,374 | `4831a6121b35e6b645506a86e62f4f339dd41a161cf73fdb8235b775228438f5` |
| `artifacts/camera-morph-duplicated.pptx` | 364,811 | `83c6f9db04bb26c91bccec9fc4a6596eaa8a30b4b0d81ed181d98e4b5cf84ce1` |
| `preview/transition-sheet-morph.png` | 454,434 | `a4f0a756d77963160afcd987d6fd8f6e517555fd17420e27ee41df5f0aedf816` |
| `preview/transition-sheet-fade.png` | 520,050 | `ee9b84bd209f310ab3e1d88da0e9375f1326bf7ea0c926e4f95fb2371531f831` |
| `preview/transition-sheet-shared.png` | 685,714 | `dced716b3dff9af99827ef45e3a3122576ffdd6f9d8e24a278770232d378e976` |

Committed task weight ≈ 5.6 MB including the T055 files this task does not own
(the four MP4s stay local and are git-ignored). The 25-rung ladder is
regenerated by `camera_ladder.py`; only the three key rungs are committed.

## Negative results and limitations

- **T055's own deck never had a Morph transition.** The re-audit finds no
  `<p:transition>` on any slide, and all three slides use the same camera
  `(-0.85, 0.45, 2.10)`. Its "named camera views and Morph" claim is not
  supported (review R3).
- **T055's "52 × 28 clip" was a bug, not a PowerPoint limit.** `CreateVideo`'s
  arguments were in the wrong order; the corrected call renders 1920 × 1080.
- **Morph does not animate the camera with per-slide embeds.** This is the
  construction `Shapes.Add3DModel` produces naturally, so the default authoring
  path fails the test.
- **The fade is a sequential dip, not a cross-dissolve.** Variant A dims the
  outgoing render, is at background level for 12 frames (0.43 s under peak
  40/255 at 30 fps, `preview/variantA-gap.json`), then dims the incoming one.
  Calling it "a cross-fade" would be wrong; the Fade control is the
  cross-dissolve, and it ghosts.
- **Residuals are not zero during the sweep** (5.6–14.9 vs 2.0 at rest). The
  ladder is sampled every 0.1 camera units and the true camera is between
  rungs; a 0.05 shift on a high-contrast edge costs several grey levels. The
  monotone camera estimate and the constant brightness, not the residual alone,
  carry the claim.
- **CreateVideo is not an interactive slide show.** It auto-advances and renders
  with PowerPoint's own compositor; whether the live show looks identical
  (especially the 3D re-render during the transition) is rung 6 and untested
  here. T058's harness is the right tool.
- **One model, two cameras, one PowerPoint build (16.0.17932).** Other models
  (textures, animation, many nodes) and other builds may behave differently.
- **Same-family review.** The T055 critique is by the same model family as the
  author; it is a second pass, not the different-family review the protocol
  prefers.
- **The full suite needs `PYTHONUTF8=1` on this host** (cp1258 locale); without
  it, 12 unrelated tests fail on `Path.read_text()` with no encoding. That is a
  pre-existing lab defect for T065, not a T055 regression.

## Next

1. **Forge layout `product3d`.** Build it on the rule this task established:
   insert the model once, duplicate the slide, then set per-view cameras, so the
   model part is shared and Morph works. Wire `Model3D` camera setters into the
   Forge spec (`{"view": {"camera": [...], "look_at": [...], "fov": ...}}`).
2. **A Morph-3D guard.** `morph_studio.py` / `add_morph.py` should refuse, or
   warn, when consecutive slides carry different `model3d` parts: that is the
   silent-fade condition found here.
3. **T055 author response.** R3, R4, R6, R7, R8 are small fixes; R4 (delete the
   unverified Morph decks) also removes 911 KB.
4. **Live verification.** Run T058's harness on `camera-morph-shared.pptx` to
   move the camera claim from rung 5 to rung 6 without a human in the loop, or
   record a human play-through.
5. **Generality.** Repeat the probe with a textured, higher-poly GLB and on a
   second PowerPoint build; publish the result as a pptx design rule only when
   it holds twice.
6. **DeckCraft cross-check (T059/T060).** Its `render-transition` should show
   the same sweep for variant B; if it does, it becomes a cheap Morph QA path.
   If not, its Morph fidelity is disproved for 3D.

## Review response

Pending. This report has not been reviewed yet; T064 is itself the reviewer of
T055, so another agent (preferably Claude or Argon) should review this work
before any of it enters `knowledge/` or a product path.
