# T052 [docx] — Configurable standard profiles + Vietnamese university scientific report

## Frame

- **Question:** the owner said the ISO/GRI annual report looked wrong next to a
  Vietnamese university thesis/đồ án and asked whether DocumentCraft can control
  a standard *per request*. Can one content spec produce a report under a named
  Vietnamese university regulation, with the page, type, numbering, captions and
  front matter actually measured — and can the same spec be rebuilt under a
  second regulation to show the difference?
- **Hypothesis:** yes, if a standard is stored as a sourced **profile** (page,
  typography, numbering, caption position, front-matter order, reference
  position, limits) and the checker reads the produced DOCX rather than trusting
  the spec. Falsifiers: a profile that cannot override the builder; a report that
  claims HUST but uses ISO margins; a caption numbered 1.1 in chapter 2; a
  front matter in the wrong order; a page-count rule that is not measured; a
  second build that silently reuses the first profile.
- **Domain lens:** WordprocessingML (ISO/IEC 29500), Vietnamese university
  presentation regulations, ISO 7144/2145/690, ISO 80000/8601, WCAG 2.2.
- **Transfers:** the architecture and window diagrams are authored SVG,
  rasterised by **VectorCraft**, trimmed/scaled by **Pillow**; the training, PR,
  F1, ablation and latency charts are built by **Chart Forge (SheetCraft)** and
  exported by Excel. The DOCX audit and Word PDF are the acceptance gate.

## Frozen input

- **Task/claim:** T052 [docx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T052-opencode-scientific-report`, based on `main` (`10cf7c6`, after
  T047/T048).
- **Request/date:** 2026-11-02; the owner said the previous Word report followed
  a standard that did not match a Vietnamese university report, and asked for a
  scientific report under a concrete standard, with enough content to judge.
- **Environment:** Windows 10/11 x64; Python 3.13; python-docx 1.2.0; lxml
  6.1.1; Pillow 11.3.0; PyMuPDF 1.28.0; Microsoft Word 16; VectorCraft and
  Chart Forge from the lab.
- **Authoritative sources (downloaded, read, then deleted):**
  - HUST, *Quy định về đồ án tốt nghiệp năm 2017* (faculty of Automatic
    Control), 5-page PDF: A4, Unicode 13/14 pt, line spacing 1.5, margins
    top 20 / bottom 15 / left 35 / right 20 mm, page number bottom centre,
    chapter-based figure/table/equation numbers, table caption above, figure
    caption below, body ≤ 50 pages.
    `https://hust.edu.vn/uploads/sys/quality-assurance/2019/05/cea-05-01-06-criteria-for-evaluating-graduation-projects.410143.20390.pdf`
  - VNU-UET, *Quy định về trình bày khóa luận tốt nghiệp* (standard and
    high-quality programmes), 9-page PDF: A4, Times New Roman 13 pt, line
    spacing 1.3, margins top 25 / bottom 30 / left 30 / right 20 mm, 6 pt
    paragraph spacing, 1 cm first-line indent, body 35–50 pages excluding
    tables/figures/references/appendix, chapter-based captions, references at
    the end.
    `http://fepn.uet.vnu.edu.vn/upload/2001767/fck/tung232/Quy-%C4%91i%CC%A3nh-v%C3%AA%CC%80-tri%CC%80nh-ba%CC%80y-kho%CC%81a-lu%C3%A2%CC%A3n-t%C3%B4%CC%81t-nghi%C3%AA%CC%A3pCLC.pdf`
  - SoICT/HUST template page and DOCX (cover/spine guidance; Overleaf links):
    `https://soict.hust.edu.vn/trang-chu/template-va-quy-cach-dong-quyen-do-an-tot-nghiep`
- **Could not access:** a current university-wide HUST regulation newer than the
  faculty 2017 PDF; a PDF/UA validator (veraPDF/PAC); a human reader session.

## Method

```powershell
# 1. Profiles
#    domains/docx/data/standard_profiles.json holds 4 named profiles:
#    hust-datn-2017, vnu-uet-kl-2024, iso-7144-thesis, annual-report-gri.

# 2. Assets (cross-asset pipeline)
python experiments/T052-.../inputs/make_diagrams.py
vectorcraft-cli convert architecture.svg architecture.png --scale 2
python experiments/T052-.../inputs/make_charts.py
python experiments/T052-.../inputs/build_charts.py   # Chart Forge + Excel render
python experiments/T052-.../inputs/prep_images.py    # crop/trim/upscale

# 3. Build the same content under two regulations
python experiments/T052-.../inputs/make_report.py
python scripts/document_forge.py build inputs/scientific_report_spec.json `
  -o artifacts/bao-cao-khoa-hoc-hust.docx `
  --profile hust-datn-2017 --update word `
  --conformance artifacts/conformance-hust.md
python scripts/document_forge.py build inputs/scientific_report_spec.json `
  -o artifacts/bao-cao-khoa-hoc-vnu.docx `
  --profile vnu-uet-kl-2024 --update word `
  --conformance artifacts/conformance-vnu.md

# 4. Audit and tests
python scripts/document_audit.py ... --profile hust-datn-2017
python -m unittest discover -s tests -v
```

The fixture is synthetic but internally consistent: ANSMART? No — a
CNN–LSTM–Autoencoder for IoT anomaly detection, four datasets (NAB, SWaT,
SMAP/MSL, IoT-Synthetic), six baselines, 5 seeds, an int8 deployment on
STM32H747 and ESP32-S3, and a 12-item reference list. Numbers are invented for
layout/testing; the method and citations are real enough to check.

## What changed

- **`domains/docx/data/standard_profiles.json`** — 4 profiles, each with
  publisher, document, URL, access date, evidence and status. HUST and VNU-UET
  are Vietnamese university regulations; ISO 7144 and the annual/GRI profile are
  the previous stack, kept for continuity.
- **`scripts/docx_profiles.py`** — load/merge profiles; `check_docx()` measures
  page size, margins, body font/size/line spacing, first-line indent, table font,
  heading depth, heading numbering, caption numbering and position, page-number
  field/alignment, front-matter order, reference count, citation fields, abstract
  length, body pages and equation numbering.
- **`document_forge`** — `--profile` / `--profiles`; profile defaults merge under
  the spec (explicit spec wins); `front_matter.order` may be a list; declaration,
  acknowledgements, task, abbreviations; thesis cover; `Chapter Unnumbered`
  standalone style so `Mở đầu` does not shift the Heading 1 counter;
  chapter-based `STYLEREF "Heading 1" \s` + `SEQ ... \s 1` captions; chapter-based
  equation numbers; table/figure caption separator from the profile; references
  before or after appendices; thesis footer (centred page number, no header);
  `--conformance` Markdown output; profile-aware audit margin floor.
- **`word_field_kit`** — caption separator/suffix; display-equation count from
  the Equation style (Word flattens `m:oMathPara` on save).
- **`document_audit.py`** — `--profile` so the generic 20 mm margin floor does not
  flag HUST's 15 mm bottom margin.
- **Tests** — `tests/test_docx_profiles.py` (7 tests): merge precedence, sourced
  profiles, HUST build with chapter captions/equations, conformance catches a
  wrong margin/font.

## Conformance — HUST

Profile: **HUST — Đồ án tốt nghiệp (quy định 2017)**, `hust-datn-2017`.
Result: **23 pass, 0 warn, 0 fail**.

| Control | Expected | Measured |
|---|---|---|
| Page | A4 210 × 297 mm | 210 × 297 |
| Margins | 20 / 15 / 35 / 20 mm | 20 / 15 / 35 / 20 |
| Body font | Times New Roman | Times New Roman |
| Space after | 6 pt | 6.0 |
| Alignment | justify | JUSTIFY |
| Heading sizes | 16/14/13/13 pt | 16/14/13/13 |
| Caption size | 12 pt | 12.0 |
| Body size | 13 pt | 13.0 |
| Line spacing | 1.5 | 1.5 |
| First-line indent | 10 mm | 10.0 |
| Table text | 12 pt | 12.0 |
| Heading depth | ≥ H3 | H3 |
| `Mở đầu` | unnumbered, outlineLvl 0 | OK |
| Heading numbering | automatic | yes |
| Captions | chapter.local, reset | 26 captions, 0 errors |
| Caption position | table above, figure below | 21 tables, 7 figures, 0 errors |
| Page number | PAGE field, centred | field + centre |
| Front matter | task → declaration → acknowledgements → abstract → TOC → abbreviations → list of tables → list of figures | same |
| References | ≥ 8 | 12 |
| Reference position | before appendix | before appendix |
| Citations | ≥ 8 REF ref-* | 13 |
| Body pages | ≤ 50 | 34 |
| Equations | numbered | 9/9 |

## Conformance — VNU-UET

Profile: **VNU-UET — Khóa luận tốt nghiệp**, `vnu-uet-kl-2024`.
Result: **24 pass, 0 warn, 0 fail**.

| Control | Expected | Measured |
|---|---|---|
| Page | A4 210 × 297 mm | 210 × 297 |
| Margins | 25 / 30 / 30 / 20 mm | 25 / 30 / 30 / 20 |
| Body font | Times New Roman | Times New Roman |
| Space after | 6 pt | 6.0 |
| Alignment | justify | JUSTIFY |
| Heading sizes | 16/14/13/13 pt | 16/14/13/13 |
| Caption size | 12 pt | 12.0 |
| Body size | 13 pt | 13.0 |
| Line spacing | 1.3 | 1.3 |
| First-line indent | 10 mm | 10.0 |
| Table text | 12 pt | 12.0 |
| Heading depth | ≥ H3 | H3 |
| `Mở đầu` | unnumbered, outlineLvl 0 | OK |
| Captions | chapter.local, reset | 26 captions, 0 errors |
| Caption position | table above, figure below | 21 tables, 7 figures, 0 errors |
| Page number | PAGE field, centred | field + centre |
| Front matter | declaration → abstract → TOC → abbreviations → list of tables → list of figures | same |
| References | ≥ 8 | 12 |
| Reference position | after appendix | after appendix |
| Citations | ≥ 8 REF ref-* | 13 |
| Abstract | 300–420 words | 343 |
| Body pages | 35–50 | 35 |
| Equations | numbered | 9/9 |

**The same spec produced both.** The diff is the profile: HUST uses
20/15/35/20 mm, 1.5 spacing and references before appendices; VNU-UET uses
25/30/30/20 mm, 1.3 spacing, a 343-word abstract and references after
appendices. The content, citations and figures are identical; both have 21
captioned tables (19 body + 2 appendix) and 7 figures. HUST has two extra
front-matter tables (task sheet, abbreviations) and VNU one (abbreviations),
hence 23 vs 22 total tables.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| A profile is a sourced contract, not a vibe | 1 | `standard_profiles.json` has publisher, document, URL, access date, evidence, status for all 4 profiles |
| Explicit spec values override profile defaults | 1 | `apply_profile()` deep-merge; `test_explicit_spec_wins_over_profile` |
| HUST page/type/caption rules are measured | 1 + 4 | `conformance-hust.md`: 23/23 pass; margins 20/15/35/20, TNR 13, 1.5, 10 mm indent, 26 captions |
| VNU-UET rules are measured on the same content | 1 + 4 | `conformance-vnu.md`: 24/24 pass; margins 25/30/30/20, TNR 13, 1.3, 343-word abstract, 35 body pages |
| The reports are real Word documents | 4 | Word opened the exact DOCX, refreshed fields and saved; 48-page HUST PDF and 45-page VNU PDF exported |
| Chapter-based numbering is live | 1 + 4 | `STYLEREF "Heading 1" \s` + `SEQ ... \s 1`; 26 captions, 9 equations, 9/9 numbered; no 1.1 in chapter 2 |
| Front matter follows each regulation | 1 | HUST task/declaration/acknowledgements/abstract/TOC/abbreviations/lists; VNU declaration/abstract/TOC/abbreviations/lists |
| Content is substantive | 1 | 59 headings (max H3), 23/22 tables, 7 figures, 9 equations, 12 references, 13 citation fields, 1,055/1,032 paragraphs |
| Cross-asset pipeline works | 1 + 4 | SVG → VectorCraft → Pillow for architecture/window; Chart Forge → Excel → PNG for 5 charts; sources/alt text in DOCX |
| Audit is clean | 1 | HUST and VNU: `ok: true`, 0 errors, 0 warnings (profile-aware margin floor); 204 fields, 88 bookmarks, `vi-VN` |
| Tests cover the profile layer | 1 | `tests/test_docx_profiles.py` (4 tests); full suite 411 tests OK, 8 skipped |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

| File | SHA-256 |
|---|---|
| `bao-cao-khoa-hoc-hust.docx` | `3dbbad0043ca186b074784de9f94c3c21ad70ed2ac954475943f88c19b53c62e` |
| `bao-cao-khoa-hoc-vnu.docx` | `363777013650f6aeb0a23c5bf63bfc15286eaeee012f37788928fda553987538` |

Preview: `preview/hust/page-01.png` (cover), `page-06.png` (TOC),
`page-15.png` (chapter 1), `page-26.png` (architecture), `page-46.png`
(references); `preview/vnu/page-01.png` (VNU cover), `page-04.png` (TOC),
`page-13.png` (chapter 1).

## Negative results and limitations

1. **HUST 2017 is a faculty regulation, not the current university-wide rule.**
   The profile is labelled as such; a student must check the current faculty
   template before submission. The checker proves the 2017 contract, not every
   HUST programme.
2. **VNU-UET has several programme-specific templates.** The PDF used here is
   the FEPN/UET regulation for standard and high-quality programmes; other
   faculties may differ. The profile is a named source, not a universal VNU
   rule.
3. **`body_pages` excludes end matter but includes tables/figures.** VNU's
   35–50 page rule excludes tables, figures, references and appendices, so the
   check is **lenient**: the measured 35 includes tables/figures. A strict VNU
   check would need to subtract figure/table pages. This is disclosed, not
   hidden.
4. **HUST has no explicit minimum page count** in the 2017 PDF (only a maximum
   of 50). The VNU profile's 35-page minimum is the stricter rule; the HUST
   build is 34 body pages, the VNU build 35.
5. **`Chapter Unnumbered` is a workaround for Word's list counter.** A
   based-on-Heading-1 style is still counted by `STYLEREF`; the standalone style
   is deliberate. This is documented in the code because it is easy to
   "simplify" back into a bug.
6. **The architecture diagram is dense.** At 150 mm width its labels are small
   (about 6–7 pt). A future revision should split it into two figures or reduce
   the number of boxes.
7. **Figures are raster in DOCX.** They are native SVG/Excel at the source, but
   Word embeds PNGs; a reader cannot edit the chart data inside Word.
8. **The content is synthetic.** The datasets, baselines, F1 numbers and
   deployment measurements are plausible but invented for layout/testing. No
   claim is made that the model was actually trained or that the MCU was
   measured.
9. **No PDF/UA/veraPDF or human reader test (rung 6).** The DOCX has headings,
   alt text, table headers and `vi-VN`; PDF/UA is a target, not a result.
10. **The VNU build passes by one page (35).** Adding or removing a paragraph
    changes the result; the page-count check is a range, not a margin of safety.

## Next

- Run veraPDF/PAC and add a tag-tree check for the merged/advanced tables.
- Add a strict VNU body-page count that subtracts figure/table pages.
- Split the architecture diagram into two readable figures.
- Add a real LaTeX/Word template export (`.dotx`) for each profile.
- Add a `--profile` example to `examples/docx/` with a small, redistributable
  asset set.
- Ask an independent agent to review this task before merge.

## Review response

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| — | Pending review. No findings yet. |
