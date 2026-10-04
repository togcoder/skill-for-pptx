# T006 — Native timed paths and choreography

Status: queued. Owner: unassigned. Check open PRs/claims before starting.

User priority: advanced effects from a short natural-language prompt that keep
all requested actions and constraints. T005 proves restricted intent/geometry,
but requires many clicks and does not establish impressive animation.

Hypothesis to freeze before implementation: one native timed motion path with
synchronized upright labels can replace orbit waypoint slides while preserving
object identity and intent. Study authoritative OOXML/PowerPoint documentation
and an actual viewed source effect; log which media was observed and its rights.

Work in an isolated backend/experiment. Do not silently change the current
Morph-only renderer or allow add_morph to overwrite existing timing. Preserve
all baselines. Compare a minimal timeline with T005's explicit geometry; then
test a genuinely different compound effect and fresh prompt, not just new node
counts. Define trigger, dependencies, duration, easing, target mapping and end
state explicitly. Separate unsupported visual demands from fallback choices.

Acceptance: structural schema/parity checks, render every final slide, capture
actual PowerPoint playback tied to exact file hash/version, assess intermediate
overlap, pauses, sequence/target fidelity and editability. Without a native
runtime, prepare code/fixtures/capture instructions and keep native acceptance
pending; HTML/video simulations do not replace that gate. A video fallback may
be offered only with its lost editability clearly stated.
