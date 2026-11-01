# T047 [docx] — Standards-controlled annual/ESG report

## Frame

- **Question:** can DocumentCraft produce a report that is convincing as a
  *document*, not just a set of blocks — one that declares a concrete standards
  stack, proves each control, and carries enough narrative, tables, figures and
  equations for a reader to judge the craft?
- **Hypothesis:** yes, if the report is built around a published standards
  profile (ISO 7144 structure, ISO 2145 numbering, ISO 690 references, ISO
  80000/8601 units and dates, WCAG 2.2, GRI 1/2/3/305 content) and every claim
  maps to an audit statistic or a rendered page. Falsifiers: a standards table
  with no evidence; a TOC/list that does not match the body; an appendix before
  the references; a page that is mostly blank because a table split; a chart
  with no source; an ESG claim without a boundary/limitation.
- **Domain lens:** WordprocessingML (ISO/IEC 29500), ISO 7144:1986, ISO
  2145:1978, ISO 690:2021, ISO 80000-1:2022, ISO 8601-1:2019, WCAG 2.2,
  GRI 1/2/3/305; a real annual report (Vinamilk 2025) was used only as a
  structural reference.
- **Transfers from other domains:** the product illustration is authored SVG,
  rasterised by **VectorCraft**, trimmed/graded/composited by **Pillow**, then
  accepted by the DOCX render/audit. The revenue/emissions charts are built by
  **Chart Forge (SheetCraft)** and exported by Excel, then embedded as figures.
  This is the lab's cross-asset pipeline (T044) applied end to end.

## Frozen input

- **Task/claim:** T047 [docx], OpenCode (DeepSeek V4.1 Flash), branch
  `work/T047-opencode-standards-report`, based on `main` (`f7185ae`, after
  T045/T046).
- **Request/date:** 2026-11-01; the owner said the T045 Word report was not
  impressive enough, lacked a concrete standard set and enough content to judge.
  The request was to find stronger references, use a specific standard stack,
  and show what is controlled.
- **Environment:** Windows 10/11 x64; Python 3.13; python-docx 1.2.0; lxml
  6.1.1; Pillow 11.3.0; PyMuPDF 1.28.0; Microsoft Word 16; VectorCraft and
  GridCraft from `D:\artcraft`.
- **Reference documents (local, not redistributed):** ISO 7144:1986 sample
  PDF (9 pages), GRI 1: Foundation 2021 PDF (38 pages), Vinamilk Annual Report
  2025 PDF (112 pages, A4). ISO texts are paywalled; the report cites the
  catalogue/abstract pages and the downloaded preview. The Vinamilk PDF was
  deleted after the page/structure teardown; no content or image was copied.
- **Could not access:** a PDF/UA validator (veraPDF/PAC), a human screen-reader
  session, external ESG assurance.

## Method

```powershell
# 1. Standards research + profile
#    ISO 7144 current (reviewed 2024), ISO 2145, ISO 690:2021,
#    ISO 80000-1:2022, ISO 8601-1:2019, WCAG 2.2, GRI 1/2/3/305.
#    Written to domains/docx/data/report_standard.json.

# 2. Cross-asset product illustration
python experiments/T047-.../inputs/make_product_svg.py
vectorcraft-cli convert camera.svg camera.png --scale 2
python experiments/T047-.../inputs/make_assets.py   # trim, grade, cover

# 3. Charts in SheetCraft
python scripts/chart_forge.py build inputs/chart_revenue_spec.json `
  -o artifacts/charts/revenue.xlsx --render artifacts/charts
python scripts/chart_forge.py build inputs/chart_emissions_spec.json `
  -o artifacts/charts/emissions.xlsx --render artifacts/charts
# crop/upsample the Excel PNGs for 150 dpi at 145 mm (Pillow)

# 4. Build the report; Word refreshes fields; PDF for page inspection
python experiments/T047-.../inputs/make_report.py
python scripts/document_forge.py build inputs/annual_report_spec.json `
  -o artifacts/annual-report-2026.docx --update word

# 5. Audit and tests
python scripts/document_audit.py artifacts/annual-report-2026.docx --md artifacts/audit.md
$env:PYTHONUTF8='1'; python -m unittest discover -s tests -v
```

The fixture is synthetic: ANSMART, a smart-device company, with 2022–2026
financials, 880 employees, 23,250 tCO₂e, a 10-topic materiality matrix and a
GRI content index. The report deliberately discloses that ESG is self-declared
and not externally assured.

## Standards profile and controls

`domains/docx/data/report_standard.json` declares 10 standards and 10 controls.
The front matter prints the control table *before* the TOC, so the reader sees
the claim, the clause and the evidence in one place.

| Control | Clause | What the report does | Evidence |
|---|---|---|---|
| DOC-STRUCT | ISO 7144 §5 | abstract → preface → TOC → lists → body → annexes → end matter | `front_matter.order = iso7144`; 3 sections; TOC/lists |
| DOC-NUMBER | ISO 2145 | 1 / 1.1 / 1.1.1, no trailing dot | Word multilevel list; TOC |
| DOC-EQUATION | ISO 7144 §15.5 | display equation, extra space, number in parentheses at right | 5 OMML equations in Equation style (5 display); 2 `SEQ Equation` |
| DOC-FIGTABLE | ISO 7144 §12, §15.7 | caption + source; list of figures/tables with page | 4 figures (cover + 3 captioned), 38 tables (23 captioned), 2 lists |
| DOC-REF | ISO 690:2021 | element order; numbered citations | 11 references; `{{cite:key}}` links |
| DOC-UNITS | ISO 80000-1 / 8601-1 | unit symbols, value–unit space, ISO dates | table headers, document control |
| DOC-ACCESS | WCAG 2.2 AA / PDF/UA target | headings, alt text, table headers, `vi-VN` | audit: 4 figures, 38 tables, language `vi-VN` |
| GRI-CONTENT | GRI 1/2/3 | materiality, boundary, stakeholders, index | 37-row GRI index appendix |
| GRI-305 | GRI 305:2016 | Scope 1/2/3, intensity, target | emissions table, equation, 2030 target |
| DOC-ASSURANCE | GRI 1 §5 / ISO 7144 preface | limitation statement | self-declared, no external assurance |

The table is a **control matrix, not a certificate**. Two rows are explicitly
partial/limited: PDF/UA was not validated, and external assurance was not
obtained.

## Evidence

| Claim | Rung | Evidence |
|---|---|---|
| The report is a real Word document, not a PDF mock | 4 | Word opened the exact DOCX, refreshed fields and saved; `updated_by: word`; 25-page PDF exported |
| Front matter follows the declared ISO 7144 order | 1 | New `front_matter.order = iso7144`; test asserts abstract < preface < TOC; references after appendix |
| ISO 2145 numbering is live | 1 + 4 | multilevel heading list; TOC 3 levels; 37 headings, max level 3 |
| Equations are native OMML with ISO 7144 numbering | 1 + 4 | 5 `m:oMath`; 2 `SEQ Equation`; Word page 5/10/12 show right-aligned numbers |
| Figures/tables are captioned and listed | 1 | 4 figures (cover + 3 captioned), 23 captioned tables, List of Figures/Tables via REF/PAGEREF (63 PAGEREF fields) |
| References are ISO 690-shaped and linked | 1 | 11 references, labels [1]–[11], citation bookmarks; references after appendices |
| GRI content is substantive | 1 | 10 material topics, 5 stakeholder groups, 37-row GRI index, Scope 1/2/3, intensity, target |
| The product illustration is a controlled vector asset | 1 + 4 | SVG authored (≈120 shapes), VectorCraft 2× raster, Pillow trim/grade/composite; DOCX render page 4 |
| Charts are native SheetCraft exports | 1 + 4 | Chart Forge combo/stacked workbooks, Excel PNG export, embedded with source + alt; audit no DPI note at 145 mm |
| Audit is clean | 1 | `ok: true`, 0 errors/warnings; 135 fields, 91 bookmarks, 37 headings (max H3), 38 tables, 4 figures, 5 equations (5 display, 2 numbered), 1 image in cell, 5 merged cells, `vi-VN`, 1,174 paragraphs; 11 unique references cited |
| Tests cover the new order/parser | 1 | `tests/test_document_standards.py` (2 tests); full suite 387 tests OK |

**Hashes:** see `artifacts/SHA256SUMS.txt`.

| File | SHA-256 |
|---|---|
| `annual-report-2026.docx` | `0915dd049a31455e9e760927540431542eb94698a8699acab5e7f0acf95ef14a` |
| `annual-report-2026.pdf` | `a53b459f5b327ada78c1f3cd5bfc81f64ccb35a77df7f963876e5bee1e2c9e56` |
| `audit.json` | see SHA256SUMS |

Preview: `preview/page-01.png` (cover), `page-03.png` (standards control),
`page-11.png` (financial chart/equation), `page-16.png` (materiality),
`page-17.png` (emissions), `page-25.png` (references).

## Negative results and limitations

1. **ISO 7144 is for theses and similar documents, not annual reports.** It is
   used for structure, numbering, equations, lists and end matter; it does not
   certify an annual report. The report says this explicitly.
2. **ISO 7144 does not fix margins, typeface or colour.** Those follow the
   DocumentCraft house style and WCAG contrast; they are not claimed as ISO
   requirements.
3. **The ESG content is self-declared.** GRI 1 allows an “in accordance” claim
   only with the content index and reporting principles; external assurance is
   absent. The report discloses that limitation on the cover control page and
   in section 13.
4. **PDF/UA is a target, not a result.** The DOCX has headings, alt text, table
   headers and `vi-VN`; no veraPDF/PAC run, so WCAG/PDF-UA conformance is not
   claimed.
5. **The report is synthetic.** ANSMART, its financials, employees and emissions
   are invented for layout/testing; no customer or Vinamilk content is reused.
6. **The Vinamilk 2025 PDF was used only for structural teardown** (112 A4
   pages, front matter/body/ESG index). It was deleted after the exercise; the
   report cites it as a reference, not as a data source.
7. **Charts are raster in DOCX.** They are native Excel charts at the source
   (SheetCraft), but the DOCX embeds PNGs; a reader cannot edit the chart data
   inside Word.
8. **The vector camera is semi-flat, not photoreal.** It has ~120 shapes, three
   body tones, a five-ring lens and a textured grip; it is deliberately calmer
   than a photoreal render, and still a synthetic product.
9. **No human reader test (rung 6).** The pages were inspected as images; no
   usability or comprehension test was run.
10. **The table of contents is two pages.** The 37-entry, three-level TOC
    spills a few lines onto the second page; a shorter H2 set or a smaller TOC
    font would fit one page. Body pagination is otherwise continuous.

## Next

- Run veraPDF/PAC on the PDF and add a tag-tree check for merged tables.
- Add a real external-assurance-style limited assurance statement (synthetic)
  and a GRI content-index validator.
- Add a 30+ page table/landscape section to test header repetition and pagination.
- Replace the raster chart images with editable native Word charts or embedded
  OLE objects if the customer requires in-Word editing.
- Ask an independent agent to review this task before merge.

## Review response

Argon review 2026-11-01 (chat `0:cf4bb6173adaaa34`), verdict **revise**.

| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| B1: ISO 2145 claim not evidenced (`max_heading_level=1`) | **Fixed.** Added H2/H3 sections (37 headings, max level 3); TOC is 3 levels; test asserts `max_heading_level >= 3`. |
| B2: display equations count 0; equation pages inconsistent | **Fixed/clarified.** Word flattens `m:oMathPara` on save, so the audit now counts `m:oMath` in `Equation` style: 5/5 display equations, 2 numbered. Report no longer claims `m:oMathPara` or three numbered pages. |
| B3: figure/table/reference counts wrong; only one reference cited | **Fixed.** Counts corrected: 4 figures (cover + 3 captioned), 38 tables (23 captioned), 22 `SEQ Table`; all 11 references now have `REF ref-*-label` citations (13 REF fields, 11 unique); test checks citations. |
| M1: sparse body page / mixed PDF vs body page numbers | **Fixed.** Section 6/10/11 now flow instead of forced page breaks; materiality equation moved up; balance-sheet table added; 25 pages, continuous body. Report uses PDF page numbers and explains the body-footer numbering. |
| M2: Control Matrix before TOC is outside ISO 7144 §5; units/GRI not automated | **Clarified/limited.** Preface and report now say the control matrix is a DocumentCraft house extension, not an ISO 7144 clause. Unit/date and GRI checks remain manual inspection; no automated checker is claimed. |
| m1: only 2 tests | **Improved.** The 2 tests now cover escaped LaTeX, front-matter order, references-after-appendix, H3 structure, display equations and citation fields. Full suite 387 tests. |
| Note: `display_equations` definition | **Disputed as an XML-only definition, fixed as a semantic one.** Word rewrites display OMML; the style-based count is the stable contract. |
