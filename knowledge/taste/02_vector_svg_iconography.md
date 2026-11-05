# Domain 2: Vector Graphics, SVG Craft & Iconography

## 1. Overview & Cultural Authority
Vector design at the highest level (Google Material Symbols, Apple SF Symbols 6, Lucide Icons, The Noun Project, and W3C SVG 2 Specification) is governed by strict mathematical normalization grids, geometric keylines, optical weight balancing, and path continuity.

A common failure in amateur or AI-generated presentation iconography is mixing vectors of different stroke weights, disparate bounding box aspect ratios, or off-center visual weight, making interfaces feel chaotic and unpolished.

---

## 2. GitHub Repositories & Engine References

| Repository | Focus & Innovation | Core Invariant Extracted |
|---|---|---|
| [`google/material-design-icons`](https://github.com/google/material-design-icons) | 2,500+ glyphs built on a strict $24\times 24$ grid | $2\text{dp}$ stroke width, $20\text{dp}$ circular keyline, $18\times 18\text{dp}$ square keyline, $4\text{dp}$ corner radius ceiling. |
| [`lucide-icons/lucide`](https://github.com/lucide-icons/lucide) | Community-driven clean SVG icon toolkit | 100% vector stroke preservation (`vector-effect: non-scaling-stroke`), round caps/joins, zero embedded bitmaps. |
| [`Pomax/bezierjs`](https://github.com/Pomax/bezierjs) | Mathematical implementation of Bézier curve calculus | Gauss-Legendre numerical quadrature for arc length, curvature extrema derivation, cubic-to-arc approximations. |
| [`paperjs/paper.js`](https://github.com/paperjs/paper.js) | Vector graphics scripting library | Path Boolean operations, curve normal vectors, winding rules (`nonzero` vs `evenodd`), smooth tangent maintenance. |

---

## 3. Mathematical Foundations & Vector Geometry

### 3.1. The $24\times 24\text{dp}$ Keyline Normalization Grid
All iconography must be authored within a standardized coordinate space where outer shapes occupy matched perceptual surface areas:
$$\begin{aligned}
\text{Canvas Size} &= 24\text{dp} \times 24\text{dp} \quad (1\text{dp} = 1/160\text{ inch}) \\
\text{Circular Keyline Diameter} &= 20\text{dp} \quad (\text{Area } A_{\text{circle}} = \pi \cdot 10^2 \approx 314.16\text{ dp}^2) \\
\text{Square Keyline Bounds} &= 17.72\text{dp} \times 17.72\text{dp} \quad (\text{Area } A_{\text{square}} \approx 314\text{ dp}^2) \\
\text{Horizontal Rectangle Bounds} &= 20\text{dp} \times 16\text{dp} \quad (\text{Area } A_{\text{rect\_h}} = 320\text{ dp}^2) \\
\text{Vertical Rectangle Bounds} &= 16\text{dp} \times 20\text{dp} \quad (\text{Area } A_{\text{rect\_v}} = 320\text{ dp}^2)
\end{aligned}$$
*Rule:* By matching the visual surface area of circles, squares, and rectangles to $\approx 314 - 320\text{ dp}^2$, shapes of different topologies appear identical in visual weight when placed in adjacent cards.

### 3.2. Optical Center of Mass vs. Geometric Bounding Box
The geometric center $(\bar{x}_{\text{geo}}, \bar{y}_{\text{geo}})$ of a shape's bounding box is often visually incorrect for asymmetric shapes (e.g., play triangles, stars, bell icons). Human perception balances according to the **two-dimensional centroid (center of area mass)**:
$$\mathbf{r}_{\text{centroid}} = \frac{1}{A} \iint_{S} \begin{bmatrix} x \\ y \end{bmatrix} dA$$

*Example: Right-Pointing Play Triangle:*
- For an equilateral triangle of width $W$, the geometric midpoint is $W/2 = 0.50 W$.
- The center of area mass is located at:
  $$x_{\text{centroid}} = \frac{1}{3} W \approx 0.333 W \quad (\text{from the flat base})$$
- *Prescription:* Inside a circular badge or button, the play icon must be translated rightward by:
  $$\Delta x = +\left(\frac{1}{2} - \frac{1}{3}\right) W = +\frac{1}{6} W \approx +0.167 W$$
  Centering the geometric bounding box makes the play button appear awkwardly dragged to the left.

### 3.3. Pomax Arc Length & Gauss-Legendre Quadrature
A parametric cubic Bézier curve is defined by:
$$C(t) = (1-t)^3 P_0 + 3(1-t)^2 t P_1 + 3(1-t) t^2 P_2 + t^3 P_3 \quad (t \in [0, 1])$$
Its velocity vector is $C'(t) = [x'(t), y'(t)]$. The arc length $L$ cannot be computed analytically in closed form:
$$L = \int_0^1 \sqrt{x'(t)^2 + y'(t)^2} \, dt$$
We approximate $L$ with 5-point Gauss-Legendre quadrature:
$$L \approx \sum_{i=1}^5 w_i \cdot \left\| C'\left(\frac{1 + x_i}{2}\right) \right\| \cdot \frac{1}{2}$$
Where $x_i$ and $w_i$ are standard Legendre roots and weights. This is critical for computing dashed border strokes and stroke-dasharray animations that do not pinch or distort at corners.

### 3.4. Curvature ($\kappa$) and Smoothness
$$\kappa(t) = \frac{x'(t) y''(t) - y'(t) x''(t)}{\left(x'(t)^2 + y'(t)^2\right)^{3/2}}$$
Smooth aesthetic curves maintain $\kappa(t)$ continuous without sudden spikes, preventing kinks in custom DrawingML paths.

---

## 4. OpenXML DrawingML Vector Architecture

In PowerPoint OOXML, custom vector geometry is authored inside `<p:sp>` using `<a:custGeom>` and `<a:pathLst>`:

```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="201" name="Vector Icon: Shield Check"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="1828800" y="1828800"/>
      <a:ext cx="457200" cy="457200"/> <!-- 0.5in x 0.5in = 457200 EMU -->
    </a:xfrm>
    <a:custGeom>
      <a:avLst/>
      <a:gdLst/>
      <a:ahLst/>
      <a:cxnLst/>
      <a:rect l="0" t="0" r="2400" b="2400"/>
      <a:pathLst>
        <a:path w="2400" h="2400">
          <a:moveTo><a:pt x="1200" y="200"/></a:moveTo>
          <a:cubicBezTo>
            <a:pt x="1800" y="200"/><a:pt x="2200" y="600"/><a:pt x="2200" y="1200"/>
          </a:cubicBezTo>
          <a:cubicBezTo>
            <a:pt x="2200" y="1800"/><a:pt x="1200" y="2200"/><a:pt x="1200" y="2200"/>
          </a:cubicBezTo>
          <a:cubicBezTo>
            <a:pt x="1200" y="2200"/><a:pt x="200" y="1800"/><a:pt x="200" y="1200"/>
          </a:cubicBezTo>
          <a:cubicBezTo>
            <a:pt x="200" y="600"/><a:pt x="600" y="200"/><a:pt x="1200" y="200"/>
          </a:cubicBezTo>
          <a:close/>
        </a:path>
      </a:pathLst>
    </a:custGeom>
    <a:solidFill><a:srgbClr val="0F172A"/></a:solidFill>
    <a:ln w="19050" cap="rnd"> <!-- 1.5pt line width, round cap -->
      <a:solidFill><a:srgbClr val="38BDF8"/></a:solidFill>
      <a:round/> <!-- round join -->
    </a:ln>
  </p:spPr>
</p:sp>
```

---

## 5. Python Centroid Offset Calculation Tool

```python
"""
Optical Centroid Calculator for Vector Shapes
Computes the exact delta (dx, dy) required to optically balance a vector inside an outer frame.
"""
import numpy as np

def compute_polygon_centroid(vertices):
    """
    vertices: list of (x, y) tuples forming a closed polygon.
    Returns (area, centroid_x, centroid_y) using Green's Theorem.
    """
    x = np.array([v[0] for v in vertices])
    y = np.array([v[1] for v in vertices])
    
    # Shoelace formula terms
    cross = x[:-1] * y[1:] - x[1:] * y[:-1]
    area = 0.5 * np.sum(cross)
    
    cx = np.sum((x[:-1] + x[1:]) * cross) / (6.0 * area)
    cy = np.sum((y[:-1] + y[1:]) * cross) / (6.0 * area)
    
    # Geometric bounding box midpoint
    bbox_mid_x = 0.5 * (np.min(x) + np.max(x))
    bbox_mid_y = 0.5 * (np.min(y) + np.max(y))
    
    optical_offset_x = bbox_mid_x - cx
    optical_offset_y = bbox_mid_y - cy
    
    return {
        "area": abs(area),
        "centroid": (cx, cy),
        "bbox_midpoint": (bbox_mid_x, bbox_mid_y),
        "recommended_shift": (optical_offset_x, optical_offset_y)
    }
```

---

## 6. Comprehensive DOs and DON'Ts

### DO:
1. **Lock uniform stroke widths across all icons.** Every icon on a slide must share the exact same stroke weight (e.g. $1.5\text{pt}$ or $2.0\text{pt}$ in DrawingML `w="19050"` or `w="25400"`).
2. **Apply optical centering to asymmetric glyphs.** Shift triangles, arrows, and chevron icons toward their apex to align their centroid with the parent badge center.
3. **Use consistent corner caps and joints.** Set `cap="rnd"` and `<a:round/>` joins uniformly across all strokes to avoid harsh spiked corners.
4. **Normalize bounding box scales.** Ensure that circle icons are scaled to $\varnothing 20\text{dp}$ and square icons to $18\times 18\text{dp}$ so visual weight remains balanced.

### DON'T:
1. **Never scale icons non-uniformly.** An icon stretched to fit an arbitrary aspect ratio (e.g. oval circle or squashed shield) immediately signals amateur design.
2. **Never mix filled and outlined icons in the same row.** If Card 1 uses an outlined linear icon, Cards 2, 3, and 4 must also use outlined linear icons.
3. **Never place intricate multi-color raster illustrations as icons.** Detailed clipart with gradients, drop shadows, and complex shading turns into visual mud at presentation viewing distances.
