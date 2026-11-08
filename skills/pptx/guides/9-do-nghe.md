# 9. Đồ nghề

Đồ nghề chỉ để làm những việc lời chỉ dẫn không tự làm được: ghi file, ghi chuyển động, xuất ảnh để
xem. Mọi quyết định thiết kế là của bạn, theo các mục 1–8.

## Dựng slide

- Dựng bằng `python-pptx`, chạy trong thư mục gốc của repo.
- Có file mẫu của người dùng thì mở chính file đó: `Presentation("mau.pptx")`.
- Không có file mẫu: `Presentation()`, rồi đặt `slide_width = Inches(13.333)`,
  `slide_height = Inches(7.5)`, dùng layout trống (`slide_layouts[6]`).
- **Đặt tên cho mọi vật thể:** `shape.name = "Tieu de"`, `"The A"`, `"!!buoc-5"`. Tên là cách bạn nói
  chuyện với công cụ chuyển động và với Morph. Mỗi tên chỉ dùng một lần trên mỗi slide.
- Vật đi tiếp sang slide sau bằng Morph: dùng **cùng tên bắt đầu bằng `!!`** ở cả hai slide (mục 7).
- Đặt cỡ chữ rõ ràng cho từng đoạn. Tắt tự co chữ:
  `text_frame.auto_size = MSO_AUTO_SIZE.NONE` và `word_wrap = True`.
- Biểu đồ: `slide.shapes.add_chart(...)`, để người dùng sửa được số liệu.
- Ảnh: cắt cho vừa khung bằng `crop_left/right/top/bottom`, không co giãn ảnh.
- Lưu bản tĩnh (chưa có chuyển động) thành một file riêng, ví dụ `deck.static.pptx`, để dễ quay lại.

## Ảnh có giấy phép

```
python scripts/forge_assets.py photos "tesla cybercab rear" --orientation landscape
```

Lệnh trả về danh sách ảnh (giấy phép, tác giả) và một tấm ảnh ghép để bạn chọn. Muốn tải ảnh đã
chọn vào trong code:

```python
import sys; sys.path.insert(0, "scripts")
import forge_assets
path, cand = forge_assets.resolve_photo({"search": "tesla cybercab rear", "pick": 2},
                                        Path("forge-cache"), box_ratio=16/9)
# cand["attribution"], cand["license"]: ghi vào slide nguồn ảnh
```

## Ghi chuyển động: `pptx_tools.py motion`

Viết một kế hoạch ngắn (JSON), gọi vật thể bằng tên:

```json
{
  "transitions": {"default": "none", "2": "morph", "6": "morph", "9": "fade"},
  "clicks": {
    "4": [["Truc", "Cot truoc"], ["Cot sau:wipe"], ["Ket luan:rise"]],
    "7": [["Nhanh May", "Nhanh Nguoi", "Nhanh Vat lieu"], ["Nguyen nhan goc:zoom"]]
  }
}
```

- `transitions`: kiểu chuyển **vào** slide đó, gồm `morph`, `fade` hoặc `none`. `default` áp cho mọi
  slide không ghi tên.
- `clicks`: mỗi phần tử là một lần bấm, liệt kê các vật hiện cùng lúc (tự cách nhau 0,12 giây).
  Viết `Ten:kieu` để chọn kiểu: `fade` (mặc định), `rise`, `wipe` hoặc `zoom`.
- Vật **không** nằm trong `clicks` thì có mặt ngay khi slide mở.
- Chuyển động cũ trên các slide có tên trong `clicks` sẽ bị thay; các slide khác giữ nguyên.

```
python scripts/pptx_tools.py motion deck.static.pptx plan.json -o deck.pptx
python scripts/morph_studio.py audit deck.pptx
python scripts/pptx_tools.py look deck.pptx
```

Gõ sai tên vật thể thì công cụ liệt kê các tên có thật trên slide. Nếu bạn cho một vật `!!` xuất
hiện bằng lần bấm trên một slide vào bằng Morph, công cụ báo lỗi (mục 7, luật 3).

**Speaker notes.** Viết notes cho từng slide theo mẫu: `[T=0]` một câu mở; sau đó `[CLICK 1]`,
`[CLICK 2]` … mỗi lần bấm một câu. Số `[CLICK n]` phải bằng số lần bấm của slide; `design_critic.py`
kiểm đúng số này (`NAR-ALIGN`) và dùng notes để chấm narrative. Với bộ slide **có sẵn** (mục 10),
notes là lời của tác giả: giữ nguyên câu, chỉ thêm nhãn `[T=0]` / `[CLICK n]` vào đầu câu.

## Bộ slide có sẵn (mục 10)

Các lệnh `inventory`, `rechart`, `scale`, `unstretch`, `numbers` đọc và ghi file; xem `python
scripts/pptx_tools.py -h`. Ba việc còn lại làm bằng `python-pptx`, gọi hàm của đồ nghề:

```python
import sys; sys.path.insert(0, "scripts")
import pptx_tools as tools
from pptx import Presentation

prs = Presentation("goc.pptx")
tools.theme_fonts(prs, "Segoe UI", "Segoe UI")   # hai font vào theme
for slide in prs.slides:
    tools.follow_theme(slide._element)           # xóa font gõ tay, chữ ăn theo theme
# chữ tiêu đề: run.font.name = "+mj-lt" (font tiêu đề của theme)

# đổi tên vật thể trước khi viết kế hoạch chuyển động
for shape in prs.slides[3].shapes:
    print(shape.shape_id, shape.name, shape.has_text_frame and shape.text_frame.text[:30])
prs.slides[3].shapes[2].name = "Nhanh may moc"

# biểu đồ mới (ví dụ dựng từ số trong một bảng) cùng kiểu với rechart
tools.add_chart(slide, "line", (left, top, width, height), ["Tuần 1", "Tuần 2"],
                [("Tỉ lệ lỗi (%)", [3.8, 3.0])], "0.0", color="1F4E79")
prs.save("moi.static.pptx")
```

Chuyển một bảng lớn xuống phụ lục mà không mất số: thêm slide cuối, chép phần tử của bảng sang
(`copy.deepcopy(table._element)` rồi `slide.shapes._spTree.append(...)`), xóa bảng ở slide cũ.
Ví dụ đầy đủ: `experiments/T093-20261108-claude-harmonize-deck/inputs/harmonize.py`.

## Công cụ cũ: dùng có điều kiện

- **Slide Forge** (`slide_forge.py`): dựng nhanh từ một bản mô tả, nhưng bố cục chung chung. Nếu
  dùng, đặt `"motion": {"morph": false}` để nó không tự thêm hình tròn `!!orb` vào góc mọi slide
  (nguyên nhân của Morph khắp nơi). Sau đó vẫn phải xem và sửa theo các mục 3–8.
  Các lỗi đã biết, đang chờ sửa:
  - giá trị KPI bằng 0 làm dừng bản dựng;
  - tiêu đề thẻ bị thu xuống 14 pt;
  - thanh tiến độ và logo bằng chữ bị gắn cứng.
- **Motion Director** (`motion_director.py draft/apply`): tự đề xuất chuyển động cho bộ slide có sẵn.
  Nó hay tạo quá nhiều lần bấm (bìa 6 lần bấm) và gắn Morph cho mọi lần chuyển slide. Nếu dùng, sửa
  kế hoạch nó đề xuất theo mục 6–7 trước khi `apply`. Với bộ slide mới, `pptx_tools.py motion` đơn
  giản hơn.
