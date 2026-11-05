# Domain 3: 3D Computer Graphics & PBR (Physically Based Rendering)

## 1. Overview & Cultural Authority
3D graphics and modern shading taste (Pixar, Disney Animation, Google Filament by Romain Guy, Unreal Engine 5 Lumen/Nanite, and Three.js `MeshPhysicalMaterial`) have permanently moved away from empirical, plastic-looking Blinn-Phong lighting toward **Physically Based Rendering (PBR)**.

In UI and presentation design, applying 3D taste does not mean creating garish 3D spinning logos. It means understanding **light transport, physical energy conservation, surface microfacets, contact shadowing (SSAO), and depth planes** to give flat shapes a grounded, tactile, and premium presence.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Shading Architecture | Core Invariant Extracted |
|---|---|---|
| [`google/filament`](https://github.com/google/filament) | Mobile & desktop real-time PBR engine by Romain Guy | Exact energy conservation; Frostbite-style clearcoat; GGX anisotropic specular; ambient occlusion attenuation. |
| [`mrdoob/three.js`](https://github.com/mrdoob/three.js) | WebGL standard 3D engine (`MeshPhysicalMaterial`) | Schlick Fresnel approximation; Roughness-Metallic workflow; transmission/roughness decoupling. |
| [`KhronosGroup/glTF-Sample-Viewer`](https://github.com/KhronosGroup/glTF-Sample-Viewer) | Official reference implementation for glTF 2.0 PBR | Ground truth validation for Cook-Torrance BRDF; IBL (Image Based Lighting) split-sum approximation. |
| [`mitsuba-renderer/mitsuba3`](https://github.com/mitsuba-renderer/mitsuba3) | Research-grade physically based spectral path tracer | Radiative transfer equations; reciprocal BRDF symmetry; microfacet shadowing derivations. |

---

## 3. Mathematical Foundations & Microfacet Shading

### 3.1. Cook-Torrance Specular Microfacet BRDF
The Bidirectional Reflectance Distribution Function (BRDF) describes how light arriving from direction $\mathbf{l}$ reflects toward the camera $\mathbf{v}$ off a surface with macroscopic normal $\mathbf{n}$. Surfaces are modeled as collections of microscopic mirror facets with micro-normals $\mathbf{m} = \mathbf{h} = \frac{\mathbf{l} + \mathbf{v}}{\|\mathbf{l} + \mathbf{v}\|}$ (the half-vector).

The specular term is mathematically defined as:
$$f_r(\mathbf{l}, \mathbf{v}) = \frac{D(\mathbf{h}) \cdot F(\mathbf{v}, \mathbf{h}) \cdot G(\mathbf{l}, \mathbf{v}, \mathbf{h})}{4 (\mathbf{n} \cdot \mathbf{l}) (\mathbf{n} \cdot \mathbf{v})}$$

#### A. Normal Distribution Function $D(\mathbf{h})$: GGX (Trowbridge-Reitz)
GGX features a heavier, extended tail than older Gaussian models, matching real-world surfaces:
$$D_{\text{GGX}}(\mathbf{h}) = \frac{\alpha^2}{\pi \left( (\mathbf{n} \cdot \mathbf{h})^2 (\alpha^2 - 1) + 1 \right)^2}$$
Where $\alpha = \text{roughness}^2$ (Burley's perceptual roughness re-mapping).

#### B. Fresnel Term $F(\mathbf{v}, \mathbf{h})$: Schlick Approximation
Quantifies reflection intensity as a function of the incident angle:
$$F(\mathbf{v}, \mathbf{h}) = F_0 + (1 - F_0) \left( 1 - (\mathbf{v} \cdot \mathbf{h}) \right)^5$$
- For dielectrics (plastics, glass, paper): $F_0 \approx 0.04$ (constant $4\%$ reflectance at normal incidence).
- For conductors (metals like gold, aluminum): $F_0 = \text{Albedo Color}$, and diffuse reflectance is $0$.

#### C. Geometric Shadowing-Masking Term $G(\mathbf{l}, \mathbf{v}, \mathbf{h})$: Smith Height-Correlated
Accounts for microfacets occluding each other:
$$G(\mathbf{l}, \mathbf{v}) = \frac{2 (\mathbf{n} \cdot \mathbf{l}) (\mathbf{n} \cdot \mathbf{v})}{(\mathbf{n} \cdot \mathbf{v}) \sqrt{\alpha^2 + (1 - \alpha^2)(\mathbf{n} \cdot \mathbf{l})^2} + (\mathbf{n} \cdot \mathbf{l}) \sqrt{\alpha^2 + (1 - \alpha^2)(\mathbf{n} \cdot \mathbf{v})^2}}$$

### 3.2. Law of Physical Energy Conservation
A surface cannot reflect more light energy than it receives:
$$k_d + k_s \le 1.0 \quad \text{where } k_s = F(\mathbf{v}, \mathbf{h})$$
$$k_d = (1 - k_s)(1 - \text{metallic})$$

*Aesthetic Rule for 2D UI & Slides:*
When an object is elevated or highlighted, never increase both its fill brightness and its border brightness simultaneously. Brightening both violates energy conservation, making elements appear radioactive or blown-out.

---

## 4. Lighting Ratios & Contact Shadows (SSAO Grounding)

### 4.1. The 3-Point Studio Lighting Model
High-end visual presentation applies cinematic studio lighting to 2D card surfaces and typography:
$$\begin{aligned}
\text{Key Light (Primary illuminator, top-left 45}^\circ\text{)} &: I_{\text{key}} = 1.00 \quad (T = 5500\text{K neutral}) \\
\text{Fill Light (Diffuses harsh shadows, right 60}^\circ\text{)} &: I_{\text{fill}} = 0.33 - 0.50 \quad (T = 6500\text{K cool sky}) \\
\text{Rim / Backlight (Separates subject from background)} &: I_{\text{rim}} = 0.50 - 0.75 \quad (T = 3200\text{K warm})
\end{aligned}$$
*Key-to-Fill Contrast Ratio:*
$$\text{Contrast Ratio} = \frac{I_{\text{key}} + I_{\text{fill}}}{I_{\text{fill}}} \approx 3:1 \text{ to } 4:1$$
This ratio provides crisp three-dimensional depth without obscuring shadow details.

### 4.2. SSAO (Screen-Space Ambient Occlusion) & Grounding
Floating elements without contact shadows look detached and fake. Ambient occlusion models how light cannot reach tight crevices and floor contact zones:
$$A_{\text{occlusion}} = 1.0 - \frac{1}{\pi} \int_{\Omega} V(\mathbf{p}, \omega) (\mathbf{n} \cdot \omega) \, d\omega$$

In PowerPoint DrawingML, SSAO is emulated using a two-tier shadow structure:
1. **Tier 1 (Contact Crevice):** Tight blur ($2\text{pt}$), low offset ($1.5\text{pt}$), medium opacity ($25\%$), simulating immediate surface occlusion.
2. **Tier 2 (Ambient Diffusion):** Wide blur ($16 - 24\text{pt}$), vertical offset ($6 - 8\text{pt}$), soft opacity ($8 - 12\%$), simulating diffused room bounce.

---

## 5. OpenXML DrawingML PBR Shadow Formulation

```xml
<p:sp>
  <p:nvSpPr>
    <p:cNvPr id="301" name="PBR Grounded Card"/>
    <p:cNvSpPr/>
    <p:nvPr/>
  </p:nvSpPr>
  <p:spPr>
    <a:xfrm>
      <a:off x="1828800" y="2743200"/>
      <a:ext cx="4572000" cy="2743200"/>
    </a:xfrm>
    <a:prstGeom prst="roundRect">
      <a:avLst><a:gd name="adj" fmla="val 8000"/></a:avLst>
    </a:prstGeom>
    <a:solidFill><a:srgbClr val="1E293B"/></a:solidFill>
    <!-- Single-layer PBR ambient contact shadow -->
    <a:effectLst>
      <a:outerShdw blurRad="203200" dist="63500" dir="5400000" algn="ctr"> <!-- 16pt blur, 5pt offset, 90 deg down -->
        <a:srgbClr val="000000">
          <a:alpha val="12000"/> <!-- 12% soft opacity -->
        </a:srgbClr>
      </a:outerShdw>
    </a:effectLst>
  </p:spPr>
</p:sp>
```

---

## 6. Comprehensive DOs and DON'Ts

### DO:
1. **Ground all floating cards with soft ambient shadows.** Set blur radius $\ge 16\text{pt}$ and opacity $\le 15\%$ to emulate diffused ambient light.
2. **Maintain a single global light direction.** All shadows and surface gradients across a deck must align with a single virtual light source (e.g. from top-left, angle $5,400,000$ in DrawingML).
3. **Use subtle normal gradients on cards.** Top edge of card: $L^* = 22\%$; bottom edge: $L^* = 18\%$. This $4\%$ delta simulates light falling across a planar microfacet surface.
4. **Reserve metallic sheens for focal data points.** Dielectrics have soft white specular highlights; metals take their specular color from the material's albedo.

### DON'T:
1. **Never use hard, opaque black drop shadows.** A shadow with `blurRad="0"` and `alpha="100000"` is a hallmark of amateur 1995 clip-art.
2. **Never apply bevel/emboss filters.** 3D extrusion and bevel filters in PowerPoint distort typographic antialiasing and produce jagged polygon seams.
3. **Never introduce conflicting light angles.** Card 1 casting a shadow to the right while Card 2 casts a shadow to the bottom-left destroys visual cohesion.
