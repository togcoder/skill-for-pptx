---
name: vector-craft
description: Reconstruct a product photo as a clean, editable 2.5D vector illustration — identify the parts, set one projection, build boxes/cylinders/plates/controls, and paint the visible faces. Use when the user supplies a photo and asks for a vector drawing, product illustration, technical line art, print asset, or says an auto-trace looks crude, noisy or traced. Do not use edge tracing as the deliverable.
---

# Vector Craft

> **Status: EXPERIMENTAL — T053 [vector], review requested.** This skill is not a
> canonical product path until an independent review accepts it. T051 is kept
> as a **negative result**: Canny tracing was rejected by the owner.

You are reconstructing an object, not tracing a photograph. A camera image is
a projection full of noise, reflections and occlusion. A drawing is a **model**:
parts with known shapes, one camera, deliberate materials. The photo supplies
proportions, colours and the camera; it never supplies the line work.

The distinction is testable:

| Trace (T051, rejected) | Reconstruction (T053) |
|---|---|
| Canny contours in pixel coordinates | boxes/cylinders in object coordinates |
| every reflection becomes a line | reflections become material tones |
| 1,437 nodes of edge soup | semantic groups: `base`, `tower`, `group-head` |
| one line at a time | a dimension change moves the whole part |
| no occlusion model | faces painted back-to-front |

## Workflow

1. **Measure the object, not the pixels.**
   - Crop the product; record overall width, height and depth ratios.
   - List the parts and their primitives: base, lower body, tower, top panel,
     drip tray, group head, portafilter, steam wand, knobs, badge, controls.
   - Write down which faces are visible (front, left side, top) and the
     approximate depth order. This list is the scene graph.
2. **Choose one projection.**
   ```
   X = ox + x·sx + z·dx
   Y = oy − y·sy + z·dy
   ```
   `x` runs along the front, `y` up, `z` back. One projection for every part;
   never eyeball a second vanishing point. If the view is taller than wide,
   stretch `sy` and compensate front-plane circles (`ry = r·sx/sy`) so they
   stay round on screen.
3. **Build primitives in object coordinates.**
   ```powershell
   python $ROOT/scripts/vector_reconstruct.py inspect reconstruction.svg
   ```
   - `box(x0,y0,z0,x1,y1,z1)` paints left side, top, front.
   - `cylinder_y` for knobs and feet; `cylinder_z` for the portafilter.
   - `front_rounded` / `front_circle` for plates, badges, switches.
   - `tube` only for a hose/wand; it is screen-space, not a traced edge.
4. **Paint the faces with one light.**
   - Front lighter, left side darker, top lightest (or the reverse, but keep it
     consistent).
   - Chrome is a light-to-dark gradient, not a copy of the reflections.
   - Add at most two designed highlight bands on the front; they are shapes,
     not edge clusters.
5. **Add only the controls that identify the product.**
   - A badge is a cream disc + red ring + **typeset** wordmark, not traced
     lettering.
   - A switch plate is a rounded black plate + three cream paddles + tiny
     labels. Do not trace every screw or vent.
   - A drip grid is a repeated slot pattern on the tray's top face.
6. **Render and iterate.**
   ```powershell
   vectorcraft-cli convert reconstruction.svg reconstruction.png --scale 2
   vectorcraft-cli info reconstruction.svg
   ```
   Look for: floating parts, a part that reads as a different object (a group
   head that looks like a camera lens), a seam that cuts a panel in half,
   inconsistent depth, a badge that is too large, a cast shadow that is not a
   designed ellipse.
7. **Verify.**
   - SVG parses; groups carry semantic IDs; no `<image>`, no base64.
   - VectorCraft `info` reports paths/groups and no warnings.
   - The scene is deterministic: building twice gives the same bytes.
   - The smallest detail is readable at the final width.

## Primitive map

| Part | Primitive | Notes |
|---|---|---|
| base / plinth | box | slightly larger than the body; feet below |
| lower body | box | chrome front, yellow side |
| tower | box + split front faces | chrome lower, black upper |
| top panel | box | overhangs the tower; cup rails on top |
| drip tray | box + top slot pattern | grid is repeated quads, not texture |
| group head | cylinder along z + rings | boss + gasket + portafilter |
| portafilter | cylinder along z | chrome collar, black handle |
| steam wand | screen-space tube | chrome + black grip |
| knobs | vertical cylinder | black base ring + yellow body |
| badge | front circle + text | cream disc, red ring, vector wordmark |
| controls | front rounded rects | black plate, cream paddles, labels |

## Do not

- **Do not pass Canny/RDP contours off as a reconstruction.** T051 did that and
  was rejected. The tell is node soup, doubled contours, text traced as a
  scribble, and reflections drawn as lines.
- Do not use a different projection for each part.
- Do not trace a logo at 2–3 mm; typeset it or omit it.
- Do not model a through-hole by filling it; add a paper-coloured layer.
- Do not claim photogrammetry or exact dimensions. This is a designed
  interpretation from a single photo.

## Honesty

- Record the photo source/licence and the manual measurements.
- Say which parts are simplified, which controls are omitted, and which
  materials are flat approximations.
- A reconstruction can be edited by changing a number; a trace cannot. If the
  user cannot change the depth/width without redrawing, it is a trace.
- VectorCraft render is rung 4; a physical print and a second editor are still
  separate checks.
