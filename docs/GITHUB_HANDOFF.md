# Nhập dự án vào GitHub

Đích đã xác minh ngày 04/10/2026: https://github.com/togcoder/skill-for-pptx.
Repo private, thuộc togcoder, connector báo quyền push/admin. Người dùng tự tạo
repo và yêu cầu đẩy toàn bộ dự án cùng handoff cho các model nghiên cứu chung.

Trước khi nhập, main chỉ chứa README `# skill-for-pptx`, tại commit
`98438336925574e58068769a20277ac7e06eb3c1`. Commit khởi tạo này được giữ làm
parent của lần nhập; không force-push hoặc dùng repo không liên quan.

Git CLI trong phiên hiện tại không có xác thực GitHub. Vì vậy dữ liệu được nhập
qua GitHub connector thành snapshot của toàn bộ tracked files, kèm
`archive/pre-github-v0.4.bundle` giữ nguyên lịch sử local đến `19a7c88`.
Không tuyên bố các commit local cũ là ancestor trực tiếp của main GitHub.
Đọc archive/README.md để kiểm tra hash và mở lịch sử cũ.

Bộ bàn giao:
- HANDOFF.md, docs/COLLABORATION.md và AGENTS.md.
- docs/ENVIRONMENT.md, scripts/check_environment.py.
- Bốn task nghiên cứu và quy trình claim theo nhánh/draft PR.
- Mẫu báo cáo và PR, nguồn skill, builder, tests, frozen baselines, PPTX và ảnh.

Không đóng gói dependency của host, font, credential hoặc video tham khảo bên
ngoài. Không cài personal skill hay phát hành public release trong lần nhập.
Repo private không tự cấp quyền cho model khác: chúng cần kết nối GitHub được
chủ tài khoản cấp quyền. GitHub là nguồn làm việc chính cho các lần tiếp tục.
