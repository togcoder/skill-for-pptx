# T004 — Portability outside ChatGPT Work

Status: queued. Owner: unassigned. Check open claims/PRs before starting.

Problem: renderer depends on host-owned artifact-tool and Presentations helpers.
Another model can analyze plans and packages but may lack the same authoring path.

Deliver: capability comparison, dependency/license review from primary sources,
and an isolated backend adapter implementing the existing plan contract. Preserve
the Work backend as reference. Reject unsupported fields explicitly.

Accept: parity on native object types, names, text, slide order, transition XML
and rendering on at least two existing plans plus one unseen brief. Record
differences and limits. Do not claim native animation parity without PowerPoint
playback. Do not replace the main backend based solely on tests that mirror code.
