# T063 [pptx] — Forge debt users see: print-safe count-ups, highlight alignment, type scale, MOT-SETTLE

- **Agent / model:** OpenCode (DeepSeek V4.1 Flash Max), T058–T065 programme.
- **Date:** 2026-11-04. **Base:** `main` @ `ac5b45e` (`T058-T065: claim the next research programme`).
- **Branch:** `work/T063-opencode-forge-debt`.
- **Brief:** `experiments/T057-20261104-claude-leader-review/REPORT.md`, section “T063 [pptx] Forge debt that users see”.
- **Scope:** `scripts/slide_forge.py`, `scripts/text_metrics.py`, `scripts/motion_engine.py`,
  `scripts/motion_components.py`, `scripts/counter_component.py`, `scripts/motion_director.py`,
  `scripts/pptx_animator.py`, `scripts/forge_qa.py`, tests; plus this experiment.
- **Review:** requested from Argon (different model family), per the T057 table.

## Frame

### Question

Can the five example Forge decks lose the four defects a user actually sees —
ghost count-up frames in print/PDF/Morph, a highlight marker that ignores
horizontal alignment, 13–15 type sizes, and MOT-SETTLE warnings — without
changing the deck specs or removing native motion?

### Hypothesis

1. If the count-up proxies sit **below** an opaque final-value shape, then
   edit view, PDF and static Morph frames show one value, while the slide show
   still reveals the proxies one at a time. The final value must be last in the
   z-order and painted with the container colour.
2. If the highlight geometry reads the paragraph alignment and measures the
   real font instead of the text box, the marker follows centred and
   right-aligned words.
3. If every text run is snapped to the Office kit's `type_scale_pt` (plus the
   design-system `kpi_stat` display token when the deck has a KPI), a deck uses
   3–6 sizes instead of 13–15.
4. If Ken Burns returns to its authored frame before Morph, and a generated
   process token is authored at its last stop (T034's “author at destination”
   fix), Morph has nothing to snap.

### Falsifiers

- PDF/PNG still shows two or more count-up values on one KPI.
- The PowerPoint CreateVideo frames no longer show intermediate count-up values
  (the print fix destroyed the motion).
- A centred or right-aligned highlight marker is still offset by more than
  0.01 of slide width from the measured text.
- Any example deck still reports `TYP-SIZES` or `MOT-SETTLE` as a warning.
- Any example deck fails to build, or the test suite regresses.

All five falsifiers were tested; none held. Details in Evidence and Negative
results.

### Domain lens

PowerPoint is the target: OOXML PresentationML timing, `p:set` visibility,
z-order (`p:spTree` child order), text-frame alignment, `p14:morph`, and
PowerPoint 16.0's own PDF/PNG/CreateVideo renderers. The critic is a
measurement tool, not a substitute for PowerPoint; every visual claim below
names which renderer produced the pixels.

### Transfers

- **Type-scale transfer from Office designer kits** (`knowledge/office_design_kits.json`)
  into Forge's layout vocabulary. Tested on all five examples and all 11 kits
  through `deck_type_scale`.
- **Author-at-destination from T034** into generated process tokens. Tested by
  `tests/test_forge_debt.py::SettleTests::test_token_is_authored_at_its_last_stop`
  and by the report fixture's process slide.
- **No cross-domain import**: no Word/Excel/vector canon is used; the defect and
  the fix are native PowerPoint behaviours.

## Frozen input

- **Request:** T063 brief in the T057 report, plus the four named defects:
  count-ups, highlight marker, type scale, MOT-SETTLE.
- **Base commit:** `ac5b45efb4e98359e1c68b13927db86696b35126`.
- **Example specs (unchanged):** `examples/pptx/forge/*.json`:
  - `coffee_office_dynamic.json` (`office:Slice`, `dynamic`, 10 slides)
  - `coffee_report.json` (`midnight`, `modern`, 10 slides)
  - `coffee_report_photos.json` (`midnight`, `modern`, 10 slides)
  - `vi_brand_seed.json` (brand seed `#DA251D`, `cinematic`, 9 slides)
  - `vi_chuyen_doi_so.json` (`paper`, `cinematic`, 9 slides)
- **Environment:** Windows 11; PowerPoint 16.0 (COM, build 17932);
  Python 3.13.5; python-pptx 1.0.2; lxml; Pillow; PyMuPDF 1.28.0;
  DeckCraft CLI 0.13.1 (`D:\artcraft\DeckCraft\deckcraft-cli.exe`);
  ffmpeg/ffprobe. `PYTHONUTF8=1` for every command.
- **Not accessed:** interactive slide-show clicking (T058); PowerPoint's
  Morph animation frames except through CreateVideo; DeckCraft's timing tree
  (it renders static end states and transitions, not in-slide animation).
- **Reproduction inputs:** the baseline decks are the five specs built at
  `ac5b45e`; `artifacts/before/` keeps two of them, the other three are
  reproducible with the command in Method. All hashes are in
  `artifacts/manifest.json`.

## Method

### Code changes

| Area | Change | File |
|---|---|---|
| Shared text metrics | One font map and one width model for Forge fitting, critic/QA and the motion components. Real font when installed, 0.55 em fallback. | `scripts/text_metrics.py` (new) |
| Type scale | `deck_type_scale()` reads the Office kit `type_scale_pt`; body is the highest body level ≥ 18 pt; `small` is capped by the design-system `body_base` 14 pt (never below 12); `display` is the `kpi_stat` 72 pt token only for decks with a KPI. Every `Builder.text()` call names a semantic level; `fit_level()` only steps down the scale. | `scripts/slide_forge.py` |
| Count-up stack | Proxies are inserted below the final source; the source is painted with the container colour, so edit view/PDF/static Morph see only the final value. Without an opaque container the counter falls back to a static value revealed with its click. | `scripts/counter_component.py`, `scripts/motion_director.py` |
| Highlight | `text_block()` now honours paragraph alignment and measures the real font; the marker takes its width from that extent instead of a character estimate. Single-line oval labels use the full diameter (PowerPoint lays text in the box, not the 0.707 inscribed rectangle). | `scripts/motion_engine.py`, `scripts/motion_components.py`, `scripts/forge_qa.py` |
| MOT-SETTLE | Ken Burns releases to the authored frame in the design system's move time before the slide ends. Generated process tokens are authored at the last stop and jump to the first stop while fading in (T034 author-at-destination). | `scripts/motion_engine.py`, `scripts/motion_components.py`, `scripts/motion_director.py` |
| Paragraph facts | The deck model now carries `align`, `font`, `size_pt`, `bold` per paragraph. | `scripts/pptx_animator.py` |

### Commands

```powershell
$env:PYTHONUTF8=1

# build every example (baseline and fixed)
python -c "import json,sys; from pathlib import Path; sys.path.insert(0,'scripts'); import slide_forge as sf; [sf.build(json.loads(p.read_text(encoding='utf-8')), Path('workspace/final')/(p.stem+'.pptx')) for p in sorted(Path('examples/pptx/forge').glob('*.json'))]"

# critic, machine-readable and markdown
python scripts/design_critic.py workspace/final/vi_chuyen_doi_so.pptx --md workspace/crit.md

# tests
python -m unittest discover -s tests -v

# PowerPoint PDF + per-slide PNG (COM)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/powerpoint_render.ps1 -Pptx workspace/final/vi_chuyen_doi_so.pptx -OutDir workspace/evidence/after/pptrender -SecondsPerSlide 5

# DeckCraft Morph frame (static end state of the outgoing KPI slide)
D:\artcraft\DeckCraft\deckcraft-cli.exe render-transition workspace/final/vi_chuyen_doi_so.pptx --slide 3 --t 0.5 workspace/evidence/after/deckcraft/morph-into-chart.png
```

PowerPoint PDF/PNG was produced with `Presentation.Export(...,"PDF")` and
`Slide.Export(...,"PNG",1280,720)`. CreateVideo produced a 59.6 s MP4; frames
were extracted with `ffmpeg -ss … -frames:v 1`. The MP4 is local (3.3 MB) and
not committed under the 2 MB/file cap; `preview/ppt-kpi-contact.png` is the
committed contact sheet.

## Evidence

### Type scale

| Deck | Sizes before | Warnings before | Overall before | Sizes after | Warnings after | Overall after |
|---|---:|---|---:|---|---:|---:|
| `coffee_office_dynamic` | 14 | TYP-SIZES, MOT-SETTLE ×2 | 4.36 | 6 | none | 4.70 |
| `coffee_report` | 15 | TYP-SIZES, MOT-SETTLE ×2 | 4.52 | 6 | none | 4.87 |
| `coffee_report_photos` | 15 | TYP-SIZES, MOT-SETTLE ×2 | 4.52 | 6 | none | 4.87 |
| `vi_brand_seed` | 13 | TYP-SIZES, MOT-SETTLE ×1 | 4.53 | 6 | none | 4.88 |
| `vi_chuyen_doi_so` | 13 | TYP-SIZES, MOT-SETTLE ×1 | 4.53 | 6 | none | 4.88 |

- The five decks use `{14, 20, 24, 28, 44, 72}` (Office Theme fallback) and
  `{14, 16, 18, 20, 36, 72}` (Slice). Body 24 / 18, title 44 / 36, display 72.
- `design_critic.py` reports `TYP-SIZES: good` on every deck; no `TYP-SMALL`,
  `TYP-RATIO` or `TYP-FAMILIES` warning.
- **Rung 1** (structural, critic) for the count; **rung 5** for the same sizes
  in PowerPoint PDF/PNG renders (`artifacts/after/vi-pdf-slide3.png`,
  `preview/midnight-kpi-after.png`).
- The critic scores are measurements, not human ratings; see Limitations.

### Count-ups: static, print and Morph

- **PDF export (PowerPoint 16.0):** `artifacts/after/vi_chuyen_doi_so.pdf`,
  page 3 rendered with PyMuPDF at 120 dpi:
  `artifacts/after/vi-pdf-slide3.png`. Only `32%`, `4,8/5`, `1.250`, `-18%`.
  Before: `artifacts/before/vi-pdf-slide3.png` shows the overlapping stack.
  **Rung 5.**
- **PowerPoint slide PNG:** `preview/vi-kpi-after.png`,
  `preview/office-kpi-after.png`, `preview/midnight-kpi-after.png` show one
  value per card. **Rung 5.**
- **PowerPoint CreateVideo frames:** `preview/ppt-kpi-contact.png` is a 6×6
  contact sheet over slide 3. The KPI values are seen as `0% → 17% → 27% →
  31% → 32%`, `0.372 → 1.036 → 1.204 → 1.248`, and `0% → -5% → -13% → -16% →
  -18%`: the motion still exists, one value at a time, and the final frame has
  only the final values. **Rung 5** (PowerPoint's own renderer).
- **Morph frame:** DeckCraft `render-transition --slide 3 --t 0.5` on the
  outgoing KPI slide (`preview/morph-kpi-after.png`) shows the final values
  only; before, `preview/morph-kpi-before.png` shows the ghosts. **Rung 4**
  (DeckCraft reads our file; it does not play PowerPoint's timing tree — see
  T057). We do **not** present this as PowerPoint Morph verification.
- **Mechanism:** `counter_component.insert_counter_stack(..., mask_color)` sets
  the source fill to the smallest filled container below it
  (`motion_components.container_fill`), inserts proxies below the source in
  ascending order, and keeps the source last. `p:set` visibility still hides
  the source until its last appear, so the proxies show during the slide show.
- **Rung 1** for the z-order/fill invariants
  (`tests/test_forge_debt.py::CounterStaticTests`).

### Highlight marker

- **Centred text:** before/after crop in `preview/highlight-before-after.png`.
  Before, the marker spans the left part of the full-width text box while the
  words are centred; after, the marker is symmetric under the words. The
  PowerPoint slide PNG is `preview/vi-highlight-after.png`. **Rung 5.**
- **Right-aligned text:** `tests/test_forge_debt.py::HighlightAlignmentTests::test_marker_ends_at_right_aligned_text`
  asserts the marker's right edge equals the measured text's right edge minus
  the 0.004 padding. **Rung 2** (model/geometry); no right-aligned example
  exists, so no PowerPoint render. See Limitations.
- **Mechanism:** `text_block()` uses `a:pPr/@algn`, `a:rPr/@sz`, `@b` and
  `a:latin/@typeface`; `text_metrics.width_pt()` measures the installed font.
  On this machine Segoe UI is present, so the marker measured 0.447 of slide
  width for the 28 pt takeaway (the words render at 0.447).
- **Rung 1** for the geometry unit tests, **rung 5** for the centred render.

### MOT-SETTLE

- `design_critic.py` reports no `MOT-SETTLE` on any of the five directed decks.
- `morph_studio.settle_report()` returns `[]` for all five.
- **Picture settle (Ken Burns):** the recipe now runs `~80 %` of its duration
  as the push-in and the last `~20 %` (capped at the design-system `move`
  default, 700 ms) as a release to the authored scale/offset. PowerPoint
  CreateVideo frames: `preview/ppt-cover-start.png` (0.3 s),
  `preview/ppt-cover-drift.png` (3.0 s, visibly pushed in),
  `preview/ppt-cover-settled.png` (6.3 s, authored frame). **Rung 5** for the
  picture; **rung 1** for the state model.
- **Token settle (T034 author-at-destination):** the generated process token is
  authored at the last step's centre + rail offset; the first travel keyframe
  jumps to the first stop with a forced 200 ms fade (`force_enter`), then the
  token travels through the stops. The last keyframe is the authored position,
  so the end state is exact. `settle_report()` on the directed report fixture
  is empty (`workspace/gesture_out.pptx`, not committed).
  **Rung 1** (state model + unit test); no PowerPoint render of the token
  because the example decks' Vietnamese notes do not trigger the English
  sequence cues, and the report fixture's token was not played in a slide show.
- **Deviation from T034, stated:** for **pictures**, authoring the zoomed
  destination in the XML was rejected. A full-bleed hero grows past the slide
  edge and `forge_qa` reports `OFF_SLIDE`; a contained picture would change the
  authored layout by 5 %. The canonical `release` settle (end on the authored
  frame) is used instead. Tokens, where the authored destination is inside the
  slide, use the T034 fix literally.

### Deck specs and tests

- All five example specs build with `ok: true`, no errors, unchanged spec
  files. `coffee_report`/`coffee_report_photos` have two `TEXT_SHRUNK`
  receipts; no `TEXT_OVERFLOW`, `WORD_BREAK`, `OFF_SLIDE` or `LOW_CONTRAST`.
- `python -m unittest discover -s tests` → **470 tests, OK, 8 skipped**
  (461 before + 9 new T063 tests). The only stderr line is a Pillow
  deprecation in `theme_engine.py`, unrelated.
- `python lab/tools/check_layout.py` → `layout OK`.
- Baseline hashes (before → after) are in `artifacts/manifest.json`; the two
  committed before decks are `2a164ce8…` (`coffee_office_dynamic`) and
  `21786efc…` (`vi_chuyen_doi_so`), the after decks are `8b3147ec…` and
  `3d63ba68…`. The PDFs are recorded there too.

## Negative results and limitations

- **Counter masks need an opaque container.** The mask is the smallest filled
  shape below the KPI value. A gradient or translucent card returns
  `NONSOLID`, and the counter falls back to a static value revealed with its
  click; the receipt marks `static_fallback: true`. No example has such a
  card, so the fallback is untested in PowerPoint. A blended mask (the
  `container_fill` alpha path used by `motion_components`) is the next step.
- **DeckCraft is not a motion verifier.** Its `render-transition` frame shows
  the static end state, not PowerPoint's animated Morph state. It is used only
  as a second reader for the print/static stack; the motion evidence is
  PowerPoint CreateVideo (rung 5).
- **Right-aligned highlight** has geometry/unit evidence only. There is no
  right-aligned text in the five example decks, so no PowerPoint render of that
  case. The centred case is rendered.
- **Picture settle is a release, not author-at-destination.** Explained above;
  authoring the destination would break `OFF_SLIDE` or the authored layout.
  This is a deliberate deviation from T034, not a claim that T034 was applied
  to pictures.
- **Type scale maps the Office Theme 18 pt step away for small text.** The
  kit's smallest body level is 18 pt, but a kicker at 18 pt overflows its
  0.38 in band. `small` is capped at the design-system `body_base` 14 pt (12 pt
  floor); the 18 pt step is then unused, so the deck still has ≤ 6 sizes. The
  body stays 24 pt (Office Theme) / 18 pt (Slice), above the 18 pt rule.
- **Scores are not human judgement.** The critic's 4.7–4.9 are measurements of
  the design system, not an eye test. The before/after images are the closest
  evidence; no rung 6 session was run.
- **One PowerPoint CreateVideo run failed** with a stuck `POWERPNT.EXE` COM
  instance; after killing the process it produced the 59.6 s MP4. This is an
  environment note, not a deck defect.
- **`TEXT_SHRUNK` remains** on the two Vietnamese decks (headings that step
  down one level to fit); it is advisory and does not affect the acceptance.

## Next

1. **Right-aligned render test:** build a two-slide fixture with a right-aligned
   takeaway, apply the highlight component, export PNG, and assert the marker's
   right edge in pixels. This closes the only geometry-only case.
2. **Gradient/translucent counter containers:** either blend the mask from the
   container alpha (reuse `motion_components.container_fill`'s alpha path) or
   surface `[static]` in the build verdict; add a fixture.
3. **Type scale across all 11 Office kits:** build one KPI deck per kit and
   assert 3–6 sizes and body ≥ 18 in the critic; the `Integral`/`Retrospect`
   duplicate body levels need a decision.
4. **T061:** the canonical interaction/timing writer should own the counter
   stack and the token jump, so `patch_existing_timeline` and Forge cannot
   drift apart.
5. **T059/T060:** DeckCraft's static frame is a useful second reader; its
   in-slide animation player remains the missing motion-verification channel.
6. **Spec contract:** add an explicit `motion.counters: "auto" | "off"` and a
   `[static]` receipt in the verdict, so an agent can choose the print-safe
   fallback without reading the XML.

## Review response

Pending. Findings from the Argon review will be answered here as fixed,
disputed (with evidence) or deferred (with a task row).
