#!/usr/bin/env python3
"""EXPERIMENTAL (T062) - measure the three routes in PowerPoint and in pixels.

Reads the three PPTX files, records what each one actually contains (OOXML and
PowerPoint's own object model), exports each slide to PNG with PowerPoint, and
computes the render metrics the report quotes:

  * art_parts_addressable : how many of the spec's art parts a Director can name
  * renderer_delta_pct    : route reference render vs PowerPoint's render, art crop
  * silhouette_iou_vs_native, mean_rgb_error : route C/B against route A

Writes artifacts/route-evidence.json plus the PNGs. Rung 1/3/4/5 evidence;
never rung 6 (no human has judged the slide).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import route_stage as stage  # noqa: E402

ART_CROP_X = 1120  # 560 pt at 2x: the copy column ends before the art
BG = (15, 23, 42)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ooxml_inventory(pptx: Path) -> dict:
    with zipfile.ZipFile(pptx) as package:
        slides = [n for n in package.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        xml = "".join(package.read(n).decode("utf-8") for n in slides)
        media = [n for n in package.namelist() if n.startswith("ppt/media/")]
        return {
            "slides": len(slides),
            "shapes": xml.count("<p:sp>") + xml.count("<p:sp "),
            "pictures": xml.count("<p:pic>"),
            "graphic_frames": xml.count("<p:graphicFrame>"),
            "groups": xml.count("<p:grpSp>"),
            "custom_geometry": xml.count("<a:custGeom>"),
            "scene3d": xml.count("<a:scene3d>"),
            "sp3d": xml.count("<a:sp3d>"),
            "model3d": xml.count("model3d"),
            "timing_nodes": xml.count("<p:cTn "),
            "media": media,
        }


def powerpoint_inventory(pptx: Path, png: Path) -> dict:
    import win32com.client as win32

    app = win32.Dispatch("PowerPoint.Application")
    app.Visible = True
    presentation = app.Presentations.Open(str(pptx.resolve()), WithWindow=False)
    try:
        slide = presentation.Slides(1)
        shapes = []
        for index in range(1, slide.Shapes.Count + 1):
            shape = slide.Shapes(index)
            shapes.append({"name": shape.Name, "type": int(shape.Type),
                           "box": [round(v, 1) for v in (shape.Left, shape.Top, shape.Width, shape.Height)]})
        sequence = slide.TimeLine.MainSequence
        animations = []
        for index in range(1, sequence.Count + 1):
            effect = sequence(index)
            animations.append({"shape": effect.Shape.Name, "effect": int(effect.EffectType),
                               "duration_ms": round(effect.Timing.Duration * 1000),
                               "delay_ms": round(effect.Timing.TriggerDelayTime * 1000)})
        slide.Export(str(png.resolve()), "PNG", 1920, 1080)
        return {"shapes": shapes, "animations": animations, "slides": presentation.Slides.Count,
                "slide_size": [presentation.PageSetup.SlideWidth, presentation.PageSetup.SlideHeight]}
    finally:
        presentation.Close()
        app.Quit()


def art_pixels(path: Path) -> np.ndarray:
    image = np.asarray(Image.open(path).convert("RGB")).astype(int)
    return image[:, ART_CROP_X:]


def composite_over_bg(path: Path, out: Path) -> Path:
    image = Image.open(path).convert("RGBA")
    canvas = Image.new("RGB", image.size, BG)
    canvas.paste(image, (0, 0), image)
    canvas.save(out)
    return out


def diff(a: np.ndarray, b: np.ndarray) -> dict:
    delta = np.abs(a - b)
    worst = delta.max(axis=2)
    return {
        "mean_abs": round(float(delta.mean()), 2),
        "pct_over_24": round(float((worst > 24).mean() * 100), 2),
        "pct_over_64": round(float((worst > 64).mean() * 100), 2),
    }


def silhouette(image: np.ndarray) -> np.ndarray:
    return np.abs(image - np.array(BG)).sum(axis=2) > 24


def compare_masks(a: np.ndarray, b: np.ndarray) -> dict:
    from PIL import ImageFilter

    ma, mb = silhouette(a), silhouette(b)
    intersection = ma & mb
    union = ma | mb
    iou = float(intersection.sum() / max(1, union.sum()))
    # Colour agreement on and around the native silhouette: the dark body of the
    # native art sits too close to the background to be a reliable mask, so the
    # mask is dilated instead of trusting the strict silhouette.
    grown = np.asarray(
        Image.fromarray((ma * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(25))
    ) > 0
    colour_error = float(np.abs(a[grown] - b[grown]).mean())
    return {
        "iou": round(iou, 4),
        "mean_rgb_error_on_native": round(colour_error, 2),
        "art_coverage_pct": [round(float(ma.mean() * 100), 2), round(float(mb.mean() * 100), 2)],
        "native_silhouette_recall": round(float(intersection.sum() / max(1, ma.sum())), 4),
        "bbox_pt": [_bbox(ma), _bbox(mb)],
    }


def _bbox(mask: np.ndarray) -> list[float]:
    ys, xs = np.where(mask)
    if not len(xs):
        return [0, 0, 0, 0]
    return [round(xs.min() / 2, 1), round(ys.min() / 2, 1),
            round((xs.max() - xs.min()) / 2, 1), round((ys.max() - ys.min()) / 2, 1)]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--glb", type=Path, required=True)
    parser.add_argument("--svg-art-png", type=Path, required=True)
    parser.add_argument("--native-render", type=Path, required=True,
                        help="DeckCraft's render of the native PPTX (its own reference)")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    spec, theme = stage.load(args.spec)
    asset = spec["asset"]["native_art"]
    art_names = [p["name"] for p in asset["parts"] if p["role"] == "art"]

    args.out.mkdir(parents=True, exist_ok=True)
    routes = {}
    for key, pptx in (("A_native", args.native), ("B_svg", args.svg), ("C_glb", args.glb)):
        png = args.out / f"render-{key.split('_')[0].lower()}.png"
        routes[key] = {
            "pptx": str(pptx),
            "bytes": pptx.stat().st_size,
            "sha256": sha256(pptx),
            "ooxml": ooxml_inventory(pptx),
            "powerpoint": powerpoint_inventory(pptx, png),
            "render": str(png),
        }
        present = {shape["name"] for shape in routes[key]["powerpoint"]["shapes"]}
        routes[key]["art_parts_addressable"] = sum(1 for name in art_names if name in present)
        routes[key]["art_parts_missing"] = [name for name in art_names if name not in present]
        routes[key]["named_shapes"] = sorted(present)

    native_px = art_pixels(args.out / "render-a.png")
    svg_px = art_pixels(args.out / "render-b.png")
    glb_px = art_pixels(args.out / "render-c.png")

    reference_svg = composite_over_bg(args.svg_art_png, args.out / "reference-b.png")
    metrics = {
        "A_native": {"reference_render": str(args.native_render),
                     "renderer_delta": diff(art_pixels(args.native_render), native_px)},
        "B_svg": {"reference_render": str(reference_svg),
                  "renderer_delta": diff(art_pixels(reference_svg), svg_px)},
        "C_glb": {"reference_render": None,
                  "renderer_delta": None,
                  "note": "no independent glTF render was produced; PowerPoint is the only renderer"},
    }
    metrics["B_svg"]["vs_native"] = compare_masks(native_px, svg_px)
    metrics["C_glb"]["vs_native"] = compare_masks(native_px, glb_px)

    evidence = {
        "spec": str(args.spec),
        "art_parts_declared": len(art_names),
        "routes": routes,
        "metrics": metrics,
    }
    (args.out / "route-evidence.json").write_text(json.dumps(evidence, indent=1), encoding="utf-8")
    summary = {
        key: {
            "bytes": routes[key]["bytes"],
            "shapes": routes[key]["powerpoint"]["shapes"].__len__(),
            "animations": len(routes[key]["powerpoint"]["animations"]),
            "art_parts_addressable": routes[key]["art_parts_addressable"],
            "renderer_delta_pct": metrics[key]["renderer_delta"]["pct_over_24"] if metrics[key]["renderer_delta"] else None,
            "vs_native_iou": metrics[key].get("vs_native", {}).get("iou"),
            "vs_native_rgb_error": metrics[key].get("vs_native", {}).get("mean_rgb_error_on_native"),
        }
        for key in routes
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
