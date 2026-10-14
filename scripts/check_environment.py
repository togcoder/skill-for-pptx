#!/usr/bin/env python3
"""Read-only capability inventory for a new research checkout; not playback QA."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


def _safe_is_file(p):
    try:
        return bool(p and Path(p).is_file())
    except (PermissionError, OSError):
        return False


def _safe_is_dir(p):
    try:
        return bool(p and Path(p).is_dir())
    except (PermissionError, OSError):
        return False


host = Path('/root/.codex/skills/builtins/presentations')
node = os.environ.get('CODEX_PRIMARY_RUNTIME_NODE')
modules = os.environ.get('CODEX_PRIMARY_RUNTIME_NODE_MODULES')
runtime_python = os.environ.get('CODEX_PRIMARY_RUNTIME_PYTHON')
runtime_root = os.environ.get('CODEX_PRIMARY_RUNTIME_ROOT')
checks = {
    'runtime_node_exists': _safe_is_file(node),
    'runtime_python_exists': _safe_is_file(runtime_python),
    'artifact_tool_package_exists': _safe_is_file(Path(modules)/'@oai/artifact-tool/package.json') if modules else False,
    'runtime_override_dir_exists': _safe_is_dir(Path(runtime_root)/'dependencies/bin/override') if runtime_root else False,
    'host_finalizer_exists': _safe_is_file(host/'container_tools/artifact_tool_utils.mjs'),
    'host_renderer_exists': _safe_is_file(host/'container_tools/render_presentation.mjs'),
}
print(json.dumps({
    'python_version': sys.version.split()[0], 'platform': sys.platform,
    'plan_and_geometry_checks_available': True,
    'lxml_available': importlib.util.find_spec('lxml') is not None,
    'pillow_available': importlib.util.find_spec('PIL') is not None,
    'libreoffice_available': bool(shutil.which('soffice') or shutil.which('libreoffice')),
    'pdftoppm_available': shutil.which('pdftoppm') is not None,
    'work_builder_prerequisites_present': all(checks.values()),
    'work_builder_checks': checks,
    'powerpoint_executable_on_path': shutil.which('POWERPNT.EXE') is not None,
    'powerpoint_playback_verified': False,
    'limitations': ['Presence checks do not prove executables run or PowerPoint is usable. PowerPoint outside PATH may exist. Follow host instructions before authoring.']
}, indent=2))
