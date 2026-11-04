# T070 [cross] Tổng hợp nghiên cứu T001–T069, phản biện và hướng đi

- **Agent / model:** Claude (Opus 5.5), vai trò trưởng nhóm, phiên desktop trên máy chủ dự án.
- **Ngày:** 2026-11-04. **Base:** `main` @ `d1ef906` (sau T069a).
- **Yêu cầu của chủ dự án:**
  1. tổng hợp toàn bộ nghiên cứu;
  2. phản biện những chỗ chưa ổn;
  3. dẫn đường để dự án vượt bậc so với các công cụ ArtCraft và ứng dụng văn phòng thông
     thường, trọng tâm là PPTX.

  Chủ dự án nêu ba điều:
  - chưa thấy dự án tạo ra "một cái nhìn tốt hơn hẳn";
  - các model bối rối khi phản hồi và việc mới bị giao trong cùng một phiên;
  - Morph có vẻ rất khó.
- **Lộ trình chi tiết** (tài liệu sống, agent làm theo): [docs/ROADMAP.md](../../docs/ROADMAP.md).
- **Bằng chứng mới trong task này:**
  - `preview/critic-499-vs-eye.jpg`;
  - `preview/t066-bespoke-deck.jpg`.

  Phần còn lại trích từ báo cáo các task, kèm đường dẫn.

## Tóm tắt

1. **Lõi kỹ thuật PPTX đã mạnh và nhiều phần đã có bằng chứng trong PowerPoint thật:**
   - viết timing native;
   - 198 preset;
   - ảnh chuyển động;
   - trigger bấm thật (T058);
   - Morph camera 3D (T064);
   - nhà máy hình native (T062).
2. **Thứ chưa có là "gu", và lab không đo được gu.** Critic chấm 4,99/5 cho deck có ô trống,
   tiêu đề bị cắt và chữ giữ chỗ (T068). Nó cũng chấm 4,99 điểm chuyển động cho deck mà chủ dự
   án gọi là "không có gu" (T066). Agent tối ưu con số chứ không tối ưu thứ chủ dự án nhìn thấy.
3. **Deck đẹp nhất (T066) là một script 524 dòng viết tay riêng,** không đi qua sản phẩm. Gu bị
   mắc kẹt trong script dùng một lần và không quay lại công cụ. Vì vậy agent yếu không thể lặp
   lại được kết quả.
4. **Morph khó vì cả lab đang nghĩ theo từng slide.** Morph thực chất là bài toán *danh tính
   vật thể giữa hai trạng thái*. Các quy luật đã tìm ra (`!!` name, ẩn vật thể có entrance,
   chung model part 3D) còn rời rạc, chưa thành bộ luật để công cụ tự áp dụng.
5. **Hướng đi gồm ba bước.**
   - (a) Đặt **mắt chủ dự án làm thước đo gốc**: bộ đề cố định và so sánh A/B; mọi điểm số máy
     phải hiệu chỉnh theo đó.
   - (b) **Biên dịch cảnh (scene compiler):** agent chỉ mô tả các trạng thái, công cụ tự sinh
     hiệu ứng và Morph.
   - (c) **Đưa gu vào sản phẩm** thành công thức có kiểm chứng, để model yếu cũng ra kết quả
     gần model mạnh.

## 1. Tổng hợp theo giai đoạn

| Giai đoạn | Task | Ai làm | Câu hỏi | Kết quả còn giá trị |
|---|---|---|---|---|
| **I. Học ngôn ngữ timing** (04–05/10) | T001–T018 | Codex | PowerPoint lưu chuyển động thế nào; viết được không; chạy được không? | Ma trận ngữ nghĩa timing, viết đúng click group, công thức data motion (chart theo series, KPI đếm số), QA native ban đầu. Nhiều writer cũ đã bị đóng băng. |
| **II. Đạo diễn cho deck có sẵn** (05/10) | T019–T023 | Claude cloud | Đọc deck có sẵn, giữ nguyên nội dung, thêm nhịp click theo lời nói? | Writer timing chuẩn duy nhất (T019); Motion Director v0.6; compound motion: assemble, spotlight, cycle, swap, travel, zoom-focus (T023). |
| **III. Tạo deck mới + tri thức** (07–19/10) | T024–T034 | Claude desktop/cloud, Argon | Vì sao ảnh không chuyển động; làm deck mới từ đầu; thế nào là đẹp? | Ken Burns cho ảnh và motion graphic intro (T024b); Slide Forge: spec JSON thành deck có QA (T025); ảnh/icon có giấy phép (T026); 198 preset harvest từ PowerPoint, Office design kit, corpus DNA (T027); Morph Studio với `!!`, staging, camera (T028); motion token (T029); theme từ màu thương hiệu OKLCH (T030); design system + critic (T034). |
| **IV. Mở rộng bề ngang** (31/10–03/11) | T035–T056 | Antigravity, OpenCode, Argon | Lab đa lĩnh vực: Word, Excel, vector, 3D, CAD, video | DeckCraft bridge; docx (HUST/VNU), xlsx (UserForm, dashboard); vector (T053/T056 iso); game 1 slide (T049) và điều hướng phi tuyến (T048b); theme engine (T043). Lõi PPTX đứng yên. |
| **V. Gate và kiểm chứng** (04/11 sáng) | T057–T065 | Claude (lead), OpenCode | Đóng các cổng kiểm chứng T057 đặt ra | Xem mục 2. Đây là đợt chất lượng nhất: đề bài hẹp, có điều kiện bác bỏ, đo trong PowerPoint thật. |
| **VI. Đạo diễn câu chuyện** (04/11 chiều) | T066–T069b | OpenCode, Antigravity | Deck triết học "tốt nhất có thể"; vì sao nó "không có gu"? | T066 có bản sắc thị giác tốt nhất từ trước đến nay nhưng là script viết tay. T067 audit đúng nguyên nhân: không có tài liệu đạo diễn trước layout. T068/T069b thêm Deck Director, narrative critic và speaker notes. T069a có 4 Morph trạng thái. |

## 2. Tài sản thật (bằng chứng PowerPoint, rung ≥ 5)

Đây là nền móng có thể xây tiếp mà không phải làm lại.

| Năng lực | Bằng chứng | Rung |
|---|---|---|
| Writer timing chuẩn, click group, after-previous, 198 preset | T019, T027 (PowerPoint đọc đúng EffectType), T029 (122 hiệu ứng) | 4–5 |
| Ảnh chuyển động (Ken Burns, float), accent motion graphic | Forge render bằng CreateVideo (T024b, T025) | 5 |
| Count-up an toàn khi in/PDF, thang chữ 6 cỡ, MOT-SETTLE được sửa | T063: PDF chỉ còn giá trị cuối; critic hết TYP-SIZES | 5 |
| Trigger tương tác bấm thật trong slideshow | T058: 25/25 bước, 9/9 cạnh điều hướng | 5b |
| Một writer tương tác duy nhất | T061: rebuild T048b byte-identical | 1 + 4 |
| **Morph camera 3D** | T064: Morph quét camera khi hai slide **dùng chung một model part**; nếu mỗi slide một bản GLB thì Morph rơi về fade có khoảng đen 0,4 s | 5 |
| Hình minh họa native, tách từng phần để animate | T062: 20/20 phần có tên, 21 hiệu ứng, 25 KB; thắng tuyến SVG (0/20) và GLB (0/20) | 4–5 |
| DeckCraft: ảnh tĩnh gần PowerPoint, nhưng Morph và round-trip thì không | T059: `render-transition` không phải Morph; `convert` mất 149 behaviour | 5 vs 2 |
| DeckCraft có player animation thật, thiếu lệnh headless | T060: prototype 151 dòng `render-animation`; motion path lệch ≤ 0,78%; preset chỉ 67/198 đúng | 2 vs 5 |

## 3. Tuyên bố chưa được chứng minh (đừng dùng làm nền)

- **"Narrative score 5,00", "overall 4,99" (T068, T069b).** Thang đo tự xây và tự chấm. Ảnh
  render cho thấy ngược lại (mục 4, P1).
- **"Two-Pass Choreography Architecture", "Split-Sentence Bridging", "Implicit Deictic
  Anchoring", "5 narrative laws" (T068).** Đây là tên gọi, chưa có thí nghiệm A/B nào cho thấy
  deck theo các luật này được người xem ưa hơn.
- **"Lifecycles … rung 4" (T068).** Thực chất đây là đếm XML, tức rung 1.
- **"T066 deck tốt nhất có thể".** Chủ dự án đã bác: chuyển động không có gu, ảnh xuất hiện
  cuối mà không có lý do, deck làm trước khi có kịch bản.
- **Mọi điểm critic trong mọi báo cáo** cho tới khi critic được hiệu chỉnh theo mắt chủ dự án
  (ROADMAP, T071).

## 4. Phản biện

### P1. Thước đo bão hòa: lab đang tối ưu thứ nó đo được, không phải thứ người xem thấy

- **Bằng chứng 1 (`preview/critic-499-vs-eye.jpg`).** Hai deck đạo diễn của T068/T069b được
  critic chấm overall **4,99** và narrative **5,00**. Ảnh render cho thấy:
  - thẻ lớn trống gần hết;
  - tiêu đề chạm mép, bị cắt ("…gắn kết hữu cơ");
  - chữ giữ chỗ lọt vào slide ("Luận điểm và Đột phá Bước 3", "…nguồn nhân lực 3");
  - style `editorial-crimson` khai báo trong `direction.json` không được áp dụng: slide ra
    theme tối mặc định.
- **Bằng chứng 2.** T066 bị chủ dự án gọi là "không có gu" nhưng có motion **4,99**. T067 đã
  đo: 93% phép kiểm motion là kiểm vi mô (thời lượng, độ tương phản, vùng an toàn). Không phép
  nào hỏi chuyển động có *lý do* hay không.
- **Bằng chứng 3.** Khi critic thêm chiều "narrative" (T069b), điểm của deck do chính tác giả
  làm tăng lên 5,00. Người xây thước và người được chấm là một (Gemini xây, Gemini review).
- **Kết luận.** Critic hữu ích để bắt lỗi kỹ thuật. Nó **không** phải thước đo chất lượng. Khi
  một báo cáo dùng điểm critic để nói "tốt hơn", đó là định luật Goodhart: thước đo trở thành
  mục tiêu thì không còn đo được nữa.

### P2. Gu nằm ngoài sản phẩm

- **Deck đẹp nhất lab từng có (T066)** là `build_deck.py` 524 dòng viết tay: tự đặt tọa độ, tự
  chọn hiệu ứng, tự xử lý ảnh (rembg, duotone, mặt nạ tròn). Không dòng nào đi qua Forge.
- **Sản phẩm (Forge)** có 14 layout cố định cộng heuristic của Director. Kết quả đúng kỹ thuật
  nhưng trông như template.
- **Deck Director (T068)** biên dịch *vào chính các layout đó*, nên thừa hưởng nguyên sự nhạt
  nhẽo, và còn làm mất style.
- **Hệ quả.** Mỗi lần chủ dự án muốn "đẹp nhất", agent phải viết script riêng. Phần gu học được
  không quay về công cụ, và agent tiếp theo phải làm lại từ đầu. Đây là lý do chính khiến chủ
  dự án "chưa thấy một cái nhìn tốt hơn hẳn": sản phẩm không tích lũy được gu.

### P3. Bộ biên dịch đoán bằng chuỗi ký tự và tự bịa nội dung

- **`deck_director.py` ánh xạ diễn viên sang vật thể bằng chuỗi con.** Ví dụ: id chứa `"arr"`,
  `"growth"` hoặc `"nrr"` thì được coi là thẻ KPI số 1, 2, 3. Cách này đúng cho đúng một deck
  mẫu và sai với deck tiếp theo.
- **Một agent đang vá tiếp kiểu này** ngay trong checkout của chủ dự án lúc viết báo cáo này
  (thay đổi chưa commit ở `scripts/deck_director.py`).
- **Khi thiếu nội dung, compiler tự điền giá trị bịa:**
  - `"100%"` cho KPI;
  - `"Bước hoàn thiện"` cho process;
  - `"Chỉ số 1"` cho nhãn.

  Việc này vi phạm luật của chính lab là "never invent figures". Lỗi đáng ra phải là một mã lỗi
  trả lại cho agent.

### P4. Thuật ngữ phồng lên nhanh hơn bằng chứng

- **Tên gọi lớn, kiểm chứng ít.** Nhiều báo cáo đặt tên lớn cho ý tưởng nhỏ ("architecture",
  "laws", "100% canonical", "100% working"), trong khi bằng chứng là unit test trên ví dụ do
  chính tác giả viết.
- **Gán sai rung bằng chứng:** đếm XML được ghi là rung 4; ảnh DeckCraft được đặt cạnh cột
  "verification".
- **Hệ quả.** Chủ dự án và agent sau khó phân biệt điều gì đã thật, điều gì mới là tên gọi.

### P5. Quy trình: tốc độ cao, kiểm soát thấp

- **Một ngày (04/11) có 12 task (T058–T069b)** và hầu hết được merge trong ngày.
  - Toàn bộ T058–T065 do một agent làm (OpenCode/DeepSeek). Cặp builder/critic khác họ model mà
    T057 đề ra không được tuân theo.
  - T068/T069b do Gemini viết và Gemini review.
- **Mã task trùng lần nữa:** T069a và T069b.
- **Phản hồi và việc mới bị giao trong cùng một phiên** (chủ dự án tự nhận ra). Agent vừa sửa
  theo nhận xét vừa xây cái mới, nên cùng một ngày sinh ra hai hướng chồng nhau:
  - T067 "VisualStyle/1";
  - T068 "Deck Director" có style riêng.

  Kết quả là lớp style bị bỏ rơi lần thứ hai: trước đó `theme_engine.py` của T043 cũng không
  được ai dùng.
- **Nhận xét đúng về đợt T058–T065.** Khi đề bài hẹp, có điều kiện bác bỏ và phải đo trong
  PowerPoint thật, cùng một model (DeepSeek) tạo ra nghiên cứu rất tốt: T058, T059, T060 và T064
  là những báo cáo chặt nhất của lab. **Vấn đề không nằm ở model yếu. Vấn đề là đề bài mơ hồ.**

### P6. Vì sao Morph khó, và vì sao nó không cần phải khó

**Morph không phải một hiệu ứng để chọn.** Nó là *hệ quả* của cách hai slide được dựng.
PowerPoint ghép vật thể ở slide A với vật thể ở slide B, rồi nội suy vị trí, kích thước, màu và
góc quay. Morph đẹp hay hỏng phụ thuộc hoàn toàn vào việc ghép đó.

Lab đã tìm ra một số luật ghép, nhưng chúng nằm rải rác:
- T028: tên `!!` ép hai vật thể ghép với nhau.
- T059: vật thể có entrance effect bị ẩn trong lúc Morph.
- T064: model 3D phải dùng chung một part; ghép theo part, không theo ảnh raster.
- T032: ghi nhận PowerPoint tự ghép nhầm các vật thể không liên quan (chưa kiểm chứng).

Agent thấy Morph khó vì ba lý do:
1. Agent nghĩ theo từng slide ("slide này có gì"), trong khi Morph đòi nghĩ theo **cảnh**: một
   tập vật thể bền vững, mỗi vật thể có nhiều trạng thái theo thời gian.
2. Không có bộ luật ghép được kiểm chứng có hệ thống, nên mỗi agent tự đoán.
3. Không có cách xem nhanh khung hình Morph thật. CreateVideo mất vài phút, còn DeckCraft vẽ
   sai (T059).

Ba lý do này đều giải được bằng công cụ, không cần model giỏi hơn. Agent chỉ cần mô tả "vật
thể X ở trạng thái 1 nằm đây, ở trạng thái 2 nằm kia". Bộ biên dịch cảnh tự đặt tên, chọn cách
dựng slide, chặn ghép nhầm và chọn Morph hay hiệu ứng trong slide (ROADMAP, chặng 2).

### P7. Bề ngang không hiện ra trong PPTX

docx, xlsx, vector, 3D, CAD và video tiêu tốn khoảng một nửa số task từ T035. Chỉ hai nhánh quay
về phục vụ PPTX: 3D (T055/T064) và hình native (T062). Phần còn lại có thể có giá trị riêng,
nhưng không làm deck đẹp hơn. Đề nghị tiếp tục đóng băng.

## 5. Nguyên nhân gốc (một đoạn)

Lab tối ưu những gì nó đo được, mà thứ nó đo được không phải thứ chủ dự án nhìn thấy. Trí tuệ
về gu nằm trong đầu agent mạnh và trong các script viết tay. Nó không nằm trong công cụ, dữ liệu
và cổng kiểm. Vì vậy:
- agent yếu không lặp lại được;
- điểm số tăng mà mắt không thấy khác;
- việc nào cũng phải bắt đầu lại.

Muốn vượt bậc thì phải đảo ngược điều đó:
- **Thước đo gốc là mắt người.** Thước máy chỉ dùng được khi đã dự đoán đúng mắt người.
- **Gu thành công thức trong công cụ.** Agent chỉ làm phần cần phán đoán: câu chuyện, chọn công
  thức, nội dung.

## 6. Hướng đi

Chi tiết, đề bài và tiêu chí nghiệm thu nằm trong [docs/ROADMAP.md](../../docs/ROADMAP.md).
Tóm tắt:

1. **Chặng 1: thước đo thật (T071–T074).** Bộ đề vàng cố định cho chủ dự án so sánh A/B. Cổng
   lỗi thị giác trên khung hình render. Máy xem chuyển động nhanh (DeckCraft `render-animation`
   hoặc ghi slideshow thật bằng harness T058). Bộ luật ghép Morph kiểm chứng bằng ma trận thí
   nghiệm.
2. **Chặng 2: Morph và cảnh (T075–T077).** `scene.json` gồm diễn viên và trạng thái, bộ biên dịch
   cảnh, thư viện 10 nước Morph có khung hình mẫu. Deck Director xuất ra cảnh thay vì đoán
   layout.
3. **Chặng 3: gu vào sản phẩm.**
   - Style preset và xử lý ảnh từ T066/T067.
   - Bộ dàn trang theo lưới thay cho 14 layout cố định.
   - Đánh giá chéo model: cùng đề bài, DeepSeek, Gemini và Claude dùng chung công cụ. Khoảng
     cách giữa các model chính là thước đo độ tốt của công cụ.
4. **Quy trình:**
   - phiên phản hồi tách khỏi phiên làm việc, có sổ phản hồi đánh số;
   - mỗi tuần một bản phát hành so A/B với tuần trước;
   - builder và critic phải khác họ model;
   - tối đa 3 task PPTX mở cùng lúc.

## Giới hạn của báo cáo này

- Tôi xem ảnh render và đọc báo cáo, mã nguồn, chưa xem video chuyển động của T066/T069a. Nhận
  xét về "gu chuyển động" dựa trên phản hồi của chủ dự án và phép đo của T067.
- Không đánh giá lại chất lượng các nhánh docx, xlsx và vector.
- Phần so sánh với Office/Copilot và các công cụ khác dựa trên hiểu biết chung đến giữa 2026,
  chưa tra cứu lại; cần một task nghiên cứu riêng nếu dùng để ra quyết định.
