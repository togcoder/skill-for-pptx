#!/usr/bin/env python3
"""Motion phrases from the most motion-complex corpus decks (T027).

    phrase_scan.py knowledge/corpus_motion_design.json local-media/corpus/zenodo_dna.jsonl -n 60 -o knowledge/motion_phrases.json
"""
import argparse
import json
import sys
import urllib.parse
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import deck_dna  # noqa: E402
from corpus_scan import BASE  # noqa: E402
from knowledge_build import _names  # noqa: E402


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("knowledge",type=Path)
    ap.add_argument("jsonl",type=Path)
    ap.add_argument("-n",type=int,default=60)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    rows=[json.loads(l) for l in a.jsonl.read_text(encoding="utf-8").splitlines() if l.strip()]
    top=sorted([r for r in rows if r.get("motion_complexity")],key=lambda r:-r["motion_complexity"])[:a.n]
    names=_names()

    def namer(k):
        cls,pid,sub=k.split(":")
        return names.get(k) or names.get(f"{cls}:{pid}") or ("custom-path" if cls=="path" else k)

    def job(r):
        f=deck_dna.RangeFile(BASE+urllib.parse.quote(r["path"]))
        chains,groups=[],[]
        with zipfile.ZipFile(f) as z:
            parts,_=deck_dna._slides(z)
            for part in parts[:80]:
                root=deck_dna._xml(z,part)
                if root is not None:
                    c,g=deck_dna.phrases(root,namer)
                    chains+=c
                    groups+=g
        return chains,groups

    chains=Counter()
    shapes=Counter()
    sizes=[]
    staggered=0
    with ThreadPoolExecutor(10) as pool:
        for c,g in pool.map(job,top):
            chains.update(" > ".join(x) for x in c)
            for grp in g:
                sizes.append(grp["n"])
                staggered+=grp["staggered"]
                shapes[" + ".join(grp["kinds"])+(" [staggered]" if grp["staggered"] else "")]+=1
    out={"decks":len(top),"click_groups":len(sizes),
         "effects_per_click":{"mean":round(sum(sizes)/max(1,len(sizes)),2),
                              "share_multi":round(sum(n>1 for n in sizes)/max(1,len(sizes)),3)},
         "staggered_share":round(staggered/max(1,len(sizes)),3),
         "object_lifecycles":chains.most_common(40),
         "click_group_shapes":shapes.most_common(40)}
    a.output.write_text(json.dumps(out,indent=1,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False)[:2500])


if __name__=="__main__":
    main()
