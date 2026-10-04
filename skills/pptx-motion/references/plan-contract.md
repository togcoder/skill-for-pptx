# Motion plan v0.1

Use UTF-8 JSON. Root fields: version ("0.1"), brief (nonempty), canvas, data_provenance, objects, states, transitions. Set data_provenance to none, synthetic or user-provided.

Canvas: width=16, height=9, units="normalized". Coordinates are fractions of slide width and height, not inches. The current renderer maps to 1280x720 px. A circle with diameter d px needs w=d/1280 and h=d/720.

Each object needs id (lowercase letters, digits, hyphens), kind, persistent (boolean), morph_name ("!!"+stable name).
Renderer fields: geometry (rect/ellipse for shape, textbox for text), fill and stroke (#RRGGBB or none), stroke_width (pixels), text, font_size (CSS pixels), text_color, bold (boolean). Omitted text settings use renderer defaults. Objects render in array order, back to front. Do not add unsupported fields.

Each state: id, message (purpose), objects mapping semantic IDs to x,y,w,h,rotation_deg,opacity. Positive w/h, finite values. Opacity must equal 1 in this renderer even though the broader validator accepts 0..1. Off-canvas positions need off_canvas=true. Use native text with no fill for labels; give each label enough width at the chosen font size.

Each transition: from, to, kind="morph", duration_ms (positive integer <=4294967295), track (IDs present at both ends). Exactly one transition for each consecutive state. The declaration belongs to the destination slide. `track` expresses required continuity; byObject Morph may also move other matched objects. It is not an inclusion filter.

All persistent objects must appear in every state. IDs denote semantic identity, not the slide-local cNvPr integer. The patcher requires source forced names to match the state's declared objects exactly.

Start from experiments/E001/baseline/plan.json for syntax, but construct a new composition for a new brief.

## Export representation observed in H001 and corrected in E002

The raw artifact-tool export used in H001 encoded planned textboxes as native p:sp rectangles with p:txBody, without cNvSpPr txBox=1. H001's strict check remains failed in its historical report. E002 corrects only these declarations using scripts/normalize_textboxes.py: match exact plan names and ordered slides, require an existing native text body and rect geometry, then set txBox=1 only for kind=text. A shape containing text stays a shape when planned as kind=shape. The pipeline runs this pass before adding Morph. E002 passes the unchanged H001 criteria with 14 declared textboxes, no other semantic package changes and identical endpoint pixels. This establishes the representation correction only; native playback and real-application editing remain unobserved.
