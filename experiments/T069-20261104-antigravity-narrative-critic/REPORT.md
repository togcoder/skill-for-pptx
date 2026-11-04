# T069 [pptx] — Narrative Critic & Two-Pass Screenplay Scaffold

- **Agent / model:** Antigravity (Gemini 2.5 Pro).
- **Date:** 2026-11-04. **Base:** `main` @ `3015182`. **Branch:** `work/T069-antigravity-narrative-critic`.
- **Reviewer:** Argon (Gemini 4 Argon, chat `1:6da99b570c8482b1`).
- **Status:** completed. Review requested.

## Frame

**Question.** Can we close the end-to-end screenplay loop so that:
1. Spoken lines and choreography cues (`[T=0]`, `[CLICK]`) are automatically compiled into native PowerPoint Speaker Notes (`ppt/notesSlides/notesSlide*.xml`).
2. `scripts/design_critic.py` measures narrative technique directly on the native PPTX (6th dimension: `"narrative"`), catching blank $t=0$ states, active view word clutter, additive clutter (`lifecycles == 0`), and out-of-sync speaker notes.
3. AI agents have a structured 2-pass workflow (`scaffold` and `check --pass-1`) to write professional presentation screenplays without violating cognitive laws.

**Hypothesis.** By integrating the Narrative Critic into `design_critic.py` and compiling synchronized speaker notes into OOXML notes slides, the QA gate will automatically reward decks with rich object lifecycles and clean cognitive pacing while penalizing additive clutter.

## Method & Execution

1. **Upgraded `scripts/deck_director.py`:**
   - **Speaker Notes Compiler (`format_speaker_notes`):** Automatically weaves `t0_says` and `clicks[]` into tagged cues:
     `[T=0] <speech>`
     `[CLICK <n> - <c_id>] <lead_in> [CLICK] (<state>) <post_click_says>`
     and writes to `slide_dict["notes"]`, automatically picked up by `slide_forge.py`'s `notes_slide.notes_text_frame.text`.
   - **Exit Lifecycle (`exit_targets`):** Handled in `compile_direction` to generate `operation: "exit"`, `fade-out`, 400ms beats.
   - **Two-Pass Separation (`check_direction(data, pass_num=1|2)` & CLI `--pass-1`):** Allows AI agents to lock down the visual stage, objects, and lifecycles in Pass 1 before weaving spoken dialogue in Pass 2.
   - **Two-Pass Scaffold (`scaffold_direction` & CLI `scaffold`):** Generates compliant multi-slide screenplay templates.
   - **Semantic Target Mapper (`_map_target`):** Generalized shape token mapping across all slide forge layouts (`title`, `asymmetric`, `bullets`, `kpis`, `process`).

2. **Added 6th Dimension `"narrative"` to `scripts/design_critic.py`:**
   - `_slide_notes_text(pkg, slide_part)`: Inspects native `notesSlide` relationships and extracts speaker notes runs.
   - `NAR-BASE-STATE`: Fails if a slide with click groups opens blank at $t=0$ (`len(t0_objs) == 0`).
   - `DEN-ACTIVE-WORDS`: Simulates visible text state across click events (`entr`, `exit`, `emph` dimming with `pid=9`), ensuring active words $\le 45$.
   - `NAR-LIFECYCLE`: Flags slides with $\ge 2$ clicks and $>45$ words where all clicks are purely additive (`slide_lifecycles == 0`).
   - `NAR-ALIGN`: Ensures speaker notes contain `[T=0]` and `[CLICK]` tags matching slide click group count.
   - Added `"narrative"` to dimension score aggregation.

3. **Updated Skill Documentation (`skills/deck-director/SKILL.md`):**
   - Documented `scaffold`, `check --pass-1`, speaker notes auto-compilation, and the 4 narrative critic codes.

4. **Expanded Unit Test Suite (`tests/test_deck_director.py`):**
   - 12/12 unit tests passing (100%), including `test_pass1_check_ignores_speech`, `test_scaffold_direction`, `test_compile_exit_targets`, and `test_narrative_critic_on_directed_pptx`.

## Empirical Evidence & Contrast Matrix

| Metric / Dimension | T066 (Undirected Control) | T068 (Directed Deck) | T069 (Scaffolded Deck) | Target / Law |
|---|---|---|---|---|
| **Narrative Score** | **2.70 / 5.00** (FAIL) | **5.00 / 5.00** (PASS) | **5.00 / 5.00** (PASS) | $\ge 4.80$ |
| **Overall Critic Score** | **3.76 / 5.00** | **4.99 / 5.00** | **4.84 / 5.00** | $\ge 4.50$ |
| **Object Lifecycles** | **0** (Additive Clutter) | **2** | **4** | $\ge 1$ |
| **Empty Base States ($t=0$)** | **1** (Slide 1 opens blank) | **0** | **0** | **0** |
| **Active View Clutter** | **5 slides > 55 words** (up to 80w) | All active states $\le 45$ words | All active states $\le 45$ words | `DEN-ACTIVE-WORDS` |
| **Speaker Notes Sync** | **None** (`NAR-ALIGN: note`) | Synced `[T=0]` & `[CLICK]` | Synced `[T=0]` & `[CLICK]` | `NAR-ALIGN: good` |
| **Pass 1 Check** | N/A | PASSED | PASSED | `check --pass-1` |
| **Pass 2 Check** | N/A | PASSED | PASSED | `check` |

## Artifacts Produced

- `experiments/T069-20261104-antigravity-narrative-critic/inputs/direction.json`: 3-slide scaffolded screenplay.
- `experiments/T069-20261104-antigravity-narrative-critic/artifacts/deck.json`: Compiled deck with speaker notes.
- `experiments/T069-20261104-antigravity-narrative-critic/artifacts/director.json`: Canonical Director v0.7 plan with lifecycles.
- `experiments/T069-20261104-antigravity-narrative-critic/artifacts/T069_scaffold_directed.pptx`: Native PPTX (QA `ok: true`, Narrative Critic: 5.00).
- `experiments/T069-20261104-antigravity-narrative-critic/preview/slide-*.png`: 3 Full HD DeckCraft renders.

## Verification Checklist

- [x] `scripts/deck_director.py check` passes with and without `--pass-1`.
- [x] `scripts/deck_director.py scaffold` generates clean compliant direction.
- [x] `scripts/deck_director.py compile` weaves tagged speaker notes into `deck.json`.
- [x] `slide_forge.py build --plan` embeds notes into `notesSlide` and builds valid OOXML timing.
- [x] `scripts/design_critic.py` measures 6 dimensions including `narrative` (5.0 on directed decks, 2.7 on T066).
- [x] 12/12 unit tests passing in `tests/test_deck_director.py`.
- [x] `python lab/tools/check_layout.py` returns `layout OK`.
