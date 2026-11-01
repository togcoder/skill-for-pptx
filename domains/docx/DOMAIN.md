# Domain: docx (Word documents)

## Scope
Long-form documents: reports, contracts, papers. "Done well" means readable
typography, correct styles and numbering, and accessible structure.

## Thesis (to be written by the first docx task)
Documents are read, not presented. The canon is Word's own model:
- styles, not direct formatting;
- headings and the TOC;
- sections, page layout, fields;
- tables with header rows.

Do **not** import slide grids, motion or click rhythm.

## Native canon and sources (start here)
- ECMA-376 WordprocessingML.
- The Word object model.
- Built-in style sets and themes.
- Typographic measure (45–75 characters per line).
- Accessibility (heading order, alt text).

## Code
| Module | Status | Tests |
|---|---|---|
| `scripts/wordcraft_bridge.py` | Experimental (T037): bridge to the external ArtCraft WordCraft tool (Windows, `D:\artcraft`); unreviewed | `tests/test_craft_bridges.py` |

## Evidence ladder
| Rung | Tool |
|---|---|
| 1 | schema (WML XSD) |
| 3 | LibreOffice Writer render |
| 4–5 | Word COM open / PDF export |
| 6 | person edits and prints |

## State (2026-11-01)
- T039 (OpenCode) has claimed "DocumentCraft & SheetCraft", with no report yet.
- Nothing is reviewed. There is no docx design system yet.

## Open questions
- Should docx use its own design-system file (`domains/docx/data/`)? It
  should, by `lab/standards/MERGE.md`.
