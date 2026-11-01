# Document system: professional DOCX with real links

Status: EXPERIMENTAL — T039 [docx], review requested (2026-11-01). Evidence
reached: structural (rung 1), WordCraft layout (rung 2) and Microsoft Word
parse + field refresh + PDF export (rungs 4–5). No LibreOffice (rung 3), no
human edit/print (rung 6), no PDF/UA or PDF/A validation. PowerPoint playback
is irrelevant here; Word playback is not claimed.

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
| `domains/docx/schemas/document_spec.schema.json` | Semantic input for the generator |
| `scripts/word_field_kit.py` | Fields, TOC, SEQ captions, REF/PAGEREF, STYLEREF, bookmarks, numbering, audit |
| `scripts/document_forge.py` | Build DOCX from a spec; refresh with Word/WordCraft; render |
| `scripts/document_audit.py` | Standalone structural audit |
| `skills/document-craft/` | Workflow, standards note, Word property matrix, layout recipes |
| `tests/test_document_craft.py` | Structural build/audit tests |

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

## Next

1. Add an OOXML schema validation step (`--xsd`) for the DOCX parts.
2. Add a native Word field-refresh/PDF export harness script (rung 4/5) with a
   recorded Word build and hash.
3. Add PDF/UA tag-tree checks (veraPDF or a PAC-compatible report) instead of
   only DOCX structure.
4. Add a real bibliography path (`b:Sources` + `CITATION`/`BIBLIOGRAPHY`) for
   customers who require Word's source manager.
5. Test landscape tables and two-column sections on a 30+ page fixture.
