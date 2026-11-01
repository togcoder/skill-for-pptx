---
name: vector-craft
description: Turn a product photo into a controlled, editable SVG line illustration — keep the silhouette, simplify part boundaries, cap detail and remove texture/lettering that cannot be read at the final size. Use when the user supplies a photo and asks for a vector drawing, a technical illustration, a line-art version, a laser/print asset, or complains that an auto-trace looks noisy, sketchy or over-detailed.
---

# Vector Craft

> **Status: EXPERIMENTAL — T051 [vector], review requested.** This skill is not a
> canonical product path until an independent review accepts it. Use it, test
> it, and report failures; do not cite it as lab canon yet.

You are the illustrator, not a tracer. A camera photo contains four kinds of
ink: the **silhouette**, **part boundaries**, **controls**, and **texture**
(reflections, dust, lettering, shadows). A good drawing keeps the first three
selectively and removes the fourth. "Trace every edge" is the failure mode, not
the goal.

Scripts live two levels above this file: `ROOT=<this skill dir>/../..`.

- **Required:** Python 3, OpenCV (`opencv-python-headless`), NumPy, Pillow.
- **Native vector tool:** VectorCraft (`vectorcraft-cli`) for SVG inspection and
  rendering. The SVG is the deliverable; a PNG is a preview only.

## Workflow

1. **Freeze the brief.**
   - What is the final width (mm or px)? Detail that is 1 mm wide is invisible
     at 60 mm and clear at 300 mm.
   - Line style or flat colour? A **line drawing** is usually more readable for
     a technical product; flat colour is a material study.
   - Which marks are semantic (a logo, a warning label, a control) and which
     are texture? Ask if a brand mark must remain; do not trace lettering.
   - Is the photo licensed for reuse? Record source, licence, access date.
2. **Segment before drawing.**
   ```powershell
   python $ROOT/scripts/photo_vector.py build photo.jpg -o line.svg `
     --level catalogue --colors 5 --width-mm 120 --style line `
     --source "..." --license "CC0" --json metrics.json
   ```
   The default segments with GrabCut, removes the shadow skirt, flattens colour,
   extracts/dedupes Canny edges, classifies and writes a layered SVG.
3. **Read the layers, not just the render.**
   ```powershell
   vectorcraft-cli info line.svg
   vectorcraft-cli convert line.svg line.png --scale 2
   ```
   Open `preview/layer-stack.png` or make it: silhouette / colour / form /
   detail. If the form layer is not a clean drawing, fix the form budget before
   adding detail.
4. **Choose a budget and say why.**
   - `silhouette`: shape check only.
   - `form`: material blocks + structure, no detail.
   - `catalogue`: 30–35 form + 12–16 detail; the default.
   - `full`: the strawman; use only to show why it is worse.
5. **Curate.** The pipeline is a first pass. Remove brand lettering, decals,
   dust and reflection clusters by hand or with an include/exclude box. A
   single wrong line is better removed than smoothed.
6. **Verify.** SVG parses; `vectorcraft-cli info` reports no warnings; render at
   the final size; check that the smallest kept detail is ≥ 1.5 mm and that the
   silhouette IoU is ≥ 0.96 against a hand-checked mask. State the limits.

## The hierarchy

| Layer | What belongs | Line weight (share of object height) | Rule |
|---|---|---|---|
| Silhouette | outer body, base, handle, wand | 0.48% | always; RDP 1.2 px + Bézier |
| Form | panel edges, part boundaries, tray lip | 0.26% | length ≥ 5.5% diagonal, turning ≤ 0.55°/px |
| Detail | buttons, knobs, vents, badge ring | 0.125% | short + strong; closed controls ≥ 3 mm, circularity ≥ 0.28 |
| Texture | reflections, dust, lettering, shadow | — | remove; flatten colour instead |

At 120 mm width this photo gives 0.80 / 0.43 / 0.21 mm. The ratios are optical,
not ISO 128 millimetres; do not claim ISO 128 compliance.

## One rule per failure

| Symptom | Real cause | Fix |
|---|---|---|
| Every edge is a double line | Canny returns two contours per ridge | dedupe with a 3 px mask, ≥70% coverage |
| Drawing looks sketchy | detail budget is filling with 20×2 px slivers | score closed loops by bbox/area, not circumference; reject < 3 mm |
| Badge/logo is a scribble | lettering traced as line or as holes | fill small holes; remove low-circularity decals; keep the badge shape |
| Grey puddle under the object | cast shadow is inside the GrabCut mask | trim below the lowest dark pixel per column; disclose the IoU loss |
| “Detail” is a second pile of long lines | detail chosen from leftover long edges | classify form first; detail only from short edges |
| Chrome is a dark clump | k-means splits reflections into islands | 5 tones, bilateral + mode filter, small-island merge, rim suppression |
| Line drawing is too heavy | silhouette/form weights are absolute px | derive from object height, clamp, then check at final width |
| Full trace looks “more accurate” | coverage is chasing texture | compare node count and ink; show the full trace as the strawman |

## Honesty

- The pipeline is **not semantic**: it cannot know a logo from a vent. Say which
  parts were curated by a human.
- A photo is a projection; a drawing is an interpretation. Removing a shadow or
  a reflection is a decision, not a bug — record it.
- Do not promise a print proof from a screen render. VectorCraft render is rung
  4; Illustrator/Inkscape and print are separate rungs.
- Keep the source photo only when its licence permits redistribution; otherwise
  reference it and keep it out of the repository.
