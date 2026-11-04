#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - Forge ``asset`` -> ``{"native_art": ...}`` compiler.

Turns a Forge asset spec into a PPTX whose illustration is a set of named,
individually addressable PowerPoint shapes, by driving the ArtCraft DeckCraft
CLI (``deckcraft-cli``) on Windows.

This is a research prototype. It is deliberately NOT imported by
``slide_forge.py`` and is not part of any product path until a peer review
accepts it (``lab/standards/REVIEW.md``).

Why DeckCraft and not python-pptx: DeckCraft exposes Merge Shapes, Freeform,
Edit Points and Shape Effects as *commands*, which is the capability this
route is testing. python-pptx has no merge/freeform/3D API.

Platform contract (the part the report calls the "skip"):
    Windows + deckcraft-cli  -> compile
    anything else           -> raise NativeArtUnavailable with a coded error:
                               SKIP_NATIVE_ART_PLATFORM / SKIP_NATIVE_ART_NO_DECKCRAFT

Usage:
    python build_native_art.py --check
    python build_native_art.py native_art_spec.json --out ../artifacts --emit-only
    python build_native_art.py native_art_spec.json --out ../artifacts
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SKIP_PLATFORM = "SKIP_NATIVE_ART_PLATFORM"
SKIP_NO_CLI = "SKIP_NATIVE_ART_NO_DECKCRAFT"
COMPILE_FAILED = "NATIVE_ART_COMPILE_FAILED"

DECKCRAFT_CANDIDATES = (
    Path(r"D:\artcraft\DeckCraft\deckcraft-cli.exe"),
    Path(r"C:\artcraft\DeckCraft\deckcraft-cli.exe"),
)

REPO = Path(__file__).resolve().parents[3]
DESIGN_SYSTEM = REPO / "knowledge" / "design_system.json"


class NativeArtUnavailable(RuntimeError):
    """The route cannot run on this machine. ``code`` is the machine-readable skip."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


# ---------------------------------------------------------------------------
# Platform contract


def find_cli() -> Path | None:
    override = os.environ.get("DECKCRAFT_CLI")
    if override and Path(override).is_file():
        return Path(override)
    for candidate in DECKCRAFT_CANDIDATES:
        if candidate.is_file():
            return candidate
    found = shutil.which("deckcraft-cli") or shutil.which("deckcraft-cli.exe")
    return Path(found) if found else None


def availability() -> dict:
    if sys.platform != "win32":
        return {"ok": False, "code": SKIP_PLATFORM, "detail": f"platform is {sys.platform}, DeckCraft compile is Windows-only"}
    cli = find_cli()
    if cli is None:
        return {"ok": False, "code": SKIP_NO_CLI, "detail": "deckcraft-cli not found (set DECKCRAFT_CLI)"}
    return {"ok": True, "code": None, "detail": str(cli), "cli": str(cli)}


def require_available() -> Path:
    state = availability()
    if not state["ok"]:
        raise NativeArtUnavailable(state["code"], state["detail"])
    return Path(state["cli"])


# ---------------------------------------------------------------------------
# Lab sources of truth


def load_theme(name: str) -> dict:
    """Palette from scripts/slide_forge.py THEMES - not a second hard-coded copy."""
    if str(REPO / "scripts") not in sys.path:
        sys.path.insert(0, str(REPO / "scripts"))
    import slide_forge  # noqa: WPS433  (deliberate: one palette authority)

    if name not in slide_forge.THEMES:
        raise KeyError(f"unknown theme {name!r}; have {sorted(slide_forge.THEMES)}")
    return slide_forge.THEMES[name]


def load_design_system() -> dict:
    return json.loads(DESIGN_SYSTEM.read_text(encoding="utf-8"))


def colour(value: str, theme: dict) -> str:
    """Theme role -> RRGGBB; anything else must already be RRGGBB."""
    if value in theme:
        return theme[value].lstrip("#").upper()
    if len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value):
        return value.upper()
    raise ValueError(f"colour {value!r} is neither a theme role nor RRGGBB")


# ---------------------------------------------------------------------------
# Command emission


def _cmd(cmd: str, params: dict | None = None) -> str:
    if params is None:
        return cmd
    return f"{cmd}={json.dumps(params, ensure_ascii=False, separators=(',', ':'))}"


def _fill(part: dict, theme: dict) -> dict | None:
    spec = part.get("fill")
    if not spec:
        return None
    params: dict = {"color": colour(spec["color"], theme)}
    if "transparency" in spec:
        params["transparency"] = spec["transparency"]
    return params


def _roundrect_adjust(part: dict) -> int | None:
    radius = part.get("radius_pt")
    if radius is None:
        return None
    _, _, w, h = part["rect"]
    return max(0, min(50000, round(radius / min(w, h) * 100000)))


def stage1_commands(asset: dict, theme: dict, art_parts: int) -> list[str]:
    """Create every part in z-order and name it. No ids needed: each add selects."""
    commands: list[str] = [
        _cmd("file.new", {"blank": True}),
        _cmd("slide.new", {"layout": "blank"}),
        _cmd("design.background", {"color": colour(asset["stage"]["background"], theme)}),
    ]
    for part in asset["parts"]:
        kind = part["kind"]
        if kind in ("rect", "roundRect", "ellipse"):
            commands.append(_cmd("shape.insert", {"preset": kind, "rect": part["rect"]}))
        elif kind == "polygon":
            commands.append(_cmd("shape.freeform", {"points": part["polygon"], "closed": True}))
        elif kind == "text":
            text = part["text"]["value"].replace("{art_parts}", str(art_parts))
            commands.append(_cmd("insert.textBox", {"rect": part["rect"], "text": text}))
        else:
            raise ValueError(f"{part['name']}: unknown kind {kind!r}")
        # Every add above selects the new shape, so the rename needs no id.
        commands.append(_cmd("shape.rename", {"name": part["name"]}))
        adjust = _roundrect_adjust(part) if kind == "roundRect" else None
        if adjust is not None:
            commands.append(_cmd("shape.adjust", {"index": 0, "value": adjust}))
        fill = _fill(part, theme)
        if fill:
            commands.append(_cmd("shape.fill", fill))
        # shape.insert writes a theme <p:style>, so every unlined shape would
        # otherwise get a hairline in the render. PowerPoint's own "No Outline".
        commands.append(_cmd("shape.line", part.get("line") or {"none": True}))
        if part.get("effects"):
            commands.append(_cmd("shape.effects", part["effects"]))
    return commands


def ops_commands(asset: dict, ids: dict[str, int]) -> list[str]:
    """Merge Shapes, by resolved id. A merge re-ids its result (see compile)."""
    commands: list[str] = []
    for op in asset.get("ops", []):
        merge = op["merge"]
        targets = [ids[name] for name in merge["ids"]]
        commands.append(_cmd("shape.merge", {"op": merge["op"], "ids": targets}))
        # A merge selects its result, so the rename needs no id either.
        commands.append(_cmd("shape.rename", {"name": merge["name"]}))
    return commands


def text_and_motion_commands(asset: dict, ids: dict[str, int], theme: dict) -> list[str]:
    """Format text boxes and add motion, all by resolved id."""
    commands: list[str] = []

    for part in asset["parts"]:
        if part["kind"] != "text":
            continue
        text = part["text"]
        sid = ids[part["name"]]
        commands.append(_cmd("selection.select", {"id": sid}))
        commands.append(_cmd("format.font", {"family": asset.get("font", "Segoe UI")}))
        commands.append(_cmd("format.size", {"size": text["size_pt"]}))
        commands.append(_cmd("format.bold", {"on": bool(text.get("bold"))}))
        commands.append(_cmd("format.color", {"color": colour(text.get("color", "text"), theme)}))
        if text.get("spacing_pt") is not None:
            commands.append(_cmd("format.spacing", {"pt": text["spacing_pt"]}))
        if text.get("line_spacing") is not None:
            commands.append(_cmd("format.lineSpacing", {"lines": text["line_spacing"]}))
        commands.append(_cmd("format.align", {"align": text.get("align", "left")}))
        commands.append(_cmd("format.autofit", {"mode": "none"}))
        commands.append(_cmd("format.margins", {"left": 0, "top": 0, "right": 0, "bottom": 0}))
        commands.append(_cmd("format.anchor", {"anchor": text.get("anchor", "top")}))
        x, y, w, h = part["rect"]
        commands.append(_cmd("shape.setBounds", {"x": x, "y": y, "w": w, "h": h, "ids": [sid]}))

    for step in asset.get("motion", []):
        params = {
            "effect": step["effect"],
            "ids": [ids[name] for name in step["parts"]],
            "start": step.get("start", "onClick"),
            "duration": step["duration_ms"],
        }
        if step.get("class"):
            params["class"] = step["class"]
        if step.get("option"):
            params["option"] = step["option"]
        if step.get("delay_ms"):
            params["delay"] = step["delay_ms"]
        commands.append(_cmd("animation.add", params))

    return commands


# ---------------------------------------------------------------------------
# DeckCraft driver


def _run(cli: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([str(cli), *args], capture_output=True, text=True, encoding="utf-8", check=False)


def run_command_file(cli: Path, path: Path, *, source: Path | None, save: Path | None) -> tuple[list[dict], str]:
    args = ["run"]
    if source is not None:
        args += ["--in", str(source)]
    args += ["--cmd-file", str(path), "--print"]
    if save is not None:
        args += ["--save", str(save)]
    result = _run(cli, args)
    if result.returncode != 0:
        raise NativeArtUnavailable(COMPILE_FAILED, f"{path.name}: {result.stderr.strip() or result.stdout.strip()}")
    answers = []
    for line in result.stdout.splitlines():
        if "\u2192" in line:
            command, _, payload = line.partition("\u2192")
            try:
                answers.append({"cmd": command.strip(), "answer": json.loads(payload.strip())})
            except json.JSONDecodeError:
                answers.append({"cmd": command.strip(), "answer": payload.strip()})
    return answers, result.stdout


def inspect_slide(cli: Path, deck: Path) -> dict:
    result = _run(cli, ["run", "--in", str(deck), "--cmd", "slide.inspect", "--print"])
    if result.returncode != 0:
        raise NativeArtUnavailable(COMPILE_FAILED, f"slide.inspect failed: {result.stderr.strip()}")
    for line in result.stdout.splitlines():
        if "\u2192" in line:
            return json.loads(line.partition("\u2192")[2].strip())
    raise NativeArtUnavailable(COMPILE_FAILED, "slide.inspect returned no JSON")


def _walk(shapes: list[dict]):
    for shape in shapes:
        yield shape
        yield from _walk(shape.get("children") or [])


# ---------------------------------------------------------------------------
# Compile


def validate_motion(asset: dict) -> list[str]:
    """Durations must sit inside the design-system band for their class."""
    bands = load_design_system()["motion"]["duration_ms"]
    warnings = []
    for step in asset.get("motion", []):
        klass = step.get("class") or ("emphasis" if step["effect"] in ("pulse", "spin", "growShrink") else "enter")
        role = "emphasis" if klass == "emphasis" else "enter"
        low, high = bands[role]["band"]
        if not low <= step["duration_ms"] <= high:
            warnings.append(
                f"{step['parts'][0]}/{step['effect']}: {step['duration_ms']} ms outside {role} band {low}-{high}"
            )
    return warnings


def compile_spec(spec_path: Path, out_dir: Path) -> dict:
    cli = require_available()
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    asset = spec["asset"]["native_art"]
    theme = load_theme(asset["stage"]["theme"])
    art_parts = [p for p in asset["parts"] if p["role"] == "art"]

    out_dir = Path(out_dir)
    work = out_dir / "native-art-work"
    work.mkdir(parents=True, exist_ok=True)

    stage1 = stage1_commands(asset, theme, len(art_parts))
    stage1_path = work / "stage1.commands.txt"
    stage1_path.write_text("\n".join(stage1) + "\n", encoding="utf-8")

    answers1, _ = run_command_file(cli, stage1_path, source=None, save=work / "stage1.deckcraft")
    slide = inspect_slide(cli, work / "stage1.deckcraft")
    by_name = {s["name"]: s for s in _walk(slide["shapes"])}
    missing = [p["name"] for p in asset["parts"] if p["name"] not in by_name]
    if missing:
        raise NativeArtUnavailable(COMPILE_FAILED, f"parts missing after stage 1: {missing}")
    ids = {name: shape["id"] for name, shape in by_name.items()}

    # Merge Shapes re-ids its result: DeckCraft does not error on a stale id, it
    # accepts the command and the animation is silently lost on convert. So the
    # compiler merges first, then re-reads the ids before adding motion.
    ops = ops_commands(asset, ids)
    if ops:
        ops_path = work / "stage2.commands.txt"
        ops_path.write_text("\n".join(ops) + "\n", encoding="utf-8")
        run_command_file(cli, ops_path, source=work / "stage1.deckcraft", save=work / "stage2.deckcraft")
        merged = inspect_slide(cli, work / "stage2.deckcraft")
        by_name = {s["name"]: s for s in _walk(merged["shapes"])}
        missing = [p["name"] for p in asset["parts"] if p["role"] != "helper" and p["name"] not in by_name]
        if missing:
            raise NativeArtUnavailable(COMPILE_FAILED, f"parts missing after merge: {missing}")
        ids = {name: shape["id"] for name, shape in by_name.items()}
        base_deck = work / "stage2.deckcraft"
    else:
        ops_path = None
        base_deck = work / "stage1.deckcraft"

    stage2 = text_and_motion_commands(asset, ids, theme)
    stage2_path = work / "stage3.commands.txt"
    stage2_path.write_text("\n".join(stage2) + "\n", encoding="utf-8")
    run_command_file(cli, stage2_path, source=base_deck, save=work / "art.deckcraft")

    final = inspect_slide(cli, work / "art.deckcraft")
    final_names = {s["name"]: s for s in _walk(final["shapes"])}

    deck = out_dir / f"{spec['asset']['id']}.deckcraft"
    pptx = out_dir / f"{spec['asset']['id']}.pptx"
    shutil.copyfile(work / "art.deckcraft", deck)
    converted = _run(cli, ["convert", str(deck), str(pptx)])
    if converted.returncode != 0:
        raise NativeArtUnavailable(COMPILE_FAILED, f"convert failed: {converted.stderr.strip()}")

    # Parity: the same deck saved straight to .pptx must carry the same parts.
    parity = _run(cli, ["run", "--in", str(deck), "--save", str(work / "parity.pptx")])
    if parity.returncode != 0:
        raise NativeArtUnavailable(COMPILE_FAILED, f"parity save failed: {parity.stderr.strip()}")

    anims = final.get("animations", [])
    manifest = {
        "ok": True,
        "asset": spec["asset"]["id"],
        "route": "native_art/deckcraft",
        "deckcraft": str(deck),
        "pptx": str(pptx),
        "cli": str(cli),
        "parts": {
            "declared": len(asset["parts"]),
            "art": len(art_parts),
            "helpers": len([p for p in asset["parts"] if p["role"] == "helper"]),
            "copy": len([p for p in asset["parts"] if p["role"] == "copy"]),
            "stage": len([p for p in asset["parts"] if p["role"] == "stage"]),
            "present_in_deckcraft": len(final_names),
        },
        "shapes": [
            {"name": n, "id": s["id"], "kind": s["kind"], "box": s.get("box")}
            for n, s in final_names.items()
        ],
        "animations": anims,
        "motion_warnings": validate_motion(asset),
        "commands": {"stage1": len(stage1), "stage2_ops": len(ops), "stage3_text_motion": len(stage2),
                     "total": len(stage1) + len(ops) + len(stage2)},
        "answers_stage1": len(answers1),
        "bytes": {"deckcraft": deck.stat().st_size, "pptx": pptx.stat().st_size},
        "sha256": {"deckcraft": hashlib.sha256(deck.read_bytes()).hexdigest(),
                   "pptx": hashlib.sha256(pptx.read_bytes()).hexdigest()},
    }
    (out_dir / "native-art-manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", nargs="?", type=Path, help="native_art_spec.json")
    parser.add_argument("--out", type=Path, default=Path("."), help="output directory")
    parser.add_argument("--check", action="store_true", help="print availability JSON and exit 0")
    parser.add_argument("--emit-only", action="store_true", help="write commands.txt files, run nothing")
    args = parser.parse_args(argv)

    if args.check:
        print(json.dumps(availability(), indent=1))
        return 0
    if not args.spec:
        parser.error("spec is required unless --check")
    try:
        if args.emit_only:
            asset = json.loads(args.spec.read_text(encoding="utf-8"))["asset"]["native_art"]
            theme = load_theme(asset["stage"]["theme"])
            art = len([p for p in asset["parts"] if p["role"] == "art"])
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "stage1.commands.txt").write_text("\n".join(stage1_commands(asset, theme, art)) + "\n", encoding="utf-8")
            print(f"emitted {len(stage1_commands(asset, theme, art))} stage-1 commands to {args.out}")
            return 0
        manifest = compile_spec(args.spec, args.out)
    except NativeArtUnavailable as exc:
        print(json.dumps({"ok": False, "code": exc.code, "detail": exc.detail}))
        return 2
    print(json.dumps({"ok": True, "pptx": manifest["pptx"], "bytes": manifest["bytes"]["pptx"],
                      "art_parts": manifest["parts"]["art"], "animations": len(manifest["animations"]),
                      "motion_warnings": len(manifest["motion_warnings"])}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
