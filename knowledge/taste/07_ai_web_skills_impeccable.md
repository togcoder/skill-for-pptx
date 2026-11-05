# Domain 7: AI Web Design Skills & Anti-Slop Guidelines

## 1. Overview & Cultural Authority
Over 2024–2026, the proliferation of LLM code generation gave rise to a ubiquitous visual phenomenon: "AI slop"—generic, cookie-cutter UI templates characterized by purple-blue neon glows, identical rounded card grids, oversized hero text, gradient text headers, and fake vanity metrics.

In response, open-source engineering leaders and AI design pioneers created rigorous counter-guidelines:
- Paul Bakaus’s **`pbakaus/impeccable`** (Apache-2.0)
- Anthropic’s **`frontend-design`** skill in `anthropics/skills`
- Bergside’s **`awesome-design-skills`** registry
- Jim Liu’s **`baoyu-design`** local design engine
- Shadcn's semantic three-tier design tokens.

These systems establish a strict "craft floor" that actively identifies, intercepts, and eliminates generic AI design defaults before code or slides ship.

## 2. Core Principles & Anti-Patterns

### 2.1. The 7 Deadliest AI Design Tells (To Strictly Ban)
1. **The SaaS-Card Kit:** Content arbitrarily chopped into 3 identical rounded cards, each with a centered icon, bold header, 2 lines of text, and a soft grey shadow (`rgba(0,0,0,0.1)`).
2. **The Kicker / Eyebrow Reflex:** An all-caps, tracked-out label above every heading (`SYSTEM // 2024` or `FEATURES`). The heading carries its own weight; delete the kicker.
3. **The Neon Glow & Purple Gradient:** Purple/cyan outer glows, neon drop shadows, and linear-gradient text across headers. Emphasis comes from weight, size, or contrast—never rainbow fills.
4. **The "Ghost Card" Elevation Bug:** Declaring BOTH a 1px border and a wide soft drop shadow on the same card. Declare elevation ONCE: either a clean 1px border OR a soft diffused shadow, never both stacked together.
5. **Fabricated Metrics & Vanity Claims:** Inventing fake numbers (`99.99% UPTIME`, `124ms RESPONSE TIME`, `10x FASTER`) or AI marketing buzzwords (*"Elevate"*, *"Seamless"*, *"Unleash"*, *"Next-Gen"*).
6. **The Unexamined Dark Theme:** Defaulting to pure black (`#000000`) with acid-green or lime-yellow accents, or warm cream (`#F4F1EA`) with terracotta (`#D97757`) regardless of the brief's real domain.
7. **The Trapped Hero Card:** Stacking elements with absolute positioning until text overlaps emblems or icons get clipped into narrow margins.

### 2.2. Proximity Before Containers
Containers (boxes, cards, background panels) are the lazy designer's crutch.
- **Rule:** Before drawing a box around a group of elements, test whether **whitespace proximity alone** makes the group recognizable:
  $$\text{Gap}_{\text{within group}} \le \frac{1}{3} \times \text{Gap}_{\text{between groups}}$$
- If items within a group are separated by $12\text{px}$, the space separating that group from the next section must be $\ge 36\text{px}$. When proximity holds, delete the card container.

### 2.3. The Squint Test for Hierarchy
- **Procedure:** Squint at the screen (or apply a 10px Gaussian blur to a screenshot of the slide).
- **Passing Criteria:**
  1. The primary focal element (Hero metric or main conclusion) stands out unmistakably.
  2. The secondary tier (section titles, supporting data series) is clearly distinguished from the background.
  3. Tertiary detail (captions, source notes) recedes into the background.
  If everything blurs into an undifferentiated grey soup, the layout has failed hierarchy.

### 2.4. Single Elevation Discipline
In both web and presentation design, an element exists on exactly one elevation tier:
- Tier 0: Canvas base surface.
- Tier 1: Grounded card or structural column (1px border, 0px shadow).
- Tier 2: Raised interactive card or modal focus (soft ambient shadow, 0px border).
- Never combine Tier 1 borders with Tier 2 shadows on the same element.

### 2.5. Motion Thesis & Settling Time
- Every slide or view has at most **one authored focal moment**.
- Motion must never be applied to every element simultaneously.
- When an element enters or transforms:
  - Exit faster than entrance ($60\% - 70\%$ duration).
  - Use exponential ease-out: `cubic-bezier(0.16, 1, 0.3, 1)`.
  - Provide $0.6 - 1.0\text{s}$ of settling time before triggering subsequent beats.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Layout Topology** | Asymmetric layouts: split screens, 2-column zig-zag, horizontal timelines | Repetitive 3-column equal card grids on every slide |
| **Color Base** | Neutral chromatic bases: Zinc (`#09090b`), Slate (`#0f172a`), or Off-White (`#f8fafc`) | Pure black (`#000000`) or default PowerPoint bright blue |
| **Accents** | Exactly 1 accent color with saturation $< 80\%$; reserved for the focal point | Rainbow gradients and colorful icons competing for attention |
| **Writing** | Direct, functional verbs: *"Cut deployment time by 4 minutes"* | AI clichés: *"Seamlessly elevate your workflows"* |
| **Data Honesty** | Label illustrative data clearly as `[ILLUSTRATIVE]` or use supplied real data | Inventing fake statistics and presenting them as facts |

## 4. Translation to PowerPoint (OOXML)
- Avoid native WordArt gradient text fills (`a:gradFill` inside text runs); use solid color fills `<a:solidFill><a:srgbClr val="..."/></a:solidFill>`.
- Replace heavy 3D bevels with flat 1px subtle borders `<a:ln w="9525"><a:solidFill><a:srgbClr val="334155"/></a:solidFill></a:ln>` ($0.75\text{pt}$ border in slate-700).
- Sanitize all visible text: run automated regex checks to ensure internal developer tokens (`!!err_`, `[TODO]`, `NaN%`) never leak onto user-facing slides.
