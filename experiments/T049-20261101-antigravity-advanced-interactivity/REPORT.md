# T049 — 1-Slide Native Interactive Mini-Games: Root Cause Analysis, Fixes & Implementation

- **Domain:** `pptx` (Presentation Craft)
- **Agent:** Antigravity (Google DeepMind)
- **Date (UTC):** 2026-11-01
- **Branch:** `work/T049-advanced-presentation-interactivity`
- **Status:** Complete (review requested)

---

## 1. Phân Tích Toàn Diện Nguyên Nhân Lỗi (Root Cause Analysis)

Sau phản hồi của lab owner:
> *"không hiệu quả không hoạt động, đúng vậy nâng cao chính là chuyển động trong cùng 1 slide tạo 1 game mà chỉ hoạt động trong 1 slide, tìm kiếm nguyên nhân lỗi cũng như làm sao để cải thiện"*

Chúng tôi đã tiến hành phân tích sâu vào cơ chế hoạt động thực tế của PowerPoint 16.0 COM và cấu trúc OpenXML PresentationML. Bốn nguyên nhân cốt lõi khiến bản thử nghiệm trước không hoạt động đã được làm sáng tỏ:

### 1.1. Lỗi Che Khuất Sự Kiện Chuột (Hit-Test Hijack / Z-Order Blocking)
* **Hiện tượng:** Người dùng nhấp vào nút "Xem Chi Tiết" nhưng không có phản hồi nào xảy ra.
* **Nguyên nhân kỹ thuật:** Chúng tôi đã tạo một hình chữ nhật phủ mờ (`Dimmer`) kích thước toàn màn hình `(0, 0, 13.333", 7.5")` đặt ở Z-order cao hơn nút bấm trong `<p:spTree>`. Trong cơ chế kết xuất của PowerPoint, bất kỳ hình vẽ nào nằm phía trên đều **chặn trọn vẹn sự kiện click chuột** tới các hình bên dưới, kể cả khi hình đó có hiệu ứng xuất hiện. Nút bấm ở tầng dưới không bao giờ nhận được sự kiện chuột.

### 1.2. Xung Đột Giữa Thẻ Action Hyperlink và Animation Trigger
* **Hiện tượng:** Trigger hoạt ảnh bị vô hiệu hóa hoàn toàn khi gắn âm thanh qua hyperlink.
* **Nguyên nhân kỹ thuật:** Để gắn tệp âm thanh nhị phân, chúng tôi đã thêm thẻ DrawingML `<a:hlinkClick action="ppaction://noaction">`. Trong kiến trúc của PowerPoint, khi một shape có thẻ `hlinkClick`, trình điều khiển Hyperlink sẽ nuốt trọn sự kiện nhấp chuột (click event) và lập tức dừng lan truyền (stopPropagation), khiến bộ máy Trigger hoạt ảnh (`interactiveSeq`) không bao giờ nhận được tín hiệu kích hoạt.

### 1.3. Lệch Chuẩn Cấu Trúc OOXML `interactiveSeq` của `pptx_animator.py`
* **Hiện tượng:** Hoạt ảnh không tự khởi động khi click.
* **Nguyên nhân kỹ thuật:** Qua việc đối chiếu trực tiếp với mã sinh ra từ PowerPoint 16.0 COM (`native_chest_game.pptx`), chúng tôi phát hiện 2 điểm sai lệch chí mạng trong `pptx_animator.py`:
  1. Thẻ `<p:stCondLst><p:cond evt="onClick" delay="0"><p:tgtEl><p:spTgt spid="..."/></p:tgtEl></p:cond></p:stCondLst>` bắt buộc phải nằm **trực tiếp trên node `cTn` của `interactiveSeq`** (chứ không chỉ nằm ở `nextCondLst` của `p:seq`).
  2. Node `cTn` con bên trong chứa `<p:cond delay="indefinite"/>` thay vì `<p:cond delay="0"/>`, khiến PowerPoint hiểu rằng hoạt ảnh phải đợi một lệnh điều khiển bên ngoài mới chạy, dẫn đến việc không chạy khi nhấp chuột.

### 1.4. Thiết Kế Chồng Đè Gây Phá Vỡ Chế Độ Thiết Kế (Edit View)
* Khi xếp các khối thoại nổi khổng lồ đè lên giao diện chính, trong chế độ thiết kế (hoặc xuất ảnh tĩnh), PowerPoint luôn vẽ toàn bộ các hình, tạo ra một mớ chữ chồng chéo gây ức chế thị giác.

---

## 2. Giải Pháp Cải Thiện & Kiến Trúc Mini-Game 1 Slide Chuẩn Mực

Để tạo ra một trò chơi hoạt động **100% trong 1 SLIDE DUY NHẤT**, chúng tôi đã chuẩn hóa mô hình thiết kế theo chuẩn trò chơi PowerPoint chuyên nghiệp:

### 2.1. Game 1: Khám Phá Rương Báu Hoàng Gia (Mystery Treasure Chests)
* **Bố cục:** 3 rương báu xếp độc lập song song (Cột 1, Cột 2, Cột 3), không hề có hình vẽ nào che khuất nhau ngoài phạm vi từng rương.
* **Cơ chế Nắp Che - Phần Thưởng (Cover-Reward Mechanism):**
  * Tầng dưới: Thẻ phần thưởng (`Reward_1`, `Reward_2`, `Reward_3`).
  * Tầng trên: Thẻ nắp rương (`Cover_1`, `Cover_2`, `Cover_3`) đặt khớp kích thước với thẻ phần thưởng.
* **Tương tác Tự Kích Hoạt (Self-Triggered Exit):**
  * Nhấp trực tiếp vào `Cover_1` -> `Cover_1` biến mất bằng hiệu ứng Zoom-out (`presetID="53"`, `presetClass="exit"`), làm lộ ra phần thưởng 1,000 Kim Cương bên dưới!
  * Tương tự cho `Cover_2` (Bùa Sấm Sét) và `Cover_3` (Bẫy Rồng).
* **Nút Reset Chơi Lại Tại Chỗ:**
  * Nút `[🔄 Đóng Lại Tất Cả Rương (Reset)]` kích hoạt hoạt ảnh Entrance (`Zoom-in`) cho cả 3 nắp rương cùng lúc, cho phép chơi lại vô tận ngay trên 1 slide.

### 2.2. Game 2: Đấu Trí Trắc Nghiệm Tương Tác (Interactive Quiz Battle)
* **Bố cục Phân Vùng Rõ Ràng (Partitioned Layout):**
  * Khung câu hỏi ở phía trên.
  * 3 thẻ lựa chọn đáp án A, B, C đặt ở cột trái (`width=460`).
  * 3 thẻ phản hồi kết quả (Feedback Badge) đặt ở cột phải (`width=380`), hoàn toàn không đè lên nút lựa chọn.
* **Phản Hồi Tức Thì:**
  * Nhấp Choice A (Sai) -> Huy hiệu đỏ ❌ "Sai rồi!" xuất hiện ở cột phải.
  * Nhấp Choice B (Đúng) -> Huy hiệu xanh 🎉 "Chính xác! +100 Điểm!" xuất hiện.
  * Nhấp Choice C (Sai) -> Huy hiệu đỏ ❌ xuất hiện.
  * Nút `[🔄 Làm Lại Câu Hỏi]` kích hoạt Exit hoạt ảnh ẩn toàn bộ huy hiệu phản hồi để trả lời lại.

---

## 3. Bằng Chứng Thực Nghiệm & Xác Minh

1. **PowerPoint 16.0 COM Native:**
   * Slide 1: 10 shapes, 4 InteractiveSequences (3 Exit triggers cho 3 rương + 1 Entrance trigger cho nút Reset).
   * Slide 2: 10 shapes, 4 InteractiveSequences (3 Entrance triggers cho 3 đáp án + 1 Exit trigger cho nút Reset).
   * Tệp mở hoàn hảo, không có cảnh báo lỗi XML hay sửa tệp.
2. **DeckCraft CLI Render:**
   * Kết xuất thành công 2 slide ở độ phân giải 1920x1080 không một lỗi nhỏ.
3. **Bộ Kiểm Thử Tự Động:**
   * Full lab test suite: **400/400 tests passing 100%**.
   * `lab/tools/check_layout.py`: Báo cáo `layout OK`.

---

## 4. Tệp Tin & Thành Phẩm

- Tệp trình diễn: [`experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/one_slide_games_suite.pptx`](file:///c:/Users/COMPUTER/Desktop/làm chung với ai/skill-for-pptx/experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/one_slide_games_suite.pptx)
- Tệp audit: [`experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/audit_one_slide_games.json`](file:///c:/Users/COMPUTER/Desktop/làm chung với ai/skill-for-pptx/experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/audit_one_slide_games.json)
- Ảnh xem trước:
  - Slide 1: [`artifacts/previews/slide-01.png`](file:///c:/Users/COMPUTER/Desktop/làm chung với ai/skill-for-pptx/experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/previews/slide-01.png)
  - Slide 2: [`artifacts/previews/slide-02.png`](file:///c:/Users/COMPUTER/Desktop/làm chung với ai/skill-for-pptx/experiments/T049-20261101-antigravity-advanced-interactivity/artifacts/previews/slide-02.png)
