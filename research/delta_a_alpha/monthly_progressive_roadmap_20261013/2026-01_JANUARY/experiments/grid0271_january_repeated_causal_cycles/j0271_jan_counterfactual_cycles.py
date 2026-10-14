"""Research ONLY: exact Jan original tick Bid/Ask matched to EXISTING V1 entries.
Static exit/direction what-if, no trade entry selection or portfolio capacity simulation.
NOT a full V1 replay, no inference of source-exact original Watchdog edge.
"""
from pathlib import Path
import numpy as np,pandas as pd,json,csv,time
from numba import njit
ROOT=Path('/mnt/data/GRID0271_JAN_RESEARCH');OUT=ROOT/'JAN_ORIGINAL_TICK_COUNTERFACTUAL';OUT.mkdir(exist_ok=True)
src=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
@njit(cache=True)
def trial(t,a,b,idx,side,original_price,stop,target,horizon,trail_start,trail_gap,reverse):
 n=len(idx);cash=np.empty(n);hold=np.empty(n);code=np.empty(n,np.int8)
 for k in range(n):
  i=idx[k];start=t[i];sgn=-int(side[k]) if reverse else int(side[k]);enter=(b[i] if sgn==-1 else a[i])/1000.
  if not reverse:enter=original_price[k]
  trail=-stop;peak=-1e8;j=i
  while j<len(t):
   px=(b[j] if sgn==1 else a[j])/1000.;fav=sgn*(px-enter)
   peak=max(fav,peak)
   if trail_start>0 and peak>=trail_start:trail=max(trail,peak-trail_gap)
   if fav<=trail:rc=1;break
   if fav>=target:rc=2;break
   if t[j]>=start+horizon:rc=3;break
   j+=1
  if j==len(t):j-=1;rc=4
  cash[k]=sgn*((b[j] if sgn==1 else a[j])/1000.-enter)-.20;hold[k]=t[j]-start;code[k]=rc
 return cash,hold,code

def summarize(v,days):
 gp=v[v>0].sum();gl=v[v<0].sum();d={k:round(float(v[days==k].sum()),4) for k in np.unique(days)}
 return dict(net=round(float(v.sum()),4),n=len(v),wins=int((v>0).sum()),pf=round(float(gp/-gl),4) if gl<0 else None,gross_profit=round(float(gp),4),gross_loss=round(float(gl),4),positive_entry_days=sum(x>0 for x in d.values()),day_cohort=d)

def main():
 start=time.monotonic();print('LOAD ORIGINAL JAN 9.1M TICKS',flush=True)
 f=pd.read_csv(src,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
 t=f.timestamp_ms_utc.to_numpy();a=f.ask_raw.to_numpy();b=f.bid_raw.to_numpy()
 assert len(t)==9135062 and np.all(t[1:]>=t[:-1]);del f
 tr=pd.read_csv(ROOT/'JAN_BASELINE/all_completed_shadow_trades.csv')
 ix=np.searchsorted(t,tr.entry_utc_ms.to_numpy(np.int64));assert np.all(t[ix]==tr.entry_utc_ms.to_numpy(np.int64))
 sgn=np.where(tr.side=='BUY',1,-1).astype('int8');op=tr.entry_price_usd_oz.to_numpy(float)
 days=pd.to_datetime(tr.entry_utc_ms,unit='ms',utc=True).dt.strftime('%Y-%m-%d').to_numpy()
 base=tr.net_shadow_usd.to_numpy(float)
 print('ENTRY MATCH: max raw first-tick diff',np.max(np.abs(np.where(sgn>0,a[ix],b[ix])/1000-op)),flush=True)
 cases=[('FAST10_TP1_SL2',2,1,10000,0,0,0),('FAST30_TP1_SL2',2,1,30000,0,0,0),('FAST60_TP2_SL3',3,2,60000,0,0,0),('HOLD120_TP3_SL3',3,3,120000,0,0,0),('HOLD240_TP4_SL3',3,4,240000,0,0,0),('HOLD240_TP4_SL4',4,4,240000,0,0,0),('TRAIL120_TP4_SL3_T1_G1',3,4,120000,1,1,0),('TRAIL240_TP4_SL3_T2_G1',3,4,240000,2,1,0),('REVERSE10_TP1_SL2',2,1,10000,0,0,1),('REVERSE60_TP2_SL3',3,2,60000,0,0,1),('REVERSE120_TP3_SL3',3,3,120000,0,0,1)]
 results=[];early=days<'2026-01-17'
 for case,sl,tp,ms,ts,tg,rev in cases:
  x,h,c=trial(t,a,b,ix,sgn,op,sl,tp,ms,ts,tg,rev);o=summarize(x,days);o.update(case=case,stop=sl,target=tp,max_horizon_ms=ms,reverse_direction=bool(rev),first_half_net=round(float(x[early].sum()),4),second_half_net=round(float(x[~early].sum()),4),mean_hold_s=round(float(h.mean()/1000),3),stop_fraction=round(float((c==1).mean()),4),target_fraction=round(float((c==2).mean()),4));results.append(o);print('TRIAL',case,o['net'],o['pf'],o['positive_entry_days'],flush=True)
 record={'scope':'STATIC_QUOTE_SIDED_SAME_EXISTING_ENTRIES_COUNTERFACTUALS_ONLY_NO_PORTFOLIO_CONCURRENCY_NO_CAUSAL_ROUTER_CHANGE','source_original_dukascopy_sha256':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','tick_count':len(t),'unchanged_v1_baseline':summarize(base,days),'trials':results,'target_R9_synth_net':41520.82,'narrow_limit':'This does not represent a full V1 live entry or funded replay; profitable exit policies cannot be promoted without strict full causal order+capacity and crossmonth QA','runtime_s':time.monotonic()-start}
 (OUT/'JAN_REPLAY_STATIC_COUNTERFACTUAL_11_TRIALS.json').write_text(json.dumps(record,indent=2))
 with (OUT/'JAN_STATIC_TRIALS.csv').open('w',newline='') as f:
  fields=['case','net','pf','gross_profit','gross_loss','n','wins','positive_entry_days','first_half_net','second_half_net','mean_hold_s','stop_fraction','target_fraction'];w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader();w.writerows(results)
 print('ALL_DONE',len(results),'seconds',round(time.monotonic()-start,1),flush=True)
if __name__=='__main__':main()
