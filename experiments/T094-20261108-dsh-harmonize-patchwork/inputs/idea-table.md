# Bảng ý — trước khi sửa (bước 1, mục 10)

Bộ gốc: `experiments/T093-20261108-claude-harmonize-deck/artifacts/qcc-chap-va.pptx` (10 slide,
13.33 × 7.50 in, dữ liệu giả lập). Bảng này lập từ tiêu đề, nội dung, biểu đồ, bảng và speaker notes
của chính bộ gốc — chưa mở bản `qcc-dong-bo*`, `harmonize.py`, `plan.json` hay REPORT của T093.

| Slide | Muốn người nghe nhớ gì (1 câu) | Bằng chứng (số, ảnh) | Nhóm |
|---|---|---|---|
| 1 Bìa | Đề tài giảm tỉ lệ lỗi hàn dây chuyền B, nhóm QCC Ánh Dương 2026 | — | Sửa vỏ |
| 2 Lý do | Lỗi hàn 4,1% gấp đôi mục tiêu 2%, tốn chi phí/giao hàng và khách đã phản hồi 2 lần → chọn đề tài đưa xuống dưới 2% trong 3 tháng | đoạn văn 111 chữ (4,1%, 2%, 2 lần, 3 tháng) | Làm lại (đoạn văn dài) |
| 3 Hiện trạng | Cả 6 tháng đều trên mục tiêu 2%, trung bình 4,1% | biểu đồ cột 3D 6 tháng + mục tiêu; notes 3,8–4,1 | Sửa vỏ (biểu đồ 3D) |
| 4 Xương cá | 4 nhóm nguyên nhân (Con người, Máy móc, Phương pháp, Vật liệu), 8 nguyên nhân; lỗi hàn 4,1% là kết quả | 20 hình, chữ 24–26 pt, 6 hiệu ứng, tràn 0,75 in | Sửa vỏ (thu gọn) |
| 5 Nguyên nhân | Que hàn ẩm là nguyên nhân lớn nhất (38%), sau đó đầu hàn mòn 24%, thợ mới 16%, bề mặt phôi 12%, khác 10% | biểu đồ tròn 3D 5 miếng | Làm lại (tròn 3D cho “cái nào lớn nhất”) |
| 6 Theo dõi | Qua 6 tuần tỉ lệ lỗi giảm 3,8% → 1,2%, tuần 6 đạt mục tiêu | bảng 7×8: sản lượng 5.000/tuần, mối lỗi 190…60, tỉ lệ 3,8…1,2 | Làm lại (bảng nhiều cột cho một xu hướng) |
| 7 Các bước | 5 bước cải tiến đã làm | gạch đầu dòng 5 bước | Làm lại (danh sách bước = quy trình) |
| 8 Ảnh | Mối hàn trước rỗ khí/bắn tóe; sau cải tiến đều | 2 ảnh vẽ (1.200×900), trước bị kéo ngang 50%, sau bị kéo dọc 34% | Sửa vỏ (ảnh méo) |
| 9 Kết quả | 4,1% → 1,2%, đạt mục tiêu dưới 2% | hai con số + câu “đạt mục tiêu” | Làm lại (bỏ trang trí, “!!!”) |
| 10 Cảm ơn | Kết thúc, cảm ơn | — | Sửa vỏ |
| 11 Phụ lục | (mới) bảng đủ 6 tuần để tra cứu | bảng gốc của slide 6 | mới |

## Hệ thống sẽ dùng (bước 4)

- 1 họ font: **Century Gothic** (font của dự án QCC; bộ gốc dùng 5 font), ghi vào theme.
- 5 cỡ: 54 / 44 / 32 / 20 / 18 pt (số lớn / tiêu đề bìa / tiêu đề / nội dung / nhãn).
- Nền trắng cho slide nội dung; bìa và slide cảm ơn cùng một nền **1F4E79** (xanh đậm, màu đang
  chiếm nhiều nhất trong bộ gốc: nền bìa + cột biểu đồ), chữ trắng.
- Chữ **262626**; nhấn **C00000** (đỏ dùng cho “mục tiêu” trong bộ gốc); xám **A6A6A6** cho mục tiêu
  và đường lưới. Không bóng, không phát sáng, không clip-art.
- Tiêu đề mọi slide nội dung cùng chỗ (0,6 in; 0,35 in), 32 pt, đậm, màu chính, canh trái.
- Chuyển slide: Fade, bìa không có; không Morph (không có vật nào thật sự đi tiếp).

## Câu hỏi "?" cho chủ dự án (ghi riêng, không tự sửa)

1. Chỉ slide 2 có số thứ tự trong tiêu đề (“1. Lý do chọn đề tài”). Giữ số hay bỏ ở mọi slide?
2. Hai dòng thông điệp mới dưới tiêu đề slide 3 và 5 lấy đúng số đã có trên slide — giữ không?
3. Tiêu đề phụ lục do tôi đặt: “Phụ lục: kết quả theo dõi sau cải tiến”.
4. Bảng phụ lục 8 cột ở 13,33 in: có cần giữ đúng 18 pt (sẽ phải xuống dòng nhiều) hay 16 pt?
