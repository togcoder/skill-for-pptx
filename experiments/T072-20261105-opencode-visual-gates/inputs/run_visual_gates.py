"""T072 evidence run: visual gates on the T068, T066 and T069a decks."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

CASES = [
    ("t068", ROOT / "experiments/T068-20261104-antigravity-deck-director/artifacts/T068_directed.pptx",
     ROOT / "experiments/T068-20261104-antigravity-deck-director/preview"),
    ("t066", ROOT / "experiments/T066-20261104-opencode-triet-hoc-ch1/artifacts/T066-Triet-hoc-Mac-Lenin-Chuong-1.pptx",
     ROOT / "experiments/T066-20261104-opencode-triet-hoc-ch1/preview"),
    ("t069a", ROOT / "experiments/T069-20261104-opencode-directed-deck/artifacts/T069-directed-morph.pptx",
     ROOT / "experiments/T069-20261104-opencode-directed-deck/preview"),
]
OUT = ROOT / "experiments/T072-20261105-opencode-visual-gates/artifacts"
OUT.mkdir(parents=True, exist_ok=True)

for name, deck, render in CASES:
    out = OUT / f"{name}-visual.json"
    subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts/design_critic.py"),
                    str(deck), "--render", str(render), "-o", str(out)], check=True)
    data = json.loads(out.read_text(encoding="utf-8"))
    vis = [i for i in data["issues"] if i["code"].startswith("VIS-")]
    print(name, data["scores"], len(vis), sorted({i["code"] for i in vis}))
