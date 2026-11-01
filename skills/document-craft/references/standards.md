# Standards for professional documents

This is the research note behind `domains/docx/data/document_system.json`. It is written
for a document engineer, not a lawyer. **No standard is self-executing.** A
standard becomes mandatory when a law, regulation, contract, procurement clause
or institutional submission rule cites it. Always verify the current edition and
the exact clause at the publisher before putting a standard number in a
deliverable.

Statuses below were checked against the publisher on 2026-11-01.

## 1. The binding hierarchy

Use this order when requirements conflict:

1. **Law / regulation** — e.g. EU accessibility law, national archive rules,
   Vietnamese administrative-document rules, product-safety law.
2. **Contract / procurement** — the customer's document standard, security
   classification, data-protection clauses, deliverable format.
3. **Institution / programme template** — university thesis regulation, project
   management plan, brand/style guide.
4. **International standards** — ISO/IEC/IEEE, IEC, W3C, ECMA.
5. **This skill's defaults** — only where the four levels above are silent.

A standard is not "mandatory for large projects" by itself. For example:

- ISO 9001 certification is a market/contract requirement, not a general
  statutory formatting law.
- ISO 7144 is guidance for theses; a university regulation usually overrides
  its margins and type sizes.
- ISO 5966 was withdrawn in 2000; a template that cites it is citing a legacy
  document, not a current ISO requirement.
- PDF/A is mandatory when an archive, court or regulator requires it.
- WCAG 2.2 / EN 301 549 bind public-sector ICT procurement in the EU and many
  accessibility clauses elsewhere; WCAG itself is a W3C Recommendation, not an
  ISO standard (ISO/IEC 40500 is WCAG 2.0).

## 2. Standards map

### 2.1 Report and thesis structure

| Standard | Status | What it controls | How to comply in Word |
|---|---|---|---|
| **ISO 7144:1986** Documentation — Presentation of theses and similar documents | Current (confirmed) | Title page, front matter, contents, headings, illustrations, tables, references, appendices, pagination | Use the institutional template first. Separate cover/front matter/body/appendices into sections. Real Heading styles. TOC field. Captions with SEQ. Appendices A, A.1. |
| **ISO 5966:1982** Documentation — Presentation of scientific and technical reports | **Withdrawn 2000-10-03** | The classic report layout: title page, contents, headings, figures, tables, references, appendices | Do not present it as current. If a legacy template cites it, keep the template's structure and note the withdrawal. |
| **ISO 2145:1978** Numbering of divisions and subdivisions | Current (confirmed 2026) | 1, 1.1, 1.1.1; Arabic numerals; full stops between levels; no final full stop | Link a multilevel list to Heading 1–9. Use `lvlText` `%1`, `%1.%2` (not `%1.`). Do not type numbers. |
| **ISO 690:2021** Bibliographic references and citations | Current | Deterministic references and in-text citations for monographs, articles, web resources, datasets | Pick one style; hanging indent; ISO 8601 dates; DOI/URL with access date; link citations to entries. |
| **ISO 7200:2004** Data fields in title blocks and document headers | Current (confirmed 2025) | Document identifier, title, revision, date, author, owner, classification, page count | Map the fields into the Word header/footer or drawing title block. Keep field names and lengths stable. |
| **ISO 8601-1/-2:2019** Date and time | Current | `YYYY-MM-DD`, times, durations, intervals, UTC offsets | Use ISO dates in metadata, references and tables; state the time zone for timestamps. |
| **ISO 80000-1:2022** Quantities and units | Current | Quantity/unit symbols, prefixes, decimal sign, significant figures | Units in column headers; space between value and unit; consistent decimal marker; stable precision. |
| **ISO 216:2007** A and B paper series | Current | A4 = 210 × 297 mm | Set A4 explicitly; check the PDF at 100%. |
| **ISO 3098-1:2015** Technical lettering | Current | Legibility, character height, stroke width for technical drawings | Use a technical sans face at the specified height; no decorative face for dimensions. |
| **ISO 15489-1:2016** Records management | Current | Authenticity, reliability, integrity, usability, retention, access | Document ID, version, owner, approval, classification, retention and audit trail. |
| **ISO 9001:2015 clause 7.5** Documented information | Check current edition | Creation, updating, identification, review, approval, availability, protection, retention | Controlled template with ID/revision/approval/change log; distribution and retention records. |
| **ISO 10013:2021** Guidance for documented information | Current | Structure, content, review, approval, control | Define document types, owners and change control before writing. |
| **ISO/IEC 27001:2022** ISMS | Current | Classification, access control, supplier security, incident records | Classification in header/footer; distribution matrix; no sensitive metadata leakage. |
| **ISO 21502:2020** Project management | Current | Governance, business case, plans, stage reports, risk, change, lessons learned | Align the report hierarchy with the project lifecycle and decision gates. |
| **ISO/IEC/IEEE 15288:2023** System life cycle | Current | Technical/project/agreement processes and their information items | Map each deliverable to a lifecycle process and a gate; link requirements, architecture, V&V. |
| **IEC/IEEE 82079-1:2019** Information for use | Current | Safety information, task orientation, language, readability, illustrations, usability | Task-based instructions; safety before the task; warnings distinct; user testing; required languages. |
| **ISO 17100:2015 / ISO 18587:2017** Translation / MT post-editing | Current | Competence, process, revision, review, post-editing quality | Freeze the source; provide terminology; second-linguist revision; record post-editing level. |
| **ISO 704:2022 / ISO 10241-1:2011** Terminology | Current | Term formation, definitions, synonyms, scope notes | Project glossary; one preferred term per concept; define before first use. |
| **ISO 3166-1 / ISO 639 / ISO 4217** Codes | Current | Country, language, currency codes | Use codes in metadata and tables; version the code list. |

### 2.2 File format, accessibility and preservation

| Standard | Status | What it controls | How to comply |
|---|---|---|---|
| **ISO/IEC 29500-1:2016** Office Open XML | Current | Package, WordprocessingML, SpreadsheetML, PresentationML, fields, styles, sections, tables, drawings | Write valid OOXML; keep relationships; validate ZIP/XML; preserve parts when patching. Word writes transitional OOXML by default; do not claim Strict without a test. |
| **WCAG 2.2** W3C Recommendation, 5 Oct 2023 | Current | Perceivable, operable, understandable, robust content: contrast, alt text, headings, tables, keyboard, reading order, language | Real heading styles; alt text; table header rows; 4.5:1 text (3:1 large/graphics); document title; language; tagged PDF; screen-reader test. |
| **EN 301 549 v3.2.1 (2021)** | Current | ICT accessibility requirements for EU procurement | Treat WCAG 2.2 AA as the baseline; check the procurement's exact clause. |
| **ISO 14289-1:2014 (PDF/UA-1)**, **ISO 14289-2:2024 (PDF/UA-2)** | Current | Tag tree, reading order, alt text, language, table headers, bookmarks, metadata | Export a tagged PDF; validate the tag tree/reading order; alt text and headings must come from the authoring file. |
| **ISO 19005-4:2020 (PDF/A-4)** | Current | Long-term preservation: embedded fonts, device-independent colour, no external dependencies, metadata | Export tagged PDF/A at the required level; embed fonts; validate with veraPDF. |
| **ISO 32000-2:2020** PDF 2.0 | Current | PDF object model, tags, metadata | Use a conforming PDF writer; do not hand-edit PDFs for accessibility. |
| **ISO 12647-2:2013 / ISO 15930 (PDF/X) / ISO 3664:2009** | Current | Print colour, ink limits, ICC profiles, PDF/X, viewing conditions | Use the printer's ICC profile; convert to the target CMYK; export PDF/X with bleed/trim; proof under ISO 3664. |

### 2.3 Vietnamese administrative documents

If the deliverable is a **Vietnamese state administrative document** (văn bản
hành chính), the binding rules are not ISO 7144. Check **Nghị định
30/2020/NĐ-CP** (30/12/2020, effective 05/03/2021) and its appendices, plus any
amending document. It specifies the national format, font, margins, page
numbers and signing block for those documents. For theses and research reports,
the university/programme regulation is the binding document; many are based on
ISO 7144 but override margins, font and citation style. Do not apply the
administrative-document format to a project report unless the client asks for it.

## 3. Structure rules that survive editing

### 3.1 Headings

- Use built-in **Heading 1–9** styles, not bold body text. The navigation pane,
  TOC, PDF bookmarks and screen readers all read the outline level.
- Link a **multilevel list** to the heading styles. ISO 2145 is `1`, `1.1`,
  `1.1.1` with no trailing full stop. Word's default is `1.`, `1.1.`; choose one
  and keep it consistent.
- Keep `keepNext`, `keepLines` and `widowControl` on. H1 may start a new page;
  H2/H3 should not create a page by themselves.
- Do not skip levels. A document that goes H1 → H3 fails the accessibility
  structure and often produces a broken TOC.

### 3.2 TOC and field results

- The TOC is a field: `TOC \o "1-3" \h \z \u`. `\h` makes entries clickable;
  `\z` hides tab/page numbers in web layout; `\u` uses outline levels.
- A TOC field has a **cached result**. After building, the result is a
  placeholder until Word/LibreOffice/WordCraft refreshes it. `w:updateFields`
  asks Word to refresh on open; `Ctrl+A`, `F9` refreshes manually.
- In Word, the TOC uses the **displayed page number** of each heading. If the
  body section restarts at 1, the TOC should show 1, 2, …; if it shows the
  physical page index, the section's `pgNumType` is wrong or the TOC was
  generated by a renderer that ignores section numbering. Test the exact file.
- A list of figures/tables is normally `TOC \h \z \c "Figure"` /
  `\c "Table"`. Word's caption cache can repeat the first `SEQ` value when the
  captions and the list are updated in one pass. The T039 implementation uses
  `REF` + `PAGEREF` per entry instead: the label and page are live, and the list
  cannot cache the wrong number. If you use `TOC \c`, refresh captions first,
  then the list, and inspect the result.

### 3.3 Captions and cross-references

- Figure: `Figure <SEQ Figure \* ARABIC> — caption`, below the image.
- Table: `Table <SEQ Table \* ARABIC> — caption`, above the table.
- Appendix: `Figure A.1` / `Table A.1`; use an appendix heading list (A, A.1)
  and a per-appendix reset (`SEQ … \r 1`) or `\s 1` with a verified heading
  number. The T039 generator uses an explicit `A.` prefix plus a per-appendix
  SEQ reset because Word's `\s 1` did not pick up a directly-numbered appendix
  heading in testing.
- Bookmark the number (for `{{num:fig-1}}`) and the label+number (for
  `{{ref:fig-1}}`), not the whole paragraph. Use `REF bookmark \h` and
  `PAGEREF bookmark \h`.
- Every `REF`/`PAGEREF` target must exist. Renaming or deleting a bookmark
  breaks the link; the audit must catch it.

### 3.4 Sections, headers and page numbers

- Cover: no header/footer, no page number.
- Front matter: roman numerals (`i`, `ii`, …), restart at 1.
- Body: arabic numerals, restart at 1.
- Appendix: continue body numbering unless the institution says otherwise.
- Header: document ID/classification plus `STYLEREF "Heading 1"`; footer:
  classification plus `PAGE` / `NUMPAGES` (or `SECTIONPAGES` for front matter).
- Use `different first page` for the cover; use `different odd/even` only when
  the document is printed double-sided.
- Header/footer distance 12 mm; header rule 0.5 pt; header font 8–9 pt.

### 3.5 Appendices

- Start after references, each on a new page.
- Number headings `A`, `A.1`, `A.1.1`; figures/tables `Figure A.1`, `Table A.1`.
- A appendix is self-contained: title, data, source, method, limitations.
- Include appendices in the TOC (they are Heading 1) but not in the main
  narrative's figure numbering.

## 4. Typography

No ISO standard mandates Calibri or Times New Roman. What the standards and
accessibility guidance do require is legibility and consistency:

- Body 10–12 pt (Vietnamese diacritics need a font with full glyph coverage);
  line spacing 1.15–1.5; 60–90 characters per line.
- One heading family plus one body family is enough. More families usually
  signal an assembled document, not a designed one.
- H1 1.5–2× body; each level steps down by 2–4 pt; 3–6 distinct sizes per
  document, not 15.
- Left-aligned body is the safest default; justified text needs hyphenation and
  consistent word spacing, especially in Vietnamese.
- Captions 8–10 pt; tables 8–10 pt; footnotes 8–9 pt; headers/footers 8–9 pt.
- Contrast: 4.5:1 for body text; 3:1 for large text (≥18 pt, or ≥14 pt bold) and
  graphical objects (WCAG 2.2 SC 1.4.3 / 1.4.11).
- Font embedding: embed in PDF; in DOCX use "Embed fonts in the file" only if
  the font licence permits it. Check `fsType` before redistributing.
- Vietnamese: use a Unicode font with full Vietnamese coverage (Calibri, Arial,
  Times New Roman, Aptos, Noto Sans/Serif). Test `ế ộ ữ ợ ẩ` in the actual PDF,
  not only in Word.

## 5. Images

- **Alignment:** centre inline images on the text column. Use floating anchors
  only when text wrap is part of the design; floating images drift when the
  text changes.
- **Size:** width ≤ text column (≈155 mm on A4 with 30/25 mm margins); preserve
  aspect ratio; leave room for the caption on the same page.
- **Resolution:** effective PPI = pixels ÷ (display width in inches). Aim for
  ≥150 PPI on screen, ≥300 PPI for photo print, ≥600 PPI for line art. Never
  upscale a 72 PPI screenshot to full width and call it print-ready.
- **Formats:** PNG for screenshots/line art, JPEG for photos, SVG/EMF for
  vectors, TIFF for print. Avoid GIF for static figures.
- **Alt text:** describe the information, not "image". Decorative images should
  be marked decorative. In OOXML the text is `wp:docPr@descr` (and `@title`).
- **Captions:** below the figure, `Figure N — caption`, source note below in
  8 pt italic. Keep the image paragraph with the caption (`keepNext`).
- **Crop/scale:** crop with `a:srcRect`; do not squash by setting width and
  height independently. Check `wp:extent` against the image's aspect ratio.

## 6. Tables

- **Caption above**, table below; source note below the table.
- **Fixed layout** (`w:tblLayout type="fixed"`), explicit `w:tblGrid` widths
  summing to the text column. AutoFit is not a layout strategy.
- **Header row** repeats (`w:tblHeader`) and does not split (`w:cantSplit`).
- **Borders:** booktabs style — top/bottom rules and a header rule; no vertical
  grid unless the data is a matrix that needs it.
- **Alignment:** text left; numbers right with a consistent number format;
  short codes/percentages centered; units in the header, not repeated in every
  cell.
- **Padding:** 1.5–3 mm; row height at least 6 mm; font 8–10 pt.
- **Accessibility:** repeat header row, `w:tblCaption` / `w:tblDescription`,
  avoid merged cells for data tables, do not use tables for page layout unless
  the reading order is simple.
- **Wide tables:** switch the section to landscape or split the table; do not
  shrink the font below 8 pt to make it fit.

## 7. References and citations

- Choose one style: ISO 690:2021, APA 7, IEEE, Chicago, Harvard or Vancouver.
  The contract/journal/institution decides.
- Use a hanging indent (≈8 mm), 9–10.5 pt, consistent punctuation.
- Dates in ISO 8601; DOI/URL with access date; no bare "available online".
- In-text citation → reference entry must be traversable. Word's native
  Citations & Bibliography uses a `b:Sources` customXml part and `CITATION` /
  `BIBLIOGRAPHY` fields; the T039 generator uses bookmark-linked `REF` fields
  as a portable alternative. If the customer requires Word's source manager,
  use WordCraft `references.citation` / `references.bibliography` or Word's
  References tab, and keep the source list in the document.

## 8. Accessibility and PDF export

- Set the document title, language and author in core properties.
- Use real headings, table header rows, alt text, and a logical reading order.
- Do not put body copy in floating text boxes; screen readers and PDF tags may
  read them out of order.
- Export **tagged PDF**; enable "Document structure tags for accessibility" and
  "Create bookmarks using headings".
- Validate PDF/UA with a tag-tree/reading-order checker, not only a visual look.
- For PDF/A, embed fonts and validate with veraPDF. A PDF that looks correct can
  still fail PDF/A because of transparency, colour or metadata.
- Keep the DOCX as the editable source; the PDF is a derivative.

## 9. Print

- A4, 100% scale, no "fit to page" unless the client accepts it.
- Use the printer's ICC profile; convert images to the target CMYK; check ink
  limits; export PDF/X with bleed and trim marks.
- Proof under ISO 3664 viewing conditions; do not judge colour on an uncalibrated
  office monitor.
- Keep body text at least 9 pt for print; 10–11 pt is safer.

## 10. Sources

- ISO catalogue pages: [ISO 7144](https://www.iso.org/standard/13736.html),
  [ISO 5966](https://www.iso.org/standard/12160.html) (withdrawn),
  [ISO 2145](https://www.iso.org/standard/6937.html),
  [ISO 7200](https://www.iso.org/standard/35446.html),
  [ISO 690](https://www.iso.org/standard/72642.html).
- [ECMA-376 / ISO/IEC 29500](https://ecma-international.org/publications-and-standards/standards/ecma-376/).
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/).
- [PDF/UA](https://pdfa.org/resource/iso-14289-pdfua/) and
  [PDF/A](https://pdfa.org/resource/iso-19005/).
- [BIPM SI Brochure](https://www.bipm.org/en/publications/si-brochure).
- [ISO 8601 date/time](https://www.iso.org/iso-8601-date-and-time-format.html).
- Microsoft Word field/TOC/cross-reference help: see
  `references/word-properties.md` for the exact UI paths and commands.

Where a URL above is a catalogue/search page rather than the standard text, the
standard is paywalled; the citation identifies the edition, not a free copy.
