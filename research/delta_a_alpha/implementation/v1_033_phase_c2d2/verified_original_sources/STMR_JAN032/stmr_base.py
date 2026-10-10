import pandas as pd, numpy as np, math, json, time
from pathlib import Path
from numba import njit

PRICE_SCALE=1000
POINT_RAW=10
DAY_MS=86400000
US_DST_START_2026_MS=np.int64(1772953200000)
UK_DST_START_2026_MS=np.int64(1774746000000)
P75_POINTS=np.array([20,20,21,21],dtype=np.int64)
ENTRY_START=np.int64(1767571200000) # 2026-01-05 00:00 UTC
SPLIT=np.int64(1768608000000) # 2026-01-17 00:00 UTC
# session codes: 0 Asia,1 LondonOpen,2 London,3 overlap,4 NY,5 Late,6 rollover
GAPS=np.array([750,0,1000,750,1500,500,0],dtype=np.int32)
# sleeve ids 0..11 matching artifact order
N_SLEEVES=12

@njit(cache=True)
def session_code_p75(t):
    tod=t%DAY_MS
    london_start=7*3600000 if t>=UK_DST_START_2026_MS else 8*3600000
    london_end=london_start+8*3600000+30*60000
    ny_start=12*3600000 if t>=US_DST_START_2026_MS else 13*3600000
    ny_end=ny_start+9*3600000
    il=london_start<=tod<london_end
    iny=ny_start<=tod<ny_end
    if il and iny:return 2
    if il:return 1
    if iny:return 3
    return 0

@njit(cache=True)
def q_half(target2,tick): return ((target2+tick)//(2*tick))*tick

@njit(cache=True)
def materialize(t,sa,sb):
    n=t.size;a=np.empty(n,np.int32);b=np.empty(n,np.int32)
    for i in range(n):
        spread=P75_POINTS[session_code_p75(np.int64(t[i]))]*POINT_RAW
        mid2=np.int64(sa[i])+np.int64(sb[i])
        bb=q_half(mid2-spread,POINT_RAW); aa=bb+spread
        b[i]=bb;a[i]=aa
    return a,b

def load(path):
    df=pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'})
    return df.timestamp_ms_utc.to_numpy(),df.ask_raw.to_numpy(),df.bid_raw.to_numpy()

def bar_states(t, px, tf_ms, use_ema=True):
    buck=t//tf_ms
    starts=np.r_[0,np.flatnonzero(buck[1:]!=buck[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    bars=buck[starts]
    closes=px[ends].astype(np.float64)
    n=len(closes)
    ema8=np.empty(n);ema21=np.empty(n)
    ema8[0]=closes[0];ema21[0]=closes[0]
    a8=2/9;a21=2/22
    for i in range(1,n):
        ema8[i]=a8*closes[i]+(1-a8)*ema8[i-1]
        ema21[i]=a21*closes[i]+(1-a21)*ema21[i-1]
    state=np.zeros(n,np.int8)
    state[ema8>ema21]=1;state[ema8<ema21]=-1
    # map each tick to previous completed observed bar
    qb=t//tf_ms
    bi=np.searchsorted(bars,qb,side='left')-1
    out=np.zeros(len(t),np.int8)
    ok=bi>=0
    out[ok]=state[bi[ok]]
    return out

@njit(cache=True)
def sess_fixed(t):
    x=t%DAY_MS
    if x>=23*3600000 or x<7*3600000:return 0
    if x<9*3600000:return 1
    if x<13*3600000+30*60000:return 2
    if x<16*3600000:return 3
    if x<20*3600000:return 4
    if x<22*3600000:return 5
    return 6

@njit(cache=True)
def choose_sleeve(s,d,h4,h1,m15,m5):
    macro=(h4!=0 and h4==h1)
    if s==0:
        if macro and m15==m5 and m15==-h1 and d==m5:return 0
        if macro and m15==-h1 and m5==h1 and d==m5:return 1
    elif s==2:
        if macro and m15==h1 and m5==-h1 and d==m5:return 2
        if macro and m15==-h1 and m5==h1 and d==m5:return 3
    elif s==3:
        if macro and m15==m5 and m15==-h1 and d==m5:return 4
        if macro and m15==m5 and m15==h1 and d==-m5:return 5
    elif s==4:
        if h4!=0 and h1!=0 and h4!=h1:
            if m15!=0 and m5==-m15 and d==m5:return 6
            if m15==m5 and m15!=0 and d==-m5:return 7
    elif s==5:
        if h4==h1 and h1==m15 and m15==m5 and h4!=0 and d==m5:return 8
        if h4!=0 and h1!=0 and h4!=h1 and m15!=0 and m5==-m15 and d==m5:return 9
        if macro and m15==h1 and m5==-h1 and d==-m5:return 10
        if macro and m15==m5 and m15==-h1 and d==m5:return 11
    return -1

@njit(cache=True)
def phase_ok(sl,t):
    minute=(t%DAY_MS)//60000
    if sl==0: return minute>=1380
    if sl==2: return minute>=660 and minute<720
    return True

@njit(cache=True)
def count_events(t,px,h4,h1,m15,m5, anchor_mode, seen_mode, mark_gate_fail):
    # anchor_mode unused here except px chosen externally. seen_mode:0 sleeve+cell, 1 sleeve+cell+dir, 2 physical cell global
    counts=np.zeros((2,N_SLEEVES),np.int64)
    sess=-1; anchor=0; prev_cell=0
    seen=np.zeros((N_SLEEVES,4096,2),np.uint8)
    seen_global=np.zeros((4096,2),np.uint8)
    off=2048
    for i in range(t.size):
        ti=t[i]
        s=sess_fixed(ti)
        if s!=sess:
            sess=s; anchor=int(px[i]); prev_cell=0
            seen[:]=0; seen_global[:]=0
            continue
        if ti<ENTRY_START: continue
        gap=GAPS[s]
        if gap<=0: continue
        diff=int(px[i])-anchor
        # floor division consistent with python/C
        cell=diff//gap
        if cell==prev_cell: continue
        # emit each crossed boundary sequentially
        step=1 if cell>prev_cell else -1
        c=prev_cell
        while c!=cell:
            nc=c+step
            d=step
            # boundary/cell key: target cell for up, source cell for down? current uses nc always
            key=nc+off
            if 0<=key<4096:
                sl=choose_sleeve(s,d,h4[i],h1[i],m15[i],m5[i])
                if sl>=0:
                    di=1 if d>0 else 0
                    already=False
                    if seen_mode==0: already=seen[sl,key,0]!=0
                    elif seen_mode==1: already=seen[sl,key,di]!=0
                    else: already=seen_global[key,di]!=0
                    if not already:
                        ok=phase_ok(sl,ti)
                        if ok:
                            part=0 if ti<SPLIT else 1
                            counts[part,sl]+=1
                        if ok or mark_gate_fail:
                            if seen_mode==0: seen[sl,key,0]=1
                            elif seen_mode==1: seen[sl,key,di]=1
                            else: seen_global[key,di]=1
            c=nc
        prev_cell=cell
    return counts

names=['ASIA_LOWER_TAKEOVER','ASIA_M15_DIVERGE_M5_RECLAIM','LONDON_M5_TAKEOVER','LONDON_M5_RECLAIM','OVERLAP_LOWER_TAKEOVER','OVERLAP_ALIGNED_COUNTERCROSS','NY_LOWER_TRANSFER','NY_LOWER_COUNTERCROSS','LATE_ALIGNED_MOMENTUM','LATE_MACRO_SPLIT_TRANSFER','LATE_M5_REJECTION','LATE_LOWER_TAKEOVER']
target_disc=np.array([69,30,28,13,44,39,23,30,103,15,36,82])
target_val=np.array([55,27,48,50,406,157,26,95,442,98,105,62])

if __name__=='__main__':
    p=Path('/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz')
    st=time.time();t,sa,sb=load(p);print('loaded',len(t),time.time()-st)
    a,b=materialize(t,sa,sb); print('mat',time.time()-st)
    mids=((a.astype(np.int64)+b.astype(np.int64))//2).astype(np.int32)
    for barpx_name,barpx in [('bid',b),('mid',mids)]:
        print('states',barpx_name)
        h4=bar_states(t,barpx,4*3600000);h1=bar_states(t,barpx,3600000);m15=bar_states(t,barpx,15*60000);m5=bar_states(t,barpx,5*60000)
        for pxname,px in [('bid',b),('mid',mids),('ask',a)]:
          for sm in [0,1,2]:
            for mg in [0,1]:
              c=count_events(t,px,h4,h1,m15,m5,0,sm,mg)
              err=np.abs(c[0]-target_disc).sum()+np.abs(c[1]-target_val).sum()
              print(barpx_name,pxname,'seen',sm,'mark',mg,'tot',c.sum(axis=1).tolist(),'err',int(err))
              if err<800:
                print('disc',dict(zip(names,c[0].tolist())))
                print('val ',dict(zip(names,c[1].tolist())))
    print('target',target_disc.sum(),target_val.sum())