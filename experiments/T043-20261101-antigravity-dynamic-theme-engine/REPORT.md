# T043 [pptx] — Dynamic Theme Engine: Need-Based Synthesizer, Reference Teardown & AI Image Visual Harmonizer

## Frame
- **Question:** How can an AI presentation agent dynamically synthesize, propose, or reverse-engineer endless presentation themes based on user need or reference files, rather than being confined to hardcoded preset themes?
- **Hypothesis (and what would falsify it):** A presentation theme can be mathematically parameterized as a `ThemeSpec` containing:
  1. Area-weighted 60-30-10 color hierarchy in OKLab/OKLCH perceptual space.
  2. Relative luminance canvas classification (`DARK_CANVAS`, `WARM_PAPER`, `LIGHT_CANVAS`, `MID_TONE_CANVAS`).
  3. Character-mode typography profile (`font_display`, `font_body`) and geometric modular scale ($r = (S_{\text{h1}} / S_{\text{body}})^{1/3}$).
  4. Shape geometry DNA (`SHARP_CHAMFER`, `FREEFORM_ANGLED`, `SOFT_ORGANIC_PILL`, `ROUNDED_BENTO`).
  5. AI image prompt directives (synchronizing lighting Kelvin, color grading, and aspect ratio).
  Falsified if reverse-engineering sample decks misidentifies dark/warm/light canvas, collapses contrast below WCAG AA (< 4.5:1), or produces AI image prompts that clash with slide lighting.
- **Domain lens (native canon and sources used):**
  - `domains/pptx/DOMAIN.md`
  - OKLab / OKLCH Color Space (Björn Ottosson, 2020)
  - WCAG 2.1 Relative Luminance & Contrast Math
  - User-provided reference sample decks: `Blue Modern Business Pitch Deck Presentation.pptx` & `Webinar Keynote Presentation.pptx`
- **Transfers from other domains (and how they are tested):**
  - Brand palette OKLCH color science (T030) transferred into Area-Weighted Clustering and Dynamic Hue Override. Tested in `NeedBasedSynthesizerTests`.
  - Visual prompts from `image-generator` harmonized with deck canvas mode. Tested in `ImagePromptHarmonizerTests`.

## Frozen input
- Request / date: User strategic direction to synthesize themes based on user needs and extract from reference decks (2026-11-01).
- Base commit: `9c5ec6dd0a594a8367c59288de9b45a86e343d62`
- Environment: Windows 11, Python 3.12, Pillow, DeckCraft CLI (`D:\artcraft\DeckCraft\deckcraft-cli.exe`).
- Reference files:
  - `C:\Users\COMPUTER\Desktop\QCC - SHARP Team\reference\sample_decks\Blue Modern Business Pitch Deck Presentation.pptx`
  - `C:\Users\COMPUTER\Desktop\QCC - SHARP Team\reference\sample_decks\Webinar Keynote Presentation.pptx`

## Method
Commands to reproduce:
```powershell
$env:PYTHONUTF8=1
cd skill-for-pptx
python -m py_compile scripts/theme_engine.py tests/test_theme_engine.py
python -m unittest tests/test_theme_engine.py -v
python -m unittest discover -s tests
python lab/tools/check_layout.py
```

## Evidence
| Claim | Rung (0–6) | Evidence (path, hash, output) |
|---|---|---|
| Area-Weighted Color Math | Rung 0 | `scripts/theme_engine.py`: OKLab/OKLCH roundtrip, Relative Luminance, WCAG contrast pass in `ColorMathTests` |
| Native Reference Teardown (Blue Modern) | Rung 4 | Extracted `DARK_CANVAS` (`#01152B`), `#FFFFFF` text, `Aileron` font, `hero_kpi_pt = 202.0`, `custGeom` mask from `Blue Modern` PPTX |
| Native Reference Teardown (Webinar) | Rung 4 | Extracted `WARM_PAPER` (`#F4F1E9`), `#1A1A1A` text, `TT Commons Pro` + `TAN Mon Cheri` fonts, pastel accents (`#FFD0E0`, `#C6A4BF`, `#EAA86B`) from `Webinar` PPTX |
| Need-Based Semantic Synthesizer | Rung 0 | Synthesizes tailored palettes for QCC reports, AI Pitch Decks, and Corporate Keynotes with $\ge 4.5$ WCAG contrast |
| Dynamic Hue Override | Rung 0 | Rotates accent Hue in OKLCH while preserving Lightness and Chroma without contrast degradation |
| AI Image Visual Harmonizer | Rung 0 | Generates 6-layer prompts with 6500K for Dark Canvas, 3800K for Warm Paper, 5500K for Light Canvas, and slots (16:9, 4:5, 1:1) |
| Full Suite Conformance | Rung 0 | All 352 unit tests pass 100% (skipped=4); `lab/tools/check_layout.py` reports `layout OK` |

## Negative results and limitations
- If full-bleed background artwork is a purely raster graphic without XML vector tokens, `Pillow` is required to sample pixel clusters; a mathematical fallback is provided when Pillow is absent.
- Custom boutique display fonts (e.g. `TAN Mon Cheri`, `Aileron`) require the font files to be present on the presenter's operating system to render; fallback font stacks (`Century Gothic`, `Segoe UI`, `Georgia`, `Playfair Display`) are supplied in each ThemeSpec.

## Next
- Wire `theme_engine.py` into `slide_forge.py` CLI (`--ref-deck <file.pptx>` and `--need "<prompt>"`).
- Connect `build_harmonized_image_prompt` directly to subagent `image-generator` to auto-insert generated PNGs into slide placeholders.

## Review response
| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| (Pending peer review from Claude / OpenCode) | review requested |
