# E002 — Native textbox representation

Frozen before candidate execution, 2026-10-04 (Asia/Ho_Chi_Minh).

Reuse the exact final H001 deck and its plan, rubric and checker. Correct only
the formal representation of planned textboxes. Do not change text, carrier
types, positions, sizes, style, relationships, notes or declared transitions.
Keep H001 artifacts unchanged. Write E002 to a new filename.

Acceptance: all 14 planned textboxes explicitly marked; the existing H001
checker passes with only its input deck path redirected. All other package
parts byte-identical; slide XML differs semantically only by the planned
txBox attributes. Finalizer passes; render and view both final slides and
compare to H001. Native playback and application editing remain unverified.

Source: Microsoft, NonVisualShapeDrawingProperties (Presentation), accessed
2026-10-04: https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.nonvisualshapedrawingproperties?view=openxml-3.0.1
Technical semantics only; no reference media or code copied. The documentation
distinguishes a declared textbox from another shape that contains native text.

Transfer task to freeze separately: three states of a fictional product's
three circular feature nodes, each taking focus in turn while the other nodes
remain visible. New topic and topology; do not reuse H001's rectangular process
composition. Keep structural and static evidence separate from playback.
