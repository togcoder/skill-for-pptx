# Handoff — Design Research Lab

Cập nhật: 04/11/2026, sau chương trình **T058–T069** (T058–T065 nền tảng; T066 deck bị chủ dự án phê bình; T067 direction + style; T068 compiler; T069a directed deck với 4 Morph; T069b narrative critic + speaker notes). Tệp này được **viết lại** mỗi lần bàn giao, không ghi nối thêm. Lịch sử nằm ở [docs/CHANGELOG.md](docs/CHANGELOG.md). Chương trình và đề bài gốc: [experiments/T057-20261104-claude-leader-review/REPORT.md](experiments/T057-20261104-claude-leader-review/REPORT.md).

> Lưu tệp văn bản bằng **UTF-8 không BOM**. `lab/tools/check_layout.py` giờ chặn mojibake, BOM, ký tự điều khiển và mã task trùng.

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Mục tiêu không đổi

Một công cụ dành cho AI để tạo file **PPTX có độ hoàn thiện cao nhất, với chuyển động thật**:
- ảnh chuyển động;
- motion graphic;
- vũ đạo theo nội dung;
- Morph.

Lab đa lĩnh vực (docx, xlsx, vector…) phục vụ mục tiêu đó, không thay thế mục tiêu đó.

## Chúng ta đang ở đâu

- `main` sau T058–T069: **556 test qua, 6 skipped**, cả khi đặt `PYTHONUTF8=1` và khi không đặt (máy Windows tiếng Việt, locale cp1258). `lab/tools/check_layout.py` OK.
- **T058–T065 đã đóng một chu kỳ gate:**

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

## Việc còn mở (ưu tiên)

1. **T070: join the four state pairs to `deck_director.py`.** Author the pairs as `direction.json` shots, compile, and compare the hand timing with the compiler's; add a short PowerPoint `CreateVideo` excerpt so Morph interpolation is frame evidence.
2. **Promote `deck_state_critic`.** It exists (`scripts/deck_state_critic.py`, experimental) and separates T066 from T069; review it, add tests, then wire it as a post-build gate in `slide_forge build`.
3. **T055 fixes** R3/R4/R6/R7/R8: camera views/Morph claim, evidence paths, review cùng họ model, v.v. Đọc `research/reviews/T055-opencode-20261104.md`.
4. **T059/T060 wiring:** T059 mới là hàm fallback + test, chưa nối `slide_forge.render`; T060 mới là prototype, chưa upstream `storytold/deckcraft`.
5. **Rung 6:** chưa ai review toàn bộ ảnh click/Morph; T058 chỉ đạt 5b, T068 mới có preview tĩnh.
6. **Template contract + generic patch** (từ T057): vẫn là khoảng trống lớn nhất so với `CxyZyr/PPTX-Template-Skills`, `pptx-style`, `OfficeCLI`, `hands-on-deck`.
7. **4:3 / 40 slide / font thiếu:** 57/57 deck tracked là 16:9, ≤12 slide; Forge vẫn hard-code 16:9.
8. **Design context:** cỡ chữ theo góc nhìn, WCAG + room lift, 134 codepoint tiếng Việt, `fontScale` — chưa thành checker.
9. **Repo weight:** T055/T059 thêm vài MB; size cap mới chỉ cảnh báo, Git LFS vẫn là quyết định mở.

## DeckCraft (ArtCraft, `D:\artcraft\DeckCraft`, v0.13.1, MIT/Apache)

- **Dùng để tạo tài sản PPTX native:** Merge Shapes, freeform cong, bevel/glow, xóa nền, SmartArt, icon — python-pptx không làm được.
- **Dùng làm static fallback có nhãn** `DeckCraft render (not PowerPoint)`, rung 2; không dùng để chấm điểm thiết kế thay PowerPoint.
- **Không dùng để kiểm chứng animation/Morph:** `render-transition` vẽ cả shape đang bị entrance ẩn; Morph camera không nội suy.
- **Không để DeckCraft là bước ghi cuối** deck đã có timing: `convert` mất 149 behavior, đổi chart build target.
- **Cơ hội upstream:** T060 đã có patch prototype `render-animation`; cần chủ dự án đồng ý trước khi mở PR cho `storytold/deckcraft`.

## Quy tắc bắt buộc

- **Mọi thay đổi product path pptx phải qua PR + review** của agent khác họ model. Product path gồm `motion_director`, `pptx_animator`, `motion_engine`, `slide_forge`, `morph_studio`, `design_critic`, `slide_navigator`, `advanced_interactivity`, `interactive_triggers`, `theme_engine` và `knowledge/design_system.json`.
- **Không tự review bài của mình. Không dùng lại mã task.** Mã trống kế tiếp: **T066**.
- **Ghi đúng rung:** mở được = 4; render/play có máy assert = 5/5b; người review = 6. Không gọi simulation là PowerPoint.
- **UTF-8 không BOM**, `encoding="utf-8"` cho mọi `read_text`.
- **Artifact ≤2 MB/file, ≤10 MB/task**; file lớn hơn giữ local và ghi hash.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch main.
Read HANDOFF.md, AGENTS.md, lab/PROTOCOL.md, domains/pptx/DOMAIN.md and
experiments/T057-20261104-claude-leader-review/REPORT.md.
Run `python -m unittest discover -s tests` and `python lab/tools/check_layout.py`.
Take the next free ID (T066) or one of the open items above; change its INDEX row to claimed
with your agent and branch, push, then work on that branch.
Try the falsifiers yourself; tag every claim with its evidence rung. Open a PR; do not push
product code to main. Ask a critic from a different model family to review in research/reviews/.
Save every text file as UTF-8 without BOM.
```
