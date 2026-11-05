# Domain 12: Spatial Geometry, Collision Physics & Layout Algorithms

## 1. Overview & Cultural Authority
Spatial layout taste (computational geometry, Minkowski sum collision detection, and 1D/2D Box-Packing & Gutter Equalization) treats the 2D presentation canvas not as an arbitrary canvas for human guessing, but as a **continuous 2D geometric coordinate space governed by spatial constraints**.

The most catastrophic failure in automated presentation generation—exemplified directly in the user's Slide 2 defect—is the **AABB Collision Defect**: placing an emblem, graphic, or decorative node at coordinates that physically intersect the bounding box of a headline or subtitle text frame. Computational spatial physics exists to eliminate geometric collisions mathematically.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Focus & Implementation | Core Invariant Extracted |
|---|---|---|
| [`d3/d3-hierarchy`](https://github.com/d3/d3-hierarchy) | Hierarchical layout algorithms (Squarified Treemaps, Pack) | Bruls-Huizing-van Wijk aspect ratio optimization ($\approx 1.0$); non-overlapping containment guarantees. |
| [`mourner/rbush`](https://github.com/mourner/rbush) | High-performance 2D spatial index for bounding boxes | R-tree spatial indexing; $O(\log N)$ collision queries; fast bounding-box overlap pruning. |
| [`Chlumsky/msdfgen`](https://github.com/Chlumsky/msdfgen) | Multi-channel signed distance field generator | Exact Euclidean distance fields; signed boundary distance computation for spatial clearance. |

---

## 3. Mathematical Foundations: Collision Physics & Safe Zones

### 3.1. Axis-Aligned Bounding Box (AABB) Intersection
Let shape $A$ and shape $B$ be defined by their minimum and maximum coordinates in PowerPoint EMUs:
$$A = [x_{\min}^A, y_{\min}^A, x_{\max}^A, y_{\max}^A], \quad B = [x_{\min}^B, y_{\min}^B, x_{\max}^B, y_{\max}^B]$$

Two shapes collide if and only if their projections overlap on **both** the X and Y axes simultaneously:
$$\text{Collide}(A, B) \iff \left( x_{\min}^A < x_{\max}^B \land x_{\max}^A > x_{\min}^B \right) \land \left( y_{\min}^A < y_{\max}^B \land y_{\max}^A > y_{\min}^B \right)$$

#### Overlap Area Computation
$$\begin{aligned}
W_{\text{overlap}} &= \max\left(0, \min(x_{\max}^A, x_{\max}^B) - \max(x_{\min}^A, x_{\min}^B)\right) \\
H_{\text{overlap}} &= \max\left(0, \min(y_{\max}^A, y_{\max}^B) - \max(y_{\min}^A, y_{\min}^B)\right) \\
\text{Area}_{\text{overlap}} &= W_{\text{overlap}} \times H_{\text{overlap}}
\end{aligned}$$
*Invariant:* In professional layout, $\text{Area}_{\text{overlap}}$ must equal **exactly zero** between all non-nested elements.

---

### 3.2. Minkowski Sum & Safe-Zone Buffer Expansion
Merely avoiding physical touching ($\text{Area}_{\text{overlap}} = 0$) is insufficient for aesthetic taste. Text boxes and graphic icons require an **aesthetic breathing zone (Safe Zone)**.

We define the Minkowski sum of shape $B$ with an isotropic metric disk/buffer of radius $\delta$:
$$B_{\text{safe}} = B \oplus D_\delta = \left[ x_{\min}^B - \delta, y_{\min}^B - \delta, x_{\max}^B + \delta, y_{\max}^B + \delta \right]$$

For enterprise presentation decks:
$$\delta_{\text{safe}} \ge 0.350'' \quad (320,040\text{ EMU})$$

*The Collision Guard Condition:*
$$\text{Collide}(A, B_{\text{safe}}) = \text{False}$$
If shape $A$ enters the expanded safe zone of shape $B$, the layout engine must either translate shape $A$ along the separating axis vector or re-architect into a two-column modular grid.

---

### 3.3. OpenXML Group & Rotation Coordinate Resolution

In PowerPoint OpenXML, an automated collision linter will fail if it evaluates local coordinates without matrix un-nesting:

#### A. Group Coordinates Mapping (`p:grpSp`)
Coordinates of a child shape inside a group are defined in child space (`a:chOff`, `a:chExt`) and must be transformed into slide space:
$$\begin{aligned}
X_{\text{world}} &= X_{\text{grp}} + (X_{\text{child}} - chOff_X) \times \frac{cx_{\text{grp}}}{chExt_X} \\
Y_{\text{world}} &= Y_{\text{grp}} + (Y_{\text{child}} - chOff_Y) \times \frac{cy_{\text{grp}}}{chExt_Y}
\end{aligned}$$

#### B. Rotated Bounding Box Expansion (`rot`)
PowerPoint specifies rotation in units of $1/60,000$ degree (`rot="angle"`). Rotation occurs around the shape's center point. The expanded axis-aligned bounding box of a rotated shape is:
$$\begin{aligned}
\theta &= \frac{\text{rot}}{60000} \times \frac{\pi}{180} \\
W'_{\text{rot}} &= W \cdot |\cos\theta| + H \cdot |\sin\theta| \\
H'_{\text{rot}} &= W \cdot |\sin\theta| + H \cdot |\cos\theta| \\
x'_{\min} &= x_c - \frac{W'_{\text{rot}}}{2}, \quad x'_{\max} = x_c + \frac{W'_{\text{rot}}}{2}
\end{aligned}$$

#### C. Optical Centroid Offset for Asymmetric Icons (Play Triangles)
For asymmetric directional icons (e.g. right-pointing triangle play button), the visual center of mass does not coincide with the bounding box center:
$$\Delta x = +\frac{1}{6} W_{\text{icon}}$$
Inside a circular badge, shift the triangle rightward by $\Delta x$ so visual mass balances naturally.

---

### 3.4. 1D/2D Box-Packing & Gutter Equalization
When distributing $N$ cards across a canvas, gutters must remain strictly identical:
$$x_{i+1} = x_i + w_i + G \quad (\forall i \in [1, N-1])$$
$$G = 0.250'' = 228,600\text{ EMU}$$
Symmetric outer margins:
$$M_{\text{left}} = M_{\text{right}} = 0.800'' = 731,520\text{ EMU}$$

---

## 4. Python Complete AABB Minkowski Solver (With Group & Rotation Support)

```python
"""
Complete AABB Minkowski Collision Solver
Resolves OpenXML Group coordinates (chOff/chExt) and rotation expansion (rot).
"""
import math

def get_world_aabb(shape_dict, parent_grp=None):
    """
    shape_dict: dict with 'x', 'y', 'w', 'h', 'rot'
    parent_grp: dict with 'x', 'y', 'cx', 'cy', 'chOff_x', 'chOff_y', 'chExt_x', 'chExt_y'
    """
    x, y, w, h = shape_dict["x"], shape_dict["y"], shape_dict["w"], shape_dict["h"]
    rot = shape_dict.get("rot", 0)
    
    # 1. Transform from group local space if nested
    if parent_grp:
        scale_x = parent_grp["cx"] / parent_grp["chExt_x"]
        scale_y = parent_grp["cy"] / parent_grp["chExt_y"]
        x = parent_grp["x"] + (x - parent_grp["chOff_x"]) * scale_x
        y = parent_grp["y"] + (y - parent_grp["chOff_y"]) * scale_y
        w = w * scale_x
        h = h * scale_y
        
    # 2. Compute rotated bounding box
    if rot != 0:
        theta = math.radians(rot / 60000.0)
        w_rot = w * abs(math.cos(theta)) + h * abs(math.sin(theta))
        h_rot = w * abs(math.sin(theta)) + h * abs(math.cos(theta))
        xc = x + w / 2.0
        yc = y + h / 2.0
        return [xc - w_rot / 2.0, yc - h_rot / 2.0, xc + w_rot / 2.0, yc + h_rot / 2.0]
    else:
        return [x, y, x + w, y + h]

def check_minkowski_collision(aabb_a, aabb_b, safe_buffer_emu=320040):
    # Expand AABB B by Minkowski safe buffer
    bx1 = aabb_b[0] - safe_buffer_emu
    by1 = aabb_b[1] - safe_buffer_emu
    bx2 = aabb_b[2] + safe_buffer_emu
    by2 = aabb_b[3] + safe_buffer_emu
    
    ax1, ay1, ax2, ay2 = aabb_a
    
    overlap_x = max(0, min(ax2, bx2) - max(ax1, bx1))
    overlap_y = max(0, min(ay2, by2) - max(ay1, by1))
    
    overlap_area = overlap_x * overlap_y
    return overlap_area > 0, overlap_area
```

---

## 5. Comprehensive DOs and DON'Ts

### DO:
1. **Maintain $\ge 0.35''$ ($320,040\text{ EMU}$) clear safe zone between text and vector graphics.**
2. **Transform local group coordinates and expand rotated bounding boxes** before calculating collision checks.
3. **Shift asymmetric play triangles by $+\frac{1}{6} W$** toward their apex to align the optical centroid.

### DON'T:
1. **Never place emblems behind high-contrast text.**
2. **Never calculate collision using un-transformed child coordinates.**
3. **Never allow uneven gutters between adjacent cards.**
