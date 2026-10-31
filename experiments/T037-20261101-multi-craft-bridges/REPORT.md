# T037 — Multi-Craft Native Bridges & Intent-Empathy Decoder Engine

## Frozen input

- **Request.** Implement concrete bridges for the primary ArtCraft creative applications (WordCraft, GridCraft, VectorCraft), connect the Intent & Empathy Decoder engine implementing Protocol 00, and ensure all tests pass with full native verification.
- **Base.** Branch `work/T037-multi-craft-bridges` @ `eaef343` (branched from T036).
- **Environment.** Windows 10/11 x64, Python 3.12, ArtCraft Suite (`D:\artcraft`).

## What was built

### 1. Multi-Craft Native Bridges
- `scripts/wordcraft_bridge.py`:
  - Discovers `wordcraft-cli.exe` in `D:\artcraft\WordCraft`.
  - Exposes `inspect_document()`, `render_page()`, `convert_document()`, and `extract_text()`.
- `scripts/gridcraft_bridge.py`:
  - Discovers `gridcraft-cli.exe` in `D:\artcraft\GridCraft`.
  - Exposes `inspect_sheet()`, `eval_formula()`, `convert_sheet()`, and `cat_range()`.
  - Evaluates formulas natively via headless calc oracle (e.g. `2 * 3.14159 * 10 -> 62.8318`).
- `scripts/vectorcraft_bridge.py`:
  - Discovers `vectorcraft-cli.exe` in `D:\artcraft\VectorCraft`.
  - Exposes `inspect_vector()` and `convert_vector()` with artboard and scale options.

### 2. Intent & Empathy Decoder Engine (`scripts/intent_decoder.py`)
- Concrete implementation of Protocol 00.
- Decodes raw user prompts into 5 dimensions:
  1. *Audience Persona:* Executive C-Level, Technical Engineer, Student, Commercial Client, General Public.
  2. *Cognitive Budget:* Max visual groups (3–4), word count limits, Z-pattern vs F-pattern, comprehension target seconds ($\le 3.0$–$5.0$s).
  3. *Viewing Context:* Projector in bright room (enforcing $\ge 18$pt font), Desktop screen, Print A4 CMYK.
  4. *Canonical System:* Swiss Grid, Dieter Rams Minimal, Edward Tufte Data, IBM Carbon, Material 3.
  5. *Craft Routing:* Directs tasks to `deckcraft`, `wordcraft`, `gridcraft`, or `vectorcraft`.
- Validates the generated output against `schemas/intent_brief.schema.json`.

### 3. Test Coverage & Verification Evidence
- Added `tests/test_craft_bridges.py` and `tests/test_intent_decoder.py`.
- Test suite expanded from 296 to **302 tests, all passing (0 failures, 4 skipped)**:
  ```text
  Ran 302 tests in 8.698s
  OK (skipped=4)
  ```
- Evaluated formulas and vector/word binaries against the live `D:\artcraft` installation.

## Next steps

1. Update `HANDOFF.md`, `CHANGELOG.md`, and `INDEX.md` (freeing T038).
2. Wire Intent Decoder directly into `slide_forge.py` and `motion_director.py` CLI options.
3. Prepare the cross-craft orchestration runner for compound multi-asset decks.
