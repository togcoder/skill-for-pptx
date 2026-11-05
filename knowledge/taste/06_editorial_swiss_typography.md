# Domain 6: Swiss Style, Typography & Editorial Layout

## 1. Overview & Cultural Authority
The International Typographic Style (Swiss Style), pioneered in Zurich and Basel in the 1950s by Josef Müller-Brockmann, Armin Hofmann, and Emil Ruder, established that graphic design should be objective, mathematically ordered, and free from superficial decoration. Paired with Robert Bringhurst’s *The Elements of Typographic Style* and Matthew Butterick’s *Practical Typography*, Swiss design provides the ultimate architectural foundation for information legibility.

In slide design, Swiss style transforms chaotic bulleted slides into clean, authoritative, publication-grade editorial layouts.

## 2. Core Principles & Formulas

### 2.1. The 12-Column Modular Grid
A standard $16:9$ canvas ($13.333"\times 7.500"$) is divided into 12 vertical columns separated by uniform gutters:
- **Number of columns:** $N = 12$
- **Outer margins:** Left and right margins $M = 0.80"$ ($731,520$ EMUs)
- **Gutter width:** $G = 0.25"$ ($228,600$ EMUs)
- **Column width formula:**
  $$W_{\text{col}} = \frac{W_{\text{total}} - 2M - (N - 1)G}{N} = \frac{13.333 - 1.60 - 11(0.25)}{12} = \frac{8.983}{12} \approx 0.748"$$
- **Spans:**
  - 1-Column layout (Full-width hero): Spans 12 columns.
  - 2-Column layout (Split screen / Comparison): Two blocks, each spanning 6 columns (or asymmetric $4 + 8$ columns).
  - 3-Column layout (Triad / Pillars): Three blocks, each spanning 4 columns.
  - 4-Column layout (Metrics row): Four blocks, each spanning 3 columns.
All elements snap strictly to these column bounds; no arbitrary free-floating text boxes!

### 2.2. Modular Typographic Scale Ratios
Font sizes must not be chosen at random (e.g. 15, 17, 23, 31). They must follow a strict geometric progression from a chosen base body size ($S_0 = 18\text{pt}$ for presentations):
$$S_n = S_0 \times r^n$$

```
Ratio Choice:
├── 1.250 (Major Third): Dense multi-tier technical slides (18pt, 22.5pt, 28pt, 35pt, 44pt)
├── 1.333 (Perfect Fourth): Standard executive and editorial pitch decks (18pt, 24pt, 32pt, 42.6pt, 56.8pt)
└── 1.618 (Golden Ratio): High-impact keynote hero statements (18pt, 29pt, 47pt, 76pt, 123pt)
```

**Recommended Presentation Scale (Perfect Fourth, $r = 1.333$):**
- Step -1 (Caption / Meta): $13.5\text{pt} \approx 14\text{pt}$
- Step 0 (Body Text): $18\text{pt}$ (The readable baseline)
- Step 1 (Subheading / Card Title): $24\text{pt}$
- Step 2 (Section Title): $32\text{pt}$
- Step 3 (Slide Main Title): $42\text{pt}$
- Step 4 (Hero Statistic / Key Metric): $56\text{pt} - 72\text{pt}$

### 2.3. Measure (Line Length) & Line Height (Leading)
- **Optimal Line Length (Measure):**
  $$\text{Line Length} \in [45, \; 75] \text{ characters per line (ideal 60-65ch)}$$
  If a text column exceeds 80 characters, the reader's eye loses tracking when returning to the next line. If a column is $< 35$ characters, words break awkwardly and hyphenate.
- **Line Height Ratio ($LH / S$):**
  - **Display / Hero Titles ($\ge 32\text{pt}$):** Tight leading: $1.10\times - 1.20\times$ font size. (Large headers look fractured if lines drift apart).
  - **Body Copy ($18\text{pt} - 24\text{pt}$):** Comfortable leading: $1.35\times - 1.50\times$ font size.

### 2.4. Tracking (Letter-Spacing) Calibration
- Display type ($\ge 36\text{pt}$): Apply slightly negative tracking ($-0.02\text{em}$ to $-0.03\text{em}$, or $-20\text{pt}/1000$) to hold large letters together as cohesive words.
- All-caps labels (used with extreme restraint): Apply positive tracking ($+0.05\text{em}$ to $+0.10\text{em}$) to maintain legibility.
- Body text: Leave tracking at zero ($0.0\text{em}$). Never track out lowercase body text.

### 2.5. Font Pairing Rules
Never pair fonts arbitrarily:
1. **The Maximum-2-Families Rule:** A presentation uses at most 2 font families (or 1 versatile superfamily).
2. **High-Contrast Classification:** Pair a distinctive modern Serif with a clean geometric Sans-Serif:
   - *Example:* Palatino Linotype (Serif Headline) + Segoe UI (Clean Sans Body).
   - *Example:* Fraunces / Instrument Serif (Display) + Geist / Inter (Body).
3. **The Ban on Similar Faces:** Never pair two different fonts from the same family classification (e.g. Arial + Helvetica, or Georgia + Times New Roman). They look like an accidental formatting error.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Alignment** | Strong left alignment anchored to grid columns; ragged-right text | Justified text on narrow columns creating rivers of white space |
| **Hierarchy** | Hierarchy driven by scale step and weight contrast (Bold $700$ vs Regular $400$) | Using 6 different colors and underlines to create emphasis |
| **Line Breaks** | Break headings manually between grammatical phrases; keep lone last words ("orphans") down | Leaving a single word on the final line of a header |
| **Grid Adherence** | Snap cards, text boxes, and images to consistent 12-column intervals | Freehand eyeballing of element positions across slides |
| **Numbers** | Use tabular figures / monospace numerals for data comparison columns | Proportional figures where number columns wobble out of alignment |

## 4. Translation to PowerPoint (OOXML)
- In PPTX, line spacing is set via `<a:lnSpc><a:spcPct val="135000"/></a:lnSpc>` ($135\%$ line height).
- Margin padding inside text frames:
  ```xml
  <p:spPr>
    <a:xfrm .../>
    <a:prstGeom prst="rect"/>
  </p:spPr>
  <p:txBody>
    <a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0"/>
  </p:txBody>
  ```
  Setting text insets (`lIns`, `tIns`, `rIns`, `bIns`) explicitly to $0$ ensures text lines snap directly to the 12-column grid without invisible internal offsets!
