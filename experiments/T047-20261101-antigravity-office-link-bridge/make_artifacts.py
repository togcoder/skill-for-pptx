import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from office_link_bridge import (
    inspect_office_charts,
    link_chart_to_external_excel,
    embed_sheetcraft_workbook,
    sync_office_chart_data,
    refresh_presentation_links_com,
)

DECKCRAFT_CLI = r"D:\artcraft\DeckCraft\deckcraft-cli.exe"
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
PREVIEWS_DIR = ARTIFACTS_DIR / "previews"
PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_PPTX = Path(__file__).resolve().parents[2] / "build" / "forge" / "coffee_report.pptx"


def create_financial_model(path: Path) -> Path:
    wb = openpyxl.Workbook()

    # Sheet 1: Financial Summary
    ws = wb.active
    ws.title = "DoanhThu_LoiNhuan"
    ws.views.sheetView[0].showGridLines = True

    # Styling
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Segoe UI Semibold", size=11, color="FFFFFF", bold=True)
    bold_font = Font(name="Segoe UI", size=10, bold=True)
    regular_font = Font(name="Segoe UI", size=10)
    currency_fmt = '#,##0" Tr"'

    headers = ["Chỉ tiêu tài chính (Triệu VNĐ)", "Quý 1", "Quý 2", "Quý 3", "Quý 4"]
    ws.append(headers)
    for col_idx in range(1, 6):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center" if col_idx > 1 else "left", vertical="center")

    rows = [
        ("Doanh thu thuần", 1250, 1480, 1620, 1950),
        ("Giá vốn hàng bán (COGS)", 520, 590, 640, 780),
        ("Lợi nhuận gộp", "=B2-B3", "=C2-C3", "=D2-D3", "=E2-E3"),
        ("Chi phí hoạt động (OPEX)", 380, 410, 430, 490),
        ("Lợi nhuận thuần (EBIT)", "=B4-B5", "=C4-C5", "=D4-D5", "=E4-E5"),
    ]

    for r_idx, row_data in enumerate(rows, start=2):
        ws.append(list(row_data))
        is_subtotal = row_data[0].startswith("Lợi nhuận")
        for col_idx in range(1, 6):
            cell = ws.cell(row=r_idx, column=col_idx)
            cell.font = bold_font if is_subtotal else regular_font
            if col_idx > 1:
                cell.number_format = currency_fmt
                cell.alignment = Alignment(horizontal="right")

    # Sheet 2: Regional breakdown
    ws_reg = wb.create_sheet(title="ChiTiet_VungMien")
    ws_reg.views.sheetView[0].showGridLines = True
    ws_reg.append(["Vùng miền", "Đóng góp (%)", "Doanh thu (Tr VNĐ)"])
    for col_idx in range(1, 4):
        ws_reg.cell(row=1, column=col_idx).fill = header_fill
        ws_reg.cell(row=1, column=col_idx).font = header_font

    reg_data = [
        ("Miền Bắc", 0.45, "=DoanhThu_LoiNhuan!E2*0.45"),
        ("Miền Nam", 0.40, "=DoanhThu_LoiNhuan!E2*0.40"),
        ("Miền Trung", 0.15, "=DoanhThu_LoiNhuan!E2*0.15"),
    ]
    for r in reg_data:
        ws_reg.append(list(r))

    # Sheet 3: KPI Metrics
    ws_kpi = wb.create_sheet(title="ChiSo_KPI")
    ws_kpi.views.sheetView[0].showGridLines = True
    ws_kpi.append(["Chỉ số", "Giá trị"])
    ws_kpi.cell(row=1, column=1).fill = header_fill
    ws_kpi.cell(row=1, column=1).font = header_font
    ws_kpi.cell(row=1, column=2).fill = header_fill
    ws_kpi.cell(row=1, column=2).font = header_font

    ws_kpi.append(["Biên lợi nhuận gộp", "=DoanhThu_LoiNhuan!E4/DoanhThu_LoiNhuan!E2"])
    ws_kpi.append(["Biên lợi nhuận ròng", "=DoanhThu_LoiNhuan!E6/DoanhThu_LoiNhuan!E2"])

    wb.save(path)
    return path


def main():
    print("=== T047 Artifact Generation ===")

    # 1. Create source financial model
    model_path = ARTIFACTS_DIR / "financial_model.xlsx"
    create_financial_model(model_path)
    print(f"[1] Created multi-sheet financial model: {model_path}")

    # 2. Create Embedded Connected Deck
    # Categories: Quý 1, Quý 2, Quý 3, Quý 4 (B1:E1)
    # Series 1 (Doanh thu thuần): B2:E2
    # Series 2 (Lợi nhuận thuần): B6:E6
    deck_embedded = ARTIFACTS_DIR / "executive_deck_embedded.pptx"
    mappings = [
        {
            "sheet": "DoanhThu_LoiNhuan",
            "name": "Doanh thu thuần",
            "name_cell": "A2",
            "categories_range": "$B$1:$E$1",
            "values_range": "$B$2:$E$2",
        },
        {
            "sheet": "DoanhThu_LoiNhuan",
            "name": "Lợi nhuận thuần",
            "name_cell": "A6",
            "categories_range": "$B$1:$E$1",
            "values_range": "$B$6:$E$6",
        },
    ]
    res_emb = embed_sheetcraft_workbook(
        SAMPLE_PPTX,
        model_path,
        chart_index=0,
        output_path=deck_embedded,
        sheet_name="DoanhThu_LoiNhuan",
        series_mappings=mappings,
    )
    print(f"[2] Created embedded connected deck: {deck_embedded}")

    # 3. Create Linked External Deck
    deck_linked = ARTIFACTS_DIR / "executive_deck_linked.pptx"
    res_link = link_chart_to_external_excel(
        deck_embedded,
        model_path,
        chart_index=0,
        output_path=deck_linked,
        sheet_name="DoanhThu_LoiNhuan",
        auto_update=True,
    )
    print(f"[3] Created linked external deck: {deck_linked}")

    # 4. Modify financial model (Q4 expansion: Revenue from 1950 -> 2450)
    wb = openpyxl.load_workbook(model_path)
    ws = wb["DoanhThu_LoiNhuan"]
    ws["E2"] = 2450  # Q4 surge
    ws["E3"] = 920   # Revised COGS
    ws["E5"] = 550   # Revised OPEX
    wb.save(model_path)
    print("[4] Updated Q4 metrics in financial_model.xlsx")

    # 5. Run Offline Cache Synchronization
    deck_synced = ARTIFACTS_DIR / "executive_deck_synced.pptx"
    res_sync = sync_office_chart_data(deck_linked, excel_path=model_path, output_path=deck_synced)
    print(f"[5] Synchronized chart cache into: {deck_synced}")

    # 6. Inspect final synced deck
    audit_data = {
        "embedded_deck": inspect_office_charts(deck_embedded),
        "linked_deck": inspect_office_charts(deck_linked),
        "synced_deck": inspect_office_charts(deck_synced),
        "sync_diff": res_sync,
    }
    audit_path = ARTIFACTS_DIR / "audit.json"
    audit_path.write_text(json.dumps(audit_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[6] Wrote inspection audit: {audit_path}")

    # 7. Render slide previews with DeckCraft CLI
    if Path(DECKCRAFT_CLI).exists():
        # Slide 3 contains the chart in coffee_report.pptx
        preview_emb = PREVIEWS_DIR / "slide_embedded.png"
        preview_sync = PREVIEWS_DIR / "slide_synced.png"
        subprocess.run([DECKCRAFT_CLI, "render", str(deck_embedded), "--slide", "3", str(preview_emb)], check=True)
        subprocess.run([DECKCRAFT_CLI, "render", str(deck_synced), "--slide", "3", str(preview_sync)], check=True)
        print(f"[7] Rendered DeckCraft 1920x1080 previews to: {PREVIEWS_DIR}")

    # 8. Compute SHA256 checksums
    sha_lines = []
    for f in sorted(ARTIFACTS_DIR.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS.txt":
            rel = f.relative_to(ARTIFACTS_DIR)
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            sha_lines.append(f"{h}  {rel}")
    (ARTIFACTS_DIR / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")
    print("[8] Computed SHA256SUMS.txt")
    print("All T047 artifacts ready!")


if __name__ == "__main__":
    main()
