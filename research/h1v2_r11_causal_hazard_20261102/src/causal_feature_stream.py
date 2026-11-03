"""R11 memory-bounded, source-ordinal exact full-month 300s causal event graph.

Never include future quotes. Stream every raw tick and every R11 eligible
250ms candidate, storing a fixed supervised feature subset in a disk-backed
NumPy array. Overlap each chunk by >5min plus 2 predecessor ordinals so
mark transitions and event-path windows are preserved exactly.
"""
from __future__ import annotations
import hashlib,json,time,pathlib
import numpy as np
from numpy.lib.format import open_memmap
from event_graph import extract,NAMES,WINDOWS_MS,FIELDS
from h1v2_teacher import read_ticks
from entry_contract import MONTHS,PINNED,candidate_v5,verify_file_sha

FIELDS_USED=('quote_count','signed_path_efficiency','mid_delta','mid_range','extrema_order','mean_spread','mixed_compress_fraction','mixed_widen_fraction','bid_leads_ask_count','ask_leads_bid_count')
# Fifty-three? actual 10 *7 =70 fixed causal features, no future labels.
USE_INDICES=tuple(k*len(FIELDS)+FIELDS.index(f) for k in range(len(WINDOWS_MS)) for f in FIELDS_USED)
USE_NAMES=tuple(NAMES[i] for i in USE_INDICES)

def stream_month(month,raw_root,output,quote_chunk=350000):
    if month not in MONTHS or quote_chunk<1000:raise ValueError('bad stream request')
    root=pathlib.Path(raw_root)
    src=root/f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz'
    verify_file_sha(src,PINNED[month]);started=time.monotonic()
    t,b,a=read_ticks(src); ix=candidate_v5(t,b,a)
    output=pathlib.Path(output);output.mkdir(parents=True,exist_ok=True)
    path=output/f'R11_CAUSAL_GRAPH_V5_{month}.npy'
    X=open_memmap(path,mode='w+',dtype=np.float32,shape=(len(ix),len(USE_INDICES)))
    chunks=[]
    for pos in range(0,len(t),quote_chunk):
        end=min(pos+quote_chunk,len(t))
        ilo=int(np.searchsorted(ix,pos,side='left'))
        ihi=int(np.searchsorted(ix,end,side='left'))
        if ilo==ihi:continue
        # Include two full preceding ordinal revisions before the first tick at
        # the earliest 300s window cutoff, preserving mark and pair transitions.
        hist=max(0,int(np.searchsorted(t,t[pos]-int(WINDOWS_MS[-1]),side='left'))-2)
        x=extract(t[hist:end],b[hist:end],a[hist:end],ix[ilo:ihi]-hist)
        X[ilo:ihi]=x[:,USE_INDICES]
        chunks.append({'first_source_raw_quote':pos,'past_prefix_start':hist,'last_source_raw_quote_exclusive':end,
                       'first_eligible_candidate':ilo,'last_eligible_candidate_exclusive':ihi,
                       'output_candidates':ihi-ilo})
        del x
        if len(chunks)%5==0:
            X.flush(); print(month,'GRAPH',end,'/',len(t),'records',ihi,'/',len(ix),flush=True)
    X.flush(); del X
    from hashlib import sha256
    with path.open('rb') as f:sh=hashlib.file_digest(f,'sha256').hexdigest()
    receipt={'month':month,'source_raw_sha256':PINNED[month],'original_raw_quote_rows':len(t),
       'r11_v5_250ms_complete_candidates':len(ix),'feature_count':len(USE_NAMES),'feature_names':USE_NAMES,
       'graph_source':'R11 event_graph.py full raw quote ordinal, 300sec memory, no future outcomes',
       'chunking':chunks,'source_matrix_npy':str(path),'matrix_size_bytes':path.stat().st_size,
       'matrix_sha256':sh,'elapsed_s':round(time.monotonic()-started,2),
       'status':'ALL_SOURCE_QUOTES_ALL_ELIGIBLE_CANDIDATES_FEATURED_ASOF_NO_FITTED_MODEL'}
    (output/f'R11_CAUSAL_GRAPH_V5_{month}_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    return receipt

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--month',required=True,choices=MONTHS);p.add_argument('--raw-root',default='/mnt/data');p.add_argument('--output',default='/mnt/data/h1v2_r11_lab/graph');p.add_argument('--quote-chunk',type=int,default=350000)
 z=p.parse_args();r=stream_month(z.month,z.raw_root,z.output,z.quote_chunk)
 print(json.dumps({k:r[k] for k in ('month','original_raw_quote_rows','r11_v5_250ms_complete_candidates','feature_count','matrix_size_bytes','matrix_sha256','elapsed_s')},indent=2),flush=True)
