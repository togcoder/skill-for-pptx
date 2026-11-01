"""Generate the T045 rich-report spec and a VectorCraft cover asset.

This script is part of the T045 fixture, not the product generator.  It writes
the synthetic report data + a cover SVG, then asks VectorCraft to rasterise the
SVG (the cross-craft step recorded in the report).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
VECTORCRAFT = Path(r"D:\artcraft\VectorCraft\vectorcraft-cli.exe")


def cover_svg() -> Path:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="520" viewBox="0 0 1400 520">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#123B5C"/>
      <stop offset="0.55" stop-color="#1F4E79"/>
      <stop offset="1" stop-color="#2E75B6"/>
    </linearGradient>
    <linearGradient id="warm" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#C55A11"/>
      <stop offset="1" stop-color="#ED7D31"/>
    </linearGradient>
  </defs>
  <rect width="1400" height="520" fill="url(#g)"/>
  <circle cx="1180" cy="90" r="210" fill="#2E75B6" opacity="0.28"/>
  <circle cx="1240" cy="430" r="160" fill="#C55A11" opacity="0.30"/>
  <path d="M0 440 C 260 340, 520 500, 780 400 S 1180 300, 1400 380 L1400 520 L0 520 Z" fill="#0B2A42" opacity="0.55"/>
  <g stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="2">
    <path d="M80 60 H1320"/><path d="M80 96 H1320"/><path d="M80 132 H1320"/>
  </g>
  <rect x="80" y="170" width="120" height="8" fill="url(#warm)"/>
  <text x="990" y="300" font-family="Arial, sans-serif" font-size="130" font-weight="700" fill="#FFFFFF" opacity="0.14" text-anchor="middle">2026</text>
  <text x="80" y="430" font-family="Arial, sans-serif" font-size="22" fill="#BDD7EE">Văn phòng Chương trình · DX-2026-001</text>
</svg>"""
    path = HERE / "cover.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def make_assets() -> dict:
    svg = cover_svg()
    png = HERE / "cover.png"
    if VECTORCRAFT.is_file():
        subprocess.run([str(VECTORCRAFT), "convert", str(svg), str(png), "--scale", "1"],
                       check=True, capture_output=True, text=True)
    # Small icon-like images for the image table: use simple SVG squares.
    icons = []
    for i, color in enumerate(["#1F4E79", "#2E75B6", "#548235", "#C55A11"], start=1):
        s = f'<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160"><rect width="160" height="160" rx="24" fill="{color}"/><circle cx="80" cy="80" r="38" fill="#FFFFFF" opacity="0.85"/></svg>'
        sp = HERE / f"icon-{i}.svg"
        sp.write_text(s, encoding="utf-8")
        pp = HERE / f"icon-{i}.png"
        if VECTORCRAFT.is_file():
            subprocess.run([str(VECTORCRAFT), "convert", str(sp), str(pp), "--scale", "1"],
                           check=True, capture_output=True, text=True)
        icons.append(str(pp))
    return {"cover": str(png), "icons": icons}


def build_spec(assets: dict) -> Path:
    spec = {
        "meta": {
            "title": "Báo cáo thường niên 2026",
            "subtitle": "Chuyển đổi số và năng lực dữ liệu",
            "author": "Nhóm Nghiên cứu và Chuyển đổi số",
            "organization": "Văn phòng Chương trình",
            "document_id": "DX-2026-001",
            "version": "1.0",
            "date": "2026-11-01",
            "language": "vi-VN",
            "classification": "Nội bộ",
            "keywords": ["dữ liệu", "chuyển đổi số", "thường niên"],
        },
        "cover": {
            "enabled": True,
            "hero_image": assets["cover"],
            "hero_alt": "Dải màu xanh navy với vòng tròn cam và tiêu đề báo cáo thường niên.",
            "hero_height_mm": 62,
        },
        "front_matter": {
            "toc": {"enabled": True, "levels": 3, "title": "Mục lục"},
            "list_of_figures": {"enabled": True, "title": "Danh mục hình"},
            "list_of_tables": {"enabled": True, "title": "Danh mục bảng"},
            "abstract": {"enabled": True, "title": "Tóm tắt điều hành", "text": "Báo cáo tổng hợp kết quả chuyển đổi số năm 2026, tập trung vào chất lượng dữ liệu, năng lực phân tích và các quyết định dựa trên dữ liệu.\n\nBáo cáo sử dụng dữ liệu tổng hợp cho mục đích trình diễn kỹ thuật; không đại diện cho một tổ chức cụ thể.", "keywords": ["dữ liệu", "KPI", "quản trị"]},
        },
        "sections": [
            {
                "heading": "Tổng quan",
                "level": 1,
                "blocks": [
                    {"type": "paragraph", "text": "Năm 2026 đánh dấu bước chuyển từ thử nghiệm sang vận hành có đo lường. Báo cáo này trình bày kết quả theo ba trục: dữ liệu, năng lực và tác động."},
                    {"type": "key_values", "items": [
                        {"label": "Chỉ số tổng hợp", "value": "77/100"},
                        {"label": "Tăng trưởng", "value": "+11,6%"},
                        {"label": "Đơn vị tham gia", "value": "24"},
                    ]},
                    {"type": "callout", "title": "Thông điệp chính", "text": "Dữ liệu tốt không phải là dữ liệu nhiều; đó là dữ liệu được định nghĩa, kiểm soát và dùng đúng chỗ.", "fill": "EAF1F8"},
                ],
            },
            {
                "heading": "Kết quả và phương pháp",
                "level": 1,
                "blocks": [
                    {"type": "figure_text", "path": str(HERE / "cover.png"), "alt": "Dải màu thương hiệu của báo cáo.", "caption": "Bản sắc hình ảnh của báo cáo.", "heading": "Hình ảnh và dữ liệu", "text": "Mỗi hình được đặt cạnh phần diễn giải để người đọc không phải rời mắt khỏi lập luận.\n\nẢnh bìa được tạo bằng SVG và VectorCraft, sau đó nhúng vào DOCX ở chế độ inline để không bị trôi khi sửa nội dung.", "image_side": "left", "image_width_mm": 70, "source": "Nhóm thiết kế"},
                    {"type": "paragraph", "text": "Tốc độ tăng trưởng được mô tả bằng công thức:"},
                    {"type": "equation", "latex": r"g_t = \frac{Y_t - Y_{t-1}}{Y_{t-1}} \times 100", "caption": "Tốc độ tăng trưởng theo năm."},
                    {"type": "paragraph", "text": "Chỉ số tổng hợp dùng trung bình có trọng số:"},
                    {"type": "equation", "latex": r"S = \sum_{i=1}^{n} w_i x_i, \quad \sum_{i=1}^{n} w_i = 1", "number": False},
                ],
            },
            {
                "heading": "Bảng dữ liệu phức hợp",
                "level": 1,
                "blocks": [
                    {"type": "paragraph", "text": "Bảng dưới đây minh hoạ header nhiều tầng, gộp ô, ảnh trong ô và căn chỉnh theo từng cột."},
                    {"type": "table", "advanced": True, "caption": "Chỉ số theo đơn vị", "alt": "Bảng có header hai tầng, ảnh biểu tượng ở cột đầu và các chỉ số căn phải.", "columns": [
                        {"header": "Đơn vị", "width_mm": 42, "align": "left"},
                        {"header": "Dữ liệu", "width_mm": 36, "align": "right"},
                        {"header": "Năng lực", "width_mm": 36, "align": "right"},
                        {"header": "Tác động", "width_mm": 36, "align": "right"},
                    ], "header_rows": [
                        [{"text": "Đơn vị", "rowspan": 2, "align": "left"}, {"text": "Điểm thành phần", "colspan": 2, "align": "center"}, {"text": "Tác động", "rowspan": 2, "align": "center"}],
                        [{"text": "Dữ liệu", "align": "right"}, {"text": "Năng lực", "align": "right"}],
                    ], "rows": [
                        [{"image": assets["icons"][0], "width_mm": 12, "alt": "Biểu tượng đơn vị A"}, "81", "74", "68"],
                        [{"image": assets["icons"][1], "width_mm": 12, "alt": "Biểu tượng đơn vị B"}, "76", "79", "72"],
                        [{"image": assets["icons"][2], "width_mm": 12, "alt": "Biểu tượng đơn vị C"}, "70", "83", "77"],
                        [{"image": assets["icons"][3], "width_mm": 12, "alt": "Biểu tượng đơn vị D"}, "68", "88", "81"],
                    ], "row_heights_mm": [9, 8, 14, 14, 14, 14], "cell_margins_mm": 1.8, "zebra": True, "source": "Dữ liệu tổng hợp cho mục đích trình diễn."},
                ],
            },
            {
                "heading": "Kết luận",
                "level": 1,
                "blocks": [
                    {"type": "paragraph", "text": "Ba ưu tiên tiếp theo là chuẩn hoá dữ liệu chủ, tự động hoá kiểm tra chất lượng và đào tạo năng lực kể chuyện dữ liệu."},
                    {"type": "callout", "title": "Kiến nghị", "text": "Đo lường hàng quý, công bố minh bạch và giữ một nguồn dữ liệu chuẩn cho mọi báo cáo điều hành.", "fill": "FFF2E5"},
                ],
            },
        ],
        "references": {"enabled": True, "items": [
            {"key": "iso690", "label": "[1]", "text": "ISO. 2021. ISO 690:2021 Information and documentation — Guidelines for bibliographic references and citations to information resources."},
            {"key": "wcag", "label": "[2]", "text": "W3C. 2023. Web Content Accessibility Guidelines (WCAG) 2.2. W3C Recommendation."},
        ]},
        "appendix": [{
            "letter": "A",
            "title": "Dữ liệu nguồn",
            "blocks": [
                {"type": "paragraph", "text": "Bảng nguồn được giữ tách khỏi phần diễn giải để thuận tiện đối chiếu."},
                {"type": "table", "caption": "Dữ liệu nguồn theo quý", "columns": [
                    {"header": "Quý", "width_mm": 30}, {"header": "Giá trị", "width_mm": 30, "align": "right"}, {"header": "Ghi chú", "width_mm": 95}
                ], "rows": [["Q1", "70", "Khởi động"], ["Q2", "74", "Ổn định"], ["Q3", "77", "Tăng tốc"], ["Q4", "81", "Kiểm chứng"]], "source": "Dữ liệu tổng hợp."},
            ],
        }],
    }
    path = HERE / "annual_report_spec.json"
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    assets = make_assets()
    path = build_spec(assets)
    print(path)
