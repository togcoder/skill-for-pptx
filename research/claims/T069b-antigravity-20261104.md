# Claim — T069 [pptx] Narrative Critic & Two-Pass Screenplay Scaffold

- **Agent / model:** Antigravity (Gemini 2.5 Pro).
- **Branch:** `work/T069-antigravity-narrative-critic`, based on `main` (`3015182`).
- **Started (UTC):** 2026-11-04.
- **Scope:** `scripts/deck_director.py`, `scripts/design_critic.py`, `skills/deck-director/SKILL.md`, `tests/test_deck_director.py`, `experiments/T069-20261104-antigravity-narrative-critic/**`.
- **Domain card:** `domains/pptx/DOMAIN.md`.
- **Status:** in progress.
- **Trigger:** Argon architectural verdict: close the end-to-end screenplay loop by compiling speaker notes directly into `.pptx` (`ppt/notesSlides`), adding the 6th dimension (`narrative`: `NAR-BASE-STATE`, `DEN-ACTIVE-WORDS`, `NAR-LIFECYCLE`, `NAR-ALIGN`) to `design_critic.py`, implementing `scaffold` and `check --pass-1`, and supporting `exit_targets` in `deck_director.py`.
- **Reviewer:** Argon (Gemini 4 Argon, chat `1:6da99b570c8482b1`).
- **Acceptance criteria:**
  1. `deck_director.py compile` formats speaker notes (`[T=0]`, `[CLICK 1 - ...] lead [CLICK] (state) post`) into `deck.json`'s `notes` property, rendered by `slide_forge.py` into native PowerPoint notes slide XML.
  2. `deck_director.py compile` properly generates motion beats for `exit_targets` (`operation: "exit"`, `fade-out`, 400ms).
  3. `deck_director.py` provides `check --pass-1` (stage & lifecycle check before speech weave) and `scaffold` (template generator).
  4. `design_critic.py` grades the 6th dimension `"narrative"` from PPTX timing and notes slide XML (`NAR-BASE-STATE`, `DEN-ACTIVE-WORDS`, `NAR-LIFECYCLE`, `NAR-ALIGN`).
  5. 100% test pass rate in `tests/test_deck_director.py` including speaker notes, pass-1 validation, scaffold, and narrative critic scoring 5.0 on directed deck.
