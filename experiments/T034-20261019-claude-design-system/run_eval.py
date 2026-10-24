#!/usr/bin/env python3
"""T034 evaluation: one critic, two generator versions, many decks.

Arm "base" is the research tip before T034 (commit in base-commit.txt,
checked out read-only as a git worktree); arm "t034" is this tree. Both arms
direct the same static inputs; every output is graded by the *current*
design critic, so the yardstick is the same. Also critiques existing decks
(landscape) and compares PowerPoint and LibreOffice renders of one deck
(render calibration).

    python3 experiments/T034-20261019-claude-design-system/run_eval.py BASE_WORKTREE WORKDIR

Writes results.json and results.md next to this script.
"""
import collections
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import design_critic as dc  # noqa: E402

GENERATED={"MOT-DURATION","MOT-EASING","MOT-STAGGER","MOT-AMBIENT","MOT-CLICKS","MOT-MOVERS","MOT-EFFECTS",
           "MOT-STATIC","MOT-VOCAB","MOT-SETTLE","COL-GRAPHIC","MOT-TITLE","TEC-PRESET"}
LANDSCAPE={
    "fixture: report (raw)":"tests/fixtures/report_deck.pptx",
    "fixture: showcase (raw)":"tests/fixtures/motion_showcase_deck.pptx",
    "T019 director output":"experiments/T019-20261005-claude-motion-director/report_deck_motion.pptx",
    "T022 Codex T009 candidate":"experiments/T022-20261005-claude-t009-recompile/output/T022_r1_codex_plan_canonical.pptx",
    "T024 Argon complex showcase":"experiments/T024-20261014-gemini-complex-motion-rigging/output/T024_complex_motion_directed.pptx",
    "T025 Forge coffee (EN)":"experiments/T025-20261007-claude-slide-forge/coffee_report.pptx",
    "T025 Forge chuyển đổi số (VI)":"experiments/T025-20261007-claude-slide-forge/vi_chuyen_doi_so.pptx",
    "T028 report pro":"experiments/T028-20261008-claude-morph-studio/output/T028_report_pro.pptx",
    "T028 showcase pro":"experiments/T028-20261008-claude-morph-studio/output/T028_showcase_pro.pptx",
}


def run(cmd,**kw):
    return subprocess.run(cmd,capture_output=True,text=True,**kw)


def inputs(work):
    """Static decks: the four repository fixtures plus five themed Forge decks
    built from inputs/spec_*.json (Forge's static stage, before motion)."""
    out={f"fixture:{p.stem}":p for p in sorted((ROOT/"tests"/"fixtures").glob("*.pptx"))}
    for spec in sorted((HERE/"inputs").glob("spec_*.json")):
        deck=work/f"{spec.stem}.pptx"
        r=run([sys.executable,str(ROOT/"scripts"/"slide_forge.py"),"build",str(spec),"-o",str(deck)])
        verdict=json.loads(r.stdout)
        out[f"forge:{spec.stem[5:]}"]=Path(verdict["static_pptx"])
    return out


def direct(arm_root,deck,out,style):
    r=run([sys.executable,str(Path(arm_root)/"scripts"/"motion_director.py"),"auto",str(deck),"-o",str(out),
           "--style",style,"--force"],cwd=str(arm_root),timeout=900)
    return out.is_file() and r.returncode==0


def summarise(v):
    warns=[i for i in v["issues"] if i["severity"]=="warn"]
    return {"scores":v["scores"],"warnings":len(warns),
            "generator_warnings":sum(1 for i in warns if i["code"] in GENERATED),
            "by_code":dict(collections.Counter(i["code"] for i in warns))}


def main():
    base,work=Path(sys.argv[1]),Path(sys.argv[2])
    work.mkdir(parents=True,exist_ok=True)
    results={"arms":{},"landscape":{},"render_calibration":{}}
    decks=inputs(work)
    for name,deck in decks.items():
        for style in ("modern","cinematic"):
            row={}
            for arm,root in (("base",base),("t034",ROOT)):
                out=work/f"{arm}_{name.replace(':','_')}_{style}.pptx"
                if not direct(root,deck,out,style):
                    row[arm]=None
                    continue
                row[arm]=summarise(dc.critique(out))
            results["arms"][f"{name} / {style}"]=row
    for label,rel in LANDSCAPE.items():
        p=ROOT/rel
        if p.is_file():
            results["landscape"][label]=summarise(dc.critique(p))
    coffee=ROOT/"experiments/T025-20261007-claude-slide-forge/coffee_report.pptx"
    render=ROOT/"experiments/T025-20261007-claude-slide-forge/render-en"
    if render.is_dir() and shutil.which("soffice"):
        ppt=dc.critique(coffee,render=str(render))["frames"]
        lo=dc.critique(coffee,render="lo")["frames"]
        results["render_calibration"]={"deck":str(coffee.relative_to(ROOT)),
                                       "powerpoint":ppt,"libreoffice":lo}
    (HERE/"results.json").write_text(json.dumps(results,indent=1,ensure_ascii=False)+"\n",encoding="utf-8")
    (HERE/"results.md").write_text(markdown(results)+"\n",encoding="utf-8")
    print(markdown(results))


def markdown(res):
    lines=["# T034 evaluation results","","## Same inputs, two generator versions, one critic","",
           "| Input / style | base: overall | base: generator warnings | T034: overall | T034: generator warnings | codes fixed |",
           "|---|---|---|---|---|---|"]
    tot={"base":0,"t034":0}
    for key,row in res["arms"].items():
        b,t=row.get("base"),row.get("t034")
        if not b or not t:
            lines.append(f"| {key} | {'–' if not b else b['scores'].get('overall')} | | {'–' if not t else t['scores'].get('overall')} | | |")
            continue
        tot["base"]+=b["generator_warnings"]
        tot["t034"]+=t["generator_warnings"]
        fixed=sorted(set(b["by_code"])-set(t["by_code"]))
        lines.append(f"| {key} | {b['scores'].get('overall')} | {b['generator_warnings']} | {t['scores'].get('overall')} | "
                     f"{t['generator_warnings']} | {', '.join(fixed)} |")
    lines+=["",f"Generator-controlled warnings in total: base {tot['base']}, T034 {tot['t034']}.","",
            "## Landscape (existing decks, current critic)","",
            "| Deck | design | motion | rhythm | coherence | overall | warnings (top codes) |","|---|---|---|---|---|---|---|"]
    for label,v in res["landscape"].items():
        s=v["scores"]
        top=", ".join(f"{k} {n}" for k,n in sorted(v["by_code"].items(),key=lambda kv:-kv[1])[:4])
        lines.append(f"| {label} | {s.get('design','–')} | {s.get('motion','–')} | {s.get('rhythm','–')} | "
                     f"{s.get('coherence','–')} | {s.get('overall','–')} | {v['warnings']} ({top}) |")
    rc=res.get("render_calibration")
    if rc:
        lines+=["","## Render calibration: PowerPoint 16.0 frames vs LibreOffice 24.2 (same deck)","",
                "| Slide | background share PPT / LO | balance PPT / LO | colourfulness PPT / LO |","|---|---|---|---|"]
        for a,b in zip(rc["powerpoint"],rc["libreoffice"]):
            lines.append(f"| {a['slide']} | {a['background_share']} / {b['background_share']} | "
                         f"{a['balance_offset']} / {b['balance_offset']} | {a['colourfulness']} / {b['colourfulness']} |")
    return "\n".join(lines)


if __name__=="__main__":
    main()
