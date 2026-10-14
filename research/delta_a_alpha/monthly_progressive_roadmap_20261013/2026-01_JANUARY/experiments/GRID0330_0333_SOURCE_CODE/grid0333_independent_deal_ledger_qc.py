"""GRID0333 independent read-only source and cash auditing of GRID0331.
Uses the original immutable January gzip SHA, the ten locked seven-day starts,
original observed quote-side fills and chronologically booked closing events.
No R9 future teacher inputs; does not certify original signal selection or real broker fills.
"""
from pathlib import Path
import gzip,hashlib,json,time
import numpy as np
import grid0331_profit_funded_shock_slots as s
ROOT=Path(__file__).resolve().parent
TICK=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
ORIGINAL_SHA='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'

def main():
 st=time.time();h=hashlib.sha256()
 with TICK.open('rb') as f:
  for piece in iter(lambda:f.read(4*1024*1024),b''):h.update(piece)
 assert h.hexdigest()==ORIGINAL_SHA
 result=json.loads((ROOT/'grid0331_profit_funded_shock_slots_results.json').read_text())
 t,bid,ask,z,kind,owner,pgid,r9,origin=s.cohort.sim.prior.g.g.base.p.ancestor.base.materialize()
 _,days=s.cohort.select_days(r9,t);assert result['sample_dates']==days
 rows=[];passed=0;reasons={}
 for d in days:
  day=int(np.datetime64(d+'T00:00:00','ms').astype('int64'));lo=np.searchsorted(t,day,'left');hi=np.searchsorted(t,day+7*86400000,'left')
  tt=t[lo:hi];b=bid[lo:hi];a=ask[lo:hi]
  mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
  zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
  keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
  for j in np.flatnonzero(trunc):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=s.original.features(tt,b,a)
  x=s.run(tt,b,a,zz,kk,oo,pgid,cash=100.,initial_cap=2,admission_margin_fraction=.20,stopout_ratio=.5,
       screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=s.ALL_ORD)
  book=x['booked_ledger'];accepted=x['accepted_indices'];ev=result['episodes'][days.index(d)]
  assert len(book)==x['trades_closed']==ev['trades'];passed+=1
  assert len(accepted)==x['candidate_entries'];passed+=1
  assert set(int(j) for j in accepted)==set(int(rec[1]) for rec in book);passed+=1
  assert all(int(t[lo+zz['entry_idx'][int(j)]])<=int(t[lo+ix]) for ix,j,net,reason in book);passed+=1
  assert abs(100+sum(float(rec[2]) for rec in book)-x['final_cash'])<1e-6;passed+=1
  assert abs(x['final_cash']-ev['final'])<1e-6;passed+=1
  assert abs(x['worst_hour_drawdown']-ev['worst_hour'])<1e-6;passed+=1
  assert abs(x['min_tick_equity']-ev['min_equity'])<1e-6;passed+=1
  assert x['forced_events']==0 and x['min_tick_equity']>0;passed+=1
  assert x['final_cash']<10000;passed+=1
  for ix,j,net,reason in book:
   ix,j=int(ix),int(j);dr=int(zz['direction'][j]);exitpx=int(b[ix] if dr>0 else a[ix]);en=int(zz['entry_price_raw'][j]);cash=dr*(exitpx-en)/1000.-.20
   assert abs(float(net)-cash)<1e-8,(d,j,net,cash)
   assert int(en)==int(a[int(zz['entry_idx'][j])] if dr>0 else b[int(zz['entry_idx'][j])]);passed+=2
   reasons[reason]=reasons.get(reason,0)+1
   rows.append({'episode_date':d,'entry_idx_global':int(lo+zz['entry_idx'][j]),'exit_idx_global':int(lo+ix),
     'entry_utc_ms':int(tt[int(zz['entry_idx'][j])]),'exit_utc_ms':int(tt[ix]),'source':str(zz['source'][j]),
     'direction':dr,'entry_raw':en,'exit_raw':exitpx,'cash_after_cost':float(net),'close_reason':reason})
  print('QC',d,'accepted',len(accepted),'booked',len(book),flush=True)
 target=ROOT/'grid0333_independent_full_booked_trade_ledger.json.gz'
 with gzip.open(target,'wt') as f:json.dump(rows,f,separators=(',',':'))
 summary={'id':'GRID0333_INDEPENDENT_TEN_START_EXACT_QUOTE_CASH_QC','disposition':'UNPROMOTED_RESEARCH_ONLY',
 'original_tick_sha256':ORIGINAL_SHA,'unique_sample_dates':days,'booked_deals':len(rows),'cash_and_quote_checks_passed':passed,'close_reasons':reasons,
 'each_scenario_100_to_10000_7day_pass':False,'subtle_caveat':'Original stream exits and some source selection are historically precomputed; no signal generation certification',
 'time_seconds':time.time()-st}
 (ROOT/'grid0333_independent_qc_results.json').write_text(json.dumps(summary,indent=2))
 print('SUMMARY',summary)
if __name__=='__main__':main()
