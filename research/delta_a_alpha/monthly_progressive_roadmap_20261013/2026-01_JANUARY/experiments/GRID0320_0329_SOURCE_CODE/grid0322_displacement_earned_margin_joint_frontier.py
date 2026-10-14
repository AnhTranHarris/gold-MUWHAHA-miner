"""GRID0322: independent ten seeded dates; causal pre-request shock + funded margin combinations.
Same source / test windows as original GRID0313, not a new January date optimization.
"""
from __future__ import annotations
import json,time,hashlib
from pathlib import Path
import numpy as np
import grid0321_pre_request_stress_ten_random_starts as prior
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent
# Joint candidates only; controls inherited and immutable.
POLICIES=[('BASE_M20',0.,.20),('DISP_0P50_M20',.5,.20),('DISP_0P50_M25',.5,.25),('DISP_0P50_M30',.5,.30),
          ('DISP_0P75_M20',.75,.20),('DISP_0P75_M25',.75,.25),('DISP_0P75_M30',.75,.30),
          ('DISP_0P35_M25',.35,.25),('DISP_0P35_M30',.35,.30),('NO_DISP_M25',0.,.25),('NO_DISP_M30',0.,.30)]

def main():
    start=time.time();t,bid,ask,z,kind,owner,pgid,r9,origin=prior.sample.sim.prior.g.g.base.p.ancestor.base.materialize()
    eligible,dates=prior.sample.select_days(r9,t)
    out=[]
    for d in dates:
        day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
        et=t[lo:hi];eb=bid[lo:hi];ea=ask[lo:hi]
        mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
        zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
        zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
        keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
        for j in np.flatnonzero(trunc):
            ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(eb[ix] if dr>0 else ea[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
        pre,shock=prior.sim.features(et,eb,ea)
        for name,minshock,margin in POLICIES:
            x=prior.sim.run(et,eb,ea,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=margin,stopout_ratio=.5,
                            screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=minshock)
            x.pop('booked_ledger');x.pop('accepted_indices')
            out.append(dict(date=d,policy=name,final_cash=x['final_cash'],trades=x['trades_closed'],
                            min_eq=x['min_tick_equity'],worst_hour=x['worst_hour_drawdown'],
                            max_dd=x['max_tick_drawdown'],min_margin_ratio=x['min_margin_ratio_observed'],
                            broker_forced=x['forced_events'],blocked=x['denied'].get('pre_request_microstructure',0),
                            target100x=x['final_cash']>=10000.))
        print('Completed date',d,'elapsed',round(time.time()-start,1),flush=True)
    summary={}
    for name,*_ in POLICIES:
        a=[x for x in out if x['policy']==name]
        summary[name]=dict(nonruin=sum(x['min_eq']>0 for x in a),no_forced=sum(x['broker_forced']==0 for x in a),
            positive_profit=sum(x['final_cash']>100 for x in a),targets_10000=sum(x['target100x'] for x in a),
            end_min=min(x['final_cash'] for x in a),end_max=max(x['final_cash'] for x in a),end_median=float(np.median([x['final_cash'] for x in a])),
            min_equity=min(x['min_eq'] for x in a),worst_hour=max(x['worst_hour'] for x in a),trade_total=sum(x['trades'] for x in a),
            forced_events=sum(x['broker_forced'] for x in a))
        print(name,summary[name],flush=True)
    r=dict(id='GRID0322_PRE_REQUEST_DISPLACEMENT_EARNED_MARGIN_JOINT_JAN_7DAY',status='UNPROMOTED',
           seed=prior.sample.SEED,days=dates,policies=POLICIES,summary=summary,episodes=out,
           original_tick_sha=hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest(),
           research_limitations=['All sourced candidates and exit schedules inherited from January historical research',
               'No genuine broker request timestamp, order queue, slippage distribution, hedged margin, contract leverage',
               'No lot escalation: 0.01 lots fixed, no Martingale or loss-dependent sizing',
               'Ten in-sample historical seven-day windows do not imply guaranteed $100 survivability'],
           seconds=time.time()-start)
    (ROOT/'grid0322_displacement_earned_margin_joint_results.json').write_text(json.dumps(r,indent=2))
if __name__=='__main__': main()
