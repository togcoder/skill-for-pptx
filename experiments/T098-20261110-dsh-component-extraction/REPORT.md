# T098 [pptx] Tách thành phần dùng lại từ một bộ deck đã có

Agent: dsh (DeepSeek, DSH) · Ngày: 2026-11-10 · Nhánh `work/T098-dsh-component-extraction` (xếp trên
`work/T097-claude-rebuild-pipeline`).

## Câu hỏi

Chủ dự án trong dự án QCC: *"tôi đã muốn ai tách các thành phần có trong slide ra để làm tư liệu các AI khác có
thể tận dụng… biểu đồ xương cá có thể tách khỏi nền mà sao nó lại không tách, không biết cách tách group?"* Cần
trả lời vì sao bước bóc tách trước đây không lấy được xương cá, và bổ sung năng lực đó vào repo skill.

## Vì sao xương cá chưa được tách

- `extract` (T097) chỉ lấy **ảnh/video gốc + manifest**. Xương cá trong bộ gốc không phải một ảnh, cũng không
  phải một group: slide 29 của `QCC - SHARP Team Ver3-4.pptx` có **40 hình cấp cao**, gồm 37 hình vẽ xương cá
  (lines, text, rounded rects), **một ảnh nền full-slide** `Picture 85`, tiêu đề `TextBox 17`, và thanh bước
  `Group 60`. `extract` chỉ xuất `Picture 85` (media) — xương cá không đi theo.
- `cutout` chỉ nhận **một ảnh** có nền đơn giản; nó không chọn được 37 hình rời, không bỏ được ảnh nền, và
  `cutout` với nền ảnh phức tạp bị chính guide 10 từ chối.
- `ungroup` chưa có trong đồ nghề. Nhóm (group) có tâm lý "mở ra là xong", nhưng toạ độ con nằm trong
  `chOff/chExt` và phải map qua scale/rotation/flip; làm sai thì xương cá vỡ hoặc dồn về góc.
- Vì vậy Ver5 **vẽ lại** xương cá trong 3 slide mẫu thay vì tách từ bản gốc. Bản thân bước "bóc tách" của pipeline
  chỉ dừng ở media + manifest, nên câu trả lời cho chủ dự án là: **chưa tách thành phần; và trước T098 không có
  công cụ để tách**.

## Đã thêm vào repo (D011: chỉ làm việc lời không làm được)

### Đồ nghề — `scripts/pptx_tools.py` (+ các test)

| Lệnh | Việc |
|---|---|
| `components DECK [--slide N]` | kiểm kê thành phần tách được trên slide: group (kèm số con), bảng, chart (báo dùng `rechart`), ảnh nền (cờ `covers the slide`), chrome (`!!`, Logo, Title, Footer, Page number); in cả gợi ý lệnh |
| `ungroup DECK SLIDE [--name ...] [--all-groups] [--force] -o OUT` | làm phẳng group thành shape cấp cao, **map đúng toạ độ con** qua scale/rotation/flip; giữ z-order; từ chối group có animation (timing trỏ vào id group) trừ `--force`; từ chối trường hợp không biểu diễn được (mirror+rotation, rotation+scale không đều) và chỉ rõ cách xử lý |
| `component DECK SLIDE [--name ...] [--exclude ...] [--exclude-chrome] [--freeze] [--ungroup] [--margin px] [--png PNG] [--manifest FILE] -o OUT.pptx` | tách thành **file một slide**: chọn hình theo tên, tự bỏ ảnh nền sát mép, cắt khung + lề, nền trong suốt, chép ảnh kèm crop và sửa relationship id; `--freeze` đổi theme colour/font thành giá trị thật để dán sang bộ khác vẫn giữ màu; ghi manifest JSON; `--png` xuất ảnh xem trước đúng tỉ lệ (không bóp thành 16:9) |
| `place COMPONENT DECK --slide N [--at X,Y] -o OUT` | dán thành phần trở lại một slide: chữ vẫn sửa, ảnh giữ crop, cấp lại shape id trùng |

Phần khó phải làm bằng code: XML group chỉ đọc được qua `chOff/chExt`, relationship id của ảnh nằm ở part
quan hệ; không có lệnh thì người dùng phải mở PowerPoint ungroup tay từng nhóm và tự sửa lỗi.

### Guide — `skills/pptx/guides/12-tach-thanh-phan.md`

Quy trình 4 bước (kiểm kê → tách → dùng lại → kiểm), bảng "nhóm / nhiều hình rời / một ảnh" với 3 cách tách,
luật giữ nguyên hiệu ứng kể cơ chế, cách đặt viên thành phần (`assets/components/`, manifest, giấy phép), và
danh sách giới hạn. Đã nối từ `SKILL.md`, `guides/9`, `guides/10` (chỗ "ảnh có nền dính liền") và `guides/11`
(chỗ dựng lại bộ).

## Bằng chứng trên bộ QCC thật (để ngoài repo, không commit deck 240 MB)

| Việc | Kết quả | Bậc |
|---|---|---|
| `components` slide 29, Ver3-4 | 40 hình: 1 ảnh nền `Picture 85`, tiêu đề `TextBox 17`, thanh bước `Group 60`, 37 hình xương cá | 1 |
| `component … --exclude Picture 85 --exclude TextBox 17 --exclude Group 60 --freeze` | **37 hình** → `assets/components/fishbone_ver34.pptx`, 16,09 × 9,03 in, PNG preview đúng tỉ lệ, manifest JSON | 1 |
| `component … --exclude-chrome` trên Ver5 slide 2 | **64 hình** xương cá → `fishbone_ver5.pptx`, 15,54 × 9,19 in; thanh bước cùng slide → `stepbar_ver5.pptx`, 10 hình, 9,16 × 1,0 in | 1 |
| `place fishbone_ver34` lên một slide tối của bộ khác | 37 hình, chữ trắng hiện đúng, chữ vẫn sửa được, ảnh giữ crop; PowerPoint mở/export được | 4 |
| PowerPoint 16.0 mở các file component và file `place` | mở được; `look` xuất ảnh thật | 4 |
| `unittest discover -s tests` | 609 test, 1 fail do layout đang chờ REPORT này; riêng `tests/test_components.py` **9/9 pass** | 1 |
| Chủ dự án dùng lại component trong bộ mới | chưa | 6 |

## Giới hạn

- Không mang animation. Group có timing: `ungroup` từ chối; tách cả group làm component, hoặc copy cả slide.
- Chart/SmartArt/video/audio: từ chối rõ ràng (chart dùng `rechart`; SmartArt/video copy slide).
- `place` không thu phóng: text giữ cỡ gốc; muốn cỡ khác thì thiết kế viên ở cỡ đúng hoặc dùng `scale` sau.
- `--freeze` biến theme colour/font thành giá trị thật, nên viên không theo theme bộ nhận; không freeze thì
  ngược lại. Guide ghi rõ hai lựa chọn.
- Tự nhận diện ảnh nền chỉ khi ảnh nằm sát mép; nền đặt lệch (như `Picture 85` ở y=92) phải `--exclude`.
- Preview PNG cần PowerPoint trên máy; không có thì vẫn có file `.pptx`.
- Đây là công cụ tách **thành phần tĩnh**; animation "kể cơ chế" vẫn phải giữ nguyên slide (guide 10).

## Chưa làm / câu hỏi cho trưởng nhóm

- T096/T097 đã merge vào `main` (PR #77/#78, 2026-11-10); nhánh này đã merge `main` mới nhất. PR T098 giờ chỉ
  còn phần của T098. `HANDOFF.md` do trưởng nhóm viết được lấy từ `main` (D006).
- Có nên thêm lệnh này vào pipeline dựng lại (mục 11) như một bước bắt buộc "tách thành phần trước khi vẽ lại"
  không? Đề xuất: chỉ bắt buộc khi bản gốc có khung sơ đồ/thanh bước; nếu không có thì bỏ qua.
- Có nên đưa `assets/components/` vào chuẩn thư mục dùng chung của domain (như `assets/` trong QCC) và yêu cầu
  mọi viên phải có manifest? Đề xuất: có, kèm giấy phép/nguồn.
- Cần review chéo bởi model khác họ (D008) cho 4 lệnh mới + guide 12.

## Tệp

- `scripts/pptx_tools.py` (4 lệnh mới), `tests/test_components.py` (9 test), `skills/pptx/guides/12-tach-thanh-phan.md`,
  cập nhật `SKILL.md`, `guides/9`, `guides/10`, `guides/11`.
- Bằng chứng ngoài repo: `C:\Users\COMPUTER\Desktop\QCC - SHARP Team\assets\components\` (fishbone_ver34,
  fishbone_ver5, stepbar_ver5 + manifest + preview) và `_scratch/components/placed_fishbone_dark.pptx`.
