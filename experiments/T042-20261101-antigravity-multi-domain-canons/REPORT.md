# T042 [cross] — Multi-Domain Design Canons: Video, Vector/SVG, 3D/Solid, CAD & Audio

## Frame
- **Question:** How can AI agents operating across disparate design mediums (video, vector, 3D solid modeling, engineering drafting, audio mastering) produce deterministic, professional-grade output rather than amateurish artifacts?
- **Hypothesis (and what would falsify it):** Every creative medium has a non-arbitrary mathematical and geometric canon (safe margins, stroke scaling formulas, Bézier curvature ratios, no-sharp-edge micro-bevels, ISO line weight hierarchies, EBU R128 loudness targets). If cross-domain generation adheres to these formal JSON tokens and pre-flight validators, generated outputs will conform to international industry standards (SMPTE, ISO 128, ISO 5457, ISO 7200, EBU R128). Falsified if agents produce illegible text in video dead zones, blurry subpixel vector lines, unrenderable razor-sharp 3D edges, non-standard CAD line weights, or clipped audio.
- **Domain lens (native canon and sources used):**
  - **Video Domain:** SMPTE RP 2046-2, EBU R95 safe areas, EBU R128 / ITU-R BS.1770-4 loudness.
  - **Vector Domain:** W3C SVG 2.0, Material Design 24x24 Icon Grid, Apple Squircle $G^2$ curvature.
  - **3D Domain:** ISO 10303 (STEP), Khronos glTF 2.0 PBR Metallic-Roughness, 3-Point Studio Lighting.
  - **CAD Domain:** ISO 5457 (Drawing sheets), ISO 128 (Line weight groups), ISO 129 (Dimensioning), ISO 7200 (Title blocks).
  - **Sound Domain:** EBU R128, AES TD1004.
  - **ArtCraft Native Suite:** Probed and verified 13 headless Rust CLIs in `D:\artcraft`.
- **Transfers from other domains (and how they are tested):**
  - Pacing and timeline concepts from `pptx` motion director transferred to `video` ASL and J/L-cuts. Tested by `test_video_pacing_and_cuts`.
  - Token-first architecture established in T038 (`pptx_design_canon.json`) transferred to all 5 specialized domain JSON canons in `knowledge/`.

## Frozen input
- Request / date: User request to establish foundational steps for Video, SVG, 3D, and CAD via Argon consultation (2026-11-01).
- Base commit: `6fa3126bfa2ec447d372d261f4fe6caebf1dbf22`
- Environment: Windows 11, Python 3.12, ArtCraft Native Suite (Rust 2024 headless CLIs in `D:\artcraft`).
- Could not access: None (all 13 CLIs in `D:\artcraft` were discovered, probed, and executed).

## Method
Commands to reproduce:
```powershell
$env:PYTHONUTF8=1
cd skill-for-pptx
python lab/tools/check_layout.py
python -m unittest tests/test_multi_domain_canons.py -v
python -m unittest discover -s tests
python scripts/cadcraft_bridge.py sample bracket experiments/T042-20261101-antigravity-multi-domain-canons/artifacts/cad_sample_bracket.svg
python scripts/solidcraft_bridge.py icon experiments/T042-20261101-antigravity-multi-domain-canons/artifacts/solidcraft_icon.png
```

## Evidence
| Claim | Rung (0–6) | Evidence (path, hash, output) |
|---|---|---|
| Domain Canons Defined | Rung 0 | `knowledge/video_canon.json`, `knowledge/vector_canon.json`, `knowledge/3d_solid_canon.json`, `knowledge/cad_iso_canon.json`, `knowledge/sound_canon.json` |
| Mathematical Tokens Evaluated | Rung 0 | `scripts/multi_domain_canons.py`: 24 unit tests pass in `tests/test_multi_domain_canons.py` |
| Video Safe Margins & Dead Zones | Rung 0 | 16:9 Action (3.5% = 1786x1004), Title (5.0% = 1728x972), 9:16 mobile UI dead zones verified |
| Non-linear Stroke Scaling | Rung 0 | $W(S) = W_0 (S/S_0)^{0.75}$: 16px→1.5px, 24px→2.0px, 32px→2.5px, 48px→3.25px verified |
| Bézier Curvature $\kappa$ Ratio | Rung 0 | Circle arc 90° handle length $\kappa = \frac{4}{3}(\sqrt{2}-1) \approx 0.55228$ verified |
| No-Sharp-Edge Law & Bevels | Rung 0 | Micro-bevel formula $R = 0.005 \times \min(W,H,D)$ bounded in $[0.2, 0.5]\text{ mm}$ verified |
| ISO 128 / 5457 / 7200 CAD Standard | Rung 0 | Sheet sizes A4–A0, 0.50mm line weight group (0.50, 0.25, 0.18mm), 10mm/7mm offsets, 180mm title block verified |
| Native ArtCraft CLI Discovery | Rung 1 | `FilmCraft\filmcraft-cli.exe`, `SolidCraft\solidcraft-cli.exe`, `CADCraft\cadcraft-cli.exe`, `SoundCraft\soundcraft-cli.exe` operational |
| Native CAD Vector & Raster Generation | Rung 4 | Generated `artifacts/cad_sample_bracket.svg` (99KB) and `artifacts/cad_sample_bracket.png` (115KB) via `cadcraft-cli sample` |
| Native 3D Icon Raster Generation | Rung 3 | Generated `artifacts/solidcraft_icon.png` (21KB) via `solidcraft-cli icon` |
| Lab Conformance & Test Suite | Rung 0 | `lab/tools/check_layout.py` reports `layout OK`; 340 tests pass 100% (skipped=4) |

## Negative results and limitations
- Real-time video rendering of full timelines with complex transitions requires high GPU/CPU resources; pre-flight validation must be relied on before triggering headless rendering.
- `CADCraft` sample generator supports `bracket` and `floorplan`; custom procedural scripts require valid DXF/DWG entity syntax which will be expanded in domain-specific tasks.
- Ambiguous PBR materials (metalness between 0.2 and 0.8) are strictly flagged as errors to prevent physically inaccurate renderings.

## Next
- Task T043: Implement `FilmCraft` scene synthesis and timeline scripting validator (`pacing_and_lufs_validator.py`).
- Task T044: Implement `SolidCraft` procedural CSG generator with automatic micro-bevel enforcement.
- Task T045: Implement `CADCraft` ISO 128 multi-view drawing layout generator.

## Review response
| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| (Pending peer review from Claude / OpenCode) | review requested |
