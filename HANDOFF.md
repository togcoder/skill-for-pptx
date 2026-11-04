# Handoff — Design Research Lab

Cập nhật: 04/11/2026, sau **T057** (Claude, đánh giá vai trò trưởng nhóm). Tệp này được
**viết lại** mỗi lần bàn giao, không ghi nối thêm. Lịch sử nằm ở
[docs/CHANGELOG.md](docs/CHANGELOG.md). Bản đánh giá đầy đủ và các đề bài tiếp theo:
[experiments/T057-20261104-claude-leader-review/REPORT.md](experiments/T057-20261104-claude-leader-review/REPORT.md).

> Lưu tệp văn bản bằng **UTF-8**. Bản HANDOFF trước bị lỗi mã hóa (UTF-8 bị đọc thành
> cp1252 rồi lưu lại). Nó ghi mã kế tiếp là T047, trong khi mã đúng lúc đó là T057.

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Mục tiêu không đổi

Mục tiêu là một công cụ dành cho AI để tạo file **PPTX có độ hoàn thiện cao nhất, với chuyển động thật**:
- ảnh chuyển động;
- motion graphic;
- vũ đạo theo nội dung;
- Morph.

Lab đa lĩnh vực (docx, xlsx, vector…) phục vụ mục tiêu đó. Nó không thay thế mục tiêu đó.

## Chúng ta đang ở đâu

- `main` @ sau T057: **461 test qua** (`python -m unittest discover -s tests`, 4 test bỏ qua).
- **PPTX lõi đã trưởng thành và đã được PowerPoint render.** Gồm:
  - Motion Director, Morph Studio và Slide Forge;
  - 198 preset `ppt:`;
  - hệ thiết kế cùng critic.
- **Lõi PPTX đứng yên từ T038 (01/11).** Ba vấn đề của T034 vẫn còn mở:
  - deck có 13 cỡ chữ, trong khi chuẩn là 3–6;
  - lỗi MOT-SETTLE;
  - chưa ai bấm thử tương tác trong slideshow thật.
- **T035–T056 mở rộng theo bề ngang** sang docx, xlsx, vector, 3D, CAD và video.
  Phần lớn do OpenCode/DeepSeek và Antigravity làm, và chỉ Argon review.
- **Còn treo, chưa gộp:**
  - `work/T054-opencode-vector-match`;
  - `work/T055-opencode-pptx-3d`. Nhánh này xếp chồng trên T054 và sẽ được tách ra ở T064.

## Khó khăn chính (chi tiết trong báo cáo T057)

1. **Thiếu kiểm chứng thật.** Các tính năng tương tác (T048b/T049) được ghi là "100% working",
   nhưng mới ở rung 4: PowerPoint đọc được trigger, chưa ai bấm thử trong slideshow.
2. **Mở rộng bề ngang trước khi đào sâu.** 8/22 task là pptx nhưng không task nào đóng được
   gate nào của pptx.
3. **Quy trình hỏng khi nhiều agent chạy song song.**
   - 5 mã task bị dùng trùng: T042, T043, T047, T048, T049.
   - Code pptx được đẩy thẳng lên `main`, không qua PR hay review.
   - Chỉ có một người review.
4. **Lớp timing bị phân mảnh.** Ba module viết `interactiveSeq` riêng rẽ.
5. **Lỗi Forge mà người dùng nhìn thấy.**
   - Khi in hoặc xuất PDF, số count-up bị chồng lên nhau.
   - Thanh highlight lệch so với chữ căn giữa.
6. **Repo nặng.** `.git` 116 MB, 392 file media/office.

## DeckCraft (ArtCraft, `D:\artcraft\DeckCraft`, v0.13.1, MIT/Apache)

- **Dùng để tạo tài sản PPTX native.** DeckCraft có 330 lệnh, chạy qua CLI hoặc MCP:
  - Merge Shapes;
  - freeform dạng cong;
  - hiệu ứng bevel/glow;
  - xóa nền ảnh;
  - SmartArt;
  - icon.

  python-pptx không làm được các việc này.
- **Dùng để xem trước Morph nhanh,** khoảng 0,2 giây. Độ chính xác so với PowerPoint chưa
  được kiểm chứng (T059).
- **Không dùng để kiểm chứng chuyển động trong slide.** DeckCraft không render timeline
  animation, nên việc này vẫn cần PowerPoint CreateVideo.
- **Không để DeckCraft là bước ghi cuối** một deck mà ta đã viết timing, vì `convert` viết lại
  một số node.

## Việc tiếp theo: đề bài đã giữ chỗ

Hãy nhận đúng mã đã giữ dưới đây. Sửa hàng tương ứng trong
`research/tasks/INDEX.md` thành `claimed` cùng tên agent và nhánh, rồi push trước khi làm.
Mã trống kế tiếp cho việc mới là **T066**.

| Mã | Việc | Người làm → người phản biện (khác họ model) |
|---|---|---|
| T058 | [pptx] Harness bấm chuột tự động trong slideshow và chụp kết quả | Claude desktop → Argon |
| T059 | [pptx] DeckCraft làm renderer thứ hai: ma trận độ khớp tĩnh/Morph, bảng mất mát khi lưu lại | OpenCode → Claude |
| T060 | [pptx] Đọc mã nguồn DeckCraft: khả năng render khung hình animation trong slide | Claude → OpenCode |
| T061 | [pptx] Một module duy nhất viết tương tác (interactiveSeq, trigger, hyperlink) | OpenCode → Claude |
| T062 | [pptx] Nhà máy tài sản native qua lệnh DeckCraft, so với tuyến SVG và GLB | Antigravity → Claude |
| T063 | [pptx] Nợ Forge: count-up an toàn khi in, căn highlight, thang cỡ chữ, MOT-SETTLE | OpenCode → Argon |
| T064 | [pptx] Tách T055 (3D native) khỏi T054, review, thử Morph giữa hai góc camera 3D | Claude → OpenCode |
| T065 | [cross] Vệ sinh lab: sửa mã hóa, chặn trùng mã task, bắt buộc PR cho pptx, giới hạn kích thước artifact | bất kỳ → chủ dự án |

**Đóng băng một chu kỳ:**
- Không mở domain hay canon mới cho video, 3D (trừ T064) và CAD cho đến khi T058–T061 được review.
- docx, xlsx và vector chỉ tiếp tục khi chủ dự án yêu cầu.

## Quy tắc bắt buộc (nhắc lại)

- **Mọi thay đổi vào product path pptx phải qua PR và có review** của agent thuộc họ model
  khác. Product path pptx gồm `motion_director`, `pptx_animator`, `motion_engine`,
  `slide_forge`, `morph_studio`, `design_critic` và các module tương tác.
- **Không tự review bài của mình. Không dùng lại mã task.**
- **Ghi đúng rung bằng chứng.** "PowerPoint mở được" là rung 4, "PowerPoint render" là rung 5,
  "bấm thử trong slideshow hoặc người xem" là rung 6.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch main.
Read HANDOFF.md, AGENTS.md, lab/PROTOCOL.md, domains/pptx/DOMAIN.md and
experiments/T057-20261104-claude-leader-review/REPORT.md. Run the tests.
Take one reserved brief (T058–T065): change its INDEX row to claimed with your agent and
branch, push, then work on that branch. Try the brief's falsifiers yourself and tag every
claim with its evidence rung. Open a PR; do not push product code to main. Ask the critic
named in the brief to review in research/reviews/. Save every text file as UTF-8.
```
