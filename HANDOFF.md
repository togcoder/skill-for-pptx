# Handoff — PPTX Motion Lab & Skill for Design

Cập nhật: 31/10/2026 (sau T035). Tệp này **viết lại mỗi lần bàn giao, không ghi
nối thêm**. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md) và
[docs/archive/HANDOFF-history-2026-10.md](docs/archive/HANDOFF-history-2026-10.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Bắt đầu trong 5 phút

1. Đầu nghiên cứu mới nhất nằm trên nhánh `work/T035-deckcraft-bridge` (dựa trên
   `claude/blissful-pasteur-gmll59`, T034 + T035).
2. Đọc theo thứ tự:
   - `AGENTS.md`;
   - tệp này;
   - `docs/STATUS.md`;
   - `docs/DESIGN_SYSTEM.md`;
   - `docs/VERIFICATION.md`;
   - skill của phần việc bạn làm: `skills/pptx-motion-director/SKILL.md` hoặc
     `skills/slide-forge/SKILL.md`.
3. Chạy `python -m unittest discover -s tests`. Kết quả phải là **292 tests OK**.
4. Lấy mã task kế tiếp trong `research/tasks/INDEX.md` (hiện là **T036**). Thêm
   dòng `claimed` rồi push trước khi làm phần tốn kém.

## Đang ở đâu

- **Bốn năng lực cốt lõi**:
  - **DeckCraft Native Bridge (T035):** `scripts/deckcraft_bridge.py` kết nối trực
    tiếp với engine headless `D:\artcraft\DeckCraft\deckcraft-cli.exe`. Render slide Full HD
    (1920x1080) và trích xuất metrics cho `design_critic.py --render deckcraft` chỉ trong 1–2 giây,
    giải phóng hoàn toàn sự phụ thuộc vào LibreOffice hay Microsoft Office COM.
  - **Motion Director:** deck có sẵn, kịch bản → nhịp click → chuyển động phức hợp nhiều lớp.
  - **Morph Studio:** Morph giữa các slide (`!!`, bay vào/ra, camera, thẻ nở, cuộn ngang).
  - **Slide Forge:** dựng deck mới từ spec.
- **Hệ thiết kế (T034):** `knowledge/design_system.json` là nguồn duy nhất cho
  cái đẹp và kỹ thuật (thời lượng, easing, nhịp, tương phản, cỡ chữ, mật độ).
  Bộ sinh đọc nó, còn `scripts/design_critic.py` chấm deck theo đúng các con
  số đó (hỗ trợ cả render native DeckCraft).
- **Tiến hóa Skill for Design:** Định vị repo trở thành bộ kỹ năng thiết kế tổng
  hợp cho AI Agent (với PPTX làm nhánh tiên phong, chuẩn bị mở rộng sang WordCraft và GridCraft).

## Việc tiếp theo (xếp hạng)

1. **Tích hợp DeckCraft render vào Slide Forge và Motion Director:**
   - Thêm cờ `--render-native` vào `slide_forge.py` và `motion_director.py` để tự động
     sinh preview PNG Full HD ngay khi tạo deck.
2. **Sửa hai phát hiện của critic:**
   - MOT-SETTLE: token kết thúc lệch chỗ trước Morph orb của Forge. Cách sửa:
     đặt token ở điểm đích, chuyển động *từ* điểm đầu.
   - Thang cỡ chữ của Forge: hiện dùng 13–15 cỡ, cần đọc `type_scale_pt` từ
     Office kit.
3. **Mở rộng sang Document Craft (WordCraft):**
   - Viết bridge tương tự cho `D:\artcraft\WordCraft\wordcraft-cli.exe` để xử lý
     tài liệu DOCX/PDF chuyên nghiệp.
4. **Hiệu chỉnh critic bằng người:** Xếp hạng tay khoảng 20 deck rồi so
   Spearman với critic.

## Prompt giao việc cho model khác

```text
Continue PPTX Motion Lab & Skill for Design at https://github.com/togcoder/skill-for-pptx on branch
work/T035-deckcraft-bridge. Read AGENTS.md, HANDOFF.md, docs/STATUS.md, docs/DESIGN_SYSTEM.md and
docs/VERIFICATION.md. Run the tests (292 must pass). Take the next free ID in
research/tasks/INDEX.md (T036) and claim it.
With DeckCraft available (D:\artcraft\DeckCraft\deckcraft-cli.exe): native visual inspection
is ready via scripts/deckcraft_bridge.py or scripts/design_critic.py --render deckcraft.
New numbers go into knowledge/design_system.json, never hard-coded. Write your report
in experiments/<ID>-<date>-<agent>-<slug>/REPORT.md, add a CHANGELOG entry, rewrite
docs/STATUS.md and this HANDOFF, and open a PR.
```
