"""Independent incremental-vs-batch candle parity on original January tick prefix.
No future quotes or synthetic interpolated bars. January source SHA pinned by integration.
"""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from v2_streaming_chassis import StreamingF1
from v2_f1_integrated import prev_frames,micro_features,PIN,RAW

def run(n_ticks=180000):
    assert hashlib.file_digest(RAW.open('rb'),'sha256').hexdigest()==PIN
    d=pd.read_csv(RAW,compression='gzip',nrows=n_ticks,usecols=['timestamp_ms_utc','bid_raw','ask_raw'])
    ms=d.timestamp_ms_utc.to_numpy();bid=d.bid_raw.to_numpy();ask=d.ask_raw.to_numpy()
    sec=ms//1000;ix=np.r_[0,np.flatnonzero(sec[1:]!=sec[:-1])+1]
    ends=np.r_[ix[1:]-1,len(ms)-1]
    first=bid[ix].astype(float)*.001
    hi=np.maximum.reduceat(bid,ix).astype(float)*.001
    lo=np.minimum.reduceat(bid,ix).astype(float)*.001
    cl=bid[ends].astype(float)*.001
    frames={p:prev_frames(sec[ix],first,hi,lo,cl,width) for p,width in [('M1',60),('M5',300),('M15',900),('H1',3600),('H4',14400)]}
    counts=np.diff(np.r_[ix,len(ms)]).astype(np.int32)
    quality,_,_,_,_,_=micro_features(sec[ix],first,hi,lo,cl,counts)
    stream=StreamingF1();tests=0;diff=[];sidx=-1;lastsec=-1;microtests=0
    for j in range(len(ms)):
        snapshot=stream.on_quote(int(ms[j]),int(bid[j]),int(ask[j]))
        if sec[j]!=lastsec:
            sidx+=1;lastsec=sec[j]
            if sidx>=24:
                microtests+=1
                if snapshot.s1_quality!=quality[sidx]:diff.append((j,"S1_QUALITY",int(quality[sidx]),int(snapshot.s1_quality)))
            for period,frame in frames.items():
                cb=snapshot.completed[period]
                expected=frame[3][sidx]
                if np.isnan(expected):
                    if cb is not None:diff.append((j,period,'expected_none',cb.closing))
                else:
                    if cb is None or abs(cb.closing-expected)>1e-9:diff.append((j,period,'close_mismatch',expected,cb.closing if cb else None))
                tests+=1
    qa={'real_original_quotes_tested':len(ms),'observed_seconds_tested':len(ix),'completed_bar_comparisons':tests,'source_S1_micro_quality_comparisons':microtests,'discrepancies':diff[:20], 'discrepancy_count':len(diff),'timeframes':['M1','M5','M15','H1','H4'],'source_sha':PIN,'intended_use':'incremental feature parity, not funded strategy profitability'}
    out=Path(__file__).parent/'V2_ORIGINAL_SOURCE_STREAM_BATCH_PARITY_QA.json'
    out.write_text(json.dumps(qa,indent=2)+'\n')
    print('SOURCE_PARITY',json.dumps(qa))
    if diff:raise AssertionError(diff[:5])
if __name__=='__main__':run()
