# T042 [docx] — Advanced report craft: side-by-side media, equations, rich tables

## Frame

- **Question:** can the T039 DocumentCraft builder produce a report that feels
  authored rather than generated — image beside text, native equations, a
  designed cover, and a multi-level table with merged cells and image cells —
  while keeping Word fields, accessibility and editability intact?
- **Hypothesis:** yes, if advanced blocks are expressed as semantic spec
  entries and emitted as native OOXML (`m:oMath`, `w:tbl` with `gridSpan`/
  `vMerge`, inline `w:drawing` in cells), not as images of a layout.
  Falsifiers: a picture that behaves like a screenshot; an equation that is
  plain text; a merged table that Word repairs; a cover image that hides the
  real title; a side-by-side block that breaks the reading order.
- **Domain lens:** WordprocessingML (ISO/IEC 29500-1), Office Math (`m:oMath`),
  Word table model (`tblGrid`, `tcW`, `gridSpan`, `vMerge`), inline DrawingML,
  ISO 7144/2145/690, WCAG 2.2.
- **Transfers from other domains:** the cover/icon SVG is rasterised with
  **VectorCraft** and embedded in DOCX. The transfer is tested in the receiving
  domain by the DOCX audit + Word render. No slide grid/motion is imported.

## Frozen input

- **Task/claim:** T042 [docx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T042-opencode-advanced-docx`, based on `main` (`db58b3d`, after
  T039/T041).
- **Request/date:** 2026-11-01; the owner asked for a real report: image left /
  text right, math formulas, a real cover, complex table alignment and image
  cells; use online/local assets where useful, and feed cross-craft needs back
  into the other ArtCraft tools.
- **Environment:** Windows 10/11 x64; Python 3.13; python-docx 1.2.0; lxml
  6.1.1; Pillow 11.3.0; PyMuPDF 1.28.0; Microsoft Word 16; WordCraft and
  VectorCraft from `D:\artcraft`.
- **Could not access:** a PDF/UA validator (veraPDF/PAC), LibreOffice Writer,
  a human screen-reader session. ISO texts are paywalled; the report uses the
  catalogue/abstract pages.

## Method

```powershell
# 1. Synthetic cover/icons: SVG written locally, rasterised by VectorCraft
cd experiments/T042-20261101-opencode-advanced-docx/inputs
vectorcraft-cli convert cover.svg cover.png --scale 1
vectorcraft-cli convert icon-1.svg icon-1.png --scale 1

# 2. Build the report; Word refreshes fields; PDF for page inspection
python scripts/document_forge.py build `
  experiments/T042-20261101-opencode-advanced-docx/inputs/annual_report_spec.json `
  -o experiments/T042-20261101-opencode-advanced-docx/artifacts/annual-report.docx `
  --update word
# Word.Documents.Open(...).ExportAsFixedFormat(annual-report.pdf, 17)

# 3. Audit
python scripts/document_audit.py `
  experiments/T042-20261101-opencode-advanced-docx/artifacts/annual-report.docx `
  --md experiments/T042-20261101-opencode-advanced-docx/artifacts/audit.md

# 4. Tests
$env:PYTHONUTF8='1'; python -m unittest discover -s tests -v
```

The fixture is synthetic: an 11-page annual report with a cover hero, KPI strip,
callout, side-by-side figure/text, 2 equations, a merged-header table with icon
cells, references and appendix A. The cover/icons are generated SVG; no
third-party media is redistributed.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| Advanced blocks are native OOXML | 1 | `audit.json`: `ok: true`, no errors/warnings; 20 fields, 15 bookmarks, 6 tables, 6 drawings, 3 sections |
| Equations are real OMML | 1 + 5 | `word_math.omml_from_latex`; `m:oMath`, `m:f`, `m:sSup`, `m:nary`; Word PDF page 7 shows the fraction, growth equation and weighted sum |
| Side-by-side image/text is a real table, not a screenshot | 1 + 5 | borderless 2-cell `w:tbl`, inline `w:drawing`, caption `Hình 1 — …`; Word PDF page 7 |
| Rich table has multi-row header, merges and image cells | 1 + 5 | `header_rows`, `gridSpan`, `vMerge`, `w:drawing` in `w:tc`, `rowHeights`; Word PDF page 8 |
| Callouts and KPI strip are editable | 1 + 5 | `w:tbl` with shading/left border; `key_values` borderless table; Word PDF page 6 |
| Cover hero is a designed asset, title still a paragraph | 1 + 5 | inline hero image + `wp:docPr@descr`; title remains `Title` style; Word PDF page 1 |
| Cross-craft asset is accepted in DOCX | 1 + 5 | VectorCraft converted `cover.svg`/`icon-*.svg`; DOCX audit/render is the acceptance gate |
| Existing T039 guarantees still hold | 1 | TOC 3, `SEQ` 4, `STYLEREF`/`SECTIONPAGES`; no broken reference; T039 tests still pass |
| Tests cover the new blocks | 1 | `tests/test_document_advanced.py` (2 tests) + `test_document_craft.py` (6); full suite 334 tests OK |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

| File | SHA-256 |
|---|---|
| `annual-report.docx` | `853de7729e03a5df5bef735f80ba48c9e1e99a29f0776063adba588b7a2085df` |
| `annual-report.pdf` | `c75deb1925d53be20a338e932e16cc82474c7661c5ce01bb7d29d5f04b895132` |

Preview: `preview/cover.png`, `kpi-callout.png`, `side-equations.png`,
`rich-table.png`, `appendix.png`.

## Negative results and limitations

1. **LaTeX coverage is a subset.** Fractions, scripts, roots, nary operators,
   delimiters, accents, Greek letters and common operators work. Matrices,
   `cases`, aligned environments and chemistry are not supported; the parser
   raises a clear error instead of emitting a broken equation.
2. **Merged cells can hurt screen-reader header association.** The visual table
   is correct; a PDF/UA tag-tree/screen-reader test is still needed. `tblHeader`
   marks the header rows, but `gridSpan`/`vMerge` need an accessibility review.
3. **Image cells do not always auto-expand rows.** `row_heights_mm` is explicit;
   a future version should calculate the row height from image height + padding.
4. **The cover hero is inside the text column, not full-bleed.** It is an inline
   image with alt text; a print cover with bleed/trim is a different layout.
5. **Cross-craft assets are synthetic.** The SVG/PNG carries no customer brand;
   the VectorCraft command/version and licence must be recorded for real work.
6. **No PDF/UA or PDF/A validation; no human edit/print (rung 6).** The render is
   Word's PDF, inspected as images.
7. **The table is a single-page fixture.** Header repetition across pages and
   landscape tables are not tested here; they remain a T039 limitation.
8. **Equation numbering is per document, not per appendix.** If appendices need
   `(A.1)`, a separate `SEQ Equation` reset is needed.

## Next

- Add matrix/cases/aligned equations and a MathML→OMML fallback.
- Add a PDF/UA tag-tree check for merged tables and equations.
- Test header repetition on a 30+ page table and landscape sections.
- Add a print/full-bleed cover variant with trim/bleed guidance.
- Ask an independent agent to review this task; the cross-craft rule was added
  to `AGENTS.md`/`lab/standards/RESEARCH.md` and needs lab review.

## Review response

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| — | Pending review. No findings yet. |
