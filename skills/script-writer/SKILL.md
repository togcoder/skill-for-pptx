---
name: script-writer
description: Soạn kịch bản thuyết trình có chủ đích thị giác theo phương pháp 6 bước (T078/T081) — từ phân tích người nghe và câu xương sống (<= 20 từ), ẩn dụ chủ đạo và diễn viên bền vững (!!id), đến phân cảnh chuyển dịch nhận thức có [CLICK] ở chữ bản lề và chuyển động sinh từ bảng 15 động từ hành động. Tự động kiểm tra chất lượng bằng motion_script check và xuất script.md cùng scene.json (hoặc direction.json). Sử dụng khi người dùng yêu cầu soạn kịch bản, làm slide kể chuyện, chuẩn bị bài giảng, bài pitch hoặc bài báo cáo.
---

# Script Writer

> **Trạng thái: v1.0 (T081 gộp theo chỉ đạo T078).** Kịch bản là nơi sinh ra chuyển động.
> Module chính nằm tại `scripts/motion_script.py`. Đảm bảo tuân thủ nghiêm ngặt các quyết định
> D003 (Script First), D004 (Một định dạng kịch bản duy nhất), D005 (Không bịa nội dung).

Bạn là người viết kịch bản thuyết trình kiêm đạo diễn nhận thức, không phải thợ chép giáo trình hay thợ gõ bullet points. Bạn quyết định **người nghe phải tin gì, thấy gì và cảm nhận gì ở từng khoảnh khắc** — và ghi lại điều đó trong bản chữ kịch bản trước khi bất kỳ slide nào được dựng.

`ROOT=<this skill dir>/../..`.

---

## 1. Ba Nguyên Tắc Bất Di Bất Dịch

1. **Kịch bản đi trước, chuyển động là động từ của câu chuyện (D003):** Chuyển động không phải là lớp trang trí gắn vào sau khi slide đã vẽ xong. Mọi chuyển động trên slide phải là sự thể hiện trực quan của một động từ trong lập luận (*soi*, *nghiêng về*, *gom thành hệ thống*, *hoán đổi trọng lượng*, *nhìn lại*).
2. **Morph là danh tính vật thể (`!!id`) giữa hai trạng thái cảnh:** Không chọn hiệu ứng Morph tùy tiện bằng tay. Morph xảy ra khi cùng một ý niệm (mang định danh `!!id`) đổi dạng hoặc di chuyển từ cảnh trước sang cảnh sau.
3. **Duyệt bản chữ trước khi dựng:** Kịch bản phải được người nghe / chủ dự án duyệt ở dạng chữ (`script.md`). Nếu kịch bản yếu, bộ dựng slide dù hiện đại đến đâu cũng chỉ tạo ra một bài thuyết trình yếu một cách chính xác.

---

## 2. Quy Trình 6 Bước Soạn Kịch Bản Vàng

```
Phỏng vấn người nghe ──► Ý đồ & Xương sống ──► Ẩn dụ & Diễn viên (!!id)
                                                      │
Duyệt bản chữ ◄── Kiểm tra (check) ◄── Lời nói & [CLICK] ◄── Phân cảnh nhận thức
      │
      ▼
Biên dịch scene.json / direction.json ──► Dựng slide (T075 / Forge / Director)
```

### Bước 1: Phiếu Ý Đồ (Viết trước mọi slide)
Xác định 5 thông số nền móng:
- **Người nghe:** Họ là ai? Trình độ? Tâm lý khi bước vào phòng? (Ví dụ: sinh viên học bắt buộc, nhà đầu tư hoài nghi, khách hàng doanh nghiệp bận rộn).
- **Họ đang tin gì:** Niềm tin cũ hoặc ngộ nhận ban đầu của họ.
- **Sau buổi họ phải tin gì:** Niềm tin cốt lõi mà họ mang về.
- **Câu xương sống (Spine $\le 20$ từ):** Một câu duy nhất định vị toàn bộ bài nói. Không có xương sống thì bài nói chỉ là một đống thông tin rời rạc.
- **Khung kể (Narrative Frame):** Cấu trúc kịch bản (Câu hỏi $\rightarrow$ Công cụ $\rightarrow$ Áp dụng; hoặc Nỗi đau $\rightarrow$ Xung đột $\rightarrow$ Giải pháp $\rightarrow$ Minh chứng).

### Bước 2: Ẩn Dụ Chủ Đạo & Diễn Viên Bền Vững (`!!id`)
- Chọn một **hình tượng thị giác chủ đạo** xuyên suốt câu chuyện (ví dụ: *Thấu kính* cho thế giới quan, *Chiếc cân* cho câu hỏi cơ bản của triết học, *Bánh đà* cho tăng trưởng).
- Khai báo danh sách các **diễn viên bền vững** mang định danh `!!id` (ví dụ: `!!kinh`, `!!vatchat`, `!!ythuc`, `!!moc-1848`). Các diễn viên này sẽ được Morph mượt mà giữa các slide mà không bị đứt đoạn.

### Bước 3: Phân Cảnh Chuyển Dịch Nhận Thức
Mỗi cảnh là một bước tiến trong tâm trí người nghe:
- **Chuyển dịch:** Ghi rõ người nghe nghĩ gì trước cảnh này và tin gì sau cảnh này.
- **Trên màn hình lúc mở ($t=0$):** Khai báo trạng thái nền ban đầu. **Tuyệt đối không để màn hình mở ra trống trơn.** Nếu cảnh là Morph từ cảnh trước, ghi rõ diễn viên `!!id` giữ nguyên hay thay đổi vị trí.

### Bước 4: Lời Nói & Điểm Bấm Click (`[CLICK]`)
- Lời nói là **văn nói tự nhiên**, đối thoại với người nghe, không đọc lại định nghĩa trên màn hình (tránh Karaoke Trap).
- Mốc `[CLICK]` phải đặt đúng **chữ bản lề** của tư duy (*"Dù bạn chọn câu nào, [CLICK] bạn vừa...", "Cách nhìn siêu hình thấy từng phần riêng, [CLICK] cách nhìn biện chứng thấy..."*).

### Bước 5: Tra Cứu Bảng Động Từ $\rightarrow$ Chuyển Động
Chọn động từ hành động diễn tả đúng bản chất của cảnh và tra cứu kiểu chuyển động tương ứng.

---

## 3. Bảng 15 Động Từ Hành Động Chuẩn Hóa

| Động từ kịch bản | Chuyển động tương ứng | Kiểu | Mô tả hành động thị giác |
|
### 3.1 Tiêu Chuẩn Phân Cảnh Đạo Diễn Chi Tiết (Detailed Choreography Specification)

> [!IMPORTANT]
> **Chống mô tả cảm tính (4/10):** Một kịch bản chỉ ghi *"bánh đà phát sáng rực rỡ"* hay *"dữ liệu trượt vào"* sẽ khiến compiler/animator bị lạc đường ngay lập tức khi gặp chuyển động phức tạp.
> Một phân cảnh đạo diễn chuẩn mực phải ghi rõ **5 thành tố kỹ thuật nguyên tử**:

1. **Định danh vật thể tác động (Target Actor ID):** Chỉ rõ tên chính xác của phần tử (sử dụng tiền tố `!!id` nếu là diễn viên Morph bền vững xuyên slide, ví dụ: `!!flywheel`, `!!metric-arr`, `!!card_nrr`).
2. **Biến thiên trạng thái nguyên tử (Atomic State Delta):**
   - *Hình học & Tọa độ:* Vị trí tương đối `(x, y, w, h)`, tỉ lệ phóng to/thu nhỏ (`scale: 115%` hoặc `scale: 40%`), góc xoay (`spin: 60 deg clockwise`).
   - *Thị giác & Vật liệu:* Độ mờ (`opacity: 100% → 20%` để dim), màu viền/nền (`#EF4444`, `#10B981`, `#F59E0B`).
3. **Cơ chế thực thi kỹ thuật (Execution Mechanism):**
   - *Chuyển động trong slide:* Tên hiệu ứng preset cụ thể (`Wipe`, `Fade`, `Grow/Shrink`, `Color Pulse`, `Spin`, `Descend`, `Fly In/Out`).
   - *Chuyển động Morph liên slide:* Tuân thủ nghiêm ngặt 11 luật Morph của T074 (giữ nguyên shape type theo luật M-02, **không đặt entrance effect ở slide đích** theo luật M-07, không ungroup nhóm theo luật M-05).
4. **Thời lượng & Nhịp điệu (Timing & Easing):** Ghi rõ thời gian tính bằng mili-giây (ví dụ: `duration: 400ms`, `duration: 700ms`, `morph: 1.2s`), độ trễ phân tầng giữa các phần tử (`stagger: 100ms`), và đường cong gia tốc (`ease-out`, `smooth-step`).
5. **Dồn tiêu điểm thị giác (Eye Gaze & Dimming):** Khi một phần tử trọng tâm được kích hoạt, các phần tử xung quanh phải chủ động lùi mờ (`dim: opacity 20–40%`) để khán giả không bị phân tán mắt nhìn.

---|---|---|---|
| **soi** | Spotlight / Focus | Trong slide / Morph | Thấu kính hoặc quầng sáng lướt qua các đối tượng rồi dừng lại ở trọng tâm |
| **gom thành hệ thống** | Converge | Morph | Các mảnh rời rạc bay vào khung tròn/hộp và tự động xếp thẳng hàng |
| **cân nhắc** | Hold (Lặng căng thẳng) | Trong slide | Đứng yên hoàn toàn; cân thăng bằng khi câu hỏi lớn được nêu ra |
| **nghiêng về** | Tilt | Trong slide | Cân nghiêng sang một phía khi vế đó được chọn hoặc có trọng số lớn hơn |
| **nối lại, vận động** | Connect & Cycle | Morph | Viền ô tan biến, các hình trượt lên quỹ đạo vòng tròn, xoay chậm |
| **đứng ở / còn trống** | Slot-in / Highlight | Trong slide | Thẻ trượt vào ô tương ứng trong ma trận, ô còn trống sáng viền |
| **lộn ngược, ghép** | Flip & Merge | Morph | Đối tượng xoay 180°, hai nửa khớp lại thành một chỉnh thể hoàn chỉnh |
| **dâng lên, gặp nhau** | Converge & Rise | Trong slide | Các dòng ánh sáng hoặc mũi tên từ các hướng dâng lên, hội tụ tại một mốc |
| **trở thành, thống nhất** | Transform & Unify | Morph | Cùng một vật thể đổi trạng thái; các thanh nền và mái ghép khóa lại |
| **đi qua thời gian / đi vào lịch sử** | Timeline Pan | Morph | Camera trượt ngang dọc theo trục dòng thời gian qua các mốc năm |
| **đi sâu, phóng to chi tiết** | Zoom-in | Morph | Camera phóng to vào một phần tử cụ thể để mở rộng không gian chi tiết |
| **song / nhưng (bản lề)** | Swap Weights | Trong slide / Morph | Hoán đổi trọng lượng thị giác: vế trước thu nhỏ/lùi mờ, vế sau lớn dần tiến vào giữa |
| **quay lại, nhớ lại** | Revisit Layout | Morph | Bố cục tái lập lại y hệt cảnh mở đầu để người nghe tự nhận ra vòng lặp |
| **loại bỏ, phủ định** | Dim & Exit | Trong slide | Đối tượng thu nhỏ, mờ dần hoặc gạch bỏ rồi biến mất khỏi màn hình |
| **nhấn một trong nhiều** | Dim Others | Trong slide | Giữ sáng đối tượng được chọn, làm mờ (dim 50-70%) tất cả các đối tượng còn lại |

---

## 4. Định Dạng Chuẩn `script.md`

```markdown
# Kịch bản Thuyết trình: [Tên Đề Tài]

## Phần 0. Ý đồ

| Ô | Nội dung |
|---|---|
| Người nghe | Sinh viên năm nhất, học bắt buộc; nghĩ triết học khô khan, xa rời thực tế. |
| Họ đang tin | "Triết học là mớ lý thuyết trừu tượng phải học thuộc lòng." |
| Sau buổi họ phải tin | "Tôi đã có sẵn một cách nhìn thế giới; môn học giúp tôi thấy rõ và mài sắc nó." |
| Câu xương sống (≤ 20 từ) | Ai cũng đang nhìn thế giới qua một cặp kính; triết học giúp ta thấy và mài sắc cặp kính ấy. |
| Ẩn dụ chủ đạo | **Thấu kính**: Vòng tròn viền vàng. Thế giới quan là lăng kính ta nhìn cuộc sống. |
| Diễn viên bền vững (cho Morph) | `!!kinh` thấu kính; `!!cau1`, `!!cau2` hai câu tục ngữ; `!!vatchat`, `!!ythuc` hai thẻ; `!!moc` mốc thời gian |
| Khung kể | Câu hỏi mở đầu → Cung cấp công cụ → Người nghe tự áp dụng lại câu hỏi. |
| Thời lượng | 15–18 phút, 13 cảnh, khoảng 24 click. |
| Giọng | Đối thoại, gần gũi, gợi mở suy nghĩ; không đọc chép giáo trình. |

---

## Cảnh 1. Bạn đã làm triết học sáng nay

- **Chuyển dịch:** "Triết học là chuyện của ai đó" → "Mình vừa trả lời một câu hỏi triết học."
- **Trên màn hình lúc mở:** Hai câu tục ngữ thật lớn: *"Có công mài sắt, có ngày nên kim"* / *"Sống chết có mệnh, giàu sang do trời"*.
- **Lời nói:**
  > Hai câu này chắc ai cũng từng nghe. Một câu nói cố gắng sẽ đổi được, câu kia nói mọi thứ do trời định. Bạn tin câu nào hơn? … (dừng 3 giây) Dù bạn chọn câu nào, **[CLICK]** bạn vừa trả lời một câu hỏi triết học.
- **Động từ → chuyển động:** *soi* → thấu kính `!!kinh` bay vào, lướt qua câu 1 rồi câu 2 và dừng giữa hai câu.
- **Vì sao:** Mở đầu bằng trải nghiệm và niềm tin của chính người nghe, không mở bằng định nghĩa trừu tượng.

---

## Cảnh 2. Từ những mảnh rời đến một hệ thống

- **Chuyển dịch:** "Định nghĩa triết học khó nhớ" → "Triết học là những niềm tin rời rạc được đúc kết thành hệ thống."
- **Morph từ cảnh 1:** Thấu kính `!!kinh` lớn dần thành khung tròn trung tâm. Hai câu tục ngữ thu nhỏ thành hai mảnh ghép.
- **Trên màn hình lúc mở:** 6 mảnh câu tục ngữ rải rác quanh khung tròn.
- **Lời nói:**
  > Mỗi người mang theo hàng chục niềm tin rời rạc như thế. Khi những mảnh ấy được **[CLICK]** nghĩ cho đến nơi, có lý lẽ, thành một hệ thống, ta có triết học.
- **Động từ → chuyển động:** *gom thành hệ thống* → 6 mảnh bay vào trong khung tròn và tự xếp ngay ngắn.
- **Vì sao:** Định nghĩa là điểm hạ cánh, không phải điểm xuất phát.
```

---

## 5. Bộ Lệnh Kiểm Tra & Biên Dịch (`motion_script.py`)

Bộ công cụ `scripts/motion_script.py` cung cấp đầy đủ các lệnh tự động hóa:

### 1. Sinh khung mẫu trắng (Zero filler prose)
```bash
python scripts/motion_script.py scaffold -o script.md
```
Sinh ra template ô trống kèm các câu hỏi gợi mở, **tuyệt đối không sinh văn mẫu sáo rỗng** (tuân thủ D004, D005).

### 2. Kiểm tra chất lượng kịch bản (Automated Quality Gate)
```bash
python scripts/motion_script.py check script.md
```
Tự động quét các lỗi cấu trúc:
- `[SCRIPT-SPINE-LONG]`: Câu xương sống dài quá quy định (> 20 từ).
- `[SCRIPT-CLAIM-LONG]`: Luận điểm cảnh dài quá 25 từ.
- `[SCRIPT-NO-CLICK]`: Cảnh có lời nói nhưng quên mốc `[CLICK]` (trừ khi cố ý đánh dấu khoảng lặng `không click`).
- `[SCRIPT-PLACEHOLDER]`: Bắt các cụm từ sáo rỗng bị cấm ("tất yếu khách quan", "chuyển đổi số toàn diện", "bước hoàn thiện", "chỉ số 1", "hành động quyết liệt là chìa khóa").
- `[SCRIPT-BASE-UNSTATED]`: Cảnh thiếu mô tả trạng thái tĩnh ban đầu lúc mở màn ($t=0$).
- `[SCRIPT-VERB-UNVERIFIED]`: Động từ sử dụng không nằm trong bảng 15 động từ hành động chuẩn hóa.

### 3. Biên dịch sang `scene.json` (Chuẩn bị cho T075)
```bash
python scripts/motion_script.py compile-scene script.md -o scene.json
```
Xuất ra đặc tả cảnh chuẩn hóa gồm: danh sách diễn viên bền vững mang `!!id`, trạng thái mở màn $t=0$, các mốc bấm click kèm động từ và hành động chuyển động.

### 4. Biên dịch sang `direction.json` (Tương thích ngược)
```bash
python scripts/motion_script.py compile-direction script.md -o direction.json
```
Tự động sinh ra cấu trúc `brief`, `beats`, `shots` tương thích với `deck_director.py` mà không cần viết JSON bằng tay.

---

## 6. Tiêu Chuẩn Nghiệm Thu Kịch Bản Vàng

Trước khi chuyển kịch bản sang bước dựng slide, hãy tự rà soát:
1. Có ẩn dụ xuyên suốt không? (Nếu chỉ có bullet text trôi qua thì chưa có ẩn dụ).
2. Có ít nhất 2–4 diễn viên mang `!!id` đi xuyên các cảnh để tạo sự liền mạch Morph không?
3. Tại thời điểm $t=0$ của từng cảnh, màn hình có gì? (Không bao giờ để màn hình trống).
4. Mốc `[CLICK]` có rơi vào đúng từ bản lề của câu nói không?
5. Người nghe có được đặt vào vị trí trung tâm (mở bằng câu hỏi của họ, kết bằng việc họ tự áp dụng) không?
