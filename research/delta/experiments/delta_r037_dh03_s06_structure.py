"""DH03-S06 13A causal structure helpers. No strategy thresholds."""
from __future__ import annotations
import numpy as np
import delta_r037_dh02_s08_cleanroom_parity as base

def structural_state_by_bar(b,width=2):
    rt,rs,rl,_=base.symmetric_swings(b,width);e=b["end_ms"]
    st=np.zeros(e.size,np.int8);hi=np.zeros(e.size,np.int64);lo=np.zeros(e.size,np.int64)
    h1=h2=l1=l2=si=0
    for j,tm in enumerate(e):
        while si<rt.size and rt[si]<=tm:
            if rs[si]>0:h2,h1=h1,int(rl[si])
            else:l2,l1=l1,int(rl[si])
            si+=1
        hi[j]=h1;lo[j]=l1
        if h1 and h2 and l1 and l2:
            if h1>h2 and l1>l2:st[j]=1
            elif h1<h2 and l1<l2:st[j]=-1
    return st,hi,lo

def parent_series(b15,b30):
    s15,h15,l15=structural_state_by_bar(b15);s30,h30,l30=structural_state_by_bar(b30)
    d15=base.directional_label(b15,3,.3,.3);d30=base.directional_label(b30,3,.3,.3)
    ts=np.unique(np.r_[b15["end_ms"],b30["end_ms"]]).astype(np.int64)
    ps=np.zeros(ts.size,np.int8);pd=np.zeros(ts.size,np.int8)
    li=np.zeros(ts.size,np.int64);si=np.zeros(ts.size,np.int64)
    for k,tm in enumerate(ts):
        a=np.searchsorted(b15["end_ms"],tm,side="right")-1
        b=np.searchsorted(b30["end_ms"],tm,side="right")-1
        if a<0 or b<0:continue
        x,y=int(s15[a]),int(s30[b]);dx,dy=int(d15[a]),int(d30[b])
        if x and y:ps[k]=x if x==y else 0
        elif x:ps[k]=x
        elif y:ps[k]=y
        else:ps[k]=dx if dx and dx==dy else 0
        pd[k]=dx if dx and dx==dy else 0
        lows=[z for z in (int(l15[a]),int(l30[b])) if z]
        highs=[z for z in (int(h15[a]),int(h30[b])) if z]
        if lows:li[k]=max(lows)
        if highs:si[k]=min(highs)
    return ts,ps,pd,li,si

def latest_fast_pivots(b):
    rt,rs,rl,_=base.symmetric_swings(b,2);e=b["end_ms"]
    hi=np.zeros(e.size,np.int64);lo=np.zeros(e.size,np.int64)
    ht=np.zeros(e.size,np.int64);lt=np.zeros(e.size,np.int64)
    h=l=hx=lx=q=0
    for j,tm in enumerate(e):
        while q<rt.size and rt[q]<=tm:
            if rs[q]>0:h,hx=int(rl[q]),int(rt[q])
            else:l,lx=int(rl[q]),int(rt[q])
            q+=1
        hi[j]=h;lo[j]=l;ht[j]=hx;lt[j]=lx
    return hi,lo,ht,lt
