# T055 [pptx] — PowerPoint-native 3D product explainer

## Frame

- **Question:** after the T054 vector route failed the owner's eye test, can
  PowerPoint itself carry a product explainer — a real 3D model that the
  audience can rotate, with callouts that stay editable — instead of another
  flattened illustration?
- **Hypothesis:** `Shapes.Add3DModel` with an embedded GLB, a fixed
  three-quarter camera and native PowerPoint callouts produces a deck that is
  natively 3D, reopens without repair, keeps its camera after save, and keeps
  every annotation editable.
- **Falsifiers:** the imported model becomes a picture; the camera or rotation
  is lost on reopen; the model requires a repair; the callouts are baked into a
  raster; the GLB cannot be re-extracted from the package; the deck cannot be
  exported by PowerPoint.
- **Domain lens:** PowerPoint native 3D (`am3d` / `model3d`), glTF 2.0, PBR
  materials, slide-level art direction, editable native shapes.
- **Transfers:** the geometry is the T054 SolidCraft CSG blockout (24 bodies,
  53.96 × 10⁶ mm³). The GLB is rebuilt from the blockout's command stream, not
  from its OBJ, because the OBJ export merges `group_housing` into
  `chrome_top`. The blockout travels as a **frozen input artifact**
  (`inputs/blockout.json`, a byte copy pinned by SHA-256); no vector asset and
  no T054 commit is used in the deck. Decoupling: T064.

## Frozen input

- **Task/claim:** T055 [pptx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T055-opencode-pptx-3d`, claim commit `64d6d47`. Rebased onto `main`
  `ac5b45e` by T064: the branch no longer contains T054 commits and no longer
  needs T054 to be merged first.
- **Request/date:** 2026-11-03. The owner asked for a capability that current
  AI models do not have, after repeated SVG/vector disappointment.
- **Geometry source (frozen):** `inputs/blockout.json`, a byte copy of
  `experiments/T054-20261102-opencode-vector-match/artifacts/blockout.json` at
  T054 commit `b387146`, SHA-256
  `86bf30f8fe649a261c8aeb0ee0cc359c0b3e16d6a2bed86126de371342cd389b`;
  24 visible bodies, 196 edges, 118 faces, 53.96 × 10⁶ mm³. Rebuilding the GLB
  from this copy reproduces `artifacts/quickmill-blockout.glb` byte for byte
  (SHA-256 `fd252d7c…f959143`), so decoupling changed no evidence.
- **Photo reference (not redistributed):** Wikimedia Commons, *File:Quick Mill
  Omre Espresso Machine.jpg*, **CC0**,
  <https://commons.wikimedia.org/wiki/File:Quick_Mill_Omre_Espresso_Machine.jpg>,
  accessed 2026-11-02.
- **Environment:** Windows 10/11 x64; Microsoft PowerPoint 16.0 (COM,
  `Add3DModel`); Python 3.13; trimesh 5.2.0; manifold3d; pywin32; Pillow;
  ffmpeg 8.1.1.
- **Could not access:** a final product CAD mesh; a clean-room PowerPoint
  session for Morph playback; a human reviewer for rung 6.

## Method

1. **Rebuild the GLB from the blockout definition** (`inputs/make_product_glb.py`):
   - read `solid.box`, `solid.cylinder` and `solid.combine` commands;
   - boolean-cut the bay and tray with manifold3d;
   - paint the yellow left tower, the dark bay and the dark tray from face
     geometry in source millimetres;
   - split each colour region into its own mesh/material (PowerPoint ignores
     `COLOR_0` when a material is present);
   - set every material to `metallicFactor = 0` (PowerPoint's IBL turns metal
     into a white mirror);
   - convert X/Y/Z millimetres to glTF Y-up metres, bottom on Y = 0;
   - add four chrome rim bars and one vertical corner trim.
2. **Build the deck** (`inputs/build_product_deck_v3.py`):
   - 960 × 540 pt, dark stage, native radial glow, floor rule;
   - one `Add3DModel` per slide, camera `(-0.85, 0.45, 2.10)`, look-at
     `(0, 0.28, 0)`, FOV 40°, rotation `(6, 0, 0)`;
   - native focus boxes (corner ticks + numbered chip), native spec rows,
     editable callout label/caption, footer.
3. **Reopen and audit** (`inputs/native_audit_v3.py`):
   - reopen the exact PPTX in PowerPoint, count Type-30 shapes, read cameras,
     export PDF;
   - inspect the three embedded `model3d*.glb` files.
4. **Contract tests** (`tests/test_product_deck_3d.py`): 3 slides, one native
   model per slide, three GLBs, Y-up metre bounds, metallic 0, editable text,
   native shapes, manifest camera, native-audit evidence.
5. **Review sheets** (`inputs/make_contact_sheets.py`).

```powershell
python experiments/T055-20261103-opencode-pptx-3d/inputs/make_product_glb.py
python experiments/T055-20261103-opencode-pptx-3d/inputs/build_product_deck_v3.py
python experiments/T055-20261103-opencode-pptx-3d/inputs/native_audit_v3.py
python experiments/T055-20261103-opencode-pptx-3d/inputs/make_contact_sheets.py
python -m unittest tests.test_product_deck_3d -v
python -m unittest discover -s tests -v
python lab/tools/check_layout.py
```

## Evidence

| Claim | Evidence | Rung |
|---|---|---|
| PowerPoint inserts a native 3D model, shape Type **30** | `preview/spike-cube-v2.png`, `preview/spike-cube-v2.json`; `native-audit-v3.json` reports Type 30 on all three slides | 4 |
| Camera, look-at, rotation and FOV survive save/reopen | `preview/native-audit-v3.json`; values `(-0.85, 0.45, 2.1)`, `(0, 0.28, 0)`, `(6, 0, 0)`, FOV 40 | 4 |
| The deck has three slides, one native model each | 3 slides × 33 shapes; one `am3d:model3d` per slide; `native-audit-v3.json` | 4 |
| The model is embedded, not linked | 3 `ppt/media/model3d*.glb`; slide relationships type `.../2017/06/relationships/model3d`; no external link | 1/4 |
| The three embedded GLBs are the same model | semantic fingerprint (mesh names, node names, material colours) identical; each 93,876 bytes after PowerPoint re-encode | 1 |
| The GLB is Y-up, metres, 400 × 553 × 326 mm | source GLB bounds `[-0.2, 0, -0.163] … [0.2, 0.553, 0.163]`; `glb-manifest.json` | 1 |
| Materials are non-metallic | all 34 materials `metallicFactor = 0`; `native-audit-v3.json` `metallic = [0.0]` | 1/4 |
| Callouts are editable PowerPoint text | `TOP HOUSING`, `GROUP HEAD`, `SWITCH PLATE`, captions and `ROTATE IN POWERPOINT` are `<a:t>` runs; test `test_callouts_are_editable_powerpoint_text` | 1/4 |
| The focus boxes are native shapes, not images | 20 `p:sp` + 12 `p:cxnSp` + 1 `p:graphicFrame` per slide; test `test_focus_boxes_are_native_shapes` | 1 |
| PowerPoint opens the exact file and exports it | `preview/quickmill_native_product_tour_v3.pdf`, 252,060 bytes; `native-audit-v3.json` | 5 |
| The deck is internally consistent | 469 tests, OK, 8 skipped (after this REPORT was added); `check_layout.py` passes | 1 |
| Human "mỹ mãn" approval | not obtained | 6 (missing) |

Artifacts and hashes (SHA-256):

| File | Bytes | SHA-256 |
|---|---:|---|
| `artifacts/quickmill_native_product_tour_v3.pptx` | 459,597 | `fc4f2c0d8937c20eff012f26e69b170b665c2e5f1a8299ea7d37241c8a4efaf7` |
| `artifacts/quickmill-blockout.glb` | 56,544 | `fd252d7c6e2470b9809766d9dcba0bbd546c8169209b7426ea6ceb363f959143` |
| `preview/quickmill_native_product_tour_v3.pdf` | 252,060 | `87066501bbea21f9427aaf433dc34c11a9e804644dbdaa50dc67fb3b47fcbdfa` |
| `preview/contact-sheet-v3.png` | 157,459 | `08e3feaaa0fafac0b18f6f136a342f7bf2334be8c6fa85542eeae8b269f208ef` |

### What the native renderer does to materials

These are the observations that changed the design; each is a negative result
for a naive "just import a PBR model" assumption.

| Test | Observation | Evidence |
|---|---|---|
| glTF metallic 1.0 (trimesh default) | The whole model renders white/cream; the black top and yellow tower disappear | `preview/product-spike.png` |
| Per-face `COLOR_0` inside a cream material | PowerPoint keeps the material colour and ignores the yellow `COLOR_0`; the left tower stays cream | first v2 render; material-split fix in `make_product_glb.py` |
| Metallic 0 + one mesh per colour region | Yellow tower, dark bay and black tray survive | `preview/tour-v3-1.png` |
| Black top face under the fixed key light | A rough black cube's top renders light grey (`#B0B0B0`), even at `metallic 0`, `roughness 0.82` | `preview/calib-black.png` |
| Patch `am3d:ambientLight` / `am3d:ptLight` in the slide XML | PowerPoint re-renders with the same light rig; the export is visually identical | `preview/light-test.png` |
| glTF base-colour texture | Textures render, but the per-face UVs in the calibration cube are wrong; not used in the deck | `preview/calib-texture.png` |

The design consequence is explicit: the lid is a **chrome lid**, not a black
lid, and the black mass is the 80 mm band around the bay. The copy and the
callout were rewritten to match what the native renderer can actually show.

### Camera study

Six camera candidates were rendered from the same GLB. The left three-quarter
view (B) is the only one that keeps the front controls, the group head and the
yellow tower readable at once. `preview/camera-study-sheet.png` is the review
sheet; `camera-study.json` records the cameras.

## Negative results and limitations

- **The model is a massing study, not final product fidelity.** It has no
  bevels, no group-head detail, no realistic portafilter, and no textures. It
  is honest about being a blockout; it is not a photoreal product render.
- **The native 3D lighting is fixed.** A black horizontal face renders grey.
  The deck designs around it (chrome lid, black vertical band). An XML patch of
  the `am3d` light rig did not change the render.
- **Morph was not verified visually.** `SlideShowTransition.EntryEffect = 384`
  fails with "Invalid enumeration value". A direct `<p14:morph>` was stripped
  by PowerPoint. The correct structure — `mc:AlternateContent` with
  `p159:morph` and a fade fallback, as used by `scripts/add_morph.py` — is
  accepted: `EntryEffect` reads **3954** on slides 2 and 3, and the XML survives
  a save (`preview/morph-3d.json`). The 3D camera interpolation itself was not
  observed: `CreateVideo` produced a 52 × 28 clip, and a screen-capture attempt
  captured the wrong foreground window. **No Morph claim is made.**
  *T064 correction:* the 52 × 28 clip was an argument-order bug in
  `inputs/morph_video.py` (`CreateVideo(path, 3, 3, 30, 85)` sets the height to
  30 px); the documented order `CreateVideo(path, True, 4, 1080, 30, 95)`
  renders 1920 × 1080. T064 then showed that this deck's per-slide embeds make
  Morph fade the model instead of moving the camera.
- **The first 3D product render washed out** because of metallic materials; the
  v2 deck was discarded rather than shipped. `preview/product-spike.png` keeps
  the failure.
- **The focus boxes are approximate.** They are placed from the rendered
  three-quarter view; rotating the model in PowerPoint moves the feature away
  from the box. They are annotations for the authored view, not tracking
  overlays.
- **No human review.** The owner has not yet accepted the deck as "mỹ mãn".
  Rung 6 is missing.
- T054 and T055 are independent after the T064 rebase: T055 builds from the
  frozen `inputs/blockout.json`, so it can merge without T054.
- **Morph was undecided in this report and is now answered by T064:** with
  `Shapes.Add3DModel` on each slide (this deck), the model is a separate media
  part per slide and Morph does not animate the camera — it fades the model out
  and in. With one shared `model3d` part (duplicate the slide, then change the
  camera) Morph does sweep the camera, verified at rung 5. See
  `experiments/T064-20261104-opencode-native-3d/REPORT.md`.

## Next

1. Replace the blockout with a proper product mesh (bevelled boxes, group-head
   detail, portafilter, knobs) and re-run the same three-slide compiler.
2. Verify Morph playback in a clean PowerPoint session; if the 3D camera
   interpolates, record it as a separate claim with a full-resolution capture.
3. Add a fourth "rotate me" slide or a short screen recording that shows the
   model responding to drag, so the native interaction is visible without a
   narrator.
4. Send the deck and this report to review; T064 already reviewed it and
   decoupled it from T054, so it no longer waits for the T054 merge.

## Review response

Reviewed in `research/reviews/T055-opencode-20261104.md` (T064, OpenCode). The
verdict, the findings R1–R9 and the fixes applied in the T064 rebase are there;
this section stays the author's to fill. No reviewer has accepted the report
yet. T064 answered the open Morph question and left the remaining findings to
the T055 author.
