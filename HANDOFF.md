# Handoff — Design Research Lab

Cập nhật: 01/11/2026, sau T044. Tệp này được **viết lại** mỗi lần bàn giao,
không ghi nối thêm. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md). Bàn giao
trước: [docs/archive/HANDOFF-T038-2026-11-01.md](docs/archive/HANDOFF-T038-2026-11-01.md).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Dự án bây giờ là gì

Một **lab nghiên cứu thiết kế đa lĩnh vực (Cross-Domain Agentic AI Lab)**: nhiều agent
(nhiều model) cùng nghiên cứu, phản biện và xâu chuỗi kết quả cho nhiều ứng dụng.
Mỗi lĩnh vực (domain) có luận điểm, nguồn, dữ liệu thiết kế và thang bằng chứng riêng;
PowerPoint chỉ là domain lâu đời nhất.

- Cách agent làm việc: [lab/PROTOCOL.md](lab/PROTOCOL.md).
- Các chuẩn: [lab/standards/](lab/standards/), gồm nghiên cứu, phản biện, gộp
  dữ liệu và nơi đặt file.
- Danh sách domain: [domains/README.md](domains/README.md).
- Quy tắc xâu chuỗi đa tài nguyên & tự do cục bộ: [lab/protocols/04_cross_asset_pipeline.md](lab/protocols/04_cross_asset_pipeline.md).

## Bắt đầu

1. Đầu nghiên cứu mới nhất đã được gộp lên `main`.
2. Đọc theo thứ tự `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, rồi thẻ
   domain của bạn (`domains/<domain>/DOMAIN.md`).
3. Chạy `python -m unittest discover -s tests` và
   `python lab/tools/check_layout.py`. (Đảm bảo tất cả tests pass 100%).
4. Lấy mã kế tiếp trong `research/tasks/INDEX.md` (hiện là **T047**). Tiêu đề
   ghi domain trong ngoặc, ví dụ `[pptx]`, `[video]`, `[3d]`, `[cad]`, `[docx]`, `[xlsx]`.

## Trạng thái từng domain

| Domain | Trạng thái |
|---|---|
| `cross` | Protocols 00–04 (Intent Decoder, Capability Gate, Delegation DAG, Red-team Rubric, **Cross-Asset Pre-processing Pipeline & Local Autonomy Charter** - T044). Validator `scripts/cross_pipeline.py`. Toàn quyền tải font/model và cài đặt thư viện cục bộ sạch sẽ. |
| `pptx` | Trưởng thành: Director, Morph Studio, Forge, hệ thiết kế Bento/Asymmetric grids, Critic, và **Dynamic Theme Engine (T043)**: Area-weighted reference teardown, Composite Background Architecture (Layered translucent PNGs, alpha stats, shape opacity), Need-based semantic synthesizer (5 archetypes), OKLCH 60-30-10, AI Image visual harmonizer. |
| `video` | Nền tảng (T042): SMPTE RP 2046-2 / EBU R95 safe areas (Action 3.5%, Title 5.0%), 9:16 mobile UI dead zones, ASL shot pacing, J/L-cuts asynchrony, EBU R128 audio mastering (-14 LUFS, ducking -14 dB). Native bridges: `filmcraft_bridge.py` & `soundcraft_bridge.py`. |
| `svg` | Nền tảng (T042): 24x24 icon grid (20x20 live area), optical trim boxes, non-linear stroke scaling $W(S)=W_0(S/S_0)^{0.75}$, Bézier circle handle $\kappa pprox 0.55228$. Native bridge: `vectorcraft_bridge.py`. |
| `3d` | Nền tảng (T042): Metric scale (mm, Y-up glTF), No-Sharp-Edge Law (micro-bevel $0.2-0.5	ext{ mm}$), concentric fillets, True Isometric camera ($35.264^\circ$ elev), 3-point studio lighting, PBR albedo clamp. Native bridge: `solidcraft_bridge.py`. |
| `cad` | Nền tảng (T042): ISO 5457 sheet dimensions (A4–A0, 20mm left margin), ISO 128 line weight hierarchy (0.50mm group: 0.50, 0.25, 0.18mm), ISO 129 dimensioning geometry (10mm/7mm offsets, 3:1 arrowheads), ISO 7200 title block (180mm). Native bridge: `cadcraft_bridge.py`. |
| `docx` | T039 DocumentCraft on `main`; **T045** advanced report (side-by-side media, OMML equations, merged-header/image-cell tables, callout/KPI, VectorCraft cover asset) `work/T045-opencode-advanced-docx`, audit sạch 11 trang Word PDF; Argon **approve T045** (round 2), chờ owner merge. Chưa có PDF/UA, PDF/A, LibreOffice rung 3, human rung 6. |
| `xlsx` | T041 SheetCraft on `main`; **T046** advanced workbook/dashboard (7 sheets, ảnh trong bảng, Gantt native start trong suốt, ma trận quan hệ, pivot GridCraft + fallback, VBA, KPI công thức) `work/T046-opencode-advanced-xlsx`, audit sạch, print ~93% A4; Argon **approve T046** (round 2), chờ owner merge. Waterfall/treemap/histogram/box/funnel vẫn là recipe OOXML. |

## Việc tiếp theo (xếp hạng)

1. **Phản biện chéo (Peer Review)**, theo `lab/standards/REVIEW.md`, do agent khác tác giả viết:
   - T044 (Cross-Asset Pipeline & Local Autonomy, review requested);
   - T043 (Dynamic Theme Engine & Teardown, review requested);
   - T042 (Multi-domain canons & bridges, review requested);
   - T039 & T041 (docx / xlsx round 2);
   - T038 (pptx canon);
   - T035 (DeckCraft);
   - T036–T037 (cross protocols và multi-craft bridges).
2. **Đồng bộ hóa với OpenCode:**
   - Sử dụng `scripts/cross_pipeline.py` để tiền xử lý biểu đồ (`validate_chart_data_for_presentation`) và ảnh (`validate_image_for_embedding`) trước khi chèn chéo vào Word và Excel.
3. **Tích hợp Theme Engine vào Slide Forge (`slide_forge.py`):**
   - Hỗ trợ cờ `--ref-deck <file.pptx>` để tự động clone theme từ file mẫu bất kỳ.
   - Hỗ trợ cờ `--need "<chuỗi mô tả>"` để tự động tổng hợp theme độc bản theo nhu cầu.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch
main. Read AGENTS.md, lab/CHARTER.md, lab/PROTOCOL.md and
domains/<your domain>/DOMAIN.md. Run the tests and lab/tools/check_layout.py.
Take the next free ID in research/tasks/INDEX.md with the domain in brackets and
push the claim. Frame your question from the domain's native canon before
building. Follow lab/protocols/04_cross_asset_pipeline.md to pre-process assets
before embedding. Put every output into experiments/<ID>-<date>-<agent>-<slug>/ (never the
repo root). Tag claims with evidence rungs. Ask another agent to review per
lab/standards/REVIEW.md before anything enters a product path.
```
