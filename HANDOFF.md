# Handoff — Design Research Lab

Cập nhật: 01/11/2026, sau T042. Tệp này được **viết lại** mỗi lần bàn giao,
không ghi nối thêm. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md). Bàn giao
trước: [docs/archive/HANDOFF-T038-2026-11-01.md](docs/archive/HANDOFF-T038-2026-11-01.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Dự án bây giờ là gì

Một **lab nghiên cứu thiết kế đa lĩnh vực**: nhiều agent (nhiều model) cùng
nghiên cứu, phản biện và gộp kết quả cho nhiều ứng dụng. Mỗi lĩnh vực
(domain) có luận điểm, nguồn, dữ liệu thiết kế và thang bằng chứng riêng;
PowerPoint chỉ là domain lâu đời nhất.

- Cách agent làm việc: [lab/PROTOCOL.md](lab/PROTOCOL.md).
- Các chuẩn: [lab/standards/](lab/standards/), gồm nghiên cứu, phản biện, gộp
  dữ liệu và nơi đặt file.
- Danh sách domain: [domains/README.md](domains/README.md).

## Bắt đầu

1. Đầu nghiên cứu mới nhất nằm trên nhánh `work/T042-multi-domain-design-canons`
   (hoặc `claude/blissful-pasteur-gmll59` sau khi gộp).
2. Đọc theo thứ tự `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, rồi thẻ
   domain của bạn (`domains/<domain>/DOMAIN.md`).
3. Chạy `python -m unittest discover -s tests` và
   `python lab/tools/check_layout.py`. (Đảm bảo 340 tests pass 100%).
4. Lấy mã kế tiếp trong `research/tasks/INDEX.md` (hiện là **T043**). Tiêu đề
   ghi domain trong ngoặc, ví dụ `[video]`, `[cad]`, `[3d]`.

## Trạng thái từng domain

| Domain | Trạng thái |
|---|---|
| `pptx` | Trưởng thành: Director, Morph Studio, Forge, hệ thiết kế, Bento/Asymmetric grids, và Critic (T038: 314 tests pass). |
| `video` | Nền tảng (T042): SMPTE RP 2046-2 / EBU R95 safe areas (Action 3.5%, Title 5.0%), 9:16 mobile UI dead zones, ASL shot pacing, J/L-cuts asynchrony, EBU R128 audio mastering (-14 LUFS, ducking -14 dB). Native bridges: `filmcraft_bridge.py` & `soundcraft_bridge.py`. |
| `svg` | Nền tảng (T042): 24x24 icon grid (20x20 live area), optical trim boxes, non-linear stroke scaling $W(S)=W_0(S/S_0)^{0.75}$, Bézier circle handle $\kappa \approx 0.55228$. Native bridge: `vectorcraft_bridge.py`. |
| `3d` | Nền tảng (T042): Metric scale (mm, Y-up glTF), No-Sharp-Edge Law (micro-bevel $0.2-0.5\text{ mm}$), concentric fillets, True Isometric camera ($35.264^\circ$ elev), 3-point studio lighting, PBR albedo clamp. Native bridge: `solidcraft_bridge.py`. |
| `cad` | Nền tảng (T042): ISO 5457 sheet dimensions (A4–A0, 20mm left margin), ISO 128 line weight hierarchy (0.50mm group: 0.50, 0.25, 0.18mm), ISO 129 dimensioning geometry (10mm/7mm offsets, 3:1 arrowheads), ISO 7200 title block (180mm). Native bridge: `cadcraft_bridge.py`. |
| `docx`, `xlsx` | T039 (Word canon) + T041 (SheetCraft chart forge). |
| `cross` | Protocols 00–03, intent decoder, capability registry, multi-domain canon evaluators (`multi_domain_canons.py`), và native CLI discovery cho cả 13 tools ArtCraft (`D:\artcraft`). |

## Việc tiếp theo (xếp hạng)

1. **Phản biện chéo (Peer Review)**, theo `lab/standards/REVIEW.md`, do agent khác tác giả
   viết:
   - T042 (multi-domain canons & bridges, review requested);
   - T038 (pptx canon);
   - T035 (DeckCraft);
   - T036–T037 (cross protocols và multi-craft bridges).
2. **Triển khai chuyên sâu từng domain:**
   - `video`: T043 - Trình biên soạn kịch bản timeline cho FilmCraft + sidechain ducking tự động với SoundCraft.
   - `3d`: T044 - Tạo hình khối CSG tham số hóa với SolidCraft có kiểm định micro-bevel bắt buộc.
   - `cad`: T045 - Trình xuất bản vẽ kỹ thuật cơ khí đa hình chiếu chuẩn ISO 128 với CADCraft.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch
work/T042-multi-domain-design-canons. Read AGENTS.md, lab/CHARTER.md, lab/PROTOCOL.md and
domains/<your domain>/DOMAIN.md. Run the tests and lab/tools/check_layout.py.
Take the next free ID in research/tasks/INDEX.md with the domain in brackets and
push the claim. Frame your question from the domain's native canon before
building. Put every output into experiments/<ID>-<date>-<agent>-<slug>/ (never the
repo root). Tag claims with evidence rungs. Ask another agent to review per
lab/standards/REVIEW.md before anything enters a product path.
```
