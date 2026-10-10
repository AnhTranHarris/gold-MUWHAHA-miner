"""Actual quote-by-quote causal Python port vs whole original Jan037 archive E/S/D.

No future X/R/P/H in the new online engine. The original Jan037 E/S/D reference
is used only for a separate parity assertion and never consumed by on_quote.
"""
import sys,hashlib,json,time,zipfile,io,os
from pathlib import Path
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'032_source'))
import stmr_base as c
c.materialize=lambda t,sa,sb:(sa.copy(),sb.copy()) # exact JAN037 prep original source
import gamma02_m1_density as gmd
from original_jan037_heartbeat50_online_033 import OriginalJAN037Heartbeat50ms
ARCH='/mnt/data/bootstrap_inputs/JAN037_ITERATIVE_XAUUSD_TICK_RESEARCH_BUNDLE.zip'
MEM='research/JAN037_EXPANDED_L3_50MS_PROPOSALS.npz'
EXPECTED_MEMBER='e36ccf38e3dff2b1cbf770bca11086b070e0c3c1450ce52e636cf0bfdb572530'
OUT=ROOT/'JAN037_272931_ORIGINAL_NATIVE_HEARTBEAT_ONLINE_PARITY.json'

def main():
 start=time.time()
 # All 9.135m JAN quotes, same exact source-completed H4/H1/M15/M5 family.
 T,A,B,M,H4,H1,M15,M5=gmd.prep()[:8]
 with zipfile.ZipFile(ARCH) as z:raw=z.read(MEM)
 if hashlib.sha256(raw).hexdigest()!=EXPECTED_MEMBER:raise ValueError('Original JAN037 prepared member SHA mismatch')
 with np.load(io.BytesIO(raw),allow_pickle=False) as z:
  s=z['S'];keep=s>=17
  E=z['E'][keep];S=s[keep];D=z['D'][keep]
 # Snapshot arrays contain only original entry identity E/S/D.
 o=OriginalJAN037Heartbeat50ms()
 recorded=[];direct_compared=0;first_bad=[];counts=Counter()
 for i in range(len(T)):
  item=o.on_observed_quote(i,int(T[i]),int(M[i]),int(H4[i]),int(H1[i]),int(M15[i]),int(M5[i]))
  if item is None: continue
  recorded.append((item.quote_ordinal,item.source_id,item.side))
  counts[item.source_id]+=1
  if direct_compared<len(E):
   if (item.quote_ordinal,item.source_id,item.side)!=(int(E[direct_compared]),int(S[direct_compared]),int(D[direct_compared])) and len(first_bad)<4:
    first_bad.append([i,item.quote_ordinal,item.source_id,item.side,int(E[direct_compared]),int(S[direct_compared]),int(D[direct_compared])])
  direct_compared+=1
 arr=np.asarray(recorded,np.int64)
 ref=np.stack([E,S,D],axis=1).astype(np.int64)
 mismatch=int(np.sum(np.any(arr[:min(len(arr),len(ref))]!=ref[:min(len(arr),len(ref))],axis=1)))+abs(len(arr)-len(ref))
 report={
 'original_source':'JAN037 package research/jan037_expand_l3.py + 032_source/gamma02_campaign_heartbeat_019.py, both unmodified',
 'original_JAN037_source_member_sha256':EXPECTED_MEMBER,
 'original_real_Jan_quotes':len(T),'original_reference_L3_50ms_events':len(ref),
 'causal_online_port_50ms_events':len(arr),'entry_index_side_source_mismatches':mismatch,
 'first_source_mismatches':first_bad,'generated_by_source':{str(k):v for k,v in sorted(counts.items())},
 'source_H4_H1_M15_M5':'JAN032 exact stmr_janjul.make_states input of genuine Dukascopy Bid',
 'all_source_parameter_holding_tp_sl':'Original unmodified source functions and static CI contracts',
 'future_hypothetical_X_R_P_H_not_imported_into_new_module':True,
 'offline_original_source_generator_exact':mismatch==0,
 'month_label_used_to_select_events':False,
 'full_optimized_JAN039_FEB045_FEB047_funded_parity':False,
 'elapsed_seconds':round(time.time()-start,2)}
 OUT.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 if mismatch:raise AssertionError('Online source generator does not match original Jan037 event oracle')

if __name__=='__main__':main()
