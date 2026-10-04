# T010 click-beat semantics — source note

Date: 2026-10-05 Vietnam.

## User correction

Packing motion into one slide is not equivalent to one click triggering all
motion. The system must understand presenter-controlled rhythm: what belongs in
one cluster, what waits for the next click, what runs concurrently, and what
automatically follows.

## Microsoft product semantics

Microsoft Support documents:

- On Click starts the animation when the presenter clicks;
- With Previous starts it at the same time as the previous effect;
- After Previous starts it after the previous effect finishes;
- Delay is measured relative to the chosen Start behavior.

Sources:

- https://support.microsoft.com/en-us/powerpoint/set-the-start-time-and-speed-of-an-animation-effect
- https://support.microsoft.com/en-us/powerpoint/apply-multiple-animation-effects-to-one-object
- https://support.microsoft.com/en-us/powerpoint/training/animate-text-or-objects

This establishes the interaction model exposed to PowerPoint authors.

## Empirical OOXML evidence

Two independent public implementations/articles were inspected as structural
cross-checks, not vendored runtime dependencies.

1. lindexi OpenXML PowerPoint timing article:
   https://github.com/lindexi/lindexi.github.io/blob/0084be094c0177dcaa2de5bdbfee4ae00b5e3b8d/dotnet%20OpenXML%20PPT%20%E5%8A%A8%E7%94%BB%E6%A1%86%E6%9E%B6%E5%85%A5%E9%97%A8.md

   The article derives examples from PowerPoint files and distinguishes:
   - several automatic animations wrapped under one click-controlled parent;
   - separate click actions represented as separate children under `mainSeq`.

2. agentsea/nautilo animation serializer:
   https://github.com/agentsea/nautilo/blob/0f02e50472b09b96b18ae711412b4c36dd2a7b13/packages/office-slides/src/export/pptx/animation.ts

   Its model starts a new click group for `onClick`; `withPrev` and
   `afterPrev` continue the current group, and the serializer emits one
   `mainSeq` child group per click.

These are empirical implementation observations. Native Microsoft PowerPoint
playback remains the acceptance gate.

## Resulting architecture decision

Use:

`Slide -> Click Beat -> Stage -> Effects`

and retain T006's one-click cumulative-delay writer only as a legacy pacing
baseline. T010 v0.2 uses distinct main-sequence click groups.
