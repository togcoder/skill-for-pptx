# 8. Tự kiểm tra: mở ra xem rồi sửa

Bạn không được nói "xong" trước khi **nhìn thấy** từng slide.

## Vòng xem và sửa

1. `python scripts/pptx_tools.py look DECK.pptx`. Lệnh này xuất ảnh từng slide bằng PowerPoint thật,
   cộng một tấm ảnh ghép `sheet.jpg`.
2. **Mở và nhìn** `sheet.jpg` (đọc file ảnh). Slide nào đáng ngờ thì mở ảnh riêng của slide đó.
3. Trả lời bảng câu hỏi dưới đây cho từng slide. Sửa, rồi quay lại bước 1.
4. Tối đa ba vòng. Sau ba vòng còn chỗ chưa ổn thì **báo cho người dùng chỗ đó**, đừng tuyên bố đã
   đạt.

Lưu ý: ảnh xuất ra là slide **đã hiện đủ mọi thứ**. Để kiểm tra lúc slide vừa mở, hãy tự lấy danh
sách vật thể của slide trừ đi những vật nằm trong các lần bấm, rồi xem phần còn lại có đứng được một
mình không.

**Trước khi ghi chuyển động, làm bước t=0:** tự trừ các vật trong kế hoạch bấm rồi trả lời "slide
còn đứng được một mình không?". Lỗi hay gặp nhất là slide mở ra chỉ có tiêu đề và một khung trống;
sửa bố cục lúc này rẻ hơn sửa sau khi đã ghi hiệu ứng.

## Câu hỏi cho từng slide

- Nheo mắt nhìn: điểm nhấn có phải thứ quan trọng nhất không?
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
