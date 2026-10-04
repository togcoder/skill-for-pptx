#!/usr/bin/env python3
"""Run the frozen H001 checker, replacing only the candidate input path."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
checker = root / 'experiments/H001/verify_package.py'
source = checker.read_text()
old = 'DECK = ROOT / "output/PPTX_Motion_Lab_H001.pptx"'
assert source.count(old) == 1
candidate = str(Path(sys.argv[1]).resolve())
source = source.replace(old, 'DECK = Path(' + repr(candidate) + ')')
exec(compile(source, str(checker), 'exec'), {'__file__': str(checker), '__name__': '__main__'})
