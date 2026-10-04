# T005 frozen brief and criteria

Frozen before implementation: 2026-10-04T14:19:22Z.
Base: f3745118ca2334156038680747a3893397259470.

Prompt: "Bung một lõi thành 12 nút, xoay cả vòng, phóng nút 3, tách nó thành
4 lớp rồi ghép lại; chữ luôn đứng thẳng."

Assumptions because prompt does not specify them: synthetic system diagram,
numbered nodes, clockwise quarter-turn (90 degrees, not a full revolution),
6 orbit segments of 15 degrees, 4 vertical internal layers, final state restores
the rotated ring, dark background, native 2D diagram, click-through Morph.
These are explicit design choices, not user requirements. No actual 3D or
smooth custom path. Ring orbit is a piecewise approximation. Do not claim
continuous/autoplay choreography or verified PowerPoint playback.

Hypothesis: a strict intermediate intent contract and deterministic transform
composition can preserve compound requirements more reliably than manually
editing unrelated endpoint frames. AI translates the user's words into the
contract; the Python compiler itself does not understand arbitrary language.

Frozen machine checks: (1) exactly N semantic nodes; (2) requested operation
order; (3) ring angle and direction; (4) requested focus identity/scale;
(5) requested layer count and separation; (6) exact reassembly at end;
(7) all label rotations zero; (8) native package parity with plan.
All 8 must pass for this restricted recipe. Quantify waypoint count, arc/chord
error, child binding error and bounding-box overlaps for the orbit phase.
Do not treat deliberate launch occlusion or split containment as collisions.

Frozen subjective 1–5: readability, focus clarity, static visual complexity.
Use previous evaluation rubric for general criteria; animation quality and
motion creativity remain null without playback. Do not conflate complexity
with quality. No arbitrary combined score.

Negative control: omit orbit intermediates but keep its endpoints. Compare the
same continuous-linear geometric proxy: maximum radial chord deviation and
inter-node clearance. This is a deliberate ablation, not a discovered bug.

Transfer: after candidate source instructions exist, give a fresh-context
agent only those instructions and a different short request. Preserve raw
output and record interventions. It may select supported parameters or reject
unsupported requests; it must not silently ignore them. This is a recipe
transfer test, not proof of general understanding or a blind independent study.

Next task after this test: native playback acceptance, then genuinely different
motion primitives (timelines/custom paths/3D) with independent capability gates.
