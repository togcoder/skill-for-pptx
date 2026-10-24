# Kiểm chứng chuyển động

## Các mức bằng chứng

| Mức | Ý nghĩa | Không chứng minh |
|---|---|---|
| planned | Kế hoạch được checker chấp nhận | File PPTX đã tồn tại |
| structure_checked | ZIP/XML và điều kiện được checker hỗ trợ đã kiểm tra | Toàn bộ OOXML hợp lệ hoặc PowerPoint mở không lỗi |
| layout_reviewed | Đã xem ảnh render của mọi slide | Animation hoặc Morph đã chạy |
| playback_verified | Đã mở và chạy trên PowerPoint được ghi rõ | Tương thích với mọi phiên bản hoặc hệ điều hành |

Inspector trong repo không phải trình xác thực schema OOXML đầy đủ. Nếu một tính năng không được kiểm tra thì giữ trạng thái chưa kiểm chứng.

## Phiên chạy nghiệm thu

1. Ghi SHA-256 của PPTX, hệ điều hành, tên ứng dụng, phiên bản/build, font và kích thước màn hình.
2. Mở bản chính xác có hash đó. Ghi cảnh báo repair, thiếu font, media hoặc external link.
3. Kiểm tra Selection Pane và tên đối tượng liên tục.
4. Chạy từng chuyển tiếp trong Slide Show. Kiểm tra nguồn, đích, thứ tự, đường chuyển động, nhịp và phần đọc được.
5. Kiểm tra đối tượng không nhảy, biến mất hoặc cross-fade ngoài ý đồ. Với biểu đồ native phải ghi nhận giới hạn Morph.
6. Thử sửa chữ và đổi một dữ liệu để xem cấu trúc có còn dùng được.
7. Xuất video bằng PowerPoint hoặc ghi màn hình. Lưu file bằng chứng cùng báo cáo, đánh dấu cách thu.
8. So sánh các mốc trước, giữa và sau chuyển tiếp. Ảnh từng slide chỉ kiểm tra trạng thái cuối.
9. Chạy lại trên máy trình chiếu đích nếu khác môi trường đã thử.

## Mẫu báo cáo

```json
{
  "experiment": "E01",
  "pptx_sha256": null,
  "application": null,
  "version": null,
  "os": null,
  "structure_checked": false,
  "layout_reviewed": false,
  "playback_verified": false,
  "repair_warning": "not_checked",
  "evidence_files": [],
  "limitations": ["PowerPoint playback has not been tested"]
}
```

