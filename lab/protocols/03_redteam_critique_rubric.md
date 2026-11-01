# Protocol 03: Red-Team Critique Rubric (Dual-Layer 100-Point Audit)

> **Mục tiêu:** Thiết lập cơ chế kiểm định độc lập, nghiêm khắc và lượng hóa được về mặt mỹ thuật
> và kỹ thuật, đảm bảo sản phẩm trước khi xuất xưởng đạt đẳng cấp studio chuyên nghiệp.

---

## 1. Cơ chế Thẩm định Kép (Dual-Layer Critique)

Mọi sản phẩm tạo tác bắt buộc phải đi qua 2 lớp thẩm định trước khi được cấp trạng thái `PASS`:

```
[Sản phẩm tạo tác]
        │
        ▼
[Lớp 3A: Deterministic Linter (Toán học)]
- Kiểm tra va chạm hộp (Bounding-box collision)
- Đo tỷ lệ tương phản chữ/nền WCAG 2.1
- Đo độ tràn viền (Overflow) và kích thước font tối thiểu
        │
        ▼ (Nếu Lớp 3A thông qua)
[Lớp 3B: Render-Before-Review (Thị giác & Nghệ thuật)]
- Gọi lệnh Native Render (DeckCraft / WordCraft render PNG)
- Red-Team Critic soi ảnh render thực tế
- Chấm Rubric 100 điểm
```

---

## 2. Bảng Rubric Thẩm định 100 Điểm

Sản phẩm chỉ được duyệt (**PASS**) khi:
- **Tổng điểm $\ge 85/100$**.
- **Không dính bất kỳ Điểm Liệt (Auto-Fail) nào**.

| Hạng mục Thẩm định | Điểm tối đa | Chuẩn Tham chiếu | Tiêu chí Đo lường Cụ thể | Điểm Liệt (Auto-Fail = 0đ) |
| :--- | :---: | :--- | :--- | :--- |
| **1. Thấu hiểu Ý định & Nhận thức** | 25 | Miller's Law, Minto Pyramid, Norman | Tiêu đề mang thông điệp hành động; mắt nhận diện ý chính trong $< 3\text{ s}$; đúng tông cảm xúc khán giả. | Nhồi nhét quá 5 cụm thông tin; tiêu đề vô nghĩa ("Báo cáo"). |
| **2. Lưới, Bố cục & Khoảng trắng** | 25 | Swiss Grid, IBM Carbon $2\times$ Grid ($8\text{ px}$) | Căn thẳng hàng trục lưới; tỷ lệ khoảng trắng (whitespace) $\ge 35\%$; cân bằng trọng lượng thị giác. | Hai phần tử đè lên nhau ngoài ý muốn; chữ tràn ra ngoài mép khung. |
| **3. Typography & Phân cấp** | 20 | Modular Scale ($1.25$ hoặc $1.333$) | Tối đa 2 họ font; tối đa 3 cấp cỡ chữ; độ dài dòng $45\text{–}75$ ký tự cho văn bản đọc. | Chữ vỡ dấu tiếng Việt; font mỏng/nhỏ dưới ngưỡng đọc của bối cảnh. |
| **4. Màu sắc & Tối giản** | 15 | Material 3, Dieter Rams, WCAG AA/AAA | Độ tương phản $\ge 4.5:1$ (chữ nhỏ) hoặc $\ge 3.0:1$ (chữ lớn); màu nhấn $\le 15\%$ diện tích. | Tương phản $< 3.0:1$ gây mù chữ; dùng quá 4 màu lung tung ngoài token. |
| **5. Kỷ luật Công cụ & Hệ sinh thái** | 15 | ArtCraft Native Architecture | Dùng đúng lệnh native của ArtCraft; giao việc đúng phân hệ chuyên trách. | Tự code Python vẽ hình/chắp vá file thô sơ khi CLI native đã hỗ trợ. |

---

## 3. Đầu ra của Báo cáo Thẩm định

Critic Agent phải xuất bản báo cáo tuân thủ `lab/schemas/critique_report.schema.json`.
Nếu bị **REJECT**, Critic phải chỉ rõ:
1. `issue_code` vi phạm.
2. `severity` (critical, warn, note).
3. `fix_instruction`: Hướng dẫn sửa chữa định lượng (ví dụ: *"Tăng padding lề trái thêm 16px, đổi màu chữ từ #777777 sang #1A1A24 để đạt tương phản 8.2:1"*).
4. `target_tool`: Công cụ cần thực thi việc sửa chữa.
