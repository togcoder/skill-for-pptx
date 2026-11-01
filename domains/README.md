# Domains

Each design domain is its own research line, with its own thesis, canon,
design-system data and evidence ladder. Before working, read the domain card.
Before adding a domain, copy `_template/DOMAIN.md` and add a row here (owner
approval needed).

| Domain | Target application(s) | Card | Maturity | Canonical entry points |
|---|---|---|---|---|
| `pptx` | PowerPoint (OOXML presentation) | [pptx/DOMAIN.md](pptx/DOMAIN.md) | Mature: T001–T038, 300+ tests | `motion_director.py`, `morph_studio.py`, `slide_forge.py`, `design_critic.py` |
| `docx` | Word (OOXML document) | [docx/DOMAIN.md](docx/DOMAIN.md) | Early: T039 DocumentCraft (experimental, review requested); T037 bridge | `word_field_kit.py`, `document_forge.py`, `document_audit.py` (experimental) |
| `xlsx` | Excel (OOXML workbook, charts) | [xlsx/DOMAIN.md](xlsx/DOMAIN.md) | Early: one unreviewed bridge (T037); T039 claimed | `gridcraft_bridge.py` (experimental) |
| `svg` | Vector graphics (SVG, print) | [svg/DOMAIN.md](svg/DOMAIN.md) | Early: one unreviewed bridge (T037) | `vectorcraft_bridge.py` (experimental) |
| `cross` | Orchestration across applications: intent briefs, delegation, capability registry | [cross/DOMAIN.md](cross/DOMAIN.md) | Early: protocols and hub (T036–T037), unreviewed | `intent_decoder.py`, `artcraft_hub.py`, `validate_handoff.py`, `lab/protocols/` |

**Physical layout.** Code still lives in `scripts/` and tests in `tests/`.
Each module belongs to exactly one domain (see the cards). Moving the code
into per-domain packages is task T041, which needs a review of import paths,
skills and frozen experiments. New domain data goes into `domains/<d>/data/`;
new example specs into `examples/<d>/`.
