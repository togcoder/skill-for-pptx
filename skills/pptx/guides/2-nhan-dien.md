# 2. Nhận diện: màu, font, logo

## Không bắt người dùng làm "bộ nhận diện"

Phần lớn công ty đã có sẵn nhận diện trong một file slide cũ hoặc một template. Việc của bạn là
**lấy nó ra**, không phải bắt người dùng điền một bản khai.

| Người dùng có | Bạn làm |
|---|---|
| File template (`.potx`) hoặc một bộ slide cũ của công ty | **Dựng ngay trong file đó.** Mở bằng `Presentation("mau.pptx")`, thêm slide từ các layout của nó, xóa các slide cũ không dùng. Theme, font, logo trên slide master được giữ nguyên. Đây là cách giữ nhận diện tốt nhất. |
| Logo (ảnh) | Đặt logo đúng một chỗ cố định (thường là góc trên phải hoặc dưới phải, cách mép 0,4–0,5 in, cao 0,35–0,5 in) trên các slide nội dung. Không đặt trên bìa nếu bìa đã có logo lớn. |
| Vài mã màu | Màu đậm nhất làm nền hoặc màu chữ. Màu nổi nhất làm màu nhấn. Thêm 2–3 sắc xám lấy cùng tông. |
| Một tài liệu mẫu để theo (báo cáo in, brochure, PDF): "làm theo kiểu này" | Xem mục "Khi có một tài liệu mẫu để theo" bên dưới. |
| Không có gì | Chọn một phong cách theo bảng dưới. Nói cho người dùng biết bạn đã chọn gì. |

**Không có logo thì không có logo.** Đừng viết tên công ty bằng chữ rồi gọi đó là logo. Đừng tự
thêm thanh tiến độ, số trang lớn hay hình trang trí ở góc chỉ vì công cụ có sẵn.

## Khi có một tài liệu mẫu để theo

Sếp hay khách đưa một bản báo cáo in hoặc một file PDF và nói "làm theo kiểu này". Họ muốn **giọng**
của tài liệu đó: chữ, biểu đồ, bảng, cách trình bày số. Họ không muốn bạn chép lại từng trang.

1. **Đọc mẫu bằng `sample`.** Chạy `python scripts/pptx_tools.py sample mau.pdf --pages 5,11`. Lệnh
   cho biết tên thật của font và máy này có font đó không, các cỡ chữ và màu chữ hay dùng, màu của các
   khối tính theo diện tích, kèm ảnh các trang. Tên font và mã màu thì mắt không đọc ra được.
2. **Xem ảnh các trang. Ghi lại những gì lặp lại trên nhiều trang.** Thường là: tiêu đề trang; biểu đồ
   (nền, kiểu cột hay đường, nhãn số, lưới, chú giải, đơn vị); con số lớn và đơn vị đi kèm; bảng; trang
   mở chương; chân trang. Đó là giọng của mẫu. Một chi tiết chỉ có trên một trang thì không phải giọng.
   Lấy **hệ thống** của mẫu: lưới, thứ bậc, khoảng trắng, cách dựng một biểu đồ. Đừng lấy **phụ kiện**
   của bản in như dòng chữ đầu trang, chú thích hình có đánh số, chữ 8 pt. Mang phụ kiện lên slide mà
   không có hệ thống thì được một slide vừa rối vừa trống (mục 3).
3. **Hỏi lấy gì của mẫu, giữ gì của bộ đang có.** Câu "lấy biểu đồ, font chữ…, không phải toàn bộ"
   có nghĩa là chỉ lấy những thứ đó. Nền, ảnh và chuyển động của bộ đang có thì giữ lại.
4. **Font không có trên máy thì thay bằng font gần nhất có sẵn trên mọi máy, và nói cho người dùng
   biết.** Helvetica và Helvetica Neue thay bằng Arial. Font hình học (Futura, Avenir, Gotham) thay
   bằng Century Gothic. Font nhân văn (Frutiger, Myriad) thay bằng Segoe UI. Font có chân (Minion,
   Garamond) thay bằng Cambria hoặc Georgia. Slide tiếng Việt thì phải chọn trong danh sách font an
   toàn ở mục Font bên dưới.
5. **Bản in và màn chiếu khác nhau.** Báo cáo A4 dùng chữ 8–9 pt. Slide vẫn theo thang cỡ chữ ở mục
   4. Lấy **tỉ lệ** của mẫu, đừng lấy cỡ: số lớn gấp mấy lần nhãn, đơn vị nhỏ đặt cạnh số. Mẫu in càng
   dày chữ thì càng nên gom về ít cỡ chữ.
6. **Màu.** Màu chính của mẫu thường là màu công ty, nên lấy được. Màu số liệu thì theo quy ước:
   xám cho phần trước hoặc phần không cần chú ý, nhạt cho phần trung gian, màu chính cho kết quả, đỏ
   cho NG, xanh lá cho đạt.
7. **Không chép.** Không lấy ảnh, biểu tượng, câu chữ, hay nguyên bố cục một trang của mẫu. Học cách
   mẫu làm, rồi tự làm.

## Khi phải tự chọn phong cách

Chọn theo **người nghe và nội dung**, không theo sở thích:

| Tình huống | Gợi ý |
|---|---|
| Báo cáo nội bộ, QCC, kỹ thuật | Nền sáng hoặc tối trung tính, một màu nhấn (vàng, cam hoặc xanh của công ty). Ảnh thật của sản phẩm hay hiện trường. Sơ đồ rõ ràng. |
| Sếp duyệt nhanh, ra quyết định | Tối giản. Mỗi slide một con số hoặc một kết luận, nhiều khoảng trống. |
| Bài giảng, giáo dục | Nền sáng ấm (kem, trắng ngà), font có chân cho tiêu đề, ảnh minh họa giàu cảm xúc. |
| Ra mắt, truyền cảm hứng | Nền tối, ảnh lớn tràn slide, chữ lớn, rất ít chữ. |
| Gọi vốn | Trắng hoặc tối, sạch; số liệu là vai chính. |

Một phong cách tốt thường có **một ý tưởng thị giác lặp lại nhất quán**. Ví dụ ở bộ Triết học (T066):
chân dung cắt tròn tông đỏ, gạch vàng mảnh dưới tiêu đề. Một ý, lặp lại khắp bộ, là đủ. Năm ý trang
trí khác nhau thì thành rối.

## Font

- Một họ font, tối đa hai: một cho tiêu đề, một cho nội dung.
- **Tiếng Việt: font phải có đủ dấu.** Các font an toàn: Segoe UI, Arial, Calibri, Cambria, Times New
  Roman, Roboto, Noto Sans và Noto Serif, Be Vietnam Pro, Montserrat, Lora. Font lạ thì mở ra xem
  (`look`) để chắc chắn không bị lỗi dấu.
- Font không có trên máy người xem sẽ bị thay bằng font khác, làm vỡ bố cục. Chọn font phổ biến, hoặc
  nhúng font.
