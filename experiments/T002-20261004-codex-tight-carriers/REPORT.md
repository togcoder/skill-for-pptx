# T002 — Siết khung nền theo hộp chữ

Ngày 04/10/2026. Base main `2d93fa70c9441ac604b1bff8ef7a30b568b73830`.
Nhánh `work/T002-codex-20261004`, PR #2. Đánh giá tĩnh không mù bởi Codex/root.

## Kết quả

Giữ E004 làm baseline bất biến. Candidate giữ nguyên ba slide, thứ tự focus,
toàn bộ chữ, font, màu, label 360×96 px, vị trí label, ID, loại đối tượng,
hai Morph 1100 ms và renderer. Chỉ đổi x/y/w/h của ba carrier: focus từ
480×200 thành 404×112 px, context từ 400×150 thành 372×104 px, luôn căn giữa
quanh label. Kích thước được khóa trong brief trước khi dựng và không tune lại.

| Phép đo proxy tuyến tính | E004 | T002 |
|---|---:|---:|
| Cặp label có khoảng chồng / 6 | 0 | 0 |
| Cặp carrier có khoảng chồng / 6 | 6 | 0 |
| Đối tượng / textbox mỗi slide | 8 / 5 | 8 / 5 |
| Slide / Morph | 3 / 2 | 3 / 2 |

`verify_pair.py` kiểm tra toàn bộ plan và chỉ chấp nhận geometry của `*-block`
thay đổi. Diagnostic E003 giữ nguyên, giả định các hộp không xoay, nội suy đồng
bộ tuyến tính trên canvas 1280×720. Kết quả không mô phỏng easing hoặc playback
PowerPoint. Điểm native motion và real editing tiếp tục để null.

## PPTX và ảnh cuối

File `output/PPTX_Motion_Lab_T002.pptx`, SHA-256
`c41f2289bfd662f2642ea611b119d8aeaf35678425cba4cf4b7ffe0640922186`.
Package checker đạt: 3 slide, 8 native objects/slide, 5 textbox/slide, không
picture, Morph byObject nằm trên slide đích 2 và 3. Đây không phải kiểm tra full
OOXML schema. Finalizer đạt; artifact-tool import được file.

Đã render file cuối bằng artifact-tool 2.8.77, 1280×720, font Bitstream Charter
và xem riêng 3/3 ảnh trong `final-renders/`. Không thấy chữ bị cắt, xuống dòng
ngoài dự kiến hoặc chồng tĩnh. Focus vẫn lớn hơn context nhưng chênh lệch giảm.
Điểm tĩnh: brief 4/5, readability 5/5, creative 2/5, focus emphasis 3/5 so với
4/5 của E004. Đây là tradeoff chủ quan. Không có điểm tổng.

## Quyết định và giới hạn

Giữ candidate vì đạt mục tiêu geometry mà không đổi chữ, đường label, số đối
tượng hoặc slide. Quy tắc tái sử dụng: khi label path đã sạch nhưng carrier
path còn giao nhau, đo carrier riêng và thu gọn padding quanh label trước khi
đổi route. Giữ một chênh lệch kích thước có chủ đích cho focus rồi đánh giá
lại cả collision lẫn emphasis. Không dùng kích thước 404/372 như hằng số chung.

T002 không làm hiệu ứng trở nên ấn tượng hơn; nó loại một rủi ro occlusion
trong mô hình và làm bố cục gọn hơn. Cần exact-hash playback trong PowerPoint
để biết việc carrier lướt sát nhau có còn gây artefact, thứ tự che phủ hoặc
cảm giác chuyển động yếu. Không có môi trường PowerPoint ở lượt này.

## Kiểm tra và bước tiếp

`python3 -m unittest discover -s tests -v`: 34 tests đạt. Chạy
`python3 experiments/T002-20261004-codex-tight-carriers/verify_pair.py` để tái
lập phép đo; `package-report.json`, `validation.json`, `inventory.json` và
`environment.json` giữ bằng chứng. Không tìm nguồn web mới vì đây là sửa tiếp
trực tiếp cho gap đã ghi trong E004.

Tiếp theo: T001 phát chính file hash trên và E004 trong PowerPoint để so tác
động thật; hoặc T004 tách backend portable. Nếu tiếp tục T002, cần giả thuyết
mới về focus emphasis hoặc z-order, không lặp lại việc dò kích thước endpoint.
