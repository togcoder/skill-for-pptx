# PPTX Motion Lab — checkpoint

Cập nhật ngày 04/10/2026, giờ Việt Nam. Phiên bản nghiên cứu v0.4 (H003/E004, khoảng cách nhãn dài).

## Trạng thái thực tế

M0 đã có bộ thực thi thử nghiệm và bằng chứng cấu trúc/bố cục E001, H001. M1 chưa đạt vì thiếu phát thử PowerPoint. Đây là nhánh dựng mẫu và kiểm tra phần mềm trong lúc chờ cổng native; không hạ tiêu chuẩn nghiệm thu M1. Nguồn skill là bản nghiên cứu trong dự án, chưa cài vào tài khoản.

Repo chính đã xác minh: `https://github.com/togcoder/skill-for-pptx`, private, owner `togcoder`, quyền push. Chủ repo tạo README khởi tạo ngày 04/10/2026. Bản handoff nhập snapshot v0.4 cùng nguồn, demo và bằng chứng vào repo này; lịch sử cũ nguyên vẹn tại `archive/pre-github-v0.4.bundle`. Đọc `HANDOFF.md`, `docs/COLLABORATION.md` và các nhánh/PR trước khi nhận việc. Không dùng tên dự kiến `pptx-motion-lab` làm repo GitHub nữa.

## Đã hoàn tất

1. Khôi phục scaffold từ phiên trước, giữ snapshot gốc. Phát hiện nguồn SKILL.md còn template TODO và đường dựng chưa hoàn tất.
2. Hoàn thiện đường dựng hạn chế bằng artifact-tool, kế hoạch JSON, chèn Morph và kiểm tra file cuối.
3. Dựng E001 ba cảnh với 13 đối tượng native mỗi slide; hai khai báo Morph 1.200 ms. Render và xem toàn bộ file cuối.
4. Sửa bộ chèn Morph: đọc đúng thứ tự slide, kiểm tra số cảnh và tên, bảo vệ file có timing, từ chối duration lẻ, không để lại file dở và không ghi đè.
5. Cùng bộ 7 lỗi mục tiêu: baseline 1/7, candidate 7/7. Toàn bộ 19 unit tests hiện có pass. Không coi đó là điểm chất lượng chuyển động hay benchmark độc lập.
6. Viết nguồn skill v0.2 cùng hợp đồng, công thức, rubric và hướng dẫn thực thi có thể gọi lại.
7. Dùng một agent với ngữ cảnh tối thiểu để áp dụng skill vào H001: hai cảnh Collect/Inspect/Decide, phóng lớn Inspect và giữ bối cảnh hai bên. Đã tạo PPTX và xem hai slide cuối. Không tiết lộ đáp án/chẩn đoán E001 cho agent đó.
8. H001 phát hiện nguồn tham khảo E001 bị gắn cứng trong speaker notes; đã sửa renderer để dùng nguồn thực sự trong kế hoạch.
9. H001 cũng phát hiện planned textbox xuất thành native shape có p:txBody nhưng không có txBox=1. Giữ kiểm tra nghiêm ngặt thất bại, ghi ranh giới trong skill; không sửa rubric để che lỗi.
10. E002 sửa đúng 14 khai báo textbox của H001 theo kế hoạch. Bộ kiểm tra H001 giữ nguyên: từ 14 lỗi còn 0 lỗi, 93/93 kiểm tra đạt. Chỉ hai slide XML thay đổi bởi txBox; mọi phần khác giữ nguyên byte. Hai ảnh cuối giống H001 từng pixel. 25 unit tests đạt. Nguồn skill/bộ dựng đã dùng bước chuẩn hóa này.

11. H002 đã hoàn tất từ đề độc lập về đèn ORBIT: 3 slide, 11 đối tượng native mỗi slide, 6 textbox/slide đúng khai báo, 2 Morph 1.100 ms. Agent và parent đã xem đủ ảnh cuối. Agent không đọc plan/artifact cũ, nhưng được thu gọn phần việc sau giai đoạn đọc hướng dẫn; không coi đây là benchmark tự hành có đo thời gian.
12. H002 lộ nguy cơ nhãn gặp nhau khi đổi chỗ đối ứng. E003 giữ baseline và cùng phép đo hình học tuyến tính liên tục: từ 2 cặp nhãn có khoảng chồng xuống 0 trên 6 cặp/chuyển cảnh. Chỉ đổi bố trí/đường đi thành chu kỳ qua ba đỉnh tam giác; giữ 3 slide, chữ, loại/kích thước đối tượng và thời lượng. File cuối đạt cấu trúc, render/xem đủ 3 slide. Đây là cải thiện trong mô hình giả định, chưa phải playback PowerPoint.

13. H003 thử đề mới với ba nhãn tiếng Việt dài 360×96 px. Giữ rubric và chẩn đoán E003: 4/6 cặp nhãn có khoảng chồng theo mô hình. E004 chỉ đổi y của khối/nhãn, tăng khoảng cách hai tầng từ 200 lên 300 px, số cặp nhãn chồng về 0. Cả hai vẫn 6/6 cặp khối có khoảng chồng. File cuối có 3×8 đối tượng native, 5 textbox/slide và hai Morph 1.100 ms; kiểm tra và xem đủ 6 ảnh cuối.
14. Bổ sung scripts/cyclic_label_clearance.py với ngưỡng H >= 3*d*h/(2*d-w) cho ba nhãn đều, ba vị trí đối xứng, nội suy đồng bộ tuyến tính; có miền áp dụng rõ. Bốn test mới đối chiếu chẩn đoán cũ, tổng 29 unit tests đạt. Đã cập nhật nguồn skill với bài học và giữ lỗi plan/preflight ban đầu.

Tại thời điểm bàn giao chưa tạo claim nghiên cứu mới. Luôn kiểm tra nhánh và PR mở để biết công việc đang chạy. Nguồn skill bổ sung công thức cyclic focus và phân biệt số trạng thái với số chuyển cảnh. Read của H002/E003 mở ở tư thế lớn; không có đoạn phóng lớn riêng trên slide đầu.

## Bằng chứng cần đọc

- `experiments/E001/REPORT.md`, `scores.json`, `regression-comparison.json`, `validation.json`, `final-renders/`.
- `experiments/H001/`: kế hoạch độc lập, rubric, báo cáo và bằng chứng file cuối.
- `experiments/E002/REPORT.md`, `comparison.json`: sửa textbox, giữ baseline và tiêu chí H001; `output/PPTX_Motion_Lab_E002.pptx`.
- `experiments/H002/`: đề, plan, rubric, qa và bản sao bằng chứng tại `evidence/`.
- `experiments/E003/REPORT.md`: H002 và E003, chẩn đoán đường đi, kiểm tra cấu trúc và điểm tĩnh chủ quan. Native motion/editability vẫn null; không tính điểm tổng.
- `experiments/E004/REPORT.md`, `package-comparison.json`, `unit-tests.txt`, `scores.json`, các `path-diagnostic.json` và `carrier-paths.json` H003/E004; `output/PPTX_Motion_Lab_E004.pptx`.
- `research/skill-source-validation.json`: kiểm tra nguồn thử nghiệm, không phải chứng nhận cài đặt skill.
- `docs/POWERPOINT_QA.md`: yêu cầu bằng chứng native.

PPTX E001: `output/PPTX_Motion_Lab_E001.pptx`. SHA-256: b3b4e28c14f00bc4fe05d6a71400752819413661e1280eb92301b4a6305e7c37.
PPTX H001: `output/PPTX_Motion_Lab_H001.pptx`; dùng hash trong bằng chứng H001.

Điểm E001: đáp ứng đề 4/5, cấu trúc chỉnh sửa 4/5, định danh 4/5, dễ đọc tĩnh 4/5, bố cục sáng tạo tĩnh 3/5. Đây là nhận xét không mù của người làm. Chuyển động chưa chấm, không có điểm tổng.

## Việc tiếp theo theo giá trị

1. Phát thử H003/E004 và H002/E003 bằng PowerPoint khi có môi trường hợp lệ, ghi hash/phiên bản/video và tác động của khối nền giao nhau. M1 vẫn pending.
2. Nếu chưa có PowerPoint, xử lý nguy cơ khối nền giao nhau của H003/E004 theo cùng brief và rubric, hoặc thử một công thức mới từ nguồn sơ cấp. Không gọi hết chồng nhãn là hết chồng toàn cảnh. Không dựng lại các bản này nếu không có giả thuyết mới.
3. Chia phần việc theo T001–T004 trong `research/tasks/`. Nhận claim/nhánh riêng trước khi làm để tránh trùng. Skill và renderer hiện vẫn phụ thuộc môi trường Work như `docs/ENVIRONMENT.md`.
4. Chuẩn bị công cụ thu bằng chứng trên PowerPoint Windows khi phù hợp, không giả lập kết quả. Benchmark 18 lượt chưa thực hiện.

## Khôi phục và lưu tiếp

GitHub `togcoder/skill-for-pptx` là nguồn làm việc chính. Clone/fetch main mới nhất, kiểm tra nhánh/PR và đọc HANDOFF.md. Đọc docs/RECOVERY.md để tra lịch sử trước khi nhập GitHub. Bundle và các checkpoint cloud cũ là snapshot phục hồi lịch sử; không ghi chúng đè lên repo mới hơn. Code và kết quả đã gắn GitHub được commit/push về đúng repo, không tạo bản sao code mới song song trong Library.
