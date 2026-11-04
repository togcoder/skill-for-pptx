"""Interactive PowerPoint slide-show harness (T058). EXPERIMENTAL.

Antigravity multi-domain design research lab.

What it does
------------
Starts a real PowerPoint slide show in a *windowed* show window, finds that
window on the interactive desktop, maps slide points (points, as stored in the
PPTX) to physical screen pixels under per-monitor DPI awareness, sends real
Win32 mouse clicks to trigger shapes, captures the frames before and after, and
asserts that pixels changed inside the target shape's box.

Why it exists
-------------
T057 found that every "interactive" claim in the lab stopped at rung 4
(PowerPoint parsed the file).  ``SlideShowView.GotoClick`` only drives the
main animation sequence; it is a no-op for ``interactiveSeq`` shape triggers.
This module drives the real input path instead, so a trigger can be observed
end to end without a human at the keyboard.

Evidence boundary
-----------------
A passing run is **rung 5b**: COM-driven live playback, machine-asserted, not
human-reviewed.  It is never rung 6 and never
``powerpoint_playback_verified``.

Known constraints (recorded in the T058 report)
-----------------------------------------------
* Windows only; needs an interactive desktop (``WinSta0\\Default``, session
  != 0, input desktop openable).
* The windowed show window is class ``PPTFrameClass`` with a title starting
  ``PowerPoint Slide Show -``.  ``screenClass`` is the fullscreen show window.
  T057 searched only for ``screenClass`` and therefore found nothing.
* PowerPoint reports window geometry in points at 96 DPI (``Width`` 864 for a
  1440 px window at 125 %).  ``GetWindowRect`` is used instead.
* The show window may be restored under the taskbar; the harness moves it into
  the monitor work area before capturing.
* A ``NUIScrollbar`` child window can overlay the right edge of the slide.
  Clicks landing on it are refused (``TARGET_UNDER_SCROLLBAR``).

Usage
-----
    python scripts/interactive_show_harness.py probe
    python scripts/interactive_show_harness.py run --plan plan.json --out DIR

Exit codes: 0 all assertions passed, 2 assertion failed, 3 infrastructure
error (no desktop / no show window / foreground denied), 4 harness error.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# Error taxonomy: an infrastructure failure must never look like a product
# failure, and a product failure must never be reported as a pass.
# --------------------------------------------------------------------------


class HarnessError(RuntimeError):
    code = "HARNESS_ERROR"
    exit_code = 4

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message)
        self.message = message
        self.details = details

    def as_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class InfraError(HarnessError):
    code = "INFRA_ERROR"
    exit_code = 3


class NoInteractiveDesktop(InfraError):
    code = "INFRA_NO_INTERACTIVE_DESKTOP"


class ShowWindowNotFound(InfraError):
    code = "INFRA_SHOW_WINDOW_NOT_FOUND"


class ForegroundDenied(InfraError):
    code = "INFRA_FOREGROUND_DENIED"


class WindowObstructed(InfraError):
    code = "INFRA_WINDOW_OBSTRUCTED"


class InputDenied(InfraError):
    code = "INFRA_INPUT_DENIED"


class MappingError(HarnessError):
    code = "MAPPING_ERROR"


class AssertionFailed(HarnessError):
    code = "ASSERTION_FAILED"
    exit_code = 2


# --------------------------------------------------------------------------
# Pure geometry
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Rect:
    """Screen-pixel rectangle, edges inclusive-exclusive like Win32 RECT."""

    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def center(self) -> Tuple[float, float]:
        return (self.left + self.width / 2.0, self.top + self.height / 2.0)

    def inset(self, px: float) -> "Rect":
        return Rect(self.left + px, self.top + px, self.right - px, self.bottom - px)

    def contains_point(self, x: float, y: float, tol: float = 0.0) -> bool:
        return (self.left - tol <= x <= self.right + tol
                and self.top - tol <= y <= self.bottom + tol)

    def contains_rect(self, other: "Rect", tol: float = 0.0) -> bool:
        return (self.left - tol <= other.left and self.top - tol <= other.top
                and other.right <= self.right + tol and other.bottom <= self.bottom + tol)

    def union(self, other: "Rect") -> "Rect":
        return Rect(min(self.left, other.left), min(self.top, other.top),
                    max(self.right, other.right), max(self.bottom, other.bottom))

    def to_bbox(self) -> Tuple[int, int, int, int]:
        return (int(round(self.left)), int(round(self.top)),
                int(round(self.right)), int(round(self.bottom)))

    def as_list(self) -> List[float]:
        return [round(self.left, 2), round(self.top, 2),
                round(self.right, 2), round(self.bottom, 2)]

    @classmethod
    def from_win32(cls, r: Any) -> "Rect":
        return cls(float(r.left), float(r.top), float(r.right), float(r.bottom))


@dataclass(frozen=True)
class SlideMapping:
    """Affine map from slide points to physical screen pixels."""

    slide_width_pt: float
    slide_height_pt: float
    scale: float
    content: Rect

    @property
    def origin(self) -> Tuple[float, float]:
        return (self.content.left, self.content.top)

    def point(self, x_pt: float, y_pt: float) -> Tuple[float, float]:
        return (self.content.left + x_pt * self.scale,
                self.content.top + y_pt * self.scale)

    def box(self, left_pt: float, top_pt: float,
            width_pt: float, height_pt: float) -> Rect:
        return Rect(self.content.left + left_pt * self.scale,
                    self.content.top + top_pt * self.scale,
                    self.content.left + (left_pt + width_pt) * self.scale,
                    self.content.top + (top_pt + height_pt) * self.scale)

    def shifted(self, dx: float, dy: float, scale: Optional[float] = None) -> "SlideMapping":
        s = self.scale if scale is None else scale
        return SlideMapping(
            slide_width_pt=self.slide_width_pt,
            slide_height_pt=self.slide_height_pt,
            scale=s,
            content=Rect(self.content.left + dx, self.content.top + dy,
                         self.content.right + dx, self.content.bottom + dy),
        )

    def with_content(self, content: Rect) -> "SlideMapping":
        return SlideMapping(self.slide_width_pt, self.slide_height_pt, self.scale, content)


def predict_mapping(client: Rect, slide_width_pt: float, slide_height_pt: float,
                    reserve_right_px: float = 0.0) -> SlideMapping:
    """Aspect-fit the slide into the client area, centred.

    ``reserve_right_px`` accounts for a scrollbar that PowerPoint overlays on
    the right edge in some window geometries; calibration measures the real
    offset, so this is only the starting estimate.
    """
    if slide_width_pt <= 0 or slide_height_pt <= 0:
        raise MappingError("slide size must be positive")
    usable_width = client.width - max(0.0, reserve_right_px)
    if usable_width <= 0 or client.height <= 0:
        raise MappingError("client area is empty")
    scale = min(usable_width / slide_width_pt, client.height / slide_height_pt)
    content_w = slide_width_pt * scale
    content_h = slide_height_pt * scale
    ox = client.left + (usable_width - content_w) / 2.0
    oy = client.top + (client.height - content_h) / 2.0
    return SlideMapping(slide_width_pt, slide_height_pt, scale,
                        Rect(ox, oy, ox + content_w, oy + content_h))


def union_of_boxes(boxes: Iterable[Rect]) -> Optional[Rect]:
    out: Optional[Rect] = None
    for b in boxes:
        out = b if out is None else out.union(b)
    return out


# --------------------------------------------------------------------------
# Image diff (Pillow only; no numpy dependency)
# --------------------------------------------------------------------------


def _require_pil():
    from PIL import Image, ImageChops, ImageStat  # noqa: F401
    return Image, ImageChops, ImageStat


def rgb_max_difference(before: Any, after: Any, box: Optional[Rect] = None) -> Any:
    """Return a single-channel image of max(|R|,|G|,|B|) per pixel."""
    Image, ImageChops, _ = _require_pil()
    a = before.convert("RGB")
    b = after.convert("RGB")
    if a.size != b.size:
        raise HarnessError(f"image size mismatch: {a.size} vs {b.size}")
    if box is not None:
        crop = (max(0, int(box.left)), max(0, int(box.top)),
                min(a.width, int(box.right)), min(a.height, int(box.bottom)))
        if crop[2] <= crop[0] or crop[3] <= crop[1]:
            raise HarnessError("diff box is empty after clamping", box=box.as_list())
        a = a.crop(crop)
        b = b.crop(crop)
    diff = ImageChops.difference(a, b)
    r, g, bl = diff.split()
    return ImageChops.lighter(ImageChops.lighter(r, g), bl)


def diff_stats(before: Any, after: Any, box: Optional[Rect] = None,
               threshold: int = 24) -> Dict[str, Any]:
    """Count pixels whose max channel delta exceeds ``threshold``."""
    _, _, ImageStat = _require_pil()
    d = rgb_max_difference(before, after, box)
    hist = d.histogram()
    total = d.width * d.height
    changed = int(sum(hist[threshold + 1:]))
    mean = sum(i * h for i, h in enumerate(hist)) / float(total)
    mask = d.point(lambda v: 255 if v > threshold else 0)
    bbox = mask.getbbox()
    origin_x = 0 if box is None else max(0, int(box.left))
    origin_y = 0 if box is None else max(0, int(box.top))
    return {
        "area_px": total,
        "changed_px": changed,
        "pct_changed": round(100.0 * changed / total, 4) if total else 0.0,
        "mean_abs": round(mean, 3),
        "changed_bbox": None if bbox is None else
        [bbox[0] + origin_x, bbox[1] + origin_y, bbox[2] + origin_x, bbox[3] + origin_y],
    }


def compare_frames(before: Any, after: Any, target: Optional[Rect],
                   threshold: int = 24) -> Dict[str, Any]:
    """Diff inside ``target`` and outside it, with a share-inside metric."""
    full = diff_stats(before, after, None, threshold)
    if target is None:
        return {"whole": full, "inside": full, "outside": None, "share_inside": 1.0}
    inside = diff_stats(before, after, target, threshold)
    outside_changed = full["changed_px"] - inside["changed_px"]
    outside_area = full["area_px"] - inside["area_px"]
    outside = {
        "area_px": outside_area,
        "changed_px": max(0, outside_changed),
        "pct_changed": round(100.0 * max(0, outside_changed) / outside_area, 4)
        if outside_area > 0 else 0.0,
    }
    share = (inside["changed_px"] / full["changed_px"]) if full["changed_px"] else 0.0
    return {"whole": full, "inside": inside, "outside": outside,
            "share_inside": round(share, 4)}


# --------------------------------------------------------------------------
# Mapping calibration against a PowerPoint slide export
# --------------------------------------------------------------------------


def calibrate_mapping(client_capture: Any, slide_export: Any, mapping: SlideMapping,
                      client: Rect, max_shift: int = 48,
                      ignore_right: int = 0) -> Dict[str, Any]:
    """Search the offset that best aligns an exported slide with the capture.

    The export is scaled to the predicted content size, then compared with the
    capture at integer offsets around the prediction (step 4, then step 1).
    Returns the measured shift and the MAE before/after.
    """
    Image, ImageChops, ImageStat = _require_pil()
    width = int(round(mapping.content.width))
    height = int(round(mapping.content.height))
    if width <= 1 or height <= 1:
        raise MappingError("predicted content rect is empty")
    ref = slide_export.convert("L").resize((width, height), Image.LANCZOS)
    cap = client_capture.convert("L")
    pred_x = int(round(mapping.content.left - client.left))
    pred_y = int(round(mapping.content.top - client.top))

    def mae_at(dx: int, dy: int) -> Optional[float]:
        x = pred_x + dx
        y = pred_y + dy
        if x < 0 or y < 0 or x + width > cap.width or y + height > cap.height:
            return None
        crop = cap.crop((x, y, x + width, y + height))
        if ignore_right > 0:
            crop = crop.crop((0, 0, max(1, width - ignore_right), height))
            r = ref.crop((0, 0, max(1, width - ignore_right), height))
        else:
            r = ref
        return float(ImageStat.Stat(ImageChops.difference(crop, r)).mean[0])

    predicted = mae_at(0, 0)
    coarse_step = 4
    best: Optional[Tuple[float, int, int]] = None
    span = range(-max_shift, max_shift + 1, coarse_step)
    for dy in span:
        for dx in span:
            m = mae_at(dx, dy)
            if m is not None and (best is None or m < best[0]):
                best = (m, dx, dy)
    if best is None:
        raise MappingError("calibration could not place the export inside the capture")
    # Refine by one pixel around the coarse winner.
    fine = best
    for dy in range(best[2] - coarse_step + 1, best[2] + coarse_step):
        for dx in range(best[1] - coarse_step + 1, best[1] + coarse_step):
            m = mae_at(dx, dy)
            if m is not None and m < fine[0]:
                fine = (m, dx, dy)
    best = fine
    return {
        "predicted_offset_px": [pred_x, pred_y],
        "shift_px": [best[1], best[2]],
        "mae": round(best[0], 3),
        "mae_predicted": round(predicted, 3) if predicted is not None else None,
        "improved_mae": round((predicted - best[0]), 3) if predicted is not None else None,
        "search_boundary": abs(best[1]) >= max_shift or abs(best[2]) >= max_shift,
        "content_size_px": [width, height],
        "ignored_right_px": ignore_right,
    }


# --------------------------------------------------------------------------
# Win32 desktop layer (ctypes only; COM is imported separately)
# --------------------------------------------------------------------------

_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_shcore = None
try:  # Windows 8.1+
    _shcore = ctypes.WinDLL("shcore", use_last_error=True)
except OSError:
    _shcore = None

WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

_user32.EnumWindows.argtypes = [WNDENUMPROC, wt.LPARAM]
_user32.EnumWindows.restype = wt.BOOL
_user32.EnumChildWindows.argtypes = [wt.HWND, WNDENUMPROC, wt.LPARAM]
_user32.EnumChildWindows.restype = wt.BOOL
_user32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
_user32.GetClassNameW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
_user32.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
_user32.GetClientRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
_user32.ClientToScreen.argtypes = [wt.HWND, ctypes.POINTER(wt.POINT)]
_user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
_user32.GetForegroundWindow.restype = wt.HWND
_user32.SetForegroundWindow.argtypes = [wt.HWND]
_user32.BringWindowToTop.argtypes = [wt.HWND]
_user32.SetFocus.argtypes = [wt.HWND]
_user32.AttachThreadInput.argtypes = [wt.DWORD, wt.DWORD, wt.BOOL]
_user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
_user32.GetCursorPos.argtypes = [ctypes.POINTER(wt.POINT)]
_user32.mouse_event.argtypes = [wt.DWORD, wt.DWORD, wt.DWORD, wt.DWORD, ctypes.c_void_p]
_user32.WindowFromPoint.argtypes = [wt.POINT]
_user32.WindowFromPoint.restype = wt.HWND
_user32.GetAncestor.argtypes = [wt.HWND, ctypes.c_uint]
_user32.GetAncestor.restype = wt.HWND
_user32.MonitorFromWindow.argtypes = [wt.HWND, wt.DWORD]
_user32.MonitorFromWindow.restype = wt.HANDLE
_user32.SetWindowPos.argtypes = [wt.HWND, wt.HWND, ctypes.c_int, ctypes.c_int,
                                 ctypes.c_int, ctypes.c_int, ctypes.c_uint]
_user32.ShowWindow.argtypes = [wt.HWND, ctypes.c_int]
_user32.IsWindowVisible.argtypes = [wt.HWND]
_user32.IsIconic.argtypes = [wt.HWND]
_user32.GetDpiForWindow.argtypes = [wt.HWND]
_user32.GetDpiForWindow.restype = ctypes.c_uint
_user32.GetSystemMetrics.argtypes = [ctypes.c_int]
_user32.GetSystemMetrics.restype = ctypes.c_int
_user32.GetProcessWindowStation.restype = wt.HANDLE
_user32.GetThreadDesktop.argtypes = [wt.DWORD]
_user32.GetThreadDesktop.restype = wt.HANDLE
_user32.GetUserObjectInformationW.argtypes = [
    wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD, ctypes.POINTER(wt.DWORD)]
_user32.GetUserObjectInformationW.restype = wt.BOOL
_user32.OpenInputDesktop.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
_user32.OpenInputDesktop.restype = wt.HANDLE
_user32.CloseDesktop.argtypes = [wt.HANDLE]
_user32.keybd_event.argtypes = [wt.BYTE, wt.BYTE, wt.DWORD, ctypes.c_void_p]
_user32.keybd_event.restype = None
_kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
_kernel32.OpenProcess.restype = wt.HANDLE
_kernel32.GetExitCodeProcess.argtypes = [wt.HANDLE, ctypes.POINTER(wt.DWORD)]
_kernel32.GetExitCodeProcess.restype = wt.BOOL
_kernel32.CloseHandle.argtypes = [wt.HANDLE]
_kernel32.CloseHandle.restype = wt.BOOL
_kernel32.GetCurrentThreadId.restype = wt.DWORD
_kernel32.ProcessIdToSessionId.argtypes = [wt.DWORD, ctypes.POINTER(wt.DWORD)]

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
GA_ROOT = 2
MONITOR_DEFAULTTONEAREST = 2
SW_RESTORE = 9
SWP_SHOWWINDOW = 0x0040
SWP_NOACTIVATE = 0x0010
DESKTOP_READOBJECTS = 0x0001


class MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT),
                ("rcWork", wt.RECT), ("dwFlags", wt.DWORD)]


def enable_dpi_awareness() -> Dict[str, Any]:
    """Become per-monitor DPI aware v2 before any window geometry is read.

    Without this, Windows virtualises coordinates: a 1920x1080 display at 125 %
    is reported as 1536x864 and ``SetCursorPos`` receives the wrong pixels.
    This is exactly the 0.75/1.25 factor seen in earlier probes.
    """
    record: Dict[str, Any] = {"applied": None}
    try:
        ok = _user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        if ok:
            record["applied"] = "per_monitor_v2"
    except AttributeError:
        pass
    except OSError:
        pass
    if record["applied"] is None and _shcore is not None:
        try:
            if _shcore.SetProcessDpiAwareness(2) == 0:
                record["applied"] = "per_monitor"
        except OSError:
            pass
    if record["applied"] is None:
        try:
            if _user32.SetProcessDPIAware():
                record["applied"] = "system"
        except OSError:
            pass
    record["applied"] = record["applied"] or "none"
    record["system_dpi"] = int(_user32.GetDpiForSystem())
    record["screen_px"] = [int(_user32.GetSystemMetrics(0)), int(_user32.GetSystemMetrics(1))]
    return record


def _window_text(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(512)
    _user32.GetWindowTextW(hwnd, buf, 512)
    return buf.value


def _window_class(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    _user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _window_pid(hwnd: int) -> int:
    pid = wt.DWORD()
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def window_rect(hwnd: int) -> Rect:
    r = wt.RECT()
    _user32.GetWindowRect(hwnd, ctypes.byref(r))
    return Rect.from_win32(r)


def client_rect(hwnd: int) -> Rect:
    r = wt.RECT()
    _user32.GetClientRect(hwnd, ctypes.byref(r))
    pt = wt.POINT(0, 0)
    _user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return Rect(pt.x, pt.y, pt.x + r.right, pt.y + r.bottom)


def work_area(hwnd: int) -> Tuple[Rect, Rect]:
    mon = _user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    if not _user32.GetMonitorInfoW(mon, ctypes.byref(mi)):
        raise InfraError("GetMonitorInfoW failed", error=ctypes.get_last_error())
    return Rect.from_win32(mi.rcMonitor), Rect.from_win32(mi.rcWork)


def enumerate_windows(pid: Optional[int] = None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def callback(hwnd, _lparam):
        if pid is not None and _window_pid(hwnd) != pid:
            return True
        r = wt.RECT()
        _user32.GetWindowRect(hwnd, ctypes.byref(r))
        out.append({
            "hwnd": int(hwnd),
            "class": _window_class(hwnd),
            "title": _window_text(hwnd),
            "pid": _window_pid(hwnd),
            "rect": Rect.from_win32(r).as_list(),
            "visible": bool(_user32.IsWindowVisible(hwnd)),
            "minimized": bool(_user32.IsIconic(hwnd)),
            "dpi": int(_user32.GetDpiForWindow(hwnd)),
        })
        return True

    _user32.EnumWindows(WNDENUMPROC(callback), 0)
    return out


def enumerate_children(hwnd: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def callback(child, _lparam):
        r = wt.RECT()
        _user32.GetWindowRect(child, ctypes.byref(r))
        out.append({
            "hwnd": int(child),
            "class": _window_class(child),
            "title": _window_text(child),
            "rect": Rect.from_win32(r).as_list(),
            "visible": bool(_user32.IsWindowVisible(child)),
        })
        return True

    _user32.EnumChildWindows(hwnd, WNDENUMPROC(callback), 0)
    return out


def describe_foreground() -> Dict[str, Any]:
    hwnd = int(_user32.GetForegroundWindow() or 0)
    if not hwnd:
        return {"hwnd": 0, "class": "", "title": "", "pid": 0}
    return {"hwnd": hwnd, "class": _window_class(hwnd),
            "title": _window_text(hwnd), "pid": _window_pid(hwnd)}


def desktop_capability() -> Dict[str, Any]:
    """Report whether this process can drive a real interactive desktop."""
    k32 = _kernel32
    pid = k32.GetCurrentProcessId()
    session = wt.DWORD()
    k32.ProcessIdToSessionId(pid, ctypes.byref(session))

    def _object_name(handle: int) -> str:
        if not handle:
            return ""
        buf = ctypes.create_unicode_buffer(256)
        need = wt.DWORD()
        ok = _user32.GetUserObjectInformationW(handle, 2, buf, ctypes.sizeof(buf),
                                               ctypes.byref(need))
        return buf.value if ok else ""

    station = _object_name(int(_user32.GetProcessWindowStation() or 0))
    desk = _object_name(int(_user32.GetThreadDesktop(k32.GetCurrentThreadId()) or 0))
    input_ok = False
    input_error = 0
    try:
        h = _user32.OpenInputDesktop(0, False, DESKTOP_READOBJECTS)
        input_ok = bool(h)
        if h:
            _user32.CloseDesktop(h)
        else:
            input_error = ctypes.get_last_error()
    except AttributeError:
        input_error = -1
    fg = describe_foreground()
    interactive = (session.value != 0 and station == "WinSta0" and desk == "Default")
    return {
        "pid": pid,
        "session_id": int(session.value),
        "window_station": station,
        "desktop": desk,
        "input_desktop_openable": input_ok,
        "input_desktop_error": input_error,
        "interactive_desktop": bool(interactive),
        "foreground": fg,
        "screen_px": [int(_user32.GetSystemMetrics(0)), int(_user32.GetSystemMetrics(1))],
        "system_dpi": int(_user32.GetDpiForSystem()),
    }


def require_interactive_desktop() -> Dict[str, Any]:
    cap = desktop_capability()
    if not cap["interactive_desktop"]:
        raise NoInteractiveDesktop(
            "no interactive desktop: shell cannot drive a slide show",
            **cap)
    return cap


def is_show_window(class_name: str, title: str, deck_stem: str = "") -> bool:
    """Windowed shows are PPTFrameClass; fullscreen shows are screenClass."""
    cls = class_name.lower()
    if cls == "screenclass":
        return True
    if cls == "pptframeclass" and title.startswith("PowerPoint Slide Show -"):
        return True
    return False


def find_show_window(pid: int, deck_stem: str = "", timeout_s: float = 12.0,
                     poll_s: float = 0.25) -> Dict[str, Any]:
    deadline = time.time() + timeout_s
    seen: List[Dict[str, Any]] = []
    while time.time() < deadline:
        seen = [w for w in enumerate_windows(pid)
                if w["visible"] and is_show_window(w["class"], w["title"], deck_stem)]
        # Prefer the windowed show (PPTFrameClass) over a fullscreen one.
        seen.sort(key=lambda w: (w["class"].lower() != "pptframeclass",))
        if seen:
            return {"window": seen[0], "candidates": seen,
                    "waited_ms": int((timeout_s - (deadline - time.time())) * 1000)}
        time.sleep(poll_s)
    raise ShowWindowNotFound(
        f"no PowerPoint show window for pid {pid} within {timeout_s:.0f}s",
        pid=pid, deck_stem=deck_stem, candidates=seen, timeout_s=timeout_s)


def _cursor_probe(x: int, y: int) -> Dict[str, Any]:
    ok = bool(_user32.SetCursorPos(int(x), int(y)))
    return {"ok": ok, "error": 0 if ok else ctypes.get_last_error(),
            "point": [int(x), int(y)]}


def _alt_key_nudge() -> None:
    """A synthetic Alt tap unlocks SetForegroundWindow on Windows."""
    VK_MENU = 0x12
    KEYEVENTF_KEYUP = 0x0002
    try:
        _user32.keybd_event(VK_MENU, 0, 0, None)
        _user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, None)
        time.sleep(0.05)
    except Exception:
        pass


def _switch_to_window(hwnd: int, *, attach_target: bool, attach_foreground: bool,
                      topmost_nudge: bool, alt_nudge: bool) -> Dict[str, Any]:
    """One foreground attempt; returns what was tried and the resulting HWND."""
    my_tid = int(_kernel32.GetCurrentThreadId())
    fg = int(_user32.GetForegroundWindow() or 0)
    fg_tid = int(_user32.GetWindowThreadProcessId(fg, None)) if fg else 0
    target_tid = int(_user32.GetWindowThreadProcessId(hwnd, None))
    attached: List[int] = []
    try:
        if attach_target and target_tid and target_tid != my_tid:
            if _user32.AttachThreadInput(my_tid, target_tid, True):
                attached.append(target_tid)
        if attach_foreground and fg_tid and fg_tid != my_tid and fg_tid not in attached:
            if _user32.AttachThreadInput(my_tid, fg_tid, True):
                attached.append(fg_tid)
        if topmost_nudge:
            HWND_TOPMOST = -1
            SWP_NOMOVE_NOSIZE = 0x0002 | 0x0001
            _user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE_NOSIZE)
        if alt_nudge:
            _alt_key_nudge()
        _user32.BringWindowToTop(hwnd)
        _user32.SetForegroundWindow(hwnd)
        if attach_foreground or attach_target:
            _user32.SetFocus(hwnd)
        if topmost_nudge:
            HWND_NOTOPMOST = -2
            SWP_NOMOVE_NOSIZE = 0x0002 | 0x0001
            _user32.SetWindowPos(hwnd, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE_NOSIZE)
    finally:
        for tid in attached:
            _user32.AttachThreadInput(my_tid, tid, False)
    time.sleep(0.16)
    cr = client_rect(hwnd)
    probe = _cursor_probe(int(cr.center[0]), int(cr.center[1]))
    return {"foreground_before": fg, "attached_to": attached,
            "attach_target": attach_target, "attach_foreground": attach_foreground,
            "topmost_nudge": topmost_nudge, "alt_nudge": alt_nudge,
            "cursor_probe": probe,
            "foreground_after": int(_user32.GetForegroundWindow() or 0)}


def force_foreground(hwnd: int) -> Dict[str, Any]:
    record: Dict[str, Any] = {"attempts": [], "ok": False}
    strategies = [
        ("attach_foreground", dict(attach_target=False, attach_foreground=True,
                                   topmost_nudge=False, alt_nudge=False)),
        ("topmost_nudge", dict(attach_target=False, attach_foreground=False,
                               topmost_nudge=True, alt_nudge=False)),
        ("alt_key_nudge", dict(attach_target=False, attach_foreground=False,
                               topmost_nudge=True, alt_nudge=True)),
        ("attach_target", dict(attach_target=True, attach_foreground=True,
                               topmost_nudge=False, alt_nudge=False)),
    ]
    for i, (label, kwargs) in enumerate(strategies):
        fg = int(_user32.GetForegroundWindow() or 0)
        if fg == hwnd:
            record["ok"] = True
            record["attempts"].append({"n": i, "already_foreground": True,
                                       "foreground_before": fg})
            break
        if _user32.IsIconic(hwnd):
            _user32.ShowWindow(hwnd, SW_RESTORE)
        r = _switch_to_window(hwnd, **kwargs)
        r.update({"n": i, "strategy": label})
        record["attempts"].append(r)
        if r["foreground_after"] == hwnd:
            record["ok"] = True
            record["strategy"] = label
            break
    record["cursor_ok"] = any(a.get("cursor_probe", {}).get("ok")
                              for a in record["attempts"])
    record["foreground_final"] = describe_foreground()
    return record


def click_title_bar(hwnd: int) -> Dict[str, Any]:
    """Activate a windowed show by clicking its title bar (no slide hit)."""
    wr = window_rect(hwnd)
    cr = client_rect(hwnd)
    title_h = int(round(cr.top - wr.top))
    if title_h < 12:
        return {"attempted": False, "reason": "no title bar"}
    x = int(wr.left + min(120, wr.width / 2))
    y = int(wr.top + title_h / 2)
    res = click_at(x, y)
    time.sleep(0.25)
    res.update({"attempted": True, "point": [x, y], "title_height_px": title_h,
                "foreground_after": describe_foreground()})
    return res


def obstruction_at(hwnd: int, rect: Rect, points: Optional[Sequence[Tuple[int, int]]] = None
                   ) -> List[Dict[str, Any]]:
    """Return sampled points inside ``rect`` covered by a different top-level window."""
    if points is None:
        inset = 6
        xs = [rect.left + inset, rect.center[0], rect.right - inset]
        ys = [rect.top + inset, rect.center[1], rect.bottom - inset]
        points = [(int(x), int(y)) for x in xs for y in ys]
    bad: List[Dict[str, Any]] = []
    for x, y in points:
        h = int(_user32.WindowFromPoint(wt.POINT(x, y)) or 0)
        root = int(_user32.GetAncestor(h, GA_ROOT) or 0) if h else 0
        if root != hwnd:
            bad.append({"point": [x, y], "hwnd": h, "root": root,
                        "class": _window_class(h) if h else "",
                        "title": _window_text(h) if h else ""})
    return bad


def place_window_in_work_area(hwnd: int, slide_aspect: float,
                              margin_px: int = 8) -> Dict[str, Any]:
    """Move/resize the show window so it sits fully inside the monitor work area."""
    before = {"window": window_rect(hwnd).as_list(), "client": client_rect(hwnd).as_list()}
    monitor, work = work_area(hwnd)
    wr = window_rect(hwnd)
    cr = client_rect(hwnd)
    frame_w = int(round(wr.width - cr.width))
    frame_h = int(round(wr.height - cr.height))
    avail_w = max(64, int(work.width) - frame_w - margin_px * 2)
    avail_h = max(64, int(work.height) - frame_h - margin_px * 2)
    client_h = min(avail_h, int(round(avail_w / slide_aspect)))
    client_w = int(round(client_h * slide_aspect))
    if client_w > avail_w:
        client_w = avail_w
        client_h = int(round(client_w / slide_aspect))
    x = int(work.left) + margin_px + (avail_w - client_w) // 2
    y = int(work.top) + margin_px + (avail_h - client_h) // 2
    _user32.SetWindowPos(hwnd, 0, x, y, client_w + frame_w, client_h + frame_h,
                         SWP_SHOWWINDOW)
    time.sleep(0.35)
    after = {"window": window_rect(hwnd).as_list(), "client": client_rect(hwnd).as_list()}
    inside = (after["window"][0] >= work.left and after["window"][1] >= work.top
              and after["window"][2] <= work.right and after["window"][3] <= work.bottom)
    return {"before": before, "after": after, "monitor": monitor.as_list(),
            "work_area": work.as_list(), "frame_px": [frame_w, frame_h],
            "target_client_px": [client_w, client_h],
            "fully_inside_work_area": bool(inside)}


def scrollbar_children(hwnd: int) -> List[Dict[str, Any]]:
    return [c for c in enumerate_children(hwnd)
            if c["visible"] and "scrollbar" in c["class"].lower()]


def capture_rect(rect: Rect) -> Any:
    from PIL import ImageGrab
    img = ImageGrab.grab(bbox=rect.to_bbox(), all_screens=True)
    if img.size != (max(1, int(round(rect.width))), max(1, int(round(rect.height)))):
        # A DPI-virtualised grab can come back at the wrong size; fail loudly.
        raise InfraError("screen grab size does not match the requested rect",
                         requested=rect.as_list(), got=list(img.size))
    return img.convert("RGB")


def click_at(x: float, y: float) -> Dict[str, Any]:
    pt = wt.POINT()
    _user32.GetCursorPos(ctypes.byref(pt))
    before = [int(pt.x), int(pt.y)]
    if not _user32.SetCursorPos(int(round(x)), int(round(y))):
        err = ctypes.get_last_error()
        if err == 5:
            raise InputDenied("SetCursorPos denied: input desktop is not available",
                              x=x, y=y, error=err)
        raise InfraError("SetCursorPos failed", x=x, y=y, error=err)
    time.sleep(0.04)
    _user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, None)
    time.sleep(0.03)
    _user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, None)
    time.sleep(0.04)
    _user32.GetCursorPos(ctypes.byref(pt))
    return {"requested": [round(x, 2), round(y, 2)],
            "cursor_before": before, "cursor_after": [int(pt.x), int(pt.y)]}


# --------------------------------------------------------------------------
# PowerPoint COM session
# --------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _powerpnt_pids() -> set:
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process POWERPNT -ErrorAction SilentlyContinue).Id"],
            capture_output=True, text=True, timeout=20)
        return {int(x) for x in out.stdout.split() if x.strip().isdigit()}
    except Exception:
        return set()


def _kill_pid(pid: int) -> None:
    if not pid:
        return
    subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                   capture_output=True, text=True, timeout=20)


PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259


def _pid_alive(pid: int) -> bool:
    if not pid:
        return False
    handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
    if not handle:
        return False
    try:
        code = wt.DWORD()
        if not _kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == STILL_ACTIVE
    finally:
        _kernel32.CloseHandle(handle)


def wait_until_stable(capture: Callable[[], Any], timeout_s: float = 3.0,
                      interval_s: float = 0.12, eps_pct: float = 0.03,
                      need: int = 2, threshold: int = 24) -> Dict[str, Any]:
    """Poll frames until the screen stops changing; returns the settled frame."""
    started = time.time()
    last = capture()
    series: List[Dict[str, Any]] = []
    stable = 0
    while time.time() - started < timeout_s:
        time.sleep(interval_s)
        cur = capture()
        d = diff_stats(last, cur, None, threshold)
        series.append({"t_ms": int((time.time() - started) * 1000),
                       "pct": d["pct_changed"], "mean": d["mean_abs"]})
        if d["pct_changed"] <= eps_pct:
            stable += 1
            if stable >= need:
                return {"frame": cur, "settled": True, "series": series,
                        "elapsed_ms": int((time.time() - started) * 1000)}
        else:
            stable = 0
        last = cur
    return {"frame": last, "settled": False, "series": series,
            "elapsed_ms": int((time.time() - started) * 1000)}


class ShowSession:
    """Owns a dedicated PowerPoint instance and a windowed slide show."""

    def __init__(self, deck: Path, *, windowed: bool = True,
                 place_window: bool = True) -> None:
        self.deck = Path(deck).resolve()
        self.windowed = windowed
        self.place = place_window
        self.app = None
        self.pres = None
        self.pid = 0
        self.hwnd = 0
        self.info: Dict[str, Any] = {}
        self._pythoncom = None
        self._started = False

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> Dict[str, Any]:
        if not self.deck.is_file():
            raise HarnessError(f"deck not found: {self.deck}")
        try:
            import pythoncom
            import win32com.client
        except Exception as exc:  # pragma: no cover - environment specific
            raise InfraError("pywin32 is required for the COM half of the harness",
                             error=str(exc)) from exc
        self._pythoncom = pythoncom
        pythoncom.CoInitialize()
        # Let a previous instance finish shutting down; PowerPoint returns
        # "Object does not exist" if a new instance starts too early.
        existing = _powerpnt_pids()
        wait_started = time.time()
        while (time.time() - wait_started < 8.0
               and any(_pid_alive(p) for p in existing)):
            time.sleep(0.25)
        before = _powerpnt_pids()
        t0 = time.time()
        self.app = win32com.client.DispatchEx("PowerPoint.Application")
        self.info["com_instance_created_ms"] = int((time.time() - t0) * 1000)
        self.info["pids_before"] = sorted(before)
        try:
            self.app.Visible = True
            self.app.DisplayAlerts = 1          # ppAlertsNone: no modal dialogs
            try:
                self.app.AutomationSecurity = 3  # msoAutomationSecurityForceDisable
            except Exception:
                pass
            t0 = time.time()
            self.pres = self.app.Presentations.Open(
                str(self.deck), ReadOnly=True, Untitled=False, WithWindow=True)
            self.info["open_ms"] = int((time.time() - t0) * 1000)
            self.info["slide_count"] = int(self.pres.Slides.Count)
            self.info["slide_width_pt"] = float(self.pres.PageSetup.SlideWidth)
            self.info["slide_height_pt"] = float(self.pres.PageSetup.SlideHeight)
            self.info["version"] = str(getattr(self.app, "Version", ""))
            self.info["build"] = str(getattr(self.app, "Build", ""))
            self.info["application"] = str(getattr(self.app, "Name", ""))
            self.info["application_path"] = str(getattr(self.app, "Path", ""))
            self.pid = self._discover_pid(_powerpnt_pids() - before)
            self.info["pid"] = self.pid
            self._run_show()
            self._started = True
            return self.info
        except Exception:
            self.close()
            raise

    def _discover_pid(self, new_pids: Iterable[int]) -> int:
        stem = self.deck.stem
        # 1) Prefer a new PowerPoint process whose window title names the deck.
        for w in enumerate_windows():
            if stem in w["title"] and w["class"].lower() in ("pptframeclass", "screenclass"):
                cand = int(w["pid"])
                if cand not in set(new_pids) and new_pids:
                    continue
                return cand
        # 2) Fall back to a new process with any visible top-level window.
        for w in enumerate_windows():
            if int(w["pid"]) in set(new_pids) and w["visible"]:
                return int(w["pid"])
        # 3) Last resort: any PowerPoint window naming the deck.
        for w in enumerate_windows():
            if stem in w["title"]:
                return int(w["pid"])
        raise InfraError("could not identify the PowerPoint process", deck=self.deck.name,
                         new_pids=sorted(new_pids))

    def _acquire_foreground(self) -> Dict[str, Any]:
        rec = force_foreground(self.hwnd)
        if not rec["ok"]:
            rec["titlebar_activation"] = click_title_bar(self.hwnd)
            rec["ok"] = int(_user32.GetForegroundWindow() or 0) == self.hwnd
        return rec

    def _run_show(self) -> None:
        settings = self.pres.SlideShowSettings
        settings.ShowType = 2 if self.windowed else 1  # ppShowTypeWindow / Speaker
        settings.ShowWithAnimation = True
        settings.ShowWithNarration = False
        settings.AdvanceMode = 1                        # manual, never auto-advance
        t0 = time.time()
        attempts = []
        started = False
        for attempt in range(3):
            try:
                settings.Run()
                time.sleep(0.7)
                count = int(self.app.SlideShowWindows.Count)
                attempts.append({"attempt": attempt, "ok": count > 0,
                                 "show_windows": count})
                if count > 0:
                    started = True
                    break
            except Exception as exc:
                attempts.append({"attempt": attempt, "ok": False, "error": str(exc)})
            try:
                if int(self.app.SlideShowWindows.Count) > 0:
                    self.app.SlideShowWindows(1).View.Exit()
            except Exception:
                pass
            time.sleep(0.8)
        if not started:
            raise InfraError("SlideShowSettings.Run did not leave a running show",
                             attempts=attempts)
        self.info["run_attempts"] = attempts
        self.info["run_ms"] = int((time.time() - t0) * 1000)
        self.info["show_windows_count"] = int(self.app.SlideShowWindows.Count)
        found = find_show_window(self.pid, self.deck.stem)
        self.hwnd = int(found["window"]["hwnd"])
        self.info["show_window"] = found
        self.info["show_com_geometry"] = self._com_geometry()
        self.info["focus"] = self._acquire_foreground()
        if not self.info["focus"]["ok"]:
            raise ForegroundDenied("could not bring the show window to the foreground",
                                   focus=self.info["focus"])
        if self.place:
            aspect = self.info["slide_width_pt"] / self.info["slide_height_pt"]
            self.info["placement"] = place_window_in_work_area(self.hwnd, aspect)
            self.info["focus_after_place"] = self._acquire_foreground()
        self.info["show_client_rect"] = client_rect(self.hwnd).as_list()
        self.info["show_window_rect"] = window_rect(self.hwnd).as_list()
        self.info["scrollbars"] = scrollbar_children(self.hwnd)
        self.refresh_obstruction()

    def _com_geometry(self) -> Dict[str, Any]:
        try:
            w = self.app.SlideShowWindows(1)
            return {"left_pt": float(w.Left), "top_pt": float(w.Top),
                    "width_pt": float(w.Width), "height_pt": float(w.Height)}
        except Exception as exc:
            return {"error": str(exc)}

    def refresh_obstruction(self) -> None:
        cr = client_rect(self.hwnd)
        bad = obstruction_at(self.hwnd, cr)
        self.info["obstruction"] = {"sampled_points": 9, "bad": bad,
                                    "clean": not bad}
        if bad:
            raise WindowObstructed(
                "the show window is covered; a capture would be wrong",
                obstructed_by=bad[:4], window_rect=window_rect(self.hwnd).as_list())

    def ensure_foreground(self) -> None:
        if int(_user32.GetForegroundWindow() or 0) == self.hwnd:
            return
        rec = self._acquire_foreground()
        self.info.setdefault("foreground_recoveries", []).append(rec)
        if not rec["ok"]:
            raise ForegroundDenied("lost the foreground and could not recover it",
                                   focus=rec)

    def guarded_capture(self, expected_client: Optional[Rect] = None) -> Any:
        """Capture only when the show owns the foreground and is unobstructed."""
        if int(_user32.GetForegroundWindow() or 0) != self.hwnd:
            self.ensure_foreground()
            time.sleep(0.15)
        cr = client_rect(self.hwnd)
        if expected_client is not None:
            if (abs(cr.left - expected_client.left) > 1
                    or abs(cr.top - expected_client.top) > 1
                    or abs(cr.right - expected_client.right) > 1
                    or abs(cr.bottom - expected_client.bottom) > 1):
                raise InfraError("the show window moved during the run",
                                 expected=expected_client.as_list(),
                                 now=cr.as_list(), code="WINDOW_MOVED")
        bad = obstruction_at(self.hwnd, cr)
        if bad:
            raise WindowObstructed("the show window is covered during capture",
                                   obstructed_by=bad[:4],
                                   window_rect=window_rect(self.hwnd).as_list())
        return capture_rect(cr)

    # -- queries -----------------------------------------------------------
    @property
    def view(self):
        return self.app.SlideShowWindows(1).View

    def current_slide(self) -> int:
        return int(self.view.CurrentShowPosition)

    def is_running(self) -> bool:
        try:
            return int(self.app.SlideShowWindows.Count) > 0
        except Exception:
            return False

    def click_count(self) -> int:
        return int(self.view.GetClickCount())

    def click_index(self) -> int:
        return int(self.view.GetClickIndex())

    def goto_slide(self, index: int) -> None:
        self.view.GotoSlide(int(index))
        time.sleep(0.35)

    def goto_click(self, click: int) -> Dict[str, Any]:
        before = {"count": self.click_count(), "index": self.click_index()}
        error = None
        try:
            self.view.GotoClick(int(click))
        except Exception as exc:
            error = str(exc)
        return {"before": before, "error": error}

    def shape_info(self, slide_index: int, name: str) -> Dict[str, Any]:
        slide = self.pres.Slides(int(slide_index))
        try:
            shape = slide.Shapes(name)
        except Exception as exc:
            raise HarnessError(f"shape {name!r} not found on slide {slide_index}",
                               slide=slide_index, shape=name, error=str(exc)) from exc
        return {
            "name": str(shape.Name),
            "id": int(shape.Id),
            "type": int(shape.Type),
            "left_pt": float(shape.Left),
            "top_pt": float(shape.Top),
            "width_pt": float(shape.Width),
            "height_pt": float(shape.Height),
            "rotation": float(getattr(shape, "Rotation", 0.0)),
        }

    def export_slide(self, slide_index: int, width: int, height: int,
                     path: Optional[Path] = None) -> Any:
        from PIL import Image
        tmp = path
        if tmp is None:
            import tempfile
            fd, name = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            tmp = Path(name)
        self.pres.Slides(int(slide_index)).Export(str(tmp), "PNG", int(width), int(height))
        img = Image.open(tmp).convert("RGB")
        if path is None:
            try:
                tmp.unlink()
            except OSError:
                pass
        return img

    # -- teardown ----------------------------------------------------------
    def close(self) -> Dict[str, Any]:
        record: Dict[str, Any] = {}
        if self.app is not None:
            try:
                if int(self.app.SlideShowWindows.Count) > 0:
                    self.app.SlideShowWindows(1).View.Exit()
                    record["show_exited"] = True
                    time.sleep(0.2)
            except Exception as exc:
                record["show_exit_error"] = str(exc)
            try:
                if self.pres is not None:
                    self.pres.Close()
                    record["presentation_closed"] = True
            except Exception as exc:
                record["close_error"] = str(exc)
            try:
                self.app.Quit()
                record["quit_called"] = True
            except Exception as exc:
                record["quit_error"] = str(exc)
        pid = self.pid
        if pid:
            deadline = time.time() + 6.0
            while time.time() < deadline and _pid_alive(pid):
                time.sleep(0.25)
            if _pid_alive(pid):
                _kill_pid(pid)
                record["killed_pid"] = pid
        self.app = None
        self.pres = None
        if self._pythoncom is not None:
            try:
                self._pythoncom.CoUninitialize()
            except Exception:
                pass
            self._pythoncom = None
        record["remaining_powerpnt_pids"] = sorted(_powerpnt_pids())
        return record


# --------------------------------------------------------------------------
# Plan execution
# --------------------------------------------------------------------------


def _save_frame(image: Any, path: Path, max_width: int = 1200) -> Dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = image
    if max_width and image.width > max_width:
        ratio = max_width / float(image.width)
        out = image.resize((max_width, max(1, int(round(image.height * ratio)))),
                           _require_pil()[0].LANCZOS)
    out.save(path, "PNG", optimize=True)
    return {"path": str(path), "sha256": sha256_file(path),
            "size": [out.width, out.height],
            "original_size": [image.width, image.height]}


def _crop_padded(image: Any, box: Rect, pad: int = 24) -> Any:
    l = max(0, int(box.left) - pad)
    t = max(0, int(box.top) - pad)
    r = min(image.width, int(box.right) + pad)
    b = min(image.height, int(box.bottom) + pad)
    return image.crop((l, t, r, b))


def _resolve_box(session: ShowSession, slide_index: int, names: Sequence[str],
                 mapping: SlideMapping) -> Tuple[Rect, List[Dict[str, Any]]]:
    infos = [session.shape_info(slide_index, n) for n in names]
    boxes = [mapping.box(i["left_pt"], i["top_pt"], i["width_pt"], i["height_pt"])
             for i in infos]
    box = union_of_boxes(boxes)
    if box is None:
        raise HarnessError("no observe box")
    return box, infos


def _evaluate(expect: Dict[str, Any], comparison: Dict[str, Any],
              target: Optional[Rect]) -> Tuple[bool, str]:
    kind = expect.get("kind", "pixel_change")
    if kind == "pixel_change":
        inside = comparison["inside"]
        min_pct = float(expect.get("min_pct", 1.0))
        min_share = float(expect.get("min_share", 0.6))
        max_outside = float(expect.get("max_outside_pct", 5.0))
        problems = []
        if inside["pct_changed"] < min_pct:
            problems.append(f"inside {inside['pct_changed']:.3f}% < {min_pct}%")
        if comparison["share_inside"] < min_share:
            problems.append(f"share_inside {comparison['share_inside']:.3f} < {min_share}")
        outside = comparison.get("outside") or {}
        if outside.get("pct_changed", 0.0) > max_outside:
            problems.append(f"outside {outside['pct_changed']:.3f}% > {max_outside}%")
        if target is not None and comparison["inside"]["changed_bbox"] is not None:
            cb = comparison["inside"]["changed_bbox"]
            if cb[0] >= cb[2] or cb[1] >= cb[3]:
                problems.append("no changed pixels")
        return (not problems), "; ".join(problems) if problems else "changed inside target"
    if kind == "noop":
        max_pct = float(expect.get("max_pct", 0.2))
        ok = comparison["whole"]["pct_changed"] <= max_pct
        return ok, (f"whole {comparison['whole']['pct_changed']:.3f}% <= {max_pct}%"
                    if ok else f"whole {comparison['whole']['pct_changed']:.3f}% > {max_pct}%")
    if kind == "slide_change":
        observed = int(expect.get("_observed_slide", -1))
        wanted = int(expect.get("to"))
        ok = observed == wanted
        return ok, f"slide {observed} -> expected {wanted}" if ok else \
            f"slide {observed} != expected {wanted}"
    return False, f"unknown expectation kind {kind!r}"


def run_plan(session: ShowSession, plan: Dict[str, Any], outdir: Path,
             *, save_frames: bool = True) -> Dict[str, Any]:
    outdir = Path(outdir)
    frames_dir = outdir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    evidence: Dict[str, Any] = {
        "schema": "pptx-interactive-show/1",
        "task": "T058",
        "deck": {"path": str(session.deck), "sha256": sha256_file(session.deck),
                 "bytes": session.deck.stat().st_size},
        "plan": plan.get("name", "unnamed"),
        "run": {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "harness": "scripts/interactive_show_harness.py"},
        "powerpoint": dict(session.info),
        "steps": [],
        "negatives": [],
    }
    client = client_rect(session.hwnd)
    evidence["show"] = {
        "pid": session.pid,
        "hwnd": session.hwnd,
        "class": _window_class(session.hwnd),
        "title": _window_text(session.hwnd),
        "window_rect": window_rect(session.hwnd).as_list(),
        "client_rect": client.as_list(),
        "dpi": int(_user32.GetDpiForWindow(session.hwnd)),
        "obstruction": session.info.get("obstruction"),
        "scrollbars": session.info.get("scrollbars"),
    }
    slide_w = session.info["slide_width_pt"]
    slide_h = session.info["slide_height_pt"]
    scroll_w = 0
    for sb in session.info.get("scrollbars") or []:
        scroll_w = max(scroll_w, int(round(sb["rect"][2] - sb["rect"][0])))
    prediction = predict_mapping(client, slide_w, slide_h, reserve_right_px=scroll_w)
    evidence["mapping"] = {
        "predicted": {"scale": round(prediction.scale, 6),
                      "content": prediction.content.as_list(),
                      "scrollbar_width_px": scroll_w},
    }

    # --- calibration on slide 1 ------------------------------------------
    session.goto_slide(1)
    client_capture = session.guarded_capture(client)
    export = session.export_slide(1, max(64, int(round(prediction.content.width))),
                                  max(64, int(round(prediction.content.height))))
    calib = calibrate_mapping(client_capture, export, prediction, client,
                              max_shift=48, ignore_right=scroll_w)
    mapping = prediction.shifted(calib["shift_px"][0], calib["shift_px"][1])
    calib["calibrated_content"] = mapping.content.as_list()
    evidence["mapping"]["calibration"] = calib
    evidence["mapping"]["used"] = {"scale": round(mapping.scale, 6),
                                   "content": mapping.content.as_list()}

    steps = plan.get("steps") or []
    for i, step in enumerate(steps):
        action = step.get("action")
        rec: Dict[str, Any] = {"index": i, "action": action, "slide_before": session.current_slide()}
        try:
            if action == "goto_slide":
                session.goto_slide(int(step["slide"]))
                rec.update({"ok": True, "slide_after": session.current_slide(),
                            "assert": {"pass": True, "reason": "moved"}})
                evidence["steps"].append(rec)
                continue
            if action not in ("click_shape", "goto_click"):
                raise HarnessError(f"unknown action {action!r}")
            session.ensure_foreground()

            if action == "goto_click":
                before_frame = session.guarded_capture(client)
                result = session.goto_click(int(step.get("click", 1)))
                stable = wait_until_stable(lambda: session.guarded_capture(client),
                                           timeout_s=1.5, interval_s=0.15)
                after_frame = stable["frame"]
                cmp = compare_frames(before_frame, after_frame, None)
                rec.update({
                    "goto_click": result,
                    "click_state_after": {"count": session.click_count(),
                                          "index": session.click_index()},
                    "diff": cmp,
                    "settled": stable["settled"],
                })
                expect = step.get("expect") or {"kind": "noop"}
                kind = expect.get("kind", "noop")
                if kind == "noop":
                    index_ok = (rec["click_state_after"]["index"] == result["before"]["index"])
                    pix_ok = cmp["whole"]["pct_changed"] <= float(expect.get("max_pct", 0.2))
                    rec["assert"] = {
                        "pass": bool(index_ok and pix_ok),
                        "reason": (f"index {result['before']['index']}->"
                                   f"{rec['click_state_after']['index']}, "
                                   f"pixels {cmp['whole']['pct_changed']:.3f}%"),
                        "index_unchanged": index_ok,
                        "pixels_unchanged": pix_ok,
                    }
                elif kind == "main_advance":
                    # GotoClick drives the main sequence; it must move the
                    # main-sequence shape and leave the trigger target alone.
                    want_index = int(expect.get("index", 1))
                    index_ok = rec["click_state_after"]["index"] == want_index
                    details = {}
                    ok = index_ok
                    slide = session.current_slide()
                    rendered = False
                    for name in expect.get("changes") or []:
                        box, _ = _resolve_box(session, slide, [name], mapping)
                        local = Rect(box.left - client.left, box.top - client.top,
                                     box.right - client.left, box.bottom - client.top)
                        st = diff_stats(before_frame, after_frame, local)
                        hit = st["pct_changed"] >= float(expect.get("min_pct", 0.5))
                        details[name] = {"expected": "changed", "pct": st["pct_changed"],
                                         "pass": hit}
                        rendered = rendered or hit
                        ok = ok and hit
                    for name in expect.get("unchanged") or []:
                        box, _ = _resolve_box(session, slide, [name], mapping)
                        local = Rect(box.left - client.left, box.top - client.top,
                                     box.right - client.left, box.bottom - client.top)
                        st = diff_stats(before_frame, after_frame, local)
                        hit = st["pct_changed"] <= float(expect.get("max_pct", 0.2))
                        details[name] = {"expected": "unchanged", "pct": st["pct_changed"],
                                         "pass": hit}
                        ok = ok and hit
                    allow_no_render = bool(expect.get("allow_no_render", False))
                    if not (expect.get("changes") or []):
                        ok = ok and (allow_no_render or index_ok)
                    rec["assert"] = {
                        "pass": bool(ok),
                        "reason": (f"index {result['before']['index']}->"
                                   f"{rec['click_state_after']['index']} "
                                   f"(want {want_index}); rendered={rendered}; "
                                   f"boxes {details}"),
                        "boxes": details,
                        "rendered": rendered,
                        "index_advanced_without_render": bool(index_ok and not rendered),
                    }
                else:
                    raise HarnessError(f"goto_click does not support expect.kind={kind!r}")
                rec["ok"] = rec["assert"]["pass"]
                if save_frames:
                    rec["frames"] = {
                        "before": _save_frame(before_frame, frames_dir / f"{i:02d}-gotoclick-before.png"),
                        "after": _save_frame(after_frame, frames_dir / f"{i:02d}-gotoclick-after.png"),
                    }
                evidence["steps"].append(rec)
                continue

            click_name = step["shape"]
            observe = step.get("observe") or [click_name]
            if isinstance(observe, str):
                observe = [observe]
            target, shape_infos = _resolve_box(session, session.current_slide(), observe,
                                               mapping)
            clicked = session.shape_info(session.current_slide(), click_name)
            if step.get("at_pt"):
                point = mapping.point(float(step["at_pt"][0]), float(step["at_pt"][1]))
            else:
                point = mapping.point(clicked["left_pt"] + clicked["width_pt"] / 2.0,
                                      clicked["top_pt"] + clicked["height_pt"] / 2.0)
            # Refuse clicks that land on the show window's own scrollbar.
            for sb in session.info.get("scrollbars") or []:
                sbx0, sby0, sbx1, sby1 = sb["rect"]
                if sbx0 <= point[0] <= sbx1 and sby0 <= point[1] <= sby1:
                    raise HarnessError("click point falls on the show-window scrollbar",
                                       point=list(point), scrollbar=sb["rect"],
                                       code="TARGET_UNDER_SCROLLBAR")
            if not mapping.content.contains_point(point[0], point[1], tol=1.0):
                raise MappingError("click point is outside the mapped slide content",
                                   point=list(point), content=mapping.content.as_list())
            before_frame = session.guarded_capture(client)
            click_rec = click_at(point[0], point[1])
            expect = step.get("expect") or {"kind": "pixel_change"}
            kind = expect.get("kind", "pixel_change")
            slide_target = int(expect.get("to", 0)) if kind == "slide_change" else None
            if slide_target:
                deadline = time.time() + float(expect.get("timeout_s", 5.0))
                moved = True
                while time.time() < deadline:
                    if not session.is_running():
                        raise HarnessError("the slide show ended during the click",
                                           slide_before=rec["slide_before"],
                                           expected_slide=slide_target,
                                           code="SHOW_ENDED")
                    if session.current_slide() != rec["slide_before"]:
                        moved = True
                        break
                    time.sleep(0.1)
                time.sleep(float(expect.get("settle_ms", 700)) / 1000.0)
                stable = wait_until_stable(lambda: session.guarded_capture(client), timeout_s=2.5)
                after_frame = stable["frame"]
                expect["_observed_slide"] = session.current_slide()
            else:
                stable = wait_until_stable(lambda: session.guarded_capture(client), timeout_s=3.0)
                after_frame = stable["frame"]
            target_local = Rect(target.left - client.left, target.top - client.top,
                                target.right - client.left, target.bottom - client.top)
            cmp = compare_frames(before_frame, after_frame, target_local)
            passed, reason = _evaluate(expect, cmp, target_local)
            rec.update({
                "shape": clicked,
                "observe": [s["name"] for s in shape_infos],
                "observe_infos": shape_infos,
                "target_box_px": target.as_list(),
                "target_box_frame": target_local.as_list(),
                "click_point_px": [round(point[0], 2), round(point[1], 2)],
                "click_point_frame": [round(point[0] - client.left, 2),
                                      round(point[1] - client.top, 2)],
                "click": click_rec,
                "diff": cmp,
                "expect": {k: v for k, v in expect.items() if not k.startswith("_")},
                "observed": {"slide_after": session.current_slide(),
                             "click_count": session.click_count(),
                             "click_index": session.click_index()},
                "settled": stable["settled"],
                "stability": stable["series"],
                "assert": {"pass": bool(passed), "reason": reason},
                "ok": bool(passed),
            })
            if save_frames:
                rec["frames"] = {
                    "before": _save_frame(before_frame, frames_dir / f"{i:02d}-{click_name}-before.png"),
                    "after": _save_frame(after_frame, frames_dir / f"{i:02d}-{click_name}-after.png"),
                    "crop_before": _save_frame(_crop_padded(before_frame, target),
                                               frames_dir / f"{i:02d}-{click_name}-crop-before.png",
                                               max_width=0),
                    "crop_after": _save_frame(_crop_padded(after_frame, target),
                                              frames_dir / f"{i:02d}-{click_name}-crop-after.png",
                                              max_width=0),
                }
            evidence["steps"].append(rec)
        except HarnessError as exc:
            rec["ok"] = False
            rec["error"] = exc.as_dict()
            evidence["steps"].append(rec)
            break
        except Exception as exc:  # unexpected: still record, never pretend
            import traceback
            rec["ok"] = False
            rec["error"] = {"code": "UNEXPECTED", "message": f"{type(exc).__name__}: {exc}",
                            "traceback": traceback.format_exc()}
            evidence["steps"].append(rec)
            break

    evidence["run"]["duration_ms"] = int((time.time() - started) * 1000)
    evidence["desktop"] = desktop_capability()
    evidence["dpi"] = {"show_window_dpi": int(_user32.GetDpiForWindow(session.hwnd)),
                       "system_dpi": int(_user32.GetDpiForSystem()),
                       "screen_px": [int(_user32.GetSystemMetrics(0)),
                                     int(_user32.GetSystemMetrics(1))]}
    evidence["claims"] = _claims(evidence)
    evidence["claim_boundary"] = {
        "rung": "5b",
        "human_reviewed": False,
        "powerpoint_playback_verified": False,
        "note": ("COM-driven windowed playback with machine pixel assertions; "
                 "rung 6 still requires a person to review the captures."),
    }
    return evidence


def _claims(evidence: Dict[str, Any]) -> Dict[str, Any]:
    steps = evidence.get("steps", [])
    clicks = [s for s in steps if s.get("action") == "click_shape"]
    goto = [s for s in steps if s.get("action") == "goto_click"]
    pixel = [s for s in steps if (s.get("expect") or {}).get("kind") == "pixel_change"]
    nav = [s for s in steps if (s.get("expect") or {}).get("kind") == "slide_change"]
    return {
        "interactive_show_window_found": bool(evidence.get("show", {}).get("hwnd")),
        "show_window_class": evidence.get("show", {}).get("class"),
        "dpi_aware": evidence.get("dpi", {}).get("show_window_dpi", 0) > 0,
        "mapping_calibrated": "calibration" in evidence.get("mapping", {}),
        "win32_click_sent": all("click" in s for s in clicks),
        "trigger_pixel_change_verified": bool(pixel) and all(s.get("ok") for s in pixel),
        "gotoclick_noop_verified": bool(goto) and all(s.get("ok") for s in goto),
        "slide_navigation_verified": bool(nav) and all(s.get("ok") for s in nav),
        "all_steps_passed": bool(steps) and all(s.get("ok") for s in steps),
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _load_plan(path: Path) -> Dict[str, Any]:
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    if "deck" not in plan:
        raise HarnessError("plan must name a deck", path=str(path))
    if not isinstance(plan.get("steps"), list) or not plan["steps"]:
        raise HarnessError("plan must contain a non-empty steps list", path=str(path))
    for i, step in enumerate(plan["steps"]):
        if step.get("action") not in ("click_shape", "goto_click", "goto_slide"):
            raise HarnessError(f"step {i}: unknown action {step.get('action')!r}")
        if step["action"] == "click_shape" and not step.get("shape"):
            raise HarnessError(f"step {i}: click_shape needs a shape name")
    plan["deck"] = str((Path(path).parent / plan["deck"]).resolve()) \
        if not Path(plan["deck"]).is_absolute() else plan["deck"]
    return plan


def cmd_probe(args: argparse.Namespace) -> int:
    info = enable_dpi_awareness()
    cap = desktop_capability()
    out = {"dpi": info, "desktop": cap,
           "windows": [w for w in enumerate_windows() if "powerpoint" in w["title"].lower()
                       or "powerpoint" in w["class"].lower()]}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0 if cap["interactive_desktop"] else 3


def cmd_run(args: argparse.Namespace) -> int:
    dpi = enable_dpi_awareness()
    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    evidence: Dict[str, Any] = {"dpi": dpi}
    plan = _load_plan(Path(args.plan))
    windowed = not args.fullscreen
    session = ShowSession(Path(plan["deck"]), windowed=windowed,
                          place_window=windowed and not args.no_place)
    start_error: Optional[HarnessError] = None
    for attempt in range(2):
        try:
            session.info = session.start()
            start_error = None
            break
        except HarnessError as exc:
            start_error = exc
            evidence.setdefault("start_attempts", []).append(exc.as_dict())
            session.close()
            time.sleep(1.5)
            session = ShowSession(Path(plan["deck"]), windowed=windowed,
                                  place_window=windowed and not args.no_place)
    try:
        if start_error is not None:
            raise start_error
        evidence = run_plan(session, plan, outdir, save_frames=not args.no_frames)
        evidence["dpi"] = dpi
    except HarnessError as exc:
        evidence.update({"error": exc.as_dict(), "steps": evidence.get("steps", []),
                         "session": session.info})
        code = exc.exit_code
    except Exception as exc:
        evidence.update({"error": {"code": "UNEXPECTED",
                                   "message": f"{type(exc).__name__}: {exc}"},
                         "session": session.info})
        code = 4
    else:
        plan_ok = all(s.get("ok") for s in evidence.get("steps", []))
        code = 0 if plan_ok else 2
    finally:
        evidence["teardown"] = session.close()
    evidence["dpi"] = evidence.get("dpi", dpi)
    json_path = Path(args.json_out) if args.json_out else outdir / "evidence.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {
        "evidence": str(json_path),
        "exit_code": code,
        "claims": evidence.get("claims"),
        "error": evidence.get("error"),
        "steps": [{"i": s.get("index"), "action": s.get("action"),
                   "ok": s.get("ok"), "reason": (s.get("assert") or {}).get("reason")}
                  for s in evidence.get("steps", [])],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return code


def cmd_open_check(args: argparse.Namespace) -> int:
    """Open a deck read-only and report whether PowerPoint accepts it."""
    deck = Path(args.deck).resolve()
    record: Dict[str, Any] = {"schema": "pptx-open-check/1", "deck": str(deck),
                              "sha256": sha256_file(deck) if deck.is_file() else None,
                              "bytes": deck.stat().st_size if deck.is_file() else None}
    code = 2
    if not deck.is_file():
        record["opened"] = False
        record["error"] = "file not found"
    else:
        try:
            import pythoncom
            import win32com.client
        except Exception as exc:
            raise InfraError("pywin32 is required", error=str(exc)) from exc
        pythoncom.CoInitialize()
        app = win32com.client.DispatchEx("PowerPoint.Application")
        try:
            app.Visible = True
            app.DisplayAlerts = 1
            record["version"] = str(getattr(app, "Version", ""))
            record["build"] = str(getattr(app, "Build", ""))
            record["application"] = str(getattr(app, "Name", ""))
            record["application_path"] = str(getattr(app, "Path", ""))
            pres = app.Presentations.Open(str(deck), ReadOnly=True,
                                          Untitled=False, WithWindow=False)
            record["opened"] = True
            record["slides"] = int(pres.Slides.Count)
            record["slide_width_pt"] = float(pres.PageSetup.SlideWidth)
            record["slide_height_pt"] = float(pres.PageSetup.SlideHeight)
            per_slide = []
            for i in range(1, int(pres.Slides.Count) + 1):
                slide = pres.Slides(i)
                try:
                    main = int(slide.TimeLine.MainSequence.Count)
                except Exception:
                    main = -1
                try:
                    inter = int(slide.TimeLine.InteractiveSequences.Count)
                except Exception:
                    inter = -1
                per_slide.append({"slide": i, "main_effects": main,
                                  "interactive_sequences": inter})
            record["slides_detail"] = per_slide
            record["main_effects_total"] = sum(s["main_effects"] for s in per_slide)
            record["interactive_sequences_total"] = sum(
                s["interactive_sequences"] for s in per_slide)
            pres.Close()
            code = 0
        except Exception as exc:
            record["opened"] = False
            record["error"] = f"{type(exc).__name__}: {exc}"
            record["com_error_args"] = list(getattr(exc, "args", ()))
        finally:
            try:
                app.Quit()
            except Exception:
                pass
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
    print(json.dumps(record, indent=2, ensure_ascii=False, default=str))
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(record, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
    return code


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="report desktop and DPI capability")
    p_probe.add_argument("--json-out")
    p_probe.set_defaults(func=cmd_probe)

    p_run = sub.add_parser("run", help="run an interaction plan against a deck")
    p_run.add_argument("--plan", required=True)
    p_run.add_argument("--out", required=True)
    p_run.add_argument("--json-out")
    p_run.add_argument("--fullscreen", action="store_true",
                       help="use a fullscreen show (screenClass); default is windowed")
    p_run.add_argument("--no-place", action="store_true",
                       help="do not move/resize the show window into the work area")
    p_run.add_argument("--no-frames", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_open = sub.add_parser("open-check",
                            help="open a deck read-only and report whether PowerPoint accepts it")
    p_open.add_argument("--deck", required=True)
    p_open.add_argument("--json-out")
    p_open.set_defaults(func=cmd_open_check)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
