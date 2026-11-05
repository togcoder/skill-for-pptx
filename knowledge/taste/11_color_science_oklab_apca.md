# Domain 11: Color Science, Perceptual Uniformity (Oklab/OKLCH) & Modern Contrast (APCA)

## 1. Overview & Cultural Authority
Color taste in modern high-performance design systems (Apple HIG, Google Material 3, CSS Color Module Level 4/5, Andrew Somers' APCA, and Björn Ottosson's Oklab) has abandoned traditional sRGB/HSL and legacy WCAG 2.x contrast ratios.

The core scientific truth: **Human color vision is profoundly non-linear, asymmetric, and polarity-dependent.** Relying on 1990s color models (like HSL or WCAG 2.1) leads to muddy gradient transitions, unreadable dark-mode text, and glaringly mismatched perceptual brightness across different hues.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Architecture & Math | Core Invariant Extracted |
|---|---|---|
| [`Myndex/SAPC-APCA`](https://github.com/Myndex/SAPC-APCA) | Andrew Somers' Accessible Perceptual Contrast Algorithm (W3C Silver candidate, APCA-W3 0.0.98G-4g) | Polarity-dependent power law contrast; spatial frequency integration; soft black clamp toe adjustment; eliminates WCAG 2 false passes/fails. |
| [`bottosson/bottosson.github.io`](https://github.com/bottosson/bottosson.github.io) | Björn Ottosson's original Oklab specification and code | Linear sRGB $\to$ LMS cone response $\to$ cube-root compression $\to$ Lab matrix; uniform chroma and hue linearity. |
| [`LeaVerou/culori`](https://github.com/LeaVerou/culori) | Comprehensive JavaScript color science library | Exact matrix transformations across CIELAB, Oklab, Oklch, Display-P3, and Rec.2020. |

---

## 3. Mathematical Foundations: The Oklab Color Space (Björn Ottosson, 2020)

### 3.1. Why sRGB and HSL Fail Perceptually
In HSL, pure Yellow (`#FFFF00`) and pure Blue (`#0000FF`) both have $L = 50\%$.
However, the human eye has vastly different spectral sensitivities across cone types (L, M, S):
$$\begin{aligned}
Y_{\text{yellow}} &= 0.2126(1) + 0.7152(1) + 0.0722(0) = 0.9278 \quad (\text{Perceived as blazing bright}) \\
Y_{\text{blue}} &= 0.2126(0) + 0.7152(0) + 0.0722(1) = 0.0722 \quad (\text{Perceived as deep dark})
\end{aligned}$$
Interpolating between Blue and Yellow in HSL passes through a dirty, desaturated olive-grey zone ("the dead zone"). Oklab solves this by enforcing **true perceptual uniformity**.

---

### 3.2. Forward Transformation: Linear sRGB $\to$ Oklab

#### Step A: Linear sRGB to Long-Medium-Short (LMS) Cone Response Matrix
$$\begin{bmatrix} l \\ m \\ s \end{bmatrix} = \begin{bmatrix} 
0.4121656120 & 0.5362752080 & 0.0514575653 \\ 
0.2118591070 & 0.6807189584 & 0.1074065790 \\ 
0.0883097947 & 0.2818474174 & 0.6302613616 
\end{bmatrix} \begin{bmatrix} R_{\text{lin}} \\ G_{\text{lin}} \\ B_{\text{lin}} \end{bmatrix}$$

#### Step B: Non-Linear Biological Compression (Cube Root)
Simulates human cone signal compression before transmission through the optic nerve:
$$l' = \sqrt[3]{l}, \quad m' = \sqrt[3]{m}, \quad s' = \sqrt[3]{s}$$

#### Step C: LMS' to Oklab Matrix
$$\begin{bmatrix} L \\ a \\ b \end{bmatrix} = \begin{bmatrix} 
0.2104542553 & 0.7936177850 & -0.0040720468 \\ 
1.9779984951 & -2.4285922050 & 0.4505937099 \\ 
0.0259040371 & 0.7827717662 & -0.8086757660 
\end{bmatrix} \begin{bmatrix} l' \\ m' \\ s' \end{bmatrix}$$

#### Cylindrical OKLCH Representation
$$C = \sqrt{a^2 + b^2} \quad (\text{Chroma / Saturation})$$
$$h = \text{atan2}(b, a) \quad (\text{Hue Angle in radians / degrees})$$

---

### 3.3. OpenXML Rendering Pitfalls & Engineering Solutions

#### A. Gamut Mapping via Binary Search Chroma Reduction
OKLCH gamut is significantly wider than sRGB. Direct conversion of high-chroma colors yields invalid $R, G, B \notin [0, 1]$.
*Solution:* To convert $(L, C, h) \to \text{sRGB}$, hold $L$ and $h$ fixed, and binary-search $C \in [0, C]$ until all linear RGB channels lie within $[0.0, 1.0]$. Never clamp RGB channels individually with `min/max`, as this shifts hue and lightness.

#### B. The PowerPoint Gradient Interpolation Trap (`<a:gradFill>`)
PowerPoint internally interpolates gradient stops in gamma-encoded sRGB (`<a:lin>`). If only 2 endpoints are defined, the midpoint will still fall into a muddy grey-brown zone.
*Solution:* To achieve true Oklab gradient blending in PowerPoint, **bake at least 5 stops** (`pos="0"`, `25000`, `50000`, `75000`, `100000`) calculated via Oklab space into the DrawingML XML:
```xml
<a:gradFill>
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="0284C7"/></a:gs>
    <a:gs pos="25000"><a:srgbClr val="06B6D4"/></a:gs>
    <a:gs pos="50000"><a:srgbClr val="10B981"/></a:gs>
    <a:gs pos="75000"><a:srgbClr val="84CC16"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="EAB308"/></a:gs>
  </a:gsLst>
  <a:lin ang="5400000"/>
</a:gradFill>
```

#### C. Helmholtz-Kohlrausch Effect Across Peer Cards
Colors with high chroma appear perceptually brighter than neutral colors of identical lightness $L$. Across horizontal comparison cards (Span 4 or Span 3), maintain $\Delta C \le 0.04$ so that no card appears unintentionally dominant.

---

## 4. APCA: Advanced Perceptual Contrast Algorithm (Andrew Somers / W3C Silver)

### 4.1. The Fatal Flaws of Legacy WCAG 2.x
The legacy WCAG 2 formula $(L_1 + 0.05) / (L_2 + 0.05)$:
1. **Ignores polarity:** It assumes dark text on white is visually identical to white text on dark. In reality, light text on dark background undergoes **optical irradiation** (light blooming into adjacent retinal cones), making thin fonts appear thinner.
2. **Fails in dark mode:** WCAG 2 passes low-contrast dark greys that are physically illegible to human eyes while failing perfectly readable high-contrast combinations.

---

### 4.2. The APCA Mathematical Model (APCA-W3 0.0.98G-4g Specification)

#### Step 1: Linearize sRGB Channels
$$R_{\text{lin}} = \left(\frac{R}{255}\right)^{2.4}, \quad G_{\text{lin}} = \left(\frac{G}{255}\right)^{2.4}, \quad B_{\text{lin}} = \left(\frac{B}{255}\right)^{2.4}$$
$$Y = 0.2126729 \cdot R_{\text{lin}} + 0.7151522 \cdot G_{\text{lin}} + 0.0721750 \cdot B_{\text{lin}}$$

#### Step 2: Soft Black Clamp (Toe Adjustment for Ambient Flare)
$$Y' = \begin{cases} 
Y + (0.022 - Y)^{1.414} & \text{if } Y < 0.022 \\ 
Y & \text{if } Y \ge 0.022 
\end{cases}$$

#### Step 3: Polarity-Aware Power-Law Scaling
$$\begin{aligned}
\text{Case A: Normal Polarity (Dark text on Light bg, } Y'_{\text{bg}} > Y'_{\text{txt}}\text{):} \\
L_c = \left( (Y'_{\text{bg}})^{0.56} - (Y'_{\text{txt}})^{0.57} \right) \times 1.14 \times 100 \\
\\
\text{Case B: Reverse Polarity (Light text on Dark bg, } Y'_{\text{txt}} > Y'_{\text{bg}}\text{):} \\
L_c = \left( (Y'_{\text{bg}})^{0.65} - (Y'_{\text{txt}})^{0.62} \right) \times 1.14 \times 100
\end{aligned}$$

*Note:* In Reverse Polarity, $L_c$ produces a negative value ($-L_c$), indicating light text on a dark background.

---

### 4.3. APCA Compliance Thresholds for Presentations

| Polarity | Context | Minimum Metric | Target Font |
|---|---|:---:|---|
| **Normal ($L_c > 0$)** | Primary Body Text | **$L_c \ge +75.0$** | $16\text{pt} - 18\text{pt}$ Regular |
| **Normal ($L_c > 0$)** | Subtitles / Captions | **$L_c \ge +60.0$** | $14\text{pt}$ Regular |
| **Normal ($L_c > 0$)** | Large Headlines | **$L_c \ge +45.0$** | $\ge 32\text{pt}$ Bold |
| **Reverse ($L_c < 0$)** | **Dark Mode Body Text** | **$\vert L_c \vert \ge 80.0$** | $16\text{pt} - 18\text{pt}$ Regular (or $\ge 75$ with Medium weight) |
| **Reverse ($L_c < 0$)** | Dark Mode Titles | **$\vert L_c \vert \ge 65.0$** | $\ge 32\text{pt}$ SemiBold |
| **Any Polarity** | Non-Text Borders | $\vert L_c \vert \ge 45.0$ | Structural lines |
| **Any Polarity** | **Illegible Defect** | $\vert L_c \vert < 45.0$ | **BANNED on all presentation slides** |

---

## 5. Python Production APCA & OKLCH Gamut Mapping Engine

```python
"""
Production APCA & OKLCH Color Engine
Implements APCA-W3 0.0.98G-4g with Soft Black Clamp and OKLCH Binary-Search Gamut Mapping.
"""
import math

def srgb_to_y(r, g, b):
    r_lin = (r / 255.0) ** 2.4
    g_lin = (g / 255.0) ** 2.4
    b_lin = (b / 255.0) ** 2.4
    y = 0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin
    # Soft black clamp
    if y < 0.022:
        y += (0.022 - y) ** 1.414
    return y

def calc_apca_lc(hex_txt, hex_bg):
    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    txt_rgb = hex_to_rgb(hex_txt)
    bg_rgb = hex_to_rgb(hex_bg)
    
    y_txt = srgb_to_y(*txt_rgb)
    y_bg = srgb_to_y(*bg_rgb)
    
    # APCA-W3 0.0.98G-4g
    if y_bg > y_txt:
        # Normal Polarity (Dark on Light)
        lc = (math.pow(y_bg, 0.56) - math.pow(y_txt, 0.57)) * 1.14 * 100.0
    else:
        # Reverse Polarity (Light on Dark): Exponents 0.65 and 0.62
        lc = (math.pow(y_bg, 0.65) - math.pow(y_txt, 0.62)) * 1.14 * 100.0
        
    return round(lc, 1)

def oklch_to_srgb_hex(L, C, H_deg):
    """
    Converts OKLCH to sRGB Hex with Binary Search Gamut Mapping.
    Guarantees in-gamut sRGB without shifting Lightness or Hue.
    """
    H_rad = math.radians(H_deg)
    
    def in_gamut(c_val):
        a = c_val * math.cos(H_rad)
        b = c_val * math.sin(H_rad)
        
        # Oklab to LMS
        l_ = L + 0.3963377774 * a + 0.2158037573 * b
        m_ = L - 0.1055613458 * a - 0.0638541728 * b
        s_ = L - 0.0894841775 * a - 1.2914855480 * b
        
        l = l_ ** 3
        m = m_ ** 3
        s = s_ ** 3
        
        # LMS to Linear sRGB
        r_lin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
        g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
        b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
        
        return (0.0 <= r_lin <= 1.0) and (0.0 <= g_lin <= 1.0) and (0.0 <= b_lin <= 1.0), (r_lin, g_lin, b_lin)
    
    # Binary search Chroma reduction
    low = 0.0
    high = C
    best_rgb = (0, 0, 0)
    
    for _ in range(20):
        mid = (low + high) / 2.0
        valid, rgb_lin = in_gamut(mid)
        if valid:
            best_rgb = rgb_lin
            low = mid
        else:
            high = mid
            
    # Linear to Gamma sRGB
    def gamma(v):
        v = max(0.0, min(1.0, v))
        return 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1.0 / 2.4)) - 0.055
        
    r_byte = int(round(gamma(best_rgb[0]) * 255))
    g_byte = int(round(gamma(best_rgb[1]) * 255))
    b_byte = int(round(gamma(best_rgb[2]) * 255))
    
    return f"{r_byte:02X}{g_byte:02X}{b_byte:02X}"
```

---

## 6. Comprehensive DOs and DON'Ts

### DO:
1. **Target $\vert L_c \vert \ge 80$ for white/light text on dark presentation slides.** Compensate for optical irradiation thinning.
2. **Apply binary search gamut mapping when converting OKLCH to Hex.** Maintain perceptual lightness $L$ and hue $h$ without clipping artifacts.
3. **Bake at least 5 intermediate stops into `<a:gradFill>`.** Bypass PowerPoint's muddy sRGB gamma gradient engine.

### DON'T:
1. **Never rely on legacy WCAG 2 ratios alone.** A 4.5:1 ratio can easily be illegible in dark themes.
2. **Never allow $\Delta C > 0.04$ between peer cards of identical lightness.** Saturated colors appear artificially brighter due to the Helmholtz-Kohlrausch effect.
3. **Never allow $\vert L_c \vert < 45$ on any text.**
