# T019 — PowerPoint-canonical timing and one-command Motion Director

Status: implemented and structurally checked; PowerPoint playback pending.

## Problem

1. The existing-deck writers (patch v0.2–v0.5) put every stage of a click beat
   in one `p:par` with `delay=0`. In the SMIL time model that PowerPoint uses,
   siblings of a `par` start together, so `after-previous` stages run
   concurrently. They also omit `set style.visibility`, preset classes and write
   duplicate `bldP` entries.
2. Any slide with existing timing was rejected, although AGENTS requires
   existing choreography to be preserved and extended.
3. Real decks use layout placeholders without slide geometry, bullet bodies and
   pictures; there was no one-command path from PPTX + goal to output.

## Acceptance

- Timing tree in the shape PowerPoint saves (click group → time blocks → effect
  par with presetClass/presetID/nodeType → set visibility + behaviours).
- `after-previous` begins at the end of the previous block (checked by tests
  and by an independent importer).
- Existing main sequence kept byte-equal; new groups appended with fresh ids.
- Autonomous draft produces a valid Director plan from deck evidence; apply
  verifies preservation and simulated end state.
- Native playback claim stays false until docs/POWERPOINT_NATIVE_HARNESS.md runs.
