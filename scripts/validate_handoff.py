#!/usr/bin/env python3
"""Validate Handoff Contracts and Schemas (T036).

Verifies whether an intent brief, delegation contract, or critique report
matches the formal JSON schemas defined under ``lab/schemas/``.

Usage:
    python scripts/validate_handoff.py brief sample_brief.json
    python scripts/validate_handoff.py contract sample_contract.json
    python scripts/validate_handoff.py critique sample_critique.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCHEMA_MAP = {
    "brief": "intent_brief.schema.json",
    "contract": "handoff_contract.schema.json",
    "critique": "critique_report.schema.json",
}


def load_schema(kind: str) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[1]
    schema_name = SCHEMA_MAP.get(kind)
    if not schema_name:
        raise ValueError(f"Unknown schema kind '{kind}'. Valid kinds: {list(SCHEMA_MAP.keys())}")

    schema_file = repo_root / "lab" / "schemas" / schema_name
    if not schema_file.is_file():
        raise FileNotFoundError(f"Schema file missing: {schema_file}")

    return json.loads(schema_file.read_text(encoding="utf-8"))


def validate_dict(instance: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Lightweight deterministic validator without requiring external jsonschema package."""
    errors = []

    required = schema.get("required", [])
    for field in required:
        if field not in instance:
            errors.append(f"Missing required field: '{field}'")

    properties = schema.get("properties", {})
    for k, v in instance.items():
        if k in properties:
            prop_def = properties[k]
            expected_type = prop_def.get("type")
            if expected_type == "string" and not isinstance(v, str):
                errors.append(f"Field '{k}' expected string, got {type(v).__name__}")
            elif expected_type == "integer" and (not isinstance(v, int) or isinstance(v, bool)):
                errors.append(f"Field '{k}' expected integer, got {type(v).__name__}")
            elif expected_type == "number" and not isinstance(v, (int, float)):
                errors.append(f"Field '{k}' expected number, got {type(v).__name__}")
            elif expected_type == "boolean" and not isinstance(v, bool):
                errors.append(f"Field '{k}' expected boolean, got {type(v).__name__}")
            elif expected_type == "array" and not isinstance(v, list):
                errors.append(f"Field '{k}' expected list, got {type(v).__name__}")
            elif expected_type == "object" and not isinstance(v, dict):
                errors.append(f"Field '{k}' expected dict, got {type(v).__name__}")

            # Check enum
            if "enum" in prop_def and v not in prop_def["enum"]:
                errors.append(f"Field '{k}' value '{v}' not in allowed enum: {prop_def['enum']}")

    return errors


def validate_file(kind: str, file_path: Path) -> list[str]:
    schema = load_schema(kind)
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return validate_dict(data, schema)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["brief", "contract", "critique"], help="Schema kind to validate")
    parser.add_argument("file", type=Path, help="JSON file to validate")

    args = parser.parse_args()
    if not args.file.is_file():
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        errors = validate_file(args.kind, args.file)
        if errors:
            print(f"Validation FAILED for {args.file} against {args.kind} schema:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print(f"Validation PASSED: {args.file} matches {args.kind} schema.")
    except Exception as exc:
        print(f"Error during validation: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
