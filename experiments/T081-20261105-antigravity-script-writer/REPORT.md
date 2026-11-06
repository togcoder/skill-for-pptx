# T081 [pptx] — script-writer skill and unified screenplay compiler

- **Agent / model:** Antigravity (Gemini 2.5 Pro).
- **Date:** 2026-11-05. **Base:** `main` @ `bbdc3a3`. **Branch:** `work/T081-antigravity-script-writer`.
- **Capability:** `pptx.script` (extended canonical `scripts/motion_script.py`; standalone skill in `skills/script-writer/SKILL.md`).
- **Owner Feedback Addressed:** F9 (approved by project owner: *"kịch bản khá tốt tôi duyệt, hãy thực hiện nhiệm vụ được chỉ định"*).
- **Decisions Binding:** D001 (Owner's eye), D003 (Script First), D004 (One Script Format), D005 (Never Invent Content), D006 (Single Writer), D007 (Coordination Claim), D008 (Different Model Reviewer: OpenCode / DeepSeek).
- **Status:** Complete; review requested from OpenCode.

---

## 1. Bối cảnh & Vấn đề (Frame & Diagnosis)

Trưởng nhóm (Claude, T070/T078) và kiểm toán T067 đã chỉ rõ lỗ hổng lớn nhất khiến slide có chuyển động mà không có "gu":
1. **Phân mảnh kịch bản:** Tồn tại hai hệ thống kịch bản song song không tương thích: `scripts/motion_script.py` (Markdown có `[click]` cho deck có sẵn) và `scripts/deck_director.py` (viết tay `direction.json` bằng JSON phức tạp).
2. **Cơ khí hóa & Văn mẫu khuôn sáo (D004, D005):** Hàm `scaffold_direction()` trước đây tự sinh các câu văn sáo rỗng điền sẵn ("tất yếu khách quan", "chuyển đổi số toàn diện", "hành động quyết liệt là chìa khóa", "bước hoàn thiện"), làm mất đi tính chân thực và trí tuệ của bài nói.
3. **Chuyển động không bắt nguồn từ động từ câu chuyện:** Hiệu ứng bị gán ép máy móc vào các hộp tĩnh sau khi dựng, thay vì chuyển động là *động từ của câu chuyện* và Morph là *danh tính vật thể bền vững (`!!id`)* chuyển đổi trạng thái giữa hai cảnh.

---

## 2. Giải pháp Thực Hiện (Method)

Theo chỉ đạo của `docs/SCRIPT_TRACK.md` và Quyết định D004:

### 2.1 Mở rộng Module Chuẩn `scripts/motion_script.py`
Thay vì tạo thêm script mới gây phân mảnh registry, mở rộng trực tiếp canonical module `pptx.script`:
- **Bảng 15 Động Từ Hành Động (`VERB_TABLE`):** Chuẩn hóa 15 động từ từ kịch bản mẫu vàng T078 (`soi`, `gom thành hệ thống`, `cân nhắc`, `nghiêng về`, `nối lại, vận động`, `đứng ở / còn trống`, `lộn ngược, ghép`, `dâng lên, gặp nhau`, `trở thành, thống nhất`, `đi qua thời gian`, `đi sâu, phóng to chi tiết`, `song/nhưng`, `quay lại, nhớ lại`, `loại bỏ, phủ định`, `nhấn một trong nhiều`) cùng từ đồng nghĩa tự nhiên và phân loại (`in-slide`, `morph`).
- **Cấm hoàn toàn từ ngữ sáo rỗng (`BANNED_PLACEHOLDERS`):** Lập danh sách chặn các cụm từ điền sẵn vô nghĩa.
- **Trình phân tích thống nhất (`parse_intent`, `parse_gold_script`, `parse_script_full`):**
  - Đọc Section 0 (`## Phần 0. Ý đồ`) trích xuất: Người nghe, Họ đang tin gì, Sau buổi họ phải tin gì, Câu xương sống ($\le 20$ từ), Ẩn dụ chủ đạo, Diễn viên bền vững (`!!id`), Khung kể, Thời lượng, Giọng điệu.
  - Đọc từng cảnh (`## Cảnh N.`) trích xuất: Chuyển dịch nhận thức (`turn`), Màn hình lúc mở $t=0$ (`base_state`), Morph liên kết (`morph_from`), Lời nói có mốc bấm `[CLICK]`, Động từ $\rightarrow$ Chuyển động, và Lý do sư phạm (`why`).
  - Tương thích ngược hoàn toàn với định dạng slide markdown cũ.
- **Cổng kiểm tra chất lượng tự động (`check_script`):** Không cần gọi LLM, kiểm tra chính xác các luật:
  - `[SCRIPT-SPINE-LONG]`: Chặn câu xương sống $> 22$ từ; cảnh báo khuyến nghị khi $> 20$ từ.
  - `[SCRIPT-CLAIM-LONG]`: Chặn luận điểm cảnh $> 25$ từ.
  - `[SCRIPT-NO-CLICK]`: Chặn cảnh có lời thoại mà quên đặt `[CLICK]` (cho phép ngoại lệ nếu đánh dấu khoảng lặng có chủ đích `không click`).
  - `[SCRIPT-PLACEHOLDER]`: Chặn các cụm từ sáo rỗng bị cấm.
  - `[SCRIPT-BASE-UNSTATED]`: Cảnh báo cảnh thiếu trạng thái $t=0$ khi không có Morph kế thừa.
  - `[SCRIPT-VERB-UNVERIFIED]`: Cảnh báo động từ không khớp với bảng 15 động từ chuẩn hóa.
- **Biên dịch đặc tả cảnh (`compile_to_scene`):**
  - Xuất ra `scene.json` chuẩn bị trực tiếp cho bộ biên dịch cảnh T075 (chứa `intent`, danh sách diễn viên bền vững mang `!!id`, và các cảnh với mốc click, động từ, hành động thị giác).
- **Biên dịch tương thích ngược (`compile_to_direction`):**
  - Xuất ra `direction.json` cho `deck_director.py` mà không phải viết JSON tay.
- **Sinh khung mẫu trắng (`scaffold_script`):**
  - Chỉ sinh ô trống kèm câu hỏi gợi mở trong comment HTML, **0 câu văn mẫu**.

### 2.2 Đóng Gói Skill Độc Lập `skills/script-writer/SKILL.md`
- Xây dựng quy trình 6 bước rõ ràng từ phỏng vấn người nghe đến duyệt bản chữ.
- Bảng tra cứu 15 động từ hành động $\rightarrow$ chuyển động.
- Trích dẫn phân tích mẫu vàng Triết học Chương 1 (T078).

---

## 3. Bằng Chứng & Kiểm Chứng (Evidence & Verification)

### 3.1 Kiểm thử Kịch bản Mẫu Vàng T078
Chạy kiểm tra kịch bản vàng thực tế `experiments/T078-20261104-claude-script-track/gold-script-triet-hoc-ch1.md`:
```powershell
python scripts/motion_script.py check experiments/T078-20261104-claude-script-track/gold-script-triet-hoc-ch1.md
```
**Kết quả:**
- `PASS: 13 scenes, spine: 21 words`. 0 lỗi cấu trúc.
- Cảnh báo khuyến nghị duy nhất: `[SCRIPT-SPINE-RECOMMENDATION]` (câu xương sống có 21 từ, khuyến nghị $\le 20$ từ).
- Biên dịch thành công ra `artifacts/triet-hoc-ch1-scene.json` (13 scenes, 11 diễn viên bền vững `!!id`).
- Biên dịch thành công ra `artifacts/triet-hoc-ch1-direction.json` (13 beats, 13 shots).

### 3.2 Bộ Unit Test Chuyên Biệt (`tests/test_script_writer.py`)
11/11 bài test pass 100%:
1. `test_parse_gold_script_structure`: Đọc đúng 13 cảnh, 11 diễn viên `!!id`, intent table.
2. `test_check_gold_script_passes`: Đạt trạng thái PASS trên kịch bản vàng.
3. `test_check_catches_banned_placeholder`: Bắt chính xác cụm "tất yếu khách quan", "chuyển đổi số toàn diện".
4. `test_check_catches_long_spine`: Bắt lỗi khi câu xương sống $> 22$ từ.
5. `test_check_catches_missing_click`: Bắt lỗi cảnh có lời nói nhưng không có mốc `[CLICK]`.
6. `test_check_allows_intentional_hold_silence`: Chấp nhận cảnh khoảng lặng có chủ đích (`không click`).
7. `test_check_catches_long_claim`: Bắt lỗi claim $> 25$ từ.
8. `test_scaffold_has_zero_canned_prose`: Xác nhận scaffold chỉ có comment gợi ý, 0 văn mẫu.
9. `test_compile_to_scene_structure`: Xác thực schema `scene.json` cho T075.
10. `test_compile_to_direction_backward_compatibility`: Xác thực tương thích với `deck_director.py`.
11. `test_verb_table_completeness`: Đảm bảo đủ 15 động từ hành động chuẩn hóa.

### 3.3 Toàn Bộ Test Suite Repo
Chạy toàn bộ test suite của repo:
- **575/575 tests pass** (9 skipped), thời gian chạy 27.9s.
- `lab/tools/check_layout.py`: **layout OK** (không mojibake, không UTF-8 BOM).
- `lab/tools/coord.py check`: **coordination OK**.

---

## 4. Tệp Tin Của Nhiệm Vụ (Artifacts & Deliverables)

1. `skills/script-writer/SKILL.md`: Tài liệu hướng dẫn nghiệp vụ chuẩn cho agent và người dùng.
2. `scripts/motion_script.py`: Mở rộng các lệnh CLI `scaffold`, `check`, `compile-scene`, `compile-direction`.
3. `tests/test_script_writer.py`: 11 bài test tự động.
4. `experiments/T081-20261105-antigravity-script-writer/artifacts/triet-hoc-ch1-scene.json`: Bản đặc tả cảnh biên dịch từ kịch bản vàng (đầu vào cho T075).
5. `experiments/T081-20261105-antigravity-script-writer/artifacts/triet-hoc-ch1-direction.json`: Bản đặc tả `direction.json` tương thích ngược.
6. `experiments/T081-20261105-antigravity-script-writer/artifacts/template-scaffold.md`: Khung kịch bản mẫu ô trống sạch 100%.

---

## 5. Bàn Giao & Bước Tiếp Theo (Handoff)

- **Yêu cầu phản biện (Review Request):** Chuyển giao sang OpenCode (DeepSeek) để thực hiện review theo luật D008 (Builder = Gemini, Critic = DeepSeek).
- **Kích hoạt nhiệm vụ tiếp theo:**
  - **T079 (Đo lường năng lực kịch bản của model yếu):** Dùng skill `script-writer` này để kiểm tra A/B mù giữa các model trên 3 đề thi chuẩn.
  - **T075 (`scene.json` + Trình biên dịch cảnh):** Sử dụng cấu trúc `scene.json` vừa được chuẩn hóa tại `triet-hoc-ch1-scene.json` để hiện thực hóa trình biên dịch Morph và timing OOXML.
