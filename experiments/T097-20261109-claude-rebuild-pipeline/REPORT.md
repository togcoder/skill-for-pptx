# T097 [pptx] Dựng lại cả một bộ bằng agent: bóc tách, chấm điểm, chia chặng

Agent: Claude (Opus 5.5), trưởng nhóm. Ngày: 2026-11-09. Nhánh xếp sau T096 (cần bản `inventory` đã sửa).

## Vì sao

Chủ dự án nhờ một agent dựng lại bộ QCC 37 slide (ngoài repo) theo bản giao việc của trưởng nhóm, và loại
kết quả (xem T096, mục Ver4). Chủ dự án giao việc tiếp: nghiên cứu **cách chấm điểm**, **cách bóc tách
tài nguyên** của bộ gốc, và **cách hợp lý để các agent tái cơ cấu slide từ đầu đến cuối**.

## Tham khảo

Đọc lướt (phần tóm tắt, không đọc toàn văn):

- **PPTAgent** (Zheng và cộng sự, EMNLP 2025, arXiv 2501.03936):
  - sửa slide tham chiếu bằng các lệnh, thay vì dựng từ đầu, để giữ bố cục;
  - có bước phân tích bộ gốc thành sơ đồ nội dung;
  - tự sửa theo phản hồi khi chạy lệnh;
  - PPTEval chấm ba phần: nội dung, thiết kế, mạch.
- **AutoPresent / SlidesBench** (CVPR 2025): chấm hai kiểu, so với slide gốc (vị trí, nội dung, màu) và chấm
  thiết kế không cần slide gốc.
- **Auto-Slides** (arXiv 2509.11062) có agent kiểm tra riêng; **DeepPresenter** (ACL 2026 Findings) có
  người chấm chỉ nhìn sản phẩm.
- **DECKBench** (KDD 2026) chấm cả nhiều lượt làm theo yêu cầu.

Ba điều rút ra, khớp với lỗi của Ver4:

1. Sửa trên slide gốc.
2. Phân tích trước, sửa sau mỗi đợt theo kết quả chạy.
3. Người chấm tách khỏi người dựng.

## Đã làm

**Đồ nghề** (`scripts/pptx_tools.py`, D011: chỉ những việc chữ không làm được):

- **`extract DECK -o DIR`**: chép mọi ảnh và video gốc ra file (mỗi file một lần) và ghi `manifest.json`.
  Mỗi slide có:
  - chữ, notes;
  - số của biểu đồ, ô của bảng;
  - ảnh và video: file, vị trí theo % slide, phần ảnh còn thấy, có hiệu ứng không;
  - kiểu chuyển slide, số hiệu ứng.

  Lý do: agent Ver4 cắt ảnh từ ảnh chụp slide, nên ảnh mờ, mất chữ và mô phỏng không còn chạy.
- **`check BEFORE AFTER [--map map.json]`**: 8 cổng đạt/không.
  - Dùng chung cho cả bộ:
    1. kiểu chuyển slide;
    2. hiệu ứng trỏ tới vật thể đã xóa;
    3. đủ video;
    4. video tràn slide;
    5. đủ số;
    6. ảnh gốc không bị cắt chặt hơn bản gốc.
  - Cần map:
    7. slide `keep` đủ hiệu ứng;
    8. ảnh gốc nằm đúng slide, trừ ảnh ghi trong `drop`.

  Lệnh in thêm danh sách ảnh không lấy từ bộ gốc (bỏ qua hình nền lặp ở từ 3 slide trở lên). Ảnh được so
  theo hình (dHash 64 bit, lệch tối đa 6 bit), không theo byte: agent Ver4 đã lưu lại mọi ảnh nên không
  ảnh nào trùng byte, dù 46 ảnh vẫn là ảnh gốc.

**Lời hướng dẫn:**

- **Guide 11 mới** (`11-dung-lai-ca-bo.md`):
  - ba bước Hiểu → Làm → Kiểm; một agent làm được từ đầu đến cuối; các cổng máy agent tự chạy; chỉ dừng
    hỏi người dùng ở ba chỗ (bản hiểu ý, 3 slide mẫu, bản cuối);
  - dựng trên bản sao bộ gốc, kèm đoạn mã sắp lại thứ tự slide;
  - cách viết `map.json`;
  - chấm hai tầng: cổng máy trước, rồi mắt (4 phần, mỗi phần 1–5 điểm, có mốc 1/3/5, kèm 3 slide tệ
    nhất). Không cộng thành một con số, vì Giữ ruột 1 điểm thì bộ slide không dùng được (D001).
- **Guide 1, phần mới "Việc lớn: hỏi cho tới khi hiểu":** 7 điều.
  - Đọc hết trước khi hỏi. Mỗi vòng 3–5 câu, câu nào cũng có đề xuất.
  - Hỏi ý và gu, không hỏi kỹ thuật. Gu thì cho xem 2–3 phương án.
  - Đưa cả ý người dùng chưa nghĩ tới, nhưng chỉ như một lựa chọn.
  - Kể lại thành bản hiểu ý một trang.
  - Dừng khi không còn dấu "?" và người dùng nói "đúng". Ba vòng vẫn chưa rõ thì chọn theo đề xuất và đánh
    dấu lại; 3 slide mẫu là phép thử cuối.
- SKILL.md bước 1: việc nhỏ hỏi tối đa 2 câu, việc lớn hỏi theo vòng. SKILL.md trỏ tới guide 11 và hai lệnh
  mới; guide 9 có mục cho `extract` và `check`.
- **Vòng sửa theo chủ dự án:** bản đầu có 7 chặng. Chủ dự án thấy chặt chẽ nhưng quá dài, và đề nghị để
  agent hỏi cho tới khi chắc chắn hiểu ý. Rút còn 3 bước; các cổng giữ nguyên, nằm bên trong từng bước.

## Bằng chứng (bậc 1: lệnh chạy trên file thật, giữ ngoài repo)

- `extract` trên Ver3-4 (243 MB): 37 slide, 102 ảnh, 5 video, 85 file; 12 biểu đồ có số, 9 bảng, 37
  slide có notes. Lệnh nêu đúng 5 slide mô phỏng (648, 98, 40, 56 và 134 hiệu ứng).
- `check` Ver3-4 với chính nó: **6/8**. Hai cổng trượt là lỗi có sẵn trong bản gốc: chuyển slide cổ, 2
  video nhỏ. Các cổng giữ ruột đạt.
- `check` Ver3-4 → Ver4, map lấy từ dàn ý của chính agent: **2/8**. Lệnh bắt đúng các lỗi chủ dự án đã
  nêu:
  - chuyển slide cổ;
  - thiếu 1 video, 4 video chiếm 49–64% slide;
  - 976 hiệu ứng mô phỏng còn 0;
  - ảnh gốc vắng trên 29 slide.

  Danh sách ảnh lạ đúng là các ảnh chụp mô phỏng và 5 ảnh thành viên cắt nhỏ.
- `pytest`:
  - 2 test mới: `extract`; `check` đạt trên bản sao đúng, và trượt đúng 5 cổng khi làm mất từng thứ;
  - ảnh lưu lại vẫn được nhận là ảnh gốc;
  - 599 test qua.

## Áp vào dự án QCC (ngoài repo)

- Chặng 0 đã làm: thư mục extract, bảng tổng quan từng slide.
- Quy trình Ver5 theo 3 bước, có sẵn 5 câu hỏi vòng 1 và mốc so sánh Ver4. Bước 1 chờ câu chuyện sếp chốt.

## Không làm

- Không dùng model nhìn ảnh để chấm thiết kế bằng máy. Tầng 2 là mắt người hoặc agent khác (D001, D008).
- Không có lệnh chép slide giữa hai file kèm hiệu ứng: dựng trên bản sao và sắp lại thứ tự là đủ.
- Không làm bộ thành phần riêng cho QCC (đề nghị của DSH): skill dùng chung cho mọi bộ.
- dHash có trần: hai ảnh trơn hay gần trắng có thể bị nhận nhầm là một. Ghi `ponytail:` trong mã.

## Việc tiếp theo

Khi có câu chuyện sếp chốt: chạy bước 1 (Hiểu). Lần chạy đó là bài thử đầu tiên của guide 11. Chủ
dự án chấm ở chặng 2 và 6.
