"""GRID0318 full-tick leverage + trading-cost sensitivity, same 10 seeded Jan starts.
Leverage 500 is published *maximum*, not verified instrument-specific account value.
All three inputs (leverage, fee, slippage) are scenario assumptions, never runtime
future outcomes; no martingale, 0.01 fixed lot; inherited source research only.
"""
import json,time
from pathlib import Path
import numpy as np
import grid0313_seven_day_ten_start_stopout_frontier as p
ROOT=Path(__file__).resolve().parent
POLICIES=[
 ('LEVERAGE100_RESERVE20',100.,.20,.20,0.),
 ('LEVERAGE200_RESERVE20',200.,.20,.20,0.),
 ('LEVERAGE300_RESERVE20',300.,.20,.20,0.),
 ('LEVERAGE500_RESERVE20',500.,.20,.20,0.),
 ('LEVERAGE500_RESERVE20_FEE40_SLIP10',500.,.20,.40,.10),
 ('LEVERAGE500_RESERVE35_FEE40_SLIP10',500.,.35,.40,.10)
]
def main():
 t0=time.time();t,bid,ask,z,kind,owner,pgid,r9,orig=p.sim.prior.g.g.base.p.ancestor.base.materialize()
 e,ds=p.select_days(r9,t);assert ds==json.load(open(ROOT/'grid0313_seven_day_100usd_stopout_froniter.json'))['sample_dates']
 results=[]
 for d in ds:
  s=int(np.datetime64(d+'T00:00:00','ms').astype('int64'))
  lo=int(np.searchsorted(t,s,'left'));hi=int(np.searchsorted(t,s+7*86400000,'left'))
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi);zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo; tr=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];tr=tr[keep]
  t1=t[lo:hi];b1=bid[lo:hi];a1=ask[lo:hi]
  for j in np.flatnonzero(tr):
   x=int(zz['exit_idx'][j]);di=int(zz['direction'][j]);zz['net_cash'][j]=di*(int(b1[x] if di>0 else a1[x])-int(zz['entry_price_raw'][j]))/1000.-.20
  for name,leverage,fract,fee,slip in POLICIES:
   x=p.sim.run(t1,b1,a1,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=fract,
         stopout_ratio=.50,liquidation_style='flatten',leverage=leverage,
         fees_per_roundtrip=fee,max_tick_slippage_usd=slip)
   ledger=x.pop('booked_ledger');x.pop('accepted_indices')
   x.update(date=d,policy=name,positive_end=x['final_cash']>100.,
             survived_model=x['min_tick_equity']>0 and x['forced_events']==0,
             reached_10000=x['final_cash']>=10000.,
             booked_cash_exact=abs(100+sum(z[2] for z in ledger)-x['final_cash'])<1.e-6)
   if not x['booked_cash_exact']:raise AssertionError('cash fail')
   results.append(x)
   print(d,name,'net',round(x['net_cash'],2),'N',x['trades_closed'],'min eq',round(x['min_tick_equity'],2),'forced',x['forced_events'],flush=True)
 summary={}
 for name,*_ in POLICIES:
  a=[x for x in results if x['policy']==name]
  summary[name]={'trades':sum(x['trades_closed'] for x in a),'positive_end':sum(x['positive_end'] for x in a),
      'nonruin_no_stopout':sum(x['survived_model'] for x in a),'target10000_7d':sum(x['reached_10000'] for x in a),
      'ends_range':[min(x['final_cash'] for x in a),max(x['final_cash'] for x in a)],
      'min_tick_equity':min(x['min_tick_equity'] for x in a),'broker_stopout_events':sum(x['forced_events'] for x in a)}
 path=ROOT/'grid0318_leverage_cost_seven_day_results.json';path.write_text(json.dumps({'id':'GRID0318_SEVEN_DAY_LEVERAGE_SPREAD_FEE_SLIPPAGE_SENSITIVITY',
       'status':'UNPROMOTED_EXPERIMENTAL_ACCOUNT_MARGIN_NOT_REAL_BROKER','dates':ds,'policies':POLICIES,'summary':summary,'episodes':results,
       'elapsed_seconds':round(time.time()-t0,2)},indent=2));print('SAVED',path,flush=True)
if __name__=='__main__':main()
