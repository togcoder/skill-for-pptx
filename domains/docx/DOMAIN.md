# Domain: docx (Word documents)

## Scope

Long-form documents: reports, theses, contracts, project manuals, papers.
"Done well" means readable typography, correct styles and numbering, real
fields, and an accessible structure that survives editing.

## Thesis

Documents are read, not presented. The canon is Word's own model:

- styles, not direct formatting;
- built-in headings, a multilevel list linked to the styles, and a `TOC` field;
- sections, page numbering, headers/footers, and `STYLEREF`/`PAGE` fields;
- `SEQ` captions, bookmarked numbers, `REF`/`PAGEREF` cross-references;
- fixed table grids with a repeating header row;
- inline pictures with alt text, not drifting floating anchors;
- native OMML equations, side-by-side media/text, merged-header tables and
  image cells for a report that is more than body paragraphs;
- document language and title metadata for accessibility.

A DOCX is structurally valid when the fields are balanced, the bookmarks
resolve and the table/image geometry fits the text column. A DOCX is *finished*
only when a layout engine refreshes the fields and the rendered pages are
inspected.

Do **not** import slide grids, motion, click rhythm, or PowerPoint design tokens.
They are a different native model. There is no accepted transfer from `pptx`
to `docx` yet.

## Native canon and sources

- ECMA-376 / ISO/IEC 29500-1 WordprocessingML: `w:sectPr`, `w:styles`,
  `w:fldChar`/`w:instrText`, `w:bookmarkStart`, `w:tbl`, `w:drawing`.
- The Word object model (`Fields`, `TablesOfContents`, `Range`, `Styles`,
  `PageSetup`, `InlineShapes`).
- Built-in style sets and themes; `w:outlineLvl`.
- ISO 7144 (theses/reports, current), ISO 2145 (numbering, confirmed 2026),
  ISO 690:2021 (references), ISO 7200 (title-block/header fields), ISO 8601
  (dates), ISO 80000 (units); ISO 5966 is **withdrawn**.
- WCAG 2.2, PDF/UA (ISO 14289), PDF/A (ISO 19005), ISO 15489 (records).
- Typographic measure: 60–90 characters per line, 10–12 pt body, 1.15–1.5 line
  spacing. These are judgement/published defaults, not an ISO clause.

## Code

| Module | Status | Tests |
|---|---|---|
| `scripts/wordcraft_bridge.py` | Experimental (T037): bridge to the external ArtCraft WordCraft tool (Windows, `D:\artcraft`); unreviewed | `tests/test_craft_bridges.py` |
| `scripts/word_field_kit.py` | Experimental (T039): fields, TOC, SEQ captions, REF/PAGEREF, STYLEREF, bookmarks, numbering, structural audit | `tests/test_document_craft.py` |
| `scripts/document_forge.py` | Experimental (T039): build a DOCX from `domains/docx/schemas/document_spec.schema.json`; refresh via Word/WordCraft; render | `tests/test_document_craft.py` |
| `scripts/document_audit.py` | Experimental (T039): standalone audit entry point | `tests/test_document_craft.py` |
| `scripts/word_math.py` | Experimental (T045): LaTeX subset → OMML equations; strict errors for unsupported commands | `tests/test_document_advanced.py` |
| `scripts/docx_profiles.py` | Experimental (T049): named standard profiles, profile merge and DOCX conformance check | `tests/test_docx_profiles.py` |

No docx module is a product path until `research/reviews/` contains an accepted
review. The modules carry `Status: EXPERIMENTAL` in their headers.

## Data and skill

| Item | Path | Status |
|---|---|---|
| Design/standards data | `domains/docx/data/document_system.json` | T039; provenance recorded; unreviewed |
| Report standards profile | `domains/docx/data/report_standard.json` | T047; ISO/GRI sources, controls and status; unreviewed |
| Named standard profiles | `domains/docx/data/standard_profiles.json` | T049; HUST 2017, VNU-UET, ISO 7144, annual/GRI; sourced; unreviewed |
| Spec schema | `domains/docx/schemas/document_spec.schema.json` | T039/T045; unreviewed |
| Skill | `skills/document-craft/` | T039/T045/T047/T049; experimental |
| Example specs | `examples/docx/report_spec.json`, `annual_report_spec.json` | T039/T045; synthetic, CC0-style assets |

The data file contains page/type/figure/table/field/accessibility tokens,
standard statuses and `sources`. Every threshold used by the audit reads a token;
do not hard-code a new one in a generator.

## Evidence ladder

| Rung | Tool | T039/T045/T047/T049 evidence |
|---|---|---|
| 1 | schema / structural audit | T039: 29 fields, 22 bookmarks; T045: 20 fields, 2 equations, 5 merged cells; T047: 135 fields, 91 bookmarks, 37 headings (max H3), 38 tables, 4 figures, 5 equations, 11 references; T049: HUST 204 fields, 88 bookmarks, 59 headings (max H3), 23 tables, 7 figures, 9 equations, 12 references, 13 citations, 1,055 paragraphs; VNU 22 tables, 1,032 paragraphs; both `vi-VN`, no errors/warnings |
| 2 | layout engine (WordCraft) | T039/T045 WordCraft render; T047/T049 use Word COM for the final layout |
| 3 | independent reader (LibreOffice Writer) | Not run on this host |
| 4 | Word COM open / field update | T045/T047/T049: Word opened the exact DOCX, refreshed fields, saved; T049 `updated_by: word` |
| 5 | Word PDF export / page inspection | T045: 11 pages; T047: 25 pages; T049: HUST 48 pages (34 body pages), VNU-UET 45 pages (35 body pages); cover, TOC, chapter, table, architecture, equations, references and appendix inspected |
| 6 | human edits/prints | Not run |

The T039 report is `experiments/T039-20261101-opencode-office-canon/REPORT.md`.

## State (2026-11-02)

- **T049 [docx] configurable standard profiles**: a profile layer
  (`hust-datn-2017`, `vnu-uet-kl-2024`, `iso-7144-thesis`,
  `annual-report-gri`), a 34-page HUST scientific report (48 pages total) and a
  35-page VNU-UET build of the same content (45 pages total). Both pass their
  conformance check (17/17 and 18/18); **review requested**.
- **T047 [docx] standards report**: a 25-page annual/ESG report with a declared
  ISO/GRI standards profile, a control matrix, ISO 7144 front-matter order,
  ISO 2145 numbering, 5 OMML equations, 38 tables, GRI index, VectorCraft
  product illustration and SheetCraft charts; **review requested**.
- **T045 [docx] advanced report**: native OMML equations, side-by-side
  figure/text, merged-header tables, image cells, callouts, cover hero and a
  synthetic annual-report fixture; **review requested**.
- **T039 [docx]**: DocumentCraft prototypes + audit + standards/data + skill;
  merged to `main` after owner approval, with the Argon review fixes applied.
- Evidence reached: rung 1 structural and rung 4/5 Word parse/render. No rung 6
  human edit/print; no PDF/UA or PDF/A validation.
- Known limitation: Word and WordCraft paginate differently (12 vs 13 pages on
  the fixture). The generator uses Word for final field refresh when available;
  WordCraft is a fallback.
- Known limitation (T049): a style based on Heading 1 is still counted by
  `STYLEREF "Heading 1"` and shifts the chapter counter. `Mở đầu` uses a
  standalone `Chapter Unnumbered` style (outlineLvl 0, no basedOn); do not
  "simplify" it back to a Heading 1 derivative.
- Known limitation (T049): `body_pages` excludes end matter but includes
  tables/figures. VNU-UET's 35–50 rule excludes tables/figures, so the check is
  lenient; a strict counter is still open.
- Known limitation (T049): the HUST profile is the 2017 faculty regulation, not
  the current university-wide template; the VNU-UET profile is one faculty PDF.
  Both are named sources, not universal rules.
- Known limitation: an early `TOC \\c` list repeated the first `SEQ` number
  because the Word refresh updated `TablesOfContents` but not
  `TablesOfFigures`. The fix updates `TablesOfFigures`; the `ref_pageref`
  fallback remains for renderers that cannot update a TOF.
- Known limitation: WordCraft `convert --update-fields` dropped
  `wp:docPr@descr`; T039 repairs it for the WordCraft path.

## Open questions

1. Should `document_forge` become the canonical builder, or should it merge into
   `wordcraft_bridge`? One canonical module per capability (MERGE.md).
2. PDF/UA: add a veraPDF/tag-tree check; DOCX structure is necessary but not
   sufficient.
3. LibreOffice Writer render for rung 3 on a machine without Word.
4. Native Word bibliography (`b:Sources` + `CITATION`/`BIBLIOGRAPHY`) for
   customers who require Word's source manager.
5. Landscape tables and two-column sections on a 30+ page fixture.
6. Font embedding and Vietnamese/CJK glyph coverage checks.
7. Equation coverage: matrix/aligned environments, cases, and a MathML/OMML
   fallback for formulas outside the LaTeX subset.
8. Table accessibility: merged cells can change the header association; test
   with a screen reader/PDF tag tree.
9. Cross-craft asset provenance: record the VectorCraft version/command and the
   licence for every generated cover/icon in the report.
10. Cover art: full-bleed/print-safe variants; the current hero is an inline
    image inside the text column.
