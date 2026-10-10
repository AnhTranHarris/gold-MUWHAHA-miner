"""Real Dukascopy Jan/Feb ALL-QUOTE STMR 032 source L2 state parity.

Original *full* stmr_base.materialize generates source-research bid from real
midpoint, and exact AST of stmr_janjul.bar_states_span is the reference.
Every recorded quote receives a result, not a fitted event sample. The online
port computes boundary transitions from observed first+last quote of each
completed bucket; within a bucket its observable completed state is constant.
Physical fills are not simulated and must use *real* original Bid/Ask.
"""
import sys,hashlib,json,time,argparse
from pathlib import Path
import numpy as np
import pandas as pd
from source_stmr_completed_ema_033 import _OriginalCompletedEMA,TF_WIDTH_MS,TF_LABELS
from test_source_stmr_completed_ema_033 import original_source_function,SRC_MULTI,SRC_DIR,SHA_BASE,SHA_MULTI,SRC_BASE

EXPECTED={
'jan':('XAUUSD_DUKAS_2026_01_ticks.csv(3).gz','d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5',9135062),
'feb':('XAUUSD_DUKAS_2026_02_ticks.csv(3).gz','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d',7538339)
}
def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()

def audit(root,months,output):
 assert sha256(SRC_BASE)==SHA_BASE and sha256(SRC_MULTI)==SHA_MULTI
 sys.path.insert(0,str(SRC_DIR))
 import stmr_base as original_base  # full original source, unchanged
 ref=original_source_function(SRC_MULTI,'bar_states_span')
 evidence={'unit':'C2D3I_JAN032_STMR_SOURCE_EMA_FOUR_ROLE_ORIGINAL_FULL_QUOTE_PARITY',
 'original_sources':{'stmr_base_sha256':SHA_BASE,'stmr_janjul_sha256':SHA_MULTI},
 'scope':'ORIGINAL_STMR_RESEARCH_BID_COMPLETED_8_21_EMA_PARITY_ONLY_NOT_JAN039_FEB045_FEB047_FULL_V1_OR_BROKER_PARITY',
 'months':{},'scientific_limits':['Original source materializes session-dependent research Bid from real midpoint; this cannot substitute for broker executable Bid/Ask L7 fills.', 'No owner-approved source-derived daily, weekly or rolling monthly routing classifier identified in these STMR functions; do not create one.', 'No full Jan-Feb endogenous funded profit is reproduced by this signal audit.']}
 for month in months:
  file,h,n=EXPECTED[month];p=Path(root)/file
  observed_sha=sha256(p)
  if observed_sha!=h:raise ValueError(f'{month} input SHA mismatch')
  st=time.monotonic()
  df=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'int64','ask_raw':'int32','bid_raw':'int32'})
  t=df.timestamp_ms_utc.to_numpy();ask=df.ask_raw.to_numpy();bid=df.bid_raw.to_numpy()
  if len(t)!=n or np.any(t[1:]<t[:-1]):raise AssertionError('missing or reordered source quotes')
  _,source_bid=original_base.materialize(t,ask,bid)
  del df,ask,bid
  result={'source_file':file,'source_sha256':h,'source_quotes':int(n), 'first_time_ms':int(t[0]),'last_time_ms':int(t[-1]),'source_price':'original STMR research c.materialize(t, actual_ask, actual_bid) -> bid', 'role_states':{}}
  for label, width in zip(TF_LABELS,TF_WIDTH_MS):
   start_ix=np.r_[0,np.flatnonzero((t[1:]//width)!=(t[:-1]//width))+1]
   end_ix=np.r_[start_ix[1:]-1,n-1]
   tester=_OriginalCompletedEMA(width)
   online_states=np.empty(len(start_ix),dtype=np.int8)
   complete=0
   for k,(i,e) in enumerate(zip(start_ix,end_ix)):
    online_states[k]=tester.on_quote(int(t[i]),int(source_bid[i]))
    if tester.last_full and tester.completed_end is not None and tester.completed_end<t[i]: complete+=1
    if e>i: tester.on_quote(int(t[e]),int(source_bid[e]))
   expanded=np.repeat(online_states, np.diff(np.r_[start_ix,n]))
   original=ref(t,source_bid,width,8,21)
   mismatches=np.flatnonzero(expanded!=original)
   if len(mismatches):raise AssertionError(f'{month} {label} source parity mismatch at {mismatches[:5]}')
   result['role_states'][label]={
     'timeframe_ms':width,'completed_observed_source_buckets':int(len(start_ix)-1),
     'observed_buckets':int(len(start_ix)),'quote_count_compared':int(n),
     'mismatch_count':int(len(mismatches)),'state_counts':{str(v):int(np.count_nonzero(expanded==v)) for v in (-1,0,1)},
     'first_eligible_bucket_starts_with_full_prehistory':int(complete),
     'missing_wall_clock_buckets_unfilled':int(tester.skipped),
     'original_reference':'verbatim JAN032 stmr_janjul.py::bar_states_span'
   }
   print(f'{month} {label}: n={n:,} source_buckets={len(start_ix):,} mismatch=0 +={np.count_nonzero(expanded==1):,} -={np.count_nonzero(expanded==-1):,}',flush=True)
  evidence['months'][month]=result
  print(f'{month} COMPLETED in {time.monotonic()-st:.1f}s',flush=True)
 Path(output).write_text(json.dumps(evidence,indent=2)+'\n')
 print('AUDIT',output,flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',default='/mnt/data');parser.add_argument('--months',nargs='+',default=['jan','feb']);parser.add_argument('--output',default='STMR_JAN_FEB_FULL_SOURCE_PARITY.json');a=parser.parse_args();audit(a.root,a.months,a.output)