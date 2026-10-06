from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

MULTS=((0.5,'A05'),(1.0,'A10'),(1.5,'A15'))
COMMISSION=0.02

@njit(cache=True)
def proof_trades(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    pi=np.full(n,-1,np.int64)
    pnl=np.zeros(n,np.float64)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        event_entry=a[i] if side>0 else b[i]
        proof=max(1,int(round(0.25*g))); fail=max(1,int(round(0.50*g)))
        p=-1; j=i+1
        while j<t.size and t[j]<=end:
            px=b[j] if side>0 else a[j]
            if side>0:
                if px<=event_entry-fail: break
                if px>=event_entry+proof: p=j; break
            else:
                if px>=event_entry+fail: break
                if px<=event_entry-proof: p=j; break
            j+=1
        if p<0: continue
        pi[k]=p
        entry=a[p] if side>0 else b[p]
        tp=entry+g if side>0 else entry-g
        sl=entry-g if side>0 else entry+g
        ex=entry; last=p; q=p+1
        while q<t.size and t[q]<=end:
            last=q
            if side>0:
                if b[q]>=tp or b[q]<=sl: ex=b[q]; break
            else:
                if a[q]<=tp or a[q]>=sl: ex=a[q]; break
            q+=1
        else:
            ex=b[last] if side>0 else a[last]
        pnl[k]=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-COMMISSION
    return pi,pnl

def signed_efficiency_at(t,mid,qidx,tf_ms):
    bucket=t//tf_ms
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    bars=bucket[starts]; closes=mid[ends].astype(float)
    ser=np.full(len(closes),np.nan)
    if len(closes)>=7:
        d=np.abs(np.diff(closes)); cs=np.r_[0.0,np.cumsum(d)]
        j=np.arange(6,len(closes)); net=closes[j]-closes[j-6]; path=cs[j]-cs[j-6]
        ser[j]=np.divide(net,path,out=np.zeros_like(net),where=path>0)
    qb=t[qidx]//tf_ms; bi=np.searchsorted(bars,qb,side='left')-1
    out=np.full(len(qidx),np.nan); ok=bi>=0; out[ok]=ser[bi[ok]]
    return out

@njit(cache=True)
def parent_reclaim(t,a,b,ei,ed,eg,pi,eligible,horizon=300000):
    n=ei.size
    pnl=np.zeros(n,np.float64); entered=np.zeros(n,np.int8); reason=np.zeros(n,np.int8)
    for k in range(n):
        if not eligible[k] or pi[k]<0: continue
        i=int(ei[k]); p=int(pi[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        parent=-1 if d>0 else 1
        ref_mid=0.5*(a[p]+b[p]); need=max(1,int(round(0.25*g)))
        q=p+1; rp=-1
        while q<t.size and t[q]<=end:
            mid=0.5*(a[q]+b[q])
            if parent>0:
                if mid>=ref_mid+need: rp=q; break
            else:
                if mid<=ref_mid-need: rp=q; break
            q+=1
        if rp<0: continue
        entered[k]=1
        entry=a[rp] if parent>0 else b[rp]
        tp=entry+g if parent>0 else entry-g
        sl=entry-g if parent>0 else entry+g
        ex=entry; last=rp; rr=3; q=rp+1
        while q<t.size and t[q]<=end:
            last=q
            if parent>0:
                if b[q]>=tp: ex=b[q]; rr=1; break
                if b[q]<=sl: ex=b[q]; rr=2; break
            else:
                if a[q]<=tp: ex=a[q]; rr=1; break
                if a[q]>=sl: ex=a[q]; rr=2; break
            q+=1
        else:
            ex=b[last] if parent>0 else a[last]
        reason[k]=rr
        pnl[k]=((ex-entry) if parent>0 else (entry-ex))/PRICE_SCALE-COMMISSION
    return pnl,entered,reason

def stats(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def variant(t,a,b,mid,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    pi,child_pnl=proof_trades(t,a,b,ei,ed,eg)
    opened=pi>=0
    side=np.where(ed<0,-1.0,1.0)
    idx=np.where(opened,pi,ei)
    p5=signed_efficiency_at(t,mid,idx,300000)*side
    p15=signed_efficiency_at(t,mid,idx,900000)*side
    match5=p5>=.5; match15=p15>=.5; opp5=p5<=-.5; opp15=p15<=-.5
    eligible=opened&(~match5)&(~match15)&(opp5|opp15)
    route_pnl,entered,reason=parent_reclaim(t,a,b,ei,ed,eg,pi,eligible)
    rm=entered==1; split=2*len(t)//3; disc=ei<split; val=~disc
    child=stats(child_pnl[eligible]); route=stats(route_pnl[rm])
    days=len(np.unique(t[ei[rm]]//DAY_MS)) if rm.any() else 0
    return {
      'eligible_parent_opposed':int(eligible.sum()),
      'child_cont_baseline':child,
      'reclaim_proven':int(rm.sum()),
      'reclaim_proven_pct':100*float(rm.sum()/max(1,eligible.sum())),
      'trades_per_active_day':float(rm.sum()/days) if days else 0.0,
      'parent_reclaim_full':route,
      'parent_reclaim_discovery':stats(route_pnl[rm&disc]),
      'parent_reclaim_validation':stats(route_pnl[rm&val]),
      'exit_reasons':{'target':int(np.sum(reason[rm]==1)),'stop':int(np.sum(reason[rm]==2)),'timeout':int(np.sum(reason[rm]==3))},
      'net_value_vs_child_baseline':float(route['net']-child['net']),
      'gross_loss_magnitude_reduction_pct':100*float((abs(child['gross_loss'])-abs(route['gross_loss']))/abs(child['gross_loss']))
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()
    t,sa,sb=load(z.source)
    a,b,maxe=materialize(t,sa,sb)
    mid=(a.astype(np.int64)+b.astype(np.int64))/2.0
    out={
      'schema':'delta-a-alpha-grid001-january-parent-opposed-reclaim-route-v1',
      'unit':'DAA_GRID_001_JANUARY_PARENT_OPPOSED_RECLAIM_ROUTE_001',
      'status':'COMPLETE','surface':'DUKAS_COINEXX_LIKE_P75','ticks':int(len(t)),
      'variants':{name:variant(t,a,b,mid,m) for m,name in MULTS},
      'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
