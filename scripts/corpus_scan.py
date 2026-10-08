#!/usr/bin/env python3
"""Scan a sample of the Zenodo10K corpus (licensed .pptx on Hugging Face) for
design + motion DNA via HTTP Range reads (T027). Appends JSON lines.

    corpus_scan.py INDEX.json -n 800 -o local-media/corpus/zenodo_dna.jsonl
"""
import argparse
import json
import random
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import deck_dna  # noqa: E402

BASE="https://huggingface.co/datasets/Forceless/Zenodo10K/resolve/main/"
SKIP_LICENCES={"other-closed"}


def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("index",type=Path)
    ap.add_argument("-n",type=int,default=800)
    ap.add_argument("-o","--output",type=Path,required=True)
    ap.add_argument("--seed",type=int,default=27)
    ap.add_argument("--workers",type=int,default=12)
    a=ap.parse_args()
    files=[f for f in json.loads(a.index.read_text()) if f["path"].split("/")[1] not in SKIP_LICENCES
           and f["path"].lower().endswith(".pptx")]
    done=set()
    if a.output.is_file():
        done={json.loads(l)["path"] for l in a.output.read_text(encoding="utf-8").splitlines() if l.strip()}
    sample=[f for f in random.Random(a.seed).sample(files,min(a.n,len(files))) if f["path"] not in done]

    def job(f):
        url=BASE+urllib.parse.quote(f["path"])
        try:
            d=deck_dna.dna(url,remote=True)
        except Exception as exc:
            d={"error":f"{type(exc).__name__}: {exc}"[:200]}
        d.update(path=f["path"],licence=f["path"].split("/")[1],size=f["size"])
        return d

    ok=0
    with open(a.output,"a",encoding="utf-8") as out, ThreadPoolExecutor(a.workers) as pool:
        for i,fut in enumerate(as_completed([pool.submit(job,f) for f in sample]),1):
            d=fut.result()
            ok+=("error" not in d)
            out.write(json.dumps(d,ensure_ascii=False)+"\n")
            out.flush()
            if i%50==0:
                print(f"{i}/{len(sample)} ok={ok}",flush=True)
    print(f"done {len(sample)} ok={ok}")


if __name__=="__main__":
    main()
