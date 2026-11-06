# Domain 4: CAD & Industrial Design Craftsmanship

## 1. Overview & Cultural Authority
Industrial design craftsmanship (Dieter Rams' 10 Principles for Braun, Jony Ive's unibody design at Apple, Teenage Engineering, Bang & Olufsen, and Class-A automotive surfacing) is grounded in **rigorous surface continuity, geometric proportion, and functional necessity**.

Dieter Rams' central philosophy—***Weniger, aber besser*** (Less, but better)—dictates that every fillet, radius, line, and enclosure must justify its physical existence. In presentation design, CAD craftsmanship governs card rounding, nested concentric padding, and structural grid alignments.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Architecture & Focus | Core Invariant Extracted |
|---|---|---|
| [`FreeCAD/FreeCAD`](https://github.com/FreeCAD/FreeCAD) | Open-source parametric 3D CAD modeler (OpenCASCADE kernel) | B-spline curvature comb analysis; G2 fillet transition computation; non-manifold edge detection. |
| [`solvespace/solvespace`](https://github.com/solvespace/solvespace) | Parametric geometric constraint solver | Exact dimension constraint satisfaction; tangent and perpendicularity propagation without floating-point drift. |
| [`libigl/libigl`](https://github.com/libigl/libigl) | Geometry processing library | Discrete differential geometry; Laplace-Beltrami mean curvature flow; minimal surface area optimization. |

---

## 3. Mathematical Foundations: Curvature Continuity ($G_0$ to $G_3$)

In CAD and industrial styling, the interface between two joining curve segments $C_1(t)$ and $C_2(u)$ at joint $t=1, u=0$ is classified into 4 discrete mathematical continuity tiers:

```
[ G0: Positional ]     [ G1: Tangential ]     [ G2: Curvature Continuous ]     [ G3: Torsion / Jerk Free ]
      /\                     ╭──────╮                   ╭──────╮                          ╭──────╮
     /  \                    │ Fillet│                  │Squircle│                        │Class-A│
    /    \                   │ (Arc) │                  │ (G2)  │                        │ (G3)  │
Sharp Corner (Kink)     Highlight Snaps       Highlight Flows Cleanly          Porsche/Apple Surface
```

### 3.1. $G_0$ Continuity (Positional)
$$C_1(1) = C_2(0)$$
The curves touch at a single point, but their tangent vectors differ. This forms a sharp corner or knife edge.

### 3.2. $G_1$ Continuity (Tangential - Standard Fillet)
$$C_1(1) = C_2(0) \quad \text{and} \quad C'_1(1) = k \cdot C'_2(0) \quad (k > 0)$$
The tangent directions match, preventing a corner point. However, because a straight line has curvature $\kappa = 0$ ($R = \infty$) and a circular arc has constant curvature $\kappa = 1/R$, the curvature experiences an **instantaneous step-function jump**:
$$\Delta \kappa = \left| \frac{1}{R} - 0 \right| = \frac{1}{R} \ne 0$$
*Visual Defect:* Across this seam, light reflections break abruptly. Human eyes perceive a visible "crease line" at the tangent junction.

### 3.3. $G_2$ Continuity (Curvature - The Squircle)
The magnitude and center of curvature match across the junction:
$$\kappa_1(1) = \kappa_2(0) \implies \frac{\| C'_1(1) \times C''_1(1) \|}{\| C'_1(1) \|^3} = \frac{\| C'_2(0) \times C''_2(0) \|}{\| C'_2(0) \|^3}$$
The curvature accelerates smoothly from $0$ to its maximum, eliminating specular highlight seams.

*The Lamé Superellipse (Squircle Formula):*
$$\left| \frac{x}{a} \right|^n + \left| \frac{y}{b} \right|^n = 1$$
Where $n \approx 4.0 - 5.0$ defines the Apple squircle icon and hardware curvature. At $n=2$, the curve is a circle; at $n \to \infty$, it approaches a square.

### 3.4. $G_3$ Continuity (Acceleration & Torsion)
The rate of change of curvature ($\kappa'$) is continuous:
$$C'''_1(1) = k \cdot C'''_2(0)$$
This represents the highest tier of Class-A surfacing used in Apple unibody enclosures and high-performance automotive bodywork.

---

## 4. The Concentric Radii Law

When nesting one rounded container inside another (e.g. an inner icon badge inside an outer card, or an inner image box inside a framed container), the corner radii must maintain **geometric concentricity**.

### 4.1. Mathematical Formulation
$$\mathbf{R}_{\text{inner}} = \max\left(0, \mathbf{R}_{\text{outer}} - \mathbf{P}\right)$$
Where:
- $R_{\text{outer}}$ is the corner radius of the outer container.
- $P$ is the uniform padding distance between inner and outer containers.
- $R_{\text{inner}}$ is the target corner radius of the inner element.

### 4.2. Geometric Failure Proof
- **Case 1: $R_{\text{inner}} = R_{\text{outer}}$ (The Constant Radius Failure)**
  If $R_{\text{inner}} = R_{\text{outer}}$, the physical distance between the inner and outer boundary in the corner diagonal ($d_{\text{diag}}$) becomes:
  $$d_{\text{diag}} = \sqrt{2} \cdot P - (\sqrt{2} - 1) \cdot R_{\text{outer}} < P$$
  The padding visibly pinches at the corners.
- **Case 2: $R_{\text{inner}} = 0$ while $R_{\text{outer}} > P$ (The Sharp Corner Trap)**
  Placing a sharp $90^\circ$ rectangle inside a rounded card with padding $P < R_{\text{outer}}$ causes the sharp inner vertex to punch visually toward the curved outer wall.

---

## 5. OpenXML DrawingML Adjustment Formula

In DrawingML, the `<a:gd name="adj" fmla="val ..."/>` attribute for `<a:prstGeom prst="roundRect">` does not represent a static pixel value. It is defined as a fraction of $100,000$ relative to $\min(W, H)$:
$$\text{adj} = \text{round}\left( \frac{R_{\text{EMU}}}{\min(W_{\text{EMU}}, H_{\text{EMU}})} \times 100000 \right)$$

To achieve concentric radii between Outer Card ($W_1, H_1$) and Inner Container ($W_2, H_2$ with padding $P$):
$$\text{adj}_{\text{inner}} = \text{round}\left( \frac{R_{\text{outer\_EMU}} - P_{\text{EMU}}}{\min(W_{2\text{\_EMU}}, H_{2\text{\_EMU}})} \times 100000 \right)$$

---

## 6. Python Concentric Radii Engine

```python
"""
CAD Concentric Radii Engine
Calculates DrawingML adjustment values (adj) ensuring G2-compliant concentric corners.
"""
def calculate_concentric_adj(outer_w_in, outer_h_in, outer_r_in, padding_in):
    EMU_PER_INCH = 914400
    
    outer_w = int(outer_w_in * EMU_PER_INCH)
    outer_h = int(outer_h_in * EMU_PER_INCH)
    outer_r = int(outer_r_in * EMU_PER_INCH)
    pad = int(padding_in * EMU_PER_INCH)
    
    inner_w = outer_w - 2 * pad
    inner_h = outer_h - 2 * pad
    inner_r = max(0, outer_r - pad)
    
    adj_outer = round((outer_r / min(outer_w, outer_h)) * 100000)
    adj_inner = round((inner_r / min(inner_w, inner_h)) * 100000) if inner_r > 0 else 0
    
    return {
        "outer": {
            "w_emu": outer_w, "h_emu": outer_h,
            "r_emu": outer_r, "adj": adj_outer
        },
        "inner": {
            "w_emu": inner_w, "h_emu": inner_h,
            "r_emu": inner_r, "adj": adj_inner
        },
        "is_concentric": (outer_r - inner_r) == pad
    }
```

---

## 7. Comprehensive DOs and DON'Ts

### DO:
1. **Always enforce $R_{\text{inner}} = R_{\text{outer}} - \text{padding}$.** Never copy-paste the outer container's radius onto nested badges or image frames.
2. **Align card borders to the physical pixel grid.** Ensure all coordinates in EMUs divide cleanly by $9,525$ ($1\text{pt} = 12,700\text{ EMU}$, $1\text{px at 96 DPI} = 9,525\text{ EMU}$) to prevent blurry antialiased border edges.
3. **Keep corner radii restrained.** A card corner radius should never exceed $12\text{pt}$ ($152,400\text{ EMU}$) on standard presentation cards. Massive "pill" cards look juvenile and waste content area.

### DON'T:
1. **Never use non-uniform corner radii on adjacent cards.** If Card 1 has an $8\text{pt}$ radius, Cards 2 and 3 must not use $16\text{pt}$ or $4\text{pt}$.
2. **Never place a sharp inner element inside a rounded outer container without sufficient clearance.** If $R_{\text{inner}} = 0$, padding must satisfy $P \ge R_{\text{outer}}$.
3. **Never stretch a rounded rectangle non-uniformly without locking the radius adjustment.** In PowerPoint, resizing a `roundRect` without adjusting `adj` stretches the corner into an egg shape.
