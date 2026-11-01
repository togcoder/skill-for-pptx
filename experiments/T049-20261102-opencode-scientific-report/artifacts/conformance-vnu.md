# Conformance — VNU-UET — Khóa luận tốt nghiệp

- **Profile:** `vnu-uet-kl-2024`
- **Source:** Quy định về trình bày khóa luận tốt nghiệp (chương trình chuẩn và chất lượng cao)
- **URL:** http://fepn.uet.vnu.edu.vn/upload/2001767/fck/tung232/Quy-%C4%91i%CC%A3nh-v%C3%AA%CC%80-tri%CC%80nh-ba%CC%80y-kho%CC%81a-lu%C3%A2%CC%A3n-t%C3%B4%CC%81t-nghi%C3%AA%CC%A3pCLC.pdf
- **Accessed:** 2026-11-02
- **Result:** PASS (18 pass, 0 warn, 0 fail)

| # | Kiểm soát | Kỳ vọng | Thực tế | Trạng thái |
|---|---|---|---|---|
| 1 | Khổ giấy A4 (210 × 297 mm) | [210.0, 297.0] | [210.0, 297.0] | `pass` |
| 2 | Lề trang (trên/dưới/trái/phải) | {'top': 25.0, 'bottom': 30.0, 'left': 30.0, 'right': 20.0} | {'top': 25.0, 'bottom': 30.0, 'left': 30.0, 'right': 20.0} | `pass` |
| 3 | Phông chữ thân bài | Times New Roman | Times New Roman | `pass` |
| 4 | Cỡ chữ thân bài (pt) | 13 | 13.0 | `pass` |
| 5 | Giãn dòng | 1.3 | 1.3 | `pass` |
| 6 | Thụt đầu dòng (mm) | 10 | 10.0 | `pass` |
| 7 | Cỡ chữ bảng (pt) | 12 | 12.0 | `pass` |
| 8 | Độ sâu heading tối thiểu | >= H3 | H3 | `pass` |
| 9 | Heading 1 có đánh số tự động | True | True | `pass` |
| 10 | Hình/bảng đánh số theo chương | chapter.local, reset mỗi chương | 26 caption; 0 lỗi | `pass` |
| 11 | Vị trí chú thích bảng/hình | bảng trên, hình dưới | 21 bảng, 7 hình; 0 lỗi | `pass` |
| 12 | Số trang ở chân trang | PAGE field, căn giữa | field=True, align=CENTER (1) | `pass` |
| 13 | Thứ tự front matter | LỜI CAM ĐOAN → TÓM TẮT → MỤC LỤC → DANH MỤC KÝ HIỆU → DANH MỤC BẢNG → DANH MỤC HÌNH | declaration → abstract → toc → abbreviations → list_of_tables → list_of_figures | `pass` |
| 14 | Số tài liệu tham khảo tối thiểu | 8 | 12 | `pass` |
| 15 | Trích dẫn động tới tài liệu | >= 8 REF ref-* | 13 | `pass` |
| 16 | Độ dài tóm tắt (từ) | 300–420 | 343 | `pass` |
| 17 | Số trang phần thân | 35–50 | 35 | `pass` |
| 18 | Phương trình có số hiệu | 9 | 9/9 | `pass` |

> `warn` is a disclosed limitation or a range outside the regulation; `fail` is a measured mismatch that must be fixed before delivery.