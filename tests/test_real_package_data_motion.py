import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from make_data_motion_fixture import make_fixture
from inspect_existing_deck import inspect_existing_deck
from compile_data_motion_patch import compile_data_motion_patch
from patch_existing_timeline import patch_existing
from inspect_pptx import inspect as inspect_package

BASE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


def director_for(inv):
    slide=inv["slides"][0]
    chart=next(s for s in slide["shapes"] if s.get("name")=="Trend Chart")
    kpi=next(s for s in slide["shapes"] if s.get("name")=="Hero KPI")
    return {
        "version":"0.3",
        "kind":"existing-deck-motion-director",
        "source":{
            "pptx_sha256":inv["source_sha256"],
            "inventory_version":inv["version"],
            "source_slide_count":len(inv["slides"]),
        },
        "user_instruction":"Reveal the line chart, then count the KPI.",
        "script":{
            "source":"inferred",
            "summary":"Trend first, KPI conclusion second.",
            "evidence":["Native line chart and standalone KPI on slide 1."],
            "beats":["trend","kpi"],
        },
        "preservation":{
            "preserve_text_by_default":True,
            "preserve_media_by_default":True,
            "preserve_theme_by_default":True,
            "preserve_slide_order_by_default":True,
            "slide_count_policy":"preserve",
        },
        "slides":[{
            "source_index":1,
            "role":"evidence-to-result",
            "objective":"Explain the trend before landing the KPI.",
            "beats":[
                {
                    "id":"trend",
                    "purpose":"Reveal the native line chart.",
                    "operation":"chart-reveal",
                    "targets":[chart["name"]],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                    "data_motion":{
                        "kind":"chart",
                        "chart_type":"line",
                        "recipe":"series-trace",
                        "build":"series",
                        "animate_background":False,
                        "rationale":"Line chart communicates ordered progression.",
                    },
                },
                {
                    "id":"kpi",
                    "purpose":"Count to the final KPI.",
                    "operation":"kpi-highlight",
                    "targets":[kpi["name"]],
                    "reuse_existing":True,
                    "same_slide":True,
                    "timing_intent":"on-click",
                    "data_motion":{
                        "kind":"number-counter",
                        "recipe":"count-up",
                        "from_value":0,
                        "to_value":98.5,
                        "duration_ms":1200,
                        "steps":7,
                        "prefix":"",
                        "suffix":"%",
                        "decimal_places":1,
                        "implementation":"stepped-text",
                        "rationale":"The KPI is the conclusion and should land numerically.",
                    },
                },
            ],
            "click_beats":[
                {
                    "id":"click-trend",
                    "purpose":"Reveal trend evidence.",
                    "motion_beats":["trend"],
                    "stable_state":"The chart is fully visible.",
                    "pause_after":"presenter-explanation",
                    "boundary_reason":"First click establishes evidence.",
                },
                {
                    "id":"click-kpi",
                    "purpose":"Land the KPI.",
                    "motion_beats":["kpi"],
                    "stable_state":"98.5% is visible.",
                    "pause_after":"slide-complete",
                    "boundary_reason":"KPI waits until the trend has been explained.",
                },
            ],
            "components":[],
        }],
        "target_slide_count":len(inv["slides"]),
        "research_metadata":{"sources":[]},
    }


class RealPackageDataMotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.work=Path(self.tmp.name)
        self.fixture=self.work/"fixture.pptx"
        make_fixture(BASE,self.fixture)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fixture_is_real_package_and_inventory_sees_chart_kpi(self):
        package=inspect_package(self.fixture)
        self.assertEqual(package["errors"],[])
        inv=inspect_existing_deck(self.fixture)
        self.assertEqual(inv["errors"],[])
        self.assertEqual(len(inv["slides"]),2)
        chart=next(s for s in inv["slides"][0]["shapes"] if s.get("name")=="Trend Chart")
        kpi=next(s for s in inv["slides"][0]["shapes"] if s.get("name")=="Hero KPI")
        self.assertEqual(chart["kind"],"chart")
        self.assertEqual(chart["chart_summary"]["primary_type"],"line")
        self.assertEqual(chart["chart_summary"]["series_count"],2)
        self.assertEqual(chart["chart_summary"]["category_count"],4)
        self.assertEqual(kpi["data_semantics"]["standalone_number"]["numeric_value"],98.5)

    def test_real_package_end_to_end_data_motion(self):
        inv=inspect_existing_deck(self.fixture)
        director=director_for(inv)
        patch=compile_data_motion_patch(director,inv)
        patch_path=self.work/"patch.json"
        patch_path.write_text(json.dumps(patch),encoding="utf-8")
        output=self.work/"motion.pptx"

        with ZipFile(self.fixture) as z:
            before_slide2=z.read("ppt/slides/slide2.xml")
            before_chart=z.read("ppt/charts/chartT016.xml")
            before_rels=z.read("ppt/slides/_rels/slide1.xml.rels")

        receipt=patch_existing(self.fixture,patch_path,output)
        self.assertEqual(receipt["patched_slides"],[1])
        self.assertEqual(receipt["click_beat_count"],2)
        self.assertFalse(receipt["powerpoint_playback_verified"])

        package=inspect_package(output)
        self.assertEqual(package["errors"],[])
        out_inv=inspect_existing_deck(output)
        self.assertEqual(out_inv["errors"],[])
        timing=out_inv["slides"][0]["timing_summary"]
        self.assertEqual(timing["click_group_count"],2)
        chart_build=next(
            x for x in timing["build_entries"]
            if x["type"]=="bldGraphic" and x["target"] and x["target"]["name"]=="Trend Chart"
        )
        self.assertEqual(chart_build["build"],"series")
        self.assertEqual(chart_build["anim_bg"],"0")

        chart_effects=[
            effect for effect in timing["effects"]
            if effect["target"] and effect["target"]["name"]=="Trend Chart"
        ]
        self.assertEqual(len(chart_effects),2)
        self.assertEqual(
            [e["properties"]["chart_target"]["series_index"] for e in chart_effects],
            ["0","1"],
        )

        shapes=out_inv["slides"][0]["shapes"]
        source_kpi=next(s for s in shapes if s.get("name")=="Hero KPI")
        proxies=[s for s in shapes if (s.get("name") or "").startswith("__counter_")]
        self.assertEqual(source_kpi["text"],"98.5%")
        self.assertGreater(len(proxies),0)

        with ZipFile(output) as z:
            self.assertEqual(z.read("ppt/slides/slide2.xml"),before_slide2)
            self.assertEqual(z.read("ppt/charts/chartT016.xml"),before_chart)
            self.assertEqual(z.read("ppt/slides/_rels/slide1.xml.rels"),before_rels)

    def test_output_source_hash_differs_but_slide_count_does_not(self):
        inv=inspect_existing_deck(self.fixture)
        patch=compile_data_motion_patch(director_for(inv),inv)
        patch_path=self.work/"patch.json"
        patch_path.write_text(json.dumps(patch),encoding="utf-8")
        output=self.work/"motion.pptx"
        receipt=patch_existing(self.fixture,patch_path,output)
        self.assertNotEqual(receipt["sha256"],receipt["source_sha256"])
        self.assertEqual(
            len(inspect_existing_deck(output)["slides"]),
            len(inv["slides"]),
        )


if __name__=="__main__":
    unittest.main()
