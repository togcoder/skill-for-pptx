#!/usr/bin/env python3
"""DeckCraft vs PowerPoint fidelity harness (T059) — EXPERIMENTAL.

Measures how close the ArtCraft DeckCraft CLI renderer is to desktop
PowerPoint for the lab's own decks:

- static slide diff, whole frame and per object kind;
- designer-critic score parity when the frames come from each renderer;
- Morph transition frames against PowerPoint ``CreateVideo`` frames at the
  same normalised time, including entrance-hidden shapes;
- the timing nodes that DeckCraft ``convert`` rewrites, and whether PowerPoint
  still parses and plays the round-tripped deck the same way.

This module is research code. It is not wired into a product path; see the
T059 REPORT for the proposed ``slide_forge.render`` fallback. DeckCraft output
must always be labelled "DeckCraft render", never "PowerPoint".

Commands (run from the repository root, Windows):

    python scripts/deckcraft_fidelity.py static  --decks workspace/decks --out experiments/T059-.../artifacts
    python scripts/deckcraft_fidelity.py critic  --decks workspace/decks --out ...
    python scripts/deckcraft_fidelity.py morph   --pptx ... --slide 3 --work workspace/morph
    python scripts/deckcraft_fidelity.py roundtrip --pptx ... --out ...

Pure functions (``region_metrics``, ``shape_kinds``, ``timing_inventory``,
``visibility_label``) are unit-tested in tests/test_deckcraft_fidelity.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.oxml.ns import qn

try:  # script and package import paths both work in this repo
    from scripts.deckcraft_bridge import find_deckcraft_cli, is_available, render_slides
except ImportError:  # pragma: no cover
    from deckcraft_bridge import find_deckcraft_cli, is_available, render_slides  # type: ignore

# Analysis frame: 960x540 keeps text antialiasing comparable between the two
# renderers and is the resolution T057 used. Renders stay at 1920x1080.
FRAME_W, FRAME_H = 960, 540
RENDER_W, RENDER_H = 1920, 1080
DIFF_T = 40
MORPH_TS = (0.25, 0.5, 0.75)

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"


# --------------------------------------------------------------------------
# Small image helpers
# --------------------------------------------------------------------------

def load_frame(path: str | Path, size: tuple[int, int] = (FRAME_W, FRAME_H)) -> np.ndarray:
    """RGB uint8 array, resized to the analysis frame."""
    im = Image.open(path).convert("RGB")
    if im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im, dtype=np.uint8)


def diff_map(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Per-pixel max-channel absolute difference (uint8 arrays)."""
    return np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2)


def region_metrics(diff: np.ndarray, mask: np.ndarray | None = None) -> dict:
    """Mean absolute difference and threshold shares on a region."""
    d = diff if mask is None else diff[mask]
    n = int(d.size)
    if n == 0:
        return {"pixels": 0, "mean_abs": None, "pct_gt10": None, "pct_gt40": None, "max_abs": None}
    return {
        "pixels": n,
        "mean_abs": round(float(d.mean()), 3),
        "pct_gt10": round(float((d > 10).mean()) * 100, 3),
        "pct_gt40": round(float((d > DIFF_T).mean()) * 100, 3),
        "max_abs": int(d.max()),
    }


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _heat(d: np.ndarray, gain: float = 4.0) -> Image.Image:
    """Amplified red heat map for a difference array."""
    r = np.clip(d.astype(np.float32) * gain, 0, 255)
    g = np.clip(d.astype(np.float32) * gain - 90, 0, 255)
    b = np.clip(d.astype(np.float32) * gain - 180, 0, 255)
    return Image.fromarray(np.stack([r, g, b], axis=2).astype(np.uint8), "RGB")


def panel(im: Image.Image, w: int, h: int, label: str = "") -> Image.Image:
    im = im.convert("RGB")
    if im.size != (w, h):
        im = im.resize((w, h), Image.LANCZOS)
    if not label:
        return im
    out = Image.new("RGB", (w, h + 22), "white")
    out.paste(im, (0, 22))
    ImageDraw.Draw(out).text((6, 3), label, fill=(20, 20, 20), font=_font(14))
    return out


def save_jpeg(im: Image.Image, path: str | Path, quality: int = 82) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "JPEG", quality=quality, optimize=True)
    return path


# --------------------------------------------------------------------------
# Shape inventory and object-kind attribution
# --------------------------------------------------------------------------

def _shape_xml_kinds(shape) -> set[str]:
    """Kinds inferred from the shape XML (formatting that python-pptx hides)."""
    el = shape._element
    kinds: set[str] = set()
    if el.find(".//" + qn("c:chart")) is not None:
        kinds.add("chart")
    if el.tag == qn("p:pic"):
        if el.find(".//{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip") is not None:
            kinds.add("picture-svg")
        else:
            kinds.add("picture")
    if el.find(".//" + qn("a:gradFill")) is not None:
        kinds.add("gradient")
    eff = el.find(".//" + qn("a:effectLst"))
    if eff is not None and len(eff):
        kinds.add("effects")
    style = el.find(qn("p:style"))
    if style is not None:
        ref = style.find(qn("a:effectRef"))
        if ref is not None:
            try:
                if int(ref.get("idx", "0")) > 0:
                    kinds.add("effects-theme")
            except ValueError:
                pass
    if el.tag == qn("p:grpSp"):
        kinds.add("group")
    return kinds


def shape_kinds(shape) -> set[str]:
    """Primary kinds for one top-level shape.

    A shape can belong to several kinds (a text box with a gradient fill);
    per-kind metrics therefore may count its pixels in more than one row.
    """
    kinds = _shape_xml_kinds(shape)
    try:
        if shape.has_text_frame and shape.text_frame.text.strip():
            kinds.add("text")
    except (AttributeError, ValueError):
        pass
    try:
        if shape.has_chart:
            kinds.add("chart")
    except (AttributeError, ValueError):
        pass
    if not (kinds - {"effects-theme"}):
        kinds.add("vector")
    return kinds


def _emu_box(shape, slide_w: int, slide_h: int) -> tuple[int, int, int, int]:
    """Shape box in analysis-frame pixels, clipped to the frame."""
    try:
        l, t, w, h = int(shape.left), int(shape.top), int(shape.width), int(shape.height)
    except (TypeError, ValueError):
        return (0, 0, 0, 0)
    if slide_w <= 0 or slide_h <= 0:
        return (0, 0, 0, 0)
    x0 = int(round(l / slide_w * FRAME_W))
    y0 = int(round(t / slide_h * FRAME_H))
    x1 = int(round((l + w) / slide_w * FRAME_W))
    y1 = int(round((t + h) / slide_h * FRAME_H))
    return (max(0, x0), max(0, y0), min(FRAME_W, x1), min(FRAME_H, y1))


def slide_objects(pptx: str | Path, slide_index: int) -> list[dict]:
    """Top-level shapes of a slide in z-order (back to front)."""
    p = Presentation(str(pptx))
    sw, sh = int(p.slide_width), int(p.slide_height)
    slide = p.slides[slide_index]
    out = []
    for z, shape in enumerate(slide.shapes):
        x0, y0, x1, y1 = _emu_box(shape, sw, sh)
        out.append({
            "z": z,
            "name": shape.name,
            "spid": int(shape.shape_id),
            "box": [x0, y0, x1, y1],
            "kinds": sorted(shape_kinds(shape)),
            "has_text": bool(getattr(shape, "has_text_frame", False) and shape.text_frame.text.strip()),
        })
    return out


def ownership_map(objects: list[dict]) -> np.ndarray:
    """Pixel owner per shape: bbox rasterisation, topmost shape wins.

    This is a rectangle approximation, not a geometry mask. It is stable and
    cheap, and the REPORT records the limitation.
    """
    owner = np.full((FRAME_H, FRAME_W), -1, dtype=np.int16)
    for i, o in enumerate(objects):
        x0, y0, x1, y1 = o["box"]
        if x1 > x0 and y1 > y0:
            owner[y0:y1, x0:x1] = i
    return owner


def object_metrics(diff: np.ndarray, objects: list[dict]) -> list[dict]:
    owner = ownership_map(objects)
    rows = []
    for i, o in enumerate(objects):
        m = region_metrics(diff, owner == i)
        rows.append({**o, **m})
    return rows


def kind_metrics(diff: np.ndarray, objects: list[dict]) -> dict[str, dict]:
    owner = ownership_map(objects)
    acc: dict[str, list] = defaultdict(lambda: [0, 0.0, 0, 0, 0])  # n, sum, gt10, gt40, max
    names: dict[str, list] = defaultdict(list)
    for i, o in enumerate(objects):
        mask = owner == i
        n = int(mask.sum())
        if not n:
            continue
        d = diff[mask]
        for kind in o["kinds"]:
            a = acc[kind]
            a[0] += n
            a[1] += float(d.sum())
            a[2] += int((d > 10).sum())
            a[3] += int((d > DIFF_T).sum())
            a[4] = max(a[4], int(d.max()))
            names[kind].append((o["name"], round(float(d.mean()), 3)))
    out = {}
    for kind, (n, total, g10, g40, mx) in acc.items():
        worst = max(names[kind], key=lambda t: t[1]) if names[kind] else ("", None)
        out[kind] = {
            "objects": len(names[kind]),
            "pixels": n,
            "pixel_share": round(n / (FRAME_W * FRAME_H) * 100, 2),
            "mean_abs": round(total / n, 3),
            "pct_gt10": round(g10 / n * 100, 3),
            "pct_gt40": round(g40 / n * 100, 3),
            "max_abs": mx,
            "worst_object": worst[0],
            "worst_object_mean": worst[1],
        }
    return out


# --------------------------------------------------------------------------
# Renderers
# --------------------------------------------------------------------------

def deckcraft_render(pptx: str | Path, out_dir: str | Path, scale: int = 2) -> list[Path]:
    if not is_available():
        raise RuntimeError("deckcraft-cli is not available on this system")
    images = render_slides(pptx, out_dir, scale=scale)
    if not images:
        raise RuntimeError(f"deckcraft-cli rendered no slides for {pptx}")
    return images


def powerpoint_export(pptx: str | Path, out_dir: str | Path) -> list[Path]:
    """Export every slide with PowerPoint COM ``Slide.Export``."""
    try:
        import win32com.client as win32
    except ImportError as exc:  # pragma: no cover - Windows only
        raise RuntimeError("PowerPoint export needs pywin32") from exc
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir = out_dir.resolve()
    app = win32.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(str(Path(pptx).resolve()), ReadOnly=True, WithWindow=False)
    try:
        paths = []
        for i in range(1, pres.Slides.Count + 1):
            target = out_dir / f"slide-{i:02d}.png"
            pres.Slides(i).Export(str(target), "PNG", RENDER_W, RENDER_H)
            paths.append(target)
        return paths
    finally:
        _safe_close(pres)


def _deck_name(path: str | Path) -> str:
    return Path(path).stem


def render_frames_with_fallback(pptx: str | Path, out_dir: str | Path,
                                prefer: str = "auto") -> dict:
    """Proposed ``slide_forge.render`` fallback contract.

    PowerPoint when present; DeckCraft static frames otherwise. The result
    always names the renderer, and a DeckCraft result is never labelled
    PowerPoint. There is no video and no in-slide animation frame from
    DeckCraft: those stay PowerPoint-only (rung 2 vs rung 5).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("slide-*.png"):
        old.unlink()
    source = "powerpoint"
    try:
        if prefer == "deckcraft":
            raise RuntimeError("DeckCraft requested")
        images = powerpoint_export(pptx, out_dir)
    except Exception as exc:
        source = "deckcraft"
        images = deckcraft_render(pptx, out_dir, scale=2)
        reason = str(exc)
    else:
        reason = ""
    return {
        "renderer": source,
        "label": "PowerPoint Slide.Export" if source == "powerpoint" else "DeckCraft render (not PowerPoint)",
        "evidence_rung": 5 if source == "powerpoint" else 2,
        "frames": [str(p) for p in images],
        "video": None,
        "note": ("DeckCraft has no in-slide animation renderer; static frames only."
                 if source == "deckcraft" else ""),
        "fallback_reason": reason,
    }


# --------------------------------------------------------------------------
# Static comparison
# --------------------------------------------------------------------------

def compare_static(pptx: str | Path, pp_dir: str | Path, dc_dir: str | Path) -> tuple[list[dict], list[dict]]:
    """Return (slide rows, object rows) for one deck."""
    pptx = Path(pptx)
    pp_dir, dc_dir = Path(pp_dir), Path(dc_dir)
    n = len(Presentation(str(pptx)).slides)
    deck = _deck_name(pptx)
    slide_rows, object_rows = [], []
    for i in range(n):
        pp = load_frame(pp_dir / f"slide-{i + 1:02d}.png")
        dc = load_frame(dc_dir / f"slide-{i + 1:02d}.png")
        diff = diff_map(pp, dc)
        whole = region_metrics(diff)
        objects = slide_objects(pptx, i)
        kinds = kind_metrics(diff, objects)
        objs = object_metrics(diff, objects)
        big = [o for o in objs if (o["pixels"] or 0) >= 1000] or objs
        worst = max(big, key=lambda o: o["mean_abs"] or 0) if big else None
        slide_rows.append({
            "deck": deck, "slide": i + 1, "kind": "__slide__", "objects": len(objects),
            "pixels": whole["pixels"], "pixel_share": 100.0,
            "mean_abs": whole["mean_abs"], "pct_gt10": whole["pct_gt10"],
            "pct_gt40": whole["pct_gt40"], "max_abs": whole["max_abs"],
            "worst_object": worst["name"] if worst else "",
            "worst_object_mean": worst["mean_abs"] if worst else None,
        })
        for kind, m in sorted(kinds.items()):
            slide_rows.append({"deck": deck, "slide": i + 1, "kind": kind, **m})
        for o in objs:
            object_rows.append({
                "deck": deck, "slide": i + 1, "z": o["z"], "name": o["name"],
                "spid": o["spid"], "kinds": "+".join(o["kinds"]),
                "box": "x".join(str(v) for v in o["box"]),
                "pixels": o["pixels"], "mean_abs": o["mean_abs"],
                "pct_gt10": o["pct_gt10"], "pct_gt40": o["pct_gt40"], "max_abs": o["max_abs"],
            })
    return slide_rows, object_rows


def write_csv(path: str | Path, rows: list[dict], fields: list[str] | None = None) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fields = fields or list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return path


def slide_artifacts(pptx: str | Path, pp_dir: Path, dc_dir: Path, deck_out: Path,
                    max_theta: float = 999.0) -> dict:
    """Per-slide 3-up JPEGs and a deck contact sheet."""
    pptx = Path(pptx)
    n = len(Presentation(str(pptx)).slides)
    deck = _deck_name(pptx)
    deck_out = Path(deck_out)
    rows = []
    for i in range(n):
        pp = Image.open(pp_dir / f"slide-{i + 1:02d}.png").convert("RGB")
        dc = Image.open(dc_dir / f"slide-{i + 1:02d}.png").convert("RGB")
        d = diff_map(load_frame(pp_dir / f"slide-{i + 1:02d}.png"), load_frame(dc_dir / f"slide-{i + 1:02d}.png"))
        m = region_metrics(d)
        rows.append((i + 1, m))
        if (m["mean_abs"] or 0) <= max_theta:
            strip = Image.new("RGB", (3 * 360, 203 + 22), "white")
            strip.paste(panel(pp, 360, 203, "PowerPoint Slide.Export"), (0, 0))
            strip.paste(panel(dc, 360, 203, "DeckCraft render (not PowerPoint)"), (360, 0))
            strip.paste(panel(_heat(d), 360, 203, "abs diff x4"), (720, 0))
            draw = ImageDraw.Draw(strip)
            draw.text((6, 206), f"slide {i + 1:02d}  mean {m['mean_abs']}  >40 {m['pct_gt40']}%", fill=(40, 40, 40),
                      font=_font(13))
            save_jpeg(strip, deck_out / "diffs" / f"{deck}-slide-{i + 1:02d}.jpg", 80)
    # contact sheet
    row_h, gap, label_w, pw, ph = 203 + 26, 6, 54, 460, 259
    sheet = Image.new("RGB", (label_w + 3 * pw + 4 * gap, 40 + n * (ph + gap)), "white")
    dr = ImageDraw.Draw(sheet)
    dr.text((gap, 10), f"{deck} — PowerPoint (left) vs DeckCraft render (middle) vs abs diff x4", fill=(20, 20, 20),
            font=_font(18))
    for i in range(n):
        y = 40 + i * (ph + gap)
        dr.text((4, y + ph // 2 - 8), f"s{i + 1:02d}", fill=(30, 30, 30), font=_font(15))
        sheet.paste(panel(Image.open(pp_dir / f"slide-{i + 1:02d}.png"), pw, ph - 26), (label_w + gap, y))
        sheet.paste(panel(Image.open(dc_dir / f"slide-{i + 1:02d}.png"), pw, ph - 26), (label_w + 2 * gap + pw, y))
        d = diff_map(load_frame(pp_dir / f"slide-{i + 1:02d}.png"), load_frame(dc_dir / f"slide-{i + 1:02d}.png"))
        sheet.paste(panel(_heat(d), pw, ph - 26), (label_w + 3 * gap + 2 * pw, y))
        m = rows[i][1]
        dr.text((label_w + gap, y + ph - 22), f"mean {m['mean_abs']}   >40 {m['pct_gt40']}%",
                fill=(40, 40, 40), font=_font(13))
    save_jpeg(sheet, deck_out / "static" / f"{deck}-contact.jpg", 78)
    return {"deck": deck, "slides": n}


# --------------------------------------------------------------------------
# Design-critic parity
# --------------------------------------------------------------------------

def critic_parity(pptx: str | Path, pp_dir: str | Path) -> dict:
    """Run the critic twice: PowerPoint frames vs DeckCraft frames."""
    import design_critic
    a = design_critic.critique(pptx, render=str(pp_dir))
    b = design_critic.critique(pptx, render="deckcraft")
    scores = {}
    for dim in a["scores"]:
        pv, dv = a["scores"].get(dim), b["scores"].get(dim)
        scores[dim] = {
            "powerpoint": pv, "deckcraft": dv,
            "delta": None if pv is None or dv is None else round(dv - pv, 3),
        }
    frame_rows = []
    for fa, fb in zip(a.get("frames", []), b.get("frames", [])):
        for key in ("background_share", "balance_offset", "colourfulness"):
            frame_rows.append({
                "deck": _deck_name(pptx), "slide": fa["slide"], "metric": key,
                "powerpoint": fa[key], "deckcraft": fb[key],
                "delta": round(fb[key] - fa[key], 4),
            })
    return {"deck": _deck_name(pptx), "scores": scores, "frames": frame_rows,
            "issues_powerpoint": a.get("issues_by_code", {}),
            "issues_deckcraft": b.get("issues_by_code", {})}


# --------------------------------------------------------------------------
# PowerPoint video helpers and Morph frames
# --------------------------------------------------------------------------

def _com_app():
    import win32com.client as win32
    return win32.Dispatch("PowerPoint.Application")


def _safe_close(pres) -> None:
    """Close a presentation, tolerating PowerPoint crashing after CreateVideo."""
    try:
        pres.Close()
    except Exception:
        pass


def make_pair_deck(pptx: str | Path, target: int, out_pptx: str | Path) -> Path:
    """Copy a deck, keep slides target-1 and target, strip slide 1's timing
    and incoming transition. ``target`` is 1-based."""
    out_pptx = Path(out_pptx)
    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    app = _com_app()
    pres = app.Presentations.Open(str(Path(pptx).resolve()), ReadOnly=False, WithWindow=False)
    try:
        for i in range(pres.Slides.Count, 0, -1):
            if i not in (target - 1, target):
                pres.Slides(i).Delete()
        pres.SaveAs(str(out_pptx.resolve()))
    finally:
        _safe_close(pres)
    p = Presentation(str(out_pptx))
    el = p.slides[0]._element
    t = el.find(qn("p:timing"))
    if t is not None:
        el.remove(t)
    for child in list(el):
        if child.tag == f"{{{MC}}}AlternateContent" and child.find(".//" + qn("p:transition")) is not None:
            el.remove(child)
    direct = el.find(qn("p:transition"))
    if direct is not None:
        el.remove(direct)
    p.save(str(out_pptx))
    return out_pptx


def make_single_deck(pptx: str | Path, target: int, out_pptx: str | Path) -> Path:
    """Copy a deck with only slide ``target`` (1-based), no incoming transition."""
    out_pptx = Path(out_pptx)
    out_pptx.parent.mkdir(parents=True, exist_ok=True)
    app = _com_app()
    pres = app.Presentations.Open(str(Path(pptx).resolve()), ReadOnly=False, WithWindow=False)
    try:
        for i in range(pres.Slides.Count, 0, -1):
            if i != target:
                pres.Slides(i).Delete()
        # A leading blank slide makes CreateVideo start on a static slide, then
        # play the kept slide's click-triggered animation exactly as it does for
        # the second slide of a normal deck.
        pres.Slides.Add(1, 12)
        pres.SaveAs(str(out_pptx.resolve()))
    finally:
        _safe_close(pres)
    p = Presentation(str(out_pptx))
    idx = 1 if len(p.slides) > 1 else 0
    el = p.slides[idx]._element
    for child in list(el):
        if child.tag == f"{{{MC}}}AlternateContent" and child.find(".//" + qn("p:transition")) is not None:
            el.remove(child)
    direct = el.find(qn("p:transition"))
    if direct is not None:
        el.remove(direct)
    p.save(str(out_pptx))
    return out_pptx


def create_video(pptx: str | Path, out_mp4: str | Path, seconds: int = 2,
                 resolution: int = RENDER_H, fps: int = 30) -> Path:
    out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    if out_mp4.exists():
        out_mp4.unlink()
    app = _com_app()
    pres = app.Presentations.Open(str(Path(pptx).resolve()), ReadOnly=True, WithWindow=False)
    try:
        pres.CreateVideo(str(out_mp4.resolve()), True, seconds, resolution, fps, 85)
        t0 = time.time()
        while not out_mp4.exists() or out_mp4.stat().st_size == 0:
            time.sleep(1)
            if time.time() - t0 > 900:
                raise RuntimeError(f"CreateVideo timed out for {pptx}")
        prev, stable = -1, 0
        while stable < 3:
            time.sleep(1)
            size = out_mp4.stat().st_size
            stable = stable + 1 if size == prev else 0
            prev = size
    finally:
        _safe_close(pres)
    return out_mp4


def transition_info(pptx: str | Path, slide_index: int) -> dict:
    """Transition kind and duration (ms) for a 0-based slide index."""
    p = Presentation(str(pptx))
    el = p.slides[slide_index]._element
    alt = el.find(f"{{{MC}}}AlternateContent")
    node = None
    if alt is not None:
        node = alt.find(".//" + qn("p:transition"))
    if node is None:
        node = el.find(qn("p:transition"))
    if node is None:
        return {"kind": "none", "duration_ms": 0}
    kind = "unknown"
    for child in node:
        local = child.tag.split("}")[-1]
        if local in ("morph", "fade", "push", "wipe", "cut", "split", "cover", "uncover"):
            kind = local
            break
    dur = node.get(f"{{{P14}}}dur")
    if dur is None:
        spd = node.get("spd")
        dur = {"slow": 1500, "med": 750, "fast": 375}.get(spd or "", 1500)
    return {"kind": kind, "duration_ms": int(float(dur))}


def extract_frames(video: str | Path, out_dir: str | Path, fps: int = 30,
                   duration: float | None = None) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("*.jpg"):
        f.unlink()
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += ["-i", str(video), "-vf", f"fps={fps},scale={FRAME_W}:{FRAME_H}", "-q:v", "2",
            str(out_dir / "f-%04d.jpg")]
    subprocess.run(cmd, check=True)
    return sorted(out_dir.glob("f-*.jpg"))


def detect_transition_start(frames: list[Path], fps: int = 30, skip_s: float = 2.0,
                            threshold: float = 0.12) -> int:
    """First frame index after ``skip_s`` with two consecutive frame changes."""
    prev = None
    run = 0
    start = None
    for i, f in enumerate(frames):
        im = np.asarray(Image.open(f).convert("L").resize((480, 270)), dtype=np.int16)
        if prev is not None and i / fps >= skip_s:
            d = float(np.abs(im - prev).mean())
            if d > threshold:
                run += 1
                if run == 1:
                    start = i
                if run >= 2:
                    return start if start is not None else i
            else:
                run = 0
        prev = im
    return int(skip_s * fps)


def _region_diff(frame: np.ndarray, other: np.ndarray, box: list[int]) -> float | None:
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        return None
    return round(float(diff_map(frame[y0:y1, x0:x1], other[y0:y1, x0:x1]).mean()), 3)


def _alpha_estimate(frame: np.ndarray, prev: np.ndarray, final: np.ndarray,
                    box: list[int]) -> float | None:
    """Median opacity of the final state over a shape region.

    0 = the region still looks like the previous slide, 1 = final state.
    Pixels where the final and previous states are nearly equal carry no
    information and are ignored.
    """
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        return None
    a = frame[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    p = prev[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    f = final[y0:y1, x0:x1].astype(np.float32).mean(axis=2)
    denom = f - p
    mask = np.abs(denom) > 30
    if int(mask.sum()) < 50:
        return None
    alpha = (a[mask] - p[mask]) / denom[mask]
    return round(float(np.clip(np.median(alpha), 0, 1.5)), 3)


def _entrance_hidden(frame: np.ndarray, prev: np.ndarray, final: np.ndarray,
                     boxes: list[list[int]]) -> int:
    """Pixels inside the union of entrance shape boxes that still match the
    previous slide rather than the final one."""
    mask = np.zeros((FRAME_H, FRAME_W), dtype=bool)
    for box in boxes:
        x0, y0, x1, y1 = box
        if x1 > x0 and y1 > y0:
            mask[y0:y1, x0:x1] = True
    dp = diff_map(frame, prev)
    df = diff_map(frame, final)
    return int(((dp < 15) & (dp < df) & mask).sum())


def entrance_spids(pptx: str | Path, slide_index: int) -> Counter:
    """Effect count per shape id for entrance effects on a slide."""
    p = Presentation(str(pptx))
    root = p.slides[slide_index]._element
    timing = root.find(qn("p:timing"))
    counts: Counter = Counter()
    if timing is None:
        return counts
    for ctn in timing.findall(".//" + qn("p:cTn")):
        if ctn.get("presetClass") != "entr":
            continue
        for tgt in ctn.findall(".//" + qn("p:spTgt")):
            spid = tgt.get("spid")
            if spid:
                counts[int(spid)] += 1
    return counts


def visibility_label(frame: np.ndarray, prev: np.ndarray, final: np.ndarray, box: list[int]) -> tuple[str, float | None, float | None]:
    """Classify a shape region as final / previous / other at one time."""
    dp = _region_diff(frame, prev, box)
    df = _region_diff(frame, final, box)
    if df is None:
        return "empty", dp, df
    if df <= 15 and (dp is None or dp > 15):
        return "final", dp, df
    if dp is not None and dp <= 15 and df > 15:
        return "previous", dp, df
    if dp is not None and df < dp * 0.7:
        return "mostly-final", dp, df
    if dp is not None and dp < df * 0.7:
        return "mostly-previous", dp, df
    return "other", dp, df


def morph_compare(pptx: str | Path, target: int, work: str | Path,
                  pp_static: str | Path, out_dir: str | Path) -> dict:
    """Compare DeckCraft render-transition frames with PowerPoint video frames.

    ``target`` is the 1-based slide the transition leads into; ``pp_static``
    holds PowerPoint ``Slide.Export`` PNGs for the whole deck.
    """
    pptx = Path(pptx)
    work = Path(work)
    work.mkdir(parents=True, exist_ok=True)
    out_dir = Path(out_dir)
    name = _deck_name(pptx)
    tr = transition_info(pptx, target - 1)
    dur = max(tr["duration_ms"], 300)
    pair = work / f"{name}-pair-s{target:02d}.pptx"
    video = work / f"{name}-pair-s{target:02d}.mp4"
    make_pair_deck(pptx, target, pair)
    create_video(pair, video)
    frames = extract_frames(video, work / f"{name}-s{target:02d}-frames", fps=30, duration=8.5)
    start = detect_transition_start(frames, fps=30)
    t_frames = {t: min(len(frames) - 1, start + int(round(t * dur / 1000 * 30))) for t in MORPH_TS}

    # DeckCraft transition frames
    dc_dir = work / f"{name}-s{target:02d}-dc"
    dc_dir.mkdir(parents=True, exist_ok=True)
    out_png = dc_dir / "frame.png"
    cli = find_deckcraft_cli()
    subprocess.run([str(cli), "render-transition", str(pptx), "--slide", str(target - 1),
                    "--t", ",".join(str(t) for t in MORPH_TS), str(out_png)],
                   check=True, capture_output=True, text=True)
    dc_paths = {t: dc_dir / f"frame-t{t:.3f}.png" for t in MORPH_TS}
    for t, p in dc_paths.items():
        if not p.exists():
            raise RuntimeError(f"DeckCraft frame missing: {p}")

    final = load_frame(Path(pp_static) / f"slide-{target:02d}.png")
    prev = load_frame(Path(pp_static) / f"slide-{target - 1:02d}.png")
    objects = slide_objects(pptx, target - 1)
    entr = entrance_spids(pptx, target - 1)
    entr_boxes = [o["box"] for o in objects if o["spid"] in entr]
    rows = []
    for t in MORPH_TS:
        pp_frame = load_frame(frames[t_frames[t]])
        dc_frame = load_frame(dc_paths[t])
        d = diff_map(pp_frame, dc_frame)
        m = region_metrics(d)
        # Entrance shapes hidden: count pixels inside entrance boxes that still
        # look like the previous slide rather than the final one.
        pp_hidden = _entrance_hidden(pp_frame, prev, final, entr_boxes)
        dc_hidden = _entrance_hidden(dc_frame, prev, final, entr_boxes)
        rows.append({
            "deck": name, "slide": target, "t": t, "transition": tr["kind"],
            "duration_ms": dur, "pp_frame": t_frames[t], "start_frame": start,
            "mean_abs": m["mean_abs"], "pct_gt10": m["pct_gt10"], "pct_gt40": m["pct_gt40"],
            "pp_vs_final": region_metrics(diff_map(pp_frame, final))["mean_abs"],
            "dc_vs_final": region_metrics(diff_map(dc_frame, final))["mean_abs"],
            "pp_vs_prev": region_metrics(diff_map(pp_frame, prev))["mean_abs"],
            "dc_vs_prev": region_metrics(diff_map(dc_frame, prev))["mean_abs"],
            "pp_entrance_px": pp_hidden,
            "dc_entrance_px": dc_hidden,
        })

    hidden = []
    for o in objects:
        if o["spid"] not in entr:
            continue
        for t in MORPH_TS:
            pp_frame = load_frame(frames[t_frames[t]])
            dc_frame = load_frame(dc_paths[t])
            pp_lab, pp_prev_d, pp_fin_d = visibility_label(pp_frame, prev, final, o["box"])
            dc_lab, dc_prev_d, dc_fin_d = visibility_label(dc_frame, prev, final, o["box"])
            hidden.append({
                "deck": name, "slide": target, "shape": o["name"], "spid": o["spid"],
                "entrance_effects": entr[o["spid"]], "box": "x".join(str(v) for v in o["box"]),
                "t": t, "pp_state": pp_lab, "pp_diff_prev": pp_prev_d, "pp_diff_final": pp_fin_d,
                "dc_state": dc_lab, "dc_diff_prev": dc_prev_d, "dc_diff_final": dc_fin_d,
                "pp_alpha": _alpha_estimate(pp_frame, prev, final, o["box"]),
                "dc_alpha": _alpha_estimate(dc_frame, prev, final, o["box"]),
            })

    # 3x3 strip artifact (PowerPoint / DeckCraft / diff per t)
    cw, ch = 400, 225
    left, top = 108, 64
    strip = Image.new("RGB", (left + 3 * (cw + 8) + 8, top + 3 * (ch + 12) + 8), "white")
    dr = ImageDraw.Draw(strip)
    dr.text((10, 8), f"{name} slide {target} — transition '{tr['kind']}' {dur} ms. "
                     f"PowerPoint CreateVideo frames vs DeckCraft render-transition at matched t.",
            fill=(20, 20, 20), font=_font(15))
    for col, t in enumerate(MORPH_TS):
        dr.text((left + col * (cw + 8), 36), f"t = {t:.2f}", fill=(20, 20, 20), font=_font(15))
    row_labels = ["PowerPoint\n(video)", "DeckCraft\nrender", "abs diff\nx4"]
    for row, label in enumerate(row_labels):
        y = top + row * (ch + 12)
        dr.multiline_text((6, y + ch // 2 - 18), label, fill=(30, 30, 30), font=_font(13), spacing=3)
    for col, t in enumerate(MORPH_TS):
        x = left + col * (cw + 8)
        pp_im = Image.open(frames[t_frames[t]])
        dc_im = Image.open(dc_paths[t])
        d = diff_map(load_frame(frames[t_frames[t]]), load_frame(dc_paths[t]))
        strip.paste(panel(pp_im, cw, ch), (x, top))
        strip.paste(panel(dc_im, cw, ch), (x, top + ch + 12))
        strip.paste(panel(_heat(d), cw, ch), (x, top + 2 * (ch + 12)))
    morph_jpg = out_dir / "morph" / f"{name}-s{target:02d}.jpg"
    save_jpeg(strip, morph_jpg, 80)
    return {"rows": rows, "hidden": hidden, "strip": str(morph_jpg), "transition": tr}


# --------------------------------------------------------------------------
# Timing inventory and round trip
# --------------------------------------------------------------------------

def _local(el) -> str:
    return el.tag.split("}")[-1]


def timing_inventory(pptx: str | Path, slide_index: int) -> dict:
    """Semantic inventory of a slide's <p:timing> tree and transition."""
    p = Presentation(str(pptx))
    root = p.slides[slide_index]._element
    timing = root.find(qn("p:timing"))
    inv = {
        "effects": [], "tags": Counter(), "transition": transition_info(pptx, slide_index),
        "total_ctn": 0, "par": 0, "seq": 0, "cond": 0, "graphic_el": 0,
    }
    if timing is None:
        return inv
    inv["total_ctn"] = len(timing.findall(".//" + qn("p:cTn")))
    inv["par"] = len(timing.findall(".//" + qn("p:par")))
    inv["seq"] = len(timing.findall(".//" + qn("p:seq")))
    inv["cond"] = len(timing.findall(".//" + qn("p:cond")))
    inv["graphic_el"] = len(timing.findall(".//" + qn("p:graphicEl")))
    for el in timing.iter():
        tag = _local(el)
        if tag in ("anim", "animEffect", "animMotion", "animRot", "animScale", "animClr", "set",
                   "cmd", "audio", "video", "animBg"):
            inv["tags"][tag] += 1
    for ctn in timing.findall(".//" + qn("p:cTn")):
        if ctn.get("presetID") is None:
            continue
        spids = [int(t.get("spid")) for t in ctn.findall(".//" + qn("p:spTgt")) if t.get("spid")]
        delay = None
        cond = ctn.find(qn("p:stCondLst") + "/" + qn("p:cond"))
        if cond is not None:
            delay = cond.get("delay")
        children = []
        child_list = ctn.find(qn("p:childTnLst"))
        if child_list is not None:
            for ch in child_list:
                children.append(_local(ch))
        props = [a.text for a in ctn.findall(".//" + qn("p:attrName")) if a.text]
        inv["effects"].append({
            "spid": spids[0] if spids else None,
            "class": ctn.get("presetClass"),
            "preset": ctn.get("presetID"),
            "subtype": ctn.get("presetSubtype"),
            "node": ctn.get("nodeType"),
            "dur": ctn.get("dur"),
            "delay": delay,
            "repeat": ctn.get("repeatCount"),
            "grp": ctn.get("grpId"),
            "children": sorted(children),
            "props": sorted(set(props)),
        })
    return inv


def _shape_names(pptx: str | Path, slide_index: int) -> dict[int, str]:
    p = Presentation(str(pptx))
    return {int(s.shape_id): s.name for s in p.slides[slide_index].shapes}


def roundtrip_compare(original: str | Path, converted: str | Path) -> tuple[list[dict], list[dict]]:
    """Compare timing inventories of two decks. Returns (summary rows, effect rows)."""
    original, converted = Path(original), Path(converted)
    deck = _deck_name(original)
    n = len(Presentation(str(original)).slides)
    summary, effect_rows = [], []
    for i in range(n):
        a = timing_inventory(original, i)
        b = timing_inventory(converted, i)
        names = _shape_names(original, i)
        tags = sorted(set(a["tags"]) | set(b["tags"]))
        for tag in tags:
            summary.append({
                "deck": deck, "slide": i + 1, "node": tag,
                "original": a["tags"].get(tag, 0), "roundtrip": b["tags"].get(tag, 0),
                "delta": b["tags"].get(tag, 0) - a["tags"].get(tag, 0),
            })
        for node in ("total_ctn", "par", "seq", "cond", "graphic_el"):
            summary.append({
                "deck": deck, "slide": i + 1, "node": node,
                "original": a[node], "roundtrip": b[node], "delta": b[node] - a[node],
            })
        summary.append({
            "deck": deck, "slide": i + 1, "node": "transition",
            "original": f"{a['transition']['kind']}:{a['transition']['duration_ms']}",
            "roundtrip": f"{b['transition']['kind']}:{b['transition']['duration_ms']}",
            "delta": 0 if a["transition"] == b["transition"] else 1,
        })
        # effect-level signature match
        sig_a = Counter((e["spid"], e["class"], e["preset"], e["node"], e["dur"], e["delay"],
                         tuple(e["children"]), tuple(e["props"])) for e in a["effects"])
        sig_b = Counter((e["spid"], e["class"], e["preset"], e["node"], e["dur"], e["delay"],
                         tuple(e["children"]), tuple(e["props"])) for e in b["effects"])
        for sig, count in (sig_a - sig_b).items():
            effect_rows.append({"deck": deck, "slide": i + 1, "status": "lost", "count": count,
                                "spid": sig[0], "shape": names.get(sig[0], ""), "class": sig[1],
                                "preset": sig[2], "node": sig[3], "dur": sig[4], "delay": sig[5],
                                "children": "+".join(sig[6]), "props": "+".join(sig[7])})
        for sig, count in (sig_b - sig_a).items():
            effect_rows.append({"deck": deck, "slide": i + 1, "status": "added", "count": count,
                                "spid": sig[0], "shape": names.get(sig[0], ""), "class": sig[1],
                                "preset": sig[2], "node": sig[3], "dur": sig[4], "delay": sig[5],
                                "children": "+".join(sig[6]), "props": "+".join(sig[7])})
    return summary, effect_rows


def powerpoint_timeline(pptx: str | Path) -> list[dict]:
    """What PowerPoint parses: main-sequence effects per slide (rung 4)."""
    app = _com_app()
    pres = app.Presentations.Open(str(Path(pptx).resolve()), ReadOnly=True, WithWindow=False)
    out = []
    try:
        for i in range(1, pres.Slides.Count + 1):
            slide = pres.Slides(i)
            seq = slide.TimeLine.MainSequence
            effects = []
            for j in range(1, seq.Count + 1):
                e = seq.Item(j)
                try:
                    timing = e.Timing
                    behaviors, btypes = 0, []
                    try:
                        bs = e.Behaviors
                        behaviors = int(bs.Count)
                        btypes = [int(bs.Item(k).Type) for k in range(1, behaviors + 1)]
                    except Exception:
                        pass
                    effects.append({
                        "shape": e.Shape.Name,
                        "type": int(e.EffectType),
                        "duration": round(float(getattr(timing, "Duration", 0)), 1),
                        "trigger": int(getattr(timing, "TriggerType", 0)),
                        "repeat": float(getattr(timing, "RepeatCount", 1)),
                        "rewind": bool(getattr(timing, "Rewind", False)),
                        "behaviors": behaviors,
                        "behavior_types": btypes,
                    })
                except Exception:
                    effects.append({"shape": e.Shape.Name, "error": True})
            tr = slide.SlideShowTransition
            out.append({
                "slide": i,
                "main_sequence": seq.Count,
                "effects": effects,
                "transition_entry": int(tr.EntryEffect),
                "transition_duration": round(float(tr.Duration), 1),
                "advance_on_click": bool(tr.AdvanceOnClick),
            })
    finally:
        _safe_close(pres)
    return out


def pp_compare(original: str | Path, converted: str | Path) -> list[dict]:
    """Compare what PowerPoint parses in the two decks (rung 4)."""
    a = powerpoint_timeline(original)
    b = powerpoint_timeline(converted)
    deck = _deck_name(original)
    rows = []
    for sa, sb in zip(a, b):
        sig_a = Counter(json.dumps(e, sort_keys=True) for e in sa["effects"])
        sig_b = Counter(json.dumps(e, sort_keys=True) for e in sb["effects"])
        lost = sum((sig_a - sig_b).values())
        added = sum((sig_b - sig_a).values())
        beh_a = sum(e.get("behaviors", 0) for e in sa["effects"])
        beh_b = sum(e.get("behaviors", 0) for e in sb["effects"])
        rows.append({
            "deck": deck, "slide": sa["slide"],
            "effects_original": sa["main_sequence"], "effects_roundtrip": sb["main_sequence"],
            "lost": lost, "added": added,
            "behaviors_original": beh_a, "behaviors_roundtrip": beh_b, "behaviors_lost": beh_a - beh_b,
            "transition_original": f"{sa['transition_entry']}:{sa['transition_duration']}",
            "transition_roundtrip": f"{sb['transition_entry']}:{sb['transition_duration']}",
            "transition_equal": sa["transition_entry"] == sb["transition_entry"]
                                and sa["transition_duration"] == sb["transition_duration"],
            "advance_equal": sa["advance_on_click"] == sb["advance_on_click"],
            "signature_equal": sa["effects"] == sb["effects"],
        })
    return rows


def playback_compare(original: str | Path, converted: str | Path, target: int,
                     work: str | Path, final_pp_dir: str | Path) -> list[dict]:
    """Create pair videos for original and round-tripped decks, compare phases."""
    work = Path(work)
    name = _deck_name(original)
    rows = []
    frames_by = {}
    for label, deck in (("original", original), ("roundtrip", converted)):
        pair = work / f"rt-{name}-{label}-s{target:02d}.pptx"
        video = work / f"rt-{name}-{label}-s{target:02d}.mp4"
        make_pair_deck(deck, target, pair)
        create_video(pair, video)
        frames = extract_frames(video, work / f"rt-{name}-{label}-s{target:02d}-frames", fps=30, duration=8.5)
        start = detect_transition_start(frames, fps=30)
        frames_by[label] = (frames, start)
    tr = transition_info(original, target - 1)
    dur = max(tr["duration_ms"], 300)
    fa, sa = frames_by["original"]
    fb, sb = frames_by["roundtrip"]
    for t in MORPH_TS:
        ia = min(len(fa) - 1, sa + int(round(t * dur / 1000 * 30)))
        ib = min(len(fb) - 1, sb + int(round(t * dur / 1000 * 30)))
        d = diff_map(load_frame(fa[ia]), load_frame(fb[ib]))
        m = region_metrics(d)
        rows.append({"deck": name, "slide": target, "phase": f"t={t}", "mean_abs": m["mean_abs"],
                     "pct_gt10": m["pct_gt10"], "pct_gt40": m["pct_gt40"]})
    # settled end of the pair video (last frame)
    d = diff_map(load_frame(fa[-1]), load_frame(fb[-1]))
    m = region_metrics(d)
    rows.append({"deck": name, "slide": target, "phase": "settled-end", "mean_abs": m["mean_abs"],
                 "pct_gt10": m["pct_gt10"], "pct_gt40": m["pct_gt40"]})
    return rows


def animation_playback(original: str | Path, converted: str | Path, target: int,
                       work: str | Path, out_dir: str | Path) -> dict:
    """Play one slide in both decks and compare the animation path frame by frame.

    A single-slide deck has no incoming transition, so any difference comes
    from the slide's own timing tree. Frames are paired by index; both videos
    start on the same slide and PowerPoint auto-advances the same triggers.
    """
    work, out_dir = Path(work), Path(out_dir)
    work.mkdir(parents=True, exist_ok=True)
    name = _deck_name(original)
    frames_by = {}
    for label, deck in (("original", original), ("roundtrip", converted)):
        single = work / f"anim-{name}-{label}-s{target:02d}.pptx"
        video = work / f"anim-{name}-{label}-s{target:02d}.mp4"
        make_single_deck(deck, target, single)
        create_video(single, video)
        frames = extract_frames(video, work / f"anim-{name}-{label}-s{target:02d}-frames", fps=30)
        frames_by[label] = frames
    fa, fb = frames_by["original"], frames_by["roundtrip"]
    # The first slide is blank; align each video on the frame where its target
    # appears, then compare relative frames.
    sa = detect_transition_start(fa, fps=30, skip_s=0.5, threshold=0.2)
    sb = detect_transition_start(fb, fps=30, skip_s=0.5, threshold=0.2)
    fa, fb = fa[sa:], fb[sb:]
    n = min(len(fa), len(fb))
    series = []
    for i in range(n):
        d = diff_map(load_frame(fa[i]), load_frame(fb[i]))
        series.append(float(d.mean()))
    base = float(np.median(series[:10])) if series else 0.0
    peak_i = int(np.argmax(series)) if series else 0
    changed = [i for i, v in enumerate(series) if v > max(base + 5, 5)]
    settled = float(np.mean(series[-10:])) if series else 0.0
    # peak strip artifact
    strip = Image.new("RGB", (3 * 400, 225 + 26), "white")
    strip.paste(panel(Image.open(fa[peak_i]), 400, 225, "original"), (0, 0))
    strip.paste(panel(Image.open(fb[peak_i]), 400, 225, "round trip"), (400, 0))
    d = diff_map(load_frame(fa[peak_i]), load_frame(fb[peak_i]))
    strip.paste(panel(_heat(d), 400, 225, "abs diff x4"), (800, 0))
    strip_path = out_dir / "morph" / f"roundtrip-anim-{name}-s{target:02d}.jpg"
    save_jpeg(strip, strip_path, 82)
    return {
        "deck": name, "slide": target, "frames": n, "baseline": round(base, 3),
        "peak_frame": peak_i, "peak_mean": round(max(series) if series else 0, 3),
        "changed_frames": len(changed), "first_changed": changed[0] if changed else None,
        "last_changed": changed[-1] if changed else None, "settled_mean": round(settled, 3),
        "same_end_state": settled < 2.0, "strip": str(strip_path),
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _deck_paths(decks: str | Path) -> list[Path]:
    p = Path(decks)
    if p.is_file():
        return [p]
    return sorted(x for x in p.glob("*.pptx") if ".static." not in x.name and not x.name.startswith("~$"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("static")
    sp.add_argument("--decks", required=True)
    sp.add_argument("--out", required=True)
    sp.add_argument("--work", default="workspace/t059")

    cp = sub.add_parser("critic")
    cp.add_argument("--decks", required=True)
    cp.add_argument("--out", required=True)

    mp = sub.add_parser("morph")
    mp.add_argument("--pptx", required=True)
    mp.add_argument("--slide", type=int, required=True)
    mp.add_argument("--work", default="workspace/t059-morph")
    mp.add_argument("--out", required=True)
    mp.add_argument("--pp-static", required=True, help="directory of PowerPoint slide-NN.png for this deck")

    mb = sub.add_parser("morph-batch")
    mb.add_argument("--pptx", required=True)
    mb.add_argument("--slides", required=True, help="1-based comma list, e.g. 2,3,4")
    mb.add_argument("--work", default="workspace/t059-morph")
    mb.add_argument("--out", required=True)
    mb.add_argument("--pp-static", required=True)

    rp = sub.add_parser("roundtrip")
    rp.add_argument("--pptx", required=True)
    rp.add_argument("--out", required=True)
    rp.add_argument("--work", default="workspace/t059-rt")

    pc = sub.add_parser("pp-compare")
    pc.add_argument("--original", required=True)
    pc.add_argument("--roundtrip", required=True)
    pc.add_argument("--out", required=True)

    pb = sub.add_parser("playback")
    pb.add_argument("--original", required=True)
    pb.add_argument("--roundtrip", required=True)
    pb.add_argument("--slide", type=int, required=True)
    pb.add_argument("--work", default="workspace/t059-playback")
    pb.add_argument("--out", required=True)

    an = sub.add_parser("animation")
    an.add_argument("--original", required=True)
    an.add_argument("--roundtrip", required=True)
    an.add_argument("--slide", type=int, required=True)
    an.add_argument("--work", default="workspace/t059-animation")
    an.add_argument("--out", required=True)

    a = ap.parse_args(argv)

    if a.cmd == "static":
        out = Path(a.out)
        work = Path(a.work)
        slide_rows, object_rows, crit_rows, frame_rows = [], [], [], []
        for deck in _deck_paths(a.decks):
            name = _deck_name(deck)
            pp_dir = work / "pp" / name
            dc_dir = work / "dc" / name
            n_slides = len(Presentation(str(deck)).slides)
            if len(list(pp_dir.glob("slide-*.png"))) != n_slides:
                powerpoint_export(deck, pp_dir)
            if len(list(dc_dir.glob("slide-*.png"))) != n_slides:
                deckcraft_render(deck, dc_dir)
            s, o = compare_static(deck, pp_dir, dc_dir)
            slide_rows += s
            object_rows += o
            slide_artifacts(deck, pp_dir, dc_dir, out)
            try:
                c = critic_parity(deck, pp_dir)
                for dim, v in c["scores"].items():
                    crit_rows.append({"deck": name, "dimension": dim, **v})
                frame_rows += c["frames"]
            except Exception as exc:  # critic is a secondary measurement
                crit_rows.append({"deck": name, "dimension": "error", "powerpoint": None,
                                  "deckcraft": None, "delta": None, "error": str(exc)})
            print("static", name, len(s), "rows")
        write_csv(out / "fidelity.csv", slide_rows)
        write_csv(out / "fidelity_objects.csv", object_rows)
        write_csv(out / "critic_parity.csv", crit_rows)
        write_csv(out / "critic_frames.csv", frame_rows)
        return 0

    if a.cmd == "critic":
        out = Path(a.out)
        rows = []
        for deck in _deck_paths(a.decks):
            name = _deck_name(deck)
            pp_dir = Path("workspace/t059/pp") / name
            if not pp_dir.exists():
                powerpoint_export(deck, pp_dir)
            c = critic_parity(deck, pp_dir)
            for dim, v in c["scores"].items():
                rows.append({"deck": name, "dimension": dim, **v})
            print("critic", name)
        write_csv(out / "critic_parity.csv", rows)
        return 0

    if a.cmd == "morph":
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        res = morph_compare(a.pptx, a.slide, a.work, a.pp_static, out)
        write_csv(out / "morph.csv", res["rows"], fields=list(res["rows"][0].keys()))
        write_csv(out / "morph_hidden.csv", res["hidden"], fields=list(res["hidden"][0].keys()) if res["hidden"] else None)
        print(json.dumps({"strip": res["strip"], "rows": len(res["rows"]), "hidden": len(res["hidden"])}))
        return 0

    if a.cmd == "morph-batch":
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        rows, hidden = [], []
        for target in [int(x) for x in a.slides.split(",") if x.strip()]:
            try:
                res = morph_compare(a.pptx, target, a.work, a.pp_static, out)
                rows += res["rows"]
                hidden += res["hidden"]
                print("morph", _deck_name(a.pptx), target, "ok", len(res["rows"]), len(res["hidden"]))
            except Exception as exc:
                print("morph", _deck_name(a.pptx), target, "FAILED", exc)
        write_csv(out / "morph.csv", rows)
        write_csv(out / "morph_hidden.csv", hidden)
        return 0

    if a.cmd == "roundtrip":
        out = Path(a.out)
        work = Path(a.work)
        work.mkdir(parents=True, exist_ok=True)
        rt = work / f"{_deck_name(a.pptx)}-roundtrip.pptx"
        if not rt.exists():
            cli = find_deckcraft_cli()
            subprocess.run([str(cli), "convert", str(a.pptx), str(rt)], check=True)
        summary, effects = roundtrip_compare(a.pptx, rt)
        write_csv(out / "roundtrip.csv", summary)
        write_csv(out / "roundtrip_effects.csv", effects)
        try:
            pp = pp_compare(a.pptx, rt)
            write_csv(out / "roundtrip_pp.csv", pp)
        except Exception as exc:
            print("pp compare failed:", exc)
        print(json.dumps({"deck": _deck_name(a.pptx), "rows": len(summary), "effect_diffs": len(effects)}))
        return 0

    if a.cmd == "pp-compare":
        rows = pp_compare(a.original, a.roundtrip)
        write_csv(Path(a.out) / "roundtrip_pp.csv", rows)
        print(json.dumps({"deck": _deck_name(a.original), "rows": len(rows)}))
        return 0

    if a.cmd == "playback":
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        rows = playback_compare(a.original, a.roundtrip, a.slide, a.work, Path(a.work))
        write_csv(out / "roundtrip_playback.csv", rows)
        print(json.dumps({"deck": _deck_name(a.original), "slide": a.slide, "rows": len(rows)}))
        return 0

    if a.cmd == "animation":
        out = Path(a.out)
        out.mkdir(parents=True, exist_ok=True)
        row = animation_playback(a.original, a.roundtrip, a.slide, a.work, out)
        write_csv(out / "roundtrip_animation.csv", [row])
        print(json.dumps(row))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
