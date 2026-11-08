# T095 [pptx] Sửa mục 10 và đồ nghề theo diễn tập của DSH (T094)

Agent: Claude (Opus 5.5), trưởng nhóm. Ngày: 2026-11-09.

## Vì sao

Chủ dự án mở bản đồng bộ của DSH (T094): chuyển động ngang hoặc khá hơn bản của trưởng nhóm, nhưng
**sơ đồ xương cá bị vẽ lại đến mức không nhận ra** (chỉ còn một nửa, nhãn lơ lửng không bám xương,
xương nghiêng ngược, mất mũi tên chạy dọc xương sống). Trưởng nhóm tìm ra ba nguyên nhân nằm ở hướng
dẫn và đồ nghề, không chỉ ở DSH:

1. Mục 10 xếp "bố cục" vào phần được đổi mà không nói hình dạng của sơ đồ chuẩn là phần phải giữ.
2. Câu cảnh báo của `scale` khi chữ dưới 18 pt nói "rework the layout"; lời hướng dẫn nói khác, nhưng
   câu trên màn hình mạnh hơn.
3. Mục 9 dạy viết notes theo mẫu `[T=0]/[CLICK n]`, mục 10 nói notes là của tác giả. DSH viết lại
   notes cả bộ, và câu "mũi tên vàng chạy tới vấn đề" mất vật của nó.

Cộng thêm hai lỗi DSH tìm ra trong đồ nghề (review `research/reviews/T093-dsh-20261108.md`, R1, R2), và
lỗi "slide mở ra chỉ có tiêu đề" có ở cả hai bản.

## Đã sửa

**Lời hướng dẫn** (`skills/pptx/guides/10-dong-bo-slide-co-san.md`, `9-do-nghe.md`):

- Bảng ruột/vỏ: thêm **hình dạng của sơ đồ chuẩn** (xương cá, PDCA, Pareto, Gantt, cây lỗi, lưu đồ),
  speaker notes **và mọi vật notes nhắc tới**, khổ slide vào phần giữ; viết hoa/thường và cỡ/màu/nét
  của sơ đồ vào phần đổi được.
- Đoạn "Sơ đồ chuẩn đọc theo quy ước": được thu, đổi màu, nhích nhãn; không vẽ sang dạng khác, không
  bỏ một nửa, không tách nhãn khỏi nhánh. Đổi dạng là "Làm lại" và phải hỏi.
- `scale` báo chữ dưới 18 pt: giữ hình, đặt chữ về 18 pt, nới khung chữ; vẫn không vừa thì tách sơ đồ
  ra hai slide. Không bao giờ vẽ lại thành dạng khác. (Đề nghị số 3 của DSH, "dừng thu và dựng lại bố
  cục", **không** được nhận vì chính hướng đó làm hỏng xương cá.)
- Notes: giữ câu của tác giả, chỉ thêm nhãn `[CLICK n]`.
- "Thêm ý" có ví dụ ("… và duy trì kết quả").
- Chuyển động: slide làm lại thì viết nhịp bấm từ bảng ý; nhịp "số liệu có sẵn, kết luận hiện khi bấm"
  (lấy từ bản của DSH); **slide không được mở ra trắng**.
- Các chỗ mơ hồ DSH nêu: giữ khổ slide (1), hoa/thường và số thứ tự tiêu đề (2), màu chính lấy từ
  dòng `fills` (5), font theme (6), tiêu đề và cỡ chữ phụ lục, thêm phụ lục ở cuối (4, 7, 11), nhịp bấm
  slide làm lại (8), `numbers` là điều kiện cần (9), notes (10), mẫu câu hỏi bàn giao (12).

**Đồ nghề** (`scripts/pptx_tools.py`):

- `inventory` in **tên thật** của font theme (trước đó in "(theme body)"), thêm dòng **fills** (màu nền
  và màu khối), và báo **slide mở ra chỉ thấy tiêu đề**.
- `numbers` tách "2%" khỏi "2", và báo số **xuất hiện ít lần hơn** bản gốc. Ví dụ của DSH ("mục tiêu
  2%" mất, "2 lần" còn) giờ bị bắt nếu "2%" xuất hiện ít hơn.
- `scale`: câu cảnh báo mới; lỗi placeholder nói cách làm.
- 3 test mới (12/12): tên font theme + fills + slide mở trắng; "2%" khác "2" và đếm số lần; `unstretch`
  với ảnh đã cắt sẵn (R6).

**Không sửa:** R3 của DSH (vật trong nhóm tràn ra ngoài không được báo). Khung của một nhóm luôn bao
các vật con, và tọa độ vật con tính trong hệ của nhóm; kiểm khung nhóm là đủ.

## Bằng chứng

`preview/inventory-three-decks.txt`: `inventory` và `numbers` mới chạy trên bản gốc, bản T093 và bản
T094.

| | Font (tên thật) | Slide mở ra chỉ thấy tiêu đề | Số bị mất |
|---|---|---|---|
| Bản gốc chắp vá | Arial, Tahoma, Calibri (theme), Times New Roman | 1, 2, 4, 7, 10 | — |
| T093 (Claude) | Segoe UI | **4, 7** | 0 |
| T094 (DSH) | Century Gothic | **2, 6, 7** | 0 |

Cả hai bản đều có slide mở ra trắng; lệnh mới bắt được cả hai. Bản T093 không được sửa lại: nó là bản
ghi của lần diễn tập.

`pytest`: toàn bộ test qua. Bậc bằng chứng: 1 (cấu trúc). Chưa có lần chạy lại của một model khác trên
hướng dẫn mới.

## Việc tiếp theo

Khi chủ dự án nhận bộ slide thật của đồng nghiệp: agent đi theo mục 10 bản này, dùng `inventory` trước
tiên, và gửi danh sách "Cần bạn quyết" trước khi làm những slide "Làm lại".
