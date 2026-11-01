# Word component and property matrix

How to change the same thing in four places: the Word UI, WordCraft's command
API, the OOXML part, and a portable Python path. Command IDs come from
`wordcraft-cli commands --json` (T037 bridge); OOXML clause numbers refer to
ISO/IEC 29500-1:2016 / ECMA-376 Part 1.

Legend:

- **UI** — the path a human uses in Word (ribbon / dialog).
- **WordCraft** — `wordcraft-cli run --file doc.docx --cmd 'id={json}'`.
- **OOXML** — the element/attribute the file actually stores.
- **Portable** — `python-docx` or raw `lxml`; the T039 helper is named where it
  exists.
- **Check** — what `document_audit.py` / `word_field_kit.audit_docx` looks for.

## Page and section

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| Page size | Layout → Size | `layout.pageSetup={"section":{"page":{"width":595.3,"height":841.9}}}` | `w:sectPr/w:pgSz@w,@h` (twips) | `section.page_width = Mm(210)` | A4/Letter note |
| Orientation | Layout → Orientation | `layout.orientation={"value":"landscape"}` | `w:pgSz@orient="landscape"` | swap width/height | page ratio |
| Margins | Layout → Margins | `layout.margins={"top":70.9,"bottom":70.9,"left":85,"right":70.9}` (pt) | `w:pgMar@top,@right,@bottom,@left` | `section.top_margin = Mm(25)` | ≥20 mm |
| Gutter / mirror | Layout → Margins → Gutter / Multiple pages | `layout.margins={"gutter":…,"mirror":true}` | `w:pgMar@w:gutter`, `w:mirrorMargins` | raw XML | margin check |
| Columns | Layout → Columns | `layout.columns={"count":2,"space":18}` | `w:cols@num,@space` | raw XML | column count |
| Section break | Layout → Breaks → Section Break | `layout.break={"kind":"nextPage"}` | `w:p/w:pPr/w:sectPr` + `w:type` | `doc.add_section(WD_SECTION.NEW_PAGE)` | section count |
| Page-number format | Insert → Page Number → Format | `layout.pageNumberFormat={"format":"lowerRoman","start":1}` | `w:pgNumType@fmt,@start` | `word_field_kit.set_page_numbering` | roman/arabic |
| Different first page | Header → Different First Page | `layout.differentFirstPage={}` | `w:titlePg` | `section.different_first_page_header_footer` | cover blank |
| Different odd/even | Header → Different Odd & Even | `layout.differentOddEven={}` | `w:evenAndOddHeaders` | `word_field_kit.set_even_odd_headers` | header refs |
| Header / footer | Insert → Header/Footer | `insert.header={"text":"…"}`, `insert.footer`, `insert.editHeader` | `w:headerReference`, `w:footerReference` | `section.header/footer` | refs count |
| Header/footer distance | Header → Position | `hf.position={"header":34,"footer":34}` (pt) | `w:pgMar@header,@footer` | `section.header_distance` | 12 mm |
| Page number field | Insert → Page Number | `insert.pageNumber={"position":"bottom","align":"right"}` | `PAGE` field | `add_page_number` | PAGE field |
| Page X of Y | Insert → Page Number → Format | `insert.pageNumber={"format":"x of y"}` | `PAGE` + `NUMPAGES` | `add_page_number` ×2 | NUMPAGES |

## Styles, fonts and language

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| Paragraph style | Home → Styles | `para.style={"style":"Heading 1"}` | `w:p/w:pPr/w:pStyle@val` | `paragraph.style` | outline level |
| Create/modify style | Styles pane → New/Modify | `styles.create`, `styles.modify` | `w:style`, `w:basedOn`, `w:next` | `doc.styles.add_style` | style exists |
| Font family | Home → Font | `format.font={"name":"Calibri","eastAsia":"…"}` | `w:rFonts@ascii,@hAnsi,@eastAsia,@cs` | `run.font.name`, raw `rFonts` | family count |
| Font size | Home → Font Size | `format.size={"size":11}` | `w:sz@w:val` (half-points) | `run.font.size = Pt(11)` | 3–6 sizes |
| Font colour | Home → Font Color | `format.color={"color":"1A1A1A"}` | `w:color@w:val` | `run.font.color.rgb` | contrast |
| Bold/italic | Home → B/I | `format.bold` / `format.italic` | `w:b`, `w:i` | `run.bold/italic` | — |
| Language | Review → Language | `format.font` eastAsia; or `styles.modify` | `w:lang@val,@eastAsia` | raw XML | `vi-VN`/`en-US` |
| Theme fonts | Design → Fonts | `design.themeFonts={"heading":"Calibri Light","body":"Calibri"}` | `theme1.xml/a:majorFont`, `a:minorFont` | raw XML | theme match |
| Styles from template | Developer → Document Template | `tools.updateStyles`, `styles.copyFrom` | `w:style` parts | `styles.organizer` | no duplicate |
| Style visibility | Styles pane → Options | `styles.setVisibility` | `w:qFormat`, `w:semiHidden`, `w:unhideWhenUsed` | raw XML | gallery |

## Headings and numbering

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| Heading level | Home → Styles | `para.style={"style":"Heading 2"}` | `w:pStyle` + style `w:outlineLvl` | `doc.add_heading(text, 2)` | no jumps |
| Heading number | Home → Multilevel List | `para.multilevel`, `para.numbering`, `para.listLevel` | `w:numPr`, `w:abstractNum`, `w:lvl`, `w:pStyle` | `word_field_kit.add_heading_numbering` | linked to style |
| Number format | Define New Number Format | `para.defineNumber`, `list.define` | `w:numFmt`, `w:lvlText`, `w:start` | helper / XML | ISO 2145 |
| Restart numbering | Home → Numbering → Set Value | `para.restartNumbering`, `para.setNumberingValue` | `w:lvlOverride/w:startOverride` | raw XML | appendix reset |
| Appendix numbering | Multilevel List | `list.define` with upperLetter | `w:numFmt="upperLetter"`, `w:lvlText="Phụ lục %1"` | `add_appendix_numbering` | A, A.1 |
| TOC entry level | References → TOC → Custom | `references.toc={"levels":3}` | `TOC \o "1-3"` | `add_toc` | levels ≥ max H |

## Fields, TOC, captions and references

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| TOC field | References → Table of Contents | `references.toc={"levels":3,"hyperlinks":true}` | `TOC \o "1-3" \h \z \u` | `add_toc` | TOC field |
| Update TOC | References → Update Table | `references.updateToc={}`, `references.updateFields={"all":true}` | field result refresh | `--update word/wordcraft` | not dirty |
| Update all fields | Ctrl+A, F9 | `references.updateFields={"all":true}` | `w:updateFields` | `set_update_fields` | update flag |
| Field code view | Alt+F9 | `view.fieldCodes={"value":true}` | `w:fldChar`, `w:instrText` | audit | balanced |
| Insert field | Insert → Quick Parts → Field | `insert.field={"instr":"…","result":"…"}` | `w:fldChar` begin/separate/end | `add_field` | instruction |
| Caption / SEQ | References → Insert Caption | `references.caption={"label":"Figure","text":"…","position":"below"}` | `SEQ Figure \* ARABIC` | `add_seq_caption` | SEQ + bookmark |
| Table of figures | References → Insert Table of Figures | `references.tableOfFigures={"label":"Figure"}` | `TOC \h \z \c "Figure"` | `add_toc_of` / REF list | entries |
| Cross-reference | References → Cross-reference | `insert.crossReference={"to":"figure","target":"…","show":"number"}` | `REF bookmark \h`, `PAGEREF` | `add_cross_reference` | target exists |
| Bookmark | Insert → Bookmark | `insert.bookmark={"name":"fig-1"}` | `w:bookmarkStart/@w:name,@w:id`, `w:bookmarkEnd` | `add_bookmark_to_paragraph` | unique/valid |
| Citation | References → Insert Citation | `references.citation={"tag":"…"}` | `CITATION` field + `b:Sources` | `add_citation` (REF) | style |
| Bibliography | References → Bibliography | `references.bibliography={"title":"…"}` | `BIBLIOGRAPHY` field + `customXml` | reference list | entries |
| Citation style | References → Style | `references.citationStyle={"style":"ISO 690 (author-date)"}` | `b:Sources` style | document text | one style |
| Footnote / endnote | References → Insert Footnote | `references.footnote={"text":"…"}`, `references.noteOptions` | `w:footnoteReference`, `footnotes.xml` | raw XML | numbering |
| Equation | Insert → Equation | `insert.equation={"latex":"…"}` | `m:oMath` / `m:oMathPara` | `word_math.omml_from_latex` | OMML present |
| Equation number | References → Insert Caption (Equation) | `equation.number={"value":true}` | `SEQ Equation` field | `add_field` | number field |
| Index | References → Insert Index | `references.index`, `references.updateIndex` | `INDEX` field | audit | entries |

## Tables

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| Insert table | Insert → Table | `insert.table={"rows":3,"cols":4,"style":"…"}` | `w:tbl`, `w:tblGrid`, `w:tr`, `w:tc` | `doc.add_table` | count |
| Table style | Table Design → Style | `table.style={"style":"…"}`, `table.look` | `w:tblStyle`, `w:tblLook` | `table.style` | style |
| Borders | Table Design → Borders | `table.borders={"kind":"outside","width":0.75}` | `w:tblBorders` | `_set_table_borders` | booktabs |
| Shading | Table Design → Shading | `table.shading={"color":"F2F2F2"}` | `w:shd@w:fill` | raw XML | contrast |
| Column width | Table Layout → Width | `table.columnWidth={"width":40}`, `table.autofit={"mode":"fixed"}` | `w:tblGrid/w:gridCol@w`, `w:tcW`, `w:tblLayout` | `column.width`, `cell.width` | sum ≤ text width |
| Row height | Table Layout → Height | `table.rowHeight={"height":18,"rule":"atLeast"}` | `w:trHeight@val,@hRule` | `row.height` | min |
| Repeat header | Table Layout → Repeat Header Rows | `table.repeatHeader={}` | `w:trPr/w:tblHeader` | `tblHeader` | first row |
| Don't split row | Row → Allow row to break | `table.properties={"allowBreak":false}` | `w:cantSplit` | `trPr` | rows |
| Cell alignment | Table Layout → Align | `table.cellAlign={"value":"center"}` | `w:tcPr/w:vAlign`, `w:jc` | `cell.vertical_alignment` | numeric right |
| Cell margins | Table Properties → Cell Margins | `table.cellMargins={"top":2,"left":2,"bottom":2,"right":2}` | `w:tblCellMar` | raw XML | 1.5–3 mm |
| Merge / split | Table Layout → Merge/Split | `table.merge`, `table.split` | `w:gridSpan`, `w:vMerge` | `cell.merge`; T042 `merges`/`header_rows` | accessibility |
| Image in cell | Insert → Pictures inside a cell | `insert.picture` at the caret | `w:drawing` in `w:tc` | `cell.paragraphs[0].add_run().add_picture` | alt text, row height |
| Table caption/alt | Table Properties → Alt Text | `table.altText={"text":"…","title":"…"}` | `w:tblCaption`, `w:tblDescription` | raw XML | present |
| Sort table | Table Layout → Sort | `table.sort={"column":1,"header":true}` | table data | manual | numeric order |

## Images and objects

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| Insert picture | Insert → Pictures | `insert.picture={"path":"…","width":400}` | `w:drawing`, `wp:inline`, `a:blip` | `run.add_picture` | count |
| Size / aspect | Picture Format → Size | `picture.size={"width":400,"lockAspect":true}` | `wp:extent@cx,@cy`, `a:xfrm` | `inline.width/height` | aspect |
| Crop | Picture Format → Crop | `picture.crop={"left":0.1,"top":0.1}` | `a:srcRect@l,@t,@r,@b` | raw XML | crop |
| Alt text | Picture Format → Alt Text | `picture.altText={"text":"…","decorative":false}` | `wp:docPr@descr,@title` | `docPr.set("descr", …)` | alt required |
| Wrap | Picture Format → Wrap Text | no dedicated command; use OOXML | `wp:anchor` + `wrapSquare`/`wrapTight`/`wrapTopAndBottom` | raw XML | inline default |
| Position | Picture Format → Position | no dedicated command; use OOXML | `wp:anchor/positionH/V` | raw XML | no drift |
| Border / style | Picture Format → Picture Styles | `picture.style={"style":"simpleFrame"}`, `picture.border` | `a:ln`, `p:style` | raw XML | contrast |
| Compress | Picture Format → Compress | `picture.compress={"maxPixels":…}` | image part | — | DPI |
| Logo on cover | Insert → Pictures | `insert.picture` | `wp:inline` | `add_picture` | alt text |
| Cover hero band | Insert → Pictures | `insert.picture` | `wp:inline` | `cover.hero_image` | alt text / width |
| Side-by-side media | Insert → Table (borderless) | `insert.table` + `insert.picture` | `w:tbl` + `w:drawing` in cell | `figure_text` | caption below |

## Review, protection and output

| Component | Word UI | WordCraft | OOXML | Portable / T039 | Check |
|---|---|---|---|---|---|
| Track changes | Review → Track Changes | `review.trackChanges={"value":true}` | `w:ins`, `w:del` | raw XML | markup |
| Comment | Review → New Comment | `review.newComment={"text":"…"}` | `comments.xml` | raw XML | comments |
| Protect document | File → Info → Protect | `file.protect={"mode":"readOnly"}`, `review.restrict` | `w:documentProtection` | raw XML | protection |
| Document properties | File → Info → Properties | `file.properties={"title":"…","author":"…"}` | `docProps/core.xml`, `app.xml` | `doc.core_properties` | title/author |
| Export PDF | File → Export → PDF | `wordcraft-cli convert in.docx out.pdf` | PDF | Word COM / LibreOffice | tagged |
| Export PDF/A | Acrobat/Word PDF/A | WordCraft `convert` + PDF/A option where available | PDF/A | Word COM `ExportAsFixedFormat` | veraPDF |
| Print | File → Print | `file.print` (if available) | print settings | OS | scale |

## The four implementation paths

1. **Word UI** — best for a human author; not reproducible.
2. **WordCraft commands** — best when the native engine is available; the
   command IDs above are stable and cover fields, styles, tables, images and
   review. `wordcraft-cli inspect` gives the structure back as JSON.
3. **OOXML** — the source of truth; use it when a property has no API
   (`w:tblCaption`, `w:updateFields`, `wp:anchor` wrap, `w:pgNumType`).
4. **python-docx + lxml** — portable path. `python-docx` is good for paragraphs,
   styles, sections, images and tables; it does **not** compute fields, TOC
   pages or layout. `word_field_kit.py` adds the field/bookmark/TOC/caption
   layer. A layout engine (Word, WordCraft, LibreOffice) is still required to
   refresh results.

### Rules that apply to every path

- Never type a TOC, caption number or page number as plain text.
- Never rename a bookmark without updating every `REF`/`PAGEREF`.
- Never set image width and height independently; always preserve aspect.
- Never let a table grid exceed `page width − left margin − right margin`.
- Never put page numbers in a text box; use the footer and `PAGE`.
- Never claim a field result is correct until a layout engine has refreshed it.
- Never claim PDF/UA or PDF/A from a visual check; validate the file.
