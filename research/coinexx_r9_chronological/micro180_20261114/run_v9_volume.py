"""Bounded on-policy original-Coinexx sample: original dual OR vs V9 alternatives."""
from __future__ import annotations
import argparse,hashlib,json,sys,time,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROJECT=Path(os.environ.get('R9_RESEARCH_ROOT',str(ROOT.parent)))
if not (PROJECT/'src').is_dir():
    raise RuntimeError('Set R9_RESEARCH_ROOT to the existing research/coinexx_r9_chronological source directory')
for p in (PROJECT/'src',PROJECT/'variable_cash_horizon_20261114',
          PROJECT/'dual_basket_20261114',ROOT):sys.path.insert(0,str(p))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9Config,R9HybridGateBaseline
from on_policy_cash_replay import ResearchCash
from dual_basket import DualBasketBaseline
from v9_volume_router import VolumePreservingMicroV9,V9Spec


def execute():
    p=argparse.ArgumentParser()
    p.add_argument('--ticks',type=Path,required=True)
    p.add_argument('--limit',type=int,default=200_000)
    p.add_argument('--expected-sha',default='')
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--governor',action='store_true')
    p.add_argument('--capital',type=float,default=100_000)
    args=p.parse_args()
    if args.limit<=0:raise ValueError('bounded prefixes only, no implicit whole-month replay')
    if args.expected_sha:
        h=hashlib.file_digest(args.ticks.open('rb'),'sha256').hexdigest()
        if h.lower()!=args.expected_sha.lower():raise ValueError('Source file changed')
    cfg=R9Config()
    cash=lambda:ResearchCash(k=1.,cost=.20,initial_capital=args.capital,governor=args.governor)
    models={
      'r9_original_60s':R9HybridGateBaseline(cfg),
      'dual_original_exit':DualBasketBaseline(cfg),
      'v9_high_volume_first_cash010':VolumePreservingMicroV9(cfg,cash()),
      'v9_defensive_micro_loss':VolumePreservingMicroV9(cfg,cash(),V9Spec(exit_action='early_path_defense')),
      'v9_reverse_side_diagnostic':VolumePreservingMicroV9(cfg,cash(),V9Spec(entry_action='reverse_all_research')),
    }
    start=time.perf_counter();n=0
    for n,t in enumerate(iter_coinexx_ticks(args.ticks,strict=True),1):
        for model in models.values(): model.on_tick(t)
        if n>=args.limit:break
    out={}
    for key,m in models.items():
        if type(m) in (DualBasketBaseline,R9HybridGateBaseline):
            vals=[x.net_price_u/100.-.20 for x in m.trades]
            out[key]={'trades':len(vals),'net_cash':round(sum(vals),3),
                      'net_per_trade':round(sum(vals)/max(1,len(vals)),6),
                      'buys':sum(x.side>0 for x in m.trades),'sells':sum(x.side<0 for x in m.trades),
                      'buy_net_cash':round(sum(v for x,v in zip(m.trades,vals) if x.side>0),3),
                      'sell_net_cash':round(sum(v for x,v in zip(m.trades,vals) if x.side<0),3),
                      'open_position_at_end':bool(m.position)}
        else:
            r=m.report()
            out[key]={k:r.get(k) for k in ('trades','net_cash','net_per_trade','win_fraction',
                 'gross_realized_losses','closed_trade_cvar95_loss','loss_le_minus_2',
                 'max_account_peak_drawdown_cash','close_reasons','v9','governor_halts')}
            out[key]['open_position_at_end']=bool(m.position)
            out[key]['buys']=sum(x.side>0 for x in m.trades)
            out[key]['sells']=sum(x.side<0 for x in m.trades)
            out[key]['buy_net_cash']=round(sum((x.net_price_u/100.*m.cash.k-m.cash.cost) for x in m.trades if x.side>0),3)
            out[key]['sell_net_cash']=round(sum((x.net_price_u/100.*m.cash.k-m.cash.cost) for x in m.trades if x.side<0),3)
            out[key]['research_account']={
                'governor_enabled':m.cash.governor,
                'day_lock_at_end':bool(m.account.day_lock),
                'permanent_lock_at_end':bool(m.account.permanent_lock),
                'equity_cash':round(m.account.equity,3),
                'daily_gross_consumed_cash':round(m.account.consumed(),3),
                'daily_budget_cash':round(m.account.allowed_budget(),3),
            }
    result={'scope':'IN_SAMPLE_FIRST_SOURCE_RECORDS_NOT_OOS','source':args.ticks.name,'n':n,
            'elapsed_s':round(time.perf_counter()-start,2),
            'raw_data_created':False,'unverified_k':1.,'unverified_cost':.20,
            'governor':args.governor,'native_mt5_parity':False,
            'full_nine_month_volume_verified':False,'models':out}
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True))
    print(json.dumps({k:(v['trades'],v['net_cash']) for k,v in out.items()}),flush=True)

if __name__=='__main__':execute()
