# 11. Dựng lại cả một bộ: nhiều chặng, nhiều agent, chấm hai tầng

Dùng mục này khi một bộ slide đã có nội dung thật (ảnh hiện trường, video, mô phỏng, số liệu) phải được
**tái cơ cấu từ đầu đến cuối**: đổi thứ tự câu chuyện, gộp và tách slide, đổi giao diện. Việc dài, nên
chia cho nhiều phiên hoặc nhiều agent. Mục 10 vẫn là luật giữ ruột; mục này là cách chia việc và cách
chấm.

## Vì sao phải chia chặng

Bài học thật (bộ QCC 37 slide, 2026-11-09): một agent nhận một bản giao việc 300 dòng và dựng cả 38 slide
trong một lượt. Kết quả: nó tự xóa 1.042 hiệu ứng mô phỏng, đổi xương cá thành sơ đồ khác, đặt video
vào khung nhỏ, rồi tự chấm "đã kiểm". Nó biết các luật đó; luật nằm xa chỗ làm và không có cổng nào chặn.

Các nghiên cứu về agent làm slide đi tới cùng ba điều:

1. **Sửa trên slide gốc thay vì vẽ lại.** PPTAgent (EMNLP 2025) sinh các lệnh sửa slide tham chiếu, nhờ
   vậy giữ được bố cục và chi tiết khó làm lại. Với ta: slide Giữ và Sửa vỏ là chính slide cũ.
2. **Phân tích trước, dựng sau, sửa theo kết quả chạy.** PPTAgent tách bước đọc bộ gốc thành sơ đồ nội
   dung, rồi tự sửa theo phản hồi khi chạy lệnh. Với ta: chặng 0 và 1, rồi cổng sau mỗi đợt dựng.
3. **Người chấm tách khỏi người dựng.** Auto-Slides có agent kiểm riêng; DeepPresenter có người chấm chỉ
   nhìn sản phẩm. Với ta: chặng 5, khác họ model với người dựng (D008).

## Bảy chặng

Mỗi chặng là một phiên làm việc: đọc đầu vào là **file**, không dựa vào trí nhớ của phiên trước; ghi
đầu ra là file; dừng ở cổng.

| Chặng | Việc | Đầu ra | Cổng (không qua thì không sang chặng sau) |
|---|---|---|---|
| 0. Bóc tách | `extract`, `inventory`, `look` bộ gốc | thư mục `extract/` (ảnh, video gốc, `manifest.json`), báo cáo, ảnh từng slide | Mở trình chiếu mọi slide có từ 20 hiệu ứng: ghi mỗi slide kể cơ chế gì |
| 1. Bảng ý | Viết câu chuyện mới thành bảng ý (mục 10, bước 1) và `map.json` | `storyboard.md`, `map.json` | Người dùng duyệt. Slide gốc nào không có trong map thì có tên trong danh sách bỏ, kèm lý do |
| 2. Ba slide mẫu | Dựng 3 slide, trong đó có slide khó giữ nhất (sơ đồ chuẩn, mô phỏng) | `samples.pptx` | `check --map` đạt; người dùng duyệt. Mẫu chưa ổn thì sửa mẫu, không làm tiếp cả bộ |
| 3. Dựng theo đợt | Mỗi đợt một phần của câu chuyện, không quá 8 slide | bộ slide sau mỗi đợt | Sau mỗi đợt: `check --map`, `inventory`, `look` và nhìn **từng** slide của đợt |
| 4. Chuyển động | Viết `plan.json` (mục 6, 7), chạy `motion` | bộ có chuyển động | `check` (cổng chuyển slide), `morph_studio.py audit` |
| 5. Chấm độc lập | Agent khác chấm theo bảng điểm dưới đây | bảng điểm | Không đọc báo cáo của người dựng trước khi chấm |
| 6. Người dùng xem | Mở file trong PowerPoint | duyệt, hoặc danh sách sửa | — |

Cách giao việc cho agent: mỗi chặng một **thẻ việc** chừng một trang: đầu vào, việc, đầu ra, cổng, điều
cấm. Thẻ trỏ tới các mục guide cần đọc, không chép lại. Một bản giao việc dài cho cả bảy chặng là thứ đã
thất bại.

## Dựng trên bản sao bộ gốc

- Tạo bản sao, rồi dọn ngay mọi kiểu chuyển slide cũ: `motion` với `{"transitions": {"default": "none"}}`.
- Slide **Giữ** và **Sửa vỏ** là chính slide cũ, thay vỏ tại chỗ (mục 10, "Slide có hiệu ứng").
- Slide **Làm lại** và slide mới: thêm vào cuối rồi dời tới chỗ của nó. Ảnh và video lấy từ thư mục
  `extract/media`, **không bao giờ** cắt từ ảnh chụp màn hình của slide cũ: ảnh chụp mờ, mất chữ, và mô
  phỏng thì không còn chạy.
- Ảnh bằng chứng cắt bằng tính năng crop của PowerPoint, không cắt file ảnh: bản gốc còn nguyên bên trong,
  và `check` so được.
- Sắp lại thứ tự slide:

  ```python
  ids = prs.slides._sldIdLst
  items = list(ids)
  order = [1, 2, 3, 38, 4]          # số slide trong bản sao, theo thứ tự mới
  for el in items:
      ids.remove(el)
  for n in order:
      ids.append(items[n - 1])
  # slide bỏ: không có trong order; xóa luôn quan hệ của nó: prs.part.drop_rel(items[n - 1].rId)
  ```

## `map.json`: bảng ý cho máy đọc

Khóa là số slide mới. `old`: các slide gốc mà slide này lấy nội dung. `group`: `keep`, `reskin` hoặc
`rebuild`. `drop`: tên ảnh của slide gốc cố ý không dùng (mặt cười, nền cũ), lấy tên từ `manifest.json`.

```json
{
  "1":  {"old": [1], "group": "reskin", "drop": ["Picture 30"]},
  "18": {"old": [17], "group": "keep"},
  "17": {"old": [15, 16], "group": "rebuild"},
  "16": {"old": [], "group": "rebuild"}
}
```

`check` dùng map để kiểm: slide `keep` còn đủ hiệu ứng của slide gốc; slide `keep` và `reskin` còn đủ ảnh
của slide gốc, trừ ảnh có tên trong `drop`.

## Chấm điểm: hai tầng

### Tầng 1: cổng máy (đạt hoặc không)

```
python scripts/pptx_tools.py check goc.pptx moi.pptx --map map.json
python scripts/pptx_tools.py inventory moi.pptx
```

`check` có 8 cổng: kiểu chuyển slide chỉ còn Fade, Morph hoặc không có; không hiệu ứng nào trỏ tới vật
thể đã xóa; đủ video; video tràn slide; đủ số liệu; ảnh gốc không bị cắt chặt hơn bản gốc; slide `keep`
đủ hiệu ứng; ảnh gốc nằm đúng slide. Nó còn liệt kê ảnh không lấy từ bộ gốc để người chấm nhìn từng ảnh.
`inventory` thêm: một hoặc hai font, 3–6 cỡ chữ, không chữ nhỏ hơn mốc.

Còn cổng trượt thì chưa đem chấm tầng 2. Cổng đạt chỉ nói nội dung còn nguyên, **không nói bộ slide đẹp**
(D001).

### Tầng 2: mắt (agent chấm độc lập, rồi người dùng)

Bốn phần, mỗi phần 1–5 điểm (cách chia của PPTEval: nội dung, thiết kế, mạch; thêm phần chuyển động).
Chấm trên ảnh từng slide **và** khi trình chiếu, không chấm trên ảnh ghép thu nhỏ.

| Phần | 5 | 3 | 1 |
|---|---|---|---|
| **Câu chuyện** | Chỉ đọc tiêu đề là hiểu bài; mỗi slide một ý; mỗi số chính có một slide chủ | Đa số slide rõ ý; vài slide hai ý hoặc tiêu đề chỉ là nhãn | Đọc tiêu đề không ra mạch; slide dồn ý |
| **Giữ ruột** | Sơ đồ chuẩn đúng dạng; mô phỏng chạy như bản gốc; ảnh bằng chứng đủ và rõ | Còn đủ, nhưng có ảnh bị thu quá nhỏ hoặc sơ đồ lệch nét | Sơ đồ đổi dạng, mô phỏng thành ảnh, ảnh bị cắt mất chữ |
| **Thiết kế** | Một hệ thống: font, màu, lưới, tiêu đề cùng chỗ; mỗi slide một điểm nhấn; ảnh đặt có vai trò | Hệ thống có, vài slide lệch lưới hoặc dày chữ | Mỗi slide một kiểu; chữ bay, mũi tên lệch, icon khác bộ |
| **Chuyển động** | Morph chỉ ở chỗ có vật đi tiếp; tối đa 3 lần bấm; slide mở ra đã thấy khung | Đúng luật, nhưng có slide bấm thừa hoặc thiếu | Hiệu ứng cổ; chỗ có chỗ không; slide mở ra trống |

Bảng điểm của người chấm: điểm từng phần, rồi **3 slide tệ nhất** kèm lý do và cách sửa. Không cộng
thành một con số chung: phần Giữ ruột 1 điểm thì bộ slide không dùng được, dù ba phần kia 5 điểm.

Ví dụ đã chấm: bản dựng lại đầu tiên của bộ QCC qua 2/8 cổng (chuyển slide cổ, thiếu một video, 4 video
chỉ chiếm 49–64% slide, 80 con số mất, 976 hiệu ứng mô phỏng còn 0, ảnh gốc vắng trên hầu hết slide).
Theo luật trên, nó không được đem chấm tầng 2. Người dùng xem và loại nó với cùng các lý do đó.
