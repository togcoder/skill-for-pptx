# T003 — Tách lớp, ghép lại và ràng buộc chi tiết

Ngày: 04/10/2026. Tác giả/đánh giá: Codex/root, không mù. Base GitHub main:
`24606a4c823f2786f92d9862d036ac1e5eceeaf5`. PR #1, nhánh `work/T003-codex-20261004`.

## Kết luận có bằng chứng

Giữ generator 2D có 3–5 lớp, quy tắc tọa độ con theo lớp và ô số rộng 60 px.
Đã dựng hai chủ đề: mô-đun QUANTA năm lớp và nền tảng học trực tuyến bốn lớp.
Mỗi bài có tổng thể → tách lớp → ghép lại, hai khai báo Morph 1100 ms. Bộ dựng
và renderer cũ không bị đổi; các đối tượng vẫn là rect/ellipse/textbox native.
Đây là công thức sơ đồ hoạt động ở mức cấu trúc và ảnh tĩnh, chưa chứng minh
chuyển động đẹp hoặc đúng trong PowerPoint, chưa phải skill đã cài đặt.

| So sánh | Trước | Sau | Loại bằng chứng |
|---|---:|---:|---|
| Chi tiết sai offset, QUANTA | 16/60 | 0/60 | Phép đo: ablation cố ý → candidate v1 |
| Độ lệch offset lớn nhất | 64 px | 0 px | Hình học endpoint; kéo theo bất biến nếu nội suy tịnh tiến đồng bộ tuyến tính |
| Ô số xuống hai dòng, QUANTA | 15/15 | 0/15 | Đếm bằng mắt từ 3 ảnh cuối: v1 → v2 |
| Ô số xuống hai dòng, bài học trực tuyến | 12/12 | 0/12 | Đếm bằng mắt từ 3 ảnh cuối: v1 → v2 |
| Tests của repo | 29 trước task | 34 đạt | Thêm 5 tests cho miền input, đóng cảnh, ràng buộc và giới hạn proxy |

Hai phép so sánh tách biệt: lỗi ràng buộc là **fixture được chủ động tạo**;
lỗi số xuống dòng là **lỗi thật phát hiện khi xem output**. Không dùng ablation
để tuyên bố đã cải thiện từ một generator sản xuất hoặc một benchmark độc lập.

## Thiết kế, nguồn và giới hạn sáng tạo

Brief và rubric được commit trước khi dựng tại GitHub `9826c2716eaf6af9b623d7f686f79320b5e67ba0`.
Đọc `BRIEF.md`, `rubric.json`, `SOURCES.md`. Ý đồ: mở khoảng cách giữa các bộ
phận để giải thích vai trò, rồi quay lại cấu trúc ban đầu. Đường đi giữ thứ tự,
không hoán đổi các lớp. Số/màu nối lớp di chuyển với rail đứng yên; chi tiết con
dùng tọa độ cục bộ. Đây là đối tượng phẳng riêng, không phải nhóm PowerPoint.

Nguồn sơ cấp đã đọc: Microsoft Morph tips và tutorial layer diagram của
Presentation Process. Chỉ đọc nội dung trang, **không quan sát video animation
của nguồn**. Tutorial gợi ý các tầng 3D; backend hiện tại không có extrusion,
camera hay chiều sâu. Tác phẩm này chỉ là diễn giải 2D độc lập. Không copy tài
sản bên ngoài, không khẳng định đã tái tạo hiệu ứng tham khảo 3D. Vì vậy T003
mới hoàn thành phần recipe 2D; phần phân tích choreography nguồn và đánh giá
độ ấn tượng của chuyển động vẫn mở.

## Lỗi, sửa và đối chứng giữ nguyên

Generator v1 đặt số 01–05 vào textbox 42×32 px, font 23 px. Cả validator lẫn
package checker đều đạt nhưng ảnh cho thấy hai chữ số xuống dòng. Giữ toàn bộ
v1 tại `generator-v1.py`, `plan.json`, `candidate-renders/` và PPTX v1. V2 chỉ
tăng chiều rộng của textbox số từ 42 lên 60 px. Không sửa font, chữ, vị trí,
carrier, thời lượng hoặc rubric. `verify_study.py` so sánh toàn bộ kế hoạch,
không chỉ những trường mong đợi, để xác nhận đúng thay đổi này.

Ablation giữ child ở vị trí ban đầu khi carrier tách ra. Candidate lấy vị trí
child = parent + offset ở từng cảnh. Cùng 20 child × 3 cảnh, 16 lệch biến mất;
bốn child của lớp giữa vốn không di chuyển. Khoảng hở carrier ở endpoint nhỏ
nhất 4 px; nội suy tuyến tính đồng bộ giữ khoảng hở dương. Không kết luận
PowerPoint dùng đúng nội suy này. Proxy từ chối input xoay hoặc thay kích thước.

Lần render cuối đầu tiên thiếu biến `RUNTIME_NODE_MODULES`; lệnh dừng trước khi
render. Đặt biến từ runtime rồi chạy thành công. Đây là lỗi thiết lập lệnh,
không phải quota hoặc lỗi của PPTX. Không gặp thông báo giới hạn sử dụng.

## Bài thử chủ đề mới

Agent `layer_forward` nhận một ngữ cảnh mới, chỉ nguồn skill/reference và hai
script generator/validator trong thư mục riêng. Không cung cấp deck QUANTA,
plan cũ, chẩn đoán lỗi số hoặc yêu cầu tạo đáp án mong đợi. Phạm vi được giao
chỉ là lập kế hoạch; parent chịu trách nhiệm export, render và đánh giá. Bản
reference mà agent đọc có ghi phép đo binding như bằng chứng của skill; vì vậy
không gọi bài này là thí nghiệm mù hoàn toàn. Prompt và input hash nằm trong
`transfer/CONTEXT.md` và `transfer/input-manifest.json`.

Agent tự chọn bốn lớp, tiếng Việt, source metadata và bản địa hóa eyebrow.
Không có can thiệp trong lúc agent làm. Plan hợp lệ, 38 native objects/slide,
16 child × 3 cảnh, 0 lệch. Parent xuất v1 và quan sát cùng lỗi số xuống dòng.
Sau đó parent chỉ áp dụng width 60 px cho số, giữ thay đổi eyebrow của agent;
v2 không còn lỗi. **V2 là sửa theo lỗi đã biết, không phải holdout thứ hai**.
`transfer/NOTES.md` giữ bản ghi nguyên của agent. Đây là transfer của bước lập
kế hoạch và quy tắc sửa, chưa là benchmark tự hành end-to-end.

## Tệp cuối và kiểm chứng

| Deck trong `output/` | Đối tượng / slide | Textbox / slide | Mục đích |
|---|---:|---:|---|
| T003_layer_ablation.pptx | 46 | 25 | Fixture tách rời chi tiết; giữ lỗi số v1 |
| T003_layer_candidate.pptx | 46 | 25 | Binding đúng; số v1 vẫn lỗi |
| T003_layer_candidate_v2.pptx | 46 | 25 | Bản QUANTA nên dùng |
| T003_transfer_v1.pptx | 38 | 21 | Đề mới do agent lập kế hoạch; số v1 lỗi |
| T003_transfer_v2.pptx | 38 | 21 | Bài học trực tuyến sau sửa |

Đã xem riêng **15/15 ảnh 1280×720** render từ năm PPTX cuối bằng artifact-tool
2.8.77, font Bitstream Charter. Mỗi deck có 3 slide, không picture, hai Morph
byObject 1100 ms, tên và geometry/text/type khớp plan. Hash từng file nằm trong
`evidence/study-comparison.json`. Không có kiểm tra toàn bộ schema OOXML,
PowerPoint repair warning, font substitution ở máy khác, native playback hay
thao tác sửa thật trong PowerPoint. Native motion/editing vẫn null.

Điểm chủ quan giữ rubric ban đầu: QUANTA v1 → v2: đáp ứng đề 3→4, dễ đọc 3→4,
sáng tạo tĩnh 3→3. Bài transfer cũng 3→4, 3→4, 3→3. Bố cục giải thích rõ hơn
nhưng vẫn là các lớp phẳng lặp lại; không chấm là đặc biệt ấn tượng. Không có
điểm tổng hoặc suy luận các điểm này thành chất lượng chuyển động.

## Tái lập

Từ gốc repo, chạy `python3 -m unittest discover -s tests -v`, sau đó
`python3 experiments/T003-20261004-codex-layer01/verify_study.py`.
Script kiểm tra cả 5 plan, package, binding, geometry đóng cảnh, rail và chỉ
những khác biệt được phép. `evidence/commands.md` ghi lệnh dựng/render.
Chọn tên output/build mới khi dựng lại; không ghi đè chứng cứ đã đóng băng.

## Review và bước tiếp

Parent đã review diff, chạy 34 tests, parity trên 5 deck và xem 15 ảnh cuối.
Đây là self-review; agent lập kế hoạch không phải reviewer độc lập của PR.
Giữ thay đổi vì lỗi wrap được sửa trên cả hai chủ đề và binding có phép đo;
không đổi backend hoặc hạ rubric. Nguồn skill v0.5 bổ sung recipe/ràng buộc và
cảnh báo kiểm tra số ngắn, vẫn là nguồn nghiên cứu trong repo.

Tiếp: T001 phát exact-hash candidate_v2 và transfer_v2 trong PowerPoint; ghi
repair warning, duration thực tế, child attachment và font. T003 còn cần xem
choreography thật của một nguồn có thể truy cập hợp lệ, rồi thiết kế biến thể
có ý đồ mạnh hơn; không lặp lại v1/v2 nếu không có giả thuyết mới. T002 về
carrier crossing H003/E004 và T004 portability vẫn chưa nhận ở task này.
