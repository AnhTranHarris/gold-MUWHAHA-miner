"""One-pass exact original Coinexx R9 versus 15s/30s breakout, hold/exit arms.

Strict source SHA and frozen original R9 position-level ledger parity required for
full-month acceptance. Market input streamed ONCE, no tick/bar/feature duplication.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time, zipfile
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'variable_cash_horizon_20261114'))
sys.path.insert(0,str(ROOT/'quarter_basket'))
from coinexx_r9.ticks import iter_coinexx_ticks
from coinexx_r9.r9_baseline import R9HybridGateBaseline,R9Config
from on_policy_cash_replay import ResearchCash,QuoteRegime
from run_coinexx import verify_month, source_sha, summarize_original, reuse_only_identical_market_context
from quarter_basket import BasketSpec,QuarterBasketBaseline,QuarterBasketCash


def brief_result(sim,cash):
    if isinstance(sim,QuarterBasketBaseline):
        ret=summarize_original(sim,cash)
        ret['basket_starts']=sim.stats['15sec_basket_starts']
        ret['basket_rearms']=sim.stats['15sec_opposite_rearms']
        ret['basket_cross_exits']=sim.stats['15sec_cross_basket_exit_no_rearm']
        return ret
    ret=sim.report()
    ret['basket_starts']=sim.stats['15sec_basket_starts']
    ret['basket_rearms']=sim.stats['15sec_opposite_rearms']
    ret['basket_cross_exits']=sim.stats['15sec_cross_basket_exit_no_rearm']
    return ret

def research_run(args):
    cfg=R9Config()
    cash=ResearchCash(args.k,args.c,args.start_capital,args.governor)
    control=R9HybridGateBaseline(cfg)
    reg=QuoteRegime()
    spec15=BasketSpec(breakout_seconds=15,
                      minimum_mid_displacement_cents=args.mid_displacement_cents)
    spec30=BasketSpec(breakout_seconds=30,
                      minimum_mid_displacement_cents=args.mid_displacement_cents,
                      minimum_completed_seconds=8)
    arms={
      '15b_15break_original_exit':QuarterBasketBaseline(cfg,spec15),
      '15b_30break_original_exit':QuarterBasketBaseline(cfg,spec30),
      '15b_15break_cash050':QuarterBasketCash(cfg,cash,'cash_harvest',spec15,reg),
      '15b_30break_cash050':QuarterBasketCash(cfg,cash,'cash_harvest',spec30,reg),
    }
    if args.experiment_regime_probe:
        arms['15b_30break_nested_trend_probe']=QuarterBasketCash(
            cfg,cash,'regime_probe',spec30,reg)
    reuse_only_identical_market_context(control,*arms.values())
    start=len(control.trades)
    offset=0
    result={
      'classification':'QUOTE_SIDE_ON_POLICY_RESEARCH_NOT_ACTUAL_MT5_FILLS',
      'original_engine_source':'UNMODIFIED original coinexx_r9.r9_baseline baseline',
      'original_five_second_model':'FROZEN_SHADOW_ONLY_NO_VALIDATED_NEW_BREAKOUT_ENTRY_SCORES',
      'no_fabricated_155_features':True,
      'cash_scenario':{'K_account_cash_per_1xau_move':cash.k,'extra_roundtrip_cash_C':cash.cost,
            'governor_scenario_enabled':cash.governor,
            'initial_capital':cash.initial_capital,'broker_cost_verified':False},
      'basket':{'seconds':15,'original_minute_control_seconds':60,
                'breakout_windows_seconds':[15,30],
                'minimum_midquote_displacement_cents':args.mid_displacement_cents,
                'full_quote_stream_replayed':True},
      'months':[], 'arm_results':{},
      'cautions':['No actual MT5 fills, order rejects, freeze/slippage; original governor approximated only',
                   'AUC trained at ORIGINAL R9 minute-entry ordinals, not the NEW 15s entries',
                   '15s and 30s completed-second quote close windows, not native MT5 timeframe bars',
                   'Previous Jan-Sep Coinexx months are development-exposed; not pristine OOS',
                   'No minimum $.10 profit exit. Cash ladder $0.50 floor and $1.75 stretch remain'],
    }
    with zipfile.ZipFile(args.receipt) as z:
        pinned=json.loads(z.read('source_receipt.json'))
        for mm in args.months:
            path=args.data/f'XAUUSD_MT5_BROKER_2026_{mm}_ticks_ALL.csv.gz'
            if not path.is_file():raise FileNotFoundError(path)
            got=source_sha(path)
            want=pinned['source_months'][mm]['source_sha256']
            if got!=want:raise ValueError(f'Gzip source SHA mismatch {mm}: {got}')
            begin=time.monotonic();count=0
            for tick in iter_coinexx_ticks(path,strict=True,ordinal_offset=offset):
                reg.update(tick)
                control.on_tick(tick)
                for arm in arms.values():arm.on_tick(tick)
                count+=1
                if args.max_rows and count>=args.max_rows:break
            full=count==pinned['source_months'][mm]['rows']
            matched=verify_month(control,start,mm,z,pinned) if full else None
            start=len(control.trades)
            offset+=count
            m={'month':mm,'rows':count,'source_sha256':got,
               'expected_rows':pinned['source_months'][mm]['rows'],
               'original_frozen_trade_parity':bool(matched),
               'original_trades':len(control.trades),
               'arm_counts':{a:len(m.trades) for a,m in arms.items()},
               'elapsed_s':round(time.monotonic()-begin,2)}
            result['months'].append(m)
            print('MONTH '+json.dumps(m,sort_keys=True),flush=True)
            # If truncated, this is explicitly only a smoke/coverage test.
            if not full:break
    result['original_control']=summarize_original(control,cash)
    baseline=result['original_control']
    for name,arm in arms.items():
        report=brief_result(arm,cash)
        report['volume_retention_vs_original']=round(report['trades']/baseline['trades'],5) if baseline['trades'] else None
        report['net_delta_vs_original']=round(report['net_cash']-baseline['net_cash'],5)
        report['share_trades_net_ge_050']=round(report.get('target_ge_0_5',0)/report['trades'],6) if report['trades'] else None
        report['share_trades_net_ge_175']=round(report.get('target_ge_1_75',0)/report['trades'],6) if report['trades'] else None
        result['arm_results'][name]=report
    result['complete_original_month_parity']=all(v['original_frozen_trade_parity'] for v in result['months'])
    result['evaluation_complete']=bool(result['complete_original_month_parity'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('FINAL '+json.dumps({'evaluation_complete':result['evaluation_complete'],
      'baseline':{'trades':baseline['trades'],'net':baseline['net_cash']},
      'arms':{k:{'trades':v['trades'],'net':v['net_cash'],
                 'pct_ge_050':v.get('share_trades_net_ge_050'),
                 'retention':v.get('volume_retention_vs_original')} for k,v in result['arm_results'].items()}},sort_keys=True),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=Path('/mnt/data'))
    p.add_argument('--receipt',type=Path,default=Path('/mnt/data/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip'))
    p.add_argument('--months',nargs='+',default=['01'])
    p.add_argument('--k',type=float,default=1.)
    p.add_argument('--c',type=float,default=.2)
    p.add_argument('--start-capital',type=float,default=100000.)
    p.add_argument('--mid-displacement-cents',type=int,default=10)
    p.add_argument('--max-rows',type=int,default=0)
    p.add_argument('--governor',action='store_true')
    p.add_argument('--experiment-regime-probe',action='store_true')
    p.add_argument('--output',type=Path,default=Path('/mnt/data/R9_15S_JAN_2026_RESEARCH_SCORECARD.json'))
    research_run(p.parse_args())