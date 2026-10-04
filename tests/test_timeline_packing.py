import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from choreography import compile_intent
from pack_timeline import compile_packed_timeline, validate_timeline

EXPERIMENT=ROOT/"experiments/T005-20261004-codex-choreography"


class TimelinePackingTests(unittest.TestCase):
    def load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_candidate_packs_twelve_legacy_states_into_one_slide(self):
        intent=self.load(EXPERIMENT/"candidate.intent.json")
        legacy=compile_intent(intent)
        plan=compile_packed_timeline(intent)
        self.assertEqual(len(legacy["states"]),12)
        self.assertEqual(len(plan["slides"]),1)
        self.assertEqual([s["operation"] for s in plan["slides"][0]["timeline"]],
                         ["burst","orbit","focus","split","reassemble","restore"])
        meta=plan["research_metadata"]["motion_packing"]
        self.assertEqual(meta["legacy_state_count"],12)
        self.assertEqual(meta["final_slide_count"],1)
        self.assertEqual(meta["packed_motion_events"],6)
        self.assertEqual(meta["resource_set_changes"],0)
        self.assertEqual(validate_timeline(plan),[])

    def test_orbit_waypoints_become_path_points_not_slides(self):
        intent=self.load(EXPERIMENT/"candidate.intent.json")
        plan=compile_packed_timeline(intent)
        orbit=next(s for s in plan["slides"][0]["timeline"] if s["id"]=="orbit")
        paths=[e for e in orbit["effects"] if e["type"]=="motion_path"]
        self.assertTrue(paths)
        self.assertTrue(any(len(e["points"])==intent["orbit_segments"]+1 for e in paths))
        self.assertEqual(len(plan["slides"]),1)

    def test_initial_text_overrides_survive_packing(self):
        # Full-pipeline failure: phase has empty object text and state-only copy.
        # Check resolved text for every object on both frozen regression inputs.
        for path in (EXPERIMENT/"candidate.intent.json", EXPERIMENT/"transfer"/"intent.json"):
            intent=self.load(path)
            legacy=compile_intent(intent)
            plan=compile_packed_timeline(intent)
            source=legacy["states"][0]["objects"]
            packed=plan["slides"][0]["initial_objects"]
            for obj in legacy["objects"]:
                oid=obj["id"]
                self.assertEqual(packed[oid].get("text",obj.get("text")),
                                 source[oid].get("text",obj.get("text")))
            self.assertEqual(packed["phase"]["text"],"Lõi hệ thống")

    def test_focus_combines_motion_and_scale_on_same_resources(self):
        intent=self.load(EXPERIMENT/"candidate.intent.json")
        plan=compile_packed_timeline(intent)
        focus=next(s for s in plan["slides"][0]["timeline"] if s["id"]=="focus")
        target=f"node-{intent['focus_node']}-layer-1"
        kinds={e["type"] for e in focus["effects"] if e["target"]==target}
        self.assertEqual(kinds,{"motion_path","scale"})

    def test_transfer_also_packs_to_one_slide(self):
        intent=self.load(EXPERIMENT/"transfer"/"intent.json")
        plan=compile_packed_timeline(intent)
        self.assertEqual(len(plan["slides"]),1)
        self.assertEqual(plan["research_metadata"]["motion_packing"]["packed_motion_events"],6)
        self.assertEqual(validate_timeline(plan),[])

    def test_validator_rejects_unknown_target(self):
        intent=self.load(EXPERIMENT/"candidate.intent.json")
        plan=compile_packed_timeline(intent)
        bad=copy.deepcopy(plan)
        bad["slides"][0]["timeline"][0]["effects"][0]["target"]="missing-object"
        self.assertIn("unknown effect target: missing-object",validate_timeline(bad))


if __name__=="__main__":
    unittest.main()
