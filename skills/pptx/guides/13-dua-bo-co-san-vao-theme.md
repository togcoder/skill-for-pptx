# 13. Đưa một bộ có sẵn vào một theme

Dùng mục này khi người dùng có **một bộ slide đã đủ nội dung** và **một theme** (một bộ mẫu, một bộ quy
định về nền, thanh bước, logo, tiêu đề, font), và muốn bộ slide đó mang theme này. Mục 10 vẫn là luật giữ
ruột; mục 11 là quy trình khi phải kể lại câu chuyện. Mục này là **thao tác ở giữa**: đổi vỏ, giữ nguyên
cách tác giả đã sắp nội dung.

## Vì sao việc này hay hỏng

Bài học thật: bộ QCC 37 slide, bốn lần làm, bốn kiểu hỏng — vẽ lại từ đầu (mất ảnh, đổi biểu đồ, chữ nhỏ);
"đừng làm hỏng nội dung" thành không đụng gì; dán vỏ mới lên slide cũ (hai logo, tiêu đề đè bảng, chữ
sáng trên nền tối). Ba nguyên nhân: (1) không có thao tác ở giữa "vẽ lại hết" và "để nguyên"; (2) vỏ cũ
nằm trong slide master chứ không nằm trên slide; (3) không nhìn — chạy vài lệnh đếm thấy "đạt" rồi giao.

## Ba mức cho mỗi slide

Trước khi làm, xếp **từng slide** vào một mức. Ghi vào bảng ý.

| Mức | Làm gì | Dùng cho |
|---|---|---|
| **0. Để nguyên** | Chỉ đổi vỏ quanh nó. Không co, không dời. | Slide tràn hình (một cảnh, một video), slide mô phỏng nhiều hiệu ứng |
| **1. Vào theme** (mặc định) | Gỡ vỏ cũ, gắn vỏ mới, co cả khối nội dung vào vùng theme để trống, đổi mực cho chữ không còn đọc được. **Cách sắp xếp của tác giả giữ nguyên.** | Hầu hết các slide |
| **2. Dựng lại bố cục** | Sắp lại nội dung theo [mục 14](14-dung-lai-bo-cuc-mot-slide.md), vẫn đủ mọi ảnh, số, biểu đồ, bảng của slide gốc (mục 10). Làm mẫu trước, người dùng duyệt rồi mới làm. | Chỉ những slide người dùng chỉ ra, hoặc đã duyệt trên mẫu |

Hai câu người dùng hay nói, và nghĩa của chúng:

- **"Đừng làm hỏng nội dung nữa"** nghĩa là lùi về **mức 1**, không phải mức 0. Vẫn phải vào theme, vẫn
  phải sạch lỗi. Để nguyên bản gốc rồi giao lại là không làm việc.
- **"Chưa thấy khác gì"** nghĩa là có slide cần **mức 2**. Hỏi slide nào, làm 2–3 mẫu, đừng tự dựng lại
  cả bộ.

Đừng nhảy từ cực này sang cực kia sau một lời chê. Tìm xem lời chê nói về mức nào của slide nào.

## Vỏ cũ nằm ở đâu

Vỏ là thứ lặp lại: nền, logo, thanh bước, khung tiêu đề, chân trang. Nó nằm ở ba chỗ, và phải gỡ **cả
ba**:

- **slide master**: thường là nền và logo. Sửa ở đây một lần là mọi slide đổi theo;
- **layout**: ít gặp hơn, cùng cách xử lý;
- **trên từng slide**: một nhóm hình hoặc một ảnh đặt đúng một chỗ trên hầu hết các slide (thanh bước).

```
python scripts/pptx_tools.py shell goc.pptx
```

Lệnh liệt kê cả ba chỗ, mỗi thứ một mã (`m1`, `l1`, `r1`…), kèm chữ của nó. Đọc kỹ dòng "text differs per
slide": chữ đó là **nội dung** (đang ở bước nào, tiêu đề gì), bạn cần nó để dựng vỏ mới.

## Sáu bước

Viết cả sáu bước vào **một script dựng**, đọc từ bản gốc, ghi ra file mới. Không sửa tay trên file kết quả.

1. **Gỡ vỏ cũ.**
   ```
   python scripts/pptx_tools.py shell goc.pptx --strip m1,m2,r1 --background F6F2EA -o 1_tran.pptx
   ```
   Vật có hiệu ứng thì lệnh giữ lại. Chữ của những thứ đã gỡ nằm trong `1_tran.shell.json`, theo từng slide.
2. **Tiêu đề.** Tiêu đề cũ thành tiêu đề của theme, **giữ nguyên chữ**. Slide không có tiêu đề riêng thì
   lấy tên bước của nó từ thanh bước cũ. Không đặt tiêu đề mới bằng lời của bạn.
3. **Co nội dung vào vùng theme để trống** (mức 1):
   ```
   python scripts/pptx_tools.py fit 2_tieude.pptx --into 0.67,2.2,18.67,8.3 --slides 2-36 -o 3_vua.pptx
   ```
   `--into` là vùng dưới tiêu đề, trên chân trang, tính bằng inch: trái, trên, rộng, cao. Cả khối nội dung
   được co đều, giữ nguyên vị trí tương đối, mã và hiệu ứng. Chữ không bao giờ bị co xuống dưới mức tối
   thiểu của mục 4. Slide mức 0 thì để ngoài `--slides`.
4. **Gắn vỏ mới**: nền, thanh bước, logo, tiêu đề, chân trang của theme. Đặt tên các vật của vỏ bắt đầu
   bằng `!!`. Ảnh trang trí của nền phải nằm **dưới** nội dung.
   - Nếu có dùng `follow_theme` xóa font gõ tay, kiểm tra ngay các ký tự mũi tên/ô đánh dấu kiểu Wingdings
     (`U+F000–U+F0FF`): sang Arial/Calibri chúng biến thành ô vuông (``). Đổi sang Unicode chuẩn (`→`,
     `▸`, `✓`) hoặc giữ font biểu tượng (`inventory` và `glance` sẽ bắt lỗi này ở mục `broken symbol`).
   - Nếu dựng lại hoặc chỉnh XML **biểu đồ xếp chồng** (`stacked` / `percentStacked` bar/area), không bao
     giờ dùng `dLblPos="outEnd"` — PowerPoint sẽ từ chối mở file (dùng `ctr`, `inEnd`, hoặc `inBase`).
5. **Đổi mực.** Chữ trắng viết cho nền tối sẽ biến mất trên nền sáng:
   ```
   python scripts/pptx_tools.py glance 4_vo.pptx --ink 1D2433 5_xong.pptx
   ```
   Chỉ chữ không đọc được mới đổi màu, kể cả chữ trong biểu đồ và bảng. Chữ đỏ, chữ xanh có nghĩa thì giữ.
   Nếu bảng cần đổi cả nền ô tiêu đề và lưới viền, dùng `retable` thay vì tự sửa từng ô bằng tay.
6. **Kiểm** (phần dưới). Còn lỗi thì sửa **trong script**, chạy lại từ bước 1. Không tách kiểm tra riêng lẻ
   trước khi chốt mà không nhìn đủ từng `slide-NN.png`, và không dán cùng một ảnh chứng cứ nhiều lần lên
   cùng một slide hay đặt chữ trực tiếp lên vùng ảnh rối.

Dựng lại cả bộ 37 slide theo cách này mất khoảng hai phút. Vì vậy không có lý do gì để vá tay.

## Kiểm trước khi đưa cho ai xem

Ba việc, theo thứ tự; thiếu một việc là chưa được nói "đã kiểm". Câu hỏi chi tiết ở mục 8.

**1. `glance`:** `python scripts/pptx_tools.py glance 5_xong.pptx` — lỗi người xem thấy trong một giây,
khoanh đỏ trên `faults-NN.png`. Mở ảnh đó, sửa trong script, dựng lại, chạy lại cho tới khi hết; lỗi nào
để lại (ví dụ có sẵn trong bản gốc) ghi vào bàn giao kèm lý do. `glance` không đo gu: hết lỗi chưa phải tốt.

| Lệnh ghi | Nghĩa |
|---|---|
| `text on text` | hai dòng chữ in đè lên nhau (hai tiêu đề, vỏ gắn hai lần) |
| `cannot read` | chữ gần trùng màu nền, kể cả chữ trong biểu đồ và ô bảng |
| `picture on the master's picture` | logo mới nằm trên logo cũ của master |
| `same picture twice` | một ảnh nằm hai lần, hoặc ảnh nội dung lặp ở nhiều khung |
| `text hidden` / `content under the shell` | ảnh, video, bảng đè lên chữ / nội dung chui dưới vỏ |
| `text on picture` / `title on content` | chữ hoặc tiêu đề đặt lên ảnh, bảng, biểu đồ có nền rối |
| `text spills` / `text off the slide` | chữ tràn sang vật bên cạnh / ra ngoài slide |
| `tiny text` | chữ dưới sàn (một phần năm số chữ, đoạn nhỏ hơn 75% sàn, hoặc chữ bảng/biểu đồ dưới sàn) |
| `broken symbol` | ký tự Wingdings/PUA rơi về font thường thành ô vuông |
| `draft text` | còn chữ mẫu/nháp ("Lorem ipsum", `[TODO]`, "kept from...") |
| `missing` | slide thiếu thứ hầu hết slide khác có (tiêu đề, thanh bước) |

**2. Mở từng slide ở cỡ lớn.** Mở **từng** `slide-NN.png`, không xem ảnh ghép thu nhỏ; mỗi ảnh có mã nhìn
ba ký tự ở dải dưới, nộp bằng `python scripts/pptx_tools.py seen <thư-mục> 3=U6G 4=K7P …` (mục 14).

**3. Đặt cũ cạnh mới.** `python scripts/pptx_tools.py compare goc.pptx 5_xong.pptx` — mỗi slide một ảnh cũ
trên, mới dưới; trả lời: bản cũ có gì bản mới không còn, có gì mới tệ hơn, có gì mới không có trong gốc.

Rồi chạy `check` (mục 11) cho phần giữ ruột.

## Khi người dùng chê

- Mỗi lời chê ghi một dòng vào sổ sửa (mục 1): lời nguyên văn, slide nào, mức nào.
- Sửa **trong script dựng**, chạy lại từ bản gốc. Không mở file kết quả ra vá. Vá chồng lên vá là lý do
  "càng sửa càng hỏng": mỗi lần vá dựa trên một file đã lệch, và không ai còn biết file đang ở trạng thái
  nào.
- Không lấy một bản dựng lỗi làm nền cho bản sau. Nguồn luôn là bản gốc.
- Người dùng bảo "kiểm lại đi": chạy lại cả ba việc ở trên, rồi **trả lời bằng danh sách**: slide nào còn
  lỗi gì, đã sửa gì. Câu "đã kiểm, ổn" không có danh sách đi kèm là câu chưa kiểm.

## Bàn giao

1. File `.pptx`, và thư mục ảnh cặp cũ/mới.
2. `glance` còn bao nhiêu slide có lỗi, từng lỗi để lại vì sao.
3. Danh sách slide theo mức 0, 1, 2. Slide nào bạn nghĩ cần mức 2 mà chưa làm, nói ra và hỏi.
4. Những gì chưa làm: chuyển động, bìa, slide kết.
