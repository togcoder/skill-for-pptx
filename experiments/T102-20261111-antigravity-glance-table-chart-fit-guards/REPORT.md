# T102: Harden `glance`, `fit`, `check`, and Guidance Guards Against Small-Model Workflow Failures (Issue #83)

**Agent:** `Antigravity (Gemini)`  
**Date:** 2026-11-11  
**Branch:** `work/T102-antigravity-glance-table-chart-fit-guards`  
**Capability:** `pptx.skill` (`scripts/pptx_tools.py`, `skills/pptx/`, `tests/`)  
**Issue:** [#83](https://github.com/togcoder/skill-for-pptx/issues/83)

---

## 1. Frame & Problem Statement

Following `T100` (which introduced `glance`, `shell`, `fit`, `compare` and `guides/13-dua-bo-co-san-vao-theme.md`), post-mortem inspection of a multi-round deck reskin failure by small/fast models (tracked under Issue `#83`) exposed seven concrete technical and workflow gaps that remained after `T100`:

1. **`glance` table blindness (and `tiny text` micro-box gap):** `T100` explicitly skipped native PowerPoint tables (`HasTable`, `Type=19`) and single-character shapes (`len < 2`), and only flagged `tiny text` when >20% of slide characters dropped below floor (`micro = 0.75 * floor` inside small blocks went unflagged).
2. **`glance` chart text size & pre-COM XML hazard:** `_chart_inks` checked colour contrast, not chart font sizes (`_chart_sizes`). Separately, stacked bar/area charts with `<c:dLblPos val="outEnd"/>` raise PowerPoint COM `E_FAIL` (`-2147467259`) during `Presentations.Open(...)` without actionable context.
3. **`glance --slides` partial-check distortion:** Filtering `_facts(..., slides=[...])` dropped the remaining slides from `_slots(...)` and changed `(numbers[0], numbers[-1])` to the first/last requested slide, stripping slot exemptions (`!!step`, `Title`, `Logo`) and suppressing `"missing"` checks on partial runs.
4. **PUA missing-glyph symbols, cross-region duplicate photos, busy photo overlays, and draft/meta wording leaks:** `follow_theme()` removes explicit Wingdings/Webdings fonts and exposes `\uF000-\uF0FF` PUA bytes as tofu (`□`) in Latin fonts; duplicated content photos placed in separate grid frames passed; high-contrast busy imagery behind non-slot text passed median luminance contrast; placeholder/meta strings (e.g. `"Lorem ipsum"`, `"Charts kept from..."`, `"[TODO]"`) passed.
5. **`fit()` overflow when font floor clamps shrink ratio:** When `factor < 1.0` and `MIN_PT` clamps shrunk text above `box * factor`, the text frame and table cells still shrank by `factor`, squeezing text into overflow without using adjacent whitespace inside `into`.
6. **`check()` table content bypass & chart XML validity:** `"tables kept"` checked table count only, letting gutted/empty placeholder tables pass (`1 == 1`). Stacked chart `dLblPos="outEnd"` XML errors were also unchecked.
7. **Small-model process bypass (`SKILL.md`, Guides `8` and `13`):** Small/fast models wrote private regex/XML scripts to bypass `glance`, trusted unverified subagent `"0 faults"` reports, and silently crunched overfull frames instead of stopping at 3 rounds / escalating layout level 2.

---

## 2. Empirical Probe (PowerPoint 16.0 Build 17932 COM)

Before changing `_facts()`, native table geometry and COM behavior were measured directly in PowerPoint 16.0 (Windows `pywin32`, `960x540` pt slide exported at `1600x900` PNG -> PNG pixels measured against COM bounds):

- **Table cell text coordinates (`TrimText`):** `tbl.Cell(r, c).Shape.TextFrame.TextRange.TrimText().BoundLeft` and `.BoundTop` are **relative to cell geometry + `VerticalAnchor` + cell top/bottom margins**, NOT slide-absolute:
  - `VerticalAnchor in (1, 2)` (Top/Baseline): `base_y = cs.Top + cs.TextFrame.MarginTop`
  - `VerticalAnchor == 4` (Bottom): `base_y = cs.Top + cs.Height - cs.TextFrame.MarginBottom`
  - `VerticalAnchor == 3` / other (Middle): `base_y = cs.Top + (cs.Height + MarginTop - MarginBottom) / 2.0`
  - Slide-absolute text bbox = `[cs.Left + inked.BoundLeft, base_y + inked.BoundTop, inked.BoundWidth, inked.BoundHeight]`. Verified within `< 1 px` on `1600x900` PNG renders across TOP, MIDDLE, and BOTTOM alignments. Merged cells share identical `(Left, Top, Width, Height)` rectangles in COM and are deduplicated by cell box tuple.
- **Stacked chart XML crash:** Injecting `<c:dLblPos val="outEnd"/>` on `XL_CHART_TYPE.COLUMN_STACKED` causes `app.Presentations.Open(...)` to fail with `pywintypes.com_error: (-2147352567, 'Exception occurred.', (0, None, None, None, 0, -2147467259), None)`.

---

## 3. Changes Implemented

### Code (`scripts/pptx_tools.py`)
- **Pre-COM chart validation (`_chart_xml_faults`, `_invalid_chart_xml`):** Rejects stacked/percentStacked bar & area charts carrying `<c:dLblPos val="outEnd"/>` before COM opens the file (`_facts`), flags them cleanly in `inventory()`, and adds a `"charts valid"` gate to `check()`. `main()` catches `ValueError` on `glance` for clean error output.
- **Native table inspection in `_facts()`, `_glance_slide()`, and `reink()`:**
  - Collects deduplicated table cells with `VerticalAnchor`-calibrated `TrimText()` bounds and runs.
  - Checks cell text contrast (`cannot read` + `unreadable`) and cell font floor (`tiny text`: `>20%` below floor or `>= 3` chars below `0.75 * floor`).
  - Protects readable dark-filled header cells (`<a:tcPr>/<a:solidFill>/<a:srgbClr>`) in `reink()` when body cells of the same table fail white-on-white contrast.
- **Chart sizes, PUA glyphs, duplicate photos, busy backgrounds, micro floor, and draft wording:**
  - `_chart_sizes()` reads visible chart XML font sizes (`c:txPr`, `c:rich`, skipping deleted elements, empty titles, and hidden `dLbls`); `_glance_slide()` and `inventory()` check against scaled floor.
  - `_pua_hits()` flags `U+F000–U+F0FF` characters outside symbol fonts (`Wingdings`, `Webdings`, `Symbol`, etc.), scanning all runs and table cells via `_slide_text_notes()` (`broken symbol`).
  - `_pic_key()` pairs SHA-1 hash with crop fractions so uncropped/identically cropped non-`!!` content photos (`>= 1.5%` slide area) repeated in separate frames trigger `"same picture twice"` while deck-wide icons (`>= max(3, 0.3 * N)` slides) remain allowed.
  - High-variance backgrounds (`spread > BUSY = 28`) behind non-slot text on `picture|chart|table` trigger `"text on picture"`.
  - Localized small blocks (`>= 12` chars at `< 0.75 * floor`) trigger `"tiny text"` even when `< 20%` of slide characters.
  - `_meta_hit()` flags leaked placeholder/meta phrases (`"Lorem ipsum"`, `"Charts kept from..."`, `"[TODO]"`, etc.) as `"draft text"`.
- **Partial `--slides` preservation in `_facts()` and `glance()`:** Collects lightweight top-level slide slot geometry (`_slot_slides`) across all slides without exporting extra PNGs, and evaluates cover/closing exemptions against `(1, total_slides)` instead of `(numbers[0], numbers[-1])`.
- **Clamped `fit()` whitespace reclaim (`_reclaim_clamped_boxes`):** When `factor < 1.0` and `MIN_PT` clamps text size larger than `factor`, expands constrained text boxes and tables into available right/down slack inside `into` while maintaining `>= 0.06 in` clearance from siblings and scaling `<a:gridCol>` / `<a:tr>` proportionally.
- **Table content retention in `check()`:** Counts non-empty, non-merged `<a:tc>` cells; when `old_pop >= 4` and `new_pop < 0.5 * old_pop`, `"tables kept"` fails (`empty/gutted table`).

### Guidance (`skills/pptx/`)
- `skills/pptx/SKILL.md`: Tightened Rule 6 (scaled floor + tables/charts) and strengthened `"Nếu bạn là model nhỏ hoặc nhanh"` (mandatory use of `scripts/pptx_tools.py`, no custom XML/check bypass scripts, fail-closed subagent verification, batch size `5–7` slides, escalate when `fit` hits floor).
- `skills/pptx/guides/8-tu-kiem-tra.md`: Documented new `glance` checks, `--slides` behavior, ban on private check bypasses, and fail-closed subagent inspection rule.
- `skills/pptx/guides/13-dua-bo-co-san-vao-theme.md`: Added Wingdings PUA warning on `follow_theme`, `dLblPos="outEnd"` warning on stacked charts, `retable` guidance, duplicate photo / busy photo guidance, and updated the `glance` fault table.

---

## 4. Verification & Evidence

- **Rung 1 & 4 (synthetic unit & OOXML checks):**
  - `python -m unittest discover -s tests -q`: run on full suite (`646` tests, covering both existing regressions and `10` new `T102` tests across `tests/test_glance.py` and `tests/test_fidelity_gates.py`).
  - `python lab/tools/check_layout.py`: `layout OK`.
- **Rung 5 (real PowerPoint 16.0 COM export + `read_file` visual inspection on synthetic fixture):**
  - `PPTX_NATIVE=1 python -m unittest tests.test_glance tests.test_fidelity_gates -v`: **29/29 passed** (`OK`), including real PowerPoint COM `test_glance_native_tables_charts_pua_dup_photos_and_partial_slides`.
  - Synthetic 4-slide trial (`inputs/build_trial.py` -> `artifacts/synthetic_broken.pptx`, `artifacts/synthetic_fixed.pptx`):
    - `glance` on `synthetic_broken.pptx`:
      - Slide 2 detected **5/5** injected faults (`cannot read` `'1200' FFFFFF on FFFFFF`, `tiny text` `8 pt` `'4.8%'`, `same picture twice` across `'PartA'`/`'PartB'`, `broken symbol` `U+F0E8` in `'Arial'`, `draft text` `'Charts kept from'`).
      - Slide 3 detected **3/3** injected faults (`text on picture` on striped photo, chart `tiny text` at `8 pt`, micro textbox `tiny text` at `8 pt`).
    - `glance` on `synthetic_fixed.pptx`: **0 faults across slides 1–4**.
    - Opened and visually verified `preview/broken/faults-02.png`, `preview/broken/faults-03.png`, `preview/fixed/slide-02.png`, and `preview/fixed/slide-03.png` directly: red boxes `[1]..[5]` frame the exact `1200` and `4.8%` cells inside `AuditTable`, the duplicate photo frames, the `□` tofu character box, and the draft string; fixed slides render cleanly.

---

## 5. Negative Results & Limits

1. **`test_watch_the_real_show` (pre-existing interactive slideshow harness test in `tests/test_pptx_tools.py`)** failed during baseline COM runs on this desktop (`KeyError: 'clicks'` from PowerPoint slideshow window navigation), unrelated to `T102`; `watch()` was not modified. Additionally, aborted COM runs can leave background `/AUTOMATION -Embedding` `POWERPNT.EXE` servers open if processes are killed mid-flight.
2. **Busy-background heuristic (`spread > BUSY` in `_behind`)**: `_behind` samples the 50% of background pixels farthest in RGB distance from ink color. On strictly two-tone binary black-and-white stripes aligned symmetrically against black ink, all dark pixels sort into the near half and white pixels form a uniform far half (`spread == 0`), whereas multi-tone textures/photos with >50% light variance or mixed hues produce high spread and reliably trigger `"text on picture"`.
3. **Grouped tables and COM run cap:** Shapes with `HasTable` inside PowerPoint COM report `BoundLeft`/`BoundTop` relative to cell origin + vertical anchor across `runs[:12]`; runs past index 12 fall back cleanly to XML `_slide_text_notes()` for PUA/draft checks, while contrast and size measurement remains capped at the first 12 formatted COM runs per cell/textbox for speed.
4. **Co-ordination boundaries:** Kept completely orthogonal to `work/T101-claude-look-meaning-arrange` (`arrange`/`seen`/`_stamp` in `scripts/pptx_tools.py` untouched) and open `PR #79` (`work/T089-opencode-harmful-defaults`, leaving `guides/6` and `guides/9` untouched).

---

## 6. Artifacts

- `inputs/build_trial.py` (100% synthetic generator + trial runner)
- `artifacts/synthetic_broken.pptx`, `artifacts/synthetic_fixed.pptx`, `artifacts/fit_input.pptx`, `artifacts/fit_reclaimed.pptx`, `artifacts/trial_summary.json`
- `preview/broken/slide-01..04.png`, `preview/broken/faults-02.png`, `preview/broken/faults-03.png`, `preview/fixed/slide-01..04.png`
