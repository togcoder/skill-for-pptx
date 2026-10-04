# Reproduction commands

Work from repository root. Python 3.12.14, lxml 6.1.1, Node 24.19.0, artifact-tool 2.8.77; see environment.json. Host Presentations skill operation marker was emitted before authoring. Extra outputs were produced to retain the unexpected wrapping failure.

```bash
python3 scripts/layer_separation.py experiments/T003-20261004-codex-layer01/config.json NEW_PLAN.json
python3 scripts/validate_plan.py NEW_PLAN.json
bash scripts/run_experiment.sh NEW_PLAN.json build/NEW_BUILD output/NEW_DECK.pptx
export RUNTIME_NODE_MODULES="$CODEX_PRIMARY_RUNTIME_NODE_MODULES"
"$CODEX_PRIMARY_RUNTIME_NODE" /root/.codex/skills/builtins/presentations/container_tools/render_presentation.mjs --input output/NEW_DECK.pptx --output_dir NEW_RENDER_DIR --scale 1
python3 -m unittest discover -s tests -v
python3 experiments/T003-20261004-codex-layer01/verify_study.py
```

The frozen v1 generator is generator-v1.py, not the current scripts/layer_separation.py. Its --ablate-binding variant created ablation-plan.json. Current generator creates plan-v2 geometry. The agent generated transfer/plan.json with v1 and localized only eyebrow; parent changed only width of attached number boxes for transfer/plan-v2.json. Preserve this intervention when reproducing, as described in transfer/NOTES.md and CONTEXT.md.

Used build/ directories: T003-layer-candidate, T003-layer-ablation, T003-layer-candidate-v2, T003-transfer-v1, T003-transfer-v2. Corresponding exported files and exact hashes are in study-comparison.json. All final PNGs are committed under candidate-renders/, ablation-renders/, candidate-v2-renders/, transfer/v1-renders/, transfer/v2-renders/.
