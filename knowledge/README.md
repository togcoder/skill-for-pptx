# Knowledge base: what good design and complex motion look like

Derived data, not copied files. The source decks and themes stay in
`local-media/` (git-ignored) or in the user's Office install. Only numbers,
names and PowerPoint's own XML for its built-in effects are committed.
Regenerate everything with the commands at the end.

## Files

| File | Source | What it gives the tools |
|---|---|---|
| `powerpoint_presets.json` | PowerPoint 16.0 authored every `MsoAnimEffect` (`harvest_presets.ps1`) | 198 effects (52 entrance, 52 exit, 30 emphasis, 64 motion paths) as canonical XML templates. The writer accepts them as `"ppt:<name>"`. |
| `office_design_kits.json` | Microsoft's designer themes in the local Office install (11 `.thmx`, 23 colour schemes, 25 font pairings) | Palettes, font pairs, master type scale, margins and decoration. Forge themes `office:<Name>` come from here. |
| `corpus_motion_design.json` | 797 licensed real decks sampled from Zenodo10K (CC BY etc.), read XML-only over HTTP Range | How real people animate and typeset; the most motion-complex decks. |
| `motion_phrases.json` | the 60 most motion-complex corpus decks | Object lifecycles and click-group shapes, i.e. what "complex" means in practice. |

## Design: what designers do (Office themes)

- **Type scale:**
  - Titles are 36–50 pt and level-1 body text is 18–28 pt on a 13.33 in slide.
  - Title ≈ 2 × body. Each body level steps down by 2–4 pt.
  - Only 4–5 sizes are in play.
- **Fonts:** one or two families per theme (Century Gothic, Trebuchet,
  Gill Sans, Garamond, Tw Cen MT / Tw Cen MT Condensed, Calibri Light +
  Calibri, Aptos Display + Aptos). A display face for headings plus its text
  sibling is the common pairing.
- **Layout and decoration:**
  - The left margin is 5–21% of the slide width.
  - Masters carry 0–6 decorative shapes. Restraint is the norm.
- **Colour:**
  - Palettes have 2 darks, 2 lights and 6 accents.
  - Accent 1 leads and accent 2 supports. The rest go to charts.
  - Forge derives light and dark variants and nudges colours until every text
    role passes WCAG AA (4.5:1).

### Contrast with real decks (corpus medians)

| | Corpus median | Corpus p90 | Designer themes |
|---|---|---|---|
| Distinct type sizes per deck | 9 | 18 | 4–5 |
| Characters per slide | ~270 | ~550 | Forge keeps bullets ≤ 12 words |
| Shapes per slide | ~7 | ~22 | |

The gap between corpus and designer is the design brief: fewer sizes, fewer
words, more space.

## Motion: what "complex" really is

- Only **43%** of real decks animate anything, and only **20%** of slides.
- **93%** of effects are entrances. Emphasis is 1.2%, motion paths 0.8%,
  exits 2.7%.
- The median animated deck uses **2** distinct effects (p90: 6).
- The top effects are Appear, Faded Zoom, Wipe, Fade, Fly, Ascend and
  Dissolve. So "text fades in" really is the average deck. An AI that
  imitates the average produces exactly the deck the owner complained about.
- In the 60 most complex decks:
  - Complexity comes from **object lifecycles**, not exotic presets:
    - appear → disappear (replace in place)
    - fade → fade-out
    - wipe → fly-out
    - appear → motion path
    - custom path → spin
    - fade → transparency (dim after discussion)
    - fade → flash bulb → custom path → grow-and-turn-out
  - The mean is 1.94 effects per click; 27% of clicks move several objects.
  - Delay-staggered groups are rare (1.8%). Designers chain with
    with/after-previous instead.
- Morph appears in 11 of 797 decks, and fade is the dominant transition.

### What the tools now do with this

- **Director:**
  - Lifecycles are first-class: reveal → spotlight/dim → release; travel;
    swap; assemble → tour → release; Ken Burns; loops.
  - `style: "dynamic"` uses the presets complex decks actually use (Faded
    Zoom, Ascend, Rise Up, Expand, Grow & Turn).
  - Any beat may name any `ppt:` preset.
- **Forge:**
  - `office:<Name>` themes (light/dark) carry designer palettes, fonts and scale.
  - Vietnamese text is checked against fonts without full Vietnamese glyphs (`FONT_GLYPHS`).

## Motion tokens (T029)

`scripts/motion_tokens.py` translates open design-system easing into
PowerPoint. PowerPoint has only accel/decel fractions, so each curve is
fitted by its worst-case progress error:

- [IBM Carbon](https://carbondesignsystem.com/elements/motion/overview/) (`@carbon/motion`, Apache-2.0) fits within 1.5–8%.
- Material 3 emphasized curves (`@material/web` tokens, Apache-2.0) only fit within 18–44%.

Engine roles therefore use Carbon:

| Role | accel / decel | Used for |
|---|---|---|
| `standard` | 0.15 / 0.70 | the new keyframe default |
| `enter` | 0 / 0.90 | assemble, rise |
| `exit` | 0.35 / 0 | disperse |
| `expressive` | | |

`travel_ms(distance)` lengthens longer journeys (Material/Carbon guidance).

## Regenerate

```bash
powershell -File scripts/harvest_presets.ps1 -Output local-media/corpus/powerpoint_presets.pptx   # Windows + PowerPoint
python scripts/extract_presets.py local-media/corpus/powerpoint_presets.pptx -o knowledge/powerpoint_presets.json
python scripts/office_design_dna.py -o knowledge/office_design_kits.json                          # Windows + Office
python scripts/corpus_scan.py local-media/corpus/zenodo10k_index.json -n 800 -o local-media/corpus/zenodo_dna.jsonl
python scripts/knowledge_build.py local-media/corpus/zenodo_dna.jsonl -o knowledge/corpus_motion_design.json
python scripts/phrase_scan.py knowledge/corpus_motion_design.json local-media/corpus/zenodo_dna.jsonl -n 60 -o knowledge/motion_phrases.json
```

The Zenodo10K index comes from the Hugging Face API
(`/api/datasets/Forceless/Zenodo10K/tree/main/pptx?recursive=true`).

## Sources and limits

- [Zenodo10K](https://huggingface.co/datasets/Forceless/Zenodo10K) (PPTAgent):
  10,448 decks, 93% CC BY 4.0. Read only through XML parts; NC/ND decks
  were analysed but nothing from them is redistributed. These are research
  talks, so their design is average by intent: they say what is common, not
  what is beautiful.
- Microsoft Office themes are the "beautiful" reference. They are used for
  derived metrics only and are not redistributed.
- SlidesCarnival (CC BY 4.0) is designer-made, but its `robots.txt`
  disallows automated `/download/`. The owner can download favourites by
  hand into `local-media/` and run `deck_dna.py` on them.
- Commercial template marketplaces (Envato, SlideModel, Slidesgo/Freepik) are
  excluded by their licences and terms.
