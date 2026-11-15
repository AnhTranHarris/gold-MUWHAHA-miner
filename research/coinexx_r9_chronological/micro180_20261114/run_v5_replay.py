"""Source-native limited replay, no raw tick file output, no AUC or live orders."""
import argparse,json,time,sys
from dataclasses import replace,asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if not (ROOT/"src").is_dir():ROOT=ROOT/"r9_runner"
for d in ("src","variable_cash_horizon_20261114","micro180_20261114"):
    sys.path.insert(0,str(ROOT/d))
if (ROOT.parent/"micro180_v3_exact").is_dir():
    sys.path.insert(0,str(ROOT.parent/"micro180_v3_exact"))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config
from on_policy_cash_replay import ResearchCash
from micro180 import Micro180R9,Micro180Spec
from v5_path_lifecycle import PathLifecycleV5,V5Spec


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--ticks',type=Path,required=True)
    p.add_argument('--limit',type=int,default=200_000)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--profile',choices=('active','fast'),default='fast')
    args=p.parse_args()
    if args.limit<=0:raise SystemExit('Explicit capped research only; use prior full-month calibration runner')
    active=Micro180Spec(breakout_router='balanced_30s_veto',s1_mode='micro_only',structural_confirmation='causal_active_or_completed')
    fast=replace(active,min_5s_mid_move_u=3,min_15s_confirm_u=0,
                 min_complete_15s=5,min_complete_30s=9,min_quote_updates_5s=1,
                 min_efficiency_15s=.12,min_normalized_breakout=0.0,
                 max_quote_gap_ms=5000,spread_shock_ratio=1.6,
                 use_m1_directional_veto=False)
    spec=active if args.profile=='active' else fast
    cfg=R9Config()
    def cash():return ResearchCash(k=1.,cost=.20,initial_capital=100_000.,governor=False)
    models={
      'existing_v3_qualifier':Micro180R9(cfg,cash(),spec),
      'v5_path_entry_cash_harvest':PathLifecycleV5(cfg,cash(),spec,v5=V5Spec()),
      'v5_path_entry_early_exit':PathLifecycleV5(cfg,cash(),spec,v5=V5Spec(permit_early_adverse_exit=True)),
      'v5_path_entry_protected_hold':PathLifecycleV5(cfg,cash(),spec,v5=V5Spec(enable_protected_continuation=True))
    }
    start=time.perf_counter();n=0
    for n,t in enumerate(iter_coinexx_ticks(args.ticks),1):
        for sim in models.values():sim.on_tick(t)
        if n>=args.limit:break
    out={}
    for name,m in models.items():
        r=m.report()
        out[name]={k:r.get(k) for k in ('trades','net_cash','net_per_trade','win_fraction','gross_realized_losses','closed_trade_cvar95_loss','loss_le_minus_2','max_account_peak_drawdown_cash','close_reasons','v5_lifecycle','entry_gate_stats','last_and_volume_nonzero_quotes')}
        out[name]['open_position_at_end']=bool(m.position)
        out[name]['buy_count']=sum(z['side']>0 for z in m.entries)
        out[name]['sell_count']=sum(z['side']<0 for z in m.entries)
    payload={'research_only':True,'full_month':False,'source':args.ticks.name,
        'source_rows':n,'elapsed_seconds':round(time.perf_counter()-start,2),
        'cost':.20,'K':1.,'governor':False,'profile':args.profile,'spec':asdict(spec),
        'status':'NO_PROFIT_CERTIFICATION','arms':out}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,indent=2,sort_keys=True))
    print(json.dumps({k:(v['trades'],v['net_cash']) for k,v in out.items()}))

if __name__=='__main__':main()
