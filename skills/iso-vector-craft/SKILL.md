---
name: iso-vector-craft
description: Draw a specific product as a clean, editable isometric SVG from reference photos — a named part inventory, real dimensions in object coordinates, one chosen camera, four-tone flat materials and painter's order. Use when the user asks for a product illustration, hero/technical SVG, "turn this photo into a vector", or rejects an auto-trace, a flat icon or a primitive-only drawing. Not for icons, logos, charts, diagrams or photo filters.
---

# Isometric Vector Craft

> **Status: merged to `main` as EXPERIMENTAL — Argon review
> `accept-with-fixes` (round 2, 2026-11-03).**
> Flagship: Technics SL-1200, 518 paths, 12 part groups. Easy: Gale Silver
> Monitor, front + rear. Hard: Rolleiflex TLR stress test. Built on the
> MIT-licensed Anatomy kit (`kit/`, vendored; see `kit/ATTRIBUTION.md`).

## The one idea

A product illustration is a **model**, not a picture.

You name the parts, give them dimensions in object coordinates, choose one
camera, and paint their visible faces back to front. The photo supplies
identity, proportion and finish. It never supplies line work.

A drawing usually fails in one of two ways:

- **Trace.** Contours extracted from a photo. Noisy, flat, impossible to edit,
  and it cannot answer "make the platter 2 mm thinner".
- **Icon.** Boxes and circles that say "a turntable" but not *this* turntable.
  Correct topology, wrong identity.

The difference is a **part inventory with dimensions** and a **camera chosen
for this product**, not the kit default.

> **"Isometric" is the kit's name, not a locked 35.26°.** The camera is a general
> axonometric projection with an azimuth and an elevation. A product portrait
> usually wants a lower elevation than a true isometric drawing; the rules below
> say when. Use the word **axonometric** when precision matters.

## When to use it

Use it for:

- a product photo → an editable SVG for a deck, a landing page, a manual or print;
- a hero illustration where the object must be recognisable at 390 px;
- a technical view where parts must be separable and dimensionally honest;
- "the auto-trace looks like a scribble" or "this looks like an icon, not the product".

Do not use it for:

- icons, logos, maps, charts, UI, lettering (use the icon/vector canon instead);
- photorealistic rendering with gradients, textures and reflections;
- a 3D turntable/animation (this is a still, flat-shaded drawing);
- tracing a photo when the photo is the deliverable.

## Size tiers

| Tier | Solids | Typical paths | Time | Example |
|---|---|---|---|---|
| Easy | 12–25 | 50–150 | < 1 h | Gale speaker, 79 front / 114 rear |
| Figure | 30–60 | 250–600 | 2–4 h | Technics SL-1200, ~45 solids / 518 paths |
| Hero | 60–100 | 600–1200 | 4–8 h | studio deck with dust cover, cables, accessories |
| Epic | 100+ | — | do not start without a measured drawing | full hi-fi rack, car, building |

Paths are a symptom, not a target. 518 paths is not better than 300 if the
extra paths are unreadable at 390 px. Stop when the next detail is under
**2 object units** at final size or you cannot name the part it belongs to.

## Workflow

### 1. Survey the reference before any geometry

- Get **at least two angles** (front 3/4 and rear or side). One photo hides
  exactly the surfaces you will have to invent.
- Identify the **exact model and variant**. "SL-1200" is not enough: MK2 has a
  different plinth, target light and tonearm base from MK5/MK7.
- Write the **true dimensions in millimetres** from a spec sheet or a measured
  photo. If you only have ratios, derive them from one known dimension and mark
  them **derived**, not measured.
- Estimate the photo camera: which two faces are visible, how much of the top,
  and the ellipse ratio of a known circle. Record azimuth and elevation.
- List the **identity features** that must survive at 390 px. Examples:
  - SL-1200: low plinth, Ø330 platter, S-arm with headshell, Ø96 arm well, target light.
  - Gale: two drivers, gold script logo, black ash cabinet, rear port + terminal plate.
  - Rolleiflex: two stacked lenses, folded hood, chrome nameplate, side crank.
- List what you will **not** draw: dust, reflections, background, cable clutter,
  hard cast shadows, every screw.

### 2. Write the part inventory

Before drawing, make a table. Every row is a solid or a named detail.

| Part | Role | Plan / axis | z-range | Material | Painter slot |
|---|---|---|---|---|---|
| feet ×4 | support | Ø48 circles at corners | −12…0 | dark rubber | 1 |
| plinth | body | 450 × 360 r12 | 0…54 | silver + rubber | 2–4 |
| platter + record | subject surface | Ø330 / Ø300 | 54…86 | silver, black, cream | 6–8 |
| tonearm | mechanism | pivot at (150, −120) | 54…94 | steel + dark | 10–17 |
| controls + marks | interface | front deck | 54…62 | silver, ink | 18–21 |

The full SL-1200 inventory (17 rows) is in the worked example. Use these
columns for any product; do not copy the turntable's rows.

Rules:

- Every part **sits on another part**. No floating solids.
- A part that crosses another (tonearm over platter) gets a painter slot after it.
- A part that wraps another (gimbal, collar, ring) is split into **back half and
  front half**, with the wrapped part in between.
- Count the solids. Under 30 usually means the object will read as an icon;
  over 100 usually means you are modelling screws nobody will see.

### 3. Choose the world and the camera

- **1 unit = 1 mm.** Origin at the centre of the footprint, `z = 0` on the desk,
  `+y` = front, `+x` = right. This makes every dimension checkable.
- The kit projects `x/y` on the floor and `z` up. `fitProjection` takes the
  projected corners and fits them to the viewBox.
- Camera for a product portrait:

| Azimuth | What you see | Use |
|---|---|---|
| 40–60 | front on the left, +x side on the right | front-left 3/4; crank/controls on the right |
| 120–140 | front on the lower right, −x side on the lower left; +x is the far side | front-right 3/4; platter on the left, arm on the upper right |
| 210–240 | rear on the left, −x side on the right | rear-left 3/4; back panel + left connectors |
| 300–320 | rear on the right, +x side on the left | rear-right 3/4; ports, terminals, labels |

- **Estimate elevation from a known horizontal circle.** In an axonometric
  projection, a horizontal circle becomes an ellipse whose short/long axis ratio
  is `sin(elevation)`: `e = asin(minor / major)`. Verify it on the platter or a
  knob before trusting the eye.

- **Avoid exactly 45 / 135 / 225 / 315** for a product portrait: the corner
  points at the viewer, both faces are equally wide and the result reads as a
  CAD icon. The kit default 45 is for explanatory figures, not product identity.
- **Elevation:**
  - 20–27° for a desktop object: enough top to read the deck, not a plan view.
  - 10–16° for a tall cabinet whose front face is the identity (the Gale speaker
    is 14°).
  - 18–24° for a tall compound object where the top or hood must read; the
    Rolleiflex needed 22°, and 15° flattened the hood into a slab.
  - 30–40° only when the top is the subject (open hood, tray, controls).
  - The SL-1200 was drawn at 18° first; it hid the top deck and made the 98-unit
    plinth look like a lunchbox. 24° fixed the silhouette more than any detail.
- **Fit once.** `fitProjection` with `pad: 40–48`, then never move the origin to
  fix a composition problem; change the object or the camera.

### 4. Build geometry in object coordinates

Use the kit, not hand-written pixel paths:

| Call | Use |
|---|---|
| `slabOf(plan, z, h, P, steps, bevel)` | boxes, plinths, plates, baffles |
| `cylinder(cx, cy, r, z, h, P, steps, bevel)` | knobs, platter, feet, caps |
| `ring(cx, cy, r, z, P, steps)` | grooves, seams, rims, scale circles |
| `sideRing([x,y,z], r, axis, P, steps)` | a circle on a vertical face (lens, driver, port) |
| `planOutline(plan, z, P, steps)` | an edge, not a filled face |
| `lineOnTop([x,y], [x,y], z, P)` | a line on a horizontal face |
| `segment([x,y,z], [x,y,z], P)` | a line in space |
| `tubePieces(points, r, P, {maxLength, spacing})` | pipes, tonearms, cables, S-curves |
| `tubeSvg(piece, {tone})` | draw one tube chunk |
| `haloOf(plan, z, h, P)` | the soft contact shadow |
| `topMatrix(at, z, P, axis)` + `faceTextSvg` | live text on a face |

Practical rules:

- **Overlap by 0.5–1 unit.** Solids that merely touch show hairline gaps after
  projection. A cylinder seated on a slab should start 1 unit inside it.
- **Round visible circles properly.** `steps: 48` for a driver or lens at 800 px,
  `96` for a 330 mm platter, `20–24` only for a screw or a hidden foot.
  Twenty segments on a 92 mm woofer reads as a dodecagon.
- **Bevel 0.4–1.4.** A 1-unit bevel catches the edge light and separates two
  silver parts; 0 is a raw extrusion.
- **A box is three faces, not six.** The kit paints the visible top and two
  sides. Never draw hidden edges as wireframe.
- **One tube per route.** Chunk it with `tubePieces`; do not approximate a curve
  with three cylinders.
- **Text is live text**, not paths. Use Arial/Helvetica for a technical mark, a
  script only where the real logo is script. Set `font-family` explicitly; a CSS
  variable font family is fragile in editors. A script wordmark needs a fallback
  stack (the Gale example uses `Segoe Script, Brush Script MT, cursive`); a
  fallback changes the lettering, never the geometry.

### 5. Materials: four tones and one light

Pick **4–6 materials**, never one per part. A material is a family. The table
below is the SL-1200 palette; treat it as a template for tone spacing, not a
fixed set of six materials.

| Material | Fill | Shade 0 | Shade 1 | Shade 2 | Shade 3 | Top | Edge |
|---|---|---|---|---|---|---|---|
| Silver | `#B8B5AC` | `#7A7770` | `#A8A59C` | `#C9C6BC` | `#D8D5CC` | `#E8E6DE` | `#5E5B54` |
| Dark | `#151719` | `#08090B` | `#0E1012` | `#151719` | `#23262A` | `#2E3238` | `#000000` |
| Record | `#08090B` | — | — | — | — | `#0A0C0E` | `#000000` |
| Label | `#F2EBDC` | — | — | — | — | `#FBF7EA` | `#8E8B82` |
| Steel tube | body `#B8B5AC` | — | shine `#F5F3EA` | shade `#6E6B64` | — | — | `#5E5B54` |
| Wood / black ash | `#151515` | `#090909` | `#111111` | `#1A1A1A` | `#242424` | `#2A2A2A` | `#000000` |

- **One light, upper-left in screen space.** Top lightest; the face turned to
  the light is lighter than the face turned away. Keep the same order on every
  material, or the object falls apart.
- **Flat fills only.** A gradient is allowed only for a genuine mirror cylinder,
  and then three stops, not a rainbow. No texture maps, no blurred reflections.
- **Shadows:** one soft halo under the base and, at most, one contact shadow
  under a lifted part. No hard black polygons: they fight the four-tone shading.
- **Line tone is material-scoped.** A light-theme `faint` line is nearly
  invisible on silver and glaring on a black cabinet. For dark materials set an
  explicit dark stroke (`#2A2A2A`) or wrap the lines in a material group. This
  was the single worst defect in the first speaker pass: nine bright "wood
  grain" lines turned a black cabinet into a plank fence.
- **Edges 0.5–0.8 px**, darker than the darkest fill. Never pure black on a dark
  material; use `#000` only for a true gap.

### 6. Painter's order is geometry, not taste

Draw **bottom to top, back to front**:

1. ground: halo, feet, contact shadow;
2. main body: plinth, cabinet, housing;
3. recesses and top surfaces: wells, top plates, baffles;
4. parts seated on the body: platter, hood, tray;
5. parts seated on those: record, drivers, lenses;
6. **far-side** wrapping parts: the plate, collar or ring behind the thing it wraps;
7. parts that cross the body: arms, pipes, cables, handles;
8. **near-side** wrapping parts: the matching front plate, collar or ring;
9. controls, connectors and marks.

The SL-1200 order (halo → feet → plinth → platter → record → arm well →
bearing → far gimbal → counterweight → arm → near gimbal → headshell → rest →
controls → target light → marks) is in the worked example.

The gimbal is the canonical test:

```
far yoke plate → far axle cap → counterweight → arm tube → near yoke plate → near cap
```

If the near plate is drawn before the arm, the arm floats in front of the
bearing. If the counterweight is drawn after the near plate, it covers the
yoke. The tonearm crosses both the platter and the plinth: it must come after
both, and its cast shadow (if any) before the arm.

### 7. Spend detail on identity, not on noise

Three tiers:

1. **Silhouette** (must): plinth height, platter diameter, cabinet proportions,
   lens spacing, hood shape. Get this wrong and no detail saves it.
2. **Mechanism** (worth it): gimbal, headshell, counterweight, arm rest, cue
   lever, rear port, terminal plate, side crank. These tell the viewer the object
   is real.
3. **Surface** (only if it survives 390 px): logo, model number, pitch scale,
   9 groove rings, 2 strobe rings.

Rejected as noise in the SL-1200 study:

- 60 strobe dots → two thin rings;
- 45 adapter recess → removed (read as a second control knob);
- gimbal top bridge → removed (read as a heavy block, hid the bearing);
- dust cover → not drawn (it occludes the deck; a separate variant, not a detail);
- hard cast-shadow polygons → one soft halo, one platter shadow.

### 8. Verify like an editor, not a renderer

1. **Structural:** XML parses; one `<svg>`; `viewBox`; `role="img"`; `aria-label`;
   `<title>` and `<desc>`; no `<image>`, `data:` URI, external `href` or
   `<foreignObject>`.
2. **Tool:** `vectorcraft-cli info file.svg` must report 0 warnings and no
   missing fonts. Anatomy's CSS variables are invisible to several rasterisers;
   `kit/product-svg.mjs` bakes the light palette into literal values. Material
   classes (`.qm-*`, `.tb-*`) remain: VectorCraft resolves them, but a strict
   editor may not. If that happens, bake `fill`/`stroke` onto each path; that is
   not automated yet and is recorded as a limitation.
3. **Visual:** render at 1× and 2×. Read the PNG. Then:
   - 25% zoom: is it instantly this product?
   - 390 px wide: do the identity features survive?
   - 4× on every junction: gimbal, headshell, arm rest, port, lens, hood.
   - compare with the reference at the same angle, side by side.
4. **Editability:** each solid is its own `<g class="iso-solid">`; major
   assemblies carry `data-part`; move a dimension and the part moves without
   redrawing the rest; text is still text.
5. **Honesty:** write down what is simplified. A clean 45-solid drawing with a
   named limitation is better than a 900-path drawing that pretends to be a
   survey.

## Kit API (the subset this skill uses)

```js
import * as k from "../../kit/iso-kit.mjs";
import { tubePieces, tubeSvg } from "../../kit/tube.mjs";
import { productSvg } from "../../kit/product-svg.mjs";

const P = k.fitProjection(points, width, height, { pad, azimuth, elevation });
k.iso([x, y, z], P);

k.slabOf(plan, z, height, P, steps = 8, bevel = 0);
k.cylinder(cx, cy, radius, z, height, P, steps = 32, bevel = 0);
k.ring(cx, cy, radius, z, P, steps = 40);
k.sideRing(center, radius, axis, P, steps = 20);
k.planOutline(plan, z, P, steps = 8);
k.lineOnTop(from, to, z, P);
k.segment(from, to, P);
k.haloOf(plan, z, height, P);
k.boxCorners(plan, z0, z1);
k.corners(plan, inset);
k.insetPlan(plan, by);
k.topMatrix(at, z, P, axis);
k.faceTextSvg(matrix, text, { size, tone, anchor });
k.solidSvg(paths, { tone, className, crease, halo, lit, flat, inner });
k.lineSvg(d, { tone });
k.dotsSvg(points, { size, tone });
k.figureSvg({ width, height, label, body, standalone });
productSvg({ width, height, label, title, desc, body, palette });
```

`productSvg` is ours, not Anatomy's: it wraps `figureSvg`, bakes the light
palette, adds `<title>/<desc>` and pins a real font family.

### Kit DOM and coordinate contract

An agent needs these conventions before writing a build:

- **Plans:** `plan = { x, y, w, d, r }` is a rounded rectangle on the floor;
  `(x, y)` is its **top-left** corner, `w` runs along `+x`, `d` along `+y`.
- **Cylinders:** `cylinder(cx, cy, r, ...)` takes the **centre** `(cx, cy)`, not
  a corner. Do not mix the two conventions in one part.
- **Projection points:** pass `boxCorners(plan, z0, z1)` for the body, plus any
  protrusion that must not clip (platter rim, raised arm, controls) to
  `fitProjection`.
- **Solid DOM:** `solidSvg` emits `<g class="iso-solid qm-…">` with child paths:
  `.iso-fill`, `.iso-shade[data-shade="0"…"3"]`, `.iso-top`, `.iso-edge`,
  `.iso-crease`. `lineSvg` emits `.iso-line[data-tone]`; `tubeSvg` emits
  `.tb-body`, `.tb-shine`, `.tb-shade`, `.tb-edge`, `.tb-ring`.
- **Assembly DOM:** wrap major assemblies in `<g data-part="…">` (plinth,
  tonearm, controls). A small one-assembly study may use only `iso-solid`
  groups; a hero should have 8–15 `data-part` groups. `data-part` is not a
  replacement for the per-solid group.
- **Material CSS:** define `.qm-<material> .iso-fill`, `.iso-shade[data-shade]`,
  `.iso-top` and `.iso-edge` in one style block; do not style individual paths.

## Worked example: Technics SL-1200

**Reference:** Wikimedia Commons, *Technics SL-1200MK2*, CC BY-SA 2.5 /
CC BY 2.0. Dimensions checked against the real machine: 453 × 353 mm body,
Ø332 platter, Ø300 LP, Ø100 label.

**Build:** `examples/technics/build.mjs`, viewBox 980 × 900, azimuth 130,
elevation 24, 12 part groups, ~45 solids, 518 paths.

Part inventory (the full table; sections 2–6 keep only the generic rules):

| Part | Plan / axis | z-range | Material | Painter slot |
|---|---|---|---|---|
| feet ×4 | Ø48 at corners | −12…0 | dark rubber | 1 |
| plinth base | 450 × 360 r12 | 0…18 | dark rubber | 2 |
| plinth body | 450 × 360 r12 | 18…50 | silver | 3 |
| top chamfer | inset 4 | 50…54 | silver, lit | 4 |
| platter | Ø330 at (−45, 0) | 54…78 | silver | 6 |
| record | Ø300 | 80…84 | record black | 7 |
| label | Ø100 | 84…86 | cream | 8 |
| tonearm well | Ø96 at (150, −120) | 54…57 | dark | 10 |
| bearing | Ø36 | 60…78 | dark | 11 |
| gimbal | far plate + axle cap | 72…90 | silver | 12 |
| counterweight | Ø28 | 88 | dark | 13 |
| arm tube | 5-point S, Ø8 | 88…91 | steel | 14 |
| gimbal | near plate + cap | 72…90 | silver/dark | 15 |
| headshell | 34 × 16 | 86…94 | dark | 16 |
| arm rest | 2 posts | 54…74 | silver/dark | 17 |
| controls | start/stop, 33/45, pitch | 54…59 | silver/dark | 18 |
| target light | Ø12 pop-up | 54…62 | silver/warm | 19 |
| marks | logo, model, pitch scale | front/top | ink | 20 |

Paint order: halo → feet → plinth → platter → record → arm well → bearing →
far gimbal + cap → counterweight → arm → near gimbal + cap → headshell → arm
rest → controls → target light → marks.

What changed between passes:

| Pass | Paths | Change | Verdict |
|---|---|---|---|
| V1 | 411 | 98-unit plinth, 18° camera, Ø48 arm base, 12-unit platter | silhouette wrong: "lunchbox" |
| V2 | 463 | plinth 54, no fake top plate, 24° camera, Ø96 well, 26-unit platter, deadwax | silhouette fixed |
| V3 | 545 | gimbal stack, anti-skate scale, cue lever, cartridge wires, feet rings | mechanism credible |
| final | 518 | removed the rejected 45-adapter recess (27 paths); export-safe palette | shipped example |

The lessons that generalise:

- **Plinth height was the whole drawing.** 98 → 54 units changed the object more
  than 130 added paths.
- **Camera elevation is a proportion tool.** 18° → 24° made the top deck and the
  S-arm readable; it was not a cosmetic tweak.
- **The arm base was too small.** Ø48 → Ø96 gave the tonearm a real mount and
  fixed the "wire stuck in the deck" look.
- **Deadwax sells a record.** Grooves R = 68–144, flat black R = 50–68, label
  Ø100. Without the deadwax the record reads as a black sticker.
- **Detail order matters.** The gimbal stack, cartridge wires and target light
  moved it from "good" to "expert"; the 45 adapter and top bridge did not.

## Hard subject: Rolleiflex TLR

`experiments/T056-20261103-opencode-iso-vector/inputs/build_rolleiflex.mjs`
builds a 217-path stress test. It is deliberately **not** shipped as a skill
example: the folded hood is a slab, the lens barrels are concentric rings, and
the body proportions are derived, not measured. It proves the method scales to
a compound object and shows where it stops: a camera needs a measured multi-view
survey and lathe profiles for the lens barrels before it is expert.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| "Lunchbox" | plinth/body too tall | measure the real height; cut it before adding detail |
| "Wire arm" | uniform tube, no mount | Ø96 well, bearing stack, collars, counterweight |
| "Sticker record" | no deadwax, label too big | label Ø100 on Ø300; grooves start at R=68 |
| "CAD icon" | 45° azimuth, equal faces | move to 30–35° off-axis |
| "Icon stack" | < 30 solids, no part inventory | name 30–60 parts; add mechanism tier |
| "Traced photo" | pixel coordinates, noisy contours | rebuild in object coordinates |
| "Gradient soup" | a gradient per face | 4–6 flat materials, one light |
| Floating parts | no support / no overlap | seat every part, overlap 0.5–1 unit |
| White seams on black | theme line tone on dark material | explicit material-scoped stroke |
| Faceted circles | 20 segments on a large ring | 48–96 segments |
| Hidden wireframe | bottom/back outlines drawn | remove; paint only visible faces |
| Detail noise | 60 dots, every screw | 2 rings, 9 grooves, 3–5 screws |

## Checklist

Copy this into the task and tick it:

- [ ] Exact model identified; ≥ 2 reference angles; licence recorded.
- [ ] True dimensions in mm, or derived and marked.
- [ ] 30–60 named parts with z-ranges, material and painter slot.
- [ ] 5–9 identity features listed; they survive at 390 px.
- [ ] One camera; azimuth not 45/135; elevation justified.
- [ ] 1 unit = 1 mm; origin at footprint centre; object sits on z = 0.
- [ ] 4–6 materials; four tones + top; one light.
- [ ] Painter's order written down; wrapping parts split back/front.
- [ ] Large circles ≥ 48 segments; no hidden edges; no gradient soup.
- [ ] No `<image>`, no data URI, no external href; title/desc present.
- [ ] `vectorcraft-cli info` 0 warnings, 0 missing fonts.
- [ ] Rendered at 1× and 2×; compared side by side with the reference.
- [ ] Limitations written in the report.

## Files

```
skills/iso-vector-craft/
  SKILL.md
  kit/
    iso-kit.mjs      MIT, Anatomy 1482e84
    tube.mjs         MIT, Anatomy 1482e84
    lathe.mjs        MIT, Anatomy 1482e84
    iso.css          MIT, Anatomy 1482e84
    LICENSE          MIT, upstream
    ATTRIBUTION.md
    product-svg.mjs  export wrapper (this lab)
  examples/
    technics/build.mjs
    gale-speaker/build-front.mjs
    gale-speaker/build-rear.mjs
```

Run an example from the repository root:

```powershell
New-Item -ItemType Directory -Force out | Out-Null
node skills/iso-vector-craft/examples/technics/build.mjs out/technics.svg
node skills/iso-vector-craft/examples/gale-speaker/build-front.mjs out/gale-front.svg
node skills/iso-vector-craft/examples/gale-speaker/build-rear.mjs out/gale-rear.svg
```

## Attribution

The geometry kit is **Anatomy** by Ryan
(<https://github.com/wheresryan22/anatomy>), MIT, vendored at commit
`1482e8469b0a9e0d8cc18ea2740a01423d29ae80`. The product drawings, the part
inventories, the camera rules and the export wrapper are this lab's work.
Reference photos are cited in the reports and are **not** redistributed.
