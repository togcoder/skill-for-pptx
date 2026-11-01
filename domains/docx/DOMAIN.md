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

No docx module is a product path until `research/reviews/` contains an accepted
review. The modules carry `Status: EXPERIMENTAL` in their headers.

## Data and skill

| Item | Path | Status |
|---|---|---|
| Design/standards data | `domains/docx/data/document_system.json` | T039; provenance recorded; unreviewed |
| Spec schema | `domains/docx/schemas/document_spec.schema.json` | T039; unreviewed |
| Skill | `skills/document-craft/` | T039; experimental |
| Example spec | `examples/docx/report_spec.json` | T039; synthetic |

The data file contains page/type/figure/table/field/accessibility tokens,
standard statuses and `sources`. Every threshold used by the audit reads a token;
do not hard-code a new one in a generator.

## Evidence ladder

| Rung | Tool | T039 evidence |
|---|---|---|
| 1 | schema / structural audit | `document_audit.py`: 29 fields, 22 bookmarks, 3 sections, 3 tables, 2 figures; no errors/warnings |
| 2 | layout engine (WordCraft) | WordCraft render; TOC updated, but page numbers were physical and a `TOC \\c` caption list repeated the first number |
| 3 | independent reader | Not run (LibreOffice Writer not installed on this host) |
| 4–5 | Word COM open / PDF export | Word opened the exact DOCX, refreshed fields, exported a 12-page PDF; pages inspected |
| 6 | human edits/prints | Not run |

The T039 report is `experiments/T039-20261101-opencode-office-canon/REPORT.md`.

## State (2026-11-01)

- **T039 [docx]**: DocumentCraft prototypes + audit + standards/data + skill;
  report written; tests pass; **review requested**. Not merged into a product
  path.
- Evidence reached: rung 1 structural and rung 4/5 Word parse/render. No rung 6
  human edit/print; no PDF/UA or PDF/A validation.
- Known limitation: Word and WordCraft paginate differently (12 vs 13 pages on
  the fixture). The generator uses Word for final field refresh when available;
  WordCraft is a fallback.
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
