# 14. Dựng lại bố cục một slide: nhìn, nghĩa, sắp

Dùng mục này khi **nội dung và tài nguyên đã có đủ** (ảnh, số, biểu đồ, câu chữ của slide gốc) và việc
của bạn chỉ là **sắp lại cho chuyên nghiệp** trong một theme. Đây là mức 2 của mục 13. Bạn không viết thêm
nội dung, không vẽ thêm hình.

## Vì sao việc "chỉ sắp lại" mà vẫn hỏng

1. **Gộp ba việc làm một.** Hiểu slide nói gì, quyết định cái gì to cái gì nhỏ, và đặt tọa độ là ba việc.
   Agent viết thẳng một script tọa độ cho cả bộ, nên cả ba đều làm dở.
2. **Đặt tọa độ mà không nhìn.** Người thiết kế đặt một vật, nhìn, rồi chỉnh. Agent viết 300 con số rồi
   mới xuất ảnh một lần ở cuối, hoặc không xuất.
3. **Kiểm bằng lệnh đếm thay cho mắt.** Lệnh đo nói "0 lỗi" trong khi slide có chú thích đè lên ảnh, dải
   trống vô nghĩa, ảnh phụ to hơn ảnh chính. Những thứ đó chỉ mắt mới thấy.
4. **Coi theme là đồ để thêm vào.** Theme là luật: vùng nội dung, lưới, thang cỡ chữ, vai của từng màu.
   Agent thêm thẻ, dải màu, icon, số to, câu tóm tắt "cho giống theme", và các thứ đó tranh nhau với nội
   dung.

## Luật gốc: mỗi yếu tố trên slide có một việc

Trước khi sắp, viết **sổ vai trò** của slide: liệt kê mọi yếu tố, mỗi yếu tố đúng một việc.

| Việc | Là gì | Trên slide |
|---|---|---|
| **Luận điểm** | Câu người xem phải mang về. Mỗi slide một câu. | Gần tiêu đề, chữ rõ, đậm |
| **Bằng chứng** | Thứ làm người xem tin luận điểm: ảnh hiện trường, biểu đồ, bảng, con số | To nhất, chiếm phần lớn slide |
| **Nhãn** | Chữ nói một phần của bằng chứng là gì | Dính vào thứ nó gọi tên, nhỏ hơn luận điểm |
| **Dẫn mắt** | Mũi tên, vòng khoanh, màu nhấn: chỉ chỗ phải nhìn | Nằm trên bằng chứng, đi cùng nó khi dời |
| **Cách làm** | Dụng cụ, máy, người đã làm: nói bằng chứng có từ đâu | Nhỏ, ở rìa |
| **Vỏ** | Thanh bước, logo, tiêu đề, chân trang của theme | Đúng chỗ theme quy định, không đổi |
| **Trang trí** | Hình mờ, vệt sáng của theme | Phía sau, không nằm dưới nội dung |

Ba phép thử cho từng yếu tố:

- **Bỏ nó đi, người xem có mất gì không?** Không mất thì nó không có việc. Yếu tố của **bản gốc** không có
  việc: hỏi người dùng trước khi bỏ. Yếu tố **bạn định thêm** không có việc: không thêm.
- **Có hai thứ làm cùng một việc không?** Tiêu đề và một gạch đầu dòng cùng chữ; hai câu kết luận; hai
  logo. Giữ một.
- **Có hai thứ tranh nhau không?** Hai vật cùng to, cùng đậm; ảnh nội dung nằm đè lên hình trang trí; chữ
  phụ to hơn chữ chính. Slide chỉ có một thứ được to nhất.

Những thứ agent hay tự thêm và **không được thêm**: câu tóm tắt do mình viết, khẩu hiệu, số to "cho có
điểm nhấn", icon minh họa, khung thẻ quanh một vật đứng một mình, dải màu, dòng ghi chú về cách mình làm
("biểu đồ giữ từ bản gốc"). Không có trong bản gốc và không ai yêu cầu thì không lên slide.

## Bảy bước cho một slide

Làm **từng slide một**. Xong một slide mới sang slide khác.

1. **Nhìn slide gốc** (ảnh cỡ lớn). Viết một câu: *xem xong slide này, người ta phải nhớ gì?* Câu đó
   thường đã có sẵn trên slide (dòng kết luận). Dùng chữ của tác giả.
2. **Viết sổ vai trò.** Mỗi vật thể của slide một dòng: tên, việc của nó. Tên lấy từ `components` hoặc
   `shell`. Vật nào đi cùng nhau (ảnh và các mũi tên vẽ trên nó) thì ghi thành một **khối**.
3. **Xếp hạng.** Bằng chứng chính là gì: nó được phần lớn diện tích. Luận điểm đứng ngay dưới tiêu đề hoặc
   ngay dưới bằng chứng. Cách làm và nguồn thì nhỏ, ở rìa.
4. **Chọn dáng theo loại ý, viết bố cục bằng vùng.** Không tính tọa độ.

   | Slide nói | Dáng |
   |---|---|
   | Một phát hiện, có ảnh làm chứng | Luận điểm một dòng; bằng chứng tràn bề ngang; cách làm nhỏ ở góc |
   | Trước và sau, hai phương án | Hai cột bằng nhau, cùng cỡ ảnh, nhãn cùng chỗ; kết luận một dòng ở dưới |
   | Số liệu và một nhận định | Biểu đồ chiếm 2/3; nhận định và con số chính ở 1/3 còn lại |
   | Quy trình, các bước | Một hàng ngang theo thứ tự, các bước bằng nhau |
   | Bảng tra cứu | Bảng tràn vùng nội dung; không thêm gì bên cạnh |

   ```json
   {"in": [0.67, 2.25, 18.67, 8.25], "gap": 0.25, "col": [
     {"item": "Ket luan", "weight": 0.9},
     {"block": ["Anh thao", "Vong do", "Mui ten", "Anh phong to"], "weight": 6},
     {"row": [{"block": ["Anh dao cat", "Chu dao cat"]}, "Nhom kinh hien vi", {"weight": 5}], "weight": 1.9}]}
   ```
   ```
   python scripts/pptx_tools.py arrange deck.pptx 13 bo-cuc.json -o deck2.pptx
   ```
   `in` là vùng nội dung của theme (inch). `col` xếp chồng, `row` xếp ngang, `weight` là phần chia. `block`
   là các vật đi cùng nhau, giữ nguyên cách sắp bên trong. `{"weight": 5}` đứng một mình là ô để trống có
   chủ ý. Ảnh và khối được co vừa ô mà không méo; chữ trong khối không bao giờ bị phóng to; ô chữ lấy bề
   ngang của ô và giữ cỡ chữ.
5. **Xuất ảnh slide đó và mở ra nhìn**: `glance deck2.pptx --slides 13`, rồi mở `slide-13.png`. Viết ra
   **ba điều tệ nhất** bạn thấy, bằng lời (phần "Nhìn là nhìn gì" bên dưới). Không thấy gì để viết nghĩa là
   chưa nhìn.
6. **Sửa bố cục, xuất lại, nhìn lại.** Tối đa ba vòng. Sau ba vòng còn chỗ chưa ổn thì ghi lại cho người
   dùng.
7. **Đặt cạnh slide gốc** (`compare`): slide mới có mất vật nào, chữ nào của bản gốc không? Có thứ gì không
   có trong bản gốc không?

## Nhìn là nhìn gì

Lệnh đo (`glance`) chỉ là sàn. Khi mở ảnh, tự hỏi theo thứ tự:

1. **Mắt rơi vào đâu trước?** Có phải bằng chứng chính không? Nếu rơi vào logo, vào một khung màu, vào ảnh
   phụ: thứ bậc sai.
2. **Trong ba giây có đọc ra luận điểm không?**
3. **Chỗ trống nào không có lý do?** Một dải trống giữa hai khối, một nửa slide trắng trong khi ảnh chính
   bé: bằng chứng chưa được cho đủ chỗ.
4. **Có gì đè lên nhau, chạm nhau, cắt qua nhau không?** Chú thích đè ảnh bên cạnh, chữ cắt qua vạch chân
   trang, ảnh nằm trên hình trang trí.
5. **Thứ phụ có to hơn thứ chính không?** Chú thích to hơn kết luận, ảnh dụng cụ to bằng ảnh bằng chứng.
6. **Các mép có thẳng hàng không?** Mép trái của các khối, mép trên của hai ảnh cạnh nhau.
7. **Có thứ gì bạn không gọi được tên việc của nó không?** Bỏ.

## "Đã nhìn" phải chứng minh được

- Mọi ảnh `glance` và `compare` xuất ra đều có một **mã nhìn** ba ký tự ở dải dưới ảnh. Mã chỉ có trong
  ảnh. Sau khi mở ảnh:
  ```
  python scripts/pptx_tools.py seen deck2-glance 13=U6G 14=K7P
  ```
  Dán kết quả của lệnh vào bàn giao. Slide nào chưa có mã đúng là slide chưa được mở ra nhìn.
- Mỗi slide một dòng **"đã thấy gì"**: ba điều tệ nhất ở vòng đầu, đã sửa gì, còn gì.
- **Bạn không đọc được ảnh** (model không có mắt, hoặc công cụ không cho mở ảnh): nói ngay với người dùng,
  ở câu đầu tiên. Khi đó bạn chỉ làm được mức 1 của mục 13 và các lệnh đo. Không nhận việc dựng lại bố
  cục, và không viết "đã kiểm".

## Ví dụ thật: một slide, ba vòng

Slide gốc: tiêu đề nhỏ dạng gạch đầu dòng "Teardown SPK"; hai ảnh lớn (ảnh tháo loa có vòng xanh, vòng đỏ
và mũi tên; ảnh phóng to chỗ lỗi); hai ảnh dụng cụ nhỏ có chú thích; một dòng "After teardown SPK we found
glue between Frame & Rearcover not fully".

Sổ vai trò: dòng "After teardown…" là **luận điểm**. Hai ảnh lớn cùng vòng và mũi tên là **bằng chứng**,
một khối. Hai ảnh dụng cụ là **cách làm**. Gạch đầu dòng "Teardown SPK" là tiêu đề của tác giả: chữ đó
thành tiêu đề của theme, gạch đầu dòng bỏ vì trùng việc.

| Vòng | Bố cục | `glance` | Mắt thấy |
|---|---|---|---|
| 1 | Luận điểm trên; bằng chứng bên trái, dụng cụ thành cột bên phải | 0 lỗi | Dải trống trên và dưới bằng chứng (bị cột dụng cụ ép hẹp); chú thích "Ultrasonic cutter" đè lên ảnh kính hiển vi; ảnh dụng cụ và chữ của nó bị phóng to hơn mức của thứ phụ |
| 2 | Bằng chứng tràn bề ngang; dụng cụ nhỏ ở góc dưới phải | 0 lỗi | Chú thích xuống hai dòng và cắt qua vạch chân trang; ảnh dụng cụ nằm đè lên hình xe mờ của theme |
| 3 | Dụng cụ sang góc dưới trái (nền trống); chú thích một dòng | 0 lỗi | Sạch. Dừng. |

Ba vòng, năm lỗi, lệnh đo báo "0 lỗi" cả ba lần. Không vật nào của slide gốc bị mất; không vật nào được
thêm.

## Làm cả bộ

1. Cả bộ vào theme ở mức 1 trước (mục 13). Người dùng có ngay một bộ dùng được.
2. Người dùng chỉ ra slide nào cần dựng lại, hoặc bạn đề nghị danh sách và hỏi.
3. Làm **2–3 slide mẫu** theo mục này, đưa người dùng duyệt cùng cặp cũ/mới.
4. Làm tiếp từng đợt không quá 5 slide. Mỗi đợt: bảy bước cho từng slide, rồi `seen`, rồi giao.
5. Mỗi lời chê ghi vào sổ sửa (mục 1); sửa trong script dựng; không vá file kết quả (mục 13).
