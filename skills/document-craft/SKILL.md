---
name: document-craft
description: Build, repair and audit professional Word documents — reports, theses, project manuals and technical manuscripts — with real heading numbering, a live TOC, list of figures/tables, captions, cross-references, running headers, linked appendices, accessible images/tables and PDF/A or PDF/UA export. Use when the user asks for a DOCX/report/manuscript/thesis/proposal, complains that a TOC or figure number is wrong, needs Word formatting standards, wants tables and images aligned, or needs the document to survive editing in Word with or without WordCraft.
---

# Document Craft

> **Status: EXPERIMENTAL — T039 [docx], review requested.** This skill is not a
> canonical product path until an independent review accepts it. Use it, test
> it, and report failures; do not cite it as lab canon yet.

You are the document engineer, not a text formatter. The deliverable is an
editable Word file whose structure is real: headings are styles, the TOC is a
field, figure numbers are `SEQ` fields, "see Figure 3" is a `REF` field, and the
page numbers are `PAGE` fields. A PDF is an export, not the source.

Scripts live two levels above this file: `ROOT=<this skill dir>/../..`.

- **Required:** Python 3, `python-docx`, `lxml`.
- **Optional:** WordCraft (`wordcraft-cli`) for native field refresh/render;
  Microsoft Word via `pywin32` for the strongest field refresh/PDF export;
  LibreOffice for a cross-platform render; Pillow for image DPI checks.

## Workflow

1. **Freeze the requirement.** Determine, in this order:
   - the binding standard or template: institutional thesis rules, customer
     style guide, ISO 7144/ISO 2140/ISO 690, accessibility (WCAG 2.2 /
     PDF/UA), archival (PDF/A), or a technical-documentation standard
     (IEC/IEEE 82079-1, ISO 7200);
   - language(s), page size, output (DOCX, PDF, PDF/A, PDF/UA), classification;
   - whether an existing document/template must be preserved.
   If the user gives no standard, use the defaults in
   `$ROOT/domains/docx/data/document_system.json` and say so. Never invent a
   "mandatory ISO" clause; a standard is mandatory only when a law, contract or
   institution cites it.
2. **Inventory before editing.** For an existing DOCX, list sections, page
   setup, styles, fields, bookmarks, captions, cross-references, headers,
   footers, tables, images and metadata. Preserve what works. Read
   `references/word-properties.md` for the exact component/property map.
3. **Plan the document map.** Cover → front matter (TOC, lists, abstract) →
   body (numbered headings) → references → appendices. Assign figure/table
   numbers and bookmarks before writing the lists of figures/tables.
4. **Build with structure.**
   - Preferred: `python3 $ROOT/scripts/document_forge.py build spec.json -o out.docx`.
     The spec schema is `$ROOT/domains/docx/schemas/document_spec.schema.json`.
   - Or use the native commands in `references/word-properties.md`
     (`wordcraft-cli run --file … --cmd '…'`).
   - Or patch an existing DOCX with `python-docx` + the helpers in
     `$ROOT/scripts/word_field_kit.py`.
   Never type a TOC, figure number or page number as plain text.
5. **Refresh fields.** Word computes page numbers and TOC entries; the file
   must be opened by a layout engine. Use, in order:
   - `document_forge.py … --update word` (Microsoft Word via COM);
   - `--update wordcraft` (`wordcraft-cli convert … --update-fields`);
   - if neither is available, leave `w:updateFields` set and tell the user to
     press `Ctrl+A`, `F9` in Word. Do not claim a final TOC from stale results.
6. **Audit and render.** Run
   `python3 $ROOT/scripts/document_audit.py out.docx --md audit.md` (or
   `document_forge.py audit`). Fix every error, then inspect the rendered pages
   from `--render`. A clean XML audit is rung 1, not proof that Word paginated
   correctly.
7. **Deliver** the DOCX, the audit JSON/Markdown, the rendered page images and
   a short change report naming the evidence rung (see
   `$ROOT/docs/VERIFICATION.md`).

## Rich-report blocks (T045)

A real report is not only body paragraphs. The spec supports:

| Block | Use | Key rules |
|---|---|---|
| `figure_text` | One image beside a text column | Borderless 2-cell table; image ≤60% width; caption below; alt text; inline image |
| `equation` | Native Word math | LaTeX subset → OMML; `SEQ Equation` number right-aligned; unsupported command raises an error |
| `table` + `advanced` | Multi-row header, merged cells, image cells, per-cell alignment | `header_rows`, `colspan`/`rowspan`, `merges`, `row_heights_mm`, `cell_margins_mm`; header repeats |
| `callout` | A single message/insight | Shaded panel, left accent rule, readable contrast |
| `key_values` | KPI strip | Borderless label/value rows; values bold; no fake table header |
| `cover.hero_image` | Brand/cover band | Inline image, alt text, title remains a paragraph for metadata/accessibility |

**Cover assets are a cross-craft opportunity.** The T045 fixture writes a cover
SVG, rasterises it with VectorCraft, then embeds the PNG. The DOCX render/audit
is the acceptance gate. Record the source tool/version/command and the asset
licence. If VectorCraft is absent, use a plain PNG; the document path must still
work.

## Ask for the standard, then control it (T052)

A Word report is not "a document"; it is a thesis, a đồ án, a scientific report,
an annual report. The presentation rules are part of the deliverable.

1. **Ask which standard, and which edition.** "Đồ án đại học" is not enough:
   HUST 2017 and VNU-UET differ in margins, line spacing, page limits and
   reference position. If the user has no template, choose a named profile,
   state its source and scope, and let them correct it.
2. **Load the profile, do not retype it.**
   ```powershell
   python scripts/document_forge.py build spec.json -o report.docx `
     --profile hust-datn-2017 --update word `
     --conformance artifacts/conformance-hust.md
   ```
   Profiles live in `domains/docx/data/standard_profiles.json`; `--profiles`
   points at another file. `python scripts/docx_profiles.py list` shows them.
3. **The spec wins.** Profile → spec deep merge; explicit page/typography values
   override the profile. Do not hand-copy profile values into the spec.
4. **Measure the produced file.** `check_docx()` reads margins, fonts, spacing,
   captions, front matter, page numbers, references and page count. A clean
   build report is not a conformance report.
5. **Chapter-based captions.** For HUST/VNU, `numbering.captions = "chapter"`
   uses `STYLEREF "Heading 1" \s` + `SEQ ... \s 1`. `Mở đầu` uses the standalone
   `Chapter Unnumbered` style; a Heading 1 derivative shifts every chapter.
6. **State the limits.** HUST 2017 is a faculty regulation; VNU-UET is one
   programme PDF. A profile is a source, not a certificate. `body_pages`
   excludes end matter but includes tables/figures; VNU excludes tables/figures,
   so the check is lenient.
7. **Show the user the evidence.** Print a small table: control, expected,
   measured, status. That is the difference between "I followed a standard" and
   "I measured the file against a standard".

**Do not promise a page count you did not measure in Word.** Word and
LibreOffice paginate differently; profile page limits need a Word/PDF count.

## Standards-controlled report (T047)

Use this when the user says “a real report”, “a standard”, “show me what you
control”, or asks for an annual/ESG/thesis/manual.

1. **Pick a profile, not a vibe.** `domains/docx/data/report_standard.json`
   records ISO 7144 (structure), ISO 2145 (numbering), ISO 690 (references),
   ISO 80000/8601 (units/dates), WCAG 2.2, GRI 1/2/3/305. Do not claim a
   standard you cannot evidence.
2. **Print the control matrix before the TOC.** For each control: ID, clause,
   implementation, evidence, status (`met` / `partly` / `limited`).
3. **Order front matter for the standard.** `front_matter.order: "iso7144"`
   gives abstract → preface → TOC → lists. References go after appendices and
   carry no body section number.
4. **Give the reader enough.** A 20+ page annual report has: cover, document
   control, abstract, TOC/lists, strategy, products, financials, operations,
   governance, risk, materiality, environment, social, supply chain,
   methodology, conclusion, GRI index, data appendix, glossary, references.
5. **Every table/figure has caption, source and number; every equation has a
   number and a symbol legend when needed.**
6. **State limits.** Self-declared ESG, no external assurance, PDF/UA not
   validated, synthetic data. A limitation is part of the craft.

**Do not use ISO 7144 as a certification for an annual report.** It is a
presentation standard for theses and similar documents; use its structure and
numbering, and say so.

## One rule per failure mode

| Symptom | Real cause | Fix |
|---|---|---|
| TOC shows `{TOC \o "1-3" \h \z \u}` | Field codes are displayed, or the field was never updated | `Alt+F9` to hide codes; update fields; keep the TOC as a field |
| TOC page numbers start at 4, not 1 | TOC copied physical page index, or section page numbering is wrong | Put front matter and body in separate sections; set `pgNumType start=1` on the body; update in Word |
| Figure numbers are all "1" | Captions are typed text or SEQ fields are not updated | Use `SEQ Figure \* ARABIC`; update fields; one field per caption |
| "Figure 3" does not follow the caption | The cross-reference points at the wrong bookmark or the caption was copied | Bookmark the number (and the caption), use `REF bookmark \h` / `PAGEREF` |
| Image jumps to another page | Floating anchor with wrap | Use inline images for report figures; centre; keep with caption |
| Image is blurry | Effective PPI too low at the placed size | Place at ≤ native size; 150 PPI screen, 300 PPI print, 600 PPI line art |
| Table spills into the margin | AutoFit/percent width | Fixed layout, explicit `tblGrid` widths summing to the text column |
| Header shows the wrong chapter | `STYLEREF` style name is wrong or the heading is not a real Heading 1 | Use built-in Heading 1; `STYLEREF "Heading 1"` in the header |
| Appendix figures say "Figure 1" | No appendix numbering/reset | Appendix heading list (A, A.1), caption prefix A., separate SEQ reset per appendix |
| PDF looks right but is inaccessible | No tags/alt text/heading structure | Author with styles and alt text; export tagged; validate PDF/UA |
| Font changes on another machine | Font not embedded/available | Use a standard font or embed it; check the licence; PDF/A embeds subsets |

## Standards: what is actually binding

Read `references/standards.md` for the full map and sources. The short version:

- **Structure/report:** ISO 7144 (theses/reports, current), ISO 5966
  (**withdrawn 2000**, legacy only), ISO 2145 (numbering, current), ISO 690
  (references, 2021), ISO 7200 (title-block/header fields, current), ISO 8601
  (dates), ISO 80000 (units).
- **Quality/records:** ISO 9001 clause 7.5 (documented information), ISO
  10013, ISO 15489-1 (records), ISO/IEC 27001 (classification/access).
- **Projects/systems:** ISO 21502 (project management), ISO/IEC/IEEE 15288
  (system life cycle), IEC/IEEE 82079-1 (information for use).
- **Files/accessibility:** ISO/IEC 29500 (OOXML), ISO 19005 (PDF/A), ISO 14289
  (PDF/UA), WCAG 2.2 / EN 301 549.
- **Print:** ISO 216 (A4), ISO 12647 / PDF/X, ISO 3664.

Do not call a standard "mandatory" without naming the law, contract, template
or procurement clause that makes it mandatory. When they conflict, the order is:
law/regulation → contract/procurement → institutional template → the standards
above → this skill's defaults.

## Design defaults (not standards)

From `$ROOT/domains/docx/data/document_system.json`:

- A4, margins 25/25/30/25 mm, text width ≈155 mm; one column.
- Body 10–12 pt, line spacing 1.15–1.5, 60–90 characters per line.
- H1 18–20 pt, H2 14–16, H3 12–13, H4 10.5–12; one heading family plus one
  body family; keep the family count low.
- Figure caption below; table caption above; captions 8–10 pt.
- Tables 8–10 pt, fixed grid, repeating header, numeric columns right-aligned,
  units in the header, source note below.
- Text contrast 4.5:1; large text/graphics 3:1; alt text on informative images;
  document title and language set.

These are defaults. A customer template or accessibility law overrides them.
Do not hard-code a new threshold in a script; add a token with a source.

## With or without WordCraft

**With WordCraft** (native app engine):
- Build: `references.toc`, `references.caption`, `insert.crossReference`,
  `insert.bookmark`, `insert.header`, `insert.footer`, `insert.pageNumber`,
  `layout.pageSetup`, `table.repeatHeader`, `table.columnWidth`,
  `picture.altText`, `styles.modify`, `list.define`, `para.multilevel`.
- Refresh: `wordcraft-cli convert in.docx out.docx --update-fields` or
  `wordcraft-cli run --file in.docx --cmd 'references.updateFields={"all":true}' --save out.docx`.
- Render: `wordcraft-cli render out.docx page.png --page N --scale 2`.
- Inspect: `wordcraft-cli inspect out.docx` (fields, styles, blocks).
- Convert: `wordcraft-cli convert out.docx out.pdf`.

**Without WordCraft** (portable path):
- Build with `python-docx` for content/styles/sections/images/tables and
  `word_field_kit.py` for the fields/TOC/captions/cross-references.
- Refresh with Word COM (`pywin32`) on Windows or LibreOffice headless on
  Linux/macOS. Neither computes a TOC as reliably as Word; test the exact
  output.
- Audit with `word_field_kit.audit_docx` / `document_audit.py`: balanced
  fields, bookmark targets, TOC levels, table grid vs `gridSpan`/`vMerge`,
  image width vs cell width, image DPI/alt text, OMML fractions/n-ary bodies,
  equation counts, section page numbering and language.
- Render with Word → PDF → PNG (`--render`) or LibreOffice → PDF. Record which
  engine produced the pixels.

**Neither** is a valid answer for the final TOC/page numbers: the fields are
there, but the cached results are placeholders until a layout engine refreshes
them. Say so.

## Commands

```bash
# Build from a semantic spec (schema: domains/docx/schemas/document_spec.schema.json)
python3 $ROOT/scripts/document_forge.py build report.json -o report.docx \
  --update word --render preview/ --report build.json

# Rich report: cover hero, side-by-side, equations, merged table, image cells
python3 $ROOT/scripts/document_forge.py build \
  $ROOT/examples/docx/annual_report_spec.json -o annual.docx \
  --update word --render preview/

# Audit an existing DOCX (no build)
python3 $ROOT/scripts/document_audit.py report.docx --md audit.md

# List fields (TOC/SEQ/REF/PAGE/STYLEREF) and cached results
python3 $ROOT/scripts/word_field_kit.py fields report.docx

# WordCraft native path
wordcraft-cli run --file report.docx \
  --cmd 'references.updateFields={"all":true}' \
  --cmd 'references.updateToc={}' \
  --save report.updated.docx
```

## Definition of done

- Every heading is a built-in Heading style; numbering is a multilevel list
  linked to the styles; no typed numbers.
- The TOC, list of figures/tables, figure/table numbers, cross-references and
  page numbers are fields with resolved results.
- Every `REF`/`PAGEREF` target exists; bookmarks are unique; no field is
  unbalanced.
- Images are inline, centred, aspect-preserving, ≤ text width, with alt text
  and effective PPI at or above the target.
- Tables have a fixed grid inside the text column, a repeating header, a
  caption above and a source note below.
- Cover/front matter/body/appendix pagination is correct; headers show the
  current chapter, not the previous one.
- The rendered pages were inspected; the audit and the render agree.
- The report names the evidence rung and does not claim Word playback or PDF/UA
  conformance without the corresponding tool and check.
