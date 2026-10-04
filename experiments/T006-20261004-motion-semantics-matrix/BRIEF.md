# Frozen brief — Two-stage motion semantics matrix

Base: ad707aa77408cae07c4e744598f7284c57c05ed9. Frozen UTC: 2026-10-04T19:57:29Z.

## Question

For one shape moving A -> B -> C on one slide after one click, which combination preserves stage continuity in Microsoft PowerPoint?

1. stage-local paths + behavior fill=remove;
2. stage-local paths + behavior fill=hold;
3. authored-layout anchored paths + behavior fill=remove;
4. authored-layout anchored paths + behavior fill=hold.

The current production writer corresponds to variant 1. Variant 4 is the leading repair hypothesis from the T006 coordinate audit. No production change is authorized by this hypothesis alone.

## Fixed scene and timeline

- One 16:9 slide.
- Moving native circle authored at center A=(0.20, 0.55).
- Visible native target rings at B=(0.45, 0.55) and C=(0.70, 0.55).
- Stage 1: A -> B, 900 ms, on-click.
- Stage 2: B -> C, 900 ms, after-previous in the plan and cumulative delay in the current writer.
- Same objects, order, durations, timing IDs and group structure across variants except the intended path/fill attributes.
- Synthetic labels/data only; no external visual asset.

## Machine acceptance

- Four finalized one-slide PPTX files, unique exact SHA-256 hashes.
- Each file has identical non-slide bytes and identical slide XML after normalizing only the intended path/fill attributes.
- One clickEffect group, two motion behaviors, delays 0 and 900 ms, durations 900 ms.
- Stage-local paths: M 0 0 L 0.25 0 for both stages.
- Anchored paths: stage 1 M 0 0 L 0.25 0; stage 2 M 0.25 0 L 0.50 0.
- ZIP/package/finalizer checks pass; all final slides rendered and inspected.
- Full repository unit suite passes.

## Native observation rubric

For each exact hash record: repair warning, click count, stage-1 endpoint, whether stage 2 starts from B or jumps to A, final endpoint, persistence after 1.8 s, Animation Pane editability and evidence capture. The useful result is a discriminating observation, including total failure.

Do not call any variant correct without actual playback in a named PowerPoint version. Static rendering checks only the common initial state.
