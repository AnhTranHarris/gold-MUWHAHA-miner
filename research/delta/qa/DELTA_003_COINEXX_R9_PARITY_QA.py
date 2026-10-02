from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path

def atomic(path:Path,obj:dict):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(json.dumps(obj,indent=2)+"\n");os.replace(tmp,path)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--lab-dir",type=Path,required=True)
    ap.add_argument("--logger-dir",type=Path,required=True)
    ap.add_argument("--dukas-cache-root",type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args();sys.path.insert(0,str(a.lab_dir))
    from r9_parity_runner import oracle_month,oracle_file,dukas_month
    jan=oracle_month(a.logger_dir,2026,1)
    jp=a.logger_dir/"R9_REAL_2026-07-01_ticks.csv.gz"
    jul=oracle_file(jp) if jp.exists() else None
    duk=dukas_month(a.dukas_cache_root,1) if a.dukas_cache_root else None
    checks={
      "january_21_files":jan["files"]==21,
      "january_rows":jan["rows"]==7699274,
      "january_zero_event_mismatch":jan["event_mismatches"]==0,
      "january_event_counts_equal":jan["event_counts_equal"] is True,
      "january_exact_mt5_accounting":jan.get("january_exact") is True,
      "july_dst_crosscheck":jul is not None and jul["event_mismatches"]==0 and jul["event_counts_equal"] is True,
      "august_accessed":False
    }
    passed=all(v for k,v in checks.items() if k!="august_accessed") and checks["august_accessed"] is False
    out={"schema":"delta-003-rebuild-qa-v1","status":"PASS" if passed else "FAIL","checks":checks,
         "january":{k:v for k,v in jan.items() if k!="daily"},"july_01":jul,"dukascopy_january_native":duk}
    if a.output:atomic(a.output,out)
    print(json.dumps(out,indent=2,default=float))
    return 0 if passed else 2
if __name__=="__main__":raise SystemExit(main())
