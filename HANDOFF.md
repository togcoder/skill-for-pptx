# Handoff — PPTX Motion Lab

Repo chính: https://github.com/togcoder/skill-for-pptx (private).
Chủ dự án: togcoder. Cập nhật bàn giao: 04/10/2026.

## Bắt đầu trong 5 phút

1. Fetch nhánh mới nhất, xem thay đổi chưa commit và các nhánh/PR đang mở.
2. Đọc `AGENTS.md`, tài liệu này, `docs/PRODUCT_TARGET.md`, `docs/STATUS.md`,
   `docs/MOTION_PACKING.md`, `docs/CLICK_BEAT_CHOREOGRAPHY.md` và
   `skills/pptx-motion/SKILL.md`. Đọc reference theo phần việc, không nạp toàn bộ
   lịch sử thí nghiệm vào ngữ cảnh nếu không cần.
3. Đọc `docs/COLLABORATION.md`, chọn một task chưa có người làm trong
   `research/tasks/`, rồi tạo nhánh riêng. Xác nhận claim trước khi dựng bài thử.
4. Chạy `python3 scripts/check_environment.py` để chọn phần việc môi trường hỗ trợ.
5. Đọc brief, rubric và report của baseline liên quan. Giữ nguyên baseline.

## Mục tiêu sản phẩm

Đọc `docs/PRODUCT_TARGET.md`. Đích đến là **AI Motion Director cho PowerPoint có
sẵn**: nhận deck hiện hữu, hiểu report/story và resource; nếu có script thì bám
script, nếu không thì dùng notes, choreography native đang có, hoặc tự suy luận
trình tự báo cáo rồi tạo script; chỉ nghiên cứu ngoài khi phù hợp; thiếu component
mới tạo thêm trong đúng design language của deck; sau đó giữ/nối/sửa motion hiện
có thay vì xóa timing cũ, và giữ slide count/order/content theo mặc định. North-star:
người dùng có thể chỉ thả PPTX + mục tiêu chung, không cần chỉ từng animation.

Fresh-deck prompt, QCC và các recipe hiện tại là bài thử/backend building blocks,
không phải đích sản phẩm cuối.

## Điểm xuất phát đã có bằng chứng

| Nội dung | Trạng thái |
|---|---|
| Nguồn skill | v0.7 nghiên cứu trong repo, chưa cài thành personal skill |
| Backend | Morph baseline + T006 packed-timeline research path; artifact-tool 16:9 rect/ellipse/textbox; timing writer motion/scale/rotate, PowerPoint playback pending |
| Kiểm tra tự động | 150 unit tests tại T018 QA review; Python compile và PowerShell syntax parse pass; chưa phải schema OOXML đầy đủ hoặc native playback |
| E002 | Sửa 14 khai báo textbox; checker H001 giữ nguyên đạt 93/93; ảnh không đổi |
| H002/E003 | Nhãn ORBIT chồng 2→0 theo mô hình tuyến tính |
| H003/E004 | Nhãn Việt dài chồng 4→0; khối nền vẫn chồng 6→6 theo mô hình |
| T002 | Giữ label 0/6; siết carrier giảm 6/6→0/6, focus emphasis tĩnh 4→3; native pending |
| T003 | Tách lớp 2D trên hai chủ đề; binding fixture 16→0; sửa wrap số trên 27 vị trí; choreography nguồn và native pending |
| T005 | Intent nghiêm ngặt cho chuỗi 6 thao tác, 2 chủ đề/22 ảnh cuối; chord proxy 65,608→1,916 px; vẫn click-through, chưa native playback |
| T006 full candidate | 1 slide/31 objects/6 stages/82 behaviors; sửa lỗi mất chữ mở đầu; exact final render đã xem; 47 path-origin model mismatches còn cần native diagnosis |
| T006 semantics matrix | 4 exact one-slide fixtures isolate local/anchored path × remove/hold fill; 83 tests, all static renders checked; native winner pending |
| File và ảnh | PPTX tại `output/`, bằng chứng và ảnh cuối trong từng experiment |
| PowerPoint playback | Chưa có; M1 chưa đạt, điểm native motion và editing để null |

`E01`–`E04` trong đề cương là nhóm nghiên cứu dự kiến; `E001`–`E004` là mã
thí nghiệm thực tế. Không nhầm E004 nhãn dài với benchmark E04 gồm 18 lượt.
H001/H002 có agent dùng đề mới với ngữ cảnh hạn chế; H003 là đề mới do cùng
người nghiên cứu thực hiện, không phải holdout độc lập. E002/E003/E004 là các
lượt sửa theo lỗi đã biết, không phải đề chưa từng thấy.

## Chỉ thị kiến trúc mới — ưu tiên cao nhất

Latest QA checkpoint: `experiments/T018-20261005-qa-evidence-review/REPORT.md`
(PR #21). A 26-case synthetic evidence review repaired 18 false click passes.
The complete suite now has 150 tests. Use `docs/POWERPOINT_NATIVE_HARNESS.md`
for the existing Windows probe and exact-artifact manifest instead of building
another harness. The original T018 branch is preserved. No native playback has
occurred; click indices cannot certify final animation states or M1 acceptance.

Latest exact-file checkpoint: `experiments/T006-20261004-packed-validation/REPORT.md`.
The full candidate now exists. Start from its frozen hash and playback checklist,
not another duplicate build. Resolve origin/fill/trigger semantics with a native
two-stage path fixture before extending this timing writer. PR #5 was closed as
superseded; PR #11 owns this validation experiment. No actual playback yet.

The requested two-stage fixture now exists at
experiments/T006-20261004-motion-semantics-matrix/REPORT.md with four exact
hashes and a playback checklist (PR #12). Do not generate another origin/fill
matrix. Play all four files in PowerPoint first; production timing remains
unchanged until that evidence exists.

Người dùng đã sửa hướng phát triển ngày 04/10/2026: **không dùng mặc định một
chuyển động/state = một slide**. Ngày 05/10/2026 người dùng sửa tiếp: **gom vào
một slide không có nghĩa click đầu chạy sạch mọi motion**. Đọc cả
`docs/MOTION_PACKING.md` và `docs/CLICK_BEAT_CHOREOGRAPHY.md`. Nếu nhiều chuyển
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

T006/T010 hiện có hai mode writer: v0.1 giữ one-click packed timing làm baseline
lịch sử; v0.2 tạo nhiều presenter click-beat trong cùng slide. `scripts/add_timeline.py`
ghi motion, scale và rotate; `scripts/run_timeline_experiment.sh`
nối validate → artifact-tool source → textbox normalize → timing → finalizer.
Historical T006 CI đã pass 55 tests; T010 click-beat hiện pass 86 tests + Python compile. Đọc
`experiments/T006-20261004-native-timing/REPORT.md` trước khi sửa writer.
PowerPoint exact-file playback vẫn chưa có, nên không gọi writer là verified.

T007 đã đi thêm một bước cho deck thật: `scripts/patch_existing_timeline.py`
target object bằng slide-local native ID + name, không yêu cầu `!!`, giữ
untargeted slide byte-identical và từ chối timing cũ chưa biết merge. Intake có
`design_profile` để làm cơ sở sinh component đúng font/palette/geometry.
Đọc `experiments/T007-20261004-source-object-patcher/REPORT.md`.

## Chỉ thị T017 — generic motion phải giữ semantic beat/click

Một motion beat có thể compile thành nhiều stage. `stagger-reveal` và
`focus` là regression chuẩn: không được biến mỗi stage thành click riêng.

Chart vẫn phải đi data-motion, không được dùng `shape_entrance` để né chart
semantics. Move/rotate chỉ compile khi có tham số cụ thể.

H001 hiện là transfer fixture thật cho generic path. PowerPoint runtime QA là
ưu tiên cao hơn việc mở rộng effect gallery.


Chart/KPI pipeline đã chạy qua PPTX package thật. Model sau không được đánh giá
chỉ bằng isolated slide XML.

Bài học mới: ChartML có thể dùng `strLit/numLit` thay vì `strCache/numCache`;
inventory phải hiểu cả hai. Không sửa test bằng cách bỏ category-count check.

T016 giữ byte-identical cho untargeted slide, chart part và relationship part,
nhưng PowerPoint playback vẫn pending.


Với slide mà toàn bộ motion beats đều là data-motion được hỗ trợ, dùng
`scripts/compile_data_motion_patch.py` để bridge Director v0.3 → patch v0.4.
Compiler giữ click grouping, resolve source object và ghi fallback counter.

Nếu slide còn generic motion chưa có execution contract, **block slide**. Không
được bỏ beat đó rồi compile phần còn lại, vì sẽ làm sai nhịp T010/T011.

Bài học test: `bldLst` có thể chứa lẫn `bldP` và `bldGraphic`; không suy
semantic từ vị trí trong danh sách, phải match type + spid.


Counter v0.4 không rewrite KPI source. Nó clone source shape làm proxy trung gian,
animate các proxy trong cùng click beat, rồi reveal chính source shape ở cuối.
Nếu source text đã đổi so với `preserve_final_text`, abort.

Đừng đổi hướng sang tạo một textbox final mới chỉ vì dễ hơn; như vậy sẽ phá
source preservation. Playback PowerPoint vẫn pending, đặc biệt visibility của
entrance effect trước thời điểm chạy.

Chặng có giá trị tiếp theo: adapter Director v0.3 → patch plan v0.4 để chart/KPI
semantic decisions đi thẳng tới execution mà không cần model viết tay low-level
effect JSON.


Model sau không được quay lại animate chart như generic shape nếu v0.3 patch path
phù hợp. Dùng `chart_entrance`, giữ exact source chart, và để writer fan-out
series/category/point qua `a:chart` sub-targets.

Density guard mặc định 24. Nếu fan-out bị hạ granularity, phải giữ receipt và
không gọi đó là recipe gốc đã được thực thi đầy đủ.

Native PowerPoint playback cho chart vẫn pending. T014 tiếp theo: counter
component dạng stacked source-style proxies + sequential exit, kết thúc bằng
textbox nguồn không thay đổi.


Khi inventory gặp chart, model phải đọc
`skills/pptx-motion/references/data-motion-recipes.md` và dùng chart subtype /
series/category/point count để chọn recipe. Director v0.3 sẽ từ chối chart target
không có `data_motion`.

Standalone number chỉ là candidate. Chỉ khi narrative coi nó là hero KPI/result/
target thì dùng counter. Counter không được đổi final source value/format và
không tự tạo click mới.

Backend native chart-build và counter component vẫn pending; không tuyên bố
playback chỉ vì semantic tests pass.

## Chỉ thị T011 — AI phải hiểu nhịp trước khi viết XML

T010 đã sửa writer. T011 đưa cùng nguyên tắc lên tầng Director: **motion beat
không đồng nghĩa click beat**. Director v0.2 phải nhóm các motion action thành
presenter click-beats, ghi `stable_state`, `pause_after`, và từ click thứ hai
ghi `boundary_reason`. Existing-deck patch v0.2 giữ nhiều click groups trên một
slide mới chưa có timing. T008 vẫn chịu trách nhiệm merge an toàn với timing cũ.

Model sau không được lấy danh sách motion rồi tự động map "mỗi motion = click"
hoặc "mọi motion = một click". Nhịp click phải được quyết định từ narrative.

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
| T007 | Existing Deck Motion Director | Intake + director contract + arbitrary source-object timing patcher + design fingerprint; tiếp theo director-beat compiler và helper-component insertion |
| T008 | Existing Motion Continuation | Đọc timing có sẵn, preserve/extend/retime có chủ đích; không xóa timing để làm lại từ đầu |
| T009 | Autonomous No-Script Benchmark | Chỉ PPTX + mục tiêu chung → tự dựng report script → gap → component → motion → exact-file playback |
| T010 | Presenter-paced Click Beats | Slide → click beat → stage → effects; giữ 1 slide nhưng dừng đúng nhịp presenter, không dùng delay để giả thời gian nói |
| T011 | Director Click Rhythm | Bắt AI Director tự nhóm motion beats thành presenter clicks có purpose/stable state/boundary reason, rồi giữ nhịp đó khi patch existing deck |
| T012 | Semantic Data Motion | Nhận diện chart subtype + hero KPI; chart dùng recipe riêng theo encoding, KPI highlight dùng count-up/down và giữ nguyên giá trị nguồn |
| T013 | Native Chart Execution | chart_entrance v0.3 → a:chart sub-targets + bldGraphic/bldChart + density guard; 112 tests pass; PowerPoint playback pending |
| T014 | KPI Counter Execution | number_counter v0.4 → source-style proxy stack + entrance/exit chain + untouched source final value; 120 tests pass; playback pending |
| T015 | Director → Execution | compile Director v0.3 data-motion → patch v0.4, preserve click groups, explicit counter fallback, block mixed unsupported slides; 126 tests pass |
| T016 | Real-Package Integration | real PPTX → inventory → Director → compiler → chart+counter patch → readback; literal ChartML parser bug fixed; 130 tests pass |
| T017 | Generic Report Motion | Director v0.4 + patch v0.5: reveal/stagger/focus/explicit move/rotate; H001 real-deck transfer; 140 tests pass |

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
> Đọc AGENTS.md, HANDOFF.md, docs/PRODUCT_TARGET.md, docs/STATUS.md, docs/MOTION_PACKING.md, docs/CLICK_BEAT_CHOREOGRAPHY.md và skill nguồn. Kiểm tra task/nhánh/PR
> đang chạy, nhận một task chưa có người làm phù hợp môi trường rồi tạo nhánh
> riêng. Nếu đầu vào là PPTX có sẵn: inventory trước, dùng script có sẵn nếu có; nếu không thì notes → existing timing/choreography → visible narrative → inferred narrative → researched narrative; giữ source content/slide count mặc định và chỉ tạo component mới khi có narrative gap. HARD RULE: slide là scene/execution container, không phải motion frame;
> khi các action dùng chung resource set, pack tối đa vào một native slide timeline
> và không tạo waypoint/state slide chỉ vì dễ làm. SAU KHI pack, phải chia timeline
> thành presenter click-beats: trạng thái ổn định cần thuyết trình thì dừng chờ click;
> motion đồng thời dùng with-previous; motion nối tự động dùng after-previous. Không
> dùng delay dài để giả thời gian presenter nói. Mọi slide/click boundary phải có lý do. Giữ baseline và rubric, làm một thay đổi có giả thuyết rõ, tạo bằng
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
