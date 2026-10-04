# Motion Packing Policy

This document is a hard planning rule for all future work in PPTX Motion Lab.

## Core rule

A slide is a **scene/execution container**, not a motion frame.

When consecutive actions reuse the same semantic objects/assets and stay in the
same scene, pack as many of those actions as PowerPoint can robustly express
into **one slide timeline**. Do not create a new slide merely to represent an
intermediate pose, waypoint, rotation sample, emphasis step, split step, or
return step.

Prefer this order:

1. one slide + multiple native animation tracks/timings/triggers,
2. the minimum number of slides required by a real PowerPoint limitation,
3. state-per-slide Morph only as a fallback or a deliberate experiment.

## What counts as reusable resources

Treat two actions as sharing a resource set when they operate on the same
persistent semantic objects, images, shapes, text, charts, or other assets,
even if position, scale, rotation, emphasis, visibility, or timing changes.

Pre-created hidden/occluded objects still count as reusable resources. If the
objects already exist and only their visual state changes, the default target is
one slide.

## Split a scene only when necessary

A new slide needs an explicit reason. Valid reasons include:

- a real scene/topic boundary where the resource set materially changes;
- a topology change PowerPoint cannot express reliably on one timeline;
- Morph is specifically required for a transform that cannot be represented
  robustly with native animation on one slide;
- PowerPoint authoring/playback constraints make the packed timeline unstable,
  uneditable, or impossible to verify;
- the user explicitly requests separate slides.

"More convenient to implement" is not a valid reason.

If one-slide packing fails, record the technical blocker and use the **minimum
slide count** that satisfies the intent.

## T005 reinterpretation

T005's radial drill-down used many Morph waypoint slides to represent:

burst -> orbit -> focus -> split -> reassemble -> restore.

All persistent objects already existed across the sequence. Therefore T005 is a
legacy structural baseline, **not the target architecture**. T006 must attempt to
pack the same semantic sequence into a single native-timeline slide. Orbit
waypoints should become motion-path/timing samples or another native animation
mechanism, not extra slides, unless a verified PowerPoint limitation prevents it.

## Planning metrics

For every new compound-motion experiment record:

- semantic scene count;
- final PowerPoint slide count;
- requested motion-event count;
- packed motion-event count per slide;
- resource-set changes;
- every reason a slide boundary was introduced.

Define:

`packing_ratio = requested_motion_events / final_slide_count`

Use it only as an efficiency diagnostic. Do not inflate it by merging unrelated
scenes or making an unreadable timeline. The real objective is **maximum
feasible packing while preserving intent, editability, readability, and native
PowerPoint playback**.

## Model behavior

Before designing slides, partition the request into semantic scenes and motion
events. Then cluster adjacent events that reuse the same resource set. Attempt
one-slide execution for each cluster.

Never assume:

- one user verb = one slide;
- one animation waypoint = one slide;
- one Morph state = one slide in the final architecture.

When writing a handoff, state explicitly whether a multi-slide sequence is a
legacy Morph fallback or a proven minimum-slide solution.

## Evidence requirement

A packed timeline is not accepted merely because OOXML exists or a static render
looks correct. Preserve the existing evidence boundary: actual playback must be
verified in a named PowerPoint version against the exact file hash before
claiming native behavior.

