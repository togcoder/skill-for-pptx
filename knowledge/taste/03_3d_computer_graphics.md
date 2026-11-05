# Domain 3: 3D Computer Graphics & PBR Aesthetics

## 1. Overview & Cultural Authority
3D graphics in modern presentations, web interfaces, and product visualizers have evolved beyond the harsh plastic phong shading of the 1990s and early 2000s. Driven by Brent Burley’s seminal 2012 Disney Principled BRDF paper and modern Physically Based Rendering (PBR), digital 3D aesthetics now obey strict physical laws of energy conservation and microfacet scattering.

High-taste 3D graphics in slide design convey tangible materiality, spatial depth, and architectural solidity. In contrast, amateur 3D designs suffer from blown-out specular highlights, pitch-black floating drop shadows, ungrounded floating geometry without contact shadows, and disorienting wide-angle camera distortion.

## 2. Core Principles & Formulas

### 2.1. Conservation of Energy in Physically Based Rendering
Light reflecting off a surface is strictly bounded:
$$R_{\text{diffuse}} + R_{\text{specular}} + A \le 1.0$$
where $R$ is reflected light and $A$ is absorbed energy. A surface can never reflect more light than it receives.

In the **Metallic-Roughness Workflow (Disney BRDF)**:
- **Dielectric / Non-Metal (Metallic = 0.0):**
  - Base color dictates diffuse albedo.
  - Specular reflectance $F_0$ is monochromatic and capped at $4\%$ ($0.04$).
  - Examples: plastic, wood, matte paint, fabric.
- **Conductor / Metal (Metallic = 1.0):**
  - Zero diffuse reflection ($R_{\text{diffuse}} = 0$).
  - All color comes from specular reflectance, which tints reflections with the material's base color.
  - Examples: gold, chrome, anodized aluminum, brass.
- **Roughness ($\alpha \in [0.0, 1.0]$):**
  - Low roughness ($< 0.15$): sharp, brilliant, mirror-like specular highlights.
  - Medium-high roughness ($0.40 - 0.70$): smooth, broad, soft satin highlights (the preferred finish for hardware keynotes).

### 2.2. Studio Three-Point Lighting Ratios
To sculpt a 3D object so it reads with clear depth and silhouette separation:
1. **Key Light ($100\%$ intensity):**
   - Position: $30^\circ - 45^\circ$ horizontally off-axis, elevated $30^\circ - 45^\circ$.
   - Purpose: Establishes primary highlights, shadow direction, and physical volume.
2. **Fill Light ($30\% - 50\%$ intensity):**
   - Position: Opposite the key light relative to the camera, near camera axis.
   - Purpose: Softens shadows to prevent harsh pure-black silhouettes.
   - Contrast Ratio:
     $$\text{Key : Fill} \approx 2:1 \text{ to } 3:1 \quad (\text{corporate/product aesthetic})$$
3. **Rim Light / Backlight ($40\% - 70\%$ intensity):**
   - Position: Directly behind the object, pointing toward camera.
   - Purpose: Grazes the outer silhouette, creating a delicate edge rim that visually separates ("lifts") the model from dark backgrounds.

### 2.3. Ambient Occlusion (AO) & Contact Shadow Grounding
Light rays cannot easily penetrate tight crevices, cracks, and contact points between two adjacent surfaces.
- **Visual Failure:** Without contact shadows, a 3D model looks like a cheap sticker pasted onto the slide canvas.
- **Formula for Contact Shadow:** An elliptical gradient shadow placed immediately below the contact plane:
  - Width: $1.1\times - 1.2\times$ the object's base width.
  - Height: $0.15\times - 0.25\times$ the object's base width.
  - Vertical offset: directly tangent to the bottom edge ($y_{\text{shadow}} = y_{\text{base}} - \epsilon$).
  - Opacity: $25\% - 35\%$ with soft gaussian blur.

### 2.4. Camera Lens & Perspective Choice
- **50mm Lens (Field of View $\approx 40^\circ$):** "Normal" human vision perspective. Zero fish-eye distortion; preserves realistic proportions.
- **85mm Lens (Field of View $\approx 24^\circ$):** Telephoto compression. Ideal for technical diagrams and isometric-like product views.
- **Rule:** Never use ultra-wide lenses ($< 28\text{mm}$, $\text{FOV} > 65^\circ$) for product presentations; wide angles warp straight lines into distorted curves at slide margins.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Material Finish** | Matte, satin, or bead-blasted anodized aluminum (Roughness $0.4 - 0.6$) | Hyper-reflective chrome or wet plastic (Roughness $< 0.05$) reflecting fake checkerboards |
| **Shadows** | Soft, diffused contact shadows tinted with the background hue | Hard-edged, pure-black ($#000000$) drop shadows with zero blur |
| **Lighting** | Multi-point studio lighting with ACES tone-mapping curve | Flat uniform ambient light that erases all form and depth |
| **Model Hierarchy** | Clean primary subject with a clear visual hero axis | Random cluster of 3D floating shapes with competing angles and scales |

## 4. Translation to PowerPoint (OOXML)
- PowerPoint supports native 3D models via `model3d` parts (`.glb` / glTF format).
- **Camera Continuity Law (T064):** In Morph transitions between slides, PowerPoint will only smoothly interpolate 3D camera angles if both slides reference the **exact same internal `model3d` relationship part**. If separate parts are embedded, PowerPoint falls back to an abrupt 0.40s white fade!
- For native 2D shapes with 3D bevels (`a:bevelT`, `a:bevelB`), use subtle bevel depths ($0.5\text{pt} - 1.5\text{pt}$) and soft material lighting (`warmMatte` or `softmetal`) rather than extreme plastic extrusions.
