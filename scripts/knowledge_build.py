#!/usr/bin/env python3
"""Aggregate corpus DNA into knowledge the tools can use (T027).

    knowledge_build.py local-media/corpus/zenodo_dna.jsonl -o knowledge/corpus_motion_design.json

Output: how real decks animate (share animated, effect vocabulary ranked and
named via the PowerPoint preset library, compound features), how they are
typeset, and the most motion-complex decks to study by eye.
"""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

LIB=Path(__file__).resolve().parents[1]/"knowledge"/"powerpoint_presets.json"


def _names():
    out={}
    if LIB.is_file():
        for p in json.loads(LIB.read_text(encoding="utf-8"))["presets"]:
            out.setdefault(f"{p['presetClass']}:{p['presetID']}:{p['presetSubtype']}",p["name"])
            out.setdefault(f"{p['presetClass']}:{p['presetID']}",p["name"])
    return out


def q(values,qs=(0.25,0.5,0.75,0.9)):
    v=sorted(values)
    return {f"p{int(x*100)}":v[min(len(v)-1,int(x*len(v)))] for x in qs} if v else {}


def build(rows):
    names=_names()
    ok=[r for r in rows if "error" not in r and r.get("slides")]
    animated=[r for r in ok if r["motion"].get("effects")]
    presets=Counter()
    for r in animated:
        for k,v in r["presets"].items():
            presets[k]+=v
    def name(k):
        cls,pid,sub=k.split(":")
        return names.get(k) or names.get(f"{cls}:{pid}") or ("custom-path" if cls=="path" and pid=="0" else k)
    named=Counter()
    for k,v in presets.items():
        named[name(k)]+=v
    feat=Counter()
    for r in ok:
        m=r["motion"]
        for key in ("custom_path","repeat","auto_reverse","interactive_sequences","text_build","chart_or_diagram_build","transition:morph"):
            feat[key]+=m.get(key,0)>0
        feat["any_transition"]+=any(k.startswith("transition:") for k in m)
    trans=Counter()
    for r in ok:
        for k,v in r["motion"].items():
            if k.startswith("transition:"):
                trans[k[11:]]+=v
    d=[r["design"] for r in ok if r["design"].get("median_pt")]
    complex_=sorted(animated,key=lambda r:-r["motion_complexity"])[:25]
    return {
        "source":"Zenodo10K sample (licensed pptx, Hugging Face Forceless/Zenodo10K), XML-only DNA",
        "decks_scanned":len(ok),"errors":len(rows)-len(ok),
        "animated_share":round(len(animated)/max(1,len(ok)),3),
        "animated_slide_share":round(sum(r["animated_slides"] for r in ok)/max(1,sum(min(r["slides"],80) for r in ok)),3),
        "effects_per_animated_deck":q([r["motion"]["effects"] for r in animated]),
        "max_effects_on_one_slide":q([r["max_effects_slide"] for r in animated]),
        "vocabulary_per_animated_deck":q([len(r["presets"]) for r in animated]),
        "class_share":{c:round(sum(r["motion"].get("class:"+c,0) for r in animated)/max(1,sum(r["motion"]["effects"] for r in animated)),3)
                       for c in ("entr","exit","emph","path")},
        "trigger_share":{t:round(sum(r["motion"].get("node:"+t,0) for r in animated)/max(1,sum(r["motion"]["effects"] for r in animated)),3)
                         for t in ("clickEffect","withEffect","afterEffect")},
        "top_effects":named.most_common(30),
        "feature_deck_counts":dict(feat),
        "transitions":trans.most_common(15),
        "design":{
            "type_levels":q([x["type_levels"] for x in d]),
            "max_pt":q([x["max_pt"] for x in d]),
            "median_pt":q([x["median_pt"] for x in d]),
            "chars_per_slide":q([x["chars_per_slide"] for x in d]),
            "shapes_per_slide":q([x["shapes_per_slide"] for x in d]),
            "picture_coverage":q([x["picture_coverage"] for x in d]),
            "fonts":Counter(f for r in ok for f in (r["theme"].get("fonts") or {}).values() if f).most_common(15),
        },
        "most_complex":[{"path":r["path"],"licence":r["licence"],"slides":r["slides"],"effects":r["motion"]["effects"],
                         "vocabulary":len(r["presets"]),"complexity":r["motion_complexity"],
                         "top":[name(k) for k in list(r["presets"])[:6]]} for r in complex_],
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jsonl",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    rows=[json.loads(l) for l in a.jsonl.read_text(encoding="utf-8").splitlines() if l.strip()]
    k=build(rows)
    a.output.write_text(json.dumps(k,indent=1,ensure_ascii=False),encoding="utf-8")
    print(json.dumps({x:k[x] for x in k if x not in ("most_complex",)},ensure_ascii=False)[:3000])


if __name__=="__main__":
    main()
