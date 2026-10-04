# T011 — Director Click-Rhythm Contract and Existing-Deck Execution

Status: active research.

Read T007, T009, T010 and `docs/CLICK_BEAT_CHOREOGRAPHY.md`.

## Goal

Move presenter pacing upstream from the XML writer into the AI Motion Director.

The AI must decide, from report meaning, which motion actions share a presenter
click and which require a new click **before** low-level timing is authored.

## Semantic hierarchy

`Deck Narrative -> Slide Objective -> Click Beat -> Motion Beat -> Effects`

T010's lower-level hierarchy is compatible:

`Slide -> Click Beat -> Stage -> Effects`

A director motion beat may later compile to one or more concrete stages, but its
click-beat membership must survive compilation.

## Contract v0.2

Each slide keeps ordered `beats` and adds ordered `click_beats`.

A click beat records:

- audience purpose;
- ordered motion-beat IDs;
- the stable state reached;
- what kind of pause follows;
- from click 2 onward, why a new click is narratively necessary.

Validation requires exact ordered partitioning and forbids nested `on-click`
inside one declared presenter beat.

## Existing-deck patch path

The low-level existing-deck timeline patch contract also gains v0.2 click beats.
A fresh unanimated source slide can therefore preserve multiple presenter clicks
without becoming multiple slides.

This does not solve T008 merge with pre-existing native timing; that remains a
separate research problem.

## Acceptance

1. Legacy director/patch v0.1 plans remain valid for historical reproduction.
2. Director v0.2 rejects ungrouped/ambiguous presenter rhythm.
3. Existing-deck patch v0.2 emits multiple click groups on one source slide.
4. Intake reads those groups back.
5. Untargeted slide/package content stays preserved.
6. No presenter pause is represented as a guessed wall-clock delay.
7. T009 no-script benchmark scores click-boundary/stable-state quality.
8. Actual PowerPoint playback remains required before native behavior claims.

## Next transfer test

Use a real existing report slide with at least three meaningful source resources.
Create two semantic plans:

- a deliberately bad one-click autoplay plan;
- a narrative click-beat plan inferred from the slide objective.

Keep slide count and source resources identical. Compare human review of reveal
timing, premature information exposure and presenter control before native
playback.
