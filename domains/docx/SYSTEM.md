# Document system: professional DOCX with real links

Status: EXPERIMENTAL — T039/T045/T047/T052 [docx], review requested (2026-11-02).
Evidence reached: structural (rung 1), WordCraft layout (rung 2) and Microsoft
Word parse + field refresh + PDF export (rungs 4–5). No LibreOffice (rung 3), no
human edit/print (rung 6), no PDF/UA or PDF/A validation. PowerPoint playback is
irrelevant here; Word playback is not claimed.

## Why

Before T039 the repository could connect to WordCraft but had no document
knowledge: no standards map, no shared page/type/table tokens, no generator and
no audit for the things that break Word documents:

- a TOC typed as text, or a field that never refreshes;
- captions typed as "Figure 1", "Figure 1", "Figure 1";
- cross-references pointing at deleted bookmarks;
- floating images that jump to the next page;
- tables that spill into the margin;
- appendices numbered "1" instead of "A";
- a header that shows the previous chapter;
- PDF/UA or PDF/A claimed from a visual check.

The fix is structural, mirroring T034's design system:

```
domains/docx/data/document_system.json   standards, tokens, rules, sources
        │ read by                         │ graded by
        ▼                                  ▼
document_forge.py                  document_audit.py
word_field_kit.py                    word_field_kit.audit_docx
        │                                  │
        └────────── build → refresh → render → fix ──────────┘
```

## Files

| File | Role |
|---|---|
| `domains/docx/data/document_system.json` | Page/type/figure/table/field/accessibility tokens, standards, rules, sources |
| `domains/docx/data/report_standard.json` | T047 ISO/GRI standards profile, controls, evidence and status |
| `domains/docx/data/standard_profiles.json` | T052 named profiles: HUST 2017, VNU-UET, ISO 7144, annual/GRI |
| `domains/docx/schemas/document_spec.schema.json` | Semantic input for the generator |
| `scripts/word_field_kit.py` | Fields, TOC, SEQ captions, REF/PAGEREF, STYLEREF, bookmarks, numbering, audit |
| `scripts/document_forge.py` | Build DOCX from a spec; refresh with Word/WordCraft; render |
| `scripts/document_audit.py` | Standalone structural audit |
| `scripts/word_math.py` | LaTeX subset → OMML equations (T045) |
| `examples/docx/annual_report_spec.json` | Rich-report fixture: cover hero, side-by-side, equations, merged table, image cells (T045) |
| `skills/document-craft/` | Workflow, standards note, Word property matrix, layout recipes |
| `tests/test_document_craft.py` | Structural build/audit tests |
| `tests/test_document_advanced.py` | OMML, side-by-side, rich tables, malformed-grid/alt negative tests |
| `tests/test_document_standards.py` | Escaped LaTeX, ISO 7144 front-matter order, references after appendix |

## What the generator guarantees

- **Headings** use built-in Heading 1–9 styles, linked to a multilevel list
  (ISO 2145: `1`, `1.1`, `1.1.1`, no trailing dot). Front matter headings are
  unnumbered and excluded from the TOC.
- **TOC** is a `TOC \o "1-3" \h \z \u` field. The list of figures/tables is a
  standard `TOC \h \z \c "Figure"` / `"Table"` field; Word updates it through
  `TablesOfFigures`. A `ref_pageref` fallback exists for renderers that cannot
  update a TOF, but it has static caption text and does not auto-add entries.
- **Captions** are `SEQ Figure/Table` fields; the number and the label+number
  are bookmarked; body text uses `{{ref:fig-1}}`, `{{num:fig-1}}`,
  `{{page:fig-1}}`, `{{cite:key}}`.
- **Images** are inline, centred, aspect-preserving, ≤ text width, with alt text
  and an effective-DPI report.
- **Tables** are fixed-layout, grid widths sum to the text column, header row
  repeats, numeric columns right-align, caption above, source note below.
- **Sections**: cover (no header/footer), front matter (roman, start 1), body
  (arabic, start 1); `STYLEREF "Heading 1"` in the body header; `PAGE` /
  `SECTIONPAGES` in the footer (`NUMPAGES` would count the front matter too).
- **Appendices** use `Phụ lục A`, `A.1`; captions use `Bảng A.1` and reset the
  sequence per appendix.
- **Fields** are refreshed by Microsoft Word (three passes, via `pywin32`),
  including `TablesOfContents` and `TablesOfFigures`; WordCraft
  `convert --update-fields` is the fallback. `w:updateFields` is set when the
  file is delivered without a native refresh.

## Advanced report blocks (T045)

- **Side-by-side media/text** (`figure_text`): a borderless two-cell table,
  image on the left or right, text column beside it, caption below. Inline
  images; alt text; no floating anchors.
- **Native equations** (`equation`): LaTeX subset → OMML (`m:oMath`), optional
  right-aligned `SEQ Equation` number. Supported: fractions, powers,
  subscripts, roots, sums/integrals, parentheses, accents, Greek letters and
  common operators. Unsupported commands raise a clear error, not a broken
  equation.
- **Merged-header tables** (`table.advanced`): multiple header rows
  (`tblHeader`), `colspan`/`rowspan`, explicit merges, row heights, cell
  margins, per-cell alignment/vertical alignment, fills and image cells.
- **Callouts** (`callout`): a shaded single-cell panel with a left accent rule.
- **KPI list** (`key_values`): a borderless label/value table; values bold.
- **Cover hero** (`cover.hero_image`): a full-text-width inline image above the
  title; the title remains a paragraph for accessibility and metadata.
- **Cross-craft asset**: the T045 cover/icon SVG is rasterised with VectorCraft;
  the receiving DOCX test is the acceptance gate. The generator still works
  with a plain PNG if VectorCraft is absent.

## Standard profiles (T052)

A user does not ask for "a Word document"; they ask for a thesis, a đồ án, a
scientific report, an annual report. Each has a presentation contract.

- **Profile file:** `domains/docx/data/standard_profiles.json`. Every profile
  has `id`, `title`, `source` (publisher, document, URL, access date, evidence,
  status), `page`, `typography`, `paragraph`, `numbering`, `captions`,
  `front_matter_order`, `cover`, `headers_footers`, `references`, `limits`.
- **Merge order:** `DEFAULTS` → profile → explicit spec. The spec always wins;
  the profile is a default, never a cage. A profile is not "applied" by copying
  its values into a spec by hand.
- **Conformance:** `check_docx()` reads the produced DOCX and measures page
  size, margins, body/table font and size, line spacing, first-line indent,
  heading depth/numbering, caption numbering and position, page-number field,
  front-matter order, references/citations, abstract length, body pages and
  equation numbering. It returns `pass` / `warn` / `fail`; warnings are
  disclosures, failures block delivery.
- **University profiles:** `hust-datn-2017` (20/15/35/20 mm, TNR 13, 1.5,
  chapter captions, references before appendices, ≤50 body pages) and
  `vnu-uet-kl-2024` (25/30/30/20 mm, TNR 13, 1.3, 1 cm indent, 35–50 body
  pages, references after appendices).
- **Chapter numbering:** when `numbering.captions = "chapter"`, captions use
  `STYLEREF "Heading 1" \s` + `SEQ ... \s 1`; equations use the same pair.
  `Mở đầu` must use the standalone `Chapter Unnumbered` style, not a style based
  on Heading 1, or Word shifts every chapter by one.
- **Reference position:** `references.position` is `before_appendix` (HUST) or
  `after_appendix` (VNU/ISO).
- **Honesty:** a profile is a source, not a certificate. HUST 2017 is a faculty
  regulation; VNU-UET is one programme PDF. Label the scope.

## Standards-controlled report (T047)

A report that claims a standard must print the claim and the evidence.

- **Profile:** `domains/docx/data/report_standard.json` lists the standard,
  clause/scope, control, evidence and status. `front_matter.preface` renders it
  before the TOC.
- **ISO 7144 order:** `front_matter.order: "iso7144"` renders abstract → preface
  → TOC → lists. References are placed after appendices and use an unnumbered
  Heading 1 so the running header/STYLEREF still works.
- **ISO 2145:** heading numbering remains `1 / 1.1 / 1.1.1`.
- **ISO 690:** references use a labelled list plus `{{cite:key}}` links.
- **ISO 80000/8601:** unit symbols and value–unit spacing; ISO dates in data
  tables. ISO 7144 does not define margins/typeface, so those are house style.
- **GRI:** materiality, stakeholder table, GRI content index and Scope 1/2/3.
  The report says “self-declared, not externally assured”.
- **PDF/UA:** target only; the audit checks headings/alt/table headers/language,
  not the PDF tag tree.

**Do not turn the control table into a certificate.** A row is `met`,
`partly met` or `limited`; evidence is a file/field/page, not a logo.

## Rules → generator → checker

| Rule | Generator | Checker |
|---|---|---|
| DOC-PAGE-A4 | `page.size` / margins | page size, margins ≥20 mm |
| DOC-HEADING-HIERARCHY | built-in Heading styles | no jump >1 |
| DOC-HEADING-NUMBER | multilevel list linked to styles | numbering.xml + style link |
| DOC-TOC-FIELD | `TOC` field | TOC exists; levels cover headings |
| DOC-CAPTION-SEQ | `SEQ` + bookmark | caption field + bookmark |
| DOC-XREF-RESOLVE | `REF`/`PAGEREF` | target bookmark exists |
| DOC-FIGURE-INLINE | `wp:inline`, width only | extent ≤ text width |
| DOC-FIGURE-ALT | `wp:docPr@descr` | alt text present |
| DOC-FIGURE-DPI | width from aspect + token | effective PPI ≥150 |
| DOC-TABLE-WIDTH | fixed grid, scaled widths | grid ≤ text width + tolerance |
| DOC-TABLE-HEADER | `tblHeader` + `cantSplit` | header repeats |
| DOC-SECTION-PAGINATION | 3 sections + `pgNumType` | roman + decimal |
| DOC-HEADER-FIELDS | `STYLEREF`/`PAGE` | fields present |
| DOC-LANG | Normal style `w:lang` | language note |
| DOC-METADATA | core properties | title/author |
| DOC-FIELDS-UPDATED | Word/WordCraft refresh | dirty fields warning |
| DOC-APPENDIX | appendix list + `A.` prefix + reset | heading/caption check |
| DOC-EQUATION | `word_math.omml_from_latex`; `SEQ Equation` number | OMML present; equations count |
| DOC-SIDE-BY-SIDE | borderless 2-cell table, image width ≤ 60% | table/image width; caption below |
| DOC-TABLE-MERGE | header rows + `gridSpan`/`vMerge` | merge ranges; no header warning on layout tables |
| DOC-CELL-IMAGE | inline image in a table cell, alt text | `wp:docPr@descr`; row height |
| DOC-COVER-HERO | inline hero image, alt text, title still a paragraph | image width/alt; cover title |

## T045 evidence

- 11-page annual-report fixture: cover hero, KPI strip, callout, side-by-side
  figure/text, 2 OMML equations, merged-header table with icon cells, appendix.
- Word opened the exact DOCX, refreshed fields and exported PDF; pages 1, 6, 7,
  8 and 11 inspected.
- Audit: `ok: true`, 20 fields, 15 bookmarks, 6 tables, 6 drawings, 3 sections,
  2 equations (1 numbered), 5 merged cells, 5 images in cells; table-grid,
  vMerge-origin, image-width and alt-text checks; language `vi-VN`; no
  errors/warnings.
- Cross-craft: VectorCraft rasterised the SVG cover/icons; the DOCX render is
  the acceptance gate. The cross-craft rule is in `AGENTS.md` and
  `lab/standards/RESEARCH.md`.
- Report: `experiments/T045-20261101-opencode-advanced-docx/REPORT.md`.

## Using it

```bash
python3 scripts/document_forge.py build spec.json -o report.docx \
  --update word --render preview/ --report build.json
python3 scripts/document_audit.py report.docx --md audit.md
python3 scripts/word_field_kit.py fields report.docx
```

`--update word` requires Microsoft Word + `pywin32`; `--update wordcraft`
requires WordCraft. `--update none` builds valid fields with placeholder
results and sets `w:updateFields`.

## Limits

- **No Word playback.** The T039 evidence is structural, WordCraft-rendered and
  Word-exported PDF. It is not an interactive Word session with a human
  clicking every field.
- **Layout engine differs.** Word and WordCraft paginate differently (12 vs 13
  pages on the same fixture). TOC page numbers must be refreshed by the engine
  that produces the final PDF. The generator uses Word when available.
- **Field cache.** A DOCX can be structurally perfect and still show
  `{TOC ...}` until a layout engine refreshes it. The audit warns about dirty
  fields; it cannot compute page numbers.
- **PDF/UA and PDF/A** are not validated by this audit. Use veraPDF and a
  tag-tree/reading-order checker; the DOCX structure is necessary but not
  sufficient.
- **Fonts.** The audit checks effective DPI and alt text, not glyph coverage or
  font licences. Test Vietnamese/CJK glyphs in the final PDF.
- **Standards status.** The knowledge file records status at 2026-11-01. ISO
  5966 is withdrawn; ISO 7144/2145/7200/690 are current. Verify before citing.
- **Equation coverage.** The LaTeX parser covers the report subset, not
  matrices, `cases`, aligned environments or chemistry. Unsupported input
  raises an error; use WordCraft's equation command or a MathML→OMML path for
  those.
- **Merged-cell accessibility.** `gridSpan`/`vMerge` can change the header
  association for a screen reader; test the tag tree, not only the visual table.
- **Image-cell row heights.** A picture in a cell does not always expand the row
  automatically; the spec's `row_heights_mm` is the explicit control.
- **Cover art.** The hero is an inline image inside the text column, not a
  full-bleed print cover. Record the VectorCraft/other-tool version, command and
  asset licence; the synthetic art is CC0-style, not a customer brand.
- **Cross-craft acceptance.** A VectorCraft asset is accepted only after the
  DOCX render/audit; a tool transfer is not canonical by itself.

## Next

1. Add an OOXML schema validation step (`--xsd`) for the DOCX parts.
2. Add a native Word field-refresh/PDF export harness script (rung 4/5) with a
   recorded Word build and hash.
3. Add PDF/UA tag-tree checks (veraPDF or a PAC-compatible report) instead of
   only DOCX structure.
4. Add a real bibliography path (`b:Sources` + `CITATION`/`BIBLIOGRAPHY`) for
   customers who require Word's source manager.
5. Test landscape tables and two-column sections on a 30+ page fixture.
