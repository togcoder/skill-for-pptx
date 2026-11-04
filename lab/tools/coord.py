#!/usr/bin/env python3
"""Coordination between agents and the owner (T083).

Three commands, one registry (lab/capabilities.json), one decision log
(lab/DECISIONS.md):

    python lab/tools/coord.py claim --agent opencode --slug morph-rules \
        --title "[pptx] Morph matching rulebook" [--id T074] [--capability pptx.morph]
    python lab/tools/coord.py board            # who works on what, collisions
    python lab/tools/coord.py check            # registry + single-writer checks

`claim` reserves the task ID against main AND every open branch (a row that
exists only on an unmerged branch still counts), creates the branch and a
separate worktree under the shared checkout's workspace/, commits the INDEX
row and claim file, pushes, and prints the briefing: the capability's owner
files, the decisions that bind it, other branches touching it, and the
owner's open feedback.

check_layout.py imports registry_problems(), single_writer_problems() and
import_warnings() from here.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=ROOT/"lab"/"capabilities.json"
DECISIONS=ROOT/"lab"/"DECISIONS.md"
INDEX="research/tasks/INDEX.md"
SCRIPT_EXT={".py",".ps1",".mjs",".sh"}
ROLES={"canonical","support","experimental","shim","tool","fixture","frozen"}
PRODUCT_ROLES={"canonical","support"}
WORK_BRANCH=re.compile(r"^(?:origin/)?work/(T\d{3})[a-c]?-([a-z0-9]+)-")
ROW_ID=re.compile(r"^\| (T\d{3})[a-c]?\b(.*)$",re.M)
# Files every task touches; they are not a collision.
SHARED_FILES=("research/tasks/INDEX.md","docs/CHANGELOG.md")
SHARED_PREFIXES=("research/claims/","research/reviews/","experiments/","research/feedback/")
ACTIVE_DAYS=14


def git(*args,cwd=ROOT,check=True):
    r=subprocess.run(["git",*args],cwd=cwd,capture_output=True,text=True,encoding="utf-8",errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def load_registry(root=ROOT):
    return json.loads((root/"lab"/"capabilities.json").read_text(encoding="utf-8"))


def file_owners(reg):
    """path -> list of (capability id, role)."""
    owners={}
    for cap in reg["capabilities"]:
        for path,role in cap["files"].items():
            owners.setdefault(path,[]).append((cap["id"],role))
    return owners


# ---------------------------------------------------------------- checks

def registry_problems(root=ROOT,reg=None):
    reg=reg or load_registry(root)
    out=[]
    owners=file_owners(reg)
    present={f"scripts/{p.name}" for p in (root/"scripts").iterdir()
             if p.is_file() and p.suffix in SCRIPT_EXT}
    for path in sorted(present-set(owners)):
        out.append(f"{path}: not registered in lab/capabilities.json "
                   "(extend the canonical module of its capability, or ask the lead to register it; D002)")
    for path,caps in sorted(owners.items()):
        if path not in present:
            out.append(f"lab/capabilities.json: {path} is registered but does not exist")
        if len(caps)>1:
            out.append(f"lab/capabilities.json: {path} has {len(caps)} owners {[c for c,_ in caps]}; one owner per file")
        for cap,role in caps:
            if role not in ROLES:
                out.append(f"lab/capabilities.json: {path} in {cap} has unknown role '{role}'")
    return out


def import_warnings(root=ROOT,reg=None):
    """A product module (canonical/support) importing experimental or frozen code."""
    reg=reg or load_registry(root)
    role={Path(p).stem:caps[0][1] for p,caps in file_owners(reg).items() if p.endswith(".py")}
    out=[]
    for stem,r in sorted(role.items()):
        if r not in PRODUCT_ROLES:
            continue
        path=root/"scripts"/f"{stem}.py"
        if not path.is_file():
            continue
        src=path.read_text(encoding="utf-8",errors="replace")
        for mod in sorted(set(re.findall(r"^\s*(?:import|from)\s+([a-z_0-9]+)",src,re.M))):
            if role.get(mod) in ("experimental","frozen"):
                out.append(f"scripts/{stem}.py ({r}) imports {mod} ({role[mod]})")
    return out


def current_branch(root=ROOT):
    for var in ("GITHUB_HEAD_REF","GITHUB_REF_NAME"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        return git("rev-parse","--abbrev-ref","HEAD",cwd=root).strip()
    except RuntimeError:
        return ""


def changed_since_main(root=ROOT):
    """Files changed on this branch since it left origin/main, or None if unknown."""
    try:
        base=git("merge-base","origin/main","HEAD",cwd=root).strip()
        return [l for l in git("diff","--name-only",base,"HEAD",cwd=root).splitlines() if l]
    except RuntimeError:
        return None


def single_writer_problems(branch,changed,reg):
    m=WORK_BRANCH.match(branch or "")
    if not m or changed is None:
        return []
    agent=m.group(2)
    if agent in reg.get("lead",[]):
        return []
    guarded=set(reg.get("single_writer",[]))
    return [f"{p}: written by the lead only (D006); report through your INDEX row, REPORT, "
            f"CHANGELOG and PR description instead (branch {branch})" for p in changed if p in guarded]


# ---------------------------------------------------------------- task IDs

def ids_in_index(text):
    """Task numbers that have a row, ignoring the '*next free ID*' placeholder row."""
    return {int(t[1:]) for t,rest in ROW_ID.findall(text) if "next free ID" not in rest}


def remote_work_branches(root=ROOT):
    out=git("for-each-ref","--format=%(refname:short) %(committerdate:unix)","refs/remotes/origin/work",cwd=root)
    return [(n,int(t)) for n,t in (l.split() for l in out.splitlines() if l.strip())]


def all_claimed_ids(root=ROOT):
    """IDs on main's INDEX, on every open branch's INDEX, and in branch names."""
    ids=set()
    texts=[git("show",f"origin/main:{INDEX}",cwd=root)]
    for name,_ in remote_work_branches(root):
        m=WORK_BRANCH.match(name)
        if m:
            ids.add(int(m.group(1)[1:]))
        texts.append(git("show",f"{name}:{INDEX}",cwd=root,check=False))
    for t in texts:
        ids|=ids_in_index(t)
    return ids


def next_free_id(ids):
    return f"T{max(ids,default=0)+1:03d}"


def reserved_rows(root=ROOT):
    """ID -> row text for rows whose status says 'open', on main or any branch."""
    rows={}
    for ref in ["origin/main"]+[n for n,_ in remote_work_branches(root)]:
        for tid,rest in ROW_ID.findall(git("show",f"{ref}:{INDEX}",cwd=root,check=False)):
            cells=[c.strip() for c in rest.split("|")]
            if len(cells)>4 and cells[4].startswith("open"):
                rows.setdefault(tid,f"| {tid}{rest}")
    return rows


# ---------------------------------------------------------------- board

def branch_files(name,root=ROOT):
    try:
        base=git("merge-base","origin/main",name,cwd=root).strip()
        return [l for l in git("diff","--name-only",base,name,cwd=root).splitlines() if l]
    except RuntimeError:
        return []


def collisions(branch_to_files,owners):
    """Pairs of branches that touch the same non-shared file or capability."""
    def caps(files):
        return {c for f in files for c,_ in owners.get(f,[])}
    def own(files):
        return {f for f in files if f not in SHARED_FILES and not f.startswith(SHARED_PREFIXES)}
    names=sorted(branch_to_files)
    out=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            fa,fb=branch_to_files[a],branch_to_files[b]
            same_files=sorted(own(fa)&own(fb))
            same_caps=sorted(caps(fa)&caps(fb))
            if same_files or same_caps:
                out.append((a,b,same_files,same_caps))
    return out


def shared_checkout_dirty(root=ROOT):
    first=git("worktree","list","--porcelain",cwd=root).splitlines()[0]
    main_path=Path(first.split(" ",1)[1])
    dirty=[l[3:] for l in git("status","--porcelain",cwd=main_path).splitlines() if l and not l.startswith("??")]
    return main_path,dirty


def open_feedback(root=ROOT):
    items=[]
    for f in sorted((root/"research"/"feedback").glob("*.md")):
        if f.name=="README.md":
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("- [ ]"):
                items.append(f"{f.name}: {line[6:].strip()}")
    return items


def board(root=ROOT,days=ACTIVE_DAYS):
    reg=load_registry(root)
    owners=file_owners(reg)
    now=dt.datetime.now().timestamp()
    active={}
    for name,ts in remote_work_branches(root):
        if now-ts>days*86400:
            continue
        files=branch_files(name,root)
        if files:
            active[name]=files
    lines=["# Board (coord.py board)",""]
    lines.append(f"Active work branches (commits in the last {days} days, not in main): {len(active)}")
    for name,files in sorted(active.items()):
        caps=sorted({c for f in files for c,_ in owners.get(f,[])})
        lines.append(f"- {name.replace('origin/','')}: {len(files)} files; capabilities: {', '.join(caps) or '—'}")
    col=collisions(active,owners)
    lines.append("")
    lines.append(f"Collisions: {len(col)}")
    for a,b,fs,cs in col:
        lines.append(f"- {a.replace('origin/','')} × {b.replace('origin/','')}: "
                     f"files {fs or '—'}; capabilities {cs or '—'}")
    path,dirty=shared_checkout_dirty(root)
    lines.append("")
    lines.append(f"Shared checkout {path}: {'clean' if not dirty else str(len(dirty))+' uncommitted change(s): '+', '.join(dirty)}")
    fb=open_feedback(root)
    lines.append("")
    lines.append(f"Owner feedback and questions still open: {len(fb)}")
    lines.extend(f"- {i}" for i in fb)
    return "\n".join(lines),active,col


# ---------------------------------------------------------------- claim

def decision_rows(ids):
    if not DECISIONS.is_file():
        return []
    rows=[]
    for line in DECISIONS.read_text(encoding="utf-8").splitlines():
        m=re.match(r"^\| (D\d{3}) \| (.+?) \|",line)
        if m and m.group(1) in ids:
            rows.append(f"{m.group(1)}: {m.group(2)}")
    return rows


def briefing(tid,branch,wt,capability,reg,active):
    out=[f"Claimed {tid} on {branch}.",
         f"Work ONLY in {wt} (never in the shared checkout; D007).",""]
    always={"D001","D006","D007","D008"}
    cap=next((c for c in reg["capabilities"] if c["id"]==capability),None)
    if capability and not cap:
        out.append(f"Capability '{capability}' is not registered: ask the lead before writing new modules (D002).")
    if cap:
        out.append(f"Capability {cap['id']}: {cap['title']}")
        for f,r in cap["files"].items():
            out.append(f"  {r:12s} {f}")
        for o in cap.get("overlaps",[]):
            out.append(f"  OVERLAP: {o['note']}")
        if cap.get("open_tasks"):
            out.append(f"  Related reserved tasks: {', '.join(cap['open_tasks'])}")
        always|=set(cap.get("decisions",[]))
        owners=file_owners(reg)
        others=[n for n,files in active.items() if any(c==cap["id"] for f in files for c,_ in owners.get(f,[]))]
        out.append(f"  Other active branches on this capability: {', '.join(others) or 'none'}")
        out.append("")
    out.append("Decisions that bind you (lab/DECISIONS.md):")
    out.extend(f"  {r}" for r in decision_rows(always))
    fb=open_feedback()
    if fb:
        out.append("")
        out.append("Owner feedback still open (research/feedback/):")
        out.extend(f"  {i}" for i in fb)
    out.append("")
    out.append("Your brief: docs/ROADMAP.md or docs/SCRIPT_TRACK.md. Report through INDEX row, REPORT, "
               "CHANGELOG and the PR description; do not edit HANDOFF/ROADMAP (D006).")
    return "\n".join(out)


def claim(agent,slug,title,tid=None,capability=None,dry_run=False):
    agent=agent.lower()
    if not re.fullmatch(r"[a-z0-9]+",agent) or not re.fullmatch(r"[a-z0-9-]+",slug):
        raise SystemExit("agent: lowercase letters/digits; slug: lowercase letters, digits, hyphens")
    git("fetch","origin","--prune")
    ids=all_claimed_ids()
    reserved=reserved_rows()
    if tid:
        if tid not in reserved:
            raise SystemExit(f"{tid} is not an open reserved task on main or any branch; omit --id to take {next_free_id(ids)}")
        if any(WORK_BRANCH.match(n) and WORK_BRANCH.match(n).group(1)==tid for n,_ in remote_work_branches()):
            raise SystemExit(f"{tid} already has a work branch: someone claimed it")
    else:
        tid=next_free_id(ids)
    branch=f"work/{tid}-{agent}-{slug}"
    main_path,_=shared_checkout_dirty()
    wt=main_path/"workspace"/tid
    reg=load_registry()
    _,active,_=board()
    if dry_run:
        print(f"[dry run] would create {branch} at {wt}\n")
        print(briefing(tid,branch,wt,capability,reg,active))
        return tid
    git("worktree","add","-b",branch,str(wt),"origin/main")
    idx=wt/INDEX
    text=idx.read_text(encoding="utf-8")
    today=dt.date.today().isoformat()
    row=f"| {tid} | {title} | {agent} | `{branch}` | claimed | `experiments/{tid}-{today.replace('-','')}-{agent}-{slug}/REPORT.md` |"
    m=re.search(rf"^\| {tid} \|.*$",text,re.M)
    nxt=next_free_id(ids|{int(tid[1:])})
    if m and "next free ID" not in m.group(0):
        text=text[:m.start()]+row+text[m.end():]
    else:
        text=re.sub(r"^\| T\d{3} \| \*next free ID\*.*$",lambda _:row+f"\n| {nxt} | *next free ID* | | | | |",text,count=1,flags=re.M)
    text=re.sub(r"next free ID \(\*\*T\d{3}\*\*\)",f"next free ID (**{nxt}**)",text)
    idx.write_text(text,encoding="utf-8")
    cl=wt/"research"/"claims"/f"{tid}-{agent}-{today.replace('-','')}.md"
    cl.write_text(f"# Claim — {tid} {title}\n\n- Agent: {agent}\n- Branch: `{branch}`\n- Started: {today}\n"
                  f"- Capability: {capability or 'not given'}\n- Status: claimed\n",encoding="utf-8")
    git("add",INDEX,str(cl.relative_to(wt)),cwd=wt)
    git("commit","-m",f"Claim {tid} {title}",cwd=wt)
    r=subprocess.run(["git","push","-u","origin",branch],cwd=wt,capture_output=True,text=True)
    if r.returncode:
        raise SystemExit(f"push failed, the claim is NOT visible to others: {r.stderr.strip()}")
    print(briefing(tid,branch,wt,capability,reg,active))
    return tid


def main(argv=None):
    for s in (sys.stdout,sys.stderr):
        try:
            s.reconfigure(encoding="utf-8",errors="backslashreplace")
        except (AttributeError,ValueError):
            pass
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=ap.add_subparsers(dest="cmd",required=True)
    c=sub.add_parser("claim")
    c.add_argument("--agent",required=True)
    c.add_argument("--slug",required=True)
    c.add_argument("--title",required=True,help='with the domain in brackets, e.g. "[pptx] Morph rules"')
    c.add_argument("--id",help="a reserved open task ID, e.g. T074")
    c.add_argument("--capability",help="registry id, e.g. pptx.morph")
    c.add_argument("--dry-run",action="store_true")
    b=sub.add_parser("board")
    b.add_argument("--days",type=int,default=ACTIVE_DAYS)
    sub.add_parser("check")
    a=ap.parse_args(argv)
    if a.cmd=="claim":
        claim(a.agent,a.slug,a.title,a.id,a.capability,a.dry_run)
    elif a.cmd=="board":
        git("fetch","origin","--prune")
        print(board(days=a.days)[0])
    else:
        reg=load_registry()
        ps=registry_problems(reg=reg)+single_writer_problems(current_branch(),changed_since_main(),reg)
        for p in ps:
            print(p)
        for w in import_warnings(reg=reg):
            print(f"warning: {w}")
        print("coordination OK" if not ps else f"{len(ps)} coordination problem(s)")
        return 1 if ps else 0
    return 0


if __name__=="__main__":
    sys.exit(main())
