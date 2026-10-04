# E002 — Sửa biểu diễn textbox

Ngày 04/10/2026. Kết quả: giữ bản sửa có phạm vi hẹp trong bộ dựng; nguồn skill
nghiên cứu v0.3. Chưa cài skill vào tài khoản và chưa xác minh PowerPoint.

## Phát hiện và cách sửa

H001 có chữ native nhưng thiếu `p:cNvSpPr/@txBox` cho 14 textbox trong kế hoạch.
Tài liệu Microsoft phân biệt textbox được khai báo với shape có chứa chữ.
Bản sửa đối chiếu tên và thứ tự slide theo kế hoạch, chỉ thêm `txBox="1"` cho
đối tượng `kind=text`, yêu cầu sẵn text body và hình học rect. Không tự đổi mọi
shape có chữ thành textbox. Đường dựng mới chạy bước này trước chèn Morph.

Nguồn sơ cấp: Microsoft, *NonVisualShapeDrawingProperties (Presentation)*,
đọc 04/10/2026:
https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.nonvisualshapedrawingproperties?view=openxml-3.0.1
Chỉ vận dụng thông tin kỹ thuật; không sao chép tài nguyên hình ảnh, template
hoặc mã nguồn bên ngoài. Trang thuộc tài liệu Microsoft, không mặc định tài
nguyên bên ngoài được phép phân phối lại.

## Bằng chứng cải thiện

- Đầu vào là đúng file H001 đã chốt; không dựng lại nội dung hoặc đổi tiêu chí.
- Bộ kiểm tra H001 được giữ nguyên. Adapter chỉ đổi đường dẫn PPTX cần kiểm tra.
  14 lỗi loại đối tượng ở baseline thành 0 lỗi ở candidate. Không đổi rubric.
- 14/14 textbox có khai báo đúng; mỗi slide giữ 5 rectangle và 7 textbox.
- Chỉ hai slide XML thay đổi. Sau khi bỏ 14 thuộc tính vừa thêm, cây XML của
  slide bằng baseline theo canonical XML. Mọi phần khác trong ZIP giống byte.
  Nội dung, vị trí, màu, tên, notes, quan hệ và khai báo Morph được giữ nguyên.
- Hai slide cuối được render bằng Artifact Tool ở 1280×720 và xem riêng từng
  ảnh. So với ảnh H001 cùng đường render: 0/921.600 pixel khác trên mỗi slide.
- Finalizer: package, geometry, font policy và import đều đạt, không có findings.
- Thêm 6 kiểm thử cho phạm vi sửa, shape có chữ, lỗi slide cuối, sai định danh,
  chạy lại và bảo vệ file đích. Tổng cộng 25 unit tests đều đạt.

Đây là bằng chứng sửa biểu diễn và bảo toàn đầu ra, không phải điểm độ đẹp hay
chất lượng chuyển động. Không cộng điểm thẩm mỹ vì các ảnh không đổi. Điểm
playback và chỉnh sửa thực tế trong PowerPoint vẫn null; không có điểm tổng.

## Đầu ra và giới hạn

`output/PPTX_Motion_Lab_E002.pptx`, SHA-256:
`9edf3fe2c825f7223adefcd73f13cc576cc57936d0ae47084deb940b66049f87`.

Baseline H001 được giữ nguyên với hash
`3d59b50afbc2c084e560e0b5d04d990b4f6890a66afca86dc6b951156a436e96`.

Bản sửa hỗ trợ nhóm shape phẳng rect/ellipse/textbox của backend hiện tại.
Không phải công cụ sửa PPTX bất kỳ. Chưa kiểm tra đầy đủ OOXML schema, chưa mở
file trong PowerPoint hoặc thực hiện chỉnh sửa bằng ứng dụng đó. Phát thử
Morph thật vẫn là cổng M1 còn thiếu.

## Tái lập

Xem `commands.md`, `environment.json`, `normalization.json`,
`h001-candidate-check.json`, `comparison.json`, `unit-tests.txt`,
`finalizer-validation.json` và `final-render/`. `compare.py` tái tính phép đo,
`evaluate_h001.py` chạy nguyên tiêu chí cũ với file đầu vào mới.

Bước tiếp: H002 dùng một câu lệnh mới về ba chế độ đèn ORBIT với các vòng tròn
luân phiên lấy trọng tâm, kiểm tra đường dựng đầy đủ trên chủ đề khác.
