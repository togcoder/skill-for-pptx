"""Aggregate the T058 run evidence into one machine-readable summary."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "artifacts" / "runs"
OUT = HERE / "artifacts" / "evidence_summary.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    steps = d.get("steps", [])
    rows = []
    for s in steps:
        row = {
            "index": s.get("index"),
            "action": s.get("action"),
            "shape": (s.get("shape") or {}).get("name"),
            "ok": s.get("ok"),
            "reason": (s.get("assert") or {}).get("reason"),
        }
        diff = s.get("diff") or {}
        if diff.get("inside"):
            row["inside_pct"] = diff["inside"].get("pct_changed")
            row["share_inside"] = diff.get("share_inside")
            row["outside_pct"] = (diff.get("outside") or {}).get("pct_changed")
        if diff.get("whole"):
            row["whole_pct"] = diff["whole"].get("pct_changed")
        rows.append(row)
    return {
        "run": path.parent.name,
        "evidence": str(path.relative_to(HERE)),
        "evidence_sha256": sha256(path),
        "deck": d.get("deck"),
        "powerpoint": {k: (d.get("powerpoint") or {}).get(k)
                       for k in ("version", "build", "slide_count",
                                 "slide_width_pt", "slide_height_pt")},
        "show": {k: (d.get("show") or {}).get(k) for k in ("class", "hwnd", "dpi")},
        "mapping": (d.get("mapping") or {}).get("calibration"),
        "claims": d.get("claims"),
        "steps": rows,
        "passed": sum(1 for s in steps if s.get("ok")),
        "total": len(steps),
        "error": d.get("error"),
        "teardown": d.get("teardown"),
    }


def main() -> int:
    runs = [summarize(p) for p in sorted(RUNS.glob("*/evidence.json"))]
    summary = {
        "schema": "pptx-interactive-show-summary/1",
        "task": "T058",
        "runs": runs,
        "totals": {
            "runs": len(runs),
            "steps": sum(r["total"] for r in runs),
            "passed": sum(r["passed"] for r in runs),
            "failed": sum(r["total"] - r["passed"] for r in runs),
        },
    }
    neg = HERE / "artifacts" / "negatives"
    if neg.is_dir():
        summary["open_checks"] = []
        for p in sorted(neg.glob("*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            summary["open_checks"].append({
                "deck": Path(d.get("deck", "")).name,
                "sha256": d.get("sha256"),
                "opened": d.get("opened"),
                "main_effects_total": d.get("main_effects_total"),
                "interactive_sequences_total": d.get("interactive_sequences_total"),
                "error": d.get("error"),
            })
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary["totals"], indent=2))
    print("wrote", OUT, OUT.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
