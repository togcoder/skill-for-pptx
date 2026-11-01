"""Rebuild every T049 chart and copy its rendered PNG to a stable name."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHARTS = HERE.parent / "artifacts" / "charts"


def main() -> None:
    CHARTS.mkdir(parents=True, exist_ok=True)
    for name in ("training", "pr", "f1", "ablation", "latency"):
        spec = HERE / f"{name}.json"
        xlsx = CHARTS / f"{name}.xlsx"
        res = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "scripts" / "chart_forge.py"),
             "build", str(spec), "-o", str(xlsx), "--render", str(CHARTS)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if res.returncode != 0:
            print(name, "FAILED", res.stdout[-800:], res.stderr[-800:])
            continue
        data = json.loads(res.stdout[res.stdout.find("{"):])
        rendered = data.get("rendered") or []
        if not rendered:
            print(name, "no render", data.get("audit", {}).get("errors"))
            continue
        target = CHARTS / f"{name}.png"
        shutil.copyfile(rendered[-1], target)
        print(name, "->", target, data.get("chart_type"))


if __name__ == "__main__":
    main()
