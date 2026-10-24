# Design system: one source for beauty and technique

Status: implemented in T034 (2026-10-19). The evidence levels are structural,
simulated and LibreOffice-rendered. PowerPoint playback has not been
observed; see [VERIFICATION.md](VERIFICATION.md).

## Why

Before T034, "what looks good" lived in prose and "how it is built" lived in
code, and the two disagreed:

- **Easing:** five different systems.
- **Durations:**
  - Entrance durations differed between the craft rules, the director
    styles, the recipe defaults and a pacing module.
  - Travel time scaled with distance in theory but was never used.
- **Colour:** three contrast functions, plus a QA threshold of 24 pt where
  WCAG says 18 pt.
- **Morph timing:** a Morph rule existed only as a warning.

The result was decks that passed every check and still looked wrong:

- Generated halos and orbit rings were painted at 1.14:1 on dark brand
  themes, so they were invisible (see
  `experiments/T034-20261019-claude-design-system/preview/before-after-helpers.png`).
- A merge silently reverted the arrival easing.

The fix is structural. Generators and checkers read the same numbers from one
file, so beauty and technique cannot drift apart again.

```
knowledge/design_system.json        tokens + rules (+ sources)
        │  read by                         │  graded by
        ▼                                  ▼
generators                         checkers
  motion_engine (easing, defaults,   validate_director_plan (limits)
    overshoot clamp, travel time)    motion_director.verify (structure)
  pptx_animator (default easing)     forge_qa (contrast, overflow, type)
  motion_director (styles, chart     morph_studio.settle_report
    steps, helper colours, marker)   design_critic (every rule, scored)
  motion_components (deck_style)            │
  slide_forge (contrast via the             ▼
    same function)                   report: rule · measured · band · fix · tool
        ▲                                  │
        └──────────── fix (author or AI) ◄──┘
```

This is the detect-and-correct loop of DesignLab (2025), with *computed*
metrics as the judge. The latest benchmarks favour computed metrics:

- SlidesGen-Bench (2026): computational aesthetics reach Spearman 0.71
  against human rankings, versus 0.53–0.57 for LLM judges, including
  PPTEval.
- Inui et al. (2025): seven design metrics reach Pearson up to 0.83 with
  human visual-quality ratings, above VLM judges.

No benchmark measures slide motion, so the motion rules come from perception
research and design-system tokens (below).

## Files

| File | Role |
|---|---|
| `knowledge/design_system.json` | Bands (good) and limits (acceptable) per token, rule list with evidence, sources |
| `scripts/design_system.py` | Loader: `duration(role)`, `default_ms`, `grade`, `clamp`, `easing(role)`, `travel_ms`, `contrast`, `text_contrast_needed`, `graphic_contrast_needed` |
| `scripts/motion_tokens.py` | Easing curves (Carbon, Material 3) fitted to PowerPoint accel/decel (T029) |
| `scripts/design_critic.py` | Measures a deck against every rule; JSON verdict and Markdown; `--render lo\|DIR`, `--xsd` |
| `scripts/forge_critique.py` | Compatibility entry for the T031 critique (now delegates) |

A **band** is `[good_min, good_max]` and a **limit** is
`[hard_min, hard_max]`. Outside the band, a finding is a *note*. Outside the
limit, it is a *warning*. Validators reject only what is outside a limit or
structurally wrong.

## Tokens

| Token | Band | Limit | Default | Grounds |
|---|---|---|---|---|
| enter | 250–700 ms | 150–1000 | 500 | Carbon moderate–slow, Material medium–long; presentations sit at the slow end |
| exit | 200–500 ms | 120–900 | 350 | Exits shorter than entrances (Material) |
| emphasis | 250–600 ms (autoRev counts twice) | 150–1200 | 450 | |
| move | 400–1200 ms, `travel_ms(distance)` | 250–2000 | 700 | Longer journeys take longer (Carbon/Material); Heer & Robertson 2007 |
| morph | 1000–1600 ms | 500–3000 | 1400 | Camera moves need time to be followed |
| ambient cycle | 6–60 s | 3–120 s | 12 s | Slow enough to stay background (coherence principle) |
| letter / word gap | 20–60 / 60–200 ms | | 35 / 100 | Typewriter legibility |
| stagger | 60–150 ms | 0–400 | 120 | Chevalier et al. 2014: staggering does not help tracking, so it only shows order |
| overshoot / anticipate | ≤ 0.08 / ≤ 0.05 | | | Material 3 Expressive: low bounce for spatial motion |
| clicks per slide | ≤ 6 | ≤ 8 | | Segmenting principle |
| movers per click | ≤ 4 | ≤ 8 | | Multiple-object tracking ≈ 4 (Pylyshyn & Storm 1988), variable with speed (Alvarez & Franconeri 2007) |
| effects per click | ≤ 8 | ≤ 14 | | Corpus mean is 1.94 per click (knowledge/) |
| effect kinds per deck | 3–10 | 2–14 | | One language, above the corpus median of 2 |
| text contrast | 4.5:1; large text 3:1 (≥ 18 pt, or 14 pt bold) | | | WCAG 2.2 SC 1.4.3 |
| graphic contrast | 3:1 | | | WCAG 2.2 SC 1.4.11 (helpers: halo, ring, rail, token, underline) |
| type sizes per deck | 3–6 | 2–9 | | Office designer themes use 4–5 |
| body text | ≥ 18 pt | ≥ 12 | | Office themes: body 18–28 pt |
| title / body | 1.5–2.6 | 1.2–4.0 | | Office themes: title ≈ 2× body |
| words per content slide | ≤ 45 | ≤ 80 | | Designer decks vs corpus (knowledge/) |
| settled frame background | 60–95 % | 45–98.5 % | | Whitespace (Inui 2025) |
| balance offset | ≤ 0.15 | ≤ 0.22 | | Layout balance (Inui 2025) |
| colourfulness (Hasler–Süsstrunk) | 15–80 | 5–110 | | Engagement (SlidesGen-Bench) |

Easing roles map to fitted PowerPoint pairs:

| Role | Token | accel / decel | Fit error |
|---|---|---|---|
| move, emphasis | Carbon standard productive | 0.15 / 0.70 | 1.5 % |
| enter | Carbon entrance productive | 0 / 0.90 | 2.4 % |
| exit | Carbon exit productive | 0.35 / 0 | 4.4 % |
| hero | Carbon standard expressive | 0.15 / 0.75 | 6.1 % |
| ambient | linear | 0 / 0 | |

Material's emphasized curves fit only within 18–44 % with one accel/decel
pair, so they stay addressable (`md-*`) but are not role defaults.

## Rules → generator → checker

| Rule | Statement (short) | Generator obeys by | Checked by |
|---|---|---|---|
| MOT-DURATION | Each effect lasts what its role allows | `STYLES` in band; chart steps `ds.clamp(…,"enter")`; ring reveal = enter max; recipe default `ds.default_ms("move")`; travel hops `ds.travel_ms` | critic |
| MOT-EASING | Moves slow in/out | Keyframes default to `standard`; arrivals use `enter`, departures use `exit`; writer default path easing = `move` role | critic (linear paths) |
| MOT-STAGGER | 60–150 ms, only for order | Recipe defaults 120–140 | validator (limit), critic |
| MOT-MOVERS | ≤ 4 independent movers per click | Draft builds one idea per click | critic (identical paths count once) |
| MOT-CLICKS | ≤ 6 clicks per slide | Draft caps lists and tours | critic |
| MOT-VOCAB | 3–10 effect kinds per deck | Styles; cinematic adds secondary layers | critic |
| MOT-STATIC | ≤ 30 % static content slides | `auto` | critic |
| MOT-AMBIENT | Loops cycle ≥ 6 s, never on the focus | Ambient recipes; `motion_engine.conflicts` blocks loops on animated properties | critic, engine |
| MOT-TITLE | Titles still inside a slide | Draft never targets titles | critic (note) |
| MOT-SETTLE | End on the authored layout before Morph | Script layer adds a release click | `morph_studio.settle_report`, critic |
| MOT-OVERSHOOT | Overshoot ≤ 0.08, anticipation ≤ 0.05 | Engine clamps | validator |
| COL-TEXT | WCAG text contrast | Forge themes, `brand_palette`; the highlighter tint is sized so the text keeps its contrast | `forge_qa`, critic (inherited colours and alpha tints resolved) |
| COL-GRAPHIC | Helpers ≥ 3:1 against what is behind | `deck_style(model, background)` picks or moves the accent | critic |
| TYP-* | Scale, body size, ratio, families | Forge themes | `forge_qa`, critic (inherited sizes resolved) |
| DEN-WORDS | ≤ 45 words is good | Forge spec limits | critic |
| LAY-* | Safe area, settled-frame density and balance | Forge layouts, Morph staging | `forge_qa`, critic (`--render`) |
| TEC-SCHEMA | Valid ISO 29500 PresentationML | Writer | critic (`--xsd`) |
| TEC-PRESET | Named PowerPoint presets | `ppt:` library | critic (note) |

## Using it

```bash
python3 scripts/design_system.py                     # print tokens, roles, rules
python3 scripts/design_critic.py deck.pptx --md critique.md
python3 scripts/design_critic.py deck.pptx --render lo        # + frame metrics (LibreOffice)
python3 scripts/design_critic.py deck.pptx --render render/   # + PowerPoint strips (slide_forge render)
python3 scripts/motion_director.py critique deck.pptx         # same, from the director CLI
```

`motion_director.py apply|auto` adds a *Design critique* section to its report:
source vs output scores and open warnings, with the critique JSON written next
to the output (`--no-critique` skips it). `slide_forge.py build` puts the
critique into its verdict (advisory; QA errors still decide `ok`).
`morph_studio.py apply` adds scores to its report.

Scores (1–5 per dimension) summarise the checks. Deck-level and slide-level
checks weigh equally, so a static or monotone deck cannot hide behind many
passing slides. Scores are **not** calibrated human ratings; act on the
findings.

## Changing the system

1. Change a value in `knowledge/design_system.json` together with its
   evidence (add the source to `sources`).
2. Run `python3 -m unittest tests.test_design_system`. It checks that bands
   are ordered, rules cite known sources, and the director's output passes
   the rules it generates for.
3. Re-run `experiments/T034-20261019-claude-design-system/run_eval.py` to see
   the effect on the corpus.

Do not hard-code a new duration, easing or contrast threshold in a generator.
Add or read a token instead.

## Limits

- **No playback evidence.** Rendered frames come from LibreOffice and match
  PowerPoint's own CreateVideo frames closely on one 10-slide deck. The
  median background-share difference is 0.022, with a rank correlation of
  0.99. Timing and Morph have not been observed in PowerPoint.
- **Estimated measurements.**
  - Colours are resolved from theme, colour map, placeholder and master
    styles, but gradients and pictures behind text are skipped.
  - The word count splits on spaces, so it counts Vietnamese syllables and
    over-counts words.
- **Some bands are judgement.** Several bands are judgement calls anchored to
  design-system tokens and corpus numbers, not experimental optima, and
  `sources` says which. A user study would be the next step.
