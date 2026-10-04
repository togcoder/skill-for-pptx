# E003 — Đường đi luân phiên cho ba chế độ

Ngày 04/10/2026. Giữ bản thử nghiệm đã điều chỉnh vì có cải thiện đo được trong
mô hình hình học đã khai báo. Chưa có bằng chứng chuyển động trong PowerPoint.

## Chuỗi thử nghiệm

H002 dùng câu lệnh mới về đèn bàn giả tưởng ORBIT: ba vòng Read, Relax, Create
lần lượt lấy trọng tâm, ít chữ và màu nổi bật. Agent tự tạo plan và rubric,
không đọc plan hoặc đầu ra E001/H001/E002. Hướng dẫn nguồn vẫn có tóm tắt bài
học cũ. Lượt agent được thu gọn sau giai đoạn đọc/chọn bố cục; phần dựng, kiểm
tra và render do agent thực hiện, báo cáo/lưu trữ cuối do parent hoàn thiện.
Đây không phải benchmark tự hành có đo thời gian hoặc chi phí.

H002 đạt kiểm tra cấu trúc và ảnh tĩnh: 3 slide × 11 đối tượng native, mỗi slide
có 6 textbox, 4 ellipse và 1 rectangle; 2 khai báo Morph 1.100 ms. 18 textbox
qua bước chuẩn hóa mới. Ba slide cuối được agent và parent xem riêng. H001
vẫn là baseline lỗi cũ; H002 xác nhận đường dựng đầy đủ trên chủ đề mới.

Trong H002, Read bắt đầu lớn ở slide 1; chỉ có hai chuyển cảnh. Việc đổi chỗ
hai vòng theo đường đối ứng cũng tạo nguy cơ chồng nhãn ở giữa. Agent đã ghi
giới hạn này độc lập, chưa quan sát playback.

## Phép đo cố định và bản sửa

E003 giữ nguyên nội dung, loại đối tượng, màu, font, kích thước vòng/nhãn,
số slide và thời lượng H002. Chỉ đổi vị trí hai vòng bên thành các đỉnh thấp
hơn, và đổi thứ tự di chuyển thành chu kỳ ba phần tử. Bản này được chỉnh dựa
trên H002, vì thế không gọi là một bài thử chưa từng thấy thứ hai.

`path_diagnostic.py` kiểm tra liên tục khoảng chồng diện tích của ba cặp khung
nhãn ở mỗi chuyển cảnh, với giả định các khung cùng nội suy tuyến tính và
không quay. Tiêu chí được ghi trước khi dựng E003. Bốn ca hình học đơn giản
kiểm tra các trường hợp đứng riêng, tiếp xúc cạnh, đổi chỗ và khác hàng.

| Phép đo | H002 | E003 |
|---|---:|---:|
| Cặp nhãn có khoảng chồng theo mô hình, trên 6 cặp/chuyển cảnh | 2 | 0 |
| Khoảng chồng ở mỗi cặp bị ảnh hưởng | 26,19%–73,81% tiến trình | Không có |
| Số slide / Morph khai báo | 3 / 2 | 3 / 2 |
| Textbox native mỗi slide | 6 | 6 |
| Lỗi kiểm tra cấu trúc được thực hiện | 0 | 0 |
| Playback PowerPoint | Chưa kiểm tra | Chưa kiểm tra |

Tỷ lệ tiến trình trong bảng thuộc mô hình tuyến tính, không phải thời điểm
đo trên PowerPoint. Checker E003 đối chiếu vị trí tất cả 33 đối tượng trong
file cuối với plan, chữ, loại shape, danh tính và thời lượng. Finalizer đạt
kiểm tra package, layout/font và import. Cả ba ảnh cuối 1280×720 được xem:
các nhãn rõ, không cắt chữ và không có chồng lấn tĩnh ngoài chủ đích.

## Chấm điểm và giới hạn

Đánh giá tĩnh không mù của parent, thang 0–5 theo evaluation.md:

| Tiêu chí | H002 | E003 | Giải thích |
|---|---:|---:|---|
| Đáp ứng đề | 4 | 4 | Đủ ba chế độ và hai vòng ngữ cảnh; Read mở ở tư thế lớn, không có đoạn lớn dần riêng |
| Dễ đọc tĩnh | 5 | 5 | Ba nhãn rõ ở mọi slide, không thấy cắt hoặc đè chữ |
| Sáng tạo bố cục tĩnh | 3 | 3 | Demo ring-lamp rõ ý nhưng hình học còn đơn giản; không tăng điểm chỉ vì đổi đường đi |
| Chất lượng chuyển động native | null | null | Chưa có playback thật |
| Chỉnh sửa trong ứng dụng | null | null | Chưa thử bằng PowerPoint |

Không có điểm tổng. Mô hình không kiểm tra nhịp, easing, text morph, viền vòng
đè nhau hay trải nghiệm người xem. Không dùng ảnh tĩnh hoặc kết quả mô hình
để kết luận Morph sẽ chạy mượt hay hấp dẫn. Bộ kiểm tra XML H002 từng xử lý
sai target tuyệt đối trong lần thử đầu; agent đã sửa checker, không sửa PPTX.
Chi tiết lỗi được ghi trong qa.json, không có trace lỗi ban đầu còn lưu.

## File và bước tiếp

- H002 SHA-256: `f311537bce6345a640dec81f5868deee25eb8583c372d77bbf7531ef9df57a11`.
- E003 SHA-256: `517dd23371c7768d19cb0286e4f3292cdbaebffc045a1e5884ae00fd403d6164`.
- `create_plan.py`, `plan.json`, `baseline-paths.json`, `candidate-paths.json`,
  `diagnostic-checks.json`, `verify_candidate.py`, `package-check.json`,
  `finalizer-validation.json`, `final-render/` và `commands.md` tái lập phép thử.
- Nguồn tham khảo kỹ thuật H002: Microsoft Support,
  https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks,
  đọc 04/10/2026. Không dùng tài nguyên đồ họa bên ngoài. Bố cục và chẩn đoán
  hình học là phần tự dựng, không tuyên bố tính mới so với mọi nghiên cứu khác.

Skill bổ sung quy tắc phân biệt số tư thế với số chuyển cảnh, kiểm tra nguy cơ
đổi chỗ nhãn, và công thức cyclic focus có ranh giới bằng chứng rõ ràng.
Bước tiếp có giá trị cao nhất: phát thử đúng hai file trên PowerPoint, so sánh
nhãn và viền vòng giữa cảnh. Nếu môi trường native chưa có, thử công thức này
với tên chế độ dài và số phần tử khác; giữ tiêu chí và lưu cả thất bại.
