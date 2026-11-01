# Domain: cross (orchestration across applications)

## Scope
Things every domain may use:
- intent briefs, from a short request to audience and goals;
- delegation between specialist agents (handoff contracts);
- the registry of available native tools;
- red-team critique protocols.

## Thesis
A shared layer only helps when it is proven in several domains. Until then it
must not shape how a single domain thinks. This is the monoculture risk.

## Code and data
| Item | Status |
|---|---|
| `lab/protocols/00–03` (intent decoder, capability-first gate, delegation DAG, red-team rubric) | T036; unreviewed; Vietnamese |
| `lab/schemas/` (intent_brief, handoff_contract, critique_report) | T036 |
| `lab/registry/artcraft_capabilities.json` | T036; depends on the owner's local ArtCraft install (`D:\artcraft`) |
| `scripts/intent_decoder.py`, `artcraft_hub.py`, `sync_artcraft_capabilities.py`, `validate_handoff.py` | Experimental (T036–T037); unreviewed |

## Rules
- A universal layer becomes canonical only after accepted reviews in **two
  domains** (`lab/PROTOCOL.md`, anti-monoculture).
- Domain cards may reject a cross-layer rule for their domain, with reasons.

## State (2026-11-01)
None of the above has been reviewed. First review targets:
- protocol 01 ("capability-first") and its dependency on one local tool suite;
- whether the schemas fit docx and xlsx, not only pptx.
