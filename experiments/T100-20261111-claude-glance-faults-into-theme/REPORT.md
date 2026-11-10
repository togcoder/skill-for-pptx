# T100 [pptx] Đưa một bộ có sẵn vào theme: lỗi thấy ngay, cặp cũ/mới, thao tác ở giữa

Agent: Claude (Fable 5.2), trưởng nhóm. Ngày: 2026-11-11. Việc do issue #83 và lời chủ dự án giao: một
agent đưa bộ QCC 37 slide vào theme, hỏng bốn lần, lần nào cũng báo "đã kiểm". Chủ dự án cho gộp không cần
phản biện.

## Chẩn đoán (đọc file thật, không đọc lại lời agent)

File của dự án nằm ngoài repo; các số dưới đây đo trên chính các file đó.

1. **Vỏ cũ nằm trong slide master.** Logo cũ (`Picture 35`) và tấm nền tối (`Rectangle 8`) của bộ gốc là
   vật thể của master. Script dựng của agent chỉ dò vật thể trên từng slide, nên không bao giờ gỡ được: 36/37
   slide có hai logo, chữ xanh của theme nằm trên nền tối cũ. Skill chưa có dòng nào nói về master.
2. **Không có thao tác ở giữa.** Bốn bản là hai cực: dựng lại từ đầu (mất ảnh, đổi biểu đồ, chữ nhỏ, câu
   bịa) hoặc để nguyên bản gốc. Mục 10 có ba nhóm Giữ / Sửa vỏ / Làm lại nhưng không có lệnh nào làm được
   "Sửa vỏ" cho cả một slide.
3. **Công cụ kiểm ngập trong nhiễu và mù với lỗi thấy ngay.** Trên bản lỗi nặng nhất, `design_critic` cho
   531 cảnh báo (163 về thời lượng hiệu ứng, 71 về easing) và `inventory` cho 108 dòng; không dòng nào nói
   hai logo, tiêu đề đè bảng, chữ bị video che. `check` chỉ đo nội dung còn hay mất nên đạt 5/6.
4. **Mục 8 bảo agent nhìn ảnh ghép thu nhỏ**, "slide nào đáng ngờ thì mở ảnh riêng". Ở cỡ thu nhỏ các lỗi
   trên không thấy được.

## Đã làm

**Đồ nghề** (`scripts/pptx_tools.py`; việc chữ không làm được, D011):

- **`glance DECK`**: hỏi chính PowerPoint từng vật thể nằm đâu, **chữ thật sự nằm đâu** (khung chữ đã vẽ,
  không phải khung hình), màu và cỡ chữ như đã vẽ, kể cả vật thể của layout và master; xuất ảnh từng slide.
  Báo 12 loại lỗi mà người xem thấy trong một giây (bảng ở mục 13), khoanh đỏ trên ảnh `faults-NN.png`. Mã
  thoát 1 khi còn lỗi. `--ink HEX OUT.pptx` đổi mực cho chữ không đọc được, kể cả chữ trong biểu đồ.
- **`shell DECK`**: liệt kê vỏ cũ ở cả ba chỗ (master, layout, vật lặp cùng chỗ trên nhiều slide), kèm chữ
  của nó. `--strip m1,r1 --background HEX -o OUT` gỡ; vật có hiệu ứng được giữ; chữ đã gỡ ghi ra JSON.
- **`fit DECK --into X,Y,W,H`**: co cả khối nội dung của mỗi slide vào vùng theme để trống; giữ cách sắp
  xếp, mã, hiệu ứng, đường bay; chữ không bị co dưới mức tối thiểu.
- **`compare OLD NEW`**: mỗi slide một ảnh lớn, cũ trên mới dưới.

**Lời hướng dẫn:**

- **Mục 13 mới**: ba mức cho mỗi slide (để nguyên / vào theme / dựng lại bố cục); nghĩa của "đừng làm hỏng
  nội dung" và "chưa thấy khác gì"; vỏ cũ nằm ở đâu; sáu bước trong một script dựng từ bản gốc; ba việc kiểm
  trước khi giao; không vá chồng lên vá; "đã kiểm" phải là một danh sách.
- Mục 8: bước 1 là `glance`; bước 2 là mở **từng** slide ở cỡ lớn, ảnh ghép chỉ để xem nhịp.
- SKILL.md: điều 11 (giao khi chưa nhìn) và 12 (vá chồng lên vá); lối vào mục 13; sáu dòng lệnh.
- Mục 9, 10, 11 trỏ tới các lệnh mới.

## Bằng chứng

Luật của `glance` được chỉnh trên bốn bộ thật cho tới khi tách được chúng:

| Bộ (ngoài repo) | Slide có lỗi | Lỗi chính |
|---|---|---|
| Bản gốc Ver3-4 | 16 / 37 | chữ nhỏ ở 8 slide; chữ đỏ trên nền xám xanh và chữ xanh lá trên nền nhạt ở 10 slide (lỗi thật có sẵn) |
| Theme v6 | 8 / 13 | chữ nhỏ (theme tự nó dùng chữ dưới 18 pt trên slide 20 in) |
| Ver7 (dán vỏ lên slide cũ) | **36 / 37** | hai logo 36 slide; chữ không đọc được 23 slide; chữ đè chữ 15 slide |
| Ver5 (dựng lại) | **23 / 39** | chữ bị che 32 chỗ; chữ đè chữ 12 slide; vỏ gắn hai lần ở 3 slide; đúng các slide chủ dự án đã khoanh (13, 17, 21) |

Bậc 5: ảnh và số đo đều từ PowerPoint; trưởng nhóm đã mở ảnh khoanh đỏ của từng loại lỗi.

**Thử thao tác ở giữa trên chính việc đã hỏng** (script `_scratch/t100/build.py` trong thư mục dự án): bản
gốc → `shell --strip m1,m2,r1,r2` → tiêu đề cũ thành tiêu đề theme → `fit` → vỏ v6 → `glance --ink`.

- Dựng cả 37 slide mất 2 phút 14 giây, chạy lại được từ bản gốc bất cứ lúc nào.
- `glance`: 30 slide có lỗi trước khi đổi mực, **13 slide** sau (179 đoạn chữ được đổi mực). Không còn hai
  logo, không còn tiêu đề đè nội dung, không còn chữ bị che do vỏ.
- `check` so với bản gốc: hiệu ứng nguyên vẹn (648 / 98 / 40 / 56 / 134 ở 5 slide mô phỏng), 5/5 video, đủ
  số, không ảnh nào bị cắt.
- Trưởng nhóm đã xem cả 37 slide trên hai tấm tổng quan và mở cỡ lớn các slide 13, 17, 20.

`pytest`: 14 test mới chạy ở mọi máy (luật `glance` trên dữ liệu dựng tay, `shell`/`fit`/`reink` trên file
dựng trong test), 1 test chạy PowerPoint thật khi đặt `PPTX_NATIVE=1`. Cả bộ: 636 qua.

## Kết quả âm tính và giới hạn

1. **Bản thử chưa phải bản giao.** 13 slide còn lỗi `glance` liệt kê: chữ nhỏ 7 slide (phần lớn có sẵn
   trong bản gốc), chữ tràn khung 5, chữ đè chữ 2 (nhãn trên slide 17 và 26, do chữ không bị co theo khung),
   1 chữ bị che ở slide kết. Thanh "Cause 1–4" mất ở vài slide mô phỏng vì script thử chỉ gắn lại khi tiêu
   đề có chữ "Cause". Kiểu chuyển slide cũ chưa dọn. Bìa và slide kết chưa đụng. Chưa slide nào được dựng
   lại bố cục (mức 2).
2. **`glance` không đo gu.** Slide trống, không điểm nhấn, bố cục đơn điệu: không có luật nào. Hết lỗi
   `glance` không có nghĩa là slide tốt.
3. **Luật thử rồi bỏ:** ảnh đè ảnh (bản gốc có 15 cặp cố ý), ảnh xoay nghiêng (bản gốc có 4, của tác giả),
   tỉ lệ chữ dưới 27 pt (29/37 slide gốc), khung chữ gốc thay cho khung chữ đã vẽ (báo nhầm khi ô chữ có dòng
   trống ở cuối).
4. Chữ trong bảng chưa được đo (bảng không cho PowerPoint đọc khung chữ theo cách này).
5. `glance` và `compare` cần PowerPoint trên Windows; khoảng 1 giây mỗi slide.
6. Chưa làm trong issue #83: cổng giữ hình dạng sơ đồ chuẩn (xương cá thành bốn hộp). Thao tác ở giữa không
   vẽ lại sơ đồ nên không sinh ra lỗi đó; với slide mức 2 thì vẫn cần.
7. Chưa model nhỏ nào làm việc này theo mục 13.

## Việc tiếp theo

- Agent đang làm bộ QCC dựng lại theo mục 13 từ script thử, sửa 13 slide còn lỗi, rồi mới bàn mức 2 với chủ
  dự án trên 2–3 slide mẫu.
- Cổng hình dạng sơ đồ chuẩn cho slide mức 2.
