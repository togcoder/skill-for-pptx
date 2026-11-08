#!/usr/bin/env python3
"""Small toolbox for the PPTX guidance skill (skills/pptx, T087).

The skill decides what the deck should look like and how it should move. These
commands only do what written guidance cannot:

    look DECK [-o DIR]          export every slide as PNG with PowerPoint, plus one
                                contact sheet, so the agent can see what it built
    motion DECK PLAN -o OUT     write click reveals and slide transitions from a
                                short plan that names shapes, not ids

Plan (JSON), slide numbers start at 1:

    {"transitions": {"default": "none", "2": "morph", "7": "fade"},
     "clicks": {"3": [["Title"], ["Card A", "Card B"], ["Chart:wipe"]]}}

- transitions: "morph", "fade" or "none" for a slide (the transition *into* that
  slide). "default" covers every slide not listed. Slides not covered keep theirs.
- clicks: a list of clicks for a slide; each click lists the shapes that appear
  together, 120 ms apart. "Name:effect" picks fade (default), rise, wipe or zoom.
  Shapes not listed are visible when the slide opens.

A slide named in "clicks" gets its old animation replaced; every other slide
keeps its animation. Shape names are the names in PowerPoint's Selection Pane.
"""
import argparse
import json
import sys
from pathlib import Path

from lxml import etree as E
from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pptx_animator as anim  # noqa: E402

NS = anim.NS
EFFECTS = {"fade": ("fade", 500), "rise": ("float-in", 600), "wipe": ("wipe-right", 500), "zoom": ("zoom", 500)}
STAGGER_MS = 120
MORPH_MS = 1400


def _remove_transition(root):
    for node in list(root):
        tag = E.QName(node).localname
        if tag == "transition" or (tag == "AlternateContent" and node.find(".//p:transition", NS) is not None):
            root.remove(node)


def _add_fade(root):
    tr = E.Element(anim.q("transition"), spd="med")
    E.SubElement(tr, anim.q("fade"))
    anchor = root.find("p:timing", NS)
    if anchor is None:
        anchor = root.find("p:extLst", NS)
    if anchor is not None:
        anchor.addprevious(tr)
    else:
        root.append(tr)


def _shape_ids(slide):
    ids = {}
    for shape in slide.shapes:
        if shape.name in ids:
            raise ValueError(f"two shapes are named {shape.name!r}; give each a unique name")
        ids[shape.name] = str(shape.shape_id)
    return ids


def _clicks(slide_no, slide, clicks, morph_in):
    ids = _shape_ids(slide)
    out = []
    for n, names in enumerate(clicks, 1):
        if not names:
            raise ValueError(f"slide {slide_no}, click {n} is empty")
        effects = []
        for k, item in enumerate(names):
            name, _, effect = item.partition(":")
            effect = effect or "fade"
            if effect not in EFFECTS:
                raise ValueError(f"slide {slide_no}: unknown effect {effect!r}; use one of {sorted(EFFECTS)}")
            if name not in ids:
                raise ValueError(f"slide {slide_no}: no shape named {name!r}; shapes are {sorted(ids)}")
            if morph_in and name.startswith("!!"):
                # T074 M-07: an entrance on a Morph actor stops the Morph.
                raise ValueError(f"slide {slide_no}: {name!r} carries the Morph; it cannot also have a click entrance")
            preset, ms = EFFECTS[effect]
            effects.append({"preset": preset, "spid": ids[name], "trigger": "click" if k == 0 else "with",
                            "duration_ms": ms, "delay_ms": k * STAGGER_MS})
        out.append({"id": f"s{slide_no}c{n}", "start": "click", "effects": effects})
    return out


def apply_motion(deck, plan, output):
    prs = Presentation(deck)
    slides = list(prs.slides)
    trans = {str(k): v for k, v in (plan.get("transitions") or {}).items()}
    clicks = {str(k): v for k, v in (plan.get("clicks") or {}).items()}
    for key in list(trans) + list(clicks):
        if key != "default" and not (key.isdigit() and 1 <= int(key) <= len(slides)):
            raise ValueError(f"slide {key} does not exist (deck has {len(slides)} slides)")
    summary = {"morph": [], "fade": [], "clicks": {}}
    for i, slide in enumerate(slides, 1):
        root = slide._element
        kind = trans.get(str(i), trans.get("default"))
        if kind is not None:
            if kind not in ("morph", "fade", "none"):
                raise ValueError(f"slide {i}: transition must be morph, fade or none, not {kind!r}")
            _remove_transition(root)
            if kind == "morph":
                anim.add_morph_transition(root, duration_ms=MORPH_MS, strip_empty_placeholders=True)
            elif kind == "fade":
                _add_fade(root)
            if kind != "none":
                summary[kind].append(i)
        if str(i) in clicks:
            timing = root.find("p:timing", NS)
            if timing is not None:
                root.remove(timing)
            groups = _clicks(i, slide, clicks[str(i)], kind == "morph")
            if groups:
                anim.apply_timeline(root, groups)
            summary["clicks"][i] = len(groups)
    prs.save(output)
    return summary


def look(deck, out_dir):
    try:
        import win32com.client as win32
    except ImportError:
        sys.exit("look needs PowerPoint on Windows (pywin32). Without it: "
                 "python scripts/design_critic.py DECK --render dc")
    from PIL import Image, ImageDraw
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    app = win32.Dispatch("PowerPoint.Application")
    was_open = app.Presentations.Count
    pres = app.Presentations.Open(str(Path(deck).resolve()), True, False, False)
    paths = []
    try:
        for i in range(1, pres.Slides.Count + 1):
            target = (out_dir / f"slide-{i:02d}.png").resolve()
            pres.Slides(i).Export(str(target), "PNG", 1600, 900)
            paths.append(target)
    finally:
        pres.Close()
        if not was_open:
            app.Quit()
    cols, w = 4, 480
    h = w * 9 // 16
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 8) + 8), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    for n, p in enumerate(paths):
        x, y = 8 + (n % cols) * (w + 8), 8 + (n // cols) * (h + 8)
        sheet.paste(Image.open(p).convert("RGB").resize((w, h)), (x, y))
        draw.rectangle([x, y, x + 34, y + 22], fill=(0, 0, 0))
        draw.text((x + 6, y + 5), str(n + 1), fill=(255, 255, 255))
    sheet.save(out_dir / "sheet.jpg", quality=85)
    return paths, out_dir / "sheet.jpg"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("look", help="export slides as PNG + contact sheet (PowerPoint)")
    a.add_argument("deck")
    a.add_argument("-o", "--output", default=None, help="folder (default: <deck>-look)")
    a = sp.add_parser("motion", help="write clicks and transitions from a plan")
    a.add_argument("deck")
    a.add_argument("plan")
    a.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)
    if args.cmd == "look":
        out = args.output or str(Path(args.deck).with_suffix("")) + "-look"
        paths, sheet = look(args.deck, out)
        print(f"{len(paths)} slides -> {out}\ncontact sheet: {sheet}")
    else:
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
        try:
            summary = apply_motion(args.deck, plan, args.output)
        except ValueError as exc:
            sys.exit(f"error: {exc}")
        print(json.dumps(summary, ensure_ascii=False))
        print("next: python scripts/morph_studio.py audit " + args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
