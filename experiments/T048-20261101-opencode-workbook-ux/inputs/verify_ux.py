from __future__ import annotations

import os
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
XLSX = ART / "workbook-ux.xlsx"
XLSM = ART / "workbook-ux.xlsm"

excel = win32.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False
try:
    excel.AutomationSecurity = 1  # msoAutomationSecurityLow: allow the test macro
    wb = excel.Workbooks.Open(str(XLSX), False, True)
    print("visible sheets:", [(wb.Worksheets(i).Name, wb.Worksheets(i).Visible)
                              for i in range(1, wb.Worksheets.Count + 1)])
    inp = wb.Worksheets("Input")
    print("Input protect:", inp.ProtectContents)
    print("Input buttons:", inp.Buttons().Count)
    for i in range(1, inp.Buttons().Count + 1):
        print("  button", i, inp.Buttons(i).Caption, inp.Buttons(i).OnAction)
    print("Input merged:", inp.Range("C6:D6").MergeCells)
    print("validation C6:", inp.Range("C6").Validation.Type)
    print("validation C7:", inp.Range("C7").Validation.Type)
    print("tab colors:", [(wb.Worksheets(i).Name, wb.Worksheets(i).Tab.Color)
                          for i in range(1, wb.Worksheets.Count + 1)
                          if wb.Worksheets(i).Visible == -1])
    wb.Close(False)

    wb2 = excel.Workbooks.Open(str(XLSM), False, True)
    try:
        comps = [wb2.VBProject.VBComponents(i).Name
                 for i in range(1, wb2.VBProject.VBComponents.Count + 1)]
        print("modules:", comps)
        inp = wb2.Worksheets("Input")
        data = wb2.Worksheets("Data")
        before = data.Cells(data.Rows.Count, "A").End(-4162).Row  # xlUp
        inp.Range("C6").Value = "Dữ liệu"
        inp.Range("F6").Value = "Lan Nguyễn"
        inp.Range("C7").Value = "2026-06-01"
        inp.Range("F7").Value = 10
        inp.Range("C8").Value = 100
        inp.Range("F8").Value = 220
        inp.Range("C9").Value = "On track"
        inp.Range("F9").Value = "High"
        try:
            excel.Run("'" + XLSM.name + "'!DashboardTools.AddRecord")
            after = data.Cells(data.Rows.Count, "A").End(-4162).Row
            print("data rows before/after:", before, after)
            print("new row:", [data.Cells(after, c).Value for c in range(1, 12)])
            print("status:", inp.Range("B20").Value)
            print("input cleared:", repr(inp.Range("C6").Value))
        except Exception as exc:
            print("macro run blocked:", exc)
            print("module code present:", "AddRecord" in wb2.VBProject.VBComponents("DashboardTools").CodeModule.Lines(1, 200))
    finally:
        try:
            wb2.Close(False)
        except Exception:
            pass
finally:
    excel.Quit()
