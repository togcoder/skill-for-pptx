"""Build the T047 standards-controlled annual/ESG report spec.

The report declares a concrete standards stack and proves each control in a
front-matter table. Content is synthetic but internally consistent.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STANDARD = json.loads((ROOT / "domains/docx/data/report_standard.json").read_text(encoding="utf-8"))


def c(text, **kw):
    return {"text": str(text), **kw}


def tbl(columns, rows, caption="", alt="", source="", **kw):
    spec = {
        "type": "table",
        "advanced": True,
        "columns": columns,
        "rows": rows,
        "caption": caption,
        "alt": alt or caption,
        "source": source,
        **kw,
    }
    return spec


def col(header, width, align="left"):
    return {"header": header, "width_mm": width, "align": align}


def status(text):
    if text.startswith("met"):
        label = "Đạt (tự công bố)" if "self-declared" in text else "Đạt"
        return c(label, fill="E2EFDA", bold=True, align="center")
    if text.startswith("partly"):
        return c("Một phần", fill="FFF2CC", bold=True, align="center")
    return c("Hạn chế", fill="FCE4D6", bold=True, align="center")


def build() -> dict:
    control_rows = []
    for ctrl in STANDARD["controls"]:
        control_rows.append([
            c(ctrl["id"], bold=True),
            c(ctrl["standard"]),
            c(ctrl["control"]),
            c(ctrl["evidence"]),
            status(ctrl["status"]),
        ])

    kpis = [
        {"label": "Doanh thu", "value": "940 tỷ", "delta": "+20,4% so với 2025"},
        {"label": "EBITDA", "value": "166 tỷ", "delta": "biên 17,7%"},
        {"label": "Lợi nhuận sau thuế", "value": "118 tỷ", "delta": "+28,3%"},
        {"label": "Nhân sự", "value": "880", "delta": "+70 người"},
    ]

    summary_rows = [
        [c("Doanh thu", bold=True), c("940", align="right"), c("781", align="right"), c("+20,4%", align="right", fill="E2EFDA"), c("Tăng nhờ kênh Smart Home và xuất khẩu")],
        [c("EBITDA", bold=True), c("166", align="right"), c("132", align="right"), c("+25,8%", align="right", fill="E2EFDA"), c("Biên 17,7% (2025: 16,9%)")],
        [c("Lợi nhuận sau thuế", bold=True), c("118", align="right"), c("92", align="right"), c("+28,3%", align="right", fill="E2EFDA"), c("Một lần hoàn nhập thuế 4,2 tỷ")],
        [c("Nhân sự", bold=True), c("880", align="right"), c("810", align="right"), c("+8,6%", align="right"), c("Tuyển 112, nghỉ 42")],
        [c("Cường độ phát thải", bold=True), c("24,73", align="right"), c("30,26", align="right"), c("-18,3%", align="right", fill="E2EFDA"), c("tCO₂e/tỷ VND doanh thu")],
        [c("Giờ đào tạo/người", bold=True), c("20,9", align="right"), c("18,5", align="right"), c("+13,0%", align="right", fill="E2EFDA"), c("Tổng 18.400 giờ")],
    ]

    segment_rows = [
        [c("Smart Home", bold=True), c("612", align="right"), c("65%", align="right"), c("34,0%", align="right"), c("Camera AI, hub, cảm biến")],
        [c("Smart Care", bold=True), c("214", align="right"), c("23%", align="right"), c("41,0%", align="right"), c("Thiết bị chăm sóc sức khỏe tại nhà")],
        [c("Platform & dịch vụ", bold=True), c("114", align="right"), c("12%", align="right"), c("52,0%", align="right"), c("Thuê bao ANSMART Cloud, tích hợp API")],
    ]

    financial_rows = [
        [c("Doanh thu", bold=True), c("420", align="right"), c("512", align="right"), c("638", align="right"), c("781", align="right"), c("940", align="right")],
        [c("EBITDA", bold=True), c("64", align="right"), c("82", align="right"), c("104", align="right"), c("132", align="right"), c("166", align="right")],
        [c("Biên EBITDA", bold=True), c("15,2%", align="right"), c("16,0%", align="right"), c("16,3%", align="right"), c("16,9%", align="right"), c("17,7%", align="right")],
        [c("Lợi nhuận sau thuế", bold=True), c("42", align="right"), c("55", align="right"), c("71", align="right"), c("92", align="right"), c("118", align="right")],
        [c("Nhân sự", bold=True), c("620", align="right"), c("680", align="right"), c("740", align="right"), c("810", align="right"), c("880", align="right")],
        [c("Phát thải (tCO₂e)", bold=True), c("25.350", align="right"), c("24.680", align="right"), c("24.020", align="right"), c("23.630", align="right"), c("23.250", align="right")],
    ]

    cost_rows = [
        [c("Giá vốn hàng bán", bold=True), c("598", align="right"), c("63,6%", align="right"), c("595", align="right")],
        [c("Lợi nhuận gộp", bold=True), c("342", align="right"), c("36,4%", align="right"), c("331", align="right")],
        [c("R&D", bold=True), c("78", align="right"), c("8,3%", align="right"), c("66", align="right")],
        [c("Bán hàng & marketing", bold=True), c("62", align="right"), c("6,6%", align="right"), c("58", align="right")],
        [c("Quản lý doanh nghiệp", bold=True), c("36", align="right"), c("3,8%", align="right"), c("35", align="right")],
        [c("EBITDA", bold=True), c("166", align="right", fill="E2EFDA"), c("17,7%", align="right", fill="E2EFDA"), c("132", align="right")],
    ]

    ops_rows = [
        [c("NPS", bold=True), c("62", align="right"), c("58", align="right"), c("+4", align="right"), c("Khảo sát 3.240 khách hàng")],
        [c("Giao hàng đúng hạn", bold=True), c("96,4%", align="right"), c("94,1%", align="right"), c("+2,3 điểm", align="right"), c("Đơn hàng B2B, 4 nhà máy")],
        [c("Tỷ lệ lỗi sản phẩm", bold=True), c("0,42%", align="right"), c("0,55%", align="right"), c("-0,13 điểm", align="right"), c("Lô xuất xưởng")],
        [c("Điện năng tiêu thụ", bold=True), c("12,4 GWh", align="right"), c("11,9 GWh", align="right"), c("+4,2%", align="right"), c("Sản lượng tăng 18%")],
        [c("Nước tiêu thụ", bold=True), c("38.000 m³", align="right"), c("36.500 m³", align="right"), c("+4,1%", align="right"), c("Tái sử dụng 22%")],
        [c("LTIFR", bold=True), c("0,21", align="right"), c("0,28", align="right"), c("-25%", align="right"), c("Số vụ mất ngày công/1 triệu giờ")],
    ]

    board_rows = [
        [c("Trần Minh An", bold=True), c("Chủ tịch HĐQT"), c("Không điều hành"), c("7/7"), c("Chiến lược, M&A")],
        [c("Nguyễn Thu Hà", bold=True), c("Thành viên HĐQT"), c("Điều hành (TGĐ)"), c("7/7"), c("Điều hành, sản phẩm")],
        [c("Lê Quang Dũng", bold=True), c("Thành viên HĐQT"), c("Không điều hành"), c("6/7"), c("Tài chính, kiểm toán")],
        [c("Phạm Mai Lan", bold=True), c("Thành viên HĐQT"), c("Độc lập"), c("7/7"), c("ESG, nhân sự")],
        [c("Vũ Hoàng Nam", bold=True), c("Thành viên HĐQT"), c("Độc lập"), c("7/7"), c("Công nghệ, rủi ro")],
        [c("Đỗ Thị Kim", bold=True), c("Thành viên HĐQT"), c("Độc lập"), c("6/7"), c("Khách hàng, thị trường")],
    ]

    committee_rows = [
        [c("Kiểm toán", bold=True), c("Phạm Mai Lan (chủ tịch), Vũ Hoàng Nam, Lê Quang Dũng"), c("4"), c("Giám sát kiểm toán, soát xét BCTC")],
        [c("Chiến lược & đầu tư", bold=True), c("Trần Minh An (chủ tịch), Nguyễn Thu Hà, Đỗ Thị Kim"), c("3"), c("Kế hoạch 5 năm, M&A")],
        [c("ESG & rủi ro", bold=True), c("Phạm Mai Lan (chủ tịch), Vũ Hoàng Nam, Nguyễn Thu Hà"), c("4"), c("Khí hậu, chuỗi cung ứng, tuân thủ")],
    ]

    risk_rows = [
        [c("R1", bold=True), c("Gián đoạn chuỗi cung ứng linh kiện"), c("4"), c("4"), c("Đa nguồn 2 nhà cung cấp; tồn kho an toàn 8 tuần"), c("COO")],
        [c("R2", bold=True), c("Tấn công mạng vào nền tảng Cloud"), c("3"), c("5"), c("SOC 24/7, ISO 27001, diễn tập ứng cứu"), c("CTO")],
        [c("R3", bold=True), c("Thay đổi quy định dữ liệu tại EU"), c("3"), c("4"), c("Rà soát luật theo quý; DPIA cho sản phẩm mới"), c("Legal")],
        [c("R4", bold=True), c("Biến động tỷ giá VND/USD"), c("4"), c("3"), c("Hợp đồng forward 60% nhu cầu 6 tháng"), c("CFO")],
        [c("R5", bold=True), c("Thiếu hụt nhân sự R&D"), c("3"), c("3"), c("Học bổng, cổ phiếu thưởng, đối tác đại học"), c("CHRO")],
        [c("R6", bold=True), c("Rủi ro khí hậu vật lý (lũ lụt)"), c("2"), c("4"), c("Nâng nền nhà máy, bảo hiểm, kế hoạch BCP"), c("COO")],
    ]

    heat = [
        [c("5 (Cao)", bold=True), c("", fill="FFF2CC"), c("", fill="FFF2CC"), c("", fill="FCE4D6"), c("", fill="F8CBAD"), c("", fill="F8CBAD")],
        [c("4", bold=True), c("", fill="E2EFDA"), c("", fill="FFF2CC"), c("R4", fill="FCE4D6"), c("R1", fill="F8CBAD"), c("", fill="F8CBAD")],
        [c("3", bold=True), c("", fill="E2EFDA"), c("", fill="E2EFDA"), c("R5", fill="FFF2CC"), c("R3", fill="FCE4D6"), c("R2", fill="F8CBAD")],
        [c("2", bold=True), c("", fill="E2EFDA"), c("", fill="E2EFDA"), c("", fill="FFF2CC"), c("R6", fill="FCE4D6"), c("", fill="FCE4D6")],
        [c("1", bold=True), c("", fill="E2EFDA"), c("", fill="E2EFDA"), c("", fill="E2EFDA"), c("", fill="FFF2CC"), c("", fill="FFF2CC")],
    ]

    materiality = [
        [c("5", bold=True), c("", fill="FFF2CC"), c("", fill="FCE4D6"), c("", fill="FCE4D6"), c("T2", fill="F8CBAD"), c("T10", fill="F8CBAD")],
        [c("4", bold=True), c("", fill="E2EFDA"), c("", fill="FFF2CC"), c("T4", fill="FCE4D6"), c("T1", fill="F8CBAD"), c("T8", fill="F8CBAD")],
        [c("3", bold=True), c("", fill="E2EFDA"), c("T7", fill="FFF2CC"), c("T3", fill="FCE4D6"), c("", fill="FCE4D6"), c("T5", fill="F8CBAD")],
        [c("2", bold=True), c("", fill="E2EFDA"), c("T6", fill="E2EFDA"), c("", fill="FFF2CC"), c("T9", fill="FCE4D6"), c("", fill="FCE4D6")],
        [c("1", bold=True), c("", fill="E2EFDA"), c("", fill="E2EFDA"), c("", fill="E2EFDA"), c("", fill="FFF2CC"), c("", fill="FFF2CC")],
    ]

    topic_rows = [
        [c("T1", bold=True), c("Chất lượng dữ liệu và quyền riêng tư"), c("4"), c("4"), c("Trọng yếu cao")],
        [c("T2", bold=True), c("An ninh mạng và liên tục kinh doanh"), c("5"), c("4"), c("Trọng yếu cao")],
        [c("T3", bold=True), c("Đổi mới sản phẩm và IP"), c("3"), c("3"), c("Trọng yếu")],
        [c("T4", bold=True), c("Phát thải và hiệu quả năng lượng"), c("4"), c("3"), c("Trọng yếu")],
        [c("T5", bold=True), c("Chuỗi cung ứng có trách nhiệm"), c("3"), c("5"), c("Trọng yếu cao")],
        [c("T6", bold=True), c("Đa dạng và hòa nhập"), c("2"), c("2"), c("Theo dõi")],
        [c("T7", bold=True), c("An toàn và sức khỏe nghề nghiệp"), c("3"), c("2"), c("Theo dõi")],
        [c("T8", bold=True), c("Tác động kinh tế địa phương"), c("4"), c("5"), c("Trọng yếu cao")],
        [c("T9", bold=True), c("Tiếng nói khách hàng và NPS"), c("2"), c("4"), c("Trọng yếu")],
        [c("T10", bold=True), c("Quản trị và minh bạch thuế"), c("5"), c("5"), c("Trọng yếu cao")],
    ]

    stakeholder_rows = [
        [c("Khách hàng", bold=True), c("Khảo sát NPS, hộp thư hỗ trợ, hội đồng người dùng"), c("Hàng tháng"), c("NPS, tỷ lệ lỗi, thời gian phản hồi")],
        [c("Nhân viên", bold=True), c("Khảo sát gắn kết, đối thoại công đoàn"), c("6 tháng"), c("Gắn kết, đào tạo, LTIFR")],
        [c("Nhà đầu tư", bold=True), c("Đại hội cổ đông, công bố thông tin, roadshow"), c("Quý"), c("Doanh thu, EBITDA, ESG")],
        [c("Nhà cung cấp", bold=True), c("Đánh giá ESG, hội nghị nhà cung cấp"), c("Năm"), c("Tỷ lệ đánh giá, OTIF")],
        [c("Cộng đồng", bold=True), c("Đối thoại địa phương, quỹ học bổng"), c("6 tháng"), c("Việc làm, đào tạo, tác động môi trường")],
    ]

    emission_rows = [
        [c("Phạm vi 1", bold=True), c("1.250", align="right"), c("1.280", align="right"), c("1.200", align="right"), c("-2,3%", align="right")],
        [c("Phạm vi 2 (thị trường)", bold=True), c("3.400", align="right"), c("3.550", align="right"), c("3.150", align="right"), c("-4,2%", align="right")],
        [c("Phạm vi 3", bold=True), c("18.600", align="right"), c("18.800", align="right"), c("17.500", align="right"), c("-1,1%", align="right")],
        [c("Tổng", bold=True), c("23.250", align="right", fill="E2EFDA"), c("23.630", align="right"), c("21.850", align="right"), c("-1,6%", align="right")],
        [c("Cường độ (tCO₂e/tỷ VND)", bold=True), c("24,73", align="right", fill="E2EFDA"), c("30,26", align="right"), c("24,28", align="right"), c("-18,3%", align="right")],
    ]

    workforce_rows = [
        [c("Tổng nhân sự", bold=True), c("880", align="right"), c("810", align="right"), c("+8,6%", align="right")],
        [c("Nữ giới", bold=True), c("392 (44,5%)", align="right"), c("355 (43,8%)", align="right"), c("+37", align="right")],
        [c("Nữ ở cấp quản lý", bold=True), c("38%", align="right"), c("35%", align="right"), c("+3 điểm", align="right")],
        [c("Nhân sự dưới 30", bold=True), c("31%", align="right"), c("30%", align="right"), c("+1 điểm", align="right")],
        [c("Giờ đào tạo", bold=True), c("18.400", align="right"), c("14.985", align="right"), c("+22,8%", align="right")],
        [c("Tỷ lệ nghỉ việc", bold=True), c("4,8%", align="right"), c("5,2%", align="right"), c("-0,4 điểm", align="right")],
    ]

    supplier_rows = [
        [c("Tier 1 — linh kiện chính", bold=True), c("86"), c("78%"), c("Đánh giá ESG 2 năm/lần"), c("4 nhà cung cấp chiến lược")],
        [c("Tier 2 — gia công", bold=True), c("124"), c("54%"), c("Tự đánh giá + mẫu kiểm tra"), c("Ưu tiên 20 nhà cung cấp")],
        [c("Dịch vụ & logistics", bold=True), c("42"), c("61%"), c("Điều khoản ESG trong hợp đồng"), c("3 nhà vận chuyển chính")],
    ]

    data_rows = [
        [c("Doanh thu, EBITDA", bold=True), c("ERP + BCTC kiểm toán"), c("CFO"), c("Đối chiếu 3 chiều; khóa sổ hàng tháng"), c("Không")],
        [c("Phát thải Scope 1–3", bold=True), c("Đồng hồ, hóa đơn, mô hình chi tiêu"), c("ESG"), c("Hệ số phát thải có nguồn; soát xét nội bộ"), c("Scope 3 2025: +1,2%")],
        [c("Nhân sự & đào tạo", bold=True), c("HRIS"), c("CHRO"), c("Đối chiếu bảng lương; kiểm tra 10% mẫu"), c("Không")],
        [c("NPS", bold=True), c("Khảo sát độc lập"), c("CMO"), c("Cỡ mẫu 3.240; biên ±1,7 điểm"), c("Không")],
        [c("Nhà cung cấp", bold=True), c("Hồ sơ đánh giá"), c("COO"), c("Mẫu 20%; hiệu lực 24 tháng"), c("Không")],
    ]

    gri_rows = [
        [c("GRI 2-1", bold=True), c("Tên, địa chỉ, hình thức pháp lý"), c("Mục 2.1; Phụ lục C")],
        [c("GRI 2-2", bold=True), c("Các thực thể trong báo cáo"), c("Mục 1.2")],
        [c("GRI 2-3", bold=True), c("Kỳ báo cáo, tần suất, đầu mối"), c("Mục 1.1")],
        [c("GRI 2-4", bold=True), c("Trình bày lại thông tin"), c("Mục 8.2")],
        [c("GRI 2-5", bold=True), c("Đảm bảo bên ngoài"), c("Lời nói đầu; Mục 8.3")],
        [c("GRI 2-6", bold=True), c("Hoạt động, chuỗi giá trị"), c("Mục 2.2")],
        [c("GRI 2-7", bold=True), c("Nhân sự"), c("Mục 7.1; Bảng 7.1")],
        [c("GRI 2-9", bold=True), c("Cơ cấu quản trị"), c("Mục 5.1; Bảng 5.1")],
        [c("GRI 2-10", bold=True), c("Đề cử và lựa chọn HĐQT"), c("Mục 5.1")],
        [c("GRI 2-11", bold=True), c("Chủ tịch HĐQT"), c("Mục 5.1")],
        [c("GRI 2-12", bold=True), c("Vai trò HĐQT trong giám sát tác động"), c("Mục 5.2")],
        [c("GRI 2-13", bold=True), c("Ủy quyền quản lý tác động"), c("Mục 5.2")],
        [c("GRI 2-14", bold=True), c("Vai trò HĐQT trong báo cáo"), c("Lời nói đầu")],
        [c("GRI 2-15", bold=True), c("Xung đột lợi ích"), c("Mục 5.3")],
        [c("GRI 2-16", bold=True), c("Trao đổi mối quan tâm"), c("Mục 5.3")],
        [c("GRI 2-22", bold=True), c("Tuyên bố chiến lược phát triển bền vững"), c("Mục 2.3")],
        [c("GRI 2-23", bold=True), c("Cam kết chính sách"), c("Mục 6.2")],
        [c("GRI 2-24", bold=True), c("Nhúng cam kết vào thực thi"), c("Mục 6.2")],
        [c("GRI 2-25", bold=True), c("Quy trình khắc phục tác động tiêu cực"), c("Mục 6.3")],
        [c("GRI 2-26", bold=True), c("Cơ chế tư vấn và khiếu nại"), c("Mục 6.3")],
        [c("GRI 2-27", bold=True), c("Tuân thủ pháp luật"), c("Mục 6.3")],
        [c("GRI 2-28", bold=True), c("Hiệp hội thành viên"), c("Mục 6.4")],
        [c("GRI 2-29", bold=True), c("Cách tiếp cận bên liên quan"), c("Mục 6.1")],
        [c("GRI 2-30", bold=True), c("Thỏa ước lao động tập thể"), c("Mục 7.2")],
        [c("GRI 3-1", bold=True), c("Quy trình xác định trọng yếu"), c("Mục 6.1; Hình 6.1")],
        [c("GRI 3-2", bold=True), c("Danh mục chủ đề trọng yếu"), c("Bảng 6.2")],
        [c("GRI 3-3", bold=True), c("Quản lý từng chủ đề trọng yếu"), c("Mục 6.2; 7; 8")],
        [c("GRI 305-1", bold=True), c("Phát thải Scope 1"), c("Bảng 7.1")],
        [c("GRI 305-2", bold=True), c("Phát thải Scope 2"), c("Bảng 7.1")],
        [c("GRI 305-3", bold=True), c("Phát thải Scope 3"), c("Bảng 7.1; Mục 8.2")],
        [c("GRI 305-4", bold=True), c("Cường độ phát thải"), c("Công thức 7.1; Bảng 7.1")],
        [c("GRI 305-5", bold=True), c("Giảm phát thải và mục tiêu"), c("Mục 7.3")],
        [c("GRI 401-1", bold=True), c("Tuyển dụng và nghỉ việc"), c("Bảng 7.2")],
        [c("GRI 404-1", bold=True), c("Giờ đào tạo/người"), c("Bảng 7.2")],
        [c("GRI 405-1", bold=True), c("Đa dạng trong quản trị"), c("Bảng 5.1; 7.2")],
        [c("GRI 413-1", bold=True), c("Tác động cộng đồng địa phương"), c("Mục 7.4")],
        [c("GRI 418-1", bold=True), c("Khiếu nại về quyền riêng tư"), c("Mục 8.3")],
    ]

    years = [
        [c("Doanh thu (tỷ VND)", bold=True), c("420"), c("512"), c("638"), c("781"), c("940")],
        [c("EBITDA (tỷ VND)", bold=True), c("64"), c("82"), c("104"), c("132"), c("166")],
        [c("Lợi nhuận sau thuế (tỷ VND)", bold=True), c("42"), c("55"), c("71"), c("92"), c("118")],
        [c("Nhân sự (người)", bold=True), c("620"), c("680"), c("740"), c("810"), c("880")],
        [c("Phát thải Scope 1+2 (tCO₂e)", bold=True), c("5.550"), c("5.280"), c("5.020"), c("4.830"), c("4.650")],
        [c("Phát thải Scope 3 (tCO₂e)", bold=True), c("19.800"), c("19.400"), c("19.000"), c("18.800"), c("18.600")],
        [c("Giờ đào tạo (giờ)", bold=True), c("7.400"), c("9.600"), c("12.100"), c("14.985"), c("18.400")],
    ]

    glossary_rows = [
        [c("ANSMART", bold=True), c("Công ty CP Thiết bị Thông minh An Nhiên")],
        [c("EBITDA", bold=True), c("Lợi nhuận trước lãi vay, thuế và khấu hao")],
        [c("GRI", bold=True), c("Global Reporting Initiative — bộ tiêu chuẩn báo cáo phát triển bền vững")],
        [c("LTIFR", bold=True), c("Tần suất tai nạn lao động mất ngày công trên 1 triệu giờ làm việc")],
        [c("NPS", bold=True), c("Net Promoter Score — chỉ số thiện chí giới thiệu")],
        [c("Scope 1/2/3", bold=True), c("Phân loại phát thải khí nhà kính theo GRI 305 / GHG Protocol")],
        [c("Tier 1/2", bold=True), c("Nhà cung cấp trực tiếp / gián tiếp trong chuỗi cung ứng")],
        [c("tCO₂e", bold=True), c("Tấn CO₂ tương đương")],
        [c("DPIA", bold=True), c("Đánh giá tác động quyền riêng tư dữ liệu")],
        [c("OTIF", bold=True), c("Giao đúng hạn và đủ số lượng")],
    ]

    sections = [
        {
            "heading": "Tổng quan và phạm vi báo cáo",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Báo cáo thường niên và ESG 2026 của ANSMART trình bày kết quả kinh doanh, quản trị và tác động môi trường – xã hội của công ty trong kỳ 2026-01-01 đến 2026-12-31. Báo cáo được lập cho HĐQT, cổ đông, nhà đầu tư và các bên liên quan; nội dung ESG được chuẩn bị theo GRI 1: Foundation 2021 {{cite:gri1}}."},
                {"type": "key_values", "items": kpis},
                {"type": "table", "advanced": True,
                 "columns": [col("Hạng mục", 42), col("Nội dung", 110)],
                 "rows": [
                     [c("Tên tài liệu", bold=True), c("Báo cáo thường niên và ESG 2026")],
                     [c("Mã tài liệu", bold=True), c("ANSMART-AR-2026")],
                     [c("Kỳ báo cáo", bold=True), c("2026-01-01 → 2026-12-31")],
                     [c("Phạm vi", bold=True), c("ANSMART và 3 công ty con; nhà máy Bình Dương, R&D TP.HCM")],
                     [c("Đơn vị tiền tệ", bold=True), c("tỷ VND; 1 tỷ = 10⁹ VND")],
                     [c("Tiêu chuẩn", bold=True), c("ISO 7144:1986; ISO 2145; ISO 690:2021; ISO 80000-1; ISO 8601-1; WCAG 2.2 AA; GRI 1/2/3/305")],
                     [c("Đảm bảo", bold=True), c("BCTC kiểm toán độc lập; nội dung ESG tự công bố, chưa được đảm bảo bên ngoài")],
                 ], "alt": "Thông tin kỳ báo cáo và phạm vi", "caption": ""},
                {"type": "callout", "title": "Cách đọc báo cáo", "text": "Số liệu tài chính làm tròn đến 1 tỷ VND; tỷ lệ % làm tròn 1 chữ số thập phân. Chênh lệch nhỏ có thể do làm tròn. Các số liệu trình bày lại được nêu rõ ở Mục 8.2.", "fill": "EAF1F8"},
                {"type": "callout", "title": "Tuyên bố tuân thủ", "text": "Báo cáo được lập theo GRI 1: Foundation 2021 và GRI 2/3/305 ở mức tự công bố. Cấu trúc và đánh số theo ISO 7144/ISO 2145; tài liệu tham khảo theo ISO 690:2021. PDF/UA là mục tiêu nhưng chưa được xác nhận bằng veraPDF/PAC; đây là giới hạn được công bố, không phải một tuyên bố tuân thủ.", "fill": "EAF1F8"},
                {"type": "paragraph", "text": "Báo cáo ưu tiên tính có thể kiểm chứng: mỗi bảng có nguồn, mỗi hình có số và chú thích, mỗi công thức có số hiệu; danh mục kiểm soát tiêu chuẩn ở phần Lời nói đầu nêu rõ điều khoản và bằng chứng."},
            ],
        },
        {
            "heading": "Tóm tắt điều hành",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Năm 2026 là năm tăng tốc có kiểm soát. Doanh thu đạt 940 tỷ VND, tăng 20,4%; EBITDA đạt 166 tỷ, biên 17,7%. Tăng trưởng đến từ camera AI thế hệ mới, mở rộng kênh xuất khẩu và doanh thu thuê bao Cloud."},
                {"type": "table", "advanced": True,
                 "columns": [col("Chỉ tiêu", 36), col("2026", 22, "right"), col("2025", 22, "right"), col("Thay đổi", 26, "right"), col("Ghi chú", 46)],
                 "rows": summary_rows, "caption": "Chỉ tiêu điều hành 2026", "alt": "Bảng chỉ tiêu điều hành 2026 so với 2025", "source": "BCTC kiểm toán 2026; HRIS; ESG ledger"},
                {"type": "bullets", "items": [
                    "**Tăng trưởng có chất lượng:** doanh thu tăng 20,4% nhưng điện năng chỉ tăng 4,2%; cường độ phát thải giảm 18,3%.",
                    "**Khách hàng:** NPS 62 (+4 điểm), tỷ lệ lỗi sản phẩm 0,42% (2025: 0,55%).",
                    "**Con người:** 880 nhân sự, 18.400 giờ đào tạo, tỷ lệ nghỉ việc 4,8%.",
                    "**Quản trị:** 3/6 thành viên HĐQT độc lập; Ủy ban ESG & rủi ro họp 4 lần/năm.",
                ]},
                {"type": "callout", "title": "Thông điệp của Chủ tịch HĐQT", "text": "“Chúng tôi không đổi tăng trưởng lấy niềm tin. Mỗi sản phẩm mới phải vượt qua kiểm soát dữ liệu, an toàn và tác động môi trường trước khi ra thị trường.” — Trần Minh An", "fill": "FFF2E5"},
                {"type": "paragraph", "text": "Báo cáo này cũng là một bài kiểm tra tính minh bạch: các chỉ số được trình bày cùng nguồn, chủ sở hữu dữ liệu và kiểm soát nội bộ; các giới hạn được nêu thay vì che giấu. Người đọc có thể đối chiếu bảng số với hình, công thức và phụ lục GRI."},
            ],
        },
        {
            "heading": "Mô hình kinh doanh và chiến lược",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "ANSMART thiết kế, sản xuất và vận hành thiết bị thông minh cho không gian sống: camera AI, hub, cảm biến và thiết bị chăm sóc sức khỏe tại nhà. Doanh thu đến từ phần cứng, thuê bao phần mềm và dịch vụ tích hợp cho doanh nghiệp."},
                {"type": "table", "advanced": True,
                 "columns": [col("Danh mục", 42), col("Doanh thu 2026 (tỷ VND)", 32, "right"), col("Tỷ trọng", 24, "right"), col("Biên gộp", 24, "right"), col("Sản phẩm chính", 33)],
                 "rows": segment_rows, "caption": "Cơ cấu doanh thu theo danh mục", "alt": "Bảng cơ cấu doanh thu theo ba danh mục", "source": "Báo cáo quản trị 2026"},
                {"type": "paragraph", "text": "Chiến lược 2026–2030 gồm ba trụ: (1) tăng tỷ trọng thuê bao và dịch vụ; (2) mở rộng thị trường Đông Nam Á; (3) giảm cường độ phát thải trên mỗi tỷ doanh thu. Mỗi trụ có chỉ tiêu và chủ sở hữu riêng trong bảng điều hành."},
                {"type": "callout", "title": "Lợi thế cạnh tranh", "text": "Tích hợp phần cứng – phần mềm – dữ liệu trong cùng một hệ sinh thái; chứng nhận ISO 27001 cho nền tảng Cloud; mạng lưới 1.200 đối tác lắp đặt tại 12 tỉnh thành.", "fill": "EAF4E7"},
            ],
        },
        {
            "heading": "Danh mục sản phẩm và đổi mới",
            "level": 1,
            "blocks": [
                {"type": "figure_text", "path": "../artifacts/product-camera.png", "alt": "Minh họa sản phẩm camera AI ANSMART: thân máy graphite, ống kính nhiều lớp, vòng lấy nét màu cam và tay nắm có vân.", "title": "Camera AI ANSMART S2", "caption": "Camera AI S2 — thiết kế năm 2026.", "heading": "Thiết kế để tin cậy", "text": "Camera S2 dùng ống kính 5 lớp, cảm biến 1/1.8 inch và xử lý AI tại biên. Vỏ graphite giảm phản xạ, tay nắm có vân giúp lắp đặt nhanh; vòng cam là điểm nhận diện thương hiệu.\n\nThiết kế phần cứng được đánh giá cùng kiểm soát quyền riêng tư: đèn trạng thái vật lý, công tắc che ống kính và mã hóa đầu cuối.", "image_side": "left", "image_width_mm": 72, "source": "ANSMART Design Studio; minh họa vector bởi VectorCraft + Pillow."},
                {"type": "table", "advanced": True,
                 "columns": [col("Nhóm", 40), col("Sản phẩm", 44), col("Doanh thu 2026", 28, "right"), col("Tỷ trọng", 20, "right"), col("Biên gộp", 23, "right")],
                 "header_rows": [
                     [{"text": "Danh mục", "rowspan": 2}, {"text": "Doanh thu", "colspan": 2, "align": "center"}, {"text": "Hiệu quả", "rowspan": 2}],
                     [{"text": "2026 (tỷ VND)", "align": "right"}, {"text": "Tỷ trọng", "align": "right"}],
                 ],
                 "rows": [
                     [c("Smart Home", bold=True), c("Camera AI S2, Hub H3, cảm biến"), c("612", align="right"), c("65%", align="right"), c("34,0%", align="right")],
                     [c("Smart Care", bold=True), c("Thiết bị chăm sóc tại nhà"), c("214", align="right"), c("23%", align="right"), c("41,0%", align="right")],
                     [c("Platform", bold=True), c("ANSMART Cloud, API"), c("114", align="right"), c("12%", align="right"), c("52,0%", align="right")],
                 ],
                 "caption": "Danh mục sản phẩm và hiệu quả", "alt": "Bảng danh mục sản phẩm với header hai tầng", "row_heights_mm": [8, 8, 10, 10, 10], "cell_margins_mm": 1.6, "source": "Báo cáo quản trị 2026"},
                {"type": "paragraph", "text": "R&D là trung tâm của mô hình: 78 tỷ VND, 8,3% doanh thu, 186 kỹ sư. Danh mục sáng chế đạt 42 bằng sáng chế được cấp, trong đó 11 bằng liên quan đến xử lý ảnh tại biên và tiết kiệm năng lượng."},
            ],
        },
        {
            "heading": "Hiệu quả tài chính",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Doanh thu 2026 đạt 940 tỷ VND, hoàn thành 104% kế hoạch. EBITDA 166 tỷ, biên 17,7%. Lợi nhuận sau thuế 118 tỷ, tăng 28,3% nhờ tăng trưởng doanh thu và tối ưu chi phí bán hàng."},
                {"type": "table", "advanced": True,
                 "columns": [col("Chỉ tiêu", 46), col("2022", 20, "right"), col("2023", 20, "right"), col("2024", 20, "right"), col("2025", 20, "right"), col("2026", 20, "right")],
                 "rows": financial_rows, "caption": "Tóm tắt tài chính 5 năm", "alt": "Bảng tóm tắt tài chính 2022–2026", "source": "BCTC kiểm toán 2022–2026; đơn vị tỷ VND trừ khi ghi khác"},
                {"type": "figure", "path": "../artifacts/charts/revenue-print.png", "alt": "Biểu đồ cột doanh thu 2022–2026 và đường mục tiêu; doanh thu tăng từ 420 lên 940 tỷ VND.", "caption": "Doanh thu và mục tiêu 2022–2026.", "width_mm": 145, "source": "Chart Forge (SheetCraft) từ BCTC kiểm toán; xuất bằng Excel."},
                {"type": "paragraph", "text": "Tốc độ tăng trưởng kép 2022–2026 được tính như sau:"},
                {"type": "equation", "latex": r"CAGR = \left(\frac{940}{420}\right)^{1/4} - 1 = 22{,}3\%", "caption": "Tăng trưởng kép doanh thu 2022–2026."},
                {"type": "page_break"},
                {"type": "table", "advanced": True,
                 "columns": [col("Khoản mục", 62), col("2026 (tỷ VND)", 30, "right"), col("% doanh thu", 26, "right"), col("2025 (tỷ VND)", 30, "right")],
                 "rows": cost_rows, "caption": "Cơ cấu chi phí và EBITDA", "alt": "Bảng cơ cấu chi phí 2026 so với 2025", "source": "BCTC kiểm toán 2026"},
                {"type": "paragraph", "text": "R&D tăng 18,2% lên 78 tỷ, tập trung vào cảm biến hình ảnh và mô hình AI tiết kiệm điện. Chi phí bán hàng tăng chậm hơn doanh thu nhờ kênh đối tác và thuê bao."},
                {"type": "table", "advanced": True,
                 "columns": [col("Thị trường", 52), col("2026 (tỷ VND)", 28, "right"), col("2025 (tỷ VND)", 28, "right"), col("Tăng trưởng", 24, "right"), col("Tỷ trọng", 23, "right")],
                 "rows": [
                     [c("Việt Nam", bold=True), c("704", align="right"), c("598", align="right"), c("+17,7%", align="right"), c("75%", align="right")],
                     [c("ASEAN", bold=True), c("178", align="right"), c("141", align="right"), c("+26,2%", align="right"), c("19%", align="right")],
                     [c("Khác", bold=True), c("58", align="right"), c("42", align="right"), c("+38,1%", align="right"), c("6%", align="right")],
                     [c("Tổng", bold=True), c("940", align="right", fill="E2EFDA"), c("781", align="right"), c("+20,4%", align="right", fill="E2EFDA"), c("100%", align="right")],
                 ], "caption": "Doanh thu theo thị trường", "alt": "Bảng doanh thu theo thị trường 2026", "source": "Báo cáo bán hàng 2026"},
                {"type": "table", "advanced": True,
                 "columns": [col("Chỉ tiêu", 60), col("2026", 32, "right"), col("2025", 32, "right"), col("Thay đổi", 31, "right")],
                 "rows": [
                     [c("Dòng tiền hoạt động kinh doanh (tỷ VND)", bold=True), c("172", align="right"), c("138", align="right"), c("+24,6%", align="right")],
                     [c("Capex (tỷ VND)", bold=True), c("-64", align="right"), c("-52", align="right"), c("+23,1%", align="right")],
                     [c("Nợ ròng / EBITDA", bold=True), c("0,8x", align="right"), c("1,1x", align="right"), c("-0,3x", align="right")],
                     [c("ROE", bold=True), c("18,4%", align="right"), c("16,1%", align="right"), c("+2,3 điểm", align="right")],
                     [c("Cổ tức trên cổ phiếu", bold=True), c("1.200 đ", align="right"), c("1.000 đ", align="right"), c("+20%", align="right")],
                 ], "caption": "Dòng tiền và chỉ số tài chính", "alt": "Bảng dòng tiền và chỉ số tài chính", "source": "BCTC kiểm toán 2026; Nghị quyết ĐHĐCĐ 2026"},
                {"type": "paragraph", "text": "Phân bổ vốn 2026 ưu tiên R&D (34% capex), tự động hóa nhà máy (28%), mở rộng kênh phân phối (22%) và hạ tầng dữ liệu (16%). Công ty giữ nợ ròng/EBITDA dưới 1,0x và duy trì tỷ lệ cổ tức 20% lợi nhuận sau thuế."},
            ],
        },
        {
            "heading": "Hiệu quả vận hành",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Sáu chỉ tiêu vận hành dưới đây là bảng điều hành hàng tháng của Ban Tổng Giám đốc. Mỗi chỉ tiêu có chủ sở hữu, nguồn dữ liệu và ngưỡng cảnh báo."},
                {"type": "table", "advanced": True,
                 "columns": [col("Chỉ tiêu", 42), col("2026", 24, "right"), col("2025", 24, "right"), col("Thay đổi", 24, "right"), col("Ghi chú", 41)],
                 "rows": ops_rows, "caption": "Chỉ tiêu vận hành 2026", "alt": "Bảng chỉ tiêu vận hành 2026", "source": "ERP, HRIS, nhật ký sản xuất"},
                {"type": "callout", "title": "Điểm cần cải thiện", "text": "Điện năng tăng 4,2% trong khi sản lượng tăng 18% — tốt hơn mục tiêu decoupling, nhưng vẫn cần giảm 6% vào 2027 để đạt lộ trình 1,5°C.", "fill": "FFF2CC"},
            ],
        },
        {
            "heading": "Quản trị công ty",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "HĐQT gồm 6 thành viên, 3 độc lập (50%), 2 nữ (33%). HĐQT họp 7 lần trong năm; tỷ lệ tham dự 6,9/7. Các ủy ban giúp HĐQT giám sát kiểm toán, chiến lược và ESG – rủi ro."},
                {"type": "table", "advanced": True,
                 "columns": [col("Thành viên", 38), col("Vai trò", 38), col("Tính độc lập", 32, "center"), col("Tham dự", 18, "right"), col("Chuyên môn", 29)],
                 "rows": board_rows, "caption": "Thành viên HĐQT và tỷ lệ tham dự", "alt": "Bảng thành viên HĐQT", "source": "Báo cáo quản trị 2026"},
                {"type": "table", "advanced": True,
                 "columns": [col("Ủy ban", 34), col("Thành viên", 62), col("Số cuộc họp", 22, "right"), col("Nhiệm vụ", 37)],
                 "rows": committee_rows, "caption": "Các ủy ban của HĐQT", "alt": "Bảng các ủy ban của HĐQT", "source": "Điều lệ HĐQT; biên bản 2026"},
                {"type": "paragraph", "text": "Chính sách chống tham nhũng, xung đột lợi ích và bảo vệ người tố giác được phổ biến hàng năm; 100% thành viên HĐQT và 96% nhân sự quản lý đã ký cam kết tuân thủ."},
            ],
        },
        {
            "heading": "Quản trị rủi ro",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Rủi ro được đánh giá theo khả năng xảy ra (1–5) và tác động (1–5). Ma trận dưới đây là công cụ điều hành: vùng đỏ cần kế hoạch giảm thiểu trong 90 ngày; vùng vàng theo dõi hàng quý."},
                {"type": "table", "advanced": True,
                 "columns": [col("Khả năng \\ Tác động", 34), col("1", 20, "center"), col("2", 20, "center"), col("3", 20, "center"), col("4", 20, "center"), col("5", 20, "center")],
                 "rows": heat, "caption": "Ma trận rủi ro 2026", "alt": "Ma trận 5x5 khả năng và tác động, các rủi ro R1–R6", "row_heights_mm": [9, 9, 9, 9, 9, 9], "source": "Ban Quản trị rủi ro, 2026-11-30"},
                {"type": "table", "advanced": True,
                 "columns": [col("Mã", 14, "center"), col("Rủi ro", 46), col("Khả năng", 18, "right"), col("Tác động", 18, "right"), col("Giảm thiểu", 44), col("Chủ sở hữu", 15)],
                 "rows": risk_rows, "caption": "Danh mục rủi ro trọng yếu", "alt": "Bảng rủi ro trọng yếu R1–R6", "source": "Ban Quản trị rủi ro, 2026-11-30"},
            ],
        },
        {
            "heading": "Trọng yếu và các bên liên quan",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Quy trình trọng yếu 2026 kết hợp khảo sát 3.240 khách hàng, 42 cuộc phỏng vấn bên liên quan và đánh giá tác động kinh doanh. 10 chủ đề được xếp hạng; 5 chủ đề trọng yếu cao được đưa vào kế hoạch hành động 2027."},
                {"type": "table", "advanced": True,
                 "columns": [col("Tác động kinh doanh \\ Kỳ vọng bên liên quan", 34), col("1", 20, "center"), col("2", 20, "center"), col("3", 20, "center"), col("4", 20, "center"), col("5", 20, "center")],
                 "rows": materiality, "caption": "Ma trận trọng yếu 2026", "alt": "Ma trận trọng yếu 5x5 với các chủ đề T1–T10", "row_heights_mm": [9, 9, 9, 9, 9, 9], "source": "Khảo sát bên liên quan 2026; Ủy ban ESG"},
                {"type": "table", "advanced": True,
                 "columns": [col("Mã", 14, "center"), col("Chủ đề", 58), col("Kỳ vọng", 22, "right"), col("Tác động", 22, "right"), col("Mức", 30)],
                 "rows": topic_rows, "caption": "Danh mục chủ đề trọng yếu", "alt": "Bảng 10 chủ đề trọng yếu", "source": "Ủy ban ESG, 2026-11-30"},
                {"type": "table", "advanced": True,
                 "columns": [col("Bên liên quan", 32), col("Cách tương tác", 62), col("Tần suất", 22), col("Chỉ số theo dõi", 39)],
                 "rows": stakeholder_rows, "caption": "Tương tác với các bên liên quan", "alt": "Bảng tương tác bên liên quan", "source": "Báo cáo ESG 2026"},
                {"type": "paragraph", "text": "Điểm trọng yếu được tính theo công thức có trọng số, sau đó chuẩn hóa về thang 1–5:"},
                {"type": "equation", "latex": r"S_i = 0{,}45\,B_i + 0{,}35\,P_i + 0{,}20\,D_i", "caption": "Điểm trọng yếu có trọng số (B: tác động kinh doanh; P: kỳ vọng bên liên quan; D: mức độ dữ liệu sẵn có).", "number": False},
            ],
        },
        {
            "heading": "Môi trường",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Tổng phát thải 2026 là 23.250 tCO₂e, giảm 1,6% so với 2025 trong khi doanh thu tăng 20,4%. Cường độ phát thải giảm 18,3%, đưa công ty về gần mục tiêu 2027."},
                {"type": "table", "advanced": True,
                 "columns": [col("Phạm vi", 52), col("2026 (tCO₂e)", 30, "right"), col("2025 (tCO₂e)", 30, "right"), col("Mục tiêu 2027", 28, "right"), col("Thay đổi", 20, "right")],
                 "rows": emission_rows, "caption": "Phát thải khí nhà kính theo phạm vi", "alt": "Bảng phát thải Scope 1, 2, 3 và cường độ", "source": "GRI 305; hệ số phát thải Việt Nam 2024; ESG ledger"},
                {"type": "figure", "path": "../artifacts/charts/emissions-print.png", "alt": "Biểu đồ cột chồng phát thải 2022–2026; Scope 3 chiếm phần lớn, Scope 1 và 2 nhỏ hơn.", "caption": "Phát thải theo phạm vi 2022–2026.", "width_mm": 145, "source": "Chart Forge (SheetCraft) từ ESG ledger; xuất bằng Excel."},
                {"type": "paragraph", "text": "Cường độ phát thải được tính trên doanh thu:"},
                {"type": "equation", "latex": r"I_{2026} = \frac{23.250}{940} = 24{,}73\ \text{tCO}_2\text{e/tỷ VND}", "caption": "Cường độ phát thải 2026 (GRI 305-4)."},
                {"type": "paragraph", "text": "Lộ trình giảm phát thải gồm: điện mặt trời áp mái 4,2 MWp (hoàn thành 2026), thay thế 60% xe vận chuyển bằng xe điện vào 2028, và yêu cầu nhà cung cấp Tier 1 công bố dữ liệu Scope 3 từ 2027."},
                {"type": "callout", "title": "Mục tiêu 2030", "text": "Giảm 42% phát thải Scope 1+2 và 25% cường độ Scope 3 so với 2022; Net Zero vào 2050. Lộ trình được rà soát hàng năm bởi Ủy ban ESG & rủi ro.", "fill": "EAF4E7"},
            ],
        },
        {
            "heading": "Xã hội",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "ANSMART có 880 nhân sự tại 4 địa điểm. Năm 2026, tỷ lệ nghỉ việc giảm còn 4,8%; giờ đào tạo tăng 22,8% nhờ chương trình học trực tuyến và chứng chỉ kỹ năng."},
                {"type": "table", "advanced": True,
                 "columns": [col("Chỉ tiêu", 62), col("2026", 34, "right"), col("2025", 34, "right"), col("Thay đổi", 25, "right")],
                 "rows": workforce_rows, "caption": "Nhân sự và đào tạo", "alt": "Bảng nhân sự, giới tính, đào tạo và nghỉ việc", "source": "HRIS 2026; GRI 401, 404, 405"},
                {"type": "paragraph", "text": "Giờ đào tạo bình quân được tính như sau:"},
                {"type": "equation", "latex": r"H_{tb} = \frac{18.400}{880} = 20{,}9\ \text{giờ/người}", "caption": "Giờ đào tạo bình quân đầu người 2026.", "number": False},
                {"type": "paragraph", "text": "An toàn lao động: LTIFR 0,21, không có tai nạn nghiêm trọng. 100% nhân sự được huấn luyện an toàn định kỳ; 92% tham gia khảo sát gắn kết, điểm gắn kết 78/100."},
                {"type": "callout", "title": "Cam kết cộng đồng", "text": "Quỹ học bổng ANSMART trao 120 suất cho sinh viên STEM tại Bình Dương và TP.HCM; 38% người nhận là nữ.", "fill": "EAF1F8"},
            ],
        },
        {
            "heading": "Chuỗi cung ứng và đạo đức kinh doanh",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Chuỗi cung ứng gồm 252 nhà cung cấp, trong đó 86 Tier 1. 78% chi tiêu Tier 1 được đánh giá ESG trong 24 tháng gần nhất; 4 nhà cung cấp chiến lược chiếm 46% chi tiêu."},
                {"type": "table", "advanced": True,
                 "columns": [col("Nhóm", 42), col("Số lượng", 20, "right"), col("Đã đánh giá ESG", 30, "right"), col("Cơ chế", 42), col("Ghi chú", 21)],
                 "rows": supplier_rows, "caption": "Chuỗi cung ứng và đánh giá ESG", "alt": "Bảng nhà cung cấp theo tier và tỷ lệ đánh giá ESG", "source": "Procurement 2026"},
                {"type": "paragraph", "text": "Bộ Quy tắc Ứng xử Nhà cung cấp quy định về lao động, môi trường, dữ liệu và chống tham nhũng. 100% hợp đồng mới có điều khoản ESG; 3 nhà cung cấp bị yêu cầu khắc phục trong năm, 2 đã hoàn tất."},
                {"type": "callout", "title": "Kênh tố giác", "text": "Đường dây độc lập 24/7 và hộp thư ethics@ansmart.example; 12 báo cáo trong 2026, 100% được xác nhận trong 5 ngày làm việc, không có báo cáo về tham nhũng.", "fill": "FFF2E5"},
            ],
        },
        {
            "heading": "Phương pháp và chất lượng dữ liệu",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "Mỗi chỉ số trong báo cáo có một chủ sở hữu dữ liệu, nguồn, tần suất và kiểm soát. Bảng dưới đây là danh mục kiểm soát nội bộ; các trình bày lại được nêu riêng."},
                {"type": "table", "advanced": True,
                 "columns": [col("Chỉ số", 40), col("Nguồn", 44), col("Chủ sở hữu", 20), col("Kiểm soát", 40), col("Trình bày lại", 21)],
                 "rows": data_rows, "caption": "Danh mục chất lượng dữ liệu", "alt": "Bảng nguồn và kiểm soát dữ liệu", "source": "Ban Kiểm soát nội bộ, 2026-12-15"},
                {"type": "paragraph", "text": "Điểm chất lượng dữ liệu tổng hợp được tính theo trọng số nguồn, kiểm soát và tần suất:"},
                {"type": "equation", "latex": r"Q = 0{,}40\,N + 0{,}35\,K + 0{,}25\,T", "caption": "Điểm chất lượng dữ liệu (N: nguồn; K: kiểm soát; T: tần suất). Kết quả 2026: 86/100.", "number": False},
                {"type": "callout", "title": "Trình bày lại", "text": "Scope 3 năm 2025 được điều chỉnh +1,2% (từ 18.576 lên 18.800 tCO₂e) do cập nhật hệ số phát thải của nhà cung cấp logistics. Số 2026 đã dùng hệ số mới; không có trình bày lại nào khác.", "fill": "FFF2CC"},
                {"type": "paragraph", "text": "Giới hạn: báo cáo ESG chưa được đảm bảo bên ngoài; một số dữ liệu Scope 3 là ước tính từ chi tiêu. Báo cáo tài chính đã được kiểm toán độc lập. PDF/UA chưa được xác nhận bằng trình kiểm tra chuyên dụng."},
            ],
        },
        {
            "heading": "Kết luận và kiến nghị",
            "level": 1,
            "blocks": [
                {"type": "paragraph", "text": "2026 là năm ANSMART chứng minh tăng trưởng có thể đi cùng kỷ luật dữ liệu. Doanh thu tăng 20,4%, cường độ phát thải giảm 18,3%, NPS tăng 4 điểm và quản trị có 50% thành viên độc lập."},
                {"type": "bullets", "items": [
                    "**Duy trì đà giảm phát thải:** ưu tiên Scope 3, yêu cầu nhà cung cấp Tier 1 công bố dữ liệu từ 2027.",
                    "**Tăng tỷ trọng thuê bao:** mục tiêu 18% doanh thu từ Platform vào 2028.",
                    "**Chuẩn hóa dữ liệu:** mở rộng kiểm soát tự động từ 5 chỉ số lên 12 chỉ số trọng yếu.",
                    "**Quản trị:** giữ 50% thành viên HĐQT độc lập; thành lập tiểu ban an ninh mạng trực thuộc Ủy ban ESG & rủi ro.",
                    "**Minh bạch:** tiến tới đảm bảo ESG có giới hạn cho các chỉ số phát thải và nhân sự vào 2028.",
                ]},
                {"type": "callout", "title": "Cam kết 2027", "text": "Hoàn thành lộ trình 1,5°C theo kế hoạch; công bố báo cáo ESG có đảm bảo giới hạn; duy trì tỷ lệ trình bày lại dưới 2% số chỉ số.", "fill": "EAF4E7"},
            ],
        },
    ]

    spec = {
        "meta": {
            "title": "Báo cáo thường niên và ESG 2026",
            "subtitle": "Thiết bị thông minh cho không gian sống",
            "author": "Ban Tài chính và Phát triển bền vững",
            "organization": "Công ty CP Thiết bị Thông minh An Nhiên (ANSMART)",
            "document_id": "ANSMART-AR-2026",
            "version": "1.0",
            "date": "2026-12-31",
            "language": "vi-VN",
            "classification": "Công khai",
            "keywords": ["báo cáo thường niên", "ESG", "GRI", "quản trị", "phát thải"],
        },
        "cover": {
            "enabled": True,
            "hero_image": "../artifacts/cover.png",
            "hero_alt": "Dải bìa navy với camera AI ANSMART bên phải, vạch cam và lưới isometric mờ.",
        },
        "front_matter": {
            "order": "iso7144",
            "abstract": {
                "enabled": True,
                "title": "Tóm tắt điều hành",
                "text": "Báo cáo thường niên và ESG 2026 của ANSMART trình bày kết quả kinh doanh, quản trị và tác động môi trường – xã hội trong kỳ 2026-01-01 đến 2026-12-31. Doanh thu đạt 940 tỷ VND (+20,4%), EBITDA 166 tỷ (biên 17,7%), lợi nhuận sau thuế 118 tỷ (+28,3%).\n\nBáo cáo được lập theo GRI 1: Foundation 2021 và các tiêu chuẩn trình bày ISO 7144/2145/690/80000/8601; cấu trúc, đánh số, tài liệu tham khảo và kiểm soát dữ liệu được nêu trong Lời nói đầu. Nội dung ESG tự công bố, chưa được đảm bảo bên ngoài; báo cáo tài chính đã kiểm toán độc lập.\n\nBáo cáo gồm 14 mục, 3 phụ lục và 11 tài liệu tham khảo. Phần trọng yếu nêu phương pháp và giới hạn; phần môi trường trình bày Scope 1–3 và cường độ phát thải; phần xã hội trình bày nhân sự, đào tạo và an toàn; phần quản trị trình bày HĐQT, rủi ro và đạo đức.\n\nNgười đọc có thể kiểm tra chéo: mỗi bảng có nguồn, mỗi hình có số hiệu, mỗi công thức có số; chỉ mục GRI ở Phụ lục A liên kết từng disclosure tới vị trí tương ứng.",
                "keywords": ["ANSMART", "GRI 2021", "ESG", "ISO 7144", "báo cáo thường niên"],
            },
            "preface": {
                "enabled": True,
                "title": "Lời nói đầu và kiểm soát tài liệu",
                "text": "Báo cáo này được kiểm soát như một tài liệu có phiên bản, không phải một tệp trình bày. Bảng dưới đây công bố bộ tiêu chuẩn áp dụng và bằng chứng kiểm soát tương ứng; mọi thay đổi sau phát hành phải qua quy trình phê duyệt và được ghi trong nhật ký phiên bản.",
                "blocks": [
                    {"type": "table", "advanced": True,
                     "columns": [col("Hạng mục", 42), col("Nội dung", 110)],
                     "rows": [
                         [c("Tên tài liệu", bold=True), c("Báo cáo thường niên và ESG 2026")],
                         [c("Mã tài liệu / phiên bản", bold=True), c("ANSMART-AR-2026 / 1.0")],
                         [c("Ngày phát hành", bold=True), c("2026-12-31")],
                         [c("Kỳ báo cáo", bold=True), c("2026-01-01 → 2026-12-31")],
                         [c("Phạm vi", bold=True), c("ANSMART và 3 công ty con; nhà máy Bình Dương, R&D TP.HCM")],
                         [c("Đơn vị tiền tệ", bold=True), c("tỷ VND; 1 tỷ = 10⁹ VND")],
                         [c("Phê duyệt", bold=True), c("HĐQT 2026-12-20; TGĐ ký 2026-12-31")],
                         [c("Đảm bảo", bold=True), c("BCTC kiểm toán độc lập; ESG tự công bố, chưa assured")],
                         [c("Liên hệ", bold=True), c("investor@ansmart.example")],
                     ], "alt": "Thông tin kiểm soát tài liệu", "caption": ""},
                    {"type": "table", "advanced": True,
                     "columns": [col("Mã", 22, "center"), col("Tiêu chuẩn / điều", 32), col("Kiểm soát", 40), col("Bằng chứng", 38), col("Trạng thái", 23, "center")],
                     "rows": control_rows, "alt": "Bảng kiểm soát tiêu chuẩn", "caption": "",
                     "cell_margins_mm": 0.9},
                ],
            },
            "toc": {"enabled": True, "levels": 3, "title": "Mục lục"},
            "list_of_figures": {"enabled": True, "title": "Danh mục hình", "mode": "ref_pageref", "page_break_after": False},
            "list_of_tables": {"enabled": True, "title": "Danh mục bảng", "mode": "ref_pageref"},
        },
        "sections": sections,
        "appendix": [
            {
                "letter": "A",
                "title": "Chỉ mục nội dung GRI",
                "blocks": [
                    {"type": "paragraph", "text": "Bảng dưới đây đối chiếu các disclosure GRI 2, GRI 3, GRI 305, GRI 401, 404, 405, 413 và 418 với vị trí trong báo cáo. Báo cáo tự công bố theo GRI 1; chưa có đảm bảo bên ngoài."},
                    {"type": "table", "advanced": True,
                     "columns": [col("GRI", 22), col("Nội dung", 98), col("Vị trí", 34)],
                     "rows": gri_rows, "caption": "Chỉ mục nội dung GRI 2026", "alt": "Bảng đối chiếu disclosure GRI với vị trí báo cáo", "source": "GRI 1: Foundation 2021; GRI 2/3/305/401/404/405/413/418"},
                ],
            },
            {
                "letter": "B",
                "title": "Dữ liệu 5 năm",
                "blocks": [
                    {"type": "table", "advanced": True,
                     "columns": [col("Chỉ tiêu", 46), col("2022", 20, "right"), col("2023", 20, "right"), col("2024", 20, "right"), col("2025", 20, "right"), col("2026", 20, "right")],
                     "rows": years, "caption": "Dữ liệu 5 năm 2022–2026", "alt": "Bảng dữ liệu 5 năm", "source": "BCTC kiểm toán; ESG ledger; HRIS"},
                ],
            },
            {
                "letter": "C",
                "title": "Thuật ngữ và chữ viết tắt",
                "blocks": [
                    {"type": "table", "advanced": True,
                     "columns": [col("Thuật ngữ", 34), col("Định nghĩa", 118)],
                     "rows": glossary_rows, "caption": "Thuật ngữ và chữ viết tắt", "alt": "Bảng thuật ngữ", "source": ""},
                ],
            },
        ],
        "references": {
            "enabled": True,
            "title": "Tài liệu tham khảo",
            "items": [
                {"key": "iso7144", "label": "[1]", "text": "ISO. 1986. ISO 7144:1986 Documentation — Presentation of theses and similar documents. Geneva: ISO. https://www.iso.org/standard/13736.html (truy cập 2026-11-01)."},
                {"key": "iso2145", "label": "[2]", "text": "ISO. 1978. ISO 2145:1978 Documentation — Numbering of divisions and subdivisions in written documents. Geneva: ISO. https://www.iso.org/standard/5964.html (truy cập 2026-11-01)."},
                {"key": "iso690", "label": "[3]", "text": "ISO. 2021. ISO 690:2021 Information and documentation — Guidelines for bibliographic references and citations to information resources. Geneva: ISO. https://www.iso.org/standard/72642.html (truy cập 2026-11-01)."},
                {"key": "iso80000", "label": "[4]", "text": "ISO. 2022. ISO 80000-1:2022 Quantities and units — Part 1: General. Geneva: ISO. https://www.iso.org/standard/76921.html (truy cập 2026-11-01)."},
                {"key": "iso8601", "label": "[5]", "text": "ISO. 2019. ISO 8601-1:2019 Date and time — Representations for information interchange — Part 1: Basic rules. Geneva: ISO. https://www.iso.org/standard/70907.html (truy cập 2026-11-01)."},
                {"key": "wcag22", "label": "[6]", "text": "W3C. 2023. Web Content Accessibility Guidelines (WCAG) 2.2. W3C Recommendation. https://www.w3.org/TR/WCAG22/ (truy cập 2026-11-01)."},
                {"key": "gri1", "label": "[7]", "text": "Global Reporting Initiative. 2021. GRI 1: Foundation 2021. Amsterdam: GRI. https://www.globalreporting.org/standards/ (truy cập 2026-11-01)."},
                {"key": "gri2", "label": "[8]", "text": "Global Reporting Initiative. 2021. GRI 2: General Disclosures 2021. Amsterdam: GRI."},
                {"key": "gri3", "label": "[9]", "text": "Global Reporting Initiative. 2021. GRI 3: Material Topics 2021. Amsterdam: GRI."},
                {"key": "gri305", "label": "[10]", "text": "Global Reporting Initiative. 2016. GRI 305: Emissions 2016. Amsterdam: GRI."},
                {"key": "vnm2025", "label": "[11]", "text": "Vinamilk. 2026. Annual Report 2025. https://www.vinamilk.com.vn/en/investor/reports/annual (truy cập 2026-11-01; dùng làm mẫu tham chiếu bố cục, không sao chép nội dung)."},
            ],
        },
    }
    return spec


if __name__ == "__main__":
    path = HERE / "annual_report_spec.json"
    path.write_text(json.dumps(build(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
