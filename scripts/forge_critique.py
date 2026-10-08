#!/usr/bin/env python3
"""Measurable critique of a finished deck (T031).

PPTEval (PPTAgent, MIT) judges presentations on Content, Design and Coherence
with an LLM on a 1-5 scale. This critique keeps those three dimensions and
adds Motion, but scores them from measurements so an agent can act on them:
type levels, words per slide, whitespace and visual balance (from PowerPoint
render frames when available), motion vocabulary, lifecycles, click rhythm.
Thresholds come from knowledge/: Microsoft designer themes (4-5 type sizes)
and 797 real decks (median 2 effects per animated deck, 93% entrances).

    forge_critique.py deck.pptx [--render DIR]     # DIR from `slide_forge.py render`
"""
import argparse
import json
import statistics
import sys
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parent))
import deck_dna  # noqa: E402

NS=deck_dna.NS


def _frame_metrics(strip,bg_hex=None):
    """Whitespace share and centre-of-mass offset of the slide's final frame."""
    im=Image.open(strip).convert("RGB")
    w=im.width//6
    f=im.crop((5*w,0,6*w,im.height)).resize((160,90))
    px=list(f.getdata())
    bg=tuple(int(bg_hex[i:i+2],16) for i in (0,2,4)) if bg_hex else Counter(px).most_common(1)[0][0]
    ink=[(i%160,i//160) for i,p in enumerate(px) if sum(abs(a-b) for a,b in zip(p,bg))>60]
    if not ink:
        return {"whitespace":1.0,"balance_offset":0.0}
    cx=sum(x for x,_ in ink)/len(ink)/160
    cy=sum(y for _,y in ink)/len(ink)/90
    return {"whitespace":round(1-len(ink)/len(px),3),"balance_offset":round(((cx-0.5)**2+(cy-0.5)**2)**0.5,3)}


def _score(value,good,ok):
    """5 inside ``good`` (lo,hi), 3 inside ``ok``, else 1."""
    if good[0]<=value<=good[1]:
        return 5
    if ok[0]<=value<=ok[1]:
        return 3
    return 1


def critique(path,render=None):
    z=zipfile.ZipFile(path)
    parts,pres=deck_dna._slides(z)
    size=pres.find("p:sldSz",NS)
    sw,sh=int(size.get("cx")),int(size.get("cy"))
    names={}
    lib=Path(__file__).resolve().parents[1]/"knowledge"/"powerpoint_presets.json"
    if lib.is_file():
        for p in json.loads(lib.read_text(encoding="utf-8"))["presets"]:
            names.setdefault(f"{p['presetClass']}:{p['presetID']}:{p['presetSubtype']}",p["name"])
    namer=lambda k:names.get(k) or ("custom-path" if k.startswith("path:0") else k)
    slides=[]
    vocab=Counter()
    fonts=Counter()
    for i,part in enumerate(parts,1):
        root=deck_dna._xml(z,part)
        d=deck_dna.slide_design(root,sw,sh)
        m,presets,n=deck_dna.motion_dna(root)
        chains,groups=deck_dna.phrases(root,namer)
        vocab.update({namer(k):v for k,v in presets.items()})
        for r in root.iter(f"{{{deck_dna.A}}}latin"):
            if r.get("typeface"):
                fonts[r.get("typeface")]+=1
        words=sum(len((t.text or "").split()) for t in root.iter(f"{{{deck_dna.A}}}t"))
        s={"slide":i,"type_levels":len({round(x) for x in d["sizes"]}),"min_pt":min(d["sizes"],default=None),
           "words":words,"shapes":d["shapes"],"effects":n,"clicks":m.get("click_groups",0),
           "lifecycles":len(chains),"morph":bool(m.get("transition:morph")),
           "loops":m.get("repeat",0)}
        strip=Path(render)/f"slide-{i:02d}.png" if render else None
        if strip and strip.is_file():
            s.update(_frame_metrics(strip))
        slides.append(s)
    issues=[]

    def flag(dim,slide,code,detail,fix):
        issues.append({"dimension":dim,"slide":slide,"code":code,"detail":detail,"fix":fix})

    for s in slides:
        if s["words"]>70:
            flag("content",s["slide"],"WORDY",f"{s['words']} words","cut to the claim and its evidence (designer decks: ~40)")
        if s["type_levels"]>5:
            flag("design",s["slide"],"TYPE_LEVELS",f"{s['type_levels']} text sizes","use the theme scale (designer themes: 4-5 sizes)")
        # Background share of the final frame. Calibrated on PowerPoint renders of
        # Forge/Office-theme decks (82-96%); ponytail: one threshold for all layouts.
        if s.get("whitespace") is not None and not 0.6<=s["whitespace"]<=0.97:
            flag("design",s["slide"],"DENSITY",f"background {s['whitespace']:.0%} of the frame",
                 "too crowded: split the slide" if s["whitespace"]<0.6 else "nearly empty: enlarge the content or merge slides")
        if s.get("balance_offset",0)>0.22:
            flag("design",s["slide"],"BALANCE",f"visual weight {s['balance_offset']:.2f} off centre","rebalance: move or enlarge the lighter side")
        if s["clicks"]>8:
            flag("motion",s["slide"],"CLICK_FATIGUE",f"{s['clicks']} clicks","merge reveals into fewer beats")
        if s["effects"] and s["clicks"] and s["effects"]/s["clicks"]>12:
            flag("motion",s["slide"],"BUSY_CLICK",f"{s['effects']/s['clicks']:.1f} effects per click","fewer simultaneous movements")
    static=[s["slide"] for s in slides if not s["effects"] and not s["morph"]]
    if static and len(static)/len(slides)>0.3:
        flag("motion",None,"STATIC_DECK",f"{len(static)} of {len(slides)} slides never move","give structure (pictures, process, data) motion")
    distinct=len(vocab)
    if 0<distinct<3:
        flag("motion",None,"MONOTONE",f"only {distinct} effect kinds (the average real deck uses 2)",
             "use a richer style (dynamic/cinematic) or lifecycles (enter, move, dim, exit)")
    if distinct>14:
        flag("motion",None,"CHAOTIC",f"{distinct} effect kinds","one motion language per deck")
    if len([f for f in fonts if not f.startswith("+")])>3:
        flag("coherence",None,"FONTS",f"{len(fonts)} typefaces","one or two families")

    lifecycles=sum(s["lifecycles"] for s in slides)
    animated=[s for s in slides if s["effects"]]
    ws=[s["whitespace"] for s in slides if "whitespace" in s]
    scores={
        "content":_score(statistics.median([s["words"] for s in slides]) if slides else 0,(5,45),(0,80)),
        "design":round(statistics.mean(
            [_score(s["type_levels"],(2,5),(1,7)) for s in slides]+
            [_score(s["whitespace"],(0.75,0.95),(0.6,0.97)) for s in slides if "whitespace" in s]),1) if slides else 0,
        "motion":round(statistics.mean([_score(distinct,(3,10),(2,14)),
                                        _score(len(animated)/max(1,len(slides)),(0.7,1.0),(0.4,1.0)),
                                        _score(lifecycles,(1,10**6),(0,10**6))]),1),
        "coherence":_score(len([f for f in fonts if not f.startswith("+")]) or 1,(1,2),(1,3)),
    }
    for dim in ("content","design","motion","coherence"):
        scores[dim]=max(1,round(scores[dim]-0.5*sum(1 for x in issues if x["dimension"]==dim and x["slide"] is None),1))
    return {"deck":str(path),"scores":scores,"issues":issues,
            "summary":{"slides":len(slides),"effect_kinds":distinct,"top_effects":vocab.most_common(8),
                       "lifecycles":lifecycles,"static_slides":static,
                       "median_words":statistics.median([s["words"] for s in slides]) if slides else 0,
                       "median_whitespace":statistics.median(ws) if ws else None},
            "slides":slides}


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx",type=Path)
    ap.add_argument("--render",type=Path)
    a=ap.parse_args()
    print(json.dumps(critique(a.pptx,a.render),indent=1,ensure_ascii=False))


if __name__=="__main__":
    main()
