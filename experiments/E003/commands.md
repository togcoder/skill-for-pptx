# E003 commands and environment

Same supplied runtime bundle as E002/H002: 26.927.11222, Node v24.19.0,
Python 3.12.14, Artifact Tool 2.8.77. Parent Presentations authoring marker was
already emitted for this research turn; E003 was added after the H002 finding.

1. `python3 experiments/E003/create_plan.py`
2. `python3 scripts/validate_plan.py experiments/E003/plan.json`
3. `python3 experiments/E003/path_diagnostic.py experiments/H002/plan.json read-label relax-label create-label > experiments/E003/baseline-paths.json`
4. `python3 experiments/E003/path_diagnostic.py experiments/E003/plan.json read-label relax-label create-label > experiments/E003/candidate-paths.json`
5. `bash scripts/run_experiment.sh experiments/E003/plan.json build/e003 output/PPTX_Motion_Lab_E003.pptx`
6. Export RUNTIME_NODE, RUNTIME_NODE_MODULES, RUNTIME_PYTHON and RUNTIME_BIN_DIR
   from supplied CODEX_PRIMARY_RUNTIME_* variables as in scripts/run_experiment.sh.
7. `"$RUNTIME_NODE" /root/.codex/skills/builtins/presentations/container_tools/render_presentation.mjs --input output/PPTX_Motion_Lab_E003.pptx --output_dir experiments/E003/final-render --scale 1`
8. `python3 experiments/E003/verify_candidate.py > experiments/E003/package-check.json`
9. Four analytic interval fixtures passed; stored in diagnostic-checks.json.

Final images were individually inspected. No PowerPoint execution occurred.
