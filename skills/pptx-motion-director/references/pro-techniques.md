# Professional PowerPoint motion techniques — catalog for the director

The craft seen in motion-design tutorials, codified. For each technique: when it
earns its place, and how to get it here. Status: **here** = implemented in this
repository's director tools; **branch** = implemented on the parallel Claude
branch (T024 picture motion / T025 Slide Forge / T027 preset library, not yet
merged); **manual** = plan it by hand with the generic tools.

Pipeline: (1) `motion_director.py` for in-slide motion (script → clicks →
choreography), then (2) `morph_studio.py` for cross-slide Morph. Morph staging
skips objects that already animate, and the director keeps Morph scene slides
static.

## A. Morph — motion between slides

| # | Technique | Use when | How |
|---|---|---|---|
| 1 | Forced pairing with `!!name` | Two different objects are "the same thing" (card → header, icon → hero) | here: `morph_studio continuity` pairs automatically; add `pairs:[["A","B"]]` for custom |
| 2 | Title glide | Consecutive slides: the title moves/resizes instead of cutting | here: titles pair title→title; `byWord` when the titles share words |
| 3 | Off-slide staging | New objects should fly in, leaving ones fly out, instead of fading | here: `stage:true` (only for objects without their own animation) |
| 4 | Camera push-in / pull-back | Drill into one part of a diagram, matrix, map or photo | here: scene `camera-zoom` (text sizes, lines and neighbours scale like a real camera) |
| 5 | Card expands into a panel | A summary card opens into its detail | here: scene `card-expand` (grows over its neighbours, even margins; leaves as one piece) |
| 6 | Carousel / pan | A long row, timeline or gallery, one item per beat | here: scene `pan` |
| 7 | Letter shuffle | A word turns into another word | here: continuity `option:"byChar"` |
| 8 | Picture becomes thumbnail | A photo moves aside to make room for text | here: same picture pairs automatically |
| 9 | Same text, new emphasis | A number or phrase grows to become the hero of the next slide | here: same-text pairing |
| 10 | Colour morph | The same shape changes colour to signal state (red → green) | here: pair the shapes; Morph interpolates fill |
| 11 | Background orbs | Ambient shapes drift between every slide | branch: Slide Forge `!!orb` |
| 12 | Zoom-out reveal | Start close on a detail, pull back to show the whole | manual: put the `camera-zoom` slide before its source |
| 13 | Parallax | Layers move different distances across slides | manual: duplicate and offset layers by depth |
| 14 | Rotation morph | A wheel/hub turns between slides | manual: duplicate, rotate the group, pair by `!!` |

## B. Entrances and text

| # | Technique | Use when | How |
|---|---|---|---|
| 15 | Typewriter | A quote, a headline or a command line | here: `effect:"type-on"` (Appear by letter, 35 ms) |
| 16 | Word by word | A punchy one-line message | here: `by:"word"` on any entrance |
| 17 | Rise from a line | Headline or takeaway emerges cleanly | here: recipe `rise` + `mask` component (sits under the last text line, painted in the colour behind; refuses if it would cover something) |
| 18 | Highlighter sweep | The one sentence to remember | here: `highlight` component + `wipe-right`; cinematic adds it to conclusions |
| 19 | Underline draws | Section labels, key terms | here: `underline` component + `wipe-right`; cinematic adds it to labels |
| 20 | Bullets one per click | Presenter-paced lists | here: `text-build` |
| 21 | Stagger cascade | Groups of similar items | here: `stagger-reveal`, `assemble` (80–150 ms offsets) |
| 22 | Count-up | A hero metric | here: `--counters` (proxy text; note edit-view clutter) |
| 23 | Chart builds | Series/category storytelling | here: chart `data_motion` |
| 24 | Line draw | Connectors and arrows | here: connector reveals use `wipe` in the line's direction |
| 25 | Any native preset (Boomerang, Pinwheel, Grow With Color, S-curve…) | When a specific classic effect is asked for | branch: T027 `ppt:<name>` (198 presets harvested from PowerPoint) |

## C. Focus and compound motion

| # | Technique | Use when | How |
|---|---|---|---|
| 26 | Spotlight + dim | Walking through parts of one diagram | here: `spotlight` |
| 27 | Halo follows focus | Make the walk-through feel guided | here: `halo` component (`motion_parameters.halo`) |
| 28 | Pulse / ripple | Acknowledge, connect related items | here: `focus`, `ripple` |
| 29 | Drill-down in slide | Zoom into one card and back without new slides | here: `zoom-focus` → `release` |
| 30 | Swap / re-rank | Priorities change, before/after | here: `swap` |
| 31 | Cycle turn | Processes that repeat | here: `cycle` |
| 32 | Token journey | Follow one item through a process | here: `travel` + `track-line`/`token` (or the deck's own marker) |
| 33 | Overshoot / anticipation | Make moves feel physical | here: keyframe `overshoot` ≤ 0.08, `anticipate` ≤ 0.05 |
| 34 | Followers | A label must travel with its shape | here: `attach:{"Shape":["Label"]}` |
| 35 | Assemble / disperse | A system forms or breaks apart | here: `assemble`, `disperse` |

## D. Ambient layer

| # | Technique | Use when | How |
|---|---|---|---|
| 36 | Orbit ring turning | Cycles | here: `orbit-ring` + `spin-loop` (cinematic default) |
| 37 | Breathing hero | One element should feel alive while talked about | here: `breathe` |
| 38 | Drifting backdrop | Depth on content-light slides | here: `--ambient` (backdrop + `drift`) |
| 39 | Ken Burns | Photos | branch: T024 picture motion |
| 40 | Idle float | Icons, illustrations | branch: `float` recipe |

## E. Craft rules (what makes it look professional)

41. **Timing**: entrances 300–600 ms; camera Morph 1.2–1.6 s; ambient loops 8–40 s.
    Nothing important faster than 250 ms or slower than 1.6 s.
42. **Easing**: smooth start/end on moves; ease-out on arrivals; overshoot small.
43. **Direction language**: things enter from where they will live and leave
    the way they are going; keep one direction logic per deck.
44. **Rhythm**: one idea per click, ≤ 6 clicks per slide; group what belongs
    together with with-previous, chain with after-previous.
45. **Still anchors**: titles stay still inside a slide; they move only by Morph.
    **Settle before Morph**: a slide that leaves by Morph ends on its authored
    layout (release spotlights, fade helpers), or its objects snap back when
    the transition starts — `morph_studio apply` reports `unsettled` slides.
46. **Meaning first**: decoration does not move unless it is ambient and slow.
47. **Ambient restraint**: slow, low contrast, never on the object being
    discussed (the tools block a second motion on a looping property).
48. **Land the conclusion**: evidence first, then the takeaway with a secondary
    accent (highlight, underline, rise).
49. **Reuse before you generate**: move the deck's own objects; generate a
    component only with a role, in the deck's colours and font.
50. **Scenes cost slides**: each Morph scene slide needs a reason; originals stay
    untouched (only `!!` names and off-slide staging copies are added).
