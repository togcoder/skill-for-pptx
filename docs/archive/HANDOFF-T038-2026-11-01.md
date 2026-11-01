# Handoff — PPTX Motion Lab & Skill for Design

Cập nhật: 01/11/2026 (sau T038). Tệp này **viết lại mỗi lần bàn giao, không ghi
nối thêm**. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md) và
[docs/archive/HANDOFF-history-2026-10.md](docs/archive/HANDOFF-history-2026-10.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Bắt đầu trong 5 phút

1. Đầu nghiên cứu mới nhất nằm trên nhánh `work/T038-pptx-design-canon-tokens` (dựa trên
   `work/T037-multi-craft-bridges`, T035 + T036 + T037 + T038).
2. Đọc theo thứ tự:
   - `AGENTS.md`;
   - tệp này;
   - `docs/STATUS.md`;
   - `knowledge/design_system.json`;
   - `experiments/T038-20261101-pptx-design-canon-tokens/REPORT.md`;
   - `protocols/00_intent_empathy_decoder.md` đến `03_redteam_critique_rubric.md`.
3. Chạy `$env:PYTHONUTF8=1; python -m unittest discover -s tests`. Kết quả phải là **314 tests OK (0 failures, 4 skipped)**.
4. Lấy mã task kế tiếp trong `research/tasks/INDEX.md` (hiện là **T039**). Thêm
   dòng `claimed` rồi push trước khi làm phần tốn kém.

## Đang ở đâu

- **Hệ thống Chuẩn mực Thiết kế PPTX Canon (T038):**
  - **Single Source of Truth (`knowledge/design_system.json` v1.1.0):**
    - Đã mã hóa toán học và hình học chính xác cho khung slide $960 \times 540\text{ pt}$ ($13.333 \times 7.5\text{ in}$).
    - Vùng an toàn lề $48\text{ pt}$ ngang, $36\text{ pt}$ dọc (content box $864 \times 396\text{ pt}$ tại $x=48, y=108\text{ pt}$).
    - Vị trí Logo Watermark: góc trên bên phải ($x = 912 - w$, $y = 20\text{ pt}$, $w \le 72, h \le 24$, opacity 0.75, ẩn trên slide Title, Section, Closing, Duarte Break).
    - Breadcrumbs / Kicker: $x = 48\text{ pt}$, $y = 22\text{ pt}$, font $10\text{ pt}$ hoa tracked $+1.2\text{ pt}$.
    - Progress Bar: mép đáy $y = 537\text{ pt}$, cao $3\text{ pt}$, track 10% opacity, active fill proportional.
  - **Cân bằng Thị giác Icon (`optical_icons`):**
    - Khắc phục ảo ảnh diện tích hình học: Vuông $0.88\times$, Tròn $1.0\times$, Ngang $(1.08\times, 0.82\times)$, Tam giác $(1.05\times, \text{dịch tâm } -0.06\times\text{size})$. Badge tròn/bo $2.0\times$.
  - **Độ sâu Nền 3 Lớp (`background_layers`):**
    - Z0 Canvas (gradient $135^\circ$ Slate đậm `#0B0F19` $\rightarrow$ `#111827` hoặc Alabaster sáng `#F8FAFC` $\rightarrow$ `#EDF2F7`).
    - Z1 Ambient Radial Glow Orbs (tối đa 2 quả cầu mờ $120-160\text{ pt}$, opacity $0.12-0.18$, liên kết Morph `!!`).
    - Z2 Surface Cards (glassmorphism mờ $65-75\%$, viền sáng trên $1\text{ pt}$, bo góc $8-12\text{ pt}$, đệm trong $20-28\text{ pt}$).
  - **Bố cục Lưới Đột phá & Nancy Duarte Pattern Breaks:**
    - Lưới Bento ($7/12$ Hero Card $496 \times 396\text{ pt}$ + Top-Right $348 \times 188\text{ pt}$ + 2 Bottom-Right $164 \times 188\text{ pt}$).
    - Lưới Bất đối xứng Tỷ lệ Vàng (Major $522\text{ pt}$ / $61.8\%$ + Minor $322\text{ pt}$ / $38.2\%$).
    - Nhịp ngắt Duarte Break tự động kích hoạt trên deck $\ge 5$ slide tại mốc $1/3$ và $2/3$ (khoảng trắng $\ge 70\%$, ẩn chrome/cards, chỉ chứa 1 thông điệp đanh thép $36-44\text{ pt}$ hoặc 1 KPI khổng lồ $72-96\text{ pt}$).
  - **Bộ Lọc Đánh giá Tự động (`scripts/design_critic.py`):**
    - Kiểm tra `CHROME-SAFE`, `OPT-ICON`, `LAY-BENTO`, `DUA-BREAK` tự động qua dữ liệu đo lường, xuất log `evaluations`.
- **Hệ sinh thái Đa công cụ ArtCraft (T035–T037):**
  - Đầy đủ bridge cho `DeckCraft` (1080p render <1s), `WordCraft`, `GridCraft`, `VectorCraft`.
  - Intent & Empathy Decoder Engine (`scripts/intent_decoder.py`) triển khai Protocol 00.

## Việc tiếp theo (xếp hạng)

1. **Tích hợp Intent Decoder tự động chọn Layout Canon trong Slide Forge:**
   - Khi Intent Decoder nhận diện phong cách "Tech Executive Showcase", tự động gợi ý slide Bento Grid và Asymmetric Golden Ratio.
2. **Nối preview render tự động vào Forge & Director:**
   - Thêm cờ `--render-native` để mỗi khi sinh slide, máy tự động gọi DeckCraft sinh ảnh PNG Full HD vào thư mục `previews/`.
3. **Mở rộng kho mẫu SVG và Palette Preset theo Canons:**
   - Thêm các preset biểu tượng hình học đã chuẩn hóa theo quy tắc cân bằng thị giác.

## Prompt giao việc cho model khác

```text
Continue PPTX Motion Lab & Skill for Design at https://github.com/togcoder/skill-for-pptx on branch
work/T038-pptx-design-canon-tokens. Read AGENTS.md, HANDOFF.md, docs/STATUS.md, knowledge/design_system.json,
and experiments/T038-20261101-pptx-design-canon-tokens/REPORT.md.
Run tests with: $env:PYTHONUTF8=1; python -m unittest discover -s tests (all 314 tests must pass).
Take the next free ID in research/tasks/INDEX.md (T039) and claim it.
Write your report in experiments/<ID>-<date>-<agent>-<slug>/REPORT.md, add a CHANGELOG entry,
rewrite docs/STATUS.md and this HANDOFF, and open a PR.
```
