#!/usr/bin/env python3
"""Verify evidence produced by powerPoint_native_probe.ps1 against a QA manifest."""
import argparse
import json
from pathlib import Path


def verify(manifest,evidence):
    checks=[]
    def add(name,passed,details=None):
        checks.append({"name":name,"passed":bool(passed),"details":details})

    add(
        "artifact-hash",
        evidence.get("artifact",{}).get("sha256")==manifest.get("pptx_sha256")
        and evidence.get("artifact",{}).get("exact_hash_match") is True,
        {
            "expected":manifest.get("pptx_sha256"),
            "actual":evidence.get("artifact",{}).get("sha256"),
        },
    )
    add(
        "powerpoint-open",
        evidence.get("powerpoint",{}).get("presentation_opened") is True,
        evidence.get("errors"),
    )
    add(
        "slide-count",
        evidence.get("powerpoint",{}).get("slide_count")==manifest.get("slide_count"),
        {
            "expected":manifest.get("slide_count"),
            "actual":evidence.get("powerpoint",{}).get("slide_count"),
        },
    )

    evidence_slides={slide.get("index"):slide for slide in evidence.get("slides",[])}
    target_failures=[]
    sequence_failures=[]
    for expected in manifest.get("slides",[]):
        actual=evidence_slides.get(expected["index"])
        if not actual:
            sequence_failures.append({"slide":expected["index"],"reason":"missing native slide record"})
            continue
        if actual.get("sequence_error"):
            sequence_failures.append({"slide":expected["index"],"reason":actual["sequence_error"]})
        native_names={
            effect.get("shape_name")
            for effect in actual.get("effects",[])
            if effect.get("shape_name")
        }
        missing=sorted(set(expected.get("expected_target_names",[]))-native_names)
        if missing:
            target_failures.append({"slide":expected["index"],"missing":missing,"native":sorted(native_names)})

    add("main-sequence-readable",not sequence_failures,sequence_failures)
    add("expected-targets-in-main-sequence",not target_failures,target_failures)

    slideshow=evidence.get("slideshow",{})
    slideshow_attempted=slideshow.get("attempted") is True
    click_failures=[]
    index_failures=[]
    if slideshow_attempted:
        native_slides={slide.get("index"):slide for slide in slideshow.get("slides",[])}
        for expected in manifest.get("slides",[]):
            actual=native_slides.get(expected["index"])
            if not actual:
                click_failures.append({"slide":expected["index"],"reason":"missing slideshow record"})
                continue
            if actual.get("native_click_count")!=expected.get("expected_click_count"):
                click_failures.append({
                    "slide":expected["index"],
                    "expected":expected.get("expected_click_count"),
                    "actual":actual.get("native_click_count"),
                })
            for click in actual.get("clicks",[]):
                if click.get("after_index")!=click.get("click") or click.get("index_matches") is not True:
                    index_failures.append({
                        "slide":expected["index"],
                        "click":click.get("click"),
                        "after_index":click.get("after_index"),
                    })

    add(
        "native-click-count",
        slideshow_attempted and not click_failures,
        click_failures if slideshow_attempted else "slideshow probe not run",
    )
    add(
        "native-click-index-progression",
        slideshow_attempted and not index_failures,
        index_failures if slideshow_attempted else "slideshow probe not run",
    )

    parse_names={
        "artifact-hash","powerpoint-open","slide-count",
        "main-sequence-readable","expected-targets-in-main-sequence",
    }
    parse_verified=all(c["passed"] for c in checks if c["name"] in parse_names)
    click_verified=parse_verified and all(
        c["passed"] for c in checks
        if c["name"] in {"native-click-count","native-click-index-progression"}
    )

    captures=[]
    for slide in slideshow.get("slides",[]):
        pre=slide.get("pre_click_capture")
        if pre:
            captures.append(pre)
        for click in slide.get("clicks",[]):
            if click.get("capture"):
                captures.append(click["capture"])

    return {
        "version":"0.1",
        "kind":"powerpoint-native-qa-verification",
        "checks":checks,
        "claims":{
            "native_application_parse_verified":parse_verified,
            "native_click_execution_verified":click_verified,
            "visual_capture_count":len(captures),
            "visual_state_verified":False,
        },
        "overall_status":(
            "native-click-pass-pending-visual-review"
            if click_verified else
            "native-parse-pass-click-pending-or-failed"
            if parse_verified else
            "failed"
        ),
        "claim_boundary":"Screenshots/captures require separate visual review; this verifier never promotes visual_state_verified automatically.",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path)
    parser.add_argument("evidence",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    evidence=json.loads(args.evidence.read_text(encoding="utf-8-sig"))
    result=verify(manifest,evidence)
    data=json.dumps(result,ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(data+"\n",encoding="utf-8")
    else:
        print(data)
    return 0 if result["claims"]["native_click_execution_verified"] else 1


if __name__=="__main__":
    raise SystemExit(main())
