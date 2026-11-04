# Trục kịch bản: định hướng phát triển

Tài liệu sống, viết lại khi trục thay đổi. Người viết: trưởng nhóm (T078, Claude, 2026-11-04).
Ví dụ vàng đầu tiên:
[experiments/T078-…/gold-script-triet-hoc-ch1.md](../experiments/T078-20261104-claude-script-track/gold-script-triet-hoc-ch1.md).

## Vì sao có trục riêng

Chủ dự án nhận xét: *"tư duy dựng chuyển động bị tác động rất lớn bởi kịch bản"*. Nhận xét này
đúng, và nó sửa một chỗ sai trong ROADMAP bản đầu. Bản đó coi kịch bản là phần "agent tự viết" để
đưa vào công cụ. Thực tế kịch bản là **nơi sinh ra chuyển động**:
- chuyển động là *động từ* của câu chuyện;
- Morph là việc *cùng một ý* đổi trạng thái;
- nhịp click là *chỗ ngắt* của lời nói.

Kịch bản yếu thì bộ biên dịch cảnh tốt đến đâu cũng chỉ biên dịch ra một deck yếu một cách chính
xác. Vì thế kịch bản là một trục nghiên cứu riêng, và nó **đi trước** bộ biên dịch cảnh (T075).

## Chẩn đoán: vì sao kịch bản do agent viết còn yếu

Chẩn đoán dựa trên `skills/deck-director/SKILL.md`, beat sheet T069a và các `direction.json` của
T068/T069b.

1. **Skill dạy biểu mẫu, không dạy cách nghĩ.**
   - Skill có: 5 trường brief, 9 "job", các luật cấm (`NAR-KARAOKE`, `NAR-CODA-TRAP`…) và trình
     kiểm tra.
   - Skill không có: cách tìm *người nghe đang tin gì*, cách tạo căng thẳng, cách biến đề mục giáo
     trình thành câu hỏi, cách chọn ẩn dụ.
   - Luật cấm cho biết đừng làm gì; chúng không chỉ ra làm gì.
2. **Không có ví dụ vàng.** Model yếu học tốt nhất bằng cách bắt chước một mẫu tốt có chú thích.
   Lab chưa có kịch bản mẫu nào được chủ dự án duyệt.
3. **Điểm xuất phát sai: đi từ đề mục giáo trình.**
   - Beat sheet T069a đi theo đúng thứ tự mục lục.
   - Lời nói phần lớn đọc lại định nghĩa ("Triết học là hệ thống tri thức…").
   - Khi điểm xuất phát là mục lục, chuyển động chỉ còn cách trang trí mục lục.
4. **Không có cầu nối từ câu chữ sang chuyển động.** Bảng "job → figure" của skill hiện tại
   trừu tượng (`arrive`, `join`, `build`…). Agent không biết câu nói nào thì gọi figure nào.
5. **Kịch bản không được người đọc trước khi dựng.** Agent viết kịch bản, dựng ngay, rồi để
   critic chấm. Chủ dự án chỉ thấy kịch bản qua deck đã dựng, tức là sau khi mọi công sức đã bỏ
   ra.
6. **Model yếu thật sự yếu ở phần này.** Viết kịch bản tốt cần hiểu người nghe, có sự đồng cảm
   và cảm giác về nhịp. Đó là phần phán đoán nhiều nhất trong cả quy trình. Không nên giả vờ rằng
   một biểu mẫu sẽ khiến DeepSeek viết như một biên kịch.

## Câu trả lời: model yếu làm được đến đâu, và cách giúp

Chủ dự án lo rằng model yếu không làm được phần này. Câu trả lời thẳng là **mỗi việc một cách**:

| Việc | Model yếu làm được? | Cách giúp |
|---|---|---|
| Hiểu ý đồ: người nghe, niềm tin đầu và cuối | **Kém nếu tự đoán; được nếu hỏi** | Phiếu phỏng vấn 5 câu, hỏi chủ dự án trước khi viết |
| Chọn khung kể | **Được, nếu chọn từ danh sách** | Thư viện 8 khung, mỗi khung có ví dụ vàng |
| Chọn ẩn dụ chủ đạo | **Yếu** | Gợi ý từ thư viện. Nếu không có ẩn dụ tốt thì để trống; không ép |
| Chia thành cảnh, mỗi cảnh một chuyển dịch | **Được, nếu có phiếu** | Phiếu cảnh 6 ô bắt buộc (như ví dụ vàng) |
| Viết lời nói tự nhiên | **Trung bình** | Ví dụ vàng, luật "ví dụ trước, định nghĩa sau", kiểm tra trùng chữ màn hình |
| Từ câu sang chuyển động | **Được, nếu có bảng** | **Bảng động từ → chuyển động** (bên dưới), gạch chân động từ rồi tra bảng |
| Đánh giá kịch bản hay hay dở | **Không đáng tin** | Chủ dự án hoặc model mạnh đọc bản chữ (2–5 phút) trước khi dựng |

Từ bảng trên ta có một nguyên tắc phân vai: **kịch bản là khoảng 5% công sức nhưng quyết định
phần lớn chất lượng.**
- Khi có model mạnh, model mạnh viết hoặc duyệt kịch bản. Model yếu làm phần dựng, kiểm và sửa,
  là những việc mà công cụ và cổng kiểm đã đỡ được.
- Khi không có model mạnh, model yếu viết theo phiếu cộng ví dụ vàng, rồi **chủ dự án duyệt bản
  chữ** trước khi dựng.

Thí nghiệm T079 sẽ đo xem cách "phiếu cộng ví dụ" thu hẹp khoảng cách được bao nhiêu. Nếu không
đủ, phân vai là câu trả lời chính thức, không phải tạm thời.

## Phương pháp 6 bước (bản nháp, sẽ thành skill ở T081)

1. **Hỏi.** Năm câu cho người đặt deck:
   - Ai nghe?
   - Họ đang tin hoặc cảm thấy gì về chủ đề?
   - Sau buổi họ phải nghĩ hoặc làm gì khác?
   - Một điều họ nhớ nếu quên hết?
   - Giọng: trang trọng, gần gũi hay hứng khởi?

   Không hỏi được thì ghi rõ là *giả định*.
2. **Ý đồ.** Gồm:
   - niềm tin đầu và niềm tin cuối;
   - câu xương sống (≤ 20 từ);
   - ẩn dụ chủ đạo (nếu có), từ đó ra **diễn viên bền vững** cho Morph;
   - khung kể (chọn từ thư viện).
3. **Chuỗi chuyển dịch.** Mỗi cảnh là *một* chuyển dịch "người nghe nghĩ A → nghĩ B". Đề mục giáo
   trình được biến thành câu hỏi người nghe thật sự có. Không có chuyển dịch thì không có cảnh.
4. **Phiếu cảnh** (6 ô bắt buộc):
   - chuyển dịch;
   - trên màn hình lúc mở;
   - lời nói, với `[CLICK]` đặt ở chữ bản lề;
   - động từ → chuyển động;
   - diễn viên Morph sang cảnh sau;
   - vì sao.
5. **Gạch chân động từ.** Lấy động từ chính của câu then chốt trong mỗi cảnh, tra bảng động từ để
   ra chuyển động.
   - Động từ "là / có" (tĩnh) thì không cần chuyển động mạnh. **Đừng trang trí.**
   - Dùng lại tối đa khoảng 6 kiểu chuyển động cho cả deck, để deck có một ngữ pháp.
6. **Đọc to và duyệt.**
   - Đọc to, đo thời lượng (khoảng 130 từ mỗi phút nói).
   - Kiểm tra máy: mọi cảnh có chuyển dịch; mọi click có động từ thuộc bảng; lời nói không đọc
     lại chữ trên màn hình; có callback mở và đóng.
   - **Gửi bản chữ cho chủ dự án hoặc model mạnh duyệt.** Chỉ dựng sau khi được duyệt.

## Thư viện khung kể (v0, cần ví dụ vàng cho từng khung ở T082)

| Khung | Dùng khi | Cấu trúc |
|---|---|---|
| Câu hỏi → công cụ → áp dụng ngược | Bài giảng nhập môn | Mở bằng lựa chọn của người nghe, đóng bằng việc họ tự trả lời lại (ví dụ vàng T078) |
| Bí ẩn | Bài giảng khoa học, lịch sử | Một hiện tượng khó hiểu, các giả thuyết bị loại dần, lời giải |
| Hiện tại → có thể (Duarte) | Thuyết phục, chiến lược | Đan xen "đang là" và "có thể là", kết bằng lời kêu gọi |
| Kim tự tháp (Minto) | Báo cáo lãnh đạo | Kết luận trước, ba lý do, bằng chứng |
| Vấn đề → giải pháp → bằng chứng | Pitch, đề xuất | Nỗi đau, giải pháp, số liệu, hành động |
| Trước → sau | Ra mắt sản phẩm, cải tiến | Thế giới trước, khoảnh khắc thay đổi, thế giới sau |
| Hành trình | Lịch sử, quy trình | Các chặng có mốc; camera đi dọc |
| So sánh để quyết định | Lựa chọn phương án | Tiêu chí trước, so cạnh nhau, khuyến nghị |

## Bảng động từ → chuyển động (v0, giả thuyết; T080 kiểm chứng bằng A/B)

| Động từ trong câu then chốt | Chuyển động | Trong slide hay Morph |
|---|---|---|
| là, có (tĩnh) | xuất hiện nhẹ, hoặc không cần | trong slide |
| soi, chú ý vào, tập trung | khung hoặc thấu kính tới, phần còn lại mờ | trong slide |
| gom, hệ thống hóa, tổng hợp | nhiều vật thể hội tụ, xếp hàng | trong slide hoặc Morph |
| tách, chia, phân loại | một khối tách đôi, đẩy về hai phía | Morph |
| quyết định, nặng hơn, áp đảo | một bên lớn lên, bên kia nhỏ hoặc mờ; cân nghiêng | trong slide |
| đối lập, so sánh | hai trạng thái cùng lúc, đối xứng | trong slide |
| nối, liên hệ | đường nối vẽ dần | trong slide |
| vận động, phát triển, chu trình | đi theo đường cong hoặc vòng; xoay chậm | trong slide |
| trở thành, kế thừa, chuyển hóa | **cùng một vật thể** đổi hình, chữ hoặc màu | **Morph** |
| lật ngược, đảo lại | xoay 180° hoặc lật | trong slide |
| hội tụ, cùng dẫn tới | các đường đi gặp nhau tại một điểm | trong slide |
| thống nhất, cấu thành, nền móng | các phần khóa vào nhau; phần nền nằm dưới; khung bao | Morph |
| đi qua thời gian, từ… đến… | camera trượt dọc dòng thời gian | **Morph** (camera) |
| đi sâu, phóng to chi tiết | camera zoom vào | **Morph** |
| nhưng, song (bản lề) | hoán đổi trọng lượng: vế trước lùi, vế sau tiến | trong slide hoặc Morph |
| quay lại, nhớ lại | lặp bố cục cảnh trước | Morph về đúng vị trí cũ |
| loại bỏ, phủ định | thu nhỏ, mờ hoặc gạch bỏ rồi ra | trong slide |
| nhấn một trong nhiều | các mục khác mờ đi (vòng đời "dim") | trong slide |

Bảng này nối trực tiếp với thư viện 10 nước Morph (T076). Mỗi dòng "Morph" ở trên phải có một
nước tương ứng, có khung hình PowerPoint.

## Đề bài giữ chỗ

| Mã | Đề bài | Người làm → phản biện | Điều kiện |
|---|---|---|---|
| T078 | Phương pháp + ví dụ vàng đầu tiên (Triết học chương 1) | Claude | **xong**, chờ chủ dự án duyệt |
| T079 | [pptx] Model yếu cộng phương pháp có viết được kịch bản tốt không? | OpenCode → Claude | sau khi chủ dự án duyệt T078 |
| T080 | [pptx] Kiểm chứng bảng động từ → chuyển động | OpenCode → Claude | song song T074; cần T073 |
| T081 | [pptx] Skill `script-writer` | Claude → OpenCode | sau khi chủ dự án duyệt T078 |
| T082 | [pptx] Ví dụ vàng 2–5 | Claude viết; chủ dự án duyệt; OpenCode thử dùng | sau T081 |

### T079: model yếu cộng phương pháp có viết được kịch bản tốt không?

- **Thiết kế:** 3 đề trong bộ đề vàng (bài giảng, báo cáo, pitch), 4 điều kiện:
  - DeepSeek không có phương pháp;
  - DeepSeek với phiếu cộng 2 ví dụ vàng;
  - Gemini với phiếu cộng 2 ví dụ vàng;
  - Claude không có phương pháp.
- **Chấm:** chủ dự án chấm A/B **mù, trên bản chữ**, không dựng slide (rẻ: khoảng 2 phút một
  cặp).
- **Câu hỏi:** phương pháp thu hẹp khoảng cách được bao nhiêu?
- **Bác bỏ nếu:** DeepSeek có phương pháp vẫn thua Claude không có phương pháp từ 70% số cặp trở
  lên. Khi đó phân vai (model mạnh viết hoặc duyệt kịch bản) trở thành quy định.

### T080: kiểm chứng bảng động từ → chuyển động

- **Thiết kế:** 12 câu then chốt rút từ các kịch bản. Mỗi câu dựng 2–3 phương án chuyển động: theo
  bảng, ngược bảng, trang trí phổ biến. Quay khung hình PowerPoint.
- **Chấm:** chủ dự án chọn phương án đúng ý nhất.
- **Kết quả:** giữ, sửa hoặc bỏ từng dòng của bảng; thêm động từ còn thiếu.

### T081: skill `script-writer`

- **Nội dung:** tách phần kịch bản khỏi `deck-director` thành skill riêng, ngắn, gồm:
  - phiếu phỏng vấn;
  - phiếu ý đồ;
  - phiếu cảnh;
  - thư viện khung;
  - bảng động từ;
  - 1–2 ví dụ vàng;
  - lệnh `check` cho các phép kiểm máy làm được.
- **Đầu ra:** `script.md` (cho người đọc) và một bản nháp `scene.json` (cho T075).
- **Nghiệm thu:** critic là OpenCode **dùng skill** viết một kịch bản cho đề mới. Chủ dự án chấm bản
  đó với ví dụ vàng.

### T082: ví dụ vàng 2–5

- **Đề:** báo cáo số liệu, pitch, quy trình, so sánh để quyết định. Mỗi đề một khung khác nhau.
- **Quy trình:** chỉ được vào thư viện khi chủ dự án duyệt. OpenCode thử viết theo từng mẫu để đo
  mẫu có dạy được không.

## Quan hệ với ROADMAP

```
T078 kịch bản mẫu ──► chủ dự án duyệt ──► T081 skill ──► T079 đo model yếu
                                     └──► T082 thêm ví dụ vàng
bảng động từ ──► T080 kiểm chứng ──► T076 thư viện nước Morph
kịch bản (script.md) ──► scene.json ──► T075 bộ biên dịch cảnh ──► deck
```

Kịch bản đi trước. Không đề bài nào ở chặng 2 dựng deck mới mà không có kịch bản đã được duyệt
dạng chữ.
