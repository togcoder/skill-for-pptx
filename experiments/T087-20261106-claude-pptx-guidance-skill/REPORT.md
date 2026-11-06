# T087 [pptx] One PPTX skill written as design guidance; code only as a small toolbox

- **Agent / model:** Claude (Opus 5.5), lead. **Date:** 2026-11-06.
- **Branch:** `work/T087-claude-pptx-guidance-skill`.
- **Addresses:** F15 (a skill is written guidance), F18 (one Opus pass, no trial loops), F19 (help
  small agents), and the owner's points on Opus's QCC review: identity, layouts, Morph rule.

## Open first

- **Deck:** `artifacts/demo-triet-hoc.pptx`, 5 slides.
  - Open it in PowerPoint and go from slide 1 to slide 2: the three portraits slide from the
    cover into a row on the timeline.
  - Slide 2: three clicks, one per landmark.
  - Slide 3: the first click shows both answers; the second underlines the chosen one and gives
    the conclusion.
- **Skill:** `skills/pptx/SKILL.md`.

## What was built

| Part | What |
|---|---|
| `skills/pptx/SKILL.md` | Working order (8 steps, static before motion); ten don'ts, each from a failure seen in this project; the narrow path for small models; hand-over format |
| `guides/1`–`9` | Audience and title outline; identity taken from what the user already has; layout from five principles and the role of the slide (no layout catalogue); type and colour scale; images, QCC diagrams, charts; in-slide motion from the verb being said; Morph (when, seven moves, eight measured rules); self-check loop; toolbox |
| `examples.md` | Which T066 slides to copy and which not to; outside sources, learn the idea only |
| `scripts/pptx_tools.py` | `look` (PowerPoint PNG export + contact sheet) and `motion` (plan by shape names → clicks, Morph/Fade/none). It refuses an entrance on a `!!` actor of a Morph slide (T074 M-07) |

## How the owner's three questions were answered

- **"An identity kit is work for a human."** The skill builds inside the user's own template or old
  deck. Without one, it picks a style by audience. It never invents a logo or decoration.
- **"Layouts are endless, I cannot design them all."** No catalogue. A layout follows from about ten
  slide roles plus five principles. Domain diagrams (QCC) get a short drawing recipe, added when
  first met. Small models copy approved example slides.
- **"Morph rule: cover, section in/out, closing; elsewhere Fade."** Adopted, generalised as "Morph
  only when the same object continues", with seven worthwhile moves and the measured rules.

## Root cause found on the way

Running the Director on the Sonnet v3 theme deck gave 14 Morph transitions, each with the reason
"`!!orb-1`, `!!orb-2` moves". Slide Forge puts two decorative `!!orb` circles on every slide when
`motion.morph` is on (the default). The Director reads them as continuity. Guide 7 rule 5 and guide
9 tell agents to avoid this; the fix in code is briefed as T089.

## Evidence

| Claim | Evidence | Rung |
|---|---|---|
| `motion` writes valid timing | 4 unit tests; PowerPoint COM reads back fade (10), float-in, wipe (22), zoom, Morph EntryEffect 3954, Fade 3849 | 1, 4 |
| The demo's Morph is continuous | PowerPoint `CreateVideo`, frames at 1.5–3.6 s: portraits travel from the cover cluster to the row (`preview/morph-cover-to-timeline.jpg`) | 5 |
| The self-check loop catches real faults | `look` showed a gold line through a word (slide 3) and a top-heavy quote (slide 4); `design_critic` found gold on cream (contrast) and 12 type sizes. All four fixed. | 5, 1 |
| Morph audit clean | `morph_studio.py audit`: no findings | 4 |
| The skill helps a *small* model | **not yet measured**: T090 | — |

## Limits

- **The demo was built by the skill's author.** It shows that the guidance can be followed. It
  does not show that a small model can follow it (T090).
- **`look` shows each slide fully built, not its state at t=0.** The guide tells the agent to
  reason about t=0 from its plan.
- **`pptx_tools motion` has four entrance effects and no slow zoom or dimming.** That is
  deliberate for now: the guide names `motion_director` for a ken-burns effect.
- **The older skills (`slide-forge`, `pptx-motion-director`, `deck-director`) are unchanged.** They
  are now reached only through guide 9.
