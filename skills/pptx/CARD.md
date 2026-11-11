# CARD — đưa một bộ slide có sẵn vào theme (một trang cho model nhỏ)

Dùng khi chủ dự án có **bộ slide đã đủ nội dung** và **một theme**, và muốn bộ đó mang theme. Việc của bạn
là đổi vỏ + co nội dung, **không vẽ lại nội dung, không thêm chữ/số/hình, không tự viết script chấm**.
Chi tiết đầy đủ: `guides/13-dua-bo-co-san-vao-theme.md`; tự kiểm: `guides/8-tu-kiem-tra.md`.

## Thứ tự lệnh (viết cả vào một script dựng, đọc bản gốc, ghi file mới)

1. Xem vỏ cũ ở đâu: `python scripts/pptx_tools.py shell GOC.pptx` — đọc dòng "text differs per slide" để
   lấy chữ của thanh bước; ghi lại mã vỏ (m1, r1…).
2. Gỡ vỏ cũ: `python scripts/pptx_tools.py shell GOC.pptx --strip m1,m2,r1 --background F6F2EA -o 1_tran.pptx`
   (vật có hiệu ứng được giữ; chữ đã gỡ nằm trong `1_tran.shell.json`).
3. Thay tiêu đề: tiêu đề cũ thành tiêu đề theme, **giữ nguyên chữ**; slide không có tiêu đề riêng thì lấy
   tên bước từ thanh bước cũ. Không tự đặt tiêu đề mới.
4. Co nội dung (mức 1): `python scripts/pptx_tools.py fit 2_tieude.pptx --into 0.67,2.2,18.67,8.3 --slides 2-36 -o 3_vua.pptx`
   — slide tràn hình / mô phỏng để mức 0, không đưa vào `--slides`.
5. Gắn vỏ theme: nền, thanh bước, logo, tiêu đề, chân trang; tên vật của vỏ bắt đầu bằng `!!`; ảnh trang
   trí nằm **dưới** nội dung.
6. Đổi mực chữ không đọc được: `python scripts/pptx_tools.py glance 4_vo.pptx --ink 1D2433 5_xong.pptx`
   — chỉ chữ không đọc được đổi màu, kể cả chữ trong bảng/biểu đồ; chữ đỏ, xanh có nghĩa thì giữ.
7. Cặp cũ/mới: `python scripts/pptx_tools.py compare GOC.pptx 5_xong.pptx`

## Ba việc kiểm trước khi giao (thiếu một việc là chưa kiểm)

1. `python scripts/pptx_tools.py glance 5_xong.pptx` → 0 slide lỗi, **hoặc** mỗi lỗi còn lại có một dòng
   lý do (ví dụ lỗi có sẵn trong bộ gốc); mở từng ảnh `faults-NN.png` của slide còn lỗi.
2. Mỗi slide một dòng "đã thấy gì" sau khi mở `slide-NN.png` cỡ lớn; nộp mã nhìn của từng ảnh:
   `python scripts/pptx_tools.py seen <thư-mục-glance> 3=U6G 4=K7P …` (mã 3 ký tự ở dải dưới ảnh).
3. `python scripts/pptx_tools.py check GOC.pptx 5_xong.pptx --map map.json` → đạt các cổng giữ ruột:
   hiệu ứng, video, số, ảnh gốc, bảng, biểu đồ. Mất món nào phải khai `drop` + lý do, không bỏ im lặng.

## Cấm

- Không mở file kết quả ra vá; sửa trong script rồi dựng lại **từ bản gốc**.
- Không tự viết script chấm thay `glance`/`check`/`compare`; không sửa test cho qua.
- Không tự thêm câu tóm tắt, khẩu hiệu, số to, icon, ghi chú về cách làm lên slide.
- Không đọc được ảnh: **nói ngay**, chỉ làm đổi vỏ + lệnh đo, không nhận dựng lại bố cục (mức 2).
- Slide nào cần mức 2 (dựng lại bố cục): làm 2–3 slide mẫu theo `guides/14`, đưa chủ dự án duyệt trước.
