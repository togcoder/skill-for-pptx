# E004 — Đường đi cho nhãn tiếng Việt dài

Ngày 04/10/2026. Đã giữ bản sửa vì có cải thiện trong mô hình hình học cố định.
Chưa có bằng chứng playback PowerPoint.

## Bài thử và tiêu chí

H003 áp dụng công thức cyclic focus cho một đề mới: sơ đồ ba khối của đề xuất
thành phố đáng sống, với đầy đủ tên Không gian cộng đồng, Giao thông bền vững,
Hạ tầng thích ứng. Mỗi nhãn chia hai dòng trong khung 360×96 px, font 36 px.
Đây là bài thử chuyển giao do cùng người nghiên cứu thực hiện, không phải
holdout độc lập hay đánh giá mù. H003/rubric.json được lưu trước khi đo đường
đi hoặc dựng deck; không thay đổi tiêu chí sau khi xem đầu ra.

Mỗi deck có 3 slide, 8 đối tượng native/slide (3 khối và 5 textbox), hai khai
báo Morph byObject 1.100 ms. Tư thế đầu đã hiển thị, nên không có đoạn phóng
lớn riêng cho khối đầu. Cùng rubric giữ các điểm native chưa quan sát là null.

## So sánh giữ nguyên đầu vào

E004 giữ nguyên brief, đối tượng, nội dung, font, màu, kích thước, thứ tự focus
và thời lượng. Chỉ đổi tọa độ y của khối và nhãn. H003 dùng tâm focus (640,320)
và hai bên (220,520)/(1060,520). E004 dùng (640,260), (220,560)/(1060,560).

| Phép đo | H003 | E004 |
|---|---:|---:|
| Khoảng cách dọc hai tầng | 200 px | 300 px |
| Cặp nhãn có khoảng chồng trong mô hình, trên 6 cặp/chuyển cảnh | 4 | 0 |
| Cặp khối có khoảng chồng trong mô hình, trên 6 cặp/chuyển cảnh | 6 | 6 |
| Đối tượng native / textbox mỗi slide | 8 / 5 | 8 / 5 |
| Lỗi checker đối chiếu file cuối với kế hoạch | 0 | 0 |
| Finalizer / render và xem toàn bộ ảnh cuối | Đạt | Đạt |
| Playback PowerPoint | Chưa kiểm tra | Chưa kiểm tra |

Chẩn đoán dùng nguyên script E003/path_diagnostic.py với giả định tất cả khung
cùng nội suy tuyến tính, không quay. Ở H003 các khoảng chồng nhãn là khoảng
38,10%–48,00% và 52,00%–61,90% tiến trình tùy cặp. Đây không phải thời gian đo
trong PowerPoint. E004 chỉ giải quyết nguy cơ nhãn chồng nhau trong mô hình.
Khối nền vẫn giao nhau trên đường đi; cần kiểm tra tác động thị giác khi phát.

## Quy tắc tái sử dụng

Với ba nhãn cùng kích thước cố định w×h, ba vị trí đối xứng (-d,H), (0,0),
(d,H) và chuyển động chu kỳ đồng thời tuyến tính, khi 0<w<=d thì điều kiện
không chồng diện tích là H >= 3*d*h/(2*d-w). Nhãn 360×96 với d=420 cần ít nhất
252 px theo mô hình này. Chọn 300 px tạo thêm khoảng trống 48 px theo chiều dọc.
Script scripts/cyclic_label_clearance.py tính ngưỡng và báo rõ giả định, không
đánh giá chuyển động native. Bốn test mới kiểm tra trường hợp nhãn ngắn/dài,
hai phía ngưỡng, nhãn rộng vượt half-span và dữ liệu không hợp lệ. Các ca hình
học đối chiếu với chẩn đoán khoảng liên tục đã đóng băng. Tổng 29 unit tests đạt.

Nguồn skill bổ sung việc tính khoảng cách theo kích thước nhãn thực tế và
kiểm tra nhãn/khối riêng. Không thay đổi backend, không thêm dependency.

## Chấm điểm

Đánh giá ảnh tĩnh chủ quan, không mù, cùng người làm theo evaluation.md:

| Tiêu chí 0–5 | H003 | E004 | Lý do |
|---|---:|---:|---|
| Đáp ứng đề | 4 | 4 | Đủ ba trạng thái và tên, chưa kiểm tra Morph native |
| Dễ đọc tĩnh | 5 | 5 | Đủ dấu tiếng Việt, hai dòng rõ, không cắt hoặc chồng ngoài chủ đích |
| Sáng tạo bố cục tĩnh | 2 | 2 | Sơ đồ khối đơn giản phục vụ thử nghiệm, chưa đạt mục tiêu trình diễn ấn tượng |
| Chất lượng chuyển động native | null | null | Không có PowerPoint playback |
| Chỉnh sửa trong ứng dụng | null | null | Chưa thao tác trong PowerPoint |

Không có điểm tổng. Không tăng điểm thẩm mỹ chỉ vì giảm số chồng nhãn trong
phép đo. Đã xem riêng cả sáu ảnh cuối 1280×720. Cấu trúc font là Bitstream
Charter, không nhúng font. Cần kiểm tra thay thế font trên máy đích.

## Thất bại và khả năng tái lập

Hai lỗi soạn plan đã bị validator chặn: from_state/to_state thay cho from/to,
và sau đó thiếu track. Log/plan của lần dựng bị chặn được giữ trong
H003/failed-preflight và E004/failed-preflight. Sửa hợp đồng track cho cả hai
bản, không đổi hình học hoặc rubric. Đây là lỗi thực thi của người làm,
không phải kết quả chuyển động hay lỗi được phép bỏ qua.

Đọc commands.md, package-comparison.json, unit-tests.txt, clearance.json,
path-diagnostic.json, carrier-paths.json, evidence/ và final-render/.
H003 tạo kế hoạch mới qua create_plan.py; E004/create_plan.py chỉ đổi y.
Không dùng tài nguyên đồ họa bên ngoài. Quy tắc khoảng cách được suy ra tại
đây; không tuyên bố tính mới toàn cầu. Nguồn kỹ thuật Morph và điều kiện dùng
đã ghi trong docs/SOURCES.md; lần này không cần tìm thêm nguồn web.

## Bước tiếp theo

Ưu tiên phát thử H003/E004 trong PowerPoint, gắn video và môi trường với hash
file. Nếu chưa có môi trường, xử lý nguy cơ khối nền giao nhau mà không mất
chữ hoặc tăng slide ngoài đề, hoặc thử một công thức khác từ nguồn sơ cấp.
Không xem việc hết chồng nhãn là đã đạt cổng M1.

## Hash file cuối

- H003: `398a742c0f2ba46d6757ead2ac9668ef4dc4840ffa48011985699d1f2eb420cc`.
- E004: `96fc9825ea7e75d98812455662a9bca544b92eef56bb6e99a7a5a73ea68e6688`.
