# T104 [pptx] Sửa skill rồi chứng minh nó dùng được — bản giao việc 2026-11-11

Agent: lead (DeepSeek-V4.1-Flash, DSH). Nhánh `work/T104-lead-repair-and-test`, bắt đầu từ nhãn
`baseline-2026-11-11` (commit 66b8052). Việc: `docs/BRIEF_TU_BO_SKILL.md`. File của chủ dự án nằm ngoài
repo; kết quả chạy để ở `QCC - SHARP Team/_scratch/lead/` trên máy, không đưa vào repo.

## A1. Gộp bản vá đang mở (PR #85) và sửa hai luật báo nhầm

**Đã làm.** Gộp `work/T102-antigravity-glance-table-chart-fit-guards` vào nhánh này, gỡ bốn xung đột
(`scripts/pptx_tools.py`, `docs/CHANGELOG.md`, `domains/pptx/DOMAIN.md`, `research/tasks/INDEX.md`) và giữ
cả hai phía: `arrange`/`seen`/mã nhìn của T101 + các kiểm tra bảng, biểu đồ, PUA, ảnh trùng, nền rối,
meta-text của T102.

**Hai luật báo nhầm đã sửa (đều là luật mới của T102, không phải của bản chốt):**

1. **Số bước mờ trên thanh bước bị báo "cannot read".** T102 bỏ điều kiện T100 cố ý dùng — chỉ đọc ô chữ
   từ 2 ký tự trở lên — nên các số bước một ký tự (`6`, `7`, `8`, `9`) bị đem đo tương phản với nền thanh
   bước tối và bị báo sai. Sửa: trả lại điều kiện `len(text) >= 2` trong `_facts` (một ký tự là số bước,
   không phải nội dung). Đo trên bộ gốc bằng `glance`: trước sửa 57 dòng "cannot read" cho số bước một ký
   tự, sau sửa 0.
2. **Ký tự Wingdings hiện đúng bị báo "broken symbol".** Chữ có `\uf0e8` nằm trong run lai: font Latin
   `Arial`, font ký hiệu `Wingdings` khai trong `<a:sym>`; PowerPoint vẽ đúng bằng Wingdings nhưng
   `run.Font.Name` chỉ trả `Arial`, nên `_pua_hits` coi là thiếu glyph. Sửa: đọc thêm `Font.NameOther` bên
   COM (`_run_faces`) và `<a:rPr>/<a:sym@typeface>` bên XML (`_slide_text_notes`) rồi mới xét PUA. Đo trên
   bộ gốc: trước sửa 8 dòng "broken symbol", sau sửa 0. Ký tự PUA thật không có font ký hiệu vẫn bị báo
   (Ver7 còn đúng 1 dòng, đã mở `faults-28.png` xác nhận: run chỉ có `Arial`, không có `<a:sym>` → tofu).

**Nghiệm thu A1 — chạy `glance` trên bốn bộ đối chứng.** Bản chốt = nhãn `baseline-2026-11-11`; "trước A1"
đo bằng chính công cụ bản chốt tại máy này; "sau A1" đo bằng công cụ nhánh này. Lệnh cho cả bốn bộ:
`python scripts/pptx_tools.py glance "<bộ>.pptx" -o _scratch/lead/glance_a1/<bộ>` (log ở
`QCC - SHARP Team/_scratch/lead/glance_a1/g_*.txt`).

| Bộ | Bản giao việc ghi | Máy này, bản chốt | Sau A1 | Ngưỡng A1 | Kết quả |
|---|---|---|---|---|---|
| Bộ gốc Ver3-4 | 16 / 37 | 12 / 37 | **18 / 37** | không quá 18 | đạt |
| Theme v6 | 8 / 13 | 8 / 13 | **9 / 13** | không quá 9 | đạt |
| Ver7 | 36 / 37 | 36 / 37 | **36 / 37** | từ 36 lên | đạt |
| Ver5 | 23 / 39 | 22 / 39 | **22 / 39** | từ 23 lên | **không đạt tuyệt đối**: máy này đo bản chốt đã là 22, sau A1 vẫn 22 (không thoái lui) |

Hai chỗ lệch tuyệt đối so với bản giao việc (16→12 và 23→22) có từ **trước** khi sửa, trên cùng file, cùng
lệnh: nhiều khả năng do môi trường đo (bản giao việc đo ở máy khác). Không có bộ nào bị A1 làm tăng lỗi;
Ver3-4 tăng từ 12 lên 18 là do các kiểm tra mới bắt lỗi thật (xem dưới), vẫn trong ngưỡng 18.

**Các loại lỗi mới trên bộ gốc đã mở ảnh xác nhận là lỗi thật** (ảnh trong
`_scratch/lead/glance_a1/ver34/`, mở ở cỡ 1600×900):

- `faults-06.png` — `text on picture`: ba nhãn `25mm/100mm/200mm 659840…` chữ trắng, nền hộp bán trong
  suốt, dòng số nằm trực tiếp trên ảnh xe sáng → đọc kém; đồng thời `tiny text` ở hai biểu đồ (14 pt).
- `faults-08.png` — `tiny text` ở bảng Gantt gốc `Table 4` (nhỏ nhất 10,5 pt): lỗi có sẵn của bộ gốc.
- `faults-26.png` — `cannot read` ô bảng `Table 12`: ký tự `▲` vàng trên nền xanh nhạt, gần như không thấy.
- `faults-27.png` — `same picture twice`: cùng hai ảnh bằng chứng (bản vẽ keo + ảnh máy) xuất hiện hai lần
  trên một slide, cộng thêm `tiny text` biểu đồ (16 pt).

**Test.** `python -m pytest tests -q` → **648 passed, 13 skipped**; native
`PPTX_NATIVE=1 python -m pytest tests/test_glance.py tests/test_fidelity_gates.py -q` → **32 passed**.
`python lab/tools/check_layout.py` → `layout OK`; `python lab/tools/coord.py check` → `coordination OK`.
Chưa đạt ở đây: `test_watch_the_real_show` (native) vẫn hỏng — việc của A2.

**Giới hạn.** Gộp T102 làm `skills/pptx/` tăng 31 dòng (1907 → 1938); luật 5 của bản giao việc đòi tổng
số dòng không tăng, nên A3 phải cắt bù khi thêm `CARD.md`. Hai mốc tuyệt đối 16/37 và 23/39 của bản giao
việc không tái tạo được trên máy này; ghi nhận thay vì sửa số.

## A2. Hai lỗi đã biết của đồ nghề

(chờ làm)

## A3. Một trang cho model nhỏ

(chờ làm)

## B. Thử nghiệm

(chờ làm)
