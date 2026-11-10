# T073 [pptx] Mắt xem chuyển động: lệnh `watch`

Agent: Claude (Fable 5.2), trưởng nhóm. Ngày: 2026-11-10. Nhánh `work/T073-claude-motion-eyes`, xếp sau
T097 (cần bản `pptx_tools.py` mới nhất).

## Vì sao

Chủ dự án hỏi vì sao agent yếu khi làm PPTX. Đọc lại sổ góp ý và các báo cáo thì nguyên nhân nặng nhất
là agent **không nhìn thấy chuyển động**: `look` chỉ xuất ảnh slide đã hiện đủ mọi thứ. Agent không
thấy lúc slide vừa mở, từng lần bấm, hay giữa cú Morph. Bộ T069a bị chấm 6/10 "gượng gạo" trong khi
kiểm tra Morph báo 0 lỗi. Agent dựng lại bộ QCC xóa 976 hiệu ứng mô phỏng mà không biết chúng kể gì.
Chủ dự án chọn làm việc này trước.

Lời chỉ dẫn không làm thay được (D011): muốn biết PowerPoint thật sự vẽ gì ở từng lần bấm thì phải
chạy trình chiếu và chụp lại.

## Đã làm

**Đồ nghề** (`scripts/pptx_tools.py`):

- Lệnh mới **`watch DECK [--slides 3,6] [-o DIR]`**. Lệnh mở trình chiếu thật của PowerPoint trong một
  cửa sổ, tự bấm như người nói, và chụp cho mỗi slide một dải ảnh `slide-NN.jpg`:
  - ba khung giữa cú Morph (25%, 50%, 75%) nếu slide vào bằng Morph;
  - khung `open`: lúc slide vừa mở và đã đứng yên;
  - một khung sau mỗi lần bấm;
  - lần bấm chạy lâu hơn 2 giây (mô phỏng, chuỗi hiệu ứng) có thêm ba khung giữa chừng.
- Lệnh in ra, cho từng slide: vào bằng gì, mấy lần bấm, mỗi lần chạy bao lâu. Lần bấm không làm màn
  hình đổi gì được ghi `NOTHING CHANGES`; lần bấm có vật chuyển động rồi trở về như cũ được ghi riêng;
  thứ không bao giờ đứng yên (vòng lặp, video) được ghi sau 10 giây.
- Cách biết một bước đã xong: chụp liên tục, dừng khi không còn gì đổi trong 0,8 giây. Không đọc thời
  lượng từ file, vì thứ cần biết là PowerPoint thật sự vẽ gì.
- Cửa sổ trình chiếu được đẩy ra ngoài mép phải màn hình để không che người đang dùng máy, chừa 40 px
  trên màn hình (lý do ở mục kết quả âm tính). Ảnh lấy bằng `PrintWindow`, không chụp màn hình, nên cửa
  sổ khác che lên cũng không sao.

**Lời hướng dẫn:**

- Mục 8: phần mới **"Xem chuyển động: `watch`"** với câu hỏi cho từng loại khung (khung mở, mỗi lần
  bấm, lần bấm chết, ba khung Morph). Chưa chạy `watch` và chưa nhìn dải ảnh thì không được nói
  "chuyển động ổn".
- Mục 6, 7, 9, 11 và SKILL.md trỏ tới `watch`. Bước 8 của SKILL là "xem nó chuyển động". Mục 11 trước
  đây bảo agent "mở trình chiếu" các slide nhiều hiệu ứng, việc agent không làm được; nay là
  `watch --slides`.

## Bằng chứng

| Kiểm | Kết quả | Bậc |
|---|---|---|
| `watch` trên T090 (7 slide, 9 lần bấm, 1 Morph) | 29 giây; dải ảnh `preview/t090/` | 5b |
| `watch` trên T069a (14 slide, 9 lần bấm, 4 Morph) | 34 giây; `preview/t069a/` | 5b |
| `watch` trên demo T087 (5 slide, 8 lần bấm, 1 Morph) | 24 giây; `preview/t087/` | 5b |
| `watch --slides 16,17` trên bộ QCC thật 243 MB (giữ ngoài repo) | 25 giây; slide mô phỏng 648 hiệu ứng: 1 lần bấm chạy 6,4 giây, ba khung giữa chừng cho thấy vòng keo lớn dần và đồ thị tốc độ được vẽ ra | 5b |
| Chụp có sai so với trình chiếu trên màn hình không | 16/16 lần chạy cho dải ảnh **giống hệt** bản chạy trên màn hình (4 slide, 9 lần bấm mỗi lần) | 5b |
| Lần bấm chết thật | test dựng một ô chữ rỗng, cho nó hiện bằng một lần bấm: `watch` báo đúng `dead` | 5b |
| `pytest tests/test_pptx_tools.py` | 26 qua (3 test mới chạy ở mọi máy; 1 test chạy PowerPoint thật khi đặt `PPTX_NATIVE=1`) | 1 |
| Chủ dự án | chưa xem | 6 |

Bậc 5b: PowerPoint thật chạy trình chiếu, máy chụp, trưởng nhóm đã nhìn các dải ảnh; chưa phải người
xem chấm.

**Mắt mới thấy được gì trên bộ T069a** (bộ bị chấm "gượng gạo", kiểm tra Morph 0 lỗi):

- `preview/t069a/slide-04.jpg`: giữa cú Morph, tiêu đề cũ "HAY Ý THỨC?" và tiêu đề mới "QUYẾT ĐỊNH"
  đè lên nhau; dấu "?" và dấu "✓" chồng nhau; chữ trong thẻ phải nhòe hai lớp.
- `preview/t069a/slide-09.jpg`: tiêu đề "BA BỘ PHẬN" và "MỘT CHỈNH THỂ" đè lên nhau; một thẻ rơi
  xuống trong khi hai thẻ kia đứng yên.

Trên T090, `preview/t090/slide-03.jpg` cho thấy ở khung 50% câu tục ngữ thứ hai trượt đè lên câu thứ
nhất và cắt qua vạch chia cột.

## Kết quả âm tính và giới hạn

1. **Đưa cửa sổ ra hẳn ngoài màn hình thì PowerPoint thỉnh thoảng ngừng vẽ giữa hiệu ứng.** Lần chạy
   đầu trên T069a báo nhầm hai lần bấm chết, và có khung dừng ở giữa lúc chữ đang mờ dần. Đo lại so
   với bản chạy trên màn hình: 12/16 lần chạy có ít nhất một dải ảnh lệch, kể cả khi ép cửa sổ vẽ lại
   trước mỗi lần chụp (6/8) lẫn khi không ép (6/8). Chừa 40 px của cửa sổ trên màn hình thì 16/16 lần
   khớp. Người dùng máy sẽ thấy một dải mỏng ở mép phải trong lúc lệnh chạy.
2. **Tỉ lệ diện tích thay đổi không dùng được làm thước đo.** Bản đầu in "slide mở ra còn thiếu 11%".
   Slide 6 của T090 trông trống một nửa mà số chỉ 11%, vì chữ mảnh chiếm ít điểm ảnh. Đã bỏ con số
   này; agent phải nhìn khung `open`.
3. **Một quãng nghỉ dài hơn 0,8 giây ở giữa một lần bấm bị đọc là hết lần bấm.** Khung chụp khi đó là
   khung giữa chừng. Ba bộ đã thử không có trường hợp này.
4. **Loại "chuyển động rồi trở về như cũ"** (nhấn mạnh, đường bay khép kín) mới chỉ có test trên ảnh
   dựng tay, chưa thử trên trình chiếu thật.
5. **Chưa làm phần còn lại của đề bài gốc trong ROADMAP:** tuyến DeckCraft `render-animation` và bảng
   so lệch với CreateVideo. Tuyến trình chiếu thật đã cho khung hình trong 2–4 giây mỗi slide từ chính
   PowerPoint, nên tuyến DeckCraft không còn lý do để làm.
6. Cần Windows, PowerPoint và một phiên desktop đang đăng nhập. Hai agent chạy `watch` cùng lúc trên
   một máy chưa được thử.
7. Trigger bấm vào hình (`interactiveSeq`) không nằm trong dãy bấm chính nên `watch` không chạy tới;
   việc đó vẫn là của `interactive_show_harness.py` (T058).

## Việc tiếp theo

- Một model nhỏ dựng một bộ có chuyển động và dùng `watch`: nó có tự thấy và sửa được chữ đè lên nhau
  giữa cú Morph không. Đây là phép thử xem mắt mới có ích cho agent nhỏ hay chỉ cho model mạnh.
- T076 (thư viện nước Morph) và T080 (bảng động từ → chuyển động) đã hết bị chặn.
