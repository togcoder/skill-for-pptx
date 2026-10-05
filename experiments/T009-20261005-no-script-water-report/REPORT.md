# T009 — No-script motion on an unseen 10-slide report

Date: 2026-10-05 UTC. Benchmark arm: **C — no script**.

## Result

A single high-level Vietnamese instruction was sufficient to produce a defensible narrative and native timing plan on a 10-slide report outside the QCC domain. The planner used only the deck and this instruction:

> Làm bài thuyết trình này rõ ràng, mạch lạc và có chuyển động chuyên nghiệp.

It inferred the sequence title → opening options → definition → situation → causes → consequences → rebuttal → individual solutions → system solutions → conclusion options. Paired alternatives on slides 2 and 10 receive separate presenter clicks; headings and supporting paragraphs inside one alternative continue automatically within that click.

The compiled candidate contains **12 presenter clicks and 21 native stages on the original 10 slides**. All 21 animated targets are existing editable shapes. No helper component was generated.

## Input isolation

The source was a user-owned Library deck not used in previous motion experiments. The source PPTX itself is not copied as a separate fixture. The experiment freezes its SHA-256, derived inventory, high-level instruction and inferred plan. No object-by-object animation script, speaker notes, current timing or transition was available.

## Package defect found and repaired

The unedited source already failed the host integrity check because `[Content_Types].xml` named nine slide-master parts absent from the ZIP. The raw motion candidate inherited the same nine findings.

A narrow reusable repair now removes only stale `Override` entries whose exact part is absent. It changed only `[Content_Types].xml`; it did not create or remove slides, layouts, media or relationships. Findings went **9 → 0**. This is source hygiene, not playback evidence.

## Preservation and static review

- source/output slides: 10 / 10;
- source shapes: 31; text/geometry differences: 0;
- unexpected changed package members: 0;
- changed members: ten slide XML parts for timing plus `[Content_Types].xml` for the documented repair;
- finalizer: package, layout, reference-font and first-party import checks pass;
- all ten final slides were inspected individually; all ten renders are pixel-identical to the source.

Static equality is expected because the experiment adds timing rather than changing the authored layout. It does not show hidden/start states or animation playback.

## Evaluation

Measured facts and subjective ratings are separate in `evaluation.json`. Narrative coherence, click boundaries and stable states score 4/5 subjectively. Motion meaningfulness scores 3/5 because each dense paragraph is one source shape; splitting paragraphs would require content restructuring and was rejected for this preservation-first arm.

Script fidelity is not scored because arm C has no supplied script. Native PowerPoint correctness remains null.

## Reusable skill change

The source skill now requires a pre-edit package-integrity baseline. It distinguishes inherited defects from patch defects and permits only the proven stale-content-type repair. The Director contract remains grounded in the original source hash.

## Evidence boundary and next step

**152 unit tests pass**. Director validation, deterministic recompilation, finalizer checks and static comparison pass. Microsoft PowerPoint was unavailable, so the exact final hash `6e18e4f208784a8b379b2afecd627bb3ff4e2994f6802c1301bb28a793e51727` has no playback claim.

Next: play this exact file in PowerPoint through all 12 clicks and record whether each entrance hides the object until its beat, whether automatic stages stay inside one click, and whether slides 2/10 pause between alternatives. Arms A and B remain pending on the same frozen deck.
