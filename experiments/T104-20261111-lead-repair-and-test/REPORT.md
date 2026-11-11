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

**1. `watch`: slide không xem được thì dòng báo cáo thiếu khóa `clicks`.** Sửa: dòng lỗi giờ có
`"enter": "unknown", "clicks": []`, nên mọi dòng báo cáo đều có đủ khóa và bước đọc báo cáo không còn
`KeyError`. Test PowerPoint thật `test_watch_the_real_show` qua.

**2. `ungroup`: nhóm có vật xoay trong nhóm bị kéo không đều bị từ chối.** Sửa: khi phép biến đổi của
python-pptx không biểu diễn được nhóm (skew, gương+xoay), `ungroup` giữ nguyên nhóm đó (sao lưu XML rồi
khôi phục), ghi file, rồi gọi `Shape.Ungroup()` của PowerPoint trên chính file đầu ra; nếu PowerPoint cũng
không tách được thì báo lỗi. Thêm test native `test_skewed_group_falls_back_to_powerpoint_ungroup` (nhóm
lệch trục + vật con xoay) — qua.

**Thử trên file thật:** `_scratch/lead/a2_group17.pptx`, lệnh
`python scripts/pptx_tools.py ungroup "QCC - SHARP Team Ver3-4.pptx" 13 "Group 17" -o ...` →
`flattened 0 group(s) on slide 13; 1 group(s) flattened by PowerPoint`; kiểm lại bằng python-pptx: group
"Group 17" không còn, 6 vật con thành 6 vật mức trên (một vật là "Group 19" lồng bên trong, PowerPoint giữ
nguyên). Đây là đúng nhóm mà T101 từng phải gọi COM tay.

**Nghiệm thu A2:** `PPTX_NATIVE=1 python -m pytest tests -q` → **652 passed, 10 skipped, 63 subtests
passed** (50 s) trên máy này.

## A3. Một trang cho model nhỏ

**Đã làm.** `skills/pptx/CARD.md` — **38 dòng** (giới hạn 60): việc "đưa bộ có sẵn vào theme" từ đầu đến
cuối, 7 lệnh theo đúng thứ tự (shell → tiêu đề → fit → gắn vỏ → glance --ink → glance → compare), ba việc
kiểm trước khi giao (`glance` + mở từng ảnh, mỗi slide một dòng "đã thấy gì" + `seen`, `check --map` đủ cổng
ruột), và danh sách cấm. `SKILL.md` trỏ tới CARD ngay dưới tiêu đề, cùng một dòng nói các skill khác trong
`skills/` là đồ cũ (chỉ dùng cho việc này).

**Luật 5 — tổng số dòng `skills/pptx/` không tăng.** Đo bằng:
`python -c "from pathlib import Path; print(sum(len(p.read_text(encoding='utf-8').splitlines()) for p in Path('skills/pptx').rglob('*.md')))"`

| Mốc | Số dòng | Ghi chú |
|---|---|---|
| Bản chốt `baseline-2026-11-11` | **1907** | 16 file |
| Sau A1 (gộp PR #85) | 1938 | +31 dòng hướng dẫn của T102 |
| Sau A3 | **1890** | 17 file (thêm CARD 38 dòng), thấp hơn bản chốt 17 dòng |

Cắt ở đâu: SKILL.md 150 → 116 (14 điều cấm mỗi điều một dòng; mục model nhỏ còn 6 gạch; bảng lệnh còn 11
dòng, phần chi tiết đã có ở guide 9); guide 13 171 → 132 (bỏ phần "kiểm" trùng guide 8, giữ bảng nghĩa các
lỗi); guide 11 181 → 168 (10 luật cứng thay vì 12, gộp các ý trùng). Không cắt nội dung nào chỉ có một chỗ.

## A4. Tài liệu sai trong thư mục dự án (chủ dự án đồng ý ngày 2026-11-11)

Chỉ **đánh dấu là lỗi thời, không xoá**; hai file trong thư mục dự án (ngoài repo):

1. `docs/08_VER4_BRIEF.md`, mục §3.4 "Biểu đồ: thay hết, cùng một kiểu": thêm khối **LỖI THỜI** ngay dưới
   tiêu đề, nói rõ mục này trái với `guides/11` và cổng `charts kept` / `chart data kept`: chart gốc giữ
   đúng loại và dữ liệu, chỉ đổi cách trình bày khi có người duyệt ghi trong `map.json`.
2. `source/qcc_builders/build_theme_cab_v6.py`: thêm khối **LỖI THỜI** sau docstring (STEPS là tên bước
   chung, không dùng cho QCC; SCALE bắt đầu 18 px = 13,5 pt trên khung 20×11,25 in, dưới sàn 18 pt; các số
   156,179 / 64,950 là số mẫu, không phải số bộ gốc), kèm một dòng ngay trên `STEPS` và trên `SCALE`.

Không sửa nội dung nào khác; không đụng file gốc 37 slide.

## B1. Vào theme, cả bộ (37 slide)

**Cách làm.** Một script dựng `_scratch/lead/b1/build_b1.py` (trong thư mục dự án, ngoài repo), mỗi lần
chạy đều đọc `QCC - SHARP Team Ver3-4.pptx` và ghi file mới. Các bước: `shell` gỡ vỏ cũ (2 vật master,
2 vật lặp trên slide) → `motion {'transitions': {'default': 'none'}}` dọn 16 kiểu chuyển slide cũ → tiêu đề
cũ thành tiêu đề theme (giữ chữ; slide không có tiêu đề lấy tên bước) → `fit --into 0.67,2.2,18.67,8.3` co
nội dung → gắn vỏ theme (ver4_lib của dự án: nền, thanh bước, logo, tiêu đề, chân trang) → `glance --ink
1D2433` đổi mực 204 run chữ không đọc được → `glance`. Cùng một lần chạy mất khoảng 4 phút.

**Kết quả `glance`** (lệnh đã chạy, log `_scratch/lead/b1/glance.txt` trên máy):
`python scripts/pptx_tools.py glance "_scratch/lead/b1/QCC_SHARP_Team_Ver3-4_in_v6.pptx"` →
**15 / 37 slide còn lỗi**, tất cả đều là lỗi có sẵn của nội dung gốc hoặc giới hạn của mức 1; từng dòng lý
do ở bảng dưới.

**Kết quả `check`** (`python scripts/pptx_tools.py check GOC MOI --map map.json` với map 37 hàng `reskin`):
**12/13 cổng đạt** — đạt đủ các cổng giữ ruột: `effects intact`, `videos kept 5/5`, `numbers kept`,
`pictures not cut`, `source pictures on their slide`, `charts kept`, `chart data kept`, `tables kept`,
`every slide accounted for`, `charts valid`, `transitions`, `keep slides keep their effects`. Cổng trượt:
`videos fill the slide` (slide 12 = 26%, slide 15 = 52% — video gốc nhỏ, có sẵn trong bản gốc, không phải
cổng giữ ruột).

**Bằng chứng đã nhìn** (file `_scratch/lead/KIEM_B1.md` trên máy, do Lead dựng):
- `glance` xuất 37 ảnh `slide-NN.png`; một bạn trong nhóm (slide-scout) mở **37/37** bằng `read_image`,
  đọc mã nhìn từng ảnh, viết mỗi slide một dòng "đã thấy gì"; `seen` trả **"37 of 37 pictures proven seen"**.
- `compare` xuất 37 ảnh cặp `pair-NN.jpg`; một bạn khác (pair-scout) mở **37/37**, mỗi cặp ghi ba cột
  mất / tệ hơn / thêm; `seen` trả **"37 of 37 pictures proven seen"**.
- Lead tự mở các ảnh lỗi chính: `faults-02/05/06/08/17/22/26/37.png` (mô tả trong KIEM_B1.md).

**15 slide còn lỗi và lý do để lại:**

| slide | lỗi glance | lý do |
|---|---|---|
| 2 | text on picture | bố cục gốc đặt dòng "Satisfy customer requirements" ngay trên ảnh sản phẩm (mức 1 giữ cách sắp xếp của tác giả) |
| 5 | tiny text | bảng APQP/MLA/TQP gốc dùng chữ 15 pt — có sẵn trong bộ gốc |
| 6 | text on text; tiny text (chart 14 pt) | nhãn "100mm/659841" và "x3pcs" chạm nhau sau khi co 0,93; chữ chart 14 pt có sẵn |
| 8 | tiny text (bảng 10,5 pt); content under Footer | bảng Gantt gốc 32×21 cao hơn vùng nội dung theme; không giảm chữ thêm vì đã dưới sàn |
| 12 | tiny text (chart 9 pt) | chart gốc, có sẵn |
| 17 | tiny text | nhãn 15 pt của bản gốc |
| 21 | tiny text | đoạn giải thích 16 pt của bản gốc |
| 22 | tiny text | bảng so sánh máy 11 pt của bản gốc |
| 23 | tiny text | nhãn INNER/OUTER 13,5 pt của bản gốc |
| 26 | text on picture ×2; cannot read (bảng) | hai bảng gốc lớn hơn vùng nội dung, hàng tự nới; chữ bảng 8–9 pt có sẵn |
| 27 | tiny text (chart 16 pt); same picture twice ×2 | chart và ảnh bằng chứng lặp có sẵn trong bố cục gốc |
| 28 | tiny text (chart 12 pt + chữ 13,5 pt) | có sẵn |
| 32 | tiny text (chart 16 pt + chữ 14 pt) | có sẵn |
| 35 | tiny text (chart 16 pt) | có sẵn |
| 37 | text hidden | ảnh chibi gốc che chữ "SHARP Team"; bìa và slide kết chưa gắn vỏ theme (để riêng như T100) |

Chưa làm được ở B1: **bìa (slide 1) và slide kết (37) giữ nội dung gốc, chưa có vỏ theme**; nội dung
15 slide trên (chữ nhỏ, nhãn chồng) cần mức 2 mới sửa được — B2 làm 3 slide mẫu.

### B1 v2 — theo góp ý của chủ dự án ngày 2026-11-11 (ô tô nền phải di chuyển có ý đồ)

Chủ dự án: "tôi muốn phần ô tô ở background di chuyển đến những vị trí có ý đồ bổ trợ bố cục hơn là đứng
im 1 chỗ" và yêu cầu sửa được các lỗi đã tìm ra. Đã sửa trong **cùng một script dựng** (vẫn đọc bộ gốc mỗi
lần chạy, không vá file kết quả):

**Ô tô nền (và quầng sáng) theo bố cục.** Với mỗi slide, script đo hộp nội dung sau khi co, rồi chấm các vị
trí ứng viên (trái/phải × 4 mức dọc × 3 cỡ) trong dải giữa tiêu đề và chân trang — chỗ đè lên chữ bị phạt
nặng, đè lên hình/card bị phạt vừa, chạm dải tiêu đề hoặc chân trang bị phạt nặng hơn — chọn chỗ trống gần
nhất, cỡ xe theo khoảng trống, quầng sáng đặt ở góc đối diện. Kết quả: xe nằm ở nhiều vị trí khác nhau tuỳ
nội dung từng slide (trái/phải, chân/đỉnh), không đứng im một chỗ, không chui dưới footer hay dưới thẻ
chart; slide tràn hình (9, 14, 29) không có xe vì không có nền trống để đặt. Đây là chỗ sửa đúng ý "bổ trợ
bố cục": nội dung lệch phải thì xe sang trái, slide trống bên phải thì xe to hơn, slide đầy chân trang thì xe
nhỏ và nép góc trên.

**Các lỗi đã sửa (glance 15 → 5 slide lỗi):**
- toàn bộ lỗi "tiny text" của **chart** (slide 6, 12, 27, 28, 32, 35): chữ trong chart nâng lên sàn 18 pt;
- slide 6: nhãn "x3pcs" dời ra khỏi nhãn "100mm 659841" (fit đã làm hai nhãn chạm nhau);
- slide 8: bảng Gantt gốc 32×21 — bỏ margin ô và giãn dòng 84% để bảng kết thúc **trên** chân trang (trước đó
  tràn xuống dưới footer);
- slide 26: hai bảng kiểm chứng — cùng cách, hàng không còn đè lên kết luận; hết lỗi chữ không đọc được;
- slide 21, 22, 23, 28: chữ thân bài dưới 18 pt nâng lên 18 pt (box đã đủ chỗ); slide 28 nới hộp hai nhãn
  "INNER"/"OUTER" để 18 pt không xuống dòng;
- slide 32: nhãn "ACHIEVE TARGET" 18 pt + nới hộp, chart không còn bị đè;
- slide 37 (slide kết): thêm nền/logo/footer của theme, chữ "SHARP Team" đưa lên trên ảnh mascot, mascot co
  lại để không chạy dưới footer;
- bìa (slide 1) giữ nguyên làm **mức 0** (slide tràn hình video, theme cũng không đặt tiêu đề lên bìa).
- qua bốn vòng soát ảnh của nhóm (mỗi vòng một người mở lại cả 37 ảnh), các chỗ xe còn đè chữ/card đã được
  xử lý: xe bị chặn khỏi thẻ trắng/chart/table (phạt nặng khi đè), nhỏ lại (900–1200 px), và khi không còn
  góc sạch thì chỉ để một mép xe thò vào; quầng sáng cố định một góc (quầng sáng di chuyển làm glance báo
  "missing"); slide 28 nhãn INNER/OUTER đổi sang trắng 18 pt một dòng và đưa lên trên hình.

**Kết quả B1 v2** (lệnh như cũ): `glance` → **5 / 37 slide lỗi** (2, 5, 8, 17, 27), tất cả là nội dung gốc
hoặc ý tác giả: slide 2 chữ nằm trên ảnh sản phẩm của bố cục gốc; slide 5 timeline 15 pt; slide 8 bảng Gantt
10,5 pt; slide 17 nhãn sơ đồ 15 pt; slide 27 ảnh before/after dùng lại cùng ảnh để so sánh. Sửa tiếp năm chỗ
này là sửa nội dung/bố cục mức 2 (tách bảng, đổi bố cục), không phải việc "vào theme".
`check --map` vẫn **12/13** (cổng trượt là video gốc nhỏ); `seen` lại 37/37 ảnh slide và 37/37 ảnh cặp với
mã mới; `compare` xuất lại 37 cặp cũ/mới cho bộ v2.

## B2. Dựng lại bố cục, ba slide mẫu (mục 14)

Ba slide chọn: **13** (ảnh bằng chứng — teardown SPK), **18** (số liệu + biểu đồ — before/after + chart),
**22** (bảng — so sánh 3 máy). Cách làm: `_scratch/lead/b2/build_b2.py` mỗi vòng lấy bản mức 1 (B1) làm
nguồn, `ungroup` nhóm cần tách (A2 dùng `Shape.Ungroup` của PowerPoint cho nhóm 17), đặt lại bằng `arrange`
với bố cục JSON theo vùng, xuất 3 slide thành một file mẫu, rồi `glance` + mở ảnh. Mỗi vòng tối đa 3 điều
tệ nhất, sửa trong script, dựng lại từ bản mức 1 (không vá file kết quả).

| Vòng | `glance` | Mắt thấy (ba điều tệ nhất) |
|---|---|---|
| 1 | 2/3 slide lỗi (slide 18: chữ banner tràn + đè ảnh; slide 22: 69% chữ dưới 18 pt) | 13: dải trống lớn dưới ảnh, công cụ nhỏ lệch trái; 18: ảnh before/after bị bóp còn 1/3, nhãn "Before/After" rơi xuống đáy, chart cắt nhãn "134,61…"; 22: tiêu đề cột 3 bị ảnh che, phụ đề "Dots = rating" 10 pt |
| 2 | 1/3 slide lỗi (slide 22: phụ đề tràn xuống hàng 1) | 13: sạch; 18: bố cục before–after–chart đã rõ nhưng nhãn "Before/After" rời khỏi ảnh, chart vẫn cắt "134,61 5…"; 22: phụ đề 18 pt tràn khỏi ô header |
| 3 | **0/3 slide lỗi** | 13: sạch; 18: ảnh before/after to, đúng cặp; còn chart cắt nhãn số "134,61 5…" và "0…" (định dạng chart gốc, muốn sửa phải sửa nhãn dữ liệu chart — không thuộc bố cục); 22: bảng đọc được, tiêu đề cột 3 vẫn sát mép nhưng không bị che; phụ đề 14 pt |

**`glance` file mẫu:** `python scripts/pptx_tools.py glance "...B2_samples_round3.pptx"` → **0 slide lỗi**.
**`seen`:** mở 3/3 ảnh slide + 3/3 ảnh cặp cũ/mới (`compare ... --map`), `seen` trả "3 of 3 pictures proven
seen" cho cả hai bộ.
**Giữ vật:** `check GOC B2 --map` (map 3 hàng `rebuild` + 34 slide `dropped` vì đây là file mẫu 3 slide) →
11/13 cổng đạt; đạt `effects intact`, `pictures not cut`, `source pictures on their slide`, `charts kept`,
`chart data kept`, `tables kept`, `every slide accounted for`, `transitions`; hai cổng `videos kept` và
`numbers kept` không áp dụng cho file mẫu 3 slide (bộ gốc có 5 video/161 số ở 34 slide không lấy).
**Không thêm vật:** ngoài vỏ theme (`!!*`, Logo, Title, Footer, Footer rule, Page number, Cause chip) mọi
vật trên 3 slide đều lấy từ slide gốc; ở slide 13 chữ của "TextBox 37" ("Teardown SPK") được đưa lên tiêu
đề theme (giữ nguyên chữ, bỏ hộp — đúng mục 14: tiêu đề của tác giả thành tiêu đề theme).
**Chưa làm được ở B2:** nhãn dữ liệu chart 43 ("134,61 5…", "0…") bị cắt — lỗi định dạng của chart gốc,
sửa được nhưng sẽ đổi cách trình bày số của chart, ngoài phạm vi "chỉ sắp lại".

**B2 (bản cuối, cùng đợt sửa):** ba slide mẫu dựng lại từ bản B1 cuối (nền theme mới, xe đặt theo bố cục,
chữ chart 18 pt), cùng bố cục ba vòng đã duyệt; `glance` **0/3**, `seen` **3/3** ảnh slide và **3/3** ảnh
cặp, `check` trên ba slide giữ đủ ảnh/chart/bảng/effect (11/13 cổng, hai cổng video/số không áp dụng cho
file mẫu 3 slide). File `_scratch/lead/b2/QCC_SHARP_Team_B2_samples.pptx`; cặp cũ/mới
`_scratch/lead/b2/pairs/pair-01..03.jpg`. Còn một chỗ chịu: nhãn số của chart 43 vẫn bị cắt ("134,61…",
"0…") vì chart gốc có nhãn hẹp — sửa là sửa định dạng chart, ngoài "chỉ sắp lại".

## B3. Chạy mù bằng model nhỏ, đúng một lần

**Cách chạy.** Sandbox `_scratch/lead/b3/` chỉ có: `CARD.md` (38 dòng), `scripts/` (đồ nghề), `GOC_8.pptx`
(8 slide đầu của bộ gốc), `THEME_v6.pptx` (bộ mẫu theme), `VIEC.md` (đề bài: đưa 8 slide đầu vào theme, tự
kiểm theo CARD, không hỏi ai). Một phiên mới của model nhỏ (deepseek-v4.1-flash, subagent mới, không thấy
gì của phiên Lead) làm một mình. Lead không giúp, không trả lời câu hỏi.

**Kết quả (nguyên văn báo cáo của nó, đối chiếu với file trong sandbox):**

| Câu hỏi | Kết quả |
|---|---|
| Có đọc `CARD.md` không? | **có** — thứ tự lệnh nó chạy đúng thứ tự trong CARD (shell → gỡ vỏ → tiêu đề → `fit` → vỏ theme → `glance --ink` → `glance` → `check` → `compare` → `seen`); nó đọc cả phần `fit`/`glance` trong `pptx_tools.py` |
| Có chạy `glance` và `seen` không? | **có** — `glance` trên bản gốc và trên bản cuối; `seen out/glance_xong 1=N4Y … 8=4BW` trả **"8 of 8 pictures proven seen"** |
| Có tự viết script chấm không? | **không** — chỉ script dựng (`a_titles.py`, `c_shell.py`) và script chỉ-đọc để xem XML; mọi phép đo bằng `glance`/`check`/`compare`/`seen` |
| Còn bao nhiêu slide lỗi? | **4 / 8 slide** (5, 6, 7, 8), 6 dòng, **tất cả là `tiny text`**: slide 5 bảng 15 pt, slide 6 chart 14 pt, slide 7 và 8 nhãn dải bước 16,5 pt của chính theme, slide 8 bảng Gantt 8,3 pt — đều là chữ nhỏ có sẵn hoặc do bảng gốc quá lớn |
| Hỏng/kẹt ở bước nào? | (1) nó **chép nguyên vỏ theme kể cả tên bước** ("Theme selection", "Current status"...) thay vì lấy tên bước từ thanh bước cũ của QCC — sai nghĩa bước; (2) bìa video và slide nền đá full-bleed phải để mức 0; (3) bảng Gantt phải `scale --by 0.79` trước `fit` mới không tràn chân trang; (4) 4 slide còn `tiny text`, phải mức 2 mới sửa; (5) phải tự viết script chép vỏ theme vì skill không có lệnh "áp theme" |

Nó tự khai: `check` trên 8 slide của nó đạt **13/13 cổng**; file cuối
`_scratch/lead/b3/out/5_xong.pptx` (8 slide, 20×11,25 in).

## B4. Chủ dự án chấm

Chỉ chủ dự án nói "đạt". Bản giao: file B1, ba slide B2 + cặp cũ/mới, bảng B3.

## Kết luận thẳng

- **Model mạnh: dùng được.** Bộ 37 slide vào theme bằng một script dựng từ bản gốc trong ~4 phút; `check`
  giữ ruột 12/13 cổng (cổng trượt là video gốc nhỏ có sẵn); sau vòng sửa theo góp ý chủ dự án, `glance` chỉ
  còn **5 slide lỗi**, cả năm là nội dung gốc hoặc ý tác giả (chữ trên ảnh nền của bố cục gốc, timeline/bảng
  Gantt chữ nhỏ có sẵn, nhãn sơ đồ 15 pt, ảnh before/after dùng lại) — sửa tiếp là mức 2; ô tô nền giờ đặt
  theo bố cục từng slide thay vì đứng im. Ba slide dựng lại bố cục đạt `glance` 0 lỗi, `seen` chứng minh
  3/3 + 3/3 ảnh đã mở. Hai lỗi thật của đồ nghề lộ ra trong quá trình làm đã được sửa và gộp (PR #91).
- **Model nhỏ: dùng được cho mức 1, chưa dùng được cho mức 2.** Bằng chứng: một phiên mới của
  deepseek-v4.1-flash, chỉ có CARD.md + đồ nghề, đã tự làm xong 8 slide vào theme: đọc CARD, chạy đúng thứ
  tự lệnh, `glance` + `seen` đầy đủ (8/8), `check` 13/13, không tự viết script chấm. Nó còn 4/8 slide lỗi
  `tiny text` — đều là chữ nhỏ có sẵn/giới hạn mức 1 — và mắc một lỗi nghĩa: chép nguyên tên bước của theme
  thay vì tên bước của bộ gốc. Nghĩa là CARD đủ để model nhỏ làm đúng *quy trình* và không tự lừa mình,
  nhưng kết quả vẫn cần người/máy kiểm, và việc "hiểu nghĩa" (tên bước, chỗ nào cần mức 2) vẫn là chỗ hỏng
  của model nhỏ.
- **Đồ nghề vẫn thiếu một lệnh**: không có lệnh "áp vỏ theme" (cả Lead lẫn model nhỏ đều phải tự viết
  builder để chép vỏ). Đây là việc nên làm tiếp, cùng với cổng đo "thêm vật" cho file mẫu.
