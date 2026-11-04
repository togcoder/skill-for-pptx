# T068 [pptx] — Deck Director: Two-Pass Screenplay Compiler and Lifecycle State Machine

- **Agent / model:** Antigravity (Gemini 2.5 Pro).
- **Date:** 2026-11-04. **Base:** `main` @ `d214399`. **Branch:** `work/T068-antigravity-deck-director`.
- **Reviewer:** Argon (Gemini 4 Argon, chat `0:c15eb82d58ea61ff`).
- **Status:** complete; tested and verified.

## Frame

**Question.** Why did a technically sound deck with 144 native effects read as tasteless and out of sync with natural speech, and how can an AI agent direct a complex motion deck from scratch without falling into the 5 classic failure modes (Coda trap, Karaoke redundancy, Unanchored monologue, Motion collision, Additive clutter)?

**Hypothesis.** The failure is rooted in an inverted cognition pipeline: writing conversational prose (script) before establishing the spatial-temporal state machine. Directing must follow a **Two-Pass Choreography Architecture**:
1. *Pass 1 (Architecture & State Machine):* Lock Stage Inventory, $t=0$ resting base state, and lifecycle transitions (`enter`, `dim`, `highlight`, `exit`, `zoom`).
2. *Pass 2 (Natural Voice Weave):* Weave spoken dialogue using **Split-Sentence Bridging** (cues placed at causality pivots) and **Implicit Deictic Anchoring**.

**Falsifiers.**
- The validator fails to detect empty clicks or unanchored monologue;
- The compiler generates unbuildable Forge or Motion Director plans;
- Rebuilding a directed presentation leaves $t=0$ empty or fails to produce object lifecycles;
- Vocabulary overlap between speech and on-screen text exceeds 45%;
- Test suite regresses.

## Frozen input

- **Environment:** Windows 11, Python 3.13.5, python-pptx, DeckCraft CLI 0.15.0 (`D:\artcraft\DeckCraft\deckcraft-cli.exe`), lxml.
- **Specification:** `lab/schemas/deck_direction.schema.json` v0.2.
- **Inputs:** `experiments/T068-20261104-antigravity-deck-director/inputs/direction.json`.

## Method

```powershell
# 1. Validate direction against 5 hard narrative laws
python scripts/deck_director.py check experiments/T068-20261104-antigravity-deck-director/inputs/direction.json

# 2. Compile to Forge spec and Motion Director v0.7 plan
python scripts/deck_director.py compile experiments/T068-20261104-antigravity-deck-director/inputs/direction.json `
  -o experiments/T068-20261104-antigravity-deck-director/artifacts/deck.json `
  --director experiments/T068-20261104-antigravity-deck-director/artifacts/director.json

# 3. Build native presentation with Motion Director seam
$env:PYTHONPATH="scripts"
python scripts/slide_forge.py build `
  experiments/T068-20261104-antigravity-deck-director/artifacts/deck.json `
  -o experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx `
  --plan experiments/T068-20261104-antigravity-deck-director/artifacts/director.json

# 4. Extract narrative ledger
python scripts/deck_director.py ledger `
  experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx `
  --direction experiments/T068-20261104-antigravity-deck-director/inputs/direction.json

# 5. Render Full HD previews with DeckCraft 0.15.0
python scripts/deckcraft_bridge.py render `
  experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx `
  -o experiments/T068-20261104-antigravity-deck-director/preview/
```

## Evidence

| Claim | Measurement | Rung |
|---|---|---|
| Schema & Validator | `deck_direction.schema.json` + `deck_director.py check` catches all 5 narrative failure modes | 1 |
| Unit Tests | `tests/test_deck_director.py`: 7/7 tests pass in 0.11s | 1 |
| End-to-end Build | `slide_forge.py build --plan` outputs valid presentation with QA `ok: true`, 0 errors | 4 |
| Design Critic | Overall score **4.99/5.0** (Design 4.94, Motion 5.0, Rhythm 5.0, Coherence 5.0) | 3 |
| Object Lifecycles | Ledger reports **6 lifecycles** ($\ge 2$ effects on same shape: enter $\rightarrow$ dim), eliminating T066's `lifecycles: 0` defect | 4 |
| Empty Base State | **0 empty base states** at $t=0$; every slide opens with visual anchor and `t0_says` speech | 4 |
| Visual Previews | DeckCraft 0.15.0 exports 3 Full HD (1920x1080) slide renders | 2 |

## Positive results

- **Two-Pass Choreography solves the "karaoke" and "coda" traps:** Screenplay speech is written directly into `t0_says`, `lead_in`, and `post_click_says`, locking the audio-visual sync without robotic pauses.
- **`slide_forge.py` integration is seamless:** Adding the `--plan` seam enables any custom director plan to override heuristic drafting while keeping Forge's geometry compiler intact.
- **Artifacts:**
  - `scripts/deck_director.py` (~350 lines, validator, compiler, ledger).
  - `lab/schemas/deck_direction.schema.json` (canonical JSON schema).
  - `skills/deck-director/SKILL.md` (upgraded v0.2 documentation).
  - `tests/test_deck_director.py` (7 tests).
  - `experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx`.
  - `experiments/T068-20261104-antigravity-deck-director/preview/slide-01.png` ... `slide-03.png`.

## Negative results and limits

1. **Token mapping:** In v0.2, high-level actor names are mapped to Forge-generated tokens via layout heuristics. Complex custom layouts still benefit from reading back `inspect` tokens for 100% precision.
2. **Interactive Zoom (`drill`):** Non-linear zoom transitions compile via DeckCraft `insert.zoom`, which is verified natively in DeckCraft and PowerPoint, but LibreOffice still falls back to plain hyperlinks.
