# Domains

Each design domain is its own research line, with its own thesis, canon,
design-system data and evidence ladder. Before working, read the domain card.
Before adding a domain, copy `_template/DOMAIN.md` and add a row here (owner
approval needed).

| Domain | Target application(s) | Card | Maturity | Canonical entry points |
|---|---|---|---|---|
| `pptx` | PowerPoint (OOXML presentation) | [pptx/DOMAIN.md](pptx/DOMAIN.md) | Mature: T001–T038, 300+ tests | `motion_director.py`, `morph_studio.py`, `slide_forge.py`, `design_critic.py` |
| `docx` | Word (OOXML document) | [docx/DOMAIN.md](docx/DOMAIN.md) | Early: one unreviewed bridge (T037); T039 claimed | `wordcraft_bridge.py` (experimental) |
| `xlsx` | Excel (OOXML workbook, charts) | [xlsx/DOMAIN.md](xlsx/DOMAIN.md) | Early: one unreviewed bridge (T037); T039 claimed | `gridcraft_bridge.py` (experimental) |
| `svg` | Vector graphics (SVG, print, icon grids) | [svg/DOMAIN.md](svg/DOMAIN.md) | Foundational: T042 canon tokens, stroke scaling, Bézier math | `multi_domain_canons.py`, `vectorcraft_bridge.py` |
| `video` | Video editing, motion pacing & broadcast audio (FilmCraft & SoundCraft) | [video/DOMAIN.md](video/DOMAIN.md) | Foundational: T042 safe zones, ASL, J/L-cuts, EBU R128 | `multi_domain_canons.py`, `filmcraft_bridge.py`, `soundcraft_bridge.py` |
| `3d` | 3D solid CAD modeling & PBR rendering (SolidCraft & LightCraft) | [3d/DOMAIN.md](3d/DOMAIN.md) | Foundational: T042 no-sharp-edge, 3-point lighting, PBR albedo | `multi_domain_canons.py`, `solidcraft_bridge.py` |
| `cad` | Technical engineering drawings (CADCraft - ISO 128 / 5457 / 7200) | [cad/DOMAIN.md](cad/DOMAIN.md) | Foundational: T042 ISO sheet geometry, line weights, dimensioning | `multi_domain_canons.py`, `cadcraft_bridge.py` |
| `cross` | Orchestration across applications: intent briefs, delegation, capability registry | [cross/DOMAIN.md](cross/DOMAIN.md) | Early: protocols and hub (T036–T037), unreviewed | `intent_decoder.py`, `artcraft_hub.py`, `validate_handoff.py`, `lab/protocols/` |

**Physical layout.** Code still lives in `scripts/` and tests in `tests/`.
Each module belongs to exactly one domain (see the cards). Moving the code
into per-domain packages is task T041, which needs a review of import paths,
skills and frozen experiments. New domain data goes into `domains/<d>/data/`;
new example specs into `examples/<d>/`.
