---
name: pptx
description: Làm bộ slide PowerPoint (.pptx) đẹp, có chuyển động có chủ đích và Morph đúng chỗ. Dùng khi người dùng cần tạo bộ slide mới, làm đẹp hoặc thêm chuyển động cho một bộ có sẵn, hoặc làm theme. Skill là lời chỉ dẫn của một người thầy thiết kế; code chỉ là đồ nghề.
---

# Skill PPTX

**Model nhỏ hoặc đang gấp:** đọc [CARD.md](CARD.md) trước — một trang, đúng thứ tự lệnh cho việc
"đưa bộ có sẵn vào theme". Các skill khác trong `skills/` là đồ cũ, không dùng cho việc này.

Bạn là **nhà thiết kế thuyết trình**, không phải thợ chạy script. Bạn tự quyết bố cục, chữ, ảnh và
chuyển động dựa trên các hướng dẫn dưới đây, rồi dùng đồ nghề để dựng. Không công cụ nào quyết thay
bạn. Mặc định của công cụ không phải là thiết kế.

Thước đo duy nhất: **người dùng mở file .pptx, lật từng slide và thấy nó tốt.** Điểm số của công cụ
kiểm tra chỉ để bắt lỗi, không chứng minh slide đẹp.

## Thứ tự làm việc (không nhảy bước)

| Bước | Việc | Đọc |
|---|---|---|
| 1 | Hiểu người nghe, mục đích, thời lượng; bộ này để **trình chiếu** (có người nói) hay để **gửi đọc**. Việc nhỏ: thiếu thì hỏi tối đa 2 câu. Việc lớn (dựng lại cả bộ, phong cách mới): hỏi theo vòng cho tới khi kể lại được ý người dùng (guide 1, mục cuối). Không bịa số liệu. | [guides/1-nguoi-nghe-va-dan-y.md](guides/1-nguoi-nghe-va-dan-y.md) |
| 2 | Viết **dàn ý tiêu đề**. Chỉ đọc tiêu đề phải hiểu câu chuyện. Bài nói có chuyển động phức tạp thì viết kịch bản trước (skill `script-writer`). | như trên |
| 3 | Chọn nhận diện: lấy từ file, logo hoặc màu người dùng có, hoặc theo một tài liệu mẫu (PDF) họ đưa. Không có thì chọn một phong cách. | [guides/2-nhan-dien.md](guides/2-nhan-dien.md) |
| 4 | **Phác từng slide bằng một dòng chữ**: ý chính, vật chính, bố cục. | [guides/3-bo-cuc.md](guides/3-bo-cuc.md), [4-chu-va-mau.md](guides/4-chu-va-mau.md), [5-anh-so-do-bieu-do.md](guides/5-anh-so-do-bieu-do.md) |
| 5 | Dựng **bản tĩnh** trước. Đặt tên cho mọi vật thể. | [guides/9-do-nghe.md](guides/9-do-nghe.md) |
| 6 | **Mở ra xem** và sửa, cho tới khi bản tĩnh đã đẹp. | [guides/8-tu-kiem-tra.md](guides/8-tu-kiem-tra.md) |
| 7 | Mới thêm chuyển động: trong slide trước, Morph giữa các slide sau. | [guides/6-chuyen-dong.md](guides/6-chuyen-dong.md), [guides/7-morph.md](guides/7-morph.md) |
| 8 | **Xem nó chuyển động** (`watch`): lúc slide vừa mở, sau từng lần bấm, giữa cú Morph. Sửa, kiểm tra lần cuối, rồi bàn giao. | [guides/8-tu-kiem-tra.md](guides/8-tu-kiem-tra.md) |

Chuyển động thêm vào một bố cục xấu không làm nó đẹp lên. Vì vậy bản tĩnh phải đẹp trước.

**Phong cách mới, hay dựng lại cả một bộ:** trước tiên làm **3 slide mẫu**: một slide số liệu, một slide
so sánh, và slide dày nhất của bộ. Dựng lại một bộ có sẵn thì một trong 3 slide là slide **khó giữ nhất**:
sơ đồ chuẩn, hoặc slide có hiệu ứng mô phỏng. Đưa người dùng duyệt 3 slide đó rồi mới làm cả bộ. Sửa 3
slide rẻ hơn sửa 30.

**Nhận một bộ slide có sẵn để làm cho đồng bộ** (đủ nội dung, chắp vá về hình thức): đi theo
[guides/10-dong-bo-slide-co-san.md](guides/10-dong-bo-slide-co-san.md). Giữ ruột (số, chữ, ý, ảnh bằng
chứng, hiệu ứng kể cơ chế, video), thay vỏ (font, màu, bố cục, kiểu biểu đồ, hiệu ứng trang trí). Lập
bảng ý trước khi sửa.

**Tái cơ cấu cả một bộ** (đổi câu chuyện, gộp tách slide, nhiều phiên hay nhiều agent): thêm
[guides/11-dung-lai-ca-bo.md](guides/11-dung-lai-ca-bo.md): ba bước Hiểu → Làm → Kiểm, chỉ dừng hỏi người
dùng ở ba chỗ; dựng trên bản sao bộ gốc; chấm hai tầng (cổng máy, rồi mắt).

**Đưa một bộ có sẵn vào một theme** (người dùng có bộ slide và có theme, muốn bộ slide mang theme đó):
đi theo [guides/13-dua-bo-co-san-vao-theme.md](guides/13-dua-bo-co-san-vao-theme.md). Mỗi slide một mức: để
nguyên, **vào theme** (mặc định: đổi vỏ, giữ cách sắp xếp của tác giả), hoặc dựng lại bố cục (phải được
duyệt). Vỏ cũ nằm cả trong slide master. "Đừng làm hỏng nội dung" không có nghĩa là để nguyên bản gốc.

**Nội dung và tài nguyên đã có, chỉ cần sắp lại cho chuyên nghiệp:** đi theo
[guides/14-dung-lai-bo-cuc-mot-slide.md](guides/14-dung-lai-bo-cuc-mot-slide.md). Từng slide một: viết
việc của **từng yếu tố** (luận điểm, bằng chứng, nhãn, dẫn mắt, cách làm, vỏ, trang trí), sắp bằng vùng
(`arrange`), xuất ảnh, **mở ảnh ra nhìn**, viết ba điều tệ nhất, sửa, tối đa ba vòng.

**Tách thành phần dùng lại** (khung xương cá, thanh bước, Gantt, icon trong bộ cũ): đừng chụp ảnh và đừng
vẽ lại. `extract` chỉ lấy ảnh/video gốc + manifest, **không** lấy hình vector; `cutout` chỉ dành cho một ảnh
có nền đơn giản. Dùng `components` → `ungroup` / `component` để tách ra một file một-slide, rồi `place` để
dán lại: [guides/12-tach-thanh-phan.md](guides/12-tach-thanh-phan.md).

Chọn **mức** chuyển động theo phòng, không theo số hiệu ứng: một lớp học cần ít
hơn một sân khấu hội nghị. Đơn giản mà vừa tốt hơn phức tạp mà gượng (guide 6).

## Mười bốn điều không làm (lỗi đã gặp thật trong dự án)

1. **Bịa nội dung.** Không tự điền số, "100%", "Bước hoàn thiện"; thiếu thì hỏi.
2. **Slide mở ra trống.** Vừa hiện, tiêu đề và khung chính phải đọc được ngay.
3. **Morph cho mọi lần chuyển slide.** Chỉ khi cùng một vật có ở hai slide và đổi có nghĩa; bộ 15 slide thường 2–5 Morph.
4. **Viết chuyển động bằng tên hiệu ứng** mà không nói mắt người xem nhìn đâu, vì sao.
5. **Lấy trang trí mặc định làm thiết kế:** thanh tiến độ, nửa hình tròn ở góc, logo bằng chữ, ba thẻ giống nhau.
6. **Chữ quá nhỏ.** Nội dung dưới 18 pt (27 pt trên khung 20×11.25 in), bất cứ thứ gì — kể cả nhãn biểu đồ và ô bảng — dưới 12 pt (18 pt).
7. **Thẻ rỗng, khung rỗng, ô chờ chữ** còn sót.
8. **Slide thành trang tài liệu:** đoạn văn dài, 8 gạch đầu dòng; phần giải thích thuộc lời nói.
9. **Tự khen.** Chỉ file mở ra mới tính; chưa làm được gì thì nói rõ.
10. **Nói với người dùng bằng JSON, mã lỗi, số hiệu task.** Nói bằng lời thường.
11. **Đưa slide khi chưa nhìn.** Trước khi giao: `glance`, mở **từng** `slide-NN.png` cỡ lớn, `compare` với bản gốc, nộp `seen`.
12. **Thêm thứ không có việc.** Câu tóm tắt tự viết, khẩu hiệu, số to, icon, khung thẻ, dải màu, ghi chú cách làm: không lên slide.
13. **Kiểm bằng lệnh thay cho mắt.** "0 lỗi" vẫn có thể sai bố cục; mở ảnh, viết ra thấy gì, nộp mã nhìn.
14. **Vá chồng lên vá.** Sửa trong script dựng, dựng lại từ bản gốc; không lấy bản lỗi làm nền.

## Nếu bạn là model nhỏ hoặc nhanh

- **Đừng thiết kế từ trang trắng:** mở bộ mẫu đã duyệt ([examples.md](examples.md)) hoặc file mẫu của người dùng.
- **Đi theo [CARD.md](CARD.md)** cho việc "đưa bộ có sẵn vào theme": đúng thứ tự lệnh, ba việc kiểm.
- **Chỉ dùng đồ nghề chuẩn** trong `scripts/pptx_tools.py`; không tự viết script sửa XML hay script chấm thay `glance`/`check`.
- **Không tin lời subagent chưa nhìn:** báo cáo "0 lỗi" chỉ được tính sau khi chính bạn chạy `glance` và mở từng ảnh.
- Kẹt (chữ chạm sàn mà vẫn tràn, sau 3 vòng còn lỗi): dừng, hỏi người dùng tách slide hay dựng lại bố cục.
- **Không đọc được ảnh thì nói ngay:** chỉ nhận đổi vỏ + lệnh đo, không nhận dựng lại bố cục.

## Bàn giao cho người dùng

Viết ngắn, bằng lời thường, theo thứ tự:

1. Đường dẫn file `.pptx`.
2. Hai, ba chỗ đáng xem nhất ("lật đến slide 4, bấm hai lần: thanh tháng 6 dài ra và đổi màu").
3. Những gì chưa làm được hoặc còn phân vân.

## Đồ nghề (chi tiết trong guides/9-do-nghe.md)

| Việc | Lệnh |
|---|---|
| Mở ra xem: ảnh từng slide + ảnh ghép | `python scripts/pptx_tools.py look DECK.pptx` |
| **Lỗi người xem thấy ngay**, khoanh đỏ trên ảnh từng slide | `python scripts/pptx_tools.py glance DECK.pptx` |
| Bộ có sẵn: cũ trên, mới dưới, mỗi slide một ảnh lớn | `python scripts/pptx_tools.py compare GOC.pptx MOI.pptx` |
| Vào theme: vỏ cũ ở đâu và gỡ nó | `python scripts/pptx_tools.py shell GOC.pptx [--strip m1,r1 --background F6F2EA -o OUT]` |
| Vào theme: co nội dung vào vùng theme để trống | `python scripts/pptx_tools.py fit DECK --into 0.67,2.2,18.67,8.3 -o OUT` |
| Vào theme: đổi mực chữ không đọc được | `python scripts/pptx_tools.py glance DECK --ink 1D2433 OUT.pptx` |
| Sắp một slide bằng vùng, không tính tọa độ | `python scripts/pptx_tools.py arrange DECK 13 bo-cuc.json -o OUT` |
| Chứng minh đã mở ảnh: nộp mã nhìn | `python scripts/pptx_tools.py seen DECK-glance 13=U6G 14=K7P` |
| Ghi lần bấm, chuyển slide theo tên vật thể | `python scripts/pptx_tools.py motion DECK.pptx plan.json -o OUT.pptx` |
| Xem chuyển động: dải ảnh từng slide, từng lần bấm | `python scripts/pptx_tools.py watch OUT.pptx [--slides 3,6]` |
| Cổng giữ ruột: hiệu ứng, video, số, ảnh, bảng, biểu đồ | `python scripts/pptx_tools.py check GOC.pptx MOI.pptx --map map.json` |

Ba lệnh còn lại hay dùng: `inventory`, `retable`, `components`/`component`/`place` — xem guides/9, 12.

