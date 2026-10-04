# Plan paths as well as endpoints

Do not approve a moving-label composition from endpoint screenshots alone.
When two objects exchange slots at the same time, their labels can cross even
though both endpoint slides are clear. Inspect the semantic path and preserve
such failures as separate evidence.

For three modes taking focus in turn, consider a cyclic route over three
noncollinear slots. Example at 1280×720: center (640,320), left (220,520), right
(1060,520). Use slot orders [B,A,C] → [C,B,A] → [A,C,B]; label and carrier share
the same center. These coordinates are one tested composition, not defaults
for every aspect ratio, text length or object size. Recheck after changing them.

E003 compares this route with H002 reciprocal swaps. The same diagnostic found
two label-pair overlap intervals in H002 and zero in E003, with 200×64 label
boxes. Run from project root:

```bash
python3 experiments/E003/path_diagnostic.py PLAN.json read-label relax-label create-label
```

Adapt the selected IDs to the plan. The diagnostic intersects continuous
linear rectangle-overlap inequalities; it rejects rotated selected boxes.
It assumes synchronized linear interpolation of positions and dimensions.
It does not implement PowerPoint easing, timing, text morph, ring occlusion,
glyph shapes or native playback. A clean result is a design check, not a motion
pass. Keep native motion scores null until actual playback is recorded.

Three slides show three focus poses but only two transitions. If every mode
must visibly grow from an initial overview, reserve an overview state or use
a supported within-slide animation backend. Do not silently add slides to a
fixed count or promise an entrance that the backend does not implement.

## Long labels on a symmetric triangle

H003 reused the E003 slots with 360×96 px Vietnamese labels. The same frozen
diagnostic found 4 label-pair overlap intervals across two transitions. E004
changed only block/label vertical positions: focus y=260, side y=560. Label
overlaps fell to 0; text, dimensions, font and duration stayed unchanged.
All six final endpoint slides were inspected. Both decks still have 6 carrier
overlap pairs in the separate geometric diagnostic. Do not describe E004 as
a collision-free composition or a verified native animation.

For three equal, constant-size, unrotated labels on slots (-d,H), (0,0), (d,H)
under the cyclic orders above and synchronized linear motion, the positive-area
overlap-free bound is:

`H >= 3*d*h / (2*d-w)`, provided `0 < w <= d`.

Here w/h are label-box width/height, d is half the left-to-right span and H is
the vertical gap. Two diagonal routes keep horizontal separation d. A label
crossing the bottom has relative horizontal separation `2*d-3*d*t` and
vertical separation `H*t` from the incoming diagonal route. Its horizontal
overlap starts at `(2*d-w)/(3*d)`; keeping vertical overlap's end `h/H` no later
gives the bound. The outgoing route is symmetric in `1-t`. Exact edge contact
has zero area; leave extra space for strokes, layout uncertainty and perception.

```bash
python3 scripts/cyclic_label_clearance.py --half-span 420 --width 360 --height 96 --gap 300
```

For this example the model requires at least 252 px; E004 uses 300 px. Reject
the helper's assumptions if sizes differ, resize during motion, rotate, use
different slots or more/fewer objects. Run the continuous plan diagnostic for
the actual geometry instead. If width exceeds d, changing only H cannot remove
the two diagonal labels' overlap. Do not fix this by clipping or silently
shortening required content. Recompose the slots or change the motion sequence
within the requested slide count. Check carrier paths as a separate concern.

This is an algebraic design aid, cross-checked with the frozen E003 interval
diagnostic. It does not model PowerPoint easing, glyphs, stroke occlusion or
native playback. Preserve that distinction in every result.

## Tight carriers after label clearance

When label paths pass but larger background carriers still intersect, measure
the carriers separately before changing the route. First center a carrier with
small, explicit padding around the unchanged label. Keep enough size contrast
to communicate focus, then rerun both label and carrier diagnostics and review
the static emphasis. T002 held E004's 360×96 px labels and positions fixed;
changing only carrier frames from 480×200 / 400×150 to 404×112 / 372×104 px
kept label overlaps at 0/6 and reduced carrier overlaps from 6/6 to 0/6 in the
same proxy. Focus emphasis fell from subjective 4/5 to 3/5. Treat those sizes as
one measured case, not defaults. Do not shrink below readable padding, clip
required text or infer native playback from a clean box calculation.
