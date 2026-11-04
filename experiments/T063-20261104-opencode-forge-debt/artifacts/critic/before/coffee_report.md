# Design critique: coffee_report.pptx

Design system 1.1.0 · 243 checks · note 3, warn 3

| design | motion | rhythm | coherence | overall |
|---|---|---|---|---|
| 5.0 | 5.0 | 4.41 | 3.67 | 4.52 |

## Warnings

- **MOT-SETTLE** slide 1 `Hero picture`: [['moved', 'scaled']] (expected authored layout before Morph)  → end the slide on its full picture (release click) before Morph
- **MOT-SETTLE** slide 6 `Supporting picture`: [['moved', 'scaled']] (expected authored layout before Morph)  → end the slide on its full picture (release click) before Morph
- **TYP-SIZES** deck: 15 (expected [3, 6]) sizes [14, 15, 16, 18, 20, 24, 28, 30, 36, 40, 46, 48, 54, 55, 110] → use the theme scale: 3-6 sizes per deck

## Notes

- **MOT-EFFECTS** slide 7: 9 (expected [0, 8])  → fewer simultaneous effects per click
- **MOT-MOVERS** slide 7: 5 (expected [0, 4])  → move fewer things at once; group what moves together
- **DUA-BREAK** deck: 0 (expected >= 1 pattern break for 5+ slide decks) monotonous rhythm: insert a pattern break near 1/3 or 2/3 deck position → insert high-whitespace pattern break slides near 1/3 and 2/3 deck milestones to prevent audience fatigue
