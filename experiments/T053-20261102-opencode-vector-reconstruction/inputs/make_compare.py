"""Before/after: T051 edge trace vs T053 semantic reconstruction."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXP = HERE.parent
TRACE = ROOT / "experiments" / "T051-20261102-opencode-photo-vector" / "artifacts" / "line.png"
RECON = EXP / "preview" / "quickmill-reconstruction.png"
OUT = EXP / "preview" / "before-after.png"


def font(size: int, bold: bool = False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
    except Exception:
        return ImageFont.load_default()


def main() -> None:
    height = 720
    trace = Image.open(TRACE).convert("RGB")
    recon = Image.open(RECON).convert("RGB")
    trace.thumbnail((520, height), Image.LANCZOS)
    recon.thumbnail((520, height), Image.LANCZOS)
    gap, top = 24, 70
    sheet = Image.new("RGB", (gap + trace.width + gap + recon.width + gap,
                              top + height + 86), "#F2EFE8")
    d = ImageDraw.Draw(sheet)
    d.text((gap, 18), "T051 → T053: from edge trace to reconstruction",
           font=font(22, True), fill="#20242A")
    d.text((gap, top - 26), "T051 — Canny edge trace (rejected)",
           font=font(13, True), fill="#8A3A2F")
    d.text((gap + trace.width + gap, top - 26), "T053 — semantic 2.5D reconstruction",
           font=font(13, True), fill="#2F5D3A")
    sheet.paste(trace, (gap, top + (height - trace.height) // 2))
    sheet.paste(recon, (gap + trace.width + gap, top + (height - recon.height) // 2))
    d.rectangle((gap, top + (height - trace.height) // 2,
                 gap + trace.width, top + (height - trace.height) // 2 + trace.height),
                outline="#D6D0C4")
    d.rectangle((gap + trace.width + gap, top + (height - recon.height) // 2,
                 gap + trace.width + gap + recon.width,
                 top + (height - recon.height) // 2 + recon.height), outline="#D6D0C4")
    d.text((gap, top + height + 14),
           "T051: 54 traced paths, 1,437 nodes, noise and doubled contours.",
           font=font(13), fill="#4A4F55")
    d.text((gap, top + height + 38),
           "T053: 16 part groups, 105 primitive paths, 5 text elements, 0 traced pixels.",
           font=font(13), fill="#4A4F55")
    d.text((gap + trace.width + gap, top + height + 14),
           "Boxes, cylinders, plates and controls in one projection; the photo supplies",
           font=font(13), fill="#4A4F55")
    d.text((gap + trace.width + gap, top + height + 38),
           "proportions and materials, not line work.",
           font=font(13), fill="#4A4F55")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT, optimize=True)
    print(OUT)


if __name__ == "__main__":
    main()
