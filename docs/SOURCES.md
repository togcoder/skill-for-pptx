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

## T024 — Nghiên cứu đối sánh mã nguồn mở & kiến trúc chuyển động phức hợp (2026-10-14)

| Nguồn kỹ thuật / Dự án | URL | Ý nghĩa kỹ thuật áp dụng vào `skill-for-pptx` (T024) |
|---|---|---|
| [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) ([Animation Core](https://github.com/hugohe3/ppt-master/blob/main/skills/ppt-master/scripts/docs/pptx-animations.md), [Animations Reference](https://github.com/hugohe3/ppt-master/blob/main/skills/ppt-master/references/animations.md)) | `https://github.com/hugohe3/ppt-master` | Tham khảo kiến trúc tách `mainSeq` và `interactiveSeq` (`trigger_shape`), thuộc tính `p14:bounceEnd`, `repeatCount`, `autoRev`, `p:animClr` và semantic read-back. Không sao chép mã nguồn hay preset file. |
| [JimLiu/baoyu-design](https://github.com/jimliu/baoyu-design) ([Changelog `gen-pptx`](https://github.com/JimLiu/baoyu-design/blob/main/CHANGELOG.md)) | `https://github.com/jimliu/baoyu-design` | Tham khảo mô hình khai báo đường đi Bézier đa đoạn, `repeat` / `auto-reverse` và đo bounding-box thực tế trước khi xuất `<p:timing>`. |
| [jeertmans/manim-slides](https://github.com/jeertmans/manim-slides) ([Sharing PPTX](https://manim-slides.eertmans.be/latest/reference/sharing.html)) & [manim-pptx](https://www.manim.community/plugin/manim-pptx/) | `https://github.com/jeertmans/manim-slides` | Đối chứng hướng tiếp cận nhúng video clip theo từng nhịp click (`self.next_slide()`) làm phương án dự phòng khi vượt ngưỡng biểu diễn vector của OOXML. |
| [singerla/pptx-automizer](https://github.com/singerla/pptx-automizer) | `https://github.com/singerla/pptx-automizer` | Đối chứng kỹ thuật Template Grafting (ghép và biến đổi cây XML từ slide mẫu giữ nguyên timing). |
| [SlideForge: python-pptx animations](https://slideforge.dev/blog/python-pptx-animations) & [11 python-pptx limitations](https://slideforge.dev/blog/python-pptx-limitations-we-solved) | `https://slideforge.dev/blog/python-pptx-animations` | Đối chứng quy tắc static linter kiểm tra tràn khung và chồng lấp đối tượng (ngưỡng 15%). |
| [python-pptx Issue #942](https://github.com/scanny/python-pptx/issues/942), [Issue #1106](https://github.com/scanny/python-pptx/issues/1106), [Issue #400](https://github.com/scanny/python-pptx/issues/400) & [MartinPacker/md2pptx](https://github.com/MartinPacker/md2pptx) | `https://github.com/scanny/python-pptx/issues/942` | Phát hiện lỗi placeholder rỗng chưa điền nội dung làm vô hiệu hóa chuyển cảnh Morph (`empty_placeholders()` trong `pptx_animator.py`). |
| [Microsoft Learn: Working with animation (Open XML SDK)](https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation) & [ShapeCrawler](https://github.com/ShapeCrawler/ShapeCrawler) | `https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation` | Đặc tả chuẩn ECMA-376 / SMIL cho `<p:anim>`, `<p:cBhvr>`, `<p:tavLst>`, `<p:animClr>` và `<p:animMotion>`. |
