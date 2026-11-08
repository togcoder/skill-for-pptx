# T094 [pptx] Diễn tập mù: model khác họ đồng bộ bộ chắp vá bằng mục 10

Agent: dsh (DeepSeek, DSH) · Ngày: 2026-11-08 · Nhánh: `work/T094-dsh-harmonize-patchwork`
Trạng thái: **review requested** — chủ dự án mở ba file và chấm; trưởng nhóm sửa lời chỉ dẫn theo mục
"Chỗ mục 10 mơ hồ" bên dưới.

## Mở ba file này

| File | Là gì |
|---|---|
| `experiments/T093-20261108-claude-harmonize-deck/artifacts/qcc-chap-va.pptx` | bộ **gốc** chắp vá |
| `experiments/T093-20261108-claude-harmonize-deck/artifacts/qcc-dong-bo.pptx` | bản đồng bộ của T093 (Claude) |
| `experiments/T094-20261108-dsh-harmonize-patchwork/artifacts/qcc-dong-bo-dsh.pptx` | bản đồng bộ của T094 (dsh, **bản này**) |

Khi lật bản T094, xem: tiêu đề 8 slide nội dung cùng một chỗ/cỡ/màu; cả bộ 1 họ font, 6 cỡ chữ, 6 màu;
bìa và slide cảm ơn cùng nền xanh; biểu đồ 3D thành phẳng (đường + cột ngang); xương cá nằm gọn
trong khung, bấm 4 lần ra 4 nhóm 4M; ảnh trước/sau cùng cỡ, không méo; bảng 8 cột xuống phụ lục;
13 lần bấm có nhịp, còn lại Fade; không còn hiệu ứng nảy/xoay/bay.

## Nói thật về chữ "mù" (quan trọng cho phương pháp)

Tôi đã **đọc REPORT và mô tả PR của T093 trước khi làm bài** — vì PR là chỗ chủ dự án giao việc và
mô tả nó nằm ngay trên đường vào task. Tôi **không** mở `qcc-dong-bo*.pptx`, `harmonize.py`, `plan.json`
trước khi bản của tôi xong; sau khi xong mới mở để so sánh (mục cuối). Vì vậy đây là **diễn tập bán mù,
không phải mù hoàn toàn**: tôi đã biết trước một phần cách T093 xử lý vài slide.

Đề nghị cho lần sau: người giao việc đưa **chỉ file gốc + mục 10**, không đưa REPORT/PR của người đi
trước; hoặc ghi rõ "được đọc mô tả PR, không đọc REPORT".

## Bước 1 — bảng ý (lập trước khi đụng file)

Đầy đủ ở [`inputs/idea-table.md`](inputs/idea-table.md): 10 slide gốc + phụ lục, mỗi slide một câu
"người nghe nhớ gì", bằng chứng, nhóm Giữ/Sửa vỏ/Làm lại. Tóm tắt nhóm: **Sửa vỏ** 1, 3, 4, 8, 10;
**Làm lại** 2, 5, 6, 7, 9; **mới** phụ lục 11. Câu hỏi "?" gửi chủ dự án ở cuối.

## Hệ thống (bước 4, chọn một lần)

- **1 họ font: Century Gothic** (font dự án QCC; ghi vào theme, và mọi run ghi tên font để `inventory`
  đọc ra được). Bộ gốc có 5 font: Arial, Tahoma, Times New Roman, Calibri, theme.
- **6 cỡ: 16 / 18 / 20 / 32 / 44 / 54 pt** (nhãn phụ lục / nhãn / nội dung / tiêu đề / tiêu đề bìa /
  số lớn). Bộ gốc 14 cỡ.
- **6 màu chữ**: 262626 (thân), 1F4E79 (chính — lấy từ màu chiếm nhiều nhất bộ gốc: nền bìa + cột
  biểu đồ), FFFFFF, DCE6F1 (chữ phụ trên nền xanh), C00000 (nhấn — màu "mục tiêu" của bộ gốc),
  A6A6A6 (mục tiêu/đường). Bộ gốc 11 màu.
- Nền trắng cho 9 slide nội dung; **bìa + cảm ơn cùng nền 1F4E79**, chữ trắng. Không bóng, không phát
  sáng, không clip-art.
- Tiêu đề mọi slide nội dung: (0,6 in; 0,35 in), rộng 12,1 in, 32 pt đậm màu chính, canh trái.
- Chuyển slide: **Fade** cho slide 2–11, bìa không có; **không Morph** (không có vật nào thật sự đi
  tiếp — mục 7).

## Việc đã làm từng slide

| Slide | Nhóm | Đã làm | Vì sao |
|---|---|---|---|
| 1 Bìa | Sửa vỏ | Bỏ bánh răng, bỏ bóng chữ; nền xanh đậm; tiêu đề 44 pt; phụ đề + dòng "dữ liệu giả lập" | Cùng hệ thống, giữ nguyên câu chữ |
| 2 Lý do | Làm lại | Đoạn văn 111 chữ → 3 ý ngắn (4,1% so với 2%; chi phí/giao hàng; 2 lần phản hồi) + khối MỤC TIÊU; đoạn gốc vào notes | Đoạn văn dài; giữ nguyên số và từ |
| 3 Hiện trạng | Sửa vỏ | Cột 3D + cột mục tiêu → **đường** (số của chính biểu đồ), mục tiêu là đường xám; dòng thông điệp "Cả 6 tháng đều trên mục tiêu 2% — trung bình 4,1%" | 3D làm sai so sánh; xu hướng đọc bằng đường |
| 4 Xương cá | Sửa vỏ (thu gọn) | Thử `scale` 0,72 → chữ nhỏ nhất **17,28 pt < 18** (công cụ cảnh báo), nên **dựng lại** thành 4 nhánh dọc trên một xương sống, 4 nhóm 4M + 8 nguyên nhân, bấm 4 lần; giữ đủ chữ | Cụm 20 hình tràn 0,75 in và đè tiêu đề; thu nhỏ nữa thì chữ dưới chuẩn |
| 5 Nguyên nhân | Làm lại | Tròn 3D → **cột ngang xếp từ lớn đến nhỏ**, chỉ "Que hàn ẩm" tô màu; dòng thông điệp 38% | Câu hỏi là "cái nào lớn nhất", không phải cơ cấu |
| 6 Theo dõi | Làm lại | Bảng 7×8 → **số lớn 1,2%** + **đường 6 tuần** dựng từ chính số trong bảng (3,8…1,2) + mục tiêu 2; bảng đầy đủ sang phụ lục | Bảng nhiều cột chỉ để nói một xu hướng |
| 7 Các bước | Làm lại | 5 gạch đầu dòng → **5 bước trên một trục**, mỗi bước một lần bấm | Gạch đầu dòng là quy trình |
| 8 Ảnh | Sửa vỏ | `unstretch --box` cả hai ảnh (không cắt chỗ đang nói), đưa về **cùng khung 5,6×4,2 in**, nhãn TRƯỚC/SAU; ảnh "Sau" hiện khi bấm | Ảnh bằng chứng: không được méo, không mất phần nào |
| 9 Kết quả | Làm lại | Bỏ ngôi sao, "!!!"; hai số lớn 4,1% → 1,2%, mũi tên, dòng "Đạt mục tiêu dưới 2% — duy trì kết quả" | Sự thay đổi là hai con số cạnh nhau |
| 10 Cảm ơn | Sửa vỏ | Cùng kiểu bìa, bỏ mặt cười | Cùng hệ thống |
| 11 Phụ lục | mới | Chép bảng gốc sang slide mới, 16 pt, kẻ ngang mảnh, cột số canh phải, tiêu đề phụ lục | Giữ đủ số của bảng |

Chuyển động: 13 lần bấm / 17 nhịp (slide 2: 2; 3: 1; 4: 4; 5: 1; 6: 2; 7: 5; 8: 1; 9: 1; bìa, cảm ơn,
phụ lục không bấm), 46 hiệu ứng. Notes viết lại theo mẫu `[T=0]` / `[CLICK n]`, giữ nguyên số và
nguyên văn đoạn gốc ở slide 2.

## Bằng chứng

| Kiểm | Kết quả | Bậc |
|---|---|---|
| `inventory` gốc → bản mới | font **5 → 1 họ**; cỡ **14 → 6**; màu chữ **11 → 6**; 0 biểu đồ 3D; 0 ảnh méo; 0 vật tràn; 0 hiệu ứng trang trí; 6 kiểu chuyển → 1 (Fade) | 1 |
| `numbers` gốc → bản mới | **0 số bị mất** (số trong bảng chuyển sang phụ lục vẫn tính là còn) | 1 |
| `rechart` giữ hiệu ứng | thử trên chính slide 3: đặt 1 click vào biểu đồ, rechart → **id và tên giữ nguyên, `spTgt` vẫn trỏ đúng chart id 3** | 1 |
| `scale` 0,72 xương cá | chữ nhỏ nhất **17,28 pt** (< 18) → quyết định dựng lại thay vì thu nhỏ | 1 |
| PowerPoint 16.0 mở bản mới | **11 slide**; `EntryEffect 3849` (Fade) slide 2–11; **46 hiệu ứng**, mọi hiệu ứng **trỏ đúng hình** | 4 |
| `look` của PowerPoint, nhìn 4 vòng và sửa | `preview/after-look/` (bản trước `preview/before-look/`) | 4 |
| `pytest` toàn lab | 589 passed, 10 skipped | 1 |
| `check_layout`, `coord.py check` | sạch / không va chạm (xem PR) | 1 |
| Chủ dự án mở ba file và chấm | **chưa** | 6 |

Bản gốc có 5 kiểu chuyển (split, push, cover, wipe, zoom) và 12 hiệu ứng trang trí; bản mới chỉ còn
Fade + 13 nhịp bấm có lý do.

## Chỗ mục 10 mơ hồ hoặc thiếu — câu tôi đã phải tự đoán

Đây là phần chính của T094. Mỗi dòng: chỉ dẫn hiện tại → chỗ tắc → tôi tự quyết gì → đề nghị sửa lời.

1. **Bước 4 không nói kích thước slide.** Bộ gốc 13,33 × 7,50 in, deck QCC thật là 20 × 11,25 in.
   Tôi giữ nguyên 13,33 in (đổi khổ là dựng lại toàn bộ). *Đề nghị:* thêm một câu: "Đổi khổ slide
   không phải việc của bước đồng bộ; giữ khổ gốc và ghi câu hỏi nếu đích cần khổ khác."
2. **"Tiêu đề giữ nguyên chữ" — chữ hoa/thường có tính là chữ không?** Bộ gốc có tiêu đề VIẾT HOA
   toàn bộ và một tiêu đề có số "1." trong khi 8 slide kia không có. Tôi đổi về câu thường (coi là vỏ)
   và giữ số "1.", đưa vào câu hỏi. *Đề nghị:* ghi rõ: "chữ trong tiêu đề giữ nguyên từ; kiểu hoa/
   thường là vỏ và nên thống nhất; số thứ tự lệch thì hỏi người dùng, đừng tự thêm/bớt."
3. **Bước 3 nói "thu gọn cả cụm" nhưng không nói khi nào thì thôi thu.** Cụm xương cá 20 hình cần
   factor 0,72 để vừa khung → chữ 17,28 pt. Chỉ sau khi chạy mới thấy cảnh báo. *Đề nghị:* thêm câu:
   "Nếu `scale` báo chữ nhỏ hơn 18 pt, dừng thu và dựng lại bố cục (đừng thu tiếp)."
4. **Bảng lớn đưa xuống phụ lục nhưng không có cỡ chữ cho phụ lục.** Mục 4 đòi nội dung ≥18 pt; bảng
   8 cột trên khổ 13,33 in ở 18 pt bị xuống dòng nặng. Tôi dùng 16 pt (bản T093 cũng 16 pt).
   *Đề nghị:* một câu: "Bảng phụ lục là chỗ tra cứu: 16 pt được, tiêu đề bảng vẫn 18 pt."
5. **Chọn "màu chiếm nhiều nhất" của bộ cũ: lấy màu gì?** `inventory` chỉ đếm **màu chữ**, không đếm
   màu nền/khối; tôi phải nhìn bìa và biểu đồ để biết xanh đậm là màu chính. *Đề nghị:* hoặc
   `inventory` in thêm màu nền/khối (việc của đồ nghề), hoặc mục 10 ghi "xem bìa và biểu đồ để chọn
   màu chính".
6. **Font ghi vào theme thì `inventory` không đọc ra tên.** Nếu làm đúng mục 9 (`theme_fonts` +
   `follow_theme`), `inventory` in "(theme body)/(theme heading)" chứ không in tên font — không kiểm
   được "1 họ font" bằng lệnh. Tôi ghi tên font trực tiếp cho mọi run để `inventory` đọc ra
   "Century Gothic". *Đề nghị:* `inventory` đọc theme rồi in tên font thật (việc T095), hoặc mục 10
   nói rõ chọn một trong hai cách và cách kiểm.
7. **Phụ lục do ai đặt tiêu đề?** Mục 10 nói "chuyển bảng xuống phụ lục" nhưng không nói slide phụ lục
   có tiêu đề mới hay giữ tiêu đề cũ. Tôi tự đặt "Phụ lục: kết quả theo dõi sau cải tiến" và ghi vào
   câu hỏi. *Đề nghị:* mẫu tiêu đề phụ lục + đưa vào danh sách câu hỏi người dùng duyệt.
8. **Dựng lại một slide thì hiệu ứng cũ mất — có được viết lại không?** Mục "Giữ hiệu ứng có nghĩa"
   nói về slide giữ nguyên; với slide dựng lại, tôi viết lại nhịp bấm từ bảng ý (4 nhóm 4M, mỗi nhóm
   một lần bấm; 5 bước, mỗi bước một lần bấm). *Đề nghị:* thêm câu: "Slide dựng lại: viết lại nhịp
   bấm từ bảng ý, số lần bấm = số ý cần nói."
9. **`numbers` "phải về 0" nhưng 0 chưa đủ.** Công cụ so **tập giá trị** trên cả deck, không so vị trí/
   ngữ cảnh: ví dụ mất "mục tiêu 2%" vẫn không báo nếu đâu đó còn số 2 (tôi đã chứng minh bằng test
   nhỏ, xem review). *Đề nghị:* mục 10 sửa thành "`numbers` là điều kiện cần; đối chiếu bảng ý bằng
   mắt từng slide" và ghi rõ giới hạn này ngay ở bước 7.
10. **Notes mẫu `[T=0]/[CLICK n]` (mục 9) nhưng `numbers` có đếm số trong notes.** Khi viết lại notes
    mà quên số cũ là mất số. Tôi giữ nguyên câu gốc có số trong notes slide 2–6. *Đề nghị:* bước 7
    nhắc: "viết lại notes thì giữ nguyên câu gốc và số của nó."
11. **Plan chuyển động đánh số slide — thêm slide phụ lục thì phải đánh lại.** Không khó nhưng mục 10
    không nhắc; tôi đánh lại plan sau khi thêm phụ lục.
12. **Danh sách "câu hỏi khi bàn giao" không có mẫu.** Tôi gom 4 câu (số thứ tự tiêu đề; hai dòng
    thông điệp mới; tiêu đề phụ lục; cỡ chữ bảng phụ lục). *Đề nghị:* cho một mẫu 3–5 dòng ở cuối mục 10.

## So sánh với bản T093 (chỉ mở sau khi bản của tôi xong)

| | T093 (Claude) | T094 (dsh) |
|---|---|---|
| Số slide | 11 (10 + phụ lục) | 11 (10 + phụ lục) |
| Font | Segoe UI qua theme (inventory không in tên) | Century Gothic ghi tên trực tiếp |
| Cỡ / màu | 6 / 6 | 6 / 6 |
| Xương cá | `scale` 0,68 giữ 6 nhịp bấm, 18 hiệu ứng | dựng lại 4 nhánh, 4 nhịp bấm, 12 hiệu ứng |
| Ảnh trước/sau | `unstretch --box`, cùng khung | `unstretch --box`, cùng khung |
| Bảng phụ lục | 16 pt | 16 pt |
| Số bị mất | 0 | 0 |
| PowerPoint | mở được, mọi hiệu ứng trỏ đúng hình | mở được, mọi hiệu ứng trỏ đúng hình |

Hai model khác họ, cùng đọc mục 10, ra hai bản dùng được và rất giống nhau về hệ thống (1 font, 6 cỡ,
6 màu, Fade, bảng xuống phụ lục, ảnh không méo). Khác biệt chủ yếu ở chỗ mục 10 còn để tự do: xử lý
xương cá (thu vs dựng lại), số nhịp bấm, có/không dòng thông điệp mới, chọn font cụ thể.

## Câu hỏi gửi chủ dự án

1. Chỉ slide 2 có số thứ tự trong tiêu đề ("1. Lý do chọn đề tài"): giữ số hay bỏ ở mọi slide?
2. Hai dòng thông điệp mới (slide 3: "Cả 6 tháng đều trên mục tiêu 2% — trung bình 4,1%"; slide 5:
   "Que hàn ẩm là nguyên nhân lớn nhất: 38%") chỉ dùng số đã có trên slide — giữ không?
3. Tiêu đề phụ lục tôi đặt: "Phụ lục: kết quả theo dõi sau cải tiến" — giữ hay đổi?
4. Bảng phụ lục 8 cột tôi để 16 pt (đọc được trên 13,33 in); có cần 18 pt không?

## Tệp

- `artifacts/qcc-dong-bo-dsh.pptx` — bản giao (11 slide, chuyển động đã ghi).
- `artifacts/qcc-dong-bo-dsh.static.pptx` — bản tĩnh trước khi ghi chuyển động.
- `inputs/idea-table.md` — bảng ý bước 1.
- `inputs/harmonize_dsh.py` — các bước đồng bộ theo thứ tự mục 10 (dùng `inventory/rechart/scale/
  unstretch/numbers` + python-pptx cho phần dựng lại).
- `inputs/plan.json` — kế hoạch chuyển động.
- `inputs/evidence.py` — script bằng chứng (rechart giữ animation, numbers có/không đủ, COM, scale).
- `preview/before-look/`, `preview/after-look/` — ảnh PowerPoint gốc và bản mới; `preview/
  inventory-*.txt`, `preview/verification.txt`.

## Giới hạn

- **Không mù hoàn toàn** (đã đọc REPORT/PR của T093 trước khi làm; không mở bản sau/harmonize.py/
  plan.json trước khi xong). Đã nói ở trên.
- Bộ gốc là dữ liệu giả lập do T093 dựng; kết quả nói về quy trình, không nói về nội dung QCC thật.
- Tôi giữ khổ 13,33 × 7,50 in của bộ gốc; nếu đích là deck QCC thật (20 × 11,25 in) phải dựng lại theo
  khổ đó — mục 10 chưa nói gì về việc này.
- Chưa quay video Morph/transition; bằng chứng PowerPoint là mở file + đọc transition/hiệu ứng qua COM
  (bậc 4), chưa xem playback từng khung (bậc 5).
- Bốn câu hỏi trên chưa có câu trả lời của chủ dự án; các lựa chọn hiện tại là của tôi.
