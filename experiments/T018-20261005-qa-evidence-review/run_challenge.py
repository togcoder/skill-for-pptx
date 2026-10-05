"""Run frozen synthetic cases against a verifier module, with machine receipts."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from qa_evidence_cases import challenge_cases


def run(verifier):
    spec = importlib.util.spec_from_file_location("tested_verifier", verifier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = []
    for name, manifest, evidence, parse, click in challenge_cases():
        row = {"case": name, "expected_parse": parse, "expected_click": click}
        try:
            result = module.verify(manifest, evidence)
            actual = result["claims"]
            row.update(actual_parse=actual["native_application_parse_verified"],
                       actual_click=actual["native_click_execution_verified"])
            row["correct"] = row["actual_parse"] == parse and row["actual_click"] == click
        except Exception as exc:
            row.update(correct=False, error=type(exc).__name__ + ": " + str(exc))
        rows.append(row)
    return {"evidence_kind": "synthetic-verifier-challenge", "native_playback_tested": False,
            "cases": rows, "correct": sum(r["correct"] for r in rows), "total": len(rows),
            "false_click_passes": sum(r.get("actual_click", False) and not r["expected_click"] for r in rows),
            "crashes": sum("error" in r for r in rows)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verifier", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.verifier)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))
