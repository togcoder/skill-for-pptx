# PPTX Motion Lab

Nghiên cứu biến một câu lệnh ngắn thành PowerPoint có chuyển động có chủ đích và chỉnh sửa được.

Repo chính: [togcoder/skill-for-pptx](https://github.com/togcoder/skill-for-pptx).

**Model mới bắt đầu tại [HANDOFF.md](HANDOFF.md)**. Quy trình cộng tác và các task song song nằm ở [docs/COLLABORATION.md](docs/COLLABORATION.md).

**Bản nghiên cứu v0.7:** đã có đường dựng PPTX thử nghiệm, kiểm tra cấu trúc và ảnh tĩnh. Chưa xác nhận chuyển động trong PowerPoint. Nguồn skill trong repo chưa được cài vào tài khoản.

Mới nhất: [T005 compound choreography](experiments/T005-20261004-codex-choreography/REPORT.md) biến intent từ prompt ngắn thành chuỗi bung nút, xoay, phóng, tách lớp và ghép lại. Hai PPTX/22 ảnh cuối đã kiểm tra, 41 tests đạt. Đây là một recipe 2D hạn chế, cần bấm từng Morph; chưa phải bộ tạo mọi hiệu ứng phức tạp. [T006](research/tasks/T006-native-timeline.md) ưu tiên timeline/path và playback thật tiếp theo.

## Kết quả hiện có

- T006 full candidate: đã có PPTX 1 slide/31 đối tượng/6 chặng; sửa lỗi mất chữ làm pipeline dừng; 79 tests đạt và ảnh mở đầu đã xem. Audit tọa độ còn chỉ ra rủi ro nối chặng, chưa có playback PowerPoint. [Báo cáo và file](experiments/T006-20261004-packed-validation/REPORT.md).

- T002: giữ nguyên đường label sạch của E004 và siết carrier theo chữ. Proxy carrier giảm 6/6→0/6, nhưng focus emphasis tĩnh giảm 4/5→3/5. [Báo cáo](experiments/T002-20261004-codex-tight-carriers/REPORT.md). Native playback chưa kiểm chứng.
- T003: công thức tách/ghép 3–5 lớp, hai chủ đề, 5 PPTX gồm bản lỗi và bản sửa; 15 ảnh cuối đã xem. Sửa số xuống dòng bằng thay đổi duy nhất chiều rộng textbox. Bộ kiểm tra hiện có 34 tests đạt. [Báo cáo và giới hạn](experiments/T003-20261004-codex-layer01/REPORT.md). Chưa có playback PowerPoint hoặc quan sát choreography nguồn.

- E001: ba cảnh “tụ cụm, mở rộng, xếp hàng” với Imagine, Make, Share, Evolve. Mỗi slide có 13 đối tượng native.
- Backend giới hạn: canvas 16:9; rect, ellipse, textbox; opacity=1; Morph theo đối tượng.
- E002: sửa khai báo textbox theo kế hoạch; tiêu chí H001 giữ nguyên đạt 93/93, so với 14 lỗi trước sửa. 25 unit tests tại E002 đạt; ảnh cuối không đổi. Đây là cải thiện biểu diễn native, không phải điểm chuyển động.
- H002: đề độc lập ORBIT ba chế độ. E003: đổi sang chu kỳ qua ba vị trí tam giác, giảm 2 cặp nhãn chồng trong mô hình đường đi tuyến tính xuống 0; kiểm tra cấu trúc và ảnh cuối đạt. Cả hai chưa có playback PowerPoint.
- H003/E004: thử nhãn tiếng Việt dài, giữ nguyên nội dung và tăng khoảng cách dọc. Số cặp nhãn có khoảng chồng theo mô hình giảm 4→0, nhưng khối nền vẫn 6→6. Thêm công cụ tính khoảng cách theo kích thước nhãn và bốn test đối chiếu; tổng tại mốc E004 là 29 tests. [Bằng chứng và giới hạn](experiments/E004/REPORT.md).
- Bộ chèn Morph đọc thứ tự slide từ quan hệ của presentation, kiểm tra định danh và số slide, từ chối file đã có animation, ghi đầu ra hoàn tất mà không ghi đè.
- Bộ bài lỗi cấu trúc E001: bản cũ đạt 1/7, bản mới đạt 7/7. Đây là 7 trường hợp nhắm vào lỗi đã biết, không phải tỷ lệ thành công chung hoặc điểm chuyển động.
- Đọc [checkpoint](docs/STATUS.md) và [báo cáo mới nhất](experiments/T003-20261004-codex-layer01/REPORT.md) để biết giới hạn và việc tiếp theo.

## Dùng nguồn nghiên cứu

[Skill thử nghiệm](skills/pptx-motion/SKILL.md) phối hợp ý đồ, kế hoạch cảnh, công thức và bằng chứng. Nó tham chiếu các script ở gốc repo, chưa phải gói cài độc lập.

```bash
python3 scripts/validate_plan.py experiments/E001/baseline/plan.json
python3 -m unittest discover -s tests -v
bash scripts/run_experiment.sh experiments/E001/baseline/plan.json build/new-run output/new-demo.pptx
python3 scripts/inspect_pptx.py output/new-demo.pptx
```

Đường dựng dùng Node, Python và artifact-tool của runtime ChatGPT Work; đặt các biến CODEX_PRIMARY_RUNTIME_* theo môi trường được cấp. Python kiểm tra kế hoạch chỉ dùng thư viện chuẩn; bộ chèn Morph cần lxml đã có trong runtime. Script dựng phải dùng thư mục build và tên đầu ra mới. Theo skill Presentations của host để đánh dấu thao tác, render file cuối và kiểm tra bằng mắt.

## Hướng nghiên cứu

- [Đề cương](docs/RESEARCH_PLAN.md): giả thuyết, E01–E04 và cổng nghiệm thu.
- [Kiến trúc](docs/ARCHITECTURE.md): kế hoạch trạng thái, bộ thực thi, kiểm chứng.
- [Công thức](skills/pptx-motion/references/recipes.md): trạng thái bằng chứng của từng hiệu ứng.
- [Hợp đồng kế hoạch](skills/pptx-motion/references/plan-contract.md): trường hỗ trợ và đơn vị.
- [Quy trình PowerPoint](docs/POWERPOINT_QA.md): nghiệm thu phát chuyển động.
- [Nguồn](docs/SOURCES.md): tác giả, URL và giới hạn sử dụng.

Mục tiêu là skill áp dụng được nhiều chủ đề. QCC là một bài thử, không phải toàn bộ sản phẩm. Dùng dữ liệu tổng hợp cho các demo. Không đưa video người dùng hoặc tệp mẫu bên ngoài vào gói phân phối. Repo riêng tư; chưa chọn giấy phép phát hành.

## Cộng tác và chạy ở môi trường khác

- [HANDOFF.md](HANDOFF.md): trạng thái, thứ tự đọc, prompt giao cho model khác.
- [Môi trường](docs/ENVIRONMENT.md): phần nào chạy bằng Python, phần nào cần Work hoặc PowerPoint.
- [Tasks](research/tasks/): playback, đường đi khối nền, hiệu ứng mới và backend đa môi trường.
- [Mẫu báo cáo](templates/EXPERIMENT_REPORT.md): đầu vào, bằng chứng, quyết định và bước tiếp.
- [Lịch sử nhập dự án](docs/GITHUB_HANDOFF.md): giữ commit khởi tạo của chủ repo và archive lịch sử trước GitHub.

Nguồn skill tham chiếu repo, chưa phải gói personal skill cài độc lập. M1 vẫn chờ playback PowerPoint.
