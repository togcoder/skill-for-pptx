# Domain: cross (orchestration across applications)

## Scope
Things every domain may use:
- intent briefs, from a short request to audience and goals (`lab/protocols/00`);
- capability-first escalation ladder (`lab/protocols/01`);
- delegation between specialist agents via handoff contracts (`lab/protocols/02`);
- red-team critique protocols (`lab/protocols/03`);
- cross-asset pre-processing pipeline orchestration and local operational autonomy (`lab/protocols/04`);
- the registry of available native tools (`lab/registry/artcraft_capabilities.json`).

## Thesis
A shared layer only helps when it is proven in several domains. Until then it
must not shape how a single domain thinks. This is the monoculture risk.
However, compound deliverables require cross-asset pipelines: specialized tools
must pre-process assets (image editing/alpha masking, audio normalization,
chart synthesis) before compound assembly into target applications (pptx, docx, xlsx, video).

## Code and data
| Item | Status |
|---|---|
| `lab/protocols/00–04` (intent decoder, capability-first gate, delegation DAG, red-team rubric, cross-asset pipeline & local autonomy) | T036, T044; Vietnamese |
| `lab/schemas/` (intent_brief, handoff_contract, critique_report) | T036 |
| `lab/registry/artcraft_capabilities.json` | T036; depends on the owner's local ArtCraft install (`D:\artcraft`) |
| `scripts/intent_decoder.py`, `artcraft_hub.py`, `sync_artcraft_capabilities.py`, `validate_handoff.py` | Experimental (T036–T037); unreviewed |

## Rules
- A universal layer becomes canonical only after accepted reviews in **two
  domains** (`lab/PROTOCOL.md`, anti-monoculture).
- Domain cards may reject a cross-layer rule for their domain, with reasons.
- **Pre-process before embedding (`lab/protocols/04`):** Never embed raw, unprocessed assets. Images must be cropped/masked; audio must be normalized (-14 LUFS); data must be verified in spreadsheets before embedding.
- **Local autonomy & hygiene:** Full authority to download external assets and libraries locally; all transient scratch files must remain in `workspace/` and be cleaned up when done.

## State (2026-11-01)
- T044 added Protocol 04 (Cross-Asset Pipeline & Local Autonomy Charter) per official owner mandate.
- OpenCode is progressing on Word (`docx`) and Excel (`xlsx`); Antigravity is progressing on PowerPoint (`pptx`) and Cross-Domain (`cross`).
