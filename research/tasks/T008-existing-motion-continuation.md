# T008 — Existing Motion Continuation

Status: queued. Read docs/PRODUCT_TARGET.md and T007 first.

## Goal

Accept an existing PPTX that already contains native animation and extend its
choreography without deleting or blindly replacing the existing timing tree.

This task exists because "source already has timing" is a normal product input,
not an error condition.

## Required workflow

1. Inventory the exact source PPTX and freeze its SHA-256.
2. Extract existing transition/timing summaries and map animation targets back to
   source slide objects.
3. Derive the current choreography in the most faithful order available. Preserve
   raw start conditions when runtime order cannot be proven structurally.
4. Apply the script-priority rules from docs/PRODUCT_TARGET.md.
5. Decide which existing effects are:
   - preserve;
   - extend;
   - retime;
   - replace-with-explicit-justification.
6. Add the minimum new effects/components required by the script.
7. Keep same-resource motion on the same slide.
8. Package without reconstructing unrelated slide content.
9. Verify source-vs-output preservation.
10. Open and play the exact output in Microsoft PowerPoint before claiming success.

## First experiment

Use a source slide containing at least two existing native effects on at least
one source object.

Create two arms:

- **continuation arm**: append one meaningful new beat after the existing sequence;
- **override arm**: an explicit supplied script deliberately changes one existing
  beat, with a recorded reason.

Acceptance:

- existing target/effect inventory is readable before editing;
- unchanged effects remain semantically and structurally present;
- new timing targets the intended source object;
- no new slide is created;
- untouched package parts remain byte-identical where feasible;
- output has frozen SHA-256;
- actual PowerPoint playback confirms old + new choreography.

## Failure policy

Do not fall back to deleting `p:timing` and rebuilding from scratch merely
because merge logic is harder. If the merge cannot yet be implemented, preserve
the source, document the blocker, and improve the merge backend.
