# Môi trường và khả năng tái lập

Chạy `python3 scripts/check_environment.py` từ project root. Helper chỉ kiểm
tra khả năng hiện diện; không cài dependency và không xác nhận playback.

| Phần việc | Yêu cầu |
|---|---|
| Validate plan, chẩn đoán nhãn | Python 3, thư viện chuẩn |
| Unit tests, chèn Morph, kiểm tra package | Python + lxml |
| Dựng/render hiện tại | ChatGPT Work primary runtime, artifact-tool và Presentations host helpers |
| Playback/editing thực | PowerPoint có bản quyền và môi trường desktop được phép thao tác |

Môi trường đã thử: Python 3.12.14, lxml 6.1.1, Node 24.19.0, artifact-tool 2.8.77,
runtime bundle 26.927.11222. Đó là ghi nhận thử nghiệm, không phải cam kết mọi
phiên bản khác đều tương thích. Repo không đóng gói artifact-tool, font hay
host skill. Không tự thay backend và gọi kết quả tương đương khi chưa đo.

Nếu chỉ cần kiểm tra cấu trúc ở một checkout riêng ngoài Work:

```bash
python3 -m venv .venv
# Kích hoạt venv theo hệ điều hành, rồi cài dependency trong môi trường riêng:
python -m pip install lxml==6.1.1
python -m unittest discover -s tests -v
```

Không cài lại dependency vào runtime Work do host quản lý. Khi dùng Work,
`scripts/run_experiment.sh` lấy Node/Python/node_modules từ
`CODEX_PRIMARY_RUNTIME_NODE`, `CODEX_PRIMARY_RUNTIME_PYTHON`,
`CODEX_PRIMARY_RUNTIME_NODE_MODULES`, `CODEX_PRIMARY_RUNTIME_ROOT`.
Đọc Presentations của host để chạy marker, finalizer, render và kiểm tra mắt.

Với PowerPoint, bắt đầu bằng một PPTX đã có trong `output/` để tránh thay đổi
đầu vào trong khi đo. Ghi font thực tế và mọi lần thay thế. PNG tĩnh không cho
biết chuyển tiếp chạy đúng. Theo `docs/POWERPOINT_QA.md`.
