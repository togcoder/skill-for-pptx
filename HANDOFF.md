# Handoff — Design Research Lab

Cập nhật: 01/11/2026, sau T039/T041 vào `main` và T042/T043 mở. Tệp này được
**viết lại** mỗi lần bàn giao, không ghi nối thêm. Lịch sử:
[docs/CHANGELOG.md](docs/CHANGELOG.md). Bàn giao trước:
[docs/archive/](docs/archive/).

Repo: https://github.com/togcoder/skill-for-pptx (private). Chủ dự án: togcoder.

## Dự án bây giờ là gì

Một **lab nghiên cứu thiết kế đa lĩnh vực**: nhiều agent (nhiều model) cùng
nghiên cứu, phản biện và gộp kết quả cho nhiều ứng dụng. Mỗi lĩnh vực
(domain) có luận điểm, nguồn, dữ liệu thiết kế và thang bằng chứng riêng;
PowerPoint chỉ là domain lâu đời nhất.

- Cách agent làm việc: [lab/PROTOCOL.md](lab/PROTOCOL.md).
- Các chuẩn: [lab/standards/](lab/standards/), gồm nghiên cứu, phản biện, gộp
  dữ liệu, nơi đặt file và **cross-craft asset** (dùng tool ArtCraft sở hữu
  asset, ghi tool/version/command/licence, test ở domain nhận).
- Danh sách domain: [domains/README.md](domains/README.md).

## Bắt đầu

1. `main` hiện là `db58b3d`: T035–T041 đã vào `main`; T039 [docx] và T041 [xlsx]
   đã qua review Argon (R1–R8) và được chủ dự án duyệt.
2. Hai nhánh mới dựa trên `main`:
   - `work/T042-opencode-advanced-docx` — PR #38 (docx nâng cao, review requested);
   - `work/T043-opencode-advanced-xlsx` — T043 (xlsx nâng cao/dashboard, review requested).
3. Đọc theo thứ tự `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, rồi thẻ
   domain của bạn (`domains/docx/DOMAIN.md`, `domains/xlsx/DOMAIN.md`).
4. Chạy `python3 -m unittest discover -s tests` (đặt `PYTHONUTF8=1` trên Windows
   để tránh lỗi encoding của các test cũ) và `python3 lab/tools/check_layout.py`.
5. Lấy mã kế tiếp trong `research/tasks/INDEX.md` (hiện là **T044**). Tiêu đề
   ghi domain trong ngoặc, ví dụ `[cross]`.

## Trạng thái từng domain

| Domain | Trạng thái |
|---|---|
| pptx | Trưởng thành: Director, Morph Studio, Forge, hệ thiết kế và critic. T035 và T038 **chưa được phản biện**; còn 1 test lỗi của T038 (WORD_BREAK ở "Logo Watermark", phụ thuộc font). |
| docx | T039 DocumentCraft đã vào `main` (`document_forge.py`, `word_field_kit.py`, `document_audit.py`, dữ liệu, skill). T042 nâng cao: ảnh cạnh chữ, công thức OMML, bìa, bảng header nhiều tầng/gộp ô/ảnh trong ô, callout/KPI; Word PDF 11 trang, audit sạch (2 equations, 5 merged cells, table-grid/image/alt checks, `vi-VN`); Argon review `revise` đã trả lời (audit nâng cao, language, negative tests); **review requested** (PR #38). Chưa có PDF/UA, PDF/A, LibreOffice rung 3, human rung 6. |
| xlsx | T041 SheetCraft đã vào `main` (`chart_forge.py`, `chart_patch.py`, `chart_audit.py`, dữ liệu, skill). T043 nâng cao: 7 sheet (Data/Pivot/Model/Team/Gantt/Relations/Dashboard), công thức chéo, named range, ảnh trong bảng, Gantt native (start trong suốt, trục ngày), ma trận quan hệ, pivot GridCraft + fallback công thức, VBA `.bas`/`.xlsm`, dashboard 1 trang với KPI công thức; audit sạch; Argon review `revise` đã trả lời (Gantt axis/start, print ~93% A4, KPI formula, pivot fallback, VBA guard); **review requested**. Node-link scatter bị loại (negative result). Waterfall/treemap/histogram/box/funnel vẫn là recipe OOXML. |
| svg | Mới có bridge thử nghiệm T037; chưa phản biện. |
| cross | Protocol 00–03, schema, registry ArtCraft, intent decoder (T036–T037); chưa phản biện, chưa thành chuẩn chung (cần 2 domain chấp nhận). Quy tắc cross-craft đã ghi ở `AGENTS.md` + `lab/standards/RESEARCH.md` (T042). |

## Việc tiếp theo (xếp hạng)

1. **Phản biện chéo** theo `lab/standards/REVIEW.md`, do agent khác tác giả:
   - T042 [docx] và T043 [xlsx] — round 1 (report + audit + render);
   - T038 (pptx canon), T035 (DeckCraft), T036–T037 (cross + bridges).
2. **Docx**: PDF/UA/veraPDF, PDF/A, LibreOffice Writer rung 3, matrix/cases
   equations, landscape/two-column fixture, quyết định module canonical.
3. **Xlsx**: dashboard audit (label collision, alignment, pages), static pivot
   fallback, native node-link proof or close the matrix scope, VBA trust
   preflight, LibreOffice Calc rung 3.
4. **T044 [cross]**: dời code từ `scripts/` vào package theo domain(s), sửa
   import/skill/test, không phá thí nghiệm đã đóng băng.
5. **pptx**: cổng native (trình chiếu tương tác) và sửa test T038.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch
main. Read AGENTS.md, HANDOFF.md, lab/CHARTER.md, lab/PROTOCOL.md and
domains/<your domain>/DOMAIN.md. Run the tests and lab/tools/check_layout.py.
Take the next free ID in research/tasks/INDEX.md with the domain in brackets and
push the claim. Frame your question from the domain's native canon before
building. Put every output into experiments/<ID>-<date>-<agent>-<slug>/ (never
the repo root). Tag claims with evidence rungs. Ask another agent to review per
lab/standards/REVIEW.md before anything enters a product path. When another
ArtCraft tool owns an asset, use it, record tool/version/command/licence, and
test the asset in your domain.
```
