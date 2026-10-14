"""GRID0307 RESEARCH ONLY: isolated random January start-date <$100 research stress.

Every sampled 2026-01 UTC trading date starts an independent portfolio with $100.
Signals before the start are excluded; no inherited profitable state or margin.
Episode ends at Jan31 original tick boundary, with preserved quote-side candidate exits.
Source signals originally came from historically selected January research, not production source.
A positive resulting min-marked equity is necessary, NOT sufficient for margin survivability:
the inherited settlement engine DOES NOT implement mid-position broker stopout and may
produce further trades after liquidation would have occurred. Fail-closed: never
certify survival based on this model, especially absent Coinexx margin/stopout specs.
"""
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
import numpy as np
import grid0303_causal_coverage_source_caps as g
ROOT=Path(__file__).resolve().parent
TICK_SOURCE=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
SEED=20261014
COUNT=10

def run():
    started=time.time()
    sha=hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest()
    assert sha=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
    t,bid,ask,z,kind,owner,pgid,r9,origin=g.g.base.p.ancestor.base.materialize()
    dates=np.array(sorted(r9['daily'].keys()))
    assert len(dates)==21
    rng=np.random.default_rng(SEED)
    picked=sorted(rng.choice(dates,size=COUNT,replace=False).tolist())
    experiments=[]
    cases=[('NO_NEW_CAPITAL_GUARD',8,256,224),('SMALL_GLOBAL_CAP_2',2,2,2),('SMALL_GLOBAL_CAP_4',4,4,4)]
    for d in picked:
        first=int(np.datetime64(d+'T00:00:00','ms').astype('int64'))
        lo=int(np.searchsorted(t,first,'left'))
        tt=t[lo:];bb=bid[lo:];aa=ask[lo:]
        valid=z['entry_idx']>=lo
        zz={k:v[valid].copy() for k,v in z.items()}
        zz['entry_idx']-=lo;zz['exit_idx']-=lo
        kk=kind[valid];oo=owner[valid]
        assert len(zz['entry_idx']) and zz['entry_idx'][0]>=0
        for name,cap,c0,c2 in cases:
            st=time.time()
            r=g.replay(tt,bb,aa,zz,kk,oo,pgid,r9,cash=100.,cap=cap,
                loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=min(32,cap),
                earned_wins=7,earned_window=10,earned_edge=12,parent_cap=min(16,cap),
                earned_parent_cap=min(192,cap),parent_wins=4,parent_window=6,parent_edge=4,
                hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=min(64,cap),
                gc0_cap=c0,gc2_cap=c2)
            equity=float(r['min_actual_tick_equity']);end=float(r['ending_equity'])
            # Only a necessary mark test; no broker stopout: fail-closed, never certified.
            potential_survival=(equity>0.)
            experiments.append({'start_utc_day':d,'variant':name,'start_usd':100.0,
                'end_mark_equity_usd':end,'net_usd':float(r['net']),
                'min_marked_equity_usd':equity,
                'max_hourly_floating_dd_usd':float(r['max_hourly_tick_equity_drawdown_usd']),
                'trades':int(r['trades']),'peak_open':int(r['max_funded_positions']),
                'cash_target_10000_hit':end>=10000.,
                'necessary_positive_equity_test':potential_survival,
                'certified_margin_survival':False,
                'margin_stopout_supported':False,'duration_s':round(time.time()-st,2)})
            print(d,name,'net',round(r['net'],2),'end_eq',round(end,2),'min_eq',round(equity,2),
                'trades',r['trades'],'n_open',r['max_funded_positions'],'TARGET',end>=10000.,flush=True)
    out={'id':'GRID0307_TEN_DETERMINISTIC_RANDOM_JANUARY_START_DATES_100USD',
         'status':'RESEARCH_STRESS_ONLY_UNPROMOTED_NEVER_CLAIM_100pct_SURVIVAL',
         'source_sha256':sha,'sample_seed':SEED,'sample_method':'uniform 10 distinct from 21 recorded UTC January trading days; independent account state; replay from selected date through January last tick; no original upstream positions inherited',
         'starting_capital_usd':100,'target_ending_equity_usd':10000,'target_over_start_multiple':100.,
         'model_limitations':['Precomputed source candidate exits are allowed, but never used as runtime entry features; source pipeline historically selected on January data',
              'Broker-specific lot value, spreads, contract margin, leverage, stopout and slippage remain unverified',
              'Inherited full-tick accounting does not actually liquidate on broker stopout; positive min-equity is not sufficient to certify survival',
              'A January last-trading-day start has less opportunity than earlier starts',
              'No deposits, withdrawals, leverage increases, lot doubling or loss-sized positions',
              'The most fragile comparison is same-month $100 100x target, not guaranteed or attained by restatement'],
         'dates':picked,'candidate_origin':origin,'variants':experiments,
         'elapsed_s':round(time.time()-started,1)}
    path=ROOT/'grid0307_ten_random_dates_100usd_stress_results.json'
    path.write_text(json.dumps(out,indent=2))
    print('SAVED',path,'elapsed',round(time.time()-started,1),flush=True)
if __name__=='__main__':run()
