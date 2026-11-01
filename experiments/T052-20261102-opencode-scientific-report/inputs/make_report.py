"""Build the T052 Vietnamese scientific-report spec.

The same spec is rendered under two named profiles:
  * hust-datn-2017 (default deliverable)
  * vnu-uet-kl-2024 (comparison build)

Content is synthetic but internally consistent: a lightweight CNN-LSTM-AE for
IoT anomaly detection, with public datasets, baselines and an int8 deployment
study.  Numbers are invented for layout/testing; the method and citations are
real enough to be checked.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def c(text, **kw):
    return {"text": str(text), **kw}


def col(header, width, align="left"):
    return {"header": header, "width_mm": width, "align": align}


def tbl(columns, rows, caption, alt, source="", **kw):
    return {
        "type": "table", "advanced": True, "columns": columns, "rows": rows,
        "caption": caption, "alt": alt or caption, "source": source, **kw,
    }


def p(text):
    return {"type": "paragraph", "text": text}


def h(text, level=2):
    return {"type": "heading", "text": text, "level": level}


def sub(text):
    return {"type": "subheading", "text": text}


def bullets(items):
    return {"type": "bullets", "items": items}


def fig(path, caption, alt, source, width_mm=135, **kw):
    return {"type": "figure", "path": path, "caption": caption, "alt": alt,
            "source": source, "width_mm": width_mm, **kw}


def eq(latex, caption="", number=True):
    return {"type": "equation", "latex": latex, "caption": caption, "number": number}


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

WORK_ROWS = [
    [c("Họ và tên", bold=True), c("Nguyễn Văn An")],
    [c("Mã số sinh viên", bold=True), c("20201234")],
    [c("Ngành đào tạo", bold=True), c("Khoa học máy tính")],
    [c("Đề tài", bold=True), c("Phát hiện bất thường trên dữ liệu cảm biến IoT bằng kiến trúc học sâu nhẹ")],
    [c("Người hướng dẫn", bold=True), c("TS. Trần Minh Khoa")],
    [c("Ngày giao đề tài", bold=True), c("2026-09-01")],
    [c("Ngày hoàn thành", bold=True), c("2026-12-15")],
    [c("Yêu cầu", bold=True), c("Khảo sát bài toán, thiết kế kiến trúc, thực nghiệm trên bốn bộ dữ liệu, lượng tử hóa int8 và triển khai thử trên vi điều khiển.")],
]

RELATED_ROWS = [
    [c("Chandola và cộng sự (2009)", bold=True), c("Chuỗi thời gian, nhiều lĩnh vực"), c("Khảo sát thống kê, khoảng cách, phân cụm"), c("Đặt nền lý thuyết; chưa xét thiết bị biên")],
    [c("Malhotra và cộng sự (2015)", bold=True), c("ECG, dữ liệu chuỗi"), c("LSTM autoencoder"), c("Học biểu diễn bình thường; chưa có attention")],
    [c("Hundman và cộng sự (2018)", bold=True), c("Telemetry NASA"), c("LSTM dự báo + ngưỡng động"), c("Phát hiện sớm; nhạy với nhiễu")],
    [c("Su và cộng sự (2019)", bold=True), c("SMAP/MSL, SMD"), c("OmniAnomaly: VAE + GRU"), c("Xác suất, mạnh trên chuỗi dài; nặng cho MCU")],
    [c("Audibert và cộng sự (2020)", bold=True), c("SMD, SMAP, MSL"), c("USAD: hai autoencoder đối kháng"), c("Huấn luyện nhanh; cần nhiều bộ nhớ")],
    [c("Banbury và cộng sự (2021)", bold=True), c("MLPerf Tiny"), c("Benchmark TinyML"), c("Chuẩn đo độ trễ; chưa có bài toán bất thường")],
]

SYMBOL_ROWS = [
    [c("x_t", bold=True), c("Vector 12 kênh cảm biến tại thời điểm t"), c("—")],
    [c("w", bold=True), c("Độ dài cửa sổ trượt"), c("64 điểm")],
    [c("s", bold=True), c("Bước trượt"), c("8 điểm")],
    [c("z", bold=True), c("Vector latent sau encoder"), c("24 chiều")],
    [c("θ", bold=True), c("Tham số mạng"), c("—")],
    [c("L_rec", bold=True), c("Sai số tái tạo bình phương"), c("MSE")],
    [c("D_M", bold=True), c("Khoảng cách Mahalanobis"), c("—")],
    [c("α", bold=True), c("Trọng số hợp nhất điểm"), c("[0, 1]")],
    [c("μ, σ", bold=True), c("Trung bình, độ lệch chuẩn điểm validation"), c("—")],
    [c("k", bold=True), c("Hệ số ngưỡng"), c("3.0")],
]

METRIC_ROWS = [
    [c("Precision", bold=True), c("TP / (TP + FP)"), c("Tỷ lệ cảnh báo đúng")],
    [c("Recall", bold=True), c("TP / (TP + FN)"), c("Tỷ lệ bất thường được phát hiện")],
    [c("F1", bold=True), c("2PR / (P + R)"), c("Cân bằng precision và recall")],
    [c("AUC-PR", bold=True), c("Diện tích dưới đường PR"), c("Phù hợp dữ liệu mất cân bằng")],
    [c("FAR", bold=True), c("FP / (FP + TN)"), c("Tỷ lệ báo động giả")],
    [c("MTTD", bold=True), c("Số điểm trước cảnh báo đầu tiên"), c("Phát hiện sớm")],
]

FEATURE_ROWS = [
    [c("Thô", bold=True), c("Giá trị 12 kênh"), c("12", align="right"), c("Nhiệt độ, độ ẩm, áp suất, dòng điện, ...")],
    [c("Thống kê", bold=True), c("Trung bình, độ lệch chuẩn, min, max"), c("48", align="right"), c("Cửa sổ 16 điểm")],
    [c("Sai phân", bold=True), c("Δ bậc 1, Δ bậc 2"), c("24", align="right"), c("Bắt thay đổi đột ngột")],
    [c("Tần số", bold=True), c("Năng lượng 4 dải"), c("12", align="right"), c("FFT trên cửa sổ 64")],
    [c("Tương quan", bold=True), c("Hệ số tương quan cặp"), c("18", align="right"), c("Chọn 6 cặp quan trọng")],
]

HYPER_ROWS = [
    [c("Cửa sổ / bước trượt", bold=True), c("64 / 8"), c("10 giây / 1,25 giây ở 8 Hz")],
    [c("Số kênh đầu vào", bold=True), c("12"), c("Sau chọn đặc trưng")],
    [c("CNN filters / kernel", bold=True), c("64 / 5"), c("ReLU + batch norm")],
    [c("LSTM units", bold=True), c("64"), c("Một chiều, streaming")],
    [c("Latent", bold=True), c("24"), c("Nén 64 → 24")],
    [c("Batch size", bold=True), c("128"), c("5 seed")],
    [c("Learning rate", bold=True), c("1e-3"), c("Adam, cosine decay")],
    [c("Epochs / early stop", bold=True), c("80 / 12"), c("Patience 12")],
    [c("Ngưỡng k", bold=True), c("3.0"), c("Chọn trên validation")],
]

COMPLEX_ROWS = [
    [c("TinyAE", bold=True), c("12 K"), c("0,8 M"), c("9,2 ms"), c("42 KB")],
    [c("CNN-AE", bold=True), c("28 K"), c("3,1 M"), c("12,4 ms"), c("68 KB")],
    [c("LSTM-AE", bold=True), c("41 K"), c("4,7 M"), c("15,1 ms"), c("96 KB")],
    [c("Đề xuất float32", bold=True), c("36 K"), c("4,2 M"), c("18,4 ms"), c("112 KB")],
    [c("Đề xuất int8", bold=True), c("36 K"), c("4,2 M"), c("11,7 ms"), c("64 KB")],
]

DATASET_ROWS = [
    [c("NAB", bold=True), c("1–3"), c("58.000"), c("70/30"), c("Numenta, công khai")],
    [c("SWaT", bold=True), c("51"), c("1,4 M"), c("60/20/20"), c("iTrust, học thuật")],
    [c("SMAP/MSL", bold=True), c("25"), c("320.000"), c("70/30"), c("NASA, công khai")],
    [c("IoT-Synthetic", bold=True), c("12"), c("180.000"), c("70/30"), c("Sinh bởi tác giả")],
]

BASELINE_ROWS = [
    [c("Isolation Forest", bold=True), c("Cây cô lập"), c("200 cây, contamination 0,05")],
    [c("OCSVM", bold=True), c("One-class SVM"), c("RBF, ν = 0,05")],
    [c("LSTM-AE", bold=True), c("Autoencoder chuỗi"), c("64 cell, latent 24")],
    [c("USAD", bold=True), c("Hai autoencoder"), c("Theo Audibert và cộng sự")],
    [c("OmniAnomaly", bold=True), c("VAE + GRU"), c("Theo Su và cộng sự")],
    [c("TinyAE", bold=True), c("MLP autoencoder"), c("12 → 8 → 4 → 8 → 12")],
]

OVERALL_ROWS = [
    [c("Precision", bold=True), c("0,91"), c("[0,89; 0,93]"), c("+0,04 so với USAD")],
    [c("Recall", bold=True), c("0,87"), c("[0,84; 0,90]"), c("+0,02 so với USAD")],
    [c("F1", bold=True), c("0,89"), c("[0,87; 0,91]"), c("+0,03 so với USAD")],
    [c("AUC-PR", bold=True), c("0,91"), c("[0,89; 0,93]"), c("+0,03 so với OmniAnomaly")],
    [c("FAR", bold=True), c("0,04"), c("[0,03; 0,06]"), c("−0,02 so với LSTM-AE")],
    [c("MTTD", bold=True), c("3,2 điểm"), c("[2,8; 3,7]"), c("Sớm hơn 1,4 điểm")],
]

PER_DATASET_ROWS = [
    [c("NAB", bold=True), c("0,73"), c("0,70"), c("0,81"), c("0,85"), c("0,88")],
    [c("SWaT", bold=True), c("0,69"), c("0,66"), c("0,78"), c("0,83"), c("0,86")],
    [c("SMAP/MSL", bold=True), c("0,70"), c("0,67"), c("0,80"), c("0,84"), c("0,90")],
    [c("IoT-Synthetic", bold=True), c("0,72"), c("0,68"), c("0,77"), c("0,82"), c("0,92")],
    [c("Trung bình", bold=True), c("0,71"), c("0,68"), c("0,79"), c("0,84"), c("0,89")],
]

ABLATION_ROWS = [
    [c("AE", bold=True), c("0,780"), c("—"), c("Chỉ MLP, không học chuỗi")],
    [c("CNN-AE", bold=True), c("0,820"), c("+0,040"), c("Thêm đặc trưng cục bộ")],
    [c("CNN-LSTM-AE", bold=True), c("0,850"), c("+0,030"), c("Thêm phụ thuộc thời gian")],
    [c("+ Attention", bold=True), c("0,870"), c("+0,020"), c("Tập trung vào điểm bất thường")],
    [c("+ Mahalanobis", bold=True), c("0,885"), c("+0,015"), c("Điểm hợp nhất hai không gian")],
    [c("Đầy đủ + QAT", bold=True), c("0,890"), c("+0,005"), c("Lượng tử hóa giữ độ chính xác")],
]

LATENCY_ROWS = [
    [c("TinyAE", bold=True), c("12 K"), c("48 KB"), c("42 KB"), c("9,2 ms")],
    [c("CNN-AE", bold=True), c("28 K"), c("86 KB"), c("68 KB"), c("12,4 ms")],
    [c("LSTM-AE", bold=True), c("41 K"), c("124 KB"), c("96 KB"), c("15,1 ms")],
    [c("Đề xuất float32", bold=True), c("36 K"), c("148 KB"), c("112 KB"), c("18,4 ms")],
    [c("Đề xuất int8", bold=True), c("36 K"), c("82 KB"), c("64 KB"), c("11,7 ms")],
]

ERROR_ROWS = [
    [c("Báo động giả do drift", bold=True), c("Cảm biến nhiệt thay đổi theo mùa"), c("38% FP"), c("Cập nhật μ, σ theo cửa sổ 7 ngày")],
    [c("Bỏ sót bất thường tập thể", bold=True), c("Nhiều kênh cùng lệch nhẹ"), c("41% FN"), c("Thêm đặc trưng tương quan chéo")],
    [c("Nhiễu cảm biến", bold=True), c("Gai 1–2 điểm"), c("12% FP"), c("Lọc trung vị 3 điểm")],
    [c("Khởi động nguội", bold=True), c("Thiếu 10% dữ liệu đầu"), c("9% FN"), c("Bỏ qua 2 cửa sổ đầu")],
]

CONFUSION_ROWS = [
    [c("Bình thường", bold=True), c("8.820", align="right", fill="E2EFDA"), c("312", align="right", fill="FCE4D6"), c("9.132", align="right")],
    [c("Bất thường", bold=True), c("214", align="right", fill="FCE4D6"), c("1.654", align="right", fill="E2EFDA"), c("1.868", align="right")],
    [c("Tổng", bold=True), c("9.034", align="right"), c("1.966", align="right"), c("11.000", align="right")],
]

OBJECTIVE_ROWS = [
    [c("O1. Kiến trúc nhẹ", bold=True), c("CNN–LSTM–AE + attention, 36 K tham số"), c("Bảng 3.2; 3.3")],
    [c("O2. Độ chính xác", bold=True), c("F1 0,89; AUC-PR 0,91"), c("Bảng 4.3; Hình 4.1")],
    [c("O3. Triển khai biên", bold=True), c("11,7 ms; 64 KB RAM sau int8"), c("Bảng 4.6; Hình 4.5")],
    [c("O4. Phân tích lỗi", bold=True), c("4 nhóm lỗi, 3 biện pháp"), c("Bảng 4.9")],
]

CONFIG_ROWS = [
    [c("window", bold=True), c("64"), c("Số điểm mỗi cửa sổ")],
    [c("stride", bold=True), c("8"), c("Bước trượt")],
    [c("channels", bold=True), c("12"), c("Số kênh sau chọn")],
    [c("conv_filters", bold=True), c("64"), c("Số filter CNN")],
    [c("kernel", bold=True), c("5"), c("Kernel 1D")],
    [c("lstm_units", bold=True), c("64"), c("Số cell LSTM")],
    [c("latent", bold=True), c("24"), c("Chiều latent")],
    [c("threshold_k", bold=True), c("3.0"), c("μ + k·σ")],
    [c("quantization", bold=True), c("int8"), c("QAT, per-channel")],
]

PER_CLASS_ROWS = [
    [c("Nhiệt độ", bold=True), c("0,93"), c("0,90"), c("0,91"), c("412")],
    [c("Độ ẩm", bold=True), c("0,90"), c("0,86"), c("0,88"), c("388")],
    [c("Áp suất", bold=True), c("0,89"), c("0,85"), c("0,87"), c("356")],
    [c("Dòng điện", bold=True), c("0,94"), c("0,92"), c("0,93"), c("402")],
    [c("Điện áp", bold=True), c("0,88"), c("0,84"), c("0,86"), c("310")],
    [c("Rung", bold=True), c("0,86"), c("0,81"), c("0,83"), c("298")],
]

ANOMALY_ROWS = [
    [c("Điểm", bold=True), c("Một quan sát lệch khỏi phân phối tại thời điểm t"), c("Ngưỡng, autoencoder, Isolation Forest"), c("Cảm biến hỏng, gai nhiễu")],
    [c("Ngữ cảnh", bold=True), c("Giá trị bình thường ở điều kiện này nhưng bất thường ở điều kiện khác"), c("Mô hình chuỗi, cửa sổ trượt"), c("Nhiệt độ cao vào mùa hè")],
    [c("Tập thể", bold=True), c("Một nhóm điểm cùng lệch, dù từng điểm nằm trong ngưỡng"), c("Tương quan kênh, attention"), c("Tấn công SWaT, rò rỉ van")],
    [c("Drift", bold=True), c("Phân phối thay đổi chậm theo thời gian"), c("Cập nhật thống kê, học trực tuyến"), c("Hao mòn cảm biến, đổi mùa")],
]

COMPLEXITY_ROWS = [
    [c("Conv1D", bold=True), c("O(w · k · C_in · C_out)"), c("64 · 5 · 12 · 64 ≈ 0,25 M")],
    [c("LSTM", bold=True), c("O(w · 4H · (C + H))"), c("64 · 4 · 64 · 128 ≈ 2,1 M")],
    [c("Attention", bold=True), c("O(w² · H)"), c("64² · 64 ≈ 0,26 M")],
    [c("Decoder", bold=True), c("O(w · H · C)"), c("64 · 64 · 12 ≈ 0,05 M")],
]

FIRMWARE_ROWS = [
    [c("Tensor arena", bold=True), c("64 KB"), c("TFLite Micro, cấp phát tĩnh")],
    [c("Model flash", bold=True), c("82 KB"), c("int8, per-channel")],
    [c("DMA buffer", bold=True), c("8 KB"), c("Hai cửa sổ 64×12×2 byte")],
    [c("UART + log", bold=True), c("6 KB"), c("Cảnh báo và nhật ký vòng")],
    [c("Stack + hệ thống", bold=True), c("10 KB"), c("FreeRTOS, ngắt")],
]

THRESHOLD_ROWS = [
    [c("1,5", bold=True), c("0,82"), c("0,11"), c("0,94"), c("Quá nhạy")],
    [c("2,0", bold=True), c("0,86"), c("0,07"), c("0,92"), c("Nhiều báo động giả")],
    [c("2,5", bold=True), c("0,88"), c("0,05"), c("0,90"), c("Cân bằng")],
    [c("3,0", bold=True), c("0,89"), c("0,04"), c("0,87"), c("Chọn cho báo cáo")],
    [c("3,5", bold=True), c("0,88"), c("0,03"), c("0,84"), c("Giảm recall")],
    [c("4,0", bold=True), c("0,86"), c("0,02"), c("0,80"), c("Bỏ sót nhiều")],
]

COMPARISON_ROWS = [
    [c("LSTM-AE", bold=True), c("41 K"), c("0,79"), c("15,1 ms"), c("96 KB")],
    [c("USAD", bold=True), c("420 K"), c("0,84"), c("82 ms"), c("512 KB")],
    [c("OmniAnomaly", bold=True), c("1,2 M"), c("0,86"), c("110 ms"), c("1,2 MB")],
    [c("Đề xuất int8", bold=True), c("36 K"), c("0,89"), c("11,7 ms"), c("64 KB")],
]


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def front_matter() -> dict:
    abstract = (
        "Sự phổ biến của cảm biến IoT tạo ra dòng dữ liệu nhiều kênh, liên tục và có nhiễu. "
        "Phát hiện bất thường trên dòng dữ liệu này thường phải chạy tại biên vì độ trễ, băng thông "
        "và quyền riêng tư, nhưng các mô hình học sâu hiện đại vượt quá khả năng của vi điều khiển. "
        "Báo cáo đề xuất một kiến trúc lai CNN–LSTM–Autoencoder có attention, huấn luyện chỉ trên "
        "dữ liệu bình thường, và lượng tử hóa int8 để triển khai trên thiết bị biên.\n\n"
        "Kiến trúc gồm ba phần: encoder CNN 1D học đặc trưng cục bộ, LSTM học phụ thuộc thời gian, "
        "attention chọn các bước quan trọng; decoder tái tạo cửa sổ đầu vào. Điểm bất thường là hợp "
        "nhất của sai số tái tạo và khoảng cách Mahalanobis trong không gian latent, với ngưỡng "
        "μ + k·σ hiệu chỉnh trên tập validation. Mô hình được đánh giá trên NAB, SWaT, SMAP/MSL và "
        "một bộ dữ liệu IoT tổng hợp, so sánh với Isolation Forest, OCSVM, LSTM-AE, USAD, OmniAnomaly "
        "và một MLP autoencoder nhỏ.\n\n"
        "Kết quả cho thấy mô hình đạt F1 0,89 và AUC-PR 0,91, cao hơn baseline tốt nhất 0,03–0,05; "
        "sau lượng tử hóa int8, F1 giảm 0,008 nhưng độ trễ còn 11,7 ms và RAM còn 64 KB trên "
        "STM32H747. Phân tích ablation cho thấy attention đóng góp 0,020 F1, Mahalanobis 0,015 F1. "
        "Báo cáo cũng phân tích bốn nhóm lỗi và đề xuất biện pháp giảm báo động giả do drift.\n\n"
        "Đóng góp của báo cáo gồm ba phần: kiến trúc lai có attention, quy trình lượng tử hóa và "
        "hiệu chỉnh ngưỡng, và bộ đánh giá bốn bộ dữ liệu với phân tích lỗi. Mã nguồn và cấu hình "
        "được công bố kèm phụ lục để tái lập. Kết quả cho thấy mô hình nhỏ có thể là lựa chọn thực tế "
        "cho giám sát cảm biến tại biên, miễn là ngưỡng và lượng tử hóa được xử lý cùng nhau."
    )
    return {
        "task": {"enabled": True, "title": "NHIỆM VỤ THIẾT KẾ TỐT NGHIỆP",
                 "rows": WORK_ROWS,
                 "note": "Nhiệm vụ được giao ngày 2026-09-01; sinh viên hoàn thành và nộp quyển ngày 2026-12-15."},
        "declaration": {
            "enabled": True, "title": "LỜI CAM ĐOAN",
            "text": "Tôi xin cam đoan đây là công trình nghiên cứu do tôi thực hiện dưới sự hướng dẫn của TS. Trần Minh Khoa. Các số liệu, kết quả nêu trong báo cáo là trung thực, được tính toán từ mã nguồn và dữ liệu công khai; các kết quả chưa từng được công bố trong bất kỳ công trình nào khác. Những tài liệu, mã nguồn và ý tưởng tham khảo đều được trích dẫn rõ ràng.",
            "signature": "Hà Nội, ngày 15 tháng 12 năm 2026\nSinh viên thực hiện\n\n\nNguyễn Văn An",
        },
        "acknowledgements": {
            "enabled": True, "title": "LỜI CẢM ƠN",
            "text": "Tôi xin cảm ơn TS. Trần Minh Khoa đã định hướng đề tài, góp ý về kiến trúc và kiên nhẫn đọc từng phiên bản. Tôi cảm ơn các thầy cô trong bộ môn đã tạo điều kiện về dữ liệu và thiết bị thử nghiệm. Tôi cảm ơn các bạn trong nhóm nghiên cứu đã hỗ trợ chạy thực nghiệm, đặc biệt trong giai đoạn hiệu chỉnh ngưỡng và kiểm tra lượng tử hóa.",
        },
        "abstract": {"enabled": True, "title": "TÓM TẮT", "text": abstract,
                     "keywords": ["IoT", "phát hiện bất thường", "autoencoder", "CNN–LSTM", "TinyML"]},
        "toc": {"enabled": True, "levels": 3, "title": "MỤC LỤC"},
        "abbreviations": {"enabled": True, "title": "DANH MỤC KÝ HIỆU VÀ CHỮ VIẾT TẮT",
                          "header": ["Ký hiệu", "Diễn giải"],
                          "rows": [
                              [c("AE", bold=True), c("Autoencoder")],
                              [c("AUC-PR", bold=True), c("Area Under the Precision–Recall Curve")],
                              [c("CNN", bold=True), c("Convolutional Neural Network")],
                              [c("FAR", bold=True), c("False Alarm Rate")],
                              [c("FN", bold=True), c("False Negative")],
                              [c("FP", bold=True), c("False Positive")],
                              [c("F1", bold=True), c("F1-score")],
                              [c("IoT", bold=True), c("Internet of Things")],
                              [c("LSTM", bold=True), c("Long Short-Term Memory")],
                              [c("MCU", bold=True), c("Microcontroller Unit")],
                              [c("MSE", bold=True), c("Mean Squared Error")],
                              [c("MTTD", bold=True), c("Mean Time To Detect")],
                              [c("NAB", bold=True), c("Numenta Anomaly Benchmark")],
                              [c("QAT", bold=True), c("Quantization-Aware Training")],
                              [c("SMAP", bold=True), c("Soil Moisture Active Passive")],
                              [c("MSL", bold=True), c("Mars Science Laboratory")],
                              [c("SWaT", bold=True), c("Secure Water Treatment")],
                              [c("TN", bold=True), c("True Negative")],
                              [c("TP", bold=True), c("True Positive")],
                              [c("TinyML", bold=True), c("Machine Learning on Microcontrollers")],
                          ]},
        "list_of_figures": {"enabled": True, "title": "DANH MỤC HÌNH", "mode": "ref_pageref"},
        "list_of_tables": {"enabled": True, "title": "DANH MỤC BẢNG", "mode": "ref_pageref"},
    }


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

def mo_dau() -> dict:
    return {
        "heading": "Mở đầu",
        "level": 1,
        "numbered": False,
        "page_break_before": True,
        "blocks": [
            p("Trong thập niên vừa qua, cảm biến giá rẻ và kết nối không dây đã đưa IoT từ phòng thí nghiệm ra nhà máy, nông trại, bệnh viện và hộ gia đình. Một hệ thống giám sát nhỏ có thể sinh ra hàng chục nghìn điểm dữ liệu mỗi ngày; một nhà máy có hàng trăm cảm biến có thể sinh ra hàng triệu điểm. Dữ liệu này có giá trị chỉ khi hệ thống phát hiện được sự kiện bất thường: một cảm biến hỏng, một van bị kẹt, một đợt tấn công mạng, hay một thay đổi môi trường làm hỏng sản phẩm."),
            p("Phát hiện bất thường là bài toán xác định các điểm hoặc đoạn dữ liệu khác biệt có ý nghĩa so với hành vi bình thường. Với dữ liệu cảm biến, bài toán khó ở ba điểm. Thứ nhất, nhãn bất thường hiếm và đắt; phần lớn hệ thống chỉ có dữ liệu bình thường. Thứ hai, dữ liệu nhiều kênh, có tương quan và phụ thuộc thời gian; một ngưỡng đơn lẻ trên từng kênh bỏ sót bất thường tập thể. Thứ ba, mô hình phải chạy gần nguồn dữ liệu để giảm độ trễ và băng thông, nhưng vi điều khiển chỉ có vài trăm KB RAM và không có GPU."),
            p("Các hướng tiếp cận học sâu như autoencoder, LSTM và Transformer đã đạt kết quả tốt trên dữ liệu chuỗi thời gian, nhưng thường được đánh giá trên máy chủ. Khoảng trống giữa độ chính xác và khả năng triển khai biên là động lực của đề tài này. Báo cáo đặt câu hỏi: có thể thiết kế một mô hình đủ nhẹ để chạy trên vi điều khiển mà vẫn giữ được độ chính xác cạnh tranh với các mô hình nặng hơn hay không?"),
            sub("Tính cấp thiết"),
            p("Trong công nghiệp, một cảnh báo muộn có thể dẫn đến dừng dây chuyền, hỏng thiết bị hoặc tai nạn. Trong nông nghiệp, độ ẩm và nhiệt độ sai lệch có thể làm mất mùa. Trong y tế tại nhà, nhịp tim hoặc nồng độ oxy bất thường cần được phát hiện trong vài giây. Những tình huống này không cho phép gửi toàn bộ dữ liệu lên cloud rồi chờ kết quả: độ trễ, chi phí và quyền riêng tư đều là ràng buộc thực."),
            p("Một mô hình chạy trên thiết bị biên còn giúp hệ thống hoạt động khi mất mạng, giảm dữ liệu thô phải truyền và cho phép phản hồi cục bộ. Tuy nhiên, thiết bị biên có giới hạn về năng lượng, bộ nhớ và khả năng tính toán. Vì vậy, bài toán không chỉ là tối ưu độ chính xác mà là tối ưu đồng thời độ chính xác, độ trễ và bộ nhớ."),
            sub("Mục tiêu và câu hỏi nghiên cứu"),
            p("Mục tiêu tổng quát là thiết kế, huấn luyện và đánh giá một kiến trúc học sâu nhẹ cho phát hiện bất thường trên dữ liệu cảm biến IoT đa biến, có thể lượng tử hóa và triển khai trên vi điều khiển. Bốn câu hỏi nghiên cứu cụ thể là:"),
            bullets([
                "**RQ1:** Kiến trúc lai CNN–LSTM–Autoencoder có attention có thể học biểu diễn bình thường từ dữ liệu đa biến mà không cần nhãn bất thường hay không?",
                "**RQ2:** Kiến trúc đề xuất so sánh với các baseline thống kê, học máy cổ điển và học sâu như thế nào trên bốn bộ dữ liệu?",
                "**RQ3:** Lượng tử hóa int8 ảnh hưởng đến độ chính xác, độ trễ và bộ nhớ ra sao khi triển khai trên STM32H747?",
                "**RQ4:** Những nhóm lỗi nào chiếm ưu thế, và biện pháp nào có thể giảm báo động giả mà không giảm recall?",
            ]),
            sub("Đối tượng và phạm vi"),
            p("Đối tượng nghiên cứu là dữ liệu chuỗi thời gian đa biến từ cảm biến IoT, với giả thiết huấn luyện chỉ có dữ liệu bình thường. Phạm vi gồm bốn bộ dữ liệu: NAB, SWaT, SMAP/MSL và một bộ dữ liệu tổng hợp 12 kênh. Báo cáo không xét dữ liệu hình ảnh, âm thanh, văn bản hay chuỗi sự kiện rời rạc. Báo cáo cũng không xét học trực tuyến trên thiết bị; mô hình được huấn luyện ngoại tuyến và triển khai suy luận."),
            p("Về phần cứng, thực nghiệm dùng STM32H747 Discovery và ESP32-S3 để đo độ trễ, nhưng chỉ STM32H747 được báo cáo chi tiết vì có bộ nhớ lớn hơn. Kết quả trên ESP32-S3 được dùng để kiểm tra tính khả chuyển, không dùng để so sánh tuyệt đối."),
            sub("Phương pháp nghiên cứu"),
            p("Báo cáo kết hợp bốn phương pháp: khảo sát tài liệu để xác định khoảng trống; thiết kế kiến trúc theo hướng design science; thực nghiệm định lượng với 5 seed và khoảng tin cậy 95%; phân tích lỗi định tính trên các cửa sổ sai. Mỗi thí nghiệm có baseline, cùng cách chia dữ liệu và cùng quy trình chọn ngưỡng để bảo đảm so sánh công bằng."),
            p("Các chỉ số chính là precision, recall, F1, AUC-PR, FAR và MTTD. Độ trễ được đo bằng đồng hồ phần cứng, mỗi cấu hình 1.000 lần suy luận sau 100 lần khởi động. Bộ nhớ được đo bằng linker map và bộ đếm heap của FreeRTOS."),
            sub("Đóng góp"),
            bullets([
                "**Kiến trúc:** một autoencoder lai CNN–LSTM–attention gọn, huấn luyện chỉ trên dữ liệu bình thường, với điểm bất thường hợp nhất sai số tái tạo và Mahalanobis.",
                "**Quy trình lượng tử hóa:** QAT cho mô hình chuỗi thời gian, hiệu chỉnh ngưỡng sau lượng tử hóa, và kiểm tra trên hai vi điều khiển.",
                "**Benchmark:** so sánh 6 phương pháp trên 4 bộ dữ liệu với cùng giao thức, kèm phân tích ablation và phân tích lỗi.",
                "**Mã nguồn và cấu hình:** cấu hình huấn luyện, mã xuất TFLite Micro và script tái lập kết quả được để trong phụ lục.",
            ]),
            sub("Bố cục báo cáo"),
            p("Báo cáo gồm năm chương. Chương 1 trình bày tổng quan về IoT, bài toán phát hiện bất thường và công trình liên quan. Chương 2 trình bày cơ sở lý thuyết về autoencoder, CNN, LSTM, attention, lượng tử hóa và chỉ số đánh giá. Chương 3 mô tả kiến trúc đề xuất và quy trình huấn luyện. Chương 4 trình bày thực nghiệm, so sánh, ablation, độ trễ và phân tích lỗi. Chương 5 kết luận và nêu hướng phát triển. Tài liệu tham khảo và hai phụ lục ở cuối báo cáo."),
        ],
    }


def chuong_1() -> dict:
    return {
        "heading": "Tổng quan và công trình liên quan",
        "level": 1,
        "blocks": [
            h("IoT và dữ liệu cảm biến", 2),
            p("IoT là mạng các thiết bị vật lý có khả năng cảm nhận, tính toán và truyền thông. Một nút cảm biến điển hình gồm vi điều khiển, một hoặc nhiều cảm biến, bộ nhớ, radio và nguồn. Dữ liệu được lấy mẫu theo chu kỳ, đóng gói và gửi lên gateway hoặc cloud. Tùy ứng dụng, tần số lấy mẫu có thể từ vài giây đến vài mili giây; số kênh có thể từ một đến hàng trăm."),
            p("Dữ liệu cảm biến có bốn đặc điểm ảnh hưởng trực tiếp đến bài toán phát hiện bất thường. Thứ nhất, dữ liệu có tính chuỗi: giá trị hiện tại phụ thuộc giá trị trước đó. Thứ hai, các kênh có tương quan: nhiệt độ và độ ẩm thường đi cùng nhau, dòng điện và mô-men xoắn có quan hệ phi tuyến. Thứ ba, dữ liệu có nhiễu và mất mát: cảm biến có thể trả về NaN, giá trị cực đại hoặc giá trị kẹt. Thứ tư, phân phối có thể thay đổi theo thời gian do mùa, hao mòn hoặc thay đổi quy trình, hiện tượng gọi là concept drift."),
            p("Ba đặc điểm đầu tạo ra nhu cầu về mô hình học biểu diễn thay vì ngưỡng đơn lẻ. Đặc điểm thứ tư tạo ra nhu cầu về hiệu chỉnh ngưỡng và đánh giá theo thời gian, không chỉ trên một tập test cố định. Một mô hình có F1 cao trên tập test nhưng không thích nghi với drift sẽ nhanh chóng báo động giả trong vận hành."),
            h("Bài toán phát hiện bất thường", 2),
            p("Theo Chandola và cộng sự, bất thường có thể là điểm, ngữ cảnh hoặc tập thể {{cite:chandola2009}}. Bất thường điểm là một quan sát đơn lẻ khác xa phân phối; bất thường ngữ cảnh là quan sát bình thường ở điều kiện này nhưng bất thường ở điều kiện khác; bất thường tập thể là một nhóm quan sát cùng lệch, dù từng điểm có thể nằm trong ngưỡng. Dữ liệu cảm biến thường chứa cả ba loại."),
            p("Về cách học, bài toán được chia thành có giám sát, bán giám sát và không giám sát. Có giám sát cần nhãn cho cả bình thường và bất thường; bán giám sát thường huấn luyện chỉ trên dữ liệu bình thường; không giám sát tìm cấu trúc bất thường mà không dùng nhãn. Trong công nghiệp, nhãn bất thường hiếm và không đầy đủ, nên hướng bán giám sát thực tế hơn. Báo cáo chọn hướng này: huấn luyện chỉ trên cửa sổ bình thường, phát hiện cửa sổ không khớp với mô hình."),
            p("Một khó khăn khác là đánh giá. Nếu bất thường kéo dài nhiều điểm, một cảnh báo đúng có thể được tính là nhiều true positive, làm F1 bị thổi phồng. Báo cáo dùng nhãn theo cửa sổ và báo cáo cả phát hiện theo điểm lẫn theo đoạn; mọi bảng kết quả ghi rõ đơn vị để tránh so sánh sai."),
            h("Phân loại theo cấu trúc dữ liệu", 3),
            p("Mỗi loại bất thường đòi hỏi một cách phát hiện khác nhau. Bảng 1.2 hệ thống hóa bốn loại và ánh xạ chúng vào kỹ thuật phù hợp. Việc chọn sai loại bất thường là nguyên nhân phổ biến khiến mô hình có F1 cao trên giấy nhưng thất bại khi triển khai."),
            tbl([col("Loại", 24), col("Định nghĩa", 58), col("Cách phát hiện", 42), col("Ví dụ", 28)],
                ANOMALY_ROWS, "Phân loại bất thường trong dữ liệu cảm biến",
                "Bảng bốn loại bất thường và kỹ thuật phát hiện tương ứng",
                "Tổng hợp từ Chandola và cộng sự [1]"),
            p("Bất thường điểm dễ phát hiện nhất nhưng cũng dễ bị nhiễu đánh lừa. Bất thường ngữ cảnh cần mô hình có khái niệm thời gian, ví dụ nhiệt độ 35°C là bình thường vào mùa hè nhưng bất thường vào mùa đông. Bất thường tập thể khó nhất vì từng điểm có thể nằm trong ngưỡng; mô hình phải học tương quan giữa các kênh. Drift không phải bất thường tại một thời điểm mà là thay đổi phân phối theo thời gian, nên cần cơ chế cập nhật thay vì chỉ tăng ngưỡng."),
            p("Trong bốn bộ dữ liệu của báo cáo, NAB chủ yếu chứa bất thường điểm và ngữ cảnh; SWaT chứa bất thường tập thể do tấn công; SMAP/MSL chứa cả ba loại; bộ tổng hợp được thiết kế để kiểm tra từng loại riêng. Cách chọn này cho phép đánh giá mô hình trên phổ rộng, thay vì tối ưu cho một loại duy nhất."),
            h("Các hướng tiếp cận", 2),
            h("Phương pháp thống kê", 3),
            p("Các phương pháp thống kê như ARIMA, EWMA, kiểm soát quá trình bằng thống kê (SPC) mô hình hóa phân phối chuẩn và đánh dấu điểm nằm ngoài khoảng tin cậy. Chúng nhanh, dễ giải thích và phù hợp với tín hiệu một kênh. Tuy nhiên, chúng giả định phân phối ổn định và tuyến tính, khó bắt tương quan phi tuyến giữa nhiều kênh. Với dữ liệu cảm biến có drift, ngưỡng cố định nhanh chóng lỗi thời."),
            h("Học máy cổ điển", 3),
            p("Isolation Forest, One-Class SVM, Local Outlier Factor và kNN là những baseline mạnh cho dữ liệu nhiều chiều. Isolation Forest cô lập điểm bất thường bằng các cây ngẫu nhiên; OCSVM tìm biên bao quanh dữ liệu bình thường; LOF dựa trên mật độ cục bộ. Các phương pháp này không cần nhãn bất thường và chạy nhanh, nhưng cần đặc trưng thủ công và không mô hình hóa trực tiếp thứ tự thời gian. Với cửa sổ dài, số chiều tăng và chi phí suy luận tăng."),
            h("Học sâu", 3),
            p("Autoencoder học ánh xạ nén và tái tạo; mẫu bình thường có sai số tái tạo thấp, mẫu bất thường có sai số cao. LSTM autoencoder thêm khả năng học phụ thuộc thời gian {{cite:malhotra2015}}; VAE học phân phối xác suất và cho điểm bất thường có cơ sở xác suất; Transformer dùng self-attention để nắm phụ thuộc dài. Các mô hình này đạt kết quả tốt nhưng thường có hàng triệu tham số, khó chạy trên vi điều khiển."),
            p("Trong nhóm học sâu, hai hướng liên quan trực tiếp đến báo cáo là autoencoder chuỗi và mô hình lai. Malhotra và cộng sự dùng LSTM autoencoder để phát hiện bất thường trên ECG {{cite:malhotra2015}}. Hundman và cộng sự dùng LSTM dự báo và ngưỡng động cho telemetry vệ tinh {{cite:hundman2018}}. Su và cộng sự đề xuất OmniAnomaly, kết hợp VAE và GRU, mạnh trên chuỗi dài nhưng nặng {{cite:su2019}}. Audibert và cộng sự đề xuất USAD, hai autoencoder đối kháng, huấn luyện nhanh hơn nhưng vẫn cần nhiều bộ nhớ {{cite:audibert2020}}."),
            h("Học sâu trên thiết bị biên", 3),
            p("TinyML nghiên cứu cách đưa mô hình học sâu lên vi điều khiển có tài nguyên hạn chế. Ba kỹ thuật chính là lượng tử hóa, cắt tỉa và chưng cất tri thức. Lượng tử hóa chuyển trọng số từ float32 sang int8, giảm 4 lần bộ nhớ và tăng tốc nhờ phép nhân số nguyên; cắt tỉa loại bỏ trọng số ít quan trọng; chưng cất huấn luyện mô hình nhỏ từ mô hình lớn. Banbury và cộng sự đưa ra bộ benchmark MLPerf Tiny để so sánh độ trễ và năng lượng {{cite:banbury2021}}; Goyal và cộng sự tổng quan các kỹ thuật TinyML {{cite:goyal2020}}."),
            p("Tuy nhiên, phần lớn công trình TinyML tập trung vào phân loại ảnh hoặc từ khóa, không phải phát hiện bất thường trên chuỗi thời gian. Bài toán chuỗi có thêm hai thách thức: trạng thái ẩn của LSTM phải được quản lý giữa các cửa sổ, và ngưỡng phải hiệu chỉnh sau lượng tử hóa vì phân phối sai số thay đổi. Báo cáo giải quyết cả hai bằng cách giữ cửa sổ độc lập và hiệu chỉnh ngưỡng trên tập validation sau QAT."),
            h("Công trình liên quan", 2),
            tbl([col("Nghiên cứu", 30), col("Dữ liệu", 32), col("Phương pháp", 46), col("Hạn chế / khoảng trống", 44)],
                RELATED_ROWS, "So sánh các công trình liên quan",
                "Bảng so sánh sáu công trình theo dữ liệu, phương pháp và khoảng trống",
                "Tổng hợp từ tài liệu tham khảo [1]–[6]"),
            p("Bảng 1.1 cho thấy ba khoảng trống. Thứ nhất, các mô hình chính xác nhất (OmniAnomaly, USAD) có kích thước lớn, chưa được đánh giá trên vi điều khiển. Thứ hai, các công trình TinyML chưa xét bài toán bất thường chuỗi thời gian đa biến. Thứ ba, ít công trình báo cáo đồng thời độ chính xác, độ trễ, bộ nhớ và phân tích lỗi trên cùng một giao thức."),
            p("Khoảng trống thứ nhất không chỉ là vấn đề kỹ thuật mà còn là vấn đề kinh tế. Một nhà máy có hàng trăm điểm đo; nếu mỗi điểm cần một máy chủ nhỏ hoặc một gateway mạnh, chi phí triển khai và bảo trì tăng nhanh. Thiết bị biên giá rẻ có thể xử lý tại chỗ, chỉ gửi cảnh báo và thống kê. Tuy nhiên, thiết bị biên thường không có FPU mạnh, không có GPU và bộ nhớ bị giới hạn bởi giá thành. Vì vậy, một mô hình 36 nghìn tham số có ý nghĩa thực tiễn hơn một mô hình 1,2 triệu tham số, ngay cả khi chênh lệch F1 chỉ 0,03."),
            p("Khoảng trống thứ hai liên quan đến tính công bằng của đánh giá. Nhiều công trình chọn ngưỡng trên tập test hoặc dùng point-adjust, dẫn đến kết quả lạc quan. Khi triển khai, ngưỡng phải chọn trước khi thấy nhãn test; nếu không, con số F1 không phản ánh năng lực thực. Báo cáo giải quyết bằng cách tách validation/test theo thời gian và chọn ngưỡng chỉ trên validation. Đây là điểm khác biệt về phương pháp, không chỉ về kiến trúc."),
            p("Khoảng trống thứ ba là sự thiếu vắng phân tích lỗi có hệ thống. Một mô hình có F1 0,89 vẫn có thể thất bại trên một loại bất thường cụ thể. Nếu báo cáo chỉ nêu con số tổng hợp, người đọc không biết mô hình có phù hợp với ứng dụng của mình hay không. Báo cáo phân loại lỗi theo bốn nhóm và lượng hóa tần suất, giúp người đọc ra quyết định dựa trên rủi ro thay vì chỉ dựa trên F1."),
            h("Khoảng trống và hướng giải quyết", 2),
            bullets([
                "**Khoảng trống 1:** thiếu một kiến trúc lai vừa học được phụ thuộc thời gian vừa đủ nhỏ cho MCU. Báo cáo đề xuất CNN–LSTM–AE với latent 24 và lượng tử hóa int8.",
                "**Khoảng trống 2:** ngưỡng bất thường thường được chọn trên tập test, gây rò rỉ dữ liệu. Báo cáo chọn ngưỡng trên validation và báo cáo độ nhạy theo k.",
                "**Khoảng trống 3:** tác động của lượng tử hóa đến phát hiện bất thường chưa được phân tích tách bạch. Báo cáo so sánh float32 và int8 trên cùng kiến trúc, cùng ngưỡng hiệu chỉnh.",
                "**Khoảng trống 4:** phân tích lỗi thường chỉ nêu tổng số. Báo cáo phân loại lỗi theo drift, bất thường tập thể, nhiễu và khởi động nguội.",
            ]),
            h("Kết luận chương", 2),
            p("Chương này đã trình bày đặc điểm dữ liệu IoT, các loại bất thường, ba hướng tiếp cận và sáu công trình liên quan. Từ đó, báo cáo xác định bốn khoảng trống: kiến trúc nhẹ, chọn ngưỡng đúng, tác động lượng tử hóa và phân tích lỗi. Chương 2 trình bày cơ sở lý thuyết để giải quyết các khoảng trống này."),
        ],
    }


def chuong_2() -> dict:
    return {
        "heading": "Cơ sở lý thuyết",
        "level": 1,
        "page_break_before": False,
        "blocks": [
            h("Dữ liệu chuỗi thời gian cảm biến", 2),
            p("Một chuỗi thời gian đa biến được biểu diễn bởi ma trận X ∈ R^{T×C}, trong đó T là số điểm và C là số kênh. Tại thời điểm t, vector x_t chứa C giá trị cảm biến. Bài toán phát hiện bất thường là gán nhãn y_t ∈ {0,1} cho mỗi điểm hoặc mỗi cửa sổ, với 1 là bất thường. Trong báo cáo, nhãn được gán theo cửa sổ: cửa sổ dương nếu tâm của nó nằm trong vùng bất thường."),
            p("Trước khi đưa vào mô hình, dữ liệu được làm sạch và chuẩn hóa. Giá trị thiếu được nội suy tuyến tính nếu khoảng trống ngắn hơn 3 điểm; nếu dài hơn, cửa sổ bị loại. Ngoại lai cực đại được thay bằng trung vị của 5 điểm lân cận để tránh làm lệch chuẩn hóa. Mỗi kênh được chuẩn hóa z-score bằng trung bình và độ lệch chuẩn của tập huấn luyện, không dùng tập test."),
            p("Cửa sổ trượt kích thước w và bước s tạo ra các mẫu huấn luyện. Cửa sổ chồng lấn giúp tăng số mẫu và giữ ngữ cảnh, nhưng làm tăng tương quan giữa các mẫu, khiến đánh giá lạc quan nếu chia ngẫu nhiên. Báo cáo chia theo thời gian: 70% đầu cho huấn luyện, 15% tiếp theo cho validation, 15% cuối cho test. Cách chia này mô phỏng vận hành thực tế và tránh rò rỉ tương lai."),
            h("Autoencoder", 2),
            p("Autoencoder là mạng học hai ánh xạ: encoder f_θ: R^w×C → R^d nén đầu vào thành vector latent z, decoder g_φ: R^d → R^w×C tái tạo đầu vào. Mục tiêu huấn luyện là cực tiểu sai số tái tạo:"),
            eq(r"L_{rec} = \frac{1}{N}\sum_{i=1}^{N}\left\|x_i - g_\phi(f_\theta(x_i))\right\|_2^2",
               "Sai số tái tạo bình phương của autoencoder."),
            p("Với dữ liệu bình thường, mô hình học được đa tạp (manifold) của dữ liệu; mẫu bất thường nằm ngoài đa tạp nên có sai số cao. Tuy nhiên, autoencoder có thể tái tạo cả mẫu bất thường nếu mô hình quá linh hoạt hoặc latent quá lớn. Vì vậy, cần chọn latent nhỏ, thêm nhiễu huấn luyện và đánh giá trên dữ liệu chưa thấy."),
            p("Một biến thể là VAE, học phân phối q(z|x) và tối ưu ELBO. VAE cho điểm bất thường có cơ sở xác suất nhưng huấn luyện khó hơn và thường cần nhiều tham số. Báo cáo chọn autoencoder tất định vì mục tiêu là mô hình nhỏ, dễ lượng tử hóa; VAE được dùng làm baseline tinh thần qua OmniAnomaly."),
            h("Hạn chế của autoencoder", 3),
            p("Autoencoder không phải là giải pháp vạn năng. Nếu decoder quá mạnh, mô hình có thể học cách tái tạo cả mẫu bất thường, làm giảm sai số và bỏ sót. Hiện tượng này thường gặp khi latent quá lớn hoặc dữ liệu huấn luyện chứa nhiều nhiễu. Báo cáo kiểm soát bằng cách giữ latent 24, thêm nhiễu nhẹ và đánh giá trên dữ liệu chưa thấy."),
            p("Một hạn chế khác là autoencoder không mô hình hóa trực tiếp xác suất. Nó cho điểm tái tạo nhưng không cho biết mẫu đó hiếm đến mức nào. VAE giải quyết bằng cách học phân phối, nhưng đổi lại huấn luyện phức tạp hơn và có thể bỏ qua chi tiết. Báo cáo chọn autoencoder tất định vì mục tiêu là mô hình nhỏ, nhưng bổ sung Mahalanobis để có tín hiệu xác suất trong không gian latent."),
            p("Cuối cùng, autoencoder nhạy với chuẩn hóa. Nếu thống kê dùng để chuẩn hóa khác giữa huấn luyện và triển khai, sai số tái tạo tăng trên toàn bộ mẫu, gây báo động giả. Trong triển khai, cần lưu thống kê chuẩn hóa cùng mô hình và kiểm tra định kỳ. Đây là chi tiết kỹ thuật nhỏ nhưng có thể quyết định thành bại của hệ thống."),
            h("CNN một chiều", 2),
            p("Convolution 1D trượt một kernel trên trục thời gian, tạo ra đặc trưng cục bộ. Với đầu vào X và kernel K có kích thước k, đầu ra tại vị trí t là:"),
            eq(r"y_t = \sigma\left(\sum_{j=0}^{k-1} K_j \cdot x_{t+j} + b\right)",
               "Phép convolution một chiều."),
            p("CNN có hai lợi thế cho dữ liệu cảm biến: chia sẻ trọng số theo thời gian, giảm số tham số; và học được mẫu cục bộ như tăng đột ngột, dao động chu kỳ hoặc xung nhiễu. Xếp chồng nhiều lớp convolution tăng trường tiếp nhận (receptive field), cho phép mô hình thấy ngữ cảnh dài hơn mà không cần kết nối đầy đủ."),
            p("Batch normalization sau convolution giúp ổn định huấn luyện và giảm phụ thuộc vào khởi tạo {{cite:ioffe2015}}. Hàm kích hoạt ReLU giữ mô hình tuyến tính từng khúc, dễ lượng tử hóa. Max pooling giảm chiều và tăng bất biến với dịch nhỏ; với chuỗi cảm biến, pooling quá mạnh có thể làm mất bất thường ngắn, nên báo cáo chỉ dùng một lớp pooling."),
            h("LSTM", 2),
            p("LSTM giải quyết vấn đề vanishing gradient của RNN bằng cơ chế cổng {{cite:hochreiter1997}}. Tại mỗi bước, LSTM duy trì trạng thái ẩn h_t và trạng thái tế bào c_t. Ba cổng input, forget và output điều khiển việc ghi, xóa và đọc thông tin:"),
            eq(r"f_t = \sigma(W_f h_{t-1} + U_f x_t + b_f),\quad i_t = \sigma(W_i h_{t-1} + U_i x_t + b_i)",
               "Cổng quên và cổng vào của LSTM."),
            eq(r"c_t = f_t \cdot c_{t-1} + i_t \cdot \mathrm{tanh}(W_c h_{t-1} + U_c x_t + b_c)",
               "Cập nhật trạng thái tế bào."),
            p("Cổng quên cho phép mô hình giữ thông tin qua nhiều bước, quan trọng với chuỗi cảm biến có chu kỳ ngày hoặc tuần. Cổng vào quyết định thông tin mới nào được ghi. Cổng ra tạo h_t từ c_t. Với suy luận streaming, mô hình có thể giữ trạng thái giữa các cửa sổ, nhưng báo cáo chọn đặt lại trạng thái mỗi cửa sổ để đơn giản hóa triển khai và tránh lỗi tích lũy."),
            h("Attention", 2),
            p("Attention cho phép mô hình tập trung vào các bước quan trọng thay vì nén tất cả vào một vector cuối {{cite:vaswani2017}}. Với chuỗi trạng thái H = [h_1, …, h_w], điểm attention được tính từ query, key và value:"),
            eq(r"\alpha_t = \frac{e^{h_t^{T} W_a \bar{h}}}{\sum_{j=1}^{w}e^{h_j^{T} W_a \bar{h}}},\quad c = \sum_{t=1}^{w}\alpha_t h_t",
               "Temporal attention với query là trung bình chuỗi."),
            p("Trong bài toán bất thường, attention có hai lợi ích. Thứ nhất, nó giúp mô hình nhấn mạnh các bước có thay đổi bất thường, cải thiện recall. Thứ hai, trọng số attention là tín hiệu giải thích: khi cảnh báo, hệ thống có thể chỉ ra điểm nào đóng góp nhiều nhất. Báo cáo dùng một lớp attention đơn giản, không dùng multi-head, để giữ mô hình nhỏ."),
            h("Lượng tử hóa và triển khai biên", 2),
            p("Lượng tử hóa affine ánh xạ số thực r sang số nguyên q theo q = round(r/S) + Z, với S là scale và Z là zero-point {{cite:jacob2018}}. Với int8, mỗi trọng số chỉ chiếm 1 byte thay vì 4 byte. Phép nhân số nguyên nhanh hơn và tốn ít năng lượng hơn trên vi điều khiển không có FPU mạnh. Tuy nhiên, lượng tử hóa làm mất độ chính xác, đặc biệt với giá trị nhỏ và phân phối lệch."),
            p("Có hai cách lượng tử hóa. Post-training quantization (PTQ) lượng tử hóa mô hình đã huấn luyện, nhanh nhưng có thể giảm mạnh độ chính xác với chuỗi thời gian. Quantization-aware training (QAT) mô phỏng lượng tử hóa trong huấn luyện bằng fake-quant nodes, giúp mô hình thích nghi. Báo cáo dùng QAT với per-channel scale cho trọng số và per-tensor cho activation."),
            p("Sau lượng tử hóa, phân phối sai số tái tạo thay đổi; ngưỡng chọn trên float32 không còn tối ưu. Báo cáo hiệu chỉnh lại μ và σ trên tập validation sau QAT, giữ nguyên k. Đây là bước quan trọng để tránh giảm recall khi triển khai."),
            h("Độ phức tạp tính toán", 2),
            p("Chi phí của mô hình không chỉ là số tham số. Với chuỗi thời gian, chi phí phụ thuộc vào độ dài cửa sổ, số kênh và số bước tuần tự. Bảng 2.3 ước lượng số phép tính cho từng toán tử với w = 64, C = 12, H = 64. Convolution chiếm phần lớn phép tính nhưng chạy song song tốt; LSTM chiếm phần lớn bộ nhớ trạng thái và phụ thuộc tuần tự, khó tăng tốc bằng SIMD."),
            tbl([col("Toán tử", 34), col("Độ phức tạp", 60), col("Ước lượng", 58)],
                COMPLEXITY_ROWS, "Độ phức tạp của các toán tử",
                "Bảng độ phức tạp conv1d, LSTM, attention, decoder",
                "Tính với w = 64, C = 12, H = 64"),
            p("Tổng chi phí lý thuyết khoảng 2,7 triệu phép nhân-cộng cho một cửa sổ, tương đương 4,2 MFLOPs. Con số này khớp với ước lượng từ profiler (4,1 MFLOPs). Trên STM32H747, 4,2 MFLOPs ở 480 MHz lý thuyết mất 8,75 ms nếu đạt 1 phép tính/chu kỳ; thực tế 18,4 ms do truy cập bộ nhớ và hành vi tuần tự của LSTM. Sau int8, tốc độ tăng nhờ phép nhân số nguyên và giảm băng thông bộ nhớ."),
            p("Kết quả này giải thích vì sao chỉ giảm số tham số chưa đủ. Một mô hình ít tham số nhưng nhiều bước tuần tự vẫn chậm. Thiết kế nhẹ cần cân bằng ba yếu tố: số tham số, số phép tính và mức độ song song. CNN song song tốt, LSTM tuần tự, attention bậc hai theo độ dài cửa sổ; vì vậy báo cáo giữ cửa sổ 64 và chỉ dùng một lớp attention."),
            h("Chỉ số đánh giá", 2),
            p("Với dữ liệu mất cân bằng, accuracy không phù hợp vì mô hình đoán toàn bình thường vẫn đạt độ chính xác cao. Báo cáo dùng precision, recall, F1, AUC-PR, FAR và MTTD. Bảng 2.1 tóm tắt công thức và ý nghĩa."),
            tbl([col("Chỉ số", 32), col("Công thức", 60), col("Diễn giải", 60)],
                METRIC_ROWS, "Các chỉ số đánh giá", "Bảng công thức precision, recall, F1, AUC-PR, FAR, MTTD",
                "Tổng hợp từ tài liệu đánh giá phát hiện bất thường"),
            p("AUC-PR được ưu tiên hơn AUC-ROC khi tỷ lệ bất thường thấp, vì ROC có thể lạc quan với nhiều true negative. Báo cáo vẫn báo cáo AUC-ROC trong phụ lục để so sánh với công trình khác. MTTD được tính bằng số điểm từ lúc bất thường bắt đầu đến cảnh báo đầu tiên; giá trị nhỏ hơn là tốt hơn."),
            p("Một cạm bẫy là point-adjust: nếu bất thường kéo dài, chỉ cần một cảnh báo đúng trong đoạn được tính là phát hiện toàn bộ đoạn, làm F1 tăng giả tạo. Báo cáo không dùng point-adjust; mỗi cửa sổ được đánh giá độc lập, và kết quả theo đoạn được báo cáo riêng trong Phụ lục B."),
            p("Khi báo cáo khoảng tin cậy, cần phân biệt hai nguồn biến thiên: biến thiên do seed huấn luyện và biến thiên do chọn ngưỡng. Báo cáo cố định ngưỡng theo validation của từng seed, sau đó tính trung bình và độ lệch chuẩn trên 5 seed. Cách này bao gồm cả hai nguồn nhưng không tách bạch chúng. Nếu muốn tách, cần chạy nhiều lần chọn ngưỡng trên các tập validation khác nhau, việc này để lại cho hướng phát triển."),
            p("Với dữ liệu mất cân bằng, một mô hình có recall cao nhưng precision thấp có thể tạo quá nhiều cảnh báo, khiến người vận hành bỏ qua cảnh báo. Ngược lại, precision cao nhưng recall thấp có thể bỏ sót sự cố nghiêm trọng. Vì vậy, báo cáo không tối ưu một chỉ số duy nhất mà trình bày cả precision, recall, FAR và MTTD, để người đọc chọn điểm vận hành phù hợp."),
            h("Ký hiệu", 2),
            tbl([col("Ký hiệu", 24), col("Ý nghĩa", 92), col("Đơn vị / giá trị", 34)],
                SYMBOL_ROWS, "Ký hiệu và đơn vị", "Bảng ký hiệu dùng trong báo cáo",
                "Quy ước của tác giả"),
            h("Kết luận chương", 2),
            p("Chương này đã trình bày nền tảng của autoencoder, CNN, LSTM, attention, lượng tử hóa và các chỉ số đánh giá. Những lý thuyết này là cơ sở để thiết kế kiến trúc ở Chương 3 và diễn giải kết quả ở Chương 4. Điểm quan trọng là mỗi thành phần đều có chi phí tính toán; thiết kế nhẹ không phải là bỏ bớt tùy tiện mà là chọn đúng thành phần cho từng loại cấu trúc dữ liệu."),
        ],
    }


def chuong_3() -> dict:
    return {
        "heading": "Phương pháp đề xuất",
        "level": 1,
        "page_break_before": False,
        "blocks": [
            h("Kiến trúc tổng thể", 2),
            p("Kiến trúc đề xuất gồm một encoder lai và một decoder đối xứng. Đầu vào là cửa sổ 64×12 đã chuẩn hóa. Encoder gồm hai lớp convolution 1D (64 filter, kernel 5), batch normalization, ReLU và max pooling; tiếp theo là LSTM 64 cell; cuối cùng là temporal attention và lớp chiếu xuống latent 24 chiều. Decoder gồm lớp chiếu ngược, hai lớp transpose convolution và đầu ra 64×12. Toàn bộ mô hình có khoảng 36 nghìn tham số."),
            fig("../artifacts/figures/architecture-print.png",
                "Kiến trúc CNN–LSTM–Autoencoder có attention.",
                "Sơ đồ kiến trúc: cửa sổ 64×12, CNN 1D, LSTM, attention, latent 24, decoder, điểm hợp nhất và ngưỡng.",
                "Tác giả thiết kế; VectorCraft kết xuất.", width_mm=150),
            p("Luồng suy luận có hai nhánh điểm. Nhánh thứ nhất tính sai số tái tạo giữa đầu vào và đầu ra. Nhánh thứ hai tính khoảng cách Mahalanobis giữa vector latent và phân phối latent của tập huấn luyện. Hai điểm được chuẩn hóa và hợp nhất bằng trọng số α. Ngưỡng được chọn trên validation theo μ + k·σ của điểm hợp nhất."),
            p("Thiết kế này xuất phát từ hai quan sát. Thứ nhất, sai số tái tạo nhạy với thay đổi cục bộ nhưng có thể bỏ qua bất thường tập thể nếu decoder tái tạo tốt. Thứ hai, khoảng cách Mahalanobis nhạy với dịch chuyển phân phối trong không gian latent nhưng bỏ qua chi tiết thời gian. Hợp nhất hai điểm giúp bù trừ điểm yếu của nhau."),
            h("Tiền xử lý và đặc trưng", 2),
            p("Dữ liệu thô được làm sạch theo ba bước: loại cửa sổ có quá 10% giá trị thiếu, nội suy khoảng trống ngắn, và thay ngoại lai cực đại bằng trung vị 5 điểm. Sau đó, mỗi kênh được chuẩn hóa z-score bằng thống kê tập huấn luyện. Việc dùng thống kê tập huấn luyện cho validation và test là bắt buộc để tránh rò rỉ."),
            p("Ngoài 12 kênh thô, báo cáo thêm ba nhóm đặc trưng: thống kê cửa sổ, sai phân và năng lượng tần số. Bảng 3.1 liệt kê các nhóm và số chiều. Các đặc trưng này không thay thế CNN mà bổ sung tín hiệu toàn cục, giúp mô hình nhỏ học nhanh hơn."),
            tbl([col("Nhóm", 26), col("Đặc trưng", 64), col("Số chiều", 20), col("Ghi chú", 42)],
                FEATURE_ROWS, "Các nhóm đặc trưng đầu vào", "Bảng đặc trưng thô, thống kê, sai phân, tần số, tương quan",
                "Thiết kế của tác giả"),
            fig("../artifacts/figures/windowing-print.png",
                "Cửa sổ trượt và vùng bất thường.",
                "Sơ đồ trục thời gian với ba cửa sổ trượt W1, W2, W3 và vùng bất thường được tô đỏ.",
                "Tác giả thiết kế; VectorCraft kết xuất.", width_mm=140),
            p("Số chiều cuối cùng là 12 + 48 + 24 + 12 + 18 = 114. Tuy nhiên, mô hình chỉ dùng 12 kênh thô sau khi chọn lọc; các đặc trưng thống kê được dùng trong baseline và phân tích lỗi. Lý do là CNN có thể tự học đặc trưng cục bộ, còn đưa quá nhiều đặc trưng thủ công vào mô hình nhỏ dễ gây quá khớp."),
            h("Nhánh encoder CNN–LSTM", 2),
            p("Hai lớp convolution 1D học đặc trưng từng kênh và tương quan giữa các kênh. Lớp thứ nhất dùng 64 filter kernel 5, stride 1, padding same; lớp thứ hai dùng 64 filter kernel 3. Batch normalization đặt sau mỗi lớp, tiếp theo là ReLU. Max pooling kích thước 2 giảm chiều thời gian từ 64 xuống 16 sau hai lần pooling."),
            p("LSTM 64 cell nhận chuỗi đặc trưng đã nén và học phụ thuộc thời gian. Báo cáo dùng LSTM một chiều thay vì hai chiều vì suy luận streaming không có tương lai. Trạng thái ẩn cuối chuỗi và toàn bộ chuỗi trạng thái được giữ lại cho attention."),
            p("Attention tính trọng số cho từng bước theo công thức 2.4. Query là trung bình chuỗi trạng thái, key và value là các trạng thái. Vector ngữ cảnh c là tổng có trọng số. Lớp chiếu cuối đưa c về latent 24 chiều. Latent nhỏ là ràng buộc có chủ đích: nó buộc mô hình bỏ qua chi tiết không quan trọng và giảm nguy cơ tái tạo cả bất thường."),
            h("Decoder và điểm bất thường", 2),
            p("Decoder đối xứng với encoder: lớp chiếu từ 24 lên 64, hai lớp transpose convolution, batch normalization và ReLU. Đầu ra được cắt về đúng kích thước 64×12. Sai số tái tạo được tính theo MSE từng kênh, sau đó lấy trung bình có trọng số theo độ biến thiên của từng kênh."),
            eq(r"L_{rec}(x) = \frac{1}{C}\sum_{c=1}^{C}\frac{1}{w}\sum_{t=1}^{w}(x_{t,c}-\hat{x}_{t,c})^2",
               "Sai số tái tạo theo kênh và thời gian."),
            p("Điểm Mahalanobis được tính trên vector latent z:"),
            eq(r"D_M(z) = \sqrt{(z-\mu)^{T}\Sigma^{-1}(z-\mu)}",
               "Khoảng cách Mahalanobis trong không gian latent."),
            p("Trong đó μ và Σ là trung bình và hiệp phương sai của latent trên tập huấn luyện. Vì latent 24 chiều và số mẫu lớn, Σ được ước lượng với regularization 1e-4 để tránh suy biến. Điểm cuối cùng là hợp nhất có trọng số:"),
            eq(r"s(x) = \alpha\,L^{*}_{rec}(x) + (1-\alpha)\,D^{*}_M(z)",
               "Điểm bất thường hợp nhất; α = 0,6."),
            p("Các điểm được chuẩn hóa bằng thống kê validation trước khi hợp nhất để hai nhánh có cùng thang đo. Ngưỡng τ = μ_s + k·σ_s, với k = 3,0. Giá trị k được chọn bằng cách quét trên validation: k nhỏ làm tăng recall nhưng tăng FAR; k lớn làm giảm FAR nhưng bỏ sót. Báo cáo chọn k theo điểm F1 trên validation, không dùng test."),
            h("Huấn luyện", 2),
            p("Mô hình được huấn luyện chỉ trên cửa sổ bình thường. Hàm mất mát kết hợp sai số tái tạo và regularization latent:"),
            eq(r"L = L_{rec} + \lambda\,\|z\|_2^2,\quad \lambda = 10^{-4}",
               "Hàm mất mát huấn luyện."),
            p("Optimizer Adam {{cite:kingma2015}} với learning rate 1e-3, cosine decay về 1e-5, batch size 128, tối đa 80 epoch. Early stopping với patience 12 theo validation loss. Gradient clipping 1.0 để tránh bùng nổ gradient ở các cửa sổ có gai nhiễu. Mỗi cấu hình được chạy 5 seed; báo cáo trung bình và khoảng tin cậy 95%."),
            p("Vì chỉ có dữ liệu bình thường, không có class weighting. Tuy nhiên, dữ liệu bình thường vẫn có thể chứa nhiễu và đoạn chuyển tiếp; báo cáo thêm nhiễu Gaussian nhẹ (σ = 0.01) và time warping nhẹ để tăng đa dạng, giúp mô hình không học thuộc từng điểm."),
            p("Việc chọn siêu tham số được thực hiện trên validation, không trên test. Báo cáo quét ba giá trị latent (16, 24, 32), ba giá trị learning rate (5e-4, 1e-3, 2e-3) và hai giá trị batch size (64, 128). Kết quả cho thấy latent 24 và learning rate 1e-3 là điểm cân bằng; latent 16 làm giảm F1 0,02, latent 32 tăng tham số 18% mà chỉ tăng F1 0,005. Batch size 64 dao động lớn hơn giữa các seed, nên báo cáo chọn 128."),
            p("Để tái lập, mỗi lần chạy ghi lại seed, phiên bản PyTorch, phiên bản CUDA, hash của dữ liệu và cấu hình đầy đủ. Kết quả trong báo cáo dùng seed 42; các seed 43–46 nằm trong thư mục `results/`. Script `train.py` nhận đường dẫn cấu hình và seed, không đọc biến môi trường, để tránh khác biệt giữa các máy. Đây là chi tiết nhỏ nhưng giúp giảm đáng kể thời gian gỡ lỗi."),
            h("Lượng tử hóa và triển khai", 2),
            p("QAT được thực hiện sau 40 epoch huấn luyện float32. Mô hình được chèn fake-quant cho trọng số và activation, sau đó fine-tune 20 epoch với learning rate 1e-4. Trọng số dùng per-channel symmetric int8; activation dùng per-tensor asymmetric int8 với calibration trên 1.000 cửa sổ validation."),
            p("Mô hình sau QAT được chuyển sang TFLite và dùng TFLite Micro để chạy trên STM32H747. Firmware đọc cửa sổ từ cảm biến qua DMA, chạy suy luận, so sánh với ngưỡng và gửi cảnh báo qua UART. Bộ nhớ được cấp phát tĩnh; tensor arena 64 KB. Độ trễ đo bằng DWT cycle counter, quy đổi theo tần số 480 MHz."),
            p("Một điểm cần lưu ý là ngưỡng phải hiệu chỉnh lại sau QAT. Báo cáo chạy mô hình int8 trên 2.000 cửa sổ validation, tính lại μ_s và σ_s, giữ nguyên k. Nếu dùng ngưỡng float32, FAR tăng từ 0,04 lên 0,09 trong thử nghiệm sơ bộ; đây là lỗi phổ biến khi triển khai lượng tử hóa."),
            h("Quy trình triển khai firmware", 2),
            p("Mô hình sau QAT được chuyển thành file `.tflite`, sau đó dùng công cụ `xxd` để nhúng vào firmware dưới dạng mảng byte. Firmware chạy trên FreeRTOS với ba task: đọc cảm biến qua DMA, chạy suy luận, và gửi cảnh báo. Tensor arena được cấp phát tĩnh 64 KB; model nằm trong flash và được ánh xạ trực tiếp, không copy vào RAM."),
            p("Bảng 3.3 trình bày ngân sách bộ nhớ. Tổng RAM là 64 + 8 + 6 + 10 = 88 KB, nhưng tensor arena và DMA buffer dùng chung vùng nhớ tĩnh, nên mức cao nhất đo được là 64 KB. Flash gồm model 82 KB, firmware 96 KB và bootloader 24 KB, tổng 202 KB, phù hợp với STM32H747 (2 MB flash)."),
            tbl([col("Hạng mục", 54), col("Kích thước", 30), col("Ghi chú", 68)],
                FIRMWARE_ROWS, "Ngân sách bộ nhớ firmware", "Bảng tensor arena, model flash, DMA, UART và stack",
                "Đo từ linker map và FreeRTOS heap"),
            p("Quy trình kiểm thử gồm ba mức. Mức đơn vị kiểm tra từng toán tử với dữ liệu giả lập; mức tích hợp so sánh đầu ra TFLite Micro với PyTorch trên 1.000 cửa sổ, sai số tuyệt đối trung bình dưới 1e-3; mức hệ thống chạy 24 giờ với dữ liệu phát lại, đo số cảnh báo và nhiệt độ chip. Kết quả 24 giờ cho thấy không có rò rỉ bộ nhớ, nhiệt độ chip tăng 6°C so với môi trường."),
            p("Một chi tiết quan trọng là đồng bộ hóa cửa sổ. Cảm biến lấy mẫu 8 Hz, cửa sổ 64 điểm tương ứng 8 giây; firmware dùng bộ đệm vòng và chỉ chạy suy luận khi đủ 64 điểm. Nếu một mẫu bị mất, cửa sổ được đánh dấu không hợp lệ và bỏ qua, tránh suy luận trên dữ liệu méo. Cơ chế này đơn giản nhưng hiệu quả trong thử nghiệm."),
            h("Kiểm thử trên ESP32-S3", 2),
            p("Để kiểm tra tính khả chuyển, mô hình int8 được chuyển sang ESP32-S3, một vi điều khiển dual-core 240 MHz với 512 KB SRAM và 8 MB PSRAM. Việc chuyển đổi không cần thay đổi kiến trúc; chỉ cần giảm tensor arena từ 64 KB xuống 48 KB và dùng PSRAM cho bộ đệm đầu vào. Kết quả đo được 23,6 ms mỗi cửa sổ, chậm hơn STM32H747 khoảng 2 lần nhưng vẫn đáp ứng tần số 8 Hz."),
            p("Độ trễ tăng do ba yếu tố: xung nhịp thấp hơn, cache nhỏ hơn và thiếu DSP tối ưu cho phép nhân số nguyên. Tuy nhiên, ESP32-S3 có Wi-Fi/BLE tích hợp, phù hợp với các nút cảm biến không dây. Trong một số ứng dụng, việc gửi cảnh báo qua Wi-Fi quan trọng hơn độ trễ vài mili giây. Vì vậy, lựa chọn MCU phụ thuộc vào ưu tiên của hệ thống, không chỉ vào tốc độ."),
            p("Kết quả trên ESP32-S3 cũng cho thấy mô hình không phụ thuộc vào một dòng chip cụ thể. Đây là lợi ích của việc dùng TFLite Micro và lượng tử hóa chuẩn thay vì tối ưu cho một kiến trúc phần cứng. Trong tương lai, nhóm sẽ thử thêm trên các MCU có NPU nhỏ để so sánh hiệu quả của tăng tốc phần cứng."),
            h("Tham số và độ phức tạp", 2),
            tbl([col("Mô hình", 42), col("Tham số", 26), col("FLOPs", 30), col("Độ trễ", 28), col("RAM", 26)],
                COMPLEX_ROWS, "Độ phức tạp của các mô hình", "Bảng tham số, FLOPs, độ trễ và RAM của năm mô hình",
                "Đo trên STM32H747, 5 seed"),
            p("Bảng 3.2 cho thấy mô hình đề xuất có 36 nghìn tham số, nhỏ hơn LSTM-AE (41 nghìn) nhưng lớn hơn TinyAE (12 nghìn). Sau int8, RAM giảm từ 112 KB xuống 64 KB và độ trễ giảm từ 18,4 ms xuống 11,7 ms. Mức này phù hợp với chu kỳ lấy mẫu 1 giây của phần lớn cảm biến công nghiệp."),
            h("Kết luận chương", 2),
            p("Chương này đã mô tả kiến trúc, tiền xử lý, hàm mất mát, huấn luyện, lượng tử hóa và độ phức tạp. Kiến trúc được thiết kế để cân bằng ba mục tiêu: học được cấu trúc thời gian, giữ mô hình nhỏ, và lượng tử hóa ít mất mát. Chương 4 kiểm chứng các lựa chọn này bằng thực nghiệm."),
        ],
    }


def chuong_4() -> dict:
    return {
        "heading": "Thực nghiệm và đánh giá",
        "level": 1,
        "page_break_before": False,
        "blocks": [
            h("Bộ dữ liệu", 2),
            p("Báo cáo dùng bốn bộ dữ liệu để kiểm tra tính tổng quát. NAB là bộ dữ liệu chuỗi thời gian công khai với nhiều loại tín hiệu và nhãn bất thường do con người gán. SWaT là dữ liệu nhà máy xử lý nước với 51 kênh và các cuộc tấn công có chủ đích. SMAP/MSL là telemetry vệ tinh của NASA, thường được dùng trong các công trình phát hiện bất thường. Bộ thứ tư là dữ liệu IoT tổng hợp 12 kênh, được sinh để kiểm tra khả năng kiểm soát thí nghiệm."),
            tbl([col("Bộ dữ liệu", 38), col("Số kênh", 22), col("Số điểm", 30), col("Chia train/test", 34), col("Nguồn", 26)],
                DATASET_ROWS, "Các bộ dữ liệu thực nghiệm", "Bảng bốn bộ dữ liệu với số kênh, số điểm và cách chia",
                "NAB, SWaT, NASA SMAP/MSL; bộ tổng hợp do tác giả sinh"),
            p("Mỗi bộ được chia theo thời gian: 70% đầu huấn luyện, 15% validation, 15% test. Với NAB và SMAP/MSL, các đoạn bất thường được giữ nguyên trong test; không có bất thường trong train. Với SWaT, các cuộc tấn công được gán nhãn theo thời gian và chỉ xuất hiện trong test. Bộ tổng hợp có 12 kênh, trong đó 4 kênh có tương quan phi tuyến; bất thường được chèn theo ba kịch bản: điểm, đoạn và tập thể."),
            h("Thiết lập thực nghiệm", 2),
            p("Tất cả mô hình được chạy trên cùng phần cứng và cùng quy trình tiền xử lý. Baseline gồm Isolation Forest, OCSVM, LSTM-AE, USAD, OmniAnomaly và TinyAE. Bảng 4.2 tóm tắt cấu hình. Các baseline học sâu được huấn luyện với cùng batch size, optimizer và early stopping; riêng OmniAnomaly dùng cấu hình gốc vì kiến trúc VAE khác."),
            tbl([col("Phương pháp", 42), col("Loại", 38), col("Cấu hình", 66)],
                BASELINE_ROWS, "Cấu hình các baseline", "Bảng cấu hình sáu baseline",
                "Tác giả cài đặt, dựa trên mã nguồn công khai"),
            p("Mỗi thí nghiệm chạy 5 seed (42, 43, 44, 45, 46). Kết quả báo cáo trung bình và khoảng tin cậy 95% theo phân phối t. Với mỗi seed, ngưỡng được chọn trên validation bằng quét k từ 1,5 đến 5,0, bước 0,1; sau đó áp dụng cố định cho test. Cách này tránh rò rỉ nhãn test và phản ánh quy trình triển khai."),
            h("Kết quả chính", 2),
            p("Bảng 4.3 trình bày kết quả tổng hợp trên bốn bộ dữ liệu. Mô hình đề xuất đạt F1 0,89, AUC-PR 0,91, FAR 0,04 và MTTD 3,2 điểm. So với baseline tốt nhất (USAD), F1 tăng 0,03; so với OmniAnomaly, AUC-PR tăng 0,03. Khoảng tin cậy hẹp cho thấy kết quả ổn định qua các seed."),
            tbl([col("Chỉ số", 46), col("Giá trị", 30), col("Khoảng tin cậy 95%", 42), col("So sánh", 30)],
                OVERALL_ROWS, "Kết quả tổng hợp", "Bảng precision, recall, F1, AUC-PR, FAR, MTTD",
                "Trung bình 5 seed trên bốn bộ dữ liệu"),
            fig("../artifacts/charts/training-print.png",
                "Đường cong huấn luyện và validation.",
                "Biểu đồ đường cong loss theo epoch; train loss giảm đều, validation loss chững lại sau epoch 30.",
                "Chart Forge (SheetCraft); dữ liệu tổng hợp.", width_mm=132),
            p("Hình 4.1 cho thấy train loss giảm đều từ 0,82 xuống 0,07; validation loss giảm đến epoch 30 rồi tăng nhẹ do quá khớp. Early stopping dừng ở epoch 34. Đây là hành vi mong đợi với mô hình nhỏ và dữ liệu có nhiễu; báo cáo không chọn epoch có train loss thấp nhất mà chọn epoch có validation loss thấp nhất."),
            fig("../artifacts/charts/pr-print.png",
                "Đường cong precision–recall.",
                "Đường cong PR; precision giảm chậm đến recall 0,8 rồi giảm nhanh.",
                "Chart Forge (SheetCraft); dữ liệu tổng hợp.", width_mm=122),
            p("Đường PR cho thấy precision vẫn trên 0,80 ở recall 0,80, sau đó giảm nhanh. Vùng recall cao là vùng khó: để phát hiện thêm 10% bất thường, precision giảm khoảng 0,15. Trong vận hành, ngưỡng nên được chọn theo chi phí của false positive và false negative, không chỉ theo F1."),
            h("So sánh với baseline", 2),
            p("Bảng 4.4 so sánh F1 theo từng bộ dữ liệu. Mô hình đề xuất dẫn đầu trên NAB, SMAP/MSL và bộ tổng hợp; trên SWaT, OmniAnomaly nhỉnh hơn 0,01 nhưng chậm hơn 6 lần và cần 4 lần bộ nhớ. Điều này cho thấy lợi thế của mô hình không phải tuyệt đối trên mọi bộ, mà là cân bằng giữa độ chính xác và chi phí."),
            tbl([col("Bộ dữ liệu", 38), col("IF", 18), col("OCSVM", 20), col("LSTM-AE", 24), col("USAD", 20), col("Đề xuất", 28)],
                PER_DATASET_ROWS, "F1 theo từng bộ dữ liệu", "Bảng so sánh F1 của sáu phương pháp trên bốn bộ dữ liệu",
                "Trung bình 5 seed"),
            fig("../artifacts/charts/f1-print.png",
                "So sánh F1 của sáu phương pháp.",
                "Biểu đồ cột F1; đề xuất cao nhất 0,89, thấp nhất OCSVM 0,68.",
                "Chart Forge (SheetCraft); dữ liệu tổng hợp.", width_mm=132),
            p("Hình 4.2 cho thấy khoảng cách giữa nhóm học sâu và nhóm cổ điển là 0,11–0,13 F1. Trong nhóm học sâu, thứ tự là OmniAnomaly, USAD, đề xuất, LSTM-AE. Tuy nhiên, OmniAnomaly có 1,2 triệu tham số, gấp 33 lần mô hình đề xuất; USAD có 420 nghìn tham số, gấp 12 lần. Vì vậy, so sánh chỉ theo F1 sẽ bỏ qua chi phí triển khai."),
            h("Ablation", 2),
            p("Bảng 4.5 tách đóng góp của từng thành phần. Bắt đầu từ AE đơn giản (F1 0,780), thêm CNN tăng 0,040; thêm LSTM tăng 0,030; thêm attention tăng 0,020; thêm Mahalanobis tăng 0,015; QAT làm giảm 0,005 so với float32 nhưng vẫn giữ 0,890. Tổng cộng, kiến trúc đầy đủ tăng 0,110 F1 so với AE."),
            tbl([col("Biến thể", 50), col("F1", 24), col("ΔF1", 24), col("Nhận xét", 50)],
                ABLATION_ROWS, "Kết quả ablation", "Bảng đóng góp của CNN, LSTM, attention, Mahalanobis và QAT",
                "Trung bình 5 seed"),
            fig("../artifacts/charts/ablation-print.png",
                "Đóng góp của từng thành phần.",
                "Biểu đồ cột F1 của sáu biến thể từ AE đến đầy đủ + QAT.",
                "Chart Forge (SheetCraft); dữ liệu tổng hợp.", width_mm=132),
            p("Đóng góp lớn nhất đến từ CNN (0,040), cho thấy đặc trưng cục bộ quan trọng hơn mô hình chuỗi thuần túy. Attention đóng góp 0,020, tập trung vào các bước có thay đổi. Mahalanobis đóng góp 0,015, chủ yếu trên bộ tổng hợp có tương quan phi tuyến. QAT giảm 0,005, nhỏ hơn ngưỡng 0,01 mà nhóm đặt ra, nên được chấp nhận."),
            h("Độ trễ và bộ nhớ", 2),
            p("Bảng 4.6 trình bày độ trễ và bộ nhớ trên STM32H747. Mô hình float32 có độ trễ 18,4 ms và RAM 112 KB; sau int8, độ trễ còn 11,7 ms và RAM 64 KB. Flash giảm từ 148 KB xuống 82 KB. So với TinyAE, mô hình đề xuất chậm hơn 2,5 ms nhưng F1 cao hơn 0,11; so với LSTM-AE, nhanh hơn 3,4 ms và F1 cao hơn 0,10."),
            tbl([col("Mô hình", 42), col("Tham số", 24), col("Flash", 26), col("RAM", 24), col("Độ trễ", 26)],
                LATENCY_ROWS, "Độ trễ và bộ nhớ trên STM32H747", "Bảng tham số, flash, RAM và độ trễ của năm mô hình",
                "Đo bằng DWT cycle counter, 1.000 lần"),
            fig("../artifacts/charts/latency-print.png",
                "Độ trễ suy luận trên STM32H747.",
                "Biểu đồ cột độ trễ; đề xuất int8 thấp hơn float32 và LSTM-AE.",
                "Chart Forge (SheetCraft); dữ liệu tổng hợp.", width_mm=132),
            p("Hình 4.4 cho thấy lượng tử hóa giảm 36% độ trễ và 43% RAM. Mức giảm này quan trọng với thiết bị chạy pin: năng lượng tỷ lệ với số phép tính và số lần truy cập bộ nhớ. Trong thử nghiệm 24 giờ, thiết bị int8 tiêu thụ 18,6 mWh, so với 27,4 mWh của float32."),
            h("Độ nhạy của ngưỡng", 2),
            p("Ngưỡng là siêu tham số quan trọng nhất khi triển khai. Bảng 4.7 quét k từ 1,5 đến 4,0 trên validation và đánh giá trên test. Khi k tăng, FAR giảm nhưng recall giảm; F1 đạt cực đại quanh k = 3,0. Đây là lý do báo cáo chọn k = 3,0, nhưng trong vận hành có thể chọn k theo chi phí: nếu chi phí kiểm tra thủ công cao, tăng k lên 3,5; nếu bỏ sót nguy hiểm hơn, giảm k xuống 2,5."),
            tbl([col("k", 18), col("F1", 26), col("FAR", 26), col("Recall", 28), col("Nhận xét", 54)],
                THRESHOLD_ROWS, "Độ nhạy của ngưỡng theo k", "Bảng F1, FAR, recall khi quét k từ 1,5 đến 4,0",
                "Trung bình 5 seed"),
            p("Bảng này cũng cho thấy F1 không phải hàm lồi đối xứng: vùng k < 2,5 mất precision nhanh do báo động giả; vùng k > 3,5 mất recall nhanh do bỏ sót. Vùng 2,5–3,0 là vùng ổn định, phù hợp để triển khai. Báo cáo khuyến nghị hiệu chỉnh lại k sau mỗi 3 tháng hoặc khi phát hiện drift."),
            h("So sánh với công trình", 2),
            p("Bảng 4.8 so sánh trực tiếp với ba mô hình học sâu có mã nguồn công khai. Cột độ trễ và RAM được đo trên cùng phần cứng hoặc ước lượng từ số tham số khi không có mã nguồn. OmniAnomaly có F1 cao thứ hai nhưng chậm gấp 9 lần và cần 1,2 MB RAM, vượt khả năng của STM32H747. USAD có F1 thấp hơn 0,05 nhưng vẫn cần 512 KB. Mô hình đề xuất là mô hình duy nhất chạy dưới 64 KB RAM."),
            tbl([col("Công trình", 36), col("Tham số", 28), col("F1", 24), col("Độ trễ", 30), col("RAM", 28)],
                COMPARISON_ROWS, "So sánh với công trình công khai", "Bảng tham số, F1, độ trễ và RAM của bốn mô hình",
                "Đo trên STM32H747 hoặc ước lượng từ mã nguồn"),
            p("Cần lưu ý rằng so sánh này không hoàn toàn công bằng: OmniAnomaly được thiết kế cho máy chủ, không cho MCU. Mục tiêu của bảng không phải chứng minh mô hình đề xuất tốt hơn mọi mặt, mà cho thấy đánh đổi giữa độ chính xác và chi phí. Trong một hệ thống thực, lựa chọn đúng phụ thuộc vào ngân sách năng lượng, tần suất lấy mẫu và yêu cầu độ trễ."),
            h("Phân tích lỗi", 2),
            p("Bảng 4.9 phân loại 214 false positive và 312 false negative trên tập test. Báo động giả do drift chiếm 38% FP; bỏ sót bất thường tập thể chiếm 41% FN. Hai nhóm này gợi ý hai hướng cải thiện: cập nhật thống kê ngưỡng theo thời gian và thêm đặc trưng tương quan chéo giữa các kênh."),
            tbl([col("Loại lỗi", 38), col("Ví dụ", 58), col("Tần suất", 24), col("Biện pháp", 32)],
                ERROR_ROWS, "Phân tích lỗi", "Bảng bốn nhóm lỗi và biện pháp giảm thiểu",
                "Phân tích 526 lỗi trên tập test"),
            p("Confusion matrix trong Bảng 4.10 cho thấy mô hình có precision 0,84 và recall 0,89 ở ngưỡng vận hành. Recall cao hơn precision là lựa chọn có chủ đích: bỏ sót bất thường nguy hiểm hơn báo động giả. Trong vận hành, ngưỡng có thể tăng để giảm FAR nếu chi phí kiểm tra thủ công cao."),
            tbl([col("Thực tế \\ Dự đoán", 44), col("Bình thường", 34), col("Bất thường", 34), col("Tổng", 28)],
                CONFUSION_ROWS, "Confusion matrix trên tập test", "Bảng confusion matrix 2x2",
                "Tổng hợp 5 seed"),
            h("Thảo luận", 2),
            p("Kết quả cho thấy có thể đạt độ chính xác cạnh tranh với mô hình nhỏ hơn 10–30 lần. Điều này không có nghĩa là mô hình nhỏ luôn tốt hơn; nó có nghĩa là với bài toán cụ thể này, phần lớn thông tin nằm trong đặc trưng cục bộ và tương quan giữa các kênh, không cần hàng triệu tham số. Khi dữ liệu phức tạp hơn, khoảng cách có thể thu hẹp."),
            p("Hai hạn chế của thực nghiệm là dữ liệu tổng hợp và ngưỡng tĩnh. Dữ liệu tổng hợp do tác giả sinh có thể không phản ánh đầy đủ nhiễu công nghiệp. Ngưỡng tĩnh không thích nghi với drift; trong triển khai dài hạn, cần cơ chế cập nhật μ, σ hoặc học trực tuyến có kiểm soát. Hai hướng này được nêu trong Chương 5."),
            p("Về mặt triển khai, kết quả độ trễ 11,7 ms cho phép chạy suy luận ở tần số 8 Hz với thời gian xử lý chiếm dưới 10% chu kỳ. Phần còn lại dành cho đọc cảm biến, truyền thông và ngủ. Nếu tần số lấy mẫu tăng lên 50 Hz, mô hình vẫn đáp ứng nhưng năng lượng tiêu thụ tăng tuyến tính; khi đó cần cân nhắc chạy suy luận theo lô hoặc giảm tần số. Báo cáo không đo năng lượng trong thời gian dài, nên con số 18,6 mWh/24 giờ chỉ là ước lượng từ phép đo ngắn."),
            p("Một khía cạnh chưa được xét là bảo mật của mô hình tại biên. Kẻ tấn công có thể đọc firmware, trích xuất mô hình hoặc thay đổi ngưỡng. Trong ứng dụng công nghiệp, cần ký firmware, bảo vệ bộ nhớ và ghi log bất biến. Những biện pháp này nằm ngoài phạm vi báo cáo nhưng ảnh hưởng đến tính khả dụng của mô hình trong thực tế."),
            p("Cuối cùng, kết quả F1 0,89 không có nghĩa là mô hình đã sẵn sàng thay thế con người. Nó có nghĩa là mô hình có thể đóng vai trò lọc sơ bộ, giảm số sự kiện cần kiểm tra thủ công. Quyết định cuối cùng vẫn thuộc về kỹ thuật viên, và giao diện cần hiển thị lý do cảnh báo (trọng số attention, kênh đóng góp) để tăng độ tin cậy."),
            h("Chi phí triển khai", 2),
            p("Một câu hỏi thực tế là chi phí cho mỗi nút cảm biến. Báo cáo ước tính bo mạch STM32H747 khoảng 12 USD, cảm biến 20 USD, vỏ và nguồn 10 USD, tổng khoảng 42 USD mỗi nút. Một gateway công nghiệp có thể có giá 250–400 USD và phục vụ 20–30 nút. Với 100 nút, chi phí gateway tập trung khoảng 1.200 USD cộng với hạ tầng mạng, trong khi giải pháp biên dùng 100 bo mạch giá 42 USD, tổng 4.200 USD."),
            p("Ở quy mô nhỏ, gateway tập trung có thể rẻ hơn vì không cần bo mạch tại mỗi nút. Ở quy mô lớn hoặc khi nút nằm xa, chi phí cáp, nguồn và bảo trì của gateway tăng nhanh. Giải pháp biên cũng giảm dữ liệu truyền: mỗi nút chỉ gửi cảnh báo và thống kê thay vì toàn bộ chuỗi thô. Với 100 nút, lưu lượng có thể giảm từ vài GB/ngày xuống vài MB/ngày, tiết kiệm chi phí SIM và băng thông."),
            p("Chi phí năng lượng là yếu tố thứ hai. Với 18,6 mWh/24 giờ, một pin AA 2.000 mAh ở 3 V cung cấp khoảng 6.000 mWh, đủ cho hơn 300 ngày nếu không có chế độ ngủ. Nếu nút chỉ chạy suy luận 10% thời gian và ngủ 90%, thời lượng pin có thể kéo dài 2–3 năm. Con số này phụ thuộc vào cảm biến và radio, không chỉ vào mô hình. Báo cáo không đo tuổi thọ pin thực tế, nên chỉ nêu như ước lượng."),
            p("Chi phí ẩn lớn nhất là công sức hiệu chỉnh và bảo trì. Mỗi nhà máy có đặc thù riêng; ngưỡng và đặc trưng cần được điều chỉnh. Mỗi lần cập nhật firmware cần kiểm thử lại trên dữ liệu thật. Nếu không có quy trình quản lý phiên bản và log, chi phí bảo trì có thể vượt chi phí phần cứng sau vài năm. Đây là lý do báo cáo nhấn mạnh vào tái lập và ghi log, không chỉ vào mô hình."),
            h("Đe dọa đến tính hợp lệ", 2),
            p("Tính hợp lệ nội tại (internal validity) liên quan đến nguy cơ rò rỉ dữ liệu. Báo cáo chia dữ liệu theo thời gian và chọn ngưỡng trên validation, nhưng vẫn có thể có rò rỉ do cửa sổ chồng lấn giữa train và test. Nếu một cửa sổ test chứa điểm từ train, mô hình có thể đã thấy một phần tín hiệu. Báo cáo giảm nguy cơ bằng cách loại bỏ các cửa sổ có chồng lấn quá 50% với tập train, nhưng không loại bỏ hoàn toàn."),
            p("Tính hợp lệ bên ngoài (external validity) liên quan đến khả năng tổng quát hóa. Bốn bộ dữ liệu bao phủ nhiều lĩnh vực nhưng vẫn chưa đại diện cho mọi cảm biến. Bộ dữ liệu tổng hợp do tác giả sinh có thể đơn giản hơn thực tế. Kết quả trên STM32H747 và ESP32-S3 không đại diện cho mọi MCU. Vì vậy, không nên suy rộng kết quả cho mọi hệ thống IoT mà không kiểm chứng lại."),
            p("Tính hợp lệ cấu trúc (construct validity) liên quan đến việc dùng F1 làm thước đo chính. F1 giả định precision và recall quan trọng như nhau, trong khi chi phí thực tế của false positive và false negative có thể khác nhau. Báo cáo giảm nguy cơ bằng cách báo cáo thêm FAR, MTTD và phân tích lỗi. Tuy nhiên, một thước đo duy nhất vẫn không thể nắm hết giá trị vận hành."),
            p("Tính hợp lệ kết luận (conclusion validity) liên quan đến thống kê. Báo cáo chạy 5 seed và báo cáo khoảng tin cậy 95%, nhưng không hiệu chỉnh cho so sánh nhiều lần. Với 6 phương pháp và 4 bộ dữ liệu, xác suất có ít nhất một so sánh dương tính giả tăng lên. Kết quả nên được xem là bằng chứng định hướng, không phải kết luận thống kê chắc chắn. Các nghiên cứu sau nên dùng kiểm định có hiệu chỉnh như Holm–Bonferroni."),
            p("Những đe dọa này không làm mất giá trị của kết quả, nhưng cần được nêu rõ để người đọc đánh giá đúng. Một báo cáo khoa học tốt không chỉ trình bày kết quả mà còn nêu giới hạn của phương pháp. Đây là lý do báo cáo dành một mục riêng cho tính hợp lệ thay vì gộp vào phần hạn chế chung."),
            p("Tính hợp lệ của phép đo cũng cần xem xét. Độ trễ được đo bằng DWT cycle counter, nhưng thời gian thực thi có thể thay đổi do nhiệt độ, xung nhịp và cache. Báo cáo chạy 1.000 lần và lấy trung vị để giảm ảnh hưởng của nhiễu, nhưng không kiểm soát nhiệt độ phòng. Trong môi trường công nghiệp, nhiệt độ có thể cao hơn, làm giảm xung nhịp và tăng độ trễ. Vì vậy, con số 11,7 ms là cận dưới trong điều kiện phòng thí nghiệm, không phải bảo đảm cho mọi môi trường."),
            p("Một điểm khác là phép đo bộ nhớ. RAM được đọc từ tensor arena và linker map, nhưng không bao gồm bộ nhớ động của FreeRTOS hoặc stack ngắt. Trong thử nghiệm 24 giờ, mức sử dụng cao nhất là 64 KB, nhưng có thể tăng nếu thêm log hoặc xử lý lỗi. Báo cáo cung cấp ngân sách chi tiết để người đọc tự đánh giá, thay vì chỉ nêu một con số tổng."),
            h("Kết luận chương", 2),
            p("Chương này đã trình bày bốn bộ dữ liệu, sáu baseline, kết quả chính, ablation, độ trễ và phân tích lỗi. Mô hình đề xuất đạt F1 0,89, AUC-PR 0,91, độ trễ 11,7 ms và RAM 64 KB sau lượng tử hóa. Các kết quả này trả lời bốn câu hỏi nghiên cứu và tạo cơ sở cho kết luận ở Chương 5."),
        ],
    }


def chuong_5() -> dict:
    return {
        "heading": "Kết luận và hướng phát triển",
        "level": 1,
        "page_break_before": False,
        "blocks": [
            h("Kết quả đạt được", 2),
            p("Báo cáo đã thiết kế, huấn luyện và đánh giá một kiến trúc CNN–LSTM–Autoencoder có attention cho phát hiện bất thường trên dữ liệu cảm biến IoT. Mô hình có 36 nghìn tham số, huấn luyện chỉ trên dữ liệu bình thường, và có thể lượng tử hóa int8 để chạy trên vi điều khiển. Trên bốn bộ dữ liệu, mô hình đạt F1 0,89 và AUC-PR 0,91, cao hơn baseline tốt nhất 0,03–0,05."),
            tbl([col("Mục tiêu", 48), col("Kết quả", 58), col("Bằng chứng", 46)],
                OBJECTIVE_ROWS, "Đối chiếu mục tiêu và kết quả", "Bảng bốn mục tiêu và kết quả tương ứng",
                "Tổng hợp Chương 3 và Chương 4"),
            p("Bốn câu hỏi nghiên cứu đều có câu trả lời. RQ1: kiến trúc lai học được biểu diễn bình thường mà không cần nhãn bất thường. RQ2: mô hình cạnh tranh với baseline nặng hơn và dẫn đầu trên ba trong bốn bộ dữ liệu. RQ3: lượng tử hóa int8 giảm 36% độ trễ và 43% RAM, chỉ mất 0,005 F1. RQ4: drift và bất thường tập thể là hai nhóm lỗi chính, có biện pháp giảm thiểu."),
            h("Hạn chế", 2),
            p("Thứ nhất, dữ liệu tổng hợp do tác giả sinh chưa được kiểm chứng bởi chuyên gia miền. Các kịch bản bất thường có thể đơn giản hơn thực tế. Thứ hai, ngưỡng tĩnh không thích nghi với drift; trong triển khai dài hạn, cần cập nhật định kỳ. Thứ ba, mô hình chưa được thử trên nhiều loại vi điều khiển và chưa đo năng lượng trong thời gian dài. Thứ tư, báo cáo chưa có đánh giá người dùng về khả năng giải thích của attention."),
            p("Một hạn chế khác là cách đánh giá theo cửa sổ. Cửa sổ chồng lấn làm tăng tương quan giữa các mẫu; mặc dù báo cáo chia theo thời gian, kết quả vẫn có thể lạc quan so với triển khai trên dòng dữ liệu hoàn toàn mới. Cần thêm thử nghiệm trên dữ liệu từ cảm biến khác nhà sản xuất và điều kiện môi trường khác."),
            h("Bài học thiết kế", 2),
            p("Quá trình thực hiện để lại bốn bài học. Thứ nhất, độ chính xác không tỷ lệ thuận với số tham số: một mô hình nhỏ nhưng đúng cấu trúc dữ liệu có thể vượt mô hình lớn. Thứ hai, ngưỡng phải được chọn trên validation và hiệu chỉnh lại sau lượng tử hóa; đây là lỗi tốn nhiều thời gian nhất trong thực nghiệm. Thứ ba, attention không chỉ cải thiện độ chính xác mà còn cung cấp tín hiệu giải thích, hữu ích khi thuyết phục người dùng tin vào cảnh báo. Thứ tư, đánh giá phải tách theo loại bất thường; một con số F1 tổng hợp che giấu điểm yếu trên bất thường tập thể."),
            p("Bài học thứ năm là về quy trình. Việc tách cấu hình, dữ liệu và mã nguồn thành các tệp riêng giúp tái lập kết quả nhanh hơn nhiều so với chạy notebook. Mỗi thí nghiệm ghi seed, phiên bản thư viện và hash dữ liệu; nhờ đó, khi một kết quả bất thường xuất hiện, nhóm có thể truy vết trong vài phút thay vì vài ngày."),
            h("Tác động xã hội và đạo đức", 2),
            p("Xử lý tại biên giảm lượng dữ liệu thô phải truyền, nhưng không loại bỏ hoàn toàn rủi ro quyền riêng tư. Một mô hình cảm biến trong nhà có thể suy ra thói quen sinh hoạt, giờ đi làm hoặc số người trong nhà. Ngay cả khi không gửi dữ liệu thô, các đặc trưng và cảnh báo vẫn có thể tiết lộ thông tin. Vì vậy, cần tối thiểu hóa dữ liệu, mã hóa và quy định thời gian lưu trữ."),
            p("Tính công bằng cũng là vấn đề. Dữ liệu huấn luyện chủ yếu đến từ nhà máy và vệ tinh, không đại diện cho mọi môi trường. Một mô hình hoạt động tốt trên SWaT có thể thất bại trên một dây chuyền nhỏ với cảm biến giá rẻ. False negative trong hệ thống an toàn có thể gây hậu quả nghiêm trọng; false positive có thể khiến người vận hành mất niềm tin. Cần đánh giá theo từng bối cảnh, không chỉ theo F1 trung bình."),
            p("Trách nhiệm giải trình là yêu cầu cuối cùng. Khi hệ thống đưa ra cảnh báo, người vận hành cần biết vì sao. Attention cung cấp một tín hiệu, nhưng không đủ để giải thích toàn bộ quyết định. Cần log dữ liệu đầu vào, phiên bản mô hình, ngưỡng và điểm số; cần quy trình khiếu nại và sửa sai. Một mô hình không thể giải thích sẽ khó được chấp nhận trong môi trường có trách nhiệm pháp lý."),
            p("Về môi trường, thiết bị biên giúp giảm năng lượng truyền dẫn nhưng tạo ra rác thải điện tử nếu không được thu hồi. Tuổi thọ pin và khả năng cập nhật firmware là yếu tố thiết kế quan trọng. Một giải pháp bền vững không chỉ giảm tiêu thụ năng lượng mà còn kéo dài tuổi thọ thiết bị và cho phép sửa chữa. Báo cáo chưa đo tác động vòng đời, nhưng đây là hướng cần xét trong nghiên cứu tiếp theo."),
            p("Ở Việt Nam, việc xử lý dữ liệu cá nhân chịu sự điều chỉnh của Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân. Dữ liệu cảm biến trong nhà có thể là dữ liệu cá nhân nếu liên quan đến một người cụ thể. Hệ thống cần có sự đồng ý, mục đích rõ ràng, thời hạn lưu trữ và biện pháp bảo mật. Xử lý tại biên giúp giảm dữ liệu truyền đi nhưng không thay thế nghĩa vụ tuân thủ. Đây là lý do báo cáo khuyến nghị thiết kế quyền riêng tư ngay từ đầu, không bổ sung sau."),
            h("Hướng phát triển", 2),
            bullets([
                "**Ngưỡng thích nghi:** cập nhật μ, σ theo cửa sổ trượt 7 ngày, có phát hiện drift để tránh trôi ngưỡng.",
                "**Học trực tuyến có kiểm soát:** cập nhật mô hình với dữ liệu mới nhưng giữ một bộ nhớ kinh nghiệm để tránh quên thảm họa.",
                "**Đặc trưng tương quan:** thêm graph neural network nhẹ hoặc attention chéo kênh để bắt bất thường tập thể.",
                "**Mô hình lai phần cứng:** tối ưu kernel convolution cho DSP, thử nghiệm trên ESP32-S3 và các MCU có NPU nhỏ.",
                "**Đánh giá người dùng:** đo thời gian phản ứng và độ tin cậy của kỹ thuật viên với cảnh báo có giải thích attention.",
                "**Mở rộng dữ liệu:** thu thập dữ liệu thật từ ít nhất hai nhà máy và một hệ thống nông nghiệp, có nhãn từ chuyên gia.",
            ]),
            h("Kết luận", 2),
            p("Phát hiện bất thường trên thiết bị biên là bài toán cân bằng nhiều mục tiêu. Kết quả của báo cáo cho thấy một kiến trúc nhỏ, có attention và được lượng tử hóa đúng cách có thể đạt độ chính xác gần mô hình lớn trong khi vẫn chạy trong ngân sách tài nguyên của vi điều khiển. Đóng góp chính không phải là một con số F1 cao nhất, mà là một quy trình có thể lặp lại: chọn kiến trúc, chọn ngưỡng trên validation, lượng tử hóa, hiệu chỉnh ngưỡng, và phân tích lỗi theo loại."),
            p("Trong tương lai, nhóm nghiên cứu sẽ thử nghiệm trên dữ liệu thật, mở rộng cơ chế thích nghi drift và đánh giá với người dùng cuối. Những bước này sẽ cho biết mô hình có thực sự hữu ích ngoài phòng thí nghiệm hay không."),
            p("Ở góc độ rộng hơn, bài toán này là một ví dụ của xu hướng đưa trí tuệ nhân tạo ra khỏi trung tâm dữ liệu. Xu hướng này thay đổi cách thiết kế hệ thống: mô hình, phần cứng và quy trình vận hành phải được thiết kế cùng nhau. Báo cáo hy vọng đóng góp một điểm dữ liệu nhỏ vào cuộc thảo luận đó."),
        ],
    }


# ---------------------------------------------------------------------------
# References and appendices
# ---------------------------------------------------------------------------

REFERENCES = [
    {"key": "chandola2009", "label": "[1]", "text": "V. Chandola, A. Banerjee, V. Kumar. 2009. Anomaly detection: A survey. ACM Computing Surveys, 41(3), 1–58. https://doi.org/10.1145/1541880.1541882."},
    {"key": "malhotra2015", "label": "[2]", "text": "P. Malhotra, L. Vig, G. Shroff, P. Agarwal. 2015. Long Short Term Memory Networks for Anomaly Detection in Time Series. Proceedings of ESANN 2015, 89–94."},
    {"key": "hundman2018", "label": "[3]", "text": "K. Hundman, V. Constantinou, C. Laporte, I. Colwell, T. Soderstrom. 2018. Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding. KDD 2018, 387–395. https://doi.org/10.1145/3219819.3219845."},
    {"key": "su2019", "label": "[4]", "text": "Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, D. Pei. 2019. Robust Anomaly Detection for Multivariate Time Series through Stochastic Recurrent Neural Network. KDD 2019, 2828–2837. https://doi.org/10.1145/3292500.3330672."},
    {"key": "audibert2020", "label": "[5]", "text": "J. Audibert, M. Michiardi, F. Guyard, S. Marti, M. A. Zuluaga. 2020. USAD: UnSupervised Anomaly Detection on Multivariate Time Series. KDD 2020, 3395–3404. https://doi.org/10.1145/3394486.3403392."},
    {"key": "banbury2021", "label": "[6]", "text": "C. Banbury, V. J. Reddi, P. Torelli, et al. 2021. MLPerf Tiny Benchmark. Proceedings of the NeurIPS Track on Datasets and Benchmarks."},
    {"key": "hochreiter1997", "label": "[7]", "text": "S. Hochreiter, J. Schmidhuber. 1997. Long Short-Term Memory. Neural Computation, 9(8), 1735–1780. https://doi.org/10.1162/neco.1997.9.8.1735."},
    {"key": "vaswani2017", "label": "[8]", "text": "A. Vaswani, N. Shazeer, N. Parmar, et al. 2017. Attention Is All You Need. Advances in Neural Information Processing Systems 30, 5998–6008."},
    {"key": "jacob2018", "label": "[9]", "text": "B. Jacob, S. Kligys, B. Chen, et al. 2018. Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference. CVPR 2018, 2704–2713."},
    {"key": "kingma2015", "label": "[10]", "text": "D. P. Kingma, J. Ba. 2015. Adam: A Method for Stochastic Optimization. ICLR 2015."},
    {"key": "ioffe2015", "label": "[11]", "text": "S. Ioffe, C. Szegedy. 2015. Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift. ICML 2015, 448–456."},
    {"key": "goyal2020", "label": "[12]", "text": "A. Goyal, A. Bochkovskiy, A. K. Roy, et al. 2020. TinyML: A Review of Machine Learning on Microcontrollers. arXiv:2007.08062."},
]


def appendix() -> list[dict]:
    return [
        {
            "letter": "A",
            "title": "Cấu hình huấn luyện và triển khai",
            "blocks": [
                p("Bảng A.1 tóm tắt cấu hình được dùng để tái lập kết quả. Mã nguồn huấn luyện, script xuất TFLite và firmware mẫu được đặt trong thư mục `code/` của phụ lục điện tử; báo cáo chỉ in các tham số chính."),
                tbl([col("Tham số", 48), col("Giá trị", 48), col("Ghi chú", 54)],
                    CONFIG_ROWS, "Cấu hình huấn luyện và triển khai", "Bảng tham số cấu hình",
                    "Tệp config.yaml của tác giả"),
                p("Quy trình tái lập gồm bốn lệnh: chuẩn bị dữ liệu, huấn luyện float32, QAT và xuất TFLite. Mỗi lệnh ghi log riêng và seed vào tên tệp để bảo đảm khả năng truy vết. Kết quả trong báo cáo dùng seed 42; các seed còn lại nằm trong `results/`."),
                {"type": "paragraph", "text": "Mã giả huấn luyện:\n\n```\nfor epoch in range(80):\n    for window in normal_loader:\n        z = encoder(window)\n        x_hat = decoder(z)\n        loss = mse(window, x_hat) + 1e-4 * ||z||^2\n        loss.backward(); optimizer.step()\n    if early_stop(validation_loss): break\nquantize_qat(model, calibration_loader)\nthreshold = mean(score) + 3.0 * std(score)\nexport_tflite(model, \"model_int8.tflite\")\n```"},
            ],
        },
        {
            "letter": "B",
            "title": "Kết quả chi tiết theo lớp cảm biến",
            "blocks": [
                p("Bảng B.1 trình bày precision, recall và F1 theo từng lớp cảm biến trên bộ dữ liệu tổng hợp. Các lớp có tương quan mạnh với nhau (nhiệt độ, độ ẩm) đạt kết quả cao hơn; lớp rung có nhiễu cao và recall thấp hơn."),
                tbl([col("Lớp", 44), col("Precision", 26), col("Recall", 26), col("F1", 26), col("Support", 26)],
                    PER_CLASS_ROWS, "Kết quả theo lớp cảm biến", "Bảng precision, recall, F1 theo sáu lớp",
                    "Trung bình 5 seed, bộ dữ liệu tổng hợp"),
                p("Kết quả này nhất quán với phân tích lỗi ở Bảng 4.9: lớp rung có nhiều false negative do bất thường tập thể và nhiễu. Hướng tiếp theo là thêm đặc trưng phổ và attention chéo kênh cho lớp này."),
            ],
        },
    ]


def build() -> dict:
    return {
        "meta": {
            "title": "Phát hiện bất thường trên dữ liệu cảm biến IoT bằng kiến trúc học sâu nhẹ",
            "subtitle": "Đồ án tốt nghiệp ngành Khoa học máy tính",
            "author": "Nguyễn Văn An",
            "student_id": "20201234",
            "field": "Khoa học máy tính",
            "supervisor": "TS. Trần Minh Khoa",
            "organization": "Trường Đại học Bách khoa Hà Nội",
            "document_id": "DATN-2026-014",
            "version": "1.0",
            "date": "2026-12-15",
            "language": "vi-VN",
            "classification": "",
            "keywords": ["IoT", "phát hiện bất thường", "autoencoder", "CNN-LSTM", "TinyML"],
        },
        "cover": {"enabled": True, "layout": "thesis"},
        "front_matter": front_matter(),
        "sections": [mo_dau(), chuong_1(), chuong_2(), chuong_3(), chuong_4(), chuong_5()],
        "appendix": appendix(),
        "references": {"enabled": True, "title": "TÀI LIỆU THAM KHẢO",
                       "items": REFERENCES},
    }


if __name__ == "__main__":
    path = HERE / "scientific_report_spec.json"
    path.write_text(json.dumps(build(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
