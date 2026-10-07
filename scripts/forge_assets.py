#!/usr/bin/env python3
"""Online assets for Slide Forge (T026): licensed photos and open-source icons.

Photos come from Openverse (CC0 / CC BY / CC BY-SA, commercial use and
modification allowed; mostly Wikimedia Commons and Flickr) or, when the user
supplies PEXELS_API_KEY, from Pexels. Icons come from Iconify (Lucide ISC,
Tabler MIT, Phosphor MIT, Material Design Icons Apache-2.0).

Everything is cached under a directory the caller chooses, so a spec that says
``{"search": "coffee roastery", "pick": 2}`` keeps resolving to the same file
after the first build. Every photo carries its attribution; Forge prints it on
the slide and in the verdict.

    forge_assets.py photos "coffee roastery" -d cache   # candidates + contact sheet for the agent
    forge_assets.py icons "growth"                      # icon names
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

UA={"User-Agent":"skill-for-pptx/0.11 (+https://github.com/togcoder/skill-for-pptx)"}
OPENVERSE="https://api.openverse.org/v1/images/"
ICONIFY="https://api.iconify.design"
ICON_SETS=("lucide","tabler","ph")
MAX_BYTES=25_000_000
LICENSE_RANK={"cc0":0,"pdm":0,"pexels":0,"by":1,"by-sa":2}


def _get(url,headers=None,limit=MAX_BYTES,tries=3):
    req=urllib.request.Request(url,headers={**UA,**(headers or {})})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req,timeout=40) as r:
                data=r.read(limit+1)
            break
        except (OSError,urllib.error.URLError) as exc:  # resets and timeouts are common on public APIs
            if attempt==tries-1 or getattr(exc,"code",500)<500 and getattr(exc,"code",None) not in (None,429):
                raise
            time.sleep(1.5*(attempt+1))
    if len(data)>limit:
        raise ValueError(f"{url}: larger than {limit} bytes")
    return data


def _key(*parts):
    return hashlib.sha256("|".join(map(str,parts)).encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Photos


def search_photos(query,cache,n=12,orientation="landscape"):
    """Candidate list (cached per query): id, thumb, url, width, height,
    license, attribution, landing, source."""
    cache=Path(cache)
    cache.mkdir(parents=True,exist_ok=True)
    provider="pexels" if os.environ.get("PEXELS_API_KEY") else "openverse"
    path=cache/f"search-{provider}-{_key(query,n,orientation)}.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    out=[]
    if provider=="pexels":
        q=urllib.parse.urlencode({"query":query,"per_page":n,"orientation":orientation})
        data=json.loads(_get(f"https://api.pexels.com/v1/search?{q}",{"Authorization":os.environ["PEXELS_API_KEY"]}))
        for p in data.get("photos",[]):
            out.append({"id":f"pexels-{p['id']}","thumb":p["src"]["medium"],"url":p["src"]["large2x"],
                        "width":p["width"],"height":p["height"],"license":"pexels","license_url":"https://www.pexels.com/license/",
                        "attribution":f"Photo by {p['photographer']} on Pexels","landing":p["url"],"source":"pexels"})
    else:
        aspect={"landscape":"wide","portrait":"tall","square":"square"}.get(orientation,"wide")
        seen=set()
        # Large files first; relax the size filter when that pool is thin.
        # Anonymous Openverse caps page_size at 20.
        for size in ("large",None):
            params={"q":query,"license_type":"commercial,modification","aspect_ratio":aspect,
                    "page_size":20,"mature":"false",**({"size":size} if size else {})}
            data=json.loads(_get(OPENVERSE+"?"+urllib.parse.urlencode(params)))
            for r in data.get("results",[]):
                if r["id"] in seen or r.get("license") not in LICENSE_RANK or r.get("mature"):
                    continue
                if 0<(r.get("width") or 0)<1200:
                    continue  # too small to fill a slide
                if r.get("category") in ("illustration","digitized_artwork") or re.search(
                        r"clip ?art|illustration|vector|icon|\bpng\b|mockup|template",r.get("title") or "",re.I):
                    continue  # photos only; illustrations rarely match a deck's style
                seen.add(r["id"])
                ver=r.get("license_version") or ""
                out.append({"id":f"ov-{r['id']}","thumb":r.get("thumbnail") or r["url"],"url":r["url"],
                            "width":r.get("width") or 0,"height":r.get("height") or 0,
                            "license":r["license"],"license_url":r.get("license_url"),
                            "attribution":_short_credit(r,ver),"landing":r.get("foreign_landing_url"),"source":r.get("source")})
            if len(out)>=n:
                break
        out=out[:n]
    path.write_text(json.dumps(out,indent=1,ensure_ascii=False),encoding="utf-8")
    return out


def _short_credit(r,ver):
    title=(r.get("title") or "Untitled").strip()
    title=re.sub(r"\.(jpe?g|png|tiff?)$","",title,flags=re.I)[:60]
    who=(r.get("creator") or "unknown").strip()[:40]
    lic={"cc0":"CC0","pdm":"Public Domain","by":f"CC BY {ver}","by-sa":f"CC BY-SA {ver}"}[r["license"]].strip()
    return f"“{title}” by {who}, {lic}"


def fetch_photo(cand,cache,max_px=2400):
    """Download once, validate, downscale, store as JPEG next to a license sidecar."""
    cache=Path(cache)
    dst=cache/f"{cand['id']}.jpg"
    if not dst.is_file():
        img=Image.open(io.BytesIO(_get(cand["url"])))
        img.load()
        img=img.convert("RGB")
        img.thumbnail((max_px,max_px))
        img.save(dst,"JPEG",quality=88,optimize=True)
        (cache/f"{cand['id']}.json").write_text(json.dumps(cand,indent=1,ensure_ascii=False),encoding="utf-8")
    return dst


def resolve_photo(ref,cache,box_ratio=16/9):
    """``{"search": q, "pick": i?, "orientation"?}`` -> (path, candidate).
    Without ``pick`` the best-scored candidate is used: licence first, then how
    well its aspect ratio fits the box, then resolution."""
    orientation=ref.get("orientation") or ("portrait" if box_ratio<0.9 else "square" if box_ratio<1.2 else "landscape")
    cands=search_photos(ref["search"],cache,orientation=orientation)
    if not cands:
        raise LookupError(f"no licensed photo for {ref['search']!r}")
    if "pick" in ref:
        cand=cands[int(ref["pick"])]
    else:
        def score(c):
            r=(c["width"]/c["height"]) if c["height"] else box_ratio
            return (LICENSE_RANK[c["license"]],round(abs(r-box_ratio),1),-(c["width"]*c["height"]))
        cand=min(cands,key=score)
    errors=[]
    for c in [cand]+[c for c in cands if c is not cand]:
        try:
            return fetch_photo(c,cache),c
        except Exception as exc:  # dead link or bad image: try the next candidate
            errors.append(f"{c['id']}: {exc}")
    raise LookupError("; ".join(errors))


def _thumb_bytes(c):
    """Openverse's thumbnail proxy often fails (HTTP 424) on big Commons files;
    fall back to Wikimedia's own scaler, then to the original."""
    urls=[c["thumb"]]
    m=re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/([^/]+)$",c["url"])
    if m:
        urls.append(f"{m[1]}/thumb/{m[2]}/{m[3]}/640px-{m[3]}")
    urls.append(c["url"])
    for i,u in enumerate(urls):
        try:
            return _get(u,limit=MAX_BYTES,tries=1 if i<len(urls)-1 else 2)
        except Exception:
            if i==len(urls)-1:
                raise


def contact_sheet(cands,cache,out,cols=4,tile=(360,240)):
    """Numbered thumbnails so an agent can look and choose ``pick``."""
    rows=(len(cands)+cols-1)//cols
    sheet=Image.new("RGB",(cols*tile[0],rows*(tile[1]+34)),(24,24,28))
    d=ImageDraw.Draw(sheet)
    try:
        font=ImageFont.truetype("arial.ttf",16)
    except OSError:
        font=ImageFont.load_default()
    for i,c in enumerate(cands):
        x,y=(i%cols)*tile[0],(i//cols)*(tile[1]+34)
        try:
            th=Image.open(io.BytesIO(_thumb_bytes(c))).convert("RGB")
            th.thumbnail(tile)
            sheet.paste(th,(x+(tile[0]-th.width)//2,y+(tile[1]-th.height)//2))
        except Exception:
            d.text((x+10,y+10),"thumbnail failed",fill=(200,80,80),font=font)
        d.text((x+8,y+tile[1]+6),f"[{i}] {c['width']}x{c['height']} {c['license']}",fill=(230,230,230),font=font)
    sheet.save(out)
    return out


# ---------------------------------------------------------------------------
# Icons


def search_icons(query,limit=12,sets=ICON_SETS):
    q=urllib.parse.urlencode({"query":query,"limit":64,"prefixes":",".join(sets)})
    icons=json.loads(_get(f"{ICONIFY}/search?{q}")).get("icons",[])
    return icons[:limit]


def fetch_icon(name,color,cache):
    """SVG text for ``prefix:name`` in a solid colour (hex without #)."""
    if ":" not in name:
        found=search_icons(name,1)
        if not found:
            raise LookupError(f"no icon for {name!r}")
        name=found[0]
    prefix,icon=name.split(":",1)
    cache=Path(cache)
    cache.mkdir(parents=True,exist_ok=True)
    dst=cache/f"icon-{prefix}-{icon}-{color}.svg"
    if not dst.is_file():
        svg=_get(f"{ICONIFY}/{prefix}/{icon}.svg?"+urllib.parse.urlencode({"color":"#"+color,"height":"256"}),limit=500_000)
        if b"<svg" not in svg[:200]:
            raise LookupError(f"icon {name!r} not found")
        dst.write_bytes(svg)
    return dst,name


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("photos")
    p.add_argument("query")
    p.add_argument("-d","--cache",type=Path,default=Path("forge-cache"))
    p.add_argument("-n",type=int,default=12)
    p.add_argument("--orientation",default="landscape",choices=["landscape","portrait","square"])
    i=sub.add_parser("icons")
    i.add_argument("query")
    a=ap.parse_args(argv)
    if a.cmd=="photos":
        cands=search_photos(a.query,a.cache,a.n,a.orientation)
        sheet=contact_sheet(cands,a.cache,a.cache/f"sheet-{_key(a.query,a.orientation)}.png") if cands else None
        result={"query":a.query,"sheet":str(sheet) if sheet else None,
                "candidates":[{k:c[k] for k in ("id","width","height","license","attribution","source")} for c in cands]}
    else:
        result={"query":a.query,"icons":search_icons(a.query)}
    json.dump(result,sys.stdout,indent=1,ensure_ascii=False)
    print()


if __name__=="__main__":
    main()
