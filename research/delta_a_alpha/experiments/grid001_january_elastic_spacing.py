from __future__ import annotations
import argparse, hashlib, json, math, time
from pathlib import Path
import numpy as np, pandas as pd
from numba import njit

N=9_135_062; DAY_MS=86_400_000; H1_MS=3_600_000; M1_MS=60_000
PRICE_SCALE=1000; TICK_RAW=10; BASE_GAP_RAW=1000; TARGET_RAW=1000; WINDOW=48
P75=np.array([20,20,21,21],dtype=np.int64)
US_DST=np.int64(1772953200000); UK_DST=np.int64(1774746000000)
ALPHAS=(0.25,0.50,1.00)

def sha256(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8<<20),b''): h.update(b)
    return h.hexdigest()

def load(p:Path):
    t=np.empty(N,'i8'); a=np.empty(N,'i4'); b=np.empty(N,'i4'); pos=0
    for df in pd.read_csv(p,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'},chunksize=1_000_000):
        k=len(df); t[pos:pos+k]=df.timestamp_ms_utc; a[pos:pos+k]=df.ask_raw; b[pos:pos+k]=df.bid_raw; pos+=k
    if pos!=N: raise RuntimeError((pos,N))
    return t,a,b

@njit(cache=True)
def session(t):
    tod=t%DAY_MS
    ls=7*3_600_000 if t>=UK_DST else 8*3_600_000; le=ls+8*3_600_000+30*60_000
    ns=12*3_600_000 if t>=US_DST else 13*3_600_000; ne=ns+9*3_600_000
    il=ls<=tod<le; inn=ns<=tod<ne
    if il and inn:return 2
    if il:return 1
    if inn:return 3
    return 0

@njit(cache=True)
def materialize(t,sa,sb):
    n=t.size; a=np.empty(n,'i4'); b=np.empty(n,'i4'); maxe=0
    for i in range(n):
        spr=P75[session(np.int64(t[i]))]*TICK_RAW
        mid2=np.int64(sa[i])+np.int64(sb[i])
        bi=((mid2-spr+TICK_RAW)//(2*TICK_RAW))*TICK_RAW; ai=bi+spr
        a[i]=ai; b[i]=bi; e=abs((2*bi+spr)-mid2); maxe=max(maxe,e)
    return a,b,maxe

@njit(cache=True)
def quant_gap(raw):
    q=250
    return max(BASE_GAP_RAW,min(8000,int((raw+q//2)//q*q)))

@njit(cache=True)
def events_elastic(t,a,b,alpha,max_events=500_000,max_stack=20_000):
    bs=np.empty(max_stack,'i4'); bg=np.empty(max_stack,'i4'); nb=0
    ss=np.empty(max_stack,'i4'); sg=np.empty(max_stack,'i4'); ns=0
    max_nb=0; max_ns=0

    hi=np.empty(WINDOW-1,'i4'); lo=np.empty(WINDOW-1,'i4'); cnt=0; p=0
    hour=np.int64(-1); ch=np.int32(0); cl=np.int32(0); ready=False; rh=np.int32(0); rl=np.int32(0)

    tr_ring=np.empty(14,np.float64); tr_n=0; tr_p=0; tr_sum=0.0
    minute=np.int64(-1); mh=0.0; ml=0.0; mc=0.0; prev_close=0.0
    active_gap=BASE_GAP_RAW

    ei=np.empty(max_events,'i8'); ed=np.empty(max_events,'i1'); eg=np.empty(max_events,'i4'); dep=np.empty(max_events,'i2'); ne=0

    for i in range(t.size):
        ti=np.int64(t[i]); ai=np.int32(a[i]); bi=np.int32(b[i]); mid=0.5*(ai+bi)

        m=ti//M1_MS
        if m!=minute:
            if minute!=-1:
                tr=max(mh-ml,abs(mh-prev_close),abs(ml-prev_close)) if prev_close>0 else mh-ml
                if tr_n<14:
                    tr_ring[tr_p]=tr; tr_sum+=tr; tr_n+=1; tr_p=(tr_p+1)%14
                else:
                    tr_sum-=tr_ring[tr_p]; tr_ring[tr_p]=tr; tr_sum+=tr; tr_p=(tr_p+1)%14
                prev_close=mc
                if tr_n>=14:
                    atr_raw=tr_sum/14.0
                    cand=quant_gap(max(BASE_GAP_RAW,alpha*atr_raw))
                    if abs(cand-active_gap)>=0.10*active_gap:
                        active_gap=cand
            minute=m; mh=mid; ml=mid; mc=mid
        else:
            if mid>mh:mh=mid
            if mid<ml:ml=mid
            mc=mid

        h=ti//H1_MS
        if h!=hour:
            if hour!=-1:
                hi[p]=ch; lo[p]=cl; p=(p+1)%(WINDOW-1); cnt=min(cnt+1,WINDOW-1)
            hour=h; ch=bi; cl=bi
            if cnt>=WINDOW-1:
                rh=bi; rl=bi
                for j in range(WINDOW-1):
                    rh=max(rh,hi[j]); rl=min(rl,lo[j])
                ready=True
            else: ready=False
        else:
            ch=max(ch,bi); cl=min(cl,bi)

        while nb>0 and bi>=bs[nb-1]+bg[nb-1]: nb-=1
        while ns>0 and ai<=ss[ns-1]-sg[ns-1]: ns-=1
        if not ready: continue

        buy_anchor=bs[nb-1] if nb else rh
        if ai<buy_anchor-active_gap:
            if ne>=max_events or nb>=max_stack:return ei[:ne],ed[:ne],eg[:ne],dep[:ne],max_nb,max_ns,-1
            bs[nb]=ai; bg[nb]=active_gap; nb+=1; max_nb=max(max_nb,nb)
            ei[ne]=i; ed[ne]=-1; eg[ne]=active_gap; dep[ne]=nb; ne+=1

        sell_anchor=ss[ns-1] if ns else rl
        if ai>sell_anchor+active_gap:
            if ne>=max_events or ns>=max_stack:return ei[:ne],ed[:ne],eg[:ne],dep[:ne],max_nb,max_ns,-2
            ss[ns]=bi; sg[ns]=active_gap; ns+=1; max_ns=max(max_ns,ns)
            ei[ne]=i; ed[ne]=1; eg[ne]=active_gap; dep[ne]=ns; ne+=1
    return ei[:ne],ed[:ne],eg[:ne],dep[:ne],max_nb,max_ns,0

@njit(cache=True)
def shadows_fixed_target(t,a,b,ei,ed,horizon=300_000):
    n=ei.size; mr=np.empty(n); co=np.empty(n)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); end=t[i]+horizon
        s0=1 if d<0 else -1; s1=-s0
        for q in range(2):
            side=s0 if q==0 else s1; entry=a[i] if side>0 else b[i]
            tp=entry+TARGET_RAW if side>0 else entry-TARGET_RAW; sl=entry-TARGET_RAW if side>0 else entry+TARGET_RAW
            ex=entry; last=i; j=i+1; done=False
            while j<t.size and t[j]<=end:
                last=j
                if side>0:
                    if b[j]>=tp or b[j]<=sl: ex=b[j]; done=True; break
                else:
                    if a[j]<=tp or a[j]>=sl: ex=a[j]; done=True; break
                j+=1
            if not done: ex=b[last] if side>0 else a[last]
            pnl=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-0.02
            if q==0:mr[k]=pnl
            else:co[k]=pnl
    return mr,co

def stats(x):
    if len(x)==0:return {'n':0,'net':0,'gp':0,'gl':0,'pf':None,'expected':None,'win_pct':None}
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gp':gp,'gl':gl,'pf':gp/abs(gl) if gl<0 else None,'expected':float(x.mean()),'win_pct':100*float((x>0).mean())}

def daily_metrics(t,ei):
    days=t[ei]//DAY_MS; vals=[]
    for d in np.unique(days): vals.append(int((days==d).sum()))
    arr=np.array(vals,dtype=float)
    return {'active_days':int(len(arr)),'min':int(arr.min()) if len(arr) else 0,'median':float(np.median(arr)) if len(arr) else 0,'max':int(arr.max()) if len(arr) else 0,'mean':float(arr.mean()) if len(arr) else 0,'cv':float(arr.std()/arr.mean()) if len(arr) and arr.mean()>0 else None}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source',type=Path); ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args(); start=time.time(); t,sa,sb=load(z.source); a,b,maxe=materialize(t,sa,sb); split=2*len(t)//3
    events_elastic(t[:10000],a[:10000],b[:10000],0.5,10000,1000)
    shadows_fixed_target(t[:10000],a[:10000],b[:10000],np.empty(0,np.int64),np.empty(0,np.int8))
    rows=[]
    for alpha in ALPHAS:
        t0=time.time(); ei,ed,eg,dep,maxnb,maxns,err=events_elastic(t,a,b,alpha); gen_s=time.time()-t0
        if err: raise RuntimeError((alpha,err,len(ei)))
        mr,co=shadows_fixed_target(t,a,b,ei,ed); oracle=np.maximum(mr,co); disc=ei<split; val=~disc
        rows.append({
            'alpha':alpha,'events':int(len(ei)),'events_per_active_day':float(len(ei)/len(np.unique(t[ei]//DAY_MS))),
            'daily':daily_metrics(t,ei),'max_virtual_buy_stack':int(maxnb),'max_virtual_sell_stack':int(maxns),
            'gap_usd':{'median':float(np.median(eg)/PRICE_SCALE),'p10':float(np.quantile(eg,.1)/PRICE_SCALE),'p90':float(np.quantile(eg,.9)/PRICE_SCALE),'max':float(eg.max()/PRICE_SCALE)},
            'full':{'mr':stats(mr),'cont':stats(co),'oracle':stats(oracle),'both_negative_pct':100*float(np.mean((mr<0)&(co<0)))},
            'discovery':{'mr':stats(mr[disc]),'cont':stats(co[disc]),'oracle':stats(oracle[disc]),'both_negative_pct':100*float(np.mean((mr[disc]<0)&(co[disc]<0)))},
            'validation':{'mr':stats(mr[val]),'cont':stats(co[val]),'oracle':stats(oracle[val]),'both_negative_pct':100*float(np.mean((mr[val]<0)&(co[val]<0)))},
            'generation_seconds':gen_s
        })
    out={'schema':'delta-a-alpha-grid001-january-elastic-spacing-v1','unit':'DAA_GRID_001_JANUARY_ELASTIC_SPACING_001','status':'COMPLETE','source_sha256':sha256(z.source),'surface':'DUKAS_COINEXX_LIKE_P75','split_tick_index':int(split),'variants':rows,'timing_seconds':time.time()-start}
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
