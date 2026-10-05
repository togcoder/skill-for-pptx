"""Frozen synthetic challenge set; never real PowerPoint evidence."""
from copy import deepcopy


def positive_control():
    manifest = {
        "version": "0.1", "kind": "powerpoint-native-qa-manifest",
        "pptx_sha256": "a" * 64, "slide_count": 2, "animated_slide_count": 2,
        "slides": [
            {"index": 1, "expected_click_count": 2,
             "expected_target_names": ["Chart", "KPI"],
             "expected_clicks": [{"index": 1}, {"index": 2}]},
            {"index": 2, "expected_click_count": 1,
             "expected_target_names": ["Focus"],
             "expected_clicks": [{"index": 1}]},
        ],
    }
    evidence = {
        "version": "0.1", "kind": "powerpoint-native-qa-evidence",
        "artifact": {"sha256": "a" * 64, "expected_sha256": "a" * 64,
                     "exact_hash_match": True},
        "powerpoint": {"presentation_opened": True, "com_created": True,
                       "slide_count": 2, "version": "16.0"},
        "slides": [
            {"index": 1, "sequence_error": None, "effect_count": 2,
             "effects": [{"shape_name": "Chart"}, {"shape_name": "KPI"}]},
            {"index": 2, "sequence_error": None, "effect_count": 1,
             "effects": [{"shape_name": "Focus"}]},
        ],
        "slideshow": {"attempted": True, "success": True, "slides": [
            {"index": 1, "native_click_count": 2, "initial_click_index": -1,
             "clicks": [
                 {"click": 1, "before_index": -1, "after_index": 1, "index_matches": True},
                 {"click": 2, "before_index": 1, "after_index": 2, "index_matches": True}]},
            {"index": 2, "native_click_count": 1, "initial_click_index": 0,
             "clicks": [{"click": 1, "before_index": 0, "after_index": 1, "index_matches": True}]},
        ]},
        "errors": [],
    }
    return manifest, evidence


def challenge_cases():
    cases = []
    def add(name, mutate, parse=True, click=False):
        m, e = deepcopy(positive_control())
        mutate(m, e)
        cases.append((name, m, e, parse, click))

    add("positive-control", lambda m, e: None, click=True)
    add("parse-only", lambda m, e: e.update(slideshow={"attempted": False, "success": False, "slides": []}))
    add("empty-click-records", lambda m, e: e["slideshow"]["slides"][0].update(clicks=[]))
    add("truncated-last-click", lambda m, e: e["slideshow"]["slides"][0]["clicks"].pop())
    add("duplicated-click", lambda m, e: e["slideshow"]["slides"][0]["clicks"].append(deepcopy(e["slideshow"]["slides"][0]["clicks"][0])))
    add("reordered-clicks", lambda m, e: e["slideshow"]["slides"][0]["clicks"].reverse())
    add("broken-before-chain", lambda m, e: e["slideshow"]["slides"][0]["clicks"][1].update(before_index=0))
    add("invalid-initial-index", lambda m, e: e["slideshow"]["slides"][0].update(initial_click_index=99))
    add("failed-slideshow", lambda m, e: e["slideshow"].update(success=False))
    add("missing-slideshow-success", lambda m, e: e["slideshow"].pop("success"))
    add("reported-probe-error", lambda m, e: e["errors"].append("capture failed after COM call"))
    add("missing-error-field", lambda m, e: e.pop("errors"))
    add("duplicate-slideshow-slide", lambda m, e: e["slideshow"]["slides"].append(deepcopy(e["slideshow"]["slides"][0])))
    add("missing-slideshow-slide", lambda m, e: e["slideshow"]["slides"].pop())
    add("wrong-click-count", lambda m, e: e["slideshow"]["slides"][0].update(native_click_count=3))
    add("boolean-click-index", lambda m, e: e["slideshow"]["slides"][0]["clicks"][0].update(click=True, after_index=True))
    add("contradictory-index-flag", lambda m, e: e["slideshow"]["slides"][0]["clicks"][1].update(after_index=1, index_matches=True))
    add("missing-application-version", lambda m, e: e["powerpoint"].pop("version"), parse=False)
    add("duplicate-native-slide", lambda m, e: e["slides"].append(deepcopy(e["slides"][0])), parse=False)
    add("missing-target", lambda m, e: e["slides"][0]["effects"].pop(), parse=False)
    add("wrong-hash", lambda m, e: e["artifact"].update(sha256="b" * 64), parse=False)
    add("empty-manifest-slides", lambda m, e: m.update(slides=[], animated_slide_count=0), parse=False)
    add("manifest-count-disagrees", lambda m, e: m.update(animated_slide_count=1), parse=False)
    add("duplicate-manifest-slide", lambda m, e: m["slides"].append(deepcopy(m["slides"][0])), parse=False)
    add("manifest-click-list-incomplete", lambda m, e: m["slides"][0]["expected_clicks"].pop(), parse=False)
    add("malformed-click-list", lambda m, e: e["slideshow"]["slides"][0].update(clicks=None))
    return cases
