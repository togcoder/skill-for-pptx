# T101 [pptx] Dựng lại bố cục một slide như người thiết kế: nhìn ảnh, mỗi yếu tố một việc, sắp bằng vùng

Agent: Claude (Fable 5.2), trưởng nhóm. Ngày: 2026-11-11. Gộp theo lời chủ dự án ("luôn merge luôn").

## Vì sao

Chủ dự án, sau khi cho model nhỏ chạy lại với T100: vấn đề lớn nhất là AI **kiểm bằng code, không kiểm bằng
ảnh**; AI **không được dạy nghĩa của từng yếu tố** trên slide nên cho vào những thứ vô nghĩa, có khi đánh
nhau; quy trình làm việc sai. Nội dung và tài nguyên đã có, chỉ cần đưa vào theme và sắp lại cho chuyên
nghiệp mà vẫn không làm được. Câu hỏi: nếu là trưởng nhóm thì quy trình thế nào.

Trả lời bằng cách làm thật một slide của bộ QCC (file ngoài repo), rồi ghi đúng quy trình đã làm vào skill.

## Đã làm

**Lời hướng dẫn: mục 14 mới** (`skills/pptx/guides/14-dung-lai-bo-cuc-mot-slide.md`):

- bốn lý do việc "chỉ sắp lại" vẫn hỏng: gộp ba việc làm một; đặt tọa độ mà không nhìn; kiểm bằng lệnh đếm;
  coi theme là đồ để thêm vào;
- **luật gốc: mỗi yếu tố một việc** (luận điểm, bằng chứng, nhãn, dẫn mắt, cách làm, vỏ, trang trí), ba phép
  thử (bỏ đi có mất gì; hai thứ cùng việc; hai thứ tranh nhau), danh sách những thứ agent hay tự thêm;
- bảy bước cho **một** slide: nhìn slide gốc, viết sổ vai trò, xếp hạng, chọn dáng theo loại ý và viết bố
  cục bằng vùng, xuất ảnh và viết ba điều tệ nhất, sửa tối đa ba vòng, đặt cạnh slide gốc;
- "nhìn là nhìn gì": bảy câu hỏi theo thứ tự;
- "đã nhìn" phải chứng minh được; model không đọc được ảnh phải nói ngay và không nhận việc dựng lại bố cục.

SKILL.md: điều 12 (thêm thứ không có việc) và 13 (kiểm bằng lệnh thay cho mắt); lối vào mục 14. Mục 8, 9,
13 trỏ tới.

**Đồ nghề** (`scripts/pptx_tools.py`; việc chữ không làm được, D011):

- **`arrange DECK SLIDE LAYOUT.json`**: sắp vật thể của một slide bằng vùng (hàng, cột, phần chia, ô trống
  có chủ ý, khối các vật đi cùng nhau). Ảnh và khối co vừa ô không méo, giữ mã và hiệu ứng; chữ trong khối
  không bị phóng to; ô chữ lấy bề ngang của ô. Agent không phải tính tọa độ.
- **Mã nhìn**: mọi ảnh `glance` và `compare` xuất ra có một dải dưới ảnh mang mã ba ký tự ngẫu nhiên; mã chỉ
  có trong ảnh (file đi kèm chỉ giữ bản băm có muối). **`seen FOLDER N=CODE…`** kiểm các mã agent đọc được.

## Bằng chứng

Slide 13 của bộ QCC thật, dựng lại bằng đúng bảy bước, ba vòng (script `_scratch/t100/slide13_relayout.py`
trong thư mục dự án):

| Vòng | `glance` | Mắt thấy |
|---|---|---|
| 1 | 0 lỗi | dải trống trên và dưới bằng chứng; một chú thích đè lên ảnh bên cạnh; ảnh phụ và chữ của nó bị phóng to |
| 2 | 0 lỗi | chú thích xuống hai dòng, cắt qua vạch chân trang; ảnh phụ nằm đè lên hình trang trí của theme |
| 3 | 0 lỗi | sạch |

Năm lỗi, cả năm chỉ thấy khi mở ảnh; lệnh đo báo "0 lỗi" cả ba lần. Không vật nào của slide gốc bị mất,
không vật nào được thêm. Mã nhìn đọc trên ảnh vòng 3 được `seen` xác nhận; một mã đoán thì không.

`pytest`: 3 test mới (chia ô theo phần; `arrange` giữ dấu trên ảnh, không méo, không phóng chữ; mã nhìn chỉ
được công nhận khi đúng). Test PowerPoint thật kiểm thêm dải mã trên ảnh cặp. Bậc 5b cho ví dụ slide 13.

## Kết quả âm tính và giới hạn

1. **Mới một slide thật.** Chưa có đợt 2–3 slide mẫu được chủ dự án duyệt; chưa model nhỏ nào làm theo mục
   14.
2. **Mã nhìn chứng minh ảnh đã được mở, không chứng minh đã nhìn kỹ.** Một agent có thể đọc mã rồi bỏ qua
   slide. Dòng "đã thấy gì" mới là thứ người dùng đối chiếu được.
3. **Model không có mắt thì mục 14 không cứu được.** Chưa kiểm được model nhỏ đang dùng có thật sự đọc ảnh
   hay không; đây là câu hỏi mở cho chủ dự án.
4. `ungroup` từ chối nhóm của slide 13 (vật xoay trong nhóm bị kéo không đều). Ví dụ phải nhờ PowerPoint tách
   nhóm. Cần cho `ungroup` một đường lùi qua PowerPoint.
5. `arrange` không tách được chú thích khỏi ảnh khi chúng nằm trong cùng một nhóm; không tự căn mép giữa
   các ô khác hàng.
6. Bảng dáng theo loại ý có năm dòng, rút từ bộ QCC; chưa thử trên loại bộ khác.

## Việc tiếp theo

- Chủ dự án cho biết model nhỏ có đọc được ảnh không; nếu không, model đó chỉ làm mức 1.
- 2–3 slide mẫu mức 2 của bộ QCC theo mục 14, chủ dự án duyệt.
- `ungroup` lùi qua PowerPoint khi phép tính của nó từ chối.
