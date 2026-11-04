"""R23 exact UTC paired Coinexx-linked MT5 and Dukascopy quote-domain forensics.

Nine original R21 failing quarter timestamps are frozen from R22. This is a
source-quote comparison, never a claim simultaneous fill at two brokers.
Historical future side/firstTP labels are offline evidence only. Prospectively
observable counters contain no future price data. Price/money units never mix.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'/mnt/data/h1v2_r23_dualbroker/src')
import r23_geometry_and_causal_controls as r

ORIG_NINE=(
 ('02','2026-02-01T23:15:00Z'),('02','2026-02-06T21:45:00Z'),
 ('02','2026-02-12T23:00:00Z'),('02','2026-02-16T23:00:00Z'),
 ('06','2026-06-30T23:00:00Z'),('07','2026-07-02T23:00:00Z'),
 ('07','2026-07-08T23:00:00Z'),('07','2026-07-12T23:00:00Z'),
 ('07','2026-07-17T20:45:00Z'))
SCENARIOS=(
 ('STRICT_QUOTE_TP100_H60_CAP4000_LAG100',4000,8,100,100,60000,100,0),
 ('NEW_QUOTE_TP050_H90_CAP4000_LAG100',4000,8,50,100,90000,100,0),
 ('NEW_QUOTE_TP050_H90_CAP8000_LAG100',8000,8,50,100,90000,100,0),
 ('NEW_QUOTE_TP050_H90_CAP4000_LAG500_SLIP20',4000,8,50,100,90000,500,20),
 ('LOW_TARGET_Q1_TP025_H120_CAP4000_LAG100',4000,1,25,100,120000,100,0),
)


def run_one(source,mon):
 t,b,a,refs,oldf,olde,base,missing,proof=r.source_rec(source,mon)
 allmonths=[(m,x) for m,x in ORIG_NINE if m==mon]
 qkeys=refs['qkeys'];qref=refs['qref'];index={x['utc_quarter']:i for i,x in enumerate(refs['rows'])}
 qs=[index[x] for _,x in allmonths]
 assert len(qs)==len(allmonths)
 allrow=[];pathrows=[];hrows=[];npz={}
 for name,cap,count,tp,stop,horizon,lag,slip in SCENARIOS:
  for qi in qs:
   q0=qkeys[qi]*r.Q;q1=q0+r.Q
   lo=int(np.searchsorted(t,q0,side='left'));hi=int(np.searchsorted(t,q1,side='left'))
   raw_sp=a[lo:hi].astype(np.int64)-b[lo:hi].astype(np.int64)
   qdata,pre=r.r22.trial_from_residual(t,b,a,qkeys,np.array([qi]),shortest_age=0,atleast=count,cap=cap,lag=lag)
   if qdata is None: signal=fill=np.empty(0,np.int32)
   else:signal,fill=qdata
   codes,ends,nets=r.quote_first_passages(t,b,a,fill,tp,stop,horizon,slip)
   wins=np.argwhere(codes==1)
   first=fill[wins[:,0]].astype(np.int32);last=ends[wins[:,0],wins[:,1]].astype(np.int32)
   # Max-count in a single isolated 15m quarter, optimistic boundary crossing.
   picked=r.r22.x.exact_cardinality(t[first],t[last]);isolated=int(len(picked))
   pfx=r.causal_prefix_features(t,b,a,signal)
   side=pfx['flow3'].astype(np.int8)
   chosen=np.where(side==1,codes[:,0],np.where(side==-1,codes[:,1],-4))
   nnet=np.where(side==1,nets[:,0],np.where(side==-1,nets[:,1],-2147483647))
   valid=(chosen==0)|(chosen==1)|(chosen==2)
   asofgood=(chosen==1).sum();asofbad=(chosen==0).sum();asoftout=(chosen==2).sum()
   row={'source':source,'month':mon,'utc_quarter':refs['rows'][qi]['utc_quarter'],'scenario':name,
    'r9_SYNTH_reference_UTC_quarter':int(qref[qi]),
    'R22_C10_global_future_selected_UTC_quarter':int(base[qi]),
    'observed_source_quote_count':int(hi-lo),'distinct_ms_quote_count':int(np.count_nonzero(np.diff(t[lo:hi])>0))+int(hi>lo),
    'first_source_quote_after_quarter_start_ms':int(t[lo]-q0) if hi>lo else None,
    'last_source_quote_to_end_ms':int(q1-t[hi-1]) if hi>lo else None,
    'spread_p10_USD':float(np.percentile(raw_sp,10)/1000) if len(raw_sp) else None,
    'spread_p50_USD':float(np.median(raw_sp)/1000) if len(raw_sp) else None,
    'spread_p90_USD':float(np.percentile(raw_sp,90)/1000) if len(raw_sp) else None,
    'source_raw_spread_over4_fraction':float(np.mean(raw_sp>4000)) if len(raw_sp) else None,
    'source_raw_spread_over8_fraction':float(np.mean(raw_sp>8000)) if len(raw_sp) else None,
    'original_observed_quote_gap_over15s':int(np.count_nonzero(np.diff(t[lo:hi])>15000)),
    'signal_before_fill_ordinal_count':int(pre['eligible']),'actual_fill_quote_ordinal_count':int(len(fill)),
    'two_sides_FIRST_TP_GOOD':int((codes==1).sum()),'two_sides_FIRST_STOP_BAD':int((codes==0).sum()),
    'two_sides_TIMEOUT':int((codes==2).sum()),'two_sides_CENSORED':int((codes==-3).sum()),
    'optimistic_isolated_one_position_hindsight_upper_for_THIS_VARIANT':isolated,
    'optimistic_isolated_quarter_R9_target_reached':int(isolated>=qref[qi]),
    'asof_PAST3S_SIGN_attempt_count':int(np.count_nonzero(side)),
    'asof_PAST3S_SIGN_GOOD':int(asofgood),'asof_PAST3S_SIGN_STOP':int(asofbad),
    'asof_PAST3S_SIGN_TIMEOUT':int(asoftout),
    'asof_PAST3S_SIGN_CENSORED':int((chosen==-3).sum()),
    'asof_PAST3S_SIGN_WIN_RATE_COMPLETED':float(asofgood/valid.sum()) if valid.sum() else None,
    'asof_PAST3S_SIGN_MEAN_NET_PRICE_USD':float(nnet[valid].mean()/1000) if valid.sum() else None,
    'R23_branch_research_only_future_oracle':True,
    'broker_quote_not_broker_dealer_fill':True}
   allrow.append(row)
   for k,val in {'signal':signal,'fill':fill,'bidask_codes_both_sides':codes,'exit_bidask_ordinal_both_sides':ends,
     'net_bidask_quote_price_both_sides':nets,'future_good_fill':first,'future_good_exit':last,
     'future_known_hindsight_isolated_best_fill':first[picked],'future_known_hindsight_isolated_best_exit':last[picked],
     'asof_past3s_direction':side}.items():
    npz[name+'__'+str(qi)+'__'+k]=val
  print('R23 paired',source,mon,name,'quarters',len(qs),flush=True)
 out=r.OUT
 stem=f'R23_PAIRED_{source}_{mon}'
 csvf=out/f'{stem}_ALL_ORIGINAL_R21_DEFICIT_QUARTER_5_EXPERIMENTS.csv';r.sink(csvf,allrow)
 npzf=out/f'{stem}_ALL_FULL_NEGATIVE_POSITIVE_SOURCE_ORDINALS.npz';np.savez_compressed(npzf,**npz)
 receipt={'source':source,'month':mon,'raw_SHA':r.r22.p.r18.PINS[source][mon],
  'original_quote_count':len(t),'aligned_R9_SYNTH_reference_sha':refs['sha256'],
  'nine_source_quarter_subset_count':len(qs), 'experiments_each':len(SCENARIOS),
  'observed_vs_future_source_boundary': 'all signal rules use past, outcome and interval oracle future',
  'csv_rows':allrow,
  'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':r.sha(p)} for p in (csvf,npzf)}}
 fp=out/f'{stem}_RECEIPT.json';fp.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 return receipt


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,choices=r.r22.SOURCES)
 parser.add_argument('--month',required=True,choices=('02','06','07'))
 a=parser.parse_args();run_one(a.source,a.month)
