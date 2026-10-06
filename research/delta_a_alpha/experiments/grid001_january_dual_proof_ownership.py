from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

COMMISSION=0.02
MULTS=((0.5,'A05'),(1.0,'A10'),(1.5,'A15'))

@njit(cache=True)
def simulate(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    pnl=np.zeros(n,np.float64)
    owner=np.zeros(n,np.int8)  # 1 CONT, 2 MR, 3 ambiguous, 0 abstain
    reason=np.zeros(n,np.int8) # 1 TP, 2 SL, 3 timeout
    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        cont=-1 if d<0 else 1
        mr=-cont
        cref=a[i] if cont>0 else b[i]
        mref=a[i] if mr>0 else b[i]
        proof=max(1,int(round(0.25*g)))
        chosen=0; pi=-1; side=0
        j=i+1
        while j<t.size and t[j]<=end:
            cp=(b[j]-cref) if cont>0 else (cref-a[j])
            mp=(b[j]-mref) if mr>0 else (mref-a[j])
            cgood=cp>=proof; mgood=mp>=proof
            if cgood and mgood:
                chosen=3; break
            if cgood:
                chosen=1; pi=j; side=cont; break
            if mgood:
                chosen=2; pi=j; side=mr; break
            j+=1
        owner[k]=chosen
        if chosen==0 or chosen==3:
            continue
        entry=a[pi] if side>0 else b[pi]
        tp=entry+g if side>0 else entry-g
        sl=entry-g if side>0 else entry+g
        ex=entry; last=pi; rr=3; q=pi+1
        while q<t.size and t[q]<=end:
            last=q
            if side>0:
                if b[q]>=tp: ex=b[q]; rr=1; break
                if b[q]<=sl: ex=b[q]; rr=2; break
            else:
                if a[q]<=tp: ex=a[q]; rr=1; break
                if a[q]>=sl: ex=a[q]; rr=2; break
            q+=1
        else:
            ex=b[last] if side>0 else a[last]
        reason[k]=rr
        pnl[k]=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-COMMISSION
    return pnl,owner,reason

def stats(x):
    x=np.asarray(x,float)
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,
            'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def variant(t,a,b,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    pnl,owner,reason=simulate(t,a,b,ei,ed,eg)
    traded=(owner==1)|(owner==2)
    split=2*len(t)//3; disc=ei<split; val=~disc
    days=len(np.unique(t[ei]//DAY_MS))
    def seg(mask):
        tm=mask&traded; cm=mask&(owner==1); mm=mask&(owner==2)
        return {'events':int(mask.sum()),'trades':int(tm.sum()),
                'all':stats(pnl[tm]),'cont_owned':stats(pnl[cm]),'mr_owned':stats(pnl[mm])}
    return {'events':int(len(ei)),'events_per_active_day':float(len(ei)/days),
            'trades':int(traded.sum()),'trades_per_active_day':float(traded.sum()/days),
            'cont_owned':int(np.sum(owner==1)),'mr_owned':int(np.sum(owner==2)),
            'abstain':int(np.sum(owner==0)),'ambiguous':int(np.sum(owner==3)),
            'physical':stats(pnl[traded]),'cont_econ':stats(pnl[owner==1]),
            'mr_econ':stats(pnl[owner==2]),'discovery':seg(disc),'validation':seg(val)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()
    t,sa,sb=load(z.source); a,b,maxe=materialize(t,sa,sb)
    out={'schema':'delta-a-alpha-grid001-january-dual-proof-ownership-v1',
         'unit':'DAA_GRID_001_JANUARY_DUAL_PROOF_OWNERSHIP_001',
         'status':'COMPLETE','surface':'DUKAS_COINEXX_LIKE_P75','ticks':int(len(t)),
         'contract':{'proof_gap':0.25,'post_proof_tp_sl_gap':1.0,'horizon_seconds':300,
                     'horizon_reset':False,'fixed_lot':0.01,'roundtrip_commission_usd':0.02,
                     'martingale':False,'physical_overlap_model':False},
         'variants':{name:variant(t,a,b,m) for m,name in MULTS},
         'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))}
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
