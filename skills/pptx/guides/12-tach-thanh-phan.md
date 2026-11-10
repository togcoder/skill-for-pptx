# 12. Tách thành phần để tái dùng

Dùng mục này khi một bộ slide **đã có** những khung hình đáng giữ — sơ đồ xương cá, thanh 9 bước, Gantt, bảng
PDCA, icon, khung so sánh — và bạn muốn **tách chúng ra thành một "viên" (component) độc lập** để agent khác
dán vào bộ mới, thay vì mỗi người vẽ lại một kiểu.

Đây là việc của **thành phần**, không phải của cả slide. Mục 10 (đồng bộ bộ có sẵn) và mục 11 (dựng lại cả bộ)
vẫn giữ nguyên luật "ruột là chữ/số/ý/ảnh bằng chứng". Mục này thêm một câu hỏi trước khi vẽ: **khung này đã có
trong bộ cũ chưa, và nó có tách ra được không?**

## Trước khi tách: biết nó là loại gì

Ba loại, ba cách:

| Trong bộ cũ, thành phần là | Cách tách | Lệnh |
|---|---|---|
| **Nhóm hình PowerPoint** (`p:grpSp`) | làm phẳng nhóm, rồi tách | `ungroup` |
| **Nhiều hình rời** (xương cá vẽ tay, Gantt ghép bằng đường + chữ) | chọn theo tên, bỏ nền/chrome, cắt viền | `component` |
| **Một ảnh** (khung vẽ sẵn trên nền trắng, logo, icon) | tách nền ảnh | `cutout` (mục 10) |

`extract` (mục 11) chỉ lấy **file ảnh/video gốc + manifest**; nó **không** lấy hình vector. Vì vậy một xương cá
vẽ bằng 40 hình rời trên một ảnh nền sẽ **không** xuất hiện trong `extract/media/` — đây là lỗi thường gặp khi
tưởng "đã bóc tách" là đã có thành phần.

## Quy trình

### 1. Kiểm kê thành phần

```
python scripts/pptx_tools.py components "bo-cu.pptx" --slide 29
```

In ra từng hình cấp cao: tên, loại, khung, và cờ:

- `group of N` — nhóm, tách được bằng `ungroup`;
- `covers the slide: background` — ảnh nền (bỏ khi tách; lệnh tự bỏ nếu nằm sát mép);
- `chrome (usually excluded)` — tên bắt đầu `!!`, `Logo`, `Title`, `Footer`, `Page number`;
- `chart: rebuild with rechart` — không tách được thành hình;
- `table` — tách được (bảng là XML thuần);
- `video/audio: copy the slide` — không tách được.

**Lưu ý:** ảnh nền không sát mép (ví dụ đặt từ y=92) có thể không bị `component` tự nhận là nền. Khi đó
`--exclude` đúng tên của nó.

### 2. Tách

```
python scripts/pptx_tools.py component "bo-cu.pptx" 29 \
    --exclude "Picture 85" --exclude "TextBox 17" --exclude "Group 60" \
    --freeze --margin 30 --manifest "assets/components/fishbone.manifest.json" \
    --png "assets/components/preview/fishbone.png" -o "assets/components/fishbone.pptx"
```

Kết quả là một file `.pptx` **một slide**, đã cắt đúng khung thành phần + lề, nền trong suốt:

- `--name` (lặp lại) chọn đúng hình cần lấy; bỏ trống = lấy mọi hình cấp cao trừ nền;
- `--exclude` (lặp lại) bỏ hình theo tên — dùng cho nền không sát mép, tiêu đề, thanh bước;
- `--exclude-chrome` bỏ nhanh các tên `!!`, `Logo`, `Title`, `Footer`, `Page number`;
- `--freeze` **đóng băng theme** (đổi `schemeClr` → `srgbClr`, font theme → tên font thật) để dán vào bộ có theme
  khác vẫn giữ màu/font; không có `--freeze` thì thành phần theo theme của bộ nhận;
- `--ungroup` làm phẳng các nhóm trong thành phần; `--margin` px; `--png` ảnh xem trước đúng tỉ lệ;
- `--manifest` ghi JSON: nguồn (bộ/số slide), tên hình, số hình, khung, đã đóng băng, đã bỏ gì.

Nếu thành phần nằm trong **nhóm**, tách cả nhóm trước (giữ hiệu ứng) rồi mới tách thành phần:

```
python scripts/pptx_tools.py ungroup "bo-cu.pptx" 15 --name "Fishbone frame" -o "bo-cu-ungrouped.pptx"
```

`ungroup` tự map toạ độ con (kể cả nhóm bị scale/rotate), giữ thứ tự z. Nó **từ chối** nhóm có animation (timing
trỏ vào id nhóm) — cắt nhóm đó sẽ mất hiệu ứng; khi đó tách cả nhóm làm component, đừng phá nhóm. Nó cũng từ chối
nhóm vừa mirror vừa rotate hoặc vừa rotate vừa scale không đều (không biểu diễn được bằng shape thường) — mở
PowerPoint ungroup tay, hoặc tách cả nhóm.

### 3. Dùng lại

```
python scripts/pptx_tools.py place "assets/components/fishbone.pptx" "bo-moi.pptx" --slide 4 --at 1.6,1.0 -o "bo-moi-co-xuong-ca.pptx"
```

`place` chép hình (giữ tên, chữ sửa được, ảnh giữ crop), đặt góc trên trái ở `--at` inch. Nó **không** tự thu
phóng — thành phần có kích thước cố định; muốn khác cỡ thì thiết kế lại khung hoặc dùng `scale` sau khi dán.

Trong PowerPoint, cách khác: mở file component, `Ctrl+A` trong slide, copy, dán vào slide đích. Cách này cũng
giữ chữ sửa được.

## Viên thành phần đặt ở đâu

- Thư mục dùng chung của dự án: `assets/components/` (file `.pptx`, `.manifest.json`, `preview/*.png`).
- Tên viên = việc nó làm, không phải số slide: `fishbone_ver34`, `stepbar_ver5`, `gantt_ver5`.
- Manifest phải ghi **nguồn** (bộ nào, slide nào) và **giấy phép/ghi công** nếu là ảnh/logo. Không đưa file mật
  của khách ra ngoài thư mục dự án.
- Một viên đã `--freeze` thì màu/font cố định — đúng cho nhận diện; nếu muốn viên theo theme bộ nhận thì tách
  không freeze.

## Kiểm trước khi coi là xong

1. Mở file component bằng PowerPoint (hoặc `look`): đúng khung, không dính nền, không mất chữ, không còn mảnh
   chrome (logo/tiêu đề/thanh bước) lẫn vào.
2. Xem **trên nền sáng và nền tối**: chữ trắng của bản gốc có thể vô hình trên nền sáng — đây là lỗi hay gặp;
   đặt trên nền đúng như bản gốc hoặc đổi màu chữ khi dùng.
3. `place` thử vào một slide trống của bộ đích: hình đúng thứ tự, chữ sửa được, ảnh không mất crop.
4. Manifest khớp: đúng slide nguồn, đúng số hình đã lấy.

## Giới hạn (đọc trước khi hứa)

- **Không mang animation.** Component là hình tĩnh; hiệu ứng của nhóm/bản gốc không đi theo. Slide mô phỏng
  (mục 10) phải copy cả slide, không tách.
- **Chart, SmartArt, video/audio** không tách được: chart dựng lại bằng `rechart`, SmartArt/video copy cả slide.
- **Nhóm đang có animation**: không `ungroup`; tách cả nhóm.
- **Nhóm vừa rotate vừa scale không đều / vừa mirror vừa rotate**: `ungroup` từ chối — mở PowerPoint làm tay.
- **`place` không scale chữ**; đặt sai cỡ thì quay lại thiết kế viên ở cỡ đúng.
- **Không cắt ảnh chụp màn hình** một khung vector rồi gọi là component: mờ, mất chữ, không sửa được, không
  animate. Nếu chỉ có ảnh chụp và nền phức tạp, xin file gốc; hoặc vẽ lại đúng dạng trong PowerPoint.
- Màu/font đã `--freeze` thì không theo theme bộ nhận; chủ ý chọn một trong hai.

## Ví dụ thật (QCC, 2026-11-10)

- Bộ `QCC - SHARP Team Ver3-4.pptx`, slide 29: xương cá là **40 hình rời** (không phải một group) nằm trên
  **một ảnh nền full-slide** `Picture 85`; tiêu đề `TextBox 17`, thanh bước `Group 60`. Tách 37 hình còn lại
  → `fishbone_ver34.pptx` (16,09 × 9,03 in), đã freeze theme.
- Bộ Ver5 mẫu, slide 2: xương cá **64 hình rời**, nền `!!bg`, chrome `!!step*`, `!!badge`, `!!chapno`, car, logo,
  tiêu đề, footer → `--exclude-chrome` + tự bỏ nền → `fishbone_ver5.pptx` (15,54 × 9,19 in).
- Thanh 9 bước cùng slide: 10 hình (`!!step1..9` + xe) → `stepbar_ver5.pptx` (9,16 × 1,0 in).
- Đã thử `place` xương cá vào một slide tối của bộ khác: 37 hình, chữ trắng hiện đúng, chữ vẫn sửa được.
