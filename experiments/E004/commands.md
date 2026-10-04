# Commands and environment

Runtime bundle/version/font: environment.json. No dependencies installed.
Host Presentations operation marker ran once before first authoring, count 2.

1. `python3 experiments/H003/create_plan.py`
2. `python3 experiments/E004/create_plan.py`
3. `python3 scripts/validate_plan.py experiments/H003/plan.json`
4. `python3 scripts/validate_plan.py experiments/E004/plan.json`
5. `python3 experiments/E003/path_diagnostic.py experiments/H003/plan.json community-label transport-label infrastructure-label`
6. Repeat 5 for E004 and both plans with the three `*-block` IDs.
7. `python3 scripts/cyclic_label_clearance.py --half-span 420 --width 360 --height 96 --gap 200` and gap 300.
8. `python3 -m unittest discover -s tests -v`
9. `bash scripts/run_experiment.sh experiments/H003/plan.json build/h003-r1 output/PPTX_Motion_Lab_H003.pptx`
10. `bash scripts/run_experiment.sh experiments/E004/plan.json build/e004-r1 output/PPTX_Motion_Lab_E004.pptx`
11. `python3 experiments/E004/verify_pair.py`
12. Export RUNTIME_NODE, RUNTIME_NODE_MODULES, RUNTIME_PYTHON and RUNTIME_BIN_DIR from CODEX_PRIMARY_RUNTIME_* as in run_experiment.sh.
13. Use host `container_tools/render_presentation.mjs --input DECK --output_dir experiments/ID/final-render --scale 1` for each final deck.
14. Inspect all six final PNGs separately at 1280×720.

When repeating, choose new build/output paths; scripts refuse overwrite.
Two preflight plan mistakes were preserved in failed-preflight before correction.
Evidence copies of normalizer, renderer and finalizer receipts are in each
experiment's evidence/. No native PowerPoint playback was performed.
