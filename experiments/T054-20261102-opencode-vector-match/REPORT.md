# T054 [vector] — Comparative match to the source photo

## Frame

- **Question:** T053 is a semantic reconstruction, but the owner still reads it as
  squat, boxy and wrong in depth.  A single render hides the size of that error.
  What changes when the source photo and the vector are put together at the same
  machine height and measured on the same landmarks?
- **Hypothesis:** the difference is a proportion problem before it is a detail
  problem.  If the silhouette aspect and six vertical landmark fractions are
  matched, the remaining work is local shape (group head, tray, reflections), not
  a redraw from zero.
- **Falsifiers:** the vector only fits after non-uniform stretching; the group
  head is still a cube; the portafilter is not angled; the badge is circular; the
  tray is a shelf; the silhouette is off by more than 5%; the landmark deltas stay
  above 0.02 of body height.
- **Domain lens:** SVG 2.0, axonometric projection, product illustration,
  painter's order, photo/vector comparison.
- **Transfers:** the CC0 photo is the reference; the SVG is drawn from primitives.
  The comparison harness uses OpenCV/Pillow only to measure, not to trace.

## Frozen input

- **Task/claim:** T054 [vector], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T054-opencode-vector-match`, based on `main` (`f648ace`).
- **Request/date:** 2026-11-02. The owner says the difference is obvious when the
  source and the vector are placed together, especially to someone who knows the
  machine.
- **Source photo:** Wikimedia Commons, *File:Quick Mill Omre Espresso Machine.jpg*,
  **CC0**, 1280 × 1512 px.
  `https://commons.wikimedia.org/wiki/File:Quick_Mill_Omre_Espresso_Machine.jpg`,
  accessed 2026-11-02.
- **T053 reference:** `experiments/T053-.../preview/quickmill-reconstruction.png`,
  2000 × 2000 px.
- **Environment:** Windows 10/11 x64; Python 3.13; OpenCV 4.12; Pillow; VectorCraft
  `vectorcraft-cli.exe`; no Illustrator/Inkscape, no print proof, no human test.

## Method

1. **Crop both images to the full machine** (knobs included, base bottom):
   - photo `(220, 300, 1100, 1400)`;
   - T053 `(500, 530, 1730, 1800)`;
   - T054 `(250, 70, 1750, 1930)`.
2. **Scale both to the same machine height** (1000 px); never stretch one axis.
3. **Make three views:** side-by-side, 50 % blend, and an edge map
   (photo red, vector blue).
4. **Measure six landmark rows** as fractions of body height:
   top-panel top, black-band bottom, group-head centre, tray top, lower-panel top,
   base top, base bottom.  The photo rows are manual; the T054 rows are projected
   from object coordinates.
5. **Rebuild the scene from the fractions**, then re-run the comparison.

```powershell
python experiments/T054-.../inputs/make_compare.py
python experiments/T054-.../inputs/make_before_after.py
vectorcraft-cli convert .../quickmill-t054.svg .../quickmill-t054.png --scale 2
vectorcraft-cli info .../quickmill-t054.svg
python -m unittest tests.test_vector_match -v
```

## Research first

Searched 2026-11-03, before changing the scene:

- **fSpy — camera matching from vanishing points** (basics and source):
  <https://fspy.io/basics>, <https://github.com/stuffmatic/fSpy>.  fSpy estimates
  focal length, orientation and position from two or three perpendicular
  vanishing-point pairs.  It confirms that a photo with converging verticals
  cannot be matched by an axonometric projection.
- **Single View Metrology** (MIT vision book chapter; Criminisi et al.):
  <https://visionbook.mit.edu/3d_scene_understanding_single_view.html>,
  <https://www.cs.cmu.edu/~ph/869/papers/Criminisi99.pdf>.  The useful part is
  measuring a box and placing points on a face from one image using vanishing
  points and cross-ratios.
- **fSpy/Blender camera-match workflow**:
  <https://fspy.io/tutorial>.  Two-point perspective plus a principal point is
  enough for this machine; the verticals are close to parallel in the photo.
- **Quick Mill Omre references**: the Home-Barista restoration thread
  (`t29137`), the Orphan Espresso video `YRbjsZWRjC8`, eBay listing `267191254986`
  and the Fondazione Fiera archive.  The thread/listing returned 403; the video
  page and archive were reachable.  They were used only to confirm the machine's
  front layout, not as a second tracing source.

No ready-made "photo → clean vector product illustration" pipeline was found.
The applicable solution is: calibrate one camera or one face plane, verify the
face assignment on the photo, then redraw the primitives.  A six-corner pinhole
fit (`inputs/calibrate_camera.py`) reached **RMS 33 px**, too loose to drive the
final scene; it is recorded as a failed calibration, not used as evidence.  The
clear, verified result is the **front-face split** and switch placement below.

## Measurement, before and after

| Metric | Photo | T053 | T054 | T054 − photo |
|---|---:|---:|---:|---:|
| Machine aspect W/H | **0.800** | 0.969 | **0.806** | +0.006 |
| Black band bottom | **0.216** | 0.312 | **0.216** | 0.000 |
| Group-head centre | **0.275** | 0.424 | **0.276** | +0.001 |
| Tray top | **0.520** | 0.496 | **0.520** | 0.000 |
| Lower-panel top | **0.618** | 0.632 | **0.618** | 0.000 |
| Base top | **0.843** | 0.888 | **0.843** | 0.000 |

The T053 errors were structural: the body was **21 % too wide for its height**,
the group head sat **15 points of body height too low**, the black band extended
**10 points too far down**, and the base was too tall.  T054 moves all six
landmarks onto the photo's fractions.

### The face that was wrong

The photo's upper front is **not a full-width black band**.  On the front face
(`x = 390..930` in the photo) the chrome/black seam is at `x ≈ 600`, so the
front is **39 % chrome on the left and 61 % black on the right**.  The switch
plate (`x ≈ 455..600`) ends exactly at that seam; it sits under the **chrome
left panel**, not under the black badge panel.

T053 and the first T054 pass painted the whole upper front black.  That made the
switch plate read as if it were on a different face.  T054 now uses
`front_split_frac = 0.40`: the chrome left panel runs from `x0` to the split,
the black badge panel from the split to `x1`, and the switch plate's right edge
is the split.  The badge stays on the black panel.

Evidence: `preview/photo-top-grid.png` (photo coordinates), `preview/compare-t054.png`
(50 % overlay), `preview/t053-vs-t054.png`.

**What changed in the scene**

- `Dimensions`: width 80, height 118, depth 60; base 18.5, lower 26.6, tray 11.5,
  tower 55.6, top 5.8, black band 19.7.
- Projection: `X = 223 + 7.0x − 2.42z`, `Y = 940 − 6.95y − 0.90z` (less top-down,
  more front-on than T053).
- Top panel is **chrome**; the upper front is split: chrome left panel, black badge panel on the right; the switch plate ends at the split.
- Badge is an **oval** (7.8 × 9.6) with live `QUICK` / `MOL` / `OMRE` type.
- Group head is a compact chrome overhang over a visible vertical cylinder, with
  a round collar, dark gasket and a **chrome basket**; the handle is a thick,
  straight black tube angled down/right, drawn after the steam wand.
- Steam wand is on the right, behind the handle, not across it.
- Tray is a deep black box with a visible grid and a chrome lip, not a shelf.
- Yellow side has two screw holes and a joint line; the lower panel has stronger
  chrome bands; knobs are smaller; the top has a shallow warmer recess, not four
  heavy rails.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| The comparison is reproducible | 1 | `inputs/make_compare.py`, `inputs/make_before_after.py`; fixed crops and rows |
| T054 matches the six photo landmark fractions | 1 | `preview/measure-t054.json`; deltas 0.000–0.001 |
| T054 is much closer in silhouette | 1 | aspect 0.806 vs 0.800; T053 was 0.969 |
| The SVG is semantic and editable | 1 | 16 groups, 117 paths, 6 text elements; no `<image>` |
| It renders in the vector tool | 4 | VectorCraft: 16 groups, 118 path objects, 6 types, 0 warnings |
| The scene is parametric and deterministic | 1 | `Dimensions(width=74)` changes the SVG; two builds equal |
| The photo and both vectors are visibly comparable | 4 | `preview/t053-vs-t054.png`, `preview/compare-t054.png` |

**Files**

- `artifacts/quickmill-t054.svg`, `artifacts/info.json`, `SHA256SUMS.txt`
- `preview/quickmill-t054.png` (2×)
- `preview/compare-t054.png` (source, T054, 50 % overlay, edges)
- `preview/t053-vs-t054.png` (source, T053, T054 at matched height)
- `preview/measure-t054.json` (landmark table)
- `preview/photo-top-grid.png` (front-face coordinates)
- `preview/camera-fit.json` (failed 6-corner fit, RMS 33 px)
- `tests/test_vector_match.py` (5 tests)

## Negative results and limitations

1. **Axonometric vs camera perspective.**  T054 matches the landmark fractions
   and the face split, but a parallel projection still cannot reproduce the
   photo's converging verticals.  A six-corner pinhole fit reached RMS 33 px and
   was not good enough; a proper fSpy/vanishing-point camera is the next real
   improvement, not more decoration.
2. **The group head is still simplified.**  It is a chrome overhang + cylinder +
   basket, not the full cast group, shower screen, solenoid or portafilter
   geometry.  It reads as a group head now, but a machinist would still see the
   simplification.  The switch plate is placed by the photo's seam, not by a
   measured switch cutout.
3. **Chrome is a designed gradient.**  There are no photographic reflections,
   brushed-metal texture, scratches or dents.  The reference photo's chrome is
   doing a lot of the identity work; flat bands cannot match it.
4. **The badge is live type.**  A machine without the font will substitute; a print
   master needs outlines or an embedded font.  The tiny `OMRE` line is nearly
   illegible at the report size.
5. **The tray grid and controls are patterns, not measured parts.**  The tray
   slots, switch paddles and side screws are placed by proportion, not extracted
   from the photo.
6. **One view.**  Hidden faces, the back and the top-left corner are designed, not
   observed.  A second photo would change the model.
7. **No human test, no print proof, no Illustrator/Inkscape parity.**  VectorCraft
   is rung 4; a physical print and a second editor are still open.
8. **Camera calibration failed on this photo.**  A six-corner pinhole fit reached
   RMS 33 px (`preview/camera-fit.json`); a two-vanishing-point fit from the
   visible box edges put both VPs on the same side and produced no real focal
   length.  The photo is low-resolution, partly occluded and slightly inconsistent
   as a box.  A perspective camera is therefore not claimed; a second view or a
   measured drawing is required.

## Next

- Get a second photo or a measured drawing before attempting an fSpy-style
  camera; the single view does not give a stable calibration.  Until then, keep
  the axonometric scene and treat the face split as the verified improvement.
- Model the group head as a rounded housing with a separate collar, gasket and
  basket; test it at 100 % and at a 120 mm print.
- Add two or three designed chrome reflection bands to the lower panel and the
  group cylinder, clipped to the part faces.
- Make the side panel a sheet-metal part with a return flange and a screw
  recess, not a flat parallelogram.
- Run a human preference test: source, T053, T054, side by side, with someone who
  knows the machine.

## Review response

| Finding | Response |
|---|---|
| — | Pending review. |
