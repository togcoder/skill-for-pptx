# T027 — Learning design and complex motion from real files (2026-10-07)

Owner direction: don't fetch pictures (AI can make those). Find beautiful
.pptx/.potx and decks with complex animation, and extract what good design
and complex motion are.

## Sources used, and why

| Source | Kind | Access | Use |
|---|---|---|---|
| Desktop PowerPoint 16.0 (COM) | every built-in effect, authored by PowerPoint | local | canonical XML for 198 effects |
| Office `Document Themes 16` | 11 designer themes, 23 palettes, 25 font pairings | local install | design kits |
| [Zenodo10K](https://huggingface.co/datasets/Forceless/Zenodo10K) | 10,448 licensed real decks | HTTP Range, XML parts only | 797-deck sample, motion/design statistics |
| LibreOffice `sd/qa/unit/data/pptx` | edge-case animation test files (MPL-2.0) | GitHub API | listed for later (triggers, effect order, SmartArt) |
| SlidesCarnival | designer templates, CC BY 4.0 | **not crawled**: `robots.txt` disallows `/download/` | the owner may hand-download favourites |

## Results

The detailed numbers are in `knowledge/README.md`. The headline:

- **The average deck *is* the complaint.** 93% of real effects are entrances,
  and the median animated deck uses 2 distinct effects.
- **Complexity comes from object lifecycles**: replace in place, enter → path,
  path → spin, fade → transparency, and longer chains. Delay staggering
  appears in under 2% of click groups.

### Integrated

1. `ppt:<name>` effects in the writer, simulator, conflict check and
   Director validator (198 presets).
   - PowerPoint identified 7/7 sampled library effects by native EffectType:
     `library_effects_expected.json` vs `library_effects_native_sequence.json`.
2. `style: "dynamic"` (Director and Forge). A full Forge deck rendered by
   PowerPoint registers effect types 48/50/62/34… (Faded Zoom, Ascend, Rise
   Up, Expand, Grow & Turn); see `dynamic_native_sequence.json`.
3. `office:<Name>` Forge themes in light/dark. All 22 variants pass AA for
   every text role. `FONT_GLYPHS` blocks Vietnamese text in fonts without
   Vietnamese glyphs.

Tests: `tests/test_preset_library.py` writes all 198 presets, checks
class/ID/subtype, unique ids, retargeting and time scaling, and runs the
simulator. `OfficeKitTests` covers contrast and Vietnamese glyphs. The full
suite passes.

## Limits

- Zenodo10K is research talks: it measures what is common, not what is beautiful.
- Beauty references are Microsoft themes only. Designer marketplaces are excluded by licence/terms.
- Library emphasis effects (colour waves, teeter…) are not simulated in previews; they appear as unchanged state.
- Corpus scans read slide XML only (≤ 80 slides per deck). Media, SmartArt
  drawing parts and charts were not inspected.
