# 5. Ảnh, sơ đồ và biểu đồ

## Ảnh

- **Ảnh là vai chính, hoặc không dùng ảnh.** Ảnh chiếm từ 1/3 đến toàn bộ slide. Một ảnh nhỏ đặt ở
  góc cho có thì bỏ đi.
- **Cắt ảnh theo chủ thể.** Chủ thể (xe, máy, khuôn mặt) đặt gần một đường 1/3 của khung, hướng nhìn
  hoặc hướng chạy quay vào phía nội dung. Không kéo méo ảnh: cắt cho vừa khung, đừng co giãn.
- **Ảnh tạo phong cách.** Tách nền, hoặc phủ một lớp màu nhận diện lên ảnh (duotone), giúp ảnh từ
  nhiều nguồn trông như cùng một bộ. Chân dung cắt tròn tông đỏ ở bộ Triết học (T066) là một ví dụ.
- **Chữ đặt trên ảnh:** đặt vào vùng trống của ảnh, hoặc lót một dải màu hay lớp phủ tối 40–60% dưới
  chữ. Kiểm tra lại tương phản.
- **Giấy phép:** chỉ dùng ảnh của người dùng, hoặc ảnh có giấy phép mở tìm bằng
  `forge_assets.py photos`. Ghi nguồn ngắn ở cuối bộ slide hoặc dưới chân ảnh, cỡ 10–12 pt.
  Không đưa ảnh có bản quyền vào repo.

## Sơ đồ: vẽ bằng hình của PowerPoint, đặt tên từng phần

Vẽ sơ đồ bằng hình và đường nối gốc của PowerPoint, không chèn ảnh chụp sơ đồ. Như vậy người dùng sửa
được, và từng phần có thể chuyển động. **Đặt tên cho từng phần** ("Bước 3", "Nhánh Máy móc"); chuyển
động và Morph đều gọi đến các tên này.

Các sơ đồ thường gặp trong báo cáo QCC và cải tiến:

| Sơ đồ | Cách vẽ |
|---|---|
| **Thanh các bước QCC** | Một hàng các ô bằng nhau, mỗi ô ghi số và tên bước bằng chữ thật (không chỉ số). Bước đang nói dùng màu nhấn, các bước đã qua dùng màu đậm, các bước chưa tới dùng màu nhạt. Đặt ở đầu slide mục, hoặc thu nhỏ thành một dải ở đầu mỗi slide nội dung. Số bước theo quy định của công ty (thường 7–10). |
| **Xương cá (Ishikawa)** | Đầu cá bên phải ghi vấn đề. Xương sống là một đường ngang. Có 4–6 nhánh chéo, mỗi nhánh một nhóm nguyên nhân (Người, Máy, Phương pháp, Vật liệu, Đo lường, Môi trường), các nguyên nhân con là chữ nhỏ nằm dọc nhánh. Nguyên nhân gốc đã xác nhận dùng màu nhấn. |
| **Cây lỗi (FTA)** | Sự cố ở đỉnh, các nguyên nhân tỏa xuống dưới, cổng VÀ/HOẶC đặt ở chỗ rẽ nhánh. Các nhánh cùng cấp nằm trên cùng một hàng. Nhánh đã loại trừ làm nhạt, nhánh gốc rễ dùng màu nhấn. |
| **Gantt** | Hàng là công việc, cột là tuần hoặc tháng. Thanh kế hoạch nhạt, thanh thực tế đậm nằm chồng lên hoặc ngay dưới. Một đường dọc đánh dấu "hôm nay". |
| **Trước / sau** | Hai nửa **cùng khung, cùng thang đo, cùng thứ tự**. Chỉ phần thay đổi có màu. Nếu dùng Morph thì đặt trên hai slide liên tiếp, cùng vật thể (xem mục 7). |
| **PDCA** | Bốn ô hoặc bốn cung tròn đều nhau, theo chiều kim đồng hồ: Plan, Do, Check, Act. Pha đang nói dùng màu nhấn. |

Gặp loại sơ đồ chưa có trong bảng: tìm cách các nhà thiết kế thường vẽ nó, giữ đúng các nguyên tắc
của mục 3, rồi ghi cách vẽ vào bảng này ở lần sửa skill sau.

## Biểu đồ

- **Một biểu đồ, một thông điệp.** Tiêu đề nói kết luận ("Bước 3 loại gần hết rò khí"), không chỉ ghi
  tên dữ liệu.
- Biểu đồ cột phải **bắt đầu từ 0**. Dữ liệu không bắt đầu từ 0 thì dùng biểu đồ điểm hoặc đường.
- **Ghi nhãn trực tiếp** cạnh cột hoặc đầu đường. Bỏ chú giải nếu được. Lưới mờ hoặc bỏ hẳn.
- Tô màu nhấn cho đúng cột hoặc đường đang nói tới; phần còn lại để xám.
- Dùng biểu đồ gốc của PowerPoint (python-pptx `add_chart`), để người dùng sửa được số.
- Giá trị 0 vẫn là dữ liệu hợp lệ, phải hiện đúng. Đừng bỏ đi, đừng thay bằng chữ.
