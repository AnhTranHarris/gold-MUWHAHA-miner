from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
import numpy as np
import pandas as pd
from coinexx_r9_adapter import compare_logger_oracle,replay_logger_oracle,run_raw_r9,raw_result_dict

JAN_EXPECTED={"trades":31915,"wins":13947,"losses":17968,"gross_profit":3785.28,"gross_loss":-10436.90,"net_profit":-6651.62}

def oracle_file(path:Path)->dict:
    d=pd.read_csv(path); q=compare_logger_oracle(d); q["file"]=path.name; return q

def oracle_month(directory:Path,year:int,month:int)->dict:
    files=sorted(directory.glob(f"R9_REAL_{year:04d}-{month:02d}-*_ticks.csv.gz"))
    total_rows=total_mismatch=trades=wins=losses=0;gp=gl=net=0.;cs=Counter();ca=Counter();daily=[]
    for p in files:
        d=pd.read_csv(p);sim=replay_logger_oracle(d);actual=d.event.astype(str).tolist()
        mm=sum(a!=b for a,b in zip(sim["events"],actual));acc=sim["accounting"]
        total_rows+=len(d);total_mismatch+=mm;cs.update(sim["event_counts"]);ca.update(actual)
        trades+=acc["trades"];wins+=acc["wins"];losses+=acc["losses"];gp+=acc["gross_profit"];gl+=acc["gross_loss"];net+=acc["net_profit"]
        daily.append({"file":p.name,"rows":len(d),"event_mismatches":mm,"trades":acc["trades"],"wins":acc["wins"],"losses":acc["losses"],
                      "gross_profit":round(acc["gross_profit"],2),"gross_loss":round(acc["gross_loss"],2),"net_profit":round(acc["net_profit"],2)})
    out={"files":len(files),"rows":total_rows,"event_mismatches":total_mismatch,"event_counts_equal":cs==ca,
         "trades":trades,"wins":wins,"losses":losses,"gross_profit":round(gp,2),"gross_loss":round(gl,2),"net_profit":round(net,2),"daily":daily}
    if year==2026 and month==1:
        out["january_reference"]=JAN_EXPECTED
        out["january_exact"]=all(out[k]==v for k,v in JAN_EXPECTED.items()) and total_mismatch==0 and cs==ca
    return out

def dukas_month(cache_root:Path,month:int)->dict:
    d=cache_root/f"2026_{month:02d}";t=np.load(d/"t_ms.npy",mmap_mode="r");a=np.load(d/"ask_raw.npy",mmap_mode="r");b=np.load(d/"bid_raw.npy",mmap_mode="r")
    ints,fl=run_raw_r9(t,a,b,1000,0);sp=a.astype("int64")-b.astype("int64");r=raw_result_dict(ints,fl)
    r.update({"month":month,"ticks":len(t),"surface":"DUKAS_NATIVE","spread_price_median":float(np.median(sp))/1000.,
              "spread_price_p10":float(np.quantile(sp,.1))/1000.,"spread_price_p90":float(np.quantile(sp,.9))/1000.,
              "ticks_passing_coinexx_0p25_spread_gate_pct":100.*float(np.mean(sp<=250))})
    return r

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("oracle-file");p.add_argument("--path",type=Path,required=True)
    p=sub.add_parser("oracle-month");p.add_argument("--dir",type=Path,required=True);p.add_argument("--year",type=int,default=2026);p.add_argument("--month",type=int,required=True)
    p=sub.add_parser("dukas-month");p.add_argument("--cache-root",type=Path,required=True);p.add_argument("--month",type=int,choices=range(1,8),required=True)
    a=ap.parse_args()
    out=oracle_file(a.path) if a.cmd=="oracle-file" else oracle_month(a.dir,a.year,a.month) if a.cmd=="oracle-month" else dukas_month(a.cache_root,a.month)
    print(json.dumps(out,indent=2,default=float))
if __name__=="__main__":main()
