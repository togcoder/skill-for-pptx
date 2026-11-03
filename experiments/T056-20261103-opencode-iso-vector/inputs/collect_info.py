import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/T056-20261103-opencode-iso-vector"
ART = EXP / "artifacts"
PREV = EXP / "preview"
EXE = Path(r"D:\artcraft\VectorCraft\vectorcraft-cli.exe")

info = {}
for svg in sorted(ART.glob("*.svg")):
    raw = subprocess.run(
        [str(EXE), "info", str(svg)], capture_output=True, check=True
    ).stdout
    text = raw.decode("utf-8")
    data = json.loads(text)
    info[svg.name] = {
        "warnings": data.get("warnings", []),
        "fonts": [
            {"family": f["family"], "status": f["status"], "missing": f["missing"]}
            for f in data.get("fonts", [])
        ],
        "kinds": data.get("kinds", {}),
        "artboards": data.get("artboards", []),
    }

(ART / "info.json").write_text(
    json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

lines = []
for folder in (ART, PREV):
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix.lower() in {".svg", ".png", ".json"}:
            digest = hashlib.sha256(f.read_bytes()).hexdigest()
            lines.append(f"{digest}  {f.relative_to(EXP).as_posix()}")
(ART / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("info and hashes written", len(lines))
