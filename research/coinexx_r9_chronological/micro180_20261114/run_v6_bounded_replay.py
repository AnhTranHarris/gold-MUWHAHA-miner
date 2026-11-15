"""Source-exact bounded V5-vs-V6 cash-utility comparison; no new tick archives.

Requires existing original Coinexx gzip. Flags no positive-net or throughput
certificate. Frozen Jan/Sep sample comparison is research IN-SAMPLE.
"""
from __future__ import annotations
import argparse,json,time,sys,hashlib
from dataclasses import replace,asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in ('src','variable_cash_horizon_20261114','micro180_20261114'):
    sys.path.insert(0,str(ROOT/p))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180Spec
from v5_path_lifecycle import PathLifecycleV5,V5Spec
from v6_past_only_utility import PastOnlyCashMicroV6,V6Spec


def execute():
    p=argparse.ArgumentParser()
    p.add_argument('--ticks',required=True,type=Path)
    p.add_argument('--limit',type=int,default=200_000)
    p.add_argument('--sha256',default='',help='Optional expected SHA256 for whole original compressed file')
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--profile',choices=('fast','strict'),default='fast')
    p.add_argument('--initial-capital',type=float,default=100_000.)
    p.add_argument('--economic-control-ungoverned',action='store_true',
        help='Explicit ungoverned comparator ONLY; not deployment comparable')
    a=p.parse_args()
    if a.initial_capital<=0:raise ValueError('capital must be positive')
    if a.limit<=0:raise ValueError('Whole-month execution is a separate approved workload; use a bounded limit')
    if a.sha256:
        observed=hashlib.file_digest(a.ticks.open('rb'),'sha256').hexdigest()
        if observed.lower()!=a.sha256.lower():raise ValueError('Original gzip source hash mismatch')
    base=Micro180Spec(breakout_router='balanced_30s_veto',
         s1_mode='micro_only',structural_confirmation='causal_active_or_completed')
    fast=replace(base,min_5s_mid_move_u=3,min_15s_confirm_u=0,
        min_complete_15s=5,min_complete_30s=9,min_quote_updates_5s=1,
        min_efficiency_15s=.12,min_normalized_breakout=0.,
        max_quote_gap_ms=5000,spread_shock_ratio=1.6,
        use_m1_directional_veto=False)
    spec=base if a.profile=='strict' else fast
    cfg=R9Config()
    def cash():return ResearchCash(k=1.,cost=.20,initial_capital=a.initial_capital,
                                    governor=not a.economic_control_ungoverned)
    v6=V6Spec(min_buy_cash_edge=-.35,min_sell_cash_edge=-.35)
    models={
        'v5_250ms_frozen_cash':PathLifecycleV5(cfg,cash(),spec,v5=V5Spec()),
        'v6_cash_prior_relaxed':PastOnlyCashMicroV6(cfg,cash(),spec,v6=v6),
        'v6_cash_prior_zero_floor':PastOnlyCashMicroV6(cfg,cash(),spec,
              v6=replace(v6,min_buy_cash_edge=0.,min_sell_cash_edge=0.)),
        'v6_cash_prior_held_protected':PastOnlyCashMicroV6(cfg,cash(),
              replace(spec,experimental_runner=True),
              v5=V5Spec(enable_protected_continuation=True),
              v6=replace(v6,enable_holding_utility=True))
    }
    n=0;start=time.perf_counter()
    for n,t in enumerate(iter_coinexx_ticks(a.ticks,strict=True),1):
        for m in models.values():m.on_tick(t)
        if n>=a.limit:break
    result={}
    for key,m in models.items():
        x=m.report();result[key]={
            'trades':x['trades'],'net_cash':x['net_cash'],
            'net_per_trade':x['net_per_trade'],
            'gross_realized_losses':x['gross_realized_losses'],
            'loss_le_minus_2':x['loss_le_minus_2'],
            'win_fraction':x['win_fraction'],
            'closed_trade_cvar95_loss':x['closed_trade_cvar95_loss'],
            'account_peak_drawdown_cash':x['max_account_peak_drawdown_cash'],
            'entry_gate_stats':x['entry_gate_stats'],
            'close_reasons':x['close_reasons'],
            'v6':x.get('v6_past_cash'),
            'open_position_at_slice_end':bool(m.position),
            'buys':sum(int(q['side']>0) for q in m.entries),
            'sells':sum(int(q['side']<0) for q in m.entries)
        }
    payload={
        'source':a.ticks.name,'source_rows':n,'profile':a.profile,
        'code':'V6 researcher fork','comparison':'same original source, same illustrative cash economics',
        'elapsed_s':round(time.perf_counter()-start,2),
        'cost_in_account_currency':.20,
        'k_in_account_currency_per_one_xau_move':1.,
        'governor_on':not a.economic_control_ungoverned,
        'initial_capital_cash':a.initial_capital,
        'actual_broker_fills':False,'auc_used':False,
        'all_months_tested':False,'in_sample':True,
        'claim':'NO POSITIVE-NET OR WHOLE-SYSTEM THROUGHPUT CERTIFICATION',
        'arms':result}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({'source_rows':n,'arms':{k:(v['trades'],v['net_cash']) for k,v in result.items()}}),flush=True)


if __name__=='__main__':execute()
