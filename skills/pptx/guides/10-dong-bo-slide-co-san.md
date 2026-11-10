# 10. Đồng bộ một bộ slide có sẵn

Dùng mục này khi bạn nhận một bộ slide **đã đủ nội dung** nhưng chắp vá về hình thức: nhiều người
làm, mỗi slide một font, một màu, một kiểu hiệu ứng. Việc của bạn là làm cho cả bộ đồng điệu từ
trên xuống dưới mà không làm mất nội dung hay ý của tác giả.

## Nguyên tắc: giữ ruột, thay vỏ

| Ruột: không được đổi | Vỏ: được đổi |
|---|---|
| Mọi con số, đơn vị, nguồn | Font, cỡ chữ, màu |
| Thuật ngữ, tên người, tên bộ phận | Vị trí, bố cục, lề |
| Thứ tự lập luận và kết luận | Kiểu biểu đồ (cột, đường, thanh…) |
| Tiêu đề do tác giả viết | Cách cắt ảnh minh họa |
| Ảnh bằng chứng (hiện trường, sản phẩm, trước/sau) và video | Hiệu ứng trang trí, kiểu chuyển slide |
| **Hiệu ứng kể cơ chế** (máy chạy, dòng khí, lực dồn, vật đi theo đường bay) | Chỗ đặt và cỡ của video (mặc định tràn slide) |
| **Hình dạng của sơ đồ chuẩn** (xương cá, PDCA, Pareto, Gantt, cây lỗi, lưu đồ) | Cỡ, màu, độ dày nét của sơ đồ |
| Speaker notes của tác giả, và mọi vật mà notes nhắc tới | Viết hoa / viết thường (giữ đúng từ) |
| Logo và quy định của công ty, khổ slide | Đồ trang trí (bỏ được) |

- **Rút gọn câu được, thêm ý thì không.** Đoạn văn dài có thể tách thành ba ý ngắn, nhưng chỉ dùng
  chữ và số đã có. Câu gốc đầy đủ chuyển vào speaker notes. Một câu nghe hợp lý mà bản gốc không nói
  ("… và duy trì kết quả") vẫn là thêm ý.
- **Tiêu đề giữ nguyên chữ.** Tiêu đề viết hoa cả câu được đổi sang chữ thường đầu câu, đúng từng từ.
  Số thứ tự lệch (chỉ một slide có "1.") thì hỏi, đừng tự thêm hay bớt. Muốn thêm một câu thông điệp
  ("Que hàn ẩm chiếm 38% số lỗi") thì viết thành dòng riêng dưới tiêu đề, chỉ nói điều số liệu trên
  slide đã nói, và ghi vào danh sách để người dùng duyệt.
- **Sơ đồ chuẩn đọc theo quy ước.** Người làm QCC nhìn xương cá là biết đọc: đầu cá là vấn đề, xương
  nghiêng về phía đầu, nhánh trên và nhánh dưới, nguyên nhân bám vào xương của nó. Được thu nhỏ, đổi
  màu, đổi nét, nhích nhãn cho khỏi đè nét, bỏ trang trí. **Không được** vẽ sang dạng khác, bỏ một
  nửa, tách nhãn khỏi nhánh, đổi chiều. Muốn đổi dạng sơ đồ là việc "Làm lại" và phải hỏi trước.
- **Hiệu ứng kể cơ chế là ruột.** Slide mô phỏng máy chạy, khí thoát, lực ép là chỗ người xem hiểu ra
  vấn đề. Một bộ QCC thật có một slide 170 vật thể với 648 hiệu ứng: không ai dựng lại nổi, và ảnh chụp
  của nó thì không chạy. Không bao giờ thay slide đó bằng ảnh tĩnh của chính nó. Thay vỏ tại chỗ (bước
  5, "Slide có hiệu ứng").
- **Notes là lời của tác giả.** Giữ nguyên câu. Muốn thêm nhịp bấm thì thêm nhãn `[CLICK n]` vào đầu
  câu hoặc thêm dòng mới, không viết lại câu cũ. Vật nào notes nhắc tới (ví dụ "mũi tên vàng chạy tới
  vấn đề") là ý của tác giả: giữ vật đó.
- **Giữ khổ slide gốc.** Đổi khổ (4:3 sang 16:9, hay sang khổ của template công ty) là việc khác; hỏi.
- **Thấy số nghi sai hoặc mâu thuẫn: không tự sửa.** Ghi thành câu hỏi khi bàn giao.
- **Không ghi đè file gốc.** Lưu bản mới thành file khác.

## Bước 1. Lập bảng ý trước khi đụng vào file

Đây là thứ giữ chủ đích của bài. Mọi quyết định sau đều đối chiếu với bảng này.

| Slide | Slide này muốn người nghe nhớ gì (1 câu) | Bằng chứng (số, ảnh) | Nhóm |
|---|---|---|---|
| 3 | Tỉ lệ lỗi cả 6 tháng đều gấp đôi mục tiêu | biểu đồ 6 tháng, mục tiêu 2% | Sửa vỏ |

- Có kịch bản thì lấy từ kịch bản. Không có thì đọc tiêu đề, nội dung và speaker notes của từng slide.
- Câu nào bạn không chắc, đánh dấu "?" và hỏi. Đừng đoán ý tác giả.
- Gửi bảng này cho người dùng duyệt trước khi sửa nhiều.

## Bước 2. Kiểm kê

```
python scripts/pptx_tools.py inventory goc.pptx
python scripts/pptx_tools.py look goc.pptx
```

`inventory` liệt kê những gì mắt khó đo: cả bộ dùng mấy font (kể cả font lấy từ theme), mấy cỡ chữ,
mấy màu chữ, màu nền và màu khối nào nhiều nhất; slide nào có biểu đồ 3D, ảnh bị kéo méo, vật thể
tràn ra ngoài slide, chữ dưới 18 pt, hiệu ứng trang trí (nảy, xoay, bay), slide nào mở ra chỉ thấy
tiêu đề; các kiểu chuyển slide đang dùng và số hiệu ứng của từng slide. Tên vật thể nó in ra là tên bạn
dùng ở các bước sau. `look` cho bạn nhìn từng slide.

Slide nào có nhiều hiệu ứng (vài chục trở lên), mở ra trình chiếu xem chúng kể gì. Nếu là cơ chế, ghi
số hiệu ứng vào bảng ý: bản mới phải còn đúng số đó.

## Bước 3. Chia mỗi slide vào một nhóm

- **Giữ**: bố cục ổn, chỉ cần đổi font, màu, căn lại lề. Slide có hiệu ứng kể cơ chế luôn ở nhóm này.
- **Sửa vỏ**: cùng nội dung, sắp xếp lại; biểu đồ 3D đổi sang phẳng; ảnh cắt lại; tổ hợp hình thu gọn.
- **Làm lại**: đổi hẳn cách thể hiện. Dấu hiệu:
  - người xem không đọc ra ý chính trong khoảng 5 giây;
  - hình thức nói ngược nội dung (biểu đồ tròn cho một xu hướng theo thời gian, 3D làm sai so sánh);
  - bảng nhiều cột chỉ để nói một con số;
  - gạch đầu dòng "Bước 1, Bước 2…" thực chất là một quy trình;
  - một đoạn văn dài.

Bảng đổi dạng thường gặp:

| Đang là | Thật ra muốn nói | Đổi thành |
|---|---|---|
| Cột 3D | so sánh vài giá trị | cột hoặc thanh phẳng, nhãn số trên cột |
| Cột theo tháng + cột "mục tiêu" | xu hướng so với mục tiêu | đường, mục tiêu là đường xám |
| Tròn 3D, nhiều miếng | cái nào lớn nhất | thanh ngang xếp từ lớn đến nhỏ, tô màu một thanh |
| Bảng 6–8 cột | một con số, một xu hướng | số lớn + một câu + biểu đồ nhỏ; bảng đủ chuyển xuống phụ lục |
| Gạch đầu dòng là các bước | quy trình | sơ đồ bước trên một trục |
| Đoạn văn | vài lý do | ba ý ngắn, câu gốc vào notes |
| "Trước: X – Sau: Y" | sự thay đổi | hai số lớn cạnh nhau, số "sau" màu nhấn |

**Xem vật thể gốc trước khi xếp một slide vào nhóm Làm lại.** Bảng gốc là bảng PowerPoint thật, biểu đồ
gốc là biểu đồ thật, sơ đồ là nhóm hình có hiệu ứng: những thứ này sửa tại chỗ được (`retable`,
`rechart`, `scale`, `cutout`), nên slide đó là **Sửa vỏ**. Dựng lại từ đầu thì mất dữ liệu, mất ô gộp,
mất hiệu ứng, và tốn công. `inventory` và `extract` cho biết slide nào có bảng thật, biểu đồ thật.

Người dùng duyệt danh sách slide **Làm lại** trước khi bạn làm.

## Bước 4. Đồng bộ chung, một lần cho cả bộ

1. **Chọn hệ thống**, ghi ra một dòng: 1–2 font, 3–6 cỡ chữ (mục 4), một nền, một màu chữ, một màu
   chính, một màu nhấn. Có template công ty thì dùng template (mục 2). Không có thì lấy màu nền hoặc
   màu khối đang chiếm nhiều nhất trong bộ cũ (dòng `fills` của `inventory`) làm màu chính, để người
   quen bài vẫn nhận ra.
2. **Font vào theme, không gõ tay từng đoạn.** Ghi hai font vào theme rồi xóa font gõ tay trên các
   đoạn chữ, để chữ ăn theo theme (cách làm ở mục 9). Từ đó đổi font cả bộ chỉ cần sửa một chỗ.
3. **Mọi slide nội dung có tiêu đề ở cùng một chỗ, cùng cỡ, cùng màu.** Cùng lề trái.
4. **Bìa và slide cảm ơn cùng một kiểu**, như hai cái nắp của bài.
5. **Bỏ trang trí:** bóng chữ, chữ phát sáng, WordArt, ngôi sao, mặt cười, bánh răng, clip-art.

## Bước 5. Từng loại vật thể

### Biểu đồ

- Biểu đồ PowerPoint thật thì số nằm sẵn bên trong. Dựng lại phẳng từ chính số đó:

  ```
  python scripts/pptx_tools.py rechart vao.pptx 5 "Bieu do tron" --kind bar --sort --accent "Que hàn ẩm" -o ra.pptx
  ```

  Biểu đồ mới ở đúng chỗ cũ, giữ tên và mã của vật thể cũ, nên hiệu ứng gắn với nó vẫn chạy. Nó
  theo kiểu của mục 5 (nhãn số trực tiếp, không lưới); tiêu đề riêng của biểu đồ cũ không giữ, nên
  đưa ý đó vào tiêu đề slide hoặc dòng thông điệp. `--sort` xếp theo dãy số đầu tiên.
- Biểu đồ là **ảnh chụp** dán vào: xin tác giả file Excel. Không nhìn ảnh đoán số rồi vẽ lại.
- Được: đổi kiểu, xếp từ lớn đến nhỏ (trừ trục thời gian), tô màu một cột đang nói tới.
  Không được: đổi số, đổi đơn vị, bỏ chuỗi số liệu, cắt trục để chênh lệch trông lớn hơn.

### Ảnh

| Loại ảnh | Được làm |
|---|---|
| Minh họa, trang trí | Cắt cho vừa khung, cả bộ dùng cùng tỉ lệ khung, chỉnh tông cho hợp màu. |
| Bằng chứng (hiện trường lỗi, sản phẩm, chụp màn hình số liệu, trước/sau) | Chỉ cắt viền thừa. Không cắt mất chỗ đang nói tới, không đổi màu. |

- Ảnh bị kéo méo: `unstretch` cắt ảnh cho khớp khung (ảnh minh họa), hoặc `--box` đổi khung theo
  ảnh (ảnh bằng chứng, không mất phần nào).
- Ảnh trước/sau: cùng cỡ khung, cùng hàng, cùng cách cắt.
- Không bao giờ kéo giãn ảnh.

**Ảnh có nền dính liền** (khung xương cá vẽ sẵn trên nền nhà máy, logo trên nền trắng, icon tải về):

```
python scripts/pptx_tools.py cutout khung.png -o khung_tach.png
```

- Lệnh lấy màu nền từ viền ảnh, giữ trọn vật chính kể cả phần sáng bên trong (mắt cá, vệt bóng), bỏ nét vẽ
  mờ phía sau, viền mềm, không còn quầng sáng.
- Đặt ảnh đã tách vào **đúng hình cũ** bằng `replace_picture` (mục 9): cùng chỗ, cùng cỡ, cùng mã, nên
  hiệu ứng vẫn chạy.
- Xem ảnh tách trên nền tối **và** nền sáng trước khi dùng. Vật chính có phần nhạt gần màu nền thì hạ
  ngưỡng: `--range 30,90`.
- **Không tách bằng ngưỡng màu cứng và các ô chữ nhật cắt tay.** Cách đó chém mất phần vật chính (hàm cá,
  đuôi cá), đục lỗ chỗ sáng, và để lại viền.
- Nền là ảnh chụp nhiều chi tiết thì `cutout` không làm được. Xin tác giả file gốc, hoặc vẽ lại khung bằng
  hình PowerPoint với **đúng dạng** cũ (mục "Sơ đồ chuẩn").

### Tổ hợp hình quá to

Một sơ đồ ghép từ nhiều hình (xương cá, quy trình, sơ đồ tổ chức) tràn ra ngoài hoặc đè lên tiêu đề:

```
python scripts/pptx_tools.py scale vao.pptx 4 "Hinh 1" "Hinh 2" ... --by 0.7 --at 1.8,1.55 -o ra.pptx
```

- Lệnh thu cả cụm như một khối: vị trí, kích thước, cỡ chữ, độ dày nét, ô bảng, và đường bay của hình
  bên trong cụm. Hình dáng giữ nguyên, mã vật thể giữ nguyên nên hiệu ứng vẫn chạy.
- **Đừng group các hình đang có hiệu ứng riêng.** PowerPoint không chạy hiệu ứng cho hình nằm trong
  nhóm. Đưa danh sách tên vào `scale`, cụm vẫn rời như cũ.
- Lệnh báo khi chữ nhỏ nhất xuống dưới 18 pt. Khi đó **giữ nguyên hình sơ đồ**: đặt lại chữ về 18 pt
  và nới khung chữ; nhãn đè lên nét thì nhích nhãn ra hoặc tô nền trắng cho khung chữ. Vẫn không vừa
  thì tách sơ đồ ra hai slide (ví dụ: slide 1 cả sơ đồ chỉ có tên nhánh, slide 2 phóng to một nửa có
  đủ nguyên nhân). **Không bao giờ vẽ lại thành một dạng sơ đồ khác** để cho vừa.
- Tiêu đề là placeholder thì để nó ngoài danh sách `scale`; chỉnh vị trí tiêu đề riêng.

### Slide có hiệu ứng: thay vỏ tại chỗ

Hiệu ứng nằm trong slide (`<p:timing>`) và trỏ tới mã của từng vật thể. Nên:

- **Làm trên bản sao của bộ gốc.** Đổi thứ tự slide bằng cách đổi chỗ trong `sldIdLst`, xóa slide thừa.
  Đừng tạo slide mới rồi chép vật thể sang: hiệu ứng không đi theo vật thể.
- **Chỉ xóa vật thể của khung cũ** (thanh bước, nền, logo cũ). Không xóa vật thể có hiệu ứng, không xóa
  `<p:timing>`. Xóa nhầm một vật thể có hiệu ứng thì PowerPoint báo file hỏng khi mở.
- **Nền mới chèn xuống dưới cùng** (đầu danh sách vật thể của slide), nếu không nó che hết.
- Đổi màu khối được; dời hay thu cả cụm thì dùng `scale` (giữ mã và đường bay).
- **Kiểm:** `inventory` bản mới. Slide đó còn đúng số hiệu ứng như trong bảng ý, và không có dòng
  "effects point to … shapes that are gone".
- Không thay vỏ được mà không đụng hiệu ứng: để slide nguyên như cũ, chỉ đổi font, rồi ghi vào bàn
  giao. Muốn thay bằng ảnh hay dựng lại thì hỏi trước.

### Video

Giữ nguyên tệp. Mặc định video **tràn slide** (quay ngang) hoặc cao bằng slide (quay dọc). Tiêu đề là
một dải mỏng ở mép, hoặc nằm ở slide trước. Video thu vào một khung nhỏ thì người xem không thấy chi
tiết; muốn đặt nhỏ thì hỏi.

### Bảng

**Bảng là bảng PowerPoint thật**, không ghép từ hộp chữ và đường kẻ. Ghép tay thì đường kẻ cắt ngang
chữ, hàng lệch nhau, ô gộp phải che bằng hộp trắng, và người dùng không sửa được trong PowerPoint.

- Bảng gốc đã là bảng thật (Gantt, bảng kiểm, bảng so sánh): đổi vỏ **tại chỗ**, chữ và ô gộp giữ
  nguyên:

  ```
  python scripts/pptx_tools.py retable vao.pptx 8 "Table 4" --font Arial --head-rows 2 --fill FFFF00=7DB3E0 -o ra.pptx
  ```

  `--fill CU=MOI` đổi màu các ô theo màu cũ (thanh Gantt vàng thành xanh). Mọi ô khác thành nền trắng,
  viền mảnh; `--lines rows` chỉ kẻ ngang. Bảng quá to cho khung thì thu bằng `scale` (lệnh thu cả cột và
  hàng).
- Bảng mới: `shapes.add_table`, gộp ô bằng `cell.merge`, rồi gọi `style_table` (mục 9).
- **Gantt là một bảng:**
  - cột trái: số thứ tự, việc, chi tiết, người làm;
  - mỗi việc hai hàng Plan và Actual, các cột trái gộp qua hai hàng đó;
  - thanh tiến độ là **ô tô màu**, không phải hình đặt đè lên. Nhờ vậy thanh luôn thẳng cột;
  - mốc (milestone) là một hình nhỏ đặt theo mép cột tính từ độ rộng cột.
- Bảng nhỏ (khoảng 4×4 trở xuống) giữ dạng bảng: chữ từ 18 pt, chỉ kẻ ngang mảnh, cột số canh phải.
- Bảng lớn: hỏi "bảng này để nói điều gì?", đưa điều đó lên slide (bước 3), còn bảng đủ chuyển xuống
  slide phụ lục ở cuối bộ. Số liệu không mất, người hỏi lại vẫn tìm thấy.
- Slide phụ lục là chỗ tra cứu: chữ trong bảng 16 pt được. Tiêu đề: "Phụ lục: " + tiêu đề slide gốc,
  và ghi vào câu hỏi bàn giao. Thêm phụ lục ở **cuối** bộ để số thứ tự các slide khác không đổi.

## Bước 6. Chuyển động: dọn trước, thêm sau

1. **Dọn.** Bỏ mọi hiệu ứng `inventory` gọi là trang trí (nảy, xoay, bay, lắc), trừ hiệu ứng kể cơ
   chế. Trong kế hoạch của `pptx_tools.py motion`, một slide ghi danh sách rỗng (`"1": []`) là xóa hết
   hiệu ứng của slide đó.

   Kiểu chuyển slide thì dọn **ngay khi tạo bản sao**, trước cả bản tĩnh: chạy `motion` với
   `{"transitions": {"default": "none"}}`. Lệnh xóa cả kiểu bọc cho PowerPoint đời mới (Glitter,
   Checker, Peel Off…), thứ xóa tay hay sót. Bản tĩnh đem duyệt không còn hiệu ứng cũ lẫn vào. Dòng
   `transitions` của `inventory` phải ra `none` cho mọi slide.
2. **Giữ hiệu ứng có nghĩa.** Hiện từng nhánh sơ đồ theo lời người nói là có nghĩa. Slide nào giữ hiệu
   ứng cũ thì đừng ghi vào `clicks`: công cụ để nguyên.
3. **Đặt tên trước khi viết kế hoạch.** Tên mặc định ("TextBox 5", "Picture 12") và tên trùng nhau
   phải đổi thành tên có nghĩa (mục 9).
4. **Thêm theo mục 6:** chọn mức theo phòng. Họp nội bộ, báo cáo QCC: chuyển slide bằng Fade, mỗi ý một
   lần bấm khi người nói cần dẫn từng ý, Morph chỉ khi có một vật thật đi tiếp sang slide sau. Bìa không
   có lần bấm.
5. **Slide làm lại thì viết lại nhịp bấm từ bảng ý:** số lần bấm bằng số ý người nói cần dẫn. Một nhịp
   hay dùng trong báo cáo: số liệu có sẵn khi mở slide, câu kết luận hiện ở lần bấm.
6. **Slide không được mở ra trắng.** Lúc mở, người xem phải thấy khung của slide: tiêu đề cùng nhãn,
   trục, các ô, các số thứ tự bước. Lần bấm chỉ đưa thêm dữ liệu và kết luận. `inventory` báo slide nào
   mở ra chỉ thấy tiêu đề.

## Bước 7. Kiểm tra giữ ruột

```
python scripts/pptx_tools.py numbers goc.pptx moi.pptx
python scripts/pptx_tools.py look moi.pptx
```

- `numbers` liệt kê mọi con số có trong bản gốc (chữ, bảng, biểu đồ, notes) mà bản mới không còn, và
  số nào xuất hiện ít lần hơn trước. "2%" và "2 lần" là hai số khác nhau. Phải không còn số bị mất. Số
  chuyển xuống phụ lục hay vào notes vẫn được tính là còn.
- `numbers` sạch là **điều kiện cần, chưa đủ**: một con số có thể còn ở slide khác mà mất ở slide của
  nó. Đọc lại bảng ý ở bước 1: mỗi slide mới còn nói đúng câu đó, với đúng số đó không?
- `inventory` bản mới: dòng `transitions` chỉ còn những kiểu đã chọn; slide có hiệu ứng kể cơ chế còn
  đủ số hiệu ứng; số video bằng bản gốc, và video nào cũng tràn slide.
- Đặt notes gốc cạnh notes mới: câu của tác giả còn nguyên không?
- Chạy các câu hỏi của mục 8 trên bản mới.

## Bàn giao

- Đường dẫn file mới trước, kèm file gốc không bị đổi.
- Mỗi slide một dòng: Giữ, Sửa vỏ hay Làm lại, và vì sao.
- Những chỗ cần người dùng quyết, viết theo mẫu:

  ```
  Cần bạn quyết:
  1. Slide 2: chỉ slide này có số thứ tự trong tiêu đề. Đánh số cả bộ hay bỏ?
  2. Slide 3 và 5: tôi thêm một dòng thông điệp lấy từ số trên slide. Giữ không?
  3. Slide 11: tiêu đề phụ lục do tôi đặt. Giữ không?
  4. Slide 6: số tuần 4 (1,8%) lệch với ghi chú. Số nào đúng?   ← chỉ khi có số nghi sai
  ```
