# Domain 8: Data Visualization & Infographics

## 1. Overview & Cultural Authority
Data visualization transforms quantitative numbers into visual insights. Grounded in Edward R. Tufte’s *The Visual Display of Quantitative Information*, Claus O. Wilke’s *Fundamentals of Data Visualization*, and the Financial Times Graphics Team’s *Visual Vocabulary*, world-class data graphics prioritize intellectual integrity, graphical honesty, and high data density.

Amateur chart design is notorious for chartjunk: fake 3D cylinders, truncated bar baselines, garish rainbow colormaps, dark competing gridlines, and detached legends that force the reader's eye to travel endlessly back and forth.

## 2. Core Principles & Formulas

### 2.1. Tufte’s Data-Ink Ratio
The foundational formula of data graphics:
$$\mathbf{\text{Data-Ink Ratio} = \frac{\text{Data-Ink}}{\text{Total Ink in Graphic}} = 1 - \text{Erasable Non-Data-Ink}}$$
- **Data-Ink (Preserve):** The bars representing values, points on a scatterplot, trendlines, and direct data labels.
- **Non-Data-Ink (Erase / Minimize):**
  - Dark, heavy background fills $\to$ Erase.
  - Dark prominent gridlines $\to$ Desaturate to $15\%-20\%$ opacity or remove.
  - Heavy outer chart borders $\to$ Erase.
  - Redundant axis tick marks $\to$ Simplify.
  - Fake 3D depth / bevels $\to$ Erase completely.

### 2.2. Wilke’s Principle of Proportional Ink
The fundamental rule of geometric honesty:
$$\frac{\text{Visual Area of Graphical Element } A}{\text{Visual Area of Graphical Element } B} = \frac{\text{Data Value } A}{\text{Data Value } B}$$
- **The Zero-Baseline Rule for Bars:**
  Bar charts MUST always begin at a baseline of **zero** ($y = 0$). If a bar chart comparing 98 vs 100 truncates the y-axis to start at 95, the visual bar for 100 appears $2.5\times$ taller than 98, creating a deceptive optical lie.
- **Dots / Points for Non-Zero Baselines:**
  If showing fine-grained variance (e.g. temperature fluctuations from 36.5°C to 37.5°C), do NOT use bar charts. Use a **dot plot or line chart**, where position along a common scale encodes value without visual ink area distortion.
- **Bubble / Circle Chart Scaling:**
  When encoding values into circles, scale by **Area**, NOT Radius or Diameter:
  $$\text{Radius } r \propto \sqrt{\text{Data Value } V}$$
  Scaling radius directly makes a $2\times$ value appear $4\times$ larger in area!

### 2.3. Direct Labeling vs. Detached Legends
- **The Detached Legend Anti-Pattern:** Placing a separate color legend box in the top-right corner or below the chart forces the reader into "ping-pong scanning" (looking at a bar $\to$ looking at legend $\to$ looking back at bar).
- **The Direct Labeling Rule:** Place the series name or value label directly adjacent to the end of the line or above the bar:
  ```
  Revenue  ───────────────────────────────● $4.2M (2026)
  Cost     ──────────────● $1.8M (2026)
  ```
  Direct labeling eliminates eye fatigue and reduces comprehension time from 8 seconds to under 2 seconds.

### 2.4. Subtle Desaturated Gridlines
Gridlines exist solely to guide the eye across long distances. They must never compete with data lines:
- Gridline color: Light gray (`#e2e8f0` on light backgrounds, `#334155` on dark backgrounds).
- Stroke width: $0.5\text{pt} - 0.75\text{pt}$ (never $> 1\text{pt}$).
- Dash style: Lightly dotted or dashed.
- Gridline opacity: $\le 20\%$ relative to data series ink.

### 2.5. Data Motion Choreography
When animating charts across slide transitions or on click:
1. **Time-series Line Charts:** Animate from **left to right**, matching the chronological flow of time.
2. **Bar Charts:** Animate bars rising or extending sequentially by category or sorted by magnitude, never all popping in simultaneously.
3. **Data Annotations & Callouts:** Fade in callout cards $150-250\text{ms}$ *after* the chart geometry has finished drawing, ensuring the data establishes context before the commentary lands.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Baselines** | Start bar charts at $0$; use dot plots when zooming into non-zero scales | Truncating bar chart y-axes to exaggerate micro differences |
| **Chart Types** | Match chart type to analytical intent (Trend $\to$ Line, Comparison $\to$ Bar, Part-to-whole $\to$ 100% Stacked Bar) | Using 3D Pie charts with $> 5$ slices |
| **Colormaps** | Use perceptually uniform palettes (Viridis, ColorBrewer) or single-hue ramps | Rainbow spectrum palettes where yellow visually explodes over blue |
| **Gridlines** | Faint, subtle horizontal-only gridlines behind data | Dense dark black gridlines criss-crossing the chart |
| **Formatting** | Format numbers clearly with units: `\$4.2M`, `+18%`, `320ms` | Raw unformatted database floats: `4218942.1283` |

## 4. Translation to PowerPoint (OOXML)
- In PPTX charts (`ppt/charts/chart{N}.xml`):
  - Strip outer plot area borders: `<c:spPr><a:ln><a:noFill/></a:ln></c:spPr>`.
  - Gridlines: `<c:majorGridlines><c:spPr><a:ln w="4762"><a:solidFill><a:srgbClr val="334155"/></a:solidFill><a:prstDash val="sysDot"/></a:ln></c:spPr></c:majorGridlines>`.
  - Data series animation: In `<p:cTn>`, configure chart animation type `byCategory` or `bySeries` instead of animating the entire chart box as a single opaque block.
