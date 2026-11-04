#!/usr/bin/env python3
"""Text measurement shared by Forge, the Director and the motion components.

One font map and one width model, so a fitted text box, a highlight marker and
a rise mask all agree about where the words actually are. Pillow measures the
real font file when it is installed; otherwise a 0.55 em average is used.
"""
import math
from pathlib import Path

from PIL import ImageFont

# Font files for the families the lab uses. The first existing file wins.
FONT_FILES={
    "segoe ui":["segoeui.ttf","DejaVuSans.ttf"],"segoe ui bold":["segoeuib.ttf","DejaVuSans-Bold.ttf"],
    "segoe ui semibold":["seguisb.ttf","segoeuib.ttf","DejaVuSans-Bold.ttf"],
    "segoe ui semibold bold":["segoeuib.ttf","DejaVuSans-Bold.ttf"],
    "arial":["arial.ttf","LiberationSans-Regular.ttf"],"arial bold":["arialbd.ttf","LiberationSans-Bold.ttf"],
    "calibri":["calibri.ttf","Carlito-Regular.ttf"],"calibri bold":["calibrib.ttf","Carlito-Bold.ttf"],
    "calibri light":["calibril.ttf","Carlito-Regular.ttf"],"calibri light bold":["calibrib.ttf"],
    "century gothic":["GOTHIC.TTF"],"century gothic bold":["GOTHICB.TTF"],
    "trebuchet ms":["trebuc.ttf"],"trebuchet ms bold":["trebucbd.ttf"],
    "gill sans mt":["GIL_____.TTF"],"gill sans mt bold":["GILB____.TTF"],
    "garamond":["GARA.TTF"],"garamond bold":["GARABD.TTF"],
    "tw cen mt":["TCM_____.TTF"],"tw cen mt bold":["TCB_____.TTF"],
    "tw cen mt condensed":["TCCM_____.TTF","TCM_____.TTF"],"tw cen mt condensed bold":["TCCB_____.TTF","TCB_____.TTF"],
    "georgia":["georgia.ttf"],"georgia bold":["georgiab.ttf"],"verdana":["verdana.ttf"],"verdana bold":["verdanab.ttf"],
}
SAFETY=1.06  # renderer kerning/hinting differs slightly from Pillow's metrics
FONT_DIRS=[Path("C:/Windows/Fonts"),Path("/usr/share/fonts"),Path("/Library/Fonts"),Path.home()/".fonts"]
_font_cache={}
_path_cache={}


def font_path(family):
    fam=(family or "").strip().lower()
    if fam not in _path_cache:
        _path_cache[fam]=None
        for name in FONT_FILES.get(fam,[]):
            for d in FONT_DIRS:
                if (d/name).is_file():
                    _path_cache[fam]=d/name
                elif d.is_dir() and d.name!="Fonts":
                    _path_cache[fam]=next(d.rglob(name),None)
                if _path_cache[fam]:
                    return _path_cache[fam]
    return _path_cache[fam]


def load_font(family,size_pt):
    """Pillow font loaded at 4 px per point (the Forge fitting resolution)."""
    key=((family or "").strip().lower(),size_pt)
    if key not in _font_cache:
        path=font_path(family)
        _font_cache[key]=ImageFont.truetype(str(path),size=max(1,round(size_pt*4))) if path else None
    return _font_cache[key]


def width_pt(text,family,size_pt,bold=False):
    """Natural single-line width in points, with Forge's 1.06 safety margin."""
    fam=family or ""
    if bold and (fam.lower()+" bold") in FONT_FILES:
        fam=fam+" bold"
    font=load_font(fam,size_pt)
    raw=font.getlength(str(text)) if font else len(str(text))*size_pt*4*(0.6 if bold else 0.55)
    return raw/4*SAFETY


def wrap_lines(text,family,size_pt,width_in,bold=False):
    """Lines after word wrap, or inf when one word is wider than the box."""
    width_pt_=width_in*72
    if any(width_pt(word,family,size_pt,bold)>width_pt_ for word in str(text).split()):
        return math.inf
    lines=0
    for para in str(text).split("\n"):
        words=para.split() or [""]
        cur=""
        n=1
        for word in words:
            trial=(cur+" "+word).strip()
            if width_pt(trial,family,size_pt,bold)<=width_pt_ or not cur:
                cur=trial
            else:
                n+=1
                cur=word
        lines+=n
    return lines
