# T028 — Morph Studio and professional text tricks

## Frozen input

- Owner request (2026-10-08): the motion is good but "something is still
  missing". Tutorial videos show professional slides with smooth motion and
  hundreds of tips and tricks, for example giving two different shapes the
  same name so Morph animates one into the other. The owner wants slides at
  that level.
- Claude Code cloud session on branch `claude/blissful-pasteur-gmll59`. Base
  commit `35afaa3` (T024, see `base-commit.txt`); T024 is not merged to main.
- Parallel Claude branches exist and are not merged:
  `work/T024-claude-picture-motion-graphics`, `work/T026-claude-forge-assets`
  and `work/T027-claude-design-motion-corpus`. The parallel T024 reuses the ID
  of this branch's T024 (layers and script). Nothing here touches them.
- Hypotheses:
  1. The tutorial tricks are mostly *Morph* tricks (forced `!!` pairing,
     off-slide staging, camera moves, shape morphs). They can be planned and
     written automatically on top of an existing deck, without changing its
     original slides beyond names and off-slide copies.
  2. Several in-slide text tricks (typewriter, word by word, rise from a line,
     highlighter, underline) can be built from native effects plus generated
     helper shapes in the deck's colours.

## What was built

| Area | File | Content |
|---|---|---|
| Morph Studio | `scripts/morph_studio.py` (new) | Package editing: slide duplication (deep-copied charts, notes dropped, slide tagged `__scene:`). Continuity between consecutive slides: pairs the same picture, the same text, title to title and existing `!!` names, and renames along the whole chain so identity holds across three or more slides. Staging puts off-slide copies so new objects fly in and leaving objects fly out; objects inside a container travel with it as one piece. Scenes: `camera-zoom` (push-in and pull-back with type, line widths and insets scaled), `card-expand` (the card grows into a panel on top of its neighbours; content keeps even margins) and `pan` (carousel). Scene slides start from the source's end state. Every scene needs a reason. Also: `propose`, `apply`, `verify_scenes`, the `unsettled` end-state check, and a simulated Morph preview |
| Text tricks | `pptx_animator.py`, `motion_engine.py`, `motion_components.py`, `motion_director.py` | `type-on` (Appear by letter, 35 ms), `by: word/letter` on any entrance (`p:iterate`), recipe `rise` with a `mask` component. The mask sits under the last estimated text line and is painted in the container's fill or the slide background. The rise is refused if the mask would cover another object; when the room is clipped, it falls back to a shorter fade-rise. Also `highlight` (marker behind the first line) and `underline`, both with `wipe-right`. The cinematic draft adds the highlighter to conclusions and the underline to section labels |
| Script layer | `motion_script.py` | When a script ends during a spotlight tour, an unscripted closing click releases it. This click is reported as the gap `settle-click-without-line` |
| Catalog | `skills/pptx-motion-director/references/pro-techniques.md` (new) | 50 techniques: Morph, entrances and text, focus and compound motion, ambient, and craft rules. Each is marked as built here, on a parallel branch, or manual |

## Reproduction

Python 3.11.15, lxml 6.1.3, LibreOffice 24.2.7.2, poppler, ImageMagick 6. No
PowerPoint.

```bash
E=experiments/T028-20261008-claude-morph-studio
# Report deck: hand-refined director plan (rise on the takeaway, type-on result), then Morph
python3 scripts/motion_director.py apply tests/fixtures/report_deck.pptx $E/report-director.json -o $E/output/step1_report_inslide.pptx --force
python3 scripts/morph_studio.py propose $E/output/step1_report_inslide.pptx -o $E/report-morph.json
#   + scene: card-expand "KPI Card 1" (see report-morph.json)
python3 scripts/morph_studio.py apply $E/output/step1_report_inslide.pptx $E/report-morph.json -o $E/output/T028_report_pro.pptx
# Showcase deck: script-driven cinematic pass, then Morph with a camera push-in on the 2x2 grid
python3 scripts/motion_director.py auto tests/fixtures/motion_showcase_deck.pptx -o $E/output/step1_showcase_inslide.pptx \
  --script tests/fixtures/showcase_script.md --style cinematic --fill-gaps --write-notes --force
python3 scripts/morph_studio.py propose $E/output/step1_showcase_inslide.pptx -o $E/showcase-morph.json
#   + scene: camera-zoom "Quadrant Grow" (see showcase-morph.json)
python3 scripts/morph_studio.py apply $E/output/step1_showcase_inslide.pptx $E/showcase-morph.json -o $E/output/T028_showcase_pro.pptx
python3 scripts/morph_studio.py preview <deck> --slide N -o preview/<name>.gif --sheet preview/<name>.png
python3 scripts/lo_timing_crosscheck.py <deck> --output lo-<name>.json
```

| File | SHA-256 |
|---|---|
| `output/T028_report_pro.pptx` | `6debf60a709189f6db2337c51f0aa80545ec8e549729fbfc22fb8ad573a0add1` |
| `output/T028_showcase_pro.pptx` | `8d09f0e7b5f7b0607be4423aabbf5928501f9498de855ed55b403877a5d70a80` |
| `output/step1_report_inslide.pptx` | `5871bb5c3fe59a5fe88f49f073738eefa877da5eee7c38f168e64c4086de8383` |
| `output/step1_showcase_inslide.pptx` | `08b97719ed199f4d6f8aa158cb4e4339b4c3c22777eda1c41da8576934a4c8f3` |

## Evidence (structural + simulated; not PowerPoint playback)

### Report deck → `T028_report_pro.pptx` (7 → 8 slides)

| Moment | Technique | Preview |
|---|---|---|
| 1 → 2 and every later slide | Title glide (title to title `!!` pairs, one identity along the chain) | `report-morph-s2-title-glide` |
| Slide 3 → scene | Revenue card grows into a panel on top of the other cards, which fade behind it; value and label keep even margins | `report-morph-s4-card-expand` |
| Scene → "Revenue by channel" | Panel, value and label leave downward together | `report-morph-s5-panel-out` |
| "Revenue by channel", click 2 | Card zooms in, then the takeaway rises line by line out of an invisible line inside the card | `report-s5-rise` |
| "How we fixed fulfilment" | Rail and token journey; the result types on letter by letter, then the highlighter sweeps | `report-s6-typeon-highlight` |

`verify_scenes`: ok. All 7 original slides keep their objects, text and
geometry; only `!!` renames and fully off-slide staging copies were added.

### Showcase deck → `T028_showcase_pro.pptx` (8 → 10 slides)

| Moment | Technique | Preview |
|---|---|---|
| Market quadrants, clicks 1–4 | Assemble, then a halo-guided spotlight tour. The new closing click restores the full grid and fades the halo | `showcase-s6-tour-settle` |
| Quadrants → camera | Push-in on Grow: type grows like a camera, neighbours slide out of frame, no stray halo | `showcase-morph-s7-camera-in` |
| Camera → overview | Pull-back to the full grid | `showcase-morph-s8-camera-out` |
| → "Our roastery" | Same picture pairs and shrinks aside; the bullets are already in place | `showcase-morph-s10-picture` |

### Independent reader (LibreOffice)

- `lo-T028_report_pro.json`: 33 entrances, 9 motion paths, 4 emphasis
  effects and 1 exit.
- `lo-T028_showcase_pro.json`: 16 entrances, 28 motion paths, 39 emphasis
  effects and 2 exits.
- LibreOffice has no Morph. It reads every Morph slide's `mc:Fallback` as
  Fade (8/8 and 10/10 slides after the first), so the markup degrades as
  intended in readers without Morph.

### Defects found by looking at the previews, fixed with regression tests

1. **Card expand ran under its neighbours.** The other cards faded on top of
   the growing card, and the content stretched with the card's 3:1
   horizontal scale, leaving a wide empty panel. Fix: the card moves to the
   top on the scene slide, content scales uniformly (even margins), and
   leaving objects fade behind paired ones in the preview.
2. **The panel broke apart on exit.** The card left downward while its value
   left upward, because each object took its own nearest edge. Fix: staging
   is rigid, so contained objects take their container's offset.
3. **The rise was a fade in disguise.** The mask sat under the tall text
   *box*, not under the text, so inside the card the rise had no room. Fix:
   `text_block()` estimates the visible lines (anchor, wrapping, font size).
   The mask now sits under the last line and the rise distance comes from
   the line, so the text emerges line by line. A filled shape still counts
   as a whole box, so the refusal case still refuses.
4. **A stray halo and a snap-back at the camera move.** The duplicated scene
   copied the halo, which had already finished its tour. The script also
   ended mid-tour with three quadrants still dimmed. Morph starts from the
   authored layout, so they would snap back. Fix: scene slides drop objects
   hidden in the source's end state. The script layer adds a settle click
   when a script ends during a tour. `apply` reports `unsettled` slides
   (objects that end moved, scaled, turned or dimmed before a Morph).
5. **Already-directed decks lost their scene suggestions.** Generated helpers
   (`__gen_`) and animated objects hid the 2×2 grid. Fix: `_units` ignores
   generated helpers, and `propose` looks at layout regardless of animation.

### Smoke test on every repository deck (34 PPTX files)

Pipeline: `motion_director.py auto --style cinematic --ambient`, or the source
deck when the director has nothing to add. Then `morph_studio.py propose`,
with **every** suggestion accepted as a scene, then `apply`.

The first run found two problems:

6. **Package-absolute relationship targets.** 18 decks written by other
   generators (`Target="/ppt/slides/slide1.xml"`) crashed with
   `KeyError 'ppt/ppt/slides/…'`. Fix: `Package.resolve` handles absolute
   targets.
7. **Too many suggestions.** There were 332 suggestions, 327 of them
   card-expand, with up to 13 on one slide. Fix: at most one idea per slide,
   with priority camera-zoom > pan > card-expand. Card-expand is proposed
   only for a set of 2–6 cards that hold content, and it picks the card with
   the headline number. The deck cap is about one idea per three slides. On
   the report deck the automatic proposal is now the same card a human
   picked (KPI Card 1), plus the four-step pan.

After the fixes, **34/34 decks** pass propose and apply with all suggested
scenes accepted; `verify_scenes` is ok on all of them. There are 24
suggestions in total (13 card-expand, 7 pan, 4 camera-zoom). LibreOffice
converts all 34 outputs, and every page count equals the slide count. 8
slides are reported `unsettled`.

### Still flagged (accepted)

`T028_showcase_pro.pptx` slide 5: "Order token" ends at its last stop. When
Morph starts it snaps back to its authored position. We keep it parked
there because the presenter talks about the delivered order, and the next
slide does not pair it. The report records it.

### Tests

**219 tests pass** (`python3 -m unittest discover -s tests`). There are 14
in `tests/test_morph_studio.py`: package and absolute targets, selective
proposals, techniques, card-expand layout and rigid exit, rise line, text tricks, and Morph preview. The script test now
checks the settle click.

Native playback: null.

## Limitations

- **PowerPoint has not played any of this.** Unverified: Morph pairing of
  `!!` names across three slides; z-order of leaving objects during Morph;
  whether Morph starts from the authored layout (assumed; the `unsettled`
  check relies on it); `p:iterate` timing; mask colours against themed
  backgrounds.
- **The Morph preview is a simulation.** It is a linear box and font-size
  interpolation with smoothstep easing. PowerPoint's Morph also interpolates
  rotation, fills and geometry, and it pairs text by word or character
  (`byWord`/`byChar`), which the preview does not show.
- **Text extent is estimated.** The estimate uses average glyph width and
  1.2 line spacing. Very narrow fonts, mixed sizes, or autofit text can put
  the mask line a little off; `verify` still blocks overlap with other
  objects.
- **The card-expand panel has no new content.** It enlarges what the card
  holds; detail must come from the deck or the user, never invented.
- **Scene suggestions are conservative.** Camera zoom is suggested for 2×2
  grids, card-expand for cards and pan for rows of four or more. Other
  catalog techniques (parallax, rotation morph, zoom-out reveal) are manual.

## Next

1. Native gate on the parallel branch's PowerPoint render loop. Play both
   outputs and compare with `preview/*`. Record pairing, z-order, snap-back
   and the iterate timing.
2. Integrate the parallel branches. T027's 198 native presets and T024's
   picture motion would fill the "branch" rows of the catalog; resolve the
   T024 ID collision first.
3. Scene proposals for timelines (pan) and photos (zoom-out reveal), plus a
   `settle` option in Morph Studio that adds the release click itself when
   the director did not.
