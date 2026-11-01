# Design domains in this lab



Each domain is an application or a family of applications with its own design

language, technical model, evidence ladder and tests.



A domain has a folder `domains/<name>/` with a `DOMAIN.md` card. The card is

the contract for agents working in that domain.



| Domain | Target application(s) | Card | Maturity | Canonical entry points |

|---|---|---|---|---|

| `pptx` | PowerPoint (OOXML presentation) | [pptx/DOMAIN.md](pptx/DOMAIN.md) | Mature: T001â€“T038, T043, 350+ tests | `motion_director.py`, `morph_studio.py`, `slide_forge.py`, `theme_engine.py`, `design_critic.py` |

| `docx` | Word (OOXML document) | [docx/DOMAIN.md](docx/DOMAIN.md) | T039/T045/T047 on main; T052 standard profiles + HUST/VNU scientific report (review requested) | `word_field_kit.py`, `document_forge.py`, `word_math.py`, `document_audit.py`, `docx_profiles.py` |

| `xlsx` | Excel (OOXML workbook, charts) | [xlsx/DOMAIN.md](xlsx/DOMAIN.md) | T041/T046/T048 on main; T050 UserForm + composed dashboard (review requested) | `chart_forge.py`, `chart_patch.py`, `chart_audit.py`, `sheet_forge.py`, `vba_forge.py`, `dashboard_forge.py`, `userform_forge.py`, `gridcraft_bridge.py` |

| `svg` | Vector graphics (SVG, print, icon grids) | [svg/DOMAIN.md](svg/DOMAIN.md) | Foundational: T042 canon tokens, stroke scaling, BĂ©zier math | `multi_domain_canons.py`, `vectorcraft_bridge.py` |

| `video` | Video editing, motion pacing & broadcast audio (FilmCraft & SoundCraft) | [video/DOMAIN.md](video/DOMAIN.md) | Foundational: T042 safe zones, ASL, J/L-cuts, EBU R128 | `multi_domain_canons.py`, `filmcraft_bridge.py`, `soundcraft_bridge.py` |

| `3d` | 3D solid CAD modeling & PBR rendering (SolidCraft & LightCraft) | [3d/DOMAIN.md](3d/DOMAIN.md) | Foundational: T042 no-sharp-edge, 3-point lighting, PBR albedo | `multi_domain_canons.py`, `solidcraft_bridge.py` |

| `cad` | Technical engineering drawings (CADCraft - ISO 128 / 5457 / 7200) | [cad/DOMAIN.md](cad/DOMAIN.md) | Foundational: T042 ISO sheet geometry, line weights, dimensioning | `multi_domain_canons.py`, `cadcraft_bridge.py` |

| `cross` | Orchestration across applications: intent briefs, delegation, capability registry, pre-processing pipelines | [cross/DOMAIN.md](cross/DOMAIN.md) | Protocols 00â€“04 (T036â€“T037, T044) | `intent_decoder.py`, `artcraft_hub.py`, `cross_pipeline.py`, `validate_handoff.py`, `lab/protocols/` |



**Physical layout.** Code still lives in `scripts/` and tests in `tests/`.

Each module's domain owner is recorded in the domain card's "Code and data"

table. T042 plans the move into domain packages.

