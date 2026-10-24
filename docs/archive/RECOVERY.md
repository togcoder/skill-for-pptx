# Khôi phục dự án

## Nguồn làm việc chính

https://github.com/togcoder/skill-for-pptx, private. Dùng phiên GitHub được cấp
quyền của bạn để clone. Nếu checkout đã có thay đổi, xem status và bảo toàn chúng
trước khi fetch/rebase. Đọc HANDOFF.md, AGENTS.md, docs/STATUS.md, PR/claim đang
mở và experiment liên quan. Không khởi tạo lại từ QCC cũ hoặc template TODO.

```bash
git clone https://github.com/togcoder/skill-for-pptx.git
cd skill-for-pptx
python3 scripts/check_environment.py
```

Code/results lưu bằng commit/PR vào repo này. Khi dùng API, đọc base SHA mới
nhất, tạo commit có parent đúng và cập nhật ref fast-forward, rồi kiểm tra tree.
Không force-push để giải quyết xung đột. Backend Work không đi kèm repo; xem
ENVIRONMENT.md để chọn phần việc môi trường thực sự hỗ trợ.

## Lịch sử trước GitHub

`archive/pre-github-v0.4.bundle` chứa lịch sử nguyên vẹn đến 19a7c88. Xem
archive/README.md. Main GitHub giữ README khởi tạo của user và nhận snapshot
qua connector; commit cũ không bị tuyên bố là parent của snapshot.

Các file cloud `PPTX_Motion_Lab_Source.bundle` và `PPTX_Motion_Lab_STATUS.md`
trước lúc nhập là đường phục hồi lịch sử. Checkpoint cloud được chuyển thành
con trỏ đến repo sau khi xác minh nhập thành công. Không lấy snapshot cũ ghi
đè một remote mới hơn. Không tiếp tục tạo hai nguồn code độc lập.
