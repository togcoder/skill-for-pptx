#!/usr/bin/env python3
"""Read-only capability inventory for a new research checkout; not playback QA."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

host = Path('/root/.codex/skills/builtins/presentations')
node = os.environ.get('CODEX_PRIMARY_RUNTIME_NODE')
modules = os.environ.get('CODEX_PRIMARY_RUNTIME_NODE_MODULES')
runtime_python = os.environ.get('CODEX_PRIMARY_RUNTIME_PYTHON')
runtime_root = os.environ.get('CODEX_PRIMARY_RUNTIME_ROOT')
checks = {
    'runtime_node_exists': bool(node and Path(node).is_file()),
    'runtime_python_exists': bool(runtime_python and Path(runtime_python).is_file()),
    'artifact_tool_package_exists': bool(modules and (Path(modules)/'@oai/artifact-tool/package.json').is_file()),
    'runtime_override_dir_exists': bool(runtime_root and (Path(runtime_root)/'dependencies/bin/override').is_dir()),
    'host_finalizer_exists': (host/'container_tools/artifact_tool_utils.mjs').is_file(),
    'host_renderer_exists': (host/'container_tools/render_presentation.mjs').is_file(),
}
print(json.dumps({
    'python_version': sys.version.split()[0], 'platform': sys.platform,
    'plan_and_geometry_checks_available': True,
    'lxml_available': importlib.util.find_spec('lxml') is not None,
    'work_builder_prerequisites_present': all(checks.values()),
    'work_builder_checks': checks,
    'powerpoint_executable_on_path': shutil.which('POWERPNT.EXE') is not None,
    'powerpoint_playback_verified': False,
    'limitations': ['Presence checks do not prove executables run or PowerPoint is usable. PowerPoint outside PATH may exist. Follow host instructions before authoring.']
}, indent=2))
