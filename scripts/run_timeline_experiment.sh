#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 3 ]; then
  echo "Usage: run_timeline_experiment.sh PLAN BUILD_DIR FINAL_PPTX" >&2
  exit 2
fi
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
export RUNTIME_NODE="${CODEX_PRIMARY_RUNTIME_NODE:?}"
export RUNTIME_NODE_MODULES="${CODEX_PRIMARY_RUNTIME_NODE_MODULES:?}"
export RUNTIME_PYTHON="${CODEX_PRIMARY_RUNTIME_PYTHON:?}"
export RUNTIME_BIN_DIR="${CODEX_PRIMARY_RUNTIME_ROOT:?}/dependencies/bin/override"
test -x "$RUNTIME_NODE"
test -d "$RUNTIME_NODE_MODULES"
test -x "$RUNTIME_PYTHON"
test -d "$RUNTIME_BIN_DIR"
mkdir -p "$2"
for name in raw.pptx native.pptx timeline.pptx; do
  if [ -e "$2/$name" ]; then
    echo "Use a fresh build directory for each run" >&2
    exit 2
  fi
done
if [ ! -e "$2/node_modules" ]; then
  ln -s "$RUNTIME_NODE_MODULES" "$2/node_modules"
fi
cp "$project_root/scripts/render_timeline.mjs" "$2/render_timeline.mjs"
"$RUNTIME_NODE" "$2/render_timeline.mjs" "$1" "$2" "$3" "$project_root"
