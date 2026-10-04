import copy
import json
import unittest
from lxml import etree as E

from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from add_timeline import build_timing, inspect_timing_root, _path_data
from pack_timeline import compile_packed_timeline

P="http://schemas.openxmlformats.org/presentationml/2006/main"
NS={"p":P}


class TimelineWriterTests(unittest.TestCase):
    def plan(self):
        objects={
            "box":{"id":"box","morph_name":"!!box"},
            "dot":{"id":"dot","morph_name":"!!dot"},
        }
        slide={
            "id":"s1",
            "initial_objects":{
                "box":{"x":0.1,"y":0.2,"w":0.1,"h":0.1,"rotation_deg":0,"opacity":1},
                "dot":{"x":0.4,"y":0.2,"w":0.05,"h":0.05,"rotation_deg":0,"opacity":1},
            },
            "timeline":[
                {"id":"move","operation":"move","trigger":"on_click","duration_ms":1000,"effects":[
                    {"type":"motion_path","target":"box","path_kind":"polyline","points":[{"x":0.15,"y":0.25},{"x":0.35,"y":0.25}]},
                    {"type":"motion_path","target":"dot","path_kind":"polyline","points":[{"x":0.425,"y":0.225},{"x":0.50,"y":0.30}]},
                ]},
                {"id":"focus","operation":"focus","trigger":"on_click","duration_ms":800,"effects":[
                    {"type":"motion_path","target":"box","path_kind":"polyline","points":[{"x":0.35,"y":0.25},{"x":0.55,"y":0.5}]},
                    {"type":"scale","target":"box","from_w":0.1,"from_h":0.1,"to_w":0.2,"to_h":0.2},
                    {"type":"rotate","target":"dot","from_deg":0,"to_deg":90},
                ]},
                {"id":"settle","operation":"settle","trigger":"after_previous","duration_ms":400,"effects":[
                    {"type":"motion_path","target":"dot","path_kind":"polyline","points":[{"x":0.50,"y":0.30},{"x":0.52,"y":0.30}]},
                ]},
            ],
            "click_beats":[
                {"id":"beat-move","purpose":"Establish the first state.","stages":["move"],"pause_after":"presenter_explanation"},
                {"id":"beat-focus","purpose":"Focus then settle as one continuous idea.","stages":["focus","settle"],"pause_after":"slide_complete"},
            ],
        }
        return slide,objects

    def test_relative_path_keeps_waypoints_in_one_behavior(self):
        value=_path_data([
            {"x":0.2,"y":0.2},
            {"x":0.3,"y":0.25},
            {"x":0.4,"y":0.1},
        ])
        self.assertEqual(value,"M 0 0 L 0.100000 0.050000 L 0.200000 -0.100000 E")

    def test_click_beats_create_multiple_click_groups_and_after_effect(self):
        slide,objects=self.plan()
        timing,receipt=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        self.assertEqual(receipt["writer_mode"],"presenter-paced-click-beats")
        self.assertEqual(receipt["click_beat_count"],2)
        self.assertEqual(receipt["total_stage_duration_ms"],2200)
        self.assertEqual(receipt["behavior_count"],6)
        node_types=[n.get("nodeType") for n in timing.findall(".//p:cTn",NS)]
        self.assertEqual(node_types.count("clickEffect"),2)
        self.assertEqual(node_types.count("afterEffect"),1)
        main=timing.find(".//p:cTn[@nodeType='mainSeq']/p:childTnLst",NS)
        self.assertEqual(len(main.findall("p:par",NS)),2)
        behavior_delays=[
            n.get("delay")
            for n in timing.findall(".//p:cBhvr/p:cTn/p:stCondLst/p:cond",NS)
        ]
        self.assertTrue(behavior_delays)
        self.assertEqual(set(behavior_delays),{"0"})

    def test_scale_is_relative_to_authored_initial_size(self):
        slide,objects=self.plan()
        timing,_=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        scale=timing.find(".//p:animScale",NS)
        self.assertEqual(scale.find("p:from",NS).attrib,{"x":"100000","y":"100000"})
        self.assertEqual(scale.find("p:to",NS).attrib,{"x":"200000","y":"200000"})

    def test_rotate_uses_ooxml_angle_units(self):
        slide,objects=self.plan()
        timing,_=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        rotate=timing.find(".//p:animRot",NS)
        self.assertEqual(rotate.get("by"),str(90*60000))
        self.assertEqual(rotate.find(".//p:attrName",NS).text,"r")

    def test_build_list_has_baseline_and_stage_group_entries(self):
        slide,objects=self.plan()
        timing,receipt=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        entries=[(x.get("spid"),x.get("grpId"),x.get("animBg")) for x in timing.findall("p:bldLst/p:bldP",NS)]
        self.assertIn(("2","0","1"),entries)
        self.assertIn(("3","0","1"),entries)
        group_ids={
            str(stage["group_id"])
            for beat in receipt["click_beats"]
            for stage in beat["stages"]
        }
        self.assertTrue(group_ids)
        self.assertTrue(any(spid=="2" and grp in group_ids for spid,grp,_ in entries))
        self.assertTrue(any(spid=="3" and grp in group_ids for spid,grp,_ in entries))

    def test_unique_time_node_ids(self):
        slide,objects=self.plan()
        timing,_=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        ids=[x.get("id") for x in timing.findall(".//p:cTn",NS) if x.get("id")]
        self.assertEqual(len(ids),len(set(ids)))

    def test_t005_candidate_emits_four_presenter_click_beats(self):
        intent=json.loads(
            (ROOT/"experiments/T005-20261004-codex-choreography/candidate.intent.json")
            .read_text(encoding="utf-8")
        )
        plan=compile_packed_timeline(intent)
        slide=plan["slides"][0]
        objects={obj["id"]:obj for obj in plan["objects"]}
        mapping={obj["morph_name"]:str(i+2) for i,obj in enumerate(plan["objects"])}
        timing,receipt=build_timing(slide,objects,mapping)
        node_types=[n.get("nodeType") for n in timing.findall(".//p:cTn",NS)]
        self.assertEqual(receipt["click_beat_count"],4)
        self.assertEqual(receipt["behavior_count"],82)
        self.assertEqual(node_types.count("clickEffect"),4)
        self.assertEqual(node_types.count("afterEffect"),2)
        main=timing.find(".//p:cTn[@nodeType='mainSeq']/p:childTnLst",NS)
        self.assertEqual(len(main.findall("p:par",NS)),4)

    def test_forced_name_mismatch_is_rejected(self):
        slide,objects=self.plan()
        with self.assertRaises(ValueError):
            build_timing(slide,objects,{"!!box":"2"})

    def test_visibility_is_deliberately_not_guessed(self):
        slide,objects=self.plan()
        bad=copy.deepcopy(slide)
        bad["timeline"][0]["effects"]=[{"type":"visibility","target":"box","to":"visible"}]
        with self.assertRaisesRegex(ValueError,"visibility timing is not implemented"):
            build_timing(bad,objects,{"!!box":"2","!!dot":"3"})

    def test_structural_inspector_rejects_duplicate_ctn_ids(self):
        slide,objects=self.plan()
        timing,_=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        root=E.Element(f"{{{P}}}sld",nsmap={"p":P})
        cs=E.SubElement(root,f"{{{P}}}cSld")
        tree=E.SubElement(cs,f"{{{P}}}spTree")
        for sid,name in [("2","!!box"),("3","!!dot")]:
            sp=E.SubElement(tree,f"{{{P}}}sp")
            nv=E.SubElement(sp,f"{{{P}}}nvSpPr")
            E.SubElement(nv,f"{{{P}}}cNvPr",id=sid,name=name)
        root.append(timing)
        ids=timing.findall(".//p:cTn",NS)
        ids[-1].set("id",ids[-2].get("id"))
        report=inspect_timing_root(root)
        self.assertIn("duplicate cTn IDs",report["errors"])


if __name__=="__main__":
    unittest.main()
