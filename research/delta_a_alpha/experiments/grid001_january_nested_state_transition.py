from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

TFS=(5000,15000,60000,300000,900000)
MULTS=((0.5,'A05'),(1.0,'A10'),(1.5,'A15'))
COMMISSION=0.02

@njit(cache=True)
def proof_trades(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    pi=np.full(n,-1,np.int64); pnl=np.zeros(n,np.float64)
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        e0=a[i] if side>0 else b[i]
        proof=max(1,int(round(.25*g))); fail=max(1,int(round(.50*g)))
        p=-1; j=i+1
        while j<t.size and t[j]<=end:
            px=b[j] if side>0 else a[j]
            if side>0:
                if px<=e0-fail: break
                if px>=e0+proof: p=j; break
            else:
                if px>=e0+fail: break
                if px<=e0-proof: p=j; break
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

def stats(x):
    x=np.asarray(x,float); gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def transition_masks(side,event_ser,proof_ser):
    ae=event_ser*side[:,None]; ap=proof_ser*side[:,None]
    me=ae>=.50; mp=ap>=.50; oe=ae<=-.50; op=ap<=-.50
    nde=np.abs(event_ser)<.50; ndp=np.abs(proof_ser)<.50

    parent_sup_e=(me[:,3]|me[:,4])&(~oe[:,3])&(~oe[:,4])
    parent_sup_p=(mp[:,3]|mp[:,4])&(~op[:,3])&(~op[:,4])
    parent_neu_e=nde[:,3]&nde[:,4]
    parent_neu_p=ndp[:,3]&ndp[:,4]
    child_e=me[:,0]&me[:,1]
    child_p=mp[:,0]&mp[:,1]
    mid_not_e=~oe[:,2]; mid_not_p=~op[:,2]

    s1=parent_sup_e&parent_sup_p&child_e&child_p&mid_not_e&mid_not_p
    s2=parent_sup_e&parent_sup_p&(~child_e)&child_p&mid_not_p
    s3=parent_sup_e&parent_sup_p&oe[:,2]&(~op[:,2])&child_p
    s4=parent_sup_e&parent_sup_p&oe[:,2]&(~child_e)&(~op[:,2])&child_p
    s5=parent_neu_e&parent_neu_p&(~child_e)&child_p&mid_not_p
    s6=(~mp[:,3])&(~mp[:,4])&(op[:,3]|op[:,4])

    return {
      'S1_STABLE_ALIGN':s1,
      'S2_CHILD_RECLAIM_PARENT_TREND':s2,
      'S3_MIDDLE_RECLAIM_PARENT_TREND':s3,
      'S4_DEEP_RECLAIM':s4,
      'S5_PARENT_RANGE_CHILD_RECLAIM':s5,
      'S6_PARENT_OPPOSED_AT_PROOF':s6,
      'TRANSITION_ACCEPT':s2|s3|s4|s5,
      'RECLAIM_PARENT_ONLY':s2|s3|s4
    }

def variant(t,a,b,mid,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    pi,pnl=proof_trades(t,a,b,ei,ed,eg)
    opened=pi>=0
    ei=ei[opened]; ed=ed[opened]; pi=pi[opened]; pnl=pnl[opened]
    side=np.where(ed<0,-1.0,1.0)
    se=np.column_stack([signed_efficiency_at(t,mid,ei,tf) for tf in TFS])
    sp=np.column_stack([signed_efficiency_at(t,mid,pi,tf) for tf in TFS])
    mm=transition_masks(side,se,sp)
    split=2*len(t)//3; disc=ei<split; val=~disc
    base=stats(pnl)
    out={'opened':int(len(pnl)),'base':base,'families':{}}
    for name,m in mm.items():
        sx=stats(pnl[m]); days=len(np.unique(t[ei[m]]//DAY_MS)) if m.any() else 0
        out['families'][name]={
          'retention_pct':100*float(m.mean()),
          'trades_per_active_day':float(m.sum()/days) if days else 0.0,
          'full':sx,'discovery':stats(pnl[m&disc]),'validation':stats(pnl[m&val]),
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
      'schema':'delta-a-alpha-grid001-january-nested-state-transition-v1',
      'unit':'DAA_GRID_001_JANUARY_NESTED_STATE_TRANSITION_001',
      'status':'COMPLETE','surface':'DUKAS_COINEXX_LIKE_P75','ticks':int(len(t)),
      'variants':{name:variant(t,a,b,mid,m) for m,name in MULTS},
      'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
