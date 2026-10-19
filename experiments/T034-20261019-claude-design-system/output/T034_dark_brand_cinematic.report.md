# Motion Director report

- source sha256: `11e979da6863709d4ce5df60d28d4c33a7b1cf50818f72230dc8e53c006d3fa9`
- output sha256: `f8ce4bbf9f305a9a5239e69a78129aa84bf39e49bc04049c87d2b33d75401c01`
- structural checks: PASS
- PowerPoint playback: **not verified** (structural + simulated states only)

## Slides
### Slide 1
1 click group(s)
- auto 1: +Section accent

### Slide 2
4 click group(s); enters with Morph transition
- auto 1: +Title accent
- click 2: +KPI card 1, +KPI value 1, +KPI label 1
- click 3: +KPI card 2, +KPI value 2, +KPI label 2
- click 4: +KPI card 3, +KPI value 3, +KPI label 3

### Slide 3
7 click group(s); enters with Morph transition; generated: __gen_orbit-ring_orbit, __gen_halo_halo
- auto 1: +Title accent
- click 2: +__gen_orbit-ring_orbit, +Stage 2, ~Stage 2 (move), +Stage 3, ~Stage 3 (move), +Stage 4, ~Stage 4 (move), +Stage 1, ~Stage 1 (move), ~__gen_orbit-ring_orbit (emphasis)
- click 3: ~Stage 2 (emphasis), ~Stage 3 (emphasis), ~Stage 4 (emphasis), ~Stage 1 (emphasis), +__gen_halo_halo, ~__gen_halo_halo (emphasis)
- click 4: ~Stage 3 (emphasis), ~Stage 2 (emphasis), ~__gen_halo_halo (move)
- click 5: ~Stage 4 (emphasis), ~Stage 3 (emphasis), ~__gen_halo_halo (move)
- click 6: ~Stage 1 (emphasis), ~Stage 4 (emphasis), ~__gen_halo_halo (move)
- click 7: ~Stage 2 (emphasis), ~Stage 3 (emphasis), ~Stage 4 (emphasis), ~Stage 1 (emphasis), −__gen_halo_halo

### Slide 4
5 click group(s); enters with Morph transition; generated: __gen_track-line_track, __gen_token_token
- auto 1: +Title accent
- click 2: +Step 1, +__gen_track-line_track, +__gen_token_token, ~__gen_token_token (move), ~Step 1 (emphasis)
- click 3: +Link 1, +Step 2, ~__gen_token_token (move), ~Step 2 (emphasis)
- click 4: +Link 2, +Step 3, ~__gen_token_token (move), ~Step 3 (emphasis)
- click 5: +Link 3, +Step 4, ~__gen_token_token (move), ~Step 4 (emphasis)

### Slide 5
2 click group(s); enters with Morph transition
- auto 1: +Statement bar
- click 2: +Statement


## Design critique (design system 1.0.0)

| | design | motion | rhythm | coherence | overall |
|---|---|---|---|---|---|
| source | 5.0 | – | 1.0 | 4.0 | 3.33 |
| output | 5.0 | 5.0 | 4.92 | 4.33 | 4.81 |

Open warnings (rule → fix):
- MOT-SETTLE slide 4 __gen_token_token: [['moved']] (expected authored layout before Morph) → end the slide on its full picture (release click) before Morph

Scores summarise computed checks (docs/DESIGN_SYSTEM.md); they are not a human rating.
