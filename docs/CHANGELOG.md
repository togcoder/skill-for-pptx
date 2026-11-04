# Changelog — research log, newest first

This is the chronological record each task wrote when it finished. It used to
be `docs/STATUS.md`; since T034 the current state lives in
[STATUS.md](STATUS.md), and this file is append-only history. The entries are
kept verbatim: older ones mention test counts, versions and "next steps" that
were true at the time. Task IDs and their branches are listed in
[research/tasks/INDEX.md](../research/tasks/INDEX.md).

## T063 [pptx] Forge debt that users see — 2026-11-04

- **Why.** T057 named four defects a Forge user sees: count-up proxies stack in
  print/PDF/Morph, the highlight marker ignores horizontal alignment, decks
  carry 13–15 type sizes, and every cinematic deck trips MOT-SETTLE.
- **Fixed.** Count-up proxies now sit below an opaque final-value source (the
  container colour), so print/PDF/static Morph show one value while PowerPoint
  still counts up. Highlight geometry reads paragraph alignment and measures
  the real font. Type sizes come from the Office kit `type_scale_pt`
  (3–6 sizes; `kpi_stat` display token only when a KPI exists). Ken Burns
  releases to the authored frame before Morph; generated process tokens are
  authored at their last stop (T034 author-at-destination).
- **Evidence.** All five example decks: no TYP-SIZES or MOT-SETTLE warning,
  sizes 13–15 → 6, overall 4.36–4.53 → 4.70–4.88. PowerPoint PDF, PNG and
  CreateVideo frames inspected (rung 5); DeckCraft Morph frame used only as a
  static second reader (rung 4). 470 tests pass, 8 skipped.
- **Report.** `experiments/T063-20261104-opencode-forge-debt/REPORT.md`.

## T057 [cross] Lead review, DeckCraft evaluation and next programme — 2026-11-04

- **Why.** After 22 tasks in four days (T035–T056) the owner asked Claude to
  act as lead: judge the state, name the difficulties and set the next
  research directions, and answer whether DeckCraft makes PPTX asset creation
  easier for an AI.
- **Findings.** 461 tests pass. The pptx core has not changed since T038 and
  the T034 problems (type scale, MOT-SETTLE, native interactive gate) are
  open. Five task IDs were used twice; pptx features reached `main` without
  PR or review; every review is by one agent (Argon); `HANDOFF.md` was
  mojibake and pointed at T047 as the next ID; three modules write
  `interactiveSeq` separately.
- **DeckCraft 0.13.1.** Static renders match PowerPoint closely (0.1–2.1% of
  pixels differ by >40; charts differ most); Morph frames in 0.19 s but their
  fidelity is unproven; no in-slide animation renderer; `convert` rewrites
  some timing nodes. Its 330 commands (also over MCP) add Merge Shapes,
  freeform curves, shape effects, background removal and SmartArt that
  python-pptx cannot do: useful for native PPTX assets, not for motion QA.
  Open source (MIT/Apache-2.0), so an animation-frame renderer is a research
  option (T060).
- **Programme.** Reserved briefs T058–T065 (harness, DeckCraft fidelity,
  DeckCraft source study, one interaction writer, native asset factory, Forge
  debt, T055 3D, lab hygiene), each with a builder and a critic from a
  different model family. Breadth domains frozen for one cycle.
- **Rewritten.** `HANDOFF.md` (clean UTF-8, Vietnamese) and `docs/STATUS.md`.

## T056 [vector] Part-based isometric product illustration (`iso-vector-craft`) — 2026-11-03

- **Why.** T053 proved that a product drawing must be a model, not a trace, but
  the result still read as a diagram. T056 adds the missing method: a measured
  part inventory, one camera chosen per product, four-tone materials and a
  written painter's order. The owner accepted the Technics V3 result and asked
  for the method on `main`.
- **Skill.** `skills/iso-vector-craft/SKILL.md`: 30–60 named parts, 1 unit = 1 mm,
  azimuth/elevation rules, 4–6 materials, detail budget, failure modes and a
  checklist. The MIT **Anatomy** kit (commit `1482e84`) is vendored with
  `LICENSE`/`ATTRIBUTION.md`; `kit/product-svg.mjs` bakes the light palette into
  literal values, adds `<title>/<desc>` and pins a real font.
- **Examples.** Technics SL-1200: 518 paths, 12 part groups, plinth 54, Ø330
  platter, Ø300 record, Ø100 label, Ø96 arm well. Gale Silver Monitor: 79
  paths front / 114 rear. Rolleiflex TLR: 217 paths, kept as a labelled hard
  subject stress test, not a showcase.
- **Evidence.** resvg renders for every artifact; VectorCraft `info` 0 warnings
  and all fonts exact; `tests/test_iso_vector_skill.py` (13 tests) checks XML,
  no raster/external refs, baked palette, path counts, 12 Technics part groups
  and the MIT attribution. Progression sheet keeps V1 (411 paths, 98-unit
  plinth, 18°) as the negative result; V2 (463, 54 units, 24°) is the silhouette
  win.
- **Status.** EXPERIMENTAL; owner approved the direction; Argon review
  `accept-with-fixes` (round 2) after the gimbal order, relative anchors,
  generic rules and DOM contract fixes; merged to `main` as a skill (not a
  canonical replacement for T053).
- Report: `experiments/T056-20261103-opencode-iso-vector/REPORT.md`.

## T053 [vector] Semantic 2.5D reconstruction (supersedes T051) — 2026-11-02

- **Why.** The owner rejected T051: Canny edges are a trace, not a
  reconstruction. T053 models the machine in object coordinates and draws the
  parts, instead of extracting pixel lines.
- **Module.** `scripts/vector_reconstruct.py`: axonometric projection, box,
  front rounded rect/circle, vertical/horizontal cylinder, tube, gradients and
  an SVG scene with semantic groups.
- **Scene.** `build_quickmill.py`: 14 parts / 16 groups, 101 primitive paths,
  5 live text elements, 1000 × 1000; one light, painter's order, no raster.
- **Evidence.** VectorCraft `info`: 16 groups, 102 paths, 5 types, 0 warnings;
  before/after sheet shows the T051 trace next to the reconstruction.
- **Tests.** `tests/test_vector_reconstruct.py` (16 tests); full suite 448
  tests OK (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T053, round 3);
  merged to main (PR #50).
- Report: `experiments/T053-20261102-opencode-vector-reconstruction/REPORT.md`.

## T051 [vector] Photo-to-vector line hierarchy and detail budget — 2026-11-02

- **Pipeline.** `scripts/photo_vector.py` segments a product photo (GrabCut,
  shadow trim), flattens 5 material tones, extracts/dedupes Canny edges, and
  classifies them as silhouette, form, detail or removed with recorded reasons.
- **Policy.** Form: length ≥ 5.5% of the object diagonal and turning ≤ 0.55°/px.
  Detail: short + strong, closed controls ≥ 3 mm and circularity ≥ 0.28; 1.5 mm
  scale floor. The full trace is kept as the strawman.
- **Result.** Line style: 34 form + 16 detail, 1,437 nodes, 0 fills, GrabCut IoU
  0.959, VectorCraft 0 warnings. Colour style: 15 fills, ΔE76 10.56. Full-line strawman:
  58 + 133, 2,268 (colour 3,178) nodes, visibly scribbled.
- **Evidence.** Four budget SVGs + line + full-line, VectorCraft renders, photo-vs-vector,
  layer stack, budget sheet, `levels.json`/`line.json`; 18 new tests.
- **Tests.** `tests/test_photo_vector.py` (18 tests); full suite 422 tests OK
  (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T051, round 2);
  merged to main (PR #49).
- Report: `experiments/T051-20261102-opencode-photo-vector/REPORT.md`.
## T052 [docx] Configurable standard profiles + Vietnamese scientific report — 2026-11-02

- **Profile layer.** `domains/docx/data/standard_profiles.json` adds four
  sourced profiles: `hust-datn-2017`, `vnu-uet-kl-2024`, `iso-7144-thesis` and
  `annual-report-gri`, with page, typography, numbering, caption position,
  front-matter order, reference position and page limits.
- **Merge.** `scripts/docx_profiles.py` merges profile defaults under the spec
  (explicit spec wins) and `document_forge --profile` applies them. The same
  content spec builds a HUST report (34 body pages, 48 total) and a VNU-UET
  report (35 body pages, 45 total).
- **Conformance.** `check_docx()` measures A4, margins, body/table font, size,
  line spacing, first-line indent, heading depth/numbering, chapter captions
  and position, page number, front-matter order, references/citations, abstract
  length, body pages and equations. Both builds pass (23/23 and 24/24).
- **Chapter numbering.** `STYLEREF "Heading 1" \s` + `SEQ ... \s 1` for
  figures, tables and equations; `Chapter Unnumbered` standalone style for
  `Mở đầu` so it does not shift the Heading 1 counter.
- **Report content.** 59 headings (max H3), 23/22 tables, 7 figures, 9 native
  equations, 12 references, 13 citation fields, thesis cover, declaration,
  task, abstract, abbreviations, lists, appendices.
- **Cross-asset.** SVG architecture/window diagrams via VectorCraft; training,
  PR, F1, ablation and latency charts via Chart Forge (SheetCraft).
- **Audit.** Both builds: 0 errors, 0 warnings with profile-aware margin floor;
  204 fields, 88 bookmarks, `vi-VN`; Word refreshed fields and exported 48/45
  pages.
- **Tests.** `tests/test_docx_profiles.py` (7 tests); full suite 411 tests OK
  (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T052, round 2); merged to main (306f5f2).
- Report: `experiments/T052-20261102-opencode-scientific-report/REPORT.md`.

## T050 [xlsx] VBA UserForm + composed dashboard — 2026-11-02

- **UserForm.** `scripts/userform_forge.py` injects a real `frmEntry` (22
  controls: 8 labels, 4 combo boxes, 4 text boxes, 3 buttons, title/hint/status)
  and a `FormTools` module into an `.xlsm`; `btnSave_Click` validates and appends
  to the hidden Data sheet.
- **Dashboard.** `scripts/dashboard_forge.py` composes a 12-column A4 landscape
  dashboard: 4 KPI cards, 4 native charts (line/column/bar/doughnut), hidden
  Data/Trend/Model, 3 filter/form buttons, one-page print area.
- **Evidence.** Excel opened the exact XLSM: 4 sheets (3 hidden), 4 charts,
  3 buttons, 22 form controls; Dashboard exported as **1 page**; form code has
  `btnSave_Click`/`ClearForm`/`nextId`. Macro execution remains blocked by host
  policy; the form was not shown end-to-end.
- **Tests.** `tests/test_dashboard_userform.py` (3 tests); full suite 407 tests
  OK (8 skipped).
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T050, round 2); merged to main (90695a9).
- Report: `experiments/T050-20261102-opencode-userform-dashboard/REPORT.md`.

## T048 [xlsx] Workbook UX: hidden data, VBA input, tab colour, merges — 2026-11-01

- **UX layer.** `sheet_forge` accepts a `ux` block: per-sheet `hidden` /
  `very_hidden`, `tab_color`, `protect`, and `input_form`.
- **Input form.** A visible Input sheet with 18 merged layout ranges, 8 data
  validations, auto Task ID, inline status and 3 macro buttons.
- **Hidden data.** Data/Model/Team/Gantt/Relations hidden; Pivot/Lookups
  veryHidden; only Dashboard/Input visible. Tab colours set.
- **Protection.** Input and Dashboard protected; input cells unlocked.
- **VBA.** `AddRecord`/`ClearForm`/`RefreshDashboard`/`SetStatus`; button
  macros rewritten to `[0]!DashboardTools.*` after SaveAs.
- **Evidence.** Excel opened XLSX/XLSM; 3 buttons, 8 validations, 2 protections,
  5 hidden + 2 veryHidden; Input and Dashboard 1-page PDFs; module present in
  `.xlsm`. Macro execution blocked by host policy — not claimed.
- **Limits.** Hidden ≠ secure; merged cells layout-only; no UserForm/audit
  log/undo; form validation is type/list only.
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T048, round 2); awaiting owner merge.
- Report: `experiments/T048-20261101-opencode-workbook-ux/REPORT.md`.

## T047 [docx] Standards-controlled annual/ESG report — 2026-11-01

- **Standards profile.** `domains/docx/data/report_standard.json` declares ISO
  7144:1986 (structure), ISO 2145 (numbering), ISO 690:2021 (references), ISO
  80000-1/8601-1 (units/dates), WCAG 2.2, GRI 1/2/3/305, with 10 controls and
  evidence. The report prints the control matrix before the TOC.
- **Front matter order.** `front_matter.order: "iso7144"` renders abstract →
  preface → TOC → lists; references move after appendices and use an
  unnumbered Heading 1 so the running header still works.
- **Content depth.** 25 pages, 37 tables, 5 equations (2 numbered), 4 figures,
  10 material topics, 5 stakeholder groups, Scope 1/2/3, a 37-row GRI content
  index, data appendix, glossary and 11 references.
- **Cross-asset.** Camera illustration authored as SVG, rasterised by
  VectorCraft, trimmed/graded/composited by Pillow; revenue and emissions charts
  built by Chart Forge (SheetCraft), exported by Excel, embedded with source and
  alt text.
- **Parser.** `word_math` now accepts escaped punctuation and the LaTeX control
  space (`\%`, `\&`, `\ `), covered by tests.
- **Evidence.** Word opened the exact DOCX, refreshed fields and saved; 25-page
  PDF inspected; audit clean: 101 fields, 89 bookmarks, 37 tables, 4 figures,
  5 equations, `vi-VN`; full suite 395 tests OK.
- **Status.** EXPERIMENTAL; review accepted by Argon (approve T047, round 2); awaiting owner merge.
- Report: `experiments/T047-20261101-opencode-standards-report/REPORT.md`.

## T046 [xlsx] Advanced workbook and dashboard â€” 2026-11-01

- **Sheet Forge.** `scripts/sheet_forge.py` composes a 7-sheet programme
  workbook from a semantic spec: typed data table, cross-sheet model
  (`SUMIFS`/`COUNTIFS`/`AVERAGEIF`/`INDEX`+`MATCH`, named ranges), image table,
  native Gantt, relationship matrix, PivotTable and a designed dashboard.
- **Image table.** Pictures are inserted in cells with alt text and a fixed row
  height; the `Team` sheet prints A1:D7 on one page.
- **Gantt.** Stacked bar, transparent start series (`<a:noFill/>`),
  date-formatted value axis with explicit serial min/max (bar charts have no
  date category axis), reversed categories; inserted on the Gantt sheet and on
  the dashboard.
- **Relationship view.** Matrix heatmap with a 3-colour scale; the node-link
  scatter was tested and rejected (one series per edge does not scale, and the
  experimental build did not render every series consistently) and is recorded
  as a negative result.
- **Pivot.** Native PivotTable built by GridCraft `insert.pivotTable`; Excel
  reads `PivotTable1` over `Data!R1C1:R61C11`. Without GridCraft a `SUMIF`/
  `COUNTIF` summary is written to the `Pivot` sheet in the first pass.
- **VBA.** `scripts/vba_forge.py` writes a `DashboardTools` `.bas` (with a
  worksheet guard) and injects it into an `.xlsm` only when Excel trusts the
  VBA project object model.
- **Dashboard.** 4 formula-driven KPI cards, 2 fixed one-cell-anchored charts,
  matrix, one source note; print area 29.21 Ă— 20.39 cm (â‰ˆ93% A4), Excel export
  one page. Audit clean (3 charts, 0 errors/0 warnings/0 notes).
- **Evidence.** Excel opened the exact XLSX/XLSM, recalculated formulas, read
  the pivot and exported 5 sheets; `tests/test_sheet_craft_advanced.py` (5
  tests); full suite 385 tests OK with `PYTHONUTF8=1`.
- **Review fixes (Argon).** Gantt `Start` transparency + value-axis min/max/date
  format; re-apply axes after GridCraft's pivot round-trip; KPI formulas; pivot
  fallback on the Pivot sheet; VBA worksheet guard; dashboard/Gantt print areas
  reduced to ~93% A4; hidden-series/`gantt` audit detection; negative-result
  reasoning corrected. Argon **approve T046** (round 2).
- **Status.** EXPERIMENTAL; review accepted; awaiting owner merge.
- Report: `experiments/T046-20261101-opencode-advanced-xlsx/REPORT.md`.

## T045 [docx] Advanced report craft â€” side-by-side media, equations, rich tables â€” 2026-11-01

- **Native equations.** `scripts/word_math.py` parses a strict LaTeX subset into
  OMML (`m:oMath`): fractions, scripts, roots, sums/integrals, delimiters,
  accents, Greek letters and common operators. Unsupported constructs raise an
  explicit error. Equation numbering uses `SEQ Equation`.
- **Side-by-side media.** `figure_text` emits a borderless two-cell table with
  an inline picture and a text column, caption below; no floating anchors.
- **Rich tables.** `table.advanced` supports multiple header rows, `colspan`/
  `rowspan`, explicit merges, per-cell alignment/vertical alignment, fills,
  row heights, cell margins and image cells.
- **Callouts / KPI strip / cover hero.** Shaded single-cell callouts, a
  borderless label/value strip, and a full-text-width inline cover image.
- **Cross-craft.** Cover and icons are SVG rasterised by VectorCraft
  (`convert --scale 1`), then accepted by the DOCX audit/render.
- **Audit depth (review fix).** `audit_docx` counts equations/equation numbers,
  merged cells, images in cells and languages; validates `gridSpan` vs
  `tblGrid`, orphan `vMerge`, image width vs `tcW`, OMML empty/one-sided parts
  and alt text; `docDefaults` + styles carry `vi-VN`.
- **Evidence.** 11-page Word PDF inspected; audit clean (20 fields, 15
  bookmarks, 6 tables, 6 drawings, 2 equations/1 numbered, 5 merged cells,
  5 images in cells); `tests/test_document_advanced.py` (5 tests) + T039 tests;
  full suite 385 tests OK with `PYTHONUTF8=1`. Argon **approve T045** (round 2).
- **Status.** EXPERIMENTAL; review accepted; awaiting owner merge.
- Report: `experiments/T045-20261101-opencode-advanced-docx/REPORT.md`.

## T044 Multi-Asset Pipeline Protocol, User Experience Maximization & Local Autonomy Charter â€” 2026-11-01

- **Official Owner Mandate Codification (togcoder).** Integrated official directive on cross-domain agentic skill development:
  - Skills do not produce single isolated files; they orchestrate compound assets across multiple target applications.
  - Elevate user experience to the peak: deeply decode user intent to achieve first-pass satisfaction ("Ä‘Ăºng Ă½ ngay tá»« lÆ°á»£t Ä‘áº§u"), eliminating tedious regeneration.
  - Mandate cross-asset pre-processing pipelines: edit/crop/mask images before slide/doc embedding; normalize audio (EBU R128) before video muxing; validate structured data before chart rendering.
  - Authorize full local operational autonomy: agents working locally have complete freedom to download fonts, models, and install code libraries, provided workspaces remain tidy in git-ignored `workspace/` and transient files are deleted.
- **Protocol 04 Added (`lab/protocols/04_cross_asset_pipeline.md`):** Formally codified the 3 canonical pre-processing pipelines (Visual/Raster, Audio/Motion, Data/Chart), the First-Pass Excellence law, and the Local Autonomy & Cleanliness Law.
- **Core Governance Updates:**
  - `AGENTS.md`: Added First-Pass Intent Fulfillment, Cross-Asset Pre-processing Pipeline, and Local Autonomy & Cleanliness Law to Rules for Every Agent.
  - `lab/CHARTER.md`: Added Goals 4 & 5 (First-Pass Fulfillment, Cross-Asset Orchestration) and principles on pre-processing before embedding and local autonomy.
  - `lab/PROTOCOL.md`: Added cross-asset pipeline step and local resource freedom to the agent research lifecycle.
  - `README.md`: Upgraded the lab introduction to reflect the Cross-Domain Agentic AI Lab vision.
  - `domains/cross/DOMAIN.md`: Updated scope, code table, and rules with Protocol 04.
- **Cross-Pipeline Validator (`scripts/cross_pipeline.py`):**
  - `validate_image_for_embedding`: Verifies aspect ratios (16:9, 4:5, 1:1), minimum resolutions, alpha channels for art washes, and canvas mode luminance harmony.
  - `validate_audio_for_muxing`: Verifies EBU R128 loudness (-14.0 LUFS), True Peak safety ceiling (<= -1.0 dBTP), and BGM auto-ducking attenuation.
  - `validate_chart_data_for_presentation`: Verifies zero-error numerical integrity (no NaNs, nulls, division-by-zero) and Miller 7+-2 cognitive density.
- **Tests.** Added `tests/test_cross_pipeline.py` (5 unit tests). Full lab test suite passes **359 tests 100% (skipped=4)**; `lab/tools/check_layout.py` reports `layout OK`.

## T043 Dynamic Theme Engine: Need-Based Synthesizer, Reference Teardown, Composite Backgrounds & AI Image Harmonizer â€” 2026-11-01

- **Argon Strategic Consultation (game25072003 / yep).** In response to owner directive that themes are infinite and must be driven by user need and reference decks, collaborated with Gemini 4 Argon (`gemini-argon`) on `chat_id: 2:53675cab70c50cda` to formulate the Dynamic Theme Engine architecture:
  - Adversarial review rejected raw `<a:srgbClr>` counting in favor of Area-Weighted Clustering and `<a:schemeClr>` resolution.
  - Perceptual color math in pure Python (sRGB <-> Linear <-> OKLab <-> OKLCH, Relative Luminance Y, WCAG 2.1 contrast ratio).
- **Composite Background & Translucency Architecture (Addressing User Feedback):**
  - Addressed critical design reality: professional decks NEVER rely on flat single-color (`Ä‘Æ¡n sáº¯c`) fills.
  - Proved via Pillow alpha histogram on user's sample decks: `Webinar Keynote Presentation.pptx` media assets `image1.png` and `image6.png` feature 60.9% to 64.9% translucent pixels ($1 \le lpha \le 254$), overlaying a warm ecru canvas (`#F4F1E9`) to create soft organic pastel tone variations.
  - Proved shape alpha in `Blue Modern Business Pitch Deck Presentation.pptx`: explicit OOXML `<a:alpha val="36863"/>` (36.86% opacity) for frosted glass containers over a 2362x1575 composite image texture.
  - Integrated 4-layer Composite Background Recipe into `scripts/theme_engine.py`: Layer 0 Canvas Base Tone, Layer 1 Atmosphere/Translucent PNG Washes, Layer 2 Tint Washes/Glassmorphism Cards, Layer 3 Foreground Typography.
- **Core Engine Module (`scripts/theme_engine.py`):**
  - `PPTXThemeExtractor`: Reverse-engineers any PPTX reference file. Weighting: Backgrounds ($A = 	ext{slide\_area} 	imes 1.0$), Shapes ($A = 	ext{cx} 	imes 	ext{cy}$), Text ($W = 	ext{len} 	imes 	ext{size}^2 	imes 12700^2$), Full-slide background sampling via Pillow. Agglomerative clustering in OKLab ($\Delta E < 0.035$). Computes Salience Score for Accent: $	ext{Score} = C 	imes 2.5 + \Delta E 	imes 1.5 + \ln(1 + 	ext{ratio})$. Extracts typography hierarchy, detects mammoth Hero KPIs (e.g. 202pt), and geometric modular scale ($r = (S_{	ext{h1}} / S_{	ext{body}})^{1/3}$). Extracts `background_recipe` with translucency ratios and shape alphas.
  - `classify_canvas_mode`: Distinguishes `DARK_CANVAS` ($Y < 0.18$), `WARM_PAPER` ($0.72 \le Y \le 0.96, 0.010 \le C \le 0.060, 50^\circ \le H \le 110^\circ$), `LIGHT_CANVAS` ($Y \ge 0.72$), and `MID_TONE_CANVAS`.
  - `synthesize_theme_from_need`: Synthesizes complete ThemeSpecs from user topic/intent strings across 5 foundational archetypes (`INDUSTRIAL_QCC`, `TECH_PITCH_DARK`, `EDITORIAL_WARM_KEYNOTE`, `EXECUTIVE_STRATEGY`, `SUSTAINABLE_BIO`). Supports Dynamic Hue Override (rotates Hue in OKLCH while strictly preserving Lightness and Chroma) and assigns layered background recipes.
  - `build_harmonized_image_prompt`: Prompt builder guaranteeing visual harmony between generated AI images and the slide theme (6500K cool studio for Dark Canvas, 3800K soft morning window light for Warm Paper, 5500K high-key for Light Canvas). Slot framing: 16:9 hero full-bleed (60% negative space for typography), 16:9 atmospheric backdrop texture, 4:5 split/angled mask, 1:1 isolated translucent art wash on white background for alpha-mask conversion, 1:1 isometric bento.
- **Tests.** Added `tests/test_theme_engine.py` (14 unit tests). Verified native teardown of user's `Blue Modern Business Pitch Deck` (`DARK_CANVAS`, `#01152B`, `Aileron`, 202pt KPI, 36.86% shape alpha) and `Webinar Keynote Presentation` (`WARM_PAPER`, `#F4F1E9`, `TT Commons Pro` + `TAN Mon Cheri`, pastel accents, >60% translucent PNG overlays). Full suite passes **354 tests 100% (skipped=4)**; `lab/tools/check_layout.py` reports `layout OK`.

## T042 Multi-Domain Design Canons: Video, Vector/SVG, 3D/Solid, CAD & Audio â€” 2026-11-01

- **Argon Multi-Domain Consultation.** Partnered with Gemini 4 Argon (\gemini-argon\) to establish mathematical formulas, geometric tokens, and handoff contracts across all specialized ArtCraft domains (\D:\\artcraft\).
- **5 Formal Domain Canons (\knowledge/\):**
  - \knowledge/video_canon.json\: SMPTE RP 2046-2 / EBU R95 safe areas (Action Safe 3.5%, Title Safe 5.0%), 9:16 vertical dead zones (top 220px, bottom 440px, right action rail), ASL shot duration, J-cut (12-24 frames lead) and L-cut (15-30 frames trail) asynchrony, and EBU R128 audio mastering (-14.0 LUFS, True Peak <= -1.0 dBTP, sidechain ducking -14 dB).
  - \knowledge/vector_canon.json\: W3C SVG 2.0, 24x24 icon grid (20x20 live area), optical trim boxes (Circle d=20, Square 18x18, Landscape 20x16, Portrait 16x20), non-linear stroke scaling formula W(S) = W0 * (S/S0)^0.75, and Bezier 90-degree circle handle ratio kappa ~ 0.55228.
  - \knowledge/3d_solid_canon.json\: Metric scale (1 unit = 1.0 mm, Y-up glTF), No-Sharp-Edge Law (micro-bevel R = 0.005 * min(W,H,D) bounded in [0.2, 0.5] mm), concentric fillets, True Isometric camera (45-deg azimuth, elevation arctan(1/sqrt(2)) ~ 35.264-deg), 3-point studio lighting (Key 1.0, Fill 2:1/4:1, Rim 1.0), and PBR material albedo clamp with strict prohibition on ambiguous metalness M in [0.2, 0.8].
  - \knowledge/cad_iso_canon.json\: ISO 5457 sheet dimensions (A4 to A0) with 20.0mm left margin, ISO 128 line weight hierarchy (0.50mm group: 0.50, 0.25, 0.18mm), ISO 129 dimensioning geometry (10mm 1st tier, 7mm 2nd tier, 1.0mm origin offset, 2.0mm overshoot, 3:1 closed filled arrows), and ISO 7200 title block (180.0mm width).
  - \knowledge/sound_canon.json\: SoundCraft mastering targets (EBU R128, ITU BS.1770-4, 48kHz 24-bit PCM, stem dynamic ranges, auto-ducking attack/hold/release envelopes).
- **Multi-Domain Evaluator & Calculators (\scripts/multi_domain_canons.py\).** Implemented pure Python token accessors, geometric calculators, and pre-flight validation rules for all 5 domains.
- **4 Native ArtCraft Bridges (\scripts/\):**
  - \scripts/filmcraft_bridge.py\: Headless runner for \FilmCraft\\filmcraft-cli.exe\ (probe, render frame, export, inspect).
  - \scripts/solidcraft_bridge.py\: Headless runner for \SolidCraft\\solidcraft-cli.exe\ (eval, snapshot, render, icon export).
  - \scripts/cadcraft_bridge.py\: Headless runner for \CADCraft\\cadcraft-cli.exe\ (info, convert DXF/DWG/SVG/PNG/PDF, sample generator).
  - \scripts/soundcraft_bridge.py\: Headless runner for \SoundCraft\\soundcraft-cli.exe\ (info, convert, normalize, resample).
- **Domain Cards Registered (\domains/\):** Created \domains/video/DOMAIN.md\, \domains/3d/DOMAIN.md\, \domains/cad/DOMAIN.md\; updated \domains/svg/DOMAIN.md\ and \domains/README.md\.
- **Verification Evidence Artifacts (\experiments/T042-20261101-antigravity-multi-domain-canons/artifacts/\):**
  - \cad_sample_bracket.svg\ (99 KB) & \cad_sample_bracket.png\ (115 KB) via \cadcraft-cli.exe sample\.
  - \solidcraft_icon.png\ (21 KB) via \solidcraft-cli.exe icon\.
- **Tests.** Added \	ests/test_multi_domain_canons.py\ (24 unit tests). All **340 tests pass 100% (skipped=4)**; \lab/tools/check_layout.py\ reports \layout OK\.

## T041 [xlsx] SheetCraft â€” controlled standard DrawingML charts â€” 2026-11-01

- **Chart Forge.** `scripts/chart_forge.py` builds a workbook/chart from
  `domains/xlsx/schemas/chart_spec.schema.json`: column/bar, line, area, pie,
  doughnut, scatter, bubble, radar, stock and combo; axes, labels, legend,
  markers, trendlines, number formats and print area.
- **Chart patch.** `scripts/chart_patch.py` edits existing chart OOXML:
  title/legend/axes/bar gap/data labels/series style/manual plot layout and
  converts `xdr:twoCellAnchor` to a fixed `xdr:oneCellAnchor`.
- **Chart audit.** `scripts/chart_audit.py` measures geometry, zero baseline,
  log scaling, category density, labels, legend, contrast/deuteranopia, pie
  slices, 3-D, fonts, series count, print area, alt text and the chart cache.
- **Evidence.** Three synthetic fixtures (combo secondary axis, doughnut,
  scatter + trendline) pass the audit with no errors/warnings; Excel opened the
  exact files and exported the charts; GridCraft PDF rendered them but dropped
  Vietnamese diacritics. Waterfall/treemap/histogram/box/funnel remain raw-OOXML
  recipes, not generated.
- **Review fixes (Argon).** Combo series/axis mapping, manualLayout/`a:ln` child
  order, print-area geometry, full cache comparison with worksheet fallback,
  Excel-first `--render`, and `gridcraft_bridge` use instead of a hard-coded
  `D:\artcraft` path.
- **Tests.** `tests/test_sheet_craft.py` (10 tests) covers build/audit, combo
  second-series patch, per-axis max, print-area rejection, stale cache,
  manualLayout order, small chart, doughnut palette and schema. Full suite:
  326 tests OK with `PYTHONUTF8=1`.
- **Status.** EXPERIMENTAL; review requested. One task = one domain; the
  document half is T039 [docx].
- Report: `experiments/T041-20261101-opencode-sheet-craft/REPORT.md`.

## T039 [docx] DocumentCraft â€” professional Word canon and real fields â€” 2026-11-01

- **Standards research.** Mapped the binding hierarchy (law/contract/template â†’
  ISO 7144/2145/690/7200/8601/80000 â†’ institutional rules), marked ISO 5966 as
  withdrawn, and recorded the sources/statuses in
  `domains/docx/data/document_system.json`.
- **Document Forge.** `scripts/document_forge.py` builds a DOCX from
  `domains/docx/schemas/document_spec.schema.json`: cover, unnumbered front
  matter, linked multilevel headings, `TOC` field, standard `TOC \c` lists of
  figures/tables updated through `TablesOfFigures`, `SEQ` captions,
  `STYLEREF`/`SECTIONPAGES` headers/footers, inline images with alt text, fixed
  table grids with repeating headers, references and appendix A/A.1.
- **Word field kit.** `scripts/word_field_kit.py` writes/audits fields,
  bookmarks and captions; `scripts/document_audit.py` is the standalone audit.
- **Evidence.** Structural audit clean (29 fields, 22 bookmarks, 3 tables, 2
  figures, no errors/warnings); Word refreshed the exact file (including
  `TablesOfFigures`) and exported a 12-page PDF; pages inspected. WordCraft was
  a fallback (physical TOC page numbers, dropped `descr`, Vietnamese PDF font
  clipping). No PDF/UA, PDF/A or human edit/print yet.
- **Tests.** `tests/test_document_craft.py` (6 tests) covers fields/bookmarks,
  broken targets, broken bookmarkEnd, table width, en-US language and optional
  WordCraft refresh. Full suite: 322 tests OK with `PYTHONUTF8=1`.
- **Review fixes (Argon).** Standard `TOC \c` lists updated via
  `TablesOfFigures`; bookmarkEnd balance and per-section width checks; spec
  language instead of hard-coded `vi-VN`; `SECTIONPAGES` for the restarted body.
- **Status.** EXPERIMENTAL; review requested. One task = one domain; the
  spreadsheet half is T041 [xlsx].
- Report: `experiments/T039-20261101-opencode-office-canon/REPORT.md`.

## T040 multi-domain lab restructure â€” 2026-11-01

The repository is now organised as a multi-domain design lab:

- `lab/` holds the charter, the agent protocol, and the research, review,
  merge and outputs standards. The shared protocols, schemas, registry and
  templates moved there.
- `domains/` has a card per domain (pptx, docx, xlsx, svg, cross), each with
  its own thesis, canon, code status and evidence ladder.
- `research/reviews/` holds peer critiques.
- `workspace/` is for scratch and is git-ignored. `output/` is frozen.
- `lab/tools/check_layout.py` and its test keep outputs out of the root.
- `AGENTS.md` and `HANDOFF.md` were rewritten lab-wide.

No design research was done. Report:
experiments/T040-20261101-claude-lab-restructure/REPORT.md.

## T038 PPTX Design Canon Tokens, Asymmetric & Bento Grids, Optical Balance & Critic Rules â€” 2026-11-01

- **Argon Dissection & Design Canon Foundations.** Partnered with Gemini 4 Argon (`gemini-argon`) to dissect and codify high-craft mathematical formulas into `knowledge/design_system.json` (v1.1.0):
  - *Deck Chrome Bounds:* Slide $960 \times 540\text{ pt}$, safe margins $48/36\text{ pt}$, logo watermark ($w \le 72, h \le 24$, $y=20\text{ pt}$ top-right, suppressed on cover/divider/closing/break slides), section breadcrumbs ($10\text{ pt}$ uppercase tracked font), and progress tracker ($y=537, h=3\text{ pt}$ along bottom edge).
  - *Optical Icon Balance:* Equalizes perceived mass across geometric shapes (Square $0.88\times$, Circle $1.0\times$, Wide $1.08\times/0.82\times$, Triangle $1.05\times$ with $+0.06\times$ apex upward shift, Badge $2.0\times$).
  - *3-Layer Background Depth:* Z0 Base Canvas (135Â° Deep Slate `#0B0F19` $\rightarrow$ `#111827` or Light Alabaster `#F8FAFC` $\rightarrow$ `#EDF2F7`), Z1 Ambient Radial Glow Orbs (blurred $120-160\text{ pt}$, opacity $0.12-0.18$, morph-linked via `!!` prefix), Z2 Surface Cards (glassmorphism opacity $65-75\%$, top-lit border, corner radius $8-12\text{ pt}$, inner padding $20-28\text{ pt}$).
  - *Content Layout Canons:* Symmetric grids (2-col $422\text{ pt}$, 3-col $274\text{ pt}$, 4-col $204\text{ pt}$), Asymmetric Golden Ratio (Major $522\text{ pt}$ / $61.8\%$, Minor $322\text{ pt}$ / $38.2\%$), and Bento Grid (Hero $496 \times 396\text{ pt}$ [7/12 width], Top-Right $348 \times 188\text{ pt}$, and 2 Bottom-Right split cards $164 \times 188\text{ pt}$).
  - *Nancy Duarte Pattern Breaks:* Automatic pacing triggers for decks of $\ge 5$ slides near $1/3$ and $2/3$ milestones ($\ge 70\%$ negative space, single bold statement $36-44\text{ pt}$ or mammoth KPI $72-96\text{ pt}$, chrome suppressed) to eliminate cognitive fatigue.
  - *Color & Typography:* 60-30-10 surface area bounds, Modular Scale token table (caption $11\text{ pt}$, body_base $14\text{ pt}$, card_title $18\text{ pt}$, slide_title $28\text{ pt}$, hero $44\text{ pt}$, kpi_stat $72\text{ pt}$).
- **Programmatic Helpers (`scripts/design_system.py`).** Added `chrome()`, `optical_icon_compensation()`, `bento_grid_layout()`, `asymmetric_golden_layout()`, `duarte_break_positions()`, `modular_scale()`, and `background_layers()`.
- **Slide Forge Compilation (`scripts/slide_forge.py`).** Added `asymmetric`, `bento`, and `duarte_break` layout compilers, automatic deck chrome injection, and optical icon balancing.
- **Design Critic Rules (`scripts/design_critic.py`).** Implemented and registered `CHROME-SAFE`, `OPT-ICON`, `LAY-BENTO`, and `DUA-BREAK` rules; returns detailed `evaluations` audit log.
- **Tests.** Added `tests/test_pptx_design_canon.py` (12 unit tests). Total project test suite expanded to **318 tests, 100% passing (0 failures, 4 skipped)** in 14.90s.

## T037 Multi-Craft Native Bridges & Intent-Empathy Decoder â€” 2026-11-01

- **Multi-Craft Bridges.** Built `scripts/wordcraft_bridge.py`, `scripts/gridcraft_bridge.py`,
  and `scripts/vectorcraft_bridge.py`. Connects natively to `wordcraft-cli.exe`, `gridcraft-cli.exe`,
  and `vectorcraft-cli.exe` in `D:\artcraft`. Provides headless document/sheet/vector inspection,
  page rendering, formula evaluation, and cross-format conversion.
- **Intent & Empathy Decoder Engine (`scripts/intent_decoder.py`).** Implemented Protocol 00:
  parses raw prompts into 5-dimensional `IntentBrief` documents matching `schemas/intent_brief.schema.json`
  (Audience Persona, Cognitive Budget, Viewing Context, Canonical System, Craft Routing).
- **Tests.** Added `tests/test_craft_bridges.py` and `tests/test_intent_decoder.py`. Test suite
  expanded from 296 to **302 tests, all passing (0 failures, 4 skipped)** in 8.69s.

## T036 Universal ArtCraft Hub, Multi-Agent Protocols & Intent Schemas â€” 2026-11-01

- **Argon Architecture Consultation.** Consulted Gemini 4 Argon (`gemini-argon`) on multi-agent
  governance, identifying 4 architectural traps: unbounded mesh chat (solved by DAG contracts),
  LLM python bias (solved by 3-tier capability escalation gate), blind code review (solved by
  render-before-review), and lack of empathy (solved by 5-dimensional intent briefs).
- **Universal ArtCraft Discovery & Hub.** Built `scripts/sync_artcraft_capabilities.py` and
  `scripts/artcraft_hub.py`. Automatically catalogs all 13 tools in `D:\artcraft`, generates
  `registry/artcraft_capabilities.json` (hash `21eaaf51d6891acf`) and `registry/capability_gaps_backlog.md`.
- **Human Intent & Empathy Schema.** Created `schemas/intent_brief.schema.json` modeling 5 dimensions:
  Audience Persona, Cognitive Budget (Miller/Hick, Z/F pattern), Viewing Context, Canonical System
  (Swiss Grid, Dieter Rams, Tufte, IBM Carbon, Material 3), and Craft Routing.
- **Cross-Delegation & Critique Contracts.** Created `schemas/handoff_contract.schema.json`
  (enforcing max 2 iteration loops) and `schemas/critique_report.schema.json` (100-point dual-layer audit).
- **Foundation Protocols.** Established `protocols/00_intent_empathy_decoder.md`, `01_capability_first_gate.md`,
  `02_cross_delegation_dag.md`, and `03_redteam_critique_rubric.md`.
- **Validation & Tests.** Created `scripts/validate_handoff.py` and `tests/test_artcraft_hub.py`.
  Test suite expanded from 292 to **296 tests, all passing (0 failures, 4 skipped)** in 8.64s.

## T035 DeckCraft native bridge + Skill-for-Design evolution â€” 2026-10-31

- **Native rendering bridge (`scripts/deckcraft_bridge.py`).** Discovers `deckcraft-cli.exe`
  from the ArtCraft suite (`D:\artcraft\DeckCraft`). Headlessly renders slides to Full HD
  (1920x1080) PNGs in < 1s, inspects presentation JSON, and converts formats without
  requiring Microsoft Office or LibreOffice.
- **Critic integration.** `scripts/design_critic.py` now supports `--render deckcraft` (or `--render dc`),
  enabling instantaneous offline visual metrics extraction (background share, balance offset,
  colourfulness). Tested on `report_deck_motion.pptx` in 2.1s with 100% success.
- **Tests.** Added `tests/test_deckcraft_bridge.py`. Test suite expanded from 289 to 292 tests,
  all passing (0 failures, 4 skipped).
- **Skill-for-Design roadmap.** Established the architectural blueprint to evolve `skill-for-pptx`
  into the comprehensive Skill for Design suite with PPTX as pioneer.

## T034 design system + documentation standardised â€” 2026-10-19

Beauty and technique now share one source,
`knowledge/design_system.json` (see `docs/DESIGN_SYSTEM.md`):

- **Shared numbers.** Duration bands per role, easing roles fitted to
  PowerPoint, stagger, overshoot, rhythm limits, WCAG contrast, type scale,
  density and layout, with 18 rules and their evidence.
- **Generators read it.** Arrivals ease in, and the assemble regression from
  the Argon merge is undone. Overshoot is clamped. Travel time scales with
  distance. The default path easing is no longer 50/50. The simulator uses
  PowerPoint's accel/decel curve. Helpers take a deck colour that reaches
  3:1 against the background. The highlighter tint keeps text contrast. One
  contrast function, with WCAG large text at 18 pt.
- **Checkers grade against it.** These are the validator, `forge_qa` and the
  new `scripts/design_critic.py`. The critic resolves inherited sizes and
  colours, alpha tints and gesture segments, measures settled frames
  (LibreOffice or PowerPoint) and checks the schema. `forge_critique.py`
  (T031) now delegates to it.
- **Wiring.** Director reports, Forge verdicts and Morph Studio reports
  include the critique.
- **Evidence.** In a before/after run (36 director runs, one critic),
  generator-controlled warnings fell from 14 to 6. The invisible helpers on
  brand themes (1.14:1) became 5.33:1. LibreOffice frame metrics match
  PowerPoint's (background share: median difference 0.022, Spearman 0.99).
- **Quarantine.** The T033 modules are labelled experimental and kept out of
  product paths.
- **Documentation.** Documents were reorganised: STATUS (current state),
  CHANGELOG (this log), VERIFICATION, DESIGN_SYSTEM, ARCHITECTURE and the
  task registry. Superseded documents moved to `docs/archive/`.

289 tests pass. Report:
experiments/T034-20261019-claude-design-system/REPORT.md.

## T033 Argon second drop: morph twins, triggers, pacing â€” 2026-10-16

The owner integrated three Argon answers:

- `morph_playbook.py`: `!!` twin staging, extract_objects, homotopy;
- `interactive_triggers.py`;
- `cognitive_pacing.py`.

No report was written at the time. The T034 audit found that none of them is
wired into a product path, and that each one writes schema-invalid or wrong
XML on real decks. All three are quarantined as experimental. Report
(written in T034): experiments/T033-20261016-argon-research/REPORT.md.

## T031 measurable critique (WIP) â€” 2026-10-08

`scripts/forge_critique.py` scored PPTEval-style dimensions (content, design,
coherence) plus motion from measurements. It was a single WIP commit with no
tests or wiring and no report. T034 folded its checks into `design_critic.py`.

## T032 Argon (Gemini) research drop evaluated and integrated â€” 2026-10-15

Argon worked offline on the old main and reused ID T024. Its drop is preserved
verbatim on `import/argon-t024-20261014` and merged here. **Adopted:**

- virtual rigging with follow-through;
- the orbit, orbit-3d, wave, explode-layers and cascade-flow recipes;
- poly-segment paths;
- auto-arc collision avoidance;
- bounceEnd;
- shape-click triggers;
- two engine bug fixes;
- the Pillow-only preview fallback.

**Corrected:** `color` (wrote Change Line Color, now Change Fill Color) and
`teeter` (wrote Blast, now PowerPoint's Teeter). Its loop keys are normalised
into `loop:{}`.

**Quarantined:** the import-breaking "PHASE 2-4" block, now in
`scripts/morph_playbook.py`, experimental. 265 tests pass, 48/48 decks apply,
and PowerPoint 16.0 renders the 3D carousel and the cascade.
Report: experiments/T032-20261015-claude-argon-integration/REPORT.md.

## T030 brand palette from one colour + highlight fix â€” 2026-10-08

`scripts/brand_palette.py` builds a whole Forge theme from one brand colour
(`"theme": {"seed": "#DA251D", "mode": "light|dark", "harmony": 150}`). It
works in OKLCH (Ottosson) and picks colours by contrast target, the way Adobe
Leonardo does. The brand hue is kept, and its lightness moves only as far as
WCAG AA requires; the raw colour still paints the decoration. A test holds 47
seeds Ă— 2 modes to AA on bg and surface.

The PowerPoint render of a Vietnamese brand deck showed the T028 highlight
marker above a centred, wrapped takeaway. The marker now uses the
anchor-aware `text_block` and covers wrapped blocks; a regression test was
added and the re-render was checked. 256 tests pass.

## T029 motion tokens â€” 2026-10-08

Carbon and Material 3 easing curves (Apache-2.0) are fitted to PowerPoint's
accel/decel. Carbon fits within 1.5â€“8%; Material's emphasized curves are
18â€“44% off with one behaviour.

The keyframe default moves from the symmetric 0.5/0.5 to Carbon standard
(0.15/0.70). Assemble and rise now enter with a deceleration, and disperse
exits with an acceleration. PowerPoint 16.0 parsed all 122 effects of a
cinematic showcase deck. 251 tests pass. See `knowledge/README.md`.

## Integration 2026-10-08 â€” both lines merged

Two sessions worked in parallel, and both used the ID **T024**. Experiment
folders keep their names:

- `T024-20261005-claude-layers-script` (cloud): motion layers and the script layer.
- `T024-20261007-claude-picture-motion` (desktop): Ken Burns and the accent intro.

Use T029+ for new work. Loops are unified on the cloud representation
`loop: {repeat, auto_reverse}`. The desktop `float` recipe is now an alias of
`drift` straight up. Recipes `ken-burns`, `ppt:<name>` effects, Slide Forge,
assets and the knowledge base sit next to Morph Studio, the script layer and
layers. Natively verified so far: PowerPoint CreateVideo renders (T024
picture, T025, T027) and EffectType recognition of library presets. The
cloud work (T024 layers, T028) has simulated previews only.

## T028 Morph Studio + professional text tricks â€” 2026-10-08

Goal: the polish seen in motion-design tutorials. `scripts/morph_studio.py`
adds cross-slide Morph to a directed deck. **Continuity** pairs titles,
identical pictures and text, and existing names via `!!`, and renames along
the whole chain. It stages new and leaving objects off-slide so they fly;
contained objects travel with their card. **Scenes** each need a reason and
start from the source's end state: `camera-zoom` (push-in and pull-back, type
scaled like a lens), `card-expand` (over its neighbours, even margins) and
`pan`. `verify_scenes` keeps originals intact (only `!!` renames and
off-slide copies). The `unsettled` check lists slides whose animation ends
away from the authored layout before a Morph. The script layer adds a closing
release click when a script stops mid-tour.

Text tricks: `type-on` and `by: word/letter` (`p:iterate`), `rise` from an
invisible line (the mask sits under the last estimated text line, in the
container or background colour, and is refused if it would cover anything),
`highlight` and `underline` sweeps (added by cinematic). The catalog
`skills/pptx-motion-director/references/pro-techniques.md` lists 50
techniques with when and how.

Evidence: report deck (7â†’8 slides) and showcase deck (8â†’10 slides) with
simulated previews. LibreOffice reads every Morph slide's fallback as Fade.
Five defects were found by looking at the previews and fixed with tests.
Smoke test: 34/34 repository decks pass
propose â†’ apply with every suggestion accepted. **219 tests pass.** PowerPoint playback is pending; the native gate is in
T020 Â§A.

Report: experiments/T028-20261008-claude-morph-studio/REPORT.md.

## T027 design + complex-motion knowledge â€” 2026-10-07

- PowerPoint authored all 198 built-in effects. They are now writable as
  `ppt:<name>` (verified 7/7 by native EffectType).
- 11 Microsoft designer themes became Forge `office:<Name>` themes, AA in light and dark.
- 797 licensed Zenodo10K decks were scanned XML-only over HTTP Range. 93% of
  real effects are entrances, and complexity lives in object lifecycles.
- New `dynamic` motion style. See `knowledge/README.md` and
  experiments/T027-20261007-claude-design-motion-corpus/REPORT.md.

## T026 Forge online assets â€” 2026-10-07

Forge now finds licensed photos (Openverse CC0/BY/BY-SA, or Pexels with a
key) and open-source icons (Iconify: Lucide/Tabler/Phosphor) by itself.
Contact sheets let the agent pick photos by eye. Icons are inserted as native
SVG. Attribution goes on an automatic credits slide, in the notes and in the
verdict. Example deck rendered by PowerPoint 16.0.
Report: experiments/T026-20261007-claude-forge-assets/REPORT.md.

## T025 Slide Forge â€” agent-facing deck compiler â€” 2026-10-07

New product path for *new* decks: `scripts/slide_forge.py` (schema â†’ build â†’
qa â†’ render). An agent writes a semantic spec with 12 layouts. Forge handles
layout, measured type, art, Director motion (KPI count-up, chart builds,
process, cycle tour, Ken Burns, accent draw-ins, Morph orbs) and coded QA.
Two example decks (EN and VI) pass QA and were rendered by PowerPoint 16.0.
The renders found wrap and mid-word-break defects that QA now catches.
Skill: `skills/slide-forge/SKILL.md`; command `/forge-deck`.
Report: experiments/T025-20261007-claude-slide-forge/REPORT.md.

## T024 picture motion + motion-graphic intro â€” 2026-10-07

Prompt-made decks animated only their text: the draft heuristic skipped small
pictures, kept single-picture and title slides static, and gave other pictures
a one-off entrance. Now large pictures get `ken-burns` (slow Grow/Shrink +
drift; on slide start for backdrops and picture-only slides, after the reveal
for content pictures), thin accent bars/lines draw in at slide start, and a new
`float` recipe loops until the slide ends (`repeatCount`/`autoRev` support in
the writer, reader and simulator). Morph-carried pictures stay still.
**202 tests pass.** First native evidence in this repo: PowerPoint 16.0 parsed
the effects and its own `CreateVideo` render shows the picture push-in and the
loop (pixel-measured). Interactive click playback is still pending.

Report: experiments/T024-20261007-claude-picture-motion/REPORT.md.
## T024 motion layers + script layer â€” 2026-10-05

Motion now has three layers. **Primary** is the meaning. **Secondary** covers
a halo following each spotlight, a rail plus progress token under walked
processes, an orbit ring behind cycles, ripple, overshoot/anticipate, and
labels that follow their shapes (`attach`). **Ambient** covers native loops:
breathe, drift and spin-loop, repeating indefinitely or until the next click.
Helper shapes come from `scripts/motion_components.py` in the deck's accent and
font. The draft reuses the deck's own token when one exists. Director v0.7 adds
`layer` and `components[].generate`.

Script layer (`scripts/motion_script.py`): the script says *when*, the
director's choreography says *how*. It covers a provided script, notes, or a
generated full script (`motion_script.py draft`). First mention reveals, a
later mention focuses, a line that names nothing new releases a tour, and
paraphrased cued lines take the next resource in order. Gaps are reported and
`--fill-gaps` turns them into callouts. Every run writes `OUT.script.md`;
`--write-notes` puts the narration in speaker notes. Verified on an English
human-style script and a Vietnamese paraphrase.

**205 tests pass.** Smoke test passes on all repository decks. Native playback
is pending.

Report: experiments/T024-20261005-claude-layers-script/REPORT.md.
## Argon (Gemini) "T024" virtual rigging, poly-segment paths, auto-arc collision solver & interactiveSeq â€” 2026-10-14

Resolved the three compound-motion limitations identified in T023 and incorporated architectural lessons from an open-source review (`hugohe3/ppt-master`, `JimLiu/baoyu-design`, `scanny/python-pptx#942`, and the Open XML SDK SMIL specification):

1. **Group-aware virtual rigging (`detect_virtual_rigs`, `expand_rig_tracks` in `scripts/motion_engine.py`)**: shapes with separate floating text labels or badges sitting inside them now automatically carry those followers along in geometric lockstep (position, scale, rotation, opacity, visibility) without mutating `<p:spTree>`. `scripts/motion_director.py` (`_radial_group`) now detects and animates cycle/hub diagrams with separate text labels instead of rejecting them.
2. **Mid-flight trajectory collision detection & auto-arc avoidance (`transient_warnings`, `resolve_trajectory_collisions`)**: samples intermediate instants `(0.2, 0.35, 0.5, 0.65, 0.8)` of each click group to flag mid-motion collisions/occlusions, and automatically bends straight trajectories into obstacle-clearing cubic Bezier arcs when `auto_avoid=True`.
3. **Poly-segment motion paths (`poly_path=True`, `via=True`) & new recipes (`orbit`, `wave`)**: compiles multi-waypoint curves and 360-degree 4-quadrant orbits into a single `<p:animMotion>` element (`M ... C ... C ... E`), eliminating multi-stage path handoff seams.
4. **Canonical writer extensions (`scripts/pptx_animator.py`)**: added native `color` (`p:animClr`), `teeter` (`p:animRot`), `repeat` (`repeatCount`), `auto_reverse` (`autoRev`), `bounce_end` (`p14:bounceEnd`), shape-triggered `interactiveSeq` (`trigger_shape` / `trigger_spid`), and `empty_placeholders()` inspection/stripping for Morph transitions.
5. **Cross-platform resilience (`scripts/check_environment.py`, `scripts/motion_preview.py`)**: fixed `PermissionError` when probing `/root/.codex/...` as a non-root user and added a pure-Python `Pillow` fallback for animated GIFs and storyboard contact sheets when ImageMagick (`convert`/`montage`) is absent.

**198/198 tests pass (0 skipped).** `render_identity.py` confirms 4/4 slides RGB-identical on the T024 showcase; `lo_timing_crosscheck.py` confirms LibreOffice imports all new effects cleanly. Native PowerPoint playback remains pending: play `experiments/T024-20261014-gemini-complex-motion-rigging/output/T024_complex_motion_directed.pptx` against `preview/slide-0N.png`.

Report: `experiments/T024-20261014-gemini-complex-motion-rigging/REPORT.md`.

## T023 compound motion engine â€” 2026-10-05

Existing decks can now receive compound choreography, not only builds.
`scripts/motion_engine.py` compiles keyframe tracks and recipes (assemble,
disperse, spotlight, release, cycle, swap, travel, zoom-focus, raw tracks) into
native motion paths, Grow/Shrink, Spin, Transparency and entrance/exit effects
with exact delays. Position, scale, rotation, opacity and visibility carry
across clicks. Director v0.6 adds `choreography` beats and Morph `transitions`.

The draft detects cycle/hub diagrams (assemble, then a spotlight tour, then
release) and Morph continuity (a shared picture or text that moves). It keeps
continuing objects static. `preview` renders a simulated GIF plus a key-state
sheet of any slide (reading the timing XML back). `verify` rejects overlapping
moves of one object and warns about new occlusion or off-slide states. Those
warnings caught two real mistakes in the hand-directed showcase.

LibreOffice recognises the new motion-path, grow-and-shrink, transparency and
exit effects. Smoke test: `auto` on 27 repository decks passes, after fixing a
crash on fully animated decks and 88 bogus re-entries on Morph-state decks.
**190 tests pass.** Native playback is pending: play
`experiments/T023-20261005-claude-compound-motion/output/T023_showcase_directed.pptx`
against its preview sheets.

Report: experiments/T023-20261005-claude-compound-motion/REPORT.md.

## T022 T009 recompile + text-box deck direction â€” 2026-10-05

Continued Codex's T009 arm C (PR #22, which its review held back from merging).
The plan, unchanged, was recompiled through T019 on a timing-stripped
reconstruction (0 inventory differences over 31 shapes). In LibreOffice's
reading, the T009 candidate has 21 effects with 0 presets and all stages at
0s; R1 has 21/21 presets, with staged reveals at 0s/0.32s. A paragraph-click
variant (R2, 19 clicks) separates claims from rebuttals without content edits.

The T019 autonomous draft failed on this text-box-only deck: 40 clicks
(titles animated, wrapped titles split, labels separated). Implicit-title,
title-zone and label-body pairing rules bring it to 18 clicks. That matches
Codex's grouping on slides 2 and 10 and differs only by keeping slide 1 static.

`scripts/render_identity.py` compares renders in RGB. A negative control shows
the T009 RGBA `getbbox()` method misses real changes. R1, R2 and auto2 render
10/10 identical. **176 tests pass.** Native playback is still pending: play the
two PPTX files in `experiments/T022-20261005-claude-t009-recompile/output/`.

Report: experiments/T022-20261005-claude-t009-recompile/REPORT.md.

## T019 canonical timing + one-command Motion Director â€” 2026-10-05

Product path now exists end to end: `scripts/motion_director.py`
`inspect â†’ draft â†’ apply â†’ storyboard/verify`, packaged as skill
`skills/pptx-motion-director/` and Claude Code plugin (`.claude-plugin/`,
`/animate-deck`). Input can be only a PPTX + vague goal.

Found and fixed a writer defect: patch v0.2â€“v0.5 put all stages of a click in
one `p:par` at delay 0, so `after-previous` ran concurrently, and entrances had
no `set style.visibility`. LibreOffice's importer reads the old H001 tree as
three effects at 0s with no preset; the new `scripts/pptx_animator.py` tree as
0s/0.32s/0.64s Float/Fade entrances. Existing timing is now extended (appended,
original nodes byte-equal) instead of rejected.

Synthetic real-world fixture `tests/fixtures/report_deck.pptx` (placeholders,
bullets, KPI cards, chart, process, picture, group, notes, PowerPoint-authored
animation): autonomous draft gives 4/3/2/5/3 clicks on slides 2/3/4/5/7, keeps
title and existing-animation slides untouched; preservation checks pass.
**167 tests pass.** PowerPoint playback still pending â€” play
`experiments/T019-20261005-claude-motion-director/report_deck_motion.pptx`.

Report: experiments/T019-20261005-claude-motion-director/REPORT.md.
Next task: research/tasks/T020-motion-director-continuation.md.

## T018 native QA evidence integrity â€” 2026-10-05

Reviewed the unfinished T018 harness from a00ea03 on a separate branch (PR #21).
Frozen synthetic evidence cases found 18 false click passes and one crash in
26 cases. The corrected verifier gives 26/26 expected decisions, zero false
passes and zero crashes. **150 tests pass**, plus Python compile and PowerShell
syntax parse in GitHub Actions run 37248823323.

Exact-artifact manifest, Windows COM probe, composite fixture builder and manual
workflow are now documented in docs/POWERPOINT_NATIVE_HARNESS.md. No native
workflow was dispatched and no new PPTX artifact was delivered in this study.
Raw probe results are provisional; matching click indices do not prove animation
completion. Native playback and visual-state claims remain false.

Next: run the four frozen T006 hashes on an actual Windows PowerPoint desktop,
then chart/KPI/focus capture. Do not repeat the matrix or expand effects to avoid
the native gate. Report: experiments/T018-20261005-qa-evidence-review/REPORT.md.

## T017 generic report motion â€” 2026-10-05

Generic existing-deck semantics now bridge to native timing for reveal, staggered
reveal, process reveal, focus/emphasis, explicit move and explicit rotate.

Director v0.4 + `scripts/compile_director_patch.py` expand one semantic beat to
multiple automatic stages while preserving click groups. Patch v0.5 adds generic
`shape_entrance` and rejects charts on that path.

H001 real-deck transfer passes: 3-stage reveal in one click on slide 1, 2-stage
focus pulse in one click on slide 2, no slide inflation, source text/geometry
preserved and existing transition retained.

CI run 37239720520: **140/140 tests pass** + Python compile.

PowerPoint runtime remains the decisive missing gate.

Task: `research/tasks/T017-generic-report-motion.md`.
Report: `experiments/T017-20261005-generic-report-motion/REPORT.md`.

## T016 real-package data motion â€” 2026-10-05

T012â€“T015 now pass a real PPTX package integration, not only isolated XML.

A fixture derived from the valid H001 deck adds a native two-series/four-category
line chart plus `98.5%` KPI, then executes:

`inventory -> Director v0.3 -> compiler -> patch v0.4 -> output inventory`.

First CI exposed a genuine inventory gap: inline ChartML `strLit/numLit` points
were not counted. Parser fixed; regression added.

Final run 37239255072: **130/130 tests pass** + Python compile.

Package audit confirms two presenter clicks, source KPI preservation, native
chart build read-back, unchanged slide count, and byte-identical untargeted
slide/chart/relationship parts.

PowerPoint runtime playback remains pending.

Task: `research/tasks/T016-real-package-data-motion.md`.
Report: `experiments/T016-20261005-real-package-data-motion/REPORT.md`.

## T015 Director â†’ execution compiler â€” 2026-10-05

The manual bridge between Director v0.3 and patch v0.4 is removed for complete
data-motion slides.

`scripts/compile_data_motion_patch.py` compiles chart/KPI semantic beats into
`chart_entrance` / `number_counter`, resolves exact source targets and
preserves Director click grouping.

Safety: mixed/unsupported slides are blocked instead of partially compiled.
Odometer â†’ stepped-text fallback is explicit and can be disabled.

Final CI run 37238859486: **126/126 tests pass** + Python compile. Integration
regression preserves two presenter clicks across Director â†’ patch â†’ timing
read-back.

PowerPoint playback remains pending.

Task: `research/tasks/T015-director-to-execution.md`.
Report: `experiments/T015-20261005-director-to-execution/REPORT.md`.

## T014 KPI counter execution â€” 2026-10-05

T012 hero-metric counters now have a structural v0.4 execution path.

`number_counter` clones the exact source KPI textbox for intermediate values,
preserves style/geometry, sequences proxy entrance/exit inside one presenter
click beat, and reveals the untouched source textbox last.

Counter interpolation preserves prefix/suffix/decimal/grouping and rejects
source-text drift. The source final value is never rewritten.

CI run 37238539416: **120/120 tests pass** + Python compile.

Critical runtime gate remains: exact PowerPoint playback must prove that generated
entrance effects hide source/proxy shapes until scheduled and that only one value
is visible at a time.

Task: `research/tasks/T014-kpi-counter-execution.md`.
Report: `experiments/T014-20261005-kpi-counter-execution/REPORT.md`.

## T013 native chart execution â€” 2026-10-05

T012 semantic chart recipes now have a structural native execution path.

`existing-deck-timeline-patch` v0.3 supports `chart_entrance` on exact
existing chart graphicFrames and emits:

- chart sub-targets via `p:graphicEl/a:chart`;
- `seriesIdx/categoryIdx/bldStep`;
- `p:bldGraphic/p:bldSub/a:bldChart`;
- chart-type-specific conservative entrance filters;
- density guard with requested/effective build receipt.

Default fan-out limit is 24; excessive point-level builds degrade to series or
whole-chart rather than creating hundreds of effects.

CI run 37238145782: **112/112 tests pass** + Python compile. Structural read-back
confirms chart build mode and sub-target indices.

PowerPoint playback is still pending; this is not a native-playback claim.

Task: `research/tasks/T013-native-chart-execution.md`.
Report: `experiments/T013-20261005-native-chart-execution/REPORT.md`.

## T012 semantic data motion â€” 2026-10-05

User added a new product requirement: charts need type-specific animation, and
standalone hero metrics need dedicated number counting.

Inventory now recognizes classic ChartML subtype/dimensions and standalone
numeric candidates. `scripts/data_motion_recipes.py` maps chart semantics to
distinct defaults (baseline-grow, series-trace, segment-sweep, point-build,
etc.) and emits source-preserving KPI counter recipes.

Director v0.3 requires chart-targeting beats to declare type-specific data motion.
Hero KPI counter plans must preserve the exact source numeric value and format.
Data motion remains subordinate to T010/T011 click-beat rhythm.

CI run 37236839744: **103/103 tests pass** + Python compile.

This is semantic/structural evidence only. Native chart build and counter
playback remain pending.

Reference: `skills/pptx-motion/references/data-motion-recipes.md`.
Report: `experiments/T012-20261005-data-motion-recipes/REPORT.md`.

## T011 director click rhythm â€” 2026-10-05

T010 established click groups in the timing writer. T011 moves that decision
upstream into the AI Director.

Canonical semantic hierarchy:

`Deck Narrative -> Slide Objective -> Click Beat -> Motion Beat -> Effects`

Director v0.2 requires each click beat to record audience purpose, stable state,
pause type, and (after the first click) a narrative boundary reason. It rejects
flat/ambiguous grouping, nested `on-click`, and incomplete beat partitions.

Existing-deck patch v0.2 now preserves the same click grouping on a fresh
unanimated source slide, so multi-click pacing no longer requires multiple
slides.

CI run 37234829380: **92/92 tests pass** + Python compile. A regression patches a
real existing-deck fixture to two click groups and reads the groups back through
the deck inspector.

T009 no-script benchmark now explicitly penalizes whole-slide autoplay,
one-click-per-motion overfragmentation and premature reveals.

Report: `experiments/T011-20261005-director-click-rhythm/REPORT.md`.

## T010 presenter-paced click beats â€” 2026-10-05

User corrected the packed-motion target: one physical slide may contain many
motions **and many presenter clicks**. Packing and pacing are now separate.

Canonical rule: `docs/CLICK_BEAT_CHOREOGRAPHY.md`.
Task: `research/tasks/T010-click-beat-choreography.md`.

Native timeline v0.2 now models:

`Slide -> Click Beat -> Stage -> Effects`

T005 benchmark remains **1 slide / 82 behaviors**, but is repartitioned from the
legacy one-click chain into **4 click beats**:

1. burst;
2. orbit;
3. focus -> split;
4. reassemble -> restore.

`scripts/add_timeline.py` keeps v0.1 one-click behavior for historical
reproducibility and uses multiple `mainSeq` click groups for v0.2. The
existing-deck inspector also exposes click-group structure so authored presenter
rhythm can be preserved.

CI evidence: run 37234235795 â€” **86/86 tests pass**, Python compile pass.
Integration regression locks 4 clickEffect stages, 2 afterEffect stages and
82 behaviors on one slide. Native PowerPoint playback is still pending, so this
is structural evidence only.

Report: `experiments/T010-20261005-click-beat-choreography/REPORT.md`.

Cáº­p nháº­t ngĂ y 04/10/2026, giá» Viá»‡t Nam. PhiĂªn báº£n nguá»“n nghiĂªn cá»©u v0.7 (thĂªm T005 compound intent).

## T006 controlled motion semantics matrix â€” 2026-10-04 20:08 UTC

PR #12 prepares four exact one-slide files that differ only by stage-local vs
authored-layout motion paths and fill=remove vs fill=hold. Every file has two
900 ms motion behaviors in one click group. Four finalizers pass with no layout
warnings; all static renders were viewed and are pixel-identical. Exact audit
finds no uncontrolled package/XML difference. **83 tests pass.**

No PowerPoint runtime was available, so there is no winning native variant and
the production writer/source skill remain unchanged. Highest-value next action:
run all four exact hashes using
experiments/T006-20261004-motion-semantics-matrix/playback-checklist.json.
Only then revise path anchoring/fill and rebuild the full packed candidate.

## T006 full packed candidate â€” 2026-10-04 19:16 UTC / 05-10 Vietnam

Built `output/T006_packed_candidate.pptx`: **1 slide, 31 native objects, 6 stages,
82 encoded behaviors, 7,100 ms planned duration**. Exact SHA-256:
`41c4fb7865ea587e0d426fccf4de2c82fc1db731147a92a4fba28926b0e52094`.

Full pipeline initially failed because packing dropped state-local opening text.
Preserving initial text fixes the abort; the exact final file passes finalization
and its sole static render was viewed. **79 tests pass.** Failed raw artifact,
plans, receipt, hashes and full report are in
`experiments/T006-20261004-packed-validation/` (PR #11).

Independent audit found **47 path-origin mismatches under the authored-layout
coordinate model**, with maximum 543.766 px. This is a conditional geometry
diagnostic, not observed playback. All 82 behaviors currently use fill=remove.
Keep the evidence; do not promote native compatibility. Next: exact-file playback
and a PowerPoint-authored two-stage path fixture to resolve origin/fill/trigger
semantics. Do not rebuild this same candidate without a new hypothesis.
T007/T008 autonomy work remains as below; source skill is still research v0.7.

## T007 autonomy + existing-motion continuation

The product target is now explicit at the stronger autonomy level requested by
the user: **PPTX + optional high-level goal is enough input**. The model should
not require object-by-object animation instructions. It must discover/use a
script, infer one when absent, research reporting structure only when necessary,
reuse deck resources, synthesize only justified missing components, and return
the same report motion-directed.

Existing native animation is now first-class source evidence. Script priority is:
provided script â†’ speaker notes â†’ existing timing/choreography â†’ visible
narrative â†’ inferred narrative â†’ researched narrative. Existing timing must be
preserved/extended by default rather than rejected or deleted.

`inspect_existing_deck.py` now exposes transition and timing choreography:
effect types, source targets, durations, start conditions, numeric delays,
build groups and an order hint with an explicit structural-evidence boundary.

Branch CI run 37215400829: **75/75 tests pass** plus Python compile. New tasks:
`T008-existing-motion-continuation.md` and
`T009-autonomous-no-script-benchmark.md`.

Report: `experiments/T007-20261004-autonomy-existing-motion/REPORT.md`.

## Product destination â€” T007 Existing Deck Motion Director

NgÆ°á»i dĂ¹ng Ä‘Ă£ má»Ÿ rá»™ng Ä‘Ă­ch Ä‘áº¿n: há»‡ thá»‘ng pháº£i nháº­n **file PPTX cĂ³ sáºµn** vĂ  tá»±
Ä‘áº¡o diá»…n chuyá»ƒn Ä‘á»™ng. Náº¿u cĂ³ script/storyboard thĂ¬ bĂ¡m script. Náº¿u khĂ´ng cĂ³,
Æ°u tiĂªn speaker notes, sau Ä‘Ă³ tá»± phĂ¢n tĂ­ch trĂ¬nh tá»± bĂ¡o cĂ¡o; chá»‰ nghiĂªn cá»©u ngoĂ i
khi cáº§n vĂ  phĂ¹ há»£p. Náº¿u narrative thiáº¿u component thĂ¬ tá»± táº¡o helper component
trong Ä‘Ăºng visual framework cá»§a deck, khĂ´ng sinh decoration vĂ´ cá»›.

TĂ i liá»‡u chuáº©n: `docs/PRODUCT_TARGET.md`.
Task: `research/tasks/T007-existing-deck-motion-director.md`.

Scaffold hiá»‡n cĂ³:
- `scripts/inspect_existing_deck.py`: source-hash + slide/object/text/geometry/
  relationships/timing/transition/notes/theme/media inventory;
- `skills/pptx-motion/references/existing-deck-director.md`: director contract;
- `scripts/validate_director_plan.py`: buá»™c script source, source grounding,
  preserve slide count, target resource validity vĂ  justification cho component;
- final branch CI run `37214340363`: **67/67 tests pass**, `py_compile` pass.

Report: `experiments/T007-20261004-existing-deck-director/REPORT.md`. Pháº§n cĂ²n
pending: inference trĂªn deck tháº­t khĂ´ng cĂ³ script, synthesis component theo design
system, director-beat â†’ T006 timeline adapter, vĂ  patch/playback exact-file.

Default má»›i: preserve source slide count/order/content; resource cÅ© Ä‘Æ°á»£c reuse
trÆ°á»›c; same-resource motion pháº£i pack trong slide; generated component chá»‰ láº¥p
narrative gap.

### T007 source-object patcher checkpoint

ÄĂ£ thĂªm `scripts/patch_existing_timeline.py` vĂ 
`existing-deck-timeline-patch.md`: object deck tháº­t Ä‘Æ°á»£c target báº±ng source
slide + native `cNvPr id` + name, khĂ´ng cáº§n `!!`. Patcher kiá»ƒm source SHA-256,
chá»‰ sá»­a slide Ä‘Æ°á»£c chá»n, giá»¯ slide khĂ¡c byte-identical, preserve transition vĂ 
tá»« chá»‘i merge timing cÅ© mĂ¹ quĂ¡ng.

Deck intake cÅ©ng Ä‘Ă£ cĂ³ `design_profile` gá»“m font/fill/line/text-color/geometry
frequency Ä‘á»ƒ lĂ m basis khi sau nĂ y pháº£i sinh helper component.

Final temporary CI run `37214809106`: **73/73 tests pass** + `py_compile`
pass. Report: `experiments/T007-20261004-source-object-patcher/REPORT.md`.

Pháº§n cĂ²n thiáº¿u cho product path: director beat â†’ concrete patch-plan compiler;
native helper-component insertion + re-inventory; no-script narrative test trĂªn
deck tháº­t; exact-file PowerPoint playback.

## T006 native timing writer â€” Ä‘Ă£ cĂ³ backend cáº¥u trĂºc, playback cĂ²n pending

T006 Ä‘Ă£ tiáº¿n tá»« planning sang writer native háº¡n cháº¿. `scripts/pack_timeline.py`
váº«n nĂ©n T005 candidate 12 legacy states thĂ nh 1 semantic slide/6 stage vĂ 
transfer 10â†’1. `scripts/add_timeline.py` hiá»‡n ghi `p:timing` cho motion path,
scale vĂ  rotate trĂªn cĂ¹ng slide: waypoint náº±m trong path, cĂ¡c stage dĂ¹ng delay
tĂ­ch lÅ©y vĂ  cĂ¡c effect cĂ¹ng stage cháº¡y song song trong má»™t packed click group.

ÄÆ°á»ng dá»±ng end-to-end má»›i:
`validate_timeline.py -> render_timeline.mjs -> normalize_timeline_textboxes.py
-> add_timeline.py -> host finalizer`, gá»i báº±ng
`scripts/run_timeline_experiment.sh`.

Báº±ng chá»©ng tá»± Ä‘á»™ng: GitHub Actions branch-only run 37213501515 Ä‘áº¡t
`py_compile`, **55 unit tests**, `node --check` renderer vĂ  `bash -n` runner.
Workflow táº¡m Ä‘Ă£ xĂ³a sau kiá»ƒm tra. Prototype 1 slide/2 shape sau patch váº«n pass ZIP
CRC, má»Ÿ láº¡i báº±ng python-pptx vĂ  LibreOffice export PDF. ÄĂ¢y lĂ  báº±ng chá»©ng package,
**khĂ´ng pháº£i playback PowerPoint**.

Report: `experiments/T006-20261004-native-timing/REPORT.md`.
Native playback/editability exact-file váº«n pending; M1 chÆ°a Ä‘áº¡t.

## Chá»‰ thá»‹ má»›i â€” resource-local motion packing

NgÆ°á»i dĂ¹ng yĂªu cáº§u Ä‘á»•i kiáº¿n trĂºc: khĂ´ng coi má»—i chuyá»ƒn Ä‘á»™ng/state lĂ  má»™t slide.
Khi cĂ¡c action dĂ¹ng chung resource set vĂ  cĂ¹ng semantic scene, Æ°u tiĂªn gom tá»‘i Ä‘a
vĂ o má»™t native slide timeline. TĂ i liá»‡u chuáº©n: `docs/MOTION_PACKING.md`.

T005 12-state Morph giá»¯ nguyĂªn lĂ m baseline lá»‹ch sá»­. NĂ³ khĂ´ng cĂ²n lĂ  máº«u kiáº¿n
trĂºc má»¥c tiĂªu. T006 pháº£i cá»‘ gáº¯ng tĂ¡i hiá»‡n burst â†’ orbit â†’ focus â†’ split â†’
reassemble â†’ restore trong 1 slide vá»›i nhiá»u track/timing/trigger native; náº¿u
PowerPoint/backend buá»™c tĂ¡ch, ghi blocker vĂ  dĂ¹ng sá»‘ slide tá»‘i thiá»ƒu. CĂ¡c model
sau pháº£i Ä‘á»c rule nĂ y trÆ°á»›c khi thiáº¿t káº¿ choreography.

## Káº¿t quáº£ má»›i nháº¥t â€” T005

Æ¯u tiĂªn má»›i cá»§a ngÆ°á»i dĂ¹ng lĂ  hiá»‡u á»©ng phá»©c táº¡p tá»« má»™t cĂ¢u lá»‡nh ngáº¯n, giá»¯ Ä‘Ăºng Ă½ Ä‘á»‹nh. PR #3 vĂ  `experiments/T005-20261004-codex-choreography/REPORT.md` cĂ³ compiler intent nghiĂªm ngáº·t cho chuá»—i bung nĂºt, xoay vĂ²ng, phĂ³ng Ä‘á»‘i tÆ°á»£ng, tĂ¡ch lá»›p, ghĂ©p láº¡i vĂ  trá»Ÿ vá». AI diá»…n giáº£i prompt; compiler chá»‰ nháº­n dá»¯ liá»‡u cĂ³ cáº¥u trĂºc, khĂ´ng pháº£i NLP tá»•ng quĂ¡t.

Hai PPTX native: candidate 12 tráº¡ng thĂ¡i/31 Ä‘á»‘i tÆ°á»£ng, transfer 10 tráº¡ng thĂ¡i/22 Ä‘á»‘i tÆ°á»£ng. 7 nhĂ³m kiá»ƒm tra geometry vĂ  package parity Ä‘á»u Ä‘áº¡t trĂªn má»—i file. ÄĂ£ xem riĂªng Ä‘á»§ 22 áº£nh cuá»‘i. 41 unit tests Ä‘áº¡t. Äá»‘i chá»©ng cá»‘ Ă½ bá» waypoint cho sai lá»‡ch bĂ¡n kĂ­nh tuyáº¿n tĂ­nh 65,608 px; candidate cĂ²n 1,916 px. KhĂ´ng coi sá»‘ nĂ y lĂ  Ä‘á»™ mÆ°á»£t phĂ¡t thá»±c táº¿.

Lá»—i cĂ³ Ă­ch: tá»•ng gĂ³c xoay Ä‘Ăºng váº«n cĂ³ thá»ƒ che waypoint sai; Ä‘Ă£ giá»¯ test Ä‘á»™t biáº¿n vĂ  sá»­a kiá»ƒm tra tá»«ng waypoint/rĂ ng buá»™c nhĂ£n. Agent má»›i táº¡o bĂ i há»c táº­p 8 nĂºt, ngÆ°á»£c chiá»u 60Â°, nĂºt 6, 3 lá»›p; parent xuáº¥t file. Agent Ä‘Ă£ Ä‘á»c brief do AGENTS yĂªu cáº§u nĂªn khĂ´ng gá»i Ä‘Ă¢y lĂ  kiá»ƒm thá»­ mĂ¹ hoĂ n toĂ n.

Giá»›i háº¡n quan trá»ng: váº«n lĂ  2D Morph theo tá»«ng láº§n báº¥m, má»™t recipe háº¡n cháº¿, hĂ¬nh há»c cĂ²n Ä‘Æ¡n giáº£n; chÆ°a cĂ³ báº±ng chá»©ng hiá»‡u á»©ng áº¥n tÆ°á»£ng hoáº·c playback PowerPoint. KhĂ´ng pháº£i skill hoĂ n chá»‰nh hiá»ƒu má»i Ă½ tÆ°á»Ÿng phá»©c táº¡p, chÆ°a cĂ i personal skill. BÆ°á»›c tiáº¿p Æ°u tiĂªn T006 native timeline/path vĂ  T001 playback exact-hash; giá»¯ nguyĂªn T005 lĂ m Ä‘á»‘i chá»©ng.

File: `output/T005_compound_candidate.pptx` SHA-256 `05ddf33c89725dbb66083f5130c549d59d9aa291893321a34cc68c6cf9e9cf58`; `output/T005_compound_transfer.pptx` SHA-256 `e87d37db4a76f51c56dac893bade9c2966960cbc6bfc869ebb5bceb3d8cb5e16`.

## Káº¿t quáº£ má»›i nháº¥t â€” T002

PR #2, `experiments/T002-20261004-codex-tight-carriers/REPORT.md` giá»¯ E004 báº¥t biáº¿n vĂ  chá»‰ siáº¿t carrier quanh label. Trong cĂ¹ng proxy tuyáº¿n tĂ­nh, label giá»¯ 0/6 cáº·p chá»“ng vĂ  carrier giáº£m 6/6â†’0/6. Candidate cĂ³ 3 slide, 8 Ä‘á»‘i tÆ°á»£ng native/slide, 5 textbox/slide, 2 Morph 1100 ms; 3/3 áº£nh cuá»‘i Ä‘Ă£ xem vĂ  34 tests Ä‘áº¡t. SHA-256 `c41f2289bfd662f2642ea611b119d8aeaf35678425cba4cf4b7ffe0640922186`.

Tradeoff: focus emphasis tÄ©nh chá»§ quan giáº£m 4/5â†’3/5; creative váº«n 2/5. ÄĂ¢y lĂ  sá»­a rá»§i ro geometry, khĂ´ng chá»©ng minh motion Ä‘áº¹p hoáº·c playback Ä‘Ăºng. Native motion/editing null. Nguá»“n v0.6 chÆ°a cĂ i personal skill. BÆ°á»›c tiáº¿p: exact-hash PowerPoint playback so E004/T002, hoáº·c T004 portable backend; T002 tiáº¿p theo pháº£i cĂ³ giáº£ thuyáº¿t má»›i vá» emphasis/z-order.

## Káº¿t quáº£ má»›i nháº¥t â€” T003

Äá»c `experiments/T003-20261004-codex-layer01/REPORT.md` trÆ°á»›c khi tiáº¿p tá»¥c. NhĂ¡nh `work/T003-codex-20261004`, PR #1 cĂ³ generator 3â€“5 lá»›p, nguá»“n vĂ  rubric Ä‘Ă£ Ä‘Ă³ng bÄƒng, hai chá»§ Ä‘á» (QUANTA 5 lá»›p; há»c trá»±c tuyáº¿n 4 lá»›p), 5 PPTX giá»¯ cáº£ tháº¥t báº¡i vĂ  15 áº£nh cuá»‘i Ä‘Ă£ xem. Native parity Ä‘áº¡t trĂªn cáº£ 5 file; repo cĂ³ 34 tests Ä‘áº¡t. Backend cÅ© vĂ  cĂ¡c baseline E001â€“E004/H001â€“H003 giá»¯ nguyĂªn.

PhĂ©p Ä‘o fixture rĂ ng buá»™c: 16/60 child-state lá»‡ch â†’ 0/60, max 64 â†’ 0 px; Ä‘Ă¢y lĂ  lá»—i cá»‘ Ă½ Ä‘á»ƒ thá»­ quy táº¯c, khĂ´ng pháº£i benchmark Ä‘á»™c láº­p. Lá»—i sá»‘ tháº­t Ä‘Æ°á»£c phĂ¡t hiá»‡n báº±ng render: Ă´ 42 px lĂ m hai chá»¯ sá»‘ xuá»‘ng dĂ²ng. Chá»‰ má»Ÿ rá»™ng thĂ nh 60 px, sá»‘ lá»—i quan sĂ¡t QUANTA 15â†’0 vĂ  bĂ i má»›i 12â†’0. BĂ i má»›i do agent ngá»¯ cáº£nh riĂªng láº­p plan; parent xuáº¥t PPTX vĂ  sá»­a, khĂ´ng gá»i lĂ  benchmark tá»± hĂ nh end-to-end. Báº£n nĂªn dĂ¹ng: `output/T003_layer_candidate_v2.pptx`, `output/T003_transfer_v2.pptx`.

T003 má»›i Ä‘áº¡t pháº§n recipe 2D vĂ  transfer cáº¥u trĂºc/áº£nh tÄ©nh. Chá»‰ Ä‘á»c tutorial nguá»“n, chÆ°a xem choreography nguá»“n; khĂ´ng tĂ¡i hiá»‡n 3D extrusion. Native playback, sá»­a tháº­t trong PowerPoint, M1 váº«n pending; Ä‘iá»ƒm motion/editing null. Äiá»ƒm sĂ¡ng táº¡o tÄ©nh 3/5 lĂ  chá»§ quan, khĂ´ng pháº£i Ä‘áº¡t má»¥c tiĂªu chuyá»ƒn Ä‘á»™ng áº¥n tÆ°á»£ng. Nguá»“n v0.5 chÆ°a cĂ i thĂ nh personal skill.

BÆ°á»›c cĂ³ giĂ¡ trá»‹ tiáº¿p: T001 phĂ¡t exact-hash hai file v2; hoáº·c pháº§n tiáº¿p T003 xem animation nguá»“n thá»±c rá»“i láº­p giáº£ thuyáº¿t choreography má»›i; hoáº·c T002 xá»­ lĂ½ carrier crossing cÅ©. Claim Ä‘áº§u tiĂªn Ä‘Ă£ xong pháº¡m vi nghiĂªn cá»©u nĂ y; kiá»ƒm tra nhĂ¡nh/PR má»›i nháº¥t trÆ°á»›c khi nháº­n pháº§n tiáº¿p, khĂ´ng láº·p v1/v2.

## Tráº¡ng thĂ¡i thá»±c táº¿

M0 Ä‘Ă£ cĂ³ bá»™ thá»±c thi thá»­ nghiá»‡m vĂ  báº±ng chá»©ng cáº¥u trĂºc/bá»‘ cá»¥c E001, H001. M1 chÆ°a Ä‘áº¡t vĂ¬ thiáº¿u phĂ¡t thá»­ PowerPoint. ÄĂ¢y lĂ  nhĂ¡nh dá»±ng máº«u vĂ  kiá»ƒm tra pháº§n má»m trong lĂºc chá» cá»•ng native; khĂ´ng háº¡ tiĂªu chuáº©n nghiá»‡m thu M1. Nguá»“n skill lĂ  báº£n nghiĂªn cá»©u trong dá»± Ă¡n, chÆ°a cĂ i vĂ o tĂ i khoáº£n.

Repo chĂ­nh Ä‘Ă£ xĂ¡c minh: `https://github.com/togcoder/skill-for-pptx`, private, owner `togcoder`, quyá»n push. Chá»§ repo táº¡o README khá»Ÿi táº¡o ngĂ y 04/10/2026. Báº£n handoff nháº­p snapshot v0.4 cĂ¹ng nguá»“n, demo vĂ  báº±ng chá»©ng vĂ o repo nĂ y; lá»‹ch sá»­ cÅ© nguyĂªn váº¹n táº¡i `archive/pre-github-v0.4.bundle`. Äá»c `HANDOFF.md`, `docs/COLLABORATION.md` vĂ  cĂ¡c nhĂ¡nh/PR trÆ°á»›c khi nháº­n viá»‡c. KhĂ´ng dĂ¹ng tĂªn dá»± kiáº¿n `pptx-motion-lab` lĂ m repo GitHub ná»¯a.

## ÄĂ£ hoĂ n táº¥t

1. KhĂ´i phá»¥c scaffold tá»« phiĂªn trÆ°á»›c, giá»¯ snapshot gá»‘c. PhĂ¡t hiá»‡n nguá»“n SKILL.md cĂ²n template TODO vĂ  Ä‘Æ°á»ng dá»±ng chÆ°a hoĂ n táº¥t.
2. HoĂ n thiá»‡n Ä‘Æ°á»ng dá»±ng háº¡n cháº¿ báº±ng artifact-tool, káº¿ hoáº¡ch JSON, chĂ¨n Morph vĂ  kiá»ƒm tra file cuá»‘i.
3. Dá»±ng E001 ba cáº£nh vá»›i 13 Ä‘á»‘i tÆ°á»£ng native má»—i slide; hai khai bĂ¡o Morph 1.200 ms. Render vĂ  xem toĂ n bá»™ file cuá»‘i.
4. Sá»­a bá»™ chĂ¨n Morph: Ä‘á»c Ä‘Ăºng thá»© tá»± slide, kiá»ƒm tra sá»‘ cáº£nh vĂ  tĂªn, báº£o vá»‡ file cĂ³ timing, tá»« chá»‘i duration láº», khĂ´ng Ä‘á»ƒ láº¡i file dá»Ÿ vĂ  khĂ´ng ghi Ä‘Ă¨.
5. CĂ¹ng bá»™ 7 lá»—i má»¥c tiĂªu: baseline 1/7, candidate 7/7. ToĂ n bá»™ 19 unit tests hiá»‡n cĂ³ pass. KhĂ´ng coi Ä‘Ă³ lĂ  Ä‘iá»ƒm cháº¥t lÆ°á»£ng chuyá»ƒn Ä‘á»™ng hay benchmark Ä‘á»™c láº­p.
6. Viáº¿t nguá»“n skill v0.2 cĂ¹ng há»£p Ä‘á»“ng, cĂ´ng thá»©c, rubric vĂ  hÆ°á»›ng dáº«n thá»±c thi cĂ³ thá»ƒ gá»i láº¡i.
7. DĂ¹ng má»™t agent vá»›i ngá»¯ cáº£nh tá»‘i thiá»ƒu Ä‘á»ƒ Ă¡p dá»¥ng skill vĂ o H001: hai cáº£nh Collect/Inspect/Decide, phĂ³ng lá»›n Inspect vĂ  giá»¯ bá»‘i cáº£nh hai bĂªn. ÄĂ£ táº¡o PPTX vĂ  xem hai slide cuá»‘i. KhĂ´ng tiáº¿t lá»™ Ä‘Ă¡p Ă¡n/cháº©n Ä‘oĂ¡n E001 cho agent Ä‘Ă³.
8. H001 phĂ¡t hiá»‡n nguá»“n tham kháº£o E001 bá»‹ gáº¯n cá»©ng trong speaker notes; Ä‘Ă£ sá»­a renderer Ä‘á»ƒ dĂ¹ng nguá»“n thá»±c sá»± trong káº¿ hoáº¡ch.
9. H001 cÅ©ng phĂ¡t hiá»‡n planned textbox xuáº¥t thĂ nh native shape cĂ³ p:txBody nhÆ°ng khĂ´ng cĂ³ txBox=1. Giá»¯ kiá»ƒm tra nghiĂªm ngáº·t tháº¥t báº¡i, ghi ranh giá»›i trong skill; khĂ´ng sá»­a rubric Ä‘á»ƒ che lá»—i.
10. E002 sá»­a Ä‘Ăºng 14 khai bĂ¡o textbox cá»§a H001 theo káº¿ hoáº¡ch. Bá»™ kiá»ƒm tra H001 giá»¯ nguyĂªn: tá»« 14 lá»—i cĂ²n 0 lá»—i, 93/93 kiá»ƒm tra Ä‘áº¡t. Chá»‰ hai slide XML thay Ä‘á»•i bá»Ÿi txBox; má»i pháº§n khĂ¡c giá»¯ nguyĂªn byte. Hai áº£nh cuá»‘i giá»‘ng H001 tá»«ng pixel. 25 unit tests Ä‘áº¡t. Nguá»“n skill/bá»™ dá»±ng Ä‘Ă£ dĂ¹ng bÆ°á»›c chuáº©n hĂ³a nĂ y.

11. H002 Ä‘Ă£ hoĂ n táº¥t tá»« Ä‘á» Ä‘á»™c láº­p vá» Ä‘Ă¨n ORBIT: 3 slide, 11 Ä‘á»‘i tÆ°á»£ng native má»—i slide, 6 textbox/slide Ä‘Ăºng khai bĂ¡o, 2 Morph 1.100 ms. Agent vĂ  parent Ä‘Ă£ xem Ä‘á»§ áº£nh cuá»‘i. Agent khĂ´ng Ä‘á»c plan/artifact cÅ©, nhÆ°ng Ä‘Æ°á»£c thu gá»n pháº§n viá»‡c sau giai Ä‘oáº¡n Ä‘á»c hÆ°á»›ng dáº«n; khĂ´ng coi Ä‘Ă¢y lĂ  benchmark tá»± hĂ nh cĂ³ Ä‘o thá»i gian.
12. H002 lá»™ nguy cÆ¡ nhĂ£n gáº·p nhau khi Ä‘á»•i chá»— Ä‘á»‘i á»©ng. E003 giá»¯ baseline vĂ  cĂ¹ng phĂ©p Ä‘o hĂ¬nh há»c tuyáº¿n tĂ­nh liĂªn tá»¥c: tá»« 2 cáº·p nhĂ£n cĂ³ khoáº£ng chá»“ng xuá»‘ng 0 trĂªn 6 cáº·p/chuyá»ƒn cáº£nh. Chá»‰ Ä‘á»•i bá»‘ trĂ­/Ä‘Æ°á»ng Ä‘i thĂ nh chu ká»³ qua ba Ä‘á»‰nh tam giĂ¡c; giá»¯ 3 slide, chá»¯, loáº¡i/kĂ­ch thÆ°á»›c Ä‘á»‘i tÆ°á»£ng vĂ  thá»i lÆ°á»£ng. File cuá»‘i Ä‘áº¡t cáº¥u trĂºc, render/xem Ä‘á»§ 3 slide. ÄĂ¢y lĂ  cáº£i thiá»‡n trong mĂ´ hĂ¬nh giáº£ Ä‘á»‹nh, chÆ°a pháº£i playback PowerPoint.

13. H003 thá»­ Ä‘á» má»›i vá»›i ba nhĂ£n tiáº¿ng Viá»‡t dĂ i 360Ă—96 px. Giá»¯ rubric vĂ  cháº©n Ä‘oĂ¡n E003: 4/6 cáº·p nhĂ£n cĂ³ khoáº£ng chá»“ng theo mĂ´ hĂ¬nh. E004 chá»‰ Ä‘á»•i y cá»§a khá»‘i/nhĂ£n, tÄƒng khoáº£ng cĂ¡ch hai táº§ng tá»« 200 lĂªn 300 px, sá»‘ cáº·p nhĂ£n chá»“ng vá» 0. Cáº£ hai váº«n 6/6 cáº·p khá»‘i cĂ³ khoáº£ng chá»“ng. File cuá»‘i cĂ³ 3Ă—8 Ä‘á»‘i tÆ°á»£ng native, 5 textbox/slide vĂ  hai Morph 1.100 ms; kiá»ƒm tra vĂ  xem Ä‘á»§ 6 áº£nh cuá»‘i.
14. Bá»• sung scripts/cyclic_label_clearance.py vá»›i ngÆ°á»¡ng H >= 3*d*h/(2*d-w) cho ba nhĂ£n Ä‘á»u, ba vá»‹ trĂ­ Ä‘á»‘i xá»©ng, ná»™i suy Ä‘á»“ng bá»™ tuyáº¿n tĂ­nh; cĂ³ miá»n Ă¡p dá»¥ng rĂµ. Bá»‘n test má»›i Ä‘á»‘i chiáº¿u cháº©n Ä‘oĂ¡n cÅ©, tá»•ng 29 unit tests Ä‘áº¡t. ÄĂ£ cáº­p nháº­t nguá»“n skill vá»›i bĂ i há»c vĂ  giá»¯ lá»—i plan/preflight ban Ä‘áº§u.

Táº¡i má»‘c bĂ n giao v0.4 chÆ°a cĂ³ claim nghiĂªn cá»©u má»›i; T003 sau Ä‘Ă³ Ä‘Æ°á»£c nháº­n táº¡i PR #1 nhÆ° má»¥c má»›i nháº¥t phĂ­a trĂªn. LuĂ´n kiá»ƒm tra nhĂ¡nh vĂ  PR má»Ÿ Ä‘á»ƒ biáº¿t cĂ´ng viá»‡c Ä‘ang cháº¡y. Nguá»“n skill bá»• sung cĂ´ng thá»©c cyclic focus vĂ  phĂ¢n biá»‡t sá»‘ tráº¡ng thĂ¡i vá»›i sá»‘ chuyá»ƒn cáº£nh. Read cá»§a H002/E003 má»Ÿ á»Ÿ tÆ° tháº¿ lá»›n; khĂ´ng cĂ³ Ä‘oáº¡n phĂ³ng lá»›n riĂªng trĂªn slide Ä‘áº§u.

## Báº±ng chá»©ng cáº§n Ä‘á»c

- `experiments/E001/REPORT.md`, `scores.json`, `regression-comparison.json`, `validation.json`, `final-renders/`.
- `experiments/H001/`: káº¿ hoáº¡ch Ä‘á»™c láº­p, rubric, bĂ¡o cĂ¡o vĂ  báº±ng chá»©ng file cuá»‘i.
- `experiments/E002/REPORT.md`, `comparison.json`: sá»­a textbox, giá»¯ baseline vĂ  tiĂªu chĂ­ H001; `output/PPTX_Motion_Lab_E002.pptx`.
- `experiments/H002/`: Ä‘á», plan, rubric, qa vĂ  báº£n sao báº±ng chá»©ng táº¡i `evidence/`.
- `experiments/E003/REPORT.md`: H002 vĂ  E003, cháº©n Ä‘oĂ¡n Ä‘Æ°á»ng Ä‘i, kiá»ƒm tra cáº¥u trĂºc vĂ  Ä‘iá»ƒm tÄ©nh chá»§ quan. Native motion/editability váº«n null; khĂ´ng tĂ­nh Ä‘iá»ƒm tá»•ng.
- `experiments/E004/REPORT.md`, `package-comparison.json`, `unit-tests.txt`, `scores.json`, cĂ¡c `path-diagnostic.json` vĂ  `carrier-paths.json` H003/E004; `output/PPTX_Motion_Lab_E004.pptx`.
- `research/skill-source-validation.json`: kiá»ƒm tra nguá»“n thá»­ nghiá»‡m, khĂ´ng pháº£i chá»©ng nháº­n cĂ i Ä‘áº·t skill.
- `docs/POWERPOINT_QA.md`: yĂªu cáº§u báº±ng chá»©ng native.

PPTX E001: `output/PPTX_Motion_Lab_E001.pptx`. SHA-256: b3b4e28c14f00bc4fe05d6a71400752819413661e1280eb92301b4a6305e7c37.
PPTX H001: `output/PPTX_Motion_Lab_H001.pptx`; dĂ¹ng hash trong báº±ng chá»©ng H001.

Äiá»ƒm E001: Ä‘Ă¡p á»©ng Ä‘á» 4/5, cáº¥u trĂºc chá»‰nh sá»­a 4/5, Ä‘á»‹nh danh 4/5, dá»… Ä‘á»c tÄ©nh 4/5, bá»‘ cá»¥c sĂ¡ng táº¡o tÄ©nh 3/5. ÄĂ¢y lĂ  nháº­n xĂ©t khĂ´ng mĂ¹ cá»§a ngÆ°á»i lĂ m. Chuyá»ƒn Ä‘á»™ng chÆ°a cháº¥m, khĂ´ng cĂ³ Ä‘iá»ƒm tá»•ng.

## Viá»‡c tiáº¿p theo theo giĂ¡ trá»‹

1. Hai Ä‘Æ°á»ng Æ°u tiĂªn: (a) dĂ¹ng `output/T006_packed_candidate.pptx` Ä‘Ă£ freeze hash trong bĂ¡o cĂ¡o packed-validation Ä‘á»ƒ kiá»ƒm playback PowerPoint vĂ  Ä‘á»‘i chiáº¿u fixture hai cháº·ng vá» origin/fill/trigger; (b) T007 láº¥y má»™t deck tháº­t 3â€“10 slide, inventory â†’ script/infer â†’ motion-direct má»™t slide báº±ng resource cĂ³ sáºµn, tá»‘i Ä‘a má»™t helper component, khĂ´ng Ä‘á»•i slide count. KhĂ´ng dá»±ng láº¡i candidate cÅ© náº¿u chÆ°a cĂ³ giáº£ thuyáº¿t má»›i. KhĂ´ng quay láº¡i waypoint slides náº¿u playback lá»—i; sá»­a trong cĂ¹ng slide vĂ  giá»¯ baseline. T001/native exact-hash váº«n lĂ  cá»•ng nghiá»‡m thu; M1 pending.
2. Náº¿u chÆ°a cĂ³ PowerPoint, khĂ´ng láº·p ma tráº­n origin/fill vá»«a táº¡o. Chá»n T007/T008 hoáº·c chuáº©n bá»‹ má»™t fixture native khĂ¡c chá»‰ khi cĂ³ biáº¿n sá»‘ má»›i rĂµ rĂ ng. KhĂ´ng gá»i mĂ´ phá»ng lĂ  playback hoáº·c tÄƒng sá»‘ Ä‘á»‘i tÆ°á»£ng lĂ  tÄƒng cháº¥t lÆ°á»£ng hiá»‡u á»©ng.
3. Chia pháº§n viá»‡c theo task trong `research/tasks/`. Nháº­n claim/nhĂ¡nh riĂªng trÆ°á»›c khi lĂ m Ä‘á»ƒ trĂ¡nh trĂ¹ng. Skill vĂ  renderer hiá»‡n váº«n phá»¥ thuá»™c mĂ´i trÆ°á»ng Work nhÆ° `docs/ENVIRONMENT.md`.
4. Chuáº©n bá»‹ cĂ´ng cá»¥ thu báº±ng chá»©ng trĂªn PowerPoint Windows khi phĂ¹ há»£p, khĂ´ng giáº£ láº­p káº¿t quáº£. Benchmark 18 lÆ°á»£t chÆ°a thá»±c hiá»‡n.

## KhĂ´i phá»¥c vĂ  lÆ°u tiáº¿p

GitHub `togcoder/skill-for-pptx` lĂ  nguá»“n lĂ m viá»‡c chĂ­nh. Clone/fetch main má»›i nháº¥t, kiá»ƒm tra nhĂ¡nh/PR vĂ  Ä‘á»c HANDOFF.md. Äá»c docs/RECOVERY.md Ä‘á»ƒ tra lá»‹ch sá»­ trÆ°á»›c khi nháº­p GitHub. Bundle vĂ  cĂ¡c checkpoint cloud cÅ© lĂ  snapshot phá»¥c há»“i lá»‹ch sá»­; khĂ´ng ghi chĂºng Ä‘Ă¨ lĂªn repo má»›i hÆ¡n. Code vĂ  káº¿t quáº£ Ä‘Ă£ gáº¯n GitHub Ä‘Æ°á»£c commit/push vá» Ä‘Ăºng repo, khĂ´ng táº¡o báº£n sao code má»›i song song trong Library.
