# Handoff — Design Research Lab

Cập nhật: 04/11/2026 tối, sau **T070** (Claude, trưởng nhóm: tổng hợp T001–T069, phản biện, lộ
trình). Tệp này được **viết lại** mỗi lần bàn giao, không ghi nối thêm. Lịch sử nằm ở
[docs/CHANGELOG.md](docs/CHANGELOG.md).

**Đọc theo thứ tự:**
1. tệp này;
2. [docs/ROADMAP.md](docs/ROADMAP.md): đích đến, 6 nguyên tắc, các chặng và đề bài; [docs/SCRIPT_TRACK.md](docs/SCRIPT_TRACK.md) cho trục kịch bản;
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

## Bốn điều trưởng nhóm muốn mọi agent biết (T070, T078)

1. **Điểm critic không phải chất lượng.** Deck T068/T069b có thẻ trống, tiêu đề bị cắt và chữ
   giữ chỗ nhưng vẫn được 4,99/5 (`experiments/T070-…/preview/critic-499-vs-eye.jpg`). Muốn nói
   "tốt hơn" thì phải có chấm A/B mù trên file `.pptx` (T071). Chủ dự án tự mở và lật slide,
   không cần video (D009). Gu học từ tác phẩm tốt của nhiều lĩnh vực, không chép (D010, T086).
2. **Gu phải nằm trong công cụ, không nằm trong script riêng.** Deck đẹp nhất (T066) là script
   viết tay 524 dòng. Đừng viết thêm deck kiểu đó làm sản phẩm. Hãy đưa phần gu vào công cụ (chặng
   2–3).
3. **Kịch bản đi trước, chuyển động là động từ của kịch bản** (T078). Không dựng deck mới khi
   kịch bản chưa được duyệt dạng chữ. Đọc [docs/SCRIPT_TRACK.md](docs/SCRIPT_TRACK.md) và kịch bản
   mẫu `experiments/T078-…/gold-script-triet-hoc-ch1.md`.
4. **Morph = danh tính vật thể giữa hai trạng thái.** Đừng chọn Morph bằng tay; hãy mô tả trạng
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

## Điều phối: bắt đầu và kết thúc mọi task như thế nào (T083)

- **Bắt đầu:**
  - `python lab/tools/coord.py board` để xem ai đang làm gì và chỗ nào chồng nhau;
  - rồi `python lab/tools/coord.py claim --agent <tên> --slug <slug> --title "[pptx] …" --id <mã giữ chỗ> --capability <id>`.

  Công cụ giữ mã (nhìn cả `main` lẫn mọi nhánh đang mở), tạo nhánh và **worktree riêng**,
  rồi in ra các quyết định ràng buộc, file thuộc năng lực đó và phản hồi của chủ dự án.
- **Ai sở hữu file nào:** `lab/capabilities.json`. Thêm script mới mà không đăng ký thì CI fail.
  Muốn làm bản thứ hai của một năng lực đã có thì phải hỏi trưởng nhóm trước.
- **Quyết định ràng buộc:** `lab/DECISIONS.md`, từ D001 đến D008.
- **Hỏi chủ dự án:** ghi vào `research/feedback/questions.md`. Đừng đoán.
- **Kết thúc:** cập nhật hàng INDEX, REPORT, CHANGELOG và mô tả PR. **Không sửa HANDOFF hay
  ROADMAP**: trưởng nhóm viết các file đó (D006), và CI sẽ chặn.

## Việc tiếp theo: đề bài đã giữ chỗ (chi tiết trong ROADMAP)

| Mã | Việc | Người làm → phản biện | Điều kiện bắt đầu |
|---|---|---|---|
| **T087** | **Skill PPTX bằng lời chỉ dẫn: [skills/pptx/SKILL.md](skills/pptx/SKILL.md)** — lối vào cho mọi việc PPTX | Claude | **xong; chủ dự án chấm demo 7/10** |
| **T093** | **Đồng bộ bộ slide chắp vá của người khác: [mục 10](skills/pptx/guides/10-dong-bo-slide-co-san.md)** + diễn tập trên bộ QCC giả | Claude | **xong; chờ chủ dự án mở cặp trước/sau** |
| **T094** | Diễn tập mù: model khác họ đồng bộ cùng bộ chắp vá chỉ bằng mục 10 | DSH → Claude | **xong; chuyển động tốt, xương cá bị vẽ sang dạng khác** |
| **T095** | Sửa mục 10 và đồ nghề theo T094: giữ hình sơ đồ chuẩn và notes của tác giả, slide không mở ra trắng | Claude → DSH | **xong; chờ dùng trên bộ slide thật** |
| **T089** | Sửa mặc định gây hại: Forge (KPI 0, thu chữ 14 pt, trang trí cứng, `!!orb`), Director (bìa 6 lần bấm, Morph khắp nơi), báo tràn chữ sai khi thiếu font | OpenCode → Claude | **ngay** |
| **T090** | Model nhỏ dùng skill: sửa theo mẫu đã duyệt, chủ dự án mở và chấm | DSH → Claude | **xong (merge #70); chủ dự án chấm** |
| **T086** | **Nghiên cứu gu đám đông đa lĩnh vực → luật gu, mỗi luật kiểm chứng bằng một cặp `.pptx` chấm mù** ([ROADMAP](docs/ROADMAP.md)) | Claude hoặc Gemini → model khác họ | **ngay, song song** |
| **T078** | **Trục kịch bản: phương pháp + kịch bản mẫu Triết học ch. 1** ([SCRIPT_TRACK](docs/SCRIPT_TRACK.md)) | Claude | **xong, chờ chủ dự án đọc** |
| T079 | Model yếu + phương pháp có viết được kịch bản tốt? (A/B mù bản chữ) | OpenCode → Claude | sau khi T078 được duyệt |
| T080 | Kiểm chứng bảng động từ → chuyển động | OpenCode → Claude | cần T073 |
| T081 | Skill `script-writer` (phiếu + khung + bảng động từ + ví dụ vàng) | Claude → OpenCode | sau khi T078 được duyệt |
| T082 | Ví dụ vàng 2–5 (báo cáo, pitch, quy trình, so sánh) | Claude → chủ dự án duyệt | sau T081 |
| T071 | Bộ đề vàng 8 đề + trang chấm A/B + hiệu chỉnh critic | Claude → OpenCode | ngay |
| T072 | Cổng lỗi thị giác trên khung hình (cắt chữ, thẻ trống, chữ giữ chỗ, chữ nhỏ, mất style, va chạm) | OpenCode → Claude | ngay |
| T073 | Máy xem chuyển động nhanh: DeckCraft `render-animation` vs ghi slideshow bằng harness | Claude desktop → OpenCode | ngay |
| T074 | Bộ luật ghép Morph từ ma trận ≥ 30 thí nghiệm PowerPoint | OpenCode → Claude | ngay |
| T075 | `scene.json` + trình biên dịch cảnh | Claude → Antigravity | **tạm dừng (D011)** |
| T076 | Thư viện 10 nước Morph có khung hình mẫu | OpenCode → Claude | sau T074 |
| T077 | Deck Director xuất cảnh; bỏ ánh xạ chuỗi con và giá trị bịa | Antigravity → Claude | **tạm dừng (D011)** |

Mã trống kế tiếp: do `coord.py claim` tính (hiện là **T096**).

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
Run `python lab/tools/coord.py board`, then take ONE reserved brief whose start condition is
met with `python lab/tools/coord.py claim --agent <you> --slug <slug> --title "<title>" --id <ID>
--capability <id>`. Work only in the worktree it creates. Do only that brief in this session.
Read lab/DECISIONS.md; ask the owner in research/feedback/questions.md instead of guessing.
Do not edit HANDOFF.md or docs/ROADMAP.md. Try its falsifiers yourself; tag every claim with
its evidence rung; never use critic scores as proof of quality. Open a PR; do not push product
code to main. Ask the critic named in the brief (a different model family) to review in
research/reviews/. Save every text file as UTF-8 without BOM.
```
