"""C2D3-B independent 049 event-index/direction/hour parity vs frozen 001/017/019."""
import json,time
from pathlib import Path
import numpy as np
from test_original_ny049_union_033c2b import original_events,port_events

def run(path=Path('/mnt/data/c2d3b_work/feb_source_arrays.npz'),out=Path('/mnt/data/c2d3b_work/C2D3B_049_ORIGINAL_INDEX_PARITY.json')):
 ts=time.monotonic()
 with np.load(path,allow_pickle=False) as a:
  t=a['t'];ask=a['a'];bid=a['b'];ss=[a[n] for n in ('h4','h1','m15','m5')]
 ref=original_events(t,(ask.astype(np.int64)+bid)//2,*ss)
 actual=port_events(t,ask,bid,*ss)
 f=next(((i,x,y) for i,(x,y) in enumerate(zip(ref,actual)) if x!=y),None)
 result={'unit':'DAA_C2D3B_FEB_049_SOURCE_INDEX_PARITY','feb_quote_count':len(t),'original_count':len(ref),'ported_count':len(actual),'index_direction_hour_equal':ref==actual,'first_mismatch':f,'first_original':ref[:3],'last_original':ref[-3:],'elapsed_sec':round(time.monotonic()-ts,3),'scope':'SOURCE_CANDIDATE_INDEX_ONLY_PRE_L7__NOT_FUNDED_ORDER_PARITY','original_htf':'COMPLETED_EMA_SIGN_PROXY_NOT_FULL_V1_L2'}
 out.write_text(json.dumps(result,indent=2)+'\n');print('SOURCE_INDEX_PARITY',json.dumps(result),flush=True)
 assert len(ref)==13063 and ref==actual,('original mismatch',len(ref),len(actual),f)
if __name__=='__main__':run()
