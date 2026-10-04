# Handoff — PPTX Motion Lab

Repo chính: https://github.com/togcoder/skill-for-pptx (private).
Chủ dự án: togcoder. Cập nhật bàn giao: 04/10/2026.

## Bắt đầu trong 5 phút

1. Fetch nhánh mới nhất, xem thay đổi chưa commit và các nhánh/PR đang mở.
2. Đọc `AGENTS.md`, tài liệu này, `docs/STATUS.md` và
   `skills/pptx-motion/SKILL.md`. Đọc reference theo phần việc, không nạp toàn bộ
   lịch sử thí nghiệm vào ngữ cảnh nếu không cần.
3. Đọc `docs/COLLABORATION.md`, chọn một task chưa có người làm trong
   `research/tasks/`, rồi tạo nhánh riêng. Xác nhận claim trước khi dựng bài thử.
4. Chạy `python3 scripts/check_environment.py` để chọn phần việc môi trường hỗ trợ.
5. Đọc brief, rubric và report của baseline liên quan. Giữ nguyên baseline.

## Mục tiêu sản phẩm

Người dùng ra một câu lệnh ngắn, AI tạo được PPTX chỉnh sửa được với chuyển động
có chủ đích, độc đáo và ấn tượng. Sản phẩm cốt lõi là skill, thư viện công thức,
mã dựng và bộ đánh giá có thể dùng lại. QCC chỉ là một đề thử. Nghiên cứu nguồn
mới khi cần, ghi URL/tác giả/ngày xem/điều kiện sử dụng, tự dựng đầu ra, chấm theo
rubric cố định và cập nhật skill từ bằng chứng.

## Điểm xuất phát đã có bằng chứng

| Nội dung | Trạng thái |
|---|---|
| Nguồn skill | v0.7 nghiên cứu trong repo, chưa cài thành personal skill |
| Backend | Morph baseline + T006 packed-timeline research path; artifact-tool 16:9 rect/ellipse/textbox; timing writer motion/scale/rotate, PowerPoint playback pending |
| Kiểm tra tự động | 55 unit tests pass trên T006 branch; thêm py_compile + Node/shell syntax; chưa phải schema OOXML đầy đủ |
| E002 | Sửa 14 khai báo textbox; checker H001 giữ nguyên đạt 93/93; ảnh không đổi |
| H002/E003 | Nhãn ORBIT chồng 2→0 theo mô hình tuyến tính |
| H003/E004 | Nhãn Việt dài chồng 4→0; khối nền vẫn chồng 6→6 theo mô hình |
| T002 | Giữ label 0/6; siết carrier giảm 6/6→0/6, focus emphasis tĩnh 4→3; native pending |
| T003 | Tách lớp 2D trên hai chủ đề; binding fixture 16→0; sửa wrap số trên 27 vị trí; choreography nguồn và native pending |
| T005 | Intent nghiêm ngặt cho chuỗi 6 thao tác, 2 chủ đề/22 ảnh cuối; chord proxy 65,608→1,916 px; vẫn click-through, chưa native playback |
| File và ảnh | PPTX tại `output/`, bằng chứng và ảnh cuối trong từng experiment |
| PowerPoint playback | Chưa có; M1 chưa đạt, điểm native motion và editing để null |

`E01`–`E04` trong đề cương là nhóm nghiên cứu dự kiến; `E001`–`E004` là mã
thí nghiệm thực tế. Không nhầm E004 nhãn dài với benchmark E04 gồm 18 lượt.
H001/H002 có agent dùng đề mới với ngữ cảnh hạn chế; H003 là đề mới do cùng
người nghiên cứu thực hiện, không phải holdout độc lập. E002/E003/E004 là các
lượt sửa theo lỗi đã biết, không phải đề chưa từng thấy.

## Chỉ thị kiến trúc mới — ưu tiên cao nhất

Người dùng đã sửa hướng phát triển ngày 04/10/2026: **không dùng mặc định một
chuyển động/state = một slide**. Đọc `docs/MOTION_PACKING.md`. Nếu nhiều chuyển
động dùng chung semantic objects/assets và vẫn thuộc cùng một scene, phải gom
tối đa số chuyển động khả thi vào **một slide timeline native**. Chỉ tách slide
khi có lý do semantic hoặc giới hạn PowerPoint/backend được ghi rõ.

T005 nhiều waypoint/slide hiện là baseline Morph lịch sử, không phải kiến trúc
mục tiêu. T006 phải thử nén chuỗi burst → orbit → focus → split → reassemble →
restore xuống 1 slide vì resource set đã tồn tại xuyên suốt. Nếu không đạt 1
slide, phải chứng minh blocker và dùng số slide tối thiểu.

Bước planning có ở `skills/pptx-motion/references/native-timeline.md` và
`scripts/pack_timeline.py`: geometry T005 được gom 12 legacy states thành
1 slide/6 stage, orbit waypoint thành motion-path points.

T006 hiện đã có writer native hạn chế: `scripts/add_timeline.py` ghi motion,
scale và rotate vào một packed timing group; `scripts/run_timeline_experiment.sh`
nối validate → artifact-tool source → textbox normalize → timing → finalizer.
Branch CI đã pass 55 tests + Python/Node/shell syntax. Đọc
`experiments/T006-20261004-native-timing/REPORT.md` trước khi sửa writer.
PowerPoint exact-file playback vẫn chưa có, nên không gọi writer là verified.

## Chặng mới nhất

PR #3, `experiments/T005-20261004-codex-choreography/REPORT.md`: compound intent compiler `scripts/choreography.py`, hai PPTX và transfer agent. Lỗi oracle waypoint đã sửa và giữ test. Người dùng ưu tiên hiệu ứng phức tạp bám ý định, không chỉ tăng số khối. Nhận T006 native timeline/path tiếp theo nếu phù hợp môi trường, hoặc T001 exact-hash playback. Đây là một recipe hạn chế, chưa hiểu mọi prompt hay chứng minh motion ấn tượng. Không cài personal skill trong lượt nghiên cứu.

PR #1, `experiments/T003-20261004-codex-layer01/REPORT.md`: giữ cả thất bại và sửa, generator `scripts/layer_separation.py`, reference `layer-separation.md`. Đọc CHECKPOINT trong experiment và claim trước khi nhận việc. T003 chỉ hoàn tất phần recipe 2D; cần quan sát choreography nguồn và playback để kết luận hiệu ứng ấn tượng. Không dựng lại 5 file đã lưu nếu chưa có giả thuyết mới.

## Việc có giá trị nhất để nhận

| Task | Phần việc | Điều kiện đầu ra |
|---|---|---|
| T001 | Playback PowerPoint | Exact hash, phiên bản, repair warning, video/ghi màn hình, kết luận từng chuyển cảnh |
| T002 | Đường đi khối nền | Giữ baseline/rubric H003, đo cả nhãn và khối, không hy sinh khả năng đọc |
| T003 | Công thức hiệu ứng mới | Nguồn sơ cấp, ý đồ rõ, hai chủ đề khác nhau, PPTX và đánh giá riêng từng lớp |
| T004 | Khả năng chạy ngoài Work | Backend adapter tách biệt, cùng hợp đồng, parity tests; giữ backend cũ làm đối chứng |
| T005 | Bám ý định compound prompt | Recipe đầu đã xong; giữ yêu cầu/giả định riêng, mở rộng chỉ với kiểm thử mới |
| T006 | Native timeline/path nâng cao | Writer/runner cấu trúc đã có; tiếp theo tạo full 1-slide candidate và exact-hash PowerPoint playback |

Mỗi task có brief và acceptance criteria trong `research/tasks/T00x.md`.
Danh sách này chưa giao việc cho model nào. Model có môi trường PowerPoint
nên nhận T001; model chỉ có Python có thể làm phân tích T002 hoặc chuẩn bị T004.

## Cách chạy

Đọc `docs/ENVIRONMENT.md`. Phần kiểm tra kế hoạch/hình học chỉ cần Python.
Kiểm tra ZIP/XML và unit tests cần lxml (đã thử 6.1.1 với Python 3.12.14).
Tạo PPTX hiện phụ thuộc runtime Work; không giả định máy khác có artifact-tool.

```bash
python3 scripts/check_environment.py
python3 scripts/validate_plan.py experiments/E004/plan.json
python3 -m unittest discover -s tests -v
python3 scripts/inspect_pptx.py output/PPTX_Motion_Lab_E004.pptx
python3 experiments/E004/verify_pair.py
```

Để dựng một plan mới trong Work, đọc skill Presentations của host, gọi marker
của host và dùng đường dẫn mới:

```bash
bash scripts/run_experiment.sh PLAN.json build/UNIQUE_RUN output/UNIQUE_DECK.pptx
# Hoặc với native-timeline-plan:
bash scripts/run_timeline_experiment.sh PLAN.json build/UNIQUE_TIMELINE_RUN output/UNIQUE_TIMELINE_DECK.pptx
```

Render file PPTX cuối, xem từng slide, rồi dùng `docs/POWERPOINT_QA.md` cho
playback thật. Không dùng PNG, LibreOffice hoặc mô phỏng HTML thay bằng chứng
animation PowerPoint. Không nới rubric để giấu lỗi hoặc gọi sơ đồ khối đơn
giản là đã đạt mục tiêu sáng tạo của sản phẩm.

## Prompt giao cho model khác

> Tiếp tục PPTX Motion Lab tại https://github.com/togcoder/skill-for-pptx.
> Đọc AGENTS.md, HANDOFF.md, docs/STATUS.md, docs/MOTION_PACKING.md và skill nguồn. Kiểm tra task/nhánh/PR
> đang chạy, nhận một task chưa có người làm phù hợp môi trường rồi tạo nhánh
> riêng. HARD RULE: slide là scene/execution container, không phải motion frame;
> khi các action dùng chung resource set, pack tối đa vào một native slide timeline
> và không tạo waypoint/state slide chỉ vì dễ làm. Mọi slide boundary thêm mới phải
> có lý do semantic/kỹ thuật. Giữ baseline và rubric, làm một thay đổi có giả thuyết rõ, tạo bằng
> chứng, lưu cả thất bại. Phân biệt kiểm tra cấu trúc, ảnh tĩnh và playback
> PowerPoint. Cập nhật báo cáo, nguồn skill nếu có cải thiện được chứng minh,
> và mở PR kèm handoff cho lượt sau. Nếu hết quota, lưu checkpoint nếu còn làm
> được, dừng lượt, không mua thêm hoặc lặp yêu cầu.

Repo private: mỗi model/agent cần phiên GitHub được chủ tài khoản cấp quyền.
Link repo không tự cấp quyền truy cập. Không đưa token vào prompt hoặc repo.

## Lịch sử và điểm tiếp tục

Đọc `docs/RECOVERY.md` và `docs/GITHUB_HANDOFF.md`. Lịch sử trước khi nhập GitHub
được giữ nguyên trong `archive/pre-github-v0.4.bundle`; nhánh main GitHub giữ
commit README khởi tạo của chủ repo rồi nhận snapshot dự án. Snapshot không
phải một nghiên cứu mới, và không reset các kết quả đã có.

Khi xong một chặng, ghi commit đầu vào, file đầu ra/hash, lệnh đã chạy, lỗi,
giới hạn và bước tiếp. Chỉ cập nhật checkpoint chính khi tích hợp kết quả đã
review. Các model có thể nghiên cứu song song ở nhánh riêng theo quy trình
claim, nhưng không cùng ghi một experiment hoặc force-push main.
