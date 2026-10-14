"""GRID0310 bounded falsification of realized-profit earned capacity plus margin budget.
The previous GRID0309 fast policy had ONE >10k endpoint but two margin-floor fails;
this stress test changes admission liquidity reserve ONLY (not the original signals).
All 10 independent seeded start dates are replayed. Does not certify broker survival.
"""
from __future__ import annotations
import time,json
from pathlib import Path
import numpy as np
import grid0309_earned_cash_capped_100usd_growth as base
from grid0307_random_start_lowcapital_original_tick import SEED,COUNT
from grid0308_independent_margin_tick_qc import independent_mark
ROOT=Path(__file__).resolve().parent
MARGINS=(.20,.25,.30,.35)
TIERS=base.POLICIES[2][1]

def main():
 st=time.time();t,bid,ask,z,kind,owner,pgid,r9,origin=base.g.g.base.p.ancestor.base.materialize()
 dates=sorted(np.random.default_rng(SEED).choice(sorted(r9['daily']),COUNT,replace=False).tolist())
 results=[]
 for date in dates:
  st_ms=int(np.datetime64(date+'T00:00:00','ms').astype('int64'))
  lo=int(np.searchsorted(t,st_ms,'left'));mask=z['entry_idx']>=lo
  tt=t[lo:];bb=bid[lo:];aa=ask[lo:]
  zz={k:v[mask].copy() for k,v in z.items()};zz['entry_idx']-=lo;zz['exit_idx']-=lo
  for margin_fraction in MARGINS:
   r=base.replay(tt,bb,aa,zz,kind[mask],owner[mask],pgid,r9,
     cash=100.,cap=64,loss_pause_n=2,pause_ms=300000,
     native16_cap=2,earned_native_cap=32,earned_wins=7,earned_window=10,earned_edge=12,
     parent_cap=16,earned_parent_cap=64,parent_wins=4,parent_window=6,parent_edge=4,
     hourly_entry_lock_usd=0.,hourly_soft_parent_usd=400.,hourly_soft_parent_cap=64,
     gc0_cap=64,gc2_cap=64,earned_cash_tiers=TIERS,margin_fraction=margin_fraction)
   ix=r.pop('_accepted_candidate_rows_internal');audit=independent_mark(tt,bb,aa,zz,ix,100.,st_ms)
   assert abs(r['min_actual_tick_equity']-audit['min_tick_equity'])<1e-6
   assert abs(r['ending_equity']-audit['final_tick_equity'])<1e-6
   row={'date':date,'margin_used_as_fraction_of_post_equity':margin_fraction,
      'modeled_ending_equity':r['ending_equity'],'min_tick_equity':audit['min_tick_equity'],
      'min_margin_level':audit['min_margin_level_ratio'],
      'necessary_margin_100pct_pass':audit['first_margin_breaches']['1.0'] is None,
      'necessary_margin_200pct_pass':audit['first_margin_breaches']['2.0'] is None,
      'positive_net_to_month_end':r['net']>0,'trades':r['trades'],
      'peak_open_positions':r['max_funded_positions'],
      'utc_first24h_mark_equity':audit['utc_first_24h_mark_equity'],
      'reached_10000_by_month_end':r['ending_equity']>=10000.,
      'reached_10000_first24h':audit['24h_target_10000_hit'],
      'worst_hourly_floating_dd':r['max_hourly_tick_equity_drawdown_usd'],
      'monthly_finished_net':r['net']}
   results.append(row)
   print(date,margin_fraction,'end',round(r['ending_equity'],2),'n',r['trades'],
    'survival_margin100',row['necessary_margin_100pct_pass'],'survival_margin200',row['necessary_margin_200pct_pass'],
    'min_equity',round(audit['min_tick_equity'],2),flush=True)
 summaries={}
 for fraction in MARGINS:
  a=[x for x in results if x['margin_used_as_fraction_of_post_equity']==fraction]
  summaries[str(fraction)]={'count':len(a),'necessary_pass_margin100':sum(x['necessary_margin_100pct_pass'] for x in a),
    'necessary_pass_margin200':sum(x['necessary_margin_200pct_pass'] for x in a),
    'target10000_count':sum(x['reached_10000_by_month_end'] for x in a),
    'target10000_24h_count':sum(x['reached_10000_first24h'] for x in a),
    'lowest_equity':min(x['min_tick_equity'] for x in a),
    'min_ending':min(x['modeled_ending_equity'] for x in a),
    'max_ending':max(x['modeled_ending_equity'] for x in a),
    'total_closed_trades':sum(x['trades'] for x in a)}
 saved={'id':'GRID0310_TEN_RANDOM_START_100USD_FAST_EARNED_CAPACITY_MARGIN_FRACTION_FRONTIER',
 'status':'FALSIFIABLE_IN_SAMPLE_RESEARCH_ONLY_NOT_BROKER_SURVIVAL_CERTIFIED',
 'source_sha256':base.g.g.base.p.ancestor.base.back.SRC_SHA,
 'sample_seed':SEED,'dates':dates,
 'cash_tiers':TIERS,'leverage_hypothetical':500.,
 'fixed_0_01_lot':True,'ever_raise_lot_size_from_loss':False,
 'target_100_to_10000':True,'interpretation':'Each independently reset account runs from its own sampled UTC start through Jan last quote; 24h mark separately',
 'important_limitations':['Changing margin admission fraction cannot protect open positions from further adverse quotes; this is a conservative screen, not a broker stop-out executor',
 'Native Coinexx leverage, commission, dynamic margin, stopout, position limits, and latency unverified',
 'Source opportunities and exits are inherited from historical January source-selected set, not fully endogenous month-blind strategy',
 'Any episode breaching margin floor disqualifies candidate irrespective of subsequent recovery or positive ending equity',
 '10 historical stress samples cannot establish future 100% survival'],
 'summary':summaries,'episodes':results,'elapsed_s':round(time.time()-st,2)}
 dest=ROOT/'grid0310_fast_earned_margin_original_tick_results.json';dest.write_text(json.dumps(saved,indent=2))
 print('SAVED',dest,'TIME',round(time.time()-st,2),flush=True)
if __name__=='__main__':main()
