import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from make_motion_semantics_matrix import authored_layout_path, stage_local_path
from audit_motion_semantics_matrix import _normalized_slide
from lxml import etree as E


class MotionSemanticsMatrixTests(unittest.TestCase):
    def test_stage_local_paths_repeat_the_same_delta(self):
        first=[{"x":.20,"y":.55},{"x":.45,"y":.55}]
        second=[{"x":.45,"y":.55},{"x":.70,"y":.55}]
        self.assertEqual(stage_local_path(first),"M 0 0 L 0.250000 0.000000 E")
        self.assertEqual(stage_local_path(second),"M 0 0 L 0.250000 0.000000 E")

    def test_authored_layout_paths_encode_distinct_stage_anchors(self):
        initial={"x":.20,"y":.55}
        first=[{"x":.20,"y":.55},{"x":.45,"y":.55}]
        second=[{"x":.45,"y":.55},{"x":.70,"y":.55}]
        self.assertEqual(authored_layout_path(first,initial),
                         "M 0 0 L 0.250000 0.000000 E")
        self.assertEqual(authored_layout_path(second,initial),
                         "M 0.250000 0 L 0.500000 0.000000 E")

    def test_nonfinite_coordinates_fail(self):
        with self.assertRaises(ValueError):
            stage_local_path([{"x":0,"y":0},{"x":math.inf,"y":0}])

    def test_normalization_hides_only_path_and_behavior_fill(self):
        ns="http://schemas.openxmlformats.org/presentationml/2006/main"
        def xml(path,fill,target="3"):
            root=E.Element(f"{{{ns}}}sld",nsmap={"p":ns})
            timing=E.SubElement(root,f"{{{ns}}}timing")
            motion=E.SubElement(timing,f"{{{ns}}}animMotion",path=path)
            behavior=E.SubElement(motion,f"{{{ns}}}cBhvr")
            E.SubElement(behavior,f"{{{ns}}}cTn",fill=fill)
            target_el=E.SubElement(behavior,f"{{{ns}}}tgtEl")
            E.SubElement(target_el,f"{{{ns}}}spTgt",spid=target)
            return E.tostring(root)
        self.assertEqual(_normalized_slide(xml("M 0 0 E","remove")),
                         _normalized_slide(xml("M 1 0 E","hold")))
        self.assertNotEqual(_normalized_slide(xml("M 0 0 E","remove","3")),
                            _normalized_slide(xml("M 0 0 E","remove","4")))


if __name__=="__main__":
    unittest.main()
