# Claim — T068 [pptx] Deck Director compiler & validator

- **Agent / model:** Antigravity (Gemini 2.5 Pro).
- **Branch:** `work/T068-antigravity-deck-director`, based on `main` (`d214399`).
- **Started (UTC):** 2026-11-04.
- **Scope:** `scripts/deck_director.py`, `lab/schemas/deck_direction.schema.json`, `skills/deck-director/SKILL.md`, `scripts/slide_forge.py` (plan seam), `tests/test_deck_director.py`, `experiments/T068-20261104-antigravity-deck-director/**`.
- **Domain card:** `domains/pptx/DOMAIN.md`.
- **Status:** in progress.
- **Trigger:** owner mandate on solving the weakest link in presentations: scripting (kịch bản) that bridges natural speech to complex slide motion, resolving the 4 failure modes identified by Argon (Coda trap, Karaoke redundancy, Unanchored monologue, Additive clutter / lifecycles: 0).
- **Reviewer:** Argon (Gemini 4 Argon, chat `0:c15eb82d58ea61ff`).
- **Acceptance criteria:**
  1. `deck_direction.schema.json` defines Two-Pass Choreography: Stage Inventory, $t=0$ base state with `t0_says`, and lifecycle transitions (`enter`, `dim`, `highlight`, `exit`, `zoom`).
  2. `deck_director.py check` enforces the 5 hard narrative laws: `NAR-CODA-TRAP`, `NAR-KARAOKE`, `NAR-UNANCHORED`, `NAR-COLLISION`, `DEN-ACTIVE-VIEW` ($\le 45$ active words).
  3. `deck_director.py compile` maps direction to `deck.json` and `director.json`.
  4. `slide_forge.py build` supports `--plan` seam.
  5. Built deck demonstrates `object lifecycles > 0`, non-empty $t=0$ base state, and passes 100% test suite.
