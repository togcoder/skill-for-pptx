# Handoff — PPTX Motion Lab & Skill for Design

Cập nhật: 01/11/2026 (sau T037). Tệp này **viết lại mỗi lần bàn giao, không ghi
nối thêm**. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md) và
[docs/archive/HANDOFF-history-2026-10.md](docs/archive/HANDOFF-history-2026-10.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Bắt đầu trong 5 phút

1. Đầu nghiên cứu mới nhất nằm trên nhánh `work/T037-multi-craft-bridges` (dựa trên
   `work/T036-skill-for-design-core`, T036 + T037).
2. Đọc theo thứ tự:
   - `AGENTS.md`;
   - tệp này;
   - `docs/STATUS.md`;
   - `protocols/00_intent_empathy_decoder.md`;
   - `protocols/01_capability_first_gate.md`;
   - `protocols/02_cross_delegation_dag.md`;
   - `protocols/03_redteam_critique_rubric.md`;
   - `docs/DESIGN_SYSTEM.md`.
3. Chạy `python -m unittest discover -s tests`. Kết quả phải là **302 tests OK**.
4. Lấy mã task kế tiếp trong `research/tasks/INDEX.md` (hiện là **T038**). Thêm
   dòng `claimed` rồi push trước khi làm phần tốn kém.

## Đang ở đâu

- **Hệ sinh thái Cầu nối Đa công cụ (T037):**
  - **WordCraft Bridge (`scripts/wordcraft_bridge.py`):** Kết nối native `wordcraft-cli.exe`
    (render trang, inspect tài liệu, chuyển đổi docx/pdf/html/md, bóc tách text).
  - **GridCraft Bridge (`scripts/gridcraft_bridge.py`):** Kết nối native `gridcraft-cli.exe`
    (inspect bảng tính, eval công thức toán học/tài chính, chuyển đổi xlsx/csv/pdf, trích xuất vùng dữ liệu).
  - **VectorCraft Bridge (`scripts/vectorcraft_bridge.py`):** Kết nối native `vectorcraft-cli.exe`
    (inspect vector, convert svg/ai/pdf/png với tùy chọn artboard và scale).
  - **DeckCraft Bridge (T035):** Render slide Full HD (1920x1080) và trích xuất metrics
    cho `design_critic.py --render deckcraft` chỉ trong 1–2 giây.
- **Tầng Thấu hiểu Người dùng Thực thi (`scripts/intent_decoder.py` - T037):**
  - Đã có engine giải mã tự động từ prompt người dùng ra bản `IntentBrief` 5 chiều
    (Audience, Cognitive Budget, Viewing Context, Canonical System, Craft Routing),
    tự động kiểm chứng chống lỗi schema.
- **Universal ArtCraft Hub & Quản trị Multi-Agent (T036):**
  - `registry/artcraft_capabilities.json` quét 13 công cụ trong `D:\artcraft` (hash `21eaaf51d6891acf`).
  - Hợp đồng giao việc chéo `schemas/handoff_contract.schema.json` (max 2 vòng lặp).
  - Rubric thẩm định kép 100 điểm `schemas/critique_report.schema.json`.

## Việc tiếp theo (xếp hạng)

1. **Tích hợp Intent Decoder vào Slide Forge:**
   - Cho phép `slide_forge.py build spec.json --intent-prompt "..."` tự động nạp
     thông số nhận thức và bối cảnh trình chiếu từ Intent Decoder.
2. **Nối preview render tự động vào Forge & Director:**
   - Thêm cờ `--render-native` để mỗi khi sinh slide, máy tự động gọi DeckCraft
     sinh ảnh PNG Full HD vào thư mục `previews/`.
3. **Sửa 2 lỗi nhỏ của Critic (kế thừa từ T034):**
   - MOT-SETTLE (token kết thúc lệch chỗ trước Morph orb).
   - Thang cỡ chữ của Forge.

## Prompt giao việc cho model khác

```text
Continue PPTX Motion Lab & Skill for Design at https://github.com/togcoder/skill-for-pptx on branch
work/T037-multi-craft-bridges. Read AGENTS.md, HANDOFF.md, docs/STATUS.md and the 4 protocols in
protocols/. Run the tests (302 must pass). Take the next free ID in research/tasks/INDEX.md (T038)
and claim it. All 4 primary bridges (DeckCraft, WordCraft, GridCraft, VectorCraft) are operational,
and the Intent Decoder engine is ready in scripts/intent_decoder.py. Write your report in
experiments/<ID>-<date>-<agent>-<slug>/REPORT.md, add a CHANGELOG entry, rewrite docs/STATUS.md
and this HANDOFF, and open a PR.
```
