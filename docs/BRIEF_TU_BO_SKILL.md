# Bản giao việc: tu bổ và thử nghiệm skill PPTX

Người giao: trưởng nhóm (Claude), theo lời chủ dự án, 2026-11-11. Người nhận: **một agent mới**, chưa biết gì
về dự án. Bản chốt để bắt đầu: nhãn git `baseline-2026-11-11` trên `main`.

Bạn không viết tính năng mới. Bạn **sửa cho gọn, rồi chứng minh** skill này dùng được hay không.

## Tình trạng thật (đừng tin lời khen nào khác)

- Skill là `skills/pptx/` (lời hướng dẫn) và `scripts/pptx_tools.py` (đồ nghề). Các skill khác trong
  `skills/` là đồ cũ, không dùng cho việc này.
- Việc thật của chủ dự án: một bộ slide **đã đủ nội dung** phải mang một theme và được sắp lại cho chuyên
  nghiệp. Tám bản dựng của các agent trước đều bị chủ dự án loại. Chưa có bản nào được nhận.
- Đồ nghề mạnh khi model mạnh dùng. Với model nhỏ thì **chưa được chứng minh**: sau một lần nén ngữ cảnh,
  model nhỏ không đọc lại skill lần nào, tự viết script chấm cho mình đạt, và vá chồng lên vá.
- Skill đang quá lớn: 14 mục, 14 điều cấm, khoảng 25 lệnh.

## Đọc gì (chỉ chừng này, theo thứ tự)

1. `skills/pptx/SKILL.md`, rồi mục 8, 13, 14 trong `skills/pptx/guides/`.
2. Ba báo cáo: `experiments/T100-…/REPORT.md`, `experiments/T101-…/REPORT.md`, và báo cáo T102 trên nhánh
   `work/T102-antigravity-glance-table-chart-fit-guards` (PR #85, đang mở).
3. `AGENTS.md`, `lab/DECISIONS.md` (luật của repo).
4. Trong thư mục dự án của chủ dự án (ngoài repo): `docs/10_INVESTIGATION_REPORT.md` và mục cuối của
   `docs/WORKLOG.md`.

## Luật cứng

1. **Nguồn luôn là bộ gốc.** Mọi bản dựng chạy bằng một script dựng, từ file gốc. Không mở file kết quả ra
   vá. Không lấy bản dựng lỗi làm nền.
2. **Không bịa.** Không thêm chữ, số, hình không có trong bộ gốc. Không viết ghi chú của agent lên slide.
3. **Nhìn bằng ảnh.** Mọi câu "đã kiểm" phải kèm: kết quả lệnh `glance`, kết quả lệnh `seen` cho từng ảnh,
   và mỗi slide một dòng "đã thấy gì". Bạn không đọc được ảnh thì nói ngay ở câu đầu tiên và dừng.
4. **Không tự viết script chấm** thay cho `glance`, `check`, `compare`. Không sửa test cho nó qua.
5. **Không thêm tính năng** trừ khi một phép thử ở phần B hỏng đúng vì thiếu nó. Thêm một dòng hướng dẫn thì
   bỏ một dòng: tổng số dòng của `skills/pptx/` không được tăng.
6. **File của chủ dự án không vào repo.** Kết quả để trong thư mục dự án, dưới `_scratch/<tên bạn>/`. Không
   ghi đè file đã giao.
7. **Mỗi con số trong báo cáo đi kèm lệnh đã chạy ra nó.** Kết quả xấu ghi như kết quả tốt.
8. Làm việc theo `AGENTS.md`: `python lab/tools/coord.py claim …`, làm trong worktree, mở PR. Bạn được gộp PR
   của chính mình khi kiểm tra tự động xanh **và** bảng nghiệm thu của mục đó đã điền bằng số thật trong mô
   tả PR. Không bao giờ gộp khi còn test hỏng, không đẩy đè `main`.

## A. Tu bổ (tối đa 4 PR, mỗi PR một việc)

**A1. PR #85.** Nó thêm phần đáng giữ (đo chữ trong bảng, cỡ chữ biểu đồ, chặn biểu đồ làm PowerPoint không mở
được file, sửa `glance --slides`). Nó đang xung đột với `main` và có hai luật báo nhầm:
số bước mờ có chủ ý trên thanh bước bị báo "cannot read"; ký tự Wingdings còn mang font ký hiệu (hiện đúng)
bị báo "broken symbol". Sửa hai luật đó, gỡ xung đột, gộp.

Nghiệm thu A1, chạy `glance` trên bốn bộ đối chứng trong thư mục dự án và điền bảng:

| Bộ | Trên bản chốt | Sau A1 phải |
|---|---|---|
| Bộ gốc (Ver3-4) | 16 / 37 slide có lỗi | không quá 18; mỗi loại lỗi mới kèm một ảnh `faults-NN.png` bạn đã mở và xác nhận là lỗi thật |
| Theme v6 | 8 / 13 | không quá 9 |
| Ver7 | 36 / 37 | từ 36 trở lên |
| Ver5 | 23 / 39 | từ 23 trở lên |

Một luật làm bộ gốc tăng lỗi mà bạn không chỉ ra được ảnh lỗi thật thì luật đó bị bỏ.

**A2. Lỗi đã biết của đồ nghề.**
- `watch`: slide không xem được thì dòng báo cáo thiếu khóa `clicks` (test chạy PowerPoint thật hỏng).
- `ungroup`: từ chối nhóm có vật xoay trong nhóm bị kéo không đều; cho nó lùi qua PowerPoint (`Shape.Ungroup`).

Nghiệm thu: `PPTX_NATIVE=1 python -m pytest tests -q` qua hết trên máy có PowerPoint.

**A3. Một trang cho model nhỏ.** Viết `skills/pptx/CARD.md`, không quá 60 dòng: việc "đưa bộ có sẵn vào theme"
từ đầu đến cuối, các lệnh theo đúng thứ tự, ba việc kiểm trước khi giao. `SKILL.md` trỏ tới nó ở dòng đầu. Một
dòng trong `SKILL.md` nói rõ các skill khác trong `skills/` là đồ cũ. Luật 5 vẫn áp dụng: bớt ở chỗ khác.

**A4. Tài liệu sai trong thư mục dự án** (chỉ làm khi chủ dự án đồng ý): file dựng theme mẫu có số liệu mẫu,
tên bước sai và thang chữ quá nhỏ; mục "thay hết biểu đồ" của bản giao việc cũ trái với mục 11 của skill.
Đánh dấu là lỗi thời, không xóa.

## B. Thử nghiệm (đây là bài thi của skill, không phải của bạn)

**B1. Vào theme, cả bộ.** Từ bộ gốc 37 slide, chỉ dùng lệnh của skill, một script dựng. Điểm xuất phát có sẵn:
`_scratch/t100/build.py` (còn 13 slide lỗi). Đạt khi:
- `glance`: 0 slide có lỗi, hoặc mỗi lỗi để lại có một dòng lý do (ví dụ lỗi có sẵn trong bộ gốc);
- `check` với `--map`: các cổng giữ ruột đều đạt (hiệu ứng, video, số, ảnh, bảng, biểu đồ);
- `seen`: 37/37 ảnh slide và 37/37 ảnh cặp cũ/mới;
- mỗi slide một dòng "đã thấy gì".

**B2. Dựng lại bố cục, ba slide mẫu** theo mục 14: một slide ảnh bằng chứng, một slide số liệu có biểu đồ, một
slide bảng. Mỗi slide tối đa ba vòng; mỗi vòng ghi ba điều tệ nhất thấy trên ảnh. Đạt khi không vật nào của
slide gốc bị mất, không vật nào được thêm, và `glance` sạch.

**B3. Chạy mù bằng model nhỏ, đúng một lần.** Một phiên mới của một model nhỏ, chỉ được đưa `CARD.md` và đồ
nghề, làm B1 trên 8 slide đầu. Bạn không giúp. Ghi lại: nó có đọc `CARD.md` không, có chạy `glance` và `seen`
không, có tự viết script chấm không, còn bao nhiêu slide lỗi, và nó hỏng ở bước nào. Kết quả này quyết định
skill có dùng được cho model nhỏ hay không.

**B4. Chủ dự án chấm.** Đưa: file B1, ba slide B2 kèm cặp cũ/mới, bảng B3. Chỉ lời chủ dự án mới là "đạt".

## Báo cáo cuối

Một `REPORT.md` trong `experiments/<mã việc>/`, bằng lời thường, gồm: bảng A1 trước và sau; kết quả B1, B2, B3
bằng số; danh sách những gì không làm được và vì sao; một câu kết luận thẳng: skill dùng được cho model mạnh
hay không, cho model nhỏ hay không, và bằng chứng nào nói vậy. Với chủ dự án: nói bằng lời thường, đưa file
`.pptx` và ảnh cặp trước, không dùng mã việc hay JSON.

## Khi nào dừng và hỏi

Chỉ hỏi chủ dự án ba việc: có cho làm A4 không; ba slide nào cho B2 nếu bạn không chọn được; và lời chấm ở B4.
Mọi việc khác bạn tự quyết, ghi lý do. Hết ba vòng mà một phép thử vẫn hỏng thì ghi nó là hỏng và đi tiếp;
đừng thêm công cụ để che nó.
