from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, sys, time
from pathlib import Path
from dukas_tick_lab import load, spec as month_spec, LAB_VERSION

REQ=("opportunities","trades","wins","gross_profit","gross_loss","net_profit","max_balance_dd","max_equity_dd","avg_hold_ms")

def _load(path:Path):
    name="delta_candidate_"+hashlib.sha1(str(path).encode()).hexdigest()[:12]
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod

def _atomic(path:Path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(obj,indent=2)+"\n"); os.replace(tmp,path)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate",type=Path,required=True); ap.add_argument("--candidate-id",required=True); ap.add_argument("--version",required=True); ap.add_argument("--month",type=int,choices=range(1,8),required=True); ap.add_argument("--cache-root",type=Path,required=True); ap.add_argument("--results-root",type=Path,required=True); ap.add_argument("--config",default="{}")
    a=ap.parse_args(); config=json.loads(a.config); meta,t,ask,bid=load(a.cache_root,a.month)
    job=f"{a.candidate_id}__{a.version}__2026_{a.month:02d}"; out=a.results_root/(job+".json")
    if out.exists() and json.loads(out.read_text()).get("status")=="LOCAL_COMPLETE": print(out); return
    start=time.perf_counter(); mod=_load(a.candidate); result=mod.run_month(t,ask,bid,config)
    missing=[k for k in REQ if k not in result]
    if missing: raise RuntimeError(f"candidate missing metrics: {missing}")
    payload={"schema":"delta-month-result-v1","status":"LOCAL_COMPLETE","lab_version":LAB_VERSION,"job_id":job,"candidate_id":a.candidate_id,"version":a.version,"month":a.month,"source_sha256":month_spec(a.month)["sha256"],"ticks":len(t),"config":config,"runtime_seconds":time.perf_counter()-start,"metrics":result}
    _atomic(out,payload); print(json.dumps(payload,indent=2))
if __name__=="__main__": main()
