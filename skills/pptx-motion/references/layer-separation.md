# Layer separation (experimental 2D recipe)

Use when a whole is explained through its component layers. Choose 3–5 semantic parts, not arbitrary decoration. Show assembled → separated → reassembled. Keep IDs, colors, ordering and explanatory labels consistent; keep the rail readable while parts move.

Generate a restricted plan with `scripts/layer_separation.py CONFIG.json PLAN.json`, then use the normal validate/build/render workflow. CONFIG accepts:

```json
{
  "title": "Short title",
  "subtitle": "One sentence about the whole",
  "brief": "The user's instruction",
  "layers": [
    {"id":"surface","label":"Surface","role":"What this layer does"},
    {"id":"core","label":"Core","role":"What this layer does"},
    {"id":"foundation","label":"Foundation","role":"What this layer does"}
  ],
  "references": []
}
```

Title maximum 26 characters, subtitle 70, layer label 24, role 38; these limits do not guarantee fit. Inspect every final slide, including accented text. References are URL records. The demonstration data must be identified as synthetic. This generator is a native schematic, not a physical simulation or 3D exploded model. No scaling, rotation, grouping, opacity animation or custom motion path is implemented.

Inspect short numeric IDs too. With the current renderer/font, a 42 px box wrapped a two-digit 23 px label despite passing plan/package checks. The tested repair is a 60 px box, with every other plan field fixed. It removed 15 wrapped instances in the development deck and 12 in a second-topic deck. Do not treat that width as universal across fonts or viewers. Keep separate v1 failure and v2 repair artifacts when changing typography.

Derive each child position from its carrier-local offset in every state. The output contains flat editable objects, not native PowerPoint groups; modifying a layer later requires moving its children too. Separate the explanation rail from children that visually belong to the part. Keep size and rotation constant for this recipe. `binding_metrics(plan)` checks endpoint offsets; under synchronous linear translation, equal relative offsets at both endpoints remain equal between them. This mathematical property does not establish PowerPoint's interpolation.

Evidence: `experiments/T003-20261004-codex-layer01/` uses a deliberately broken binding ablation, not a naturally discovered bug. Child/state violations 16 → 0 across 60 checks; maximum drift 64 → 0 px. This supports the coordinate-generation rule only. See its report for exported deck/static evaluation and transfer results; native playback remains pending. `--ablate-binding` is a research fault fixture and must not be used for user-facing output.

Sources: Microsoft [Morph tips](https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks); Presentation Process [layer diagram tutorial](https://www.presentation-process.com/layer-diagram.html), both accessed 2026-10-04. Only documentation/tutorial text inspected; no external assets copied. The latter describes 3D tiers; this original 2D composition does not implement that extrusion or claim to reproduce an observed animation.
