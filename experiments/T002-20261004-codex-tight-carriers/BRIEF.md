# T002 — Tight carrier geometry

Frozen 2026-10-04 UTC before candidate authoring. Base: main `2d93fa70c9441ac604b1bff8ef7a30b568b73830`.

Baseline is E004, unchanged. It already has zero label-box overlap intervals and six carrier-box overlap intervals across two transitions under the frozen synchronized linear rectangle proxy. Native playback remains unknown.

Hypothesis: carrier rectangles contain excess background area. Centering a tighter context carrier (372×104 px) and focus carrier (404×112 px) around the unchanged 360×96 px label can reduce carrier overlap from 6/6 to 0/6 without clipping text or changing label paths. The focused carrier remains larger than context. Use these dimensions exactly; do not tune them after seeing the deck.

Fixed: prompt, three slides, state order, all object IDs/types, eight native objects per slide, five textboxes per slide, all text and font sizes, label geometry and positions, title/footer, fills/strokes, transition count/duration, renderer, diagnostic and rubric. Allowed: x/y/w/h of the three `*-block` frames only, derived by centering the frozen dimensions around their corresponding labels. No source research is needed because this is a continuation of the documented E004 geometric gap.

Acceptance: validate plan; same frozen diagnostic reports label and carrier paths separately; paired checker proves only allowed block geometry changed; exported final PPTX passes package parity; all three final renders inspected; compare subjective static scores and document loss of visual emphasis if any. Motion/editing remain null without PowerPoint.

