# Frozen brief: native QA evidence integrity

Frozen: 2026-10-05 UTC. Main base: 405c170a8512b02f2f98b73b50788e24d6760aac.
Baseline harness: a00ea0391259985257853f19f36af37a2929adb6.

## Question

Can truncated, inconsistent or failed COM evidence receive a native click pass?
Use synthetic evidence for two animated slides, with two and one click groups.
The artifacts and all expected target names are fixed. This tests the evidence
verifier, not PowerPoint or visual quality.

## Frozen acceptance

- A complete synthetic positive control passes parse/click record checks.
- Parse-only evidence can pass parse checks but never click execution.
- Incomplete, duplicated, reordered or inconsistent click records fail.
- Missing/failed slideshow completion and nonempty probe errors fail click claims.
- Invalid/empty manifest, hash, types and application identity fail safely.
- Native click indices do not establish animation completion, stable-state
  appearance, editability or full playback. Those claims stay false.
- Record baseline and candidate results for every case, including crashes.
- Run the full existing unit suite. Keep effect writers and PPTXs unchanged.

## Scope

Own this experiment, verifier, regression tests and T018 handoff. Inherit the
unfinished harness on a separate branch. Do not overwrite its original branch.
PowerPoint is unavailable here. No source skill promotion, effect gallery
expansion, paid service or self-hosted runner installation is part of this study.
