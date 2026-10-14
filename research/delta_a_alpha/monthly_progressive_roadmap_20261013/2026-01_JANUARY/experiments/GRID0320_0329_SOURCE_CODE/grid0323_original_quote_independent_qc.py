"""GRID0323 independently reconcile selected GRID0321/0322 original quote-side executions.
Read-only QC; no owner acceptance; original January tick root, all six risk dimensions
are not inferred from unrelated R9 SYNTH/OVERFIT results.
"""
from __future__ import annotations
import json,hashlib,time
from pathlib import Path
import numpy as np
import grid0322_displacement_earned_margin_joint_frontier as prior
import grid0315_independent_7day_margin_liquidation_qc as qc
from grid0307_random_start_lowcapital_original_tick import TICK_SOURCE
ROOT=Path(__file__).resolve().parent
SOURCE=(ROOT/'grid0322_displacement_earned_margin_joint_results.json')
CHECK_POLICIES={'BASE_M20':(0.,.20),'DISP_0P50_M20':(.5,.20),'DISP_0P75_M25':(.75,.25)}

def main():
 started=time.time();q=json.load(open(SOURCE));r0=json.load(open(ROOT/'grid0313_seven_day_100usd_stopout_froniter.json'))
 assert q['days']==r0['sample_dates'];t,bid,ask,z,kind,owner,pgid,r9,origin=prior.prior.sample.sim.prior.g.g.base.p.ancestor.base.materialize()
 assert hashlib.file_digest(TICK_SOURCE.open('rb'),'sha256').hexdigest()==q['original_tick_sha']
 checked=[];count=0
 for d in q['days']:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]; mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);di=int(zz['direction'][j]);zz['net_cash'][j]=di*(int(b[ix] if di>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=prior.prior.sim.features(tt,b,a)
  for p,(minshock,margin) in CHECK_POLICIES.items():
   x=prior.prior.sim.run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=margin,stopout_ratio=.5,
                          screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=minshock)
   deals=x.pop('booked_ledger');ad=x.pop('accepted_indices');y=qc.reconstruct(tt,b,a,zz,ad,deals)
   ref=next(v for v in q['episodes'] if v['date']==d and v['policy']==p)
   for lhs,rhs in [(x['final_cash'],ref['final_cash']),(x['final_cash'],y['close_cash']),
      (x['trades_closed'],y['closed_trades']),(x['min_tick_equity'],y['min_equity']),
      (x['max_tick_drawdown'],y['max_equity_dd']),(x['worst_hour_drawdown'],y['worst_hour_dd'])]:
    assert abs(lhs-rhs)<1e-5,(d,p,lhs,rhs);count+=1
   if p=='BASE_M20':
    baseline=next(v for v in r0['episodes'] if v['date']==d and v['policy']=='S20_BROKER50_WORST')
    assert abs(baseline['final_cash']-x['final_cash'])<1e-6;count+=1
   checked.append({'date':d,'policy':p,'independent_cash':y['close_cash'],'independent_hourly_dd':y['worst_hour_dd'],
                   'min_equity':y['min_equity'],'closed_count':y['closed_trades'],
                   'forced_events':x['forced_events'],'observation_ticks':len(tt)})
  print('QC',d,'done',round(time.time()-started,1),flush=True)
 assert len(checked)==30 and count==190
 out={'status':'SOURCE_EXACT_READONLY_INDEPENDENT_QC_NOT_PROMOTED','source_sha256':q['original_tick_sha'],
       'seed':prior.prior.sample.SEED,'assertions':count,'episodes_qced':len(checked),'underlying_original_tick_rows':len(t),
       'controls':['exact original tick source SHA','10 fixed preselected dates','entry fill actual Bid/Ask','closed actual opposed Bid/Ask',
         'after-cost cash','independent tick-floating minimum equity','independent hourly drawdown','independent max drawdown',
         'no duplicate settlements','baseline parity with preserved GRID0313 episode'],
       'limitations':['R9 OVERFIT separate six score dimensions not available in this archive',
           'historically preselected proposals and exits cannot establish endogenous strategy reproduction',
           'hypothetical 500x margin is not broker certification',
           '10 historical starts are 10/10 modeled instances, not 100% future survivability'],
       'details':checked,'elapsed_s':time.time()-started}
 path=ROOT/'grid0323_independent_original_quote_qc_result.json';path.write_text(json.dumps(out,indent=2))
 print('GRID0323 INDEPENDENT_CHECKS',count,'PASS; ',path,flush=True)
if __name__=='__main__':main()
