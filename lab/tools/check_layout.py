#!/usr/bin/env python3
"""Check the lab's repository layout (lab/standards/OUTPUTS.md, lab/PROTOCOL.md).

Fails on:
- unexpected entries at the repository root (outputs belong in a task's
  experiments/<ID>-…/artifacts/ or in git-ignored workspace/);
- office, media or archive files at the root;
- new files in the frozen legacy output/ folder;
- a domain folder without DOMAIN.md, or a domain missing from domains/README.md;
- an experiment folder whose name does not start with a registered task ID,
  or a task from T040 on without REPORT.md.

    python3 lab/tools/check_layout.py          # exit 1 and a list of problems
"""
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ROOT_ALLOWED={".claude-plugin",".github",".gitignore",".git","AGENTS.md","HANDOFF.md","README.md","archive","commands",
              "docs","domains","examples","experiments","knowledge","lab","output","research","scripts","skills",
              "tests","workspace","local-media",".venv","build","node_modules","__pycache__",".env"}
MEDIA=re.compile(r"\.(pptx|potx|docx|xlsx|svg|pdf|png|jpe?g|gif|mp4|mov|zip)$",re.I)
OUTPUT_FROZEN_BEFORE="2026-11-01"
NEW_REPORT_FROM=40


def problems():
    out=[]
    for p in ROOT.iterdir():
        if p.name not in ROOT_ALLOWED:
            out.append(f"root: unexpected '{p.name}' (put outputs in experiments/<ID>/artifacts/ or workspace/)")
        elif p.is_file() and MEDIA.search(p.name):
            out.append(f"root: media/office file '{p.name}'")
    legacy=ROOT/"output"/"LEGACY.md"
    if legacy.is_file():
        allowed=set(re.findall(r"`([^`]+)`",legacy.read_text(encoding="utf-8")))
        for f in (ROOT/"output").iterdir():
            name=f.name
            if name!="LEGACY.md" and name not in allowed:
                out.append(f"output/: new file '{name}' (output/ is frozen; use experiments/<ID>/artifacts/)")
    reg=(ROOT/"domains"/"README.md").read_text(encoding="utf-8") if (ROOT/"domains"/"README.md").is_file() else ""
    for d in sorted((ROOT/"domains").iterdir()) if (ROOT/"domains").is_dir() else []:
        if not d.is_dir() or d.name.startswith("_"):
            continue
        if not (d/"DOMAIN.md").is_file():
            out.append(f"domains/{d.name}: missing DOMAIN.md")
        if f"`{d.name}`" not in reg:
            out.append(f"domains/{d.name}: not listed in domains/README.md")
    index=(ROOT/"research"/"tasks"/"INDEX.md").read_text(encoding="utf-8")
    ids=set(re.findall(r"^\| (T\d{3})[a-c]?\b",index,re.M))|set(re.findall(r"\b([EH]\d{3})\b",index))
    for e in sorted((ROOT/"experiments").iterdir()):
        if not e.is_dir():
            continue
        m=re.match(r"([TEH]\d{3})",e.name)
        if not m:
            out.append(f"experiments/{e.name}: name must start with a task ID")
            continue
        tid=m.group(1)
        if tid.startswith("T") and tid not in ids:
            out.append(f"experiments/{e.name}: task {tid} is not in research/tasks/INDEX.md")
        if tid.startswith("T") and int(tid[1:])>=NEW_REPORT_FROM and not (e/"REPORT.md").is_file():
            out.append(f"experiments/{e.name}: missing REPORT.md")
    return out


def main():
    ps=problems()
    for p in ps:
        print(p)
    print("layout OK" if not ps else f"{len(ps)} layout problem(s)")
    return 1 if ps else 0


if __name__=="__main__":
    sys.exit(main())
