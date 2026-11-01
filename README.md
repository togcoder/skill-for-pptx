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

Phần dưới đây mô tả domain **pptx**.

## Ba đường sản phẩm

### 1. Motion Director cho deck có sẵn

```bash
pip install lxml python-pptx Pillow
python3 scripts/motion_director.py inspect deck.pptx                       # AI đọc deck
python3 scripts/motion_director.py auto deck.pptx -o out.pptx --style cinematic \
        --script script.md --write-notes --preview previews/                # kịch bản → click → chuyển động
python3 scripts/motion_director.py critique out.pptx --md critique.md      # chấm đẹp + kỹ thuật
```

Director giữ nguyên số slide, thứ tự, chữ, bố cục và animation có sẵn. Thứ tự
nguồn kịch bản: kịch bản người dùng > speaker notes > animation có sẵn > tự
suy luận, và thiếu thì tự viết đầy đủ (`motion_script.py draft`).

Chuyển động có 3 lớp:

- **Chính:** hiện dần, build biểu đồ, tụ lại, soi từng phần, đổi chỗ, hành
  trình, zoom.
- **Phụ:** quầng sáng đi theo tiêu điểm, đường ray và token, bút dạ quang, gạch
  chân, chữ trồi lên từ một đường kẻ.
- **Nền:** vòng quỹ đạo quay chậm, Ken Burns, nền trôi.

Skill: [`skills/pptx-motion-director`](skills/pptx-motion-director/SKILL.md),
lệnh `/animate-deck`.

### 2. Morph Studio: Morph giữa slide kiểu chuyên nghiệp

```bash
python3 scripts/morph_studio.py propose out.pptx -o morph.json
python3 scripts/morph_studio.py apply out.pptx morph.json -o final.pptx
```

Công cụ ghép cặp bằng tên `!!` dọc theo cả chuỗi slide và tạo các kiểu Morph:

- tiêu đề trượt;
- vật thể bay vào/ra từ ngoài slide;
- camera zoom vào rồi lùi ra;
- thẻ nở thành panel;
- cuộn ngang.

Danh mục 50 kỹ thuật:
[`pro-techniques.md`](skills/pptx-motion-director/references/pro-techniques.md).

### 3. Slide Forge: dựng deck mới

```bash
python3 scripts/slide_forge.py schema
python3 scripts/slide_forge.py build examples/pptx/forge/coffee_report.json -o deck.pptx   # dựng + chuyển động + QA + critique
```

AI viết một spec ngữ nghĩa với 12 layout, rồi Forge tự lo:

- bố cục và cỡ chữ đo thật;
- theme Office, hoặc theme sinh từ một màu thương hiệu;
- ảnh và icon có giấy phép;
- chuyển động native.

Skill: [`skills/slide-forge`](skills/slide-forge/SKILL.md), lệnh `/forge-deck`.

## Thống nhất cái đẹp và kỹ thuật (T034)

[`knowledge/design_system.json`](knowledge/design_system.json) là nguồn duy
nhất cho các con số "đẹp": thời lượng theo vai trò, easing đã khớp vào
PowerPoint, độ trễ so le, số click mỗi slide, số vật thể chuyển động cùng lúc,
độ tương phản WCAG, thang cỡ chữ và mật độ chữ.

Bộ sinh (engine, writer, Director, components, Forge) **đọc** các con số này.
Bộ kiểm (validator, QA, `design_critic.py`) **chấm** đúng theo chúng. Mỗi phát
hiện ghi rõ luật, giá trị đo, ngưỡng và công cụ sửa.

Căn cứ gồm design token của IBM Carbon và Material 3, WCAG 2.2, nghiên cứu cảm
nhận chuyển động (slow-in/slow-out, so le, giới hạn theo dõi khoảng 4 vật thể),
nguyên lý học đa phương tiện, và các benchmark thẩm mỹ slide mới nhất
(SlidesGen-Bench 2026). Chi tiết ở [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md).

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
/animate-deck deck.pptx      hoặc      /forge-deck spec.json
```

Repo đang private nên trình cài cần quyền truy cập GitHub.

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [AGENTS.md](AGENTS.md) | Quy tắc cho mọi agent |
| [HANDOFF.md](HANDOFF.md) | Bắt đầu nhanh, việc tiếp theo, prompt giao việc |
| [docs/STATUS.md](docs/STATUS.md) | Trạng thái hiện tại, ma trận năng lực × bằng chứng |
| [docs/PRODUCT_TARGET.md](docs/PRODUCT_TARGET.md) | Đích sản phẩm và hợp đồng tự chủ |
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
