#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):
            h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",required=True)
    ap.add_argument("--manifest",default=str(Path(__file__).with_name("r9_cloud_corpus_manifest_public.json")))
    ap.add_argument("--month",type=int,action="append")
    args=ap.parse_args()
    root=Path(args.data_dir)
    m=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    wanted=set(args.month or [x["month"] for x in m["months"]])
    failures=[]; checked=[]
    for x in m["months"]:
        if x["month"] not in wanted:
            continue
        p=root/x["filename"]
        rec={"month":x["month"],"path":str(p),"exists":p.exists()}
        if p.exists():
            rec["size_bytes"]=p.stat().st_size
            rec["sha256"]=sha256(p)
            rec["size_ok"]=rec["size_bytes"]==x["size_bytes"]
            rec["sha_ok"]=rec["sha256"].lower()==x["sha256"].lower()
            if not (rec["size_ok"] and rec["sha_ok"]):
                failures.append(rec)
        else:
            failures.append(rec)
        checked.append(rec)
    print(json.dumps({"status":"PASS" if not failures else "FAIL","checked":checked,"failures":failures},indent=2))
    return 0 if not failures else 2

if __name__=="__main__":
    raise SystemExit(main())
