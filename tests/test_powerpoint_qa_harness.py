import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

from inspect_existing_deck import inspect_existing_deck
from patch_existing_timeline import patch_existing
from make_powerpoint_qa_manifest import build_manifest
from verify_powerpoint_qa import verify
from build_powerpoint_qa_fixture import build_qa_fixture

SOURCE=ROOT/"output"/"PPTX_Motion_Lab_H001.pptx"


class PowerPointQaHarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.work=Path(self.tmp.name)
        inv=inspect_existing_deck(SOURCE)
        target=inv["slides"][0]["shapes"][0]
        plan={
            "version":"0.5",
            "kind":"existing-deck-timeline-patch",
            "source_sha256":inv["source_sha256"],
            "slides":[{
                "source_index":1,
                "stages":[{
                    "id":"reveal-one",
                    "duration_ms":350,
                    "trigger":"on-click",
                    "effects":[{
                        "type":"shape_entrance",
                        "target":{"source_id":target["id"],"source_name":target["name"]},
                        "filter":"fade",
                    }],
                }],
                "click_beats":[{"id":"click-1","stages":["reveal-one"]}],
            }],
        }
        plan_path=self.work/"patch.json"
        plan_path.write_text(json.dumps(plan),encoding="utf-8")
        self.output=self.work/"qa-target.pptx"
        patch_existing(SOURCE,plan_path,self.output)
        self.manifest=build_manifest(self.output)

    def tearDown(self):
        self.tmp.cleanup()

    def good_evidence(self):
        expected=self.manifest["slides"][0]
        target=expected["expected_target_names"][0]
        return {
            "version":"0.1",
            "kind":"powerpoint-native-qa-evidence",
            "artifact":{
                "sha256":self.manifest["pptx_sha256"],
                "expected_sha256":self.manifest["pptx_sha256"],
                "exact_hash_match":True,
            },
            "powerpoint":{
                "com_created":True,
                "presentation_opened":True,
                "slide_count":self.manifest["slide_count"],
                "version":"16.0",
            },
            "slides":[{
                "index":expected["index"],
                "effect_count":1,
                "effects":[{
                    "shape_name":target,
                    "timing":{"trigger_type":1,"trigger_name":"on-page-click"},
                }],
                "sequence_error":None,
            }],
            "slideshow":{
                "attempted":True,
                "success":True,
                "slides":[{
                    "index":expected["index"],
                    "expected_click_count":1,
                    "native_click_count":1,
                    "initial_click_index":-1,
                    "clicks":[{
                        "click":1,
                        "before_index":-1,
                        "after_index":1,
                        "index_matches":True,
                    }],
                }],
            },
            "errors":[],
        }

    def test_manifest_freezes_exact_output_hash_and_clicks(self):
        expected_hash=hashlib.sha256(self.output.read_bytes()).hexdigest()
        self.assertEqual(self.manifest["pptx_sha256"],expected_hash)
        self.assertEqual(self.manifest["slide_count"],2)
        self.assertEqual(self.manifest["animated_slide_count"],1)
        slide=self.manifest["slides"][0]
        self.assertEqual(slide["index"],1)
        self.assertEqual(slide["expected_click_count"],1)
        self.assertEqual(slide["structural_effect_count"],1)
        self.assertTrue(slide["expected_target_names"])
        self.assertTrue(self.manifest["acceptance"]["visual_state_review_required"])

    def test_verifier_promotes_native_parse_and_click_but_not_visual(self):
        result=verify(self.manifest,self.good_evidence())
        self.assertTrue(result["claims"]["native_application_parse_verified"])
        self.assertTrue(result["claims"]["native_click_execution_verified"])
        self.assertFalse(result["claims"]["visual_state_verified"])
        self.assertEqual(result["overall_status"],"native-click-pass-pending-visual-review")

    def test_click_count_mismatch_fails_click_claim(self):
        evidence=self.good_evidence()
        evidence["slideshow"]["slides"][0]["native_click_count"]=2
        result=verify(self.manifest,evidence)
        self.assertTrue(result["claims"]["native_application_parse_verified"])
        self.assertFalse(result["claims"]["native_click_execution_verified"])
        check=next(c for c in result["checks"] if c["name"]=="native-click-count")
        self.assertFalse(check["passed"])

    def test_hash_mismatch_fails_native_parse_claim(self):
        evidence=self.good_evidence()
        evidence["artifact"]["sha256"]="0"*64
        evidence["artifact"]["exact_hash_match"]=False
        result=verify(self.manifest,evidence)
        self.assertFalse(result["claims"]["native_application_parse_verified"])
        self.assertEqual(result["overall_status"],"failed")

    def test_missing_target_fails_native_parse_claim(self):
        evidence=self.good_evidence()
        evidence["slides"][0]["effects"][0]["shape_name"]="wrong-shape"
        result=verify(self.manifest,evidence)
        self.assertFalse(result["claims"]["native_application_parse_verified"])

    def test_composite_qa_fixture_has_chart_counter_and_focus_clicks(self):
        composite=self.work/"composite.pptx"
        manifest_path=self.work/"composite-manifest.json"
        result=build_qa_fixture(composite,manifest_path)
        manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(result["sha256"],manifest["pptx_sha256"])
        self.assertEqual(manifest["slide_count"],2)
        by_slide={slide["index"]:slide for slide in manifest["slides"]}
        self.assertEqual(by_slide[1]["expected_click_count"],2)
        self.assertEqual(by_slide[2]["expected_click_count"],1)
        self.assertIn("Trend Chart",by_slide[1]["expected_target_names"])
        self.assertIn("Hero KPI",by_slide[1]["expected_target_names"])
        self.assertGreater(by_slide[1]["structural_effect_count"],2)
        self.assertEqual(by_slide[2]["structural_effect_count"],2)

    def test_probe_script_contains_native_click_apis_and_visual_capture_boundary(self):
        script=(ROOT/"scripts"/"powerpoint_native_probe.ps1").read_text(encoding="utf-8")
        for token in ("GetClickCount","GetClickIndex","GotoClick","GotoSlide","MainSequence","Get-FileHash"):
            self.assertIn(token,script)
        self.assertIn("visual_state_verified = $false",script)


if __name__=="__main__":
    unittest.main()
