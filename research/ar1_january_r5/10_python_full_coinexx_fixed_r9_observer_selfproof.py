"""Full January original Coinexx REAL TickLogger chronological Python replay of research observer.
ALWAYS preserve original R9 fixed entries/exits, booked outcomes, frozen S100 tiers.
Strict predictive state from original entry second, intrahold marks from preserved original R1 fixed windows.
Never emulate an executed stop, filter or account ledger change.
"""
import hashlib,json,time,zipfile,gzip
from pathlib import Path
import numpy as np,pandas as pd
O=Path('/mnt/data/AR1_JAN_R5_MECHANISM_FIRST_20261118');started=time.monotonic()
z=zipfile.ZipFile('/mnt/data/AR1_JANUARY_R1_SOURCE_EXACT_PROGRESSIVE_RESEARCH_20261118.zip')
with gzip.GzipFile(fileobj=z.open('JAN_ALL_27980_CAUSAL_INDICATORS_AND_UNCHANGED_OUTCOMES.csv.gz')) as f:d=pd.read_csv(f)
R=pd.read_csv(O/'JAN_27980_SOURCE_EXACT_STRICT_ENTRY_RISK_OBSERVER_FULL_LEDGER.csv.gz')
X=pd.read_csv(O/'JAN_STRICT_PREENTRY_MODEL_FEATURES.csv.gz',usecols=['gross_60m_to_book','gross_5m_to_book','R9_asof_HWM_drawdown_pct','previous_5_realized_loss_count','book_tie_ambiguity'])
assert len(d)==len(R)==len(X)==27980 and d.source_row.equals(R.source_row)
pinned=json.load(z.open('JAN_RESEARCH_AUDIT_RECEIPT.json'))['pinned_original_Coinexx_tick_archives_sha256']
results=[];day_receipts=[]
for date,group in d.groupby(d.entry_time_broker.str[:10],sort=True):
 p=Path('/mnt/data')/f'R9_REAL_{date}_ticks.csv.gz';sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==pinned[p.name]
 r=pd.read_csv(p,compression='gzip',usecols=['run_label','time_msc','bid','ask'],dtype={'run_label':'category','time_msc':'int64','bid':'float64','ask':'float64'})
 assert r.run_label.astype(str).eq('REAL').all()
 ms=r.time_msc.to_numpy(dtype=np.int64);bid=np.rint(r.bid.to_numpy()*100).astype(np.int64);ask=np.rint(r.ask.to_numpy()*100).astype(np.int64)
 assert (np.diff(ms)>=0).all() and (ask>=bid).all()
 day_count=0;prior_close=-1
 for idx,tr in group.iterrows():
  a=int(np.searchsorted(ms,max(int(tr.open_ms),int(prior_close)),side='right' if int(tr.open_ms)<=int(prior_close) else 'left'))
  b=int(np.searchsorted(ms,int(tr.close_ms),side='right'))
  q=bid[a:b] if tr.side=='buy' else -ask[a:b]
  winms=ms[a:b]
  nr=len(q)
  row={'source_row':int(tr.source_row),'original_fixed_entry_ms':int(tr.open_ms),'original_fixed_exit_ms':int(tr.close_ms),
    'original_R9_net_cents':int(tr.net_cents),'original_R9_balance_before_cents':int(tr.book_before_cents),'original_R9_balance_after_cents':int(tr.book_after_cents),
    'real_Coinexx_inside_window_quote_count':int(nr),'quote_quality_strict':bool(tr.strict),
    'original_s100_gap_cents':int(tr.frozen_s100_gap_cents),
    'prediction_strict_asof_entry_R9sec_held_chrono_score':R.AR1_strict_entry_prior_training_held_score.iloc[idx],
    'prediction_full_January_fitted_DIAGNOSTIC_ONLY':float(R.AR1_strict_entry_Jan_full_fit_DIAGNOSTIC.iloc[idx]),
    'R9_book_prior_5m_gross_loss_to_book':X.gross_5m_to_book.iloc[idx],
    'R9_book_prior_60m_gross_loss_to_book':X.gross_60m_to_book.iloc[idx],
    'R9_book_preentry_hwm_drawdown_pct':X.R9_asof_HWM_drawdown_pct.iloc[idx],
    'R9_book_prior5_negative_trade_count':X.previous_5_realized_loss_count.iloc[idx],
    'same_second_prior_exit_ambiguity':bool(X.book_tie_ambiguity.iloc[idx]),'trade_action':None}
  if nr:
   peaks=np.maximum.accumulate(q);dd=peaks-q
   marks=bid[a:b]-ask[a] if tr.side=='buy' else bid[a]-ask[a:b]
   row.update({'real_Coinexx_MFE_cents':int(max(0,marks.max())),'real_Coinexx_MAE_cents':int(max(0,-marks.min())),'real_Coinexx_peak_to_trough_DD_cents':int(dd.max())})
   for lab,fract in [('u25',.25),('u50',.5),('u75',.75),('u90',.90),('s100_full_touch',1.)]:
    ar=np.flatnonzero(dd>=tr.frozen_s100_gap_cents*fract)
    row[f'Coinexx_{lab}_first_observed_quote_ms']=int(winms[ar[0]]) if len(ar) else -1
  else:
   row.update({'real_Coinexx_MFE_cents':np.nan,'real_Coinexx_MAE_cents':np.nan,'real_Coinexx_peak_to_trough_DD_cents':np.nan})
   for lab in ['u25','u50','u75','u90','s100_full_touch']:row[f'Coinexx_{lab}_first_observed_quote_ms']=-1
  assert nr==int(tr.quote_count)
  if nr:
   assert row['real_Coinexx_MFE_cents']==int(tr.observed_MFE_cents)
   assert row['real_Coinexx_MAE_cents']==int(tr.observed_MAE_cents)
   assert row['real_Coinexx_peak_to_trough_DD_cents']==int(tr.observed_peakDD_cents)
  day_count+=nr;results.append(row)
  prior_close=int(tr.close_ms)
 day_receipts.append({'day':date,'original_gzip_SHA256':sha,'all_Coinexx_quotes':len(ms),'original_R9_trades':len(group),'inside_R9_window_quotes':day_count})
 print('FULL_JANUARY_PYTHON_SELFPROOF_DAY',date,'quotes',len(ms),'trades',len(group),flush=True)
 del r,ms,bid,ask
out=pd.DataFrame(results).sort_values('source_row').reset_index(drop=True)
assert len(out)==27980 and out.source_row.equals(d.source_row)
assert int(out.original_R9_net_cents.sum())==4152082 and out.original_R9_balance_after_cents.iloc[-1]==4162082
assert int(sum(x['all_Coinexx_quotes'] for x in day_receipts))==7699274
assert (out.Coinexx_s100_full_touch_first_observed_quote_ms<0).all()
assert out.trade_action.isna().all()
out.to_csv(O/'JAN_ALL_27980_SOURCE_EXACT_RISK_OBSERVER_REAL_TICK_PYTHON_SELFPROOF.csv.gz',index=False,compression='gzip')
receipt={'original_R9_trades_reconciled':len(out),'original_R9_net_USD':41520.82,'original_R9_closing_book_USD':41620.82,
 'original_Coinexx_REAL_ticks_read':int(sum(x['all_Coinexx_quotes'] for x in day_receipts)),
 'original_real_tick_hold_quotes_read':int(sum(x['inside_R9_window_quotes'] for x in day_receipts)),
 'source_exact_count_MFE_MAE_DD_mismatches':0,'zero_inside_quote_windows':int(out.real_Coinexx_inside_window_quote_count.eq(0).sum()),
 'observed_u25_count':int(out.Coinexx_u25_first_observed_quote_ms.ge(0).sum()),
 'observed_u50_count':int(out.Coinexx_u50_first_observed_quote_ms.ge(0).sum()),
 'observed_full_s100_touch_count':int(out.Coinexx_s100_full_touch_first_observed_quote_ms.ge(0).sum()),
 'ar1_loss_predictor_held_forward_date_scored_count':int(out.prediction_strict_asof_entry_R9sec_held_chrono_score.notna().sum()),
 'ar1_loss_predictor_all_original_january_fit_scores':int(out.prediction_full_January_fitted_DIAGNOSTIC_ONLY.notna().sum()),
 'no_alternative_exits':True,'no_historical_trade_rebookings':True,'no_entry_filters':True,
 'calendar_days':day_receipts,'runtime_s':round(time.monotonic()-started,2)}
(O/'JAN_PYTHON_FULL_COINEXX_FIXED_R9_AR1_SELFPROOF_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print('FULL_JANUARY_POLICY_SELFPROOF',json.dumps({k:v for k,v in receipt.items() if k!='calendar_days'},indent=2),flush=True)
