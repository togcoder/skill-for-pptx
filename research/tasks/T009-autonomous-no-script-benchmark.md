# T009 — Autonomous No-Script Existing-Deck Benchmark

Status: queued. This is the north-star benchmark for the product destination.

## User condition

Input may be only:

- one ordinary existing PPTX; and
- optionally one high-level goal such as "make this report present clearly".

No object-by-object animation script is supplied.

The model must not ask the user to micro-direct animation unless a missing
decision could materially change facts, permissions, branding or the intended
conclusion.

## Benchmark arms

Run the same 3–10 slide deck through three conditions:

### A — Explicit script

Provide a frozen human script. Measure whether the system follows it without
overriding it with a preferred inferred story.

### B — Notes / existing timing

Hide the explicit script. Allow speaker notes and current animation choreography.
Measure whether those stronger source signals are recognized and preserved.

### C — No script

Hide the script and notes. The model must infer the report sequence from the deck.
If the deck is genuinely incomplete, external research may be used for reporting
structure, not to invent user data.

## Required outputs

For each arm:

1. source deck inventory + SHA-256;
2. script source and evidence;
3. deck-level narrative sequence;
4. per-slide objective, ordered motion beats, and explicit presenter click-beat grouping;
5. resource reuse map;
6. resource-gap list;
7. any generated components with narrative rationale, style basis and provenance;
8. native motion plan;
9. edited PPTX;
10. preservation report;
11. exact-file PowerPoint playback evidence.

## Evaluation

Score separately; do not collapse into one vague quality score:

- script fidelity;
- narrative coherence;
- factual/data preservation;
- source-resource reuse rate;
- unnecessary-component count;
- generated-component design-system fit;
- motion meaningfulness;
- click-boundary quality: each click advances one coherent audience idea;
- stable-state quality: useful explanatory states pause for presenter control;
- continuity quality: no unnecessary click interrupts one continuous action;
- premature-reveal count: content exposed before its narrative beat;
- same-slide packing efficiency;
- untouched-content preservation;
- editability;
- native PowerPoint playback correctness.

The no-script arm fails if it simply animates objects in z-order without first
constructing a defensible report sequence. It also fails if it collapses the
whole slide into one autoplay chain or creates a click for every individual
motion without narrative justification.

## North-star success

A user can drop in a real report and receive back the same report, now
professionally motion-directed, without having to explain how PowerPoint
animation works or specify every effect.
