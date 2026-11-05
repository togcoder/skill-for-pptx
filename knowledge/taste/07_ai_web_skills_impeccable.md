# Domain 7: Web AI Design Skills, Modern Frontend & Anti-Slop Craftsmanship

## 1. Overview & Cultural Authority
Modern digital interface taste (`pbakaus/impeccable`, `anthropics/skills` `frontend-design`, `bergside/awesome-design-skills`, `shadcn/ui`, and Linear/Stripe design systems) has established a fierce counter-reaction against **"AI Slop"**.

"AI Slop" is the generic, unopinionated visual noise produced by AI models that have ingested millions of mediocre SaaS templates: purple-to-cyan gradient borders, floating glossy 3D spheres, centered generic hero copy, neon pill kickers, and nested rectangular card grids with no clear visual hierarchy. Professional craftsmanship enforces an uncompromising aesthetic floor.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Focus & Ethos | Core Invariant Extracted |
|---|---|---|
| [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) | Philosophy and strict craft floor for AI-generated design | The Squint Test; "Design begins with subtraction"; ban on ornamental AI tells; intentional whitespace. |
| [`anthropics/skills` (frontend-design)](https://github.com/anthropics/skills) | Anthropic's official frontend design skill | Rejection of generic SaaS templates; purposeful typography; layout variation; high-contrast minimalism. |
| [`shadcn/ui`](https://github.com/shadcn-ui/ui) | Radix UI + Tailwind design system standard | Strict semantic token layering (background, foreground, muted, accent, card, border); radical simplicity. |
| [`tailwindlabs/tailwindcss`](https://github.com/tailwindlabs/tailwindcss) | Utility-first CSS framework | Numeric spatial spacing scale (powers of 4px/8px); predictable layout math. |

---

## 3. Mathematical Foundations: Spatial Gestalt & The Squint Test

### 3.1. The Squint Test (Gaussian Blur Spatial Low-Pass Filter)
Apply a 2D Gaussian blur filter to the slide layout with standard deviation $\sigma = 12\text{px}$:
$$I_{\text{blurred}}(x, y) = I(x, y) * G_\sigma(x, y) \quad \text{where } G_\sigma(x, y) = \frac{1}{2\pi \sigma^2} e^{-\frac{x^2 + y^2}{2\sigma^2}}$$

*The Gestalt Invariant:*
When fine text and sharp borders are blurred away, the slide must resolve into **exactly 3 distinct luminous masses**:
1. **Primary Mass ($40 - 50\%$ luminance):** The focal hero headline, primary KPI, or core architectural flow.
2. **Secondary Mass ($20 - 30\%$ luminance):** The 2-3 supporting context cards or comparative data nodes.
3. **Background Ground ($0 - 10\%$ luminance):** The ambient void.

If the blurred image looks like a uniform grey soup or a speckled array of 8 identical boxes, the layout has failed the Squint Test.

---

### 3.2. Proximity Over Containers (Gestalt Law of Grouping)
Amateur AI designs enclose every related pair of text elements inside a card with a border and a background fill. This creates visual clutter through unnecessary structural lines.

*The Mathematical Proximity Ratio:*
$$\frac{D_{\text{between\_groups}}}{D_{\text{within\_group}}} \ge 2.5$$
Where:
- $D_{\text{within\_group}}$ is the distance between a title and its descriptive body paragraph ($8\text{pt} - 12\text{pt}$).
- $D_{\text{between\_groups}}$ is the whitespace separating distinct thematic sections ($28\text{pt} - 40\text{pt}$).

By enforcing a $2.5\times$ distance ratio, the human visual system groups related elements automatically through negative space, making bounding boxes, outlines, and tinted backgrounds redundant.

---

### 3.3. The Single Elevation Law
A UI shape may communicate elevation and layer hierarchy through **one mechanism only**:
$$\text{Elevation Representation} \in \{ \text{Border}, \text{Drop Shadow}, \text{Background Tint} \} \quad (\text{Select Exactly One})$$

- **Pattern A (Flat / Architectural):** Background tint `#1E293B`, $0\text{pt}$ border, $0\text{pt}$ shadow.
- **Pattern B (Outlined / Minimalist):** Background transparent, $1\text{pt}$ subtle border `#334155`, $0\text{pt}$ shadow.
- **Pattern C (Elevated / Tactile):** Background `#1E293B`, $0\text{pt}$ border, soft $16\text{pt}$ ambient shadow.

*The AI Tell Defect (Slide 3 Analysis):*
The defective card in Slide 3 had a bright cyan border, a solid blue background, and an opaque black shadow simultaneously. This "triple elevation" looks cheap and unnatural.

---

## 4. The 8 Banned AI Tell Signatures

Any slide containing one of these signatures is immediately flagged as amateur AI-generated:

1. **The Ghost Card:** A card with a dark background, a glowing $1\text{pt}$ bright border, and an aggressive drop shadow.
2. **The Generic Kicker:** Uppercase micro-labels like `// REVOLUTIONIZING THE FUTURE` or `/// EMPOWERING NEXT-GEN`.
3. **The Unanchored Pill Badge:** Random floating capsules with icons and text scattered without grid alignment.
4. **The Neon Glow Overdose:** Cyan `#00FFFF` and Magenta `#FF00FF` drop shadows placed on non-focal text.
5. **The Cliché Metric Triptych:** Exactly 3 identical cards with arbitrary percentages ($+40\%$, $+25\%$, $+85\%$) that carry no authentic enterprise meaning.
6. **The Centered Bullet Block:** Large cards containing center-aligned bullet points with checkmark emojis.
7. **The Rainbow Gradient Text:** Hero headlines masked with 4-stop linear gradients across contrasting hues.
8. **The Decorative Floating Sphere:** Unconnected 3D orbs and geometric shapes floating in slide corners to fill whitespace.

---

## 5. Python Squint Test & Elevation Auditor

```python
"""
Anti-Slop & Single Elevation Auditor for PPTX Shapes
Ensures cards do not violate the Single Elevation Law and bans AI tell gradients.
"""
def audit_shape_anti_slop(shape_element):
    has_border = False
    has_shadow = False
    has_fill = False
    has_glow = False
    
    spPr = shape_element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}spPr')
    if spPr is None:
        return {"passed": True}
        
    # Check border
    ln = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ln')
    if ln is not None and ln.find('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill') is not None:
        has_border = True
        
    # Check fill
    solidFill = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
    if solidFill is not None:
        has_fill = True
        
    # Check shadow & glow in effectLst
    effectLst = spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst')
    if effectLst is not None:
        if effectLst.find('{http://schemas.openxmlformats.org/drawingml/2006/main}outerShdw') is not None:
            has_shadow = True
        if effectLst.find('{http://schemas.openxmlformats.org/drawingml/2006/main}glow') is not None:
            has_glow = True
            
    violations = []
    if has_border and has_shadow:
        violations.append("DUAL_ELEVATION_DETECTED: Shape has both a solid border AND a drop shadow.")
    if has_glow:
        violations.append("BANNED_AI_TELL: Neon glow effect detected on shape.")
        
    return {
        "passed": len(violations) == 0,
        "violations": violations
    }
```

---

## 6. Comprehensive DOs and DON'Ts

### DO:
1. **Embrace negative space.** If a slide feels sparse after placing the core insight, resist the urge to add decorative containers. Let the emptiness emphasize the message.
2. **Follow the Single Elevation Law.** Choose border OR shadow; never combine both on the same card.
3. **Use whitespace for grouping before adding card containers.** A $32\text{pt}$ margin separates topics more cleanly than a tinted box.
4. **Use authentic enterprise nomenclature.** Replace marketing hype with concrete technical metrics (e.g. `p99 Latency: 14ms`, `Gross Margin: 74.2%`).

### DON'T:
1. **Never use neon glow filters on corporate presentations.** Glowing text belongs in arcade games, not boardrooms.
2. **Never wrap every text element in a card.** When everything is inside a card, nothing stands out.
3. **Never apply multi-color gradients across text headlines.** Keep text solid and readable.
