# T090 [pptx] Model khác họ dùng `skills/pptx`: bộ Triết học chương 1, 7 slide

- **Agent / model:** DSH (DeepSeek V4.1 Flash) trên DeepSeek Harness, phiên desktop trên máy chủ
  dự án.
- **Ngày:** 2026-11-08. **Base:** `origin/main` @ `09296c4` + merge
  `origin/work/T087-claude-pptx-guidance-skill` @ `52cfba6` (PR #69 đang mở).
- **Yêu cầu của chủ dự án (phiên này):** *"hãy xem bạn có thể làm được gì cho dự án thì làm đi,
  tôi cũng muốn thử xem với dsh trí tuệ của bạn được đến đâu."*
- **Đề bài đã chọn:** T090 — một model khác họ dựng deck bằng `skills/pptx/` + `pptx_tools.py`.
  Đây cũng là bằng chứng còn thiếu cho nghiệm thu T087 (*"đưa skill cho một model khác họ với
  người viết (ví dụ DeepSeek). Model đó dựng lại bộ Triết học chương 1"*).
- **Trạng thái:** bản dựng xong, có bằng chứng PowerPoint; **chờ chủ dự án mở file và chấm**
  (nghiệm thu T090) và chờ review khác họ trước khi merge.

## Bàn giao (theo mục "Bàn giao" của skill)

1. **File:** `experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx`
   (7 slide, có chuyển động). Bản tĩnh để soạn lại: `…/artifacts/T090-triet-hoc-ch1.static.pptx`.
2. **Ba chỗ đáng xem khi lật:**
   - **Slide 2 → 3:** bấm sang slide 3. Hai câu tục ngữ tự thu nhỏ và xếp vào hai cột
     **DUY VẬT / DUY TÂM** (Morph 1,4 giây) — niềm tin của người nghe biến thành hai lập trường.
   - **Slide 3:** bấm lần một, hai nhãn hiện cùng lúc; bấm lần hai, gạch vàng dưới phía được chọn
     và câu kết luận hiện ra. Câu hỏi nền của chương nằm trong một slide.
   - **Slide 6:** trục và ba năm đã có sẵn; bấm ba lần, chân dung và việc làm hiện theo chiều thời
     gian — ảnh ra mắt đúng lúc người đó hành động, không phải ảnh trang trí cuối deck.
3. **Còn chưa làm được:**
   - chưa có điểm của chủ dự án (đó là nghiệm thu);
   - nội dung cần một người dạy môn này soát lại (đây là bản kể lại để giảng, không chép giáo
     trình);
   - bản 7 slide bỏ phần "điều kiện ra đời" (ba dòng chảy kinh tế – lý luận – khoa học) và lời
     dẫn định nghĩa "triết học là gì" của kịch bản gốc, vì T090 giới hạn 5–7 slide;
   - vài cảnh báo của critic còn lại, ghi ở mục 5.

## Frame

**Câu hỏi.** Một model **khác họ** với người viết skill (DeepSeek, không phải Claude) chỉ đọc
`skills/pptx/` và dùng đồ nghề nhỏ của nó có dựng được một bộ slide dùng được không?

**Giả thuyết.** Lời chỉ dẫn + mẫu đã duyệt đủ để một model khác họ ra deck 5–7 slide nhất quán,
đúng nhịp, có 1 Morph mang nghĩa và không có lỗi thị giác người thấy ngay.

**Điều kiện bác bỏ** (đã tự thử):
- (a) deck sai nội dung giáo trình, tràn chữ, chữ quá nhỏ, thẻ rỗng;
- (b) chuyển động vô nghĩa, Morph hỏng hoặc không chạy trong PowerPoint;
- (c) file không mở được trong PowerPoint;
- (d) phải viết script dựng riêng ngoài "đường hẹp" mới ra kết quả;
- (e) chính lời chỉ dẫn mâu thuẫn nhau tới mức model không quyết được.

**Lens của domain.** PPTX native: hình của python-pptx, timing qua `pptx_animator`, Morph
`p159`/`p14`; bằng chứng đọc/ghi bằng PowerPoint 16 COM; vẽ bằng hình gốc, chữ gốc, không ảnh
chụp slide.

**Chuyển giao từ trục khác:** nội dung lấy từ **kịch bản** (trục script, T078) rồi mới dựng
deck — đúng D003/D004, và đây là phép thử chuyển giao "script → deck" trong cùng domain.

## Frozen input

- **Base:** `09296c4` (main) + `52cfba6` (T087, PR #69). Nhánh `work/T090-dsh-skill-triet-hoc`,
  worktree `workspace/T090`.
- **Nội dung:** bản rút từ `experiments/T078-20261104-claude-script-track/gold-script-triet-hoc-ch1.md`
  (13 cảnh → 7 scene, `inputs/script.md`). Không có số liệu tự nghĩ ra; không chép nguyên văn giáo
  trình.
- **Ảnh:** chân dung cắt tròn tông đỏ có sẵn từ T066 — Wikimedia Commons, public domain
  (`experiments/T066-…/inputs/SOURCES.md`). Không tải thêm ảnh.
- **Môi trường:** Windows, PowerPoint **16.0 build 17932** (COM), Python 3.13.5 (Anaconda),
  python-pptx 1.0.2, lxml, Pillow 13.0.0, pywin32, ffmpeg 8.1.1.
- **Không truy cập được:** chủ dự án chưa đưa nội dung mới 5–7 slide có số liệu thật (T090 giả
  định có); chưa có người soát nội dung; chưa có bản PowerPoint thứ hai; chưa có rung 6 (người
  ngồi xem thật).

## Method

```powershell
# 1. kịch bản là bản chữ trước, có claim mỗi cảnh; tự kiểm tra
python scripts/motion_script.py check experiments/T090-20261108-dsh-skill-triet-hoc/inputs/script.md
#    -> PASS: 7 scenes, spine 20 words (1 cảnh báo: động từ cảnh bìa không thuộc bảng 15)

# 2. dựng bản tĩnh bằng python-pptx, đặt tên mọi vật thể
python experiments/T090-20261108-dsh-skill-triet-hoc/inputs/build_deck.py

# 3. ghi lần bấm và Morph theo tên vật thể (không đụng tay vào XML)
python scripts/pptx_tools.py motion `
  experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.static.pptx `
  experiments/T090-20261108-dsh-skill-triet-hoc/inputs/plan.json `
  -o experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx

# 4. tự kiểm tra: mở ra xem + audit + critic + cấu trúc
python scripts/morph_studio.py audit experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx
python scripts/pptx_tools.py look experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx -o <dir>
python scripts/design_critic.py experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx
python experiments/T090-20261108-dsh-skill-triet-hoc/inputs/verify_t0.py `
  experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx `
  experiments/T090-20261108-dsh-skill-triet-hoc/inputs/plan.json `
  -o experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/t0_check.json

# 5. PowerPoint trả lời: mở file, đọc transition, và render bằng CreateVideo
python experiments/T090-20261108-dsh-skill-triet-hoc/inputs/verify_native.py `
  experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx `
  -o experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/native_probe.json
python scripts/slide_forge.py render `
  experiments/T090-20261108-dsh-skill-triet-hoc/artifacts/T090-triet-hoc-ch1.pptx -d workspace/scratch-t090-render-v2 --seconds 4
```

## Evidence

| Bằng chứng | Đo | Rung |
|---|---|---|
| File mở được bằng PowerPoint thật | COM mở read-only, đọc đủ 7 slide; PowerPoint 16.0 build 17932 | **4** |
| Morph được PowerPoint hiểu là Morph | `SlideShowTransition.EntryEffect = 3954`, `Duration = 1,4 s` ở slide 3; fade `3849` ở slide 2/4/5/6/7; slide 1 không transition (`native_probe.json`) | **4** |
| Morph chạy thật trên khung hình | CreateVideo 720p; 6 khung 8,9–10,0 s: nền kem tan sang đỏ sẫm, hai câu tục ngữ thu nhỏ và trượt vào hai cột (`preview/morph-slide-3.jpg`) | **5** |
| Nhịp bấm khớp kế hoạch | 9 cụm bấm: slide 2=1, 3=2, 4=1, 5=1, 6=3, 7=1; tổng **28 hiệu ứng vào**; COM đếm 0/1/6/4/1/15/1 hiệu ứng theo slide | **4** |
| Slide mở ra đọc được (t=0) | mỗi slide nội dung có tiêu đề (riêng slide câu trích: câu trích) + 14–46 từ hiện sẵn; bìa **0 lần bấm** (`t0_check.json`, `ok: true`) | **1** |
| Danh tính Morph | `!!cau1`, `!!cau2` có ở cả slide 2 và 3; không có ở dạng entrance ở đích; audit **0 lỗi**, 3 cảnh báo `MORPH-UNNAMED-PAIR` (xem mục 5) | **1** |
| Thang chữ | 6 cỡ dùng lại: 14 / 18 / 24 / 32 / 44 / 64 pt; critic không còn `TYP-SIZES` | **1–2** |
| Critic (không phải thước chất lượng, D001) | design 4,98 · motion 5,00 · rhythm 4,50 · coherence 4,33 · narrative 4,45 · overall 4,65; 182 phép kiểm, 7 cảnh báo còn lại (`artifacts/critic.json`) | **1–2** |
| Nội dung | rút từ kịch bản gốc T078 + bộ Triết học T066; không có số liệu bịa; cần người dạy soát trước khi dùng thật | **0** |

**Hash:** deck `f007118b` (1.362.170 B), bản tĩnh `2cd1d9d2` (1.358.145 B), `native_sequence.json`
`1044fbb4`, `native_probe.json` `6102cbbc`, `critic.json` `382a0e8b`, `morph_audit.json`
`292754a1`, `t0_check.json` `80f95013`; preview `sheet.jpg` `f04a6ec2`, `morph-slide-3.jpg`
`eaa44dd7`.

**Ảnh chụp cuối bộ:** `preview/sheet.jpg` (7 slide, ảnh do PowerPoint xuất).

## 5. Kết quả âm tính và giới hạn

1. **Số vòng xem–sửa là 5, không phải 3 như guide 8 ghi.** Ba vòng đầu là sửa thị giác (mũi tên
   dày, chữ tràn, cột lệch). Vòng 4 là lỗi **t=0** của slide 6 (trục trống) chỉ lộ ra khi lập kế
   hoạch chuyển động; vòng 5 là lỗi Morph nhìn thấy trên khung hình (dưới đây). Đây là điểm lời
   chỉ dẫn chưa dặn: *xem t=0 trước khi ghi chuyển động*, nên tôi ghi thành đề nghị ở mục 6.
2. **Morph làm nhoè chữ khi hai slide ngắt dòng khác nhau.** Ban đầu câu tục ngữ thứ hai ở slide
   2 là một dòng, ở slide 3 là hai dòng; khung CreateVideo cho thấy chữ bị "bóng ma" chồng lên
   nhau giữa Morph. Sửa bằng cách **ngắt dòng y hệt ở cả hai slide**; khung sau khi sửa sạch
   (`preview/morph-slide-3.jpg`). Đây là một luật mới nên thêm vào guide 7 (mục 6).
3. **Morph audit còn 3 cảnh báo `MORPH-UNNAMED-PAIR`** cho `Eyebrow`, `Tieu de`, `Ket luan`: ba
   vật này cùng loại, cùng vị trí ở hai slide nên PowerPoint có thể ghép theo hình học và chuyển
   mờ khi Morph. Guide 3 lại bắt tiêu đề nằm cùng một chỗ trên mọi slide, nên cảnh báo này gần
   như không tránh được. Tôi giữ nguyên (khung hình cho thấy tiêu đề cũ mờ dần, tiêu đề mới hiện
   lên — chấp nhận được), và đề nghị sửa guide 7 thay vì đổi bố cục.
4. **Cảnh báo critic còn lại** (`artifacts/critic.json`):
   - `DEN-WORDS` slide 3 (57 từ) và slide 5 (64 từ): hai slide dạng bảng đối chiếu, không phải
     đoạn văn; ngưỡng 45 từ là ngưỡng cho slide kể chuyện. Không cắt thêm vì sẽ mất nội dung.
   - `NAR-LIFECYCLE` slide 3 và 6: `pptx_tools motion` chỉ ghi **entrance** (fade/rise/wipe/zoom),
     không có dim/exit; deck dựng đúng "đường hẹp" nên không thể qua cổng này. Đề nghị ở mục 6.
   - `DUA-BREAK`, `MOT-VOCAB`: nhịp và từ vựng chuyển động của một deck 7 slide, entrance-only.
5. **Chuyển động chỉ có entrance + 1 Morph.** Không có dim, không có motion path, không có
   Ken Burns (guide 6 nói phải gọi `motion_director` nếu muốn). Cái "gu" nằm ở việc chọn động từ,
   nhóm lần bấm và chỗ Morph — không nằm ở số hiệu ứng.
6. **Chưa có rung 6.** Chủ dự án chưa mở file; đây đúng là việc còn lại của T090. Cũng chưa có
   bản so sánh A/B mù (T071 chưa xong), nên báo cáo này **không** nói deck "tốt hơn" T066 hay
   Forge.
7. **Cỡ chữ 18 pt là sàn nội dung.** Trên slide 5, dòng nguồn gốc để 18 pt cho cân với bộ phận
   24 pt; nếu chiếu phòng lớn có thể phải bỏ bớt chữ thay vì tăng cỡ (guide 4).
8. **Nội dung bản ngắn bỏ hai phần** ("điều kiện ra đời", định nghĩa "triết học là gì") so với
   kịch bản gốc; nếu chủ dự án muốn đủ chương thì cần 9–10 slide, vượt giới hạn T090.
9. **Điều kiện bắt đầu của T090 chưa thỏa.** Đề bài ghi "sau khi chủ dự án duyệt demo T087".
   Trong phiên này chủ dự án yêu cầu agent tự làm, nên tôi dùng yêu cầu đó làm cửa vào và dựng
   deck để chủ dự án chấm một lần cho cả hai việc (duyệt demo + chấm T090). Nếu chủ dự án thấy
   demo T087 chưa đạt, phần chấm này không thay thế được phản hồi về skill.

## 6. Chỗ lời chỉ dẫn còn hỏng (để trưởng nhóm sửa `skills/pptx/`, không phải sửa code)

1. **Guide 5/7 thiếu luật "ngắt dòng giống nhau cho chữ mang Morph".** Đã đo được hậu quả thật
   (mục 5.2). Thêm một câu vào guide 7, ngay sau luật 6 ("chữ dài trong thẻ dễ méo khi Morph").
2. **Guide 8 dặn tối đa 3 vòng, nhưng không dặn thứ tự:** (a) soi t=0, (b) mở bản tĩnh, (c) mới
   ghi chuyển động, (d) xem khung Morph. Tôi đã phải thêm vòng vì làm sai thứ tự.
3. **Guide 7 mục "Kiểm tra" nên nói rõ `UNNAMED-PAIR` với tiêu đề là bình thường.** Nếu không,
   model sẽ cố "sửa" bằng cách đổi bố cục tiêu đề, trái guide 3.
4. **Guide 4 cho phép "số hoặc câu nổi bật 72–120 pt",** nhưng luật 3–6 cỡ chữ và `TYP-SIZES`
   của critic lại đếm cả dấu ngoặc kép trang trí. Tôi phải hạ dấu “ từ 120 pt xuống 64 pt để qua
   cổng. Nên ghi: đồ trang trí bằng chữ phải dùng đúng một cỡ trong thang.
5. **Guide 9 không nhắc speaker notes.** Critic có luật `NAR-ALIGN` đòi notes đúng mẫu
   `[T=0]` + `[CLICK n]` khớp số lần bấm. Model không biết thì mất điểm narrative vô ích. Chỉ
   cần một dòng mẫu trong guide 9.
6. **`pptx_tools motion` chỉ có entrance, nhưng critic `NAR-LIFECYCLE` đòi dim/exit** cho slide
   nhiều lần bấm. Hai bên mâu thuẫn: hoặc thêm `dim`/`exit` vào đồ nghề, hoặc critic miễn trừ deck
   entrance-only.
7. **Không có công cụ xem t=0.** `look` xuất slide **đã hiện đủ mọi thứ**; model phải tự trừ các
   vật trong kế hoạch bấm để đoán t=0 (T087 đã ghi giới hạn này). Một `look --state t0` (ẩn các
   vật có entrance) sẽ bắt được lỗi slide mở ra trống — đúng lỗi tôi gặp ở slide 6.
8. **`DEN-WORDS` 45 từ/slide không hợp với slide bảng đối chiếu** (slide 5: 64 từ). Nên có ngoại
   lệ cho slide dạng bảng/bản đồ, hoặc đếm theo "từ đang đọc" thay vì toàn slide.

## 7. Thay đổi trong repo

- **Chỉ thêm một thư mục thí nghiệm:** `experiments/T090-20261108-dsh-skill-triet-hoc/`
  (`inputs/` script + build + plan + hai script kiểm; `artifacts/` hai deck + 4 JSON bằng chứng;
  `preview/` ảnh ghép + dải khung Morph). Không sửa product path, không thêm script trong
  `scripts/`, không sửa `lab/capabilities.json`.
- INDEX: hàng T090 chuyển `claimed → review requested`. CHANGELOG: một mục T090. Domain card:
  một dòng ở "State". Không đụng `HANDOFF.md`, `docs/ROADMAP.md`, `lab/DECISIONS.md` (D006).

## 8. Tiếp theo

1. **Chủ dự án mở `T090-triet-hoc-ch1.pptx`, lật và chấm** (điểm + một dòng nhận xét). Đồng thời
   duyệt demo T087 nếu thấy được.
2. Nếu chủ dự án duyệt: thêm deck này vào `skills/pptx/examples.md` làm **mẫu thứ hai** (bài
   giảng 7 slide, đã có Morph trạng thái) — đó là việc của trưởng nhóm.
3. Sửa 8 điểm lời chỉ dẫn ở mục 6, rồi chạy lại T090 **một lần** với nội dung mới có số liệu thật
   do chủ dự án đưa (đúng đề bài gốc), để đo xem lần thứ hai có nhanh hơn và ít lỗi hơn không.
4. Chấm A/B mù khi T071 có (deck này so với T066 và so với Forge) — trước đó không tuyên bố
   "tốt hơn" (D001).

## Review response

Chưa có review. Đề nghị người phản biện khác họ model (Claude hoặc Gemini) đọc diff + chạy lại
lệnh ở mục Method, đối chiếu bảng Evidence, và trả lời: (1) bằng chứng rung 4/5 có đúng không;
(2) deck có lỗi thị giác nào người thấy ngay không; (3) 8 điểm ở mục 6 có đúng là lỗi của lời
chỉ dẫn không.
