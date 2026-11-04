# T057 [cross] — Lead review after T035–T056, the DeckCraft question, and the next research programme

- **Agent / model:** Claude (Opus 5.5), desktop session on the owner's machine.
- **Date:** 2026-11-04. **Base:** `main` @ `43d6047` (after T056).
- **Role:** the owner asked Claude to act as lead: read what the other agents
  did, name the difficulties, judge them, and set the next research directions
  for other agents to execute and criticise. It also asked one direct question:
  *does DeckCraft make it easier for an AI to create assets in PPTX?*
- **Environment:** Windows 11, PowerPoint 16.0 (COM), Python 3.13,
  DeckCraft CLI 0.13.1 (`D:\artcraft\DeckCraft\deckcraft-cli.exe`).

## Frame

- **Question 1:** where does the lab stand after 22 tasks in four days, and
  what is blocking the original goal: an AI-first tool that makes PPTX decks
  of the highest finish, with real motion?
- **Question 2:** is DeckCraft a better asset and verification channel for
  PPTX than python-pptx plus PowerPoint COM, and where does it stop?
- **Falsifiers:**
  - For question 2, DeckCraft's render differs visibly from PowerPoint's.
  - For question 2, DeckCraft's PPTX round trip drops our timing.
  - For question 2, DeckCraft cannot add anything that python-pptx cannot already do.
  - For question 1, the pptx open problems from T034 turn out to be closed.

## Evidence

### Lab state

| Fact | Measured | Rung |
|---|---|---|
| Test suite on `main` | 461 tests, OK, 4 skipped, 30.5 s | 1 |
| Tasks since T034 | T035–T056: 22 IDs, of which 8 pptx, 5 docx, 5 xlsx, 4 vector, 4 cross | 1 |
| Duplicate IDs | T042, T043, T047, T048 and T049 were each used twice (Antigravity vs OpenCode); INDEX papers over it with `T047b`/`T048b` | 1 |
| pptx features committed straight to `main` without a PR or review | T043 theme engine, T047 office link bridge, T048b slide navigator, T049 interactivity (`8d47bd5`, `924ed8b`, `b0677a7`, `0026dce`, `b2bf91e`) | 1 |
| Reviews | 11 files in `research/reviews/`, **all by Argon**. T035–T038, T042–T044 and T048b/T049 have no review. | 1 |
| Core pptx engine | No change to `pptx_animator.py`, `motion_engine.py` or `motion_director.py` since T038 (2026-11-01) | 1 |
| T034 open problems | Still open. A fresh Forge build of `vi_chuyen_doi_so.json` gives TYP-SIZES 13 (band 3–6) and MOT-SETTLE on slide 1. | 1 |
| Handoff readable | `HANDOFF.md` is mojibake: UTF-8 was read as cp1252 and saved again. It says the next ID is T047 when the real one is T057. Mojibake also appears in `docs/CHANGELOG.md` (133 lines), `domains/README.md` and four experiment reports. | 1 |
| `docs/STATUS.md` | Stale: still says "`main` is behind" and "289 tests". | 1 |
| Timing writers | `interactiveSeq` is written by three separate modules: `interactive_triggers.py`, `advanced_interactivity.py` and `slide_navigator.py`. `pptx_animator.py` writes none. The T049 root-cause findings (cond on the interactiveSeq `cTn`, child delay) live only in `advanced_interactivity.py`. | 1 |
| Interactive decks (T048b/T049) | PowerPoint opens all three. It parses the triggers: one-slide games give 4 interactive sequences with 6 effects per slide; the hubs give 1–3 action buttons per slide. **Nobody has clicked them in a slide show.** "100% working" in `8d47bd5` is a rung-4 claim. | 4 |
| Automated slide-show clicking | An attempt from this agent's shell did not work: the slide show started, but `screenClass` HWND = 0 and the coordinates could not be mapped. It is still open. | negative |
| Repo weight | `.git` is 116 MB; 392 tracked office/media files. T054 adds 24.8k lines and T055 adds 27.8k lines (GLB, PDF, PPTX). | 1 |
| Unmerged | `work/T054-opencode-vector-match` and `work/T055-opencode-pptx-3d`, which is stacked on T054. Codex T009/T021 are historical. | 1 |

### DeckCraft against PowerPoint (`inputs/commands.md`)

Deck: Forge build of `examples/pptx/forge/vi_chuyen_doi_so.json`, 9 slides,
99 effects, 8 Morph transitions.

| Test | Result | Rung |
|---|---|---|
| Static render, all slides, 1920×1080 | DeckCraft 2.6 s (CLI, cold). PowerPoint COM `Slide.Export` 0.85 s. **Speed is not the gain on a machine with Office.** | 4/5 |
| Static fidelity, DeckCraft vs PowerPoint | Mean absolute difference 0.2–2.8 per slide (0–255 scale). Pixels differing by more than 40: 0.1–2.1%. The visible differences are chart markers and legend style (slide 4); text, Vietnamese diacritics, gradients, picture crop and soft art all match (`preview/deckcraft-vs-powerpoint.jpg`). | 4 vs 5 |
| Reads our timing | `animation.get` returns the effects with presetId, subtype, start, duration, repeat and rewind. | 4 (DeckCraft) |
| PPTX round trip (`convert`) | 3/9 slides identical in effect structure. On 6 slides, Ascend (preset 42) loses its identity `ppt_x` anim (`p:anim` 6→3 on slide 7). Visually equivalent, but **not byte-preserving**. | 1 |
| Morph frames | `render-transition --t 0.25,0.5,0.75` 0.19 s (`preview/deckcraft-morph-t050.jpg`). PowerPoint has no equivalent short of CreateVideo, which takes minutes. **But** the frame shows the next slide's KPI count-up stack and its entrance-hidden shapes fully drawn. PowerPoint hides entrance-animated shapes during Morph. **The fidelity of DeckCraft's Morph frames is unproven.** | 4 (DeckCraft), unverified vs 5 |
| In-slide animation frames | **No such command.** `render` draws the end state; `render-transition` draws transitions only. Motion QA still needs PowerPoint CreateVideo. | — |
| Authoring surface | 330 commands, also served over MCP (`deckcraft-cli mcp`). Missing from python-pptx: `shape.merge` (union / combine / fragment / intersect / subtract), `shape.freeform` with smooth curves, `shape.points` / `shape.editPoints`, shape effects (bevel, glow, soft edges, reflection, 3D), `picture.removeBackground`, crop, artistic effects, `insert.smartArt`, `insert.icon`, `design.ideas`. Its animation gallery has 107 effects (40 paths, 24 entrance, 23 exit, 17 emphasis); our `ppt:` library has 198. | 4 (DeckCraft) |
| Licence | MIT or Apache-2.0, source at `github.com/storytold/deckcraft`. The ArtCraft brand marks are not open. | 1 |

### Defects found in passing (Forge, present in both renderers)

1. **Static and print view of KPI count-ups.**
   - The stacked count-up frames are all visible in the end state, in PDF export
     and in Morph frames: "35%" is drawn over "28%", "21%" and the other frames.
   - A printed or exported Forge deck therefore shows garbled numbers.
2. **Process takeaway highlight is misaligned horizontally.**
   - The marker spans x≈36–316 px while the centred text sits at x≈203–437 px,
     on slide 5 of the build above.
   - The T030 anchor fix covered vertical anchoring only.

## Judgement

### Where we are

The PPTX core does what the owner first asked for, and it is natively rendered
in PowerPoint:

- pictures move (Ken Burns, float);
- structures are choreographed;
- there are accent motion graphics, 198 PowerPoint presets and Morph;
- design and motion come from one design system;
- a critic scores the result.

Since 2026-11-01 the lab has spread wide: Word, Excel, vector, 3D, CAD, video
and audio canons. It has not gone deeper on the pptx core. The three T034
problems are unchanged. The interactive gate, never played in a live slide
show, is two months old. It now also covers T048b and T049.

### Difficulties, ranked by how much they block the goal

1. **Verification gap.**
   - Interactive and trigger work is claimed "100% working" at rung 4.
   - The Morph/3D claims rest on export images.
   - There is no automated slide-show harness, so every new interactive
     feature adds unverified surface.
2. **Breadth before depth.**
   - Of 22 tasks, 8 are pptx, and none closes a pptx gate.
   - `video`, `3d` and `cad` are canon tables and CLI bridges with no
     product path.
   - The repository is still called `skill-for-pptx` and the owner's goal is
     PPTX.
3. **Process hygiene broke under parallel agents.**
   - Five duplicate IDs.
   - pptx code pushed to `main` without PR or review.
   - A single reviewer (Argon) for everything: one model family judging
     another's work every time is a monoculture.
   - The first file every agent reads (`HANDOFF.md`) is corrupt and points
     at the wrong next ID.
4. **Fragmentation of the timing layer.** Three `interactiveSeq` writers mean
   a fix (T049) reaches one module and not the others. AGENTS.md's own rule,
   "one canonical module per capability", is broken.
5. **Forge debt that a user sees.**
   - Print and PDF of count-ups.
   - Highlight alignment.
   - 13 type sizes.
   - MOT-SETTLE.
6. **Repo weight.** 116 MB, growing by about 25k lines per vector/3D task.

### The DeckCraft answer

**Yes, but for asset creation and Morph previews, not for verifying motion.**

- **Where it makes PPTX asset work easier:**
  - It turns PowerPoint-only drawing operations into scriptable commands that
    an agent can call over MCP. These are Merge Shapes, freeform curves with
    edit points, bevel, glow and soft-edge effects, background removal,
    SmartArt and icons, and python-pptx cannot reach any of them.
  - An agent can therefore build native, editable illustration assets
    (badges, device mockups, custom diagram parts, cut-out photos) inside the
    PPTX, and animate each part. That is the gap the vector tasks
    (T051–T056) tried to cross through SVG.
  - It renders the same file almost identically to PowerPoint without Office.
    Agents on machines without PowerPoint can then see their work.
- **Where it does not help:**
  - It does not render in-slide animation timelines, which are the core of
    this project.
  - Its Morph frames are not yet trusted.
  - Its round trip rewrites timing nodes. Do not let DeckCraft be the last
    writer of a deck whose timing we authored. Use it to make assets, or as
    a pre-stage before the Motion Director.
- **The bigger opportunity:**
  - DeckCraft is open source and already renders transitions frame by frame.
  - A `render-animation --slide N --t …` that plays the timing tree would
    give the lab motion QA without PowerPoint. It is worth a source study
    and, if feasible, an upstream contribution.

## Next research programme

Priorities: **close gates before opening domains.** Breadth is frozen for one
cycle. No new domain or canon task until T058–T061 are reviewed, except work
that feeds a PPTX asset (T062, T064).

Each brief names a builder and a critic of a **different model family**. The
critic writes `research/reviews/<ID>-<critic>-<date>.md` and must try the
falsifiers itself.

| ID | Brief | Builder → critic |
|---|---|---|
| T058 | [pptx] Interactive slide-show harness | Claude desktop → Argon |
| T059 | [pptx] DeckCraft as second renderer: fidelity matrix | OpenCode → Claude |
| T060 | [pptx] DeckCraft source study: in-slide animation frames | Claude → OpenCode |
| T061 | [pptx] One canonical interaction writer | OpenCode → Claude |
| T062 | [pptx] Native asset factory through DeckCraft commands | Antigravity → Claude |
| T063 | [pptx] Forge debt that users see | OpenCode → Argon |
| T064 | [pptx] Decouple and review T055 native 3D | Claude → OpenCode |
| T065 | [cross] Lab hygiene | any → owner |

### T058 [pptx] Interactive slide-show harness (rung 6 without a human)

- **Question:** can an agent click shapes in a live PowerPoint slide show and
  capture the result?
- **Method:**
  - start the show windowed;
  - find the show window (UI Automation, `EnumWindows` by process, or the
    Windows-MCP tools);
  - map slide points to screen pixels with DPI awareness;
  - send clicks;
  - capture frames;
  - assert pixel change inside the target's box.
- **Apply it to:** T049 one-slide games, T048b hubs, the T032 triggers and the
  Director's spotlight decks.
- **Falsifier:** shells without an interactive desktop cannot get the window.
  If so, write the minimum manual protocol, with a checklist and a screen
  recording, and say which agent host can run it.
- **Negative result to start from:** this report, where `screenClass` HWND = 0
  from the agent shell.

### T059 [pptx] DeckCraft as second renderer: fidelity matrix

- **Static renders:** for every deck in `examples/pptx/forge/` and the T028
  pro decks, report the static diff per slide and per object kind (text,
  chart, picture, gradient, effects) against PowerPoint `Slide.Export`.
- **Morph frames:** compare `render-transition` against PowerPoint CreateVideo
  frames at matched t, including entrance-hidden shapes.
- **Round trip:** a table of which timing nodes `convert` rewrites, and
  whether PowerPoint still plays them the same.
- **Wiring:** use it in `slide_forge.py render` and `design_critic.py` as a
  fallback when PowerPoint is absent. Label the result `DeckCraft render`,
  never `PowerPoint`.
- **Falsifiers:**
  - The per-slide diff exceeds the critic's sensitivity, so critic scores
    differ by more than 0.2.
  - The Morph frames disagree.

### T060 [pptx] DeckCraft source study: in-slide animation frames

- **Question:** does `storytold/deckcraft` contain a timing-tree player? It
  must have one in some form, because its app plays slide shows.
- **Task:**
  - Find it.
  - Estimate the work to expose `render-animation --slide N --click K --t ms`.
  - Prototype it locally if small.
  - Compare against CreateVideo strips for the Forge `dynamic` deck, covering
    easing, autoRev and repeat, motion paths, and the 198 `ppt:` presets.
- **Deliverable:**
  - a feasibility report;
  - if the prototype works, a patch proposed upstream through the owner,
    never pushed on their behalf.
- **Falsifier:** no player exists in the CLI build, or the presets it plays
  are fewer than 50% of ours.

### T061 [pptx] One canonical interaction writer

- Move `interactiveSeq`, trigger and hyperlink-conflict logic into one module.
  It is either `pptx_animator.py` or a new `pptx_interaction.py` that it owns.
- `interactive_triggers.py`, `advanced_interactivity.py` and
  `slide_navigator.py` become thin callers.
- Port the T049 findings and keep their tests.
- **Acceptance:**
  - byte-stable output for the T048b and T049 artifacts, or a documented diff;
  - PowerPoint parse counts unchanged;
  - T058 clicks pass.

### T062 [pptx] Native asset factory through DeckCraft commands

- **Question:** for a PPTX-bound illustration (icon set, badge, device mockup,
  product cut-out, diagram parts), compare three routes:
  - DeckCraft shape commands (merge, freeform, effects) producing native
    shapes;
  - the SVG routes (T053/T056);
  - the GLB route (T055).
- **Measure for each route:**
  - editability in PowerPoint;
  - per-part animation (can the Director move each part?);
  - file size;
  - render diff;
  - author effort;
  - owner eye test.
- **Deliverable:** a Forge `asset` spec, `{"native_art": …}`, compiled
  through DeckCraft commands on Windows and skipped with a coded error
  elsewhere.
- **Falsifier:** the parts lose their identity after `convert`, so the
  Director cannot target them.

### T063 [pptx] Forge debt that users see

- **Count-ups:**
  - Make a static, print and Morph-safe count-up: only the final value
    visible in the end state, with the intermediate frames hidden by their
    exit or set effects.
  - Or flag it with a `[static]` fallback.
  - Verify with PDF export and `render-transition`.
- **Highlight marker:** align it horizontally for centred and right-aligned
  text.
- **Type scale:** use the Office kit `type_scale_pt` to reach 3–6 sizes.
- **MOT-SETTLE:** apply the T034 proposed fix.
- **Acceptance:** the critic has no TYP-SIZES and no MOT-SETTLE on all
  example decks, and the PowerPoint render frames are inspected.

### T064 [pptx] Decouple and review T055 native 3D

- **Rebase:**
  - Rebase T055 so that it does not depend on unmerged T054. The GLB is an
    input artifact.
  - Review it under `lab/standards/REVIEW.md`.
- **Next question:** does Morph between two camera views of the same 3D model
  play in PowerPoint (CreateVideo, rung 5)? Report frames.
- **Then:** a Forge layout `product3d`.
- **Falsifier:** Morph falls back to fade for `model3d` objects.

### T065 [cross] Lab hygiene

- **Encoding:**
  - Repair the mojibake in `docs/CHANGELOG.md`, `domains/README.md` and the
    four reports.
  - Add `check_layout.py` rules for mojibake markers (`Ã`, `â€`, `á»` and
    `Ä‘` in UTF-8 text).
- **Index:**
  - Add a rule against duplicate IDs in INDEX.
  - Record a rule that pptx product paths change only through a PR with a
    review.
- **Size cap:** cap committed artifacts at 2 MB per file and 10 MB per task,
  with larger files kept local and hashed. Owner decision: Git LFS or not.

### Not doing now

The `video`, `3d` (except T064), `cad` and audio domains stay frozen at their
T042 canon level. The docx, xlsx and vector tracks continue only where the
owner asks for them. Their reviews stay open but at low priority.

## Negative results and limits of this review

- Automated slide-show clicks did not work from this shell. That is an open
  research item (T058), not a proof that it is impossible.
- DeckCraft fidelity was measured on one deck. The Morph frame comparison
  against PowerPoint was not done.
- The breadth tasks (docx, xlsx, vector) were not re-reviewed here. Their
  Argon reviews stand.
