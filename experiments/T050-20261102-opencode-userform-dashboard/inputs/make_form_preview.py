"""Render a layout preview of the real frmEntry controls (not a runtime shot)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.userform_forge import inspect_workbook  # noqa: E402

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
PREVIEW = HERE.parent / "preview"


def font(size: int, bold: bool = False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    for base in ("C:/Windows/Fonts/",):
        try:
            return ImageFont.truetype(base + name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def main() -> None:
    info = inspect_workbook(ART / "dashboard.xlsm")
    controls = info.get("controls", [])
    scale = 2.4
    W, H = int(430 * scale), int(370 * scale)
    im = Image.new("RGB", (W, H), "#F7F9FC")
    d = ImageDraw.Draw(im)
    # Form surface and title.
    d.rounded_rectangle((6, 6, W - 6, H - 42), radius=12, fill="#F7F9FC",
                        outline="#D6DEE8", width=2)
    for control in controls:
        name = control["name"]
        x = int(control["left"] * scale)
        y = int(control["top"] * scale)
        w = max(8, int(control["width"] * scale))
        h = max(8, int(control["height"] * scale))
        caption = control.get("caption", "")
        if name == "lblTitle":
            d.text((x, y), caption, font=font(30, True), fill="#1F4E79")
        elif name == "lblHint":
            d.text((x, y), caption, font=font(15), fill="#7F7F7F")
        elif name.startswith("lbl") and name != "lblStatus":
            d.text((x, y + 2), caption, font=font(15, True), fill="#404040")
        elif name.startswith("cbo"):
            d.rounded_rectangle((x, y, x + w, y + h), radius=4, fill="#FFFFFF",
                                outline="#BFC9D6", width=2)
            d.polygon([(x + w - 18, y + 9), (x + w - 8, y + 9), (x + w - 13, y + 16)],
                      fill="#1F4E79")
        elif name.startswith("txt"):
            d.rounded_rectangle((x, y, x + w, y + h), radius=4, fill="#FFFFFF",
                                outline="#BFC9D6", width=2)
        elif name == "btnSave":
            d.rounded_rectangle((x, y, x + w, y + h), radius=6, fill="#1F4E79")
            d.text((x + 26, y + 6), caption, font=font(16, True), fill="#FFFFFF")
        elif name == "btnClear":
            d.rounded_rectangle((x, y, x + w, y + h), radius=6, fill="#C55A11")
            d.text((x + 27, y + 6), caption, font=font(16, True), fill="#FFFFFF")
        elif name == "btnCancel":
            d.rounded_rectangle((x, y, x + w, y + h), radius=6, fill="#7F7F7F")
            d.text((x + 16, y + 6), caption, font=font(16, True), fill="#FFFFFF")
        elif name == "lblStatus":
            d.rounded_rectangle((x, y, x + w, y + h), radius=6, fill="#EAF1F8")
            d.text((x + 10, y + 8), caption, font=font(14), fill="#1F4E79")
    d.text((18, H - 28), "Mô phỏng bố cục từ 22 control thật trong frmEntry — không phải ảnh runtime.",
           font=font(13), fill="#7F7F7F")
    PREVIEW.mkdir(parents=True, exist_ok=True)
    out = PREVIEW / "userform-layout.png"
    im.save(out, optimize=True)
    (PREVIEW / "userform-controls.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
