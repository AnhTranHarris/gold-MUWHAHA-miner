"""GRID0338 independently rebook quote sides, fee, cash/portfolio and hourly DD.
Read-only audited reference from GRID0335 + original source tokens. No strategy mutation.
"""
import sys, json, gzip, hashlib, zipfile
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path('/mnt/data/r8_followup_20261014');sys.path.insert(0,str(ROOT));sys.path.insert(0,'/mnt/data/jan_work/engine')
from grid0335_r8_directional_efficiency_combination import r8_asof_micro
import grid0324_source_conditioned_pre_request_routing as sim
import grid0313_seven_day_ten_start_stopout_frontier as cohort
from grid0330_initial_capacity_survival_sweep import ALL_ORD


def replicate_hour(tt,b,a,zz,accepted,booked):
 n=len(tt)
 difflo=np.zeros(n+1,np.int32);diffsh=np.zeros(n+1,np.int32);diffbasis=np.zeros(n+1);diffcash=np.zeros(n+1)
 ent_j=np.zeros(n,dtype=np.float64)
 cash_checks=0;bad=[];src=Counter();ent_used=set();pending={}
 for j in accepted:
  j=int(j);en=int(zz['entry_idx'][j]);side=int(zz['direction'][j]);ent=int(zz['entry_price_raw'][j]);assert ent==int(a[en] if side>0 else b[en])
  assert j not in ent_used
  ent_used.add(j);pending[j]=en
 for ix,j,net,reason in booked:
  j=int(j);ix=int(ix); en=pending.pop(j);dr=int(zz['direction'][j]);orig_px=int(zz['entry_price_raw'][j]);end_px=int(b[ix] if dr>0 else a[ix]);expected=dr*(end_px-orig_px)/1000.-.20
  if abs(net-expected)>1.e-8:bad.append((j,ix,net,expected))
  diffcash[ix]+=float(net);diffbasis[en]+=dr*orig_px/1000.;diffbasis[ix]-=dr*orig_px/1000.
  if dr>0:difflo[en]+=1;difflo[ix]-=1
  else:diffsh[en]+=1;diffsh[ix]-=1
  ent_used.remove(j);cash_checks+=1;src[str(zz['source'][j])]+=1
  ent_used.discard(j)
  ent_used.add(j)
  ent_used.remove(j)
  # pre-entry and post-entry same-quote check
  ent_used.add(j)
  # Save immediate entry mark debit; prices use USD x1000 quote precision.
  ent_j[en]+=(int(a[en])-int(b[en]))/1000.+.20
 assert not pending and not bad
 lon=np.cumsum(difflo[:-1]);sho=np.cumsum(diffsh[:-1]);nb=lon+sho
 cash=100.+np.cumsum(diffcash[:-1]);bas=np.cumsum(diffbasis[:-1]);q=cash+(lon*b-sho*a)/1000.-bas-.20*nb
 # The pre-entry mark allows the tester to record entry spread and fee in same tick.
 pre=q+ent_j
 key=tt//3600000;starts=np.r_[0,np.flatnonzero(np.diff(key))+1,n];worst=0.
 for left,right in zip(starts[:-1],starts[1:]):
  v=np.empty((right-left)*2,np.float64);v[0::2]=pre[left:right];v[1::2]=q[left:right]
  worst=max(worst,float(np.max(np.maximum.accumulate(v)-v)))
 return {'quote_checks':cash_checks,'end_equity':float(q[-1]),'min_equity':float(np.min(q)),'max_hourly_dd':worst,'source_closes':dict(src),'pre_entry_max':float(ent_j.max())}


def main():
 q=np.load(ROOT/'original_research_candidate_unfiltered_cache.npz');z={k:q[k] for k in ('entry_idx','exit_idx','entry_price_raw','direction','net_cash','source')};kind=q['kind'];owner=q['owner'];pgid=q['pgid']
 P=Path('/mnt/data/R8_JAN_DUKAS_RESEARCH');t=np.load(P/'ticks_t.npy',mmap_mode='r');b=np.load(P/'ticks_bid.npy',mmap_mode='r');a=np.load(P/'ticks_ask.npy',mmap_mode='r')
 r9=json.loads(Path('/mnt/data/jan_recovery_20261013/ORIGINAL/r9_synth_jan_daily_weekly.json').read_text());_,days=cohort.select_days(r9,t)
 report=json.loads((ROOT/'grid0335_r8_efficiency_source_confluence_results.json').read_text());assert report['date_cohort']==days
 bycase={(x['date'],x['policy']):x for x in report['episodes']}
 checks=0;logs=[];total=Counter();maxdelta=0.
 zippath='/mnt/data/GRID0320_0329_JANUARY_SOURCE_EXACT_ROUTING_AND_100USD_SURVIVAL_QC_UNPROMOTED.zip'
 with zipfile.ZipFile(zippath) as f:base=json.loads(f.read('RESEARCH/grid0325_ten_start_source_conditioned_results.json'))
 for day in days:
  ds=int(np.datetime64(day+'T00:00:00','ms').astype('int64'));lo=int(np.searchsorted(t,ds));hi=int(np.searchsorted(t,ds+7*86400000));tt=np.asarray(t[lo:hi]);bb=np.asarray(b[lo:hi]);aa=np.asarray(a[lo:hi]);mask=(z['entry_idx']>=lo)&(z['entry_idx']<hi)
  zz={k:v[mask].copy() for k,v in z.items()};kk=kind[mask];oo=owner[mask];zz['entry_idx']-=lo;tr=zz['exit_idx']>=hi;zz['exit_idx']=np.minimum(zz['exit_idx']-lo,hi-lo-1);good=zz['entry_idx']<zz['exit_idx']
  zz={k:v[good] for k,v in zz.items()};kk=kk[good];oo=oo[good];tr=tr[good]
  for j in np.flatnonzero(tr):
   ix=int(zz['exit_idx'][j]);dr=int(zz['direction'][j]);zz['net_cash'][j]=dr*(int(bb[ix] if dr>0 else aa[ix])-int(zz['entry_price_raw'][j]))/1000.-.20
  pre,shock=sim.features(tt,bb,aa);_,_,eff=r8_asof_micro(tt,bb,aa,zz['entry_idx'])
  for case in ['CONTROL','R8_ONE','EFF60']:
   keep=np.ones(len(kk),bool)
   ordinary=(kk==0)&np.isin(zz['source'],list(ALL_ORD))
   if case=='EFF60':keep[ordinary]&=eff[ordinary]>=.60
   part={k:v[keep] for k,v in zz.items()};kinds=kk[keep];owners=oo[keep]
   one=case=='R8_ONE'
   tiers=((100.,1),(150.,2),(300.,4),(500.,8),(1000.,16),(2000.,64)) if one else ((100.,2),(150.,4),(300.,8),(500.,16),(1000.,32),(2000.,64))
   x=sim.run(tt,bb,aa,part,kinds,owners,pgid,cash=100.,initial_cap=1 if one else 2,earned_cash_tiers=tiers,admission_margin_fraction=.20,stopout_ratio=.5,screen_quote_idx=pre,pre_request_shock_5s=shock,min_observed_5s_shock=.5,screen_sources=ALL_ORD)
   exp=bycase[(day,case)]
   assert x['trades_closed']==exp['trades_closed'] and abs(x['final_cash']-exp['final_cash'])<1e-6
   res=replicate_hour(tt,bb,aa,part,x['accepted_indices'],x['booked_ledger'])
   delta=abs(res['max_hourly_dd']-x['worst_hour_drawdown']);maxdelta=max(maxdelta,delta)
   if abs(res['end_equity']-x['final_cash'])>.001:raise AssertionError(('cash',case,day,res['end_equity'],x['final_cash']))
   if abs(res['min_equity']-x['min_tick_equity'])>0.001:raise AssertionError(('equity',case,day,res['min_equity'],x['min_tick_equity']))
   if delta>.2:raise AssertionError(('hour',case,day,delta,res['max_hourly_dd'],x['worst_hour_drawdown']))
   checks+=4+res['quote_checks'];total[case]+=res['quote_checks']
   logs.append(dict(date=day,case=case,ret=res,engine=dict(final_cash=x['final_cash'],worst_hour=x['worst_hour_drawdown'],minimum=x['min_tick_equity']),hourly_dev=delta))
  print('QC',day,'rows',len(logs),'checks',checks,flush=True)
 result=dict(state='PASS',quote_checks=dict(total),total_assertions=checks,maximum_hourly_difference=maxdelta,episodes=logs,limitations=['R8 singleton and efficiency adjunct applied to source research historically selected Jan trade events','No broker validated liquidation or mark for actual Coinexx','All original quotes and both cash and mark-to-market audited independently'])
 path=ROOT/'grid0338_independent_r8_quote_qc.json';path.write_text(json.dumps(result,indent=2));print('PASS',checks,'delta',maxdelta,flush=True)
if __name__=='__main__':main()
