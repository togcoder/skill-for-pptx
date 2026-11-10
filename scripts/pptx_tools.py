#!/usr/bin/env python3
"""Small toolbox for the PPTX guidance skill (skills/pptx, T087).

The skill decides what the deck should look like and how it should move. These
commands only do what written guidance cannot:

    look DECK [-o DIR]          export every slide as PNG with PowerPoint, plus one
                                contact sheet, so the agent can see what it built
    motion DECK PLAN -o OUT     write click reveals and slide transitions from a
                                short plan that names shapes, not ids
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
    """Numbers worth tracking across slides: >= 100, decimals or percentages; not years or step numbers."""
    keys = set()
    for found in NUMBER.finditer(text):
        m, pct = found.groups()
        if found.start() and text[found.start() - 1].isalpha():  # part of a code: H422, T35
            continue
        v = m.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+", m) else m.replace(",", ".")
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


def _scale_text(prs, slide, el, factor):
    """Give every run an explicit size, then scale all sizes. Returns smallest pt shown."""
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
            node.set("sz", str(max(100, round(int(node.get("sz")) * factor))))
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
    x0, y0 = min(s.left for s in targets), min(s.top for s in targets)
    inside, low = set(), []
    for s in targets:
        el = s._element
        pt = _scale_text(prs, slide, el, factor)
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
        dx, dy = round(at[0] * 914400) - x0, round(at[1] * 914400) - y0
        for s in targets:
            s.left, s.top = s.left + dx, s.top + dy
    prs.save(output)
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
                v = m.replace(".", "").replace(",", ".") if re.fullmatch(r"\d{1,3}(\.\d{3})+", m) else m.replace(",", ".")
                try:
                    found[f"{float(v):g}" + ("%" if pct else "")] += 1
                except ValueError:
                    pass
        out.append(found)
    return out


def missing_numbers(before, after):
    """Numbers in BEFORE that appear nowhere in AFTER: {slide no: [numbers]}."""
    kept = set().union(*_numbers(Presentation(after)))
    return {i: sorted(set(nums) - kept, key=_num_key) for i, nums in enumerate(_numbers(Presentation(before)), 1)
            if set(nums) - kept}


def fewer_numbers(before, after):
    """Numbers AFTER still has, but fewer times than BEFORE: {number: (before, after)}.

    A number that vanished from one slide can hide behind the same value on
    another ("mục tiêu 2%" gone, "2 lần" kept). A lower count is that warning.
    """
    b, a = sum(_numbers(Presentation(before)), Counter()), sum(_numbers(Presentation(after)), Counter())
    return {n: (b[n], a[n]) for n in sorted(b, key=_num_key) if 0 < a[n] < b[n]}


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
            for k, (tag, colour) in enumerate((("lnL", side), ("lnR", side), ("lnT", rule), ("lnB", rule))):
                pr.insert(k, _line(tag, colour, 0.75))
            colour = head_fill if head else fill_map.get(old, body_fill)
            if colour:
                E.SubElement(E.SubElement(pr, qn("a:solidFill")), qn("a:srgbClr"), val=colour)
                pr.insert(4, pr[-1])  # a fill comes right after the four borders
            else:
                pr.insert(4, E.Element(qn("a:noFill")))
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
    thumbs = [Image.frombytes("RGB", (p.width, p.height), p.samples)
              for p in (page.get_pixmap(matrix=fitz.Matrix(320 / page.rect.width, 320 / page.rect.width)) for page in doc)]
    th = max(t.height for t in thumbs)
    for start in range(0, len(thumbs), 20):
        batch = thumbs[start:start + 20]
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
                part = slide.part.related_part(rid)
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
        px = list(Image.open(io.BytesIO(blob)).convert("L").resize((9, 8)).getdata())
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
        weak, missing, holes = [], [], []
        old_spread = Counter(h for m in old_media for h in m)  # the old theme's art, logos
        for n, row in sorted(rows.items()):
            group, olds = row.get("group", "reskin"), row.get("old", [])
            wrong = [o for o in olds if not 1 <= o <= len(old.slides)]
            if n > len(new.slides):
                holes.append(f"the map has new slide {n}, the deck has {len(new.slides)}")
            if wrong:
                holes.append(f"new slide {n} names old slide {wrong[0]}, the original has {len(old.slides)}")
            if not olds or group == "rebuild" or n > len(new.slides) or wrong:
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
