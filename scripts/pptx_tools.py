#!/usr/bin/env python3
"""Small toolbox for the PPTX guidance skill (skills/pptx, T087).

The skill decides what the deck should look like and how it should move. These
commands only do what written guidance cannot:

    look DECK [-o DIR]          export every slide as PNG with PowerPoint, plus one
                                contact sheet, so the agent can see what it built
    motion DECK PLAN -o OUT     write click reveals and slide transitions from a
                                short plan that names shapes, not ids
    watch DECK [--slides 3,6] [-o DIR]
                                play the deck in PowerPoint's own slide show and
                                photograph what a viewer sees: each slide as it
                                opens, after every click, and three frames inside
                                every Morph; names clicks that change nothing
    glance DECK [--slides 3,6] [--ink HEX OUT.pptx] [-o DIR]
                                the faults a viewer sees in the first second, from
                                PowerPoint's own facts (where the text really is,
                                its colour and size as drawn, the master's shapes):
                                text on text, text nobody can read, a logo on the
                                master's logo, hidden text, content under the
                                shell, tiny text, a slide missing its title; each
                                boxed on a picture of the slide. Exit code 1 while
                                any is left. --ink recolours the unreadable text
    sample DOC.pdf [--pages 5,11] [-o DIR]
                                a reference to follow (a report, a brochure): its real
                                font names and whether this machine has them, the
                                sizes and colours it uses most, pictures of its pages

For a deck someone else made (skills/pptx/guides/10-dong-bo-slide-co-san.md):

    inventory DECK              fonts (theme fonts by name), sizes, text colours,
                                fills, and per-slide problems a person cannot
                                measure by eye (3D charts, stretched pictures,
                                shapes off the slide, small text, decorative
                                animation, a slide that opens with only its title)
    scale DECK SLIDE NAME... --by F -o OUT
                                shrink or grow a set of shapes as one block:
                                places, sizes, font sizes, line widths, table
                                cells and the motion paths inside it; ids and
                                animation are kept
    rechart DECK SLIDE NAME --kind column|bar|line|pie -o OUT
                                rebuild a chart (3D included) as a flat native
                                chart from its own numbers, same place, same id
    retable DECK SLIDE NAME [--fill FFFF00=0062AC] -o OUT
                                restyle a native table in place (a Gantt, a
                                check sheet): text, merges and size kept;
                                borders, fills and type follow the deck
    cutout IMAGE -o OUT.png     take a plain background off a picture (a
                                diagram frame, a logo): soft edges, inner
                                parts kept, faint marks dropped, no fringe
    unstretch DECK SLIDE NAME [--box] -o OUT
                                undo a stretched picture: crop it to its frame,
                                or with --box resize the frame to the picture
    numbers BEFORE AFTER        every number in the original (text, tables,
                                charts, notes) that the new deck no longer has,
                                or has fewer times; "2%" and "2" differ

For taking reusable parts out of a deck (skills/pptx/guides/12-tach-thanh-phan.md):

    components DECK [--slide N]
                                what on a slide could become a component: groups,
                                tables, charts, pictures, and full-slide backgrounds
    ungroup DECK SLIDE [--all-groups] -o OUT
                                flatten groups into separate, correctly placed shapes
    component DECK SLIDE [--name N] [--exclude N] --freeze -o OUT.pptx
                                one-slide component, trimmed to the shapes, theme
                                frozen (optional); --png renders a preview
    place COMPONENT DECK --slide N -o OUT
                                put the component back onto a slide, pictures and
                                text still editable

For putting an existing deck into a theme (skills/pptx/guides/13-dua-bo-co-san-vao-theme.md):

    shell DECK [--strip m1,r1] [--background HEX] [-o OUT]
                                where the old shell lives: shapes of the master and
                                the layouts, and shapes at the same place on many
                                slides; --strip takes them off (animated ones stay)
    fit DECK --into X,Y,W,H [--slides 2-36] [--skip NAME] -o OUT
                                scale each slide's content as one block into the
                                area the theme leaves free; arrangement, ids and
                                animation kept; text never under the minimum
    compare BEFORE AFTER [--map MAP.json] [-o DIR]
                                one large picture per slide: old above, new below

For re-laying out one slide (skills/pptx/guides/14-dung-lai-bo-cuc-mot-slide.md):

    arrange DECK SLIDE LAYOUT.json -o OUT
                                place shapes by regions: rows and columns with
                                weights inside a box; pictures and blocks fit
                                their cell unstretched, words take its width
    seen FOLDER N=CODE ...      every picture glance and compare write carries a
                                look code in its bottom strip; this proves the
                                pictures were opened, not only measured

For rebuilding a whole deck (skills/pptx/guides/11-dung-lai-ca-bo.md):

    extract DECK [-o DIR]       the original pictures and videos as files (never
                                screenshots) and manifest.json: per slide its
                                text, notes, chart data, tables, media boxes,
                                transition and effect count
    check BEFORE AFTER [--map MAP.json]
                                pass/fail gates: transitions, effects pointing
                                to deleted shapes, videos kept and full-slide,
                                numbers, pictures cut tighter than the original;
                                with the map, keep slides keep their effects
                                and every slide keeps its source pictures

Plan (JSON), slide numbers start at 1:

    {"transitions": {"default": "none", "2": "morph", "7": "fade"},
     "clicks": {"3": [["Title"], ["Card A", "Card B"], ["Chart:wipe"]]}}

- transitions: "morph", "fade" or "none" for a slide (the transition *into* that
  slide). "default" covers every slide not listed. Slides not covered keep theirs.
- clicks: a list of clicks for a slide; each click lists the shapes that appear
  together, 120 ms apart. "Name:effect" picks fade (default), rise, wipe or zoom.
  Shapes not listed are visible when the slide opens.

A slide named in "clicks" gets its old animation replaced (an empty list only
removes it); every other slide keeps its animation. Shape names are the names in PowerPoint's Selection Pane.
"""
import argparse
import copy
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree as E
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.dml import MSO_FILL
from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.oxml.ns import qn
from pptx.util import Pt

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


# ------------------------------------------------------------ watching the deck move

MORPH_EFFECTS = {3954, 3955, 3956}  # ppEffectMorphByObject / ByWord / ByChar
STILL_S = 0.8     # nothing moved for this long: the step has settled
LONG_S = 2.0      # a click that moves longer than this tells a mechanism: show it on the way too
GIVE_UP_S = 10.0  # a loop or a video never settles


def _slide_box(width, height, bar, aspect):
    """Where the slide sits in the show window: centred beside the scrollbar, letterboxed."""
    room = width - bar
    w, h = (round(height * aspect), height) if room / height > aspect else (room, round(room / aspect))
    left, top = (room - w) // 2, (height - h) // 2
    return left, top, left + w, top + h


def _changed(a, b):
    """Share of the frame that differs between two pictures of the slide."""
    from PIL import ImageChops
    mask = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 12 else 0)
    return mask.histogram()[255] / (a.width * a.height)


def _read_step(before, frames):
    """What one click did, from the settled picture before it and the pictures taken after it.

    -> (kind, picture to show). kind: "dead" nothing moved; "passing" something moved and the slide
    ended as it began (a pulse, a path that returns), shown at its widest; "change" otherwise."""
    shares = [_changed(before, image) for _, image in frames]
    peak = max(range(len(shares)), key=shares.__getitem__)
    if shares[peak] < 0.0005:
        return "dead", frames[-1][1]
    if shares[-1] < 0.0005:
        return "passing", frames[peak][1]
    return "change", frames[-1][1]


def _strip(shots, path, cols=3):
    from PIL import Image, ImageDraw
    w, h = shots[0][1].size
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 8) + 8), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    for n, (label, image) in enumerate(shots):
        x, y = 8 + (n % cols) * (w + 8), 8 + (n // cols) * (h + 8)
        sheet.paste(image, (x, y))
        draw.rectangle([x, y, x + 12 + 6 * len(label), y + 20], fill=(0, 0, 0))
        draw.text((x + 6, y + 4), label, fill=(255, 255, 255))
    sheet.save(path, quality=88)


def watch(deck, out_dir, slides=None, cell=640):
    """Play the deck in PowerPoint's own slide show and photograph every state a viewer sees."""
    try:
        import win32com.client as win32
        import win32gui
        import win32ui
    except ImportError:
        sys.exit("watch needs PowerPoint on Windows (pywin32)")
    import ctypes
    import time
    from PIL import Image
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # real pixels, not a scaled-down copy
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    def frames_open(parent=None):
        found = []

        def each(handle, _):
            if win32gui.IsWindowVisible(handle):
                found.append((handle, win32gui.GetClassName(handle), win32gui.GetWindowText(handle)))
            return True
        try:
            win32gui.EnumChildWindows(parent, each, None) if parent else win32gui.EnumWindows(each, None)
        except win32gui.error:
            pass
        return found

    app = win32.Dispatch("PowerPoint.Application")
    was_open = app.Presentations.Count
    pres = app.Presentations.Open(str(Path(deck).resolve()), True, False, False)
    report, tools = [], []
    try:
        aspect = pres.PageSetup.SlideWidth / pres.PageSetup.SlideHeight
        settings = pres.SlideShowSettings
        settings.ShowType, settings.AdvanceMode, settings.ShowWithAnimation = 2, 1, True  # window, manual
        front = win32gui.GetForegroundWindow()
        before = {(h, title) for h, _, title in frames_open()}
        view = settings.Run().View
        new, waited = [], time.time()
        while not new and time.time() - waited < 15:  # a cold PowerPoint shows its window late
            time.sleep(0.5)
            # PowerPoint may reuse a frame it already had on screen: then only its title is new
            new = [h for h, name, title in frames_open() if (h, title) not in before and name == "PPTFrameClass"]
        if not new:
            sys.exit("watch: no slide-show window appeared (it needs a logged-in desktop session)")
        hwnd = new[0]
        # Pushed off the right edge so the person at the machine is not covered; PrintWindow still
        # reads it. 40 px stay on screen: fully off screen PowerPoint stops painting mid-effect now
        # and then (T073: 12 of 16 runs differed from the on-screen show; with the sliver, 0 of 16).
        metric = ctypes.windll.user32.GetSystemMetrics
        win32gui.SetWindowPos(hwnd, 0, metric(76) + metric(78) - 40, 0, 1500, int(1460 / aspect) + 60, 0x0014)
        try:
            win32gui.SetForegroundWindow(front)
        except win32gui.error:
            pass
        time.sleep(0.5)
        _, _, width, height = win32gui.GetClientRect(hwnd)
        bar = max([win32gui.GetClientRect(h)[2] for h, name, _ in frames_open(hwnd) if name == "NUIScrollbar"],
                  default=0)
        box = _slide_box(width, height, bar, aspect)
        size = (cell, round(cell / aspect))
        window_dc = win32gui.GetDC(hwnd)
        source = win32ui.CreateDCFromHandle(window_dc)
        memory = source.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(source, width, height)
        memory.SelectObject(bitmap)
        tools = [lambda: win32gui.DeleteObject(bitmap.GetHandle()), memory.DeleteDC, source.DeleteDC,
                 lambda: win32gui.ReleaseDC(hwnd, window_dc)]

        def grab():
            ctypes.windll.user32.PrintWindow(hwnd, memory.GetSafeHdc(), 3)  # client area, full content
            image = Image.frombuffer("RGB", (width, height), bitmap.GetBitmapBits(True), "raw", "BGRX", 0, 1)
            return image.crop(box).resize(size)

        def burst(action):
            """Do one step, then photograph until the slide has stood still. -> frames, seconds moving, settled"""
            start = time.time()
            action()
            frames, still, moved = [], None, 0.0
            while True:
                image, t = grab(), time.time() - start
                if still is None:
                    still = image
                elif _changed(image, still) >= 0.0005:
                    # ponytail: compared with the last still frame, so slow drift adds up; a pause
                    # longer than STILL_S inside one click is read as the end of that click
                    still, moved = image, t
                frames.append((t, image))
                if t - moved > STILL_S or t > GIVE_UP_S:
                    return frames, moved, t <= GIVE_UP_S
                time.sleep(0.03)

        count = pres.Slides.Count
        shown = [i for i in range(1, count + 1) if not pres.Slides(i).SlideShowTransition.Hidden]
        finished = None  # the slide whose every click has been played
        for number in [i for i in (slides or shown) if i in shown]:
            earlier = shown[shown.index(number) - 1] if shown.index(number) else None
            if earlier is None:
                frames, moved, _ = burst(lambda: view.GotoSlide(number))
            else:
                if finished != earlier:
                    burst(lambda: view.GotoSlide(earlier))
                    for _ in range(view.GetClickCount()):
                        burst(view.Next)
                frames, moved, _ = burst(view.Next)
            if view.Slide.SlideIndex != number:
                report.append({"slide": number, "error": f"the show went to slide {view.Slide.SlideIndex}"})
                finished = None
                continue
            entry = pres.Slides(number).SlideShowTransition
            row = {"slide": number, "enter": "cut", "clicks": []}
            shots = []
            def on_the_way(label, span):
                for part in (0.25, 0.5, 0.75):
                    _, image = min(frames, key=lambda f: abs(f[0] - span * part))
                    shots.append((f"{label} {part:.0%}", image))

            if earlier is not None and entry.EntryEffect in MORPH_EFFECTS:
                span = min(moved, entry.Duration) or entry.Duration
                row["enter"] = f"morph {span:.1f} s"
                on_the_way("morph", span)
            elif earlier is not None and entry.EntryEffect:
                row["enter"] = f"transition {min(moved, entry.Duration):.1f} s"
            still = frames[-1][1]
            shots.append(("open", still))
            for click in range(1, view.GetClickCount() + 1):
                frames, moved, settled = burst(view.Next)
                if view.Slide.SlideIndex != number:
                    break
                kind, picture = _read_step(still, frames)
                still = frames[-1][1]
                row["clicks"].append({"click": click, "kind": kind if settled else "moving",
                                      "seconds": round(moved, 1)})
                if moved > LONG_S:
                    on_the_way(f"click {click}", moved)
                shots.append((f"click {click}" + {"dead": " DEAD", "passing": " passing"}.get(kind, ""), picture))
            else:
                finished = number
            row["strip"] = str(out_dir / f"slide-{number:02d}.jpg")
            _strip(shots, row["strip"])
            report.append(row)
        try:
            view.Exit()
        except Exception:  # the show may already be gone
            pass
    finally:
        for release in tools:
            release()
        try:
            pres.Close()
        except Exception:  # a deck opened without a window closes with its show
            pass
        if not was_open:
            app.Quit()
    return report


def watch_lines(report):
    lines = []
    for row in report:
        if "error" in row:
            lines.append(f"slide {row['slide']}: could not watch, {row['error']}")
            continue
        lines.append(f"slide {row['slide']}: enters by {row['enter']}, {len(row['clicks'])} clicks")
        for c in row["clicks"]:
            what = {"dead": "NOTHING CHANGES (a wasted click)",
                    "passing": f"something moves for {c['seconds']} s and the slide ends as it was",
                    "moving": f"still moving after {GIVE_UP_S:.0f} s (a loop or a video)",
                    "change": f"{c['seconds']} s"}[c["kind"]]
            lines.append(f"  click {c['click']}: {what}")
        lines.append(f"  {row['strip']}")
    return lines


# ------------------------------------------------------------ what a viewer sees at once

PICTURE, GROUP, PLACEHOLDER = 13, 6, 14          # MsoShapeType
SOLID = {13: "picture", 11: "picture", 3: "chart", 19: "table", 16: "video"}
MIN_PT = 12   # guide 4: nothing below 12 pt on a slide 7.5 in tall
UNREADABLE = 1.6   # contrast ratio; white on ivory is 1.1, mid grey on white is 2.3
BUSY = 28          # spread of the picture behind a title, 0-255; a soft glow is under 10


def _box(row):
    left, top, width, height = row
    return left, top, left + width, top + height


def _area(row):
    return max(0.0, row[2]) * max(0.0, row[3])


def _shared(a, b):
    """Area two boxes (left, top, width, height) have in common."""
    al, at, ar, ab = _box(a)
    bl, bt, br, bb = _box(b)
    w, h = min(ar, br) - max(al, bl), min(ab, bb) - max(at, bt)
    return w * h if w > 0 and h > 0 else 0.0


def _contrast(a, b):
    def lum(rgb):
        r, g, b_ = ((v / 255 / 12.92) if v / 255 <= 0.03928 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b_
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _behind(image, box, ink, k):
    """What the slide looks like behind a piece of text: (colour, spread). The half of the pixels least
    like the ink is the background; its median is the colour, its spread says plain or busy."""
    left, top, right, bottom = _box(box)
    edges = (max(0, round((left - 3) * k)), max(0, round((top - 3) * k)),
             min(image.width, round((right + 3) * k)), min(image.height, round((bottom + 3) * k)))
    if edges[2] - edges[0] < 4 or edges[3] - edges[1] < 4:   # off the slide, or a speck
        return None, 0.0
    crop = image.crop(edges)
    crop = crop.resize((min(crop.width, 96), min(crop.height, 48)))
    px = sorted(crop.get_flattened_data() if hasattr(crop, "get_flattened_data") else crop.getdata(),
                key=lambda p: -sum(abs(p[j] - ink[j]) for j in range(3)))
    far = px[:max(1, len(px) // 2)]
    colour = tuple(sorted(p[j] for p in far)[len(far) // 2] for j in range(3))
    grey = sorted(0.3 * p[0] + 0.59 * p[1] + 0.11 * p[2] for p in far)
    return colour, grey[int(len(grey) * 0.9)] - grey[int(len(grey) * 0.1)]


def _slots(slides, size):
    """(slide, id) of every slide shape that sits at the same place on many slides: the title slot, the
    step bar, the logo; and what at least 70% of the slides have: [(name, box, slides that have it)].
    `slides` is the list from _facts."""
    tol = (0.04 * size[0], 0.04 * size[1])
    groups = []  # [first box, type, [(slide, id)]]
    for s in slides:
        for r in s["shapes"]:
            if r["layer"] != "slide" or r["depth"]:
                continue
            for g in groups:
                if g[1] == r["type"] and all(abs(a - b) <= tol[j % 2] for j, (a, b) in enumerate(zip(g[0], r["box"]))):
                    g[2].append((s["slide"], r["id"]))
                    break
            else:   # the label is kept for what a viewer would miss: words or a picture
                label = r["name"] if r.get("text") or SOLID.get(r["type"]) == "picture" else None
                groups.append([r["box"], r["type"], [(s["slide"], r["id"])], label])
    need = max(3, 0.3 * len(slides))
    keys = {key for _, _, members, _ in groups if len({m[0] for m in members}) >= need for key in members}
    usual = [(label, box, {m[0] for m in members}) for box, _, members, label in groups
             if label and len({m[0] for m in members}) >= 0.7 * len(slides)]
    return keys, usual


def _glance_slide(s, size, slots, moving, image, chart_inks=None):
    """Faults on one slide: [(kind, sentence, [boxes])], and [(shape id, text colour)] of the text nobody
    can read. Pure: rows from _facts, a PIL image of the slide."""
    width, height = size
    k = image.width / width
    floor = MIN_PT * height / 540
    rows = [r for r in s["shapes"] if r["visible"] and r["type"] != GROUP]
    still = [r for r in rows if not (r["layer"] == "slide" and r["id"] in moving)]
    texts = [r for r in still if r.get("text") and _area(r["text"]["box"]) > 0]
    faults, unreadable = [], []

    def name(r):
        return repr(r["text"]["sample"]) if r.get("text") else repr(r["name"])

    for n, a in enumerate(texts):
        for b in texts[n + 1:]:
            both = _shared(a["text"]["box"], b["text"]["box"])
            if both >= 0.25 * min(_area(a["text"]["box"]), _area(b["text"]["box"])):
                faults.append(("text on text", f"{name(a)} and {name(b)} are printed over each other",
                               [a["text"]["box"], b["text"]["box"]]))
    for r in texts:
        runs = Counter()
        for chars, _, rgb in r["text"]["runs"]:
            runs[rgb] += chars
        if not runs:
            continue
        lost = []
        for rgb, chars in runs.most_common():
            if chars < 3 and lost:
                continue
            ink = (rgb & 255, rgb >> 8 & 255, rgb >> 16 & 255)   # PowerPoint gives BGR
            colour, spread = _behind(image, r["text"]["box"], ink, k)
            if colour is not None and _contrast(ink, colour) < UNREADABLE:
                lost.append(("%02X%02X%02X" % ink, "%02X%02X%02X" % colour))
        rgb = runs.most_common(1)[0][0]
        ink = (rgb & 255, rgb >> 8 & 255, rgb >> 16 & 255)
        colour, spread = _behind(image, r["text"]["box"], ink, k)
        if colour is None:
            continue
        if lost:
            faults.append(("cannot read", f"{name(r)}: text {lost[0][0]} on {lost[0][1]}", [r["text"]["box"]]))
            if r["layer"] == "slide":
                unreadable += [(r["id"], was) for was, _ in lost]
        elif r["layer"] == "slide" and (s["slide"], r["id"]) in slots and spread > BUSY:
            under = [o for o in still if o is not r and o["type"] in SOLID and _area(o["box"]) < 0.5 * width * height
                     and not (o["layer"] == "slide" and (s["slide"], o["id"]) in slots)
                     and _shared(r["text"]["box"], o["box"]) >= 0.15 * _area(r["text"]["box"])]
            if under:
                faults.append(("title on content", f"the title {name(r)} lies across the {SOLID[under[0]['type']]} "
                               f"{under[0]['name']!r}", [r["text"]["box"], under[0]["box"]]))
        left, top, right, bottom = _box(r["text"]["box"])
        if left < -2 or top < -2 or right > width + 2 or bottom > height + 2:
            faults.append(("text off the slide", f"{name(r)} runs past the edge of the slide", [r["text"]["box"]]))
    for r in still:
        if r["layer"] != "slide" or SOLID.get(r["type"]) != "chart":
            continue
        for was in sorted((chart_inks or {}).get(r["id"], ())):
            ink = tuple(int(was[j:j + 2], 16) for j in (0, 2, 4))
            colour, _ = _behind(image, r["box"], ink, k)
            if colour is not None and _contrast(ink, colour) < UNREADABLE:
                faults.append(("cannot read", f"the chart {r['name']!r}: its text {was} on {'%02X%02X%02X' % colour}",
                               [r["box"]]))
                unreadable.append((r["id"], was))
    shell_marks = [o for o in still if o["layer"] == "slide" and (s["slide"], o["id"]) in slots
                   and (o.get("text") or (SOLID.get(o["type"]) == "picture" and _area(o["box"]) < 0.03 * width * height))]
    for r in still:
        if r["layer"] != "slide" or r["type"] not in SOLID or (s["slide"], r["id"]) in slots \
                or r["name"].startswith("!!")                 or (SOLID[r["type"]] in ("picture", "video") and _area(r["box"]) >= 0.5 * width * height):
            continue   # a full-slide photo or video is a ground, not content that strayed
        under = [o for o in shell_marks if _shared(r["box"], o["box"]) >= 0.3 * _area(o["box"])]
        if under:
            faults.append(("content under the shell", f"the {SOLID[r['type']]} {r['name']!r} runs under "
                           f"{under[0]['name']!r}: content belongs in the area the theme leaves free",
                           [r["box"], under[0]["box"]]))
        elif SOLID[r["type"]] in ("chart", "table"):
            left, top, right, bottom = _box(r["box"])
            if left < -0.02 * width or top < -0.02 * height or right > 1.02 * width or bottom > 1.02 * height:
                faults.append((f"{SOLID[r['type']]} off the slide", f"{r['name']!r} is larger than the slide shows",
                               [r["box"]]))
    for r in texts:
        words, own = r["text"]["box"], r["box"]
        if _area(words) - _shared(words, own) < 0.15 * _area(words):
            continue   # the words stay inside their own box
        left, top = max(words[0], own[0]), max(words[1], own[1])
        inside = [left, top, max(0.0, min(_box(words)[2], _box(own)[2]) - left),
                  max(0.0, min(_box(words)[3], _box(own)[3]) - top)]
        for o in still:
            if o is r or not (o.get("text") or o["type"] in SOLID) or _area(o["box"]) >= 0.5 * width * height \
                    or o["name"].startswith("!!"):
                continue
            if _shared(words, o["box"]) - _shared(inside, o["box"]) >= 0.05 * _area(words):
                faults.append(("text spills", f"{name(r)} is too long for its box and runs onto {o['name']!r}",
                               [words, o["box"]]))
                break
    order = {id(r): n for n, r in enumerate(s["shapes"])}   # PowerPoint lists shapes from the back to the front
    for r in texts:
        if r["layer"] != "slide":
            continue
        over = [o for o in still if o["layer"] == "slide" and o["type"] in SOLID and order[id(o)] > order[id(r)]
                and _shared(r["text"]["box"], o["box"]) >= 0.3 * _area(r["text"]["box"])]
        if over:
            faults.append(("text hidden", f"the {SOLID[over[0]['type']]} {over[0]['name']!r} covers {name(r)}",
                           [r["text"]["box"], over[0]["box"]]))
    pictures = [r for r in still if SOLID.get(r["type"]) == "picture" and _area(r["box"]) < 0.5 * width * height]
    for n, a in enumerate(pictures):
        for b in pictures[n + 1:]:
            if a["layer"] == b["layer"] == "slide" and _shared(a["box"], b["box"]) >= 0.9 * max(_area(a["box"]), _area(b["box"])) > 0:
                faults.append(("same picture twice", f"{a['name']!r} and {b['name']!r} are in the same place: "
                               "was the shell applied twice?", [a["box"]]))
    for a in (r for r in pictures if r["layer"] == "slide"):
        for b in (r for r in pictures if r["layer"] != "slide"):
            small, big = sorted((_area(a["box"]), _area(b["box"])))
            if small and big / small <= 4 and _shared(a["box"], b["box"]) >= 0.3 * small:
                faults.append(("picture on the master's picture",
                               f"{a['name']!r} sits on {b['name']!r} of the slide {b['layer']}: an old logo under "
                               "the new one? Old shell lives in the master; change it there (guide 13)",
                               [a["box"], b["box"]]))
    chars = tiny = 0
    smallest = []
    for r in texts:
        if _box(r["text"]["box"])[1] > 0.92 * height or (r["layer"] == "slide" and (s["slide"], r["id"]) in slots):
            continue   # footers, sources and the step bar may be small
        for count, pt, _ in r["text"]["runs"]:
            chars += count
            if pt < floor:
                tiny += count
                smallest.append((pt, r))
    if chars and tiny / chars > 0.2:
        smallest.sort(key=lambda item: item[0])
        faults.append(("tiny text", f"{tiny / chars:.0%} of the text is under {floor:g} pt (smallest "
                       f"{smallest[0][0]:g} pt, e.g. {name(smallest[0][1])}): nobody in the room reads it",
                       [r["text"]["box"] for _, r in smallest[:6]]))
    return faults, unreadable


def _facts(deck, out_dir, slides=None, width=1600):
    """PowerPoint's own account of a deck: for every shape of every slide (and of its layout and master)
    where it is, where its text really is, the text's size and colour as drawn; plus a PNG of each slide."""
    try:
        import win32com.client as win32
    except ImportError:
        sys.exit("this command needs PowerPoint on Windows (pywin32)")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    def collect(shape, rows, layer, depth=0):
        try:
            kind = int(shape.Type)
            row = {"id": int(shape.Id), "name": str(shape.Name), "type": kind, "layer": layer, "depth": depth,
                   "box": [round(float(v), 1) for v in (shape.Left, shape.Top, shape.Width, shape.Height)],
                   "visible": bool(shape.Visible)}
        except Exception:  # noqa: BLE001  (a shape PowerPoint will not describe)
            return
        rows.append(row)
        if kind == GROUP:
            for n in range(1, shape.GroupItems.Count + 1):
                collect(shape.GroupItems(n), rows, layer, depth + 1)
            return
        try:
            if kind == PLACEHOLDER and int(shape.PlaceholderFormat.ContainedType) in SOLID:
                row["type"] = int(shape.PlaceholderFormat.ContainedType)
            if shape.HasTextFrame and shape.TextFrame.HasText:
                whole = shape.TextFrame.TextRange
                text = str(whole.Text).strip()
                runs = []
                for n in range(1, min(whole.Runs().Count, 12) + 1):
                    run = whole.Runs(n)
                    if str(run.Text).strip():
                        runs.append([len(str(run.Text).strip()), round(float(run.Font.Size), 1), int(run.Font.Color.RGB)])
                if len(text) >= 2 and runs:
                    inked = whole.TrimText()   # without the empty lines at the end of the box
                    row["text"] = {"sample": text.replace("\r", " ").replace("\x0b", " ")[:32], "runs": runs,
                                   "box": [round(float(v), 1) for v in (inked.BoundLeft, inked.BoundTop,
                                                                        inked.BoundWidth, inked.BoundHeight)]}
        except Exception:  # noqa: BLE001  (charts, OLE objects: no text frame to read)
            pass

    app = win32.Dispatch("PowerPoint.Application")
    was_open = app.Presentations.Count
    pres = app.Presentations.Open(str(Path(deck).resolve()), True, False, False)
    try:
        size = (float(pres.PageSetup.SlideWidth), float(pres.PageSetup.SlideHeight))
        data = {"size": size, "slides": []}
        for number in range(1, pres.Slides.Count + 1):
            if slides and number not in slides:
                continue
            slide = pres.Slides(number)
            rows = []
            for n in range(1, slide.Shapes.Count + 1):
                collect(slide.Shapes(n), rows, "slide")
            layers = [("layout", slide.CustomLayout.Shapes)]
            if slide.DisplayMasterShapes and slide.CustomLayout.DisplayMasterShapes:
                layers.append(("master", slide.Master.Shapes))
            for layer, shapes in layers:
                for n in range(1, shapes.Count + 1):
                    if int(shapes(n).Type) != PLACEHOLDER:   # an empty placeholder is not drawn
                        collect(shapes(n), rows, layer)
            png = (out_dir / f"slide-{number:02d}.png").resolve()
            slide.Export(str(png), "PNG", width, round(width * size[1] / size[0]))
            data["slides"].append({"slide": number, "png": str(png), "shapes": rows})
    finally:
        pres.Close()
        if not was_open:
            app.Quit()
    return data


def _moving(prs, data):
    """{slide: ids of the shapes an animation moves, with the children of animated groups}."""
    out = {}
    for s in data["slides"]:
        ids = {int(t.get("spid")) for t in prs.slides[s["slide"] - 1]._element.iter(qn("p:spTgt")) if t.get("spid")}
        inside = False
        for r in s["shapes"]:
            if r["layer"] != "slide":
                continue
            if not r["depth"]:
                inside = r["id"] in ids
            elif inside:
                ids.add(r["id"])
        out[s["slide"]] = ids
    return out


def _chart_inks(space, ink=None, failing=()):
    """Hex colours a chart writes its titles, axes and legend in ("FFFFFF" for the theme's light colour;
    data labels are left out). With `ink`, the
    colours in `failing` are replaced by it; returns how many."""
    found, changed = set(), 0
    for holder in space.iter(qn("c:txPr"), qn("c:rich")):
        if any(E.QName(up).localname in ("dLbls", "dLbl") for up in holder.iterancestors()):
            continue   # a label may sit inside its bar: white on a dark bar is fine, and unknowable here
        for fill in holder.iter(qn("a:solidFill")):
            if not len(fill):
                continue
            node = fill[0]
            kind = E.QName(node).localname
            was = node.get("val", "").upper() if kind == "srgbClr" else \
                "FFFFFF" if kind == "schemeClr" and node.get("val") in ("bg1", "lt1") else None
            if was is None:
                continue
            found.add(was)
            if ink and was in failing:
                fill.remove(node)
                E.SubElement(fill, qn("a:srgbClr"), val=ink.upper())
                changed += 1
    return changed if ink else found


def glance(deck, out_dir, slides=None, data=None):
    """The faults a person sees in the first second, slide by slide, from PowerPoint's own drawing.
    -> [{"slide", "png", "faults": [(kind, sentence)], "marked": png with the faults boxed}]"""
    from PIL import Image, ImageDraw
    data = data or _facts(deck, out_dir, slides)
    prs = Presentation(deck)
    moving = _moving(prs, data)
    slots, usual = _slots(data["slides"], data["size"])
    numbers = [s["slide"] for s in data["slides"]]
    report, codes = [], {}
    for s in data["slides"]:
        image = Image.open(s["png"]).convert("RGB")
        if image.height == round(image.width * data["size"][1] / data["size"][0]):   # not stamped yet
            stamped, codes[Path(s["png"]).name] = _stamp(image, f"slide {s['slide']}")
            stamped.save(s["png"])
        else:
            image = image.crop((0, 0, image.width, image.height - 34))
        inks = {}
        for shape in _walk(prs.slides[s["slide"] - 1].shapes):
            if getattr(shape, "has_chart", False) and shape.has_chart:
                inks[shape.shape_id] = _chart_inks(shape.chart._chartSpace)
        faults, unreadable = _glance_slide(s, data["size"], slots, moving[s["slide"]], image, inks)
        if s["slide"] not in (numbers[0], numbers[-1]):   # a cover and a closing slide may differ
            gone = [(label, box) for label, box, on in usual if s["slide"] not in on]
            if gone:
                faults.append(("missing", "most slides have " + ", ".join(repr(label) for label, _ in gone)
                               + " here; this one does not", [box for _, box in gone]))
        row = {"slide": s["slide"], "png": s["png"], "faults": [(kind, text) for kind, text, _ in faults],
               "unreadable": unreadable}
        if faults:
            k = image.width / data["size"][0]
            draw = ImageDraw.Draw(image)
            for n, (kind, _, boxes) in enumerate(faults, 1):
                for box in boxes:
                    left, top, right, bottom = (round(v * k) for v in _box(box))
                    draw.rectangle([left - 3, top - 3, right + 3, bottom + 3], outline=(230, 0, 40), width=4)
                    draw.rectangle([left - 3, top - 25, left + 22, top - 3], fill=(230, 0, 40))
                    draw.text((left + 3, top - 22), str(n), fill=(255, 255, 255))
            row["marked"] = str(Path(s["png"]).with_name(f"faults-{s['slide']:02d}.png"))
            image.save(row["marked"])
        report.append(row)
    if codes:
        _keep_codes(Path(data["slides"][0]["png"]).parent, codes)
    return report


def reink(deck, output, report, ink):
    """Give the text `glance` could not read a colour that can be read (the theme's ink). Only runs in the
    failing colour change; a run with a colour of its own (a red figure) keeps it. -> runs changed"""
    prs = Presentation(deck)
    changed = 0
    for row in report:
        failing = {}
        for shape_id, was in row.get("unreadable", []):
            failing.setdefault(shape_id, set()).add(was)
        if not failing:
            continue
        for shape in _walk(prs.slides[row["slide"] - 1].shapes):
            if shape.shape_id in failing and getattr(shape, "has_chart", False) and shape.has_chart:
                changed += _chart_inks(shape.chart._chartSpace, ink, failing[shape.shape_id])
        for node in prs.slides[row["slide"] - 1]._element.iter(qn("p:cNvPr")):
            if not node.get("id", "").isdigit() or int(node.get("id")) not in failing:
                continue
            was = failing[int(node.get("id"))]
            for run in node.getparent().getparent().iter(qn("a:r")):
                pr = run.find(qn("a:rPr"))
                if pr is None:
                    pr = E.Element(qn("a:rPr"))
                    run.insert(0, pr)
                own = pr.find("a:solidFill/a:srgbClr", NS)
                if own is not None and own.get("val", "").upper() not in was:
                    continue
                for old in [c for c in pr if E.QName(c).localname in ("solidFill", "gradFill", "noFill", "pattFill")]:
                    pr.remove(old)
                fill = E.Element(qn("a:solidFill"))
                E.SubElement(fill, qn("a:srgbClr"), val=ink.upper())
                pr.insert(1 if len(pr) and E.QName(pr[0]).localname == "ln" else 0, fill)
                changed += 1
    prs.save(output)
    return changed


def glance_lines(report):
    lines, bad = [], 0
    for row in report:
        if not row["faults"]:
            continue
        bad += 1
        lines.append(f"slide {row['slide']}: {len(row['faults'])} fault(s), boxed in {row['marked']}")
        lines += [f"  {n}. {kind}: {text}" for n, (kind, text) in enumerate(row["faults"], 1)]
    folder = Path(report[0]["png"]).parent if report else ""
    if bad:
        lines.append(f"{bad} of {len(report)} slides have faults a viewer sees at once. Fix each one in the builder, "
                     "build again, run glance again. Do not show this deck to anyone yet.")
    else:
        lines.append(f"no fault found on {len(report)} slides by measuring. That is not yet 'looked at': open every "
                     f"slide-NN.png in {folder} at full size before you show the deck (guide 8).")
    lines.append(f"Each slide-NN.png has a three-letter look code in the strip under the slide. After you have opened "
                 f"the pictures: python scripts/pptx_tools.py seen \"{folder}\" 1=CODE 2=CODE ...  and put its answer "
                 "in your handoff (guide 14).")
    return lines


# ------------------------------------------------------------ decks made by others

C_NS = "http://schemas.openxmlformats.org/drawingml/2006/chart"
MIN_BODY_PT = 18  # guide 4: content text, on a slide 7.5 in tall
REF_HEIGHT = 6858000  # 7.5 in
NAMES_BY_PRESET = {}
for _name, (_cls, _pid, _sub, _ms) in anim.PRESETS.items():
    NAMES_BY_PRESET.setdefault((_cls, str(_pid)), _name.removeprefix("ppt:"))
CALM = {"appear", "fade", "float-in", "zoom", "wipe", "wipe-up", "wipe-down", "wipe-left", "wipe-right",
        "rise-up", "dim", "disappear", "fade-out", "path"}


def _floor(prs):
    """Guide 4's 18 pt, scaled to this slide's height: a 20 x 11.25 in slide is shown no larger than a
    13.33 x 7.5 in one, so its text needs 27 pt to read the same."""
    return round(MIN_BODY_PT * prs.slide_height / REF_HEIGHT, 1)


def _walk(shapes):
    for s in shapes:
        yield s
        if s.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from _walk(s.shapes)


def _plot_kinds(chart):
    area = chart._chartSpace.find(f".//{{{C_NS}}}plotArea")
    return [E.QName(n).localname for n in area if E.QName(n).localname.endswith("Chart")]


def _stretch(pic):
    """Frame aspect / visible-photo aspect; 1.0 means not stretched."""
    iw, ih = pic.image.size
    vis_w = iw * (1 - pic.crop_left - pic.crop_right)
    vis_h = ih * (1 - pic.crop_top - pic.crop_bottom)
    return (pic.width / pic.height) / (vis_w / vis_h)


def _slide_effects(slide):
    names, clicks = Counter(), 0
    for ctn in slide._element.iter(qn("p:cTn")):
        cls = ctn.get("presetClass")
        if cls:
            pid = ctn.get("presetID")
            names[f"{cls}:{NAMES_BY_PRESET.get((cls, pid), 'id' + str(pid))}"] += 1
        if ctn.get("nodeType") == "clickEffect":
            clicks += 1
    return names, clicks


def _transition(slide):
    for node in slide._element.iter(qn("p:transition")):
        if not len(node):
            return "cut"
        kind = E.QName(node[0]).localname
        return node[0].get("prst", kind) if kind == "prstTrans" else kind  # p15 names: peelOff, curtains…
    return None


def _theme_faces(slide):
    """(heading, body) latin fonts of the theme behind this slide."""
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    root = E.fromstring(slide.slide_layout.slide_master.part.part_related_by(RT.THEME).blob)
    return tuple(root.find(f".//a:{tag}/a:latin", NS).get("typeface") for tag in ("majorFont", "minorFont"))


def _is_title(shape):
    return shape.is_placeholder and shape.placeholder_format.type in (PP_PLACEHOLDER.TITLE,
                                                                      PP_PLACEHOLDER.CENTER_TITLE)


def _fill(fill):
    try:
        return str(fill.fore_color.rgb) if fill.type == MSO_FILL.SOLID else None
    except (AttributeError, TypeError):  # theme colour
        return None


def _opening(slide):
    """Top-level shapes a viewer sees when the slide opens, lines and empty boxes left out."""
    entering = {t.get("spid") for ctn in slide._element.iter(qn("p:cTn")) if ctn.get("presetClass") == "entr"
                for t in ctn.iter(qn("p:spTgt"))}
    seen = []
    for s in slide.shapes:
        if str(s.shape_id) in entering or s.shape_type in (MSO_SHAPE_TYPE.LINE, None):
            continue
        has_text = s.has_text_frame and s.text_frame.text.strip()
        if has_text or s.shape_type in (MSO_SHAPE_TYPE.PICTURE, MSO_SHAPE_TYPE.GROUP) or \
                getattr(s, "has_chart", False) or getattr(s, "has_table", False):
            seen.append(s)
    return seen


def inventory(deck):
    """Plain-text report: what the deck uses, and where it breaks the guides."""
    prs = Presentation(deck)
    sw, sh = prs.slide_width, prs.slide_height
    floor = _floor(prs)
    fonts, sizes, colours, fills = Counter(), Counter(), Counter(), Counter()
    on_slides, transitions = Counter(), Counter()
    lines = []
    for i, slide in enumerate(prs.slides, 1):
        words, flags, small = 0, [], {}
        on_slides.update(_key_numbers(" ".join(n.text or "" for n in slide._element.iter(qn("a:t")))))
        head, body = _theme_faces(slide)
        bg = _fill(slide.background.fill) if slide._element.find(".//p:bg", NS) is not None else None
        if bg:
            fills[f"{bg} (background)"] += 1
        for shape in _walk(slide.shapes):
            if shape.shape_type not in (MSO_SHAPE_TYPE.PICTURE, MSO_SHAPE_TYPE.GROUP, MSO_SHAPE_TYPE.LINE) \
                    and not getattr(shape, "has_chart", False) and not getattr(shape, "has_table", False):
                colour = _fill(getattr(shape, "fill", None))  # a video has no fill
                if colour:
                    fills[colour] += 1
            frames = [shape.text_frame] if shape.has_text_frame else []
            if getattr(shape, "has_table", False):
                frames += [cell.text_frame for row in shape.table.rows for cell in row.cells]
            for frame in frames:
                for para in frame.paragraphs:
                    for run in para.runs:
                        words += len(run.text.split())
                        face = run.font.name
                        if face in (None, "+mn-lt", "+mj-lt"):
                            face = head if face == "+mj-lt" or (face is None and _is_title(shape)) else body
                        fonts[face] += 1
                        if run.font.size:
                            sizes[run.font.size.pt] += 1
                            if run.font.size.pt < floor and run.text.strip():
                                small[shape.name] = min(small.get(shape.name, 99), run.font.size.pt)
                        try:
                            colours[str(run.font.color.rgb)] += 1
                        except AttributeError:  # theme colour or none
                            pass
            if getattr(shape, "has_chart", False):
                kinds = _plot_kinds(shape.chart)
                hint = "  <- 3D: rechart" if any("3D" in k for k in kinds) else ""
                flags.append(f"chart {shape.name!r}: {', '.join(kinds)}{hint}")
            if getattr(shape, "has_table", False):
                tb = shape.table
                flags.append(f"table {shape.name!r}: {len(tb.rows)} rows x {len(tb.columns)} cols")
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                r = _stretch(shape)
                if abs(r - 1) > 0.03:
                    flags.append(f"picture {shape.name!r} stretched {abs(r - 1):.0%} "
                                 f"{'wider' if r > 1 else 'taller'} than the photo  <- unstretch")
        for shape in slide.shapes:
            if shape.width is None:
                continue
            out = max(-shape.left, -shape.top, shape.left + shape.width - sw, shape.top + shape.height - sh)
            if out > 0:
                flags.append(f"{shape.name!r} runs {out / 914400:.2f} in off the slide")
        if len(small) > 3:  # one line, or a small-type deck floods the report
            flags.append(f"text under {floor:g} pt in {len(small)} shapes (smallest {min(small.values()):g} pt), "
                         f"e.g. {', '.join(repr(n) for n in list(small)[:3])}: fine for sources and captions only")
        else:
            flags += [f"text under {floor:g} pt in {n!r} ({pt:g} pt): fine for a source or caption only"
                      for n, pt in small.items()]
        effects, clicks = _slide_effects(slide)
        if clicks and len(_opening(slide)) <= 1:
            flags.append("opens with only the title visible: show the frame (labels, axes) at the start, "
                         "let clicks add data and conclusions")
        ids = {n.get("id") for n in slide._element.iter(qn("p:cNvPr"))}
        lost = {t.get("spid") for t in slide._element.iter(qn("p:spTgt"))} - ids
        if lost:
            flags.append(f"effects point to {len(lost)} shapes that are gone: PowerPoint repairs the file and "
                         "drops them. Delete a shape and its effects together, or keep the shape")
        loud = sorted({n for n in effects if n.split(":", 1)[1] not in CALM})
        kind = _transition(slide) or "none"
        transitions[kind] += 1
        lines.append(f"slide {i}: {len(slide.shapes)} shapes, {words} words, transition "
                     f"{kind}, {clicks} clicks, {sum(effects.values())} effects")
        if loud:
            lines.append("  ! decorative effects: " + ", ".join(loud))
        if kind not in ("none", "cut", "fade", "morph"):
            lines.append(f"  ! old-style transition {kind!r}: guide 6 uses fade, Morph or none")
        lines += ["  ! " + f for f in flags]
    size_note = "" if floor == MIN_BODY_PT else f" (text floor {floor:g} pt at this height, guide 4)"
    top = [f"deck: {len(prs.slides)} slides, {sw / 914400:.2f} x {sh / 914400:.2f} in{size_note}",
           f"fonts ({len(fonts)}): " + ", ".join(f"{k} x{v}" for k, v in fonts.most_common()),
           f"sizes ({len(sizes)}; guide 4 wants 3-6): " + ", ".join(f"{k:g}" for k in sorted(sizes)),
           f"text colours ({len(colours)}): " + ", ".join(f"{k} x{v}" for k, v in colours.most_common(8)),
           f"fills ({len(fills)}): " + ", ".join(f"{k} x{v}" for k, v in fills.most_common(8)),
           "transitions: " + ", ".join(f"{k} x{v}" for k, v in transitions.most_common())]
    many = [f"{n} on {c} slides" for n, c in on_slides.most_common() if c >= 4]
    if many:
        top.append("numbers on 4+ slides (guide 3: each key number has one home slide): " + ", ".join(many[:6]))
    return "\n".join(top + lines)


def _key_numbers(text):
    """Numbers worth tracking across slides: >= 100, decimals or percentages; not years or step numbers.

    A comma or dot followed by three digits is a thousands separator (``1.200`` and ``1,200``), not a
    decimal point. This matters in Vietnamese QCC data: a false ``1.2`` can hide a missing ``1,200``.
    """
    keys = set()
    for found in NUMBER.finditer(text):
        m, pct = found.groups()
        if found.start() and text[found.start() - 1].isalpha():  # part of a code: H422, T35
            continue
        if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", m):
            v = re.sub(r"[.,]", "", m)
        else:
            v = m.replace(",", ".")
        try:
            f = float(v)
        except ValueError:
            continue
        if pct or "." in v or (f >= 100 and not (1900 <= f <= 2100 and len(m) == 4)):
            keys.add(f"{f:g}" + ("%" if pct else ""))
    return keys


def _top_shapes(slide, names):
    by_name = {}
    for s in slide.shapes:
        by_name.setdefault(s.name, []).append(s)
    out = []
    for n in names:
        found = by_name.get(n, [])
        if len(found) != 1:
            problem = "no shape" if not found else f"{len(found)} shapes"
            raise ValueError(f"{problem} named {n!r} at the top level; rename first. Shapes: {sorted(by_name)}")
        out.append(found[0])
    return out


def _inherited_sz(prs, slide, shape_el, lvl):
    """Size a run gets when it sets none. ponytail: non-placeholder text only (own list
    style, master otherStyle, presentation defaults, 18 pt); placeholders are refused."""
    tag = f"a:lvl{lvl + 1}pPr"
    for root, path in ((shape_el, f".//a:lstStyle/{tag}/a:defRPr"),
                       (slide.slide_layout.slide_master._element, f"p:txStyles/p:otherStyle/{tag}/a:defRPr"),
                       (prs._element, f"p:defaultTextStyle/{tag}/a:defRPr")):
        node = root.find(path, NS)
        if node is not None and node.get("sz"):
            return int(node.get("sz"))
    return 1800


def _scale_text(prs, slide, el, factor, floor=None):
    """Give every run an explicit size, then scale all sizes. With `floor` (pt) no text is shrunk below
    it, and text already under it is left as it is. Returns smallest pt shown."""
    for para in el.iter(qn("a:p")):
        ppr = para.find(qn("a:pPr"))
        lvl = int(ppr.get("lvl", 0)) if ppr is not None else 0
        holders = []
        for run in para:
            if E.QName(run).localname in ("r", "fld"):
                rpr = run.find(qn("a:rPr"))
                if rpr is None:
                    rpr = E.Element(qn("a:rPr"))
                    run.insert(0, rpr)
                holders.append(rpr)
        end = para.find(qn("a:endParaRPr"))
        if end is None and not holders:
            end = E.SubElement(para, qn("a:endParaRPr"))
        for h in holders + ([end] if end is not None else []):
            if not h.get("sz"):
                h.set("sz", str(_inherited_sz(prs, slide, el, lvl)))
    smallest = None
    for node in el.iter(qn("a:rPr"), qn("a:defRPr"), qn("a:endParaRPr")):
        if node.get("sz"):
            was = int(node.get("sz"))
            node.set("sz", str(max(100, round(was * factor), min(was, round(floor * 100)) if floor else 0)))
            if E.QName(node).localname == "rPr" and (node.getparent().findtext(qn("a:t")) or "").strip():
                pt = int(node.get("sz")) / 100
                smallest = pt if smallest is None else min(smallest, pt)
    for node in el.iter(qn("a:spcPts")):
        node.set("val", str(round(int(node.get("val")) * factor)))
    return smallest


def scale(deck, slide_no, names, factor, output, at=None):
    """Scale top-level shapes as one block about its top-left corner, then move the
    block's top-left corner to `at` (inches) if given.

    Shapes keep their ids, so their animation keeps working. Loose shapes that
    each have an entrance must stay loose: PowerPoint cannot animate a shape
    inside a group. Returns the smallest text size left, in pt.
    """
    if not 0.1 <= factor <= 5:
        raise ValueError("--by must be between 0.1 and 5")
    prs = Presentation(deck)
    slide = prs.slides[slide_no - 1]
    targets = _top_shapes(slide, names)
    if any(s.is_placeholder for s in targets):
        raise ValueError("a placeholder inherits its text size from the layout. Leave it out of the block, "
                         "or copy its text to a text box (same place, same words) and scale that")
    low = _scale_block(prs, slide, targets, factor, at and (round(at[0] * 914400), round(at[1] * 914400)))
    prs.save(output)
    return low


def _scale_block(prs, slide, targets, factor, at=None, floor=None, grow_text=True):
    """Scale shapes of one slide as one block about its top-left corner, then move that corner to `at`
    (EMU). `floor`: see _scale_text. Returns the smallest text size left, in pt, or None."""
    x0, y0 = min(s.left for s in targets), min(s.top for s in targets)
    inside, low = set(), []
    for s in targets:
        el = s._element
        pt = _scale_text(prs, slide, el, factor if grow_text else min(factor, 1.0), floor)
        if pt is not None:
            low.append(pt)
        for node in el.iter(qn("a:ln")):
            if node.get("w"):
                node.set("w", str(max(1, round(int(node.get("w")) * factor))))
        for body in el.iter(qn("a:bodyPr")):
            for attr, default in (("lIns", 91440), ("rIns", 91440), ("tIns", 45720), ("bIns", 45720)):
                body.set(attr, str(round(int(body.get(attr, default)) * factor)))
        for node in el.iter(qn("a:outerShdw"), qn("a:innerShdw"), qn("a:glow"), qn("a:softEdge")):
            for attr in ("dist", "blurRad", "rad"):
                if node.get(attr):
                    node.set(attr, str(round(int(node.get(attr)) * factor)))
        for node in el.iter(qn("a:gridCol")):
            node.set("w", str(round(int(node.get("w")) * factor)))
        for node in el.iter(qn("a:tr")):
            node.set("h", str(round(int(node.get("h")) * factor)))
        # the frame itself; a group's children follow it
        s.left, s.top = x0 + round((s.left - x0) * factor), y0 + round((s.top - y0) * factor)
        s.width, s.height = round(s.width * factor), round(s.height * factor)
        ids = {n.get("id") for n in el.iter(qn("p:cNvPr"))}
        inside |= ids if len(targets) > 1 else ids - {str(s.shape_id)}
    # A motion path inside the block shrinks with it. A path on one scaled group
    # is its trip across the slide and is left alone.
    num = re.compile(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?")
    for motion in slide._element.iter(qn("p:animMotion")):
        tgt = motion.find(".//p:spTgt", NS)
        if tgt is not None and tgt.get("spid") in inside and motion.get("path"):
            motion.set("path", num.sub(lambda m: f"{float(m.group()) * factor:.6g}", motion.get("path")))
    if at is not None:
        dx, dy = at[0] - x0, at[1] - y0
        for s in targets:
            s.left, s.top = s.left + dx, s.top + dy
    return min(low) if low else None


NUMBER = re.compile(r"(\d+(?:[.,]\d+)*)(\s?%)?")  # "2%" and "2 lần" are different numbers


def _numbers(prs):
    """Every number a viewer can read, per slide, with how often: text, tables, chart data, notes."""
    out = []
    for slide in prs.slides:
        texts = [n.text or "" for n in slide._element.iter(qn("a:t"))]
        for shape in _walk(slide.shapes):
            if getattr(shape, "has_chart", False):
                texts += [v.text or "" for v in shape.chart._chartSpace.iter(f"{{{C_NS}}}v")]
        if slide.has_notes_slide:
            texts.append(slide.notes_slide.notes_text_frame.text)
        found = Counter()
        for t in texts:
            for m, pct in NUMBER.findall(t):
                raw = m.replace(",", ".")
                try:
                    found[f"{float(raw):g}" + ("%" if pct else "")] += 1
                except ValueError:
                    pass
        out.append(found)
    return out


def _number_variants(token):
    """Both readings of an ambiguous grouped number: "156.179" and "156179" are the same number here.

    A deck may print 1.200 as a European thousands group while another prints 1200; the gate must not
    call that a lost number. Only dot groups of three digits are expanded; "1.2" stays a decimal.
    """
    pct = "%" if token.endswith("%") else ""
    core = token.rstrip("%")
    variants = {token}
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", core):
        variants.add(core.replace(".", "") + pct)
    return variants


def missing_numbers(before, after):
    """Numbers in BEFORE that appear nowhere in AFTER: {slide no: [numbers]}.

    Both readings of an ambiguous grouped number count as the same value, so a formatting change is not
    reported as a lost number; a number that is genuinely gone still fails.
    """
    kept = set().union(*_numbers(Presentation(after)))
    out = {}
    for i, nums in enumerate(_numbers(Presentation(before)), 1):
        gone = sorted([n for n in nums if not (_number_variants(n) & kept)], key=_num_key)
        if gone:
            out[i] = gone
    return out


def fewer_numbers(before, after):
    """Numbers AFTER still has, but fewer times than BEFORE: {number: (before, after)}.

    A number that vanished from one slide can hide behind the same value on
    another ("mục tiêu 2%" gone, "2 lần" kept). A lower count is that warning.
    """
    b, a = sum(_numbers(Presentation(before)), Counter()), sum(_numbers(Presentation(after)), Counter())
    return {n: (b[n], sum(a.get(v, 0) for v in _number_variants(n)))
            for n in sorted(b, key=_num_key)
            if 0 < sum(a.get(v, 0) for v in _number_variants(n)) < b[n]}


def _num_key(n):
    return float(n.rstrip("%")), n


def _chart_numbers(chart):
    area = chart._chartSpace.find(f".//{{{C_NS}}}plotArea")
    sers = area.findall(f".//{{{C_NS}}}ser")
    if not sers:
        raise ValueError("the chart has no series")

    def points(node):
        if node is None:
            return []
        found = {int(p.get("idx")): p.findtext(f"{{{C_NS}}}v") for p in node.iter(f"{{{C_NS}}}pt")}
        return [found[k] for k in sorted(found)]

    fmt = sers[0].findtext(f"{{{C_NS}}}val//{{{C_NS}}}formatCode") or "General"
    series = []
    for k, ser in enumerate(sers, 1):
        name = ser.findtext(f"{{{C_NS}}}tx//{{{C_NS}}}v") or f"Series {k}"
        series.append((name, [float(v) if v not in (None, "") else None for v in points(ser.find(f"{{{C_NS}}}val"))]))
    cats = points(sers[0].find(f"{{{C_NS}}}cat")) or [str(n + 1) for n in range(len(series[0][1]))]
    return cats, series, fmt


KINDS = {"column": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED,
         "line": XL_CHART_TYPE.LINE_MARKERS, "pie": XL_CHART_TYPE.PIE}


def add_chart(slide, kind, box, categories, series, number_format="General", color="1F4E79", accent=None,
              muted="C9C9C9", font=None, size=16, ink="404040"):
    """Add a flat native chart in the guide-5 style and return its frame.

    box: (left, top, width, height) in EMU. series: [(name, [values])]; the first
    series is the story and gets `color`, the others are context in grey. Direct
    labels on the story only, no gridlines, no value axis, axis from 0. With
    `accent` one category keeps `color` and the others turn grey.
    """
    if kind not in KINDS:
        raise ValueError(f"--kind must be one of {sorted(KINDS)}")
    if accent is not None and accent not in categories:
        raise ValueError(f"--accent {accent!r} is not a category; categories are {categories}")
    data = CategoryChartData(number_format=number_format)
    data.categories = categories
    for n, v in series:
        data.add_series(n, v)
    frame = slide.shapes.add_chart(KINDS[kind], *box, data)
    ch = frame.chart
    ch.has_title = False
    ch.font.size = Pt(size)
    ch.font.color.rgb = RGBColor.from_string(ink)
    if font:
        ch.font.name = font
    one = len(series) == 1
    ch.has_legend = not one and kind != "pie"
    if ch.has_legend:
        ch.legend.include_in_layout = False
        ch.legend.position = XL_LEGEND_POSITION.TOP
    plot = ch.plots[0]
    labels = plot.series[0].data_labels  # labels on the story series only
    labels.show_value = True
    labels.number_format, labels.number_format_is_linked = number_format, True
    main_c, grey = RGBColor.from_string(color), RGBColor.from_string(muted)
    if kind == "pie":
        labels.show_category_name = True
        labels.position = XL_LABEL_POSITION.OUTSIDE_END
    else:
        ch.value_axis.visible = False
        ch.value_axis.has_major_gridlines = False
        ch.value_axis.minimum_scale = 0
        ch.category_axis.has_major_gridlines = False
        ch.category_axis.format.line.color.rgb = grey
        ch.category_axis.tick_labels.font.size = Pt(size)
        if kind == "bar":
            ch.category_axis.reverse_order = True  # first category on top
        if kind == "line":
            labels.position = XL_LABEL_POSITION.ABOVE
        else:
            plot.gap_width = 60
            labels.position = XL_LABEL_POSITION.OUTSIDE_END
    for s_no, ser in enumerate(plot.series):
        colour = main_c if s_no == 0 else grey
        if kind == "line":
            ser.format.line.color.rgb, ser.format.line.width = colour, Pt(3 if s_no == 0 else 2)
            ser.marker.format.fill.solid()
            ser.marker.format.fill.fore_color.rgb = colour
            ser.marker.format.line.color.rgb = colour
            ser.smooth = False
            continue
        ser.format.fill.solid()
        ser.format.fill.fore_color.rgb = grey if one and (accent is not None or kind == "pie") else colour
        for k, cat in enumerate(categories):
            if one and (cat == accent or (kind == "pie" and accent is None and k == 0)):
                fill = ser.points[k].format.fill
                fill.solid()
                fill.fore_color.rgb = main_c
    return frame


def rechart(deck, slide_no, name, kind, output, sort=False, **style):
    """Rebuild a chart flat from its own numbers, keeping its id, name, place and layer,
    so animation that points at it still works. Style options as in add_chart."""
    prs = Presentation(deck)
    slide = prs.slides[slide_no - 1]
    (old,) = _top_shapes(slide, [name])
    if not getattr(old, "has_chart", False):
        raise ValueError(f"{name!r} is not a native chart. A picture of a chart: ask its author for the numbers")
    cats, series, fmt = _chart_numbers(old.chart)
    if sort:
        order = sorted(range(len(cats)), key=lambda k: -(series[0][1][k] or 0))
        cats = [cats[k] for k in order]
        series = [(n, [v[k] for k in order]) for n, v in series]
    new = add_chart(slide, kind, (old.left, old.top, old.width, old.height), cats, series, fmt, **style)
    new_el, old_el = new._element, old._element
    c_nv = new_el.find(".//p:cNvPr", NS)
    c_nv.set("id", str(old.shape_id))
    c_nv.set("name", old.name)
    rid = old_el.find(".//c:chart", {"c": C_NS}).get(qn("r:id"))
    old_el.addprevious(new_el)
    old_el.getparent().remove(old_el)
    slide.part.drop_rel(rid)
    prs.save(output)
    return {"categories": cats, "series": [n for n, _ in series], "kind": kind}


def theme_fonts(prs, heading, body):
    """Write the deck's two fonts into its theme. Text that names no font follows the
    body font; a run whose font is "+mj-lt" follows the heading font."""
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    for master in prs.slide_masters:
        part = master.part.part_related_by(RT.THEME)
        root = E.fromstring(part.blob)
        for tag, face in (("majorFont", heading), ("minorFont", body)):
            root.find(f".//a:{tag}/a:latin", NS).set("typeface", face)
        part._blob = E.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def follow_theme(element):
    """Remove fonts typed by hand under `element` (a slide's or shape's ._element),
    so the text follows the theme fonts again."""
    for node in element.iter(qn("a:rPr"), qn("a:defRPr"), qn("a:endParaRPr")):
        for tag in ("a:latin", "a:ea", "a:cs"):
            for face in node.findall(qn(tag)):
                node.remove(face)


def unstretch(deck, slide_no, name, output, box=False):
    """Undo a squashed picture: crop it to its frame (centre kept), or with box=True
    keep the height and centre and give the frame the photo's shape."""
    prs = Presentation(deck)
    slide = prs.slides[slide_no - 1]
    (pic,) = _top_shapes(slide, [name])
    if pic.shape_type != MSO_SHAPE_TYPE.PICTURE:
        raise ValueError(f"{name!r} is not a picture")
    r = _stretch(pic)
    if box:
        cx = pic.left + pic.width / 2
        pic.width = round(pic.width / r)
        pic.left = round(cx - pic.width / 2)
    elif r > 1:  # frame wider than the photo: cut top and bottom
        cut = (1 - pic.crop_top - pic.crop_bottom) * (1 - 1 / r) / 2
        pic.crop_top, pic.crop_bottom = pic.crop_top + cut, pic.crop_bottom + cut
    else:  # frame taller than the photo: cut the sides
        cut = (1 - pic.crop_left - pic.crop_right) * (1 - r) / 2
        pic.crop_left, pic.crop_right = pic.crop_left + cut, pic.crop_right + cut
    prs.save(output)
    return r


def _line(tag, colour, width_pt):
    ln = E.SubElement(E.Element("dummy"), qn(f"a:{tag}"), w=str(round(width_pt * 12700)) if colour else "0")
    if colour:
        E.SubElement(E.SubElement(ln, qn("a:solidFill")), qn("a:srgbClr"), val=colour)
    else:
        E.SubElement(ln, qn("a:noFill"))
    return ln


def style_table(table, font=None, size=None, ink="1D2433", head_rows=1, head_fill="0062AC", head_ink="FFFFFF",
                rule="C9D2DE", lines="grid", fill_map=None, body_fill="FFFFFF"):
    """Restyle a native PowerPoint table in place: every cell keeps its text and merges; borders, fills and
    type change. fill_map {"FFFF00": "0062AC"} recolours cells by their old fill (Gantt bars); every other
    body fill becomes body_fill (None: no fill, the slide shows through). lines: "grid" or "rows" (horizontal rules only)."""
    fill_map = {k.upper(): v for k, v in (fill_map or {}).items()}
    tbl = table._tbl
    tbl_pr = tbl.find(qn("a:tblPr"))
    for attr in ("firstRow", "bandRow", "firstCol", "lastRow", "lastCol", "bandCol"):
        tbl_pr.attrib.pop(attr, None)
    for node in tbl_pr.findall(qn("a:tableStyleId")):
        tbl_pr.remove(node)
    fills = {qn(f"a:{t}") for t in ("noFill", "solidFill", "gradFill", "blipFill", "pattFill", "grpFill")}
    for r, row in enumerate(table.rows):
        head = r < head_rows
        for cell in row.cells:
            pr = cell._tc.get_or_add_tcPr()
            old = pr.find("a:solidFill/a:srgbClr", NS)
            old = old.get("val").upper() if old is not None else None
            for node in list(pr):
                if node.tag in fills or E.QName(node).localname in ("lnL", "lnR", "lnT", "lnB"):
                    pr.remove(node)
            side = rule if lines == "grid" else None
            for tag, colour in (("lnL", side), ("lnR", side), ("lnT", rule), ("lnB", rule)):
                pr.append(_line(tag, colour, 0.75))
            # Fill belongs after every border/cell3D node, including diagonal borders that we preserve.
            insert_at = max((i for i, node in enumerate(pr)
                             if E.QName(node).localname.startswith("ln") or E.QName(node).localname == "cell3D"),
                            default=-1) + 1
            colour = head_fill if head else fill_map.get(old, body_fill)
            fill = E.Element(qn("a:solidFill")) if colour else E.Element(qn("a:noFill"))
            if colour:
                E.SubElement(fill, qn("a:srgbClr"), val=colour)
            pr.insert(insert_at, fill)
            pr.set("anchor", "ctr")
            for para in cell.text_frame.paragraphs:
                for run in para.runs:
                    if font:
                        run.font.name = font
                    if size:
                        run.font.size = Pt(size)
                    run.font.color.rgb = RGBColor.from_string(head_ink if head else ink)
                    if head:
                        run.font.bold = True


def retable(deck, slide_no, name, output, **style):
    """style_table on one table of a deck, saved to output. Returns (rows, columns)."""
    prs = Presentation(deck)
    (frame,) = _top_shapes(prs.slides[slide_no - 1], [name])
    if not getattr(frame, "has_table", False):
        raise ValueError(f"{name!r} is not a table")
    style_table(frame.table, **style)
    prs.save(output)
    return len(frame.table.rows), len(frame.table.columns)


def cutout(src, out, lo=60, hi=140):
    """Take a plain background off a picture (a diagram frame, a logo, an icon): soft edges, the subject's
    inner parts kept (an eye, a highlight), faint marks in the background dropped, no light fringe.

    The background colour is read from the picture's border. A pixel's colour distance from it decides:
    below lo is background, above hi is subject, between is the soft edge."""
    import numpy as np
    from PIL import Image
    try:
        from scipy import ndimage as ndi
    except ImportError:
        raise ValueError("cutout needs scipy: pip install scipy") from None
    im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    ring = np.concatenate([im[:8].reshape(-1, 3), im[-8:].reshape(-1, 3),
                           im[:, :8].reshape(-1, 3), im[:, -8:].reshape(-1, 3)])
    bg = np.median(ring, axis=0)
    soft = np.clip((np.sqrt(((im - bg) ** 2).sum(-1)) - lo) / (hi - lo), 0, 1)
    core = ndi.binary_opening(soft > 0.5, iterations=3)  # thin lines and specks of the background go
    lab, n = ndi.label(core)
    if not n:
        raise ValueError("nothing differs enough from the background: lower the range, e.g. --range 30,90")
    sizes = ndi.sum(core, lab, range(1, n + 1))
    big = 1 + np.flatnonzero(sizes >= 0.02 * sizes.max())  # ponytail: parts under 2% of the largest go
    body = ndi.binary_fill_holes(np.isin(lab, big))
    inner = ndi.binary_erosion(body, iterations=2)
    edge = ndi.binary_dilation(body, iterations=4) & ~inner
    alpha = np.where(inner, 1.0, np.where(edge, soft, 0.0))
    rgb = np.clip((im - (1 - alpha[..., None]) * bg) / np.maximum(alpha, 1e-3)[..., None], 0, 255)
    Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA").save(out)
    share = float((alpha > 0.5).mean())
    note = "  <- most of the picture is kept: is the background plain?" if share > 0.8 else ""
    return (f"background #{''.join(f'{round(v):02X}' for v in bg)}; kept {len(big)} part(s), dropped "
            f"{n - len(big)} small mark(s); subject is {share:.0%} of the picture{note} -> {out}")


def replace_picture(slide, name, image):
    """Put a new image file into an existing picture: same place, size, crop, name and id, so its
    animation still runs (e.g. the cutout of a diagram frame)."""
    (pic,) = _top_shapes(slide, [name])
    _, rid = slide.part.get_or_add_image_part(image)
    pic._element.blipFill.blip.rEmbed = rid


# ------------------------------------------------------------ putting a deck into a theme

def _shell_parts(prs):
    """The parts of a deck that are shell, not content: [{"key", "where", "what", "slides", "shapes"}].
    m*: shapes on a slide master. l*: shapes on a layout. r*: top-level shapes of the same kind at the
    same place on many slides (a step bar, a logo, a title slot)."""
    parts = []
    for master in prs.slide_masters:
        for shape in master.shapes:
            if not shape.is_placeholder:
                parts.append({"key": f"m{sum(p['key'][0] == 'm' for p in parts) + 1}", "where": "master",
                              "what": f"{shape.shape_type} {shape.name!r}", "slides": None, "shapes": [(None, shape)]})
        for layout in master.slide_layouts:
            used = [n for n, slide in enumerate(prs.slides, 1) if slide.slide_layout == layout]
            for shape in layout.shapes:
                if used and not shape.is_placeholder:
                    parts.append({"key": f"l{sum(p['key'][0] == 'l' for p in parts) + 1}",
                                  "where": f"layout {layout.name!r}", "what": f"{shape.shape_type} {shape.name!r}",
                                  "slides": used, "shapes": [(None, shape)]})
    tol = (0.04 * prs.slide_width, 0.04 * prs.slide_height)
    groups = []
    for n, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.is_placeholder or shape.width is None or shape.left is None:
                continue
            box = (shape.left, shape.top, shape.width, shape.height)
            for g in groups:
                if g[1] == shape.shape_type and all(abs(a - b) <= tol[j % 2] for j, (a, b) in enumerate(zip(g[0], box))):
                    g[2].append((n, shape))
                    break
            else:
                groups.append([box, shape.shape_type, [(n, shape)]])
    need = max(3, 0.3 * len(prs.slides))
    for box, kind, members in groups:
        on = sorted({n for n, _ in members})
        if len(on) >= need:
            parts.append({"key": f"r{sum(p['key'][0] == 'r' for p in parts) + 1}", "where": "slides",
                          "what": f"{kind}", "slides": on, "shapes": members, "box": box})
    return parts


def _span(numbers):
    """[1, 2, 3, 7] -> '1-3, 7'."""
    out, start, last = [], None, None
    for n in numbers + [None]:
        if start is None:
            start = last = n
        elif n is not None and n == last + 1:
            last = n
        else:
            out.append(str(start) if start == last else f"{start}-{last}")
            start = last = n
    return ", ".join(out)


def _words(shape):
    if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        return " ".join(filter(None, (_words(child) for child in shape.shapes)))
    return shape.text_frame.text.strip().replace("\n", " ") if shape.has_text_frame else ""


def shell(deck):
    """Plain-text list of where a deck's shell lives, so all of it can be taken off before a theme goes on."""
    prs = Presentation(deck)
    px = lambda v: round(v / 9525)   # noqa: E731
    lines = [f"deck: {len(prs.slides)} slides. The shell is what repeats: take all of it off before the new "
             "theme goes on, or the old one shows through (guide 13)."]
    for master in prs.slide_masters:
        bg = master._element.find(".//" + qn("p:bg"))
        kinds = [E.QName(node).localname for node in bg.iter()] if bg is not None else []
        fill = next((k for k in kinds if k in ("solidFill", "gradFill", "blipFill", "pattFill")), "none")
        lines.append(f"master background: {fill}   (key: bg)")
    own = [n for n, slide in enumerate(prs.slides, 1) if slide._element.find(qn("p:cSld")).find(qn("p:bg")) is not None]
    if own:
        lines.append(f"slides with a background of their own: {_span(own)}")
    for part in _shell_parts(prs):
        _, first = part["shapes"][0]
        box = part.get("box") or (first.left, first.top, first.width, first.height)
        place = "at ({},{}) size {}x{} px".format(*(px(v) for v in box))
        if part["where"] != "slides":
            lines.append(f"{part['key']}  on the {part['where']}: {part['what']} {place}"
                         + (f", shows on slides {_span(part['slides'])}" if part["slides"] else ", shows on every slide"))
            continue
        ids = {slide_no: {t.get("spid") for t in prs.slides[slide_no - 1]._element.iter(qn("p:spTgt"))}
               for slide_no in part["slides"]}
        moving = sum(str(shape.shape_id) in ids[n] for n, shape in part["shapes"])
        texts = [w for w in (_words(shape) for _, shape in part["shapes"]) if w]
        lines.append(f"{part['key']}  on {len(part['slides'])} slides ({_span(part['slides'])}): {part['what']} {place}"
                     + (f"; {moving} animated (kept by --strip)" if moving else ""))
        if texts:
            same = len(set(texts)) == 1
            lines.append(f"      text {'is the same everywhere' if same else 'differs per slide: its words are content'}"
                         f": {texts[0][:60]!r}" + ("" if same else f" ... {texts[-1][:60]!r}"))
    lines.append("then: shell DECK --strip m1,m2,r1 [--background F6F2EA] -o OUT.pptx   (writes OUT.shell.json: the "
                 "words of what it removed, per slide)")
    return "\n".join(lines)


def unshell(deck, output, keys, background=None):
    """Take shell parts off a deck (keys from `shell`). Animated shapes stay. `background`: a hex colour for
    the master, which also removes every slide's own background. Returns {slide: [words removed]} and a note."""
    prs = Presentation(deck)
    parts = {part["key"]: part for part in _shell_parts(prs)}
    unknown = [k for k in keys if k not in parts]
    if unknown:
        raise ValueError(f"no shell part {', '.join(unknown)}; run `shell DECK` for the keys: {', '.join(parts)}")
    words, removed, kept = {}, 0, 0
    for key in keys:
        for slide_no, shape in parts[key]["shapes"]:
            if slide_no is not None:
                slide = prs.slides[slide_no - 1]
                if str(shape.shape_id) in {t.get("spid") for t in slide._element.iter(qn("p:spTgt"))}:
                    kept += 1
                    continue
                if _words(shape):
                    words.setdefault(slide_no, []).append({"part": key, "text": _words(shape)})
            shape._element.getparent().remove(shape._element)
            removed += 1
    if background:
        for holder in [m._element for m in prs.slide_masters] + [s._element for s in prs.slides]:
            c_sld = holder.find(qn("p:cSld"))
            old = c_sld.find(qn("p:bg"))
            if old is not None:
                c_sld.remove(old)
        for master in prs.slide_masters:
            bg = E.SubElement(master._element.find(qn("p:cSld")), qn("p:bg"))
            master._element.find(qn("p:cSld")).insert(0, bg)
            pr = E.SubElement(bg, qn("p:bgPr"))
            E.SubElement(E.SubElement(pr, qn("a:solidFill")), qn("a:srgbClr"), val=background.upper())
            E.SubElement(pr, qn("a:effectLst"))
    prs.save(output)
    Path(output).with_suffix(".shell.json").write_text(json.dumps(words, ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
    return words, (f"removed {removed} shapes" + (f", kept {kept} that are animated" if kept else "")
                   + (f", background {background.upper()}" if background else ""))


def fit(deck, output, into, slides=None, skip=(), grow=1.0):
    """Scale each slide's content as one block so it sits inside `into` (x, y, width, height in inches):
    the content area the theme leaves free. Content is only made smaller unless `grow` is above 1 (a
    table is often taller on screen than its frame says, so growing one is a guess). Shapes named in `skip`, shapes whose name starts with "!!",
    placeholders and full-slide backgrounds stay where they are. Arrangement, ids and animation are kept.
    Text is never shrunk below guide 4's minimum (12 pt on a slide 7.5 in tall); a box may then be a
    little small for its words, which `glance` and your eyes catch.
    -> [(slide, factor, smallest text pt or None)]"""
    prs = Presentation(deck)
    least = MIN_PT * prs.slide_height / REF_HEIGHT
    left, top, width, height = (round(v * 914400) for v in into)
    out = []
    for n, slide in enumerate(prs.slides, 1):
        if slides and n not in slides:
            continue
        targets = [s for s in slide.shapes if s.width and s.height and s.name not in skip
                   and not s.name.startswith("!!") and not s.is_placeholder
                   and s.width * s.height < 0.85 * prs.slide_width * prs.slide_height]
        if not targets:
            continue
        x0, y0 = min(s.left for s in targets), min(s.top for s in targets)
        x1, y1 = max(s.left + s.width for s in targets), max(s.top + s.height for s in targets)
        factor = min(width / (x1 - x0), height / (y1 - y0), grow)
        at = (left + (width - (x1 - x0) * factor) / 2, top + (height - (y1 - y0) * factor) / 2)
        low = _scale_block(prs, slide, targets, factor, tuple(round(v) for v in at), least)
        out.append((n, factor, low))
    prs.save(output)
    return out


def compare(before, after, out_dir, mapping=None):
    """One picture per new slide: the old slide (or slides) above, the new one below, both as wide as the
    picture. For looking, one pair at a time. mapping: the map of `check` ({new: {"old": [...]}});
    without it slide n is paired with slide n. -> [(new slide, [old slides], path)]"""
    from PIL import Image, ImageDraw
    out_dir = Path(out_dir)
    old, _ = look(before, out_dir / "old")
    new, _ = look(after, out_dir / "new")
    rows = {int(k): v for k, v in (mapping or {}).items() if k != "dropped"}
    pairs, codes = [], {}
    for n, path in enumerate(new, 1):
        olds = [o for o in (rows[n].get("old", []) if n in rows else [n] if not mapping else []) if 1 <= o <= len(old)]
        below = Image.open(path).convert("RGB")
        w, h = below.size
        sheet = Image.new("RGB", (w, 2 * h + 60), (28, 28, 28))
        draw = ImageDraw.Draw(sheet)
        for k, o in enumerate(olds):
            cell = Image.open(old[o - 1]).convert("RGB").resize((w // len(olds), h // len(olds)))
            sheet.paste(cell, (k * (w // len(olds)), 30 + (h - cell.height) // 2))
        draw.text((10, 9), "OLD " + (", ".join(f"slide {o}" for o in olds) if olds else "(nothing: a new slide)"),
                  fill=(255, 255, 255))
        draw.text((10, h + 39), f"NEW slide {n}", fill=(255, 255, 255))
        sheet.paste(below, (0, h + 60))
        target = out_dir / f"pair-{n:02d}.jpg"
        sheet, codes[target.name] = _stamp(sheet, f"pair {n}")
        sheet.save(target, quality=88)
        pairs.append((n, olds, target))
    _keep_codes(out_dir, codes)
    return pairs


# ------------------------------------------------------------ laying a slide out by regions

def _layout_cells(node, box, gap):
    """Walk a layout tree and give every leaf its cell: [(leaf, (left, top, width, height))], in inches.
    A node is {"row": [...]} (side by side), {"col": [...]} (stacked) or a leaf; any node may carry
    "weight" (its share of the row or column, default 1)."""
    kids = node.get("row") or node.get("col") if isinstance(node, dict) else None
    if not kids:
        return [(node, box)]
    across = "row" in node
    kids = [k if isinstance(k, dict) else {"item": k} for k in kids]
    total = sum(k.get("weight", 1) for k in kids)
    room = (box[2] if across else box[3]) - gap * (len(kids) - 1)
    cells, at = [], box[0] if across else box[1]
    for k in kids:
        size = room * k.get("weight", 1) / total
        cell = (at, box[1], size, box[3]) if across else (box[0], at, box[2], size)
        cells += _layout_cells(k, cell, gap)
        at += size + gap
    return cells


def arrange(deck, slide_no, layout, output):
    """Place a slide's shapes by regions, so nobody has to compute coordinates.

    layout = {"in": [x, y, w, h] (inches: the area to fill), "gap": 0.25, "row" or "col": [...]}. A leaf is
    - "Name" or {"item": "Name"}: one top-level shape;
    - {"block": ["Photo", "Arrow 1", "Label"]}: shapes that belong together and keep their arrangement
      (a photo with its marks);
    each with optional "weight", "align" ("l", "c", "r"; default "c") and "valign" ("t", "m", "b").
    A picture, group, chart, table or block is scaled to fit its cell without being stretched (ids,
    animation follow; text inside shrinks with it but never under the minimum, and never grows: a
    caption does not become a headline because its photo grew). A text box takes the width of its cell
    and keeps its type size. {"weight": 2} with no item is an empty cell. Shapes the layout does not name
    stay where they are.
    -> ([(names, factor)], [names left where they were])"""
    prs = Presentation(deck)
    slide = prs.slides[slide_no - 1]
    least = MIN_PT * prs.slide_height / REF_HEIGHT
    emu = 914400
    placed, used = [], set()
    for leaf, (left, top, width, height) in _layout_cells(layout, tuple(layout["in"]), layout.get("gap", 0.25)):
        if "block" not in leaf and "item" not in leaf:
            continue   # {"weight": 2} alone is an empty cell: room left on purpose
        names = leaf.get("block") or [leaf["item"]]
        targets = _top_shapes(slide, names)
        used |= set(names)
        x0, y0 = min(s.left for s in targets), min(s.top for s in targets)
        w = max(s.left + s.width for s in targets) - x0
        h = max(s.top + s.height for s in targets) - y0
        only = targets[0]
        words_only = len(targets) == 1 and only.has_text_frame and only.shape_type not in (
            MSO_SHAPE_TYPE.PICTURE, MSO_SHAPE_TYPE.GROUP) and not only.is_placeholder
        if words_only:   # words take the width they are given; their size is a decision, not a fit
            only.left, only.top, only.width = round(left * emu), round(top * emu), round(width * emu)
            if leaf.get("valign", "t") != "t":
                only.top = round((top + (height - only.height / emu) / (2 if leaf["valign"] == "m" else 1)) * emu)
            placed.append((names, 1.0))
            continue
        factor = min(width * emu / w, height * emu / h)
        spare_x, spare_y = width * emu - w * factor, height * emu - h * factor
        dx = {"l": 0, "c": spare_x / 2, "r": spare_x}[leaf.get("align", "c")]
        dy = {"t": 0, "m": spare_y / 2, "b": spare_y}[leaf.get("valign", "m")]
        _scale_block(prs, slide, targets, factor, (round(left * emu + dx), round(top * emu + dy)), least,
                     grow_text=False)
        placed.append((names, factor))
    left_alone = [s.name for s in slide.shapes if s.name not in used and not s.name.startswith("!!")
                  and not s.is_placeholder]
    prs.save(output)
    return placed, left_alone


# ------------------------------------------------------------ proof of looking

def _stamp(image, label):
    """Add a strip under a review picture with a random three-letter code. Whoever reports the code has
    opened the picture. -> (picture with the strip, code)"""
    import secrets
    from PIL import Image, ImageDraw
    code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(3))
    out = Image.new("RGB", (image.width, image.height + 34), (20, 20, 20))
    out.paste(image, (0, 0))
    draw = ImageDraw.Draw(out)
    from PIL import ImageFont
    try:
        big = ImageFont.load_default(size=22)
    except TypeError:   # Pillow before 10.1 has one size only
        big = ImageFont.load_default()
    draw.text((12, image.height + 5), f"{label}  -  look code:", fill=(200, 200, 200), font=big)
    x = 12 + draw.textlength(f"{label}  -  look code:  ", font=big)
    for n, letter in enumerate(code):      # large and spaced, so it survives a scaled-down view
        draw.text((x + 26 * n, image.height + 5), letter, fill=(255, 221, 0), font=big)
    return out, code


def _codes_file(folder):
    return Path(folder) / "look-codes.json"


def _keep_codes(folder, codes):
    """Store the codes as salted hashes, so the file itself does not give them away."""
    import hashlib
    import secrets
    salt = secrets.token_hex(8)
    data = {"salt": salt, "pictures": {name: hashlib.sha256((salt + name + code).encode()).hexdigest()
                                      for name, code in codes.items()}}
    _codes_file(folder).write_text(json.dumps(data, indent=1), encoding="utf-8")


def seen(folder, claims):
    """Check the look codes an agent read off the pictures of a review folder.
    claims: {"slide-03.png" or "3": "K7P"}. -> (pictures proven seen, pictures not proven)"""
    import hashlib
    data = json.loads(_codes_file(folder).read_text(encoding="utf-8"))
    names = sorted(data["pictures"])
    said = {}
    for key, code in claims.items():
        match = [n for n in names if n == key or re.sub(r"\D", "", n).lstrip("0") == str(key).lstrip("0")]
        if len(match) == 1:
            said[match[0]] = code.strip().upper()
    ok = [n for n in names if n in said and
          hashlib.sha256((data["salt"] + n + said[n]).encode()).hexdigest() == data["pictures"][n]]
    return ok, [n for n in names if n not in ok]


# ------------------------------------------------------------ a reference document to follow

def _font_key(name):
    """'ABCDEF+HelveticaNeueLTPro-Bd' and 'Helvetica Neue LT Pro' -> 'helveticaneueltpro'."""
    key = re.sub(r"[^a-z0-9]", "", re.split(r"[-,]", name.split("+")[-1])[0].lower())
    return re.sub(r"(psmt|mt|ps)$", "", key)


def _pdf_family(name):
    return re.split(r"[-,]", name.split("+")[-1])[0]


def installed_fonts():
    """Keys (see _font_key) of the font families installed on this machine."""
    import os
    from PIL import ImageFont
    home = Path.home()
    dirs = [Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts", home / "AppData/Local/Microsoft/Windows/Fonts",
            Path("/Library/Fonts"), Path("/System/Library/Fonts"), home / "Library/Fonts",
            Path("/usr/share/fonts"), home / ".fonts", home / ".local/share/fonts"]
    keys = set()
    for d in dirs:
        if not d.is_dir():
            continue
        for f in d.rglob("*"):
            if f.suffix.lower() in (".ttf", ".otf", ".ttc"):
                for face in range(16 if f.suffix.lower() == ".ttc" else 1):  # a .ttc holds several families
                    try:
                        family = ImageFont.truetype(str(f), 12, index=face).getname()[0]
                    except OSError:
                        break
                    if family:
                        keys.add(_font_key(family))
    return keys


def sample(pdf, out_dir, pages=()):
    """What a reference document is made of: real font names (and whether this machine has them),
    the text sizes and colours it uses most, the colours of its filled shapes by area, and pictures of
    its pages to look at. Needs PyMuPDF."""
    try:
        import fitz
    except ImportError:
        raise ValueError("sample reads PDFs with PyMuPDF: pip install pymupdf")
    from PIL import Image
    doc = fitz.open(pdf)
    if len(doc) == 0:
        raise ValueError("the document has 0 pages")
    bad_pages = [n for n in pages if n < 1 or n > len(doc)]
    if bad_pages:
        raise ValueError(f"the document has {len(doc)} pages; requested page(s) out of range: {bad_pages}")
    fonts, sizes, text, fills = Counter(), Counter(), Counter(), Counter()
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    n = len(span["text"].strip())
                    if n:
                        fonts[_pdf_family(span["font"])] += n
                        sizes[round(span["size"] * 2) / 2] += n
                        text[f"{span['color']:06X}"] += n
        for d in page.get_drawings():
            colour, r = d.get("fill"), d.get("rect")
            if colour and len(colour) == 3 and r is not None and r.width * r.height > 0:
                fills["%02X%02X%02X" % tuple(round(c * 255) for c in colour)] += r.width * r.height
    have = installed_fonts()

    def share(counter, k=8):
        total = sum(counter.values()) or 1
        return ", ".join(f"{key} {v / total:.0%}" for key, v in counter.most_common(k))
    w, h = doc[0].rect.width, doc[0].rect.height
    lines = [f"document: {len(doc)} pages, {w / 72 * 25.4:.0f} x {h / 72 * 25.4:.0f} mm "
             f"({'landscape' if w > h else 'portrait'})",
             "fonts by share of characters:"]
    total = sum(fonts.values()) or 1
    main_fonts = [(n, v) for n, v in fonts.most_common() if v / total >= 0.01]
    for name, v in main_fonts:
        mark = "installed here" if _font_key(name) in have else "NOT installed here: pick the nearest installed font (guide 2)"
        lines.append(f"  {name} {v / total:.0%}  {mark}")
    if len(fonts) > len(main_fonts):
        lines.append(f"  + {len(fonts) - len(main_fonts)} more under 1% each")
    lines += [f"text sizes, pt, by share: {share(sizes)}  (print sizes: keep the ratios, not the sizes)",
              f"text colours: {share(text)}",
              f"filled shapes by area: {share(fills)}"]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(doc), 20):
        batch = []
        for page in doc[start:start + 20]:
            pix = page.get_pixmap(matrix=fitz.Matrix(320 / page.rect.width, 320 / page.rect.width))
            batch.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
        th = max(t.height for t in batch)
        sheet = Image.new("RGB", (5 * 330, ((len(batch) + 4) // 5) * (th + 10)), "white")
        for k, t in enumerate(batch):
            sheet.paste(t, ((k % 5) * 330, (k // 5) * (th + 10)))
        sheet.save(out / f"sheet{start // 20 + 1}.jpg", quality=85)
        lines.append(f"pages {start + 1}-{start + len(batch)}: {out / f'sheet{start // 20 + 1}.jpg'}")
    for n in pages:
        path = out / f"page{n}.png"
        doc[n - 1].get_pixmap(dpi=110).save(str(path))
        lines.append(f"page {n}: {path}")
    return "\n".join(lines)


def _media(slide):
    """(shape, kind, blob, ext) for every picture and video on a slide, groups included."""
    for shape in _walk(slide.shapes):
        if shape.shape_type == MSO_SHAPE_TYPE.MEDIA:
            link = shape._element.find(".//a:videoFile", NS)
            rid = link.get(qn("r:link")) if link is not None else None
            if rid:
                try:
                    part = slide.part.related_part(rid)
                except (KeyError, ValueError):
                    # External/linked media has no embedded part to extract.
                    continue
                yield shape, "video", part.blob, part.partname.ext
        elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            try:
                yield shape, "picture", shape.image.blob, shape.image.ext
            except (AttributeError, KeyError, ValueError):  # linked, not embedded
                continue


def _sha(blob):
    import hashlib
    return hashlib.sha1(blob).hexdigest()[:12]


def _dhash(blob):
    """64-bit difference hash: the same photo re-saved or resized keeps it; a crop or a screenshot does not."""
    import io
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(blob))
        if im.mode in ("P", "PA"):
            im = im.convert("RGBA")
        im = im.convert("L").resize((9, 8))
        data = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
        px = list(data)
    except Exception:  # noqa: BLE001  (EMF, WMF, broken files: no match)
        return None
    return sum(1 << i for i in range(64) if px[i // 8 * 9 + i % 8] > px[i // 8 * 9 + i % 8 + 1])


def _visible(pic):
    return (1 - pic.crop_left - pic.crop_right) * (1 - pic.crop_top - pic.crop_bottom)


def extract(deck, out_dir):
    """Take a deck apart for a rebuild: original media files (not screenshots) and one manifest of what each
    slide says, shows and animates. Returns a short summary."""
    prs = Presentation(deck)
    sw, sh = prs.slide_width, prs.slide_height
    out = Path(out_dir)
    (out / "media").mkdir(parents=True, exist_ok=True)
    slides, files = [], set()
    for i, slide in enumerate(prs.slides, 1):
        animated = {t.get("spid") for t in slide._element.iter(qn("p:spTgt"))}
        effects, clicks = _slide_effects(slide)
        row = {"slide": i, "transition": _transition(slide) or "none", "effects": sum(effects.values()),
               "clicks": clicks, "text": [], "media": [], "charts": [], "tables": [],
               "notes": slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""}
        for shape in sorted(_walk(slide.shapes), key=lambda s: (s.top or 0, s.left or 0)):
            if shape.has_text_frame and shape.text_frame.text.strip():
                row["text"].append({"name": shape.name, "text": shape.text_frame.text.strip()})
            if getattr(shape, "has_chart", False):
                try:
                    cats, series, _ = _chart_numbers(shape.chart)
                    row["charts"].append({"name": shape.name, "kinds": _plot_kinds(shape.chart),
                                          "categories": cats, "series": dict(series)})
                except ValueError:
                    pass
            if getattr(shape, "has_table", False):
                row["tables"].append({"name": shape.name, "rows": [[c.text for c in r.cells]
                                                                   for r in shape.table.rows]})
        for shape, kind, blob, ext in _media(slide):
            name = f"{_sha(blob)}.{ext}"
            if name not in files:
                (out / "media" / name).write_bytes(blob)
                files.add(name)
            item = {"name": shape.name, "kind": kind, "file": f"media/{name}",
                    "box_pct": [round(100 * v / d) for v, d in
                                ((shape.left, sw), (shape.top, sh), (shape.width, sw), (shape.height, sh))],
                    "animated": str(shape.shape_id) in animated}
            if kind == "picture":
                item["pixels"] = list(shape.image.size)
                item["visible_pct"] = round(100 * _visible(shape))
            row["media"].append(item)
        slides.append(row)
    manifest = {"deck": Path(deck).name, "slides": len(slides),
                "size_in": [round(sw / 914400, 2), round(sh / 914400, 2)], "slide_list": slides}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    count = Counter(m["kind"] for s in slides for m in s["media"])
    busy = [f"{s['slide']} ({s['effects']})" for s in slides if s["effects"] >= 20]
    return (f"{len(slides)} slides; {count['picture']} pictures and {count['video']} videos placed, "
            f"{len(files)} distinct files -> {out / 'media'}\n"
            f"charts with data: {sum(len(s['charts']) for s in slides)}; tables: "
            f"{sum(len(s['tables']) for s in slides)}; slides with notes: {sum(bool(s['notes']) for s in slides)}\n"
            f"slides with 20+ effects (watch them, guide 10 'Slide có hiệu ứng'): {', '.join(busy) or 'none'}\n"
            f"manifest: {out / 'manifest.json'}")


def _chart_kind(shape):
    """'pieChart', 'pie3DChart', 'barChart'... from the XML, so a 3D/unsupported chart does not raise."""
    for el in shape.chart._chartSpace.iter():
        local = E.QName(el).localname
        if local.endswith("Chart") and local not in ("chart", "chartSpace"):
            return local
    return "unknown"


def _chart_signature(shape):
    """Values a chart shows: (kind, categories, sorted series value tuples). None when unreadable."""
    try:
        cats, series, _fmt = _chart_numbers(shape.chart)
    except (ValueError, KeyError, TypeError):
        return None
    values = []
    for _name, vals in series:
        values.append(tuple(None if v is None else round(float(v), 6) for v in vals))
    return (_chart_kind(shape), tuple(cats), tuple(sorted(values)))


def check(before, after, mapping=None):
    """Gates for a rebuilt deck: did the content survive? [(passed, gate, detail)]. mapping: {new slide:
    {"old": [old slides], "group": "keep" | "reskin" | "rebuild", "drop": [old picture names left out on
    purpose], "video": "small" (the user agreed to a video that does not fill the slide)},
    "dropped": [old slides left out on purpose]} from the idea table."""
    old, new = Presentation(before), Presentation(after)
    sw, sh = new.slide_width, new.slide_height
    gates = []
    rows = {int(k): v for k, v in (mapping or {}).items() if k != "dropped"}
    small_agreed = {n for n, row in rows.items() if row.get("video") == "small"}

    def gate(ok, name, detail):
        gates.append((ok, name, detail))

    odd = [f"{i}:{t}" for i, s in enumerate(new.slides, 1)
           if (t := _transition(s) or "none") not in ("none", "cut", "fade", "morph")]
    gate(not odd, "transitions", "only fade, Morph or none" if not odd else "old-style: " + ", ".join(odd))
    lost = [i for i, s in enumerate(new.slides, 1)
            if {t.get("spid") for t in s._element.iter(qn("p:spTgt"))} - {n.get("id") for n in
                                                                          s._element.iter(qn("p:cNvPr"))}]
    gate(not lost, "effects intact", "no effect points to a deleted shape" if not lost
         else "effects point to deleted shapes on slides " + ", ".join(map(str, lost)))
    old_media = [{_sha(b): (sh_, k) for sh_, k, b, _ in _media(s)} for s in old.slides]
    looks = {}  # dhash -> old sha, so a re-saved original still counts as the original
    for s in old.slides:
        for _, k, b, _ in _media(s):
            if k == "picture" and (d := _dhash(b)) is not None:
                looks.setdefault(d, _sha(b))

    def source(blob, kind):
        h = _sha(blob)
        if kind == "video" or any(h in m for m in old_media):
            return h
        d = _dhash(blob)
        near = min(looks, key=lambda o: bin(o ^ d).count("1"), default=None) if d is not None else None
        # ponytail: 6 of 64 bits; plain or blank images can match each other
        return looks[near] if near is not None and bin(near ^ d).count("1") <= 6 else "new:" + h

    new_media = [{source(b, k): (sh_, k) for sh_, k, b, _ in _media(s)} for s in new.slides]
    old_vids = {h for m in old_media for h, (_, k) in m.items() if k == "video"}
    new_all = {h for m in new_media for h in m}
    gone = old_vids - new_all
    gate(not gone, "videos kept", f"{len(old_vids)} of {len(old_vids)}" if not gone
         else f"{len(gone)} of {len(old_vids)} videos missing")
    small = [f"{i}: {max(s.width / sw, s.height / sh):.0%}" for i, m in enumerate(new_media, 1)
             for s, k in m.values() if k == "video" and max(s.width / sw, s.height / sh) < 0.9
             and i not in small_agreed]
    gate(not small, "videos fill the slide", "every video >= 90% of the slide's width or height" if not small
         else "smaller: slide " + "; ".join(small))
    numbers_gone = missing_numbers(before, after)
    gate(not numbers_gone, "numbers kept", "every number of the original is still in the deck" if not numbers_gone
         else f"{sum(map(len, numbers_gone.values()))} numbers gone (run `numbers` for the list)")
    best = {}
    for m in old_media:
        for h, (s, k) in m.items():
            if k == "picture":
                best[h] = max(best.get(h, 0), _visible(s))
    cut = [f"{i}: {s.name!r}" for i, m in enumerate(new_media, 1) for h, (s, k) in m.items()
           if k == "picture" and h in best and _visible(s) < best[h] - 0.05]
    gate(not cut, "pictures not cut", "no source picture is cropped more than in the original" if not cut
         else "cropped more than the original: " + "; ".join(cut))
    spread = Counter(h for m in new_media for h in m)  # theme art repeats on many slides
    foreign = [f"{i}: {s.name!r}" for i, m in enumerate(new_media, 1) for h, (s, k) in m.items()
               if k == "picture" and h.startswith("new:") and spread[h] < 3]
    if mapping:
        weak, missing, charts_missing, charts_data_missing, tables_missing, holes = [], [], [], [], [], []
        old_spread = Counter(h for m in old_media for h in m)  # the old theme's art, logos
        for n, row in sorted(rows.items()):
            group, olds = row.get("group", "reskin"), row.get("old", [])
            wrong = [o for o in olds if not 1 <= o <= len(old.slides)]
            if n > len(new.slides):
                holes.append(f"the map has new slide {n}, the deck has {len(new.slides)}")
            if wrong:
                holes.append(f"new slide {n} names old slide {wrong[0]}, the original has {len(old.slides)}")
            if not olds or n > len(new.slides) or wrong:
                continue
            had = sum(sum(_slide_effects(old.slides[o - 1])[0].values()) for o in olds)
            has = sum(_slide_effects(new.slides[n - 1])[0].values())
            if group == "keep" and has < had:
                weak.append(f"{n} (old {'+'.join(map(str, olds))}): {has} of {had}")
            drop = set(row.get("drop", []))
            pics = {h: sh_.name for o in olds for h, (sh_, k) in old_media[o - 1].items()
                    if k == "picture" and old_spread[h] < 3 and sh_.name not in drop}
            short = [pics[h] for h in pics if h not in new_media[n - 1]]
            if short:
                missing.append(f"{n} (old {'+'.join(map(str, olds))}): {', '.join(map(repr, short))}")
            old_shapes = [sh_ for o in olds for sh_ in _walk(old.slides[o - 1].shapes)]
            new_shapes = list(_walk(new.slides[n - 1].shapes))
            old_charts = [_chart_kind(sh_) for sh_ in old_shapes if getattr(sh_, "has_chart", False)]
            new_charts = [_chart_kind(sh_) for sh_ in new_shapes if getattr(sh_, "has_chart", False)]
            for ct in set(old_charts):
                if new_charts.count(ct) < old_charts.count(ct):
                    charts_missing.append(f"{n} (old {'+'.join(map(str, olds))}): {ct}")
            old_sigs = Counter(_chart_signature(sh_) for sh_ in old_shapes if getattr(sh_, "has_chart", False))
            old_sigs.pop(None, None)
            new_sigs = Counter(_chart_signature(sh_) for sh_ in new_shapes if getattr(sh_, "has_chart", False))
            for sig, have in old_sigs.items():
                if new_sigs.get(sig, 0) < have:
                    charts_data_missing.append(
                        f"{n} (old {'+'.join(map(str, olds))}): {sig[0]} data changed or gone")
            old_tables = [sh_.name for sh_ in old_shapes if getattr(sh_, "has_table", False)
                          and sh_.name not in drop]
            new_tables = [sh_ for sh_ in new_shapes if getattr(sh_, "has_table", False)]
            if len(new_tables) < len(old_tables):
                tables_missing.append(f"{n} (old {'+'.join(map(str, olds))}): {len(old_tables)} table(s)")
        used = {o for row in rows.values() for o in row.get("old", [])} | set(mapping.get("dropped", []))
        unlisted = sorted(set(range(1, len(old.slides) + 1)) - used)
        if unlisted:  # or a hard slide passes every gate by not being in the map
            holes.append("old slides in no row: " + ", ".join(map(str, unlisted))
                         + " (give each a row, or list it under \"dropped\")")
        gate(not holes, "every slide accounted for", "each old slide has a row or is dropped on purpose"
             if not holes else "; ".join(holes))
        gate(not weak, "keep slides keep their effects", "all there" if not weak else "; ".join(weak))
        gate(not missing, "source pictures on their slide",
             "every picture of the old slide is on the new one" if not missing
             else "missing (put back, or list under \"drop\" in the map if left out on purpose): "
             + "; ".join(missing))
        gate(not charts_missing, "charts kept", "every source chart is still on its slide" if not charts_missing
             else "missing/changed chart type (put back, or list under \"drop\"): " + "; ".join(charts_missing))
        gate(not charts_data_missing, "chart data kept",
             "every source chart still shows its original categories and values" if not charts_data_missing
             else "data changed (restore from the source chart, do not redraw with invented values): "
             + "; ".join(charts_data_missing))
        gate(not tables_missing, "tables kept", "every source table is still on its slide" if not tables_missing
             else "missing table (put back, or list under \"drop\"): " + "; ".join(tables_missing))
    passed = sum(ok for ok, _, _ in gates)
    note = ("pictures not from the original (look at each: a new icon or photo is fine; a cut-out of a "
            "screenshot, or a photo cut down in an image editor, is not): " + "; ".join(foreign) if foreign else "")
    return gates, passed, note


# --------------------------------------------------------------- components another agent can reuse
# Cut a diagram frame, a step bar, a Gantt or an icon out of a finished deck so another agent can
# paste it into a new one. Written as code because PowerPoint's own XML keeps groups and pictures
# reachable only through relationship ids; words cannot move them safely (D011).

_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_P = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _xfrm_of(el):
    tag = E.QName(el).localname
    if tag == "grpSp":
        return el.find(f"{{{_P}}}grpSpPr/{{{_A}}}xfrm")
    if tag == "graphicFrame":
        return el.find(f"{{{_P}}}xfrm")
    return el.find(f"{{{_P}}}spPr/{{{_A}}}xfrm")


def _vals(x):
    if x is None:
        return None
    out = {"rot": float(x.get("rot", 0)) / 60000.0, "flipH": x.get("flipH") == "1",
           "flipV": x.get("flipV") == "1", "off": None, "ext": None, "choff": None, "chext": None}
    for key, tag in (("off", "off"), ("ext", "ext"), ("choff", "chOff"), ("chext", "chExt")):
        n = x.find(f"{{{_A}}}{tag}")
        if n is not None:
            out[key] = (int(n.get("x", 0)), int(n.get("y", 0))) if tag in ("off", "chOff") else \
                (int(n.get("cx", 0)), int(n.get("cy", 0)))
    return out


class _Mat:
    """2x3 affine transform; composition is parent @ child (child runs first)."""

    __slots__ = ("a", "b", "c", "d", "e", "f")

    def __init__(self, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
        self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f

    def __matmul__(self, o):
        return _Mat(self.a * o.a + self.c * o.b, self.b * o.a + self.d * o.b,
                    self.a * o.c + self.c * o.d, self.b * o.c + self.d * o.d,
                    self.a * o.e + self.c * o.f + self.e, self.b * o.e + self.d * o.f + self.f)

    def apply(self, x, y):
        return self.a * x + self.c * y + self.e, self.b * x + self.d * y + self.f

    def decompose(self):
        """Scale, clockwise rotation and the two flips; refuses what a shape cannot represent."""
        import math
        det = self.a * self.d - self.b * self.c
        a, b, c, d = self.a, self.b, self.c, self.d
        flipH = flipV = False
        if det < 0:
            if abs(b) < 1e-6 and abs(c) < 1e-6:
                flipH, flipV = a < 0, d < 0
                a, d = abs(a), abs(d)
            else:
                raise ValueError("a group that is mirrored and rotated cannot be flattened into shapes; "
                                 "ungroup it in PowerPoint, or copy the whole group as a component")
        su, sv = math.hypot(a, b), math.hypot(c, d)
        if su == 0 or sv == 0:
            raise ValueError("a group is scaled to zero")
        if abs(a * c + b * d) / (su * sv) > 1e-3:
            raise ValueError("a group combines rotation and unequal scaling (it skews its children); "
                             "ungroup it in PowerPoint, or copy the whole group as a component")
        return su, sv, math.degrees(math.atan2(b, a)), flipH, flipV


def _xform_mat(x):
    """Matrix mapping a group's child coordinate space to the slide."""
    import math
    v = _vals(x)
    ox, oy = v["off"]
    ecx, ecy = v["ext"]
    if v["choff"] and v["chext"]:
        cx, cy = v["choff"]
        cex, cey = v["chext"]
        sx, sy = ecx / cex, ecy / cey
        m = _Mat(sx, 0, 0, sy, ox - cx * sx, oy - cy * sy)
    else:
        m = _Mat(1, 0, 0, 1, ox, oy)
    cxm, cym = ox + ecx / 2, oy + ecy / 2
    if v["flipH"] or v["flipV"]:
        fx = -1 if v["flipH"] else 1
        fy = -1 if v["flipV"] else 1
        m = _Mat(fx, 0, 0, fy, cxm * (1 - fx), cym * (1 - fy)) @ m
    if v["rot"]:
        th = math.radians(v["rot"])
        cos, sin = math.cos(th), math.sin(th)
        rot = _Mat(cos, sin, -sin, cos, cxm - (cos * cxm - sin * cym), cym - (sin * cxm + cos * cym))
        m = rot @ m
    return m


def _apply_to_leaf(el, m):
    """Write the composed transform back into one child's xfrm (position, size, rotation, flip)."""
    x = _xfrm_of(el)
    if x is None:
        return
    v = _vals(x)
    if not v["off"] or not v["ext"]:
        return
    ox, oy = v["off"]
    ecx, ecy = v["ext"]
    su, sv, ang, fh, fv = m.decompose()
    if abs(su - sv) > 1e-3 and abs(v["rot"]) > 1e-6:
        raise ValueError("a rotated child sits inside an unequally scaled group (skew); "
                         "ungroup in PowerPoint")
    cx, cy = ox + ecx / 2, oy + ecy / 2
    ncx, ncy = m.apply(cx, cy)
    off = x.find(f"{{{_A}}}off")
    ext = x.find(f"{{{_A}}}ext")
    off.set("x", str(int(round(ncx - ecx * su / 2))))
    off.set("y", str(int(round(ncy - ecy * sv / 2))))
    ext.set("cx", str(int(round(ecx * su))))
    ext.set("cy", str(int(round(ecy * sv))))
    rot = (v["rot"] + ang) % 360
    if rot:
        x.set("rot", str(int(round(rot * 60000))))
    elif "rot" in x.attrib:
        del x.attrib["rot"]
    for attr, flag, old in (("flipH", fh, v["flipH"]), ("flipV", fv, v["flipV"])):
        new = bool(flag) ^ bool(old)
        if new:
            x.set(attr, "1")
        elif attr in x.attrib:
            del x.attrib[attr]


def _timing_group_ids(slide):
    ids = set()
    for node in slide._element.iter(f"{{{_P}}}spTgt"):
        if node.get("spid"):
            ids.add(node.get("spid"))
    return ids


def _unique_top_names(slide):
    seen = Counter()
    for sh in slide.shapes:
        seen[sh.name] += 1
        if seen[sh.name] > 1:
            sh.name = f"{sh.name} ({seen[sh.name]})"


def ungroup(deck, slide_no, names=None, output=None, all_groups=False, force=False):
    """Flatten groups into separate top-level shapes, keeping the slide's geometry.

    PowerPoint stores a child's position in the group's child coordinate space; this maps it back to
    the slide with scale, rotation and flip. Groups that carry animation are left alone unless
    force=True, because the timing points at the group id."""
    prs = Presentation(deck)
    slide = prs.slides[slide_no - 1]
    groups = [sh for sh in slide.shapes if sh.shape_type == MSO_SHAPE_TYPE.GROUP]
    if names:
        wanted = _top_shapes(slide, names)
        groups = [s for s in wanted if s.shape_type == MSO_SHAPE_TYPE.GROUP]
    elif not all_groups:
        raise ValueError("name the groups to flatten, or pass --all-groups")
    if not groups:
        raise ValueError("no groups to flatten: nothing on this slide is a group")
    timed = _timing_group_ids(slide)
    blocked = []
    for g in groups:
        if str(g.shape_id) in timed and not force:
            blocked.append(g.name)
    if blocked:
        raise ValueError(f"these groups carry animation: {', '.join(blocked)}. Copy the group whole, or "
                         f"pass --force to flatten and break its animation")
    identity = _Mat()
    for g in groups:
        leaves = []
        _flatten_children(g._element, identity, leaves)
        for el, mat in leaves:
            _apply_to_leaf(el, mat)
        for el, _ in leaves:
            g._element.addprevious(el)
        g._element.getparent().remove(g._element)
    _unique_top_names(slide)
    if output:
        prs.save(output)
    return f"flattened {len(groups)} group(s) on slide {slide_no} -> {output or '(not saved)'}"


def _flatten_children(group_el, parent, leaves):
    """Recursively collect leaf shapes with the transform from the leaf's local space to the slide."""
    gx = group_el.find(f"{{{_P}}}grpSpPr/{{{_A}}}xfrm")
    m = parent @ _xform_mat(gx) if gx is not None else parent
    for child in list(group_el):
        tag = E.QName(child).localname
        if tag == "grpSp":
            _flatten_children(child, m, leaves)
        elif tag in ("sp", "pic", "graphicFrame", "cxnSp"):
            leaves.append((child, m))


def _shape_bbox(shapes):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for sh in shapes:
        try:
            xs0.append(sh.left); ys0.append(sh.top)
            xs1.append(sh.left + sh.width); ys1.append(sh.top + sh.height)
        except (AttributeError, TypeError):
            continue
    if not xs0:
        raise ValueError("the selected shapes have no size (is one a placeholder?)")
    return min(xs0), min(ys0), max(xs1), max(ys1)


def _shift_el(el, dx, dy):
    x = _xfrm_of(el)
    if x is None:
        return
    off = x.find(f"{{{_A}}}off")
    if off is not None:
        off.set("x", str(int(off.get("x", 0)) + int(dx)))
        off.set("y", str(int(off.get("y", 0)) + int(dy)))


def _reject_non_shape(el, sh):
    if getattr(sh, "has_chart", False) and sh.has_chart:
        raise ValueError(f"{sh.name!r} is a chart: rebuild it with rechart, or copy the whole slide")
    for node in el.iter():
        tag = E.QName(node).localname
        if tag in ("videoFile", "audioFile", "wavAudioFile"):
            raise ValueError(f"{sh.name!r} carries video/audio: copy the slide, the media cannot become a component")
        if tag == "graphicData" and "diagram" in (node.get("uri") or ""):
            raise ValueError(f"{sh.name!r} is SmartArt: copy the slide, SmartArt has its own data parts")


def _remap_rels(src_slide, dest_slide, el):
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    for node in el.iter():
        for attr in (qn("r:id"), qn("r:embed"), qn("r:link")):
            old = node.get(attr)
            if not old:
                continue
            rel = src_slide.part.rels[old]
            if rel.is_external:
                new = dest_slide.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
            elif rel.reltype == RT.IMAGE:
                _part, new = dest_slide.part.get_or_add_image_part(io.BytesIO(rel.target_part.blob))
            else:
                raise ValueError(f"shape uses a {rel.reltype.split('/')[-1]} relationship; "
                                 f"only pictures can move into a component — copy the slide instead")
            node.set(attr, new)


def _freeze_theme(src_prs, dest_slide):
    """Bake theme colours and theme fonts into the copied shapes so they keep their look in a deck with
    another theme."""
    from pptx.opc.constants import RELATIONSHIP_TYPE as RT
    tp = src_prs.slide_master.part.part_related_by(RT.THEME)
    root = E.fromstring(tp.blob)
    scheme = root.find(f".//{{{_A}}}clrScheme")
    colours = {}
    for child in list(scheme):
        hexa = None
        for c in child:
            if E.QName(c).localname == "srgbClr":
                hexa = c.get("val")
            elif E.QName(c).localname == "sysClr":
                hexa = c.get("lastClr")
        if hexa:
            colours[E.QName(child).localname] = hexa
    fonts = {}
    for tag in ("majorFont", "minorFont"):
        node = root.find(f".//{{{_A}}}{tag}/{{{_A}}}latin")
        if node is not None:
            fonts["+mj-lt" if tag == "majorFont" else "+mn-lt"] = node.get("typeface") or "Arial"
    for el in list(dest_slide._element.iter()):
        ln = E.QName(el).localname
        if ln == "schemeClr":
            hexa = colours.get(el.get("val"))
            if hexa:
                new = E.Element(f"{{{_A}}}srgbClr")
                new.set("val", hexa)
                for child in list(el):
                    new.append(child)
                el.getparent().replace(el, new)
        elif ln in ("latin", "ea", "cs"):
            face = el.get("typeface", "")
            if face.startswith("+mj"):
                el.set("typeface", fonts.get("+mj-lt", "Arial"))
            elif face.startswith("+mn"):
                el.set("typeface", fonts.get("+mn-lt", "Arial"))
    return colours, fonts


def _png_of(deck_path, png_path):
    """A PNG preview of the one-slide component, at the component's own aspect (a thin step bar must not
    be rendered as a 16:9 screenshot)."""
    try:
        import win32com.client as win32
        out = Path(png_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        app = win32.Dispatch("PowerPoint.Application")
        was_open = app.Presentations.Count
        pres = app.Presentations.Open(str(Path(deck_path).resolve()), True, False, False)
        try:
            w = pres.PageSetup.SlideWidth
            h = pres.PageSetup.SlideHeight
            px = 1600
            py = max(1, round(px * h / w))
            pres.Slides(1).Export(str(out.resolve()), "PNG", px, py)
        finally:
            pres.Close()
            if not was_open:
                app.Quit()
        return f"preview -> {png_path}"
    except Exception as exc:  # PowerPoint is optional
        return f"no PNG preview: {exc}"


def component(deck, slide_no, output, names=None, exclude=None, drop_bg=True, flatten=False,
              margin=24, freeze=False, png=None, manifest=None, exclude_chrome=False):
    """Extract selected shapes as a one-slide component deck, trimmed to their bounds.

    names: top-level shape names to take; default all. exclude: top-level names to drop. drop_bg also
    drops pictures/rectangles covering most of the slide (backgrounds). flatten ungroups the copies."""
    prs = Presentation(deck)
    slide = prs.slides[slide_no - 1]
    W, H = prs.slide_width, prs.slide_height
    chosen = []
    if names:
        chosen = _top_shapes(slide, names)
    else:
        chosen = [sh for sh in slide.shapes]
    excluded = set(exclude or [])
    chrome = {"Logo", "Title", "Footer", "Footer rule", "Page number"}
    kept = []
    dropped = []
    for sh in chosen:
        if sh.name in excluded or (exclude_chrome and (sh.name.startswith("!!") or sh.name in chrome)):
            dropped.append(sh.name)
            continue
        if drop_bg:
            try:
                area = sh.width * sh.height
                covers = area >= 0.85 * W * H and sh.left <= 0.03 * W and sh.top <= 0.03 * H
            except (AttributeError, TypeError):
                covers = False
            if covers or sh.name == "!!bg":
                dropped.append(sh.name)
                continue
        kept.append(sh)
    if not kept:
        raise ValueError("nothing kept: every selected shape looks like a background or was excluded")
    for sh in kept:
        _reject_non_shape(sh._element, sh)
    margin = int(margin * 9525)  # CLI margin is in pixels of a 96 dpi slide
    dest = Presentation()
    dest.slide_width, dest.slide_height = prs.slide_width, prs.slide_height
    ds = dest.slides.add_slide(dest.slide_layouts[6])
    copied = []
    for sh in kept:
        el = copy.deepcopy(sh._element)
        _remap_rels(slide, ds, el)
        ds.shapes._spTree.append(el)
        copied.append(el)
    shapes = list(ds.shapes)
    if flatten:
        groups = [g for g in shapes if g.shape_type == MSO_SHAPE_TYPE.GROUP]
        if groups:
            for g in groups:
                leaves = []
                _flatten_children(g._element, _Mat(), leaves)
                for el, mat in leaves:
                    _apply_to_leaf(el, mat)
                for el, _ in leaves:
                    g._element.addprevious(el)
                g._element.getparent().remove(g._element)
    shapes = list(ds.shapes)
    x0, y0, x1, y1 = _shape_bbox(shapes)
    dx, dy = margin - x0, margin - y0
    for sh in shapes:
        _shift_el(sh._element, dx, dy)
    # PowerPoint refuses a slide under 1 in; a thin bar component still needs a real page
    dest.slide_width = max(int(x1 - x0 + 2 * margin), 914400)
    dest.slide_height = max(int(y1 - y0 + 2 * margin), 914400)
    ds.background.fill.background()
    if freeze:
        _freeze_theme(prs, ds)
    dest.save(output)
    meta = {
        "component": Path(output).stem,
        "source_deck": Path(deck).name,
        "source_slide": slide_no,
        "shapes": [sh.name for sh in kept],
        "kept": len(shapes),
        "dropped": dropped,
        "frozen_theme": bool(freeze),
        "size_in": [round(dest.slide_width / 914400, 2), round(dest.slide_height / 914400, 2)],
        "note": "one slide; copy its shapes into the target deck (place), or open it and copy-paste in "
                "PowerPoint. Pictures keep their crop and name; text stays editable.",
    }
    if manifest:
        Path(manifest).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = (f"{len(shapes)} shape(s) from slide {slide_no} -> {output} "
               f"({meta['size_in'][0]} x {meta['size_in'][1]} in); dropped {len(dropped)} "
               f"(background/excluded); {'theme frozen' if freeze else 'theme NOT frozen'}.")
    if manifest:
        summary += f" manifest -> {manifest}"
    if png:
        summary += " | " + _png_of(output, png)
    return summary


def place(component_deck, target_deck, slide_no, output, at=None):
    """Put a component deck's one slide onto a slide of another deck (pictures and text stay editable)."""
    src = Presentation(component_deck)
    comp = src.slides[0]
    prs = Presentation(target_deck)
    if slide_no < 1 or slide_no > len(prs.slides):
        raise ValueError(f"the target deck has {len(prs.slides)} slide(s); slide {slide_no} does not exist")
    slide = prs.slides[slide_no - 1]
    els = []
    for sh in comp.shapes:
        el = copy.deepcopy(sh._element)
        _remap_rels(comp, slide, el)
        slide.shapes._spTree.append(el)
        els.append(el)
    x0, y0, _x1, _y1 = _shape_bbox([sh for sh in slide.shapes if sh._element in els])
    at = at or (0, 0)
    for el in els:
        _shift_el(el, at[0] * 914400 - x0, at[1] * 914400 - y0)
    # PowerPoint needs one unique shape id per slide
    ids = [int(sh.shape_id) for sh in slide.shapes]
    nxt = max(ids or [1]) + 1
    seen = set()
    for sh in slide.shapes:
        i = int(sh.shape_id)
        if i in seen:
            sh._element.find(".//" + qn("p:cNvPr")).set("id", str(nxt))  # type: ignore[union-attr]
            nxt += 1
        seen.add(i)
    prs.save(output)
    note = f"at {at[0]},{at[1]} in" if at else "at the slide's top-left"
    return f"placed {len(els)} shape(s) from {Path(component_deck).name} on slide {slide_no} {note} -> {output}"


def components(deck, slide_no=None):
    """List what could become a reusable component on a slide: groups, diagram clusters, charts, tables,
    pictures, and the full-slide pictures that are only backgrounds."""
    prs = Presentation(deck)
    W, H = prs.slide_width, prs.slide_height
    out = []
    slides = [prs.slides[slide_no - 1]] if slide_no else list(prs.slides)
    for n, s in enumerate(slides, start=slide_no or 1):
        out.append(f"slide {n}: {len(s.shapes)} top-level shape(s)")
        chrome = []
        for sh in s.shapes:
            try:
                x, y, w, h = (round(v / 9525) for v in (sh.left, sh.top, sh.width, sh.height))
                flags = []
                if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                    flags.append(f"group of {len(sh.shapes)}")
                if getattr(sh, "has_chart", False) and sh.has_chart:
                    flags.append("chart: rebuild with rechart")
                if getattr(sh, "has_table", False) and sh.has_table:
                    flags.append("table")
                if sh.shape_type == MSO_SHAPE_TYPE.MEDIA:
                    flags.append("video/audio: copy the slide")
                if sh.width * sh.height >= 0.85 * W * H and sh.left <= 0.03 * W and sh.top <= 0.03 * H:
                    flags.append("covers the slide: background")
                out.append(f"  {sh.shape_type}  {sh.name!r}  ({x},{y},{w},{h})  " + ", ".join(flags))
            except (AttributeError, TypeError):
                out.append(f"  {sh.shape_type}  {sh.name!r}  (no box)")
            if sh.name.startswith("!!") or sh.name in ("Logo", "Title", "Footer", "Footer rule", "Page number"):
                chrome.append(sh.name)
        if chrome:
            out.append("  chrome (usually excluded): " + ", ".join(sorted(set(chrome))))
    out.append("")
    out.append("pick names, then: component DECK SLIDE --name A --name B -o out.pptx"
               "   (or --exclude chrome/background names)")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("look", help="export slides as PNG + contact sheet (PowerPoint)")
    a.add_argument("deck")
    a.add_argument("-o", "--output", default=None, help="folder (default: <deck>-look)")
    a = sp.add_parser("watch", help="photograph the real slide show: open, every click, inside each Morph")
    a.add_argument("deck")
    a.add_argument("--slides", default=None, help="slide numbers, e.g. 3,6 (default: all)")
    a.add_argument("-o", "--output", default=None, help="folder (default: <deck>-watch)")
    a = sp.add_parser("glance", help="the faults a viewer sees at once, measured in PowerPoint and boxed on the slide")
    a.add_argument("deck")
    a.add_argument("--slides", default=None, help="slide numbers, e.g. 3,6 (default: all)")
    a.add_argument("-o", "--output", default=None, help="folder (default: <deck>-glance)")
    a.add_argument("--ink", nargs=2, metavar=("HEX", "OUT.pptx"),
                   help="also write OUT.pptx with the text nobody can read set to this colour")
    a = sp.add_parser("compare", help="old slide above, new slide below, one large picture per slide")
    a.add_argument("before")
    a.add_argument("after")
    a.add_argument("--map", help="the map of `check`; without it slide n is paired with slide n")
    a.add_argument("-o", "--output", default=None, help="folder (default: <after>-compare)")
    a = sp.add_parser("shell", help="where the old shell lives (master, layouts, repeated shapes); --strip takes it off")
    a.add_argument("deck")
    a.add_argument("--strip", help="keys from the listing, e.g. m1,m2,r1")
    a.add_argument("--background", help="hex colour for the master background; slides lose their own")
    a.add_argument("-o", "--output", help="with --strip or --background")
    a = sp.add_parser("fit", help="scale each slide's content as one block into the theme's content area")
    a.add_argument("deck")
    a.add_argument("--into", required=True, help="the content area, inches: X,Y,WIDTH,HEIGHT")
    a.add_argument("--slides", default=None, help="e.g. 2,3,5-9 (default: all)")
    a.add_argument("--skip", action="append", default=[], help="a shape name to leave alone (repeatable)")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("arrange", help="place a slide's shapes by regions (rows and columns), no coordinates")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("layout", help='JSON file: {"in": [x, y, w, h], "gap": 0.25, "col": [{"row": ["A", "B"], '
                                  '"weight": 3}, "Conclusion"]}')
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("seen", help="prove the review pictures were opened: give the look codes read off them")
    a.add_argument("folder", help="the folder glance or compare wrote")
    a.add_argument("codes", nargs="+", help="N=CODE, e.g. 3=K7P 4=Q2M")
    a = sp.add_parser("motion", help="write clicks and transitions from a plan")
    a.add_argument("deck")
    a.add_argument("plan")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("inventory", help="what an existing deck uses, and its measurable problems")
    a.add_argument("deck")
    a = sp.add_parser("sample", help="what a reference PDF is made of: fonts, sizes, colours, pages")
    a.add_argument("pdf")
    a.add_argument("--pages", default="", help="pages to save large, e.g. 5,11")
    a.add_argument("-o", "--output", default=None, help="folder (default: <pdf>-sample)")
    a = sp.add_parser("scale", help="shrink or grow shapes as one block, text and motion included")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("names", nargs="+")
    a.add_argument("--by", type=float, required=True, help="factor, e.g. 0.7")
    a.add_argument("--at", help="move the block's top-left corner here, inches: X,Y")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("numbers", help="numbers in the original that the new deck lost")
    a.add_argument("before")
    a.add_argument("after")
    a = sp.add_parser("extract", help="original media files and a manifest of every slide, for a rebuild")
    a.add_argument("deck")
    a.add_argument("-o", "--output", default=None, help="folder (default: <deck>-extract)")
    a = sp.add_parser("check", help="gates for a rebuilt deck: what of the original survived")
    a.add_argument("before")
    a.add_argument("after")
    a.add_argument("--map", help='JSON: {"17": {"old": [15, 16], "group": "keep|reskin|rebuild", '
                                 '"drop": ["Picture 65"]}, "dropped": [9]}')
    a = sp.add_parser("retable", help="restyle a native table in place: text and merges kept")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("name")
    a.add_argument("--font")
    a.add_argument("--size", type=float, help="pt; default keeps each run's size")
    a.add_argument("--ink", default="1D2433", help="body text colour, hex")
    a.add_argument("--head-rows", type=int, default=1)
    a.add_argument("--head", default="0062AC", help="header fill, hex")
    a.add_argument("--head-ink", default="FFFFFF")
    a.add_argument("--rule", default="C9D2DE", help="border colour, hex")
    a.add_argument("--lines", choices=("grid", "rows"), default="grid")
    a.add_argument("--fill", action="append", default=[], help="recolour a cell fill: OLD=NEW, e.g. FFFF00=0062AC")
    a.add_argument("--body", default="FFFFFF", help="fill for every other body cell, hex, or none")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("cutout", help="take a plain background off a picture: soft edges, no fringe")
    a.add_argument("image")
    a.add_argument("--range", default="60,140", help="colour distance from the background: LOW,HIGH")
    a.add_argument("-o", "--output", required=True, help="PNG")
    a = sp.add_parser("rechart", help="rebuild a chart flat from its own numbers")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("name")
    a.add_argument("--kind", required=True, choices=sorted(KINDS))
    a.add_argument("--color", default="1F4E79", help="main colour, hex")
    a.add_argument("--accent", help="category to highlight; the others turn grey")
    a.add_argument("--muted", default="C9C9C9", help="grey, hex")
    a.add_argument("--font")
    a.add_argument("--size", type=float, default=16, help="label size, pt")
    a.add_argument("--ink", default="404040", help="label colour, hex")
    a.add_argument("--sort", action="store_true", help="largest first")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("unstretch", help="undo a stretched picture")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("name")
    a.add_argument("--box", action="store_true", help="resize the frame instead of cropping the photo")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("components", help="list what could become a reusable component on a slide")
    a.add_argument("deck")
    a.add_argument("--slide", type=int, help="one slide; default every slide")
    a = sp.add_parser("ungroup", help="flatten groups into separate top-level shapes")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("names", nargs="*")
    a.add_argument("--all-groups", action="store_true")
    a.add_argument("--force", action="store_true", help="also flatten groups that carry animation")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("component", help="extract selected shapes as a one-slide component deck")
    a.add_argument("deck")
    a.add_argument("slide", type=int)
    a.add_argument("--name", action="append", default=[], help="top-level shape to take; repeat")
    a.add_argument("--exclude", action="append", default=[], help="top-level shape to drop; repeat")
    a.add_argument("--no-drop-bg", action="store_true", help="keep full-slide background pictures")
    a.add_argument("--exclude-chrome", action="store_true", help="drop !! shapes, Logo, Title, Footer, page number")
    a.add_argument("--ungroup", action="store_true", help="flatten groups inside the component")
    a.add_argument("--margin", type=int, default=24, help="padding around the shapes, pixels (24)")
    a.add_argument("--freeze", action="store_true", help="bake theme colours and fonts into the component")
    a.add_argument("--png", help="also render a PNG preview (needs PowerPoint)")
    a.add_argument("--manifest", help="write a JSON manifest (default: none)")
    a.add_argument("-o", "--output", required=True)
    a = sp.add_parser("place", help="put a component deck back onto a slide")
    a.add_argument("component")
    a.add_argument("deck")
    a.add_argument("--slide", type=int, required=True)
    a.add_argument("--at", help="top-left in inches, e.g. 1,2; default 0,0")
    a.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "inventory":
            print(inventory(args.deck))
            return 0
        if args.cmd == "sample":
            out = args.output or str(Path(args.pdf).with_suffix("")) + "-sample"
            print(sample(args.pdf, out, [int(p) for p in args.pages.split(",") if p]))
            return 0
        if args.cmd == "retable":
            n = retable(args.deck, args.slide, args.name, args.output, font=args.font, size=args.size, ink=args.ink,
                        head_rows=args.head_rows, head_fill=args.head, head_ink=args.head_ink, rule=args.rule,
                        lines=args.lines, fill_map=dict(f.split("=", 1) for f in args.fill),
                        body_fill=None if args.body.lower() == "none" else args.body)
            print(f"restyled a {n[0]} x {n[1]} table -> {args.output}; render it and look at it")
            return 0
        if args.cmd == "cutout":
            lo, hi = (float(v) for v in args.range.split(","))
            print(cutout(args.image, args.output, lo, hi))
            print("look at it on a dark and a light background before using it")
            return 0
        if args.cmd == "components":
            print(components(args.deck, args.slide))
            return 0
        if args.cmd == "ungroup":
            print(ungroup(args.deck, args.slide, args.names or None, args.output,
                          all_groups=args.all_groups, force=args.force))
            return 0
        if args.cmd == "component":
            print(component(args.deck, args.slide, args.output, names=args.name or None,
                            exclude=args.exclude or None, drop_bg=not args.no_drop_bg,
                            flatten=args.ungroup, margin=args.margin, freeze=args.freeze,
                            png=args.png, manifest=args.manifest, exclude_chrome=args.exclude_chrome))
            return 0
        if args.cmd == "place":
            at = tuple(float(v) for v in args.at.split(",")) if args.at else None
            print(place(args.component, args.deck, args.slide, args.output, at))
            return 0
        if args.cmd == "extract":
            print(extract(args.deck, args.output or str(Path(args.deck).with_suffix("")) + "-extract"))
            return 0
        if args.cmd == "check":
            mapping = json.loads(Path(args.map).read_text(encoding="utf-8")) if args.map else None
            gates, passed, note = check(args.before, args.after, mapping)
            for ok, name, detail in gates:
                print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
            print(f"{passed}/{len(gates)} gates pass" + ("" if mapping else " (no --map: slide-level gates skipped)"))
            if note:
                print(note)
            print("gates check that content survived; they do not say the deck is good (guide 11)")
            return 0 if passed == len(gates) else 1
        if args.cmd == "numbers":
            lost = missing_numbers(args.before, args.after)
            for i, nums in lost.items():
                print(f"slide {i} of the original: {', '.join(nums)} not found anywhere in the new deck")
            fewer = fewer_numbers(args.before, args.after)
            for n, (was, now) in fewer.items():
                print(f"{n} appears {now} times, was {was}: check no slide lost it")
            print("every number kept" if not lost else "check each one: moved to notes or an appendix is fine, gone is not")
            print("this is a necessary check, not proof: read every new slide against the idea table")
            return 1 if lost else 0
        if args.cmd == "scale":
            at = tuple(float(v) for v in args.at.split(",")) if args.at else None
            low = scale(args.deck, args.slide, args.names, args.by, args.output, at)
            print(f"scaled {len(args.names)} shapes by {args.by} -> {args.output}")
            floor = _floor(Presentation(args.output))
            if low is not None and low < floor:
                print(f"warning: smallest text is now {low:g} pt (guide 4 wants {floor:g} at this slide size). Keep "
                      f"the diagram's form: set its text back to {floor:g} pt and widen the text boxes. If it "
                      "still does not fit, split it over two slides. Never redraw it as another kind of diagram.")
            return 0
        if args.cmd == "rechart":
            info = rechart(args.deck, args.slide, args.name, args.kind, args.output, args.sort, color=args.color,
                           accent=args.accent, muted=args.muted, font=args.font, size=args.size, ink=args.ink)
            print(json.dumps(info, ensure_ascii=False))
            return 0
        if args.cmd == "unstretch":
            r = unstretch(args.deck, args.slide, args.name, args.output, args.box)
            print(f"was {abs(r - 1):.0%} {'wider' if r > 1 else 'taller'} than the photo -> {args.output}")
            return 0
    except ValueError as exc:
        sys.exit(f"error: {exc}")
    if args.cmd == "glance":
        out = args.output or str(Path(args.deck).with_suffix("")) + "-glance"
        report = glance(args.deck, out, [int(n) for n in args.slides.split(",")] if args.slides else None)
        print("\n".join(glance_lines(report)))
        if args.ink:
            print(f"{reink(args.deck, args.ink[1], report, args.ink[0])} runs of unreadable text set to "
                  f"{args.ink[0].upper()} -> {args.ink[1]}; run glance on it and look")
        return 1 if any(row["faults"] for row in report) else 0
    if args.cmd == "arrange":
        try:
            placed, left_alone = arrange(args.deck, args.slide,
                                         json.loads(Path(args.layout).read_text(encoding="utf-8")), args.output)
        except (ValueError, KeyError) as exc:
            sys.exit(f"error: {exc}")
        for names, factor in placed:
            print(f"  {' + '.join(names)}: x{factor:.2f}")
        if left_alone:
            print("left where they were (name them in the layout, or decide they go): " + ", ".join(left_alone))
        print(f"-> {args.output}. Now render this slide and look at it: glance {args.output} --slides {args.slide}")
        return 0
    if args.cmd == "seen":
        ok, missing = seen(args.folder, dict(c.split("=", 1) for c in args.codes if "=" in c))
        print(f"{len(ok)} of {len(ok) + len(missing)} pictures proven seen")
        if missing:
            print("not proven (open the picture and read the code in its bottom strip): " + ", ".join(missing))
        return 0 if not missing else 1
    if args.cmd == "compare":
        out = args.output or str(Path(args.after).with_suffix("")) + "-compare"
        mapping = json.loads(Path(args.map).read_text(encoding="utf-8")) if args.map else None
        pairs = compare(args.before, args.after, out, mapping)
        print(f"{len(pairs)} pairs -> {out}. Open them one at a time, old above and new below, and ask of each: "
              "what did the old slide have that the new one lost, and what on the new one is worse? (guide 13)")
        for n, olds, path in pairs:
            print(f"  new {n} <- old {', '.join(map(str, olds)) or '-'}: {path}")
        return 0
    if args.cmd == "shell":
        try:
            if args.strip or args.background:
                if not args.output:
                    sys.exit("error: --strip and --background need -o OUT.pptx")
                _, note = unshell(args.deck, args.output, [k for k in (args.strip or "").split(",") if k],
                                  args.background)
                print(f"{note} -> {args.output}; the words removed are in {Path(args.output).with_suffix('.shell.json')}")
            else:
                print(shell(args.deck))
        except ValueError as exc:
            sys.exit(f"error: {exc}")
        return 0
    if args.cmd == "fit":
        picked = set()
        for part in (args.slides or "").split(","):
            if part:
                first, _, last = part.partition("-")
                picked |= set(range(int(first), int(last or first) + 1))
        into = tuple(float(v) for v in args.into.split(","))
        done = fit(args.deck, args.output, into, picked or None, set(args.skip))
        floor = _floor(Presentation(args.output))
        for n, factor, low in done:
            small = f"; smallest text now {low:g} pt, under {floor:g}: raise it or split the slide" \
                if low is not None and factor < 1 and low < floor else ""
            print(f"slide {n}: x{factor:.2f}{small}")
        print(f"{len(done)} slides fitted -> {args.output}. Now glance, then look at every slide.")
        return 0
    if args.cmd == "watch":
        out = args.output or str(Path(args.deck).with_suffix("")) + "-watch"
        picked = [int(n) for n in args.slides.split(",")] if args.slides else None
        print("\n".join(watch_lines(watch(args.deck, out, picked))))
    elif args.cmd == "look":
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
