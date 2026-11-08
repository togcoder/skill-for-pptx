# 4. Chữ và màu

## Cỡ chữ: chọn một thang và dùng lại

Cả bộ slide dùng từ 3 đến 6 cỡ chữ. Thang gợi ý cho slide 16:9:

| Vai | Cỡ |
|---|---|
| Số hoặc câu nổi bật | 72–120 pt |
| Tiêu đề | 32–44 pt, tối đa 2 dòng |
| Ý chính, chữ trong sơ đồ | 22–28 pt |
| Nội dung | 18–24 pt |
| Nhãn nhỏ (eyebrow), nguồn, chú thích | 12–14 pt, chỉ cho thông tin phụ |

- **Nội dung không bao giờ dưới 18 pt. Không có gì dưới 12 pt.** Chữ không vừa khung thì bớt chữ hoặc
  tách slide. Đừng thu nhỏ chữ.
- Đừng để công cụ tự thu chữ cho vừa hộp. Một tiêu đề ngắn bị thu xuống 14 pt là lỗi.
- Tiêu đề lớn ít nhất gấp 1,5–2,5 lần chữ nội dung. Chênh lệch quá ít thì không còn thứ bậc.
- Một dòng chữ không quá khoảng 60 ký tự. Khối chữ rộng quá thì chia cột hoặc hẹp khung lại.
- Nhãn nhỏ trên tiêu đề (eyebrow): chữ in hoa, cỡ 12–14 pt, giãn chữ, màu nhấn. Đây là cách sang
  trọng để ghi "Bước 5 · Phân tích nguyên nhân".
- Nhấn mạnh bằng độ đậm hoặc màu nhấn cho **vài từ**. Không gạch chân, không in nghiêng cả đoạn,
  không viết in hoa cả câu dài.

## Màu: một nền, một chữ, một nhấn

- **Nền:** một màu chủ đạo cho slide nội dung; bìa, mục và kết có thể dùng nền ngược lại (sáng ↔
  tối).
- **Chữ:** một màu chính, một màu phụ nhạt hơn cho chú thích. Đừng dùng đen tuyền trên trắng tuyền;
  một xám rất đậm dễ nhìn hơn.
- **Nhấn:** một màu làm **một việc**, là chỉ ra thứ quan trọng nhất. Màu nhấn chiếm diện tích nhỏ,
  khoảng một phần mười. Khi mọi thứ đều có màu nhấn thì không còn gì được nhấn.
- **Tương phản:** chữ thường cần tương phản tối thiểu 4,5:1 so với nền, chữ lớn tối thiểu 3:1.
  `design_critic.py` đo được tương phản. Chữ nhạt trên nền nhạt là lỗi hay gặp nhất.
- Màu cho số liệu: tô xám những gì không cần chú ý, chỉ tô màu nhấn đúng cột hoặc đường đang nói tới.

## Hiệu ứng trang trí: rất ít

- Nền phẳng là chuẩn. Gradient chỉ dùng có chủ ý, ví dụ cho bìa hoặc một slide câu nói.
- Một khối nổi lên dùng **hoặc** viền mảnh **hoặc** bóng mềm (mờ rộng, rất nhạt), không bao giờ cả
  hai. Không đổ bóng cho chữ, trừ khi chữ trắng đặt trên ảnh không có lớp phủ.
- Không phát sáng (glow), không phản chiếu, không chữ 3D, không clip-art.
- Biểu tượng (icon): cùng một bộ, cùng nét, cùng cỡ (0,4–0,6 in). Không dùng emoji làm biểu tượng.
- **Đồ trang trí bằng chữ** (dấu ngoặc kép, dấu chấm, số lớn) phải dùng một cỡ **trong thang** của bộ
  (ví dụ 64 pt), không thêm cỡ mới — `TYP-SIZES` đếm mọi cỡ chữ, kể cả đồ trang trí.
