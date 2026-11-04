"""The T065 hygiene rules: mojibake, duplicate task IDs, artifact size (lab/standards/OUTPUTS.md)."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"lab"/"tools"))
import check_layout  # noqa: E402

MOJI="".join(check_layout.MOJIBAKE)          # the four markers, built from the module
EMDASH_MOJI="â€"+chr(0x201D)                 # "â€”" as it appears in a damaged file
VIET="Báo cáo bằng tiếng Việt: đúng ý ngay từ lượt đầu — không lỗi mã hóa."


class MarkdownEncodingTests(unittest.TestCase):
    def write(self,text,newline="\n"):
        tmp=tempfile.NamedTemporaryFile("w",suffix=".md",delete=False,encoding="utf-8",newline="")
        tmp.write(text.replace("\n",newline))
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return Path(tmp.name)

    def test_the_markers_are_the_four_named_ones(self):
        self.assertEqual(MOJI,"Ãâ€á»Ä‘")

    def test_correct_vietnamese_is_not_flagged(self):
        self.assertEqual(check_layout._text_problems(self.write(VIET)),[])

    def test_mojibake_is_flagged_with_a_line_number(self):
        bad=self.write("ok line\nBáo cáo "+EMDASH_MOJI+" 2026\n")
        found=check_layout._text_problems(bad)
        self.assertEqual([(n,k) for n,k,_ in found],[(2,"mojibake")])

    def test_marker_only_code_spans_are_allowed(self):
        doc=self.write("The detector looks for `Ã`, `â€`, `á»` and `Ä‘` too.\n")
        self.assertEqual(check_layout._text_problems(doc),[])

    def test_code_span_with_real_text_is_still_checked(self):
        doc=self.write("Caption: `Hình 1 "+EMDASH_MOJI+" doanh thu`.\n")
        self.assertEqual([k for _,k,_ in check_layout._text_problems(doc)],["mojibake"])

    def test_a_line_can_quote_the_damage_with_a_pragma(self):
        doc=self.write("Example: `"+EMDASH_MOJI+"` is what `—` becomes. "
                       +check_layout.ALLOW_MOJIBAKE+"\n")
        self.assertEqual(check_layout._text_problems(doc),[])

    def test_bom_is_flagged(self):
        found=check_layout._text_problems(self.write("\ufeff# Title\n"))
        self.assertEqual([k for _,k,_ in found],["bom"])

    def test_control_characters_are_flagged(self):
        found=check_layout._text_problems(self.write("alpha\x07lpha\n"))
        self.assertEqual([(n,k) for n,k,_ in found],[(1,"control")])

    def test_invalid_utf8_is_flagged(self):
        path=Path(tempfile.mkdtemp())/"broken.md"
        path.write_bytes(b"caf\xe9\n")
        self.addCleanup(path.unlink)
        self.assertEqual([k for _,k,_ in check_layout._text_problems(path)],["not utf-8"])


class IndexTests(unittest.TestCase):
    def test_duplicate_ids_are_reported(self):
        rows=[("T001",30),("T002",31),("T001",44)]
        found=check_layout._duplicate_ids(rows)
        self.assertEqual(len(found),1)
        self.assertIn("T001",found[0])
        self.assertIn("30",found[0])

    def test_suffixed_ids_are_distinct(self):
        self.assertEqual(check_layout._duplicate_ids([("T047",1),("T047b",2),("T048",3)]),[])

    def test_the_real_index_has_no_duplicate_ids(self):
        self.assertEqual(check_layout._duplicate_ids(check_layout._index_ids()),[])


class SizeCapTests(unittest.TestCase):
    def test_file_over_two_megabytes_warns(self):
        files=[("experiments/T900-x/artifacts/big.pptx",3*1024*1024)]
        self.assertEqual(len(check_layout._size_warnings(files)),1)
        self.assertIn("2 MB/file",check_layout._size_warnings(files)[0])

    def test_task_over_ten_megabytes_warns_once(self):
        files=[(f"experiments/T900-x/artifacts/{i}.pptx",1024*1024) for i in range(11)]
        found=check_layout._size_warnings(files)
        self.assertEqual(len(found),1)
        self.assertIn("10 MB/task",found[0])

    def test_small_tree_is_quiet(self):
        self.assertEqual(check_layout._size_warnings([("experiments/T900-x/REPORT.md",1024)]),[])


if __name__=="__main__":
    unittest.main()
