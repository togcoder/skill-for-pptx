# Handoff — Design Research Lab

Cập nhật: 04/11/2026 tối, sau **T070** (Claude, trưởng nhóm: tổng hợp T001–T069, phản biện, lộ
trình). Tệp này được **viết lại** mỗi lần bàn giao, không ghi nối thêm. Lịch sử nằm ở
[docs/CHANGELOG.md](docs/CHANGELOG.md).

**Đọc theo thứ tự:**
1. tệp này;
2. [docs/ROADMAP.md](docs/ROADMAP.md): đích đến, 6 nguyên tắc, các chặng và đề bài;
3. [T070 REPORT](experiments/T070-20261104-claude-lead-synthesis/REPORT.md): tổng hợp và phản
   biện;
4. `AGENTS.md`, `lab/PROTOCOL.md`, `domains/pptx/DOMAIN.md`.

> Lưu tệp văn bản bằng **UTF-8 không BOM**. `lab/tools/check_layout.py` chặn mojibake, BOM, ký
> tự điều khiển và mã task trùng.

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Mục tiêu không đổi

Một công cụ dành cho AI để tạo file **PPTX có độ hoàn thiện cao nhất, với chuyển động thật**: ảnh
chuyển động, motion graphic, vũ đạo theo nội dung, Morph. Chất lượng phải đủ để chủ dự án chọn nó
thay vì deck làm tay. Lab đa lĩnh vực phục vụ mục tiêu đó và đang **đóng băng**.

## Ba điều trưởng nhóm muốn mọi agent biết (T070)

1. **Điểm critic không phải chất lượng.** Deck T068/T069b có thẻ trống, tiêu đề bị cắt và chữ
   giữ chỗ nhưng vẫn được 4,99/5 (`experiments/T070-…/preview/critic-499-vs-eye.jpg`). Muốn nói
   "tốt hơn" thì phải có chấm A/B của chủ dự án (T071).
2. **Gu phải nằm trong công cụ, không nằm trong script riêng.** Deck đẹp nhất (T066) là script
   viết tay 524 dòng. Đừng viết thêm deck kiểu đó làm sản phẩm. Hãy đưa phần gu vào công cụ (chặng
   2–3).
3. **Morph = danh tính vật thể giữa hai trạng thái.** Đừng chọn Morph bằng tay; hãy mô tả trạng
   thái (chặng 2). Các luật đã biết:
   - tên `!!` ép ghép;
   - vật thể có entrance bị ẩn trong lúc Morph (T059);
   - model 3D phải chung part (T064).

## Chúng ta đang ở đâu

- `main` sau T069a: **556 test qua, 6 skipped**. `check_layout.py` OK.
- Kết quả từng task T058–T069b (do agent ghi; điểm critic trong bảng **chưa được hiệu chỉnh**,
  xem T070 P1):

| Task | Kết quả thật |
|---|---|
| T058 | Harness bấm trigger trong slideshow thật. 5 run / 25 step pass trên T049 + T048b; 9/9 cạnh điều hướng. Rung **5b**, chưa rung 6. |
| T059 | DeckCraft vs PowerPoint: tĩnh gần (mean 0.5–1.5/255) nhưng chart (13.1), SVG icon (49.0), gradient 3 stop (14.2) vỡ; `render-transition` **không phải** Morph; `convert` mất 149 behavior. Không dùng làm last writer. |
| T060 | `deckcraft-anim` có player thật; prototype 151 dòng thêm `render-animation`; timing khớp tốt, preset chỉ 67/198 exact/path; repeat bị bỏ. Chưa upstream. |
| T061 | Một writer `interactiveSeq`/trigger/hyperlink trong `pptx_animator.py`; T048b rebuild byte-identical; T049 giữ 8 sequence. |
| T062 | DeckCraft native shape thắng SVG/GLB: 20/20 part target được, 21 animation, 25 KB. Merge đổi id, phải inspect lại trước khi animate. |
| T063 | Forge hết nợ người dùng thấy: 13–15 → **6 cỡ chữ**, không còn TYP-SIZES/MOT-SETTLE trên 5 deck; critic 4.36–4.53 → **4.70–4.88**. |
| T064 | T055 tách khỏi T054 (blockout đóng băng, GLB byte-identical). **3D Camera Morph Law:** chỉ nội suy khi các slide dùng chung một `model3d` part; mỗi slide một embed thì fade + 0.40 s trắng. |
| T065 | Sửa mojibake 5 tệp, 12 `read_text()` thiếu encoding, check_layout mới, CI Ubuntu+Windows, rule PR/review, cảnh báo size cap. |
| T066 | Deck 10 slide “Triết học Mác – Lênin, Chương 1”: đỏ son, Palatino, ảnh cắt nền duotone, 144 effect, 9 Morph. Chủ dự án chấp nhận cắt ảnh/theme/font nhưng **bác chuyển động và thứ tự ảnh**: motion không có *gu*, ảnh vĩ nhân hiện cuối vô nghĩa. |
| T067 | Chạy 4 luồng song song: audit skill (17 finding), image choreography (25 luật, A/B), motion dramaturgy (51→27 click, 144→116 effect, 0 empty base, 0 ảnh cuối, 0 Morph), `VisualStyle/1` + 5 preset (631 KB, 5 specimen). Kết luận: thiếu **direction**, không thiếu effect; 0 Morph là reset, đích là **3–4 semantic Morph**. |
| T068 | `deck_director.py` + schema + `slide_forge --plan`: Two-Pass screenplay (state machine trước, lời thoại sau), lifecycle enter/dim/highlight/exit, 5 luật cứng (`NAR-CODA-TRAP`, `NAR-KARAOKE`, `NAR-UNANCHORED`, `NAR-COLLISION`, `DEN-ACTIVE-VIEW`). Proof 3 slide: critic 4.99, 6 lifecycle, 0 empty base. |
| T069a | Directed deck thật: **14 slide, 9 click, 61 effect, 4 Morph 1.2 s, 17 shape lifecycle**, 0 base trống, 0 ảnh cuối, max 45 từ/view, 5 cỡ chữ; timeline đổi thành Engels 1848 → Marx 1867 → Lenin 1917. `deck_state_critic.py` fail T066 (58 gate) / pass T069a (0); critic 4.33 (narrative 4.92). Chưa quay Morph frame-by-frame. |
| T069b | Narrative critic (dimension thứ 6 trong `design_critic.py`), speaker notes `[T=0]`/`[CLICK]`, exit lifecycle, scaffold hai pass. T066 narrative 2.70 vs T068/T069 5.00; 12/12 test; deck scaffold 4.84, 4 lifecycle. |

- **T058 + T061 integration:** hai lỗi T058 tìm thấy (T032 writer bị PowerPoint từ chối; thiếu `stCondLst`) **đã hết** sau T061. Fixture rebuild mở được, XML có `stCondLst`/`onClick`.
- **T055 giờ nằm trên `main` nhưng là EXPERIMENTAL**, review `accept-with-fixes`; R3/R4/R6/R7/R8 còn mở. R3 là claim “named camera views + Morph” chưa đúng với deck gốc.
- **T054 vector vẫn chưa merge.** T055 không còn phụ thuộc T054.

## Việc tiếp theo: đề bài đã giữ chỗ (chi tiết trong ROADMAP)

| Mã | Việc | Người làm → phản biện | Điều kiện bắt đầu |
|---|---|---|---|
| T071 | Bộ đề vàng 8 đề + trang chấm A/B + hiệu chỉnh critic | Claude → OpenCode | ngay |
| T072 | Cổng lỗi thị giác trên khung hình (cắt chữ, thẻ trống, chữ giữ chỗ, chữ nhỏ, mất style, va chạm) | OpenCode → Claude | ngay |
| T073 | Máy xem chuyển động nhanh: DeckCraft `render-animation` vs ghi slideshow bằng harness | Claude desktop → OpenCode | ngay |
| T074 | Bộ luật ghép Morph từ ma trận ≥ 30 thí nghiệm PowerPoint | OpenCode → Claude | ngay |
| T075 | `scene.json` + trình biên dịch cảnh | Claude → Antigravity | sau T071–T072 |
| T076 | Thư viện 10 nước Morph có khung hình mẫu | OpenCode → Claude | sau T074 |
| T077 | Deck Director xuất cảnh; bỏ ánh xạ chuỗi con và giá trị bịa | Antigravity → Claude | sau T075 |

Mã trống kế tiếp cho việc ngoài danh sách: **T078**.

**Dừng ngay:**
- vá thêm luật chuỗi con trong `deck_director.py`;
- báo điểm narrative hoặc overall như bằng chứng chất lượng;
- mở domain mới;
- viết deck "đẹp nhất" bằng script riêng rồi gọi đó là sản phẩm.

**Phản hồi của chủ dự án** nằm ở `research/feedback/`. Mỗi đề bài phải ghi nó xử lý mục nào
(F1, F2…). Chỉ chủ dự án được đóng mục.

## DeckCraft (ArtCraft, `D:\artcraft\DeckCraft`, v0.13.1, MIT/Apache)

- **Dùng để tạo tài sản PPTX native:** Merge Shapes, freeform cong, bevel/glow, xóa nền, SmartArt, icon — python-pptx không làm được.
- **Dùng làm static fallback có nhãn** `DeckCraft render (not PowerPoint)`, rung 2; không dùng để chấm điểm thiết kế thay PowerPoint.
- **Không dùng để kiểm chứng animation/Morph:** `render-transition` vẽ cả shape đang bị entrance ẩn; Morph camera không nội suy.
- **Không để DeckCraft là bước ghi cuối** deck đã có timing: `convert` mất 149 behavior, đổi chart build target.
- **Cơ hội upstream:** T060 đã có patch prototype `render-animation`; cần chủ dự án đồng ý trước khi mở PR cho `storytold/deckcraft`.

## Quy tắc bắt buộc

- **Một phiên agent làm một đề bài.** Không nhận việc mới giữa chừng; phản hồi mới thì ghi vào
  sổ phản hồi.
- **Mọi thay đổi product path PPTX phải qua PR và có review** của agent khác họ model (Claude /
  Gemini / DeepSeek). Product path gồm `motion_director`, `pptx_animator`, `motion_engine`,
  `slide_forge`, `morph_studio`, `design_critic`, `deck_director`, `slide_navigator`,
  `advanced_interactivity`, `interactive_triggers`, `theme_engine` và
  `knowledge/design_system.json`.
- **Không tự review bài của mình. Không dùng lại mã task.** Tối đa 3 task PPTX mở cùng lúc.
- **Ghi đúng rung:**
  - đếm XML là rung 1;
  - DeckCraft là rung 2;
  - PowerPoint mở được là rung 4;
  - khung hình PowerPoint là rung 5 hoặc 5b;
  - người xem là rung 6.
- **Không bịa nội dung hoặc số liệu.** Thiếu thì trả mã lỗi.
- **Không làm việc trong checkout của người khác;** dùng `git worktree`.
- **UTF-8 không BOM,** `encoding="utf-8"` cho mọi `read_text`. Artifact ≤ 2 MB mỗi file, ≤ 10 MB
  mỗi task.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch main.
Read HANDOFF.md, docs/ROADMAP.md, experiments/T070-20261104-claude-lead-synthesis/REPORT.md,
AGENTS.md, lab/PROTOCOL.md and domains/pptx/DOMAIN.md.
Run `python -m unittest discover -s tests` and `python lab/tools/check_layout.py`.
Take ONE reserved brief from the HANDOFF table whose start condition is met. Change its INDEX
row to claimed with your agent and branch, push, then work in your own git worktree on that
branch. Do only that brief in this session. Try its falsifiers yourself; tag every claim with
its evidence rung; never use critic scores as proof of quality. Open a PR; do not push product
code to main. Ask the critic named in the brief (a different model family) to review in
research/reviews/. Save every text file as UTF-8 without BOM.
```
