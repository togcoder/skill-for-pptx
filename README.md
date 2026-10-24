# PPTX Motion Lab

Nghiên cứu xây dựng **AI Motion Director cho PowerPoint**: nhận một deck (hoặc
một spec) cùng mục tiêu chung, rồi tự viết kịch bản, chia nhịp click và tạo
chuyển động native, chỉnh sửa được, đẹp và đúng kỹ thuật.

- Model mới bắt đầu tại **[HANDOFF.md](HANDOFF.md)**. Trạng thái hiện tại ở
  [docs/STATUS.md](docs/STATUS.md).
- Đầu nghiên cứu mới nhất nằm trên nhánh `claude/blissful-pasteur-gmll59`
  (T034). `main` đang chậm hơn: mới dừng ở T023.

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
python3 scripts/slide_forge.py build examples/forge/coffee_report.json -o deck.pptx   # dựng + chuyển động + QA + critique
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
