"""Single-pass, read-only source-native research runner; emits only compact JSON.

Never download, regenerate, sort, or recompress Coinexx monthly archives.
This is a research candidate, not live MT5 fill/account equivalence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from dataclasses import asdict,replace
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for sub in ('src','variable_cash_horizon_20261114','micro180_20261114'):
    sys.path.insert(0,str(ROOT/sub))
from coinexx_r9.r9_baseline import R9Config
from coinexx_r9.ticks import iter_coinexx_ticks
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180R9,Micro180Spec


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ticks',required=True,type=Path)
    ap.add_argument('--limit',type=int,default=200000,
                    help='0 means entire source file; must be explicit')
    ap.add_argument('--initial-equity',type=float,default=1000.)
    ap.add_argument('--cash-per-one-dollar-xau',type=float,default=1.)
    ap.add_argument('--roundtrip-extra-cost',type=float,default=.20)
    ap.add_argument('--runner-experimental',action='store_true')
    ap.add_argument('--throughput-profile',choices=('strict','balanced','micro','active'),
                    default='strict',
                    help='strict is frozen control; all other profiles are unvalidated research only')
    ap.add_argument('--disable-account-governor-research-only',action='store_true')
    ap.add_argument('--disable-m1-veto',action='store_true')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    cfg=R9Config()
    # Risk governor ON by default, preserving existing stricter 10% peak and
    # 4–12% per-day gross-loss budget, plus 25% absolute start capital cap.
    cash=ResearchCash(k=args.cash_per_one_dollar_xau,
                      cost=args.roundtrip_extra_cost,
                      initial_capital=args.initial_equity,
                      governor=not args.disable_account_governor_research_only)
    base=dict(experimental_runner=args.runner_experimental,
              use_m1_directional_veto=not args.disable_m1_veto)
    profiles={
        'strict':{},
        'balanced':dict(breakout_router='balanced_30s_veto'),
        'micro':dict(breakout_router='balanced_30s_veto',s1_mode='micro_only'),
        'active':dict(breakout_router='balanced_30s_veto',s1_mode='micro_only',
                      structural_confirmation='causal_active_or_completed'),
    }
    spec=Micro180Spec(**base,**profiles[args.throughput_profile])
    engine=Micro180R9(cfg,cash,spec)
    start=time.perf_counter()
    last=None
    for n,t in enumerate(iter_coinexx_ticks(args.ticks),1):
        engine.on_tick(t)
        last=t
        if args.limit and n>=args.limit:break
    # Deliberately do not invent a final closing fill at EOF.
    out=engine.report()
    out.update({'quotes_seen':engine.rolling.n,
                'first_source_quote_path':str(args.ticks),
                'last_source_quote_msc':last.time_msc if last else None,
                'last_source_ordinal':last.ordinal if last else None,
                'elapsed_wall_seconds':round(time.perf_counter()-start,3),
                'source_integrity':'iter_coinexx_ticks strict in-order; source SHA check separately',
                'runner_is_unvalidated':args.runner_experimental,
                'throughput_profile':args.throughput_profile,
                'end_state_position_open':engine.position is not None,
                'spec':asdict(spec),
                'baseline':'R9 dual 5s/15s OR entry Jan–Sep frozen, not replaced',
                'synthetic_real_volume_claim':False,
                'deployment_ready':False})
    text=json.dumps(out,indent=2,sort_keys=True)
    if args.output:
        args.output.write_text(text+'\n',encoding='utf-8')
        print('Wrote compact result:',args.output,'rows:',n)
    else:print(text)

if __name__=='__main__':main()
