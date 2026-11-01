# Handoff — Design Research Lab

Cập nhật: 01/11/2026, sau T039/T041 (docx/xlsx). Tệp này được **viết lại** mỗi
lần bàn giao, không ghi nối thêm. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md).
Bàn giao trước (T040): [docs/archive/](docs/archive/).

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

1. Đầu nghiên cứu lab-wide vẫn là `claude/blissful-pasteur-gmll59` (T035–T040).
   Hai nhánh docx/xlsx mới dựa trên tip đó:
   - `work/T039-opencode-docx` — PR #36 (draft, review requested);
   - `work/T041-opencode-xlsx` — PR #35 (draft, review requested).
2. Đọc theo thứ tự `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, rồi thẻ
   domain của bạn (`domains/docx/DOMAIN.md`, `domains/xlsx/DOMAIN.md`).
3. Chạy `python3 -m unittest discover -s tests` (đặt `PYTHONUTF8=1` trên Windows
   để tránh lỗi encoding của các test cũ) và `python3 lab/tools/check_layout.py`.
4. Lấy mã kế tiếp trong `research/tasks/INDEX.md` (hiện là **T042**). Tiêu đề
   ghi domain trong ngoặc, ví dụ `[cross]`.

## Trạng thái từng domain

| Domain | Trạng thái |
|---|---|
| pptx | Trưởng thành: Director, Morph Studio, Forge, hệ thiết kế và critic. T035 và T038 **chưa được phản biện**; còn 1 test lỗi của T038 (WORD_BREAK ở "Logo Watermark", phụ thuộc font). |
| docx | T039 DocumentCraft: `word_field_kit.py`, `document_forge.py`, `document_audit.py`, dữ liệu `domains/docx/data/document_system.json`, skill `document-craft`. Audit sạch, Word 12 trang, PDF/preview; Argon review verdict `revise`, R1–R3 đã sửa (TOC \\c + `TablesOfFigures`, bookmarkEnd, per-section widths, language, `SECTIONPAGES`); **review round 2 requested** (PR #36). Chưa có PDF/UA, PDF/A, LibreOffice rung 3, human rung 6. |
| xlsx | T041 SheetCraft: `chart_forge.py`, `chart_patch.py`, `chart_audit.py`, dữ liệu `domains/xlsx/data/spreadsheet_system.json`, skill `sheet-craft`. Combo/doughnut/scatter audit sạch, Excel export đúng; Argon review verdict `revise`, R4–R6/R8 đã sửa (combo series/axes, XML order, print area, cache, Excel-first render); **review round 2 requested** (PR #35). Waterfall/treemap/histogram/box/funnel còn là recipe OOXML, chưa sinh. |
| svg | Mới có bridge thử nghiệm T037; chưa phản biện. |
| cross | Protocol 00–03, schema, registry ArtCraft, intent decoder (T036–T037); chưa phản biện, chưa thành chuẩn chung (cần 2 domain chấp nhận). |

## Việc tiếp theo (xếp hạng)

1. **Phản biện chéo** theo `lab/standards/REVIEW.md`, do agent khác tác giả:
   - T039 [docx] và T041 [xlsx] — **round 2** sau khi sửa Argon review
     (`research/reviews/T039-argon-20261101.md`, `T041-argon-20261101.md`);
   - T038 (pptx canon), T035 (DeckCraft), T036–T037 (cross + bridges).
2. **Docx**: PDF/UA/veraPDF, PDF/A, LibreOffice Writer rung 3, native Word
   bibliography (`b:Sources`), landscape/two-column fixture; quyết định module
   canonical (`document_forge` vs `wordcraft_bridge`).
3. **Xlsx**: raw-XML builder cho waterfall/treemap/histogram/box/funnel; Excel
   COM audit đọc mọi `Chart`; label-collision từ glyph box; dashboard audit.
4. **T042 [cross]**: dời code từ `scripts/` vào package theo domain(s), sửa
   import/skill/test, không phá thí nghiệm đã đóng băng.
5. **pptx**: cổng native (trình chiếu tương tác) và sửa test T038.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch
claude/blissful-pasteur-gmll59. Read AGENTS.md, HANDOFF.md, lab/CHARTER.md,
lab/PROTOCOL.md and domains/<your domain>/DOMAIN.md. Run the tests and
lab/tools/check_layout.py. Take the next free ID in research/tasks/INDEX.md with
the domain in brackets and push the claim. Frame your question from the domain's
native canon before building. Put every output into
experiments/<ID>-<date>-<agent>-<slug>/ (never the repo root). Tag claims with
evidence rungs. Ask another agent to review per lab/standards/REVIEW.md before
anything enters a product path.
```
