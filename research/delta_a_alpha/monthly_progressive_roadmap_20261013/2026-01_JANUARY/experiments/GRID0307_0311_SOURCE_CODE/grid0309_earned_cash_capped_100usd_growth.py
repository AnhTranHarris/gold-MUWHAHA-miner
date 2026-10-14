"""GRID0309: fixed 0.01 lot; only previously CLOSED cash can earn more concurrently open slots.
NO lot scaling, no Martingale, no month/date label runtime feature.
Novel test: compare staged realized-profit unlocked exposure to fixed global 2/4 slots on
10 deterministic prior GRID0307 January fresh-$100 random starts.
Failures are preserved; 10000 and survival are NOT assumed. Research-only.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
import grid0303_causal_coverage_source_caps as g
from grid0308_independent_margin_tick_qc import independent_mark
from grid0307_random_start_lowcapital_original_tick import SEED,COUNT
ROOT=Path(__file__).resolve().parent
source=g.source
assert source.count('    return r')==1
assert source.count('if len(live)>=cap:')==1
assert source.count('if post<=0 or used_margin+new_margin>max(0.,post)*.65:')==1
source=source.replace('hourly_soft_parent_cap=16,gc0_cap=0,gc2_cap=0):','hourly_soft_parent_cap=16,gc0_cap=0,gc2_cap=0,earned_cash_tiers=(),margin_fraction=0.35):')
source=source.replace('if len(live)>=cap:', '''# Only PREVIOUSLY CLOSED realized balance unlocks higher physical concurrency.
        # Only 0.01 fixed-lot trades; no loss-dependent increases, no doubling.
        earned_cap=2
        for level,slots in earned_cash_tiers:
            if balance>=level:earned_cap=int(slots)
        earned_cap=min(cap,earned_cap)
        if len(live)>=earned_cap:''')
source=source.replace('if post<=0 or used_margin+new_margin>max(0.,post)*.65:', 'if post<=0 or used_margin+new_margin>max(0.,post)*margin_fraction:')
source=source.replace('    return r','    r["_accepted_candidate_rows_internal"] = idx\n    r["earned_cash_tiers"] = earned_cash_tiers\n    r["margin_fraction"] = margin_fraction\n    return r')
ns=dict(g.g.ns);exec(source,ns);replay=ns['physical_replay']

POLICIES=[
 ('EARNED_CAUTION',((100,2),(500,4),(1000,8),(2500,16),(5000,32)),.30),
 ('EARNED_BALANCED',((100,2),(250,4),(500,8),(1000,16),(2000,32),(5000,64)),.35),
 ('EARNED_FAST',((100,2),(150,4),(300,8),(500,16),(1000,32),(2000,64)),.45)
]

def main():
    tm=time.time()
    t,bid,ask,z,kind,owner,pgid,r9,origin=g.g.base.p.ancestor.base.materialize()
    sample=sorted(np.random.default_rng(SEED).choice(sorted(r9['daily']),COUNT,replace=False).tolist())
    results=[]
    for day in sample:
        start=int(np.datetime64(day+'T00:00:00','ms').astype('int64'))
        lo=int(np.searchsorted(t,start,'left'));mask=z['entry_idx']>=lo
        tt=t[lo:];bb=bid[lo:];aa=ask[lo:]
        zz={k:v[mask].copy() for k,v in z.items()}
        zz['entry_idx']-=lo;zz['exit_idx']-=lo
        for name,tiers,marg in POLICIES:
            r=replay(tt,bb,aa,zz,kind[mask],owner[mask],pgid,r9,cash=100.,cap=64,
                loss_pause_n=2,pause_ms=300000,native16_cap=2,earned_native_cap=32,
                earned_wins=7,earned_window=10,earned_edge=12,parent_cap=16,
                earned_parent_cap=64,parent_wins=4,parent_window=6,parent_edge=4,
                hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=64,
                gc0_cap=64,gc2_cap=64,earned_cash_tiers=tiers,margin_fraction=marg)
            ix=r.pop('_accepted_candidate_rows_internal')
            audit=independent_mark(tt,bb,aa,zz,ix,100.,start)
            assert abs(audit['min_tick_equity']-r['min_actual_tick_equity'])<1e-6
            assert abs(audit['final_tick_equity']-r['ending_equity'])<1e-6
            res={'start_day':day,'policy':name,'starting_cash':100.,'end_marked_equity':r['ending_equity'],
                 'trades':r['trades'],'gross_loss':r['gross_loss'],
                 'monthly_remaining_period_positive':r['net']>0,
                 'min_equity':audit['min_tick_equity'],'max_funded':r['peak_open_stream'],
                 'max_hourly_drawdown':r['max_hourly_tick_equity_drawdown_usd'],
                 'min_margin_ratio':audit['min_margin_level_ratio'],
                 'necessary_margin100pct_pass':audit['first_margin_breaches']['1.0'] is None,
                 'necessary_margin200pct_pass':audit['first_margin_breaches']['2.0'] is None,
                 'end_10000_target_met':r['ending_equity']>=10000.,
                 'first24h_10000_target_met':audit['24h_target_10000_hit'],
                 'first24h_mark':audit['utc_first_24h_mark_equity'],
                 'first24h_max_floating_dd':audit['utc_first_24h_drawdown'],
                 'note':'modeled only, no broker stopout simulation, original candidate population historically selected'}
            results.append(res)
            print(day,name,'end',round(r['ending_equity'],2),'trades',r['trades'],
                  'min EQ',round(audit['min_tick_equity'],2),'margin100',res['necessary_margin100pct_pass'],
                  '24h',round(res['first24h_mark'],2),flush=True)
    total={}
    for name,_,_ in POLICIES:
        a=[r for r in results if r['policy']==name]
        total[name]={'count':len(a),'necessary_pass_margin100':sum(x['necessary_margin100pct_pass'] for x in a),
          'necessary_pass_margin200':sum(x['necessary_margin200pct_pass'] for x in a),
          'count_target_10000':sum(x['end_10000_target_met'] for x in a),
          'count_first24h_target_10000':sum(x['first24h_10000_target_met'] for x in a),
          'end_equity_min':min(x['end_marked_equity'] for x in a),
          'end_equity_max':max(x['end_marked_equity'] for x in a),
          'min_equity_min':min(x['min_equity'] for x in a),
          'sum_trades':sum(x['trades'] for x in a)}
    outfile=ROOT/'grid0309_earned_cash_100usd_random_start_results.json'
    outfile.write_text(json.dumps({'id':'GRID0309_REPRODUCIBLE_ORIGINAL_TICK_EARNED_CASH_CAPITAL_GROWTH',
      'source_sha256':g.g.base.p.ancestor.base.back.SRC_SHA,
      'scope':'10 seeded January date accounts run from each start to month end, $100 each, 1oz/0.01 lot $0.20 modeled fee 250ms latency',
      'status':'RESEARCH_UNPROMOTED__NO_REAL_MARGIN_CERTIFICATION',
      'seed':SEED,'start_dates':sample,'policies':POLICIES,
      'all_cash_unlocks_use_only_observed_closed_net_profits':True,
      'limits':['No broker-calibrated stopout fill or dynamic margin/commission',
         'All candidates and their exit logic precomputed from original January research; no independent month-blind V1 integration',
         'Fail closed on simulated margin floor: do not call any variant certified survival',
         'No guarantee that a 100x account is viable on future ticks'],
      'aggregates':total,'episodes':results,'wall_seconds':round(time.time()-tm,2)},indent=2))
    print('SAVED',outfile,'SECONDS',round(time.time()-tm,2),flush=True)
if __name__=='__main__':main()
