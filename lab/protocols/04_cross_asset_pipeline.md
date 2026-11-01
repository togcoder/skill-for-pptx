# Protocol 04: Cross-Asset Pipeline & Local Autonomy

> **Mục tiêu chính thức từ Project Owner (togcoder):**
> 1. Phát triển chéo (cross-domain) các kỹ năng cho Agentic AI: không chỉ tạo ra một tài nguyên đơn lẻ mà có thể tùy biến đa dạng, đáp ứng trọn vẹn nhu cầu người dùng.
> 2. Nâng trải nghiệm người dùng lên mức cao nhất: thấu hiểu sâu sắc người dùng muốn gì và tạo ra sản phẩm đúng ý nhất ngay từ lượt đầu, triệt tiêu việc phải tạo đi tạo lại nhiều lần.
> 3. Xâu chuỗi tiền xử lý đa công cụ: dùng công cụ chuyên biệt để tinh chỉnh tài nguyên (chỉnh/cắt/tách nền ảnh, chuẩn hóa âm thanh, dựng biểu đồ) trước khi lồng ghép chéo vào sản phẩm đích (slide, tài liệu, bảng tính, video).
> 4. Toàn quyền thực thi cục bộ & Tự do tài nguyên: Agent được phép tải bất kỳ tài nguyên, font chữ, mô hình, hoặc cài đặt thư viện code nào cần thiết, với điều kiện giữ môi trường gọn gàng và xóa tệp tạm thời sau khi hoàn tất.

---

## 1. Nguyên tắc "Không xuất xưởng tài nguyên thô" (Pre-Process Before Embedding)

Một sản phẩm thiết kế chuyên nghiệp không bao giờ là sự chắp vá các tệp thô chưa qua xử lý. Mọi Specialist Agent phải tuân thủ 3 đường ống (pipelines) tiền xử lý chuẩn:

### 1.1 Đường ống Hình ảnh (Visual / Raster Pipeline)
```
[Tạo ảnh AI / Tải ảnh mẫu]
         │
         ▼
[Công cụ Chỉnh ảnh chuyên biệt (Pillow / PhotoCraft / ImageMagick)]
 ├── Cắt cúp (crop) theo tỉ lệ khung nhìn đích (16:9, 4:5, 1:1)
 ├── Tách nền / Tạo mặt nạ kênh Alpha (Alpha mask) cho các chi tiết nổi
 ├── Cân chỉnh màu (Color grade / Kelvin) đồng bộ với tone nền (Canvas mode)
 └── Kiểm tra độ phân giải tối thiểu (>= 150 DPI cho in ấn / >= 1080p cho màn hình)
         │
         ▼
[Lồng ghép vào Slide PPTX / Tài liệu Word DOCX / Bảng tính Excel XLSX]
```

### 1.2 Đường ống Âm thanh & Chuyển động (Audio & Motion Pipeline)
```
[Bản ghi âm giọng đọc / Nhạc nền BGM]
         │
         ▼
[Công cụ Âm thanh chuyên biệt (SoundCraft / ffmpeg / pydub)]
 ├── Khử ồn (Noise Gate / High-pass filter ở 80Hz)
 ├── Chuẩn hóa âm lượng chuẩn phát sóng (EBU R128: -14.0 LUFS, True Peak <= -1.0 dBTP)
 └── Cấu hình Auto-ducking: Tự động hạ nhạc nền -14 dB khi có giọng thuyết minh
         │
         ▼
[Ghép vào Video (FilmCraft) hoặc Đồng bộ nhịp Click/Motion (DeckCraft)]
```

### 1.3 Đường ống Dữ liệu & Biểu đồ (Data & Chart Pipeline)
```
[Số liệu phân tích thô]
         │
         ▼
[Công cụ Bảng tính chuyên biệt (SheetCraft / GridCraft)]
 ├── Chuẩn hóa công thức và kiểm toán dữ liệu (Audit zero-error)
 ├── Tạo biểu đồ native chuẩn Edward Tufte (tối đa hóa data-ink ratio)
 └── Xuất bản đối tượng vector / XML có thể chỉnh sửa
         │
         ▼
[Nhúng vào Slide Báo cáo Ban Giám Đốc hoặc Báo cáo Thường niên Word]
```

---

## 2. Nguyên lý "Đúng ý ngay từ lượt đầu" (First-Pass Excellence)

Mục tiêu tối thượng của công cụ không phải là bắt người dùng phải làm lại nhiều lần. Để đạt được chất lượng chuẩn xác ngay từ lượt đầu:
1. **Giải mã bối cảnh (Context Decoding):** Phân tích rõ đối tượng thưởng thức (Ban giám đốc, kỹ sư, khách hàng đại chúng), không gian trình chiếu (máy chiếu sáng, laptop cá nhân, in ấn tài liệu).
2. **Đồng bộ xuyên suốt (Thematic Consistency):** Một bài thuyết trình, tài liệu hay video phải có cùng ngôn ngữ thiết kế (Design DNA): font chữ phân cấp âm nhạc, bảng màu 60-30-10 đạt chuẩn tương phản WCAG 2.1 AA/AAA, nền đa tầng composite.
3. **Cung cấp tùy chọn cấu hình linh hoạt (Parametric Adaptability):** Không bao giờ khóa cứng trong một preset tĩnh. Mọi công cụ phải nhận tham số nhu cầu của người dùng (`--need`, `--ref-deck`, `--tone`, `--custom-hue`) để tự động thích ứng.

---

## 3. Toàn quyền Cục bộ & Quy tắc Giữ gìn Vệ sinh Môi trường (Local Autonomy & Cleanliness Law)

Khi Agent đang làm việc cục bộ cho dự án này:
* **Tự do cài đặt & tải về:**
  - Được phép dùng `pip install`, `uv`, hoặc các trình quản lý gói để tải bất kỳ thư viện Python / JavaScript / hệ thống nào phục vụ chất lượng công việc.
  - Được phép tải các bộ font chữ tiêu chuẩn, mô hình cục bộ, file mẫu tham chiếu từ các nguồn tin cậy.
* **Quy tắc Giữ gìn Vệ sinh Không gian:**
  - Mọi tệp tải về tạm thời, file scratch hoặc cache phục vụ chạy thử bắt buộc phải đặt trong thư mục được `.gitignore` bảo vệ: `workspace/` hoặc thư mục scratch riêng của phiên làm việc.
  - Nghiêm cấm xả tệp rác vào thư mục gốc (`root`) của repository.
  - Sau khi hoàn thành tạo tác cuối cùng (artifact trong `experiments/<ID>/artifacts/`), phải chủ động dọn dẹp các tệp tạm thời không còn sử dụng.
  - Lệnh kiểm tra cấu trúc `python lab/tools/check_layout.py` bắt buộc phải báo `layout OK`.
