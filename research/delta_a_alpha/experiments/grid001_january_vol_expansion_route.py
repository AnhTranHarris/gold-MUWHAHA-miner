from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

ENTRY_FEE=0.01
EXIT_FEE=0.01
THRESHOLDS=(1.75,2.0)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(8<<20),b""):
            h.update(block)
    return h.hexdigest()

def vol_ratio_events(t,bid,ei):
    bucket=t//60_000
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    hi=np.maximum.reduceat(bid,starts).astype(np.int64)
    lo=np.minimum.reduceat(bid,starts).astype(np.int64)
    cl=bid[ends].astype(np.int64)
    prev=np.r_[cl[0],cl[:-1]]
    tr=np.maximum(hi-lo,np.maximum(np.abs(hi-prev),np.abs(lo-prev))).astype(float)
    cs=np.r_[0.0,np.cumsum(tr)]
    a14=np.full(len(tr),np.nan)
    a240=np.full(len(tr),np.nan)
    for k in range(14,len(tr)):
        a14[k]=(cs[k]-cs[k-14])/14.0
    for k in range(240,len(tr)):
        a240[k]=(cs[k]-cs[k-240])/240.0
    ratio=np.divide(a14,a240,out=np.full(len(tr),np.nan),
                    where=np.isfinite(a14)&np.isfinite(a240)&(a240>0))
    mins=bucket[starts]
    em=t[ei]//60_000
    mi=np.searchsorted(mins,em,side='left')-1
    out=np.full(len(ei),np.nan)
    ok=mi>=0
    out[ok]=ratio[mi[ok]]
    return out

@njit(cache=True)
def candidate_trades(t,a,b,ei,ed,eg,vr,threshold,confirm_ms=3000,horizon_ms=300000):
    n=ei.size
    cevent=np.empty(n,np.int64)
    centry=np.empty(n,np.int64)
    cexit=np.empty(n,np.int64)
    cside=np.empty(n,np.int8)
    cpnl=np.empty(n,np.float64)
    creason=np.empty(n,np.int8)
    cgap=np.empty(n,np.int32)
    cratio=np.empty(n,np.float64)
    nc=0

    for k in range(n):
        if not np.isfinite(vr[k]) or vr[k] < threshold:
            continue
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k])
        m0=0.5*(a[i]+b[i]); deadline=t[i]+confirm_ms
        j=i+1; proof=-1
        while j<t.size and t[j]<=deadline:
            m=0.5*(a[j]+b[j])
            if d>0:
                if m>=m0+g: proof=j; break
            else:
                if m<=m0-g: proof=j; break
            j+=1
        if proof<0:
            continue

        side=1 if d>0 else -1
        entry=a[proof] if side>0 else b[proof]
        target_raw=max(1,int(round(1.5*g)))
        tp=entry+target_raw if side>0 else entry-target_raw
        stop=m0
        end=t[i]+horizon_ms
        q=proof+1; last=proof; ex=entry; reason=3
        while q<t.size and t[q]<=end:
            last=q
            if side>0:
                if b[q]>=tp: ex=b[q]; reason=1; break
                if b[q]<=stop: ex=b[q]; reason=2; break
            else:
                if a[q]<=tp: ex=a[q]; reason=1; break
                if a[q]>=stop: ex=a[q]; reason=2; break
            q+=1
        else:
            ex=b[last] if side>0 else a[last]

        cpnl[nc]=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-(ENTRY_FEE+EXIT_FEE)
        cevent[nc]=i; centry[nc]=proof; cexit[nc]=last; cside[nc]=side
        creason[nc]=reason; cgap[nc]=g; cratio[nc]=vr[k]; nc+=1

    return cevent[:nc],centry[:nc],cexit[:nc],cside[:nc],cpnl[:nc],creason[:nc],cgap[:nc],cratio[:nc]

@njit(cache=True)
def single_owner(event_idx,exit_idx):
    n=event_idx.size
    keep=np.zeros(n,np.uint8)
    last_exit=-1
    suppressed=0
    for k in range(n):
        if event_idx[k] <= last_exit:
            suppressed+=1
            continue
        keep[k]=1
        last_exit=exit_idx[k]
    return keep,suppressed

@njit(cache=True)
def equity_metrics(t,a,b,entry_idx,exit_idx,side,pnl,start_balance=100000.0):
    bal=start_balance
    peak_bal=start_balance
    peak_eq=start_balance
    min_eq=start_balance
    max_bdd=0.0
    max_edd=0.0

    for k in range(entry_idx.size):
        i=int(entry_idx[k]); x=int(exit_idx[k]); s=int(side[k])
        entry=a[i] if s>0 else b[i]
        bal-=ENTRY_FEE
        if bal>peak_bal: peak_bal=bal
        max_bdd=max(max_bdd,peak_bal-bal)

        q=i
        while q<=x:
            floating=((b[q]-entry) if s>0 else (entry-a[q]))/PRICE_SCALE
            eq=bal+floating
            if eq>peak_eq: peak_eq=eq
            max_edd=max(max_edd,peak_eq-eq)
            if eq<min_eq: min_eq=eq
            q+=1

        bal += pnl[k] + ENTRY_FEE
        if bal>peak_bal: peak_bal=bal
        max_bdd=max(max_bdd,peak_bal-bal)
        if bal>peak_eq: peak_eq=bal
        max_edd=max(max_edd,peak_eq-bal)
        if bal<min_eq: min_eq=bal

    return bal-start_balance,max_bdd,max_edd,min_eq-start_balance

def stats(x):
    x=np.asarray(x,float)
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,
            'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def run(th,t,a,b,ei,ed,eg,vr):
    ce,cn,cx,cs,cp,cr,cg,cv=candidate_trades(t,a,b,ei,ed,eg,vr,th)
    candidates_before=len(ce)
    keep,supp=single_owner(ce,cx)
    m=keep.astype(bool)
    ce=ce[m]; cn=cn[m]; cx=cx[m]; cs=cs[m]; cp=cp[m]; cr=cr[m]; cg=cg[m]; cv=cv[m]

    _,bdd,edd,min_delta=equity_metrics(t,a,b,cn,cx,cs,cp)
    split=2*len(t)//3
    disc=ce<split; val=~disc
    days=len(np.unique(t[ce]//DAY_MS)) if len(ce) else 0

    return {
        'expansion_threshold':th,
        'eligible_expansion_events':int(np.sum(np.isfinite(vr)&(vr>=th))),
        'proven_candidates_before_single_owner':int(candidates_before),
        'suppressed_while_owned':int(supp),
        'trades':int(len(cp)),
        'trades_per_active_day':float(len(cp)/days) if days else 0.0,
        'full':stats(cp),
        'discovery':stats(cp[disc]),
        'validation':stats(cp[val]),
        'max_balance_drawdown':float(bdd),
        'max_equity_drawdown':float(edd),
        'min_equity_delta':float(min_delta),
        'max_total_lots':0.01 if len(cp) else 0.0,
        'small_account':{
            str(x):{'min_equity':float(x+min_delta),'positive_equity':bool(x+min_delta>0)}
            for x in (100,200,300)
        },
        'exit_reasons':{
            'target':int(np.sum(cr==1)),
            'origin_stop':int(np.sum(cr==2)),
            'timeout':int(np.sum(cr==3))
        },
        'median_gap_usd':float(np.median(cg)/PRICE_SCALE) if len(cg) else None,
        'median_expansion_ratio':float(np.median(cv)) if len(cv) else None
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()

    t,sa,sb=load(args.source)
    a,b,maxe=materialize(t,sa,sb)
    gaps=m1_atr_gap(t,b,0.5)
    ei,ed,eg=gen_events(t,a,b,gaps)
    vr=vol_ratio_events(t,b,ei)

    out={
        'schema':'delta-a-alpha-grid001-january-vol-expansion-route-v1',
        'unit':'DAA_GRID_001_JANUARY_VOL_EXPANSION_ROUTE_001',
        'status':'COMPLETE',
        'source_sha256':sha256(args.source),
        'surface':'DUKAS_COINEXX_LIKE_P75',
        'ticks':int(len(t)),
        'contract':{
            'lattice':'A05',
            'expansion_ratio':'ATR14/ATR240 completed M1',
            'thresholds':[1.75,2.0],
            'confirm_gaps':1.0,
            'confirm_max_ms':3000,
            'target_gaps':1.5,
            'stop':'original event midpoint',
            'original_event_horizon_ms':300000,
            'horizon_reset':False,
            'single_owner':True,
            'lot':0.01,
            'commission_roundtrip':0.02,
            'martingale':False
        },
        'virtual_events_total':int(len(ei)),
        'variants':{str(th):run(th,t,a,b,ei,ed,eg,vr) for th in THRESHOLDS},
        'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE))
    }
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
