# Compound intent and radial drill-down

Use this route when the prompt combines expansion, ring rotation, focus,
separation and reassembly. Preserve exact numbers, direction, named targets,
operation order and constraints before choosing a visual recipe.

## Intent procedure

1. Copy the user's prompt unchanged. List every explicit requirement. Record
   design choices separately as assumptions. Never recast a requested full
   revolution as a quarter-turn. "Xoay cả vòng" can mean the whole ring moves;
   "xoay một vòng" means 360 degrees. State the chosen interpretation if ambiguous.
2. Select a supported recipe only if it matches the actions. This compiler
   supports **radial-drilldown** with this fixed order:
   burst, orbit, focus, split, reassemble, restore. Do not rewrite a different
   requested order or substitute a different mechanism to make it pass.
3. Emit an intent JSON with every key below. AI performs the language-to-intent
   translation; the script only validates and compiles structured intent.
4. Check capabilities before export. True 3D, camera perspective, fluid motion,
   organic shapes, continuous custom curves, arbitrary synchronization,
   single-slide timeline and autoplay are unsupported in this recipe. Report the
   mismatch. Propose a new experiment/backend instead of claiming exact delivery.
5. Compile with `python3 scripts/choreography.py INTENT.json PLAN.json`; then
   use the normal plan/export/review workflow. Use fresh output paths.

## Contract

| Key | Value |
| --- | --- |
| version / recipe | `0.1` / `radial-drilldown` |
| prompt | Verbatim short request |
| title | Short subject title, up to 45 characters |
| node_count | Integer 6–12 |
| focus_node | One-based integer within node_count |
| layer_count | Integer 3–5 |
| orbit_degrees | 15–360, positive magnitude |
| orbit_segments | 1–24; use at least ceil(orbit_degrees / 15) for candidate output |
| direction | `clockwise` or `counterclockwise` |
| keep_labels_upright | `true` only |
| operations | `["burst","orbit","focus","split","reassemble","restore"]` |
| requirements | Nonempty list of explicit user requirements |
| assumptions | Nonempty list of choices the user did not specify |

All keys are mandatory; unknown fields fail. Numeric ranges are the tested
layout envelope, not a universal limit of PowerPoint. A low-segment plan is
allowed for diagnostic controls but must not be presented as smooth orbit.
Steps greater than 90 degrees fail compilation because endpoints alone would
not preserve a long rotation's direction or number of turns.

## Native construction and limits

Keep unique persistent `!!` identities. Represent the selected node by the
requested number of tightly adjacent rectangles from the first slide, rather
than pretending one shape can map to several. Compose layer positions from the
node center and scale; keep labels as separate upright textboxes. A core shape
occludes the stacked launch nodes. Preserve object stacking order across states.

Orbit centers follow sampled circle positions, then Morph interpolates between
adjacent states. For radius R and step delta, a **linear geometric proxy** has
maximum radial deviation `R*(1-cos(delta/2))`. More waypoints reduce that proxy,
but do not prove native playback smoothness or continuous angular velocity.
The current deck requires one click per transition. Do not call it an automatic
timeline. The zoom is a node transform, not an actual camera.

Verify explicit requirements against geometry and actual PPTX. Keep semantic
checks, package checks, static inspection and native playback separate. Inspect
every final slide, including waypoint slides. Use a new topic and different
parameters for a fresh-context transfer. A recipe transfer does not establish
arbitrary prompt understanding.
