#!/usr/bin/env python3
"""Check the lab's repository layout (lab/standards/OUTPUTS.md, lab/PROTOCOL.md).

Fails on:
- unexpected entries at the repository root (outputs belong in a task's
  experiments/<ID>-…/artifacts/ or in git-ignored workspace/);
- office, media or archive files at the root;
- new files in the frozen legacy output/ folder;
- a domain folder without DOMAIN.md, or a domain missing from domains/README.md;
- an experiment folder whose name does not start with a registered task ID,
  or a task from T040 on without REPORT.md;
- a task ID that appears on more than one row of research/tasks/INDEX.md;
- a Markdown file that is not valid UTF-8, starts with a byte-order mark,
  contains C0/C1 control characters, or contains the mojibake markers
  "Ã", "â€", "á»", "Ä‘" outside an inline code span. A line that quotes the
  damage on purpose may end with the HTML comment `<!-- allow-mojibake -->`;
  the marker check skips that line and still checks the rest of the file.

Warns (does not fail) on:
- a committed file larger than 2 MiB, or a task's committed files adding up
  to more than 10 MiB. The cap is the owner's T065 rule; see
  lab/standards/OUTPUTS.md.

    python3 lab/tools/check_layout.py          # exit 1 and a list of problems
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ROOT_ALLOWED={".claude-plugin",".github",".gitignore",".git","AGENTS.md","HANDOFF.md","README.md","archive","commands",
              "docs","domains","examples","experiments","knowledge","lab","output","research","scripts","skills",
              "tests","workspace","local-media",".venv","build","node_modules","__pycache__",".env"}
MEDIA=re.compile(r"\.(pptx|potx|docx|xlsx|svg|pdf|png|jpe?g|gif|mp4|mov|zip)$",re.I)
OUTPUT_FROZEN_BEFORE="2026-11-01"
NEW_REPORT_FROM=40
SKIP_DIRS={".git",".venv","node_modules","__pycache__","workspace","local-media","build"}

# A UTF-8 file read as cp1252/cp1258 and saved again leaves these sequences.
MOJIBAKE=("Ã","â€","á»","Ä‘")
INLINE_CODE=re.compile(r"`[^`\n]*`")
MARKER_ONLY=re.compile(r"^[\s,;/]*(?:and[\s,;/]*)?$")
ALLOW_MOJIBAKE="<!-- allow-mojibake -->"
BOM="\ufeff"
MAX_FILE_BYTES=2*1024*1024
MAX_TASK_BYTES=10*1024*1024


def _strip_marker_quotes(line: str) -> str:
    """Drop inline code spans that exist only to *name* the markers.

    `check_layout.py` documents the markers itself, and so do the task briefs
    and the CHANGELOG entry. Those spans hold a marker and separators and
    nothing else; a code span with real text keeps it, so damage inside
    `Hình 1 â€” â€¦` is still reported.
    """
    def replace(match):
        inner=match.group(0)[1:-1]
        rest=inner
        for marker in MOJIBAKE:
            rest=rest.replace(marker,"")
        return "" if MARKER_ONLY.match(rest) else match.group(0)
    return INLINE_CODE.sub(replace,line)


def _markdown_files():
    for p in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.relative_to(ROOT).parts):
            continue
        yield p


def _text_problems(path, limit=5):
    """Encoding problems in one Markdown file, as (line, kind, detail)."""
    out=[]
    try:
        raw=path.read_bytes()
    except OSError as exc:
        return [(0,"unreadable",str(exc))]
    try:
        text=raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [(0,"not utf-8",f"byte {exc.start}: {exc.reason}")]
    if text.startswith(BOM):
        out.append((1,"bom","file starts with a byte-order mark"))
        text=text[1:]
    for n,line in enumerate(text.splitlines(),1):
        if len(out)>=limit:
            return out
        for ch in line:
            code=ord(ch)
            if ch in "\t":
                continue
            if code<0x20 or 0x7f<=code<=0x9f:
                out.append((n,"control",f"U+{code:04X}"))
                break
        visible=_strip_marker_quotes(line)
        if ALLOW_MOJIBAKE in line:
            continue          # a line that quotes the damage on purpose
        hits=[m for m in MOJIBAKE if m in visible]
        if hits:
            out.append((n,"mojibake","".join(hits)))
    return out


def _index_ids():
    """(task ID, line number) for every task ID in the first column of INDEX.md."""
    index=ROOT/"research"/"tasks"/"INDEX.md"
    if not index.is_file():
        return None
    rows=[]
    for n,line in enumerate(index.read_text(encoding="utf-8").splitlines(),1):
        if not line.startswith("| "):
            continue
        cell=line.split("|")[1].strip()
        for tid in re.findall(r"^T\d{3}[a-z]?$",cell):
            rows.append((tid,n))
    return rows


def _duplicate_ids(rows):
    seen={}
    out=[]
    for tid,n in rows:
        if tid in seen:
            out.append(f"research/tasks/INDEX.md: task ID {tid} is used twice "
                       f"(rows {seen[tid]} and {n}); take the next free ID")
        else:
            seen[tid]=n
    return out


def _tracked_sizes():
    """List of (path, size) for committed files; None when git is unavailable."""
    try:
        raw=subprocess.run(["git","-C",str(ROOT),"ls-files","-z"],capture_output=True,
                           check=True,timeout=120).stdout
    except (OSError,subprocess.SubprocessError):
        return None
    files=[]
    for name in raw.decode("utf-8","surrogateescape").split("\0"):
        if not name:
            continue
        p=ROOT/name
        if p.is_file():
            files.append((name,p.stat().st_size))
    return files


def _size_warnings(files):
    out=[]
    per_task={}
    for name,size in files:
        if size>MAX_FILE_BYTES:
            out.append(f"{name}: {size/1048576:.1f} MB committed (cap 2 MB/file)")
        parts=Path(name).parts
        if len(parts)>1 and parts[0]=="experiments":
            task=parts[1].split("-")[0]
            per_task[task]=per_task.get(task,0)+size
    for task,size in sorted(per_task.items()):
        if size>MAX_TASK_BYTES:
            out.append(f"experiments/{task}: {size/1048576:.1f} MB committed (cap 10 MB/task)")
    return out


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
    rows=_index_ids()
    if rows is not None:
        out.extend(_duplicate_ids(rows))
    for path in _markdown_files():
        rel=path.relative_to(ROOT).as_posix()
        for line,kind,detail in _text_problems(path):
            where=f"{rel}:{line}" if line else rel
            out.append(f"{where}: {kind}: {detail}")
    return out


def warnings():
    files=_tracked_sizes()
    return [] if files is None else _size_warnings(files)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")   # the message may quote a marker
        except (AttributeError, ValueError):
            pass
    ps=problems()
    for p in ps:
        print(p)
    for w in warnings():
        print(f"warning: {w}")
    print("layout OK" if not ps else f"{len(ps)} layout problem(s)")
    return 1 if ps else 0


if __name__=="__main__":
    sys.exit(main())
