#!/usr/bin/env python3
"""FULL January fixed-R9-entry/exit and original Coinexx REAL TickLogger Python replay.
Only OBSERVATIONAL AR1 states; no order actions, alternate exits, P&L rewrite or entry suppression.
"""
from pathlib import Path
import pandas as pd,numpy as np,json,hashlib,time
P=Path('/mnt/data/AR1_JAN_R2_COMPLETED_REVERSE_ENGINEERING_20261118')
r=pd.read_csv('/mnt/data/AR1_JAN_R1_20261118/JAN_ALL_27980_IMMUTABLE_R9_COINEXX_TARGETS.csv')
s=pd.read_csv(P/'JAN_27980_IMMUTABLE_TRADES_WITH_FITTED_AR1_MODEL_SCORES.csv.gz')
assert len(r)==len(s)==27980 and r.source_row.equals(s.source_row)
r['day']=r.entry_time_broker.str[:10];r['p_pressure_model']=s.P_util25_full_January_fit.to_numpy();r['p_loss_model']=s.P_r9_negative_full_January_fit.to_numpy()
model=json.load(open(P/'JAN_AR1_REVERSE_ENGINEERED_NUMERIC_FORMULA_AND_CROSSDAY_DIAGNOSTICS.json'))
p90_pressure=model['full_january_score_percentiles']['util25']['0.9']; p90_loss=model['full_january_score_percentiles']['r9_negative']['0.9']
result=[]; dayreceipts=[];tic=time.monotonic()
for date,day in r.groupby('day',sort=True):
 path=Path('/mnt/data')/f'R9_REAL_{date}_ticks.csv.gz'
 if not path.is_file():raise FileNotFoundError(path)
 h=hashlib.sha256(path.read_bytes()).hexdigest()
 # pandas processes untouched gz file, no rebuilt tick source. Intraday quote sequencing maintained with stable row order.
 ticks=pd.read_csv(path,compression='gzip',usecols=['run_label','time_msc','bid','ask'],dtype={'run_label':'category','time_msc':'int64','bid':'float64','ask':'float64'})
 assert ticks.run_label.astype('string').eq('REAL').all()
 msc=ticks.time_msc.to_numpy(dtype=np.int64);bid=np.rint(ticks.bid.to_numpy()*100).astype(np.int64);ask=np.rint(ticks.ask.to_numpy()*100).astype(np.int64)
 assert (np.diff(msc)>=0).all() and (ask>=bid).all();start_ct=len(result);npcount=0;previous_fixed_close_ms=-1
 for tr in day.itertuples(index=False):
  a=int(np.searchsorted(msc,max(int(tr.open_ms),int(previous_fixed_close_ms)),side='right' if int(tr.open_ms)<=int(previous_fixed_close_ms) else 'left'));b=int(np.searchsorted(msc,tr.close_ms,side='right'))  # Original AR1 R3 inclusive exit-ms convention
  q=bid[a:b] if tr.side=='buy' else -ask[a:b]
  when=msc[a:b];n=len(q)
  row={'source_row':int(tr.source_row),'S100_gap_cents':int(tr.frozen_s100_gap_cents),'quote_count_python':n,'inside_window_eligible':int(n>0),'original_net_cents':int(tr.net_cents),'original_book_before_cents':int(tr.book_before_cents),'original_book_after_cents':int(tr.book_after_cents),'profit_R9':bool(tr.net_cents>0),'strict_anchor_time':bool(tr.strict),'family':tr.atomic,'entry_time_broker':tr.entry_time_broker,'fixed_open_ms':int(tr.open_ms),'fixed_close_ms':int(tr.close_ms),'p_util25_entry':float(tr.p_pressure_model),'p_R9negative_entry':float(tr.p_loss_model),'entry_risk_priority_top10pct':bool(tr.p_pressure_model>=p90_pressure),'entry_loss_priority_top10pct':bool(tr.p_loss_model>=p90_loss)}
  if not n:
   row.update({'DD_cents_python':np.nan,'MAE_cents_python':np.nan,'MFE_cents_python':np.nan,'first_u25_touch_ms':-1,'first_u50_touch_ms':-1,'first_u75_touch_ms':-1,'first_u90_touch_ms':-1,'first_full_S100_touch_ms':-1,'dd_trough_ms_python':-1,'last_quote_ms':-1,'max_spread_cents_python':np.nan})
  else:
   peaks=np.maximum.accumulate(q);dd=peaks-q;DD=int(dd.max());i=int(dd.argmax());entry_side_ref=(ask[a] if tr.side=='buy' else bid[a]); marks=(bid[a:b]-entry_side_ref if tr.side=='buy' else entry_side_ref-ask[a:b]);mae=int(max(0,-marks.min()));mfe=int(max(0,marks.max()))
   row.update({'DD_cents_python':DD,'MAE_cents_python':mae,'MFE_cents_python':mfe,'dd_trough_ms_python':int(when[i]),'last_quote_ms':int(when[-1]),'max_spread_cents_python':int((ask[a:b]-bid[a:b]).max())})
   for nm,f in [('first_u25_touch_ms',.25),('first_u50_touch_ms',.5),('first_u75_touch_ms',.75),('first_u90_touch_ms',.90),('first_full_S100_touch_ms',1.0)]:
    idx=np.flatnonzero(dd>=tr.frozen_s100_gap_cents*f);row[nm]=int(when[idx[0]]) if len(idx) else -1
  result.append(row)
  previous_fixed_close_ms=int(tr.close_ms)
  if n:npcount+=n
 # Every January quote is traversed per day; only quotes inside original fixed trade windows are evaluated as intratrade.
 dayreceipts.append({'date':date,'input_quotes':len(ticks),'r9_fixed_trades':len(day),'inside_position_quotes':int(npcount),'compressed_original_SHA256':h})
 print('PYTHON-REAL-TICK',date,'quotes',len(ticks),'trades',len(day),'inside_quote_events',npcount,flush=True)
 del ticks,msc,bid,ask
out=pd.DataFrame(result).sort_values('source_row').reset_index(drop=True)
assert len(out)==len(r)==27980 and out.source_row.equals(r.source_row)
assert out.original_net_cents.sum()==4152082 and (out.original_book_after_cents.iloc[-1]==4162082)
badcnt=out.quote_count_python.ne(r.quote_count.astype(int))
print('COUNT_DIFFERENCES',int(badcnt.sum()),'sum_abs',int((out.quote_count_python-r.quote_count.astype(int)).abs().sum()))
print(out.loc[badcnt,['source_row','entry_time_broker','fixed_open_ms','fixed_close_ms','quote_count_python']].head(30).assign(source_count=r.loc[badcnt,'quote_count'].head(30).to_numpy()).to_string(index=False))
out.to_csv(P/'JAN_DEBUG_PYTHON_DIRECT_QUOTE_COUNT_AND_PRICES.csv.gz',index=False,compression='gzip')
# A mismatched source row is a real QA discrepancy: do not silently equate it to valid source parity.
assert out.quote_count_python.equals(r.quote_count.astype(int)), 'COUNT_MISMATCH WITH ORIGINAL R3' 
match=out.inside_window_eligible.eq(1)
for n,col in [('DD_cents_python','observed_peakDD_cents'),('MAE_cents_python','observed_MAE_cents'),('MFE_cents_python','observed_MFE_cents')]:
 dif=(out.loc[match,n].to_numpy(dtype=int)-r.loc[match,col].to_numpy(dtype=int));bad=int((dif!=0).sum());print('PARITY',n,'vs',col,'mismatches',bad,'largest',abs(dif).max() if len(dif) else 0)
 if bad:print('FIRST_MISMATCH_SOURCE_ROWS',out.loc[match].loc[dif!=0,'source_row'].head(10).tolist())
 # For source parity, if minor entry-offset mismatch is due to first-quote assumptions, document rather than claim exact.
 assert bad==0, f'PRICE_PARITY_MISMATCH {n} {bad}'
assert out.first_full_S100_touch_ms.eq(-1).all()
assert sum(x['input_quotes'] for x in dayreceipts)==7699274
for x in dayreceipts:assert x['compressed_original_SHA256']==json.load(__import__('zipfile').ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip').open('JAN_RESEARCH_AUDIT_RECEIPT.json'))['pinned_original_Coinexx_tick_archives_sha256'][f"R9_REAL_{x['date']}_ticks.csv.gz"]
out.to_csv(P/'JAN_ALL_27980_PYTHON_REAL_TICK_REPLAY_POLICY_ALERT_TIMES.csv.gz',index=False,compression='gzip')
receipt={'january_trades':len(out),'original_R9_net_USD':out.original_net_cents.sum()/100,'original_R9_end_book_USD':int(out.original_book_after_cents.iloc[-1])/100,'source_quotes':sum(x['input_quotes'] for x in dayreceipts),'direct_inside_position_quotes':sum(x['inside_position_quotes'] for x in dayreceipts),'zero_quote_trades':int(out.quote_count_python.eq(0).sum()),'u25_touches':int(out.first_u25_touch_ms.ge(0).sum()),'u50_touches':int(out.first_u50_touch_ms.ge(0).sum()),'u75_touches':int(out.first_u75_touch_ms.ge(0).sum()),'u90_touches':int(out.first_u90_touch_ms.ge(0).sum()),'full_S100_observed_touches':int(out.first_full_S100_touch_ms.ge(0).sum()),'protected_positive_in_u25':int((out.profit_R9&out.first_u25_touch_ms.ge(0)).sum()),'entry_priority_top10pct':int(out.entry_risk_priority_top10pct.sum()),'days':dayreceipts,'run_seconds':time.monotonic()-tic,'zero_trade_modifications':True,'zero_alternative_exits':True,'no_forward_test':True}
json.dump(receipt,open(P/'JAN_PYTHON_CHRONOLOGICAL_REPLAY_CERTIFICATION.json','w'),indent=2)
print('PYTHON-REPLAY-ALL-JANUARY-COMPLETE',json.dumps({k:v for k,v in receipt.items() if k!='days'},indent=2))
