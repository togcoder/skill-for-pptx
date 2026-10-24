# T025 — Slide Forge: agent-facing spec → finished deck (2026-10-07)

Owner direction (2026-10-07): build a tool *for AI, not for people* that makes
slides at the highest finish. The trigger was a short-prompt deck that only
animated its text boxes. Until now the repo animated existing decks. It had no
way to *author* a deck whose structure gives the Director something to
choreograph.

## What exists now

```
deck.json ──build──▶ static PPTX ──Motion Director──▶ PPTX ──forge_qa──▶ verdict JSON
   ▲                                                    │
   └──────────── agent repairs the spec ◀── render (PowerPoint CreateVideo → per-slide strips)
```

- **Spec** (`slide_forge.py schema`): 12 semantic layouts, theme tokens, motion
  options. The validator returns coded errors with fix hints (`THEME_UNKNOWN`,
  `STRUCTURE`, `CHART_DATA`, `TOO_DENSE`, …).
- **Builder:**
  - Layout grid on 13.333×7.5 in.
  - Type is measured with the real font file. The fitter is bold-aware, refuses
    mid-word breaks and uses the inscribed rectangle for ellipses; it shrinks
    to fit and reports `TEXT_SHRUNK`/`TEXT_OVERFLOW`.
  - Pictures are cropped to fill (no distortion).
  - On-theme generated art is labelled.
  - Charts are native and themed. Process arrows are real connectors.
  - Two `!!orb` shapes rotate corner to corner, so Morph adds a motion-graphic layer between slides.
- **Motion:** the layouts are built so the Director recognises cards, process
  rows, cycles, charts, pictures and accents. That yields KPI count-ups,
  series chart builds, step-per-click processes (English or Vietnamese
  sequence words in notes), assemble → spotlight tour → release on cycles,
  Ken Burns pictures, accent draw-ins and Morph.
- **QA** (`forge_qa.py`, any PPTX):
  - Errors: `TEXT_OVERFLOW`, `WORD_BREAK`, `TEXT_COLLISION`, `OFF_SLIDE`, `LOW_CONTRAST` (WCAG AA).
  - Warnings: `TYPE_TOO_SMALL`, `MOTION_NONE`, `PICTURE_FROZEN`.
  - Metrics: effects, Morph count, motion coverage, moving pictures.
- **Render** (`slide_forge.py render`): desktop PowerPoint → MP4 plus one
  6-frame strip per slide, and the main sequence as PowerPoint parsed it.
- **Agent surface:** `skills/slide-forge/SKILL.md`, `/forge-deck`, plugin 0.10.0.

## Evidence

| Deck | Slides | Effects | Morph | Motion coverage | Pictures moving | QA |
|---|---|---|---|---|---|---|
| `coffee_report.pptx` (EN, midnight, modern) | 10 | 118 | 9 | 1.0 | 2/2 | ok, 0 warnings |
| `vi_chuyen_doi_so.pptx` (VI, paper, cinematic) | 9 | 96 | 8 | 1.0 | 1/1 | ok, 1 `TEXT_SHRUNK` |

Both were rendered by **PowerPoint 16.0 build 17932** (`render-en/`, `render-vi/`).
Looking at the renders found defects that the first QA version missed:

1. `2.1 days` wrapped out of its KPI card.
2. `Customer` and `Measure` broke mid-word inside ellipses.
3. Background orbs were large and crossed content.
4. Body type was too small for 13.3 in slides, and blocks hugged the top.

Fixes 1–2 are now caught by QA with the same metric the builder uses (rerunning
QA on the old file reports `TEXT_OVERFLOW` and two `WORD_BREAK`s). Fixes 3–4
changed the layouts.

The Vietnamese deck exposed two more problems:

- `paper`/`sunrise` accents were below 4.5:1, so `LOW_CONTRAST` fired on the
  kicker. Their palettes were fixed, and a test now holds every theme to AA.
- Vietnamese sequence words were not recognised as click cues. They now are.

Tests: `tests/test_slide_forge.py` has 11 tests. The full suite passes
(`PYTHONUTF8=1` on Windows).

## Limits

- CreateVideo auto-advances clicks. Interactive slideshow timing is still unverified.
- Generated art is abstract. Real photography must come from the user.
- No table, timeline, icon or two-picture layouts yet. One master and one font pair (Segoe UI) only.
- Fit metrics use Pillow, with a 6% safety margin; fonts missing on the render machine fall back to estimates.
- Counter proxies (KPI count-up) clutter edit view and PDF export (T014 caveat).

## Next

Tables (row reveal), timeline, icon grid, image + caption grids, two-picture
before/after with Morph, brand-template input (read a user's .potx for theme
and fonts), and a `critique` command. The critique command would score
render strips for density, balance and motion rhythm so the agent's visual
check becomes measurable.
