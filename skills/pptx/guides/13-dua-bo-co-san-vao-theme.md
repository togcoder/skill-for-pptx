# 13. Đưa một bộ có sẵn vào một theme

Dùng mục này khi người dùng có **một bộ slide đã đủ nội dung** và **một theme** (một bộ mẫu, một bộ quy
định về nền, thanh bước, logo, tiêu đề, font), và muốn bộ slide đó mang theme này. Mục 10 vẫn là luật giữ
ruột; mục 11 là quy trình khi phải kể lại câu chuyện. Mục này là **thao tác ở giữa**: đổi vỏ, giữ nguyên
cách tác giả đã sắp nội dung.

## Vì sao việc này hay hỏng

Bài học thật: một bộ QCC 37 slide, bốn lần làm, bốn kiểu hỏng.

| Lần | Agent đã làm | Người dùng thấy |
|---|---|---|
| 1, 2 | Vẽ lại từng slide từ đầu theo theme | Mất ảnh bằng chứng, biểu đồ bị đổi, chữ nhỏ như văn bản, câu tự bịa |
| 3 | "Đừng làm hỏng nội dung" → không đụng gì, chỉ đổi vài chỗ vỏ | Gần như không khác bản gốc |
| 4 | Dán vỏ mới lên trên slide cũ | Hai logo chồng nhau, tiêu đề đè lên bảng, chữ xanh trên nền tối |

Cả bốn lần agent đều báo "đã kiểm". Ba nguyên nhân:

1. **Không có thao tác ở giữa.** Agent chỉ biết hai cực: vẽ lại hết, hoặc để nguyên. Việc người dùng cần
   nằm giữa hai cực đó.
2. **Vỏ cũ không nằm trên slide.** Logo cũ và nền tối nằm trong *slide master*. Agent dò từng slide nên
   không bao giờ thấy, sửa bao nhiêu lần cũng còn hai logo.
3. **Không nhìn.** Agent chạy vài lệnh đếm, thấy "đạt", rồi giao. Lỗi mà người xem thấy trong một giây thì
   không lệnh nào trong số đó đo.

## Ba mức cho mỗi slide

Trước khi làm, xếp **từng slide** vào một mức. Ghi vào bảng ý.

| Mức | Làm gì | Dùng cho |
|---|---|---|
| **0. Để nguyên** | Chỉ đổi vỏ quanh nó. Không co, không dời. | Slide tràn hình (một cảnh, một video), slide mô phỏng nhiều hiệu ứng |
| **1. Vào theme** (mặc định) | Gỡ vỏ cũ, gắn vỏ mới, co cả khối nội dung vào vùng theme để trống, đổi mực cho chữ không còn đọc được. **Cách sắp xếp của tác giả giữ nguyên.** | Hầu hết các slide |
| **2. Dựng lại bố cục** | Sắp lại nội dung, vẫn đủ mọi ảnh, số, biểu đồ, bảng của slide gốc (mục 10). Làm mẫu trước, người dùng duyệt rồi mới làm. | Chỉ những slide người dùng chỉ ra, hoặc đã duyệt trên mẫu |

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

Ba việc, theo thứ tự. Thiếu một việc thì chưa được nói "đã kiểm".

**1. `glance`: lỗi nhìn một giây là thấy.**

```
python scripts/pptx_tools.py glance 5_xong.pptx
```

Lệnh hỏi chính PowerPoint: chữ thật sự nằm ở đâu, màu gì, cỡ bao nhiêu, kể cả **ô bảng thật**, **biểu đồ** và các vật của master. Nó báo:

| Lệnh ghi | Nghĩa |
|---|---|
| `text on text` | hai dòng chữ in đè lên nhau (hai tiêu đề, vỏ gắn hai lần) |
| `cannot read` | chữ gần trùng màu với nền phía sau nó, kể cả chữ trong biểu đồ và ô bảng |
| `picture on the master's picture` | logo mới nằm trên logo cũ của master |
| `same picture twice` | một ảnh nằm hai lần đúng một chỗ, hoặc cùng một ảnh nội dung bị lặp ở nhiều khung trên slide |
| `text hidden` | ảnh, video, bảng nằm đè lên chữ |
| `text on picture` | chữ đặt lên ảnh, bảng hoặc biểu đồ có nền rối (độ tương phản nhiễu cao) |
| `content under the shell` | ảnh, bảng, biểu đồ chui dưới thanh bước, logo, chân trang |
| `text spills` | chữ dài hơn khung của nó và tràn sang vật bên cạnh |
| `title on content` | tiêu đề nằm vắt qua ảnh, bảng |
| `text off the slide`, `table off the slide` | tràn ra ngoài slide |
| `tiny text` | hơn một phần năm số chữ nhỏ hơn mức tối thiểu, một đoạn chữ quá nhỏ (< 75% sàn), hoặc chữ trong **bảng / biểu đồ** dưới sàn |
| `broken symbol` | ký tự biểu tượng Wingdings/PUA (`U+F000–U+F0FF`) bị rơi về font chữ thường thành ô vuông |
| `draft text` | còn sót chữ mẫu hoặc câu chú thích nháp ("Lorem ipsum", `[TODO]`, "kept from...", "nothing redrawn") |
| `missing` | slide này thiếu thứ mà hầu hết slide khác có (tiêu đề, thanh bước) |

Mỗi slide có lỗi có một ảnh `faults-NN.png` khoanh đỏ từng chỗ. **Mở ảnh đó ra.** Sửa trong script, dựng
lại, chạy lại, cho tới khi hết. Lỗi nào quyết định để lại (ví dụ lỗi có sẵn trong bản gốc và người dùng
chưa nhờ sửa) thì ghi vào bàn giao, kèm lý do.

`glance` chỉ đo được những gì đo được. Nó **không** biết slide có đẹp không, có điểm nhấn không, có trống
không. Hết lỗi `glance` chưa phải là tốt.

**2. Mở từng slide ở cỡ lớn.** `glance` đã xuất `slide-NN.png` cho mọi slide. Mở **từng ảnh một**, không
xem ảnh ghép thu nhỏ: ở cỡ thu nhỏ, hai logo chồng nhau trông như một. Với mỗi slide, trả lời các câu hỏi
của mục 8.

**3. Đặt cũ cạnh mới.**

```
python scripts/pptx_tools.py compare goc.pptx 5_xong.pptx
```

Mỗi slide một ảnh: slide cũ ở trên, slide mới ở dưới. Với mỗi cặp, trả lời ba câu:

- Slide cũ có gì mà slide mới **không còn** (một ảnh, một con số, một nhãn, một mũi tên)?
- Có gì ở slide mới **tệ hơn** slide cũ (nhỏ hơn, mờ hơn, lệch hơn, khó đọc hơn)?
- Có gì ở slide mới mà **không có trong bản gốc** (một câu, một con số, một hình)? Nếu có, ai cho thêm?

Rồi mới chạy `check` (mục 11) cho phần giữ ruột.

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
