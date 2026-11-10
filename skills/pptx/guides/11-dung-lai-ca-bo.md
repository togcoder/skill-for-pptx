# 11. Dựng lại cả một bộ: hiểu, làm, kiểm

Dùng mục này khi một bộ slide đã có nội dung thật (ảnh hiện trường, video, mô phỏng, số liệu) phải được
**tái cơ cấu từ đầu đến cuối**: đổi thứ tự câu chuyện, gộp và tách slide, đổi giao diện. Mục 10 vẫn là
luật giữ ruột; mục này là quy trình và cách chấm.

## Vì sao cần một quy trình

Bài học thật (bộ QCC 37 slide, 2026-11-09). Một agent nhận một bản giao việc 300 dòng, rồi dựng cả 38
slide trong một lượt. Kết quả:

- nó tự xóa 1.042 hiệu ứng mô phỏng;
- nó đổi xương cá thành một sơ đồ khác;
- nó đặt video vào khung nhỏ;
- rồi nó tự chấm "đã kiểm".

Nó biết các luật đó. Nhưng luật nằm xa chỗ làm, không có cổng nào chặn, và nó không hỏi khi chưa hiểu.

Các nghiên cứu về agent làm slide đi tới cùng ba điều:

1. **Sửa trên slide gốc thay vì vẽ lại.** PPTAgent (EMNLP 2025) sửa các slide tham chiếu, nhờ vậy giữ
   được bố cục và những chi tiết khó làm lại.
2. **Hiểu trước, dựng sau, sửa theo kết quả chạy.** PPTAgent đọc bộ gốc thành sơ đồ nội dung trước khi
   dựng, và tự sửa theo phản hồi khi chạy lệnh.
3. **Người chấm tách khỏi người dựng.** Auto-Slides có agent kiểm riêng. DeepPresenter có người chấm chỉ
   nhìn sản phẩm.

## Ba bước

Một agent làm được từ đầu đến cuối. Trong mỗi bước, agent tự chạy các cổng máy. Nó chỉ dừng để hỏi người
dùng ở **ba chỗ** (cột cuối).

| Bước | Agent tự làm | Dừng cho người dùng |
|---|---|---|
| **1. Hiểu** | (1) Bóc tách: `extract`, `inventory`, `look`; mở trình chiếu mọi slide có từ 20 hiệu ứng, ghi mỗi slide kể cơ chế gì. (2) Hỏi cho tới khi hiểu (mục 1, phần cuối), viết **bản hiểu ý** và `map.json`. (3) Dựng **3 slide mẫu**, trong đó có slide khó giữ nhất (sơ đồ chuẩn, mô phỏng); `check` đạt trên 3 slide đó. | Duyệt bản hiểu ý. Duyệt 3 slide mẫu: chưa ổn thì sửa mẫu, không làm tiếp. |
| **2. Làm** | Dựng trên bản sao bộ gốc, mỗi đợt một phần câu chuyện (không quá 8 slide). Sau mỗi đợt: `check --map`, `inventory`, `look`, và nhìn **từng** slide của đợt. Xong cả bộ thì làm chuyển động (mục 6, 7). | Không dừng, trừ khi gặp điều bản hiểu ý chưa nói: khi đó hỏi, đừng đoán. Người dùng góp ý giữa chừng: xếp loại theo mục 1, "Sau khi đã hiểu"; sửa nhỏ thì làm luôn, hiểu sai thì hỏi lại đúng phần sai. |
| **3. Kiểm** | `check` đạt 9/9, rồi chấm tầng 2 (dưới đây). Tốt nhất là một phiên khác, model khác, chưa đọc báo cáo của người dựng. Không có thì agent tự chấm và ghi rõ "tự chấm". | Người dùng mở file, đọc bảng điểm. |

Mỗi bước ghi kết quả ra file (bản hiểu ý, map, mẫu, bộ slide, bảng điểm). Vì vậy một phiên khác hoặc một
agent khác đọc file là làm tiếp được, không cần nhớ phiên trước.

## Dựng trên bản sao bộ gốc

- Tạo bản sao, rồi dọn ngay mọi kiểu chuyển slide cũ: `motion` với `{"transitions": {"default": "none"}}`.
- Slide **Giữ** và **Sửa vỏ** là chính slide cũ, thay vỏ tại chỗ (mục 10, "Slide có hiệu ứng").
- Bảng thật, biểu đồ thật, khung sơ đồ là ảnh: sửa tại chỗ bằng `retable`, `rechart`, `cutout` (mục 10,
  bước 3 và 5), đừng dựng lại từ đầu.
- Slide **Làm lại** và slide mới thì thêm vào cuối, rồi dời tới đúng chỗ. Ảnh và video lấy từ thư mục
  `extract/media`, **không bao giờ** cắt từ ảnh chụp màn hình slide cũ: ảnh chụp mờ, mất chữ, và mô
  phỏng trong đó không còn chạy.
- Ảnh bằng chứng thì cắt bằng tính năng crop của PowerPoint, không cắt file ảnh. Như vậy bản gốc vẫn còn
  nguyên bên trong, và `check` so được.
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

- **Khóa** là số của slide mới.
- `old`: các slide gốc mà slide này lấy nội dung.
- `group`: `keep`, `reskin` hoặc `rebuild`.
- `drop`: tên các ảnh của slide gốc cố ý không dùng (mặt cười, nền cũ). Lấy tên trong `manifest.json`.
- `"video": "small"`: chỉ ghi khi **người dùng đã đồng ý** để video của slide này nhỏ hơn slide.
- `dropped` (ở ngoài cùng): số các slide gốc cố ý bỏ hẳn. Bỏ slide nào thì người dùng phải đã duyệt
  trong bản hiểu ý.

```json
{
  "1":  {"old": [1], "group": "reskin", "drop": ["Picture 30"]},
  "18": {"old": [17], "group": "keep"},
  "17": {"old": [15, 16], "group": "rebuild"},
  "16": {"old": [], "group": "rebuild"},
  "12": {"old": [12], "group": "reskin", "video": "small"},
  "dropped": [9]
}
```

`check` dùng map để kiểm ba điều:

- **mọi slide gốc đều có mặt trong map**: nằm trong `old` của một hàng, hoặc trong `dropped`. Không có
  cách nào qua cổng bằng việc lờ đi một slide khó;
- slide `keep` còn đủ hiệu ứng của slide gốc;
- slide `keep` và `reskin` còn đủ ảnh của slide gốc, trừ những ảnh có tên trong `drop`.

## Chấm điểm: hai tầng

### Tầng 1: cổng máy (đạt hoặc không)

```
python scripts/pptx_tools.py check goc.pptx moi.pptx --map map.json
python scripts/pptx_tools.py inventory moi.pptx
```

`check` có 9 cổng:

1. kiểu chuyển slide chỉ còn Fade, Morph hoặc không có;
2. không hiệu ứng nào trỏ tới vật thể đã xóa;
3. đủ video;
4. video tràn slide (trừ slide người dùng đã đồng ý để nhỏ);
5. đủ số liệu;
6. ảnh gốc không bị cắt chặt hơn bản gốc;
7. mọi slide gốc đều có mặt trong map;
8. slide `keep` đủ hiệu ứng;
9. ảnh gốc nằm đúng slide.

Lệnh còn liệt kê những ảnh không lấy từ bộ gốc, để người chấm nhìn từng ảnh. `inventory` kiểm thêm: một
hoặc hai font, 3–6 cỡ chữ, không chữ nào nhỏ hơn mốc.

Còn cổng trượt thì chưa đem chấm tầng 2. Cổng đạt chỉ nói nội dung còn nguyên, **không nói bộ slide đẹp**
(D001).

### Tầng 2: mắt

Bốn phần, mỗi phần 1–5 điểm. Ba phần đầu theo cách chia của PPTEval (nội dung, thiết kế, mạch); phần thứ
tư là chuyển động. Chấm trên ảnh từng slide **và** khi trình chiếu, không chấm trên ảnh ghép thu nhỏ.

| Phần | 5 | 3 | 1 |
|---|---|---|---|
| **Câu chuyện** | Chỉ đọc tiêu đề là hiểu bài; mỗi slide một ý; mỗi số chính có một slide chủ | Đa số slide rõ ý; vài slide hai ý hoặc tiêu đề chỉ là nhãn | Đọc tiêu đề không ra mạch; slide dồn ý |
| **Giữ ruột** | Sơ đồ chuẩn đúng dạng; mô phỏng chạy như bản gốc; ảnh bằng chứng đủ và rõ | Còn đủ, nhưng có ảnh bị thu quá nhỏ hoặc sơ đồ lệch nét | Sơ đồ đổi dạng, mô phỏng thành ảnh, ảnh bị cắt mất chữ |
| **Thiết kế** | Một hệ thống: font, màu, lưới, tiêu đề cùng chỗ; mỗi slide một điểm nhấn; ảnh đặt có vai trò | Hệ thống có, vài slide lệch lưới hoặc dày chữ | Mỗi slide một kiểu; chữ bay, mũi tên lệch, icon khác bộ |
| **Chuyển động** | Morph chỉ ở chỗ có vật đi tiếp; mỗi lần bấm là một ý người nói nói ra (mục 6); slide mở ra đã thấy khung | Đúng luật, nhưng có slide bấm thừa hoặc thiếu | Hiệu ứng cổ; chỗ có chỗ không; slide mở ra trống |

Bảng điểm gồm điểm từng phần, rồi **3 slide tệ nhất**, mỗi slide kèm lý do và cách sửa. Không cộng bốn
phần thành một con số chung: phần Giữ ruột được 1 điểm thì bộ slide không dùng được, dù ba phần kia được
5 điểm.

Ví dụ đã chấm: bản dựng lại đầu tiên của bộ QCC chỉ qua 2 trong 8 cổng có lúc đó.

- chuyển slide kiểu cũ;
- thiếu một video;
- 4 video chỉ chiếm 49–64% slide;
- 80 con số bị mất;
- 976 hiệu ứng mô phỏng còn 0;
- hầu hết slide vắng ảnh gốc.

Theo luật trên, bản đó không được đem chấm tầng 2. Người dùng xem bản đó và loại nó vì đúng những lý do
này.
