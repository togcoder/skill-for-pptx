# T096 [pptx] Theo một tài liệu mẫu; mốc chữ nhỏ theo khổ slide

Agent: Claude (Opus 5.5), trưởng nhóm. Ngày: 2026-11-09.

## Vì sao

Chủ dự án dùng skill cho một việc thật bên ngoài repo để thử sức và tìm lỗi. Việc đó là đổi theme QCC
(khổ 20 × 11,25 in) theo một báo cáo PDF 78 trang mà sếp gọi là form "chân phương": lấy biểu đồ và font
chữ của báo cáo, giữ nền của theme cũ. Bộ slide ra đời: 13 slide, chỉ một font, 7 cỡ chữ; PowerPoint mở
được; 0 con số không có nguồn. Bộ này nằm ngoài repo. Trong lúc làm, lộ ra ba điều:

1. **Mốc chữ nhỏ của `inventory` cố định 18 pt, không tính theo khổ slide.** Slide 20 × 11,25 in khi
   chiếu được thu lại cho vừa màn hình, nên chữ 18 pt trên slide đó hiện ra như chữ 12 pt trên slide
   13,33 × 7,5 in. Lệnh chỉ báo nhãn 13,5 pt, còn chữ nội dung 19,5 pt (tương đương 13 pt) thì lọt qua.
   `design_critic.py` (`TYP-SMALL`) mắc đúng lỗi này.
2. **Quy tắc "3–6 cỡ chữ" có tác dụng.** `inventory` đếm ra 21 cỡ chữ trên bản nháp đầu. Gom về một
   thang (18/22/26/32/50/64/120 px) còn 7 cỡ, và bộ slide trông gọn hơn rõ. Không phải sửa gì ở đây.
3. **Skill chưa dạy cách theo một tài liệu mẫu.** Trưởng nhóm phải tự viết mã đọc PDF để biết font thật
   (Helvetica Neue LT Pro, máy Windows không có) và các mã màu. Mắt không đọc ra được những thứ này.

## Đã sửa

**Đồ nghề** (`scripts/pptx_tools.py`, `scripts/design_critic.py`):

- `inventory`: mốc chữ nhỏ = 18 pt × chiều cao slide ÷ 7,5 in, nên slide 20 × 11,25 in có mốc 27 pt.
  Dòng đầu báo cáo ghi mốc khi khác 18. Slide có hơn 3 vật chữ nhỏ thì gom thành một dòng; nếu không,
  một bộ chữ nhỏ cho ra hàng trăm dòng (278 dòng trên bộ QCC). Cảnh báo của `scale` dùng cùng mốc này.
- `design_critic.py` `TYP-SMALL`: chấm cỡ chữ sau khi quy về slide cao 7,5 in.
- Lệnh mới **`sample DOC.pdf [--pages 5,11] [-o DIR]`**. Lệnh in ra:
  - font theo tỉ lệ số ký tự, và máy này có font đó không;
  - các cỡ chữ và màu chữ hay dùng;
  - màu các khối, tính theo diện tích;
  - ảnh ghép mọi trang (20 trang một tấm) và ảnh lớn các trang chọn.

  Lệnh cần PyMuPDF, thư viện mà repo đã dùng ở `chart_forge.py` và `document_forge.py`. Đây là phần
  mã cho việc chữ không làm được (D011): tên font trong file và mã màu chính xác.
- CI cài thêm `pymupdf` để test của `sample` thật sự chạy.

**Lời hướng dẫn:**

- `guides/2-nhan-dien.md`: thêm dòng "Một tài liệu mẫu để theo" vào bảng, và mục mới **"Khi có một tài
  liệu mẫu để theo"** gồm 7 bước:
  1. đọc mẫu bằng `sample`;
  2. ghi lại những gì lặp lại trên nhiều trang (đó là giọng của mẫu);
  3. hỏi lấy gì của mẫu, giữ gì của bộ đang có;
  4. thay font không có trên máy bằng font gần nhất có sẵn ở mọi máy;
  5. lấy tỉ lệ của bản in, không lấy cỡ chữ;
  6. màu số liệu theo quy ước;
  7. không chép (D010).
- `guides/4-chu-va-mau.md`: thang cỡ chữ viết cho slide cao 7,5 in; khổ khác thì nhân theo chiều cao.
- `guides/9-do-nghe.md`, `SKILL.md`: dòng cho `sample`; bước 3 của SKILL nhắc tới tài liệu mẫu.

## Bằng chứng

`preview/sample-and-inventory.txt` gồm hai phần:

- **`sample` chạy trên báo cáo 78 trang** (file giữ ở máy chủ dự án, không đưa vào repo). Kết quả:
  - Helvetica Neue LT Pro chiếm 100% số ký tự và không có trên máy;
  - cỡ chữ chính 8,5 pt;
  - màu chữ 231F20; màu xanh 0067AC.
  - Chạy mất khoảng 9 giây.
- **`inventory` chạy trên bộ theme 20 × 11,25 in** (giữ ngoài repo). Dòng đầu báo mốc 27 pt; chữ nhỏ
  được gom thành một dòng mỗi slide.

`pytest`: 3 test mới (15/15 trong `tests/test_pptx_tools.py`):

- mốc chữ nhỏ theo chiều cao (`inventory` và `design_critic`);
- `sample` đọc đúng font, cỡ chữ, màu chữ và màu khối của một file PDF dựng trong test.

Bậc bằng chứng: 1 (cấu trúc và lệnh chạy trên file thật). Bộ theme QCC v6 làm theo mục 2 mới chờ chủ
dự án và sếp chấm.

## Không làm

- Không bảng font thay bằng mã. Chọn font gần nhất là việc của người, theo vài dòng trong mục 2;
  `sample` chỉ báo font nào thiếu.
- Không tách độ đậm (Light, Medium, Bold) trong báo cáo của `sample`; ảnh các trang đã cho thấy điều đó.

## Việc tiếp theo

Khi người dùng đưa một tài liệu mẫu: chạy `sample`, xem ảnh các trang, rồi theo mục 2. Nếu sếp chấm
bộ QCC v6, ghi điểm vào `research/feedback/`.
