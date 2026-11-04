#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - one command that rebuilds every artifact in this task.

    python run_experiment.py            # full rebuild (needs Windows + PowerPoint + DeckCraft)

Writes:
    artifacts/field-terminal.pptx + .deckcraft + native-art-manifest.json   (route A)
    artifacts/field-terminal-routeB.pptx + .svg                             (route B)
    artifacts/field-terminal-routeC.pptx + .glb                             (route C)
    artifacts/render-a|b|c.png, native-deckcraft-render.png, route-evidence.json
    preview/compare-3up.png
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ARTIFACTS = EXP / "artifacts"
PREVIEW = EXP / "preview"
WORK = EXP.parent.parent / "workspace" / "build-t062"
SPEC = HERE / "native_art_spec.json"

sys.path.insert(0, str(HERE))
import build_native_art as native  # noqa: E402


def run(*args: str) -> None:
    print("$", " ".join(args))
    subprocess.run(args, check=True)


def main() -> int:
    state = native.availability()
    if not state["ok"]:
        print(json.dumps({"skipped": state["code"], "detail": state["detail"]}))
        return 2

    for directory in (ARTIFACTS, PREVIEW, WORK):
        directory.mkdir(parents=True, exist_ok=True)

    # Route A - DeckCraft native shapes.
    native_dir = WORK / "native"
    manifest = native.compile_spec(SPEC, native_dir)
    for name in ("field-terminal.deckcraft", "field-terminal.pptx", "native-art-manifest.json"):
        shutil.copyfile(native_dir / name, ARTIFACTS / name)
    commands = HERE / "commands"
    commands.mkdir(exist_ok=True)
    for name in ("stage1.commands.txt", "stage2.commands.txt", "stage3.commands.txt"):
        shutil.copyfile(native_dir / "native-art-work" / name, commands / name)

    cli = Path(state["cli"])
    render_dir = WORK / "deckcraft-render"
    run(str(cli), "render", str(ARTIFACTS / "field-terminal.pptx"), "--all", "--scale", "2", str(render_dir))
    shutil.copyfile(render_dir / "slide-01.png", ARTIFACTS / "native-deckcraft-render.png")

    # Route B - one SVG picture.
    run(sys.executable, str(HERE / "build_svg_route.py"), str(SPEC), str(WORK / "svg"))
    shutil.copyfile(WORK / "svg" / "field-terminal-routeB.pptx", ARTIFACTS / "field-terminal-routeB.pptx")
    shutil.copyfile(WORK / "svg" / "field-terminal-art.svg", ARTIFACTS / "field-terminal-art.svg")

    # Route C - one GLB model. Front camera: any Y rotation makes PowerPoint clip
    # the badge at the frame edge (preview/route-c-rotated-clip.png keeps that).
    run(sys.executable, str(HERE / "build_glb_route.py"), str(SPEC), "--out", str(WORK / "glb"),
        "--colour-scale", "0.42", "--frame-scale", "1.0", "--rot-y", "0", "--rot-x", "0")
    shutil.copyfile(WORK / "glb" / "field-terminal-routeC.pptx", ARTIFACTS / "field-terminal-routeC.pptx")
    shutil.copyfile(WORK / "glb" / "field-terminal-art.glb", ARTIFACTS / "field-terminal-art.glb")

    # The negative control: a three-quarter camera clips the badge at the frame edge.
    run(sys.executable, str(HERE / "build_glb_route.py"), str(SPEC), "--out", str(WORK / "glb-rotated"),
        "--colour-scale", "0.42", "--frame-scale", "1.2", "--rot-y", "-12", "--rot-x", "4",
        "--export-png", str(PREVIEW / "route-c-rotated-clip.png"))

    # Evidence.
    run(sys.executable, str(HERE / "verify_routes.py"), "--spec", str(SPEC),
        "--native", str(ARTIFACTS / "field-terminal.pptx"),
        "--svg", str(ARTIFACTS / "field-terminal-routeB.pptx"),
        "--glb", str(ARTIFACTS / "field-terminal-routeC.pptx"),
        "--svg-art-png", str(WORK / "svg" / "field-terminal-art.png"),
        "--native-render", str(ARTIFACTS / "native-deckcraft-render.png"),
        "--out", str(ARTIFACTS))

    run(sys.executable, str(HERE / "make_sheet.py"), str(ARTIFACTS), str(PREVIEW / "compare-3up.png"))
    print(json.dumps({"ok": True, "art_parts": manifest["parts"]["art"],
                      "animations": len(manifest["animations"])}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
