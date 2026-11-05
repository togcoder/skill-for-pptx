# Domain 8: Data Visualization & Quantitative Craftsmanship

## 1. Overview & Cultural Authority
Data visualization taste (Edward Tufte's *The Visual Display of Quantitative Information*, Claus Wilke's *Fundamentals of Data Visualization*, Stephen Few's *Show Me the Numbers*, the Financial Times Visual Vocabulary, and Cynthia Brewer's ColorBrewer) is founded on **intellectual honesty, geometric precision, and high data density**.

In business and technical presentations, charts are the ultimate arbiters of credibility. Distorted baselines, 3D extruded pie charts, fluorescent color palettes, and detached legends that force eye saccades instantly destroy audience trust.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Architecture & Focus | Core Invariant Extracted |
|---|---|---|
| [`d3/d3`](https://github.com/d3/d3) | Low-level grammar of graphics in JavaScript | Declarative data-binding; monotone cubic spline interpolators; quantitative scale transformations. |
| [`Financial-Times/chart-doctor`](https://github.com/Financial-Times/chart-doctor) | The FT Visual Vocabulary repository | 9 distinct communication intents (Deviation, Correlation, Ranking, Distribution, Time, Magnitude, Part-to-Whole, Spatial, Flow). |
| [`clauswilke/dataviz`](https://github.com/clauswilke/dataviz) | Companion codebase for *Fundamentals of Data Visualization* | Principle of Proportional Ink validation; color perception scales; aspect ratio bank-to-$45^\circ$ calculations. |
| [`vega/vega-lite`](https://github.com/vega/vega-lite) | High-level declarative grammar of graphics | Automated unit-spec composition; facet layering; perceptual channel mapping rules. |

---

## 3. Mathematical Foundations & Perceptual Laws

### 3.1. Edward Tufte's Data-Ink Ratio
Tufte defined the fundamental efficiency metric of any quantitative graphic:
$$\text{Data-Ink Ratio} = \frac{\text{Data-Ink}}{\text{Total Ink Used to Print / Render Graphic}}$$
$$\text{Data-Ink Ratio} = 1.0 - \text{Proportion of Graphic that can be Erased Without Loss of Data}$$

*Prescription for Slides:*
Maximize the Data-Ink Ratio to $\approx 1.0$ by systematically erasing:
1. Outer chart bounding box borders (4 lines erased).
2. Heavy dark background fills.
3. Vertical gridlines on time-series charts.
4. Redundant axis tick marks and decorative drop shadows.

---

### 3.2. Claus Wilke's Principle of Proportional Ink
The visual area or length of a graphic element must scale in direct linear proportion to the physical data value it represents:
$$\frac{\text{Visual Area}_i}{\sum_{k} \text{Visual Area}_k} = \frac{\text{Data Value}_i}{\sum_{k} \text{Data Value}_k}$$

#### The Non-Zero Baseline Distortion Proof (Why Bar Charts MUST Start at Zero)
Consider two quarterly revenue numbers: $V_1 = \$95\text{M}$ and $V_2 = \$100\text{M}$. The true growth is:
$$\text{True Relative Growth} = \frac{100 - 95}{95} = +5.26\%$$

If an analyst truncates the y-axis baseline to $B = \$90\text{M}$:
$$\begin{aligned}
h_1 &= V_1 - B = 95 - 90 = 5 \\
h_2 &= V_2 - B = 100 - 90 = 10 \\
\text{Visual Perceived Ratio} &= \frac{h_2}{h_1} = \frac{10}{5} = 2.00 \quad (+100\% \text{ visual increase!})
\end{aligned}$$
*Verdict:* Truncating the baseline of a bar chart introduces a **$19\times$ perceptual lie factor**. Bar charts must always start at $0$. If small variations in a high-baseline range must be highlighted, use a **dot plot or connected line chart**, where baseline truncation is mathematically legitimate.

---

### 3.3. Stephen Few's Perceptual Channel Accuracy Hierarchy
Human vision decodes quantitative properties with varying degrees of neurological accuracy (Cleveland & McGill psychophysical experiments):

$$\begin{aligned}
\text{Rank 1 (Most Accurate)} &: \text{Position along a common aligned scale (Dot plot, standard bar chart)} \\
\text{Rank 2} &: \text{Length / Distance (Horizontal / Vertical bars)} \\
\text{Rank 3} &: \text{Direction / Slope (Line charts, trend vectors)} \\
\text{Rank 4} &: \text{Angle / Tilt (Pie chart slices — error rate } \pm 18-25\%) \\
\text{Rank 5} &: \text{Area (Bubble charts, treemaps — error rate } \pm 20-35\%) \\
\text{Rank 6} &: \text{Volume / 3D Extrusion (Banned entirely)} \\
\text{Rank 7 (Least Accurate)} &: \text{Color Saturation / Lightness (Heatmaps, choropleths)}
\end{aligned}$$

---

### 3.4. Direct Labeling vs. Detached Legends (Eye Saccade Reduction)
A detached legend box positioned in the top-right corner forces the audience's fovea to oscillate repeatedly between the data lines and the legend key (saccadic eye strain).

*Mathematical Law of Direct Labeling:*
$$\text{Label Coordinates } (x_L, y_L) = (x_{\text{last\_data\_point}} + \Delta x, y_{\text{last\_data\_point}})$$
Place the category label directly next to the final point of each data curve, rendered in the exact same color hue as the line. Eliminate the legend box completely.

---

### 3.5. Gridline Attenuation
$$\text{Gridline Opacity } \alpha_{\text{grid}} \le 15\% \quad (\text{DrawingML: } \text{alpha}=\text{"15000"})$$
Gridlines exist solely to guide interpolation; they must sit quietly beneath the data layer, never competing with data marks.

---

## 4. Python Data-Ink & Baseline Auditor

```python
"""
Data Visualization Integrity Auditor
Validates baseline zero-anchoring and data-ink optimization on PPTX chart elements.
"""
def audit_chart_integrity(chart):
    violations = []
    
    # 1. Bar Chart Baseline Check
    if chart.has_category_axis and chart.chart_type in [
        # Bar/Column chart types
        2, 3, 4, 5, 51, 52, 53, 54, 55, 56
    ]:
        val_axis = chart.value_axis
        if val_axis.has_minimum_scale:
            if val_axis.minimum_scale != 0.0:
                violations.append(
                    f"PROPORTIONAL_INK_VIOLATION: Bar chart value axis starts at {val_axis.minimum_scale} instead of 0.0."
                )
                
    # 2. Banned 3D Chart Types Check
    chart_name = str(chart.chart_type)
    if "3D" in chart_name or chart.chart_type in [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
        violations.append("BANNED_3D_CHART: 3D perspective charts distort quantitative angles and are strictly prohibited.")
        
    return {
        "passed": len(violations) == 0,
        "violations": violations
    }
```

---

## 5. Comprehensive DOs and DON'Ts

### DO:
1. **Always anchor bar and column charts at zero.** Never truncate the baseline on bar charts.
2. **Label data series directly at their endpoints.** Erase detached legend boxes to reduce visual saccades.
3. **Mute gridlines to $\le 15\%$ opacity.** Gridlines should be barely visible guides, never heavy black lines.
4. **Highlight the single critical data series with color.** Keep 4 comparison lines in muted slate grey (`#64748B`), and color the hero metric in vibrant cyan (`#0EA5E9`).

### DON'T:
1. **Never use 3D charts.** 3D bar, pie, and ribbon charts distort angles and violate the Cleveland-McGill perceptual scale.
2. **Never use pie charts with more than 3 slices.** Use a horizontal ranked bar chart instead.
3. **Never place vertical gridlines on time-series charts.** Time naturally flows left-to-right; vertical lines create visual stutter.
