# T006 timing-writer evidence note

Date: 2026-10-04.

## Research question

Can the project replace T005's state-per-slide Morph baseline with one PowerPoint
slide containing a packed native timing tree for motion, scale and rotation?

## Official Microsoft evidence

Primary Microsoft sources inspected:

1. Working with animation
   https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation

   Confirms that slide animations are time-based and stored in the slide's
   `p:timing` element.

2. PowerPoint implementation notes for `tnLst`
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/1e399b8c-b3c4-41b3-970c-510909879f59

   PowerPoint supports one root child in `tnLst`; the root timing structure must
   be more constrained than generic schema-valid PresentationML.

3. PowerPoint implementation notes for `cTn`
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/9cc96243-2ada-46cc-9750-d8bdeb1fc2bb

   The `grpId` on a time node must match a group referenced by the build list.

4. `animMotion`
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/498c3cfa-652c-49b3-a82c-33fd94468af8

   Documents the M/L/C/Z/E path vocabulary, relative vs absolute coordinates,
   and PowerPoint defaults for motion behavior.

5. `animScale`
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/358c6de3-2cd7-459b-8eb9-b90f3721fd12

   PowerPoint expects ScaleX/ScaleY semantics and defined from/to/by
   combinations. The T006 writer uses an explicit from/to pair.

6. `bldP`
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/2936b07f-699e-42a7-a898-70122183e0a2

   Requires valid slide shape references and unique (spid, grpId) pairs.

## Empirical cross-check

A public PowerPoint-animation research project was used only as an empirical
cross-check, not as vendored runtime code:

- https://github.com/BramAlkema/pptx-animation-skill
- https://github.com/BramAlkema/svg2ooxml
- commit inspected for timing-tree implementation:
  `81f2159f5fbff460f720f5263ed65112be6b009d`

Observed independent evidence:

- visually-verified motion slots use `animMotion` with relative path data;
- scale slots use `animScale`;
- compound effects place sibling behaviors inside one click group;
- authored/golden timing trees use tmRoot -> mainSeq -> click bucket;
- build-list group IDs are treated as playback-critical;
- the project's negative catalog confirms that schema-valid animation XML can
  still be silently dropped by PowerPoint.

The external repositories are AGPL-3.0. No source file, template library or
runtime dependency is copied into this repository. Their published structures
are treated as research observations and are reimplemented independently from
the Microsoft schema/implementation notes.

## Local prototype experiment

A synthetic one-slide PPTX with two named native shapes was generated locally.
A prototype timing writer inserted one click group containing:

- stage 1: two concurrent motion paths, delay 0 ms;
- stage 2: one motion path + one scale behavior, delay 1000 ms.

Results:

- source SHA-256:
  `d85f4d19e83ba2fa824dfdbfc56e1228905faae8739fa1d0686af9452d72afbe`
- patched PPTX SHA-256:
  `5a1517f1b25edd5ab5a143d0d07234d299afead4ed6d5335ee1b601204dffe1b`
- ZIP CRC check: pass;
- reopened by python-pptx: 1 slide / 2 shapes;
- LibreOffice headless opened and exported the patched file to PDF without a
  package error.

These checks establish only package/loadability confidence. LibreOffice does
not prove PowerPoint animation playback.

## Writer design chosen

`scripts/add_timeline.py` uses:

- exactly one root `p:par` in `p:tnLst`;
- one `mainSeq`;
- one packed `clickEffect` group per slide;
- all stage behaviors as children of that group;
- cumulative behavior delays to serialize stages after the single click;
- same-stage behaviors share the same delay and therefore run concurrently;
- motion waypoints stay in one `animMotion path` string;
- scale percentages are calculated relative to authored initial dimensions;
- rotation uses PowerPoint angle units;
- two unique build-list entries per animated shape: grpId 0 and the packed group.

Visibility is intentionally excluded from v0.1 rather than guessed because
PowerPoint has known schema-valid but playback-dead animation paths.

## Evidence boundary

The writer is not accepted as native-compatible until the exact output is opened
and played in a named Microsoft PowerPoint version with captured evidence.
Structural tests, python-pptx reopen and LibreOffice loadability are lower-tier
evidence only.
