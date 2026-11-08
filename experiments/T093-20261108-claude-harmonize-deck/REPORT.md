# T093 [pptx] Đồng bộ một bộ slide chắp vá: hướng dẫn mục 10, đồ nghề, diễn tập

Agent: Claude (Opus 5.5), trưởng nhóm. Ngày: 2026-11-08.

## Mở hai file này

- `artifacts/qcc-chap-va.pptx`: bộ **trước**. 10 slide QCC giả, chắp vá có chủ đích: 5 font, 14 cỡ
  chữ, biểu đồ cột 3D, biểu đồ tròn 3D, một đoạn văn dài, bảng 8 cột, sơ đồ xương cá tràn ra ngoài,
  hai ảnh bị kéo méo, hiệu ứng nảy/xoay/bay, 5 kiểu chuyển slide. **Mọi con số là giả lập.**
- `artifacts/qcc-dong-bo.pptx`: bộ **sau**, làm theo đúng `skills/pptx/guides/10-dong-bo-slide-co-san.md`.

Khi lật, xem:

1. Tiêu đề mọi slide nội dung đứng cùng một chỗ, cùng cỡ, cùng màu. Bìa và slide cảm ơn cùng một kiểu.
2. Slide 4 (xương cá): cả cụm thu gọn vào khung, hình dáng giữ nguyên, **vẫn hiện từng nhánh khi bấm**,
   mũi tên cam vẫn chạy dọc xương sống.
3. Slide 5: biểu đồ tròn 3D thành thanh ngang, xếp từ lớn đến nhỏ, chỉ "Que hàn ẩm" có màu.
4. Slide 6: bảng 8 cột thành một con số lớn và một đường; bảng đầy đủ nằm ở slide 11 (phụ lục).
5. Slide 8: hai ảnh trước/sau hết méo, cùng cỡ, không mất phần nào của ảnh.

Ảnh ghép: `preview/before-sheet.jpg`, `preview/after-sheet.jpg`.

## Bảng ý và phân loại (bước 1 và 3 của mục 10)

| Slide | Muốn người nghe nhớ | Nhóm | Đã làm |
|---|---|---|---|
| 1 Bìa | Đề tài và nhóm | Sửa vỏ | Bỏ bánh răng, bóng chữ, 3 hiệu ứng; nền xanh chính; tiêu đề viết thường. |
| 2 Lý do | Lỗi 4,1% gấp đôi mục tiêu, tốn chi phí, khách phản hồi → mục tiêu < 2% | Làm lại | Đoạn văn 111 chữ thành 3 ý + khung mục tiêu (hiện khi bấm). Đoạn gốc vào notes. |
| 3 Hiện trạng | Cả 6 tháng đều trên mục tiêu | Sửa vỏ | Cột 3D thành đường; mục tiêu là đường xám. Thêm dòng thông điệp từ số và notes. |
| 4 Xương cá | 4 nhóm nguyên nhân, 8 nguyên nhân | Sửa vỏ | `scale` 0,68 cả cụm 19 hình; giữ nguyên hiệu ứng từng nhánh; đổi màu; nhích nhãn khỏi nét. |
| 5 Tỉ lệ nguyên nhân | Que hàn ẩm lớn nhất, 38% | Làm lại | `rechart --kind bar --sort --accent`; thêm dòng thông điệp từ notes. |
| 6 Theo dõi | Tuần 6 còn 1,2%, từ 3,8% | Làm lại | Số lớn + đường 6 tuần dựng từ chính số trong bảng; bảng sang phụ lục. |
| 7 Các bước | 5 bước đã làm | Làm lại | Gạch đầu dòng thành 5 bước trên một trục, mỗi bước một lần bấm. |
| 8 Ảnh | Mối hàn trước rỗ, sau đều | Sửa vỏ | `unstretch --box` (ảnh bằng chứng: không cắt), hai khung cùng cỡ, "Sau" hiện khi bấm. |
| 9 Kết quả | 4,1% → 1,2%, đạt mục tiêu | Làm lại | Hai số lớn, mũi tên; bỏ ngôi sao, bóng chữ, "!!!"; số sau và câu đạt mục tiêu hiện khi bấm. |
| 10 Cảm ơn | — | Sửa vỏ | Cùng kiểu bìa; bỏ mặt cười, 2 hiệu ứng. |
| 11 Phụ lục | Số liệu đủ 6 tuần | mới | Bảng gốc, chữ 18 pt, kẻ nhạt, cột số canh phải. |

Hệ thống (bước 4): một font Segoe UI ghi vào theme (tiêu đề dùng font tiêu đề của theme); 6 cỡ chữ
(72 / 40 / 32 / 22 / 18 / 16); nền trắng; chữ 262626; màu chính 1F4E79 và màu nhấn C55A11 lấy từ
chính bộ cũ (xanh là màu dùng nhiều nhất). Chuyển slide: Fade, bìa không có. Không có Morph: không có
vật nào thật sự đi tiếp từ slide này sang slide kế (mục 7).

## Câu hỏi sẽ gửi người dùng khi bàn giao (theo mục 10)

1. Chỉ slide 2 có số thứ tự trong tiêu đề ("1. Lý do chọn đề tài"). Đánh số tất cả hay bỏ số? Tôi để nguyên.
2. Hai dòng thông điệp mới (slide 3 và 5) lấy từ số và notes của chính slide. Có giữ không?
3. Tiêu đề phụ lục do tôi đặt: "Phụ lục: kết quả theo dõi sau cải tiến".

## Bằng chứng

| Kiểm | Kết quả | Bậc |
|---|---|---|
| `inventory` trước → sau | font 5 → 1 họ (theme); cỡ chữ 14 → 6; màu chữ 11 → 6; 0 biểu đồ 3D, 0 ảnh méo, 0 vật tràn, 0 hiệu ứng trang trí | 1 |
| `numbers` gốc → mới | mọi con số của bản gốc (chữ, bảng, biểu đồ, notes) còn trong bản mới | 1 |
| `morph_studio audit` | 0 lỗi | 1 |
| PowerPoint 16 mở bản mới qua COM | 11 slide; chuyển slide 3849 (Fade) ở slide 2–11; 36 hiệu ứng, **mọi hiệu ứng trỏ đúng hình**, kể cả 18 hiệu ứng xương cá sau khi thu | 4 |
| Đường bay mũi tên sau `scale` 0,68 | `L 0.72 0` → `L 0.4896 0` | 1 |
| Ảnh `look` của PowerPoint, xem bằng mắt 3 vòng | xem các ảnh trong `preview/` | 4 |
| Chủ dự án mở và chấm | chưa | 6 |

Test mới: `tests/test_pptx_tools.py` thêm 5 test (inventory, rechart giữ mã và số, scale chữ/nét/đường
bay, unstretch hai cách, numbers). 9/9 qua.

## Vì sao phải viết code (D011)

Mục 10 là lời chỉ dẫn; năm lệnh mới chỉ làm những việc lời không làm được:

- `inventory`: đo độ méo ảnh (tỉ lệ khung so với ảnh sau khi cắt), nhận biểu đồ 3D trong XML, đếm font
  và cỡ chữ trên mọi đoạn. Mắt không đo được các thứ này chính xác.
- `rechart`: số của biểu đồ nằm trong XML của biểu đồ; dựng lại mà giữ mã vật thể để hiệu ứng không mất.
- `scale`: cỡ chữ không tự thu theo khung; chữ không ghi cỡ phải tìm cỡ kế thừa; độ dày nét, ô bảng,
  đường bay đều phải thu theo. Làm tay thì sót.
- `unstretch`: phép tính cắt ảnh.
- `numbers`: so mọi con số giữa hai file, cách duy nhất để chứng minh "không mất nội dung".

## Giới hạn đã biết

- `scale` từ chối placeholder (cỡ chữ kế thừa từ layout chưa được đọc); chép chữ sang hộp chữ trước.
- `scale` không thu chữ bên trong biểu đồ nằm trong cụm, và để nguyên đường bay khi chỉ thu một nhóm
  (đường bay đó là chuyến đi của cả nhóm trên slide).
- `rechart` chỉ dựng một kiểu (cột, thanh, đường, tròn); biểu đồ kết hợp cột + đường sẽ thành một kiểu.
- `numbers` so số, không so chữ. Câu bị rút gọn vẫn phải đọc lại bằng mắt theo bảng ý.
- Slide 4: hai nhãn nguyên nhân vẫn xuống dòng; nhãn nằm sát nét xương. Đây là bố cục của tác giả;
  sửa thêm là vẽ lại sơ đồ.
- Bộ chắp vá do chính tôi dựng nên tôi biết trước lỗi. Lần diễn tập thật là T094: model khác họ làm
  mù trên cùng file, chỉ đọc hướng dẫn.

## Quyết định R2 (từ review T090)

`pptx_tools` giữ chỉ ghi entrance. Cảnh báo `NAR-LIFECYCLE` trên deck dựng bằng nó là lời nhắc, không
phải lỗi. Lý do: bài nói thường ngày hiếm khi cần làm mờ hay cho vật biến mất; thêm dim/exit làm kế
hoạch chuyển động khó viết hơn cho model nhỏ. Guide 6 đã ghi quyết định.

## Tệp

- `inputs/build_patchwork.py`: dựng bộ chắp vá và hai ảnh vẽ bằng Pillow.
- `inputs/harmonize.py`: các bước đồng bộ, theo thứ tự của mục 10.
- `inputs/plan.json`: kế hoạch chuyển động.
- `inputs/weld-truoc.jpg`, `inputs/weld-sau.jpg`: ảnh vẽ, không phải ảnh chụp.
- `artifacts/qcc-dong-bo.static.pptx`: bản tĩnh trước khi ghi chuyển động.
