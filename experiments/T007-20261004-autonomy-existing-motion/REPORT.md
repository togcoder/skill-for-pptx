# T007 — Autonomous director target + existing-motion intake

Date: 2026-10-04

## User destination clarified

The product destination is an autonomous AI Motion Director for an **existing
PowerPoint deck**.

The normal input may be only a PPTX and a high-level goal. The user should not
need to specify object-by-object animations.

The system must:

1. inspect the existing deck and freeze source identity;
2. follow an explicit script/storyboard if supplied;
3. otherwise use speaker notes;
4. otherwise treat existing native animation/transition choreography as planning
   evidence and preserve it by default;
5. otherwise infer the report sequence from the visible deck;
6. research a reporting/story pattern only when the deck is incomplete and
   research is appropriate;
7. create a report/motion script before animating;
8. reuse existing slide resources first;
9. create missing helper components only for real narrative gaps and inside the
   existing design language;
10. keep same-resource motion on the same slide whenever feasible;
11. preserve existing timing rather than rejecting an animated source deck;
12. return the same report, still editable, now professionally motion-directed.

The canonical product statement remains `docs/PRODUCT_TARGET.md`.

## Changes in this experiment

### Existing timing becomes a script source

`existing-timing` is now a valid director-plan script source, after explicit
script and speaker notes in the source-priority hierarchy.

This does not mean timing XML is automatically a complete human narrative.
It means current authored choreography is first-class evidence and must not be
discarded without a stronger source or explicit justification.

### Choreography-aware deck intake

`scripts/inspect_existing_deck.py` now reports, per slide:

- transition summary;
- native timing effect count;
- time-node count and node-type distribution;
- animation effect types;
- source target shape ID/name/text/kind when resolvable;
- effect duration;
- raw start conditions;
- numeric delay when directly available;
- effect-specific properties such as motion path, scale or rotation;
- build-list entries;
- an order hint with an explicit confidence/basis boundary.

The order hint is deliberately conservative. Complex event/master relationships
can make runtime order richer than simple document order or numeric delays.

### Future research tasks

- `T008-existing-motion-continuation.md`: preserve and extend an already animated
  deck instead of deleting timing and rebuilding from scratch.
- `T009-autonomous-no-script-benchmark.md`: benchmark the north-star condition
  where the user supplies only a deck and possibly a high-level goal.

## Microsoft evidence

Microsoft's Open XML documentation states that animations on a slide are
time-based and are stored in the slide XML inside `p:timing`. The Timing
element tracks animations/timed events through time nodes. This supports treating
existing timing as inspectable source context rather than as an opaque binary
feature.

Sources inspected 2026-10-04:

- https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation
- https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.timing
- https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-presentation-slides

These sources establish document structure, not runtime playback equivalence.

## Automated evidence

Temporary branch-only GitHub Actions run:

- run ID: 37215400829
- job ID: 111474762545
- Python: 3.12.14
- `python -m py_compile scripts/*.py`: pass
- `python -m unittest discover -s tests -v`: **75 tests passed**
- runtime: 0.354 s

New regression coverage proves:

1. `existing-timing` is accepted as a director script source;
2. Morph/fade transition structure is exposed by deck intake;
3. an existing-deck native timing patch can be read back as two effects;
4. the read-back effects resolve to the intended source shape;
5. numeric behavior delays produce an explicit order hint.

The temporary CI workflow was removed after the successful run.

## Boundaries

Not yet established:

- faithful interpretation of arbitrary PowerPoint-authored timing trees;
- merging new effects into an arbitrary pre-existing timing hierarchy;
- autonomous report-sequence quality on a real no-script corporate deck;
- component synthesis quality across arbitrary design systems;
- exact-file Microsoft PowerPoint playback of T008/T009 outputs.

The current existing-deck patcher still rejects slides with pre-existing native
timing. That is now explicitly a backend limitation to remove in T008, not an
acceptable product behavior.
