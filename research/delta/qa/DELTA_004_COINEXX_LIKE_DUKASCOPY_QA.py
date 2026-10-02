from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path

REAL_MONTHLY={
1:{"trades":31915,"wins":13947,"gross_profit":3785.28,"gross_loss":-10436.90,"net_profit":-6651.62},
2:{"trades":35394,"wins":15296,"gross_profit":6273.89,"gross_loss":-13605.10,"net_profit":-7331.21},
3:{"trades":40297,"wins":18054,"gross_profit":6719.48,"gross_loss":-13975.07,"net_profit":-7255.59},
4:{"trades":33613,"wins":14644,"gross_profit":4019.03,"gross_loss":-11048.43,"net_profit":-7029.40},
5:{"trades":31334,"wins":12655,"gross_profit":2898.99,"gross_loss":-10725.73,"net_profit":-7826.74},
6:{"trades":33603,"wins":14402,"gross_profit":3577.32,"gross_loss":-11228.84,"net_profit":-7651.52},
7:{"trades":30491,"wins":13387,"gross_profit":2906.24,"gross_loss":-9445.44,"net_profit":-6539.20}}
REAL_AGG={"trades":236647,"wins":102385,"gross_profit":30180.23,"gross_loss":-80465.51,"net_profit":-50285.28}
AGG_LIMIT={"trades":7,"wins":7,"gross_profit":10,"gross_loss_abs":10,"net_loss_abs":10}
MONTH_LIMIT={"trades":7,"wins":15,"gross_profit":20,"gross_loss_abs":15,"net_loss_abs":20}

def err(r,q):
    return {"trades":100*(r["trades"]-q["trades"])/q["trades"],"wins":100*(r["wins"]-q["wins"])/q["wins"],
            "gross_profit":100*(r["gross_profit"]-q["gross_profit"])/q["gross_profit"],
            "gross_loss_abs":100*(abs(r["gross_loss"])-abs(q["gross_loss"]))/abs(q["gross_loss"]),
            "net_loss_abs":100*(abs(r["net_profit"])-abs(q["net_profit"]))/abs(q["net_profit"])}

def atomic(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+".tmp");t.write_text(json.dumps(obj,indent=2)+"\n");os.replace(t,p)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--lab-dir",type=Path,required=True);ap.add_argument("--cache-root",type=Path,required=True);ap.add_argument("--output",type=Path)
    a=ap.parse_args();sys.path.insert(0,str(a.lab_dir))
    from coinexx_like_surface import run_control
    profiles={}
    for prof in ("P50","P75","P90"):
        months={};agg={"trades":0,"wins":0,"losses":0,"gross_profit":0.,"gross_loss":0.,"net_profit":0.}
        for m in range(1,8):
            r=run_control(a.cache_root,m,prof);months[str(m)]=r
            for k in agg:agg[k]+=r[k]
        agg["trades"]=int(agg["trades"]);agg["wins"]=int(agg["wins"]);agg["losses"]=int(agg["losses"])
        profiles[prof]={"months":months,"aggregate":agg}
    ae=err(profiles["P75"]["aggregate"],REAL_AGG)
    me={str(m):err(profiles["P75"]["months"][str(m)],REAL_MONTHLY[m]) for m in range(1,8)}
    apass=all(abs(ae[k])<=v for k,v in AGG_LIMIT.items())
    mpass=all(abs(me[str(m)][k])<=v for m in range(1,8) for k,v in MONTH_LIMIT.items())
    midpass=max(profiles["P75"]["months"][str(m)]["max_midpoint_error_price"] for m in range(1,8))<=0.005+1e-12
    out={"schema":"delta-004-rebuild-qa-v1","status":"PASS" if apass and mpass and midpass else "FAIL","default_profile":"P75",
         "profiles":profiles,"p75_aggregate_errors_pct":ae,"p75_monthly_errors_pct":me,
         "aggregate_limits_pct":AGG_LIMIT,"monthly_limits_pct":MONTH_LIMIT,
         "p75_aggregate_pass":apass,"p75_monthly_pass":mpass,"midpoint_quantization_pass":midpass,"august_accessed":False}
    if a.output:atomic(a.output,out)
    print(json.dumps(out,indent=2,default=float));return 0 if out["status"]=="PASS" else 2
if __name__=="__main__":raise SystemExit(main())
