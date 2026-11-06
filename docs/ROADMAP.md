# Lộ trình nghiên cứu PPTX

Đây là tài liệu sống: viết lại khi chặng thay đổi, không ghi nối thêm. Người viết là trưởng nhóm
(T070, Claude, 2026-11-04). Phần lý do và phản biện nằm ở
[experiments/T070-20261104-claude-lead-synthesis/REPORT.md](../experiments/T070-20261104-claude-lead-synthesis/REPORT.md).

**Agent nào cũng phải đọc tệp này trước khi nhận việc PPTX.**

## Đích đến

Đích đến là một công cụ dành cho AI. Agent đưa vào **ý đồ** gồm câu chuyện, nội dung và trạng thái
cảnh. Công cụ trả ra một file PPTX native, chỉnh sửa được, có chuyển động có lý do và có Morph liền
mạch. Kèm theo file là bằng chứng rằng PowerPoint chạy đúng. Chất lượng phải đủ để chủ dự án chọn
nó thay vì deck làm tay.

Chúng ta không cạnh tranh với PowerPoint, DeckCraft hay Copilot ở vai trò *bàn tay*: vẽ hình, đặt
hiệu ứng, sửa file. Những công cụ đó đã làm tốt và ta dùng lại chúng. Lab cạnh tranh ở vai trò
**bộ não và bằng chứng**:

| Khía cạnh | Ứng dụng văn phòng / ArtCraft | Lab nhắm tới |
|---|---|---|
| Chuyển động | Người chọn hiệu ứng cho từng hộp | Chuyển động sinh từ lập luận: mỗi click có một việc, vật thể có vòng đời |
| Morph | Người tự đặt tên và căn vị trí | Biên dịch từ trạng thái cảnh; bộ luật ghép đã kiểm chứng; không ghép nhầm |
| Dữ liệu | Biểu đồ tĩnh hoặc build theo series | Biểu đồ, KPI và quy trình có vũ đạo theo ý nghĩa |
| Hình ảnh | Ảnh dán vào slide | Ảnh qua xử lý (cắt nền, duotone, mặt nạ) và hình native tách phần để animate (T062); 3D Morph camera (T064) |
| Tương tác | Hyperlink, trigger làm tay | Game, điều hướng, trigger sinh tự động và bấm thử tự động (T058/T061) |
| Kiểm chứng | Không có | Khung hình PowerPoint thật, cổng lỗi thị giác, bộ đề vàng do người chấm |
| Người dùng | Con người qua giao diện | AI qua JSON và mã lỗi có cách sửa; model yếu vẫn ra kết quả tốt |
| Tiếng Việt | Font thiếu dấu, ngắt dòng sai | Kiểm glyph, đo chữ, sửa chữ quá dài |

## Sáu nguyên tắc dẫn đường

1. **Mắt chủ dự án là thước đo gốc.**
   - Điểm critic chỉ được dùng để nói "tốt hơn" sau khi nó dự đoán đúng lựa chọn A/B của chủ dự
     án từ 75% trở lên (T071).
   - Trước mốc đó, critic chỉ là công cụ bắt lỗi kỹ thuật.
2. **Đặt trí tuệ vào công cụ, không vào agent; riêng kịch bản thì phân vai.**
   - Công cụ làm nghề, cổng kiểm chặn lỗi.
   - **Kịch bản là nơi sinh ra chuyển động** (chuyển động là động từ của câu chuyện). Đây là phần
     cần phán đoán nhiều nhất, nên có trục riêng:
     [SCRIPT_TRACK.md](SCRIPT_TRACK.md) (T078).
   - Model yếu viết kịch bản theo phiếu cộng ví dụ vàng. Model mạnh hoặc chủ dự án **duyệt bản
     chữ trước khi dựng**.
   - Phép thử của mọi thay đổi là khoảng cách chất lượng giữa model yếu và model mạnh khi dùng
     cùng công cụ có thu hẹp lại không.
3. **Morph là đầu ra của trình biên dịch cảnh,** không phải hiệu ứng để agent chọn tay.
4. **Gu được lưu thành công thức có kiểm chứng.**
   - Mỗi công thức có khung hình mẫu từ PowerPoint, nói rõ khi nào dùng và khi nào không.
   - Script viết tay cho một deck là bản nháp nghiên cứu, không phải sản phẩm. Phần gu tốt trong
     đó phải được chuyển vào công cụ.
5. **Mỗi năng lực có đúng một nguồn sự thật:**
   - một writer timing;
   - một hệ style;
   - một bộ luật Morph;
   - một critic.

   Muốn xây cái thứ hai thì phải thay thế cái thứ nhất, kèm review.
6. **Không bịa.**
   - Thiếu nội dung thì trả mã lỗi, không điền "100%" hay "Bước hoàn thiện".
   - Tên gọi mới ("law", "architecture") chỉ được dùng khi có phép thử chứng minh nó.

## Kiến trúc mục tiêu

```
brief.md ──► script.md: ý đồ + cảnh + lời nói + động từ → chuyển động ← trục kịch bản (SCRIPT_TRACK)
             │   (chủ dự án / model mạnh duyệt bản chữ trước khi dựng)
             │
             ▼
         scene.json: diễn viên bền vững + trạng thái theo click/cảnh ← agent viết (chọn từ công thức)
             │
             ├─► layout: lưới + style preset + thang chữ              ← công cụ
             ├─► motion compiler: chênh lệch trạng thái
             │      ├─ trong cảnh: enter / exit / dim / move / scale / emphasis
             │      └─ giữa cảnh: Morph (tự đặt !!tên, chặn ghép nhầm,
             │                     chọn cách dựng theo bộ luật Morph)
             ▼
          deck.pptx (+ speaker notes từ story)
             │
             ▼
   Cổng: cấu trúc ─► khung hình tĩnh ─► khung hình chuyển động ─► bộ đề vàng (người chấm)
```

Những thứ đã có và được dùng lại:
- writer timing (`pptx_animator.py`);
- Forge (đo chữ, theme, tài sản);
- Morph Studio;
- harness T058;
- DeckCraft (cho hình native);
- phần brief và beat của Deck Director.

Những thứ bị thay:
- 14 layout cố định là nơi *duy nhất* tạo bố cục;
- cách ánh xạ diễn viên bằng chuỗi con trong `deck_director.py`;
- điểm critic dùng làm bằng chứng chất lượng.

## Trục kịch bản (T078–T082): chạy song song, đi trước chặng 2

Chi tiết trong [SCRIPT_TRACK.md](SCRIPT_TRACK.md). Việc đầu tiên: chủ dự án đọc kịch bản mẫu T078
và so với beat sheet T069a. Mọi deck mới ở chặng 2 phải có kịch bản đã được duyệt dạng chữ.

## Trục gu (T086): nghiên cứu gu đám đông từ nhiều lĩnh vực, chạy song song ngay

Chủ dự án (F11, F13): skill này cho mọi người, nên gu phải học từ những tác phẩm được nhiều người
công nhận ở nhiều lĩnh vực, không chỉ PPTX và không chỉ mắt một người. Học, thử, cải thiện; không
sao chép (F10, D010).

### T086 [cross] Nghiên cứu gu đám đông đa lĩnh vực → luật gu kiểm chứng trên PPTX

- **Câu hỏi:** những tác phẩm được đông người khen ở nhiều lĩnh vực có chung những luật nào? Luật
  nào viết được để model yếu áp dụng trên PPTX? Luật nào còn đứng sau khi thử trong PowerPoint?
- **Lĩnh vực (tối thiểu 8), mỗi lĩnh vực 5–10 nguồn tốt:**
  1. thuyết trình và keynote (keynote ra mắt sản phẩm, TED, sách và blog của các studio thiết kế
     thuyết trình);
  2. dàn trang editorial và in ấn, typography kiểu Swiss;
  3. thư viện "gu cho AI" về web:
     - `pbakaus/impeccable` (Apache-2.0);
     - skill frontend-design trong `anthropics/skills`;
     - `bergside/awesome-design-skills`;
     - `jimliu/baoyu-design`: chỉ học ý, vì tài liệu luật của nó không có giấy phép;
  4. motion design và motion graphic:
     - `motion-canvas`, Remotion;
     - reveal.js auto-animate, rất gần Morph;
     - 12 nguyên tắc hoạt hình;
     - hướng dẫn motion của Apple HIG và Material;
  5. thiết kế title phim và video giải thích;
  6. trực quan hóa dữ liệu và infographic;
  7. nhiếp ảnh và bố cục điện ảnh: khung hình, điểm nhìn, nhịp cắt;
  8. các bộ sưu tập được bình chọn (giải thưởng thiết kế, trang tuyển chọn có lượt thích hoặc
     sao), dùng làm thước đo "đám đông".
- **Phương pháp:**
  - **Ghi nguồn.** Với mỗi nguồn ghi: URL, ngày truy cập, giấy phép, và lý do nó được coi là tốt
    (giải, sao, lượt dùng).
  - **Rút luật bằng lời của mình.** Mỗi luật có: nội dung, con số nếu có, lý do, một phản ví dụ.
  - **Dịch sang PPTX.** Ghi tính năng gốc nào làm được luật đó: Morph và tên `!!`, motion path,
    crop, mặt nạ, nhịp click, chuyển slide. Ghi cả điều PPTX không làm được.
  - **Gu đám đông = luật được nhiều lĩnh vực đồng ý.**
    - Xếp hạng luật theo số lĩnh vực độc lập cùng nói.
    - Ghi rõ các luật mâu thuẫn và giữ cả hai.
  - **Kiểm chứng.**
    - Chọn 15 luật đứng đầu. Mỗi luật có một cặp `.pptx` trước/sau, **cùng nội dung**, chỉ khác
      đúng luật đó. Nội dung lấy từ T066 Triết học và đề pitch T081.
    - Ít nhất 5 luật là luật chuyển động, vì đây là điểm yếu nhất (F2, F14).
    - Chủ dự án lật từng cặp (đã đổi tên) và chọn mù.
- **Đầu ra:**
  - `experiments/T086-…/sources.md`: bảng nguồn theo lĩnh vực.
  - `experiments/T086-…/artifacts/pairs/*.pptx`: các cặp thử.
  - Các luật viết thành **văn bản chỉ dẫn** (D011), không phải JSON: mỗi luật có lời, lĩnh vực ủng hộ,
    nguồn, cách làm trong PowerPoint, ví dụ đúng/sai, và kết quả chấm mù. Đây là nguyên liệu cho
    T087.
  - Không sửa code sản phẩm. Đưa luật vào Forge và Director là việc của chặng 3.
- **Nghiệm thu:** ≥ 8 lĩnh vực, ≥ 60 nguồn có ghi giấy phép, ≥ 15 luật có cặp `.pptx` đã chấm mù.
- **Bác bỏ nếu:** bản "sau" không thắng quá 2/3 số cặp. Khi đó các luật còn quá chung chung. Phải
  viết lại cụ thể hơn (có con số, gắn với vật thể) rồi thử lại.
- **Cấm:**
  - chép nguyên văn tài liệu không có giấy phép;
  - đưa ảnh hoặc font có bản quyền vào repo (để trong `local-media/`).
- **Người làm → người phản biện:** một model mạnh (Claude hoặc Gemini) → model khác họ.
- **Cỡ:** 3–4 ngày. Có thể chia theo lĩnh vực cho nhiều phiên, mỗi phiên một nhánh (`T086a`,
  `T086b`…), cùng ghi vào một bảng nguồn.

## Skill là lời chỉ dẫn (D011, T087): ưu tiên số một

Chủ dự án (F15): skill không nhất thiết là code. Ở baoyu-design và nhiều dự án khác, skill là lời
chỉ dẫn; model đọc và tự làm. Lab này đã đi ngược: 103 script, còn 8 skill chủ yếu là sách lệnh
"chạy X, kiểm Y". Deck đẹp nhất (T066) đến từ phán đoán, không từ chuỗi công cụ.

### T087 [pptx] Skill PPTX viết như một người thầy thiết kế

- **Câu hỏi:** một model (kể cả model yếu) chỉ đọc lời chỉ dẫn và dùng vài công cụ nhỏ có làm ra
  deck đẹp hơn chuỗi công cụ hiện tại không?
- **Việc cần làm:** một skill duy nhất `skills/pptx/`:
  - `SKILL.md` ngắn: thứ tự suy nghĩ (người nghe → kịch bản → dàn ý tiêu đề → từng slide →
    chuyển động → tự mở file kiểm tra), và khi nào đọc hướng dẫn nào.
  - Các hướng dẫn ngắn, bằng lời thường, có con số và ví dụ đúng/sai: kịch bản, bố cục, chữ, ảnh,
    màu, chuyển động trong slide, Morph giữa các slide, tự kiểm tra.
  - Kiến thức đã chứng minh trong lab được viết lại thành lời (luật Morph T059/T064/T074, nhịp
    click, giới hạn PowerPoint), cùng luật gu từ T086 khi có.
  - Một hộp công cụ nhỏ: chỉ giữ những gì lời không làm được (ghi Morph và hiệu ứng vào file, đo
    chữ, mở file trong PowerPoint để chụp kiểm tra). Mọi script khác không còn là lối vào.
- **Nghiệm thu:** đưa skill cho một model khác họ với người viết (ví dụ DeepSeek). Model đó dựng
  lại bộ Triết học chương 1 và đề pitch T081. Chủ dự án mở và lật cặp `.pptx` đổi tên, so với
  T066 và với Forge hiện tại.
- **Bác bỏ nếu:** bản dựng từ lời chỉ dẫn thua Forge hiện tại. Khi đó phải ghi phần nào lời chỉ dẫn
  không truyền được, rồi mới thêm công cụ cho đúng phần đó.
- **Người làm → người phản biện:** Claude (trưởng nhóm) viết → model khác họ dùng skill để dựng.
  **Cỡ:** 2–3 ngày. Có thể bắt đầu ngay, rồi nạp luật T086 khi xong.

## Chặng 1: thước đo thật (đề bài đã giữ chỗ T071–T074)

Không ai làm chặng 2 khi T071 và T072 chưa xong. Không có thước đo thì không biết chặng 2 có
tiến bộ hay không.

### T071 [pptx] Bộ đề vàng và trang chấm A/B cho chủ dự án

- **Câu hỏi:** công cụ có làm deck tốt hơn qua từng tuần không, theo mắt chủ dự án?
- **Việc cần làm:**
  - 8 đề bài cố định, nội dung viết sẵn và có số liệu thật hoặc ghi rõ là minh họa:
    - báo cáo số liệu;
    - bài giảng (dùng nội dung Triết học chương 1);
    - ra mắt sản phẩm có ảnh;
    - quy trình;
    - pitch có KPI;
    - dòng thời gian lịch sử;
    - so sánh để ra quyết định;
    - quiz tương tác.
  - Lệnh `bench build <tag>`: dựng cả 8 đề bằng đúng lối vào sản phẩm (cấm script riêng). Đầu
    ra là **8 file `.pptx`** (D009); không cần video.
  - Lệnh `bench review A B`: đưa cặp `.pptx` A và B (đổi tên ngẫu nhiên để chấm mù) cho chủ dự án
    tự mở và lật trong PowerPoint. Chủ dự án chọn A, B hoặc ngang nhau, kèm một dòng nhận xét. Kết
    quả lưu vào `knowledge/bench/votes.jsonl`.
  - Mục tiêu dưới 10 phút cho một lượt chấm.
  - Hiệu chỉnh critic: đo tỷ lệ critic dự đoán đúng lựa chọn của chủ dự án.
- **Nghiệm thu:**
  - Chủ dự án chấm được một lượt so T066 (làm tay) với Forge hiện tại.
  - Có số đo độ khớp của critic.
- **Bác bỏ nếu:** chủ dự án thấy trang chấm tốn quá 15 phút, hoặc không phân biệt được hai bản.
  Khi đó đề bài đang quá dài và phải rút gọn.
- **Người làm → người phản biện:** Claude → OpenCode. **Cỡ:** 1–2 ngày.

### T072 [pptx] Cổng lỗi thị giác trên khung hình render

- **Câu hỏi:** máy có bắt được các lỗi mà mắt người thấy ngay không? Ví dụ các lỗi trong
  `experiments/T070-…/preview/critic-499-vs-eye.jpg`.
- **Việc cần làm** (chạy trên PNG của PowerPoint `Slide.Export`; lỗi giữa chuyển động lấy từ
  khung hình T073), mỗi lỗi là một mã **error**:
  - `VIS-CLIPPED`: chữ chạm mép slide hoặc mép khung;
  - `VIS-EMPTY-CARD`: thẻ hoặc khung có diện tích lớn mà mực dưới ngưỡng;
  - `VIS-PLACEHOLDER`: chữ giữ chỗ hoặc chữ tự sinh ("Bước hoàn thiện", "Chỉ số 1", số đuôi lặp,
    "Lorem");
  - `VIS-TINY`: cỡ chữ quy đổi theo phòng chiếu quá nhỏ (T066 có thân chữ 10–12 pt);
  - `VIS-STYLE-DROP`: style khai báo nhưng không áp dụng;
  - `VIS-COLLIDE`: chồng lấn giữa chuyển động.
- **Nghiệm thu:**
  - bắt đủ các lỗi trong ảnh bằng chứng của T070 trên deck T068;
  - không báo nhầm trên deck T066;
  - có test cho từng mã.
- **Bác bỏ nếu:** quá 10% cảnh báo trên bộ đề vàng là báo nhầm.
- **Người làm → người phản biện:** OpenCode → Claude. **Cỡ:** 1–2 ngày.

### T073 [pptx] Máy xem chuyển động nhanh

> Công cụ này để **agent** tự xem chuyển động, vì agent không lật slide được như người. Chủ dự án
> không cần video (D009).

- **Câu hỏi:** có thể xem khung hình chuyển động trong slide trong vài giây thay vì vài phút
  (CreateVideo) không?
- **Hai tuyến, làm song song rồi so:**
  1. **DeckCraft `render-animation`:** bản vá prototype của T060 cộng sửa lỗi repeat ở mức
     behaviour (bước E). Build từ commit đã ghim, lưu bản vá và script build trong repo, không
     commit binary. Khung hình gắn nhãn `DeckCraft render`.
  2. **Ghi slideshow thật bằng harness T058:** chạy show, bấm click theo kế hoạch, chụp màn hình
     theo chu kỳ. Đây là PowerPoint thật, có đồng hồ click, nên tốt hơn CreateVideo vốn không lộ
     thời điểm click.
- **Nghiệm thu:** trên 3 deck của bộ đề vàng, cả hai tuyến đều có bảng lệch so với CreateVideo.
  Tuyến 2 được dùng làm cổng cuối nếu ổn định.
- **Bác bỏ nếu:** tuyến 2 không chạy ổn trên máy có nhiều agent; khi đó cần một máy hoặc một
  phiên riêng.
- **Người làm → người phản biện:** Claude desktop → OpenCode. **Cỡ:** 2 ngày.

### T074 [pptx] Bộ luật ghép Morph, kiểm chứng bằng ma trận thí nghiệm

- **Câu hỏi:** PowerPoint ghép vật thể giữa hai slide theo luật nào, và khi nào thì Morph hỏng?
- **Phương pháp:**
  - Dùng phương pháp của T064: mỗi trường hợp là một deck 2 slide, render CreateVideo hoặc ghi
    slideshow, rồi đo "một vật thể liền" hay "hai vật thể mờ chồng". T064 đo bằng độ sáng và vị
    trí camera theo từng khung.
  - Ma trận tối thiểu 30 ô:
    - cùng `!!tên` / khác tên cùng loại / khác loại shape (chữ nhật → elip);
    - group và bỏ group;
    - chữ giống hệt / khác vài từ / tùy chọn Morph theo object, word, character;
    - ảnh cùng media / crop khác / media khác;
    - chart, table, SmartArt;
    - model 3D chung part và không chung part;
    - xoay > 180°, lật;
    - đổi gradient;
    - connector;
    - vật thể có entrance ở slide đích;
    - vật thể bay vào từ ngoài slide;
    - đổi thứ tự z.
- **Sản phẩm:**
  - `knowledge/morph_rules.json`: luật, điều kiện, kết quả đo, khung hình mẫu;
  - một trang tóm tắt "nên / không nên".
- **Nghiệm thu:** mỗi luật có khung hình PowerPoint (rung 5) và một test cấu trúc.
- **Người làm → người phản biện:** OpenCode → Claude. **Cỡ:** 2–3 ngày.

## Chặng 2: Morph và cảnh (giữ chỗ T075–T077; bắt đầu sau khi T071–T072 được review)

### T075 [pptx] `scene.json` và trình biên dịch cảnh

> **Tạm dừng (D011).** Chỉ mở lại nếu T087 cho thấy lời chỉ dẫn không đủ để làm Morph giữa các cảnh.

- **Câu hỏi:** agent có thể chỉ mô tả trạng thái mà vẫn ra Morph và chuyển động đúng không?
- **`scene.json`:**
  - `actors`: id, loại (text, picture, shape, native-art, chart, model3d), nội dung, style role;
  - `scenes`: mỗi cảnh là một slide, gồm `states` theo click;
  - mỗi state ghi vị trí theo **ô lưới có tên** (không dùng tọa độ), độ mờ, vai trò (focus, dim,
    hidden).
- **Bộ biên dịch:**
  - Chênh lệch giữa hai state trong một cảnh thì sinh hiệu ứng trong slide.
  - Diễn viên xuất hiện ở hai cảnh liên tiếp thì đặt `!!id` và áp luật T074. Model 3D thì dùng
    cách "nhân bản slide" của T064.
  - Diễn viên không có ở cảnh sau thì dùng exit hoặc fade.
  - Tên duy nhất để chặn ghép nhầm.
  - Speaker notes lấy từ story.
- **Nghiệm thu:**
  - dựng lại 4 Morph trạng thái của T069a từ `scene.json` mà không cần script riêng;
  - qua cổng T072;
  - khung hình T073 đúng.
  - Bước tiếp theo là chấm A/B với T069a trên trang T071.
- **Bác bỏ nếu:** cần hơn 20% trường hợp phải ghi đè tọa độ tay. Khi đó lưới chưa đủ.
- **Người làm → người phản biện:** Claude → Antigravity. **Cỡ:** 3–4 ngày.

### T076 [pptx] Thư viện 10 nước Morph

- **Mười nước:**
  1. camera zoom vào chi tiết;
  2. thẻ nở thành trang;
  3. danh sách → một mục được chọn;
  4. dòng thời gian trượt;
  5. biểu đồ đổi dạng;
  6. tách / gộp;
  7. vật thể dẫn đường đi xuyên các phần;
  8. 3D xoay quanh;
  9. chữ Morph theo từ;
  10. lộ ra qua mặt nạ.
- Mỗi nước là một mẫu `scene.json` có tham số, kèm dải khung hình PowerPoint, ghi rõ khi nào dùng,
  khi nào không và lỗi hay gặp.
- **Nghiệm thu:** cả 10 nước qua T072/T073; chủ dự án chọn ít nhất 6/10 là "đáng dùng".
- **Người làm → người phản biện:** OpenCode → Claude. **Cỡ:** 3 ngày.

### T077 [pptx] Deck Director xuất ra cảnh

> **Tạm dừng (D011).** Cùng lý do với T075.

- **Giữ** phần đầu của `deck_director.py`: brief, beat, lời nói, speaker notes.
- **Thay** phần sau: ánh xạ chuỗi con vào 14 layout được thay bằng xuất `scene.json` và chọn nước
  từ T076.
- **Bỏ** mọi giá trị tự bịa; thay bằng mã lỗi `CONTENT_MISSING` có cách sửa.
- **Nghiệm thu:**
  - đề "bài giảng" của T071 dựng hoàn toàn bằng lối vào sản phẩm;
  - chấm A/B thắng hoặc hòa T066 (làm tay).
- **Người làm → người phản biện:** Antigravity → Claude. **Cỡ:** 2–3 ngày.

## Chặng 3: gu vào sản phẩm (chưa giữ chỗ; trưởng nhóm mở sau chặng 2)

Luật gu của chặng này lấy từ kết quả T086, và chỉ lấy luật đã thắng chấm mù.

- **Style preset:**
  - Chuyển công thức editorial của T066 và 5 style của T067 (VisualStyle/1) vào làm *một* hệ
    style duy nhất.
  - Thêm pipeline xử lý ảnh: cắt nền, duotone, mặt nạ, với cờ chất lượng cho ảnh cắt nền lỗi.
  - Loại bỏ hoặc gộp `theme_engine.py`.
- **Dàn trang theo lưới:** dùng lưới 12 cột, baseline và thang chữ, cùng các mẫu bố cục rút từ
  corpus deck đẹp (T027). Bố cục được *sinh*, không chọn từ 14 mẫu.
- **Đánh giá chéo model:** cùng 3 đề, DeepSeek, Gemini và Claude chạy qua cùng công cụ, rồi chấm
  A/B. Khoảng cách nhỏ dần qua các bản phát hành là bằng chứng công cụ đang mang gu thay cho agent.
- **Tương tác qua cảnh:** quiz và điều hướng dùng `scene.json` cộng writer T061, rồi bấm thử bằng
  T058.

## Đóng băng và dừng

- Không mở domain hoặc canon mới (video, CAD, audio). docx, xlsx và vector chỉ làm khi chủ dự án
  yêu cầu riêng.
- Narrative critic (T069b): giữ các mã lỗi cấu trúc (slide trống ở t=0, lời nói lệch click),
  nhưng **không** báo điểm narrative như chất lượng cho tới khi T071 hiệu chỉnh.
- `deck_director.py`: không vá thêm luật chuỗi con. Mọi việc chuyển sang T077.
- Không thêm "law" hoặc "architecture" mới nếu chưa có chấm A/B ủng hộ.

## Quy trình làm việc

### Với chủ dự án

1. **Tách phiên phản hồi khỏi phiên làm việc.**
   - Khi xem deck và nhận xét, ghi nhận xét vào sổ phản hồi
     `research/feedback/<YYYY-MM-DD>-<chủ-đề>.md`, theo từng mục đánh số F1, F2, …
   - Đừng giao việc mới trong cùng phiên đó.
   - Trưởng nhóm biến các mục phản hồi thành đề bài. Một mục chỉ đóng khi chủ dự án đánh dấu.
2. **Mỗi tuần một bản phát hành.** Dựng lại bộ đề vàng. Chủ dự án mở các file `.pptx` và lật so
   với bản tuần trước, khoảng 10 phút, không cần video (D009). Đây là chỗ chủ dự án *thấy* tiến bộ.
3. **Giao việc bằng đề bài đã giữ chỗ,** không giao bằng mô tả tự do. Một phiên agent chỉ làm một
   đề bài.

### Với agent

- Đọc `HANDOFF.md`, tệp này và đề bài của mình. Nhận đúng mã đã giữ chỗ.
- Mỗi đề bài phải có câu hỏi, điều kiện bác bỏ, nghiệm thu và cỡ việc.
- Builder và critic **khác họ model**: Claude, Gemini (Antigravity/Argon), DeepSeek (OpenCode).
  Review ghi vào `research/reviews/`.
- Tối đa 3 task PPTX mở cùng lúc. Merge vào `main` chỉ khi có review và qua cổng T072 (khi đã có).
- Báo cáo ghi đúng rung bằng chứng:
  - đếm XML là rung 1;
  - DeckCraft là rung 2;
  - PowerPoint mở được là rung 4;
  - khung hình PowerPoint là rung 5;
  - người xem là rung 6.
- Khi muốn nói "tốt hơn", phải có bằng chứng từ T071 (chấm A/B). Điểm critic không đủ.
- Không làm việc trong checkout của người khác. Dùng `git worktree` riêng.
