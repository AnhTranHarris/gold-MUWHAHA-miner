"""GRID0104 creator's inventory-free price grid improved before any L1-L7 layer.
Pure Bid/Ask original tick event lab, no orders, no market/session calendar rules.
Grid step can expand to executable spread floor; confirmation event has its OWN
right-edge timestamp, no future-reference or retrospective backdate.
"""
from __future__ import annotations
from numba import njit
import numpy as np, pandas as pd, time,json,hashlib,sys
from pathlib import Path
OUT=Path('/mnt/data/grid_cycle0104');OUT.mkdir(exist_ok=True)
@njit(cache=True)
def scan_grid(t,b,a,basegap,mult_x100,cd_ms,mode,trigger_x100):
    n=len(t);idx=np.empty(n//3,np.int64);side=np.empty(n//3,np.int8);rung=np.empty(n//3,np.int16);gap_arr=np.empty(n//3,np.int32)
    nout=0
    anchor=(int(b[0])+int(a[0]))//2
    last_p=anchor
    last_emit=t[0]-9999999
    last_step=0;depth=0;armed=False;extreme=anchor;crossp=anchor;cg=basegap
    for i in range(1,n):
        p=(int(b[i])+int(a[i]))//2
        spread=int(a[i])-int(b[i]);g=max(basegap,spread*mult_x100//100)
        if p==last_p:continue
        # A pending retrace/continuation candidate is checked at this tick's right edge.
        # Even if it also crosses next grid rung, only one event can be recorded.
        evt=0
        if mode==1 and armed:  # post-cross reversal confirmed at microprice
            if last_step<0:
                if p<extreme: extreme=p
                if p>=extreme+max(100,cg*trigger_x100//100):evt=1
            else:
                if p>extreme: extreme=p
                if p<=extreme-max(100,cg*trigger_x100//100):evt=-1
            if evt!=0:armed=False
        if mode==2 and armed:  # post-cross continuation from cross point
            if last_step<0 and p<=crossp-max(100,cg*trigger_x100//100):evt=-1
            if last_step>0 and p>=crossp+max(100,cg*trigger_x100//100):evt=1
            if evt!=0:armed=False
        if p<=anchor-g:
            step=-1
        elif p>=anchor+g:
            step=1
        else:
            step=0
        if step!=0:
            if last_step==step:depth=min(32767,depth+1)
            else:depth=1
            last_step=step;anchor=p;crossp=p;extreme=p;cg=g;armed=True
            if mode==0:evt= -step # down-cross => reversion BUY, up-cross => reversion SELL
        if evt!=0 and t[i]-last_emit>=cd_ms:
            if nout>=len(idx):break
            idx[nout]=i;side[nout]=evt;rung[nout]=depth;gap_arr[nout]=g
            nout+=1;last_emit=t[i]
        last_p=p
    return idx[:nout],side[:nout],rung[:nout],gap_arr[:nout]

def read_raw(month):
    p=f'/mnt/data/XAUUSD_DUKAS_2026_{month}_ticks.csv(3).gz'
    d=pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','bid_raw','ask_raw'],dtype={'timestamp_ms_utc':'int64','bid_raw':'int32','ask_raw':'int32'})
    t=d.timestamp_ms_utc.to_numpy();b=d.bid_raw.to_numpy();a=d.ask_raw.to_numpy()
    assert np.all(np.diff(t)>=0) and np.all(a>=b) and np.all(b>0)
    return p,t,b,a

def evaluate(t,b,a,idx,side,gap,horizons=(30,120,300)):
    tm=t[idx];s=side.astype(np.int32)
    daily=pd.to_datetime(tm,unit='ms',utc=True).floor('D')
    daily_counts=pd.Series(1,index=daily).groupby(level=0).sum()
    out={'events':len(idx),'buy':int(np.sum(side==1)),'sell':int(np.sum(side==-1)),
         'active_days':len(daily_counts),'daily_min':int(daily_counts.min()) if len(idx) else 0,
         'median_spread_usd':round(float(np.median(a[idx]-b[idx]))/1000,4) if len(idx) else None,
         'median_cost_scaled_gap_usd':round(float(np.median(gap))/1000,4) if len(idx) else None,
         'spread_larger_than_gap_pct':round(float(np.mean((a[idx]-b[idx])>gap)*100),3) if len(idx) else None,
         'daily_counts':{str(k.date()):int(v) for k,v in daily_counts.items()}}
    for sec in horizons:
      ix=np.searchsorted(t,tm+sec*1000,side='left');valid=ix<len(t);ix=np.minimum(ix,len(t)-1)
      valid &= (t[ix]-(tm+sec*1000))<=20000
      if not np.any(valid):continue
      k=idx[valid];j=ix[valid];ss=s[valid]
      mark=np.where(ss>0,b[j]-a[k],b[k]-a[j])/1000
      out[f'h{sec}_quoted_mean_usd']=round(float(mark.mean()),5)
      out[f'h{sec}_quoted_win_pct']=round(float(np.mean(mark>0)*100),3)
      out[f'h{sec}_observations']=len(mark)
    return out

def all_research(month):
 p,t,b,a=read_raw(month);T=time.monotonic();res={};tapes={}
 configs=[('CROSS_BASE_075_15',750,0,15000,0,0),
          ('CROSS_SPREAD125_075_15',750,125,15000,0,0),
          ('CROSS_SPREAD150_075_15',750,150,15000,0,0),
          ('CROSS_SPREAD125_075_10',750,125,10000,0,0),
          ('CROSS_SPREAD150_075_10',750,150,10000,0,0),
          ('CONFIRM_BOUNCE025_SPREAD125_CD10',750,125,10000,1,25),
          ('CONFIRM_BOUNCE050_SPREAD125_CD10',750,125,10000,1,50),
          ('CONFIRM_BOUNCE025_SPREAD125_CD5',750,125,5000,1,25),
          ('CONFIRM_BOUNCE050_SPREAD125_CD5',750,125,5000,1,50),
          ('CONFIRM_CONT025_SPREAD125_CD10',750,125,10000,2,25),
          ('CONFIRM_CONT050_SPREAD125_CD10',750,125,10000,2,50),
          ('CONFIRM_CONT025_SPREAD125_CD5',750,125,5000,2,25),
          ('CONFIRM_CONT050_SPREAD125_CD5',750,125,5000,2,50)]
 for name,base,mult,cd,mode,trig in configs:
    idx,side,depth,gap=scan_grid(t,b,a,base,mult,cd,mode,trig)
    m=evaluate(t,b,a,idx,side,gap)
    res[name]=m
    if month=='01' and ('SPREAD125' in name and ('CROSS_SPREAD125_075_10'==name or 'BOUNCE025' in name or 'CONT025' in name)):
      pd.DataFrame({'timestamp_ms_utc':t[idx],'bid_raw':b[idx],'ask_raw':a[idx],'side':side,'rung':depth,'gap_raw':gap}).to_csv(OUT/(month+'_'+name+'.csv.gz'),index=False,compression='gzip')
    print(month,name,m['events'],m['median_cost_scaled_gap_usd'],m['spread_larger_than_gap_pct'],m.get('h30_quoted_mean_usd'),m.get('h120_quoted_mean_usd'),m.get('h300_quoted_mean_usd'),round(time.monotonic()-T,1),flush=True)
 with (OUT/(month+'_grid_cost_research.json')).open('w') as f:json.dump({'file':p,'input_ticks':len(t),'research_only':True,'configs':res},f,indent=2)
 if month=='02':
    # preserve mid-level false positive control: January thresholds were not tuned on February.
    pass
 return res
if __name__=='__main__':all_research(sys.argv[1] if len(sys.argv)>1 else '01')
