#!/usr/bin/env python3
"""Check completeness of recorded PowerPoint COM parse/click evidence.

Supplied records are not authenticated. Click indices can refer to actively
playing effects, so they do not prove timing completion or visual playback.
"""
import argparse
import json
import re
from pathlib import Path


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _object(value):
    return value if isinstance(value, dict) else {}


def _rows(value):
    return value if isinstance(value, list) else []


def _index(rows, field, label, failures):
    result = {}
    if not isinstance(rows, list):
        failures.append(label + ": expected a list")
        return result
    for row in rows:
        if not isinstance(row, dict) or not _integer(row.get(field), 1):
            failures.append(label + ": invalid record/index")
            continue
        index = row[field]
        if index in result:
            failures.append(f"{label}: duplicate index {index}")
            continue
        result[index] = row
    return result


def _manifest_errors(manifest):
    failures = []
    if manifest.get("kind") != "powerpoint-native-qa-manifest" or manifest.get("version") != "0.1":
        failures.append("unsupported manifest kind/version")
    sha = manifest.get("pptx_sha256")
    if not isinstance(sha, str) or re.fullmatch(r"[0-9a-f]{64}", sha) is None:
        failures.append("invalid exact SHA-256")
    count = manifest.get("slide_count")
    if not _integer(count, 1):
        failures.append("invalid slide count")
    slides = _index(manifest.get("slides"), "index", "manifest slides", failures)
    animated = manifest.get("animated_slide_count")
    if not slides or not _integer(animated, 1) or animated != len(slides):
        failures.append("animated slide count/records disagree or are empty")
    for index, slide in slides.items():
        if _integer(count, 1) and index > count:
            failures.append(f"manifest slide {index}: outside deck")
        clicks = slide.get("expected_click_count")
        if not _integer(clicks):
            failures.append(f"manifest slide {index}: invalid click count")
            continue
        groups = slide.get("expected_clicks")
        if (not isinstance(groups, list) or len(groups) != clicks
                or any(not isinstance(g, dict) or type(g.get("index")) is not int for g in groups)
                or [g.get("index") for g in groups] != list(range(1, clicks + 1))):
            failures.append(f"manifest slide {index}: incomplete click partition")
        names = slide.get("expected_target_names")
        if (not isinstance(names, list) or not names
                or any(not isinstance(n, str) or not n.strip() for n in names)
                or len(set(names)) != len(names)):
            failures.append(f"manifest slide {index}: invalid target names")
    return failures, slides


def verify(manifest, evidence):
    checks = []

    def add(name, passed, details=None):
        checks.append({"name": name, "passed": bool(passed), "details": details})

    manifest, evidence = _object(manifest), _object(evidence)
    manifest_errors, expected_slides = _manifest_errors(manifest)
    add("manifest-complete", not manifest_errors, manifest_errors)
    add("evidence-format", evidence.get("kind") == "powerpoint-native-qa-evidence"
        and evidence.get("version") == "0.1")
    artifact = _object(evidence.get("artifact"))
    add("artifact-hash", isinstance(manifest.get("pptx_sha256"), str)
        and artifact.get("sha256") == manifest.get("pptx_sha256")
        and artifact.get("expected_sha256") == manifest.get("pptx_sha256")
        and artifact.get("exact_hash_match") is True,
        {"expected": manifest.get("pptx_sha256"), "actual": artifact.get("sha256")})
    ppt = _object(evidence.get("powerpoint"))
    add("powerpoint-open", ppt.get("presentation_opened") is True and ppt.get("com_created") is True)
    add("powerpoint-version", isinstance(ppt.get("version"), str) and bool(ppt.get("version", "").strip()))
    add("slide-count", _integer(ppt.get("slide_count"), 1)
        and ppt.get("slide_count") == manifest.get("slide_count"))

    sequence_failures, target_failures = [], []
    native_slides = _index(evidence.get("slides"), "index", "native slides", sequence_failures)
    for index in native_slides:
        if _integer(ppt.get("slide_count"), 1) and index > ppt["slide_count"]:
            sequence_failures.append(f"native slide {index}: outside deck")
    for index, expected in expected_slides.items():
        actual = native_slides.get(index)
        if not actual:
            sequence_failures.append(f"slide {index}: missing native record")
            continue
        if actual.get("sequence_error"):
            sequence_failures.append(f"slide {index}: {actual['sequence_error']}")
        effects = actual.get("effects")
        if (not isinstance(effects, list) or any(not isinstance(e, dict) for e in effects)
                or not _integer(actual.get("effect_count")) or actual.get("effect_count") != len(effects)):
            sequence_failures.append(f"slide {index}: incomplete effect records")
            continue
        names = {e.get("shape_name") for e in effects if isinstance(e.get("shape_name"), str)}
        required = {n for n in _rows(expected.get("expected_target_names")) if isinstance(n, str)}
        missing = sorted(required - names)
        if missing:
            target_failures.append({"slide": index, "missing": missing})
    add("main-sequence-readable", not sequence_failures, sequence_failures)
    add("expected-targets-in-main-sequence", not target_failures, target_failures)
    parse_verified = all(check["passed"] for check in checks)

    show = _object(evidence.get("slideshow"))
    add("slideshow-completed", show.get("attempted") is True and show.get("success") is True)
    add("probe-no-errors", isinstance(evidence.get("errors"), list) and not evidence["errors"], evidence.get("errors"))
    record_failures, count_failures, progression_failures = [], [], []
    shown = _index(show.get("slides"), "index", "slideshow slides", record_failures)
    if set(shown) != set(expected_slides):
        record_failures.append("slideshow slide coverage differs from manifest")
    total_clicks = 0
    for index, expected in expected_slides.items():
        count = expected.get("expected_click_count")
        if not _integer(count):
            continue
        total_clicks += count
        actual = shown.get(index, {})
        if not _integer(actual.get("native_click_count")) or actual.get("native_click_count") != count:
            count_failures.append({"slide": index, "expected": count, "actual": actual.get("native_click_count")})
        clicks = actual.get("clicks")
        if (not isinstance(clicks, list) or len(clicks) != count
                or any(not isinstance(c, dict) or type(c.get("click")) is not int for c in clicks)
                or [c.get("click") for c in clicks] != list(range(1, count + 1))):
            record_failures.append(f"slide {index}: missing, duplicated or reordered click records")
            continue
        initial = actual.get("initial_click_index")
        if type(initial) is not int or initial not in (-1, 0):
            progression_failures.append(f"slide {index}: invalid pre-animation index")
        previous = initial
        for click in clicks:
            if (type(click.get("before_index")) is not int or click["before_index"] != previous
                    or type(click.get("after_index")) is not int or click["after_index"] != click["click"]
                    or click.get("index_matches") is not True):
                progression_failures.append(f"slide {index}: inconsistent click {click['click']}")
            previous = click["click"]
    add("native-click-count", not count_failures, count_failures)
    add("native-click-records-complete", not record_failures, record_failures)
    add("native-click-index-progression", total_clicks > 0 and not progression_failures, progression_failures)
    click_verified = all(check["passed"] for check in checks)
    captures = []
    for slide in shown.values():
        if slide.get("pre_click_capture"):
            captures.append(slide["pre_click_capture"])
        for click in _rows(slide.get("clicks")):
            if isinstance(click, dict) and click.get("capture"):
                captures.append(click["capture"])

    return {
        "version": "0.2", "kind": "powerpoint-native-qa-verification", "checks": checks,
        "claims": {
            "native_application_parse_verified": parse_verified,
            # Backward compatible: complete recorded click API progression only.
            "native_click_execution_verified": click_verified,
            "native_click_index_progression_verified": click_verified,
            "visual_capture_count": len(captures),
            "animation_completion_verified": False,
            "visual_state_verified": False,
            "native_playback_verified": False,
        },
        "overall_status": ("native-click-pass-pending-visual-review" if click_verified else
                           "native-parse-pass-click-pending-or-failed" if parse_verified else "failed"),
        "claim_boundary": "Supplied record integrity only, not authentication. Click indices can refer to active animations; completion, visual states and full playback require separate native capture/review.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    evidence = json.loads(args.evidence.read_text(encoding="utf-8-sig"))
    result = verify(manifest, evidence)
    data = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(data + "\n", encoding="utf-8")
    else:
        print(data)
    return 0 if result["claims"]["native_click_index_progression_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
