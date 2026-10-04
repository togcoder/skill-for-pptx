import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from inspect_existing_deck import inspect_existing_deck
from insert_helper_components import insert_helpers

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


def shape_by_name(inventory,slide_index,name):
    return next(s for s in inventory["slides"][slide_index-1]["shapes"] if s["name"]==name)


class HelperComponentSynthesisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.work=Path(self.temp.name)
        self.inventory=inspect_existing_deck(SOURCE)

    def tearDown(self):
        self.temp.cleanup()

    def write_plan(self,components,source=SOURCE):
        path=self.work/"plan.json"
        plan={
            "version":"0.1",
            "kind":"existing-deck-helper-components",
            "source_sha256":hashlib.sha256(Path(source).read_bytes()).hexdigest(),
            "components":components,
        }
        path.write_text(json.dumps(plan),encoding="utf-8")
        return path,plan

    def test_shape_helper_clones_donor_style_and_preserves_other_slide(self):
        donor=shape_by_name(self.inventory,1,"!!h001-inspect-block")
        g=donor["geometry"]
        component={
            "source_index":1,
            "donor":{"source_id":donor["id"],"source_name":donor["name"]},
            "new_name":"AI Focus Helper",
            "role":"temporary focus frame",
            "rationale":"The narrative needs a temporary focus surface around Inspect without replacing the source block.",
            "data_provenance":"synthetic-nondata",
            "geometry":{"x":g["x"]-0.01,"y":g["y"]-0.01,"w":g["w"]+0.02,"h":g["h"]+0.02,"rotation_deg":0},
            "text_action":"clear",
        }
        plan_path,_=self.write_plan([component])
        out=self.work/"out.pptx"
        report=insert_helpers(SOURCE,plan_path,out)
        self.assertTrue(report["requires_reinventory"])
        after=inspect_existing_deck(out)
        helper=shape_by_name(after,1,"AI Focus Helper")
        self.assertNotEqual(helper["id"],donor["id"])
        self.assertEqual(helper["style"],donor["style"])
        self.assertIsNone(helper["text"])
        self.assertEqual(after["slides"][0]["shape_count"],self.inventory["slides"][0]["shape_count"]+1)
        with ZipFile(SOURCE) as before, ZipFile(out) as changed:
            second=self.inventory["slides"][1]["part"]
            self.assertEqual(before.read(second),changed.read(second))

    def test_text_helper_clones_text_style_and_replaces_content(self):
        donor=shape_by_name(self.inventory,2,"!!h001-inspect-label")
        g=donor["geometry"]
        component={
            "source_index":2,
            "donor":{"source_id":donor["id"],"source_name":donor["name"]},
            "new_name":"AI Focus Caption",
            "role":"temporary explanatory caption",
            "rationale":"The focus beat needs a concise temporary caption tied to the existing Inspect visual.",
            "data_provenance":"derived-from-source",
            "geometry":{"x":g["x"],"y":g["y"]+0.08,"w":g["w"],"h":g["h"],"rotation_deg":0},
            "text_action":"replace",
            "text":"Focus: Inspect",
        }
        plan_path,_=self.write_plan([component])
        out=self.work/"out.pptx"
        insert_helpers(SOURCE,plan_path,out)
        after=inspect_existing_deck(out)
        helper=shape_by_name(after,2,"AI Focus Caption")
        self.assertEqual(helper["text"],"Focus: Inspect")
        self.assertEqual(helper["style"]["font_family"],donor["style"]["font_family"])
        self.assertEqual(helper["style"]["text_color"],donor["style"]["text_color"])

    def test_source_hash_mismatch_fails(self):
        donor=shape_by_name(self.inventory,1,"!!h001-inspect-block")
        g=donor["geometry"]
        component={
            "source_index":1,
            "donor":{"source_id":donor["id"],"source_name":donor["name"]},
            "new_name":"Hash Guard",
            "role":"focus frame",
            "rationale":"Required for a focus beat.",
            "data_provenance":"none",
            "geometry":{"x":g["x"],"y":g["y"],"w":g["w"],"h":g["h"]},
            "text_action":"clear",
        }
        plan_path,plan=self.write_plan([component])
        plan["source_sha256"]="0"*64
        plan_path.write_text(json.dumps(plan),encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"Source SHA-256 does not match"):
            insert_helpers(SOURCE,plan_path,self.work/"out.pptx")

    def test_missing_donor_fails(self):
        component={
            "source_index":1,
            "donor":{"source_id":"999999","source_name":"Missing"},
            "new_name":"Missing Donor Helper",
            "role":"focus frame",
            "rationale":"Required for a focus beat.",
            "data_provenance":"none",
            "geometry":{"x":0.1,"y":0.1,"w":0.2,"h":0.2},
            "text_action":"clear",
        }
        plan_path,_=self.write_plan([component])
        with self.assertRaisesRegex(ValueError,"donor shape not found"):
            insert_helpers(SOURCE,plan_path,self.work/"out.pptx")


if __name__=="__main__":
    unittest.main()
