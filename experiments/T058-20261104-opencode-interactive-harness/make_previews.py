"""Compose the T058 preview images from the recorded evidence frames."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RUNS = HERE / "artifacts" / "runs"
OUT = HERE / "preview"
OUT.mkdir(parents=True, exist_ok=True)

BG = (12, 17, 26)
FG = (226, 232, 240)
MUTED = (148, 163, 184)
ACCENT = (250, 204, 21)


def font(size: int):
    for name in ("segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)
        except OSError:
            continue
    return ImageFont.load_default()


def fitted(path: Path, width: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    if width and im.width != width:
        im = im.resize((width, int(round(im.height * width / im.width))), Image.LANCZOS)
    return im


def labelled(im: Image.Image, label: str, sub: str = "", pad: int = 14) -> Image.Image:
    f = font(20)
    fs = font(14)
    head = 32 if not sub else 52
    out = Image.new("RGB", (im.width, im.height + head + pad), BG)
    out.paste(im, (0, head))
    d = ImageDraw.Draw(out)
    d.text((10, 6), label, font=f, fill=FG)
    if sub:
        d.text((10, 30), sub, font=fs, fill=MUTED)
    return out


def row(images, gap=12) -> Image.Image:
    h = max(i.height for i in images)
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    out = Image.new("RGB", (w, h), BG)
    x = 0
    for im in images:
        out.paste(im, (x, 0))
        x += im.width + gap
    return out


def title_block(title: str, subtitle: str, width: int) -> Image.Image:
    out = Image.new("RGB", (width, 78), BG)
    d = ImageDraw.Draw(out)
    d.text((16, 8), title, font=font(26), fill=FG)
    d.text((16, 46), subtitle, font=font(15), fill=ACCENT)
    return out


def stack(parts) -> Image.Image:
    w = max(p.width for p in parts)
    h = sum(p.height for p in parts) + 18 * (len(parts) - 1)
    out = Image.new("RGB", (w, h), BG)
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.height + 18
    return out


def _outlined(path: Path, box_frame, frame_size, width=540) -> Image.Image:
    im = Image.open(path).convert("RGB")
    sx = im.width / frame_size[0]
    sy = im.height / frame_size[1]
    d = ImageDraw.Draw(im)
    d.rectangle([box_frame[0] * sx, box_frame[1] * sy,
                 box_frame[2] * sx, box_frame[3] * sy],
                outline=(250, 204, 21), width=3)
    return im.resize((width, int(round(im.height * width / im.width))), Image.LANCZOS)


def t049_trigger() -> Path:
    import json
    base = RUNS / "t049_slide1" / "frames"
    evidence = json.loads((RUNS / "t049_slide1" / "evidence.json").read_text(encoding="utf-8"))
    client = evidence["show"]["client_rect"]
    frame_size = (client[2] - client[0] + 1, client[3] - client[1] + 1)
    click = evidence["steps"][2]
    reset = evidence["steps"][5]
    click_box = click["target_box_frame"]
    reset_box = reset["target_box_frame"]
    click_row = row([
        labelled(_outlined(base / "02-Cover_1-before.png", click_box, frame_size),
                 "BEFORE click", "Cover_1 visible"),
        labelled(_outlined(base / "02-Cover_1-after.png", click_box, frame_size),
                 "AFTER click", "inside 100% changed, share 0.98"),
    ])
    reset_row = row([
        labelled(_outlined(base / "05-Reset_Button_S1-before.png", reset_box, frame_size),
                 "BEFORE reset", "three covers gone"),
        labelled(_outlined(base / "05-Reset_Button_S1-after.png", reset_box, frame_size),
                 "AFTER reset", "all covers re-enter"),
    ])
    body = stack([
        title_block("T049 one-slide game: real Win32 clicks in a windowed show",
                    "yellow = predicted target box; GotoClick(1) control changed 0.000%", 1100),
        click_row,
        reset_row,
    ])
    p = OUT / "t049-trigger-before-after.png"
    body.save(p, optimize=True)
    return p


def t048_hub() -> Path:
    base = RUNS / "t048b_hub" / "frames"
    seq = [
        ("01-btn_hub_strategy-before.png", "slide 1", "hub"),
        ("01-btn_hub_strategy-after.png", "slide 2", "click btn_hub_strategy"),
        ("02-btn_return_hub_1-after.png", "slide 1", "click btn_return_hub_1"),
        ("04-btn_goto_deepdive-after.png", "slide 5", "deep dive from slide 3"),
        ("05-btn_back_to_caller-after.png", "slide 3", "last slide viewed"),
    ]
    thumbs = [labelled(fitted(base / name, 380), pos, note) for name, pos, note in seq]
    body = stack([
        title_block("T048b hub: 9/9 navigation edges clicked by the harness",
                    "last_viewed edge: slide 5 -> slide 3", 1900),
        row(thumbs),
    ])
    p = OUT / "t048b-navigation.png"
    body.save(p, optimize=True)
    return p


def gotoclick_control() -> Path:
    base = RUNS / "t049_main_control" / "frames"
    pair = row([
        labelled(fitted(base / "01-gotoclick-before.png", 460),
                 "BEFORE GotoClick(1)", "index 0"),
        labelled(fitted(base / "01-gotoclick-after.png", 460),
                 "AFTER GotoClick(1)", "index 1, pixels unchanged"),
    ])
    body = stack([
        title_block("GotoClick moves the index, not the pixels",
                    "0.000% pixels changed; the title fade-out was not rendered", 960),
        pair,
    ])
    p = OUT / "gotoclick-index-without-render.png"
    body.save(p, optimize=True)
    return p


def main() -> int:
    for fn in (t049_trigger, t048_hub, gotoclick_control):
        p = fn()
        print(p.name, p.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
