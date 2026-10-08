#!/usr/bin/env python3
"""A legible deck theme from one brand colour (T030).

Works in OKLCH (Björn Ottosson's OKLab, public domain), where equal lightness
steps look equal. Like Adobe Leonardo (Apache-2.0), colours are chosen by
contrast target rather than by fixed tints: every text role is guaranteed
WCAG AA (4.5:1) on the background and on card surfaces, and the brand hue is
kept while its lightness moves only as far as legibility demands.

    brand_palette.py "#E06C4F" [--dark]
"""
import argparse
import json
import math


def _lin(c):
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4


def _gam(c):
    return 12.92*c if c<=0.0031308 else 1.055*c**(1/2.4)-0.055


def hex_to_oklch(h):
    r,g,b=(_lin(int(h.lstrip("#")[i:i+2],16)/255) for i in (0,2,4))
    l=(0.4122214708*r+0.5363325363*g+0.0514459929*b)**(1/3)
    m=(0.2119034982*r+0.6806995451*g+0.1073969566*b)**(1/3)
    s=(0.0883024619*r+0.2817188376*g+0.6299787005*b)**(1/3)
    L=0.2104542553*l+0.7936177850*m-0.0040720468*s
    a=1.9779984951*l-2.4285922050*m+0.4505937099*s
    bb=0.0259040371*l+0.7827717662*m-0.8086757660*s
    return L,math.hypot(a,bb),math.degrees(math.atan2(bb,a))%360


def _oklch_to_rgb(L,C,H):
    a,b=C*math.cos(math.radians(H)),C*math.sin(math.radians(H))
    l=(L+0.3963377774*a+0.2158037573*b)**3
    m=(L-0.1055613458*a-0.0638541728*b)**3
    s=(L-0.0894841775*a-1.2914855480*b)**3
    return (4.0767416621*l-3.3077115913*m+0.2309699292*s,
            -1.2684380046*l+2.6097574011*m-0.3413193965*s,
            -0.0041960863*l-0.7034186147*m+1.7076147010*s)


def oklch_to_hex(L,C,H):
    """Nearest in-gamut sRGB: chroma is reduced until the colour fits."""
    L=min(1.0,max(0.0,L))
    for _ in range(40):
        rgb=_oklch_to_rgb(L,C,H)
        if all(-1e-4<=v<=1+1e-4 for v in rgb):
            break
        C*=0.92
    return "".join(f"{round(_gam(min(1,max(0,v)))*255):02X}" for v in rgb)


def contrast(a,b):
    def lum(h):
        r,g,b_=(_lin(int(h[i:i+2],16)/255) for i in (0,2,4))
        return 0.2126*r+0.7152*g+0.0722*b_
    hi,lo=sorted((lum(a),lum(b)),reverse=True)
    return (hi+0.05)/(lo+0.05)


def _to_contrast(L,C,H,backs,target,toward_dark):
    """Move lightness (keeping hue) until the colour reaches ``target`` on all backs."""
    for step in range(0,101):
        Lx=L-step*0.01 if toward_dark else L+step*0.01
        h=oklch_to_hex(Lx,C,H)
        if all(contrast(h,b)>=target for b in backs):
            return h
    return oklch_to_hex(0.0 if toward_dark else 1.0,0,H)


def brand_theme(seed,mode="light",harmony=150):
    """Forge theme dict from a brand colour. ``harmony`` rotates the hue of the
    secondary accent (150 = split complement; 30 = analogous)."""
    L,C,H=hex_to_oklch(seed)
    dark=mode=="dark"
    bg=oklch_to_hex(0.18 if dark else 0.985,min(C,0.03),H)
    surface=oklch_to_hex(0.24 if dark else 0.955,min(C,0.035),H)
    text=oklch_to_hex(0.96 if dark else 0.24,min(C,0.03),H)
    backs=[bg,surface]
    muted=_to_contrast(0.75 if dark else 0.48,min(C,0.04),H,backs,4.6,not dark)
    accent=_to_contrast(L,C,H,backs,4.6,not dark)
    accent2=_to_contrast(L,C*0.9,(H+harmony)%360,backs,4.6,not dark)
    return {"bg":bg,"surface":surface,"text":text,"muted":muted,"accent":accent,"accent2":accent2,
            "seed":seed.lstrip("#").upper()}


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seed")
    ap.add_argument("--dark",action="store_true")
    ap.add_argument("--harmony",type=float,default=150)
    a=ap.parse_args()
    print(json.dumps(brand_theme(a.seed,"dark" if a.dark else "light",a.harmony),indent=1))


if __name__=="__main__":
    main()
