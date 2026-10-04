"""Aggregate six durable PDHSR C02 month chunks under the preregistered gate."""
from __future__ import annotations
import argparse, json, os, tempfile
from pathlib import Path

MONTHS=("2026-02","2026-03","2026-04","2026-05","2026-06","2026-07")

def atomic(p,o):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);n=None
    try:
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",newline="\n",prefix="."+p.name+".",suffix=".tmp",dir=p.parent,delete=False) as f:
            n=f.name;json.dump(o,f,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
        os.replace(n,p);n=None
    finally:
        if n:
            try:os.unlink(n)
            except FileNotFoundError:pass

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--chunks",type=Path,nargs=6,required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    monthly={}
    for p,month in zip(a.chunks,MONTHS):
        x=json.loads(p.read_text(encoding="utf-8"))
        if x.get("month")!=month:raise SystemExit(f"chunk month mismatch {p}: {x.get('month')} != {month}")
        monthly[month]=x["metrics"]
    trades=sum(x["trades"] for x in monthly.values());wins=sum(x["official_wins"] for x in monthly.values())
    gp=round(sum(x["gross_profit"] for x in monthly.values()),2);gl=round(sum(x["gross_loss"] for x in monthly.values()),2);net=round(sum(x["direct_net_usd"] for x in monthly.values()),2)
    nonneg=sum(x["direct_net_usd"]>=0 for x in monthly.values())
    gate={"total_trades_min_24":trades>=24,"nonnegative_months_min_4":nonneg>=4,"aggregate_net_nonnegative":net>=0}
    gate["robustness_pass"]=all(gate.values())
    out={"schema":"delta-r037-pdhsr-c02-monthly-validation-v1","status":"COMPLETE_MONTH_BY_MONTH_VALIDATION","unit":"R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION","candidate":"R037-PDHSR-C02_S5_CLOSE_RECLAIM","parent_checkpoint":"R037_PDHSR_C02_INDEPENDENT_LATER_JAN_VALIDATION_CHECKPOINT_17AE","prereg_commit":"04341c0531990e8f3685baf4066aaf85b3c1ac32","months":monthly,"aggregate":{"trades":trades,"official_wins":wins,"gross_profit":gp,"gross_loss":gl,"direct_net_usd":net,"nonnegative_months":nonneg},"gate":gate,"candidate_retuned":False,"posthoc_level_split":False,"august_accessed":False,"decision":"ADVANCE_SURROGATE_PARENT_INTEGRATION" if gate["robustness_pass"] else "RETIRE_C02_NO_RETUNE","next":"R037_PDHSR_C02_SURROGATE_PARENT_INTEGRATION_VALIDATION" if gate["robustness_pass"] else "R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST","mql5_authorized":False}
    atomic(a.output,out);print(json.dumps({"aggregate":out["aggregate"],"gate":gate,"next":out["next"]},separators=(",",":")))

if __name__=="__main__":main()
