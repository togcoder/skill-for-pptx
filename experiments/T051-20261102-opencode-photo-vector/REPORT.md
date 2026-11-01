# T051 [vector] — Photo-to-vector line hierarchy and detail budget

## Frame

- **Question:** the owner will photograph a product or machine and ask for a
  vector drawing. Which edges must be kept, which simplified, and which removed
  so the result is readable and faithful without becoming a naive auto-trace?
- **Hypothesis:** a three-layer hierarchy — silhouette, form, detail — with
  measurable admission rules and a **scale test** produces a better
  illustration than "trace every Canny edge". Falsifiers: a silhouette that
  drifts from the object; a missing part boundary; a detail budget that fills
  with dust rings; brand lettering traced as a scribble; a cast shadow wrapped
  by the object outline; a full trace that is no worse than the curated one.
- **Domain lens:** SVG 2.0, technical illustration, Canny edge extraction,
  Ramer–Douglas–Peucker simplification, Catmull–Rom → cubic Bézier, and the
  **logic** (not the millimetre values) of ISO 128 line groups: thick visible
  outlines, thin detail. This is not an ISO 128 compliance claim.
- **Transfers:** the photo is segmented/flattened with OpenCV and Pillow; the
  SVG is rendered and inspected by **VectorCraft**; no generative image model
  is used, and no vector geometry is invented beyond the source.

## Frozen input

- **Task/claim:** T051 [vector], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T051-opencode-photo-vector`, based on `main` (`29ce566`).
- **Request/date:** 2026-11-02; the camera illustration was accepted, and the
  next brief is a user-supplied product photo where the detail must be
  controlled — faithful, not naive.
- **Source photo:** Wikimedia Commons, *File:Quick Mill Omre Espresso
  Machine.jpg*, **CC0**, 1531 × 1808 px.
  `https://commons.wikimedia.org/wiki/File:Quick_Mill_Omre_Espresso_Machine.jpg`,
  accessed 2026-11-02. The file is kept locally as `inputs/quickmill.jpg`; the
  licence permits redistribution, and the SVG metadata records source and
  licence.
- **Environment:** Windows 10/11 x64; Python 3.13; OpenCV 4.12.0; NumPy 2.2.6;
  Pillow 11.3.0; VectorCraft `vectorcraft-cli.exe` (ArtCraft). Working image:
  1015 × 1200 px, object bbox `198,250 629×879`.
- **Could not access:** a human reader/print test; Illustrator or Inkscape for
  multi-editor parity; OCR or semantic segmentation for text/parts.

## Method

```powershell
# 1. Build the four budgets, the line style and the full-line strawman.
python experiments/T051-.../inputs/make_study.py
# 2. Isolate the four layers for the layer-stack study.
python experiments/T051-.../inputs/make_layers.py
# 3. Photo vs vector sheet.
python experiments/T051-.../inputs/make_compare.py
# 4. Native geometry inspection.
vectorcraft-cli info artifacts/line.svg
# 5. Tests.
python -m unittest tests.test_photo_vector -v
```

The pipeline in `scripts/photo_vector.py`:

1. **Segment.** GrabCut from a 3% border rectangle, largest external contour,
   close/open. A **ground-shadow trim** finds the lowest dark pixel per column
   in the bottom 20% of the object and removes a narrow skirt below it; this is
   what stops the silhouette stroke from wrapping the cast shadow.
2. **Flatten colour.** Bilateral filter → Lab k-means (5 colours for this
   photo) → 5×5 mode filter → small-region and small-island merge → thin bright
   rim suppression. Colour components are painted **large area first, small
   area last**; small holes are filled by overpainting, which removes brand
   lettering without OCR. The dominant fill (index 1) is skipped because the
   silhouette fill already uses it.
3. **Extract edges.** CLAHE → bilateral → Scharr magnitude → automatic Canny
   `[51, 136]` → contours inside an eroded mask. A contour that walks out and
   back along the same 1 px Canny ridge is split at its farthest point and kept
   as an **open** line; a real ring stays closed. Canny's two parallel contours
   per ridge are then deduped with a 3 px mask at 70% coverage.
4. **Classify.** Form: length ≥ 5.5% of the object diagonal, turning rate
   ≤ 0.55°/px, or a meaningful closed loop (bbox ≥ 3 mm, area ≥ 80 px²).
   Detail: short, strong, and either a closed control with a ≥ 3 mm bbox and
   circularity ≥ 0.28, or a coherent short stroke. Everything else is removed
   with a recorded reason.
5. **Simplify.** RDP ε = 1.2 px (silhouette), 1.1 px (form), 0.8 px (detail),
   1.2 px (colour). Form/silhouette use Catmull–Rom → cubic Bézier with
   corners collapsed onto the vertex when the interior angle is < 102°.
6. **Compose.** Layers: silhouette fill → flat colour → form (silhouette
   outline 4.21 px + form 2.28 px) → detail (1.10 px). At 120 mm width these
   are 0.80 / 0.43 / 0.21 mm. A `line` style keeps the same geometry and drops
   the fills; it is the recommended print deliverable.

OpenCV RNG is seeded (`setRNGSeed(0)`, one thread) so GrabCut, k-means and the
five builds are reproducible.

**Budgets** (a design decision, not a property of the photo):

| Level | Form cap | Detail cap | What it is for |
|---|---:|---:|---|
| `silhouette` | 0 | 0 | shape check only |
| `form` | 30 | 0 | material blocks + structure |
| `catalogue` | 34 | 16 | recommended controlled illustration |
| `full` | unlimited | unlimited | the naive-trace strawman |

## What changed

- **`scripts/photo_vector.py`** — new module: segmentation, ground-shadow trim,
  colour flattening, contour opening/dedupe, three-signal classification,
  budgets, RDP/Bézier paths, layered SVG, line style, fidelity/complexity
  metrics, CLI (`build`, `analyze`).
- **`tests/test_photo_vector.py`** — 18 tests: RDP, corner preservation, budget
  monotonicity, form/detail/removal rules, detail cap, scale floor, synthetic
  end-to-end build, silhouette/line layer contracts, SVG text, **open vs closed
  contour extraction**, **determinism**, **width-dependent 3 mm floor**, and
  **line/colour geometry equality**.
- **`skills/vector-craft/SKILL.md`** — the working method and failure modes.
- **`domains/svg/DOMAIN.md`** — code/data/state/evidence rows for T051.
- **`experiments/T051-.../**`** — source photo, scripts, six SVGs, renders,
  layer sheet, budget sheet, photo comparison, metrics JSON, hashes.

## Decision table

The table is read from the actual counts in `artifacts/levels.json`; the
"count" column is for the `catalogue` build.

| Edge family | Example in this photo | Decision | Rule / reason | Count |
|---|---|---|---|---:|
| Outer silhouette | body, base, portafilter handle, steam wand | **Keep + simplify** | RDP 1.2 px + Bézier; heaviest line (0.80 mm at 120 mm) | 1 path |
| Part boundaries | top panel, group head, drip-tray lip, side panel, cup rails | **Keep** | length ≥ 5.5% diagonal and turning ≤ 0.55°/px | 25 form |
| Closed structural loops | badge ring, panel cut-outs | **Keep** | closed, bbox ≥ 3 mm, area ≥ 80 px² | 9 form |
| Controls and short details | button edges, knobs, vents, switch plate | **Keep as detail** | short, strong, coherent; 0.21 mm line | 16 detail |
| Vents / slots | drip-tray and group slats | **Simplify** | keep a few short strokes, not every slat | in 16 |
| Brand lettering / decals | “QUICK”, “MOL”, “220 V”, V sticker | **Remove** | the line build does not draw the lettering; the colour build keeps a dark badge mark (disclosed) | line: 0; colour: mark |
| Chrome reflections | group-head streaks, rim bands | **Remove / flatten** | high turning rate: 58 edges removed; the rest is flattened into 5 tones | 58 |
| Dust, screws, fasteners | tiny rings, specks | **Remove** | below the 3 mm control floor | 2 |
| Cast shadow / reflection skirt | grey puddle under the base | **Trim from silhouette** | lowest dark pixel per column + 3 px; GrabCut IoU 0.959 | — |
| Sub-1.5 mm detail | isolated specks | **Remove** | at 120 mm the stroke is unreadable | 6 |
| Long edges beyond budget | secondary reflections, duplicate rims | **Remove** | over the 34-form budget | 24 |
| Details beyond budget | extra vents, texture | **Remove** | over the 16-detail budget | 117 |
| Weak / broken fragments | short Canny debris | **Remove** | not a readable control | 18 |

**Simplification is not the same as deletion.** A kept edge is reduced to a few
nodes and rebuilt as a cubic path; the corner-preserving rule keeps the
designer's right angles (panel corners, base) while smoothing chrome contours.
Opening a retraced Canny contour is what prevents every real edge from being
drawn twice; dedupe removes the remaining twin.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| Silhouette agreement is measured, not assumed | 1 | raw GrabCut vs delivered mask **0.959**; the 4% difference is the deliberately trimmed shadow skirt. This is mask agreement, **not** ground-truth object IoU |
| The line drawing is a real editable SVG | 1 + 4 | XML parses; 34 form + 16 detail paths; **1,437 nodes**; VectorCraft `info`: 54 paths, 4 groups, 1 layer, 0 warnings |
| Geometry is rendered by the vector tool, not a raster fake | 4 | VectorCraft renders `line.svg`, `catalogue.svg`, `form.svg`, `silhouette.svg`, `full.svg`, `full-line.svg`; previews inspected |
| Detail is capped | 1 | `catalogue` has exactly 16 detail paths; `full` has 133; 117 removed for the detail budget |
| Detail is scale-tested | 1 | smallest kept catalogue detail **6.19 mm** at 120 mm; 6 edges removed below 1.5 mm; 2 closed loops below 3 mm |
| The full trace is worse at the same style | 1 + 4 | **line** 34 + 16, 1,437 nodes, ink 0.265; **full-line** 58 + 133, 2,268 nodes, ink 0.347; the full render shows badge/vent/dust scribbles |
| Flat colour is controlled | 1 | 5 material tones; ΔE76 **10.56** for the colour build; 15 components after skipping the dominant fill. The badge lettering is a disclosed colour-only artifact |
| Line style is the most readable deliverable | 4 | `line.svg` keeps 34 form + 16 detail at 1,437 nodes; `preview/photo-vs-vector.png` |
| Budget layers are inspectable | 1 + 4 | `preview/layer-stack.png`: silhouette, flat colour, form lines, detail only |
| Tests cover the policy and the bugs | 1 | 18 tests in `tests/test_photo_vector.py`; full suite **422 tests OK** (8 skipped) |

**Complexity / fidelity table** (120 mm width):

| Build | Form | Detail | Fills | Nodes | Ink / Canny px | Long-edge coverage | GrabCut IoU | ΔE76 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| silhouette | 0 | 0 | 0 | 105 | 0.000 | 0.000 | 0.959 | — |
| form | 30 | 0 | 15 | 2,180 | 0.240 | 0.309 | 0.959 | 10.56 |
| catalogue | 34 | 16 | 15 | 2,347 | 0.265 | 0.351 | 0.959 | 10.56 |
| full | 58 | 133 | 15 | 3,178 | 0.347 | 0.456 | 0.959 | 10.56 |
| **line** | **34** | **16** | **0** | **1,437** | **0.265** | **0.351** | **0.959** | — |
| full-line | 58 | 133 | 0 | 2,268 | 0.347 | 0.456 | 0.959 | — |

`Ink / Canny px` is kept internal stroke pixels divided by the raw Canny
reference (the silhouette is **not** counted); `long-edge coverage` is the
fraction of ≥55 px reference edges within 2 px of a kept simplified stroke.
They are **not** quality scores: the raw reference includes reflections and
duplicates we deliberately remove, so a low value is expected. The visual
comparison and the same-style full-line row are the check that removal is
selective rather than lazy.

**Hashes:** see `artifacts/SHA256SUMS.txt`.

## Negative results and limitations

1. **The pipeline is not semantic.** It does not know that “QUICK” is a brand or
   that a knob is a control. The **line** build does not draw the badge
   lettering, but the **colour** build still shows a dark “QUICK” mark inside
   the cream badge; filling the hole or closing it made the mark worse. A real
   text/logo curation step is still needed, and a human must confirm the result.
2. **The colour style is weaker than the line style.** Flat k-means fills turn
   chrome reflections into dark clumps around the group head, and the colour
   layer obscures the form hierarchy. The line drawing is the recommended
   deliverable; the colour build is a material study, not the hero.
3. **The ground-shadow trim is a heuristic.** It assumes a dark contact line in
   the bottom 20% of the object. A white product on a white sweep, a glass
   object or a mirror floor can fail. It removed 4.1% of the raw GrabCut mask
   (IoU 0.959), which is disclosed rather than hidden.
4. **True through-holes are filled.** The mask fills the silhouette and the
   colour components are painted as solid shapes, so a cup handle or a ring
   would become solid. A paper-coloured hole layer is future work.
5. **Coverage is measured against raw Canny.** The reference contains both
   sides of each ridge and all removed texture, so coverage is conservative; a
   deduped reference would raise it. The full-line row shows the cost of
   chasing coverage: 0.347 ink, 133 detail paths, visible scribble.
6. **The 1.5 mm floor is not the binding constraint here.** The smallest kept
   catalogue detail is 6.19 mm; the 16-detail budget (117 removed) and the 3 mm
   control floor (2 removed) do most of the work. The scale rule is still
   needed for other photos, but this one does not prove it alone.
7. **Brand marks are not typeset.** A brand-conscious deliverable needs a real
   logo placed by a designer; tracing lettering at 2–3 mm is worse than omitting
   it. The line style omits the lettering but draws the badge ring as a partial
   oval (thin double contour); the colour style keeps a dark badge mark. Neither
   is a finished brand lock-up.
8. **No multi-editor or print proof.** VectorCraft renders the SVG; Illustrator,
   Inkscape, a PDF/X export and a physical print have not been tested. There is
   no human reader test (rung 6).
9. **The group-head area still has clustered reflection lines.** A human would
   redraw it as two or three clean shapes; the automatic rule keeps some
   coherent streaks because they pass the length/turning test.
10. **The ground-trim scan window is a judgement.** Bottom 20% works for this
    table-top photo; a product whose dark contact line sits above that window
    would not be trimmed, and a dark object inside the window could be cut. The
    <8% area guard limits the damage but is not a proof.
11. **One photo, one product.** The thresholds (5.5% diagonal, 0.55°/px,
    3 mm control, 1.5 mm detail) are calibrated on this machine. They are
    parameters, not universal constants; the report gives the values so another
    photo can be tested against them.

## Review round 1 (Argon) — fixed

Argon reviewed PR #49 and returned **revise** with three blockers and several
majors. The important one was real: `cv2.findContours` traces a 1 px Canny ridge
as a closed polygon that walks out and back, so every open line was classified
`closed=True`, its length was doubled, and the turning-rate rule never fired.
The fix splits the contour at its farthest point when the two halves nearly
coincide; the new regression test draws an open diagonal and a circle and
asserts the diagonal is open and the circle is closed. The turning rule now
removes **58** reflections (it removed 0 before the fix).

| Finding | Response |
|---|---|
| Blocker: Canny retrace misclassified every open edge as closed; doubled paths; turning rule silenced | **Fixed.** `_retraced_half()` + open/closed regression test; 58 reflections now removed |
| Blocker: GrabCut/k-means RNG made the five builds non-deterministic (different bbox/Canny/palette) | **Fixed.** `cv2.setRNGSeed(0)` + one thread; determinism test; line and colour share bbox/canny/counts |
| Blocker: report claimed line and catalogue have the same geometry while they differed | **Fixed by determinism**; regression test `test_line_and_colour_share_geometry` |
| Major: 3 mm control floor hard-coded as 14 px | **Fixed.** `min_control_px = 3.0 / mm_per_px`; width-scaling test |
| Major: form-loop rule did not match the decision table | **Fixed.** bbox ≥ 3 mm and area ≥ 80 px²; report matches |
| Major: delivered-mask IoU 0.998 was circular | **Removed.** Only GrabCut mask agreement 0.959 remains, labelled as not ground truth |
| Major: edge metrics used raw points and included the silhouette with mismatched kernels | **Fixed.** Simplified strokes, silhouette excluded; table regenerated |
| Major: painter's order used global label area | **Fixed.** Components sorted by component area; dominant fill skipped |
| Major: ground trim could cut the body | **Fixed.** Scan only the bottom 20% of the object |
| Minor: default 6 colours vs documented 5 | **Fixed.** Default 5 |
| Minor: dead code; closed details not smoothed; absolute paths | **Fixed.** Dead loop removed; closed details smooth; relative paths in `levels.json` |
| Major: line vs full compared different styles | **Fixed.** `full-line` built at the same style; 1,437 vs 2,268 nodes |

## Next

- Add a **curation hook** (include/exclude boxes, keep/remove path IDs) so a
  human can correct semantics without editing SVG by hand.
- Add a **paper layer** for true through-holes and a `--ground=none|ellipse|trace`
  option that separates shadow from object.
- Test five product classes: light-on-light, dark-on-dark, glass, fabric,
  reflective metal; report where the ground trim and the control floor fail.
- Add a **stroke-width ramp** per material and an ink-coverage target, not only
  path counts.
- Run Inkscape and Illustrator parity, a PDF/X export and a 120 mm print.
- Add a small human preference test: line vs colour vs full trace.
- Ask Argon to re-review this revision before merge.
