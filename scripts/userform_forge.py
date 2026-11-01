"""Inject a real VBA UserForm into an .xlsm (T050, xlsx).

Status: EXPERIMENTAL — T050.  The host may block *running* macros; this module
only needs the VBA project object model to add a form and a standard module.
That is enough to inspect the form's controls and code in the package.

The form is deliberately a modal data-entry surface, not a worksheet form:

* eight fields (workstream, owner, start, days, cost, benefit, status, priority);
* four combo boxes, four text boxes, three buttons, a status line;
* `btnSave_Click` validates and appends to the hidden Data sheet;
* `FormTools` exposes `ShowEntryForm`, `FilterRisk`, `FilterAll` for dashboard
  buttons.

CLI:
    python scripts/userform_forge.py build workbook.xlsm
    python scripts/userform_forge.py inspect workbook.xlsm
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FORM_NAME = "frmEntry"
MODULE_NAME = "FormTools"


def _rgb(value: str) -> int:
    value = value.lstrip("#")
    r, g, b = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    return r | (g << 8) | (b << 16)


FORM_CODE = r'''Option Explicit

Private Sub UserForm_Initialize()
    Me.cboWorkstream.List = Array("Dữ liệu", "Nền tảng", "Năng lực", "Trải nghiệm")
    Me.cboOwner.List = Array("Lan Nguyễn", "Minh Trần", "Hà Phạm", "Tuấn Lê", "Mai Vũ", "Khánh Đỗ")
    Me.cboStatus.List = Array("On track", "At risk", "Blocked", "Done")
    Me.cboPriority.List = Array("High", "Medium", "Low")
    Me.txtStart.Value = Format(Date, "yyyy-mm-dd")
    Me.txtDays.Value = 10
    Me.txtCost.Value = 0
    Me.txtBenefit.Value = 0
    Me.lblStatus.Caption = "Nhập thông tin rồi chọn Lưu."
End Sub

Private Sub btnSave_Click()
    Dim ws As Worksheet
    Dim lastRow As Long, nextRow As Long, nextId As String
    Dim days As Long
    On Error GoTo Failed

    If Me.cboWorkstream.ListIndex = -1 Or Me.cboOwner.ListIndex = -1 Then
        Me.lblStatus.Caption = "Chọn Workstream và Owner."
        Exit Sub
    End If
    If Me.cboStatus.ListIndex = -1 Or Me.cboPriority.ListIndex = -1 Then
        Me.lblStatus.Caption = "Chọn Trạng thái và Ưu tiên."
        Exit Sub
    End If
    If Not IsDate(Me.txtStart.Value) Then
        Me.lblStatus.Caption = "Ngày bắt đầu không hợp lệ (YYYY-MM-DD)."
        Exit Sub
    End If
    If Not IsNumeric(Me.txtDays.Value) Then
        Me.lblStatus.Caption = "Số ngày phải là số."
        Exit Sub
    End If
    days = CLng(Me.txtDays.Value)
    If days < 1 Or days > 365 Then
        Me.lblStatus.Caption = "Số ngày phải từ 1 đến 365."
        Exit Sub
    End If
    If Not IsNumeric(Me.txtCost.Value) Or Not IsNumeric(Me.txtBenefit.Value) Then
        Me.lblStatus.Caption = "Chi phí và lợi ích phải là số."
        Exit Sub
    End If

    Set ws = ThisWorkbook.Worksheets("Data")
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    nextRow = lastRow + 1
    nextId = "T" & Format(lastRow, "000")
    ws.Cells(nextRow, 1).Value = nextId
    ws.Cells(nextRow, 2).Value = Me.cboWorkstream.Value
    ws.Cells(nextRow, 3).Value = Me.cboOwner.Value
    ws.Cells(nextRow, 4).Value = CDate(Me.txtStart.Value)
    ws.Cells(nextRow, 5).Value = CDate(Me.txtStart.Value) + days - 1
    ws.Cells(nextRow, 6).Value = days
    ws.Cells(nextRow, 7).Value = 0
    ws.Cells(nextRow, 8).Value = CDbl(Me.txtCost.Value)
    ws.Cells(nextRow, 9).Value = CDbl(Me.txtBenefit.Value)
    ws.Cells(nextRow, 10).Value = Me.cboStatus.Value
    ws.Cells(nextRow, 11).Value = Me.cboPriority.Value
    Me.lblStatus.Caption = "Đã lưu " & nextId & "."
    ClearForm
    ThisWorkbook.RefreshAll
    Exit Sub

Failed:
    Me.lblStatus.Caption = "Lỗi: " & Err.Description
End Sub

Private Sub btnClear_Click()
    ClearForm
End Sub

Private Sub btnCancel_Click()
    Unload Me
End Sub

Private Sub ClearForm()
    Me.cboWorkstream.ListIndex = -1
    Me.cboOwner.ListIndex = -1
    Me.cboStatus.ListIndex = -1
    Me.cboPriority.ListIndex = -1
    Me.txtStart.Value = Format(Date, "yyyy-mm-dd")
    Me.txtDays.Value = 10
    Me.txtCost.Value = 0
    Me.txtBenefit.Value = 0
    Me.lblStatus.Caption = "Sẵn sàng."
End Sub
'''

MODULE_CODE = r'''Option Explicit

Public Sub ShowEntryForm()
    frmEntry.Show
End Sub

Public Sub FilterRisk()
    On Error Resume Next
    With ThisWorkbook.Worksheets("Data")
        .AutoFilter.ShowAllData
        .Range("A1:K25").AutoFilter Field:=10, Criteria1:="At risk"
    End With
    ThisWorkbook.RefreshAll
End Sub

Public Sub FilterAll()
    On Error Resume Next
    ThisWorkbook.Worksheets("Data").AutoFilter.ShowAllData
    ThisWorkbook.RefreshAll
End Sub
'''


def _set(control, **props) -> None:
    for key, value in props.items():
        try:
            setattr(control, key, value)
        except Exception:
            pass


def _label(controls, name, caption, x, y, w, h, *, size=9, bold=False,
           color="#404040", back="#F7F9FC", align=-1):
    c = controls.Add("Forms.Label.1", name, True)
    _set(c, Caption=caption, Left=x, Top=y, Width=w, Height=h,
         BackColor=_rgb(back), ForeColor=_rgb(color), TextAlign=align)
    c.Font.Name = "Segoe UI"
    c.Font.Size = size
    c.Font.Bold = bold
    return c


def _textbox(controls, name, x, y, w, h):
    c = controls.Add("Forms.TextBox.1", name, True)
    _set(c, Left=x, Top=y, Width=w, Height=h, BackColor=_rgb("#FFFFFF"),
         ForeColor=_rgb("#1A1A1A"), BorderStyle=1)
    c.Font.Name = "Segoe UI"
    c.Font.Size = 10
    return c


def _combo(controls, name, x, y, w, h):
    c = controls.Add("Forms.ComboBox.1", name, True)
    _set(c, Left=x, Top=y, Width=w, Height=h, Style=2,
         BackColor=_rgb("#FFFFFF"), ForeColor=_rgb("#1A1A1A"))
    c.Font.Name = "Segoe UI"
    c.Font.Size = 10
    return c


def _button(controls, name, caption, x, y, w, h, *, back, fore="#FFFFFF"):
    c = controls.Add("Forms.CommandButton.1", name, True)
    _set(c, Caption=caption, Left=x, Top=y, Width=w, Height=h,
         BackColor=_rgb(back), ForeColor=_rgb(fore))
    c.Font.Name = "Segoe UI"
    c.Font.Size = 10
    c.Font.Bold = True
    return c


def build_form(xlsm_path: str | Path, *, form_name: str = FORM_NAME) -> dict:
    """Add the form and module; return a control inventory.  None if blocked."""
    if __import__("sys").platform != "win32":
        return {"ok": False, "reason": "Windows only"}
    try:
        import win32com.client as win32
    except Exception as exc:
        return {"ok": False, "reason": f"pywin32 unavailable: {exc}"}
    path = Path(xlsm_path).resolve()
    excel = wb = None
    try:
        excel = win32.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(path))
        project = wb.VBProject
        for comp in list(project.VBComponents):
            if comp.Name in {form_name, MODULE_NAME}:
                project.VBComponents.Remove(comp)
        form = project.VBComponents.Add(3)  # vbext_ct_MSForm
        form.Name = form_name
        try:
            form.Properties("Caption").Value = "Nhập công việc"
            form.Properties("Width").Value = 430
            form.Properties("Height").Value = 360
            form.Properties("BackColor").Value = _rgb("#F7F9FC")
        except Exception:
            pass
        designer = form.Designer
        controls = designer.Controls
        _label(controls, "lblTitle", "NHẬP CÔNG VIỆC", 20, 12, 390, 30,
               size=16, bold=True, color="#1F4E79", back="#F7F9FC")
        _label(controls, "lblHint", "Biểu mẫu ghi vào sheet Data (ẩn).", 22, 40, 390, 16,
               size=9, color="#7F7F7F")
        rows = [
            ("Workstream", "cboWorkstream", 60, "combo"),
            ("Owner", "cboOwner", 60, "combo"),
            ("Ngày bắt đầu", "txtStart", 100, "text"),
            ("Số ngày", "txtDays", 100, "text"),
            ("Chi phí (triệu)", "txtCost", 140, "text"),
            ("Lợi ích (triệu)", "txtBenefit", 140, "text"),
            ("Trạng thái", "cboStatus", 180, "combo"),
            ("Ưu tiên", "cboPriority", 180, "combo"),
        ]
        for i, (label, name, y, kind) in enumerate(rows):
            x = 22 if i % 2 == 0 else 230
            _label(controls, f"lbl{i}", label, x, y, 90, 20, size=9, bold=True)
            cx = x + 94
            width = 104 if i % 2 == 0 else 96
            if kind == "combo":
                _combo(controls, name, cx, y - 2, width, 22)
            else:
                _textbox(controls, name, cx, y - 2, width, 22)
        _button(controls, "btnSave", "Lưu", 130, 220, 90, 30, back="#1F4E79")
        _button(controls, "btnClear", "Xóa", 230, 220, 90, 30, back="#C55A11")
        _button(controls, "btnCancel", "Hủy", 330, 220, 72, 30, back="#7F7F7F")
        _label(controls, "lblStatus", "Sẵn sàng.", 22, 265, 380, 40,
               size=9, color="#1F4E79", back="#EAF1F8")
        form.CodeModule.AddFromString(FORM_CODE)
        module = project.VBComponents.Add(1)  # vbext_ct_StdModule
        module.Name = MODULE_NAME
        module.CodeModule.AddFromString(MODULE_CODE)
        try:
            wb.Save()
        except Exception:
            wb.SaveAs(str(path), FileFormat=52)
        inventory = inspect_open_form(form)
        return {"ok": True, "path": str(path), "form": form_name,
                "controls": inventory, "module": MODULE_NAME}
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}
    finally:
        if wb is not None:
            try:
                wb.Close(False)
            except Exception:
                pass
        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass


def inspect_open_form(form) -> list[dict]:
    out = []
    for control in form.Designer.Controls:
        out.append({
            "name": control.Name,
            "type": control.ProgID if hasattr(control, "ProgID") else type(control).__name__,
            "caption": getattr(control, "Caption", ""),
            "left": int(getattr(control, "Left", 0)),
            "top": int(getattr(control, "Top", 0)),
            "width": int(getattr(control, "Width", 0)),
            "height": int(getattr(control, "Height", 0)),
        })
    return out


def inspect_workbook(xlsm_path: str | Path) -> dict:
    if __import__("sys").platform != "win32":
        return {"ok": False, "reason": "Windows only"}
    try:
        import win32com.client as win32
    except Exception as exc:
        return {"ok": False, "reason": f"pywin32 unavailable: {exc}"}
    path = Path(xlsm_path).resolve()
    excel = wb = None
    try:
        excel = win32.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(str(path))
        project = wb.VBProject
        names = [c.Name for c in project.VBComponents]
        form = next((c for c in project.VBComponents if c.Name == FORM_NAME), None)
        controls = inspect_open_form(form) if form is not None else []
        return {"ok": form is not None, "components": names, "controls": controls,
                "form_code_has_save": bool(form and "btnSave_Click" in form.CodeModule.Lines(1, 2000))}
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}
    finally:
        if wb is not None:
            try:
                wb.Close(False)
            except Exception:
                pass
        if excel is not None:
            try:
                excel.Quit()
            except Exception:
                pass


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("build")
    p.add_argument("xlsm", type=Path)
    p = sub.add_parser("inspect")
    p.add_argument("xlsm", type=Path)
    args = parser.parse_args()
    if args.cmd == "build":
        result = build_form(args.xlsm)
        if result.get("ok"):
            try:
                from .vba_forge import normalize_button_macros
            except ImportError:
                from vba_forge import normalize_button_macros
            normalize_button_macros(args.xlsm)
    else:
        result = inspect_workbook(args.xlsm)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
