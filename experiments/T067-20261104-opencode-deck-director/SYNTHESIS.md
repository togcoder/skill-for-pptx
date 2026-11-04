# T067 — Vì sao deck có chuyển động mà vẫn không có “gu”

**Ngày:** 2026-11-04 · **Base:** `de9923f` (T066) · **Branch:**
`work/T067-opencode-deck-director`
**Trạng thái:** nghiên cứu + prototype, chưa merge. Không thay product path.

> Đây là bản tổng hợp 4 luồng chạy song song. Báo cáo gốc nằm trong
> `experiments/T067-.../` (`REPORT.md`, `REPORT-image-choreography.md`,
> `motion/`, `experiments/T067-...-visual-style/`).

## 0. Kết luận trước

1. **Deck T066 không thiếu hiệu ứng; nó thiếu “direction”.** 144 effect, 51
   click, 9 Morph vẫn không tạo được nhịp, vì không có file nào nói: ở giây này
   khán giả phải tin/ thấy gì, và vì sao.
2. **Base state `t=0` là lỗi nặng nhất.** 3 slide mở ra gần như trống; title bị
   khóa sau click ở **9/10 slide**. Slide 4 chỉ có kicker + mũi tên + 3 chấm.
3. **Ảnh không phải “trang trí cuối slide”.** 4/4 ảnh của T066 rơi vào click
   cuối; bìa có 3 vòng vàng rỗng từ `t=0`, ảnh vào click 4/4. Slide 2 có đĩa đỏ
   + credit đứng một mình qua 7 trạng thái, tượng vào click 7/7.
4. **Motion hiện tại là “hậu kỳ gắn effect”, không phải đạo diễn.** 51 click
   chỉ thêm, **0 object lifecycle** (không dim/exit), tới 4 mover cùng lúc.
5. **Theme hiện tại là palette + font + layout, không phải style.** 5 style
   specimen đã chứng minh có thể định nghĩa style bằng vật liệu/hình học/độ
   sâu/texture/motion; nhưng liquid glass là **frost giả**, không phải blur thật.
6. **Câu trả lời không phải “bỏ hết Morph”** (bản motion đã thử: 0 Morph, êm
   hơn nhưng mất state-pair). Câu trả lời là **3–4 Morph có nghĩa**, mỗi Morph
   nối một cặp trạng thái của cùng một ý.
7. **Critic hiện tại không thấy lỗi này.** Nó chấm ảnh cuối slide và trung bình
   effect; một deck có base trống, ảnh coda, Morph/entrance xung đột vẫn có thể
   đạt motion 4.99.
8. **Skill mới cần: `deck-director`.** `brief → script → beat sheet → shot list
   → motion plan → build`, với `base_state` khai báo trước và `state_after` theo
   từng click. `visual-style` là lớp chọn style; `state critic` là cổng kiểm.

## 1. Bốn luồng đã làm gì

| Luồng | Kết quả chính | Commit |
|---|---|---|
| Skill audit | 17 finding, 3 nguyên nhân gốc; draft `skills/deck-director/SKILL.md` | `9b70e62` |
| Image choreography | Audit 7 placement, 8 finding, 25 luật, 2 variant A/B, 32 state render | `18bfdfa` |
| Motion dramaturgy | Sửa timing: 51→27 click, 144→116 effect, 0 empty base, 0 ảnh cuối, 0 Morph | `fc4021d` |
| Visual style | `VisualStyle/1`, 5 preset, 5 specimen cùng nội dung, linter, PPTX 631 KB | `02dd5a9` |

## 2. Bằng chứng T066 — những con số không biết nói dối

| Đo | Trước | Sau (motion) |
|---|---:|---:|
| Click | 51 | **27** |
| Effect | 144 | **116** |
| Slide mở ra 0 chữ | 3 | **0** |
| Ảnh hiện ở click cuối | 4/4 | **0** |
| Title bị khóa sau click | 9/10 | **0** |
| Morph | 9 (nền + sợi chỉ) | **0** |
| Mover tối đa cùng lúc | 4 | **2** |
| Critic overall | 4.03 | 4.02 |
| Motion | 4.99 | 4.94 |

Bản motion đã chứng minh một điều: **sửa base state làm deck đọc được ngay**,
nhưng **0 Morph là reset an toàn, không phải đích**. Nó bỏ luôn cơ hội
state-pair Morphing.

## 3. Ba nguyên nhân gốc (skill audit)

### A. Pipeline layout-first, motion-last

`slide_forge.build()` dựng file tĩnh xong mới để `motion_director` đọc hình học
và gắn effect. Input kể chuyện duy nhất là `spec["title"]`. Vì thế:

- ảnh do layout đặt vào slot trống cuối cùng;
- motion chỉ còn quyền chọn “click thứ mấy”;
- **4/4 ảnh T066 rơi vào click cuối**;
- **9/10 title tự chạy** (auto), không phải click có chủ đích;
- **0 lifecycle** — 51 click chỉ thêm, không bao giờ dim/exit.

### B. “Gu” không có chỗ để viết, và không ai kiểm

Plan có field `script`, nhưng nó được sinh từ chính deck (`"slide N: <title>"`);
`purpose` là câu template. Critic chỉ đọc PPTX, **không đọc plan**, nên ý đồ
không thể bị chấm. Vì vậy motion 4.99 trên một deck không có lifecycle.

### C. Style bị định nghĩa bằng token, không bằng quan điểm

`THEMES` = 6 màu + 2 font; `motion.style` = bảng preset theo role. Không có gì
quyết định: ảnh là bằng chứng hay trang trí, khoảng trắng bao nhiêu, ngữ pháp
chuyển động là gì, hình học là sắc cạnh hay blob. Đó là lý do 5 style specimen
cùng nội dung lại trông khác nhau hoàn toàn — và cũng là lý do T066 chỉ có
“một palette đẹp”, chưa phải “một style”.

## 4. Image choreography — lỗi và luật

### Lỗi đo được

- **Bìa:** 3 chân dung vào click **4/4**, nhưng 3 vòng vàng rỗng đã hiện từ
  `t=0` → **12 khung rỗng** qua 4 trạng thái.
- **Slide 2:** đĩa đỏ chiếm **60,7% chiều cao slide**, credit *“Tượng triết gia
  Hy Lạp · CC0”* đứng một mình suốt **7 trạng thái**; tượng vào click **7/7**.
- **Slide 7:** ảnh là “màn chót”, không có câu thoại gọi tên.

### Luật chốt

> Một ảnh là **một khối duy nhất** (mặt + vành + nền + chú thích). Nó vào đúng
> nhịp câu gọi tên nó — không bao giờ sau câu cuối. Ảnh neo danh tính có mặt từ
> `t=0`; ảnh bằng chứng vào cùng click với câu gọi tên; ảnh làm coda bị cấm.

Hệ quả:

- thứ tự ảnh = **thứ tự lập luận**, không phải thứ tự “dàn cast”;
- nhóm ảnh = nhóm của câu (2 người đặt nền + 1 người kế tục, không phải 3 cột
  ngang nhau);
- **A cho bìa** (ảnh là nền, title khắc lên) + **B cho slide lập luận** (ảnh
  vào đúng 1848/1867/1917; click 1867 không thêm mặt mới = “cùng con người đó
  đi tiếp”).

## 5. Motion dramaturgy — sửa gì, và cái gì vẫn chưa đủ

Bản motion đã làm đúng:

- base state đọc được ở cả 10 slide;
- 27 nhịp, tối đa 2 mover, 1 hero/slide;
- bỏ 52 tên `!!`, xóa `dialectic-foot` bị thẻ che;
- notes viết lại theo beat.

Nhưng vẫn còn 2 vấn đề:

1. **Slide 4 vẫn bất đối xứng:** click 2 ra đường thẳng + nhãn “TÁCH RỜI / BẤT
   BIẾN”, click 3 mới ra card “SIÊU HÌNH”. Người xem đã hiểu so sánh trước khi
   vế thứ hai xuất hiện. Đúng ra: cả hai vế phải hoàn tất trong **cùng một
   beat**, hoặc cả hai có mặt từ `t=0` và chỉ pulse một lần.
2. **0 Morph là quá tay.** 9 Morph cũ vô nghĩa, nhưng bỏ hết cũng bỏ luôn
   state-pair. Đề xuất: **3–4 Morph**, mỗi cái nối một cặp trạng thái thật:
   - bìa → slide 2: title lớn thu thành heading, chân dung thu thành medallion;
   - slide 3 → 4: hai card “VẬT CHẤT / Ý THỨC” biến thành “BIỆN CHỨNG / SIÊU
     HÌNH” (hoặc 4A → 4B);
   - slide 6 → 7: ba khối “ba bộ phận” thu thành ba mốc timeline;
   - slide 9 → 10: dấu ngoặc kép + câu kết.
   Không Morph nền, không Morph sợi chỉ, không Morph nếu hai bên không cùng một ý.

## 6. VisualStyle/1 — theme như một hệ thống

5 preset, cùng một nội dung (claim + Marx + 2 fact), 14–20 shape/slide,
**90,0–94,7% native**, 4–6 cỡ chữ, 31–34 từ/slide:

| Style | Một dòng | Native PPTX |
|---|---|---|
| **editorial-crimson** | đỏ son phẳng, Palatino + Arial, vàng, ảnh duotone trong vòng tròn | 100% |
| **liquid-glass** | nền tối, pane kính 10%, viền 30%, specular, ảnh 4:5 lạnh | **frost giả**; không backdrop blur |
| **clay-cartoon** | kem, squircle/blob viền dày, bevel matte 2.5D, Segoe UI Black | native nhưng viền clay bake trong PNG |
| **swiss-minimal** | giấy trắng, lưới 12 cột, Arial Bold 54, một đỏ, zero effect | 100% |
| **maximalist-collage** | giấy + halftone, dải giấy, chữ outline, ảnh xerox, xoay ±8° | native, nhưng layout rất đắt |

Bằng chứng: `styles.pptx` 631.684 B, PowerPoint COM mở **152 ms**, PDF 5
trang. Schema `VisualStyle/1` có 9 colour roles, 3 type roles, geometry /
material / depth / texture / image / motion / density; 5/5 preset validate;
linter `visual_style.py check` pass 5/5.

**Bài học OOXML:** `gradFill` đặt sau `a:ln` bị PowerPoint bỏ qua và fallback
về theme fill; đặt trước `a:ln` thì alpha từng stop mới chạy. Radial gradient
còn bị viền ở mép ellipse nếu alpha chưa về 0 trước ~78% bán kính.

## 7. Tranh luận với Argon — đồng ý và phản biện

### Đồng ý

- **Base-state gate:** `t=0` phải có title + primary anchor; nếu không, fail.
- **No orphan connector:** mũi tên/chấm không hiện trước source + target.
- **Semantic grouping:** một card là một khối; không animate lẻ từng dòng/chấm.
- **Morph/entrance conflict:** shape `!!` tham gia Morph không được có entrance.
  T066 vi phạm ở `!!thread`/`!!dot`.
- **State-sequence critic:** chấm `t=0` và từng click, không chấm ảnh cuối.
- **One salience peak:** mỗi trạng thái chỉ một vùng accent; squint test.
- **Spatial argumentation:** tắt chữ vẫn phân biệt được logic.

### Phản biện

1. **“Bỏ cut-out, đóng khung ảnh hết”** — không. Ảnh tách nền là phần owner
   khen (“cắt ảnh khá tốt”). Vấn đề là **vai trò và thời điểm**, không phải
   cut-out. Giữ cut-out, nhưng gắn với câu nói + grid.
2. **“Liquid glass là gimmick vì OOXML không có backdrop blur”** — đúng một
   nửa. Không có blur thật, nhưng translucent fill + soft edge + bevel +
   layered gradient + ảnh nền blur là frost giả đủ dùng; phải test, không nên
   xóa.
3. **“Trần 35–40 effect cho cả deck”** — quá cứng. Nên đếm **beat/hero move**,
   không đếm raw effect; một beat có thể có 3–4 shape chạy `with`.
4. **“Gộp slide_forge + motion_director thành scene_compositor”** — đúng về
   nguyên tắc “layout và motion phải giải cùng lúc”, nhưng gộp hai module lớn
   thành một monolith là rủi ro. Đề xuất **lớp `deck-director`** gọi cả hai,
   không xóa hai module.
5. **“Cartoon/clay phản cảm với triết học”** — đó là judgment về nội dung, không
   phải luật kỹ thuật. Cứ để style system sinh ra nó; người chọn style mới là
   người quyết định có hợp không.

## 8. Kiến trúc đề xuất

```text
brief → script → beat sheet → shot list → motion plan
                                      ↓
                              deck.json + director.json
                                      ↓
                    slide_forge.build + motion_director.apply
                                      ↓
                          deck_state_critic (t=0 … t_n)
```

### `deck-director` (mới)

- `direction.json`: brief, style, script, beats, shots.
- Mỗi shot khai báo `base_state` trước, rồi `state_after` theo click.
- Mỗi object có `role` (anchor / evidence / turn / payoff) và ảnh có `asset`
  + `treatment`.
- Gate: object xuất hiện đúng một lần; base state không được rỗng trừ `hook`;
  beat `contrast` phải thấy hai vế; ảnh `portrait` không được ở click cuối.

### `visual-style`

- `VisualStyle/1` + 5 preset + linter.
- Style quyết định shape language, material, depth, texture, image treatment,
  motion language, density.
- Không thay palette generator; nó là **style manifest** cho generator.

### `deck_state_critic` (phải làm tiếp)

Chấm chuỗi trạng thái, không chấm ảnh cuối:

1. **Gate `t=0`:** title/primary anchor bị ẩn → FAIL.
2. **Gate orphan decorator:** connector/dot/arrow hiện khi node đích còn ẩn → FAIL.
3. **Gate image role:** ảnh không có `spoken_cue`, hoặc portrait ở `step == max` → FAIL.
4. **Gate budget/Morph:** >3 click/slide, >6 effect/slide, hoặc `!!` shape có entrance → FAIL.
5. **Gate lifecycle:** deck chỉ có entrance, 0 dim/exit → WARN/FAIL tùy register.

## 9. Cần xoá / gộp / viết lại

**Xoá:**

- bước “Story first” dạng văn xuôi trong `slide-forge`;
- “one-shot path when speed beats craft” trong `pptx-motion-director`;
- tour tự động cho mọi cycle ≤5;
- nhận diện title bằng placeholder;
- `MOT-TITLE` mức “note”;
- cách critic chấm trung bình từng effect đè lỗi cấu trúc;
- `theme_engine.ARCHETYPES` như schema style thứ hai.

**Gộp:**

- `slide_forge` + `motion_director` **không gộp code**, nhưng phải nhận cùng
  một `director.json` / `shot list`; layout và motion giải cùng lúc.
- `visual-style` thay `theme_engine` ở phần style; `theme_engine` giữ phần
  extract/synthesize theme, không giữ style schema.

**Viết lại:**

- `skills/deck-director/SKILL.md` (draft đã có).
- `skills/slide-forge/SKILL.md`: thêm `--plan`, bỏ “story first” văn xuôi.
- `skills/pptx-motion-director/SKILL.md`: bỏ one-shot, thêm base-state gate.
- `design_critic`: thêm state-sequence mode.

## 10. Việc tiếp theo (T068)

1. **Implement `deck_state_critic`** trên T066 before/after; nó phải fail T066
   ở base-state/image-coda/Morph-conflict và pass bản directed.
2. **Build T068 “directed deck”**: 10 slide, ≤27 beat, base state đọc được,
   ảnh là block, **3–4 semantic Morph**, style `editorial-crimson`; render
   before/after states.
3. **Làm một biến thể `liquid-glass`** trên cùng nội dung để chứng minh style
   system không chỉ là 5 specimen rời.
4. **Review**: Argon/Claude phản biện; human rung 6.

## 11. Điểm yếu của chính T067

- Chưa có **một** artifact cuối kết hợp cả base-state + image block + semantic
  Morph + style system; hiện là 4 mảnh.
- Motion bản sửa **0 Morph**; chưa chứng minh state-pair Morph.
- Style specimen chỉ 5 slide, chưa áp lên toàn deck.
- Chưa có `deck_state_critic` chạy thật.
- Chưa có rung 6 (người review từng click).
- T067 vượt cap 10 MB sau khi gộp; đã cắt bớt state PNG, giữ contact sheet.
- `check_layout`/test chưa chạy trên cây T067 đã cắt gọn.

> Tóm lại: T066 chứng minh lab **làm được** ảnh đẹp, font đẹp, theme đẹp.
> T067 chứng minh lab **chưa có đạo diễn**. Việc tiếp theo không phải thêm
> hiệu ứng, mà là **viết kịch bản/beat sheet trước, khai báo base state, gắn
> ảnh với lời nói, và chỉ Morph khi cùng một ý**.
