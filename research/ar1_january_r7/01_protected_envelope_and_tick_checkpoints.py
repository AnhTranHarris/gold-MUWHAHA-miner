"""AR1 January R7. SOURCE-EXACT, immutable original R9 account and quotes.
Research only, never change a trade or simulate live broker fills.
Atlas-led discovery: characterise protected price-path corridor vs nonpositive-cycle losses.
"""
from pathlib import Path
import pandas as pd, numpy as np, gzip, zipfile, json, hashlib
O=Path('/mnt/data/AR1_JAN_R7_PROFIT_FIRST_REBUILD_20261118')
Z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=Z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as f: D=pd.read_csv(f)
assert len(D)==27980 and int(D.net_cents.sum())==4152082
D['protected']=D.protected_R9_positive_leg.astype(bool)|D.protected_R9_positive_cycle.astype(bool)
assert D.protected.sum()==26576 and (~D.protected).sum()==1404
R=pd.read_csv('/mnt/data/AR1_JAN_R6_ACCOUNT_RISK_INTEGRATED_20261118/JAN_R6_ALL_27980_INTEGRATED_ACCOUNT_RISK_OBSERVER.csv.gz')
assert np.array_equal(D.source_row,R.source_row)
M=pd.read_csv('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118/JAN_27980_STRICT_ENTRY_CAUSAL_MICRO_HA_FIB.csv')
assert np.array_equal(D.source_row,M.source_row)
T=pd.DataFrame({'source_row':D.source_row,'entry_time_broker':D.entry_time_broker,'exit_time_broker':D.exit_time_broker,'entry_s_ms':pd.to_datetime(D.entry_time_broker,utc=True).astype('int64')//1000000,'leg':D.leg,'side':D.side,'gap_cents':D.frozen_s100_gap_cents,'original_R9_net_cents':D.net_cents,'original_R9_book_before_cents':D.book_before_cents,'protected_RETROSPECTIVE_ONLY':D.protected,'original_positive_cycle_RETROSPECTIVE_ONLY':D.protected_R9_positive_cycle.astype(bool),'atomic_family_RETROSPECTIVE_ONLY':D.atomic,'quote_strict':D.strict,'quote_count_archive':D.quote_count,'observed_DD_archive':D.observed_peakDD_cents,'original_cycle_net_cents':D.cycle_net_cents,'R5_held_day_loss_score':R.AR1_R5_loss_probability_held_day_chronological})
for c in ['quotes10','quotes60','mean_spread60_USD','disp10_USD','disp60_USD','travel10_USD','travel60_USD','micro1s_ha_body_atr_side','micro5s_ha_body_atr_side','micro15s_ha_body_atr_side','micro1s_fib_retrace','micro5s_fib_retrace','micro15s_fib_retrace']:
 T[c]=M[c]
T.to_csv(O/'JAN_IMMUTABLE_27980_PROTECTED_CONTEXT.csv.gz',index=False,compression='gzip')
print('JAN_MASTER_READY',len(T),flush=True)
rows=[];source_counts=[]
for date,g in D.groupby(D.entry_time_broker.str[:10],sort=True):
 p=Path('/mnt/data')/f'R9_REAL_{date}_ticks.csv.gz'
 a=pd.read_csv(p,compression='gzip',usecols=['run_label','time_msc','bid','ask'],dtype={'time_msc':'int64','bid':'float64','ask':'float64'})
 assert a.run_label.eq('REAL').all()
 ms=a.time_msc.to_numpy(np.int64);bid=np.rint(a.bid.to_numpy(float)*100).astype(np.int64);ask=np.rint(a.ask.to_numpy(float)*100).astype(np.int64)
 assert (np.diff(ms)>=0).all() and np.all(ask>=bid)
 prev_close=-1;noquote=0;holdcount=0
 for i,tr in g.iterrows():
  ent=int(tr.open_ms);ext=int(tr.close_ms)
  lo=int(np.searchsorted(ms,max(ent,prev_close),side='right' if ent<=prev_close else 'left'))
  hi=int(np.searchsorted(ms,ext,side='right'))
  tt=ms[lo:hi];bb=bid[lo:hi];aa=ask[lo:hi];q=bb if tr.side=='buy' else -aa
  assert len(tt)==int(tr.quote_count),(date,tr.source_row,len(tt),tr.quote_count)
  holdcount+=len(tt);noquote+=(len(tt)==0)
  if len(tt):
   peak=np.maximum.accumulate(q);dd=peak-q
   marks=bb-aa[0] if tr.side=='buy' else bb[0]-aa
   assert int(dd.max())==int(tr.observed_peakDD_cents)
   assert int(max(0,marks.max()))==int(tr.observed_MFE_cents),(date,tr.source_row,'MFE',max(0,marks.max()),tr.observed_MFE_cents)
   assert int(max(0,-marks.min()))==int(tr.observed_MAE_cents),(date,tr.source_row,'MAE',max(0,-marks.min()),tr.observed_MAE_cents)
  for secs in (5,10,15):
   cutoff=int(T.entry_s_ms.iloc[i])+secs*1000
   # Only if original R9 trade still scheduled to be open at the checkpoint.
   if cutoff>ext or cutoff<ent:continue
   k=int(np.searchsorted(tt,cutoff,side='right'))
   if k==0:continue
   qm=q[:k];tm=tt[:k];bm=bb[:k];am=aa[:k];m=marks[:k]
   peak=np.maximum.accumulate(qm);draw=peak-qm
   # Price-reference independent total path travel; not executed net PnL.
   dif=np.diff(qm)
   # last prior 5s signed momentum (liquidation-side, positive is favorable)
   laststart=int(np.searchsorted(tm,cutoff-5000,side='left'))
   path_5s=qm[laststart:]
   mark=int(m[-1]);spreadnow=int(am[-1]-bm[-1])
   rows.append((int(tr.source_row),secs,int(cutoff),int(len(qm)),int(max(0,m.max())),int(max(0,-m.min())),int(draw.max()),mark,int(spreadnow),float(np.abs(dif).sum()),float(qm[-1]-qm[max(0,k-5)]),float(path_5s[-1]-path_5s[0]) if len(path_5s) else np.nan,int(tm[-1]),int(tt[0])))
  prev_close=ext
 source_counts.append({'day':date,'original_quote_count':len(ms),'r9_legs':len(g),'fixed_hold_quotes':holdcount,'missing_hold_windows':noquote,'original_gzip_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 print('DAY_DONE',date,len(ms),len(g),flush=True)
cols=['source_row','elapsed_entry_s','checkpoint_ms','quote_count_cumulative','MFE_to_checkpoint_cents','MAE_to_checkpoint_cents','peakDD_to_checkpoint_cents','liquidation_mark_from_first_quote_cents','last_spread_cents','total_liquidation_path_travel_cents','last_five_quotes_momentum_cents','last_five_seconds_momentum_cents','last_quote_ms','first_inside_quote_ms']
C=pd.DataFrame(rows,columns=cols)
assert sum(x['original_quote_count'] for x in source_counts)==7699274
assert sum(x['fixed_hold_quotes'] for x in source_counts)==2272602
assert sum(x['missing_hold_windows'] for x in source_counts)==33
C.to_csv(O/'JAN_CAUSAL_INTRAHOLD_5_10_15S_CHECKPOINTS.csv.gz',index=False,compression='gzip')
summary=[]
for secs,g in C.groupby('elapsed_entry_s'):
 g=g.merge(T[['source_row','protected_RETROSPECTIVE_ONLY','gap_cents','leg','original_R9_net_cents']],on='source_row',validate='many_to_one')
 for prot,x in g.groupby('protected_RETROSPECTIVE_ONLY'):
  summary.append({'checkpoint_sec':int(secs),'protected':bool(prot),'trades_with_checkpoint':len(x),'max_dd_cents':int(x.peakDD_to_checkpoint_cents.max()),'p95_dd_cents':float(x.peakDD_to_checkpoint_cents.quantile(.95)),'max_MAE_cents':int(x.MAE_to_checkpoint_cents.max()),'median_MFE_cents':float(x.MFE_to_checkpoint_cents.median()),'median_current_mark_cents':float(x.liquidation_mark_from_first_quote_cents.median())})
pd.DataFrame(summary).to_csv(O/'JAN_PROTECTED_VS_NONPROTECTED_CAUSAL_CHECKPOINT_ENVELOPES.csv',index=False)
rec={'original_trades':len(D),'original_protected':int(D.protected.sum()),'original_nonprotected':int((~D.protected).sum()),'source_counts':source_counts,'tick_quote_total':7699274,'fixed_hold_quote_total':2272602,'checkpoint_records':len(C),'history_unchanged':True,'no_trade_actions':True}
(O/'JAN_R7_TICK_CHECKPOINT_SOURCE_RECEIPT.json').write_text(json.dumps(rec,indent=2))
print('CHECKPOINTS_COMPLETE',len(C),'protected',int(D.protected.sum()),flush=True)
