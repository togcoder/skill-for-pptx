# Evidence and evaluation

Freeze an experiment rubric before evaluating a candidate. E001 uses experiments/E001/rubric.json. Never change criteria to improve the score after seeing an output.

Record:
- Brief coverage: objective label/state counts and human reading.
- Native object types and editability: inspect package; real application editing remains a separate check.
- Identity structure: names, ordered slide destinations, declared durations, duplicate IDs.
- Static readability: inspect full-size renders of every final slide; record renderer/version.
- Native motion: null until recorded PowerPoint playback tied to the exact PPTX hash.
- Creative quality: reviewer judgment only; a static composition does not establish motion appeal.
- Path proxy: record the exact interpolation assumption and selected objects separately. A geometry diagnostic can identify a design risk but cannot pass native-motion criteria. Preserve the unmodified failing composition before tuning a route.

Report counts separately from 0–5 subjective ratings. Give evidence and one sentence of rationale for every score. Do not produce a composite quality percentage while motion is unobserved.

Baseline comparisons must hold prompt, source plan, rendering settings and tests constant. A fault suite created for known bugs demonstrates those repairs, not universal reliability. Use a separate subject for a forward test and keep its artifacts separate. Do not disclose expected outcomes to the agent performing that task.
