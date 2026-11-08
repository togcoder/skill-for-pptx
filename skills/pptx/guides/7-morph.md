# 7. Morph giữa các slide

## Khi nào dùng

Morph làm cho **cùng một vật** trên hai slide liên tiếp trượt, đổi cỡ hoặc đổi màu từ trạng thái này
sang trạng thái kia. Nó kể được rằng "đây vẫn là thứ ấy, nhưng đã khác đi".

**Không có vật nào đi tiếp từ slide trước sang slide sau thì không dùng Morph.** Hãy dùng Fade,
hoặc không dùng hiệu ứng chuyển slide nào.

Mặc định cho một bộ slide:

| Chỗ | Chuyển slide |
|---|---|
| Bìa → slide đầu tiên, nếu tiêu đề hoặc ảnh bìa đi tiếp (thu nhỏ thành đầu trang) | Morph |
| Vào slide mục, hoặc từ slide mục vào nội dung, nếu thanh các bước hay mục lục đi tiếp | Morph |
| Slide kết, nếu nó gom lại các vật đã xuất hiện | Morph |
| Những cặp slide kể "trước → sau", "phóng to", "mở thẻ" (xem dưới) | Morph |
| Mọi chỗ khác | none hoặc Fade |

Một bộ 15 slide thường chỉ có 2–5 Morph. Morph ở mọi slide sẽ khiến bộ slide trông loạn và mất hết
ý nghĩa.

## Những nước Morph đáng làm

| Nước | Slide A → slide B |
|---|---|
| **Tiêu đề lên đầu trang** | Tiêu đề lớn giữa bìa → nhỏ lại ở vị trí tiêu đề của slide nội dung. |
| **Thanh bước đi tiếp** | Thanh các bước QCC: bước 4 sáng → bước 5 sáng. Cùng các ô, chỉ đổi màu. |
| **Phóng vào chi tiết** | Sơ đồ đầy đủ → slide B là bản sao, phần cần xem được phóng to lấp khung, các phần khác tràn ra ngoài hoặc mờ đi. |
| **Mở thẻ** | Một thẻ nhỏ trong hàng → cùng thẻ đó to ra thành cả trang chi tiết; các thẻ khác lùi xa hoặc mờ đi. |
| **Trước → sau** | Cùng khung, cùng vị trí; chỉ thanh hay số thay đổi kích thước hoặc màu. |
| **Số tăng** | Thanh ngắn → thanh dài; cùng một hình chữ nhật, đổi chiều rộng. |
| **Dòng thời gian trượt** | Trục và các mốc dịch sang trái; mốc đang nói nằm giữa và có màu nhấn. |

## Luật kỹ thuật (đã đo trong PowerPoint: T074, T059, T064)

1. **Cùng loại hình.** Chữ nhật sang chữ nhật, ảnh sang ảnh, nhóm sang nhóm. Chữ nhật sang hình elip
   thì không Morph được, kể cả khi đặt tên giống nhau: hai hình sẽ mờ chồng lên nhau. Muốn đổi dáng,
   đổi kích thước và độ bo góc của *cùng một* hình.
2. **Đặt tên giống nhau, bắt đầu bằng `!!`** ở cả hai slide (`!!buoc-5`, `!!tieu-de`), để PowerPoint
   ghép đúng cặp khi có nhiều hình giống nhau.
3. **Vật mang Morph không có hiệu ứng xuất hiện** ở slide B. Có hiệu ứng thì Morph bị chặn
   (`pptx_tools` sẽ báo lỗi).
4. **Vật nằm ngoài khung không tự bay vào.** Muốn một vật bay vào ở slide B, đặt sẵn bản sao của nó
   sát ngoài mép slide A.
5. **Trang trí lặp lại ở mọi slide không mang tên `!!`.** Hình tròn ở góc, thanh tiến độ, logo: đặt
   tên `!!` cho chúng sẽ khiến công cụ tưởng có vật đi tiếp và gắn Morph khắp nơi. Đây chính là
   nguyên nhân của bộ slide "chuyển động loạn" trước đây.
6. **Chữ dài trong thẻ dễ méo khi Morph.** Để chữ ngắn, hoặc tách chữ ra khỏi thẻ: thẻ Morph, chữ
   hiện sau.
7. **Mỗi Morph cộng thêm khoảng 1,4 giây** vào thời gian trình chiếu.
8. **Lớp trên che lớp dưới.** Thứ tự lớp ở slide B quyết định cái gì nằm trên trong lúc chuyển.
9. **Chữ mang Morph phải ngắt dòng y hệt ở hai slide.** Khác số dòng thì PowerPoint chồng hai bản
   chữ lên nhau giữa lúc chuyển — thấy "bóng ma" trên khung hình. Muốn thu nhỏ chữ vào một cột thì
   ngắt dòng sẵn ở cả hai slide, chỉ đổi cỡ và vị trí.

## Kiểm tra

```
python scripts/morph_studio.py audit OUT.pptx
```

Lệnh này báo các lỗi: khác loại hình, vật mang Morph có hiệu ứng xuất hiện, vật đích nằm ngoài khung.
Mục cảnh báo "UNNAMED-PAIR" nghĩa là có hai hình cùng loại không đặt tên, PowerPoint có thể ghép nhầm:
đặt tên `!!` hoặc đổi chỗ chúng. Riêng **tiêu đề, eyebrow, khung đặt cùng một chỗ** ở hai slide
(guide 3 bắt vậy) cũng bị báo `UNNAMED-PAIR` — đó là bình thường: PowerPoint ghép và chuyển mờ,
không phải lỗi cần đổi bố cục.
