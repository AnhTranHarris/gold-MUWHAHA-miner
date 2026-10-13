"""Strictly OFFLINE hindsight reachability for original Dukascopy tick stream.
The oracle chooses future direction AND future best exit. NO tradable edge claim.
Observed delayed entries 250ms, exits after further 250ms, Bid/Ask + .52/oz.
"""
import numpy as np, pandas as pd,json,time
from numba import njit
from pathlib import Path
from grid0261_intrinsic_time_research import load_month
ROOT=Path('/mnt/data/grid0261_intrinsic'); ROOT.mkdir(exist_ok=True)
@njit(cache=True)
def oracle_events(t,a,b,step_ms=5000,horizon_ms=60000,latency_ms=250,fee_raw=520,spreadcap_raw=800):
    # Monotonic deque future maximum Bid and minimum Ask. Samples at first
    # actual quote in each physical 5-second bucket, not manufactured ticks.
    n=len(t);sample_cap=(t[-1]-t[0])//step_ms+10
    # candidate count bounded by elapsed calendar physical time incl weekends
    sample=np.empty(sample_cap,np.int64);ns=0;prevbucket=-1
    for i in range(n):
        bucket=t[i]//step_ms
        if bucket!=prevbucket:
            if ns<len(sample):sample[ns]=i;ns+=1
            prevbucket=bucket
    samples=sample[:ns]
    k=ns
    entry=np.empty(k,np.int32);exfirst=np.empty(k,np.int32);exend=np.empty(k,np.int32)
    for p in range(k):
        i=samples[p]
        j=np.searchsorted(t,t[i]+latency_ms,side='left')
        entry[p]=j if j<n and t[j]<=t[i]+2000 else -1
        if entry[p]>=0:
            x=np.searchsorted(t,t[j]+latency_ms,side='left')
            y=np.searchsorted(t,t[j]+horizon_ms,side='right')
            exfirst[p]=x;exend[p]=y
        else:exfirst[p]=0;exend[p]=0
    # all horizon windows nondecreasing; use queue indexes of BID maxima and ASK minima
    maxq=np.empty(n,np.int32);minq=np.empty(n,np.int32)
    maxhead=0;maxtail=0;minhead=0;mintail=0;j=0
    out=np.empty((k,6),np.int32)  # timestamp index, actual spread, hindsight long, short, past-side, fee
    nn=0
    for p in range(k):
        idx=entry[p];lo=exfirst[p];hi=exend[p]
        if idx<0 or lo>=n or lo>=hi:continue
        if a[idx]-b[idx]>spreadcap_raw:continue
        if t[lo]>t[idx]+2000:continue  # at least one actual prompt exit quote
        if j<lo:j=lo;maxhead=maxtail;minhead=mintail
        while j<hi:
            vb=b[j]
            while maxtail>maxhead and b[maxq[maxtail-1]]<=vb:maxtail-=1
            maxq[maxtail]=j;maxtail+=1
            va=a[j]
            while mintail>minhead and a[minq[mintail-1]]>=va:mintail-=1
            minq[mintail]=j;mintail+=1
            j+=1
        while maxhead<maxtail and maxq[maxhead]<lo:maxhead+=1
        while minhead<mintail and minq[minhead]<lo:minhead+=1
        if maxhead>=maxtail or minhead>=mintail:continue
        long_net=b[maxq[maxhead]]-a[idx]-fee_raw
        short_net=b[idx]-a[minq[minhead]]-fee_raw
        pidx=np.searchsorted(t,t[idx]-5000,side='left')
        past=(a[idx]+b[idx])-(a[pidx]+b[pidx])
        pastdir=1 if past>0 else (-1 if past<0 else 0)
        out[nn,0]=idx;out[nn,1]=a[idx]-b[idx]
        out[nn,2]=long_net;out[nn,3]=short_net;out[nn,4]=pastdir;out[nn,5]=fee_raw
        nn+=1
    return out[:nn], np.array([ns,nn],np.int64)

def summary(out):
    if len(out)==0:return {}
    future=np.maximum(out[:,2],out[:,3]);direction=out[:,4];past=np.where(direction>0,out[:,2],np.where(direction<0,out[:,3],-9999999))
    n=len(future)
    return {'eligible_5s_source_quote_snapshots':n,'retrospective_best_net_usd_oz':round(float(future.sum()/1000),2),
      'oracle_profitable_fraction':round(float((future>0).mean()),4),
      'oracle_over_1p41_fraction':round(float((future>=1410).mean()),4),
      'oracle_over_2p1_fraction':round(float((future>=2100).mean()),4),
      'oracle_positive_count':int((future>0).sum()),
      'oracle_2p1_count':int((future>=2100).sum()),
      'past_five_second_direction_available_count':int((direction!=0).sum()),
      'past_momentum_oracle_exit_positive_fraction':round(float((past>0).mean()),4),
      'past_momentum_oracle_exit_sum_usd_oz':round(float(past[direction!=0].sum()/1000),2),
      'median_spread_usd':round(float(np.median(out[:,1])/1000),3),
      'median_hindsight_best_available_usd_oz':round(float(np.median(future)/1000),3),
      'p25_best_usd_oz':round(float(np.percentile(future,25)/1000),3)}
if __name__=='__main__':
    import sys
    elapsed=time.monotonic()
    allstats={}
    for m in range(1,8):
        t,a,b=load_month(m)
        x,c=oracle_events(t,a,b)
        stats=summary(x);allstats[str(m)]={'quotes':len(t),'source_samples':int(c[0]),**stats}
        print(m,stats,flush=True)
        del t,a,b,x
    goal_trades=int(np.ceil(.60*219342))
    goal_net=.60*309122.85
    allstats['r9_60pct_goal']={'r9_60pct_trades':goal_trades,'r9_60pct_net_broker_cash':round(goal_net,2),
         'needed_broker_net_per_trade':round(goal_net/goal_trades,3),
         'disclaimer':'These retrospective overlapping snapshots cannot be combined into real portfolio or forecasts.'}
    (ROOT/'GRID0261_R9_60PCT_RETROSPECTIVE_5SEC_QUOTE_EVENT_UPPER_BOUND.json').write_text(json.dumps(allstats,indent=2))
    print('total_seconds',round(time.monotonic()-elapsed,2))
