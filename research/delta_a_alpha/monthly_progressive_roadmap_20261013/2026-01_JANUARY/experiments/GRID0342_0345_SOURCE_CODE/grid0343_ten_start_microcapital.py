"""Independent fixed-seed research stress runs. NOT month-blind; quote data actual.
No source outcome used to decide entries; previously selected source population caveat.
"""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,'/mnt/data/jan_work/engine')
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD
from grid0342_hyperrisk_escrow import run,features
DAY=86400000
POLICIES={
 'CONTROL_2':dict(initial_cap=2,earned_cash_tiers=((100.,2),(150.,4),(300.,8),(500.,16),(1000.,32),(2000.,64)),stress_move_per_lot=0.,stress_floor_cash_frac=0.),
 'R8_SINGLE_TO_5000':dict(initial_cap=1,earned_cash_tiers=((100.,1),(5000.,8)),stress_move_per_lot=0.,stress_floor_cash_frac=0.),
 'ESCROW_8USD_70PCT':dict(initial_cap=1,earned_cash_tiers=((100.,1),(200.,2),(500.,4),(2000.,8),(5000.,16)),stress_move_per_lot=8.,stress_floor_cash_frac=.70),
 'ESCROW_4USD_65PCT':dict(initial_cap=1,earned_cash_tiers=((100.,1),(150.,2),(300.,4),(1000.,8),(5000.,16)),stress_move_per_lot=4.,stress_floor_cash_frac=.65),
 'ESCROW_8USD_90PCT':dict(initial_cap=1,earned_cash_tiers=((100.,1),(150.,2),(300.,4),(1000.,8),(5000.,16)),stress_move_per_lot=8.,stress_floor_cash_frac=.90),
 'ESCROW_12USD_80PCT':dict(initial_cap=1,earned_cash_tiers=((100.,1),(150.,2),(300.,4),(1000.,8),(5000.,16)),stress_move_per_lot=12.,stress_floor_cash_frac=.80),
}

def materialize():
 p=Path('/mnt/data/r8_followup_20261014/original_research_candidate_unfiltered_cache.npz')
 with np.load(p) as f:
  z={k:f[k] for k in ('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')}
  kind=f['kind'];owner=f['owner'];pgid=f['pgid']
 q=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH')
 t=np.load(q/'ticks_t.npy',mmap_mode='r');bid=np.load(q/'ticks_bid.npy',mmap_mode='r');ask=np.load(q/'ticks_ask.npy',mmap_mode='r')
 r9=json.loads(Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json').read_text())
 return t,bid,ask,z,kind,owner,pgid,r9

def episode_inputs(day,t,bid,ask,z,kind,owner):
 ds=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,ds));hi=int(np.searchsorted(t,ds+7*DAY));
 tt=np.asarray(t[lo:hi]);b=np.asarray(bid[lo:hi]);a=np.asarray(ask[lo:hi]);mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
 zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask]
 zz['entry_idx']-=lo;trunc=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1)
 keep=zz['entry_idx']<zz['exit_idx'];zz={k:v[keep] for k,v in zz.items()};kk=kk[keep];oo=oo[keep];trunc=trunc[keep]
 for j in np.flatnonzero(trunc):
  ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(b[ix] if dr>0 else a[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
 return tt,b,a,zz,kk,oo

def main():
 t0=time.time();t,bid,ask,z,kind,owner,pgid,r9=materialize();_,days=cohort.select_days(r9,t)
 raw_hash=hashlib.sha256(Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz').read_bytes()).hexdigest()
 assert raw_hash=='d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'
 result={'provenance':'UNPROMOTED_JAN_IN_SAMPLE_SELECTION','seed':cohort.SEED,'ten_random_days':days,'original_gzip_sha256':raw_hash,'cases':{},'partials':[]}
 if (ROOT/'grid0343_partial_checkpoint.json').exists():
  result=json.loads((ROOT/'grid0343_partial_checkpoint.json').read_text());assert result['original_gzip_sha256']==raw_hash and result['ten_random_days']==days
 (ROOT/'grid0343_partial_checkpoint.json').write_text(json.dumps(result,indent=2))
 for day in days:
  if all(any(r['day']==day and r['policy']==name and not r.get('INCOMPLETE') for r in result['partials']) for name in POLICIES):continue
  tt,b,a,zz,kk,oo=episode_inputs(day,t,bid,ask,z,kind,owner)
  pre,shock=features(tt,b,a)
  for name,kwargs in POLICIES.items():
   if any(r['day']==day and r['policy']==name and not r.get('INCOMPLETE') for r in result['partials']):continue
   try:
    x=run(tt,b,a,zz,kk,oo,pgid,cash=100.,admission_margin_fraction=.20,stopout_ratio=.5,
      screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=ALL_ORD,**kwargs)
    accepted=x.pop('accepted_indices');ledger=x.pop('booked_ledger')
    row={k:x[k] for k in ['final_cash','trades_closed','min_tick_equity','max_tick_drawdown','worst_hour_drawdown','forced_events','peak_open','denied','min_margin_ratio_observed']}
    row.update(day=day,policy=name,positive=x['final_cash']>100,pass_margin=x['forced_events']==0,pass_nonruin=x['min_tick_equity']>0,
      targeted5000=x['final_cash']>=5000)
    result['partials'].append(row)
    print('DONE',day,name,round(row['final_cash'],2),'n',row['trades_closed'],'DDhour',round(row['worst_hour_drawdown'],2),'elapsed',round(time.time()-t0,1),flush=True)
   except Exception as exc:
    result['partials'].append(dict(day=day,policy=name,INCOMPLETE=str(exc)));print('ERROR',day,name,str(exc),flush=True)
   (ROOT/'grid0343_partial_checkpoint.json').write_text(json.dumps(result,indent=2))
 for name in POLICIES:
  rows=[r for r in result['partials'] if r['policy']==name and not r.get('INCOMPLETE')]
  if len(rows)!=len(days):result['cases'][name]=dict(state='INCOMPLETE',n=len(rows));continue
  result['cases'][name]=dict(state='RESEARCH_COMPLETE',n=len(rows),positive=sum(r['positive'] for r in rows),
   nonruin=sum(r['pass_nonruin'] for r in rows),no_stopout=sum(r['pass_margin'] for r in rows),
   count=sum(r['trades_closed'] for r in rows),min_cash=min(r['final_cash'] for r in rows),max_cash=max(r['final_cash'] for r in rows),
   worst_hour=max(r['worst_hour_drawdown'] for r in rows),worst_tick=max(r['max_tick_drawdown'] for r in rows),hit5000=sum(r['targeted5000'] for r in rows))
 result['runtime_s']=time.time()-t0
 (ROOT/'grid0343_ten_start_results.json').write_text(json.dumps(result,indent=2));print('SUMMARY',json.dumps(result['cases']),flush=True)

if __name__=='__main__': main()
