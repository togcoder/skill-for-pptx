# Product Target — Existing Deck Motion Director

This document defines the destination of PPTX Motion Lab. It is the product goal
future models must optimize toward.

## Destination

The system should accept an **existing PowerPoint file** and turn it into a
coherent, editable, motion-directed presentation without requiring the user to
manually specify every animation.

The desired end state is not "generate a pretty deck" and not "one prompt = one
effect". It is an **AI Motion Director for PowerPoint**.

Given a PPTX, the AI should:

1. understand the report/story already present in the deck;
2. identify the visual resources that already exist and preserve them whenever
   practical;
3. find an existing motion/narration script if the user supplied one or if it is
   embedded in notes/briefs;
4. if no usable script exists, infer the intended reporting sequence from the
   deck itself and, when useful and allowed, research the subject/report pattern
   to create a motion script;
5. decide what should appear first, what should be emphasized, compared,
   decomposed, connected, revealed, or summarized;
6. add native PowerPoint motion to the existing slide resources;
7. create missing visual components only when the story cannot be expressed well
   with the current resources;
8. create those additions **inside the existing design language and layout
   framework**, not as unrelated decorations;
9. pack as many motions as feasible into the same slide when they reuse the same
   resources;
10. preserve editability and verify the exact final PPTX in PowerPoint before
    claiming native playback.

## Script priority

Use the strongest available source in this order:

1. explicit user-provided script / storyboard / animation instructions;
2. speaker notes or report script already associated with the deck;
3. existing native animation / transition choreography already authored in the deck;
4. explicit narrative structure visible in slide titles, order, callouts,
   diagrams, tables, charts and hierarchy;
5. inferred reporting sequence from the full deck;
6. external research on the report/story pattern when the deck is incomplete and
   external research is appropriate and permitted.

Existing animation is first-class evidence. Inventory and interpret it before
editing. Unless a stronger script explicitly overrides it, preserve the existing
choreography and extend or repair it instead of replacing the slide with a fresh
timing tree.

Never silently override an explicit script with a prettier inferred story.

## When there is no script

The AI must not simply animate every object.

It should first build a **report sequence**:

- What is the opening state?
- What question/problem is introduced?
- What evidence is revealed?
- What comparison or causal relationship matters?
- Where should attention move next?
- What is the conclusion/action?
- Which slides are scenes and which motions belong inside each scene?

The resulting motion should reveal meaning. Motion is not decoration.

## Missing components

A component may be created when all of the following are true:

- the narrative requires a visual role that the existing slide cannot provide;
- no existing resource can reasonably be reused;
- the addition can be made native/editable where practical;
- it respects the deck's visual system: typography, spacing, palette, geometry,
  density and visual hierarchy;
- it does not contradict the report's data provenance.

Examples: an emphasis ring, connector, step label, temporary comparison card,
mask/reveal surface, focus frame, small diagram part, or a derived visual proxy.

Do not manufacture unsupported business/factory data just to make an animation
look complete.

## Existing-slide policy

Default: **preserve the existing slide count and slide order**.

Create a new slide only when:

- the user explicitly asks for one;
- a genuine semantic scene is missing;
- PowerPoint imposes a verified limitation that cannot be solved with a same-slide
  native timeline;
- the report becomes materially clearer and the user goal permits structural
  editing.

"One animation needs one slide" is never a valid reason.

## Preservation policy

Before editing, inventory the source deck and freeze:

- source SHA-256;
- slide order and count;
- slide size;
- object names/IDs/types;
- text;
- media relationships;
- charts/tables when identifiable;
- existing transitions/timing;
- speaker notes where available;
- theme/master/layout references where available.

Classify planned changes as:

- `preserve`
- `animate`
- `reposition`
- `restyle-minimally`
- `create-component`
- `replace-only-with-explicit-justification`

The default for user content is `preserve`.

## Motion architecture

A slide is a semantic scene/execution container.

For each slide:

- keep the existing resources;
- build a local motion script;
- pack multiple motion events into native timing tracks;
- reuse the same semantic object identities across the timeline;
- create only the minimum additions required by the script.

Across slides:

- use slide boundaries for real narrative/scene changes;
- use Morph only when it is the appropriate cross-slide mechanism;
- do not convert same-slide motion into waypoint slides.

## North-star autonomy contract

The normal product input may be only one existing PPTX plus an optional high-level
goal. The AI must not require the user to specify object-by-object animations.

It should autonomously discover or create the report script, decide the sequence,
reuse existing resources, identify resource gaps, synthesize only the missing
components, choreograph the deck and verify the result.

Ask the user only when a missing decision could materially change facts,
permissions, branding constraints or the intended conclusion. Missing low-level
animation instructions are not a reason to stop.

The ideal output should still feel like the user's original deck—same report,
same evidence and same visual identity—but professionally motion-directed.

## Existing-motion continuation

When the source deck already contains animation:

1. parse existing timing targets, effect types and start conditions;
2. map effects back to the source objects;
3. treat the current animation sequence as director context;
4. preserve it by default;
5. add, extend or repair only what the chosen script requires;
6. never reject an animated deck merely because native timing already exists.

A "fresh timing only" patcher is a research-backend limitation, not an acceptable
product limitation.

## Desired autonomous workflow

Input:
- existing PPTX;
- optional user instruction;
- optional script/storyboard/reference;
- optional constraints (do not change layout, preserve branding, etc.).

System:

`INGEST -> UNDERSTAND -> SCRIPT -> RESOURCE GAP -> CHOREOGRAPH -> BUILD ->
VERIFY -> CRITIQUE -> REPAIR -> EXPORT`

### INGEST
Read the PPTX package and build a deck inventory.

### UNDERSTAND
Infer slide roles, report flow, visual hierarchy, object relationships and
important evidence.

### SCRIPT
Use the supplied script if present. Otherwise create a concise report/motion
script grounded in the deck and, if needed, external research.

### RESOURCE GAP
For every planned beat, decide whether an existing object can perform the role.
Create a component only for genuine gaps.

### CHOREOGRAPH
Translate the script into native per-slide timeline actions. Apply
`docs/MOTION_PACKING.md`.

### BUILD
Patch or rebuild only what is necessary. Preserve source content and design
identity.

### VERIFY
Check source-vs-output preservation, package structure, timing targets and final
visual states. Playback claims require the exact output in Microsoft PowerPoint.

### CRITIQUE
Ask whether every movement reveals meaning, whether the deck still feels like
the original deck, and whether unnecessary generated components were introduced.

### REPAIR
Fix failed conditions without discarding the user's deck or inflating slide
count.

### EXPORT
Return an editable PPTX plus evidence/report of what changed.

## Success criteria

The product is successful when a user can provide an ordinary existing report
and the AI can, with little or no animation-specific instruction:

- understand the intended presentation sequence;
- create a defensible motion script;
- reuse the deck's real resources;
- generate missing components only when necessary;
- add meaningful native motion with minimal slide expansion;
- keep the result editable;
- explain the changes;
- and produce an exact-file PowerPoint-verified result.

That is the destination. Individual recipes, Morph experiments, path writers and
QCC examples are implementation steps toward it, not the product itself.
