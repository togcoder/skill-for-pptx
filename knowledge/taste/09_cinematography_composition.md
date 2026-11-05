# Domain 9: Cinematography & Photography Composition

## 1. Overview & Cultural Authority
Cinematography is the art of directing visual attention, establishing emotional resonance, and organizing three-dimensional physical space onto a flat two-dimensional screen. Mastered across a century of film history by cinematographers (ASC) and editors like Walter Murch (*In the Blink of an Eye*), the principles of framing, lighting contrast, depth layering, and spatial continuity directly govern how human eyes consume visual media.

When applied to slide presentations, cinematographic composition elevates a deck from a dry corporate spreadsheet into an engaging, visually compelling narrative experience.

## 2. Core Principles & Formulas

### 2.1. The Rule of Thirds & Golden Power Points
Human visual attention does not naturally fixate on the dead geometric center of a rectangular frame; it scans along natural focal intersection points.
- Divide the $16:9$ canvas ($W \times H$) into a $3\times 3$ grid:
  - Vertical gridlines: $x = \frac{1}{3} W \approx 4.44"$, $x = \frac{2}{3} W \approx 8.89"$.
  - Horizontal gridlines: $y = \frac{1}{3} H = 2.50"$, $y = \frac{2}{3} H = 5.00"$.
- **The 4 "Power Points":**
  $$(1/3, 1/3), \quad (2/3, 1/3), \quad (1/3, 2/3), \quad (2/3, 2/3)$$
- **Compositional Application:**
  - Place primary focal subjects (portraits, key hardware emblems, hero KPI figures) at one of the power points.
  - Counter-balance the subject with negative space or supporting editorial text occupying the opposing two-thirds.
  - Avoid placing every element dead-center, which creates static, uninspired compositions.

### 2.2. Spatial Depth Layering: Three Planes of Composition
To create an immersive sense of physical depth on a flat presentation slide:
```
[Viewer]
   │
   ▼
┌────────────────────────────────────────────────────────┐
│ [Foreground (FG)] : Subtle framing element / accent    │
│   (e.g. translucent pill, soft floating particle)      │
├────────────────────────────────────────────────────────┤
│ [Midground (MG)]  : Primary Subject / Narrative Focus │
│   (e.g. sharp high-contrast card, hero portrait)       │
├────────────────────────────────────────────────────────┤
│ [Background (BG)] : Atmospheric depth / canvas         │
│   (e.g. dark slate tone, subtle isometric grid)        │
└────────────────────────────────────────────────────────┘
```
- By establishing 3 distinct layers with varying contrast and sharpness, the slide gains architectural depth rather than looking like flat cardboard cutouts.

### 2.3. The 180-Degree Rule & Screen Direction Continuity
In film editing, the camera must remain on one side of the axis of interaction between two characters. If the camera crosses the line, left and right swap positions, disorienting the viewer.
- **Application to Slide Transitions & Motion:**
  - If a narrative progression flows from left to right (Past $\to$ Present $\to$ Future), elements must enter from the right and travel leftward.
  - If an element exits toward the right, the subsequent slide must NOT bring that same element back from the left, which creates a jarring spatial collision.
  - Maintain consistent screen direction throughout a thematic arc.

### 2.4. Walter Murch’s Rule of Six for Editing Transitions
When transitioning between slides or states, cuts and morphs should be evaluated against Murch's hierarchy of importance:
1. **Emotion ($51\%$):** Does the transition reflect the emotional tone of the speaker?
2. **Story ($23\%$):** Does the transition advance the narrative point?
3. **Rhythm ($10\%$):** Does the cut occur on a natural speaking cadence beat?
4. **Eye-Trace ($7\%$):** Does the viewer’s eye land naturally on the new focal point without darting across the screen?
5. **Two-Dimensional Plane of Screen ($5\%$):** Does the transition respect 2D balance?
6. **Three-Dimensional Space ($4\%$):** Does the transition respect physical depth?
Notice that **Eye-Trace** ($7\%$) and **Rhythm** ($10\%$) far outweigh 3D spectacle! If a transition makes the viewer's eye hunt for information, it fails.

### 2.5. Visual Pacing: Establishing Shot to Close-Up
A presentation sequence should follow cinematographic scene pacing:
- **Slide 1 (Establishing Shot - Wide):** Broad context, setting the landscape, generous whitespace.
- **Slide 2 (Medium Shot - Subject Focus):** Introducing the specific conflict or core architecture.
- **Slide 3 (Close-Up - Hero Detail):** Zooming into the critical metric, breakthrough feature, or code execution.
- **Slide 4 (Re-establishing Shot):** Pulling back to reveal the transformed ecosystem.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Framing** | Asymmetric balance using Rule of Thirds power points | Centering every single header and card on every slide |
| **Eye-Trace** | Leading lines that naturally guide the viewer's eye from headline $\to$ chart $\to$ conclusion | Scattershot layouts where cards compete for attention in 4 corners |
| **Layering** | Clear visual separation between background, midground, and foreground elements | Flat, monochromatic layouts where cards merge into the background |
| **Pacing** | Alternating between high-density detail slides and breathing-room summary slides | Ten consecutive dense slides with identical visual density |

## 4. Translation to PowerPoint (OOXML)
- Z-order hierarchy in OOXML: Shape order inside `<p:spTree>` determines rendering order (earlier shapes paint behind later shapes).
- Foreground overlay elements must appear at the very bottom of `<p:spTree>`.
- Use translucent background overlays (`<a:solidFill><a:srgbClr val="0f172a"><a:alpha val="60000"/></a:srgbClr></a:solidFill>`, where `alpha val="60000"` is $60\%$ opacity) to create cinematographic depth planes.
