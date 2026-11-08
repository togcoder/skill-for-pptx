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
| Ảnh bằng chứng (hiện trường, sản phẩm, trước/sau) | Chuyển động, chuyển slide |
| Logo và quy định của công ty, speaker notes | Đồ trang trí (bỏ được) |

- **Rút gọn câu được, thêm ý thì không.** Đoạn văn dài có thể tách thành ba ý ngắn, nhưng chỉ dùng
  chữ và số đã có. Câu gốc đầy đủ chuyển vào speaker notes.
- **Tiêu đề giữ nguyên chữ.** Muốn thêm một câu thông điệp ("Que hàn ẩm chiếm 38% số lỗi") thì viết
  thành dòng riêng dưới tiêu đề, chỉ nói điều số liệu trên slide đã nói, và ghi vào danh sách để
  người dùng duyệt.
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

`inventory` liệt kê những gì mắt khó đo: cả bộ dùng mấy font, mấy cỡ chữ, mấy màu chữ; slide nào có
biểu đồ 3D, ảnh bị kéo méo, vật thể tràn ra ngoài slide, chữ dưới 18 pt, hiệu ứng trang trí (nảy,
xoay, bay). Tên vật thể nó in ra là tên bạn dùng ở các bước sau. `look` cho bạn nhìn từng slide.

## Bước 3. Chia mỗi slide vào một nhóm

- **Giữ**: bố cục ổn, chỉ cần đổi font, màu, căn lại lề.
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

Người dùng duyệt danh sách slide **Làm lại** trước khi bạn làm.

## Bước 4. Đồng bộ chung, một lần cho cả bộ

1. **Chọn hệ thống**, ghi ra một dòng: 1–2 font, 3–6 cỡ chữ (mục 4), một nền, một màu chữ, một màu
   chính, một màu nhấn. Có template công ty thì dùng template (mục 2). Không có thì lấy màu đang
   chiếm nhiều nhất trong bộ cũ làm màu chính, để người quen bài vẫn nhận ra.
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

  Biểu đồ mới ở đúng chỗ cũ, giữ tên và mã của vật thể cũ, nên hiệu ứng gắn với nó vẫn chạy.
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

### Tổ hợp hình quá to

Một sơ đồ ghép từ nhiều hình (xương cá, quy trình, sơ đồ tổ chức) tràn ra ngoài hoặc đè lên tiêu đề:

```
python scripts/pptx_tools.py scale vao.pptx 4 "Hinh 1" "Hinh 2" ... --by 0.7 --at 1.8,1.55 -o ra.pptx
```

- Lệnh thu cả cụm như một khối: vị trí, kích thước, cỡ chữ, độ dày nét, ô bảng, và đường bay của hình
  bên trong cụm. Hình dáng giữ nguyên, mã vật thể giữ nguyên nên hiệu ứng vẫn chạy.
- **Đừng group các hình đang có hiệu ứng riêng.** PowerPoint không chạy hiệu ứng cho hình nằm trong
  nhóm. Đưa danh sách tên vào `scale`, cụm vẫn rời như cũ.
- Lệnh báo khi chữ nhỏ nhất xuống dưới 18 pt. Khi đó cụm có quá nhiều chữ cho chỗ này: đặt lại chữ
  về 18 pt và nới khung chữ, hoặc tách sơ đồ ra hai slide. Đừng để chữ nhỏ cho vừa.

### Bảng

- Bảng nhỏ (khoảng 4×4 trở xuống) giữ dạng bảng: chữ từ 18 pt, chỉ kẻ ngang mảnh, cột số canh phải.
- Bảng lớn: hỏi "bảng này để nói điều gì?", đưa điều đó lên slide (bước 3), còn bảng đủ chuyển xuống
  slide phụ lục ở cuối bộ. Số liệu không mất, người hỏi lại vẫn tìm thấy.

## Bước 6. Chuyển động: dọn trước, thêm sau

1. **Dọn.** Bỏ mọi hiệu ứng `inventory` gọi là trang trí (nảy, xoay, bay, lắc) và các kiểu chuyển
   slide khác nhau. Trong kế hoạch của `pptx_tools.py motion`, một slide ghi danh sách rỗng
   (`"1": []`) là xóa hết hiệu ứng của slide đó.
2. **Giữ hiệu ứng có nghĩa.** Hiện từng nhánh sơ đồ theo lời người nói là có nghĩa. Slide nào giữ hiệu
   ứng cũ thì đừng ghi vào `clicks`: công cụ để nguyên.
3. **Đặt tên trước khi viết kế hoạch.** Tên mặc định ("TextBox 5", "Picture 12") và tên trùng nhau
   phải đổi thành tên có nghĩa (mục 9).
4. **Thêm theo mục 6:** chọn mức theo phòng. Họp nội bộ, báo cáo QCC: chuyển slide bằng Fade, mỗi ý một
   lần bấm khi người nói cần dẫn từng ý, Morph chỉ khi có một vật thật đi tiếp sang slide sau. Bìa không
   có lần bấm.

## Bước 7. Kiểm tra giữ ruột

```
python scripts/pptx_tools.py numbers goc.pptx moi.pptx
python scripts/pptx_tools.py look moi.pptx
```

- `numbers` liệt kê mọi con số có trong bản gốc (chữ, bảng, biểu đồ, notes) mà bản mới không còn.
  Phải về 0. Số chuyển xuống phụ lục hay vào notes vẫn được tính là còn.
- Đọc lại bảng ý ở bước 1: mỗi slide mới còn nói đúng câu đó không?
- Chạy các câu hỏi của mục 8 trên bản mới.

## Bàn giao

- Đường dẫn file mới trước, kèm file gốc không bị đổi.
- Mỗi slide một dòng: Giữ, Sửa vỏ hay Làm lại, và vì sao.
- Những chỗ cần người dùng quyết: câu thông điệp mới thêm, số nghi sai, tiêu đề không thống nhất
  (ví dụ chỉ một slide có đánh số).
