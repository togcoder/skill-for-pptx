# Handoff — Design Research Lab

Cập nhật: 01/11/2026, sau T040. Tệp này được **viết lại** mỗi lần bàn giao,
không ghi nối thêm. Lịch sử: [docs/CHANGELOG.md](docs/CHANGELOG.md). Bàn giao
trước (T038): [docs/archive/HANDOFF-T038-2026-11-01.md](docs/archive/HANDOFF-T038-2026-11-01.md).

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

1. Đầu nghiên cứu mới nhất nằm trên nhánh `claude/blissful-pasteur-gmll59`
   (đã gộp T035–T040). `main` vẫn chậm hơn.
2. Đọc theo thứ tự `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, rồi thẻ
   domain của bạn.
3. Chạy `python3 -m unittest discover -s tests` và
   `python3 lab/tools/check_layout.py`.
4. Lấy mã kế tiếp trong `research/tasks/INDEX.md` (hiện là **T041**). Tiêu đề
   ghi domain trong ngoặc, ví dụ `[xlsx]`.

## Trạng thái từng domain

| Domain | Trạng thái |
|---|---|
| pptx | Trưởng thành: Director, Morph Studio, Forge, hệ thiết kế và critic. T035 và T038 **chưa được phản biện**. Còn 1 test lỗi của T038 (WORD_BREAK ở "Logo Watermark", phụ thuộc font). |
| docx, xlsx, svg | Mới có một bridge thử nghiệm mỗi domain (T037), đều chưa được phản biện. T039 (OpenCode) đã nhận docx + xlsx. |
| cross | Có protocol 00–03, schema, registry ArtCraft và intent decoder (T036–T037). Chưa được phản biện; chưa được làm chuẩn chung (cần 2 domain chấp nhận). |

## Việc tiếp theo (xếp hạng)

1. **Phản biện chéo**, theo `lab/standards/REVIEW.md`, do agent khác tác giả
   viết:
   - T038 (pptx canon);
   - T035 (DeckCraft);
   - T036–T037 (lớp cross và các bridge).
2. **T039 docx/xlsx**: viết luận điểm riêng của domain trong thẻ domain trước
   khi viết code.
3. **T041 (cross)**: dời code từ `scripts/` vào thư mục theo domain, sửa
   import, skill và test, không phá các thí nghiệm đã đóng băng.
4. **pptx**: cổng native (trình chiếu tương tác trong PowerPoint) và sửa test
   lỗi của T038.

## Prompt giao việc

```text
Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch
claude/blissful-pasteur-gmll59. Read AGENTS.md, lab/CHARTER.md, lab/PROTOCOL.md and
domains/<your domain>/DOMAIN.md. Run the tests and lab/tools/check_layout.py.
Take the next free ID in research/tasks/INDEX.md with the domain in brackets and
push the claim. Frame your question from the domain's native canon before
building. Put every output into experiments/<ID>-<date>-<agent>-<slug>/ (never the
repo root). Tag claims with evidence rungs. Ask another agent to review per
lab/standards/REVIEW.md before anything enters a product path.
```
