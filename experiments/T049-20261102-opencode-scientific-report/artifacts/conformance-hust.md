# Conformance — HUST — Đồ án tốt nghiệp (quy định 2017)

- **Profile:** `hust-datn-2017`
- **Source:** Quy định về đồ án tốt nghiệp năm 2017 (áp dụng cho sinh viên ngành Điều khiển Tự động)
- **URL:** https://hust.edu.vn/uploads/sys/quality-assurance/2019/05/cea-05-01-06-criteria-for-evaluating-graduation-projects.410143.20390.pdf
- **Accessed:** 2026-11-02
- **Result:** PASS (17 pass, 0 warn, 0 fail)

| # | Kiểm soát | Kỳ vọng | Thực tế | Trạng thái |
|---|---|---|---|---|
| 1 | Khổ giấy A4 (210 × 297 mm) | [210.0, 297.0] | [210.0, 297.0] | `pass` |
| 2 | Lề trang (trên/dưới/trái/phải) | {'top': 20.0, 'bottom': 15.0, 'left': 35.0, 'right': 20.0} | {'top': 20.0, 'bottom': 15.0, 'left': 35.0, 'right': 20.0} | `pass` |
| 3 | Phông chữ thân bài | Times New Roman | Times New Roman | `pass` |
| 4 | Cỡ chữ thân bài (pt) | 13 | 13.0 | `pass` |
| 5 | Giãn dòng | 1.5 | 1.5 | `pass` |
| 6 | Thụt đầu dòng (mm) | 10 | 10.0 | `pass` |
| 7 | Cỡ chữ bảng (pt) | 12 | 12.0 | `pass` |
| 8 | Độ sâu heading tối thiểu | >= H3 | H3 | `pass` |
| 9 | Heading 1 có đánh số tự động | True | True | `pass` |
| 10 | Hình/bảng đánh số theo chương | chapter.local, reset mỗi chương | 26 caption; 0 lỗi | `pass` |
| 11 | Vị trí chú thích bảng/hình | bảng trên, hình dưới | 21 bảng, 7 hình; 0 lỗi | `pass` |
| 12 | Số trang ở chân trang | PAGE field, căn giữa | field=True, align=CENTER (1) | `pass` |
| 13 | Thứ tự front matter | task → LỜI CAM ĐOAN → LỜI CẢM ƠN → TÓM TẮT → MỤC LỤC → DANH MỤC KÝ HIỆU → DANH MỤC BẢNG → DANH MỤC HÌNH | declaration → acknowledgements → abstract → toc → abbreviations → list_of_tables → list_of_figures | `pass` |
| 14 | Số tài liệu tham khảo tối thiểu | 8 | 12 | `pass` |
| 15 | Trích dẫn động tới tài liệu | >= 8 REF ref-* | 13 | `pass` |
| 16 | Số trang phần thân | —–50 | 34 | `pass` |
| 17 | Phương trình có số hiệu | 9 | 9/9 | `pass` |

> `warn` is a disclosed limitation or a range outside the regulation; `fail` is a measured mismatch that must be fixed before delivery.