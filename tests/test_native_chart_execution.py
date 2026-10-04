import sys
import unittest
from pathlib import Path

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from chart_native_timing import (
    chart_fanout, concrete_chart_filter, guard_chart_fanout, ooxml_build_token,
)
from patch_existing_timeline import build_existing_timing, validate_patch_plan
from inspect_existing_deck import _timing_inventory, A, P

NS={"p":P,"a":A}


def chart_slide_root():
    xml=f"""<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
      <p:cSld><p:spTree>
        <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
        <p:grpSpPr/>
        <p:graphicFrame>
          <p:nvGraphicFramePr><p:cNvPr id="7" name="Trend Chart"/><p:cNvGraphicFramePr/><p:nvPr/></p:nvGraphicFramePr>
          <p:xfrm><a:off x="0" y="0"/><a:ext cx="100" cy="100"/></p:xfrm>
          <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">
            <c:chart r:id="rId5"/>
          </a:graphicData></a:graphic>
        </p:graphicFrame>
        <p:sp>
          <p:nvSpPr><p:cNvPr id="8" name="Not Chart"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
          <p:spPr/>
        </p:sp>
      </p:spTree></p:cSld>
    </p:sld>"""
    return E.fromstring(xml.encode())


def chart_plan(build="category-elements",series_count=2,category_count=3,fanout_limit=24):
    return {
        "version":"0.3",
        "kind":"existing-deck-timeline-patch",
        "source_sha256":"0"*64,
        "slides":[{
            "source_index":1,
            "stages":[{
                "id":"chart-reveal",
                "duration_ms":1200,
                "trigger":"on-click",
                "effects":[{
                    "type":"chart_entrance",
                    "target":{"source_id":"7","source_name":"Trend Chart"},
                    "chart_type":"column",
                    "build":build,
                    "series_count":series_count,
                    "category_count":category_count,
                    "animate_background":False,
                    "fanout_limit":fanout_limit,
                }],
            }],
            "click_beats":[{"id":"beat-chart","stages":["chart-reveal"]}],
        }],
    }


class NativeChartExecutionTests(unittest.TestCase):
    def test_chart_fanout_modes(self):
        self.assertEqual(chart_fanout("series",2,3),[(0,-4,"series"),(1,-4,"series")])
        self.assertEqual(
            chart_fanout("category-elements",2,2),
            [(0,0,"ptInCategory"),(1,0,"ptInCategory"),(0,1,"ptInCategory"),(1,1,"ptInCategory")],
        )
        self.assertEqual(ooxml_build_token("category-elements"),"categoryEl")

    def test_density_guard_degrades_large_point_fanout(self):
        guarded=guard_chart_fanout("series-elements",4,100,limit=24)
        self.assertTrue(guarded["degraded"])
        self.assertEqual(guarded["effective_build"],"series")
        self.assertEqual(guarded["fanout_count"],4)

    def test_type_specific_concrete_filters(self):
        self.assertEqual(concrete_chart_filter("column"),"wipe(up)")
        self.assertEqual(concrete_chart_filter("bar"),"wipe(right)")
        self.assertEqual(concrete_chart_filter("pie"),"wheel(1)")
        self.assertEqual(concrete_chart_filter("scatter"),"fade")

    def test_v03_plan_accepts_chart_entrance(self):
        self.assertEqual(validate_patch_plan(chart_plan()),[])

    def test_chart_entrance_rejected_on_legacy_plan(self):
        plan=chart_plan()
        plan["version"]="0.2"
        self.assertTrue(any("requires patch plan v0.3" in e for e in validate_patch_plan(plan)))

    def test_chart_writer_emits_subtargets_and_bldgraphic(self):
        root=chart_slide_root()
        plan=chart_plan()
        timing,receipt=build_existing_timing(plan["slides"][0],root)
        self.assertEqual(receipt["writer_mode"],"presenter-paced-click-beats")
        self.assertEqual(receipt["click_beat_count"],1)
        self.assertEqual(receipt["behavior_count"],6)
        chart_targets=timing.findall(".//a:chart",NS)
        self.assertEqual(len(chart_targets),6)
        self.assertEqual(
            {(x.get("seriesIdx"),x.get("categoryIdx"),x.get("bldStep")) for x in chart_targets},
            {
                ("0","0","ptInCategory"),("1","0","ptInCategory"),
                ("0","1","ptInCategory"),("1","1","ptInCategory"),
                ("0","2","ptInCategory"),("1","2","ptInCategory"),
            },
        )
        bld=timing.find("p:bldLst/p:bldGraphic/p:bldSub/a:bldChart",NS)
        self.assertIsNotNone(bld)
        self.assertEqual(bld.get("bld"),"categoryEl")
        self.assertEqual(bld.get("animBg"),"0")
        self.assertEqual(
            {n.get("filter") for n in timing.findall(".//p:animEffect",NS)},
            {"wipe(up)"},
        )

    def test_chart_writer_readback_exposes_build_and_subtargets(self):
        root=chart_slide_root()
        plan=chart_plan(build="series",series_count=2,category_count=3)
        timing,_=build_existing_timing(plan["slides"][0],root)
        root.append(timing)
        shapes=[
            {"id":"7","name":"Trend Chart","text":None,"kind":"chart"},
            {"id":"8","name":"Not Chart","text":None,"kind":"shape"},
        ]
        summary=_timing_inventory(root,shapes)
        self.assertEqual(summary["effect_count"],2)
        self.assertEqual(summary["build_entries"][0]["type"],"bldGraphic")
        self.assertEqual(summary["build_entries"][0]["build"],"series")
        self.assertEqual(summary["build_entries"][0]["anim_bg"],"0")
        targets=[e["properties"]["chart_target"] for e in summary["effects"]]
        self.assertEqual(
            targets,
            [
                {"series_index":"0","category_index":"-4","build_step":"series"},
                {"series_index":"1","category_index":"-4","build_step":"series"},
            ],
        )

    def test_chart_writer_density_guard_is_recorded(self):
        root=chart_slide_root()
        plan=chart_plan(build="series-elements",series_count=4,category_count=100,fanout_limit=24)
        timing,receipt=build_existing_timing(plan["slides"][0],root)
        effect=receipt["click_beats"][0]["stages"][0]["effects"][0]
        self.assertTrue(effect["fanout_degraded"])
        self.assertEqual(effect["effective_build"],"series")
        self.assertEqual(effect["fanout_count"],4)
        self.assertEqual(len(timing.findall(".//a:chart",NS)),4)

    def test_chart_effect_refuses_non_chart_source_shape(self):
        root=chart_slide_root()
        plan=chart_plan()
        effect=plan["slides"][0]["stages"][0]["effects"][0]
        effect["target"]={"source_id":"8","source_name":"Not Chart"}
        with self.assertRaisesRegex(ValueError,"is not a chart"):
            build_existing_timing(plan["slides"][0],root)


if __name__=="__main__":
    unittest.main()
