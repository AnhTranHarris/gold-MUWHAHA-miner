"""Read-only original Coinexx V7 conditioned pilot; no new source datasets.

Jan/Sep first-N are IN-SAMPLE, not nine-month economics or MT5 fills.
"""
from __future__ import annotations
import argparse,json,sys,time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for d in ('src','variable_cash_horizon_20261114','micro180_20261114'):
    sys.path.insert(0,str(ROOT/d))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180Spec
from v5_path_lifecycle import PathLifecycleV5,V5Spec
from v6_past_only_utility import V6Spec
from v7_conditioned_cash import SetupConditionedMicroV7,V7Spec


def execute():
    p=argparse.ArgumentParser()
    p.add_argument('--ticks',type=Path,required=True)
    p.add_argument('--limit',type=int,default=200_000)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ungoverned-economic-comparator',action='store_true')
    p.add_argument('--initial-capital',type=float,default=500.)
    a=p.parse_args()
    if a.limit<1 or a.initial_capital<=0:raise ValueError('bounded limit/initial equity required')
    s=Micro180Spec(breakout_router='balanced_30s_veto',
        s1_mode='micro_only',structural_confirmation='causal_active_or_completed')
    s=replace(s,min_5s_mid_move_u=3,min_15s_confirm_u=0,
        min_complete_15s=5,min_complete_30s=9,min_quote_updates_5s=1,
        min_efficiency_15s=.12,min_normalized_breakout=0.,
        max_quote_gap_ms=5000,spread_shock_ratio=1.6,
        use_m1_directional_veto=False)
    cfg=R9Config()
    def cash():return ResearchCash(k=1.,cost=.2,initial_capital=a.initial_capital,
                                  governor=not a.ungoverned_economic_comparator)
    v6=V6Spec(audit_only=True)
    cases={
        'v5_frozen':PathLifecycleV5(cfg,cash(),s,v5=V5Spec()),
        'v7_conditioned_shadow':SetupConditionedMicroV7(cfg,cash(),s,v6=v6),
        'v7_matched_gate_relaxed':SetupConditionedMicroV7(cfg,cash(),s,v6=v6,
            v7=V7Spec(enable_cash_gate=True,min_effective_samples=2.0,
            uncertainty_multiplier=.5,
            min_buy_penalized_cash=-.25,min_sell_penalized_cash=-.25)),
        'v7_matched_gate_profit_floor':SetupConditionedMicroV7(cfg,cash(),s,v6=v6,
            v7=V7Spec(enable_cash_gate=True,min_effective_samples=4.0,
            min_buy_penalized_cash=0.,min_sell_penalized_cash=0.)),
        'v7_conditioned_hold_protected':SetupConditionedMicroV7(cfg,cash(),
            replace(s,experimental_runner=True),
            v5=V5Spec(enable_protected_continuation=True),v6=v6,
            v7=V7Spec(enable_conditioned_holding=True)),
    }
    start=time.perf_counter();n=0
    for n,t in enumerate(iter_coinexx_ticks(a.ticks,strict=True),1):
        for mod in cases.values():mod.on_tick(t)
        if n>=a.limit:break
    score={}
    for k,m in cases.items():
        r=m.report()
        score[k]={key:r.get(key) for key in ('trades','net_cash','net_per_trade',
            'gross_realized_losses','win_fraction','closed_trade_cvar95_loss',
            'close_reasons','entry_gate_stats','research_account_governor_enabled',
            'indicator_sources','v7_setup_conditioned')}
        score[k]['open_position_at_end']=m.position is not None
        score[k]['buys']=sum(v['side']==1 for v in m.entries)
        score[k]['sells']=sum(v['side']==-1 for v in m.entries)
    out={'source':a.ticks.name,'rows':n,'elapsed_s':round(time.perf_counter()-start,3),
         'month_complete':False,'test':'IN_SAMPLE bounded diagnostic NOT whole system',
         'source_model':'original Coinexx source-native ms ordered quotes; original gzip unchanged',
         'governor_enabled':not a.ungoverned_economic_comparator,
         'cash_k':1.,'cash_round_trip_extra':.20,'broker_fills_verified':False,
         'AUC155_used':False,'performance_certificate':False,'models':score}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'rows':n,'cases':{k:{'trades':v['trades'],'net_cash':v['net_cash']}
              for k,v in score.items()}}),flush=True)
if __name__=='__main__':execute()
