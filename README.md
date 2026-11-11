# Design Research Lab (khởi đầu từ PPTX Motion Lab)

Lab nghiên cứu thiết kế **đa lĩnh vực (Cross-Domain Agentic AI Lab)**: nhiều agent và nhiều model cùng
nghiên cứu, phản biện và xâu chuỗi kết quả, để AI tạo ra các sản phẩm thiết kế vừa đẹp vừa chuẩn xác
kỹ thuật, đáp ứng đúng ý người dùng ngay từ lượt đầu.

### Triết lý Cốt lõi của Hệ thống Kỹ năng Agentic AI:
1. **Không tạo tài nguyên đơn lẻ:** Kỹ năng không bị giới hạn trong việc sinh ra một file rời rạc, mà xâu chuỗi đa tài nguyên (ảnh, video, âm thanh, bảng tính, đồ thị, vector, slide, tài liệu) thành sản phẩm hoàn chỉnh theo nhu cầu đa dạng.
2. **Nâng trải nghiệm người dùng lên mức cao nhất (First-Pass Excellence):** Thấu hiểu sâu sắc tâm lý người dùng, bối cảnh thưởng thức và đối tượng khán giả để tạo ra sản phẩm đúng ý ngay từ lượt đầu, triệt tiêu việc phải làm đi làm lại nhiều lần.
3. **Đường ống Tiền xử lý Chuyên sâu (Pre-process Before Embedding):**
   - **Ảnh:** Dùng công cụ chỉnh ảnh (Pillow, PhotoCraft) để cắt cúp, tách nền kênh Alpha, cân màu đồng bộ với tone slide/tài liệu trước khi chèn.
   - **Âm thanh:** Khử ồn, chuẩn hóa âm lượng chuẩn phát sóng (EBU R128 -14 LUFS), tự động auto-ducking nhạc nền trước khi ghép vào video (FilmCraft) hay hiệu ứng chuyển cảnh.
   - **Dữ liệu & Đồ thị:** Xử lý và kiểm toán công thức bảng tính (SheetCraft), tạo biểu đồ chuẩn Tufte trước khi nhúng vào slide báo cáo hoặc tài liệu Word.
4. **Toàn quyền Thực thi Cục bộ & Tự do Tài nguyên:** Agent hoạt động cục bộ có toàn quyền tải font chữ, file mẫu, mô hình và cài đặt mọi thư viện code cần thiết; mọi tệp tạm thời phải lưu gọn trong `workspace/` và được dọn dẹp sạch sẽ sau khi hoàn tất.

| Domain | Ứng dụng | Thẻ |
|---|---|---|
| pptx | PowerPoint (domain trưởng thành nhất) | [domains/pptx](domains/pptx/DOMAIN.md) |
| docx | Word | [domains/docx](domains/docx/DOMAIN.md) |
| xlsx | Excel | [domains/xlsx](domains/xlsx/DOMAIN.md) |
| svg | Vector, in ấn | [domains/svg](domains/svg/DOMAIN.md) |
| cross | Điều phối giữa các ứng dụng | [domains/cross](domains/cross/DOMAIN.md) |

- Bắt đầu tại **[HANDOFF.md](HANDOFF.md)**.
- Cách agent làm việc: [lab/PROTOCOL.md](lab/PROTOCOL.md).
- Các chuẩn nghiên cứu, phản biện, gộp dữ liệu và nơi đặt file:
  [lab/standards/](lab/standards/).
- Không file đầu ra nào được nằm ở thư mục gốc: kết quả của mỗi task vào
  `experiments/<ID>-…/artifacts/`, file nháp vào `workspace/`.

## PowerPoint: dùng skill nào

**Một skill duy nhất: [`skills/pptx/SKILL.md`](skills/pptx/SKILL.md).** Model nhỏ đọc
[`skills/pptx/CARD.md`](skills/pptx/CARD.md) (một trang) trước. Skill là lời hướng dẫn; đồ nghề đi kèm là
`scripts/pptx_tools.py` (`glance`, `shell`, `fit`, `arrange`, `compare`, `seen`, `watch`, `check`…).

Việc skill làm tốt nhất hiện nay: **đưa một bộ slide có sẵn vào theme** và dựng lại bố cục từng slide, kiểm
bằng ảnh (mục 13, 14 của skill). Các skill PPTX cũ (Motion Director, Morph Studio, Slide Forge, Deck
Director) đã gỡ khỏi repo ngày 2026-11-12; mã của chúng vẫn nằm trong `scripts/` làm đồ nghề
và lịch sử còn trong git.

Số "đẹp" (thời lượng, tương phản, thang chữ) nằm ở
[`knowledge/design_system.json`](knowledge/design_system.json), chi tiết ở
[docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md).

## Mức bằng chứng

Mọi tuyên bố đều ghi rõ đạt bậc nào theo
[docs/VERIFICATION.md](docs/VERIFICATION.md): cấu trúc → mô phỏng → LibreOffice
→ PowerPoint đọc → PowerPoint render (CreateVideo) → trình chiếu tương tác.

Một phần hệ thống đã được PowerPoint 16.0 đọc và render. **Chưa có deck nào được
trình chiếu tương tác bằng click trong PowerPoint.** Ảnh GIF và storyboard là mô
phỏng.

## Cài như plugin Claude Code

```text
/plugin marketplace add togcoder/skill-for-pptx
/plugin install pptx-motion@togcoder-pptx
```

Repo đang private nên trình cài cần quyền truy cập GitHub.

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [AGENTS.md](AGENTS.md) | Quy tắc cho mọi agent |
| [HANDOFF.md](HANDOFF.md) | Bắt đầu nhanh, việc tiếp theo, prompt giao việc |
| [domains/pptx/DOMAIN.md](domains/pptx/DOMAIN.md) | Trạng thái hiện tại của domain PowerPoint |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Sơ đồ module và luồng dữ liệu |
| [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md) | Hệ thiết kế: token, luật, bằng chứng, critic |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | Thang bằng chứng và quy trình kiểm chứng native |
| [docs/CLICK_BEAT_CHOREOGRAPHY.md](docs/CLICK_BEAT_CHOREOGRAPHY.md), [docs/MOTION_PACKING.md](docs/MOTION_PACKING.md) | Chính sách nhịp click và đóng gói chuyển động |
| [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md) | Phần nào chạy ở đâu |
| [docs/COLLABORATION.md](docs/COLLABORATION.md), [research/tasks/INDEX.md](research/tasks/INDEX.md) | Cộng tác, sổ đăng ký mã task |
| [docs/SOURCES.md](docs/SOURCES.md), [knowledge/README.md](knowledge/README.md) | Nguồn và dữ liệu tri thức |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Nhật ký nghiên cứu theo task |
| [docs/archive/](docs/archive/) | Tài liệu đã thay thế, giữ để tái lập |

Các thí nghiệm cũ (E001–T018, đường dựng ChatGPT Work, writer patch v0.2–v0.5)
được đóng băng để tái lập; xem [docs/CHANGELOG.md](docs/CHANGELOG.md). Demo dùng
dữ liệu tổng hợp. Tài sản tham khảo bên ngoài chỉ giữ cục bộ. Repo riêng tư,
chưa chọn giấy phép phát hành.
