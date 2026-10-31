# Handoff — PPTX Motion Lab & Skill for Design

Cập nhật: 01/11/2026 (sau T036). Tệp này **viết lại mỗi lần bàn giao, không ghi
nối thêm**. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md) và
[docs/archive/HANDOFF-history-2026-10.md](docs/archive/HANDOFF-history-2026-10.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Bắt đầu trong 5 phút

1. Đầu nghiên cứu mới nhất nằm trên nhánh `work/T036-skill-for-design-core` (dựa trên
   `work/T035-deckcraft-bridge`, T035 + T036).
2. Đọc theo thứ tự:
   - `AGENTS.md`;
   - tệp này;
   - `docs/STATUS.md`;
   - `protocols/00_intent_empathy_decoder.md`;
   - `protocols/01_capability_first_gate.md`;
   - `protocols/02_cross_delegation_dag.md`;
   - `protocols/03_redteam_critique_rubric.md`;
   - `docs/DESIGN_SYSTEM.md`.
3. Chạy `python -m unittest discover -s tests`. Kết quả phải là **296 tests OK**.
4. Lấy mã task kế tiếp trong `research/tasks/INDEX.md` (hiện là **T037**). Thêm
   dòng `claimed` rồi push trước khi làm phần tốn kém.

## Đang ở đâu

- **Hệ thống Nền tảng Multi-Agent & Universal ArtCraft Hub (T036):**
  - **Universal Hub (`scripts/artcraft_hub.py`):** Cửa ngõ kết nối thống nhất tới
    toàn bộ 13 phân hệ của ArtCraft (`D:\artcraft`).
  - **Pre-flight Capability Gate (`scripts/sync_artcraft_capabilities.py`):**
    Tự động quét và cập nhật `registry/artcraft_capabilities.json` (13 công cụ, 13 CLI, hash `21eaaf51d6891acf`).
    Khóa cứng 3 cấp ưu tiên (CLI/MCP Native $\rightarrow$ Declarative Spec $\rightarrow$ Custom Script kèm `CAPABILITY_GAP_PROOF`).
  - **Tầng Thấu hiểu Người dùng (`schemas/intent_brief.schema.json`):**
    Giải mã 5 chiều: Khán giả (C-Level, Kỹ sư...), Ngân sách nhận thức (Miller/Hick, Z/F pattern),
    Bối cảnh vật lý, Hệ quy chiếu thiết kế (Swiss Grid, Dieter Rams, Tufte, IBM Carbon, Material 3) và Định tuyến công cụ.
  - **Giao thức Giao việc chéo & Khống chế Vòng lặp (`schemas/handoff_contract.schema.json`):**
    Hợp đồng giao việc chéo giữa 13 công cụ với chốt chặn cứng `max_iterations = 2` chống lặp vô tận.
  - **Rubric Thẩm định Kép 100 Điểm (`schemas/critique_report.schema.json`):**
    Thẩm định Lớp 3A (Toán học bounding-box/contrast) + Lớp 3B (Mỹ thuật trên ảnh render) với 5 điểm liệt auto-fail.
- **DeckCraft Native Bridge (T035):** Render slide Full HD (1920x1080) và trích xuất metrics
  cho `design_critic.py --render deckcraft` chỉ trong 1–2 giây.
- **Bộ máy PPTX Motion:** Motion Director, Morph Studio, Slide Forge giữ nguyên 100% độ tương thích.

## Việc tiếp theo (xếp hạng)

1. **Nối WordCraft Bridge:** Viết bridge cho `D:\artcraft\WordCraft\wordcraft-cli.exe` để xử lý
   tài liệu DOCX/PDF chuyên nghiệp theo chuẩn Swiss Typography.
2. **Nối GridCraft Bridge:** Viết bridge cho `D:\artcraft\GridCraft\gridcraft-cli.exe` để xuất
   biểu đồ dữ liệu chuẩn Edward Tufte (High Data-Ink Ratio).
3. **Tích hợp Tầng 0 (Intent Decoder) vào Slide Forge & Motion Director:**
   - Đọc trực tiếp `intent_brief.json` để tự động chọn layout và ngân sách nhận thức.
4. **Sửa 2 lỗi nhỏ của Critic (kế thừa từ T034):**
   - MOT-SETTLE (token kết thúc lệch chỗ trước Morph orb).
   - Thang cỡ chữ của Forge.

## Prompt giao việc cho model khác

```text
Continue PPTX Motion Lab & Skill for Design at https://github.com/togcoder/skill-for-pptx on branch
work/T036-skill-for-design-core. Read AGENTS.md, HANDOFF.md, docs/STATUS.md and the 4 protocols in
protocols/. Run the tests (296 must pass). Take the next free ID in research/tasks/INDEX.md (T037)
and claim it. All 13 ArtCraft tools are mapped in registry/artcraft_capabilities.json and accessible
via scripts/artcraft_hub.py. New numbers go into knowledge/design_system.json, never hard-coded.
Write your report in experiments/<ID>-<date>-<agent>-<slug>/REPORT.md, add a CHANGELOG entry, rewrite
docs/STATUS.md and this HANDOFF, and open a PR.
```
