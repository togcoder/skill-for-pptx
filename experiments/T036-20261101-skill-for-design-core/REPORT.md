# T036 — Universal ArtCraft Hub, Multi-Agent Protocols & Intent Schemas

## Frozen input

- **Request.** On 2026-11-01, the project owner directed laying the foundational bricks for all other parts of ArtCraft, consulting Argon on setting up the multi-agent system, establishing cross-delegation and peer critique protocols, enforcing strict aesthetic standards from reputable design canons, avoiding obsolete workarounds by discovering existing native tool features, and teaching AI how to understand human users (cognitive load, audience empathy).
- **Consultation.** Consulted Argon (`gemini-argon`) with deep reasoning on multi-agent architecture. Argon delivered a 4-tier blueprint identifying 4 architectural pitfalls: unbounded mesh chat (solved by Contract-Driven DAG + max 2 iterations), LLM python bias (solved by 3-tier capability escalation gate), blind text evaluation (solved by render-before-review + dual-layer critique), and jumping to tool selection without empathy (solved by 5-dimensional intent brief).
- **Base.** Branch `work/T036-skill-for-design-core` @ `6576782` (branched from T035).
- **Environment.** Windows 10/11 x64, Python 3.12, 13 ArtCraft tools in `D:\artcraft`.

## What was built

### 1. Universal ArtCraft Discovery & Hub
- `scripts/sync_artcraft_capabilities.py`: Automatically inspects all 13 tools in `D:\artcraft` (CADCraft, DeckCraft, DesignCraft, FigCraft, FilmCraft, GridCraft, LightCraft, PdfCraft, PhotoCraft, SolidCraft, SoundCraft, VectorCraft, WordCraft). Generates:
  - `registry/artcraft_capabilities.json`: Machine-readable capability manifest (domain, CLI path, size, subcommands, MCP server availability, version hash `21eaaf51d6891acf`).
  - `registry/capability_gaps_backlog.md`: Registry for missing capabilities when fallbacks are needed.
- `scripts/artcraft_hub.py`: High-level Python API (`list_tools`, `get_tool`, `run_tool`, `is_tool_available`) and CLI (`list`, `info`, `run`).

### 2. Multi-Agent Governance Schemas
- `schemas/intent_brief.schema.json`: Enforces the 5 dimensions of human understanding:
  1. *Audience Persona:* C-Level / Technical / General / Student / Commercial.
  2. *Cognitive Budget:* Max visual groups ($\le 5$), max words, eye tracking pattern (Z/F pattern), target comprehension seconds ($\le 3$s).
  3. *Viewing Context:* Projector / Desktop / Mobile / Print, safe font threshold, lighting.
  4. *Canonical System:* Swiss Grid, Dieter Rams, Edward Tufte, IBM Carbon, Material 3.
  5. *Craft Routing:* Primary craft and supporting crafts.
- `schemas/handoff_contract.schema.json`: Formal peer-to-peer contract for cross-delegation between specialist agents, enforcing `max_iterations = 2` to eliminate infinite loops.
- `schemas/critique_report.schema.json`: Dual-layer 100-point critique report schema with auto-fail triggers and structured fix instructions.

### 3. Foundation Protocols (`protocols/`)
- `protocols/00_intent_empathy_decoder.md`: Decoding non-literal human intent and cognitive load.
- `protocols/01_capability_first_gate.md`: The 3-tier escalation ladder (Native CLI/MCP -> Declarative Spec -> Custom script only with `CAPABILITY_GAP_PROOF`).
- `protocols/02_cross_delegation_dag.md`: DAG cross-delegation rules and anti-looping protocol.
- `protocols/03_redteam_critique_rubric.md`: The 100-point rubric (Cognitive Fit 25, Grid 25, Typography 20, Color 15, Craftsmanship 15) and auto-fail rules.

### 4. Validation Engine & Tests
- `scripts/validate_handoff.py`: Standalone schema validator.
- `tests/test_artcraft_hub.py`: 4 new unit tests covering capability sync, hub listing, and intent/contract schema validations.
- Test suite expanded from 292 to **296 tests, all passing (0 failures, 4 skipped)** in 8.64s.

## Next steps

1. Update `docs/CHANGELOG.md`, `HANDOFF.md`, and `research/tasks/INDEX.md` (freeing T037).
2. Wire `WordCraft` and `GridCraft` bridges using the newly established hub.
3. Integrate the 5-dimensional `IntentBrief` generator into `slide_forge.py` and `motion_director.py`.
