#!/usr/bin/env python3
"""CLI validation for native-timeline-plan v0.1."""
import argparse
import json
from pathlib import Path

try:
    from .pack_timeline import validate_timeline
except ImportError:
    from pack_timeline import validate_timeline


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan",type=Path)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text(encoding="utf-8"))
    errors=validate_timeline(plan)
    if errors:
        print(json.dumps({"valid":False,"errors":errors},ensure_ascii=False,indent=2))
        return 1
    print(json.dumps({"valid":True,"slides":len(plan["slides"])},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
