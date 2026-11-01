# T048 [pptx] — Non-Linear Slide Navigation: Interactive Branching, Return Paths, Kiosk Mode & Mini-Game State Machine

## Frame
- **Question:** How can AI agents move beyond strictly linear, front-to-back slide generation ($S_1 \to S_2 \to \dots \to S_N$) to build real-world non-linear presentation structures—including branching navigation (Hub & Spoke), auxiliary drill-down/popup slides that return dynamically to the calling narrative ("quay về kể tiếp"), custom show sequences with automatic return, and interactive PowerPoint mini-games/quizzes locked in kiosk mode?
- **Hypothesis (and what would falsify it):** By implementing an ISO/IEC 29500 PresentationML-compliant navigation engine (`scripts/slide_navigator.py`), agents can:
  1. Wire inter-slide named hyperlinks (`a:hlinkClick` with target slide relationships) and special action schemes (`last_viewed`, `first_slide`, `next_slide`, `previous_slide`, `end_show`).
  2. Implement dynamic return paths using native `ppaction://hlinkshowjump?jump=lastslideviewed`, enabling auxiliary popup slides to return automatically to whichever slide called them.
  3. Construct custom show branching (`<p:custShowLst>`) with "Show and Return" (`action="ppaction://customshow?id=...&return=true"`), automatically resuming the main deck after sub-sequences finish.
  4. Enforce non-linear interaction by disabling accidental background clicks (`advClick="0"`) and enabling full-screen Kiosk Mode (`<p:kiosk restart="4294967295"/>`).
  5. Compile educational mini-games and quiz state machines with branch choices, wrong answer retry loops, and victory screens.
  Falsified if PowerPoint displays schema or corruption warnings, if `lastslideviewed` fails to register in PowerPoint COM (`Action != 5`), if Kiosk mode fails (`ShowType != 3`), or if DeckCraft fails to render the interactive slides.
- **Domain lens (native canon and sources used):**
  - ISO/IEC 29500-1:2016 PresentationML & DrawingML Specification
  - Microsoft PowerPoint Action Setting Architecture (`ppaction://hlinksldjump`, `ppaction://hlinkshowjump`, `ppaction://customshow`)
  - Project Owner Mandate (2026-11-01): Research and establish the non-linear interactive bridge for AI agents across ArtCraft and PowerPoint.
- **Transfers from other domains (and how they are tested):**
  - Directed Graph / DAG algorithms (`lab/protocols/02_delegation_dag.md`) transferred into presentation state machine analysis (`inspect_navigation_graph`).
  - DeckCraft CLI rendering engine (T035/T038/T044) used as a headless visual verification gate at 1920x1080.
  - Interactive click trigger mechanics (T033) extended from in-slide animation sequences to inter-slide navigation and state machines.

## Frozen input
- Request / date: User directive on non-linear presentations, branching navigation, returning to the narrative ("quay về kể tiếp"), auxiliary popup slides, and mini-games (2026-11-01).
- Base commit: `afb224e6894a2ac2c55e64a3e8fd16946d7c8f7a`
- Host environment: Windows 11, Python 3.12, Microsoft Office 16.0 (PowerPoint COM), DeckCraft CLI (`D:\artcraft\DeckCraft\deckcraft-cli.exe`).

## Method
Commands to reproduce:
```powershell
$env:PYTHONUTF8=1
cd skill-for-pptx
python -m unittest tests/test_slide_navigator.py -v
python experiments/T048-20261101-antigravity-slide-branching/make_artifacts.py
python lab/tools/check_layout.py
python -m unittest discover -s tests
```

## Evidence
| Claim | Rung (0–6) | Evidence (path, hash, output) |
|---|---|---|
| Dynamic Return Path (`last_viewed`) | Rung 4 | Tested via PowerPoint 16.0 COM: shape action evaluates to `ppActionLastSlideViewed` (`Action == 5`). Verified on both `interactive_adventure_game.pptx` (retry button) and `executive_interactive_hub.pptx` (auxiliary slide back button). Zero repair prompts. |
| Custom Show Branching with Return | Rung 4 | `<p:custShowLst>` injected before `<p:defaultTextStyle>` in schema sequence with `ppaction://customshow?id=0&return=true`. Verified via COM: `NamedSlideShows.Count == 1`, `Action == 10`, `ShowAndReturn == -1` (True). |
| Kiosk Mode & Slide Click Lock | Rung 4 | `<p:kiosk restart="4294967295"/>` injected before `p:extLst` in `ppt/presProps.xml` + `advClick="0"` on slide transitions. Verified via COM: `SlideShowSettings.ShowType == 3` (ppShowTypeKiosk) and `AdvanceOnClick == 0` (msoFalse). |
| Visual Rendering Integrity | Rung 3 | DeckCraft CLI rendered all 10 slides across both presentations to 1920x1080 PNGs in `artifacts/previews/game/` and `artifacts/previews/hub/`. |
| Directed Navigation Graph Inspection | Rung 1 | `scripts/slide_navigator.py::inspect_navigation_graph` successfully parses slides, edges, and produces Mermaid DAG and JSON audits (`audit_game.json`, `audit_hub.json`). |
| Unit Test Suite Coverage | Rung 0 | `tests/test_slide_navigator.py`: 6 tests pass in 0.36s. Full repository test suite passes 397/397 tests 100%. |
| Layout Conformance | Rung 0 | `lab/tools/check_layout.py` reports `layout OK`. |

## Key Architectural Findings: Non-Linear PPTX Mechanics
1. **The `last_viewed` Action (`ppaction://hlinkshowjump?jump=lastslideviewed`)**:
   - `python-pptx` natively treats `ActionSetting.action` as read-only and does not allow setting special show jumps.
   - Injecting `<a:hlinkClick action="ppaction://hlinkshowjump?jump=lastslideviewed"/>` directly into `<p:cNvPr>` enables dynamic return navigation. When an auxiliary or drill-down slide is called from Slide 2, clicking "Back" returns to Slide 2; if called from Slide 4, it returns to Slide 4.
2. **Kiosk Mode & Click Disabling (`advClick="0"`)**:
   - In ISO/IEC 29500 PresentationML, the attribute on slide transition is `advClick="0"` (not `advanceOnClick`).
   - In `ppt/presProps.xml`, `<p:showPr>` MUST precede `<p:extLst>`.
   - Combining both creates true kiosk / game behavior: clicking empty space on the slide does nothing; players are forced to navigate through designed buttons.
3. **Mini-Game State Machine Compilation**:
   - Structured JSON specs (`compile_mini_game_state_machine`) allow AI agents to assemble branching educational games, quiz assessments, and interactive kiosks in seconds without low-level XML handling.

## Negative results and limitations
- While DeckCraft CLI accurately renders all shapes, cards, text, and visual buttons at 1920x1080, DeckCraft is currently a headless renderer and does not run interactive slide-show click loops (which requires presentation mode in PowerPoint or an interactive viewer sidecar).
- Care must be taken with schema sequence ordering: `<p:custShowLst>` must come before `<p:defaultTextStyle>` in `presentation.xml`, and `<p:showPr>` must come before `<p:extLst>` in `presProps.xml`. Inserting after `extLst` causes PowerPoint to silently ignore the properties.

## Next
- Integrate `slide_navigator.py` into Slide Forge (`scripts/slide_forge.py`) with a declarative top-level `"navigation"` block in slide JSON specs.
- Package reusable mini-game archetypes (Multiple Choice Quiz, Jeopardy Grid, Branching Decision Tree) into ArtCraft templates.
- Submit T048 for peer review (Argon / OpenCode / Claude).

## Review response
| Finding | Response (fixed / disputed / deferred → task) |
|---|---|
| (Pending peer review) | review requested |
