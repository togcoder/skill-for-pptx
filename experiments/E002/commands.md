# E002 executed commands

Run from project root. Required runtime variables come from the host.

1. The Presentations edit marker succeeded once; receipt: operation-marker.json.
2. `python3 -m unittest discover -s tests -v`: all 25 passed; unit-tests.txt.
3. `python3 scripts/normalize_textboxes.py output/PPTX_Motion_Lab_H001.pptx experiments/H001/plan.json build/e002/normalized.pptx > experiments/E002/normalization.json`.
4. Export RUNTIME_NODE, RUNTIME_NODE_MODULES, RUNTIME_PYTHON and RUNTIME_BIN_DIR
   from CODEX_PRIMARY_RUNTIME_* as in scripts/run_experiment.sh.
5. `"$RUNTIME_NODE" experiments/E002/finalize_candidate.mjs "$PWD"`.
6. `python3 experiments/E002/evaluate_h001.py output/PPTX_Motion_Lab_E002.pptx > experiments/E002/h001-candidate-check.json`: exit 0.
7. `"$RUNTIME_NODE" /root/.codex/skills/builtins/presentations/container_tools/render_presentation.mjs --input output/PPTX_Motion_Lab_E002.pptx --output_dir experiments/E002/final-render --scale 1`: exit 0. Both images viewed.
8. `python3 experiments/E002/compare.py > experiments/E002/comparison.json`.

No PowerPoint execution occurred. The frozen baseline checker is not modified.
