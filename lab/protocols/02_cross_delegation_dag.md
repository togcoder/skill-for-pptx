# Protocol 02: Cross-Delegation DAG & Anti-Loop Protocol

> **Mục tiêu:** Cho phép 13 Agent chuyên trách của hệ sinh thái ArtCraft giao việc chéo cho nhau
> một cách khoa học, đồng thời triệt tiêu nguy cơ "vòng lặp phản biện vô tận" (Infinite Loop).

---

## 1. Nguyên tắc "Không làm việc trái sở trường"

Mỗi Agent đại diện cho một phân hệ ArtCraft chỉ tập trung vào thế mạnh cốt lõi của mình:
* **DeckCraft Agent:** Chuyên trách bố cục slide, timeline, click-beat, morph chuyển cảnh. Không tự vẽ vector phức tạp hay tính công thức tài chính.
* **VectorCraft Agent:** Chuyên trách vẽ vector, biểu tượng, sơ đồ mặt cắt, đường cong Bézier.
* **GridCraft Agent:** Chuyên trách bảng tính, công thức kế toán, phân tích thống kê và đồ thị dữ liệu Tufte.
* **WordCraft Agent:** Chuyên trách dàn trang tài liệu dài, mục lục, trích dẫn học thuật, typographic rhythm.
* **PhotoCraft / LightCraft Agent:** Chuyên trách xử lý ảnh raster, cân chỉnh màu sắc, tách nền sản phẩm.

---

## 2. Giao thức Hợp đồng Bắt buộc (`HandoffContract`)

Khi Agent A cần tài nguyên từ Agent B, Agent A **không được chat tự do**, mà phải phát hành một **`HandoffContract`** (tuân thủ `lab/schemas/handoff_contract.schema.json`):

```json
{
  "contract_id": "DEL-20261101-001",
  "intent_id": "INT-20261101-001",
  "from_craft": "deckcraft",
  "to_craft": "vectorcraft",
  "requested_asset": {
    "kind": "svg_diagram",
    "spec": {"type": "server_cluster_topology", "nodes": 4, "viewBox": "0 0 800 600"}
  },
  "constraints": {
    "palette_hex": ["#1A1A24", "#3D5AFE", "#F4F5F8"],
    "stroke_width_px": 2.0,
    "bounding_box": [120, 160, 480, 320]
  },
  "delivery": {
    "expected_format": "svg",
    "target_path": "build/assets/cluster_diagram.svg"
  },
  "iteration_count": 0,
  "max_iterations": 2
}
```

---

## 3. Khống chế Vòng lặp: Quy tắc `Max-Iterations = 2`

Để tránh tình trạng 2 Agent cãi nhau qua lại về màu sắc hay kích thước:
1. **Lần 1:** Agent A giao việc $\rightarrow$ Agent B giao sản phẩm $\rightarrow$ Agent A duyệt hoặc yêu cầu chỉnh sửa 1 lần duy nhất kèm số đo cụ thể.
2. **Lần 2:** Agent B giao bản sửa đổi cuối cùng.
3. **Chốt chặn:** Nếu sau 2 lần mà Agent A vẫn chưa ưng ý:
   - Nghiêm cấm vòng lặp thứ 3.
   - Trọng tài (Art Director Orchestrator hoặc Con người) sẽ can thiệp và chốt quyết định cuối cùng theo nguyên tắc `design_system.json`.
