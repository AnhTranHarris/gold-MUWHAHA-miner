"""Timeout-safe single-month runner for R037 PDHSR C02 robustness validation."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import delta_r037_pdhsr_c02_monthly_validation as base

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prev-source",type=Path,required=True)
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--month",required=True,choices=[x[0] for x in base.EXPECTED[1:]])
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    idx=[x[0] for x in base.EXPECTED].index(a.month)
    prev_month,prev_sha=base.EXPECTED[idx-1]
    month,cur_sha=base.EXPECTED[idx]
    _,tp,apx,bp=base.load(a.prev_source,prev_sha)
    _,seed_pdh,seed_pdl=base.last_day_levels(tp,bp)
    _,t,ask,bid=base.load(a.source,cur_sha)
    P=base.month_proposals(t,ask,bid,seed_pdh,seed_pdl)
    m=base.metrics(P,t,ask,bid)
    out={"schema":"delta-r037-pdhsr-c02-month-chunk-v1","unit":"R037_PDHSR_C02_MONTH_BY_MONTH_VALIDATION","month":month,"previous_month":prev_month,"metrics":m,"candidate_retuned":False,"posthoc_level_split":False,"august_accessed":False}
    base.atomic(a.output,out)
    print(json.dumps({"month":month,"metrics":m},separators=(",",":")))

if __name__=="__main__":main()
