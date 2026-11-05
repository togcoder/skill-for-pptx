# Domain 4: CAD & Industrial Design Aesthetics

## 1. Overview & Cultural Authority
Industrial design aesthetics govern how physical objects convey function, ergonomics, and timeless elegance. The discipline is anchored by Dieter Rams' *Ten Principles of Good Design* ("Weniger, aber besser" - Less, but better) formulated during his 30-year tenure at Braun, and further expanded by Jony Ive's team at Apple, Richard Sapper (IBM ThinkPad), and modern hardware innovators like Teenage Engineering.

When translated to digital layout and presentation design, industrial CAD principles provide rigorous mathematical rules for surface transitions, corner curvature, tactile hierarchy, and geometric honesty.

## 2. Core Principles & Formulas

### 2.1. Dieter Rams' 10 Principles of Good Design
1. **Innovative:** Innovation develops in tandem with technology, never as an end in itself.
2. **Makes a product useful:** Emphasizes utility, disregarding anything that detracts from it.
3. **Aesthetic:** Beautiful execution directly impacts psychological well-being.
4. **Makes a product understandable:** Clarifies structure; makes the object self-explanatory.
5. **Unobtrusive:** Products are tools, neither decorative art nor status trophies.
6. **Honest:** Does not exaggerate power or value with fake promises.
7. **Long-lasting:** Transcends fashionable trends; never looks dated.
8. **Thorough down to the last detail:** Care and precision show respect for the user.
9. **Environmentally friendly:** Conserves resources, minimizes visual noise.
10. **As little design as possible:** "Less, but better." Purity and simplicity.

### 2.2. Surface Continuity Mathematics (G0, G1, G2, G3)
In CAD modeling and Class-A surfacing:

```
[G0: Positional]       [G1: Tangential]        [G2: Curvature Continuous]
   Sharp Corner           Circular Fillet              Superellipse (Squircle)
    ┌─────┐                  ╭─────╮                    ╭───────╮
    │     │                  │     │                   │         │
    │     │                  │     │                   │         │
Stripes Disconnect      Stripes Kink (V-shape)    Stripes Glide Smoothly
```

- **G0 (Position):** Surfaces share an edge, but angle changes abruptly. Creates sharp seams.
- **G1 (Tangency):** Surfaces share a tangent angle at the boundary (standard circular fillet). While smooth to the touch, light reflections break with a sharp "V-kink" because the radius of curvature jumps abruptly from $\infty$ (flat line) to a fixed radius $R$.
- **G2 (Curvature Continuity):** The radius of curvature matches continuously across the boundary:
  $$\frac{d^2 y}{dx^2}_{\text{surface 1}} = \frac{d^2 y}{dx^2}_{\text{surface 2}}$$
  Light reflections flow seamlessly across the surface without visual pinching. This is the mathematical basis of Apple's hardware and icon squircles!
- **G3 (Acceleration Continuity):** The rate of change of curvature matches continuously ($\frac{d^3 y}{dx^3}$). Used in luxury automotive bodies to prevent any optical warping under dynamic lighting.

### 2.3. Concentric Corner Radii Formula (Concentricity Rule)
When nesting a rounded card inside a container or padding a border:
$$\mathbf{R_{\text{inner}} = \max(0, \; R_{\text{outer}} - \text{padding})}$$

- **Visual Failure:** If $R_{\text{inner}} = R_{\text{outer}}$, the inner corner looks abnormally thick, pinched, and visually distorted.
- **Example:**
  - Outer card corner radius: $R_{\text{outer}} = 16\text{px}$ (or $0.20"$)
  - Internal padding: $p = 12\text{px}$ (or $0.15"$)
  - Correct inner child corner radius: $R_{\text{inner}} = 16 - 12 = 4\text{px}$ (or $0.05"$).

### 2.4. Superellipse (Lamé Curve / Squircle) Formula
The mathematical curve bridging a rectangle and an ellipse:
$$\left|\frac{x}{a}\right|^n + \left|\frac{y}{b}\right|^n = 1$$
- For $n=2$: Perfect ellipse / circle.
- For $n=1$: Rhombus.
- For $n=4$: The Apple **Squircle** (optimal balance of maximum usable internal area with continuous $G^2$ curvature).

### 2.5. Tactile Affordances & Accent Discipline
- High-contrast, monochromatic neutral chassis (matte aluminum, slate, off-black).
- Exactly **one single functional accent** (e.g. Richard Sapper's red TrackPoint, Teenage Engineering's orange rotary dial).
- The accent is strictly reserved for the primary interactive affordance or focal metric; never spread across decorative borders.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Corner Curvature** | Smooth, proportional radii ($R_{\text{inner}} = R_{\text{outer}} - p$); subtle rounded corners ($8\text{px} - 16\text{px}$) | Completely mismatched nested radii or pill shapes around large content cards |
| **Material Finish** | Clean matte finishes, subtle 1px dividers, tonal background elevation | Over-glossed reflections, faux-leather textures, or skeuomorphic chrome |
| **Functional Accent** | 1 vibrant chromatic accent ($< 80\%$ saturation) anchored to the key focal point | 4 different accent colors scattered across cards |
| **Detail Thoroughness** | Meticulous alignment down to the half-pixel or EMU; equal margin distributions | Misaligned boxes, uneven padding between adjacent columns |

## 4. Translation to PowerPoint (OOXML)
- In PPTX OOXML, a rounded rectangle is defined by `<a:prstGeom prst="roundRect">` with adjustment parameter `<a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst>`.
- **Morph Shape Type Continuity (M-02):**
  A circle and a rounded rectangle morph smoothly ONLY if both are defined using the same underlying `roundRect` shape:
  - Circle / Pill: `roundRect` with `adj = 50000` (full radius).
  - Rectangle: `roundRect` with `adj = 6000` ($6\%$ corner radius).
  PowerPoint will smoothly interpolate `adj` from $50000 \to 6000$ in a native Morph transition, whereas morphing an `ellipse` into a `roundRect` causes an ugly cross-fade!
