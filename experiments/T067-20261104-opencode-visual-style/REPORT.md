# T067 [pptx] — Visual style system: five materials, one content unit

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max), builder subagent.
- **Date:** 2026-11-04. **Base:** `main` @ `7d3d9b8`.
- **Branch:** `work/T067-opencode-deck-director`.
- **Request (owner):** *“Theme không chỉ có nền, có chữ mà còn có cả phong cách
  thiết kế: hoạt hình, liquid glass, cartoon, tối giản, phức tạp…”*
- **Status:** EXPERIMENTAL deliverable for review. No product path changed, no
  INDEX/claim edit, nothing merged. This folder is the *visual style*
  workstream; the sibling `experiments/T067-*-deck-director/` folder belongs to
  the deck-direction workstream of the same task.
- **Main document:** [`style-system.md`](style-system.md) — the schema, the five
  presets, the native mapping and the linter.

## Frame

- **Question.** Can “visual style” become a **system** a generator can execute
  and a checker can audit — not a mood board — and can five genuinely different
  styles be built from native PowerPoint objects with one content unit?
- **Hypothesis.** If style is decomposed into colour roles, type roles,
  geometry, material, depth, texture, image treatment, motion language and
  density, then:
  1. the same builder can emit radically different artefacts from tokens alone;
  2. every style remains editable, with no raster background;
  3. a linter can prove a deck has not drifted from its declared style.
- **Falsifiers.**
  - the five outputs still look like one template with different colours;
  - a style needs prohibited tricks (full-bleed raster background, baked text)
    to look right;
  - the schema is descriptive only and cannot generate a deck;
  - the linter cannot tell a compliant deck from a drifted one;
  - the deck cannot be opened/rendered by PowerPoint or loses editability;
  - motion tokens do not reach the native timeline.

## Frozen input

- **Content unit (identical in all five slides):** claim “Không chỉ giải
  thích.” / “Mà cải tạo thế giới.”; one portrait (C. Mác, 1875); two facts
  (1845 — Luận cương về Phoiơbắc; 11 — luận điểm, câu cuối là mệnh lệnh);
  eyebrow “LUẬN CƯƠNG 11 · 1845”; caption “C. Mác · 1875”.
- **Image:** `Karl Marx 001.jpg`, Wikimedia Commons, public domain, downloaded
  2026-11-04. Background removed with `rembg` 2.0.86 (U2Net); cropped, graded
  and masked five ways by `inputs/prepare_assets.py`. Raw file stays in the
  git-ignored `workspace/`; only treated PNGs are embedded.
- **Design numbers:** `knowledge/design_system.json` v1.1.0 bands (type 3–6
  sizes, body 18–40 pt, one/two families, enter 250–700 ms, move 400–1200 ms,
  Morph 1000–1600 ms, 45 words).
- **Environment:** Windows 11, PowerPoint 16.0 build 17932 (COM), Python 3.13,
  python-pptx 1.0.2, Pillow 13.0.0, lxml, pypdf 6.13.0,
  DeckCraft CLI 0.15.0 (`D:\artcraft\DeckCraft\deckcraft-cli.exe`).
- **Not available:** a human review of the five plates, a second PowerPoint
  build, a projector/room measurement, easing-curve frame comparison.

## Method

```powershell
# 1. one photograph -> five treatments (circle, rounded, blob, BW, xerox)
python experiments/T067-20261104-opencode-visual-style/inputs/prepare_assets.py `
  --raw workspace/marx_raw.jpg --cut workspace/marx_cut.jpg

# 2. tokens -> base deck (native shapes, text, pictures, gradients, patterns)
python .../inputs/build_styles.py --skip-effects

# 3. DeckCraft effects writer: softEdge, sp3d/bevel, smoothCorners, shadows
deckcraft-cli run --in .../_base.pptx --cmd-file .../deckcraft-effects.txt `
  --save .../_effects.pptx

# 4. native motion, after DeckCraft (its convert path is not a safe last writer)
python .../inputs/build_styles.py --motion

# 5. PowerPoint render + COM measurement + style lint
powershell -File .../inputs/render.ps1 -Pptx .../styles.pptx -OutDir .../preview
powershell -File .../inputs/measure.ps1 -Pptx .../styles.pptx -Out .../com.json
python .../inputs/measure.py
python .../inputs/visual_style.py check .../styles.pptx `
  --styles editorial-crimson,liquid-glass,clay-cartoon,swiss-minimal,maximalist-collage
```

1. **Schema first.** `visual_style.py` encodes 9 colour roles, 3 type roles,
   5 geometry enumerations, 4 depth modes, 5 texture kinds, 5 image treatments,
   5 motion languages and density limits. Validation rejects bad contrast,
   > 2 superfamilies, > 6 sizes, body < 12 pt, motion outside the design-system
   limits, and unknown enum values. All five presets pass.
2. **Composition from tokens.** `build_styles.py` imports the resolver; no hex,
   radius or duration is written in the builders. Text sizes are fitted with
   Pillow metrics against the real system font files, so no display text
   overflows its sticker.
3. **One image, five treatments.** Duotone endpoints, posterize level, mask,
   feather and rim are all in the preset. Editorial uses a cut-out on a cream
   disk; glass a 4:5 indigo card; clay a blob medallion with a baked cream rim;
   Swiss a square BW document; collage a 4-level xerox plate plus a faded second
   print.
4. **Native only.** Every plane, rule, pill, blob, sticker and glass pane is a
   PowerPoint shape. No raster background; the photographs are elements, capped
   at 8.8–30.9 % of slide area.
5. **DeckCraft only for unreachable effects.** `shape.effects` supplies soft
   edges, matte 3D bevels and ambient shadows; `shape.smoothCorners` turns the
   clay tiles into squircles. Motion is written **after** DeckCraft by
   `pptx_animator`, because T059 measured that DeckCraft is not a safe last
   writer for timing.
6. **Measure, don't judge.** PowerPoint COM opens the deck, counts effects and
   reads their durations; `measure.py` counts shapes, pictures, text boxes,
   type sizes, words and effect-token counts; the linter checks palette/fonts/
   raster share against the declared presets.

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| Five distinct styles, one content unit | 5 slides, 165 words, 31–34 words/slide; same claim, portrait and two facts on each | 1 |
| The schema is executable | `build_styles.py` imports `visual_style.resolve()`; no literal hex/radius/duration in the builders; 5/5 presets validate | 1 |
| Style is auditable | `visual_style.py check`: 0 unknown colours, 0 unknown fonts, raster within cap on all 5 slides → `pass: true` | 1 |
| Native, editable output | 14–20 shapes/slide; 1–2 pictures/slide; native share 90.0–94.7 %; all type is live text | 1 |
| Type discipline | 4–6 sizes/slide; 1–2 superfamilies; declared body 18 pt; 31–34 words/slide | 1 |
| Contrast | measured pairs 4.76:1 (lowest) to 18.9:1; no text pair below 4.5:1 | 1 |
| PowerPoint opens it | COM opens read-only, 5 slides, no repair, **152 ms** | 4 |
| Native motion reaches the timeline | COM: **49** main-sequence effects; durations 0.25 / 0.26 / 0.30 / 0.42 / 0.62 / 0.90 s, matching the five presets | 4 |
| Render fidelity | 5 PNGs at 1920×1080; PDF **5 pages**, 1,147,519 B; 773 ms export | 5 |
| Editability / file size | **631,684 B** for 5 styles + 5 treated images; 2 custGeom shapes (clay squircles) | 1 |
| Human review | **not reached** — the plates were rendered, not judged in a room | — |

Style-specific costs (from `artifacts/lint.json`):

| Style | Shapes | Pictures | Native | Raster | `effectLst` | `sp3d` | gradient | pattern |
|---|---|---|---|---|---|---|---|---|
| editorial-crimson | 14 | 1 | 92.9 % | 30.9 % | 0 | 0 | 0 | 0 |
| liquid-glass | 19 | 1 | 94.7 % | 22.3 % | 8 | 0 | 4 | 0 |
| clay-cartoon | 18 | 1 | 94.4 % | 21.7 % | 7 | 5 | 0 | 0 |
| swiss-minimal | 16 | 1 | 93.8 % | 8.8 % | 0 | 0 | 0 | 0 |
| maximalist-collage | 20 | 2 | 90.0 % | 19.3 % | 8 | 0 | 0 | 1 |

## Findings

1. **The five styles are not five palettes.** At thumbnail size the reading
   order changes: editorial is a page (portrait as a medallion), glass is a lit
   stage (portrait behind a pane), clay is a toy (portrait as a blob sticker),
   Swiss is a document (portrait as evidence), collage is a wall (portrait
   repeated). Same words, different hierarchy.
2. **The hardest style in native PPTX is `liquid-glass`.** The material depends
   on what the background does through the pane, and DrawingML has no backdrop
   blur, no blend modes and no refraction. The specimen fakes frost with a 10 %
   pane, a 30 % rim, a specular line, a large low-alpha shadow and a pre-graded
   image. Move that pane over live content and the illusion collapses to tinted
   transparency. Clay is second: its best look needs a `custGeom` squircle and
   `sp3d` matte bevel per object, but those are native and stable.
3. **A real PPTX bug trap was found and fixed.** A `gradFill` appended after
   `a:ln` is ignored and PowerPoint falls back to the theme fill; the first
   glass build rendered opaque blue orbs. Inserting `gradFill` before `a:ln`
   makes per-stop alpha work. Radial gradients additionally ring at the ellipse
   edge unless alpha reaches 0 by ~78 % of the radius. Both are written up in
   `style-system.md` §8.
4. **Texture has exactly one native mechanism: `pattFill`.** It is a fixed
   screen (dots/lines), not a real halftone; it nevertheless gives collage a
   believable paper dot at 9 % alpha. Grain and fibre remain raster tiles.
5. **Native share is not the same as editability.** All five are > 90 % native,
   but clay's squircles are 40-point freeforms and collage has 20 rotated
   objects. Swiss (16 shapes, zero effects) is the cheapest to retune; collage
   is the most fragile.
6. **Motion is part of the style and it reached the timeline.** The five
   presets' `enter_ms` values (420 / 620 / 300 / 250 / 260) are exactly the
   durations COM reads back from the 49 effects. A deck cannot be “clay” with a
   620 ms glass float.

## Negative results and limitations

1. **Glass is fake frost, not blur.** No native backdrop filter exists; a real
   frosted pane needs a pre-blurred raster copy of whatever is behind it.
2. **Clay rims are baked.** A 6 pt picture outline around a blob mask draws a
   rectangle, so the cream rim is part of the PNG alpha. The native alternative
   (a larger custGeom blob behind the image) doubles the path editing.
3. **Maximalist uses straight paper strips, not torn edges.** A real tear is a
   custGeom per edge; the specimen trades it for speed and says so.
4. **Easing is not frame-verified.** COM proves effect vocabulary, trigger and
   duration; PowerPoint's easing lives inside the effect preset, not in our
   `p:timing`. The `motion.easing` token remains plan-level.
5. **Swiss title/body = 3.0** is outside the 1.5–2.6 band (54 / 18 pt). The
   validator flags it; either the band needs a per-style exception or Swiss
   needs a smaller title. Left open deliberately.
6. **Two styles sit at six type sizes** (glass, maximalist) — the top of the
   band; maximalist's sixth is the 92 pt ghost numeral.
7. **No Morph in the specimen.** Five different styles in one deck would make a
   Morph meaningless; `morph_ms` is defined per preset but not exercised here.
8. **Rung 6 missing.** PowerPoint rendered and exported, but no human judged the
   five plates on a projector.
9. **The schema is not wired into any product path.** `theme_engine` and
   `slide_forge` still speak palette + fonts; integration is a proposal (§7 of
   `style-system.md`) and needs review.
10. **Theme-level fonts/colours are not set.** Five styles in one file cannot
    share a theme, so every run is explicitly formatted; a real single-style
    deck should also write `a:fontScheme` / `a:clrScheme`.

## Next

1. **Human eye test** of the five plates at 1920×1080 and on a projector; mark
   which style reads at 6 m and which is only a screen style.
2. **Wire one axis at a time** into `slide_forge`: geometry first (radius +
   smooth), then depth (one shadow spec), then image treatment, then motion
   tokens. Each step gets its own review.
3. **A `STYLE-DRIFT` critic rule** using `visual_style.check_deck`, with a
   tolerance for derived tints.
4. **Glass without cheating:** test a pre-blurred backdrop baked per slide and
   measure whether the illusion survives Morph; if it does not, restrict glass
   to static slides and record it as a hard limit.
5. **Fix Swiss type ratio** (54 → 44 pt title or accept a band exception) and
   re-run the linter.
6. **Second image test:** a portrait with hair against a busy background, to see
   where `rembg` + blob masks fail; the Marx studio portrait is an easy case.

## Scope and process

- No product path was modified: `theme_engine.py`, `slide_forge.py`,
  `knowledge/design_system.json`, `motion_*`, `pptx_animator.py` are untouched.
- `research/tasks/INDEX.md` and the T067 claim were not edited by this
  workstream.
- No merge, no push, no other worktree touched; T066 was read only.
- **Branch footprint:** this workstream is 5.7 MB across 31 files (largest
  file 1.15 MB); the sibling deck-director folder tracks 16.3 MB, so
  `check_layout.py` warns that T067 is over the 10 MB/task cap. The cap is a
  shared-task budget, not a defect in the specimens.
- Review requested for the schema and the five presets before any adoption.
  The code is EXPERIMENTAL and lives only in this experiment folder.
