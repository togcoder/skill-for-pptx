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
  1015 × 1200 px, object bbox `198,248 629×881`.
- **Could not access:** a human reader/print test; Illustrator or Inkscape for
  multi-editor parity; OCR or semantic segmentation for text/parts.

## Method

```powershell
# 1. Build the four budgets + the recommended line style, then render.
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
   and removes a narrow skirt below it; this is what stops the silhouette
   stroke from wrapping the cast shadow.
2. **Flatten colour.** Bilateral filter → Lab k-means (5 colours for this
   photo) → 5×5 mode filter → small-region and small-island merge → thin bright
   rim suppression. Colour regions are closed outlines; small holes are filled
   by area-sorted overpainting, which removes brand lettering without OCR.
3. **Extract edges.** CLAHE → bilateral → Scharr magnitude → automatic Canny
   `[51, 136]` → contours inside an eroded mask. **Dedupe:** Canny returns two
   contours per ridge; a 3 px mask with 70% coverage removes the twin.
4. **Classify.** Form: length ≥ 5.5% of the object diagonal, turning rate
   ≤ 0.55°/px, or a meaningful closed loop. Detail: short, strong, and either
   a closed control with a ≥ 3 mm bbox and circularity ≥ 0.28, or a coherent
   short stroke. Everything else is removed with a recorded reason.
5. **Simplify.** RDP ε = 1.2 px (silhouette), 1.1 px (form), 0.8 px (detail),
   1.2 px (colour). Form/silhouette use Catmull–Rom → cubic Bézier with
   corners collapsed onto the vertex when the interior angle is < 102°.
6. **Compose.** Layers: silhouette fill → flat colour → form (silhouette
   outline 4.22 px + form 2.29 px) → detail (1.10 px). At 120 mm width these
   are 0.80 / 0.43 / 0.21 mm. A `line` style keeps the same geometry and drops
   the fills; it is the recommended print deliverable.

**Budgets** (a design decision, not a property of the photo):

| Level | Form cap | Detail cap | What it is for |
|---|---:|---:|---|
| `silhouette` | 0 | 0 | shape check only |
| `form` | 30 | 0 | material blocks + structure |
| `catalogue` | 34 | 16 | recommended controlled illustration |
| `full` | unlimited | unlimited | the naive-trace strawman |

## What changed

- **`scripts/photo_vector.py`** — new module: segmentation, ground-shadow trim,
  colour flattening, edge extraction + dedupe, three-signal classification,
  budgets, RDP/Bézier paths, layered SVG, line style, fidelity/complexity
  metrics, CLI (`build`, `analyze`).
- **`tests/test_photo_vector.py`** — 14 tests: RDP, corner preservation, budget
  monotonicity, form/detail/removal rules, detail cap, scale floor, synthetic
  end-to-end build, silhouette/line layer contracts, SVG accessibility text.
- **`skills/vector-craft/SKILL.md`** — the working method and failure modes.
- **`domains/svg/DOMAIN.md`** — code/data/state/evidence rows for T051.
- **`experiments/T051-.../**`** — source photo, scripts, five SVGs, renders,
  layer sheet, budget sheet, photo comparison, metrics JSON, hashes.

## Decision table

The table is read from the actual counts in `artifacts/levels.json`; the
"count" column is for the `catalogue` build.

| Edge family | Example in this photo | Decision | Rule / reason | Count |
|---|---|---|---|---:|
| Outer silhouette | body, base, portafilter handle, steam wand | **Keep + simplify** | RDP 1.2 px + Bézier; heaviest line (0.80 mm at 120 mm) | 1 path |
| Part boundaries | top panel, group head, drip-tray lip, side panel, cup rails | **Keep** | length ≥ 5.5% diagonal and turning ≤ 0.55°/px | 28 form |
| Closed structural loops | badge ring, control bezels, panel cut-outs | **Keep** | closed, bbox ≥ 3 mm, circularity ≥ 0.28 | 6 form |
| Controls | buttons, knobs, switch plate | **Keep as detail** | short, strong, closed or coherent; 0.21 mm line | 1 closed + 15 short |
| Vents / slots | drip-tray and group slats | **Simplify** | keep a few short strokes, not every slat | part of 15 |
| Brand lettering / decals | “QUICK”, “MOL”, “220 V”, V sticker | **Remove** | tracing produces a scribble; badge remains a shape | 21 |
| Chrome reflections | group-head streaks, rim bands | **Remove / flatten** | replace with 5 flat material tones; the turning-rate rule flagged **0** here, so the form budget did the removal | in 107 |
| Dust, screws, fasteners | tiny rings, specks | **Remove** | below the 3 mm control floor | 25 |
| Cast shadow / reflection skirt | grey puddle under the base | **Trim from silhouette** | lowest dark pixel per column + 3 px; GrabCut IoU 0.966 | — |
| Sub-1.5 mm detail | isolated specks | **Remove** | at 120 mm the stroke is unreadable | 3 |
| Long edges beyond budget | secondary reflections, duplicate rims | **Remove** | over the 34-form budget (this is the group that removes the reflections) | 107 |
| Details beyond budget | extra vents, texture | **Remove** | over the 16-detail budget | 33 |
| Weak / broken fragments | short Canny debris | **Remove** | not a readable control | 48 |

**Simplification is not the same as deletion.** A kept edge is reduced to a few
nodes and rebuilt as a cubic path; the corner-preserving rule keeps the
designer's right angles (panel corners, base) while smoothing chrome contours.
Dedupe is what prevents every real edge from being drawn twice.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| Silhouette is faithful to the segmented object | 1 | delivered-mask IoU **0.998**; raw GrabCut IoU **0.966** (the difference is the deliberately trimmed shadow skirt) |
| The line drawing is a real editable SVG | 1 + 4 | XML parses; 34 form + 16 detail paths; **1,567 nodes**; VectorCraft `info`: 54 paths, 4 groups, 1 layer, 0 warnings |
| Geometry is rendered by the vector tool, not a raster fake | 4 | VectorCraft renders `line.svg`, `catalogue.svg`, `form.svg`, `silhouette.svg`, `full.svg`; previews inspected |
| Detail is capped | 1 | `catalogue` has exactly 16 detail paths; `full` has 49; 33 removed for the detail budget |
| Detail is scale-tested | 1 | smallest kept detail **5.56 mm** at 120 mm; 3 edges removed below 1.5 mm; 25 closed loops below 3 mm |
| The full trace is worse, not better | 1 + 4 | `full`: 141 form + 49 detail, **5,034 nodes**, ink 0.526, visibly scribbled; `catalogue`: 34 + 16, 3,214 nodes, ink 0.338 |
| Flat colour is controlled | 1 | 5 material tones; ΔE76 **9.84** for the colour build; rim suppression and small-region merge |
| Line style is the most readable deliverable | 4 | `line.svg` keeps 34 form + 16 detail at 1,567 nodes; `preview/photo-vs-vector.png` |
| Budget layers are inspectable | 1 + 4 | `preview/layer-stack.png`: silhouette, flat colour, form lines, detail only |
| Tests cover the policy | 1 | 14 tests in `tests/test_photo_vector.py`; full suite **418 tests OK** (8 skipped) |

**Complexity / fidelity table** (120 mm width):

| Build | Form | Detail | Fills | Nodes | Ink / Canny px | Long-edge coverage | GrabCut IoU | ΔE76 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| silhouette | 0 | 0 | 0 | 104 | 0.075 | 0.000 | 0.959 | — |
| form | 30 | 0 | 18 | 2,959 | 0.313 | 0.338 | 0.963 | 10.43 |
| catalogue | 34 | 16 | 26 | 3,214 | 0.338 | 0.375 | 0.966 | 9.84 |
| full | 141 | 49 | 21 | 5,034 | 0.526 | 0.612 | 0.965 | 10.29 |
| **line** | **34** | **16** | **0** | **1,567** | **0.338** | **0.378** | **0.968** | — |

`Ink / Canny px` is kept stroke pixels divided by the raw Canny reference;
`long-edge coverage` is the fraction of ≥55 px reference edges within 2 px of a
kept stroke. They are **not** quality scores: the raw reference includes the
reflections and duplicates we deliberately remove, so a low value is expected.
The visual comparison and the full-trace row are the check that the removal is
selective rather than lazy.

**Hashes:** see `artifacts/SHA256SUMS.txt`.

## Negative results and limitations

1. **The pipeline is not semantic.** It does not know that “QUICK” is a brand or
   that a knob is a control. The circularity/area rules remove most lettering
   and dust, but a human must confirm the result; a different badge or a
   rectangular logo can survive or disappear incorrectly.
2. **The colour style is weaker than the line style.** Flat k-means fills turn
   chrome reflections into dark clumps around the group head, and the colour
   layer obscures the form hierarchy. The line drawing is the recommended
   deliverable; the colour build is a material study, not the hero.
3. **The ground-shadow trim is a heuristic.** It assumes a dark contact line
   under the object. A white product on a white sweep, a glass object or a
   mirror floor can fail. It removed 3.4% of the raw GrabCut mask (IoU 0.959–
   0.968), which is disclosed rather than hidden.
4. **True through-holes are filled.** The mask fills the silhouette and the
   colour regions are painted as solid shapes, so a cup handle or a ring would
   become solid. A paper-coloured hole layer is future work.
5. **Coverage is measured against raw Canny.** The reference contains both
   sides of each ridge and all the removed texture, so coverage is conservative;
   a deduped reference would raise it. The full trace shows the cost of chasing
   coverage: 0.526 ink and a scribble.
6. **The 1.5 mm floor is not the binding constraint here.** The smallest kept
   detail is 5.56 mm; the 3 mm closed-control floor and the 16-detail budget do
   most of the work. The scale rule is still needed for other photos, but this
   one does not prove it alone.
7. **Brand marks are removed, not typeset.** A brand-conscious deliverable needs
   a real logo placed by a designer; tracing lettering at 2–3 mm is worse than
   omitting it.
8. **No multi-editor or print proof.** VectorCraft renders the SVG; Illustrator,
   Inkscape, a PDF/X export and a physical print have not been tested. There is
   no human reader test (rung 6).
9. **The group-head area still has clustered reflection lines.** A human would
   redraw it as two or three clean shapes; the automatic rule keeps some
   coherent streaks because they pass the length/turning test.
10. **The turning-rate rule did not fire on this photo.** At 0.55°/px it
    removed **0** edges: the chrome reflections here are long and smooth, not
    jagged. They were removed by the 34-form budget (107 edges) and by flattening
    them into colour, which is a weaker, less targeted mechanism. A per-region
    reflection detector (low-saturation, low-contrast, adjacent to a highlight)
    is still needed.
11. **One photo, one product.** The thresholds (5.5% diagonal, 0.55°/px,
    3 mm control, 1.5 mm detail) are calibrated on this machine. They are
    parameters, not universal constants; the report gives the values so another
    photo can be tested against them.

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
- Ask an independent agent to review this task before merge.

## Review response

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| — | Pending review. No findings yet. |
