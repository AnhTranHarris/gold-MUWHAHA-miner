"""Bounded, source-exact R9 V9 vs V10 shadow event attribution.

Never outputs recreated tick files or trade-ledger copies. No PnL comparison:
all observed entry and exit ordinals MUST remain identical to frozen V9.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=Path(os.getenv("R9_RESEARCH_ROOT",str(HERE.parent)))
for p in (ROOT/"src",ROOT/"variable_cash_horizon_20261114",
          ROOT/"dual_basket_20261114",ROOT/"micro180_20261114",HERE):
    if not p.is_dir():raise RuntimeError("Missing existing R9 source dependency: "+str(p))
    sys.path.insert(0,str(p))

from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from v9_volume_router import VolumePreservingMicroV9
from structure_overlay import StructureShadowV10


def run(path:Path, limit:int, expected_sha:str="", governor:bool=False,
        capital:float=100000.0):
    if limit<=0:raise ValueError("Explicit bounded record limit required")
    if expected_sha:
        with path.open("rb") as fh:
            observed=hashlib.file_digest(fh,"sha256").hexdigest()
        if observed.lower()!=expected_sha.lower():
            raise ValueError("Frozen source SHA mismatch")
    config=R9Config()
    cash=lambda: ResearchCash(k=1.,cost=.20,initial_capital=capital,
                              governor=governor)
    original=VolumePreservingMicroV9(config,cash())
    shadow=StructureShadowV10(config,cash())
    count=0
    for count,tick in enumerate(iter_coinexx_ticks(path,strict=True),1):
        original.on_tick(tick)
        shadow.on_tick(tick)
        if count>=limit:break
    if count==0:raise ValueError("No source quotes")
    def events(model):
        return [(x.entry_ordinal,x.exit_ordinal,x.entry_price_u,
                 x.exit_price_u,x.reason,x.side) for x in model.trades]
    same_closed=events(original)==events(shadow)
    same_open=(
        (original.position is None)==(shadow.position is None)
        and (original.position is None or
             (original.position.entry_ordinal==shadow.position.entry_ordinal
              and original.position.entry_price_u==shadow.position.entry_price_u
              and original.position.side==shadow.position.side))
    )
    same_entries=[(x["ordinal"],x["side"],x["price_u"]) for x in original.entries]==[
                  (x["ordinal"],x["side"],x["price_u"]) for x in shadow.entries]
    if not (same_closed and same_open and same_entries):
        raise AssertionError("V10 SHADOW MODIFIED V9 LIVE DECISIONS; REJECT")
    report=shadow.report()["structure_v10"]
    return {
        "scope":"IN_SAMPLE_BOUNDED_SOURCE_PREFIX",
        "source":path.name,"observed_quotes":count,
        "trade_decisions_unchanged":True,
        "same_entry_exit_quote_ordinals":True,
        "shadow_mode":True,
        "original_v9_completed_trades":len(original.trades),
        "v10_completed_trades":len(shadow.trades),
        "risk_governor_enabled":governor,
        "native_parity_verified":False,
        "research_only_no_profit_evaluation":True,
        "structure":report,
        "recent_events":list(shadow.structure_events),
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ticks",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--limit",required=True,type=int)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--governor",action="store_true")
    p.add_argument("--capital",type=float,default=100000.)
    a=p.parse_args()
    result=run(a.ticks,a.limit,a.expected_sha,a.governor,a.capital)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in
          ("observed_quotes","original_v9_completed_trades",
           "same_entry_exit_quote_ordinals","shadow_mode")}),flush=True)


if __name__=="__main__":main()
