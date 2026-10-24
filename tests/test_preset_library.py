"""T027: every PowerPoint-authored preset can be written and read back."""
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

from lxml import etree as E

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))

import motion_engine as me
import pptx_animator as anim
from validate_director_plan import _library_effect

FIXTURE=ROOT/"tests"/"fixtures"/"picture_deck.pptx"


class PresetLibraryTests(unittest.TestCase):
    def test_library_covers_every_class(self):
        classes={}
        for v in anim.LIBRARY.values():
            classes[v["presetClass"]]=classes.get(v["presetClass"],0)+1
        self.assertEqual(classes,{"entr":52,"exit":52,"emph":30,"path":64})

    def test_every_preset_writes_with_scaled_timing_and_simulates(self):
        with ZipFile(FIXTURE) as z:
            base=z.read("ppt/slides/slide2.xml")
        for name,lib in anim.LIBRARY.items():
            root=E.fromstring(base)
            spid=next(k for k,v in anim.top_level_objects(root).items() if v.find(".//p:txBody",anim.NS) is not None)
            eff={"preset":name,"spid":spid,"trigger":"click","duration_ms":800}
            anim.apply_timeline(root,[{"id":"c","effects":[eff]}])
            ctn=root.find(".//p:cTn[@presetClass]",anim.NS)
            self.assertEqual((ctn.get("presetClass"),int(ctn.get("presetID")),int(ctn.get("presetSubtype"))),
                             (lib["presetClass"],lib["presetID"],lib["presetSubtype"]),name)
            ids=[c.get("id") for c in root.iter(anim.q("cTn"))]
            self.assertEqual(len(ids),len(set(ids)),name)
            self.assertNotIn("{spid}",E.tostring(root,encoding="unicode"),name)
            spans=[int(c.get("dur"))+sum(int(d.get("delay")) for d in c.iterfind(f"{{{anim.P}}}stCondLst/{{{anim.P}}}cond")
                                         if (d.get("delay") or "").isdigit())
                   for c in ctn.find("p:childTnLst",anim.NS).iter(anim.q("cTn")) if (c.get("dur") or "").isdigit()]
            if lib["span_ms"]>1:
                self.assertLessEqual(abs(max(spans)-800),2,name)
            me.advance({spid:me.fresh_state()},[eff])  # simulator accepts it

    def test_director_plans_may_name_library_effects(self):
        self.assertTrue(_library_effect("ppt:boomerang"))
        self.assertFalse(_library_effect("ppt:not-a-preset"))


if __name__=="__main__":
    unittest.main()
