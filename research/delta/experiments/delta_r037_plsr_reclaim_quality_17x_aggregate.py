"""Aggregate committed month-isolated DELTA R037 17X results."""
from __future__ import annotations
import argparse, hashlib, json, os, tempfile
from pathlib import Path

MONTHS=("01A","02","03","04","05","06","07")
CFG=("C01_DIRECTIONAL_RECLAIM","C02_REVERSAL_HALF_CLOSE","C03_ENGULFING_RECOVERY","C04_DIRECTIONAL_RANGE_EXPANSION")

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def atomic_json(p:Path,o:dict)->None:
    p.parent.mkdir(parents=True,exist_ok=True); n=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",dir=p.parent,prefix="."+p.name+".",suffix=".tmp",delete=False) as f:
            n=f.name; json.dump(o,f,indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(n,p); n=None
    finally:
        if n:
            try: os.unlink(n)
            except FileNotFoundError: pass

def main():
    ap=argparse.ArgumentParser()
    for m in MONTHS: ap.add_argument("--r"+m,type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    R={}; hashes={}
    for m in MONTHS:
        p=getattr(a,"r"+m); x=json.loads(p.read_text(encoding="utf-8"))
        if x.get("month")!=m or x.get("unit")!="R037_PLSR_RECLAIM_QUALITY_CROSS_MONTH_17X":
            raise SystemExit(f"17X month result identity mismatch {m}")
        if x.get("august_accessed") is not False or x.get("numeric_retuning") is not False:
            raise SystemExit(f"17X frozen-contract violation {m}")
        R[m]=x; hashes[m]=sha256(p)

    bt=sum(R[m]["baseline"]["trades"] for m in MONTHS)
    bn=round(sum(R[m]["baseline"]["direct_net_usd"] for m in MONTHS),2)
    bw=sum(R[m]["baseline"]["official_wins"] for m in MONTHS)
    summary={}
    for c in CFG:
        tr=sum(R[m]["configs"][c]["trades"] for m in MONTHS)
        wins=sum(R[m]["configs"][c]["official_wins"] for m in MONTHS)
        net=round(sum(R[m]["configs"][c]["direct_net_usd"] for m in MONTHS),2)
        mw=sum(R[m]["configs"][c]["trades"]>0 for m in MONTHS)
        nn=sum(R[m]["configs"][c]["direct_net_usd"]>=0 for m in MONTHS)
        rt=tr/bt if bt else 0.0
        gate={
          "trade_retention_fraction":rt,
          "retention_ge_0_5":rt>=0.5,
          "months_with_trades_ge_5":mw>=5,
          "nonnegative_months_ge_4":nn>=4,
          "aggregate_net_nonnegative":net>=0,
          "aggregate_net_improves_vs_baseline":net>bn,
        }
        gate["cross_month_pass"]=all(v for k,v in gate.items() if k!="trade_retention_fraction")
        summary[c]={"trades":tr,"official_wins":wins,"direct_net_usd":net,"months_with_trades":mw,"nonnegative_months":nn,"improvement_vs_baseline_usd":round(net-bn,2),"gate":gate}

    ranked=sorted(CFG,key=lambda c:(summary[c]["gate"]["cross_month_pass"],summary[c]["nonnegative_months"],summary[c]["direct_net_usd"],summary[c]["trades"]),reverse=True)
    survivors=[c for c in ranked if summary[c]["gate"]["cross_month_pass"]]
    out={
      "schema":"delta-r037-plsr-reclaim-quality-cross-month-17x-v2",
      "status":"COMPLETE_CROSS_MONTH_SCREEN",
      "unit":"R037_PLSR_RECLAIM_QUALITY_CROSS_MONTH_17X",
      "family":"R037-PLSR-RQ-v1",
      "surface":"DUKAS_COINEXX_LIKE_P75",
      "month_result_sha256":hashes,
      "baseline":{"trades":bt,"official_wins":bw,"direct_net_usd":bn},
      "summary":summary,
      "ranking":ranked,
      "finding":{"survivors":survivors,"leader":ranked[0],"next":"R037_PLSR_RQ_LEADER_FULL_SURROGATE_PARENT_CROSS_MONTH_VALIDATION" if survivors else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST"},
      "numeric_retuning":False,"post_result_retuning":False,"august_accessed":False,"mql5_authorized":False,
    }
    atomic_json(a.output,out)
    print(json.dumps({"baseline":out["baseline"],"summary":summary,"finding":out["finding"]},separators=(",",":")))

if __name__=="__main__":
    main()
