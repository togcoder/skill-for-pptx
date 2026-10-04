import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from inspect_existing_deck import inspect_existing_deck
from inspect_pptx import inspect, P
from patch_existing_timeline import patch_existing

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"
NS={"p":P}


def write_plan(path,source,slide_index,shape):
    geom=shape["geometry"]
    cx=geom["x"]+geom["w"]/2
    cy=geom["y"]+geom["h"]/2
    plan={
        "version":"0.1",
        "kind":"existing-deck-timeline-patch",
        "source_sha256":hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        "slides":[{
            "source_index":slide_index,
            "stages":[{
                "id":"focus",
                "duration_ms":700,
                "trigger":"on-click",
                "effects":[
                    {
                        "type":"motion_path",
                        "target":{"source_id":shape["id"],"source_name":shape["name"]},
                        "points":[{"x":cx,"y":cy},{"x":cx+0.02,"y":cy}],
                    },
                    {
                        "type":"scale",
                        "target":{"source_id":shape["id"],"source_name":shape["name"]},
                        "from_x":1.0,"from_y":1.0,"to_x":1.1,"to_y":1.1,
                    },
                ],
            }],
        }],
    }
    path.write_text(json.dumps(plan),encoding="utf-8")
    return plan


class ExistingDeckTimelinePatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.work=Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_patch_targets_existing_object_and_preserves_other_slide_bytes(self):
        inventory=inspect_existing_deck(SOURCE)
        shape=inventory["slides"][0]["shapes"][0]
        plan_path=self.work/"plan.json"
        write_plan(plan_path,SOURCE,1,shape)
        out=self.work/"out.pptx"
        report=patch_existing(SOURCE,plan_path,out)
        self.assertEqual(report["patched_slides"],[1])
        final=inspect(out)
        self.assertEqual(final["errors"],[])
        self.assertEqual(final["slides"][0]["timing_elements"],1)
        self.assertEqual(final["slides"][1]["timing_elements"],0)
        reinventory=inspect_existing_deck(out)
        summary=reinventory["slides"][0]["timing_summary"]
        self.assertIsNotNone(summary)
        self.assertEqual(summary["effect_count"],2)
        self.assertEqual([effect["type"] for effect in summary["effects"]],["animMotion","animScale"])
        self.assertEqual({effect["target_spid"] for effect in summary["effects"]},{shape["id"]})
        self.assertEqual(summary["order_basis"],"numeric-behavior-delay")
        self.assertEqual(summary["click_group_count"],1)
        self.assertEqual(summary["click_groups"][0]["effect_count"],2)
        self.assertIn("clickEffect",summary["click_groups"][0]["start_node_types"])
        with ZipFile(SOURCE) as before, ZipFile(out) as after:
            self.assertEqual(
                before.read(final["slides"][1]["part"]),
                after.read(final["slides"][1]["part"]),
            )

    def test_plain_nonforced_name_can_be_patched(self):
        renamed=self.work/"renamed.pptx"
        with ZipFile(SOURCE) as src, ZipFile(renamed,"w") as dst:
            for item in src.infolist():
                data=src.read(item.filename)
                if item.filename=="ppt/slides/slide1.xml":
                    root=E.fromstring(data)
                    props=root.find("p:cSld/p:spTree/p:sp/p:nvSpPr/p:cNvPr",NS)
                    self.assertIsNotNone(props)
                    props.set("name","Plain Source Object")
                    data=E.tostring(root,encoding="UTF-8",xml_declaration=True,standalone=True)
                dst.writestr(item,data)
        inventory=inspect_existing_deck(renamed)
        shape=inventory["slides"][0]["shapes"][0]
        self.assertEqual(shape["name"],"Plain Source Object")
        self.assertIsNone(shape["forced_semantic_name"])
        plan_path=self.work/"plan.json"
        write_plan(plan_path,renamed,1,shape)
        out=self.work/"out.pptx"
        report=patch_existing(renamed,plan_path,out)
        self.assertEqual(report["patched_slides"],[1])
        self.assertEqual(inspect(out)["slides"][0]["timing_elements"],1)

    def test_source_hash_mismatch_is_rejected(self):
        inventory=inspect_existing_deck(SOURCE)
        shape=inventory["slides"][0]["shapes"][0]
        plan_path=self.work/"plan.json"
        plan=write_plan(plan_path,SOURCE,1,shape)
        plan["source_sha256"]="0"*64
        plan_path.write_text(json.dumps(plan),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"Source SHA-256 does not match"):
            patch_existing(SOURCE,plan_path,self.work/"out.pptx")

    def test_wrong_native_name_is_rejected(self):
        inventory=inspect_existing_deck(SOURCE)
        shape=inventory["slides"][0]["shapes"][0]
        plan_path=self.work/"plan.json"
        plan=write_plan(plan_path,SOURCE,1,shape)
        plan["slides"][0]["stages"][0]["effects"][0]["target"]["source_name"]="Wrong Name"
        plan_path.write_text(json.dumps(plan),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"source object not found"):
            patch_existing(SOURCE,plan_path,self.work/"out.pptx")

    def test_existing_timing_is_not_merged_blindly(self):
        inventory=inspect_existing_deck(SOURCE)
        shape=inventory["slides"][0]["shapes"][0]
        first_plan=self.work/"first.json"
        write_plan(first_plan,SOURCE,1,shape)
        first=self.work/"first.pptx"
        patch_existing(SOURCE,first_plan,first)

        reinventory=inspect_existing_deck(first)
        shape2=reinventory["slides"][0]["shapes"][0]
        second_plan=self.work/"second.json"
        write_plan(second_plan,first,1,shape2)
        with self.assertRaisesRegex(ValueError,"already has native timing"):
            patch_existing(first,second_plan,self.work/"second.pptx")


if __name__=="__main__":
    unittest.main()
