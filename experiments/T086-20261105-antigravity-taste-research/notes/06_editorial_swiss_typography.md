# Domain 6: Editorial & Swiss Typography (International Typographic Style)

## 1. Overview & Cultural Authority
Swiss typography (Josef Müller-Brockmann's *Grid Systems*, Robert Bringhurst's *The Elements of Typographic Style*, Emil Ruder, and Matthew Butterick's *Practical Typography*) provides the mathematical foundation of clear human communication.

In executive presentations, typography is not decorative styling; it is **information architecture**. A slide with broken line measure, colliding text boxes, or mismatched leading instantly degrades credibility, regardless of how good the underlying technology or business model is.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Focus & Implementation | Core Invariant Extracted |
|---|---|---|
| [`harfbuzz/harfbuzz`](https://github.com/harfbuzz/harfbuzz) | Open-source text shaping engine used in browsers and OSs | OpenType feature resolution; optical kerning; glyph cluster positioning; complex script ligation. |
| [`bramstein/typeset`](https://github.com/bramstein/typeset) | JavaScript implementation of Knuth-Plass line breaking | Dynamic programming box-glue-penalty solver; hyphenation penalty matrices; demerit minimization. |
| [`system-fonts/modern-font-stacks`](https://github.com/system-fonts/modern-font-stacks) | Zero-network pure system typography stacks | High-performance native fallback matrices across macOS, Windows, Linux, and iOS. |
| [`edwardtufte/tufte-css`](https://github.com/edwardtufte/tufte-css) | CSS implementation of Edward Tufte's publishing aesthetic | Sidenotes, margin figures, strict column measure ($60\text{ch}$), tight baseline grids. |

---

## 3. Mathematical Foundations: Grid & Layout Geometry

### 3.1. The 12-Column Modular Grid System
A $16:9$ canvas ($13.333'' \times 7.500''$ in PowerPoint standard widescreen) is divided into 12 symmetric vertical columns:
$$W_{\text{canvas}} = 2 \cdot M_{\text{margin}} + 12 \cdot C_{\text{col}} + 11 \cdot G_{\text{gutter}}$$

For a professional enterprise layout:
$$\begin{aligned}
W_{\text{canvas}} &= 13.333'' \quad (12,192,000\text{ EMU}) \\
H_{\text{canvas}} &= 7.500'' \quad (6,858,000\text{ EMU}) \\
M_{\text{margin}} &= 0.800'' \quad (731,520\text{ EMU}) \\
G_{\text{gutter}} &= 0.250'' \quad (228,600\text{ EMU})
\end{aligned}$$

Solving for the single column width $C_{\text{col}}$:
$$12 \cdot C_{\text{col}} = 13.333 - (2 \cdot 0.800) - (11 \cdot 0.250) = 13.333 - 1.600 - 2.750 = 8.983''$$
$$C_{\text{col}} = \frac{8.983}{12} \approx 0.7486'' \quad (684,520\text{ EMU})$$

#### Standard Modular Spans
- **Hero Single-Column / Focus:** Span 12 ($11.733''$)
- **Two Equal Columns (Split Comparison):** Span 6 ($5.741''$ each, separated by 1 gutter $0.250''$)
- **Three Equal Cards (Triptych / Workflow):** Span 4 ($3.744''$ each, separated by 2 gutters $0.250''$)
- **Four Equal Stat Cards:** Span 3 ($2.746''$ each, separated by 3 gutters $0.250''$)

---

### 3.2. Line Measure & Bringhurst's Reading Capacity Law
The number of characters per line of body text dictates reading velocity and cognitive strain:
$$\text{Optimal Measure } M \in [45\text{ch}, 75\text{ch}] \quad (\text{Absolute Minimum: } 35\text{ch})$$

#### The Physics of the Line-Break Crash (Slide 3 Defect Analysis)
Average character width in modern sans-serif fonts (Segoe UI, Aptos, Inter, Helvetica) is:
$$W_{\text{char}} \approx 0.50 - 0.55 \times \text{FontSize}$$

For an $18\text{pt}$ body font:
$$W_{\text{char}} \approx 18\text{pt} \times 0.52 = 9.36\text{pt} = 0.130''$$
To achieve the $35\text{ch}$ minimum readability floor:
$$W_{\text{text\_min}} = 35 \times 0.130'' \approx 4.55'' \quad (4,160,000\text{ EMU})$$

*Why Slide 3 Fractured:*
The card width was set to $2.60''$. With $0.20''$ left/right margins, text width was $2.20''$.
$$\text{Actual Measure} = \frac{2.20''}{0.130''} \approx 16.9\text{ characters/line}$$
At 17 characters per line, English words of 7-10 letters force awkward breaks, resulting in ugly 2-word clipped lines.

---

### 3.3. Modular Typographic Scale (Musical Intervals)
Font sizes across a presentation must never be chosen randomly. They must follow a strict geometric progression:
$$S_n = S_0 \cdot r^n$$
Where $S_0$ is the base body font size ($16\text{pt}$ or $18\text{pt}$) and $r$ is a musical ratio:

| Ratio Name | Factor $r$ | Target Presentation Mood |
|---|---|---|
| **Minor Third** | $1.200$ | High data density, technical specifications, dashboards. |
| **Major Third** | $1.250$ | Balanced corporate reports, strategy reviews. |
| **Perfect Fourth** | $1.333$ | **Gold Standard for Keynote / Executive Pitches.** |
| **Augmented Fourth** | $1.414$ | Dynamic contrast, product launches. |
| **Golden Ratio** | $1.618$ | Bold editorial statements, Apple-style minimalist hero decks. |

*Scale Example on Perfect Fourth ($r = 1.333$, Base $16\text{pt}$):*
- Metadata / Caption: $12\text{pt}$ ($16 / 1.333$)
- Base Body: $16\text{pt}$
- Subhead / Large Body: $21.3\text{pt} \approx 21\text{pt}$
- Section Header: $28.4\text{pt} \approx 28\text{pt}$
- Slide Hero Title: $37.9\text{pt} \approx 38\text{pt}$
- Mega KPI / Stat: $50.5\text{pt} \approx 50\text{pt} \to 67\text{pt} \to 90\text{pt}$

---

### 3.4. Leading & Line-Height Mechanics
$$\text{Line Spacing} = \begin{cases} 
1.10 - 1.15 \times \text{FontSize} & \text{for Display Titles } (\ge 36\text{pt}) \\ 
1.35 - 1.50 \times \text{FontSize} & \text{for Body Text } (14\text{pt} - 22\text{pt}) 
\end{cases}$$
PowerPoint defaults to $1.20\times$ across all sizes. This makes large titles appear disjointed with huge gaps between lines, while body text feels pinched and dense.

---

### 3.5. The Font-to-Span Coupling Law
To prevent the mathematical conflict between multi-card grids (R20) and line measure floors (R17), column spans must be coupled to strict font sizes and text structures:

| Grid Configuration | Column Span | Usable Text Width ($W_{\text{text}}$) | Maximum Font Size | Text Structure Allowed |
|---|---|:---:|:---:|---|
| **1-2 Cards** | Span 6 to 12 | $5.24'' - 11.73''$ | $18\text{pt} - 20\text{pt}$ | Narrative paragraphs ($45-75\text{ch}$ measure). |
| **3 Cards** | Span 4 | $3.24''$ | **$14\text{pt} - 15\text{pt}$** | Short bullet summaries ($\le 3$ lines, $\ge 32\text{ch}$, satisfying $W_{\text{text}} \ge 16 \times \text{FontSize}$). Long text banned. |
| **4 Cards** | Span 3 | $2.25'' - 2.35''$ | **$13\text{pt} - 14\text{pt}$** | **Strictly KPI / Stat Card Structure**: Large numeral ($36-44\text{pt}$ Bold, 1 line) + micro-label ($\le 2$ lines, $\le 22\text{ch}$/line, $\le 12$ words total). Sentences banned. |

---

### 3.6. Vietnamese Diacritic Stack & Line-Height Invariant
Vietnamese typography contains compound diacritics (e.g. *ẩ, ẫ, ệ, ỗ, ợ, ử*) that significantly extend font ascenders and descenders beyond English typography.
- In English, a headline with line-height $1.15\times$ looks compact and modern.
- In Vietnamese, line-height $1.15\times$ causes upper diacritical marks on line 2 to physically collide with bottom strokes of line 1 (e.g. *"HỆ THỐNG / KIỂM ĐỊNH"*).
- **Rule for Vietnamese Slides:**
  $$\text{Line Spacing (Display Titles } \ge 28\text{pt}) \ge 125\% \quad (\text{DrawingML: } \text{spcPct}=\text{"125000"})$$
  $$\text{Line Spacing (Body Text)} \ge 140\% \quad (\text{DrawingML: } \text{spcPct}=\text{"140000"})$$
  In `<a:bodyPr>`, enforce `wrap="square"` and omit `<a:normAutofit/>` (which distorts font sizes arbitrarily between peer cards).

---

## 4. Knuth-Plass Dynamic Programming Formulation

Knuth and Plass modeled paragraph layout as an optimization problem over boxes (words), glue (spaces), and penalties:
$$\text{Demerits } D = \sum_{\text{lines}} \left( \text{constant} + |B|^3 \right) + \text{Penalty}^2$$
Where badness $B$ is a cubic function of space compression/expansion $r$:
$$B = 100 \cdot |r|^3$$

In slide presentation generation, an AI pipeline must calculate badness before emitting text shapes. If $B > 50$, the layout must automatically widen the column or split the text into a secondary slide.

---

## 5. Python Text Capacity & Word Wrap Guard

```python
"""
Swiss Typography Line Measure & Capacity Auditor
Validates that every text box meets the Bringhurst 35ch measure floor.
"""
def audit_text_measure(box_width_in, font_size_pt, margin_left_in=0.1, margin_right_in=0.1):
    usable_width_in = box_width_in - (margin_left_in + margin_right_in)
    avg_char_width_in = (font_size_pt * 0.52) / 72.0
    
    chars_per_line = usable_width_in / avg_char_width_in
    
    passed = chars_per_line >= 35.0
    status = "OPTIMAL" if 45.0 <= chars_per_line <= 75.0 else ("PASS" if passed else "CRITICAL_FAIL")
    
    return {
        "usable_width_in": usable_width_in,
        "chars_per_line": round(chars_per_line, 1),
        "status": status,
        "recommendation": "OK" if passed else f"WIDEN_COLUMN: Minimum width is {35.0 * avg_char_width_in + 0.2:.2f} inches."
    }
```

---

## 6. Comprehensive DOs and DON'Ts

### DO:
1. **Enforce minimum column widths $\ge 4.5''$ for $18\text{pt}$ body text.** Prevent the 2-word line-wrap crash.
2. **Tighten leading on large headlines.** On titles $\ge 40\text{pt}$, set PowerPoint line spacing to $0.95 - 1.05\times$ (`spcPct="100000"` in DrawingML) so multi-line headers feel cohesive.
3. **Align all content to the 12-column grid.** Outer margins must match left and right ($0.80''$ minimum); gutters must be identical between all adjacent cards.
4. **Use sentence case for headers.** Title Case ("Every Single Word Capitalized") creates jagged visual ascenders and slows reading comprehension by $14\%$.

### DON'T:
1. **Never allow widows or orphans.** A single word sitting alone on the final line of a paragraph is an editorial defect. Adjust box width or rephrase.
2. **Never mix more than two font families.** Use one sans-serif family (e.g. Inter or Segoe UI) with variations strictly in weight and scale.
3. **Never justify text on slides.** Full justification on narrow columns creates massive "rivers of white space" due to the Knuth-Plass badness explosion.
