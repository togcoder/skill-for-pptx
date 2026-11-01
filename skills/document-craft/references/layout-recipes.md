# Document layout recipes

These are recipes, not laws. A customer template or an institutional regulation
overrides them. Tokens come from `domains/docx/data/document_system.json`; change the
token and its source, not a number buried in a generator.

## 1. A4 page grid

```
A4                 210 × 297 mm
margins            25 top / 25 bottom / 30 left / 25 right
text column        155 mm
text height        247 mm
header distance    12 mm
footer distance    12 mm
body               11 pt, 1.15 line spacing, 6 pt after
line length        60–90 characters
```

For duplex printing, add a 5–10 mm gutter and mirror the margins. For a
landscape table, use a separate landscape section; do not rotate the whole
document.

## 2. Type scale

| Role | Size | Weight | Spacing |
|---|---|---|---|
| Title (cover) | 26–30 pt | Bold | 24 pt before / 6 after |
| Subtitle | 14–16 pt | Regular, muted | 12 pt after |
| H1 | 18–20 pt | Bold | 18 before / 8 after |
| H2 | 14–16 pt | Bold | 14 / 6 |
| H3 | 12–13 pt | Bold | 10 / 4 |
| H4 | 10.5–12 pt | Bold italic | 8 / 4 |
| Body | 10–12 pt | Regular | 0 / 4–8 |
| Caption | 8–10 pt | Regular, muted | 4 / 8 |
| Table text | 8–10 pt | Regular | 0 / 0 |
| Header/footer | 8–9 pt | Regular, muted | 0 / 0 |
| Reference | 9–10.5 pt | Regular | 0 / 4, hanging 8 mm |

Use at most 3–6 distinct sizes in the body. A cover is allowed a larger display
size; it is not a body heading.

## 3. Cover

1. Logo top-right, 25–32 mm wide, alt text set.
2. 2–3 empty paragraphs, then the title (26–30 pt bold).
3. Subtitle (14–16 pt muted), then one 1 pt rule.
4. A right-aligned metadata block: document ID, version, date (ISO 8601),
   classification.
5. Organisation and author at the bottom.
6. Section break → front matter, no header/footer on the cover.

Do not use a text box for the title; a cover paragraph keeps the reading order
and the accessibility tree.

## 4. Front matter and TOC

Order: cover → TOC → list of figures → list of tables → abstract → body.

- “Mục lục/Contents” uses the `TOC Heading` style, based on Normal with outline
  level 9, so it is **not** included in its own TOC.
- The TOC field: `TOC \o "1-3" \h \z \u`.
- The list of figures/tables: either `TOC \h \z \c "Figure"` or a field list
  (`REF` + `PAGEREF` per entry). The T039 generator uses the field list because
  Word's caption cache repeated the first `SEQ` number in testing.
- Front matter pagination: `pgNumType fmt="lowerRoman" start="1"`.
- Body: section break, `pgNumType fmt="decimal" start="1"`.
- Refresh the fields before delivery. If the TOC still shows a placeholder,
  it is not finished.

## 5. Figure recipe

```text
[centred inline picture, width ≤ 155 mm]
Hình 1 — Caption text
Nguồn: source, year.
```

- Choose the width from the text column and the image's aspect ratio; never set
  width and height independently.
- If the computed height leaves no room for the caption, reduce the width.
- `keep_with_next` on the picture paragraph; `keep_together` on the caption.
- Alt text describes the information (“Sơ đồ kiến trúc gồm 4 lớp…”), not “image”.
- Effective PPI: `px_width / (width_mm / 25.4)`. Warn below 150 (screen), 300
  (print), 600 (line art).
- Source note 8 pt italic, centred; cite the data owner and date.

## 6. Table recipe

```text
Bảng 1 — Caption text
┌──────────────────────────────────────────────┐
│ Header 1        Header 2        Header 3     │  header fill F2F2F2, bold
├──────────────────────────────────────────────┤
│ Text            number          12,5         │  text left, number right
│ Text            number          13,1         │  zebra optional
└──────────────────────────────────────────────┘
Nguồn: source, year.
```

- Caption above; table below; source note below.
- Fixed layout, `tblGrid` widths sum to ≤155 mm; header row repeats.
- Cell margins 2 mm; row height at least 6 mm; `cantSplit` on rows.
- Borders: top/bottom 1 pt, header rule 1 pt, inside horizontal 0.5 pt, no
  vertical lines. Use a grid only for a true matrix.
- Numeric columns right-aligned; units in the header; one decimal convention.
- `tblCaption` and `tblDescription` set for accessibility.
- Wide table: landscape section, not 7 pt font.

## 7. Header and footer

```text
Header:  [Document ID]                         [Chapter title]
         ─────────────────────────────────────────────────────
Footer:  [Classification]                      Trang 3 / 12
```

- `STYLEREF "Heading 1" \* MERGEFORMAT` for the chapter; `PAGE` / `NUMPAGES`
  for the page.
- Cover: no header/footer. Front matter: document ID only, roman page.
- Body: chapter + page. Even pages can mirror the header for duplex.
- Header rule 0.5 pt, colour `BFBFBF`; 8–9 pt text.
- Never put a page number in a text box; it will not update.

## 8. Appendix recipe

1. Page break (not a new document).
2. Heading 1 with an appendix list: `Phụ lục A`, `Phụ lục A.1`, …
3. Title: “Dữ liệu chi tiết theo đơn vị”.
4. Captions: `Bảng A.1`, `Hình A.1`; reset the sequence at the start of each
   appendix.
5. Include the appendix heading in the TOC; exclude it from the body numbering.
6. End with the source/method note and limitations.

The T039 implementation uses an explicit `A.` prefix plus `SEQ … \r 1` per
appendix. Word's `SEQ … \s 1` did not pick up a directly-numbered appendix
heading in the test; if you use `\s 1`, verify the result in Word.

## 9. References

- One style: ISO 690:2021, APA 7, IEEE, Chicago, Harvard or Vancouver.
- Hanging indent 8 mm; 9–10.5 pt; 4 pt after; alphabetical or numbered.
- ISO 8601 dates; DOI/URL with access date; no bare links.
- In-text citation → entry link; if using Word's native citation manager,
  keep the `b:Sources` part and update the bibliography field.
- The T039 generator uses bookmark-linked `REF` citations; it does not create
  Word's native `b:Sources` bibliography. Say so if the client requires the
  Word source manager.

## 10. Field XML that makes the links real

TOC:

```xml
<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>
<w:r><w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r>
<w:r><w:t>Mục lục sẽ được cập nhật.</w:t></w:r>
<w:r><w:fldChar w:fldCharType="end"/></w:r>
```

Caption:

```xml
<w:p>
  <w:pPr><w:pStyle w:val="Caption"/><w:keepNext/></w:pPr>
  <w:bookmarkStart w:id="42" w:name="fig-1"/>
  <w:r><w:t>Hình </w:t></w:r>
  <w:bookmarkStart w:id="43" w:name="fig-1-num"/>
  <w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>
  <w:r><w:instrText xml:space="preserve"> SEQ Figure \* ARABIC </w:instrText></w:r>
  <w:r><w:fldChar w:fldCharType="separate"/></w:r>
  <w:r><w:t>1</w:t></w:r>
  <w:r><w:fldChar w:fldCharType="end"/></w:r>
  <w:bookmarkEnd w:id="43"/>
  <w:bookmarkEnd w:id="42"/>
  <w:r><w:t> — Caption text</w:t></w:r>
</w:p>
```

Cross-reference:

```xml
<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>
<w:r><w:instrText xml:space="preserve"> REF fig-1 \h </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r>
<w:r><w:t>Hình 1</w:t></w:r>
<w:r><w:fldChar w:fldCharType="end"/></w:r>
```

Settings (ask Word to refresh on open; Word removes it after a successful
refresh):

```xml
<w:updateFields w:val="true"/>
```

## 11. Pre-delivery checklist

- [ ] Heading 1–9 only; no skipped level; numbering linked to styles.
- [ ] TOC field, hyperlinks, page numbers; results refreshed.
- [ ] List of figures/tables entries resolve and show the right number/page.
- [ ] Every `REF`/`PAGEREF` target exists; no duplicate bookmark.
- [ ] Figures inline, centred, ≤ text width, alt text, effective DPI OK.
- [ ] Tables fixed grid, ≤ text width, header repeats, caption above, source
      note below, numbers right-aligned.
- [ ] Cover no header/footer; front matter roman; body arabic from 1.
- [ ] Header shows the current chapter; footer shows classification + page.
- [ ] Appendix A/A.1 numbering; captions A.1; TOC includes appendix.
- [ ] Language/title metadata set; no sensitive text in properties/comments.
- [ ] Rendered pages inspected; PDF tagged; PDF/A or PDF/UA validated if
      required.
- [ ] Report names the evidence rung; no claim of Word playback or PDF/UA
      without the exact check.
