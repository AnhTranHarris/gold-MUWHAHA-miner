"""Source-exact V9/V10/V11 bounded structural attribution without PnL ranking.

Input is an EXISTING Coinexx CSV or CSV.gz, never a regenerated tick archive.
All three candidates see identical ordered original rows. Any decision drift
raises AssertionError. Output JSON holds counters only, not raw quote copies.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=Path(os.environ.get("R9_RESEARCH_ROOT",str(HERE.parent)))
for path in (ROOT/"src",ROOT/"variable_cash_horizon_20261114",
             ROOT/"dual_basket_20261114",ROOT/"micro180_20261114",HERE):
    if not path.is_dir():
        raise RuntimeError("Missing PREEXISTING source dependency: "+str(path))
    sys.path.insert(0,str(path))

from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from v9_volume_router import VolumePreservingMicroV9
from structure_overlay import StructureShadowV10
from structure_overlay_v11 import StructureShadowV11


def closed_signature(model):
    return [(x.entry_ordinal,x.exit_ordinal,x.entry_time_msc,
             x.exit_time_msc,x.entry_price_u,x.exit_price_u,x.side,x.reason)
            for x in model.trades]


def entry_signature(model):
    return [(e["ordinal"],e["side"],e["price_u"]) for e in model.entries]


def position_signature(model):
    p=model.position
    return (None if p is None else
            (p.entry_ordinal,p.entry_price_u,p.side,p.initial_sl_u))


def run(ticks:Path,limit:int,expected_sha="",capital=100000.,governor=False):
    if limit<=0:raise ValueError("Bounded, explicit max record count required")
    if expected_sha:
        with ticks.open("rb") as fh:
            found=hashlib.file_digest(fh,"sha256").hexdigest()
        if found.lower()!=expected_sha.lower():
            raise ValueError("Source SHA differs from original research pin")
    cfg=R9Config()
    cash=lambda:ResearchCash(k=1.,cost=.20,initial_capital=capital,
                             governor=governor)
    baseline=VolumePreservingMicroV9(cfg,cash())
    v10=StructureShadowV10(cfg,cash())
    v11=StructureShadowV11(cfg,cash())
    seen=0
    for seen,t in enumerate(iter_coinexx_ticks(ticks,strict=True),1):
        baseline.on_tick(t)
        v10.on_tick(t)
        v11.on_tick(t)
        if seen>=limit:break
    if not seen:raise ValueError("No source quotes processed")
    for label,model in (("V10",v10),("V11",v11)):
        if closed_signature(baseline)!=closed_signature(model):
            raise AssertionError(label+" changed original trade lifecycle")
        if entry_signature(baseline)!=entry_signature(model):
            raise AssertionError(label+" changed original entry chronology")
        if position_signature(baseline)!=position_signature(model):
            raise AssertionError(label+" changed original open position")
        if baseline.stats!=model.stats:
            raise AssertionError(label+" changed original V9 stats")
    r10=v10.report()["structure_v10"]
    r11=v11.report()["structure_v11"]
    p=r11["v11_entry_subtypes"]
    if sum(p.values())!=len(baseline.entries):
        raise AssertionError("V11 profile coverage not one-to-one with entries")
    return {
      "source":ticks.name,
      "source_sha_verified":bool(expected_sha),
      "quotes":seen,
      "full_original_file":seen<limit,  # FALSE when cap truncates source
      "entries":len(baseline.entries),
      "completed_trades":len(baseline.trades),
      "v9_v10_v11_exact_trade_decision_parity":True,
      "governor_enabled":governor,
      "structure_v10":{
          "entry_specialist_counts":r10["specialist_counts"],
          "old_unverified_lifecycle_transitions":
              r10["lifecycle_action_transitions"]},
      "structure_v11":r11,
      "research_only":True,
      "profits_evaluated":False,
      "native_mt5_compiled_or_parity_verified":False,
      "data_regenerated":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ticks",required=True,type=Path)
    p.add_argument("--limit",required=True,type=int)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--capital",type=float,default=100000.)
    p.add_argument("--governor",action="store_true")
    a=p.parse_args()
    r=run(a.ticks,a.limit,a.expected_sha,a.capital,a.governor)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"quotes":r["quotes"],"entries":r["entries"],
                      "trade_parity":r["v9_v10_v11_exact_trade_decision_parity"],
                      "old_unknown":r["structure_v10"]["entry_specialist_counts"].get(
                          "UNRESOLVED",0),
                      "v11_subtypes":r["structure_v11"]["v11_unresolved_reasons"]}),
          flush=True)


if __name__=="__main__":main()
