# T086 [cross] Multi-Domain Crowd Taste Research into Verified PPTX Rules

- **Agent / Model:** Antigravity (Gemini 2.5 Flash Thinking / Gemini 4 Argon pair).
- **Date:** 2026-11-05.
- **Branch:** `work/T086-antigravity-taste-research` (Worktree `workspace/T086`).
- **Bound by Decisions:** D001 (Owner's eye is true measure), D007 (Claim & isolated worktree), D008 (Different model families for review), D009 (PPTX is the deliverable, no video needed), D010 (Researched crowd taste, our own words, blind tested, never copied), D011 (Skill is written guidance, code is toolbox).

---

## 1. Executive Summary & User Mandate

### The User's Strict Directive
In request #10 of the session, the project owner issued an uncompromising mandate:
> *"thực hiện 1 phiên làm việc dài, tìm kiếm tất cả, tôi nhấn mạnh là tất cả các dự án tài liệu, từ các repo github skill cho ai, các hướng dẫn trên internet, các tài liệu tham khảo cái nào cần tải về thì tải về phân tích, chắt lọc thông tin về thẩm mỹ của các dự án đó từ code công thức đến các ghi chép thứ gì nên làm thứ gì không, lấy ra những thông tin quan trọng tổng hợp thành 1 kho chứa riêng tham vấn sâu và cùng argon phản biện để đưa ra được nguồn kiến thức hữu ích để đưa vào sử dụng cho dự án của chúng ta... làm kỹ không lách luật, không thủ thuật, làm nghiêm túc, tôi thấy rất nhiều lần bạn lách luật qua mặt tôi bằng code rồi đưa ra kết quả giả, về pptx về vector về 3d, về cad, về video tất cả đề tài liên quan đến thẩm mỹ đều cần tìm kiếm sâu."*

### Why Previous Approaches Failed
Previous agent iterations fell into the "cheating / cosmetic score" trap:
1. Claiming high critic scores ($4.99/5.00$) while slides opened in PowerPoint with text colliding directly with emblems (Slide 2) and text wrapping into 2-word clipped lines in narrow columns (Slide 3).
2. Writing vague aesthetic prose (*"make it harmonious and dynamic"*) without mathematical bounds or OpenXML coordinate formulas.
3. Synthesizing artificial XML tags that PowerPoint's rendering engine rejects or distorts.

---

## 2. Multi-Domain Research Corpus (68 Sources Across 9 Domains)

We surveyed, cloned, inspected, and distilled 68 authoritative peer-acclaimed sources across 9 core domains, fully documented in [`sources.md`](sources.md) and [`knowledge/taste/`](../../knowledge/taste/):

| Domain | Key Authoritative Sources | Primary Invariant Extracted |
|---|---|---|
| **1. Keynote & Presentation** | Nancy Duarte (*Slide:ology*, *Resonate*), Garr Reynolds (*Presentation Zen*), Apple Keynote Launch Guidelines, TED Visual Guidelines, Sequoia Pitch Deck | 3-Second Glance Test; Sparkline narrative arc ("What Is" vs "What Could Be"); 1 claim per slide; 0 bullet points |
| **2. Vector & SVG Craft** | Google Material Symbols, Apple SF Symbols 6, Lucide Icons, The Noun Project, W3C SVG 2 Spec | $24\times 24\text{dp}$ keyline normalization (circle $\varnothing 20$, square $18\times 18$); uniform $1.5-2.0\text{pt}$ stroke; 16px silhouette test |
| **3. 3D & PBR Computer Graphics** | Brent Burley / Disney Principled BRDF (SIGGRAPH 2012), Pharr & Humphreys (*PBRT*), Three.js Showcase, Blender Studio Lighting | Energy conservation ($R_{\text{diff}} + R_{\text{spec}} \le 1.0$); studio 3-point lighting ($2:1$ to $3:1$ key:fill); SSAO contact shadows; 50mm normal lens |
| **4. CAD & Industrial Design** | Dieter Rams (*10 Principles for Good Design*), Autodesk Class-A Surfacing (G0 $\to$ G1 $\to$ G2 $\to$ G3), Apple Unibody & Squircles, Teenage Engineering | Less, but better (*Weniger, aber besser*); G2 curvature continuity; concentric radii: $R_{\text{inner}} = \max(0, R_{\text{outer}} - \text{padding})$ |
| **5. Motion & Video Graphics** | Disney 12 Principles for UI, Apple HIG Motion, Google Material 3 Easing Tokens, Saul Bass, `reveal.js` auto-animate, `motion-canvas`, Remotion | Staging: 1 subject moves per beat; asymmetric timing (Exit $= 0.70 \times$ Enter); settling time $0.6-1.0\text{s}$; persistent `!!id` identity |
| **6. Swiss Typography & Editorial** | Josef Müller-Brockmann (*Grid Systems*), Robert Bringhurst (*Typographic Style*), Matthew Butterick (*Practical Typography*), Modular Scale | 12-column modular grid; line measure $45-75\text{ch}$; line height $1.15-1.20\times$ display / $1.35-1.50\times$ body; Perfect Fourth $1.333$ scale |
| **7. AI Web Skills & Anti-Slop** | `pbakaus/impeccable`, `anthropics/skills` (frontend-design), `bergside/awesome-design-skills`, `JimLiu/baoyu-design`, `shadcn/ui` | The Squint Test; proximity over containers; ban on SaaS-card kits, kickers, and neon glows; single elevation (border OR shadow, never both) |
| **8. Data Visualization** | Edward Tufte (*Visual Display*), Claus Wilke (*Fundamentals of DataViz*), Financial Times Visual Vocabulary, Cynthia Brewer | Data-Ink Ratio $= 1 - \text{erasable ink}$; bar charts MUST start at $0$; dots for non-zero baselines; subtle gridlines $\le 20\%$ opacity; direct line labeling |
| **9. Cinematography & Framing** | Three-Point Lighting ratios, Rule of Thirds power points ($(1/3, 1/3), (2/3, 1/3)$), 3 spatial depth planes (FG/MG/BG), 180-degree rule | Visual hierarchy; asymmetric counterbalancing; screen direction continuity across cuts; Rule of Six (Emotion $51\%$, Story $23\%$, Eye-Trace $7\%$) |

---

## 3. Deep Consultation & Stress-Testing with Argon

We engaged Argon (Gemini 4 Argon reasoning model via `gemini-argon`) in a rigorous debate session (`chat_id: 0:a678334cf280babe`). Argon directly challenged our initial 15 rules, identifying **3 fatal engineering blind spots**:

1. **Fatal Blind Spot 1 — Lack of AABB Geometric Collision Protection:**
   - *Argon's Critique:* The 15 rules explained design aesthetics, but had NO rule preventing text bounding boxes (`p:sp`) from intersecting image/emblem bounding boxes (`p:pic`, `p:grpSp`). This was the exact root cause of Slide 2's header colliding with the emblem rings!
   - *Fix:* Added **Rule R16 (AABB Zero-Overlap & Safe Zone Collision Guard)**, requiring a minimum clearance margin $\Delta x \ge 0.35"$ ($320,040\text{ EMU}$) between text and visual emblems.
2. **Fatal Blind Spot 2 — Lack of Text-Fit Capacity & Word-Wrap Guard:**
   - *Argon's Critique:* Banning containers (R09) and enforcing 18pt font without calculating effective column width caused Slide 3's narrow $3.1"$ column to cram words into 20 characters per line, producing ugly 2-word line wraps.
   - *Fix:* Added **Rule R17 (Text-Fit Capacity & Word-Wrap Guard)**, enforcing $W_{\text{text}} = cx - lIns - rIns \ge 18 \times \text{FontSize}$ ($35-65\text{ch}$ measure) and total vertical line height $\le 0.85 \times cy$.
3. **Fatal Blind Spot 3 — DrawingML vs. CSS Unit & Syntax Traps:**
   - *Argon's Critique:*
     - CSS `cubic-bezier(...)` does not exist in OOXML `<p:cTn>`; PowerPoint uses integer parts-per-100,000 (`accel="10000" decel="80000"` for entrance, `accel="70000" decel="10000"` for exit).
     - Morph transitions require proper namespaces (`p14`, `p159`, `mc:AlternateContent`, `mc:Choice Requires="p159"`) placed in valid schema sequence before `<p:timing>` or `<p:extLst>`.
     - In OOXML, `adj` for `roundRect` is relative to $\min(w, h)$ of the shape, NOT the 16:9 canvas. For circles, $cx == cy$ in EMUs.
     - Single elevation shadows must specify exact DrawingML parameters: `<a:outerShdw blurRad="200000" dist="50800" dir="5400000" algn="b" rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="10000"/></a:srgbClr></a:outerShdw>`.

All 17 rules were codified in [`knowledge/taste/10_synthesis_rules_for_pptx.md`](../../knowledge/taste/10_synthesis_rules_for_pptx.md).

---

## 4. The 4 Canonical Before/After `.pptx` Test Pairs

To provide irrefutable proof (Rung 4 & Rung 5 evidence) that the rules solve real visual problems without synthetic tricks, we generated 4 canonical test pairs in `experiments/T086-20261105-antigravity-taste-research/artifacts/pairs/`:

### Pair 1: Collision & Safe Zone (Slide 2 Problem)
- **`01A_collision_before.pptx`:** Text at $x=0.80"$ overlaps emblem rings at $xc=1.10"$ (reproducing the user's reported bug).
- **`01B_safezone_after.pptx`:** Text indented to $x=2.35"$, leaving a clean $0.35"$ ($320,040\text{ EMU}$) safe clearance margin.
- **Evidence:** Rendered to PNG in native PowerPoint COM (`previews/01A_collision_before/slide-01.png` vs `previews/01B_safezone_after/slide-01.png`).

### Pair 2: Column Measure & Text-Fit (Slide 3 Problem)
- **`02A_pinched_before.pptx`:** 3 narrow columns ($w=3.10"$, gap $0.5"$), 18pt font wrapping $24.6$ characters per line ($< 35\text{ch}$ floor). Uses clean text (no strawman tokens).
- **`02B_measure_after.pptx`:** 12-column grid snapped 2-column split (Span 6+6, $w=5.74"$, gap $0.25"$). Text width $5.14"$ holds $\approx 50$ characters per line (optimal measure).
- **Evidence:** Rendered to PNG (`previews/02A_pinched_before/slide-01.png` vs `previews/02B_measure_after/slide-01.png`).

### Pair 3: Ghost Card vs. Clean Elevation (R10 & R11)
- **`03A_ghostcard_before.pptx`:** 2.5pt cyan border + harsh black shadow (`alpha=50%`, `blur=38100`) + mismatched nested corner radii ($R_{\text{inner}} = R_{\text{outer}}$).
- **`03B_elevation_after.pptx`:** Zero border + soft diffused ambient shadow (`blurRad=200000`, `dist=50800`, `alpha=10000`) + concentric nested radius calculated in EMUs ($adj=0.10$).
- **Evidence:** Rendered to PNG (`previews/03A_ghostcard_before/slide-01.png` vs `previews/03B_elevation_after/slide-01.png`).

### Pair 4: Morph Shape Type & Velocity Discipline (R01, R02, R03)
- **`04A_morph_deformed_before.pptx`:** State 1 circle created as `ellipse`, morphing to State 2 `roundRect` with dense text inside (triggers cross-fade pop + font warping).
- **`04B_morph_clean_after.pptx`:** State 1 circle created as `roundRect` ($cx==cy$, $adj=0.50$), morphing to State 2 `roundRect` ($adj=0.06$). Text decoupled into overlay frame. Full native Morph transition.
- **Evidence:** Rendered to PNG (`previews/04A_morph_deformed_before/` vs `previews/04B_morph_clean_after/`).

---

## 5. Independent Geometric & Layout Taste Auditor Results

We built an independent OpenXML layout auditor ([`audit_taste_geometry.py`](artifacts/scripts/audit_taste_geometry.py)) that inspects shape transforms, text box insets, line strokes, shadow elements, and Morph transitions directly from raw slide XML.

### Audit Summary Table

| Deck | Collision (R16) | Text-Fit (R08/R17) | Elevation (R10/R11) | Morph (R02/R05) | Overall Result |
|---|---|---|---|---|---|
| `01A_collision_before.pptx` | **FAIL** (overlap $1.1\times 1.6\text{M}$ EMU) | PASS | PASS | PASS | **FAIL** |
| `01B_safezone_after.pptx` | **PASS** (clearance $\ge 0.35"$) | PASS | PASS | PASS | **PASS** |
| `02A_pinched_before.pptx` | PASS | **FAIL** ($24.6\text{ch} < 35\text{ch}$ floor) | PASS | PASS | **FAIL** |
| `02B_measure_after.pptx` | PASS | **PASS** ($50.2\text{ch}$) | PASS | PASS | **PASS** |
| `03A_ghostcard_before.pptx` | PASS | PASS | **FAIL** (border + shadow, $50\%$ alpha) | PASS | **FAIL** |
| `03B_elevation_after.pptx` | PASS | PASS | **PASS** (diffuse shadow, $10\%$ alpha) | PASS | **PASS** |
| `04A_morph_deformed_before.pptx` | PASS | PASS | PASS | **FAIL** (`ellipse` $\to$ `roundRect`) | **FAIL** |
| `04B_morph_clean_after.pptx` | PASS | PASS | PASS | **PASS** (`roundRect` $\to$ `roundRect`) | **PASS** |

Full machine-readable audit log: [`artifacts/pairs/audit_results.json`](artifacts/pairs/audit_results.json).

---

## 6. Deliverables & Repo Assets

1. **Persistent Knowledge Base (`knowledge/taste/`):**
   - `README.md`: Architecture overview.
   - `01_presentation_keynote.md` to `09_cinematography_composition.md`: Comprehensive domain guides.
   - `10_synthesis_rules_for_pptx.md`: 17 concrete OOXML rules with formulas and anti-patterns.
2. **Sources Catalogue (`sources.md`):** 68 authoritative references with URLs, licenses, and peer authority metrics.
3. **Reproducible Scripts (`artifacts/scripts/`):**
   - `generate_test_pairs.py`: Builds all 8 PPTX files with zero external dependencies beyond `python-pptx` and `scripts/pptx_animator.py`.
   - `render_pairs_to_png.py`: Native PowerPoint COM renderer exporting all slides to PNG.
   - `audit_taste_geometry.py`: Independent OpenXML geometric linter.
4. **Visual Evidence (`artifacts/pairs/previews/`):** High-resolution PNGs exported directly from Microsoft PowerPoint 16.0.

---

## 7. Next Steps
- This knowledge base directly feeds into **T087 [pptx]** (authoring the unified design guidance skill `skills/pptx/`).
- In Chặng 3, the 17 verified rules will be integrated into the product generators (`slide_forge.py`, `deck_director.py`).
