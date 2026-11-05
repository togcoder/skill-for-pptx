# Universal PPTX Taste & Layout Engineering Rules (OOXML)

Synthesized from 9 cross-domain disciplines (Keynote, Vector, 3D, CAD, Motion, Swiss Typography, AI Web Skills, DataViz, Cinematography) and **rigorously stress-tested and calibrated with Argon**.
Formulated in accordance with **D010** (researched crowd taste, written in our own words) and **D011** (actionable design guidance with concrete physical formulas, exact OpenXML DrawingML tags, and zero vague hand-waving).

---

## The 17 Universal Taste & Layout Engineering Rules

| ID | Name | Domain Origin | Core Quantitative Invariant in OpenXML |
|---|---|---|---|
| **R01** | **Single Focal Velocity & Alpha Dimming** | Motion / Cinematography | Exactly 1 primary subject moves per beat; background elements dimmed to $15\%-30\%$ opacity via `<a:alpha val="15000"/>` to `25000` on fill, stroke, and text runs |
| **R02** | **Morph Shape Type Continuity** | CAD / Motion Canvas | Base geometry must remain identical: `roundRect` to `roundRect`. Circular state: $cx = cy$ in EMUs, `adj="50000"`. Card state: `adj="6000"`. Decouple text from morphing cards |
| **R03** | **Asymmetric Motion Timing & OOXML Easing** | Google M3 / Disney | Exit duration $= (0.60 - 0.70) \times \text{Entrance}$. OOXML timeline: Entrance `accel="10000" decel="80000"`; Exit `accel="70000" decel="10000"`. Morph duration `<p14:dur val="1000"/>` with `p159:morph` in `mc:AlternateContent` |
| **R04** | **Eye-Trace Settling Interval** | Film Editing / Baoyu | Minimum $0.6\text{s} - 1.0\text{s}$ visual stillness after a major cut/morph before secondary action triggers (`<p:cond delay="800"/>`) |
| **R05** | **Persistent Actor Identity Law** | `reveal.js` / PowerPoint | Persistent actor token `<p:cNvPr name="!!id"/>` across consecutive states; never drop IDs across slides |
| **R06** | **Base State Grounding at $t=0$** | Impeccable / Keynote | Initial state at $t=0$ must NEVER be blank; title/hero anchor must be readable before first click (0 Entrance effects on headers/containers) |
| **R07** | **12-Column Grid Snapping** | Swiss Style / Müller-Brockmann | Canvas $13.333"\times 7.500"$, 12 cols ($W_{\text{col}} \approx 0.7486" = 684,580\text{ EMU}$, $G = 0.25" = 228,600\text{ EMU}$, $M = 0.8" = 731,520\text{ EMU}$). All cards snap integer columns |
| **R08** | **Modular Typographic Scale & Column Measure** | Bringhurst / Modular Scale | Thang Perfect Fourth $r = 1.333$ ($14\text{pt}$, $18\text{pt}$ body, $24\text{pt}$ sub, $32-42\text{pt}$ title, $56-72\text{pt}$ hero). Column text width MUST satisfy $W_{\text{text}} \ge 18 \times \text{FontSize}$ ($35-65\text{ch}$ measure) |
| **R09** | **Proximity Over Containers** | Impeccable / Gestalt | $\text{Gap}_{\text{between groups}} \ge 3 \times \text{Gap}_{\text{within group}}$; eliminate container cards when whitespace proximity suffices |
| **R10** | **Single Elevation Discipline** | Impeccable / Shadcn | An element carries EITHER a 1px border OR soft ambient shadow (`blurRad="200000"`, `dist="50800"`, `dir="5400000"`, `algn="b"`, `rotWithShape="0"`, `alpha="10000"`). NEVER combine border + shadow ("ghost card") |
| **R11** | **Concentric Corner Radii in EMUs** | CAD / Apple Hardware | $\text{adj}_{\text{inner}} = \text{round}\left( \frac{R_{\text{outer\_EMU}} - \text{padding}_{\text{EMU}}}{\min(W_{\text{inner\_EMU}}, H_{\text{inner\_EMU}})} \times 100000 \right)$; eliminates pinched, distorted nested corners |
| **R12** | **Keyline Silhouette Balance** | Material Symbols / SF Symbols | Khung icon $0.4"\times 0.4"$ to $0.6"\times 0.6"$ ($365,760 - 548,640\text{ EMU}$), stroke đồng nhất $1.5-2.0\text{pt}$ (`w="19050"` đến `25400`), 0 emojis làm icon hệ thống |
| **R13** | **Proportional Ink & Zero Baseline** | Tufte / Wilke | Biểu đồ cột BẮT BUỘC bắt đầu từ $y=0$ (`<c:min val="0"/>`); dot plot cho trục phi zero; diện tích bubble $A \propto V$ ($r \propto \sqrt{V}$) |
| **R14** | **Subtle Gridlines & Direct Labeling** | Tufte / Financial Times | Gridlines desaturated to $\le 20\%$ opacity (`w="4762" sysDot`); nhãn gắn trực tiếp vào đuôi đường/cột; bỏ hộp chú giải legend rời |
| **R15** | **Rule of Thirds Power Framing** | Cinematography (ASC) | Hero subject placed at $(1/3, 1/3)$ or $(2/3, 1/3)$; counterbalanced by 2/3 negative space or editorial text |
| **R16** | **AABB Zero-Overlap & Safe Zone Collision Guard** | Argon / CAD Collision | Bounding boxes of text frames (`p:sp`) must NEVER intersect image/emblem bounding boxes. Safe margin $\ge 0.35"$ ($320,040\text{ EMU}$). Background watermarks require `alpha <= 15000` |
| **R17** | **Text-Fit Capacity & Word-Wrap Guard** | Argon / Typography | Width $W_{\text{text}} = cx - lIns - rIns \ge 18 \times \text{FontSize}$; total line count $\times \text{LineHeight} \le 0.85 \times cy$. Zero orphan lines (words at line end $\ge 2$) |

---

## Detailed Engineering Specifications & Formulas

### Rule R01: Single Focal Velocity & Alpha Dimming
- **Principle Statement:** Only one subject carries visual velocity per beat. Inactive and background elements must quiesce or dim.
- **OOXML Implementation:**
  PowerPoint DrawingML has no top-level CSS `opacity: 0.2` on `<p:sp>` or `<p:grpSp>`. Dimming requires explicit `<a:alpha val="20000"/>` (where $100\% = 100000$, so $20000 = 20\%$ opacity) inside:
  1. Shape background fill: `<a:solidFill><a:srgbClr val="..."><a:alpha val="20000"/></a:srgbClr></a:solidFill>`
  2. Shape border stroke: `<a:ln><a:solidFill><a:srgbClr val="..."><a:alpha val="20000"/></a:srgbClr></a:solidFill></a:ln>`
  3. Every paragraph text run: `<a:rPr><a:solidFill><a:srgbClr val="..."><a:alpha val="20000"/></a:srgbClr></a:solidFill></a:rPr>`
- **Anti-Pattern:** Setting a synthetic tag or expecting text to dim when only the card background was dimmed.

---

### Rule R02: Morph Shape Type Continuity
- **Principle Statement:** Shapes morph smoothly across slides ONLY when using identical underlying shape primitives.
- **Geometry & EMU Normalization:**
  - Base primitive: `<a:prstGeom prst="roundRect">`.
  - Circular state: Must have $cx == cy$ in EMUs (e.g. $cx = 914400, cy = 914400$ for $1.0"\times 1.0"$) and `<a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst>`.
  - Rectangular card state: $cx = 3657600, cy = 1828800$ ($4.0"\times 2.0"$) and `<a:avLst><a:gd name="adj" fmla="val 6000"/></a:avLst>` ($6\%$ corner radius).
  - **Decoupled Text Rule:** Do NOT place paragraphs directly inside a morphing card. Morph the background card (`!!card_bg`), and animate the text (`p:txBody` in a separate frame) to fade in *after* the card has settled, preventing font distortion during morphing!
- **Anti-Pattern:** Morphing `prst="ellipse"` into `prst="roundRect"`, or morphing text-heavy shapes where PowerPoint warps letter glyphs.

---

### Rule R03: Asymmetric Motion Timing & OOXML Easing
- **Principle Statement:** Digital physics requires fast exits ($60\%-70\%$ of enter duration) and natural deceleration.
- **OOXML DrawingML Mapping:**
  - PowerPoint `<p:cTn>` does not accept CSS bezier strings. It uses integer parts per $100,000$ (where $\text{accel} + \text{decel} \le 100000$):
    - **Decelerate Entrance (Ease-Out):** `<p:cTn dur="300" accel="10000" decel="80000">` ($80\%$ deceleration).
    - **Accelerate Exit (Ease-In):** `<p:cTn dur="200" accel="70000" decel="10000">` ($70\%$ acceleration).
  - **Slide Morph Transition & Namespaces:**
    Slide root tag `<p:sld>` MUST declare:
    `xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main"`
    `xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main"`
    `xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"`
    `mc:Ignorable="p14 p159"`
    Inside `<p:transition spd="med" advClick="1">`:
    ```xml
    <mc:AlternateContent>
      <mc:Choice Requires="p159">
        <p159:morph option="byObject"/>
      </mc:Choice>
      <mc:Fallback>
        <p:fade/>
      </mc:Fallback>
    </mc:AlternateContent>
    ```
- **Anti-Pattern:** Omitting namespaces causing PowerPoint "Repair File" warnings, or using symmetric linear animations (`accel="0" decel="0"`).

---

### Rule R07: 12-Column Grid Snapping
- **Canvas Constants:**
  - Slide Width: $13.333" = 12,192,000\text{ EMU}$
  - Slide Height: $7.500" = 6,858,000\text{ EMU}$
  - Left / Right Margin: $M = 0.800" = 731,520\text{ EMU}$
  - Gutter: $G = 0.250" = 228,600\text{ EMU}$
  - Column Width: $W_{\text{col}} = \frac{12,192,000 - 2(731,520) - 11(228,600)}{12} = 684,580\text{ EMU} \approx 0.7486"$
- **Card Placement Formula:**
  For a card starting at column index $i \in [0, 11]$ spanning $S$ columns:
  $$x = M + i \times (W_{\text{col}} + G)$$
  $$w = S \times W_{\text{col}} + (S - 1) \times G$$
  - **Standard 2-Column Split (Span 6 + 6):**
    - Col 0-5 (Left): $x = 0.800"$, $w = 6(0.7486) + 5(0.25) = 5.7416" \approx 5.74"$ ($5,248,800\text{ EMU}$).
    - Col 6-11 (Right): $x = 0.800 + 6(0.7486) + 6(0.25) = 6.7916" \approx 6.79"$ ($6,208,980\text{ EMU}$), $w = 5.74"$.
    - Gap between columns is exactly $G = 0.25"$ ($228,600\text{ EMU}$).
- **Anti-Pattern:** Unsnapped cards with arbitrary widths ($3.47"$) or arbitrary gaps ($1.7"$) creating giant voids in the center.

---

### Rule R08 & R17: Column Measure, Text-Fit & Word-Wrap Guard
- **The Physical Problem:** If a column is too narrow (e.g. 3 columns with $w = 3.1"$), an 18pt font only fits 20-25 characters per line, causing ugly 2-word line wraps.
- **Quantitative Bounds:**
  - Effective Text Width: $W_{\text{text}} = w - lIns - rIns$.
  - Character Capacity:
    $$\text{Capacity} \approx \frac{W_{\text{text}}}{\text{FontSize}_{\text{pt}} \times 0.007"}$$
  - **The 35-Character Floor:** For body text paragraphs, $W_{\text{text}}$ MUST accommodate at least $35$ characters per line:
    $$W_{\text{text}} \ge 35 \times (\text{FontSize}_{\text{pt}} \times 0.007") \approx 0.245" \times \text{FontSize}_{\text{pt}}$$
    - For $18\text{pt}$ text: $W_{\text{text}} \ge 4.41"$ ($4,032,500\text{ EMU}$).
    - For 2-column layout ($w = 5.74"$ with $0.3"$ padding $\implies W_{\text{text}} = 5.14"$), an 18pt font holds $\approx 48-52$ characters per line (optimal measure!).
  - **Vertical Capacity:**
    $$\text{Total Lines} \times (\text{FontSize} \times \text{LineHeight}) \le 0.85 \times (h - tIns - bIns)$$
- **Anti-Pattern:** Cramming 18pt text into 3-inch columns, producing disjointed lines with 2 words per line.

---

### Rule R10: Single Elevation Discipline & Soft Ambient Shadows
- **Principle Statement:** Choose EITHER a clean 1px border OR a soft diffused ambient shadow; NEVER combine border + shadow.
- **Exact OOXML DrawingML Shadow Parameters:**
  ```xml
  <a:effectLst>
    <a:outerShdw blurRad="200000" dist="50800" dir="5400000" algn="b" rotWithShape="0">
      <a:srgbClr val="000000">
        <a:alpha val="10000"/> <!-- Exactly 10% opacity: subtle, diffused -->
      </a:srgbClr>
    </a:outerShdw>
  </a:effectLst>
  ```
  - `blurRad="200000"`: $15.75\text{pt}$ blur radius (diffused penumbra).
  - `dist="50800"`: $4\text{pt}$ vertical distance.
  - `dir="5400000"`: $90^\circ$ downward light angle.
  - `algn="b" rotWithShape="0"`: Bottom alignment, unrotated with shape.
  - `alpha val="10000"`: $10\%$ opacity (eliminates harsh dirty black spots).
- **Anti-Pattern:** Default PowerPoint shadow (`dist="25400" blurRad="38100"` at $50\%$ opacity), which looks like dirty charcoal smeared under the card.

---

### Rule R11: Concentric Corner Radii in EMUs
- **The Physical Law:** To prevent optical corner pinching, nested inner cards must have their radius reduced by the intervening padding distance.
- **Exact OOXML Formula:**
  Since PowerPoint's `adj` is a fraction of $100,000$ relative to $\min(w, h)$:
  $$R_{\text{outer\_EMU}} = \frac{\text{adj}_{\text{outer}}}{100000} \times \min(w_{\text{outer}}, h_{\text{outer}})$$
  $$R_{\text{inner\_target}} = \max(0, \; R_{\text{outer\_EMU}} - \text{padding}_{\text{EMU}})$$
  $$\mathbf{\text{adj}_{\text{inner}} = \text{round}\left( \frac{R_{\text{inner\_target}}}{\min(w_{\text{inner}}, h_{\text{inner}})} \times 100000 \right)}$$
- **Anti-Pattern:** Copy-pasting `adj="8000"` onto both the outer container and the inner nested badge, producing mismatched, bulging curves.

---

### Rule R16: AABB Zero-Overlap & Safe Zone Collision Guard
- **The Physical Problem:** Text headers colliding with emblem rings (as seen in Slide 2) occurs when bounding boxes overlap without spatial awareness.
- **Collision Invariant:**
  For any text shape $T$ and visual emblem / picture shape $P$:
  Let $AABB(S) = [x_{\min}, y_{\min}, x_{\max}, y_{\max}]$.
  $$\mathbf{AABB}(T) \cap \mathbf{AABB}(P) = \emptyset$$
  - Safe Clearance Margin:
    $$\Delta x = x_{\min}(T) - x_{\max}(P) \ge 0.35" \quad (320,040\text{ EMU})$$
  - **Exception for Watermarks:** If $P$ is an atmospheric background watermark, its opacity MUST be set to `<a:alpha val="12000"/>` ($\le 12\%$) and text contrast against the watermark background must satisfy WCAG AAA $\ge 7:1$.
- **Anti-Pattern:** Placing a text box starting at $x=0.8"$ directly over an emblem whose right boundary extends to $x=1.7"$.
