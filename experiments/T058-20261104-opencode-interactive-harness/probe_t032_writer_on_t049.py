"""Reproduce the T032 writer failure on the known-good T049 deck.

`interactive_triggers.apply_interactive_triggers` is applied to a copy of the
T049 deck (which PowerPoint opens without repair) and the result is checked with
`interactive_show_harness.py open-check`. The output file is kept in
`artifacts/negatives/` as evidence that the failure is the writer's, not the
synthetic base deck's.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from lxml import etree as ET  # noqa: E402

from scripts import interactive_triggers as trig  # noqa: E402

HERE = Path(__file__).resolve().parent
SRC = (ROOT / "experiments" / "T049-20261101-antigravity-advanced-interactivity"
       / "artifacts" / "one_slide_games_suite.pptx")
OUT = HERE / "artifacts" / "negatives" / "t049_plus_t032_writer.pptx"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SRC) as z:
        items = [(i.filename, i.compress_type, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for name, compress_type, data in items:
            if name == "ppt/slides/slide1.xml":
                root = ET.fromstring(data)
                trig.apply_interactive_triggers(root, [{
                    "trigger": "Reset_Button_S1",
                    "action": "hide",
                    "targets": ["Reward_1"],
                    "preset": "fade",
                    "duration_ms": 300,
                }])
                data = ET.tostring(root, xml_declaration=True, encoding="UTF-8",
                                   standalone=True)
            z.writestr(name, data, compress_type=compress_type)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
