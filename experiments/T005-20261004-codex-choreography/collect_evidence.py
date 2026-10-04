"""Recompute T005 structural/geometry evidence. No image or playback judgments."""
import copy
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from choreography import compile_intent
from validate_plan import validate
from verify_intent import check
spec=importlib.util.spec_from_file_location("package_parity",ROOT/"experiments/T003-20261004-codex-layer01/verify_package.py")
package=importlib.util.module_from_spec(spec);spec.loader.exec_module(package)


def save(name,data):
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    results={}
    for name,ip,pp,deck in [
        ("candidate","candidate.intent.json","candidate.plan.json","T005_compound_candidate.pptx"),
        ("transfer","transfer/intent.json","transfer/plan.json","T005_compound_transfer.pptx")]:
        intent=json.loads((HERE/ip).read_text())
        plan=json.loads((HERE/pp).read_text())
        parity=package.verify(plan,ROOT/"output"/deck)
        result=check(intent,plan)
        errors=validate(plan)
        if errors or not result["passed"] or not parity["passed"]:
            raise AssertionError((errors,result,parity))
        if compile_intent(intent)!=plan:raise AssertionError("Compiler reproduction mismatch")
        results[name]=dict(intent_geometry=result,package=parity,plan_errors=errors,compiler_reproduction=True)
    original=json.loads((HERE/"candidate.intent.json").read_text())
    ablation=copy.deepcopy(original);ablation["orbit_segments"]=1
    coarse=compile_intent(ablation)
    save("ablation.intent.json",ablation);save("ablation.plan.json",coarse)
    results["ablation"]=check(ablation,coarse)
    results["comparison_scope"]="Same intent except orbit_segments 1 vs 6. Geometry-only negative control, no ablation PPTX export."
    save("evidence.json",results)
    tests=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,text=True,capture_output=True)
    (HERE/"unit-tests.txt").write_text(tests.stdout+tests.stderr,encoding="utf-8")
    if tests.returncode:raise AssertionError("Unit tests failed")
    manifests=[]
    for folder in ["candidate-renders","transfer-renders"]:
        for file in sorted((HERE/folder).glob("slide-*.png")):
            manifests.append(dict(path=str(file.relative_to(ROOT)),sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    save("render-manifest.json",dict(render_source="Final exact PPTX via host renderer",files=manifests,
        static_inspection_record="See REPORT.md; hashes are not a visual-review or playback oracle."))
    save("environment.json",dict(python=platform.python_version(),platform=platform.platform(),
        compiler="scripts/choreography.py",renderer="unchanged Work artifact-tool backend",font="Bitstream Charter",
        baseline_remote="f3745118ca2334156038680747a3893397259470",powerpoint_playback_verified=False))
    print(json.dumps({"candidate":results["candidate"]["intent_geometry"]["orbit_linear_proxy"],
        "ablation":results["ablation"]["orbit_linear_proxy"],"transfer_passed":results["transfer"]["intent_geometry"]["passed"],
        "candidate_sha256":results["candidate"]["package"]["sha256"],"transfer_sha256":results["transfer"]["package"]["sha256"],
        "render_count":len(manifests)},indent=2))


if __name__=="__main__":main()
