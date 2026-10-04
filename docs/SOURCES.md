# Nguồn kỹ thuật

Tra cứu ngày 2026-10-03. Các kết luận về hiệu quả của kiến trúc trong repo là giả thuyết nghiên cứu, chưa phải kết quả thực nghiệm.

| Nguồn chính thức | Dùng cho |
|---|---|
| [Microsoft: Morph tips](https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks) | Quy ước `!!`, ghép đối tượng 1:1, chuyển vị trí/kích thước/góc; biểu đồ dùng cross-fade |
| [Microsoft: Morph XML](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/68d26d78-f7f5-47ab-835d-4e6c82ff39f0) | Namespace Morph `http://schemas.microsoft.com/office/powerpoint/2015/09/main`; cần đọc quy tắc tích hợp trước khi chèn XML |
| [Microsoft: Sequence.AddEffect](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.sequence.addeffect) | API thêm hiệu ứng animation vào sequence |
| [Microsoft: Presentation.CreateVideo](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.presentation.createvideo) | API xuất video với timing, độ phân giải và fps |
| [PptxGenJS: Unimplemented Features](https://github.com/gitbrent/PptxGenJS/wiki/Unimplemented-Features) | Wiki dự án liệt kê animations chưa triển khai; trang cũ, cần kiểm tra bản phần mềm cụ thể trước khi chọn |

Tài liệu đầu vào đã tham khảo: `QCC_SLIDE_ENGINE_v0.1.md` và ghi chú triển khai QCC cùng ngày. Chúng gợi ý câu chuyện 4 trạng thái và đối tượng tồn tại xuyên cảnh. Ghi chú cũ chỉ nêu render LibreOffice và chèn Morph bằng XML; không đủ để khẳng định chuyển động đã được kiểm chứng trong PowerPoint.

Không có căn cứ để gọi cách tiếp cận này là phát minh đầu tiên. Đóng góp dự kiến là quy trình có thể kiểm tra và thư viện công thức chuyển động thích ứng với nội dung.


## Bổ sung cho E001 v0.2

- [Microsoft Slide Transition Extensions](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/22ebe6b5-2ade-43d9-977a-98fa194725c2): Morph nằm trong transition mở rộng qua AlternateContent.
- [Microsoft Slide Transitions example](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/99b95b35-568a-4652-9cba-df3d1175952f): p14:dur sử dụng mili giây.
- [PowerPoint School](https://powerpointschool.com/free-animated-powerpoint-presentation-template/): nguồn hiệu ứng tham khảo E001. Đã kiểm kê PPTX cục bộ và xem cấu trúc Morph; chưa kiểm tra playback. Không phân phối lại template, video hoặc tài nguyên gốc.

Đối chiếu ngày 03/10/2026 UTC (04/10/2026 giờ Việt Nam). Những phép thử package không chứng minh file sẽ phát chính xác trên mọi PowerPoint.

## Bổ sung cho E002 v0.3

[Microsoft NonVisualShapeDrawingProperties — Presentation](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.nonvisualshapedrawingproperties?view=openxml-3.0.1), đọc 04/10/2026: thuộc tính txBox phân biệt textbox được khai báo với shape chứa chữ. E002 vận dụng ý nghĩa thuộc tính để sửa biểu diễn; không sao chép template, hình hoặc mã nguồn bên ngoài. Tài liệu thuộc Microsoft; không coi việc truy cập công khai là quyền phân phối mọi tài nguyên của trang.

## T003 — layer separation

Nguồn Microsoft Morph tips và Presentation Process layer diagram/terms đã đọc ngày 2026-10-04 UTC. [Ledger chi tiết](../experiments/T003-20261004-codex-layer01/SOURCES.md) phân biệt quan sát văn bản với video chưa xem, và ghi rõ không tái phân phối tài sản. Demo dùng hình 2D tự dựng, không tái hiện extrusion 3D.
