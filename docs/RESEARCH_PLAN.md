# Đề cương nghiên cứu

## Mục tiêu

Người dùng mô tả thông điệp, số cảnh hoặc thời lượng mong muốn bằng tiếng Việt. AI tự chọn cấu trúc kể chuyện, lập kế hoạch chuyển động, gọi bộ thực thi và báo cáo kiểm chứng. Mục tiêu sản phẩm là PPTX có thể chỉnh sửa, phù hợp thuyết trình trực tiếp.

Phạm vi ban đầu: slide 16:9, đối tượng 2D, Morph giữa các slide, hiệu ứng trình tự trong slide khi có bộ thực thi phù hợp. Windows với PowerPoint desktop là nền tảng kiểm chứng đầu tiên được đề xuất; phiên bản thực tế phải được ghi nhận trước thí nghiệm. Các nền tảng khác được kiểm tra riêng.

## Giả thuyết cần thử

| ID | Giả thuyết | Cách kiểm tra | Kết quả hiện tại |
|---|---|---|---|
| H1 | Kế hoạch trạng thái + danh tính đối tượng giảm lỗi liên tục chuyển động | So sánh với prompt tự do trên cùng bộ đề | Chưa đo |
| H2 | Công thức nhỏ phối hợp được tạo ra nhiều bố cục khác nhau | Dùng cùng công thức cho QCC, mục lục, giới thiệu sản phẩm | Chưa đo |
| H3 | Kiểm tra cấu trúc trước trình chiếu giảm số vòng sửa | Ghi lỗi phát hiện trước/sau mở PowerPoint | Chưa đo |
| H4 | Skill đọc tài liệu theo nhu cầu giảm ngữ cảnh phải nạp | So sánh lượng token nếu hệ thống cung cấp và tỷ lệ hoàn thành | Chưa đo |
| H5 | Chuyển động giải thích quan hệ dữ liệu tốt hơn trang trí thuần túy | Người xem nêu được thông điệp sau một lần xem, chấm ẩn danh | Chưa đo |

## Thí nghiệm

### E01 — Chứng minh đường tạo Morph

- Đầu vào: hai trạng thái của một hình, khác vị trí và kích thước.
- Tạo bản chuẩn bằng PowerPoint và giữ file gốc.
- Khảo sát namespace, transition, quan hệ, tên shape và đối tượng trong bản chuẩn.
- Chọn cách tái tạo bằng bộ thực thi; không tự đoán đoạn XML từ một ví dụ chưa kiểm chứng.
- Mở lại trong PowerPoint, chạy Slide Show, xuất video nếu có.
- Đạt khi không có cảnh báo sửa file, đối tượng chuyển động liên tục, tên đối tượng xác định được và có bằng chứng môi trường.

### E02 — Từ mẫu đến toàn lô

- Đầu vào: ví dụ QCC 4 trạng thái trong repo.
- 200 mẫu và 10.000 sản phẩm là số minh họa của bài thử, không phải đo lường mới.
- Khối dữ liệu lớn có thể dùng nhiều mức chi tiết. Không mặc định sinh 10.000 shape độc lập.
- Ghi rõ một dấu biểu diễn bao nhiêu đơn vị; không làm người xem tưởng số dấu bằng số sản phẩm thật.
- Đạt khi người xem theo dõi được vùng mẫu xuyên suốt, thấy khác biệt về phạm vi phân tích, dữ liệu cuối vẫn đọc được.

### E03 — Vòng tròn và chuyển bố cục

- Dựa trên quan sát video: cụm trung tâm, vòng tròn đồng tâm, tiêu đề, mục lục dạng tỏa tròn.
- Tạo hình học và bố cục riêng, chỉ tham khảo nguyên lý chuyển động.
- Đo tỷ lệ ghép sai đối tượng, số lần fade ngoài kế hoạch, độ rõ ràng của nội dung sau chuyển cảnh.
- Kiểm tra các góc quay bằng trạng thái trung gian nếu đường quay không như ý.

### E04 — Khả năng khái quát

- Sáu đề, mỗi đề chạy ba lần cho mỗi phương pháp: tổng 18 lượt mỗi phương pháp.
- Nhóm A: prompt tự do. Nhóm B: skill + kế hoạch + bộ kiểm tra.
- Giữ cùng mô hình, công cụ, tài nguyên và ngân sách sửa; ghi cấu hình đầy đủ.
- Lưu các trường hợp thất bại. Không bỏ lượt xấu hoặc chỉ giới thiệu demo đẹp nhất.
- Chấm riêng: đúng nội dung, khả năng chỉnh sửa, liên tục chuyển động, thẩm mỹ, chi phí và thời gian.
- Các ngưỡng dưới đây là mục tiêu đề xuất, không phải kết quả đã đạt.

## Mốc nghiệm thu

| Mốc | Sản phẩm | Điều kiện |
|---|---|---|
| M0 | Đề cương, nguồn, hợp đồng kế hoạch, checker | Ví dụ hợp lệ; các lỗi quan trọng bị phát hiện |
| M1 | E01 được tái tạo | File + video PowerPoint + báo cáo môi trường |
| M2 | Ba công thức có tham số | Mỗi công thức chạy được với hai nội dung khác nhau |
| M3 | Skill gọi toàn bộ quy trình | Đạt ít nhất 80% trong 18 lượt, không quá 2 vòng sửa/lượt |
| M4 | Bộ chia sẻ sử dụng lại | Hướng dẫn, môi trường hỗ trợ, giới hạn, tài nguyên có quyền phân phối |

M3 có cổng bắt buộc: không trình bày dữ liệu giả như dữ liệu thật, không gọi bản video nhúng là toàn bộ nội dung chỉnh sửa được, không tuyên bố kiểm thử PowerPoint nếu chưa thực hiện.

## Mở rộng sau MVP

Hiệu ứng theo nhịp, animation trong slide, tách lớp sản phẩm 2D, chuyển từ ảnh sang sơ đồ, các tổ hợp mới do AI đề xuất. Hiệu ứng vật lý phức tạp hoặc 3D có thể cần video. Nếu chọn hướng đó phải ghi rõ phần nào mất khả năng chỉnh sửa trong PPTX.

