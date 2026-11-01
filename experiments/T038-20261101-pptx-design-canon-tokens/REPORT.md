# T038 — PPTX Design Canon Tokens, Asymmetric & Bento Grids, Optical Balance & Critic Rules

## Frozen input

- **Request.** Dissect and implement the high-craft mathematical foundation of presentation design alongside Argon (Gemini 4 Argon), establishing:
  1. Cohesive deck-wide chrome: logo placement rules, section breadcrumbs, and bottom progress tracker.
  2. Optical icon balancing: correcting geometric size illusions (square 0.88x, circle 1.0x, wide 1.08x/0.82x, triangle apex offset).
  3. 3-Layer background depth: Z0 Canvas Base $\rightarrow$ Z1 Ambient Radial Glow Orbs $\rightarrow$ Z2 Surface Cards (glassmorphism/frosted).
  4. Content layout architecture: symmetric grids vs. asymmetric golden ratio (61.8% / 38.2%) vs. Bento Grid (7/12 hero card + 3 secondary widgets).
  5. Nancy Duarte pattern breaks: pacing breaks at ~1/3 and ~2/3 deck milestones with $\ge 70\%$ whitespace to combat cognitive fatigue.
  6. 60-30-10 color distribution rule and modular scale typography tokens.
  7. Strict modular boundary: PPTX design and motion craft domain only (`domains/pptx`, `scripts/`, `knowledge/design_system.json`, `tests/`), leaving other craft domains isolated for parallel agents.
- **Base.** Branch `work/T038-pptx-design-canon-tokens` (claim commit `b371cc8`).
- **Environment.** Windows 10/11 x64, Python 3.12, ArtCraft Suite (`D:\artcraft`).

## What was built

### 1. Design System Single Source of Truth (`knowledge/design_system.json`)
Updated version to `1.1.0` with strict backward compatibility and comprehensive new tokens:
- **`chrome`**:
  - Slide canvas: $960 \times 540\text{ pt}$ ($13.333 \times 7.5\text{ in}$).
  - Safe margins: horizontal $48\text{ pt}$ ($0.667\text{ in}$), vertical $36\text{ pt}$ ($0.5\text{ in}$).
  - Safe content box: $x \in [48, 912]$, $y \in [36, 504]$, area $864 \times 468\text{ pt}$.
  - Logo watermark: anchor top-right ($x = 912 - w$, $y = 20\text{ pt}$, max $w \le 72\text{ pt}$, max $h \le 24\text{ pt}$, opacity 0.75). Suppressed on `title`, `section`, `closing`, `statement`, and `duarte_break` slides.
  - Section breadcrumb: top-left $x = 48\text{ pt}$, $y = 22\text{ pt}$, $10\text{ pt}$ uppercase tracked font.
  - Progress bar: bottom edge $y = 537\text{ pt}$, $h = 3\text{ pt}$, active fill $w = 960 \times (idx/n)$, track opacity 0.10.
- **`optical_icons`**:
  - Multipliers compensating for shape volume illusion: Square $0.88\times$, Circle $1.00\times$, Wide $(1.08\times, 0.82\times)$, Triangle $(1.05\times, \text{apex shift } -0.06\times \text{size})$. Badge scale $2.0\times$.
- **`background_layers`**:
  - Z0 Base Canvas: Dark gradient ($135^\circ$ `#0B0F19` to `#111827`) / Light gradient (`#F8FAFC` to `#EDF2F7`).
  - Z1 Ambient Radial Glow: Max 2 orbs, $w \in [380, 520]\text{ pt}$, $h \in [320, 440]\text{ pt}$, blur $120 - 160\text{ pt}$, center opacity $0.12 - 0.18$, morph twin prefix `!!`.
  - Z2 Surface Card: Glassmorphism opacity $65 - 75\%$, top-lit border $1\text{ pt}$, corner radius $8 - 12\text{ pt}$, inner padding $20 - 28\text{ pt}$, gutters $16 - 20\text{ pt}$.
- **`layout_grids`**:
  - Content zone: $864 \times 396\text{ pt}$ at $x=48, y=108\text{ pt}$.
  - Symmetric: 2-col ($w=422\text{ pt}$), 3-col ($w=274\text{ pt}$), 4-col ($w=204\text{ pt}$).
  - Asymmetric Golden Ratio: Major card $522\text{ pt}$ ($61.8\%$), Minor card $322\text{ pt}$ ($38.2\%$), gutter $20\text{ pt}$.
  - Bento Grid: Hero card ($496 \times 396\text{ pt}$), Top-Right card ($348 \times 188\text{ pt}$), Bottom-Right 1 & 2 ($164 \times 188\text{ pt}$ each), gutter $20\text{ pt}$.
- **`duarte_breaks`**:
  - Trigger threshold: decks with $\ge 5$ slides.
  - Milestones: position fractions $[0.33, 0.67]$.
  - Negative space $\ge 70\%$, no card containers, chrome suppressed, single massive statement ($36 - 44\text{ pt}$) or hero KPI ($72 - 96\text{ pt}$).
- **`color_and_type_scales`**:
  - 60-30-10 surface area distribution bounds: $60\%$ canvas, $30\%$ structural surfaces, $10\%$ focal accents.
  - Modular scale typography: Base $14\text{ pt}$, tokens from caption ($11\text{ pt}$) to KPI stat ($72\text{ pt}$).
- **New Canon Rules**:
  - `CHROME-SAFE` (layout safe zones, logo top-right, progress bar bottom edge).
  - `OPT-ICON` (optical icon shape compensation).
  - `LAY-BENTO` (bento and asymmetric proportional hierarchy).
  - `DUA-BREAK` (cognitive pacing pattern breaks at $1/3$ and $2/3$ milestones).
  - Cited authorities: `duarte-resonate`, `swiss-grid-muller-brockmann`, `bringhurst-elements`.

### 2. Design System Programmatic API (`scripts/design_system.py`)
Exposed modular query helpers:
- `chrome()`: returns chrome dimensions and visibility rules.
- `optical_icon_compensation(shape, base_size)`: returns computed $(w, h, dx, dy, \text{badge\_size})$.
- `bento_grid_layout()`: returns 4 canonical bounding boxes for hero, top-right, and bottom split cards.
- `asymmetric_golden_layout(reverse=False)`: returns major and minor card bounding boxes.
- `duarte_break_positions(total_slides)`: computes 1-based slide indices where pattern breaks should be placed.
- `modular_scale(step_name)`: returns exact point sizes for typographic tokens.
- `background_layers()`: returns depth layer parameters.

### 3. Slide Forge Canon Layout & Chrome Builder (`scripts/slide_forge.py`)
- Added new declarative layouts:
  - `asymmetric`: builds 61.8% / 38.2% golden ratio split cards with rounded frosted surfaces and content hierarchy.
  - `bento`: builds 4-card Bento grid (Hero card $7/12$ width + Top-Right feature card + 2 Bottom-Right metric split cards).
  - `duarte_break`: builds high-whitespace cognitive reset slides with mammoth KPIs or bold provocative statements.
- Added automatic deck chrome injection:
  - Bottom progress tracker at $y = 537\text{ pt}$ on content slides (`!!progress-bar`).
  - Top-right logo watermark with AA WCAG contrast and collision clearance against headings.
- Optical icon balancing in `Builder.icon()`: supports `shape="square" | "circle" | "wide" | "triangle"`.
- Resilient static deck fallback when building decks without motion triggers.

### 4. Measurable Design Critic Engine (`scripts/design_critic.py`)
- Registered canon rules `CHROME-SAFE`, `OPT-ICON`, `LAY-BENTO`, and `DUA-BREAK`.
- Integrated per-slide and deck-wide geometric checks.
- Returns comprehensive `evaluations` audit log alongside detected issues.

### 5. Verification & Test Evidence
- Created comprehensive test suite in `tests/test_pptx_design_canon.py` (12 tests covering tokens, math, layout compilation, chrome injection, and critic checks).
- Full repository test suite expanded from 302 to **314 tests, all passing 100% (0 errors, 0 failures, 4 skipped)**:
  ```text
  Ran 314 tests in 14.905s
  OK (skipped=4)
  ```

## Next steps

1. Update `HANDOFF.md`, `docs/CHANGELOG.md`, and `research/tasks/INDEX.md` marking T038 `tip` and opening T039.
2. Commit and push branch `work/T038-pptx-design-canon-tokens`.
3. Provide final summary and execute scheduled shutdown as requested by the user.
