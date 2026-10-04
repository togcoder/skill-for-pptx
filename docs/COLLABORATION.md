# Cộng tác giữa các model

## Nhận việc, tránh làm trùng

1. Đọc main mới nhất, `research/tasks/` và các PR/nhánh đang mở trước khi claim.
2. Dùng nhánh `work/T001-<agent>-<ngay>` theo task. Nhánh, PR và thông tin claim
   phải chỉ đúng tài khoản/agent đang chạy; không tự nhận thay agent khác.
3. Ghi claim trong `research/claims/T001-<agent>-<ngay>.md`, gồm task, người làm,
   UTC bắt đầu, base commit, phạm vi file, trạng thái, thời điểm checkpoint và
   bước tiếp. Push nhánh và mở draft PR trước khi làm phần đắt hoặc kéo dài.
4. Đọc lại claim/PR cạnh tranh. Một draft PR là dấu hiệu nhận việc, không phải
   khóa giao dịch tự động. Nếu trùng, chia phạm vi hoặc chọn task khác. Không
   suy diễn claim cũ là được phép ghi đè; kiểm tra tiến độ mới nhất trước.

Task có trạng thái queued trong main vẫn có thể đã được nhận trên một draft PR.
Luôn xem cả hai. Nếu không có quyền ghi, làm đọc/đánh giá và báo đúng giới hạn;
không tuyên bố đã claim hoặc gửi PR.

## Phân tách công việc

- Dùng experiment ID riêng, ví dụ `T002-20261004-agentA-run01`. Không chiếm E005
  mà chưa kiểm tra người khác đang dùng. ID E001–E004 và H001–H003 đã có baseline.
- Mỗi agent có worktree/build/output riêng. Dùng `git worktree add` khi cùng máy
  và transport Git hợp lệ; không reset hoặc xóa thay đổi của người khác.
- Agent nghiên cứu ghi báo cáo trong experiment của mình. Người tích hợp cập
  nhật `docs/STATUS.md` và task sau khi review để giảm xung đột checkpoint.
- Các thay đổi backend/validator/skill cần nêu tác động đến bài thử cũ. Nếu có
  xung đột, giữ cả bằng chứng và tái chạy kiểm tra phù hợp trước khi hợp nhất.

## Hợp đồng một thí nghiệm

Lưu tối thiểu: brief, giả thuyết, rubric đóng băng, base commit, plan hoặc mã
dựng, môi trường, lệnh, output/hash, kiểm tra cấu trúc, ảnh cuối đã xem, kết quả
playback nếu có, điểm/rationale, lỗi và next step. Dùng
`templates/EXPERIMENT_REPORT.md`.

Đề sau khi tune không được gọi là holdout. Khi dùng agent độc lập để thử skill,
chỉ đưa câu lệnh và tài nguyên cần dùng, không tiết lộ lỗi dự đoán/đáp án.
Ghi phạm vi ngữ cảnh đã cung cấp và mọi can thiệp trong quá trình chạy.

Không giữ thay đổi chỉ vì nhìn hứa hẹn. So sánh cùng input/rubric, ghi tradeoff,
rồi thử đề mới khi phù hợp. Chấm chủ quan và phép đo máy phải tách riêng.

## Review và tích hợp

Mở PR về main theo mẫu. PR cần giải thích vấn đề, thay đổi, bằng chứng, giới
hạn và bước tiếp. Reviewer có thể là model khác; ghi rõ đã xem gì và chưa xem
gì. Đây là quy trình cộng tác, chưa phải branch protection được cấu hình trên
GitHub. Không nói có cổng CI hoặc approval bắt buộc nếu chưa thật sự bật.

Chạy unit tests và validate plan đã đổi theo AGENTS. Khi đổi PPTX, render/xem
file cuối và đối chiếu hash. Chỉ merge kết quả đã kiểm tra, tránh force push.
Không gửi email, mời collaborator hoặc nhắn người khác chỉ vì có handoff này.

## Khi dừng

Commit/push phần có thể xem lại, cập nhật claim và experiment checkpoint. Ghi
`completed`, `paused`, `blocked` hoặc `failed` đúng thực tế, cùng phần chưa xong.
Nếu báo hết quota, dừng lượt, không lặp tool request, không sleep để đợi reset
và không mua hạn mức. Lượt sau đọc remote mới nhất trước khi tiếp tục.
