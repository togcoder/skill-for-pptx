import copy
import unittest
from lxml import etree as E

from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from add_timeline import build_timing, inspect_timing_root, _path_data

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
                {"id":"focus","operation":"focus","trigger":"after_previous","duration_ms":800,"effects":[
                    {"type":"motion_path","target":"box","path_kind":"polyline","points":[{"x":0.35,"y":0.25},{"x":0.55,"y":0.5}]},
                    {"type":"scale","target":"box","from_w":0.1,"from_h":0.1,"to_w":0.2,"to_h":0.2},
                    {"type":"rotate","target":"dot","from_deg":0,"to_deg":90},
                ]},
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

    def test_packed_group_uses_one_click_and_cumulative_delays(self):
        slide,objects=self.plan()
        timing,receipt=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        self.assertEqual(receipt["total_duration_ms"],1800)
        self.assertEqual(receipt["behavior_count"],5)
        self.assertEqual(len(timing.findall(".//p:cTn[@nodeType='clickEffect']",NS)),1)
        delays=[n.get("delay") for n in timing.findall(".//p:animMotion/p:cBhvr/p:cTn/p:stCondLst/p:cond",NS)]
        self.assertEqual(delays,["0","0","1000"])
        scale_delay=timing.find(".//p:animScale/p:cBhvr/p:cTn/p:stCondLst/p:cond",NS)
        rotate_delay=timing.find(".//p:animRot/p:cBhvr/p:cTn/p:stCondLst/p:cond",NS)
        self.assertEqual(scale_delay.get("delay"),"1000")
        self.assertEqual(rotate_delay.get("delay"),"1000")

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

    def test_build_list_has_baseline_and_group_entry_per_animated_shape(self):
        slide,objects=self.plan()
        timing,_=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        entries=[(x.get("spid"),x.get("grpId"),x.get("animBg")) for x in timing.findall("p:bldLst/p:bldP",NS)]
        self.assertEqual(entries,[("2","0","1"),("2","4","1"),("3","0","1"),("3","4","1")])

    def test_unique_time_node_ids(self):
        slide,objects=self.plan()
        timing,_=build_timing(slide,objects,{"!!box":"2","!!dot":"3"})
        ids=[x.get("id") for x in timing.findall(".//p:cTn",NS) if x.get("id")]
        self.assertEqual(len(ids),len(set(ids)))

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
