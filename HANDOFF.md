# Handoff — PPTX Motion Lab

Cập nhật: 19/10/2026 (sau T034). Tệp này **viết lại mỗi lần bàn giao, không ghi
nối thêm**. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md) và
[docs/archive/HANDOFF-history-2026-10.md](docs/archive/HANDOFF-history-2026-10.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Bắt đầu trong 5 phút

1. Đầu nghiên cứu mới nhất **không phải `main`**. Hãy fetch và làm việc trên
   nhánh `claude/blissful-pasteur-gmll59`, tức T033 cộng với T034. `main`
   (`bb82c70`) mới dừng ở T023.
2. Đọc theo thứ tự:
   - `AGENTS.md`;
   - tệp này;
   - `docs/STATUS.md`;
   - `docs/DESIGN_SYSTEM.md`;
   - `docs/VERIFICATION.md`;
   - skill của phần việc bạn làm: `skills/pptx-motion-director/SKILL.md` hoặc
     `skills/slide-forge/SKILL.md`.
3. Chạy `python3 -m unittest discover -s tests`. Kết quả phải là 289 tests OK.
4. Lấy mã task kế tiếp trong `research/tasks/INDEX.md` (hiện là **T035**). Thêm
   dòng `claimed` rồi push trước khi làm phần tốn kém.

## Đang ở đâu

- **Ba đường sản phẩm**:
  - Motion Director: deck có sẵn, kịch bản → nhịp click → chuyển động phức hợp
    nhiều lớp.
  - Morph Studio: Morph giữa các slide (`!!`, bay vào/ra, camera, thẻ nở,
    cuộn ngang).
  - Slide Forge: dựng deck mới từ spec.
- **Hệ thiết kế (T034)**: `knowledge/design_system.json` là nguồn duy nhất cho
  cái đẹp và kỹ thuật (thời lượng, easing, nhịp, tương phản, cỡ chữ, mật độ).
  Bộ sinh đọc nó, còn `scripts/design_critic.py` chấm deck theo đúng các con
  số đó. Báo cáo của Director, Forge và Morph Studio đều có phần critique.
- **Bằng chứng**:
  - PowerPoint 16.0 đã đọc và render (CreateVideo) một phần hệ thống.
  - **Chưa deck nào được trình chiếu tương tác bằng click trong PowerPoint.**
  - Ma trận đầy đủ nằm trong `docs/STATUS.md`.
- **Thử nghiệm, đã cách ly**: `morph_playbook.py`, `cognitive_pacing.py`,
  `interactive_triggers.py` (T033). Không dùng trong sản phẩm.

## Việc tiếp theo (xếp hạng)

1. **Cổng native** (cần Windows + PowerPoint):
   - Phát `experiments/T028-…/output/T028_*_pro.pptx`, một deck Forge
     cinematic và các deck dark-brand của T034.
   - Ghi nhận easing, xung `autoRev`, helper có hiện trên nền tối không, Morph
     ghép `!!`, hiện tượng "giật về" trước Morph.
   - Quy trình: `docs/VERIFICATION.md`.
2. **Sửa hai phát hiện của critic** (chạy được trên cloud):
   - MOT-SETTLE: token kết thúc lệch chỗ trước Morph orb của Forge. Cách sửa:
     đặt token ở điểm đích, chuyển động *từ* điểm đầu.
   - Thang cỡ chữ của Forge: hiện dùng 13–15 cỡ, cần đọc `type_scale_pt` từ
     Office kit.
3. **Hiệu chỉnh critic bằng người**: xếp hạng tay khoảng 20 deck rồi so
   Spearman với critic.
4. **Gộp đầu nghiên cứu vào `main` qua PR.** Chủ dự án quyết định.

## Prompt giao việc cho model khác

```text
Continue PPTX Motion Lab at https://github.com/togcoder/skill-for-pptx on branch
claude/blissful-pasteur-gmll59 (the research tip; main is behind). Read AGENTS.md,
HANDOFF.md, docs/STATUS.md, docs/DESIGN_SYSTEM.md and docs/VERIFICATION.md. Run the
tests (289 must pass). Take the next free ID in research/tasks/INDEX.md and claim it.
With Windows + PowerPoint: do the native gate (HANDOFF item 1, docs/VERIFICATION.md).
Otherwise: fix item 2 with a failing critic finding first and a regression test.
New numbers go into knowledge/design_system.json, never hard-coded. Write your report
in experiments/<ID>-<date>-<agent>-<slug>/REPORT.md, add a CHANGELOG entry, rewrite
docs/STATUS.md and this HANDOFF, and open a PR. Never claim playback below rung 6.
```
