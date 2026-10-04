# E001: đường dựng PPTX và độ tin cậy của Morph

Ngày nghiên cứu: 04/10/2026, giờ Việt Nam. Trạng thái: đã kiểm tra cấu trúc và bố cục tĩnh. **Chưa kiểm chứng phát chuyển động trong PowerPoint.**

## Đầu vào giữ cố định

“Tạo ba cảnh PowerPoint cho một triển lãm sáng tạo: bốn hình tròn màu tụ quanh một tâm, mở ra thành bốn mô-đun, rồi xếp thành một dòng hành trình. Cảm giác liền mạch, bố cục táo bạo, tất cả vẫn chỉnh sửa được. Mỗi mô-đun mang một từ: Imagine, Make, Share, Evolve.”

Giữ nguyên kế hoạch baseline, font, canvas và rubric khi so sánh hai bộ chèn Morph. Đầu ra dùng đồ họa native mới, không chép hình hoặc tài nguyên từ template bên ngoài.

## Sản phẩm và bằng chứng

- PPTX ba slide, 13 đối tượng native mỗi slide, gồm 6 đối tượng có chữ. Không có ảnh raster hóa toàn slide.
- 13 tên ghép đối tượng duy nhất được giữ xuyên ba cảnh.
- Hai khai báo Morph trên slide đích, mỗi lần 1.200 ms. Thời lượng khai báo chưa được đo trong trình chiếu.
- Kiểm tra package, hình học, font và import bằng artifact-tool đều vượt qua các phép kiểm tra được hỗ trợ.
- Render lại file PPTX cuối bằng LibreOfficeDev, xem đủ ba slide 1280×720. Chữ đọc được, không cắt hoặc che nhãn. Hình tròn chồng nhau ở cảnh đầu là chủ ý của đề.
- Font Bitstream Charter được chọn từ font hiện có và ghi lại. File không nhúng font; máy trình chiếu khác có thể thay font.
- SHA-256: `b3b4e28c14f00bc4fe05d6a71400752819413661e1280eb92301b4a6305e7c37`.

## Lỗi đã tái hiện và sửa

| Tình huống | Bản cũ | Bản sửa |
|---|---|---|
| Thứ tự slide khác số trong tên part XML | Gắn hiệu ứng sai đích | Theo presentation relationships |
| Số trạng thái khác số slide | Có thể lỗi giữa chừng và để lại file dở | Từ chối trước khi ghi |
| Slide sau đã có timing animation | Không phát hiện | Từ chối, giữ nguyên nguồn |
| Tên `!!` khác kế hoạch | Vẫn chèn hiệu ứng | Từ chối |
| Duration là số lẻ | Âm thầm cắt phần thập phân | Từ chối |
| Chèn lại vào file đã có hiệu ứng | Có thể để lại file dở | Từ chối mà không tạo đầu ra |
| Đích đã tồn tại | Không ghi đè | Không ghi đè |

Bộ 7 tình huống này cho kết quả **1/7 → 7/7**. Đây là bộ kiểm tra nhắm vào lỗi đã biết, được lập khi đã phát hiện lỗi, không phải benchmark độc lập hoặc tỷ lệ thành công của skill. Toàn bộ 19 unit tests hiện có vượt qua.

## Điểm theo rubric đã cố định

Điểm 0–5 là nhận xét của cùng người thực hiện, không phải đánh giá mù: đáp ứng đề 4; cấu trúc chỉnh sửa 4; ghép đối tượng 4; dễ đọc tĩnh 4; bố cục sáng tạo tĩnh 3. Điểm chuyển động: **chưa chấm**. Không tính điểm tổng khi thiếu playback. Chi tiết và lý do có trong `scores.json`.

## Điều đã đưa vào nguồn skill

Kiểm tra khả năng backend trước khi dựng; dùng đơn vị đúng; đọc thứ tự slide qua quan hệ; đối chiếu số cảnh và định danh; kiểm tra toàn bộ file trước khi ghi; giữ trạng thái kiểm chứng riêng. Khôi phục nguồn skill đang còn TODO thành một quy trình nghiên cứu có đường dẫn chạy và giới hạn rõ.

Một lượt áp dụng độc lập cho chủ đề quy trình sản xuất được thực hiện dưới H001. Không đưa kết quả kỳ vọng hoặc các lỗi trên vào yêu cầu của lượt đó. Báo cáo H001 được giữ riêng. Trong quá trình này đã phát hiện ghi chú nguồn tham khảo E001 bị gắn cứng trong renderer, và đã sửa renderer để chỉ ghi URL thực sự có trong kế hoạch. Bản E001 được dựng trước sửa đổi ghi chú này; `renderer-used.mjs` lưu đúng mã đã tạo file.

## Chưa được chứng minh

Không có PowerPoint desktop trong môi trường Linux đang dùng. Chưa có cảnh báo mở/sửa file từ PowerPoint, video playback, kiểm chứng ghép đối tượng thực tế, đo nhịp hoặc thẩm mỹ chuyển động. HTML, ảnh tĩnh và XML không thay thế những bằng chứng đó. Chưa thử nhiều mô hình, chưa chạy benchmark 18 lượt và chưa chứng minh “skill hoàn toàn mới” theo nghĩa phát minh.

## Nguồn

- PowerPoint School: https://powerpointschool.com/free-animated-powerpoint-presentation-template/ — trang tác giả và một PPTX tham chiếu đã được khảo sát cục bộ. Chưa quan sát phát chuyển động, chưa xác minh quyền phân phối lại tệp mẫu; không đưa tệp đó vào bản nguồn chia sẻ.
- Microsoft Morph: https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks — cơ chế tên `!!` và ghép 1:1.
- Microsoft MS-PPTX: https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/22ebe6b5-2ade-43d9-977a-98fa194725c2 — cấu trúc mở rộng transition.
- Microsoft duration example: https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/99b95b35-568a-4652-9cba-df3d1175952f — `p14:dur` biểu diễn mili giây.

Đối chiếu nguồn ngày 03/10/2026 UTC, 04/10/2026 giờ Việt Nam. Bộ chèn XML là thử nghiệm phù hợp với các cấu trúc đã khảo sát, không phải chứng nhận tương thích PowerPoint.
