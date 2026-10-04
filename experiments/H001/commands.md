# H001 executed commands

All paths below are relative to the project root unless absolute.

1. `python3 scripts/validate_plan.py experiments/H001/plan.json > experiments/H001/plan-validation.json` returned valid true.
2. `python3 -m unittest discover -s tests -v > experiments/H001/unit-tests.txt 2>&1` passed all 19 tests.
3. Runtime preflight checked the supplied Node, Python, node_modules and override bin paths. Node v24.19.0, Python 3.12.14.
4. `"$CODEX_PRIMARY_RUNTIME_NODE" /root/.codex/skills/builtins/presentations/container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format pptx > experiments/H001/operation-marker.json` succeeded once.
5. `bash scripts/run_experiment.sh experiments/H001/plan.json build/h001 output/PPTX_Motion_Lab_H001.pptx > experiments/H001/build-log.txt 2>&1` succeeded. Finalizer receipt is preserved in finalizer-validation.json.
6. `python3 scripts/inspect_pptx.py output/PPTX_Motion_Lab_H001.pptx > experiments/H001/package-inventory.json` returned no inventory errors.
7. Initial `render_presentation.mjs` invocation failed because RUNTIME_NODE_MODULES was not exported in that new shell. Preserved stdout/stderr: render-attempt1-stdout.txt and render-attempt1-stderr.txt. No deck mutation occurred. The run_experiment.sh exports do not persist into later shells.
8. After explicitly exporting RUNTIME_NODE, RUNTIME_NODE_MODULES, RUNTIME_BIN_DIR and RUNTIME_PYTHON from the supplied runtime variables: `"$RUNTIME_NODE" /root/.codex/skills/builtins/presentations/container_tools/render_presentation.mjs --input output/PPTX_Motion_Lab_H001.pptx --output_dir experiments/H001/final-render --scale 1 > experiments/H001/final-render-log.json 2> experiments/H001/final-render-stderr.txt` succeeded. Both individual 1280×720 PNGs were viewed at full size.
9. `python3 experiments/H001/verify_package.py > experiments/H001/plan-package-comparison.json` returned status 1 because the strict txBox=1 assertions failed for all 14 text-bearing objects across the deck. The helper and output remain unchanged. Its other assertions, including names, geometry, text, duration, order, source notes and absence of media, passed.

No extra tests, deck mutation, source edits, STATUS edits, skill installation, upload or publication followed this evidence. H001 used the current renderer after the parent corrected hardcoded notes attribution before the build.
