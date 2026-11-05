# Domain 2: Vector Graphics, Iconography & SVG Craft

## 1. Overview & Cultural Authority
Iconography and vector graphics provide visual punctuation, rapid cognitive scanning anchors, and symbolic representations. Across Google Material Symbols, Apple SF Symbols, and open-source standards like Lucide and Feather, professional vector craft is distinguished by strict mathematical grids, uniform stroke weight, and optical correction.

Amateur AI vector graphics are plagued by inconsistent stroke weights, irregular anchor points, lack of sub-pixel grid alignment, and using colored emojis as system icons.

## 2. Core Principles & Formulas

### 2.1. Keyline Grids & Geometric Weight Balancing (Material Design)
A square and a circle of identical width and height do NOT have the same visual area:
- Square area: $A_{\text{square}} = w \times h = s^2$
- Circle area: $A_{\text{circle}} = \frac{\pi}{4} s^2 \approx 0.785 s^2$
If a circular icon is drawn at $24\times 24\text{px}$ and a square icon is drawn at $24\times 24\text{px}$, the square appears significantly heavier and visually dominates the circle.

**Keyline Normalization Rules (on a $24\times 24\text{dp}$ base canvas):**
- **Circle Keyline:** $\varnothing 20\text{dp}$ (Area $\approx 314\text{dp}^2$)
- **Square Keyline:** $17.6\times 17.6\text{dp} \approx 18\times 18\text{dp}$ (Area $\approx 310-324\text{dp}^2$)
- **Vertical Rectangle:** $16\times 20\text{dp}$ (Area $\approx 320\text{dp}^2$)
- **Horizontal Rectangle:** $20\times 16\text{dp}$ (Area $\approx 320\text{dp}^2$)
By constraining outer silhouettes to these keylines, icons of different basic shapes carry equal visual weight.

### 2.2. Uniform Stroke Weight Discipline
Within an interface or slide deck:
- Exactly **one canonical stroke weight** across all regular-scale icons:
  $$\text{Stroke Width} = 2.0\text{px} \quad (\text{or } 1.5\text{px} \text{ for delicate editorial styles})$$
- Stroke Caps and Joins: Always use `stroke-linecap="round"` and `stroke-linejoin="round"` to prevent jarring visual spikes at acute angles.
- Never mix filled and outlined icons within the same navigational or thematic tier. Outline is for unselected/neutral state; filled is for active/selected state.

### 2.3. The 16px Silhouette Readability Test (The Noun Project)
If an icon is scaled down to $16\times 16\text{px}$ and filled with solid black, its contour must remain instantly identifiable.
- Avoid internal micro-details (e.g. clock hands with minute tick marks, gear teeth with $< 8$ teeth).
- Minimum negative space gap between adjacent vector strokes:
  $$\text{Gap}_{\min} \ge 2\text{px}$$
  Anything narrower bleeds together at low resolutions or on projector displays.

### 2.4. Optical Center of Mass vs. Bounding Box Center
Geometric center of a bounding box ($\frac{x_{\min}+x_{\max}}{2}, \frac{y_{\min}+y_{\max}}{2}$) rarely coincides with the optical center of mass for asymmetric shapes (e.g., play button triangle, bell icon, speech bubble).
- A triangle pointing right must have its horizontal anchor shifted slightly to the right ($+1.5\text{px}$ to $+2\text{px}$ on a $24\text{px}$ canvas) to prevent it from looking awkwardly pushed to the left.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Format** | Clean SVG path with integer or half-integer coordinates, or native OOXML shape vectors (`p:sp` / `a:path`) | Raster PNG icons scaled up or down, showing blurry edges |
| **System** | Use one consistent vector family (Lucide, Material, or Feather) | Mixing 3 different icon styles (e.g., thin outline + 3D glossy + cartoon flat) |
| **Icons as Text** | Align icon vertically to the font's cap-height or baseline | Let icons float haphazardly above or below text lines |
| **Emoji Ban** | Use purposeful monochrome or single-tone vector glyphs | Using colorful consumer emojis (🚀, 💡, 🔥, ⚙️) as corporate slide icons |
| **Color Role** | Tint icons from the semantic palette (neutral dark, muted steel, or singular accent) | Applying random rainbow fills to every icon in a grid |

## 4. Translation to PowerPoint (OOXML)
- In PPTX, prefer native vector shapes (`p:sp` with `a:custGeom` or preset geometry) or embedded SVG (`asvg:svgBlip`) over raster bitmaps.
- For circular badges containing icons:
  - Outer circle: $0.6" \times 0.6"$ ($548,640 \times 548,640$ EMUs)
  - Centered icon: $0.32" \times 0.32"$ ($292,608 \times 292,608$ EMUs)
  - Centering coordinates: $x_{\text{icon}} = x_{\text{circle}} + \frac{w_{\text{circle}} - w_{\text{icon}}}{2}$.
- Outline stroke: `<a:ln w="19050">` ($1.5\text{pt}$ in EMUs, where $1\text{pt} = 12,700$ EMUs).
