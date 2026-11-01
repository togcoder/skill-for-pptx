"""Author the T052 diagrams as SVG, then VectorCraft rasterises them.

The diagrams are inputs to the cross-asset pipeline: SVG -> VectorCraft PNG ->
Pillow trim/scale -> DOCX.  They are deliberately flat and technical, not
decorative.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "artifacts" / "figures"


def box(x, y, w, h, title, sub="", fill="#EAF1F8", stroke="#1F4E79", title_size=24):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" '
           f'stroke="{stroke}" stroke-width="2"/>']
    out.append(f'<text x="{x + w/2}" y="{y + (26 if sub else h/2 + 6)}" text-anchor="middle" '
               f'font-family="Arial" font-size="{title_size}" font-weight="bold" fill="#10243A">{title}</text>')
    if sub:
        out.append(f'<text x="{x + w/2}" y="{y + 50}" text-anchor="middle" '
                   f'font-family="Arial" font-size="17" fill="#44546A">{sub}</text>')
    return "\n".join(out)


def arrow(x1, y1, x2, y2, color="#1F4E79", dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="2.2" marker-end="url(#arrow)"{d}/>')


def architecture() -> str:
    W, H = 1480, 760
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" '
             'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#1F4E79"/></marker></defs>',
             '<rect width="100%" height="100%" fill="#FFFFFF"/>']
    parts.append('<text x="40" y="46" font-family="Arial" font-size="30" font-weight="bold" fill="#10243A">'
                 'Kiến trúc CNN–LSTM–Autoencoder có attention cho dữ liệu cảm biến</text>')
    # Training lane
    parts.append('<rect x="40" y="72" width="1400" height="96" rx="12" fill="#F7F9FC" stroke="#D6DEE8"/>')
    parts.append('<text x="60" y="102" font-family="Arial" font-size="18" font-weight="bold" fill="#44546A">'
                 'HUẤN LUYỆN (chỉ dữ liệu bình thường)</text>')
    parts.append(box(70, 112, 190, 44, "Cửa sổ 64×12", fill="#FFFFFF", title_size=19))
    parts.append(arrow(260, 134, 300, 134))
    parts.append(box(300, 112, 190, 44, "Tăng cường + nhiễu", fill="#FFFFFF", title_size=19))
    parts.append(arrow(490, 134, 530, 134))
    parts.append(box(530, 112, 220, 44, "QAT (fake-quant)", fill="#FFFFFF", title_size=19))
    parts.append(arrow(750, 134, 790, 134))
    parts.append(box(790, 112, 240, 44, "TFLite Micro int8", fill="#FFFFFF", title_size=19))
    parts.append('<text x="1060" y="138" font-family="Arial" font-size="17" fill="#44546A">'
                 '→ triển khai trên MCU</text>')
    # Inference lane
    y = 236
    labels = [
        ("Cửa sổ\n64×12", "đầu vào", 70, 170),
        ("Làm sạch", "missing + outlier", 270, 170),
        ("Chuẩn hóa", "z-score", 470, 170),
        ("CNN 1D", "64 filter, k=5", 670, 190),
        ("LSTM", "64 cell", 890, 150),
        ("Attention", "temporal", 1070, 170),
        ("z (24)", "latent", 1270, 120),
    ]
    for title, sub, x, w in labels:
        parts.append(box(x, y, w, 82, title.replace("\n", " "), sub, fill="#EAF1F8", title_size=20))
    for i in range(len(labels) - 1):
        x1 = labels[i][2] + labels[i][3]
        x2 = labels[i + 1][2]
        parts.append(arrow(x1 + 4, y + 41, x2 - 6, y + 41))
    # Decoder lane
    y2 = 390
    parts.append(box(1070, y2, 170, 82, "Decoder", "CNN transpose", fill="#EAF4E7", stroke="#548235", title_size=20))
    parts.append(box(860, y2, 180, 82, "Sai số tái tạo", "MSE theo đặc trưng", fill="#EAF4E7", stroke="#548235", title_size=19))
    parts.append(box(650, y2, 180, 82, "Mahalanobis", "khoảng cách latent", fill="#EAF4E7", stroke="#548235", title_size=19))
    parts.append(box(440, y2, 180, 82, "Hợp nhất điểm", "α·MSE + (1−α)·D", fill="#FFF2E5", stroke="#C55A11", title_size=19))
    parts.append(box(230, y2, 170, 82, "Ngưỡng", "μ + k·σ", fill="#FFF2E5", stroke="#C55A11", title_size=20))
    parts.append(box(40, y2, 160, 82, "Cảnh báo", "cổng + log", fill="#FCE4D6", stroke="#C00000", title_size=20))
    parts.append(arrow(1130, y2 + 41, 1042, y2 + 41, color="#548235"))
    parts.append(arrow(860, y2 + 41, 832, y2 + 41, color="#548235"))
    parts.append(arrow(650, y2 + 41, 622, y2 + 41, color="#C55A11"))
    parts.append(arrow(440, y2 + 41, 402, y2 + 41, color="#C55A11"))
    parts.append(arrow(230, y2 + 41, 202, y2 + 41, color="#C00000"))
    parts.append(arrow(1310, 318, 1240, 408, color="#1F4E79"))
    parts.append(arrow(1155, 318, 1155, 390, color="#548235"))
    # Legend / notes
    parts.append('<text x="70" y="540" font-family="Arial" font-size="17" fill="#44546A">'
                 'Luồng suy luận: cửa sổ trượt 64 bước, 12 kênh cảm biến; encoder nén xuống 24 chiều.</text>')
    parts.append('<text x="70" y="566" font-family="Arial" font-size="17" fill="#44546A">'
                 'Điểm bất thường = hợp nhất sai số tái tạo và khoảng cách Mahalanobis; ngưỡng hiệu chỉnh trên tập validation.</text>')
    parts.append('<text x="70" y="592" font-family="Arial" font-size="17" fill="#44546A">'
                 'QAT: lượng tử hóa int8 trong huấn luyện; đầu ra TFLite Micro chạy trên STM32H747 / ESP32-S3.</text>')
    # Footer
    parts.append('<line x1="40" y1="640" x2="1440" y2="640" stroke="#D6DEE8"/>')
    parts.append('<text x="40" y="672" font-family="Arial" font-size="15" fill="#7F7F7F">'
                 'Nguồn: tác giả thiết kế cho T052; hình vector do VectorCraft kết xuất.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def windowing() -> str:
    W, H = 1320, 520
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
             '<rect width="100%" height="100%" fill="#FFFFFF"/>',
             '<text x="40" y="44" font-family="Arial" font-size="28" font-weight="bold" fill="#10243A">'
             'Cửa sổ trượt và vùng bất thường</text>']
    # axis
    x0, y0, x1 = 70, 300, 1250
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#7F7F7F" stroke-width="1.5"/>')
    for i in range(0, 25):
        x = x0 + i * (x1 - x0) / 24
        parts.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0+8}" stroke="#7F7F7F"/>')
        if i % 4 == 0:
            parts.append(f'<text x="{x:.1f}" y="{y0+28}" text-anchor="middle" font-family="Arial" '
                         f'font-size="15" fill="#7F7F7F">{i*2}</text>')
    # signal
    import math
    pts = []
    for i in range(0, 241):
        t = i / 10
        v = 70 + 18 * math.sin(t * 1.7) + 8 * math.sin(t * 5.1)
        if 28 <= t <= 33:
            v += 46 * math.exp(-((t - 30.5) ** 2) / 2.2)
        pts.append(f"{x0 + i*(x1-x0)/240:.1f},{y0 - v*1.65:.1f}")
    parts.append('<polyline points="' + " ".join(pts) + '" fill="none" stroke="#1F4E79" stroke-width="2.4"/>')
    # windows
    for start, color, label in [(16, "#2E75B6", "W1"), (22, "#548235", "W2"), (28, "#C55A11", "W3")]:
        xa = x0 + start * (x1 - x0) / 48
        xb = x0 + (start + 8) * (x1 - x0) / 48
        parts.append(f'<rect x="{xa:.1f}" y="120" width="{xb-xa:.1f}" height="230" fill="{color}" opacity="0.10"/>')
        parts.append(f'<rect x="{xa:.1f}" y="120" width="{xb-xa:.1f}" height="230" fill="none" stroke="{color}" stroke-width="1.6"/>')
        parts.append(f'<text x="{(xa+xb)/2:.1f}" y="112" text-anchor="middle" font-family="Arial" '
                     f'font-size="13" font-weight="bold" fill="{color}">{label}</text>')
    # anomaly band
    xa = x0 + 28 * (x1 - x0) / 48
    xb = x0 + 33 * (x1 - x0) / 48
    parts.append(f'<rect x="{xa:.1f}" y="120" width="{xb-xa:.1f}" height="230" fill="#C00000" opacity="0.18"/>')
    parts.append(f'<text x="{(xa+xb)/2:.1f}" y="372" text-anchor="middle" font-family="Arial" '
                 f'font-size="13" font-weight="bold" fill="#C00000">bất thường</text>')
    parts.append('<text x="70" y="430" font-family="Arial" font-size="17" fill="#44546A">'
                 'Mỗi cửa sổ 64 điểm, bước trượt 8 điểm; nhãn dương nếu tâm cửa sổ nằm trong vùng bất thường.</text>')
    parts.append('<text x="70" y="458" font-family="Arial" font-size="17" fill="#44546A">'
                 'Cửa sổ chồng lấn giữ ngữ cảnh nhưng làm tăng tương quan giữa các mẫu huấn luyện.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "architecture.svg").write_text(architecture(), encoding="utf-8")
    (OUT / "windowing.svg").write_text(windowing(), encoding="utf-8")
    print(OUT / "architecture.svg", OUT / "windowing.svg")


if __name__ == "__main__":
    main()
