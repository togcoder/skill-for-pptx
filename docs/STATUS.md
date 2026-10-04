# PPTX Motion Lab — checkpoint

## T016 real-package data motion — 2026-10-05

T012–T015 now pass a real PPTX package integration, not only isolated XML.

A fixture derived from the valid H001 deck adds a native two-series/four-category
line chart plus `98.5%` KPI, then executes:

`inventory -> Director v0.3 -> compiler -> patch v0.4 -> output inventory`.

First CI exposed a genuine inventory gap: inline ChartML `strLit/numLit` points
were not counted. Parser fixed; regression added.

Final run 37239255072: **130/130 tests pass** + Python compile.

Package audit confirms two presenter clicks, source KPI preservation, native
chart build read-back, unchanged slide count, and byte-identical untargeted
slide/chart/relationship parts.

PowerPoint runtime playback remains pending.

Task: `research/tasks/T016-real-package-data-motion.md`.
Report: `experiments/T016-20261005-real-package-data-motion/REPORT.md`.

## T015 Director → execution compiler — 2026-10-05

The manual bridge between Director v0.3 and patch v0.4 is removed for complete
data-motion slides.

`scripts/compile_data_motion_patch.py` compiles chart/KPI semantic beats into
`chart_entrance` / `number_counter`, resolves exact source targets and
preserves Director click grouping.

Safety: mixed/unsupported slides are blocked instead of partially compiled.
Odometer → stepped-text fallback is explicit and can be disabled.

Final CI run 37238859486: **126/126 tests pass** + Python compile. Integration
regression preserves two presenter clicks across Director → patch → timing
read-back.

PowerPoint playback remains pending.

Task: `research/tasks/T015-director-to-execution.md`.
Report: `experiments/T015-20261005-director-to-execution/REPORT.md`.

## T014 KPI counter execution — 2026-10-05

T012 hero-metric counters now have a structural v0.4 execution path.

`number_counter` clones the exact source KPI textbox for intermediate values,
preserves style/geometry, sequences proxy entrance/exit inside one presenter
click beat, and reveals the untouched source textbox last.

Counter interpolation preserves prefix/suffix/decimal/grouping and rejects
source-text drift. The source final value is never rewritten.

CI run 37238539416: **120/120 tests pass** + Python compile.

Critical runtime gate remains: exact PowerPoint playback must prove that generated
entrance effects hide source/proxy shapes until scheduled and that only one value
is visible at a time.

Task: `research/tasks/T014-kpi-counter-execution.md`.
Report: `experiments/T014-20261005-kpi-counter-execution/REPORT.md`.

## T013 native chart execution — 2026-10-05

T012 semantic chart recipes now have a structural native execution path.

`existing-deck-timeline-patch` v0.3 supports `chart_entrance` on exact
existing chart graphicFrames and emits:

- chart sub-targets via `p:graphicEl/a:chart`;
- `seriesIdx/categoryIdx/bldStep`;
- `p:bldGraphic/p:bldSub/a:bldChart`;
- chart-type-specific conservative entrance filters;
- density guard with requested/effective build receipt.

Default fan-out limit is 24; excessive point-level builds degrade to series or
whole-chart rather than creating hundreds of effects.

CI run 37238145782: **112/112 tests pass** + Python compile. Structural read-back
confirms chart build mode and sub-target indices.

PowerPoint playback is still pending; this is not a native-playback claim.

Task: `research/tasks/T013-native-chart-execution.md`.
Report: `experiments/T013-20261005-native-chart-execution/REPORT.md`.

## T012 semantic data motion — 2026-10-05

User added a new product requirement: charts need type-specific animation, and
standalone hero metrics need dedicated number counting.

Inventory now recognizes classic ChartML subtype/dimensions and standalone
numeric candidates. `scripts/data_motion_recipes.py` maps chart semantics to
distinct defaults (baseline-grow, series-trace, segment-sweep, point-build,
etc.) and emits source-preserving KPI counter recipes.

Director v0.3 requires chart-targeting beats to declare type-specific data motion.
Hero KPI counter plans must preserve the exact source numeric value and format.
Data motion remains subordinate to T010/T011 click-beat rhythm.

CI run 37236839744: **103/103 tests pass** + Python compile.

This is semantic/structural evidence only. Native chart build and counter
playback remain pending.

Reference: `skills/pptx-motion/references/data-motion-recipes.md`.
Report: `experiments/T012-20261005-data-motion-recipes/REPORT.md`.

## T011 director click rhythm — 2026-10-05

T010 established click groups in the timing writer. T011 moves that decision
upstream into the AI Director.

Canonical semantic hierarchy:

`Deck Narrative -> Slide Objective -> Click Beat -> Motion Beat -> Effects`

Director v0.2 requires each click beat to record audience purpose, stable state,
pause type, and (after the first click) a narrative boundary reason. It rejects
flat/ambiguous grouping, nested `on-click`, and incomplete beat partitions.

Existing-deck patch v0.2 now preserves the same click grouping on a fresh
unanimated source slide, so multi-click pacing no longer requires multiple
slides.

CI run 37234829380: **92/92 tests pass** + Python compile. A regression patches a
real existing-deck fixture to two click groups and reads the groups back through
the deck inspector.

T009 no-script benchmark now explicitly penalizes whole-slide autoplay,
one-click-per-motion overfragmentation and premature reveals.

Report: `experiments/T011-20261005-director-click-rhythm/REPORT.md`.

## T010 presenter-paced click beats — 2026-10-05

User corrected the packed-motion target: one physical slide may contain many
motions **and many presenter clicks**. Packing and pacing are now separate.

Canonical rule: `docs/CLICK_BEAT_CHOREOGRAPHY.md`.
Task: `research/tasks/T010-click-beat-choreography.md`.

Native timeline v0.2 now models:

`Slide -> Click Beat -> Stage -> Effects`

T005 benchmark remains **1 slide / 82 behaviors**, but is repartitioned from the
legacy one-click chain into **4 click beats**:

1. burst;
2. orbit;
3. focus -> split;
4. reassemble -> restore.

`scripts/add_timeline.py` keeps v0.1 one-click behavior for historical
reproducibility and uses multiple `mainSeq` click groups for v0.2. The
existing-deck inspector also exposes click-group structure so authored presenter
rhythm can be preserved.

CI evidence: run 37234235795 — **86/86 tests pass**, Python compile pass.
Integration regression locks 4 clickEffect stages, 2 afterEffect stages and
82 behaviors on one slide. Native PowerPoint playback is still pending, so this
is structural evidence only.

Report: `experiments/T010-20261005-click-beat-choreography/REPORT.md`.

Cập nhật ngày 04/10/2026, giờ Việt Nam. Phiên bản nguồn nghiên cứu v0.7 (thêm T005 compound intent).

## T006 controlled motion semantics matrix — 2026-10-04 20:08 UTC

PR #12 prepares four exact one-slide files that differ only by stage-local vs
authored-layout motion paths and fill=remove vs fill=hold. Every file has two
900 ms motion behaviors in one click group. Four finalizers pass with no layout
warnings; all static renders were viewed and are pixel-identical. Exact audit
finds no uncontrolled package/XML difference. **83 tests pass.**

No PowerPoint runtime was available, so there is no winning native variant and
the production writer/source skill remain unchanged. Highest-value next action:
run all four exact hashes using
experiments/T006-20261004-motion-semantics-matrix/playback-checklist.json.
Only then revise path anchoring/fill and rebuild the full packed candidate.

## T006 full packed candidate — 2026-10-04 19:16 UTC / 05-10 Vietnam

Built `output/T006_packed_candidate.pptx`: **1 slide, 31 native objects, 6 stages,
82 encoded behaviors, 7,100 ms planned duration**. Exact SHA-256:
`41c4fb7865ea587e0d426fccf4de2c82fc1db731147a92a4fba28926b0e52094`.

Full pipeline initially failed because packing dropped state-local opening text.
Preserving initial text fixes the abort; the exact final file passes finalization
and its sole static render was viewed. **79 tests pass.** Failed raw artifact,
plans, receipt, hashes and full report are in
`experiments/T006-20261004-packed-validation/` (PR #11).

Independent audit found **47 path-origin mismatches under the authored-layout
coordinate model**, with maximum 543.766 px. This is a conditional geometry
diagnostic, not observed playback. All 82 behaviors currently use fill=remove.
Keep the evidence; do not promote native compatibility. Next: exact-file playback
and a PowerPoint-authored two-stage path fixture to resolve origin/fill/trigger
semantics. Do not rebuild this same candidate without a new hypothesis.
T007/T008 autonomy work remains as below; source skill is still research v0.7.

## T007 autonomy + existing-motion continuation

The product target is now explicit at the stronger autonomy level requested by
the user: **PPTX + optional high-level goal is enough input**. The model should
not require object-by-object animation instructions. It must discover/use a
script, infer one when absent, research reporting structure only when necessary,
reuse deck resources, synthesize only justified missing components, and return
the same report motion-directed.

Existing native animation is now first-class source evidence. Script priority is:
provided script → speaker notes → existing timing/choreography → visible
narrative → inferred narrative → researched narrative. Existing timing must be
preserved/extended by default rather than rejected or deleted.

`inspect_existing_deck.py` now exposes transition and timing choreography:
effect types, source targets, durations, start conditions, numeric delays,
build groups and an order hint with an explicit structural-evidence boundary.

Branch CI run 37215400829: **75/75 tests pass** plus Python compile. New tasks:
`T008-existing-motion-continuation.md` and
`T009-autonomous-no-script-benchmark.md`.

Report: `experiments/T007-20261004-autonomy-existing-motion/REPORT.md`.

## Product destination — T007 Existing Deck Motion Director

Người dùng đã mở rộng đích đến: hệ thống phải nhận **file PPTX có sẵn** và tự
đạo diễn chuyển động. Nếu có script/storyboard thì bám script. Nếu không có,
ưu tiên speaker notes, sau đó tự phân tích trình tự báo cáo; chỉ nghiên cứu ngoài
khi cần và phù hợp. Nếu narrative thiếu component thì tự tạo helper component
trong đúng visual framework của deck, không sinh decoration vô cớ.

Tài liệu chuẩn: `docs/PRODUCT_TARGET.md`.
Task: `research/tasks/T007-existing-deck-motion-director.md`.

Scaffold hiện có:
- `scripts/inspect_existing_deck.py`: source-hash + slide/object/text/geometry/
  relationships/timing/transition/notes/theme/media inventory;
- `skills/pptx-motion/references/existing-deck-director.md`: director contract;
- `scripts/validate_director_plan.py`: buộc script source, source grounding,
  preserve slide count, target resource validity và justification cho component;
- final branch CI run `37214340363`: **67/67 tests pass**, `py_compile` pass.

Report: `experiments/T007-20261004-existing-deck-director/REPORT.md`. Phần còn
pending: inference trên deck thật không có script, synthesis component theo design
system, director-beat → T006 timeline adapter, và patch/playback exact-file.

Default mới: preserve source slide count/order/content; resource cũ được reuse
trước; same-resource motion phải pack trong slide; generated component chỉ lấp
narrative gap.

### T007 source-object patcher checkpoint

Đã thêm `scripts/patch_existing_timeline.py` và
`existing-deck-timeline-patch.md`: object deck thật được target bằng source
slide + native `cNvPr id` + name, không cần `!!`. Patcher kiểm source SHA-256,
chỉ sửa slide được chọn, giữ slide khác byte-identical, preserve transition và
từ chối merge timing cũ mù quáng.

Deck intake cũng đã có `design_profile` gồm font/fill/line/text-color/geometry
frequency để làm basis khi sau này phải sinh helper component.

Final temporary CI run `37214809106`: **73/73 tests pass** + `py_compile`
pass. Report: `experiments/T007-20261004-source-object-patcher/REPORT.md`.

Phần còn thiếu cho product path: director beat → concrete patch-plan compiler;
native helper-component insertion + re-inventory; no-script narrative test trên
deck thật; exact-file PowerPoint playback.

## T006 native timing writer — đã có backend cấu trúc, playback còn pending

T006 đã tiến từ planning sang writer native hạn chế. `scripts/pack_timeline.py`
vẫn nén T005 candidate 12 legacy states thành 1 semantic slide/6 stage và
transfer 10→1. `scripts/add_timeline.py` hiện ghi `p:timing` cho motion path,
scale và rotate trên cùng slide: waypoint nằm trong path, các stage dùng delay
tích lũy và các effect cùng stage chạy song song trong một packed click group.

Đường dựng end-to-end mới:
`validate_timeline.py -> render_timeline.mjs -> normalize_timeline_textboxes.py
-> add_timeline.py -> host finalizer`, gọi bằng
`scripts/run_timeline_experiment.sh`.

Bằng chứng tự động: GitHub Actions branch-only run 37213501515 đạt
`py_compile`, **55 unit tests**, `node --check` renderer và `bash -n` runner.
Workflow tạm đã xóa sau kiểm tra. Prototype 1 slide/2 shape sau patch vẫn pass ZIP
CRC, mở lại bằng python-pptx và LibreOffice export PDF. Đây là bằng chứng package,
**không phải playback PowerPoint**.

Report: `experiments/T006-20261004-native-timing/REPORT.md`.
Native playback/editability exact-file vẫn pending; M1 chưa đạt.

## Chỉ thị mới — resource-local motion packing

Người dùng yêu cầu đổi kiến trúc: không coi mỗi chuyển động/state là một slide.
Khi các action dùng chung resource set và cùng semantic scene, ưu tiên gom tối đa
vào một native slide timeline. Tài liệu chuẩn: `docs/MOTION_PACKING.md`.

T005 12-state Morph giữ nguyên làm baseline lịch sử. Nó không còn là mẫu kiến
trúc mục tiêu. T006 phải cố gắng tái hiện burst → orbit → focus → split →
reassemble → restore trong 1 slide với nhiều track/timing/trigger native; nếu
PowerPoint/backend buộc tách, ghi blocker và dùng số slide tối thiểu. Các model
sau phải đọc rule này trước khi thiết kế choreography.

## Kết quả mới nhất — T005

Ưu tiên mới của người dùng là hiệu ứng phức tạp từ một câu lệnh ngắn, giữ đúng ý định. PR #3 và `experiments/T005-20261004-codex-choreography/REPORT.md` có compiler intent nghiêm ngặt cho chuỗi bung nút, xoay vòng, phóng đối tượng, tách lớp, ghép lại và trở về. AI diễn giải prompt; compiler chỉ nhận dữ liệu có cấu trúc, không phải NLP tổng quát.

Hai PPTX native: candidate 12 trạng thái/31 đối tượng, transfer 10 trạng thái/22 đối tượng. 7 nhóm kiểm tra geometry và package parity đều đạt trên mỗi file. Đã xem riêng đủ 22 ảnh cuối. 41 unit tests đạt. Đối chứng cố ý bỏ waypoint cho sai lệch bán kính tuyến tính 65,608 px; candidate còn 1,916 px. Không coi số này là độ mượt phát thực tế.

Lỗi có ích: tổng góc xoay đúng vẫn có thể che waypoint sai; đã giữ test đột biến và sửa kiểm tra từng waypoint/ràng buộc nhãn. Agent mới tạo bài học tập 8 nút, ngược chiều 60°, nút 6, 3 lớp; parent xuất file. Agent đã đọc brief do AGENTS yêu cầu nên không gọi đây là kiểm thử mù hoàn toàn.

Giới hạn quan trọng: vẫn là 2D Morph theo từng lần bấm, một recipe hạn chế, hình học còn đơn giản; chưa có bằng chứng hiệu ứng ấn tượng hoặc playback PowerPoint. Không phải skill hoàn chỉnh hiểu mọi ý tưởng phức tạp, chưa cài personal skill. Bước tiếp ưu tiên T006 native timeline/path và T001 playback exact-hash; giữ nguyên T005 làm đối chứng.

File: `output/T005_compound_candidate.pptx` SHA-256 `05ddf33c89725dbb66083f5130c549d59d9aa291893321a34cc68c6cf9e9cf58`; `output/T005_compound_transfer.pptx` SHA-256 `e87d37db4a76f51c56dac893bade9c2966960cbc6bfc869ebb5bceb3d8cb5e16`.

## Kết quả mới nhất — T002

PR #2, `experiments/T002-20261004-codex-tight-carriers/REPORT.md` giữ E004 bất biến và chỉ siết carrier quanh label. Trong cùng proxy tuyến tính, label giữ 0/6 cặp chồng và carrier giảm 6/6→0/6. Candidate có 3 slide, 8 đối tượng native/slide, 5 textbox/slide, 2 Morph 1100 ms; 3/3 ảnh cuối đã xem và 34 tests đạt. SHA-256 `c41f2289bfd662f2642ea611b119d8aeaf35678425cba4cf4b7ffe0640922186`.

Tradeoff: focus emphasis tĩnh chủ quan giảm 4/5→3/5; creative vẫn 2/5. Đây là sửa rủi ro geometry, không chứng minh motion đẹp hoặc playback đúng. Native motion/editing null. Nguồn v0.6 chưa cài personal skill. Bước tiếp: exact-hash PowerPoint playback so E004/T002, hoặc T004 portable backend; T002 tiếp theo phải có giả thuyết mới về emphasis/z-order.

## Kết quả mới nhất — T003

Đọc `experiments/T003-20261004-codex-layer01/REPORT.md` trước khi tiếp tục. Nhánh `work/T003-codex-20261004`, PR #1 có generator 3–5 lớp, nguồn và rubric đã đóng băng, hai chủ đề (QUANTA 5 lớp; học trực tuyến 4 lớp), 5 PPTX giữ cả thất bại và 15 ảnh cuối đã xem. Native parity đạt trên cả 5 file; repo có 34 tests đạt. Backend cũ và các baseline E001–E004/H001–H003 giữ nguyên.

Phép đo fixture ràng buộc: 16/60 child-state lệch → 0/60, max 64 → 0 px; đây là lỗi cố ý để thử quy tắc, không phải benchmark độc lập. Lỗi số thật được phát hiện bằng render: ô 42 px làm hai chữ số xuống dòng. Chỉ mở rộng thành 60 px, số lỗi quan sát QUANTA 15→0 và bài mới 12→0. Bài mới do agent ngữ cảnh riêng lập plan; parent xuất PPTX và sửa, không gọi là benchmark tự hành end-to-end. Bản nên dùng: `output/T003_layer_candidate_v2.pptx`, `output/T003_transfer_v2.pptx`.

T003 mới đạt phần recipe 2D và transfer cấu trúc/ảnh tĩnh. Chỉ đọc tutorial nguồn, chưa xem choreography nguồn; không tái hiện 3D extrusion. Native playback, sửa thật trong PowerPoint, M1 vẫn pending; điểm motion/editing null. Điểm sáng tạo tĩnh 3/5 là chủ quan, không phải đạt mục tiêu chuyển động ấn tượng. Nguồn v0.5 chưa cài thành personal skill.

Bước có giá trị tiếp: T001 phát exact-hash hai file v2; hoặc phần tiếp T003 xem animation nguồn thực rồi lập giả thuyết choreography mới; hoặc T002 xử lý carrier crossing cũ. Claim đầu tiên đã xong phạm vi nghiên cứu này; kiểm tra nhánh/PR mới nhất trước khi nhận phần tiếp, không lặp v1/v2.

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

Tại mốc bàn giao v0.4 chưa có claim nghiên cứu mới; T003 sau đó được nhận tại PR #1 như mục mới nhất phía trên. Luôn kiểm tra nhánh và PR mở để biết công việc đang chạy. Nguồn skill bổ sung công thức cyclic focus và phân biệt số trạng thái với số chuyển cảnh. Read của H002/E003 mở ở tư thế lớn; không có đoạn phóng lớn riêng trên slide đầu.

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

1. Hai đường ưu tiên: (a) dùng `output/T006_packed_candidate.pptx` đã freeze hash trong báo cáo packed-validation để kiểm playback PowerPoint và đối chiếu fixture hai chặng về origin/fill/trigger; (b) T007 lấy một deck thật 3–10 slide, inventory → script/infer → motion-direct một slide bằng resource có sẵn, tối đa một helper component, không đổi slide count. Không dựng lại candidate cũ nếu chưa có giả thuyết mới. Không quay lại waypoint slides nếu playback lỗi; sửa trong cùng slide và giữ baseline. T001/native exact-hash vẫn là cổng nghiệm thu; M1 pending.
2. Nếu chưa có PowerPoint, không lặp ma trận origin/fill vừa tạo. Chọn T007/T008 hoặc chuẩn bị một fixture native khác chỉ khi có biến số mới rõ ràng. Không gọi mô phỏng là playback hoặc tăng số đối tượng là tăng chất lượng hiệu ứng.
3. Chia phần việc theo task trong `research/tasks/`. Nhận claim/nhánh riêng trước khi làm để tránh trùng. Skill và renderer hiện vẫn phụ thuộc môi trường Work như `docs/ENVIRONMENT.md`.
4. Chuẩn bị công cụ thu bằng chứng trên PowerPoint Windows khi phù hợp, không giả lập kết quả. Benchmark 18 lượt chưa thực hiện.

## Khôi phục và lưu tiếp

GitHub `togcoder/skill-for-pptx` là nguồn làm việc chính. Clone/fetch main mới nhất, kiểm tra nhánh/PR và đọc HANDOFF.md. Đọc docs/RECOVERY.md để tra lịch sử trước khi nhập GitHub. Bundle và các checkpoint cloud cũ là snapshot phục hồi lịch sử; không ghi chúng đè lên repo mới hơn. Code và kết quả đã gắn GitHub được commit/push về đúng repo, không tạo bản sao code mới song song trong Library.
