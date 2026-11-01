"""T043 verification: open in Excel, check formulas/pivot/VBA, render sheets."""
from __future__ import annotations

import os
from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
PREVIEW = ROOT / "preview"
PREVIEW.mkdir(parents=True, exist_ok=True)
XLSX = ART / "programme-dashboard.xlsx"
XLSM = ART / "programme-dashboard.xlsm"

excel = win32.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(XLSX), False, True)
    print("sheets:", [wb.Worksheets(i).Name for i in range(1, wb.Worksheets.Count + 1)])
    model = wb.Worksheets("Model")
    print("Model A1:E5")
    for r in range(1, 6):
        print(" ", [model.Cells(r, c).Value for c in range(1, 6)])
    print("TaskCount", wb.Names("TaskCount").RefersTo)
    print("TotalCost", wb.Names("TotalCost").RefersTo)
    print("named TotalCost value", excel.Evaluate("TotalCost"))
    print("named TaskCount value", excel.Evaluate("TaskCount"))

    team = wb.Worksheets("Team")
    print("Team shapes", team.Shapes.Count)
    for i in range(1, team.Shapes.Count + 1):
        shp = team.Shapes(i)
        print("  ", shp.Name, shp.Type, round(shp.Left, 1), round(shp.Top, 1),
              shp.AlternativeText or "")

    gantt = wb.Worksheets("Gantt")
    print("Gantt D2", gantt.Cells(2, 4).Formula, gantt.Cells(2, 4).Value)

    try:
        pivot_ws = wb.Worksheets("Pivot")
        print("Pivot tables", pivot_ws.PivotTables().Count)
        if pivot_ws.PivotTables().Count:
            pt = pivot_ws.PivotTables(1)
            print("  name", pt.Name, "source", pt.SourceData)
            print("  used", pt.TableRange1.Address)
    except Exception as exc:
        print("pivot FAIL", exc)

    dash = wb.Worksheets("Dashboard")
    print("Dashboard charts", dash.ChartObjects().Count)
    for idx in range(1, dash.ChartObjects().Count + 1):
        co = dash.ChartObjects(idx)
        print("  chart", idx, round(co.Width, 1), round(co.Height, 1),
              round(co.Left, 1), round(co.Top, 1), co.Chart.HasTitle)

    for sheet in ("Data", "Team", "Gantt", "Relations", "Dashboard"):
        pdf = PREVIEW / f"{sheet.lower()}.pdf"
        wb.Worksheets(sheet).ExportAsFixedFormat(0, str(pdf))
        with fitz.open(pdf) as doc:
            print(sheet, "pdf pages", len(doc))
            doc[0].get_pixmap(dpi=140).save(PREVIEW / f"{sheet.lower()}-page-1.png")
        pdf.unlink(missing_ok=True)
    wb.Close(False)

    if XLSM.is_file():
        wb2 = excel.Workbooks.Open(str(XLSM), False, True)
        try:
            comps = [wb2.VBProject.VBComponents(i).Name
                     for i in range(1, wb2.VBProject.VBComponents.Count + 1)]
            print("xlsm modules", comps)
            used = [s.Name for s in wb2.Worksheets]
            print("xlsm sheets", used)
        finally:
            try:
                wb2.Close(False)
            except Exception:
                pass
finally:
    excel.Quit()
