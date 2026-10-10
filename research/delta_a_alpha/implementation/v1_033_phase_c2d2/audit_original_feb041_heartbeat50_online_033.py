"""Independent true 11.4m-quote causal Jan037 HB source generator vs FEB041/FEB042 labels.

Full original FEB042/prepare.py defines expanded FEB041 E/S/D origin; no X/P/H
or future-month results are passed to the online January-source manufacturer.
"""
import sys,time,json,zipfile,hashlib,io
from collections import Counter
from pathlib import Path
import numpy as np,pandas as pd
SRC=Path('/mnt/data/c2d3l_work/032_source');sys.path.insert(0,str(SRC))
import stmr_janjul as j
from original_jan037_heartbeat50_online_033 import OriginalJAN037Heartbeat50ms
ROOT=Path('/mnt/data');FULL=ROOT/'feb_source_phase/FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip'
SHAS=('d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d')
WARM=3900880

def main():
 start=time.time();raw=[]
 for m,sha in zip(('01','02'),SHAS):
  p=ROOT/f'XAUUSD_DUKAS_2026_{m}_ticks.csv(3).gz'
  with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
  raw.append(pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'}))
 jan=raw[0].iloc[-WARM:];feb=raw[1]
 df=pd.concat([jan,feb],ignore_index=True)
 t=df.timestamp_ms_utc.to_numpy(np.int64); a=df.ask_raw.to_numpy(np.int32);b=df.bid_raw.to_numpy(np.int32)
 mid=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32)
 h4,h1,m15,m5=j.make_states(t,b,((8,21),(8,21),(8,21),(8,21)))
 with zipfile.ZipFile(FULL) as z: original=z.read('FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz')
 assert hashlib.sha256(original).hexdigest()=='64339d0e70dfdb9e85fbb90fb446f96ac1190da681b5e9520a442e3958daa29e'
 with np.load(io.BytesIO(original),allow_pickle=False) as z:
  mask=z['S']>=17;E=z['E'][mask];S=z['S'][mask];D=z['D'][mask]
 port=OriginalJAN037Heartbeat50ms();out_idx=0;mismatch=0;first=[];count=Counter();unaccounted_jan=0
 for idx in range(len(t)):
  r=port.on_observed_quote(idx,int(t[idx]),int(mid[idx]),int(h4[idx]),int(h1[idx]),int(m15[idx]),int(m5[idx]))
  if r is None: continue
  if idx<WARM:
   unaccounted_jan+=1
   continue
  if out_idx>=len(E): mismatch+=1;continue
  if (r.quote_ordinal,r.source_id,r.side)!=(int(E[out_idx]),int(S[out_idx]),int(D[out_idx])):
   mismatch+=1
   if len(first)<4:first.append((idx,r.quote_ordinal,r.source_id,r.side,int(E[out_idx]),int(S[out_idx]),int(D[out_idx])))
  count[r.source_id]+=1
  out_idx+=1
 mismatch+=abs(out_idx-len(E))
 report={'full_source_authority':['Unchanged JAN037 original 032_source/gamma02_campaign_heartbeat_019.py','Unchanged original FEB042/prepare.py','Original FEB042 prepared source E/S/D'],
 'source_type':'ORIGINAL_NATIVE_CAUSAL_L3_EVENT_MANUFACTURE_NOT_FUNDED_L7',
 'observed_true_bidask_quotes':len(t),'warmup_Jan_quotes':WARM,'real_Feb_quotes':len(feb),
 'original_FEB041_FEB042_L3_event_reference':len(E),
 'independent_stream_generated_Feb_events':out_idx,'event_E_S_D_mismatches':mismatch,
 'first_mismatches':first,'Jan_warmup_events_not_counted_as_Feb':unaccounted_jan,
 'source_counts_generated':{str(k):v for k,v in sorted(count.items())},
 'no_feb_specific_params_or_month_execution_branch':True,
 'original_future_X_P_H_never_imported':True,
 'funded_JAN039_FEB045_FEB047_parity':False,'seconds':round(time.time()-start,2)}
 path=ROOT/'c2d3l_work/JAN037_FEB041_SOURCE_NATIVE_MONTH_BLIND_PARITY_033.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if mismatch:raise AssertionError('FEB041 native source generator is not identical')

if __name__=='__main__':main()
