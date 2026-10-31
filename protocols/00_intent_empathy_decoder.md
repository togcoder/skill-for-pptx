# Protocol 00: Intent & Empathy Decoder

> **Mục tiêu:** Dạy cho AI Agent cách giải mã và thấu hiểu con người (người dùng & khán giả mục tiêu)
> đằng sau một câu lệnh ngắn, trước khi chạm vào bất kỳ dòng lệnh hay công cụ nào.

---

## 1. Nguyên lý Thấu hiểu Con người (Human-First Design)

Người dùng thường chỉ gõ một prompt ngắn 1–2 câu (ví dụ: *"Tạo slide báo cáo tài chính quý 3"* hoặc *"Vẽ sơ đồ luồng dữ liệu cho ban giám đốc"*).
AI thông thường sẽ lập tức chọn bừa template và nhồi nhét bullet point.

**Protocol 00 bắt buộc Agent phải dừng lại ở Tầng 0 và giải mã 5 thông số:**

### 1.1 Archetype Khán giả (Audience Persona)
Mỗi đối tượng người nghe có một "bộ lọc tâm lý" khác nhau:
* **Ban Giám đốc (C-Level / Executives):**
  - *Tâm lý:* Thiếu thời gian, quan tâm đến kết quả cuối cùng và rủi ro.
  - *Nguyên tắc:* Áp dụng Kim tự tháp Minto (Minto Pyramid). Đưa kết luận / khuyến nghị hành động (Action Title) ngay dòng đầu tiên. Không dùng quá 3 khối nội dung.
* **Kỹ sư / Chuyên gia kỹ thuật (Engineers / Technical Leads):**
  - *Tâm lý:* Hoài nghi, cần bằng chứng, ghét trang trí rườm rà.
  - *Nguyên tắc:* Mọi số liệu phải có nguồn và đơn vị đo. Sơ đồ mạch lạc, tỉ lệ dữ liệu / mực cao (Edward Tufte High Data-Ink Ratio). Mức độ trang trí = 0.
* **Đại chúng / Khách hàng (General Audience / Customers):**
  - *Tâm lý:* Dễ xao nhãng, bị dẫn dắt bởi cảm xúc thị giác.
  - *Nguyên tắc:* Điểm tụ thị giác rõ ràng (One Hero Focal Point), màu sắc truyền cảm hứng, cấu trúc kể chuyện (Narrative Arc).

### 1.2 Ngân sách Nhận thức (Cognitive Load Budget)
Bộ não con người bị giới hạn bởi bộ nhớ ngắn hạn:
* **Luật Miller:** Tối đa $3 \pm 1$ cụm thông tin thị giác (Visual Chunks) trên một khung nhìn.
* **Luật Hick:** Càng nhiều lựa chọn/chi tiết thừa, thời gian xử lý càng lâu. Mọi slide hay tài liệu phải được thiết kế để khán giả nắm được ý chính trong vòng **dưới 3 giây**.
* **Đường quét mắt:** 
  - Slide/Poster: Quét theo chữ Z (**Z-Pattern**).
  - Tài liệu/Báo cáo chuyên sâu: Quét theo chữ F (**F-Pattern**).

### 1.3 Bối cảnh Trình bày Vật lý (Viewing Context)
* **Chiếu máy chiếu phòng họp sáng:** Cấm dùng nền xám nhạt chữ trắng hoặc font mỏng; font tối thiểu $18\text{ pt}$, độ tương phản tối thiểu $4.5:1$.
* **Màn hình cá nhân (Desktop / Laptop 4K):** Cho phép mật độ chi tiết cao hơn, font nhỏ nhất $12\text{ pt}$.
* **In ấn / Tài liệu đọc sau (A4 / Document):** Phân chia cột, lề tối thiểu $20\text{ mm}$, tối đa 75 ký tự mỗi dòng để chống mỏi mắt.

---

## 2. Quy trình Thực thi của Tầng 0

Mỗi khi nhận đề bài, Agent Orchestrator phải xuất ra một bản **`IntentBrief`** tuân thủ schema `schemas/intent_brief.schema.json`.

```text
Prompt Người dùng ──> [Protocol 00 Decoder] ──> intent_brief.json ──> Chuyển tiếp tới Orchestrator
```
Không Agent nào được phép sinh mã hoặc gọi CLI khi chưa có `intent_brief.json`.
