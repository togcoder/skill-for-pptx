# Kịch bản Mẫu Vàng: Pitch Deck Gọi Vốn Series A ($12M)
## Aether Cognition — The Autonomous Cognitive OS for Enterprise Work

- **Tác giả:** Antigravity (Gemini 2.5 Pro), thực hiện theo chuẩn `script-writer` v1.1 (T081/T082), 2026-11-05.
- **Tiêu chuẩn Kiến trúc:** Thiết kế theo quy chuẩn **State-to-State Morph & Spatial Pacing** (tuân thủ D009/D010, ma trận T074 M-01..M-11, và kỷ luật Single Focal Velocity).
- **Trạng thái:** Bản chữ tái cấu trúc toàn diện, gửi Argon phản biện và chấm đạt trước khi trình Chủ dự án.

---

## Phần 0. Ý đồ (Intent Architecture)

| Ô | Nội dung |
|---|---|
| **Người nghe** | Các General Partners tại các quỹ đầu tư mạo hiểm hàng đầu (Top-tier VCs). Họ nghe hàng chục bài pitch mỗi tháng, cực kỳ hoài nghi các lời hứa viển vông về AI, dị ứng với biểu đồ hockey-stick không có cơ sở, và luôn cảnh giác trước nguy cơ bị Microsoft/Google đè bẹp. |
| **Họ đang tin** | "Lại thêm một startup làm vỏ bọc (wrapper) cho OpenAI; công ty này sẽ bị Microsoft Copilot nghiền nát khi họ cập nhật tính năng mới." |
| **Sau buổi họ phải tin** | "Aether không phải chatbot mà là hệ điều hành nhận thức tự hành; họ sở hữu rào cản độc quyền về dữ liệu quy trình và đã chứng minh bằng 4.2 triệu USD ARR thực tế." |
| **Câu xương sống (≤ 20 từ)** | Aether thay thế phần mềm rời rạc bằng hệ điều hành nhận thức tự hành cho doanh nghiệp. |
| **Ẩn dụ chủ đạo** | **Bánh đà nhận thức 3 vòng (3-Ring Cognitive Flywheel)**: Ba vòng đồng tâm khép kín gồm Vòng Quan sát (`!!ring_obs`), Vòng Suy luận (`!!ring_reason`), và Vòng Thực thi chuẩn xác (`!!ring_exec`). Bánh đà này biến chuyển xuyên suốt toàn bộ deck — từ mở màn, qua khủng hoảng, tái cấu trúc giải pháp, và hóa thân thành 3 trụ cột phân bổ vốn. |
| **Diễn viên bền vững (cho Morph)** | Ba vòng nhận thức: `!!ring_obs` (ngoài, xanh lơ `#06B6D4`), `!!ring_reason` (giữa, tím `#8B5CF6`), `!!ring_exec` (lõi, vàng kim `#EAB308` → xanh lục `#10B981`); cùng các vật thể định danh: `!!silos_matrix` (lưới 130 SaaS), `!!metric_arr` (cột $4.2M ARR), `!!card_nrr` (thẻ 148% NRR), `!!col_gpu` (cột chi phí GPU), `!!col_margin` (cột 82% margin), `!!card_models` (khối model nền tảng), `!!card_graph` (khối đồ thị quy trình độc quyền), `!!ask_card` (khối $12M Series A). |
| **Khung kể** | **Nỗi đau cấu trúc → Xung đột bản chất (Vì sao chatbot thất bại) → Ẩn dụ giải pháp (Bánh đà 3 vòng) → Minh chứng số liệu → Đơn vị kinh tế → Hào lũy độc quyền → Kêu gọi đầu tư.** |
| **Thời lượng** | 8–10 phút, 8 cảnh (12 slide trạng thái Morph), 14 click. |
| **Giọng** | Sắc bén, đối thoại ngang hàng, đi thẳng vào cơ chế nguyên tử và số liệu kiểm chứng; không dùng buzzword ca tụng viển vông. |

---

## Cảnh 1. Mở màn & Cú đặt cược vào cấu trúc

- **Chuyển dịch:** "Lại một startup AI đến xin tiền" → "Họ đang chỉ ra một điểm gãy cấu trúc của toàn ngành phần mềm."
- **Trên màn hình lúc mở:**
  - Ba vòng tròn đồng tâm đặt tĩnh tại trung tâm màn hình:
    - `!!ring_obs`: Vòng ngoài cùng `(x=0.38, y=0.18, w=0.24, h=0.24)`, viền xanh lơ `#06B6D4` mảnh 1.5pt, nền rỗng.
    - `!!ring_reason`: Vòng ở giữa `(x=0.41, y=0.21, w=0.18, h=0.18)`, viền tím `#8B5CF6` mảnh 1.5pt, nền rỗng.
    - `!!ring_exec`: Vòng lõi `(x=0.44, y=0.24, w=0.12, h=0.12)`, viền vàng kim `#EAB308` mảnh 2.0pt, nền rỗng.
  - Tiêu đề chính `AETHER COGNITION` (font Sans Bold, 44pt, màu trắng `#FFFFFF`) tại `(x=0.20, y=0.52, w=0.60, h=0.10)`.
  - Phụ đề: *"The Autonomous Cognitive OS for Enterprise Work"* tại `(x=0.25, y=0.65, w=0.50, h=0.06)` ở trạng thái ẩn (`opacity: 0.00`).
- **Lời nói:**
  > Thưa các anh chị, trong suốt hai mươi năm qua, toàn bộ ngành công nghệ đã hứa với các tập đoàn rằng: cứ mua thêm phần mềm thì năng suất sẽ tự động tăng lên. **[CLICK]** Nhưng thực tế hôm nay lại hoàn toàn ngược lại.
- **Động từ → chuyển động:**
  - *soi* → Tại Click 1:
    - **Tiêu điểm duy nhất:** Dòng phụ đề chuyển từ `opacity: 0.00` → `1.00`, màu vàng kim nhạt `#FDE047` (`duration: 400ms`), xác lập định vị *"Hệ điều hành nhận thức tự hành"*.
    - Ba vòng `!!ring_obs`, `!!ring_reason`, `!!ring_exec` đồng loạt phát sáng viền nhẹ một nhịp (`duration: 500ms`, không đổi tọa độ), báo hiệu cỗ máy trung tâm bắt đầu kích hoạt.
- **Vì sao:** Đi thẳng vào mâu thuẫn lớn nhất của ngành phần mềm doanh nghiệp, không chào hỏi rườm rà.

---

## Cảnh 2. Nỗi đau thực tế: Khủng hoảng 130 công cụ SaaS

- **Chuyển dịch:** "Doanh nghiệp chỉ cần đào tạo nhân viên dùng tool tốt hơn" → "Vấn đề nằm ở cấu trúc: con người đang phải làm keo dán thủ công giữa 130 hệ thống."
- **Morph từ cảnh 1:**
  - Ba diễn viên độc lập `!!ring_obs`, `!!ring_reason`, `!!ring_exec` đồng tâm cùng trượt mượt mà theo phương chéo lên góc trên bên trái màn hình:
    - `!!ring_obs` định vị tại `(x=0.06, y=0.06, w=0.10, h=0.10)`.
    - `!!ring_reason` định vị tại `(x=0.07, y=0.07, w=0.08, h=0.08)`.
    - `!!ring_exec` định vị tại `(x=0.08, y=0.08, w=0.06, h=0.06)`.
    - Cả 3 vòng giảm độ mờ xuống `opacity: 0.40` (`morph: 800ms`), đóng vai trò mỏ neo nhận thức nền.
- **Trên màn hình lúc mở:**
  - Ma trận `!!silos_matrix` gồm 130 ô vuông nhỏ xếp thành lưới 13 hàng × 10 cột tại `(x=0.15, y=0.22, w=0.70, h=0.62)`. Toàn bộ 130 ô có màu xám chì `#334155` (`opacity: 0.35`).
- **Lời nói:**
  > Một tập đoàn quy mô trung bình hiện nay phải duy trì tới 130 công cụ SaaS độc lập. Hàng nghìn nhân viên tri thức không còn thời gian để sáng tạo, **[CLICK]** mà mất tới 4.2 giờ mỗi ngày chỉ để copy paste dữ liệu thủ công giữa các ô cửa sổ. Doanh nghiệp không hề thiếu công cụ; **[CLICK]** thứ họ thiếu là một bộ não trung tâm để vận hành đồng bộ các công cụ đó.
- **Động từ → chuyển động:**
  - *nghiêng về* →
    - **Click 1 (Làm nổi bật tổn thất):** 50 ô ngẫu nhiên trong `!!silos_matrix` chuyển viền sang đỏ cảnh báo `#EF4444` (`duration: 300ms`). Tại trung tâm lưới `(x=0.35, y=0.40, w=0.30, h=0.22)` xuất hiện thẻ tổn thất `!!card_loss` (`opacity: 0.00` → `1.00`, `duration: 400ms`) với con số đỏ lớn **4.2 Giờ/Ngày** và phụ đề *"Copy-paste thủ công giữa 130 ứng dụng"*.
    - **Click 2 (Khoảng trống cấu trúc):** Toàn bộ lưới `!!silos_matrix` và thẻ `!!card_loss` lùi mờ sâu (`opacity: 0.15`, `duration: 400ms`). Tại trung tâm hiện ra khung viền nét đứt màu xanh dương rực rỡ `#38BDF8` (`duration: 400ms`) mang tên: **"THE MISSING COGNITIVE LAYER"** (font 28pt) — xác lập chính xác vị trí Aether sẽ cắm vào.
- **Vì sao:** Định lượng chính xác tổn thất (130 công cụ, 4.2 giờ) và chỉ rõ khoảng trống cấu trúc mà các phần mềm riêng lẻ không thể lấp đầy.

---

## Cảnh 3. Xung đột bản chất: Vì sao Chatbot LLM thất bại

- **Chuyển dịch:** "Sao không dùng Microsoft Copilot hay ChatGPT Enterprise?" → "Chatbot dạng hộp thoại không bao giờ giải quyết được bài toán tự hành trong doanh nghiệp."
- **Morph từ cảnh 2:**
  - Không để các diễn viên biến mất! Ba vòng nhận thức từ góc trái trên trượt vào khu vực trung tâm nhưng **ở trạng thái bị phân rã, ngắt kết nối (Disarticulated State)** để phản chiếu sự bất lực của mô hình Chatbot:
    - Vòng ngoài `!!ring_obs` trượt đến vị trí khung chatbox bên trái `(x=0.15, y=0.28, w=0.28, h=0.28)`, viền chuyển sang nét đứt mờ đục xám tro `#64748B` (`opacity: 0.30`).
    - Vòng giữa `!!ring_reason` trượt đến vị trí trung gian `(x=0.42, y=0.32, w=0.20, h=0.20)`, viền chuyển sang cam cảnh báo `#F97316`.
    - Vòng lõi `!!ring_exec` trượt đến vị trí bên phải `(x=0.68, y=0.36, w=0.14, h=0.14)`, viền chuyển thành xám khóa chặt `#475569`.
- **Trên màn hình lúc mở:**
  - Nửa trái: Khung minh họa hộp chat `!!chatbox_mockup` lồng trong `!!ring_obs` mờ đứt nét.
  - Nửa phải: Sơ đồ quy trình nghiệp vụ `!!process_tree` lồng trong `!!ring_exec` bị khóa.
- **Lời nói:**
  > Phản xạ đầu tiên của cả thị trường là đưa chatbot vào từng ứng dụng. Nhưng chatbot chỉ biết nói chuyện khi con người hỏi; **[CLICK]** nó mù ngữ cảnh quy trình nội bộ, tư duy ảo giác, và không thể bấm nút thực thi. **[CLICK]** Doanh nghiệp không cần thêm một trợ lý để chat; họ cần một hệ điều hành nhận thức biết nhìn, biết nghĩ và tự làm việc.
- **Động từ → chuyển động:**
  - *loại bỏ, phủ định* →
    - **Click 1 (Hiện thực 3 điểm nghẽn):** Dưới 3 vòng phân rã xuất hiện 3 nhãn cảnh báo đỏ tương ứng (`stagger: 100ms`, `duration: 300ms`):
      1. Dưới `!!ring_obs`: *Mù ngữ cảnh luồng công việc*.
      2. Dưới `!!ring_reason`: *Nguy cơ ảo giác xác suất*.
      3. Dưới `!!ring_exec`: *Không có quyền ghi vào hệ thống*.
    - **Click 2 (Phủ định mô hình Chatbot):** Toàn bộ nửa trái `!!chatbox_mockup` lùi mờ sâu (`opacity: 0.15`). Vòng lõi `!!ring_exec` và sơ đồ bên phải `!!process_tree` sáng rực lên với viền xanh dương `#38BDF8`, mở đường cho cấu trúc tự hành hoàn chỉnh ở cảnh sau.
- **Vì sao:** Trả lời trực diện hoài nghi lớn nhất của nhà đầu tư: "Tại sao không dùng Microsoft Copilot?", đồng thời giữ nguyên danh tính vật thể xuyên suốt mạch Morph.

---

## Cảnh 4. Giải pháp Aether: Tái lập Bánh đà Nhận thức 3 Tầng

- **Chuyển dịch:** "Họ làm cách nào khả thi về mặt kỹ thuật?" → "Kiến trúc tách rời nhận thức thành Quan sát, Suy luận và Thực thi có bảo đảm an toàn tuyệt đối."
- **Morph từ cảnh 3:**
  - Ba vòng `!!ring_obs`, `!!ring_reason`, `!!ring_exec` từ 3 vị trí phân rã bị hút mạnh về lại trung tâm màn hình, lồng khít vào nhau thành một hệ thống đồng tâm thống nhất (`morph: 1.0s`):
    - `!!ring_obs` (Vòng Quan sát): Khôi phục vị trí `(x=0.33, y=0.18, w=0.34, h=0.34)`, viền xanh lơ sáng `#06B6D4` dày 2pt.
    - `!!ring_reason` (Vòng Suy luận): Khôi phục vị trí `(x=0.38, y=0.23, w=0.24, h=0.24)`, viền tím điện `#8B5CF6` dày 2pt.
    - `!!ring_exec` (Vòng Lõi Thực thi): Khôi phục vị trí `(x=0.43, y=0.28, w=0.14, h=0.14)`, viền vàng kim `#EAB308` dày 2.5pt.
- **Trên màn hình lúc mở:**
  - Ba vòng đồng tâm đứng yên vững chãi, tiêu đề trên đỉnh: *Kiến Trúc 3 Tầng Nhận Thức Tự Hành*.
- **Lời nói:**
  > Đây là kiến trúc của Aether. Vòng ngoài cùng liên tục quan sát thao tác để hiểu quy trình thực tế. **[CLICK]** Vòng giữa phân rã công việc cho mạng lưới Agent chuyên biệt suy luận. **[CLICK]** Nhưng mấu chốt nằm ở vòng lõi: chúng tôi không dùng LLM để đoán mò, mà biên dịch trực tiếp sang các lệnh API quyết định luận, có kiểm toán và chính xác 100%.
- **Động từ → chuyển động:**
  - *nối lại, vận động* →
    - **Click 1 (Kích hoạt Tầng Quan sát & Mạng lưới Agent):**
      - Vòng ngoài `!!ring_obs` xoay góc 60° theo chiều kim đồng hồ (`spin: 60 deg`, `duration: 700ms`), nhấp nháy luồng quét thao tác màn hình.
      - Vòng giữa `!!ring_reason` bật sáng 4 nút tác tử chuyên biệt (Finance, HR, Ops, Legal) xếp đều trên đường tròn (`stagger: 80ms`, `duration: 250ms`).
    - **Click 2 (Khóa cứng Tầng Thực thi Quyết định luận):**
      - Vòng lõi `!!ring_exec` xoay nhẹ 45° rồi dừng khựng cơ học, màu viền chuyển từ vàng kim sang xanh lục bảo `#10B981` (biểu tượng an toàn tuyệt đối).
      - Hai vòng ngoài tự động lùi mờ (`opacity: 0.30`, `duration: 400ms`), dồn 100% tiêu điểm thị giác vào lõi `!!ring_exec`. Từ lõi bắn ra 3 cổng nối API thẳng tắp cắm vào hệ thống ERP/CRM với nhãn: *Deterministic API Execution · Audit Log Verifiable*.
- **Vì sao:** Tách bạch rạch ròi giữa AI suy luận (xác suất) và API thực thi (toán học chuẩn xác 100%) — luận điểm kỹ thuật đắt giá nhất thuyết phục các VC công nghệ.

---

## Cảnh 5. Minh chứng thị trường: $4.2M ARR & 148% NRR

- **Chuyển dịch:** "Sản phẩm nghe hay nhưng đã bán được chưa?" → "Tốc độ tăng trưởng và độ bám khách hàng chứng minh Product-Market Fit cực mạnh."
- **Morph từ cảnh 4:**
  - Ba vòng nhận thức `!!ring_obs`, `!!ring_reason`, `!!ring_exec` giữ nguyên cấu trúc đồng tâm, cùng thu nhỏ mượt mà xuống góc dưới bên trái `(x=0.08, y=0.80, w=0.10, h=0.10)`, đóng vai trò bệ đỡ động lực tăng trưởng.
- **Trên màn hình lúc mở:**
  - Trục tọa độ tài chính: Tiêu đề *Minh Chứng Thực Tế: Tăng Trưởng & Độ Bám Khách Hàng*.
  - Mốc khởi điểm: *Q1/2025: $1.1M ARR* tại `(x=0.18, y=0.62, w=0.15, h=0.08)`.
- **Lời nói:**
  > Chúng tôi không nói về lời hứa tương lai; chúng tôi nói về kết quả đã kiểm chứng. Trong 14 tháng qua, Aether đã cán mốc **[CLICK]** 4.2 triệu USD ARR từ 38 tập đoàn lớn. **[CLICK]** Và quan trọng hơn cả: tỷ lệ mở rộng doanh thu thuần (Net Retention Rate) đạt 148% — một khi doanh nghiệp đã đưa Aether vào vận hành, họ không bao giờ rút ra.
- **Động từ → chuyển động:**
  - *dâng lên, gặp nhau* →
    - **Click 1 (Cột Doanh thu $4.2M dâng trào):**
      - Cột biểu đồ `!!metric_arr` dâng thẳng đứng từ đáy màn hình lên mốc đỉnh `(x=0.42, y=0.24, w=0.22, h=0.56)` (`duration: 600ms`), màu xanh lục `#10B981`.
      - Đường cong tăng trưởng mượt mà nối từ $1.1M lên $4.2M vẽ đồng bộ theo bước dâng của cột. Tại đỉnh cột hiện rõ con số: **$4.2M ARR** (font 44pt Bold).
    - **Click 2 (Tiêu điểm NRR 148%):**
      - Tại `(x=0.68, y=0.32, w=0.26, h=0.36)` xuất hiện thẻ chỉ số `!!card_nrr` (`opacity: 0.00` → `1.00`, `duration: 400ms`), viền vàng kim rực rỡ `#F59E0B`.
      - Toàn bộ phần biểu đồ bên trái lùi mờ (`opacity: 0.30`, `duration: 300ms`) để mắt người xem dừng trọn vẹn vào dòng chữ đắt giá dưới thẻ NRR: *"Net Negative Churn — Khách hàng cũ mở rộng chi tiêu thêm 48% mỗi năm"*.
- **Vì sao:** NRR 148% chứng minh doanh nghiệp càng dùng Aether càng mở rộng thêm quy trình, tạo dòng tiền định kỳ siêu bền vững.

---

## Cảnh 6. Đơn vị kinh tế: Biên lợi nhuận gộp 82%

- **Chuyển dịch:** "Chi phí token suy luận có ăn hết biên lợi nhuận không?" → "Kiến trúc phân tầng nén chi phí GPU xuống 3.6 lần, bảo đảm biên lợi nhuận 82%."
- **Morph từ cảnh 5:**
  - Màn hình mở ra 3 cột số liệu có độ cao tương đương nhau (thế cân bằng):
    - Cột 1 `!!col_gpu`: Đại diện chi phí GPU thông thường (chiếm 65% doanh thu) tại `(x=0.15, y=0.30, w=0.22, h=0.52)`, màu đỏ cam `#EA580C`.
    - Cột 2 `!!col_margin`: Đại diện Gross Margin của Aether tại `(x=0.42, y=0.30, w=0.22, h=0.52)`, màu xám trung tính `#64748B`.
    - Cột 3 `!!col_cac`: Đại diện thời gian hoàn vốn CAC tại `(x=0.69, y=0.30, w=0.22, h=0.52)`, màu xám trung tính `#64748B`.
- **Lời nói:**
  > Nỗi lo lớn nhất với các công ty AI là chi phí suy luận GPU ăn mòn toàn bộ lợi nhuận. Aether giải quyết điều này bằng kiến trúc phân tầng: 80% tác vụ lặp lại được xử lý bằng các mô hình nhỏ chạy cục bộ. **[CLICK]** Nhờ đó, chi phí GPU sụp đổ và biên lợi nhuận gộp của chúng tôi đạt 82%. **[CLICK]** Với hợp đồng trung bình 120,000 USD mỗi năm, chúng tôi thu hồi toàn bộ chi phí bán hàng chỉ sau 4.5 tháng.
- **Động từ → chuyển động:**
  - *nhấn một trong nhiều* →
    - **Click 1 (Morph từ State 6A sang State 6B — Biến đổi Hình học Thật):**
      - Cột 1 `!!col_gpu` co rút chiều cao hình học thật từ `h=0.52` xuống `h=0.14` (tọa độ mới `(x=0.15, y=0.68, w=0.22, h=0.14)`), màu chuyển sang xám tro `#94A3B8`, hiển thị nhãn: *"Chỉ còn 18% chi phí nhờ SLM cục bộ"*.
      - Cột 2 `!!col_margin` vươn cao và mở rộng chiều rộng thật từ `(x=0.42, y=0.30, w=0.22, h=0.52)` thành `(x=0.40, y=0.18, w=0.26, h=0.64)`, nền chuyển sang xanh lục bảo sâu `#064E3B`, viền xanh sáng `#10B981`, con số khổng lồ **82% Gross Margin** bừng sáng ở vị trí trung tâm.
      - Cột 3 `!!col_cac` lùi mờ (`opacity: 0.20`).
      - *PowerPoint Morph tự động nội suy chuyển động co rút và vươn lớn cực kỳ êm ái, loại bỏ hoàn toàn lỗi Wipe Down.*
    - **Click 2 (Kích hoạt Tốc độ Thu hồi vốn):**
      - Cột 3 `!!col_cac` khôi phục độ sáng 100%, con số thời gian đổi thành: **4.5 Tháng** (so với 14 tháng trung bình ngành).
      - Dưới chân cột hiện con dấu xác nhận: *"LTV / CAC = 6.8x · Cash-Flow Positive Per Account"*.
- **Vì sao:** Dùng State-to-State Morph xử lý trực tiếp hình học co rút cột, đập tan định kiến "AI margin squeeze" của các VC.

---

## Cảnh 7. Hào lũy cạnh tranh: Đồ thị quy trình độc quyền

- **Chuyển dịch:** "Nếu OpenAI hay Big Tech sao chép tính năng này thì sao?" → "Hào lũy không nằm ở model mà nằm ở đồ thị quy trình độc quyền không thể cào từ internet."
- **Morph từ cảnh 6:**
  - Hai khối nội dung lớn đặt đối xứng nhau ngang bằng trên màn hình:
    - Nửa trái: Khối `!!card_models` đại diện cho *Mô hình nền tảng (Foundation Models)* tại `(x=0.10, y=0.25, w=0.38, h=0.56)`, màu xanh lam nhạt `#1E293B`.
    - Nửa phải: Khối `!!card_graph` đại diện cho *Đồ thị quy trình độc quyền của Aether* tại `(x=0.52, y=0.25, w=0.38, h=0.56)`, màu tím than `#1E1B4B`.
- **Lời nói:**
  > Các mô hình nền tảng như GPT hay Claude sẽ ngày càng thông minh hơn và rẻ hơn, nhưng chúng chỉ được huấn luyện từ dữ liệu công khai trên web. **[CLICK]** Aether nắm giữ thứ mà không web crawler nào chạm tới được: Đồ thị hành vi và quy trình vận hành thực tế của từng ngành. Càng vận hành, Aether càng hiểu sâu đặc thù doanh nghiệp, **[CLICK]** tạo ra một rào cản chuyển đổi mà không đối thủ nào có thể vượt qua.
- **Động từ → chuyển động:**
  - *song* →
    - **Click 1 (Morph từ State 7A sang State 7B — Hoán đổi Trọng lượng Thị giác Thực sự):**
      - Khối `!!card_models` bên trái co nhỏ hình học từ `w=0.38, h=0.56` xuống `w=0.26, h=0.28`, trượt xuống đáy góc trái `(x=0.08, y=0.56)`, màu chuyển sang xám chì `#475569`, độ mờ hạ xuống `opacity: 0.30`, nhãn phụ: *"Commoditized Infrastructure (Hạ tầng hàng hóa giá rẻ)"*.
      - Khối `!!card_graph` bên phải vươn lớn chiếm lĩnh toàn bộ trung tâm màn hình: từ `(x=0.52, y=0.25, w=0.38, h=0.56)` nở rộng thành `(x=0.38, y=0.18, w=0.54, h=0.66)`, viền sáng vàng kim `#F59E0B` dày 2.5pt, hiển thị đồ thị mạng nhện quy trình kết nối dày đặc.
      - *Chuyển động Swap Weights được thực hiện 100% bằng Morph hình học, không chồng chéo animation giật cục.*
    - **Click 2 (Khóa chặt Hào lũy Độc quyền):**
      - Khối `!!card_graph` sáng rực viền một nhịp. Bên trong hiển thị 38 logo tập đoàn khách hàng được liên kết chặt vào các nút đồ thị.
      - Dòng chữ hào lũy xuất hiện trên đỉnh: *"High Switching Cost — Quy trình đã học không thể xuất khẩu sang đối thủ"*.
- **Vì sao:** Đảo chiều hoàn toàn rủi ro cạnh tranh: biến sự phát triển của Big Tech LLM thành nguyên liệu giá rẻ cho đồ thị quy trình của Aether.

---

## Cảnh 8. Lời kêu gọi: $12M Series A & Ba Trụ Cột Nền Móng

- **Chuyển dịch:** "Tại sao tôi phải giải ngân cho họ ngay hôm nay?" → "Đây là cơ hội sở hữu hạ tầng nền tảng định hình tương lai của công việc tự hành."
- **Morph từ cảnh 7:**
  - Không để các vật thể biến mất ngẫu nhiên! Ba vòng nhận thức `!!ring_obs`, `!!ring_reason`, `!!ring_exec` từ khối `!!card_graph` tách ra, trượt về vị trí trang trọng trên đỉnh trung tâm màn hình:
    - `!!ring_obs` tại `(x=0.40, y=0.14, w=0.20, h=0.20)`, viền xanh lơ `#06B6D4`.
    - `!!ring_reason` tại `(x=0.42, y=0.16, w=0.16, h=0.16)`, viền tím `#8B5CF6`.
    - `!!ring_exec` tại `(x=0.44, y=0.18, w=0.12, h=0.12)`, viền xanh lục `#10B981`.
  - Khối kêu gọi đầu tư `!!ask_card` nằm ngay bên dưới tại `(x=0.25, y=0.38, w=0.50, h=0.20)` với con số vàng lớn: **$12,000,000 USD Series A**.
- **Lời nói:**
  > Chúng tôi đang kêu gọi 12 triệu USD cho vòng Series A để nhân rộng đội ngũ kỹ sư lõi và mở rộng thị phần tại 100 tập đoàn tài chính lớn nhất. **[CLICK]** Chúng tôi không tạo ra một phần mềm phụ trợ; chúng tôi đang xây dựng hệ điều hành nhận thức cho mười năm tới. Xin mời các anh chị cùng tham gia.
- **Động từ → chuyển động:**
  - *trở thành, thống nhất* →
    - **Click 1 (Morph từ State 8A sang State 8B — Ba Vòng Biến thành Ba Trụ Cột Vốn):**
      - Đây là cú Morph đắt giá nhất của kịch bản, hiện thực hóa triệt để nguyên lý *"which object becomes which"*:
        1. Vòng lõi `!!ring_exec` (Thực thi an toàn) trượt xuống góc trái dưới và biến chuyển thành **Trụ cột 1 `!!pillar_rd`** `(x=0.12, y=0.62, w=0.24, h=0.26)`: *60% ($7.2M) — R&D Autonomous Cognitive Core & On-Premise SLMs*.
        2. Vòng giữa `!!ring_reason` (Suy luận đa tác tử) trượt xuống giữa và biến chuyển thành **Trụ cột 2 `!!pillar_gtm`** `(x=0.38, y=0.62, w=0.24, h=0.26)`: *30% ($3.6M) — Enterprise GTM & Phủ sóng 100 định chế tài chính*.
        3. Vòng ngoài `!!ring_obs` (Quan sát quy trình) trượt xuống góc phải và biến chuyển thành **Trụ cột 3 `!!pillar_trust`** `(x=0.64, y=0.62, w=0.24, h=0.26)`: *10% ($1.2M) — Security, Auditability & Compliance (SOC2/ISO)*.
      - Cả 3 trụ cột được kết nối vững chãi trên một thanh bệ đỡ nền màu xanh đậm `#0F172A`, tạo thành một cấu trúc kim tự tháp cân bằng tuyệt đối — hình ảnh đọng lại cuối cùng trước khi chuyển sang phần hỏi đáp của phiên gọi vốn.
- **Vì sao:** Kết thúc bằng sự thống nhất hoàn hảo: ba vòng nhận thức ban đầu biến thành ba trụ cột sử dụng vốn rõ ràng, thuyết phục và đĩnh đạc.
