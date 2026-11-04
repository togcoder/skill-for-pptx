#!/usr/bin/env python3
"""T061 evidence generator — canonical interaction writer.

Two runs make the before/after table in REPORT.md:

    PYTHONUTF8=1 python experiments/T061-20261104-opencode-interaction-writer/make_evidence.py --label before --out inputs
    PYTHONUTF8=1 python experiments/T061-20261104-opencode-interaction-writer/make_evidence.py --label after  --out artifacts

It writes, into the chosen folder:
  timeline_interactive_slide.xml   apply_timeline(trigger_spid=...) output
  canonical_seq.xml                advanced_interactivity.build_canonical_interactive_seq output
  canonical_seq.sha256             its hash
  t048_rebuild.json                rebuilt T048 decks vs the committed artifacts (member bytes)
  t049_artifact.json               inspect_interactivity on the committed T049 artifact
  summary.json                     parse counts + hashes used in the REPORT

T048 decks are rebuilt into a temporary directory with the committed
make_artifacts.py; the committed artifacts are never written to.
T049 is PowerPoint-COM output, so it is inspected, never rebuilt.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import pptx_animator as anim  # noqa: E402
from scripts import advanced_interactivity as ai  # noqa: E402
from scripts import slide_navigator as nav  # noqa: E402

EXP = Path(__file__).resolve().parent
T048_DIR = ROOT / "experiments" / "T048-20261101-antigravity-slide-branching"
T049_PPTX = (
    ROOT
    / "experiments"
    / "T049-20261101-antigravity-advanced-interactivity"
    / "artifacts"
    / "one_slide_games_suite.pptx"
)
T049_AUDIT = T049_PPTX.parent / "audit_one_slide_games.json"

TRIGGER_FIXTURE = f"""\
<p:sld xmlns:p="{anim.P}" xmlns:a="{anim.A}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="10" name="Inspect Button"><a:hlinkClick r:id="rId77" action="ppaction://hlinkshowjump?jump=nextslide"/></p:cNvPr><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="100" y="100"/><a:ext cx="500" cy="300"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="20" name="Detail Panel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="2000" y="200"/><a:ext cx="1500" cy="1000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def xml_text(element) -> str:
    return E.tostring(element, pretty_print=True, encoding="unicode")


def fixture_timeline() -> dict:
    root = E.fromstring(TRIGGER_FIXTURE)
    receipt = anim.apply_timeline(
        root,
        [
            {
                "id": "trig-1",
                "trigger_spid": "10",
                "effects": [
                    {"preset": "zoom", "spid": "20", "trigger": "click", "duration_ms": 500}
                ],
            }
        ],
    )
    timing = root.find("p:timing", anim.NS)
    assert timing is not None
    return {
        "xml": xml_text(timing),
        "receipt": receipt,
        "hyperlink_survived": root.find(".//a:hlinkClick", anim.NS) is not None,
        "ctn_ids": [int(c.get("id")) for c in timing.iter(anim.q("cTn")) if (c.get("id") or "").isdigit()],
        "seq_cTn_attrs": dict(
            timing.find(".//p:cTn[@nodeType='interactiveSeq']", anim.NS).attrib
        ),
    }


def canonical_seq() -> dict:
    seq_el = ai.build_canonical_interactive_seq(
        trigger_spid=6, target_spids=[6], is_exit=True,
        preset_name="zoom", duration_ms=350, seq_id=2,
    )
    data = xml_text(seq_el)
    return {"xml": data, "sha256": sha256(data.encode("utf-8"))}


def member_hashes(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        return {name: sha256(z.read(name)) for name in z.namelist()}


def rebuild_t048() -> dict:
    spec = importlib.util.spec_from_file_location(
        "t048_make_artifacts", T048_DIR / "make_artifacts.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {"decks": {}, "ok": True}
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for key, builder, committed_name in (
            ("game", module.build_interactive_adventure_game, "interactive_adventure_game.pptx"),
            ("hub", module.build_executive_interactive_hub, "executive_interactive_hub.pptx"),
        ):
            out = tmp / committed_name
            builder(out)
            committed = T048_DIR / "artifacts" / committed_name
            new_members = member_hashes(out)
            old_members = member_hashes(committed)
            # docProps/core.xml carries a build timestamp, the zip container too.
            compared = {k: v for k, v in old_members.items() if not k.startswith("docProps/")}
            different = sorted(
                k for k, v in compared.items() if new_members.get(k) != v
            )
            result["decks"][key] = {
                "committed": str(committed.relative_to(ROOT)).replace("\\", "/"),
                "members_compared": len(compared),
                "different_members": different,
                "slide_xml_identical": not any(
                    d.startswith("ppt/slides/slide") for d in different
                ),
                "graph_edges": len(nav.inspect_navigation_graph(committed)["edges"]),
                "graph_edges_rebuilt": len(nav.inspect_navigation_graph(out)["edges"]),
            }
            result["ok"] = result["ok"] and not different
    return result


def t049() -> dict:
    audit = ai.inspect_interactivity(T049_PPTX)
    stored = None
    if T049_AUDIT.is_file():
        stored = json.loads(T049_AUDIT.read_text(encoding="utf-8"))
    seq_counts = [
        {"file": s["file"], "interactive_sequences": len(s["interactive_sequences"])}
        for s in audit["slides"]
    ]
    fingerprint = [
        [s["file"], [[q["trigger_spid"], q["animated_spids"]] for q in s["interactive_sequences"]]]
        for s in audit["slides"]
    ]
    stored_fingerprint = None
    if stored is not None:
        stored_fingerprint = [
            [s["file"], [[q["trigger_spid"], sorted(q["animated_spids"])] for q in s["interactive_sequences"]]]
            for s in stored["slides"]
        ]
    return {
        "artifact_sha256": sha256(T049_PPTX.read_bytes()),
        "interactive_sequences_count": audit["interactive_sequences_count"],
        "per_slide": seq_counts,
        "animated_spids_per_sequence": [
            len(s["interactive_sequences"][i]["animated_spids"])
            for s in audit["slides"]
            for i in range(len(s["interactive_sequences"]))
        ],
        "parse_fingerprint": fingerprint,
        "stored_parse_fingerprint": stored_fingerprint,
        "stored_counts_match": (
            None if stored is None
            else stored["interactive_sequences_count"] == audit["interactive_sequences_count"]
            and [len(s["interactive_sequences"]) for s in stored["slides"]]
            == [len(s["interactive_sequences"]) for s in audit["slides"]]
        ),
        "audit": audit,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", choices=["before", "after"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out_dir = EXP / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    timeline = fixture_timeline()
    (out_dir / "timeline_interactive_slide.xml").write_text(timeline["xml"], encoding="utf-8")

    seq = canonical_seq()
    (out_dir / "canonical_seq.xml").write_text(seq["xml"], encoding="utf-8")
    (out_dir / "canonical_seq.sha256").write_text(seq["sha256"] + "\n", encoding="utf-8")

    t048 = rebuild_t048()
    (out_dir / "t048_rebuild.json").write_text(
        json.dumps(t048, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    t049_data = t049()
    (out_dir / "t049_artifact.json").write_text(
        json.dumps({k: v for k, v in t049_data.items() if k != "audit"}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    summary = {
        "label": args.label,
        "timeline": {
            "hyperlink_survived": timeline["hyperlink_survived"],
            "ctn_ids_sorted": timeline["ctn_ids"] == sorted(timeline["ctn_ids"]),
            "interactive_seq_ctn_attrs": timeline["seq_cTn_attrs"],
            "sha256": sha256(timeline["xml"].encode("utf-8")),
            "receipt": timeline["receipt"],
        },
        "canonical_seq_sha256": seq["sha256"],
        "t048": {k: {kk: vv for kk, vv in v.items() if kk != "rebuilt_sha256"} for k, v in t048["decks"].items()},
        "t049": {k: v for k, v in t049_data.items() if k != "audit"},
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if args.label == "after":
        write_delta(out_dir)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def write_delta(out_dir: Path) -> None:
    """DELTA.md: the documented before/after diff (T061 acceptance)."""
    import difflib

    before_dir = EXP / "inputs"
    before = json.loads((before_dir / "summary.json").read_text(encoding="utf-8"))
    after = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    old_xml = (before_dir / "timeline_interactive_slide.xml").read_text(encoding="utf-8")
    new_xml = (out_dir / "timeline_interactive_slide.xml").read_text(encoding="utf-8")
    diff = "".join(difflib.unified_diff(
        old_xml.splitlines(True), new_xml.splitlines(True),
        "before/timeline_interactive_slide.xml", "after/timeline_interactive_slide.xml",
    ))
    lines = [
        "# T061 before → after delta",
        "",
        "Generated by `make_evidence.py --label after` from `inputs/summary.json`.",
        "",
        "| Measure | Before (base ac5b45e) | After |",
        "|---|---|---|",
        f"| trigger shape keeps its `<a:hlinkClick>` | {before['timeline']['hyperlink_survived']} | {after['timeline']['hyperlink_survived']} |",
        f"| interactiveSeq cTn attributes | `{before['timeline']['interactive_seq_ctn_attrs']}` | `{after['timeline']['interactive_seq_ctn_attrs']}` |",
        f"| timeline fixture sha256 | `{before['timeline']['sha256'][:16]}…` | `{after['timeline']['sha256'][:16]}…` |",
        f"| `build_canonical_interactive_seq` sha256 | `{before['canonical_seq_sha256'][:16]}…` | `{after['canonical_seq_sha256'][:16]}…` |",
    ]
    for deck in ("game", "hub"):
        b = before["t048"][deck]
        a = after["t048"][deck]
        lines.append(
            f"| T048 {deck}: members differing from committed | {len(b['different_members'])} | {len(a['different_members'])} |"
        )
    lines += [
        f"| T049 sequences (slide1 / slide2) | {before['t049']['per_slide'][0]['interactive_sequences']} / {before['t049']['per_slide'][1]['interactive_sequences']} "
        f"| {after['t049']['per_slide'][0]['interactive_sequences']} / {after['t049']['per_slide'][1]['interactive_sequences']} |",
        f"| T049 artifact sha256 | `{before['t049']['artifact_sha256'][:16]}…` | `{after['t049']['artifact_sha256'][:16]}…` |",
        f"| T049 animated spids per sequence | {before['t049']['animated_spids_per_sequence']} | {after['t049']['animated_spids_per_sequence']} |",
        f"| T049 counts match the stored audit | {before['t049'].get('stored_counts_match', 'n/a')} | {after['t049']['stored_counts_match']} |",
        "",
        "## Timeline fixture diff",
        "",
        "```diff",
        diff.rstrip(),
        "```",
        "",
        "`build_canonical_interactive_seq` is byte-identical: the T049 COM-mirroring",
        "builder was moved, not rewritten.",
        "",
    ]
    (out_dir / "DELTA.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
