# T056 [vector] Part-based isometric product illustration — the iso-vector-craft skill

## Frame

- **Question.** T053 reconstructed one espresso machine with a custom
  projection and 16 semantic groups, but the owner still judged the result by
  how much it looked like the product. The next step was not another primitive
  library; it was a **method** for turning a specific product photo into an
  editable SVG that reads as *that* product, not as an icon or a trace.
  Can a part-based isometric method — 30–60 named solids, one camera, four-tone
  materials, painter's order — carry a hard consumer product (a turntable),
  an easy one (a speaker) and a compound one (a TLR camera), and be taught as a
  reusable skill?
- **Hypothesis.** If the drawing is built as a model — real dimensions in object
  coordinates, a camera chosen per product, materials with four tones, and a
  written painter's order — then the result is recognisable and editable at
  every zoom, and the method transfers to other products without a new
  primitive for every object.
- **Falsifiers.**
  - the result still reads as an icon or a traced photo at 390 px;
  - changing one dimension does not move the part;
  - a part cannot be named or located in the SVG;
  - the method only works for the turntable because the code is hand-tuned;
  - the SVG needs a raster underlay, a CSS-variable browser, or a specific
    editor to render.
- **Domain lens.** SVG 2.0, axonometric projection, technical/product
  illustration, flat four-tone shading, painter's order, live text, editable
  groups. Native sources: the SVG specification, the product's real dimensions,
  the reference photographs, and the MIT Anatomy kit's camera/solid model.
- **Transfers.** The method comes from **Anatomy** (wheresryan22), a kit for
  explanatory isometric figures. Anatomy deliberately invents machines; this
  task does the opposite — it must reproduce a **specific** product. The
  transfer is the geometry/shading engine, not the "invent an object" rule.
  Tested by keeping the kit's projection, solids and four-tone shading while
  replacing its subject with a measured, photographed product.
  - **Not imported:** Anatomy's WebGL layer, 3D turn mode, print sheets,
    audit/recorder, and its "never copy a reference image" rule. A product
    illustration has to match the reference; the method must not invent.
  - **Imported and tested:** `fitProjection`, `slabOf`, `cylinder`, `ring`,
    `sideRing`, `tubePieces`, `solidSvg`, `figureSvg`.

## Frozen input

- **Task/claim:** T056 [vector], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T056-opencode-iso-vector`, based on `main` (`f648ace`).
- **Request/date:** 2026-11-03. After the Technics V3 pass the owner wrote:
  *"skill này khá được rồi đấy, học tập và cho vào main đi"* — accept the
  method, formalise it as a skill and merge it. The earlier T055 PPTX/3D
  direction was explicitly set aside; this task is SVG only.
- **Reference photographs (kept local; not redistributed):**
  - Technics SL-1200MK2: Wikimedia Commons,
    [`File:Technics SL-1200MK2-2.jpg`](https://commons.wikimedia.org/wiki/File:Technics_SL-1200MK2-2.jpg),
    2114 × 1342, **CC BY-SA 2.5**, derivative by 32bitmaschine, original by
    Dydric; and
    [`File:Technics SL-1200MK2 turntable.jpg`](https://commons.wikimedia.org/wiki/File:Technics_SL-1200MK2_turntable.jpg),
    2048 × 1536, **CC BY 2.0**, Adrian DuMay. Accessed 2026-11-03.
  - Gale Silver Monitor:
    [`Front`](https://commons.wikimedia.org/wiki/File:Gale_Silver_Monitor_Front.jpg),
    [`Back`](https://commons.wikimedia.org/wiki/File:Gale_Silver_Monitor_Back.jpg),
    [`Profile`](https://commons.wikimedia.org/wiki/File:Gale_Silver_Monitor_Profile.jpg),
    **CC BY 4.0**, Skyline400R. Accessed 2026-11-03.
  - Rolleiflex Synchro Compur (Rolleiflex T, 1958):
    [angle 1](https://commons.wikimedia.org/wiki/File:Rolleiflex_Synchro_Compur_Twin-Lens_Reflex_Camera_1.jpg),
    [angle 2](https://commons.wikimedia.org/wiki/File:Rolleiflex_Synchro_Compur_Twin-Lens_Reflex_Camera_2.jpg),
    [angle 3](https://commons.wikimedia.org/wiki/File:Rolleiflex_Synchro_Compur_Twin-Lens_Reflex_Camera_3.jpg),
    **CC BY-SA 4.0**, Heimatmuseum Aesch. Accessed 2026-11-03.
- **True dimensions (mm, from the SL-1200MK2 spec and the photos):** body
  453 × 353; platter Ø332; LP Ø300; label Ø100; body height ≈ 54; tonearm well
  ≈ Ø96; arm tube Ø8. The drawing uses **1 unit = 1 mm** and rounds to 450 × 360
  for a clean grid. Speaker and camera dimensions are **derived** from the
  photos, not measured with a ruler; marked as derived.
- **Kit:** Anatomy, <https://github.com/wheresryan22/anatomy>, MIT, commit
  `1482e8469b0a9e0d8cc18ea2740a01423d29ae80`, vendored in
  `skills/iso-vector-craft/kit/` with `LICENSE` and `ATTRIBUTION.md`.
- **Environment:** Windows 10/11 x64; Node 22.19.0; Python 3.13; `resvg_py`
  for independent raster previews; VectorCraft `vectorcraft-cli 0.19.0`
  (`D:\artcraft\VectorCraft\vectorcraft-cli.exe`).
- **Could not access:** Illustrator, Inkscape, a print proof, a measured
  drawing, a physical SL-1200, and a formal human preference test beyond the
  owner's verdict.

## Method

Run from the repository root:

```powershell
node skills/iso-vector-craft/examples/technics/build.mjs `
     experiments/T056-20261103-opencode-iso-vector/artifacts/technics-sl1200.svg
node skills/iso-vector-craft/examples/gale-speaker/build-front.mjs `
     experiments/T056-20261103-opencode-iso-vector/artifacts/gale-speaker-front.svg
node skills/iso-vector-craft/examples/gale-speaker/build-rear.mjs `
     experiments/T056-20261103-opencode-iso-vector/artifacts/gale-speaker-rear.svg
node experiments/T056-20261103-opencode-iso-vector/inputs/build_rolleiflex.mjs `
     experiments/T056-20261103-opencode-iso-vector/artifacts/rolleiflex-tlr.svg
python experiments/T056-20261103-opencode-iso-vector/inputs/collect_info.py
python -m unittest tests.test_iso_vector_skill -v
python lab/tools/check_layout.py
```

1. **Survey.** Two Technics angles, three Gale angles, four Rolleiflex angles.
   Identity features listed before geometry: SL-1200 = low plinth, Ø330
   platter, S-arm + headshell, Ø96 well, target light; Gale = two drivers,
   gold script, black cabinet, rear port; Rolleiflex = two lenses, folded hood,
   chrome nameplate, side crank.
2. **Part inventory.** 30–60 named parts with z-ranges, material and painter
   slot (the SL-1200 table is in `SKILL.md`). Every part sits on another; the
   arm is split into chunks because it crosses the platter and plinth.
3. **One camera.** 1 unit = 1 mm, origin at footprint centre, z up. SL-1200:
   azimuth 130°, elevation 24°; Gale: 130° front / 310° rear, elevation 14°;
   Rolleiflex: 60°, elevation 22°.
4. **Geometry.** `slabOf` for the plinth/cabinet, `cylinder` for platter/knobs,
   `sideRing` for drivers/port/lenses, `tubePieces` for the S-arm. 48 segments
   for visible drivers/lenses, 96 for the platter.
5. **Materials.** Four-tone silver, dark, record, label and steel tube; one
   upper-left light; flat fills; one soft halo and one platter shadow.
6. **Painter's order.** Halo → feet → plinth → platter → record → arm well →
   bearing → far gimbal + cap → counterweight → arm → near gimbal + cap →
   headshell → arm rest → controls → target light → marks. The gimbal order is
   the proof.
7. **Export.** `product-svg.mjs` wraps `figureSvg`, bakes the light palette
   into literal colours (resvg and some editors do not resolve CSS variables),
   adds `<title>/<desc>`, and pins `Arial` so text stays editable.

## Evidence

All paths are relative to
`experiments/T056-20261103-opencode-iso-vector/`.

| Artifact | viewBox | `<path>` | part groups | VectorCraft warnings | Rung |
|---|---|---:|---:|---:|---|
| `artifacts/technics-sl1200.svg` | 980 × 900 | 518 | 12 | 0 | 4 |
| `artifacts/gale-speaker-front.svg` | 820 × 900 | 79 | 0 (2 driver groups) | 0 | 4 |
| `artifacts/gale-speaker-rear.svg` | 820 × 900 | 114 | 0 | 0 | 4 |
| `artifacts/rolleiflex-tlr.svg` | 820 × 900 | 217 | 0 (2 lens groups) | 0 | 4 |

- **Rung 1 — structural.** All four SVGs parse with `xml.etree`; one `<svg>`
  root, `viewBox`, `role="img"`, `aria-label`, `<title>`, `<desc>`; no
  `<image>`, `<foreignObject>`, `data:image`, external `href` or unresolved
  `var(--anatomy-*)`. `tests/test_iso_vector_skill.py`: 13 tests OK; full suite
  461 tests OK (8 skipped); `lab/tools/check_layout.py` OK.
- **Rung 2 — rendered.** `resvg_py` renders every artifact to
  `preview/*.png`. The hero sheet is `preview/iso-hero-sheet.png`; the
  V1→V2→final comparison is `preview/progression.png`; the hard subject is
  `preview/hard-subject.png`.
- **Rung 3 — independent reader.** resvg is an independent SVG implementation.
  No browser check was run in T056; T055 used the same resvg pipeline for the
  Technics renders.
- **Rung 4 — target parsed.** `vectorcraft-cli info`: 0 warnings for all four;
  fonts exact (Arial; Segoe Script for the Gale wordmark; Arial Narrow for the
  Rolleiflex plate). Output is in `artifacts/info.json`.
- **Rung 6 — human.** The owner accepted the V3 direction (*"khá được rồi"*).
  The shipped SL-1200 is the V3 build minus the rejected 45-adapter recess
  (27 paths) and with the export-safe palette; the owner did not re-review that
  exact file, so this is a **qualified** rung 6, not a fresh acceptance.

**What changed (the useful evidence):**

| Pass | Paths | Change | Verdict |
|---|---:|---|---|
| V1 | 411 | 98-unit plinth, 18° camera, Ø48 arm base, 12-unit platter | "lunchbox"; rejected |
| V2 | 463 | 54-unit plinth, no fake top plate, 24° camera, Ø96 well, 26-unit platter, deadwax | silhouette fixed |
| V3 | 545 | gimbal stack, anti-skate, cue lever, cartridge wires, feet rings, target light | mechanism credible |
| final | 518 | removed the rejected 45-adapter (27 paths), export-safe palette | shipped example |

- **Plinth 98 → 54** was the highest-leverage change; the path count barely
  moved. This is the central claim of the skill: **proportion/camera first,
  detail second.**
- **Camera 18° → 24°** opened the top deck and made the S-arm read.
- **Ø48 → Ø96 arm well** turned a wire into a mounted tonearm.
- **Deadwax R = 50–68, grooves R = 68–144, label Ø100** made the record read as
  vinyl, not a black disc.
- **Speaker first pass** had nine bright "wood grain" lines on a black cabinet
  and 20-segment drivers. Fixed to four dark grain lines and 48-segment rings.
  The lesson is now in the skill: *line tone is material-scoped, not only
  theme-scoped.*

**Argon critique (chat `1:3b6c02550454f8bc`, account `game25072003`, high
thinking):**

| Advice | Response |
|---|---|
| plinth 98 → 54, remove fake dark top plate | accepted; root cause |
| tonearm base Ø48 → Ø96 | accepted |
| camera 18° → 24° | accepted |
| deadwax, target light, gimbal painter order, 2 strobe rings | accepted |
| hard-edged cast-shadow polygons | **rejected**: they fight the four-tone shading; one soft halo + one platter shadow |
| three custom longitudinal bands on the arm | **rejected**: `tube.mjs` already emits body/shine/shade; collars are enough |
| platter 12 units thick | **rejected**: Argon's own real-dimension premise implies 26–30; used 26 |
| "don't add labels" | accepted on the front face; kept the real logo/model/pitch scale |

## Negative results and limitations

- **V1 is kept as a negative result.** 98-unit plinth + 18° camera + Ø48 arm
  base produced a toy; more detail would not have saved it. The progression
  sheet keeps the evidence.
- **The Rolleiflex is not expert yet.** 217 paths, better after 60°/22° and a
  flatter hood, but the lens barrels are concentric rings, the hood is a slab
  and the body proportions are derived. It is a stress test, not a shipped
  example. It needs a measured multi-view survey and lathe profiles.
- **The Technics is simplified.** No bearing races, calibrated anti-skate, real
  cartridge generator, dust cover, 45 adapter, or slipmat edge. The tonearm is
  a tube, not a machined casting. The logo/model text is live horizontal text,
  not projected onto the face.
- **Dimensions.** The SL-1200 uses spec dimensions rounded to a 450 × 360 grid;
  the speaker and camera are derived from photos. No physical measurement.
- **Camera estimation.** Azimuth/elevation were chosen by eye against the
  photos, not solved from vanishing points. A wrong estimate is the easiest way
  to make a correct model look wrong.
- **Export.** Baking the palette fixes resvg/editors, but it also removes the
  live theme switch. The skill chooses portability over a dark variant.
- **No Illustrator/Inkscape/print proof.** VectorCraft and resvg only. Rung 5
  is not claimed.
- **One human verdict.** The owner liked V3; that is not a controlled test.
- **The Anatomy transfer is partial.** The kit's audit/recorder, 3D and print
  paths are not used and not tested; the skill documents only the static
  product-illustration subset.

## Next

- **Production use**: one real deck/landing page and a 300 dpi print proof in
  Illustrator/Inkscape. This is the remaining rung 5/6 gate; the current
  evidence stops at rung 4.
- **Accept or revise the Rolleiflex**: measured body/hood, lathe lens barrels,
  and a proper leather texture that ends on edges.
- **Second product family**: a flat object with no cylinders (a keyboard or a
  book) to test whether the method overfits to "box + round part".
- **Projected text**: put the logo and scale text on the actual face matrix
  (`sideMatrix`/`topMatrix`) instead of screen-horizontal text.
- **Skill packaging**: decide whether to keep the MIT kit inside the skill or
  fetch it at install time; the current choice is vendored + attribution.

## Review response

**Reviewer:** Argon (Gemini, web), chat `1:50eac399376d9783`, 2026-11-03.
**Verdict:** `revise` (round 1) → `accept-with-fixes` (round 2, after the fixes
below). The full review is summarised here; the design critique earlier in this
report is a separate, pre-code review.

| # | Finding | Response |
|---|---|---|
| R1 | Azimuth 120–140 description is wrong; elevation is not true isometric | **Accepted.** The camera at 130° is front-left: the visible vertical faces are `+y` (front, lower right) and `−x` (left, lower left); `+x` is the far side. The row was corrected. Also accepted: 210–240 was missing; 300–320 said `−x` instead of `+x`; added `e = asin(minor/major)` and clarified that "iso" is a general axonometric camera, not the 35.26° special case. |
| R2 | Gimbal cap order and counterweight order are wrong | **Accepted.** Far plate + far cap → counterweight → arm → near plate + near cap. Rebuilt and re-rendered. |
| R3 | `data-part` vs per-solid groups conflict; 3/4 artifacts have 0 part groups | **Disputed in part.** `solidSvg` already emits one `<g class="iso-solid">` per solid (43 on the Technics, 22 on the Rolleiflex, 6/9 on the speaker); `data-part` is assembly-level and optional for a one-assembly study. **Accepted:** added a DOM contract and a test that requires ≥40/5/8/20 solid groups. |
| R4 | Hardcoded arm/anti-skate/logo coordinates break the editability falsifier | **Accepted in part.** Arm pivot, S-curve, collars, counterweight, anti-skate, cue lever and logo/seam now derive from `ARM`/`PLINTH`; arm rest and controls remain pinned in the one-off build and are labelled as such. |
| R5 | SKILL.md overfits to the turntable | **Accepted.** The 17-row inventory and the 11-step paint order moved to the worked example; §2/§6 now give generic columns/topology; the palette is labelled "SL-1200 example". |
| R6 | Wrapper leaves CSS classes/`!important`; Illustrator may drop them | **Deferred with evidence.** `vectorcraft-cli info` reports 0 warnings on all four files; colours are literal, only material classes remain. Baking `fill`/`stroke` per path is a separate change that needs an Illustrator/Inkscape test (not available); recorded as a limitation and a next task. |
| R7 | Missing kit DOM/coordinate contract | **Accepted.** Added `plan` top-left vs `cylinder` centre, `fitProjection` points, `.iso-*`/`.tb-*` classes and `data-part` levels. |
| R8 | Rung 4 / test-suite / font claims are overstated | **Accepted in part.** Corrected to 13 skill tests + 461 full-suite tests; rung 4 means VectorCraft parsed the file, not that a human verified it. Script fonts now carry a fallback stack; exact font availability remains Windows-local. |

**Changes after review:** the Technics build was reordered (gimbal,
counterweight), anchored to `ARM`/`PLINTH`, and rebuilt (518 paths, 13 tests).
The report claims are narrowed. A second review round followed (full record:
`research/reviews/T056-argon-20261103.md`).

**Second review (same chat, round 2): `accept-with-fixes`.** Argon confirmed
the R1 correction, the solid/assembly split and the DOM contract, and asked for
three clean-ups: anchor the headshell to the arm end, fix the 120–140 azimuth
row (the `−x` side is the visible left face), and sync the report's paint
order. All three are applied; no third round is required. The skill remains
labelled **EXPERIMENTAL** until a production deck uses it.
