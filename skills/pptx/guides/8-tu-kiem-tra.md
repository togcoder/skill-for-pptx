# 8. Tự kiểm tra: mở ra xem rồi sửa

Bạn không được nói "xong" trước khi **nhìn thấy** từng slide. "Đã kiểm" là một danh sách: slide nào,
đã thấy gì, đã sửa gì. Một câu "đã kiểm, ổn" không có danh sách là chưa kiểm.

## Vòng xem và sửa

1. `python scripts/pptx_tools.py glance DECK.pptx`. Lệnh xuất ảnh từng slide bằng PowerPoint thật
   (`slide-NN.png`) và báo những lỗi người xem thấy ngay: chữ đè chữ, chữ không đọc được trên nền của nó
   (kể cả **ô bảng thật** và **biểu đồ**), chữ đặt lên ảnh rối (`text on picture`), chữ bị ảnh che, hai logo
   hoặc cùng một ảnh dán lặp lại, tràn khung, chữ quá nhỏ (kể cả trong **bảng** và **biểu đồ**), ký hiệu
   Wingdings/PUA vỡ font (`broken symbol`), chữ giữ chỗ còn sót (`draft text`), slide thiếu tiêu đề. Nếu
   biểu đồ xếp chồng có XML lỗi (`dLblPos='outEnd'`), lệnh báo ngay trước khi mở PowerPoint. Slide có lỗi
   có thêm ảnh `faults-NN.png` khoanh đỏ từng chỗ. Sửa hết các lỗi này trước.
   (Khi sửa một vài slide bằng `--slides 3,6`, `glance` vẫn đọc khung tiêu đề/logo của toàn bộ để không bỏ
   sót luật chồng shell; nhưng trước khi bàn giao cuối cùng luôn phải kiểm và mở toàn bộ deck.)
2. **Mở và nhìn ảnh của từng slide, ở cỡ lớn.** Ảnh ghép thu nhỏ (`look` → `sheet.jpg`) chỉ để xem nhịp cả
   bộ; ở cỡ đó hai logo chồng nhau hay một dòng chữ bị che trông vẫn ổn. Đã có bộ slide bị giao bốn lần
   với lỗi rõ như vậy vì agent chỉ nhìn ảnh ghép.
3. Trả lời bảng câu hỏi dưới đây cho từng slide. Sửa, rồi quay lại bước 1.
4. Tối đa ba vòng. Sau ba vòng còn chỗ chưa ổn thì **báo cho người dùng chỗ đó**, đừng tuyên bố đã
   đạt.

Lưu ý: ảnh `look` là slide **đã hiện đủ mọi thứ**. Nó không cho thấy lúc slide vừa mở, từng lần
bấm, hay giữa một cú Morph. Muốn thấy những lúc đó thì dùng `watch` (phần dưới).

## Xem chuyển động: `watch`

Sau khi ghi chuyển động, bạn phải **nhìn** nó chạy, như người ngồi dưới sẽ nhìn:

```
python scripts/pptx_tools.py watch DECK.pptx              # cả bộ, khoảng 2–4 giây mỗi slide
python scripts/pptx_tools.py watch DECK.pptx --slides 3,6 # chỉ vài slide vừa sửa
```

Lệnh chạy trình chiếu thật của PowerPoint, tự bấm, và chụp cho mỗi slide một dải ảnh
`slide-NN.jpg`: ba khung giữa cú Morph (25%, 50%, 75%) nếu slide vào bằng Morph, khung `open` lúc
slide vừa mở, rồi một khung sau mỗi lần bấm. Lần bấm nào chạy lâu hơn 2 giây (một mô phỏng, một
chuỗi hiệu ứng) có thêm ba khung giữa chừng. **Mở và nhìn từng dải ảnh**, trả lời:

- **Khung `open`:** slide vừa mở đã đứng được một mình chưa (có tiêu đề và khung chính), hay còn
  trống một nửa?
- **Mỗi lần bấm:** so với khung trước, cái gì vừa hiện? Mắt có biết nhìn vào đâu không? Thứ vừa hiện
  có đúng là thứ câu nói lúc đó cần không?
- **Lần bấm ghi `DEAD`** (lệnh in `NOTHING CHANGES`): người nói bấm mà màn hình không đổi gì. Bỏ lần
  bấm đó, hoặc tìm vì sao vật không hiện (vật rỗng, bị che, nằm ngoài slide).
- **Ba khung Morph:** có chữ cũ và chữ mới đè lên nhau thành "bóng ma" không? Có vật bay xuyên qua
  chữ hay qua vật khác không? Chỉ nhìn khung 50%, có hiểu **cái gì đang biến thành cái gì** không?
  Không hiểu thì đó là cú Morph gượng (mục 6, bốn câu hỏi).

Sửa rồi chạy lại `watch --slides` cho các slide vừa sửa. Chưa chạy `watch` và chưa nhìn dải ảnh thì
không được nói "chuyển động ổn".

Khi lệnh đang chạy, cửa sổ trình chiếu nằm gần hết ngoài mép phải màn hình (ló ra một dải mỏng).
Đừng thu nhỏ hay đóng nó.

**Trước khi ghi chuyển động, làm bước t=0:** tự trừ các vật trong kế hoạch bấm rồi trả lời "slide
còn đứng được một mình không?". Lỗi hay gặp nhất là slide mở ra chỉ có tiêu đề và một khung trống;
sửa bố cục lúc này rẻ hơn sửa sau khi đã ghi hiệu ứng. Ghi xong thì khung `open` của `watch` cho bạn
thấy đúng lúc đó, không phải đoán.

## Câu hỏi cho từng slide

- Nheo mắt nhìn: điểm nhấn có phải thứ quan trọng nhất không?
- Nếu chỉ nhìn khung hình đầy đủ như một poster, bố cục có cân và có một điểm
  nhấn không?
- Có chữ nào bị cắt, tràn khung, gãy giữa từ, hoặc sai dấu tiếng Việt không?
- Có chữ nội dung nào dưới 18 pt không? Có gì dưới 12 pt không?
- Có thẻ, khung hay ô nào rỗng không? Có chữ mẫu, chữ giữ chỗ nào sót lại không?
- Các khối có thẳng hàng không? Tiêu đề có ở cùng một chỗ với các slide khác không?
- Có một khối nhỏ treo trên nền trống không?
- Ảnh có bị méo, bị cắt mất chủ thể, hay quá nhỏ không?
- Chữ có đủ tương phản với nền không, nhất là chữ nhạt và chữ trên ảnh?
- Slide này có giống y hệt kiểu slide liền trước không?
- Có số liệu hay nhãn nào bạn tự nghĩ ra không?

## Câu hỏi cho cả bộ

- Chỉ đọc các tiêu đề, có hiểu câu chuyện không?
- Nhịp có xen kẽ giữa dày và thưa, sáng và tối không?
- Morph có đúng chỗ không, có quá 5 cái trong 15 slide không?
- Bỏ hết chuyển động, từng slide có đứng được một mình không?
- Cú Morph nào cần giải thích mới hiểu? Đó là cú gượng (xem guide 6).
- Mức chuyển động có vừa với phòng không? (xem bảng trong guide 6)
- Bìa có lần bấm nào không? (Bìa phải không có lần bấm nào.)

## Công cụ bắt lỗi

```
python scripts/design_critic.py DECK.pptx         # chữ tràn, chữ nhỏ, tương phản, mật độ
python scripts/morph_studio.py audit DECK.pptx    # lỗi Morph
python scripts/motion_script.py check script.md   # nếu có kịch bản: câu sáo rỗng, thiếu lần bấm
```

- Điểm số tổng của `design_critic` **không** nói slide đẹp. Chỉ đọc danh sách lỗi.
- `DEN-WORDS` (45 từ/slide) là ngưỡng cho slide kể chuyện; slide bảng/đối chiếu có thể vượt — ghi là
  đã biết, đừng cắt nội dung cho vừa số.
- `NAR-LIFECYCLE` chỉ có nghĩa khi deck có khai báo dim/exit; deck dựng bằng `pptx_tools` (chỉ
  entrance) sẽ bị cảnh báo — đó là giới hạn đồ nghề, không phải lỗi slide.
- Nếu máy thiếu font mà deck đang dùng, báo lỗi tràn chữ có thể sai. Khi đó tin vào ảnh `look` của
  PowerPoint.
- Lỗi do công cụ gây ra (công cụ tự thu chữ, tự thêm trang trí, dừng khi gặp giá trị 0) thì sửa trong
  file và ghi lại cho người dùng. Đừng lách bằng cách đổi nội dung.
- **Không tự viết script kiểm tra riêng** (regex đếm nhanh, script chỉ đo toạ độ khung rồi bỏ qua ảnh
  render) để thay `glance`, `compare`, hay `check`.
- **Fail-closed với subagent:** nếu có subagent phụ trách dựng hoặc soát slide, báo cáo "đạt / 0 lỗi" của
  subagent chỉ được tính là chưa kiểm tra cho tới khi chính bạn chạy `glance` và mở từng `slide-NN.png` xác
  nhận trực tiếp.
