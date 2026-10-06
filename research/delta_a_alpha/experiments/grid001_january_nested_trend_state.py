from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

TFS=(5000,15000,60000,300000,900000)
TF_NAMES=('5s','15s','1m','5m','15m')
MULTS=((0.5,'A05'),(1.0,'A10'),(1.5,'A15'))
COMMISSION=0.02

@njit(cache=True)
def proof_trades(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    proof_idx=np.full(n,-1,np.int64)
    pnl=np.zeros(n,np.float64)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        event_entry=a[i] if side>0 else b[i]
        proof=max(1,int(round(0.25*g))); fail=max(1,int(round(0.50*g)))
        pi=-1; j=i+1
        while j<t.size and t[j]<=end:
            px=b[j] if side>0 else a[j]
            if side>0:
                if px<=event_entry-fail: break
                if px>=event_entry+proof: pi=j; break
            else:
                if px>=event_entry+fail: break
                if px<=event_entry-proof: pi=j; break
            j+=1
        if pi<0: continue
        proof_idx[k]=pi
        entry=a[pi] if side>0 else b[pi]
        tp=entry+g if side>0 else entry-g
        sl=entry-g if side>0 else entry+g
        ex=entry; last=pi; q=pi+1
        while q<t.size and t[q]<=end:
            last=q
            if side>0:
                if b[q]>=tp: ex=b[q]; break
                if b[q]<=sl: ex=b[q]; break
            else:
                if a[q]<=tp: ex=a[q]; break
                if a[q]>=sl: ex=a[q]; break
            q+=1
        else:
            ex=b[last] if side>0 else a[last]
        pnl[k]=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-COMMISSION
    return proof_idx,pnl

def signed_efficiency_at(t,mid,query_idx,tf_ms):
    bucket=t//tf_ms
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    bars=bucket[starts]
    closes=mid[ends].astype(np.float64)
    ser=np.full(len(closes),np.nan)
    if len(closes)>=7:
        d=np.abs(np.diff(closes))
        cs=np.r_[0.0,np.cumsum(d)]
        j=np.arange(6,len(closes))
        net=closes[j]-closes[j-6]
        path=cs[j]-cs[j-6]
        ser[j]=np.divide(net,path,out=np.zeros_like(net),where=path>0)
    qb=t[query_idx]//tf_ms
    bi=np.searchsorted(bars,qb,side='left')-1
    out=np.full(len(query_idx),np.nan)
    ok=bi>=0
    out[ok]=ser[bi[ok]]
    return out

def stats(x):
    x=np.asarray(x,float)
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,
            'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def masks(side,sers):
    aligned=sers*side[:,None]
    match=aligned>=0.50
    oppose=aligned<=-0.50
    nondir=np.abs(sers)<0.50
    t1=match[:,0]&match[:,1]&match[:,2]&(~oppose[:,3])&(~oppose[:,4])&(match[:,3]|match[:,4])
    t2=match[:,0]&match[:,1]&oppose[:,2]&(~oppose[:,3])&(~oppose[:,4])&(match[:,3]|match[:,4])
    t3=match[:,0]&match[:,1]&(~oppose[:,2])&nondir[:,3]&nondir[:,4]
    t4=(oppose[:,3]|oppose[:,4])&(~match[:,3])&(~match[:,4])
    used=t1|t2|t3|t4
    return {
      'T1_FULL_ALIGN':t1,
      'T2_PULLBACK_RECLAIM':t2,
      'T3_PARENT_RANGE_CHILD_TREND':t3,
      'T4_PARENT_OPPOSED':t4,
      'T5_OTHER':~used,
      'NESTED_ACCEPT':t1|t2|t3,
      'TREND_OWNED':t1|t2
    }

def variant(t,a,b,mid,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    pi,pnl=proof_trades(t,a,b,ei,ed,eg)
    op=pi>=0
    ei=ei[op]; ed=ed[op]; pi=pi[op]; pnl=pnl[op]
    side=np.where(ed<0,-1.0,1.0)
    sers=np.column_stack([signed_efficiency_at(t,mid,pi,tf) for tf in TFS])
    mm=masks(side,sers)
    split=2*len(t)//3
    disc=ei<split; val=~disc
    days=max(1,len(np.unique(t[ei]//DAY_MS)))
    base=stats(pnl)
    out={'opened':int(len(pnl)),'opened_per_active_day':float(len(pnl)/days),
         'base':base,'families':{}}
    for name,m in mm.items():
        sx=stats(pnl[m])
        adays=len(np.unique(t[ei[m]]//DAY_MS)) if m.any() else 0
        out['families'][name]={
          'retention_pct':100*float(m.mean()),
          'trades_per_active_day':float(m.sum()/adays) if adays else 0.0,
          'full':sx,
          'discovery':stats(pnl[m&disc]),
          'validation':stats(pnl[m&val]),
          'gross_loss_reduction_vs_base_usd':float(abs(base['gross_loss'])-abs(sx['gross_loss'])),
          'gross_loss_reduction_vs_base_pct':100*float((abs(base['gross_loss'])-abs(sx['gross_loss']))/abs(base['gross_loss']))
        }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()

    t,sa,sb=load(z.source)
    a,b,maxe=materialize(t,sa,sb)
    mid=(a.astype(np.int64)+b.astype(np.int64))/2.0

    out={
      'schema':'delta-a-alpha-grid001-january-nested-trend-state-v1',
      'unit':'DAA_GRID_001_JANUARY_NESTED_TREND_STATE_001',
      'status':'COMPLETE',
      'surface':'DUKAS_COINEXX_LIKE_P75',
      'ticks':int(len(t)),
      'timeframes':list(TF_NAMES),
      'ser_lookback_completed_bars':6,
      'state_thresholds':{'trend_abs_ser':0.50,'range_abs_ser_max':0.30},
      'variants':{name:variant(t,a,b,mid,m) for m,name in MULTS},
      'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
