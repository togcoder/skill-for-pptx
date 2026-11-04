# VisualStyle/1 — a design-style system for native PPTX

- **Task:** T067 [pptx], workstream *visual style system* (the same task also
  carries a deck-direction workstream in a sibling folder).
- **Date:** 2026-11-04. **Base:** `main` @ `7d3d9b8`.
- **Status:** EXPERIMENTAL. No product path imports this yet. Proposals for
  `theme_engine` / `slide_forge` are at the end.
- **Artifacts:** `artifacts/styles.pptx` (5 specimens, 631,684 B),
  `preview/all-styles.png`, `preview/styles.pdf`, `artifacts/measure.json`,
  `artifacts/lint.json`, `artifacts/style-tokens.json`.
- **Code:** `inputs/visual_style.py` (schema, presets, resolver, linter),
  `inputs/build_styles.py` (specimen builder), `inputs/prepare_assets.py`
  (one photograph → five treatments).

The owner's brief: *“Theme không chỉ có nền, có chữ mà còn có cả phong cách
thiết kế: hoạt hình, liquid glass, cartoon, tối giản, phức tạp…”* The current
`theme` object is palette + fonts + layout. It cannot say **material**,
**geometry**, **depth**, **texture**, **image treatment** or **motion
language** — so two decks with the same palette can feel like different
products, and a deck can be “on theme” and still not look designed.

This document defines those missing axes as a machine-readable contract, gives
five presets that validate against it, and proves five of them as native,
editable PowerPoint specimens with identical content.

---

## 1. What a style is (and is not)

A style is a **mapping from narrative roles to native PPTX object properties**,
not a mood board. It answers, for every object a generator can place:

| Question | Axis | Example values |
|---|---|---|
| What is the surface made of? | `material.kind` | flat, paper, glass, clay, collage, chrome |
| How does it catch light? | `depth.kind`, `shadow`, `bevel`, `specular` | flat, layered, 2.5D, 3D |
| What shape may an object have? | `geometry.language`, `corner_radius_pt`, `radius_mode` | sharp, rounded, blob, diagonal, mixed |
| Is there a surface pattern? | `texture.kind`, `texture.native` | none, grain, halftone, paper |
| How is a photograph allowed to look? | `image.treatment`, `mask`, `edge_pt`, `grade`, `area_share_max` | cut-out duotone, cool glass, posterized clay, BW, halftone |
| How does the deck move? | `motion.language`, 5 durations, `easing`, `overshoot`, `verbs` | editorial, fluid, bouncy, mechanical, kinetic |
| How much may a slide hold? | `density.words_max`, `elements_max`, `negative_space` | 18–40 words, 12–24 elements |
| Which colours mean what? | 9 colour **roles**, not a palette list | canvas, surface, text, muted, accent, accent_2/3, accent_text, ink |

A style is **not**: a list of adjectives (“modern, clean, premium”); a font
pair; a colour palette; a background image; a set of fixed coordinates. Those
are outputs of the system, not its definition.

### Content invariant

The specimen keeps one content unit across all five styles:

> **Claim:** “Không chỉ giải thích.” / “Mà cải tạo thế giới.”
> **Image:** C. Mác, 1875 (one portrait)
> **Fact 1:** 1845 — Luận cương về Phoiơbắc
> **Fact 2:** 11 — luận điểm, câu cuối là mệnh lệnh
> **Eyebrow:** LUẬN CƯƠNG 11 · 1845 · **Caption:** C. Mác · 1875

Only the style changes. That is the test: if the style is real, the same words
produce a different *reading experience*, not different content.

---

## 2. The schema

`inputs/visual_style.py` is the reference implementation (`VisualStyle/1`).
A preset is JSON; the resolver turns roles into build tokens; the linter
audits a built deck against its declared preset.

```json
{
  "schema": "visual-style/1",
  "id": "liquid-glass",
  "color": {
    "roles": {"canvas": "#070B1E", "surface": "#141B3A", "surface_alt": "#1E2750",
              "text": "#F2F6FF", "text_muted": "#AFC0E8", "accent": "#7CC7FF",
              "accent_2": "#B39DFF", "accent_text": "#DFF3FF", "ink": "#02040C"},
    "contrast_pairs": [["text","canvas"], ["text","surface"], ["accent_text","surface"]],
    "canvas_mode": "DARK",
    "tint_rule": "translucent white/role tints only"
  },
  "type": {
    "display": {"family": "Segoe UI Light", "weight": 300, "tracking_em": -0.015,
                "line_height": 1.06},
    "body": {"family": "Segoe UI", "weight": 400, "line_height": 1.3},
    "label": {"family": "Segoe UI Semibold", "weight": 600, "tracking_em": 0.12},
    "scale_pt": {"display": 40, "title": 30, "body": 18, "label": 11, "micro": 10}
  },
  "geometry": {"language": "rounded", "corner_radius_pt": 26, "radius_mode": "preset",
               "stroke_pt": 0.75, "image_frame": "rounded"},
  "material": {"kind": "glass", "fill": "translucent", "alpha_range": [0.08, 0.34]},
  "depth": {"kind": "layered", "layers": 3, "shadow": "ambient",
            "bevel_pt": 1.5, "specular": true},
  "texture": {"kind": "none", "native": "none", "opacity": 0.0},
  "image": {"treatment": "cool-glass", "mask": "rounded", "edge_pt": 0,
            "grade": {"mode": "duotone", "shadow": "#0A1030",
                      "highlight": "#DCE9FF", "posterize": null},
            "overlay": {"kind": "glass-sheet", "alpha": 0.28},
            "area_share_max": 0.32, "aspect": "4:5"},
  "motion": {"language": "fluid", "enter_ms": 620, "move_ms": 900,
             "emphasis_ms": 520, "morph_ms": 1500, "stagger_ms": 110,
             "easing": "expressive", "overshoot": 0.02,
             "verbs": ["fade", "float-in", "zoom"]},
  "density": {"words_max": 30, "elements_max": 18, "negative_space": 0.6}
}
```

### 2.1 Colour roles

| Role | Job | Rule |
|---|---|---|
| `canvas` | the field the slide sits on | exactly one per style; 55–70 % of area |
| `surface` | a raised plane (card, pane, medallion) | must be distinguishable from canvas |
| `surface_alt` | parchment / second paper / rim | never carries body text |
| `text` | primary type | ≥ 4.5:1 on canvas **and** surface |
| `text_muted` | captions, labels | ≥ 4.5:1 on canvas (if small) |
| `accent` | one focal action per slide | never used for paragraphs |
| `accent_2` | second voice, data, seal | optional; max one use per slide |
| `accent_3` | sticker/highlight only (optional) | never body text unless contrast passes |
| `accent_text` | type **on** accent fills | ≥ 4.5:1 on accent and accent_2 |
| `ink` | shadows, outline, deepest text | used as shadow colour, not fill at 100 % |

No invented hex: tints are alpha on a role colour. This is what makes a deck
recognisably one style and lets the linter prove it.

### 2.2 Type roles

Three roles (`display`, `body`, `label`) plus a 5-step scale
(`display / title / body / label / micro`). The validator enforces:

- max **2 superfamilies** per deck (`Segoe UI Light/Semibold/Black` count as
  one family — they are one design family in Office);
- **3–6 distinct sizes** (design-system band);
- `body ≥ 18 pt` (band) and never < 12 pt;
- title/body ratio 1.5–2.6 (note: the specimens sit at 1.5–2.0; Swiss uses
  54/18 = 3.0 and is reported as a deliberate warning, see §8).

### 2.3 Geometry, material, depth, texture

| Axis | Enumerated values | Resolved token |
|---|---|---|
| `geometry.language` | sharp, rounded, blob, diagonal, mixed | `radius_pt`, `radius_mode`, `stroke_pt` |
| `geometry.radius_mode` | none, preset, squircle | `smooth` → DeckCraft `shape.smoothCorners` |
| `material.kind` | flat, paper, glass, clay, collage, chrome | fill model + alpha range |
| `material.fill` | solid, gradient, translucent, pattern, mixed | OOXML fill type |
| `depth.kind` | flat, layered, 2.5D, 3D | layer count + shadow/bevel |
| `depth.shadow` | none, soft-contact, ambient, hard-offset | `{color, blur, dist, dir, transparency}` |
| `texture.kind` | none, grain, halftone, paper, pattern | `pattFill` preset or none |
| `texture.native` | none, `pattFill pct20`, image tile | how it is made |

### 2.4 Image treatment

The image axis has four independent decisions, which is why “image style” is
not one adjective:

1. **treatment** — cutout-duotone, cool-glass, posterized-clay, bw-editorial,
   halftone-collage;
2. **mask** — circle, rounded, blob, rect, none (baked into the PNG alpha);
3. **grade** — duotone endpoints, posterize levels, grayscale, gamma;
4. **overlay** — none, glass-sheet, halftone (native translucent panel or
   pattern fill over the picture);
5. **area cap** — `area_share_max` so a photo can never become the background.

The lab rule applies: crop → mask → grade **before** embedding. The raw
photograph never enters the deck; each treatment is a separate PNG with alpha.

### 2.5 Motion language

Five durations and one grammar per style:

| Token | What it controls |
|---|---|
| `enter_ms` | objects arriving |
| `move_ms` | motion paths, wipes, line draws |
| `emphasis_ms` | pulses, beats |
| `morph_ms` | slide-to-slide Morph |
| `stagger_ms` | order between items in a beat |
| `easing` | motion-token role (`scripts/motion_tokens.py`) |
| `overshoot` | ≤ 0.08 (design-system limit) |
| `verbs` | allowed effect vocabulary (3–5 presets, not 20) |
| `grammar` | the order of a beat (type → rule → facts → image) |

Motion is part of the style, not a post-process. A bouncy clay deck and a
mechanical Swiss deck must not share a 700 ms float-in.

---

## 3. The five presets

All five validate (`visual_style.validate_preset`) and all five are built in
`styles.pptx`. Contrast pairs are measured, not estimated.

### 3.1 `editorial-crimson` — Biên tập, đỏ son

| | |
|---|---|
| **Intent** | A printed journal page: one loud field, one serif voice, a gold thread. |
| **Canvas** | `#C1121F` crimson, 100 % flat; deep red `#7A0C14` for the plate. |
| **Type** | Palatino Linotype 42/34, Arial 20 body, 12/10 labels; tracking +0.16 em on labels. |
| **Geometry** | sharp: radius 0, hairline 1 pt, circle crop only for the portrait. |
| **Material / depth** | flat / flat; **no shadow, no bevel, no gradient** anywhere. Depth comes from overlap, not from light. |
| **Texture** | none. Paper is implied by the cream, not simulated. |
| **Image** | cut-out, crimson duotone `#4A0A10 → #D8A791`, circle mask, hard edge, 31 % of slide area. |
| **Motion** | editorial: enter 420, move 620, emphasis 380, Morph 1200, stagger 90; verbs wipe-up / wipe-left / fade / zoom; no overshoot. |
| **Do** | one field; cream type only; gold for small labels; portrait cropped by a circle. |
| **Don't** | shadows, rounded cards, a third family, gold body text (contrast 3.2:1). |
| **Native map** | solid fill; 1.25 pt line ring; circle mask baked in PNG alpha; `p:timing` wipes; 3 native text boxes per fact. |
| **Impossible / expensive** | real letterpress ink and paper grain need a raster tile; foil has no native material; per-glyph optical alignment is manual. |
| **Measured** | text/canvas 5.54:1, text/surface 9.89:1, accent_text/surface 8.22:1; 14 shapes, 1 picture, 93 % native, 4 type sizes, 31 words. |

This is the T066 language promoted to a preset. The specimen is a content
slide, not the cover, so the deck can be checked against a real page rather
than a title.

### 3.2 `liquid-glass` — Kính lỏng

| | |
|---|---|
| **Intent** | Frosted panes floating over a dark, coloured light field. |
| **Canvas** | `#070B1E`; two or three radial light fields (`#7CC7FF`, `#B39DFF`) at 26–62 % peak, fading by 78 % radius. |
| **Type** | Segoe UI Light 40, Segoe UI 18, Semibold 11; tracking −0.015 em display, +0.12 em labels. |
| **Geometry** | rounded 26 pt; 0.75 pt rim; the picture repeats the radius at 4:5. |
| **Material / depth** | glass: pane at 10 % white, rim at 30 %, **layered** (orbs → pane → image → sheen), ambient shadow, 1.5 pt bevel rim, one specular line. |
| **Texture** | none; the light field is the texture. |
| **Image** | cool duotone `#0A1030 → #DCE9FF`, 4:5 rounded card, glass sheet over the lower third (34 %→0), 22 % area. |
| **Motion** | fluid: enter 620, move 900, emphasis 520, Morph 1500, stagger 110; verbs fade / float-in / zoom; overshoot 0.02. |
| **Do** | one light source top-left; rim 30–45 % alpha; shadow large and low-alpha; text on the dark side, never on a bright orb. |
| **Don't** | glass on glass on glass; opaque cards (kills the material); 1 pt black outlines; saturated glow behind body text. |
| **Native map** | `gradFill` with per-stop `<a:alpha>`; `softEdge` on orbs (70 pt); `outerShdw` via `shadowProps`; `a:ln` at 30 %; `a:alphaModFix` only if a picture must be faded. |
| **Impossible / expensive** | **backdrop blur** (no filter in DrawingML); true refraction/dispersion; cursor-following specular; a real frosted blur needs a pre-blurred raster copy per panel. |

**Hardest of the five in native PPTX.** The material is defined by what the
background does *through* the pane, and PowerPoint has no backdrop filter — only
alpha. Every convincing glass deck is therefore an illusion built from
(a) a pre-composed background the author controls, (b) translucent fills,
(c) a rim and a specular line, (d) a large soft shadow. The moment a glass pane
sits over arbitrary moving content (video, Morph, another deck), the illusion
breaks, because the background cannot be blurred live.

### 3.3 `clay-cartoon` — Đất sét, hoạt hình

| | |
|---|---|
| **Intent** | A chunky matte toy: squishy corners, thick rims, no sharp edge anywhere. |
| **Canvas** | `#FFF3E2` cream; peach `#FFE2C6` and `#FFD1AE` blobs; terracotta `#E2725B`, teal `#1F7A6E`, mustard `#F2B24C`. |
| **Type** | Segoe UI Black 42, Semibold 18, 11/10 labels; tracking −0.02 em display. |
| **Geometry** | blob: 28–60 pt radius, `smoothCorners` 92 % (custGeom squircle), 6 pt cream rim. |
| **Material / depth** | clay: flat matte fills; 2.5D from a **5–6 pt bevel with matte material**, a 6–16 pt soft-contact shadow, no specular. |
| **Texture** | none; clay is smooth, the posterized photo supplies the grain. |
| **Image** | posterized 5-level warm duotone `#5A3A2E → #FFE9CF`, blob mask with 7 px feather, cream rim baked into the alpha, 22 % area. |
| **Motion** | bouncy: enter 300, move 520, emphasis 360, Morph 1000, stagger 80; verbs zoom / float-in / pulse; overshoot 0.06. |
| **Do** | one thick rim on the hero; matte everything; shadows short (dist 6–10 pt); rotate stickers 2–8°. |
| **Don't** | hairlines, glass transparency, more than three object colours, long text in the display face. |
| **Native map** | `roundRect` + `adj`; `smoothCorners` → `custGeom` (2 shapes, ~40 points each); `sp3d` + `bevelT` + `prstMaterial="matte"`; `outerShdw`; `a:ln` 6 pt. |
| **Impossible / expensive** | soft-body squash/stretch animation; fingerprint texture without a tile; ambient occlusion where two clay shapes touch. Each blob is a custGeom (2 in the specimen); a 20-blob slide becomes tedious to edit. |

Note: the cream rim is baked into the PNG because a native 6 pt picture border
would draw a **rectangle** around the blob frame. A native alternative is a
custGeom blob behind the picture; that doubles the path editing, so the
specimen chooses the baked rim and labels it.

### 3.4 `swiss-minimal` — Thụy Sĩ, tối giản

| | |
|---|---|
| **Intent** | A grid, one red, and type doing all the work. |
| **Canvas** | `#F7F7F5` paper; `#111111` ink; one red `#E30613`; nothing else. |
| **Type** | Arial Bold 54/28, Arial 18, 9/9 labels with +0.18 em tracking; tight −0.03 em display. |
| **Geometry** | sharp 0 pt; 0.5–0.75 pt rules; square image; 12-column rhythm at 56 pt margins. |
| **Material / depth** | paper / flat; **zero effects** (no shadow, no gradient, no transparency). |
| **Texture** | paper as a solid tint; no simulated fibre. |
| **Image** | BW editorial, 1:1, 214 pt square (8.8 % area), uncoated, uncropped by a shape. |
| **Motion** | mechanical: enter 250, move 400, emphasis 250, Morph 1000, stagger 60; only fade / wipe-left; zero overshoot. |
| **Do** | one axis, flush left; image small and quiet; rules 0.5–0.75 pt; numbers as data. |
| **Don't** | centred text, shadows, more than one accent use, rounded anything. |
| **Native map** | solid fills, 0.75 pt rectangles as rules, grayscale PNG, Arial. Zero effects — the cheapest and most editable specimen. |
| **Impossible / expensive** | a true baseline grid locked to the font; optical kerning per pair; a rule thinner than 0.25 pt survives export unpredictably. |

### 3.5 `maximalist-collage` — Cắt dán, cực đại

| | |
|---|---|
| **Intent** | A wall of torn paper, halftone and stickers that still reads in one pass. |
| **Canvas** | `#F4E9D8` paper + **8–10 % `pattFill pct20`** dots; red `#D7261B`, blue `#1D4ED8`, yellow `#FFD400`, ink. |
| **Type** | Arial Bold 36/30/92 (outlined ghost numeral), Arial 18, 10/8 labels; uppercase display. |
| **Geometry** | mixed: 4 pt radius on blocks, 3 pt ink outlines, rotations −8…+8°, one hard horizontal rail (the photo edge). |
| **Material / depth** | collage: paper layers at 100 %, tape at 55–65 %, **layered** 4 deep; shadows are paper-soft (transparency 40–65 %, blur 2–4 pt). |
| **Texture** | halftone as native pattern fill; no raster texture. |
| **Image** | 4-level ink/paper posterize, 4:5, 3 pt ink border, second smaller print at 55 % alpha; 19 % area (two pictures). |
| **Motion** | kinetic: enter 260, move 460, emphasis 300, Morph 1000, stagger 60; verbs wipe-up / zoom / fade; overshoot 0.03. |
| **Do** | anchor one straight horizontal rail; 3 text sizes plus the ghost numeral; rotate within ±8°; one focal sticker. |
| **Don't** | more than four accent blocks; halftone under body text; symmetry; clean vector icons. |
| **Native map** | `pattFill` (`pct20`, 9 % alpha), `outerShdw` with blur 0 or 2–4 pt, `a:ln` 3 pt, text `a:ln` outline on the ghost numeral, `a:alphaModFix` on the stamp, rotation. |
| **Impossible / expensive** | real torn-paper fibres; blend modes (multiply/screen); a true angled halftone screen; clipping masks across independent shapes. Each tear would be a custGeom; the specimen uses straight paper strips instead and says so. |

**Most fragile to edit** (as opposed to hardest to render): 20 shapes, 2
pictures, 6 type sizes, 8 rotated objects. Moving one strip forces the author
to re-check four overlaps.

---

## 4. Native PowerPoint mapping

What each style axis becomes in OOXML, and what cannot be built natively.

| Capability | Native? | OOXML / command | Limit found in T067 |
|---|---|---|---|
| Solid fill + transparency | yes | `a:solidFill/a:srgbClr/a:alpha` | alpha is per colour, not per shape |
| Gradient with transparent stops | yes | `a:gradFill/a:gsLst/a:gs/a:srgbClr/a:alpha` | **must be in schema order, before `a:ln`**; if appended after the outline, PowerPoint silently falls back to the theme fill (measured, §8) |
| Radial / path gradient | yes | `a:gradFill/a:path` + `a:fillToRect` | last stop maps to the *fill rectangle*, not the ellipse edge; leave 20 % of radius at alpha 0 or the ellipse edge shows a ring |
| Soft edge | yes | `a:effectLst/a:softEdge` | fades the edge, does **not** blur the object |
| Outer / inner shadow | yes | `a:outerShdw` / `a:innerShdw` | blur, distance, direction, alpha; no spread control |
| Glow / reflection | yes | `a:glow`, `a:reflection` | reflection is a fixed mirror, not a material |
| Bevel / 3D | yes | `a:sp3d/a:bevelT`, `a:scene3d` | whole shape, not per face; text gets a box bevel |
| Squircle corners | yes | `custGeom` via DeckCraft `shape.smoothCorners` | each shape becomes a freeform (~40 points) |
| Pattern fill (texture) | yes | `a:pattFill` (`pct5`…`pct90`, `dotGrid`, …) | a fixed screen; not an angled halftone |
| Text outline | yes | `a:rPr/a:ln` + `a:noFill` | stroke is centred on the glyph; thick strokes eat counters |
| Picture transparency | yes | `a:blip/a:alphaModFix` | python-pptx has no API; add XML |
| Picture recolor | partly | `a:blip/a:duotone` (theme colours) or presets | custom duotone endpoints are easier baked (done here) |
| Picture remove background | yes | DeckCraft `picture.removeBackground` | tolerance-based; fine for studio backdrops, not hair |
| Backdrop blur (glass) | **no** | — | no filter/blend node in DrawingML |
| Blur filter | **no** | — | only soft edge (edge alpha) |
| Blend modes (multiply/screen) | **no** | — | alpha only |
| Mesh gradient | **no** | — | linear/path/rectangular gradients only |
| Grain / paper fibre | **no** | — | raster tile or pattern fill |
| True halftone screen | **no** | — | pattern fill is a fixed grid |
| Chromatic aberration | **no** | — | bake it |
| 3D text extrusion | partly | `sp3d` on the text-box shape | the box is extruded, not the glyphs |
| Morph | yes | `p:transition/p14:morph` | needs matching object identity; see T064/T028 |

### Pipeline (why this order)

```
Pillow (crop, mask, grade) → python-pptx (composition) → DeckCraft CLI
(shape.effects: softEdge, threeD/bevel, smoothCorners) → python-pptx +
pptx_animator (native p:timing) → PowerPoint COM render
```

DeckCraft is used **only** as an effects writer: it can set bevels, 3D
materials, soft edges and squircles that python-pptx cannot reach. It is not
the last writer, because T059 measured that its `convert` path can disturb
timing and chart targets. Motion is applied after DeckCraft, by the lab's one
timing writer. The specimen round-trips cleanly: 5 slides, all names preserved, 49 native
effects; the DeckCraft pass changes package size by −0.5 %, and the final file
is 631,684 B.

---

## 5. Style lint (making “looks like the style” measurable)

`visual_style.py check deck.pptx --styles a,b,c` audits each slide against its
declared preset:

- **palette compliance** — every `srgbClr` must be a role colour (or an
  allowed blend); no stray “designer” colour;
- **font compliance** — every `a:latin` must be one of the preset families;
- **native share** — (shapes − pictures) / shapes;
- **raster share** — picture area / slide area ≤ `image.area_share_max`;
- **effect vocabulary** — counts `effectLst`, `sp3d`, `gradFill`, `pattFill`;
- **type sizes and word count** from the same file.

Specimen result (`artifacts/lint.json`):

| Slide | Style | Colours | Shapes | Pics | Native | Raster | Effects | sp3d | grad | pattern |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | editorial-crimson | 5 | 14 | 1 | 92.9 % | 30.9 % | 0 | 0 | 0 | 0 |
| 2 | liquid-glass | 6 | 19 | 1 | 94.7 % | 22.3 % | 8 | 0 | 4 | 0 |
| 3 | clay-cartoon | 9 | 18 | 1 | 94.4 % | 21.7 % | 7 | 5 | 0 | 0 |
| 4 | swiss-minimal | 4 | 16 | 1 | 93.8 % | 8.8 % | 0 | 0 | 0 | 0 |
| 5 | maximalist-collage | 9 | 20 | 2 | 90.0 % | 19.3 % | 8 | 0 | 0 | 1 |

`pass: true` on all five. This is the difference between “a style” and “a deck
that happens to use these colours”: the linter can fail a slide that drifts.

---

## 6. What the specimen proves

`artifacts/styles.pptx`, 5 slides, 960 × 540 pt (16:9), one content unit.

| Claim | Measurement | Rung |
|---|---|---|
| Five styles, one content unit | 165 words across 5 slides; 31–34 words/slide; identical claim, portrait, two facts | 1 |
| Native, editable construction | 14–20 shapes/slide; 90.0–94.7 % non-picture; all type is live text; 1–2 pictures/slide | 1 |
| Type discipline | 4–6 sizes/slide; 1–2 superfamilies; declared body 18 pt; words ≤ 34 | 1 |
| Palette discipline | linter: 0 unknown colours, 0 unknown fonts on all 5 | 1 |
| Contrast | all declared pairs ≥ 4.5:1 (lowest 4.76:1, maximalist accent_text/accent) | 1 |
| PowerPoint opens it | COM opens read-only, 5 slides, no repair; 152 ms | 4 |
| Native motion | COM: **49** main-sequence effects; durations match tokens exactly (0.25 / 0.26 / 0.30 / 0.42 / 0.62 / 0.90 s) | 4 |
| Render fidelity | 5 PNGs at 1920 × 1080; PDF 5 pages, 1,147,519 B | 5 |
| File size | 631,684 B for 5 styles + 5 treated images | 1 |
| Human review | **not reached** | — |

The five slides are not a deck to present; they are calibration plates. A real
deck uses **one** preset and repeats it.

---

## 7. How a generator should consume this

Proposed integration (not done; product paths need review):

1. `theme_engine` keeps palette/font synthesis but returns `style_id` plus the
   resolved tokens from `visual_style.resolve()`.
2. `slide_forge` reads `geometry`, `material`, `depth`, `texture`, `image` and
   `motion` from the tokens instead of hard-coded numbers:
   - `corner_radius_pt` → `shape.adjustments`;
   - `depth.shadow` → one `outerShdw` spec;
   - `image.treatment` → the pre-processing pipeline (`forge_assets` or a new
     `style_assets` module);
   - `motion.enter_ms/move_ms/stagger_ms` → `motion_director` plan;
   - `material.kind == "glass"` → refuse `area_share_max` above 0.35 and warn
     that backdrop blur is not native.
3. The critic gets a `STYLE-DRIFT` rule using `visual_style.check_deck`.

Refusal cases the schema should make explicit: `material.kind = glass` +
`depth.kind = flat` is a contradiction (glass without light); `texture.kind =
grain` with `texture.native = none` is a promise PowerPoint cannot keep;
`geometry.language = blob` with `radius_mode = none` is a shape that has no
material logic.

---

## 8. Negative results and open questions

1. **Gradient transparency failed first, for a non-obvious reason.** A
   `gradFill` appended after `a:ln` is ignored by PowerPoint, and the shape
   falls back to the theme fill — visually a solid, saturated orb. Inserting
   the same `gradFill` before `a:ln` makes the alpha work. This is an OOXML
   child-order bug trap, not a PowerPoint limitation. Any generator that adds
   fills after lines will ship “why is my glass opaque?” decks.
2. **Radial gradients show a ring at the ellipse edge** if the last stop is at
   100 % of the *fill rectangle*. The fix is to reach alpha 0 by ~78 % of the
   radius. Both are measured in the specimen history, not theory.
3. **Glass cannot blur what is behind it.** The specimen fakes frost with a
   10 % pane, a 30 % rim, a specular line and a pre-graded image. If the pane
   sits over live content, the illusion is only “tinted glass”, never frosted.
4. **Clay rims are baked, not native.** A 6 pt picture outline around a blob
   mask draws a rectangle. The native alternative (custGeom behind the image)
   doubles the path editing. The specimen labels the rim as image treatment.
5. **Maximalist is the most editable-fragile**, not the hardest to render.
   Twenty rotated objects with paper shadows survive PowerPoint but are slow to
   retune; Swiss is the cheapest (zero effects) and the easiest to edit.
6. **Easing is not proven.** The specimen proves effect vocabulary, trigger and
   duration via COM; PowerPoint's preset easing is inside each effect preset,
   not in our timing XML. `motion.easing` remains a plan-level token until a
   frame-level test (CreateVideo) compares curves.
7. **No Morph in the specimen.** Five different styles in one deck would make a
   Morph look like an accident; `morph_ms` is a token for real decks, not
   exercised here.
8. **Swiss title/body = 3.0** exceeds the design-system band (1.5–2.6). It is
   deliberate (54 pt title / 18 pt body) and flagged by the validator as a
   warning; the band may need a per-style exception or Swiss needs a 40 pt
   title. Not resolved.
9. **Six sizes in liquid-glass and maximalist** sit at the top of the 3–6 band.
   The ghost numeral (92 pt) is the sixth in maximalist; without it the slide
   loses its middle layer.
10. **Rung 6 missing.** PowerPoint rendered and exported the deck, but no human
    reviewed the five plates on a projector.
11. **The specimen does not set theme fonts or theme colours.** Five styles in
    one file cannot share a theme; every run carries explicit formatting. A real
    single-style deck should also write `a:fontScheme` / `a:clrScheme` so new
    objects inherit the style. Not done here.

---

## 9. Files

| Path | What |
|---|---|
| `inputs/visual_style.py` | schema, 5 presets, resolver, contrast + lint |
| `inputs/build_styles.py` | token-driven builder, DeckCraft manifest, motion |
| `inputs/prepare_assets.py` | one photograph → 5 treatments (rembg, duotone, masks) |
| `inputs/render.ps1`, `inputs/measure.ps1`, `inputs/measure.py` | PowerPoint render + COM/static measurement |
| `artifacts/styles.pptx` | 5 specimens |
| `artifacts/style-tokens.json` | resolved tokens for all presets |
| `artifacts/lint.json` | style-compliance audit |
| `artifacts/measure.json`, `artifacts/com.json` | size, shapes, effects, open time |
| `preview/slide-01..05.png`, `preview/all-styles.png`, `preview/styles.pdf` | renders |
| `REPORT.md` | frame, method, evidence, negative, next |
| `inputs/SOURCES.md` | image, font, tool, licence |
