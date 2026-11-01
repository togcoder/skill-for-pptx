# Protocol 01: Capability-First Gate

> **Mục tiêu:** Chấm dứt triệt để căn bệnh AI tự viết code Python thô sơ hoặc chắp vá thư viện ngoài
> khi công cụ native trong hệ sinh thái ArtCraft (`D:\artcraft`) đã hỗ trợ sẵn.

---

## 1. Thang Ưu tiên Thực thi 3 Cấp (Execution Escalation Ladder)

Mỗi Specialist Agent khi thực hiện một nhiệm vụ tạo tác (slide, tài liệu, bảng tính, vector, CAD...)
bắt buộc phải tuân thủ nghiêm ngặt thứ tự ưu tiên sau:

```
[Nhiệm vụ Tạo tác]
        │
        ▼
┌────────────────────────────────────────────────────────┐
│ CẤP 1: NATIVE CLI / MCP TOOL CỦA ARTCRAFT (BẮT BUỘC)   │
│ - Tra cứu `lab/registry/artcraft_capabilities.json`        │
│ - Gọi lệnh subcommands hoặc server MCP tương ứng       │
│ - Kiểm tra exit code và dữ liệu phản hồi               │
└───────────────────────┬────────────────────────────────┘
                        │ (Nếu lệnh chưa đáp ứng 100%)
                        ▼
┌────────────────────────────────────────────────────────┐
│ CẤP 2: DECLARATIVE SPEC / NATIVE ENGINE MAPPING        │
│ - Sinh file đặc tả cấu trúc (JSON / DSL chuẩn)         │
│ - Cho engine native của ArtCraft biên dịch & render    │
└───────────────────────┬────────────────────────────────┘
                        │ (Nếu phát hiện tính năng THỰC SỰ THIẾU)
                        ▼
┌────────────────────────────────────────────────────────┐
│ CẤP 3: CUSTOM SCRIPT FALLBACK (BỊ KHÓA MẶC ĐỊNH)       │
│ *Chỉ mở khóa khi xuất trình `CAPABILITY_GAP_PROOF`*    │
│ *Bắt buộc ghi nhận vào `capability_gaps_backlog.md`*   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Thủ tục Mở khóa Cấp 3 (`CAPABILITY_GAP_PROOF`)

Agent **nghiêm cấm** tự ý viết script Python thao tác file trực tiếp (như can thiệp XML hay dùng Pillow/Pptx thô) trừ khi:
1. Đã chạy lệnh đối chiếu với `lab/registry/artcraft_capabilities.json` và chứng minh tính năng đó chưa có trong CLI.
2. Xuất trình khối chứng cứ định dạng:
   ```markdown
   ### CAPABILITY_GAP_PROOF
   - Tool: VectorCraft (vectorcraft-cli.exe)
   - Desired Capability: Lệnh bo góc đa giác tự động với bán kính R
   - CLI Query Result: Lệnh `shape.corner` chưa hỗ trợ tham số `smooth_radius`
   - Temporary Fallback: Script tính toán tọa độ Bézier thủ công
   ```
3. Ghi một dòng mới vào `lab/registry/capability_gaps_backlog.md` để đội ngũ phát triển ArtCraft bổ sung vào bản cập nhật sau.

---

## 3. Tự động hóa Cập nhật Năng lực

Đầu mỗi phiên làm việc hoặc khi có nghi ngờ binary trong `D:\artcraft` được cập nhật, Agent phải chạy:
```bash
python scripts/sync_artcraft_capabilities.py
```
Để đồng bộ hóa lại toàn bộ danh mục lệnh mới nhất, tránh tình trạng "công cụ đã có tính năng mới từ hôm qua nhưng Agent vẫn hì hục code bù bằng tay".
