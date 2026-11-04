"""T061 — one canonical interaction writer for interactiveSeq, triggers and
hyperlink conflicts.

The tests pin the three things the refactor claims:

1. there is one writer (no module besides ``pptx_animator`` builds
   ``nodeType="interactiveSeq"``), and the three former writers are thin
   callers that import it;
2. the T049 root-cause findings survive in the canonical output (onClick start
   condition on the interactiveSeq cTn, delay 0 click step, endSync), one
   sequence per trigger shape, and the trigger's click hyperlink is stripped;
3. the committed T048b/T049 artifacts still parse to the same counts.

Run: ``PYTHONUTF8=1 python -m unittest tests.test_interaction_writer -v``.
"""
import ast
import hashlib
import json
import unittest
import zipfile
from pathlib import Path

from lxml import etree as E

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import pptx_animator as anim  # noqa: E402
from scripts import advanced_interactivity as ai  # noqa: E402
from scripts import interactive_triggers as triggers  # noqa: E402
from scripts import slide_navigator as nav  # noqa: E402

P = anim.P
A = anim.A
NS = anim.NS
T048 = ROOT / "experiments" / "T048-20261101-antigravity-slide-branching" / "artifacts"
T049 = ROOT / "experiments" / "T049-20261101-antigravity-advanced-interactivity" / "artifacts"
CANONICAL_SEQ_SHA = "d1f76b7bdea601af3127d9b9b893acde11a35108136d6c5154740917e3e06a27"

SLIDE = f"""\
<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{anim.R}">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr/>
    <p:sp><p:nvSpPr><p:cNvPr id="10" name="Inspect Button"><a:hlinkClick r:id="rId77" action="ppaction://hlinkshowjump?jump=nextslide"/></p:cNvPr><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="100" cy="100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>
    <p:sp><p:nvSpPr><p:cNvPr id="11" name="Plain Button"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="100" cy="100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>
    <p:sp><p:nvSpPr><p:cNvPr id="20" name="Detail Panel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="200" y="0"/><a:ext cx="100" cy="100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>
    <p:sp><p:nvSpPr><p:cNvPr id="21" name="Second Panel"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      <p:spPr><a:xfrm><a:off x="300" y="0"/><a:ext cx="100" cy="100"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:sp>
  </p:spTree></p:cSld>
</p:sld>
"""


def slide():
    return E.fromstring(SLIDE)


def trigger_click(effects, trigger="10", click_id="trig"):
    return {"id": click_id, "trigger_spid": trigger, "effects": effects}


def zoom(spid="20", duration=500):
    return {"preset": "zoom", "spid": spid, "trigger": "click", "duration_ms": duration}


def written(*clicks):
    root = slide()
    receipt = anim.apply_timeline(root, list(clicks))
    return root, receipt


# ---------------------------------------------------------------------------
# 1. One writer


class OneWriterTests(unittest.TestCase):
    def _interactive_seq_writers(self):
        """Scripts that construct nodeType="interactiveSeq" themselves."""
        found = {}
        for path in sorted((ROOT / "scripts").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                hit = False
                if isinstance(node, ast.Call):
                    for kw in node.keywords:
                        if kw.arg == "nodeType" and getattr(kw.value, "value", None) == "interactiveSeq":
                            hit = True
                    if (isinstance(node.func, ast.Attribute) and node.func.attr == "set"
                            and len(node.args) >= 2
                            and getattr(node.args[0], "value", None) == "nodeType"
                            and getattr(node.args[1], "value", None) == "interactiveSeq"):
                        hit = True
                if isinstance(node, ast.Dict):
                    keys = [getattr(k, "value", None) for k in node.keys]
                    values = [getattr(v, "value", None) for v in node.values]
                    if "nodeType" in keys and "interactiveSeq" in values:
                        hit = True
                if hit:
                    found.setdefault(path.name, 0)
                    found[path.name] += 1
        return found

    def test_only_pptx_animator_builds_interactive_seq(self):
        writers = self._interactive_seq_writers()
        self.assertEqual(list(writers), ["pptx_animator.py"],
                         f"duplicate interactiveSeq writers: {writers}")

    def test_former_writers_import_the_canonical_module(self):
        for module in (triggers, ai, nav):
            source = Path(module.__file__).read_text(encoding="utf-8")
            tree = ast.parse(source)
            imported = False
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    imported = imported or (node.module or "").endswith("pptx_animator")
                    imported = imported or any(a.name == "pptx_animator" for a in node.names)
                if isinstance(node, ast.Import):
                    imported = imported or any(a.name.endswith("pptx_animator") for a in node.names)
            self.assertTrue(imported, f"{module.__name__} does not import pptx_animator")


# ---------------------------------------------------------------------------
# 2. T049 findings


class T049FindingsTests(unittest.TestCase):
    def test_interactive_seq_starts_itself_and_steps_at_zero(self):
        root, _ = written(trigger_click([zoom()]))
        seq_ctn = root.find(".//p:cTn[@nodeType='interactiveSeq']", NS)
        self.assertIsNotNone(seq_ctn)
        # finding 1: onClick start condition on the interactiveSeq cTn itself
        start = seq_ctn.find("p:stCondLst/p:cond", NS)
        self.assertEqual(start.get("evt"), "onClick")
        self.assertEqual(start.find("p:tgtEl/p:spTgt", NS).get("spid"), "10")
        # the seq-level nextCondLst is still written for click advancement
        nxt = root.find(".//p:seq/p:nextCondLst/p:cond", NS)
        self.assertEqual(nxt.find("p:tgtEl/p:spTgt", NS).get("spid"), "10")
        # native endSync
        self.assertEqual(seq_ctn.find("p:endSync/p:rtn", NS).get("val"), "all")
        # finding 2: the click step is not indefinite
        step = seq_ctn.find("p:childTnLst/p:par/p:cTn", NS)
        conds = step.findall("p:stCondLst/p:cond", NS)
        self.assertEqual([c.get("delay") for c in conds], ["0"])
        # no onBegin/tn indirection, no dur on the interactiveSeq cTn
        self.assertNotIn("dur", seq_ctn.attrib)
        self.assertEqual(seq_ctn.get("nodeType"), "interactiveSeq")

    def test_one_sequence_per_trigger(self):
        root, _ = written(
            trigger_click([zoom()], click_id="a"),
            trigger_click([{"preset": "fade", "spid": "21", "trigger": "click", "duration_ms": 300}], click_id="b"),
        )
        self.assertEqual(len(anim.interactive_sequences(root)), 1)
        groups = root.findall(".//p:cTn[@nodeType='interactiveSeq']/p:childTnLst/p:par", NS)
        self.assertEqual(len(groups), 2)

    def test_trigger_hyperlink_is_stripped(self):
        root, receipt = written(trigger_click([zoom()]))
        self.assertIsNone(root.find(".//p:cNvPr[@id='10']/a:hlinkClick", NS))
        self.assertEqual(receipt["clicks"][0]["hyperlinks_stripped"], 1)
        self.assertEqual(receipt["interactive_click_groups"], 1)

    def test_hyperlink_on_trigger_is_a_conflict(self):
        root, _ = written(trigger_click([zoom()]))
        with self.assertRaises(anim.InteractionConflict):
            anim.set_click_action(root, "10", action="ppaction://hlinkshowjump?jump=nextslide")
        skipped = anim.set_click_action(root, "10", action="ppaction://hlinkshowjump?jump=nextslide",
                                        conflict="skip")
        self.assertFalse(skipped["ok"])
        self.assertEqual(skipped["reason"], "animation_trigger")

    def test_hyperlink_on_plain_shape_keeps_native_attribute_order(self):
        root = slide()
        result = anim.set_click_action(root, "11", action="ppaction://hlinksldjump", rel_id="rId11")
        self.assertTrue(result["ok"])
        cnvpr = root.find(".//p:cNvPr[@id='11']", NS)
        self.assertEqual(
            E.tostring(cnvpr, encoding="unicode"),
            '<p:cNvPr xmlns:p="%s" xmlns:a="%s" xmlns:r="%s" id="11" name="Plain Button">'
            '<a:hlinkClick action="ppaction://hlinksldjump" r:id="rId11"/></p:cNvPr>' % (P, A, anim.R),
        )

    def test_canonical_builder_is_byte_stable(self):
        data = E.tostring(ai.build_canonical_interactive_seq(
            trigger_spid=6, target_spids=[6], is_exit=True,
            preset_name="zoom", duration_ms=350, seq_id=2),
            pretty_print=True, encoding="unicode")
        self.assertEqual(hashlib.sha256(data.encode("utf-8")).hexdigest(), CANONICAL_SEQ_SHA)


# ---------------------------------------------------------------------------
# 3. Semantic layer


class SemanticActionTests(unittest.TestCase):
    def test_actions_round_trip_without_custom_attributes(self):
        root = slide()
        plan = [
            {"trigger": "Inspect Button", "action": "reveal", "targets": ["Detail Panel"],
             "preset": "zoom", "duration_ms": 600, "delay_ms": 25},
            {"trigger": "11", "action": "toggle", "targets": ["Second Panel"],
             "preset": "float-in", "duration_ms": 550, "delay_ms": 10},
        ]
        records = triggers.apply_interactive_triggers(root, plan)
        self.assertEqual([r["action"] for r in records], ["reveal", "toggle"])
        self.assertEqual(records[0]["hlinks_removed"], 1)
        self.assertEqual(records[1]["hlinks_removed"], 0)
        read = triggers.read_interactive_triggers(root)
        by_trigger = {r["trigger_spid"]: r for r in read}
        self.assertEqual(by_trigger["10"]["action"], "reveal")
        self.assertEqual(by_trigger["10"]["preset"], "zoom")
        self.assertEqual(by_trigger["10"]["duration_ms"], 600)
        self.assertEqual(by_trigger["10"]["delay_ms"], 25)
        self.assertEqual(by_trigger["11"]["action"], "toggle")
        self.assertEqual(by_trigger["11"]["preset"], "float-in")
        self.assertEqual(by_trigger["11"]["target_spids"], ["21"])
        # T033 wrote customAction/customPreset/customDur, which are not schema.
        for ctn in root.iter(anim.q("cTn")):
            for attr in ("customAction", "customPreset", "customDur"):
                self.assertNotIn(attr, ctn.attrib)

    def test_toggle_writes_two_click_steps_on_one_sequence(self):
        root = slide()
        triggers.apply_interactive_triggers(root, [
            {"trigger": "11", "action": "toggle", "targets": ["20"], "preset": "fade",
             "duration_ms": 200},
        ])
        self.assertEqual(len(anim.interactive_sequences(root)), 1)
        classes = [c.get("presetClass") for c in root.iter(anim.q("cTn")) if c.get("presetClass")]
        self.assertEqual(classes, ["entr", "exit"])

    def test_zoom_out_preset_is_a_real_exit(self):
        root, _ = written(trigger_click([
            {"preset": "zoom-out", "spid": "20", "trigger": "click", "duration_ms": 350}]))
        ctn = next(c for c in root.iter(anim.q("cTn")) if c.get("presetClass"))
        self.assertEqual((ctn.get("presetClass"), ctn.get("presetID"), ctn.get("presetSubtype")),
                         ("exit", "53", "32"))


# ---------------------------------------------------------------------------
# 4. Committed artifacts still parse to the same counts


class CommittedArtifactTests(unittest.TestCase):
    def test_t048b_navigation_parse_counts(self):
        game = T048 / "interactive_adventure_game.pptx"
        hub = T048 / "executive_interactive_hub.pptx"
        if not game.is_file() or not hub.is_file():
            self.skipTest("T048 artifacts not present")
        self.assertEqual(len(nav.inspect_navigation_graph(game)["edges"]), 11)
        self.assertEqual(len(nav.inspect_navigation_graph(hub)["edges"]), 8)

    def test_t049_interactive_parse_counts(self):
        deck = T049 / "one_slide_games_suite.pptx"
        if not deck.is_file():
            self.skipTest("T049 artifact not present")
        audit = ai.inspect_interactivity(deck)
        self.assertEqual(audit["total_slides"], 2)
        self.assertEqual(audit["interactive_sequences_count"], 8)
        self.assertEqual([len(s["interactive_sequences"]) for s in audit["slides"]], [4, 4])
        stored = json.loads((T049 / "audit_one_slide_games.json").read_text(encoding="utf-8"))
        self.assertEqual(stored["interactive_sequences_count"], audit["interactive_sequences_count"])
        # self-triggered chests animate the trigger shape itself: the T049
        # auditor reported [] for them, the canonical reader reports the spid.
        slide1 = audit["slides"][0]["interactive_sequences"]
        self.assertTrue(all(q["animated_spids"] for q in slide1))
        self.assertEqual(slide1[0]["animated_spids"], ["6"])

    def test_t049_xml_has_the_native_shape_this_writer_emits(self):
        deck = T049 / "one_slide_games_suite.pptx"
        if not deck.is_file():
            self.skipTest("T049 artifact not present")
        with zipfile.ZipFile(deck) as z:
            root = E.fromstring(z.read("ppt/slides/slide1.xml"))
        seq_ctn = root.find(".//p:cTn[@nodeType='interactiveSeq']", NS)
        self.assertEqual(seq_ctn.find("p:stCondLst/p:cond", NS).get("evt"), "onClick")
        self.assertIsNotNone(seq_ctn.find("p:endSync/p:rtn", NS))
        step = seq_ctn.find("p:childTnLst/p:par/p:cTn", NS)
        self.assertEqual(step.find("p:stCondLst/p:cond", NS).get("delay"), "0")

    def test_t049_native_timings_read_back(self):
        """The canonical reader recovers the durations T049 recorded from COM."""
        deck = T049 / "one_slide_games_suite.pptx"
        if not deck.is_file():
            self.skipTest("T049 artifact not present")
        with zipfile.ZipFile(deck) as z:
            slide1 = E.fromstring(z.read("ppt/slides/slide1.xml"))
            slide2 = E.fromstring(z.read("ppt/slides/slide2.xml"))
        chests = [(a["action"], a["preset"], a["duration_ms"])
                  for a in anim.read_interactive_actions(slide1)]
        quiz = [(a["action"], a["preset"], a["duration_ms"])
                for a in anim.read_interactive_actions(slide2)]
        self.assertEqual(chests, [("hide", "zoom", 350)] * 3 + [("reveal", "zoom", 300)])
        self.assertEqual(quiz, [("reveal", "fade", 250)] * 3 + [("hide", "fade", 200)])


if __name__ == "__main__":
    unittest.main()
