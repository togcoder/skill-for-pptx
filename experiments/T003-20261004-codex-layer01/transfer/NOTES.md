# NOTES — T003 forward: kiến trúc học trực tuyến

Ngày thực hiện: 2026-10-04 UTC.

## Phạm vi và yêu cầu cố định

> Giải thích kiến trúc một nền tảng học trực tuyến qua 4 lớp bằng hiệu ứng tách lớp rồi ghép lại, nhãn tiếng Việt ngắn và dễ đọc.

Chỉ sử dụng nguồn trong `T003-forward`. Đầu ra gồm `result/config.json`, `result/plan.json` và tệp ghi chú này. Không tạo PPTX, không render PPTX, không sửa script/skill/checkpoint, không cài skill, không dùng GitHub. Không gặp báo hết quota.

## Tài liệu đã đọc

- `skills/pptx-motion/SKILL.md`
- `docs/STATUS.md`
- `skills/pptx-motion/references/recipes.md`
- `skills/pptx-motion/references/plan-contract.md`
- `skills/pptx-motion/references/layer-separation.md`
- `skills/pptx-motion/references/evaluation.md`
- `skills/pptx-motion/references/motion-paths.md`
- `scripts/layer_separation.py` và `scripts/validate_plan.py`

Không tìm hoặc đọc bài/đầu ra thử nghiệm khác. Các đường dẫn lịch sử trong tài liệu chỉ được đọc như nội dung tham chiếu, không được mở.

## Lựa chọn nội dung và thiết kế

Dữ liệu minh họa là **giả định** (`data_provenance=synthetic`). Đây là cách phân lớp khái niệm để giải thích, không phải thiết kế triển khai của một sản phẩm đang tồn tại.

| Thứ tự | ID | Nhãn | Vai trò |
|---|---|---|---|
| 01 | interface | Giao diện | Xem bài • làm bài • theo dõi |
| 02 | learning-services | Dịch vụ học tập | Khóa học • kiểm tra • tiến độ |
| 03 | content-data | Nội dung & dữ liệu | Video • tài liệu • kết quả |
| 04 | infrastructure | Hạ tầng | Máy chủ • lưu trữ • bảo mật |

- Recipe: `layer-separation-2d-v1` với bố cục bản địa 2D; không tuyên bố 3D hay mô phỏng vật lý.
- Cố định **3 trạng thái nhìn thấy**, tương ứng ba slide dự kiến: `assembled` → `separated` → `reassembled`.
- **2 chuyển cảnh Morph**, mỗi chuyển cảnh `1100 ms`. Tư thế ban đầu đã hiện diện, không tính là một chuyển cảnh.
- Mỗi lớp giữ màu, số, thứ tự và tên `!!` ổn định. Các lớp tịnh tiến theo trục dọc, không đổi kích thước hay góc quay.
- Thanh giải thích bên phải đứng yên để nhãn và vai trò luôn đọc được. Số trên lớp nối nghĩa với số trong thanh giải thích.
- Chi tiết trên từng lớp dùng offset cục bộ so với carrier. Chúng vẫn là các đối tượng phẳng riêng, không phải nhóm PowerPoint.
- Giữ geometry do generator tạo. Chỉ thay text của đối tượng `eyebrow` từ tiêu đề kỹ thuật tiếng Anh thành `KIẾN TRÚC / BỐN LỚP`. Thay đổi này được ghi rõ và đã kiểm tra kế hoạch không khác generator ở chỗ nào khác.
- Title dài 23 ký tự (giới hạn 26), subtitle 48 (giới hạn 70). Nhãn dài 7–18 ký tự (giới hạn 24), vai trò 26–29 (giới hạn 38). Giới hạn ký tự không thay thế kiểm tra chữ thực tế sau render.

## Nguồn và bằng chứng thực sự đã xem

Nguồn kỹ thuật: Microsoft, `https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks`.
Nguồn ý tưởng lớp: Presentation Process, `https://www.presentation-process.com/layer-diagram.html`.

Tệp `layer-separation.md` ghi ngày truy cập nguồn là 2026-10-04. Trong lần thực hiện này chỉ đọc mô tả cục bộ ngày 2026-10-04; **không truy cập lại hai trang, không xem media hay phát lại hoạt ảnh nguồn**. Các record trong `config.json` và `plan.json` phân biệt rõ ngày được nguồn cục bộ ghi lại với bằng chứng thực sự đã đọc.

Kế thừa nguyên tắc Morph ghép bằng tên `!!` và quan hệ tổng thể–lớp. Nội dung kiến trúc, nhãn tiếng Việt và lựa chọn bốn lớp được xây dựng mới. Không sao chép template hay tài sản đa phương tiện. Không xác lập quyền phân phối tài sản gốc; đầu ra không chứa chúng.

## Lệnh đã chạy

Thư mục làm việc cho các lệnh tương đối: `/workspace/scratch/7379e9724021/T003-forward`.

1. Đọc skill:
   `cat /workspace/scratch/7379e9724021/T003-forward/skills/pptx-motion/SKILL.md`
2. Liệt kê đúng phạm vi:
   `rg --files /workspace/scratch/7379e9724021/T003-forward`
3. Đọc checkpoint và reference:
   `cat docs/STATUS.md skills/pptx-motion/references/recipes.md skills/pptx-motion/references/plan-contract.md skills/pptx-motion/references/layer-separation.md skills/pptx-motion/references/evaluation.md`
4. Đọc generator và validator:
   `cat scripts/layer_separation.py scripts/validate_plan.py`
5. Đọc rủi ro đường đi:
   `cat skills/pptx-motion/references/motion-paths.md`
6. Tạo thư mục:
   `mkdir -p result`
7. Chạy khối `python3 - <<'PY'` dùng `json.dumps(..., ensure_ascii=False, indent=2)` và `Path.write_text(..., encoding='utf-8')` để ghi toàn bộ nội dung đang có trong `result/config.json`; in số lớp và độ dài title/subtitle/label/role.
8. Sinh kế hoạch, không bật fixture lỗi:
   `python3 scripts/layer_separation.py result/config.json result/plan.json`
9. Chạy khối Python cập nhật duy nhất eyebrow:

```python
import json
from pathlib import Path
path = Path('result/plan.json')
plan = json.loads(path.read_text(encoding='utf-8'))
next(obj for obj in plan['objects'] if obj['id'] == 'eyebrow')['text'] = 'KIẾN TRÚC / BỐN LỚP'
path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
```

10. Validate theo contract:
    `python3 scripts/validate_plan.py result/plan.json`
11. Chạy khối Python import `make_plan`, `binding_metrics` từ `scripts.layer_separation` và `validate` từ `scripts.validate_plan`; thực hiện các assertion bổ sung được ghi ở phần kết quả bên dưới. Không ghi hoặc sửa các script nguồn.
12. Chạy khối Python `Path('result/NOTES.md').write_text(...)` để lưu ghi chú này.

## Kết quả kiểm tra

- Validator: `valid=true`, `errors=[]`, scope `motion-plan-v0.1`.
- So sánh với `make_plan(config)` sau cùng một thay đổi eyebrow: bằng nhau hoàn toàn.
- Đúng 4 lớp, 3 trạng thái, 2 transition; `ablation=false`.
- 38 đối tượng persistent: 21 textbox và 17 shape; xuất hiện trong cả ba trạng thái.
- 16 ràng buộc child–carrier × 3 trạng thái = **48 kiểm tra**; **0 vi phạm**, độ lệch lớn nhất **0 px**.
- Các đối tượng thanh giải thích giữ nguyên geometry ở cả ba trạng thái.
- Geometry ghép lại trùng geometry tổng thể ban đầu. Caption trạng thái thay đổi theo đúng ý nghĩa.
- Khả năng backend: chỉ rect/ellipse/textbox, kích thước canvas 16:9, opacity=1, không xoay, kích thước không đổi, Morph có duration nguyên dương. Không có trường style ngoài danh sách được hỗ trợ.
- Khoảng hở dọc nhỏ nhất giữa hai carrier liên tiếp là **4 px** ở tư thế tổng thể và ghép lại; khi tách là 36 px. Với tịnh tiến tuyến tính đồng bộ, thứ tự và khoảng hở dương được bảo toàn. Đây là kiểm tra hình học giả định, không phải xác nhận PowerPoint nội suy như vậy.

## Vướng mắc và phần còn lại

Không có vướng mắc chặn bước lập kế hoạch. Thư mục nguồn chỉ cung cấp generator/validator và hướng dẫn cần thiết cho phạm vi này; không thực hiện pipeline export ở đây theo phân công.

`final_pptx_visual_qa=null`, `native_playback=null`. Trường generator `native_playback_verified=false` được giữ nguyên. Cần người xử lý export kiểm tra render **mọi slide của PPTX cuối**, đặc biệt dấu tiếng Việt, rồi inventory tên/loại đối tượng/duration. Chỉ phát deck chính xác trong phiên bản PowerPoint được ghi nhận mới xác minh chuyển động; chưa có bằng chứng đó ở bước này. Không chấm điểm sáng tạo/chuyển động hoặc đưa tỷ lệ chất lượng tổng hợp.
