# Design critique: coffee_office_dynamic.pptx

Design system 1.1.0 · 236 checks · note 3, warn 3

| design | motion | rhythm | coherence | overall |
|---|---|---|---|---|
| 5.0 | 5.0 | 4.42 | 3.0 | 4.36 |

## Warnings

- **MOT-SETTLE** slide 1 `Hero picture`: [['moved', 'scaled']] (expected authored layout before Morph)  → end the slide on its full picture (release click) before Morph
- **MOT-SETTLE** slide 6 `Supporting picture`: [['moved', 'scaled']] (expected authored layout before Morph)  → end the slide on its full picture (release click) before Morph
- **TYP-SIZES** deck: 14 (expected [3, 6]) sizes [14, 15, 18, 20, 24, 28, 30, 36, 40, 46, 48, 53, 54, 110] → use the theme scale: 3-6 sizes per deck

## Notes

- **MOT-EFFECTS** slide 7: 9 (expected [0, 8])  → fewer simultaneous effects per click
- **DUA-BREAK** deck: 0 (expected >= 1 pattern break for 5+ slide decks) monotonous rhythm: insert a pattern break near 1/3 or 2/3 deck position → insert high-whitespace pattern break slides near 1/3 and 2/3 deck milestones to prevent audience fatigue
- **MOT-VOCAB** deck: 12 (expected [3, 10]) appear, appear-out, wipe, faded-zoom, transparency, grow-shrink, path:0, expand → one motion language: a style with 3-10 effect kinds
