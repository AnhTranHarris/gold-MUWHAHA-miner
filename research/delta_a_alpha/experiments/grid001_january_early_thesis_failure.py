from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit

from grid001_january_event_label_lab import load, materialize, DAY_MS, H1_MS, PRICE_SCALE

WINDOW=48
MULTS=(1.0,1.5)
ENTRY_EXIT_COMMISSION=0.02


def m1_atr_gap(t,bid,mult):
    bucket=t//60_000
    starts=np.r_[0,np.flatnonzero(bucket[1:]!=bucket[:-1])+1]
    ends=np.r_[starts[1:]-1,len(t)-1]
    hi=np.maximum.reduceat(bid,starts).astype(np.int64)
    lo=np.minimum.reduceat(bid,starts).astype(np.int64)
    cl=bid[ends].astype(np.int64)
    prev=np.r_[cl[0],cl[:-1]]
    tr=np.maximum(hi-lo,np.maximum(np.abs(hi-prev),np.abs(lo-prev))).astype(float)
    cs=np.r_[0.0,np.cumsum(tr)]
    atr=np.full(len(tr),1000.0)
    for k in range(14,len(tr)):
        atr[k]=(cs[k]-cs[k-14])/14.0
    g=np.clip(mult*atr,750,5000)
    g=np.rint(g/100)*100
    g=np.clip(g,750,5000).astype(np.int32)
    return np.repeat(g,ends-starts+1)

@njit(cache=True)
def gen_events(t,a,b,gaps,max_events=500000,max_stack=20000):
    bs=np.empty(max_stack,np.int32); bg=np.empty(max_stack,np.int32)
    ss=np.empty(max_stack,np.int32); sg=np.empty(max_stack,np.int32)
    nb=ns=0
    hi=np.empty(WINDOW-1,np.int32); lo=np.empty(WINDOW-1,np.int32)
    cnt=p=0; hour=np.int64(-1); ch=cl=np.int32(0); ready=False; rh=rl=np.int32(0)
    ei=np.empty(max_events,np.int64); ed=np.empty(max_events,np.int8); eg=np.empty(max_events,np.int32); ne=0
    for i in range(t.size):
        ti=np.int64(t[i]); ai=np.int32(a[i]); bi=np.int32(b[i]); g=np.int32(gaps[i]); h=ti//H1_MS
        if h!=hour:
            if hour!=-1:
                hi[p]=ch; lo[p]=cl; p=(p+1)%(WINDOW-1); cnt=min(cnt+1,WINDOW-1)
            hour=h; ch=bi; cl=bi
            if cnt>=WINDOW-1:
                rh=bi; rl=bi
                for j in range(WINDOW-1):
                    rh=max(rh,hi[j]); rl=min(rl,lo[j])
                ready=True
            else:
                ready=False
        else:
            ch=max(ch,bi); cl=min(cl,bi)

        while nb>0 and bi>=bs[nb-1]+bg[nb-1]: nb-=1
        while ns>0 and ai<=ss[ns-1]-sg[ns-1]: ns-=1
        if not ready: continue

        ba=bs[nb-1] if nb else rh
        if ai<ba-g:
            bs[nb]=ai; bg[nb]=g; nb+=1
            ei[ne]=i; ed[ne]=-1; eg[ne]=g; ne+=1

        sa=ss[ns-1] if ns else rl
        if ai>sa+g:
            ss[ns]=bi; sg[ns]=g; ns+=1
            ei[ne]=i; ed[ne]=1; eg[ne]=g; ne+=1
    return ei[:ne],ed[:ne],eg[:ne]

@njit(cache=True)
def continuation_baseline_and_early(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    base=np.empty(n,np.float64)
    early=np.empty(n,np.float64)
    reason=np.empty(n,np.int8)
    confirmed=np.zeros(n,np.int8)

    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        entry=a[i] if side>0 else b[i]

        tp=entry+g if side>0 else entry-g
        sl=entry-g if side>0 else entry+g
        ex=entry; last=i; j=i+1
        while j<t.size and t[j]<=end:
            last=j
            if side>0:
                if b[j]>=tp or b[j]<=sl:
                    ex=b[j]; break
            else:
                if a[j]<=tp or a[j]>=sl:
                    ex=a[j]; break
            j+=1
        else:
            ex=b[last] if side>0 else a[last]
        base[k]=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-ENTRY_EXIT_COMMISSION

        proof_raw=max(1,int(round(0.25*g)))
        early_fail_raw=max(1,int(round(0.50*g)))
        state_confirmed=False
        ex2=entry; last2=i; r=4; j=i+1
        while j<t.size and t[j]<=end:
            last2=j
            px=b[j] if side>0 else a[j]
            if not state_confirmed:
                if side>0:
                    if px<=entry-early_fail_raw:
                        ex2=px; r=1; break
                    if px>=entry+proof_raw:
                        state_confirmed=True; confirmed[k]=1
                        if px>=entry+g:
                            ex2=px; r=2; break
                else:
                    if px>=entry+early_fail_raw:
                        ex2=px; r=1; break
                    if px<=entry-proof_raw:
                        state_confirmed=True; confirmed[k]=1
                        if px<=entry-g:
                            ex2=px; r=2; break
            else:
                if side>0:
                    if px>=entry+g:
                        ex2=px; r=2; break
                    if px<=entry-g:
                        ex2=px; r=3; break
                else:
                    if px<=entry-g:
                        ex2=px; r=2; break
                    if px>=entry+g:
                        ex2=px; r=3; break
            j+=1
        else:
            ex2=b[last2] if side>0 else a[last2]
            r=4
        reason[k]=r
        early[k]=((ex2-entry) if side>0 else (entry-ex2))/PRICE_SCALE-ENTRY_EXIT_COMMISSION
    return base, early, reason, confirmed

def stats(x):
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {
        'n':int(len(x)), 'net':float(x.sum()), 'gross_profit':gp, 'gross_loss':gl,
        'pf':gp/abs(gl) if gl<0 else None, 'expected':float(x.mean()),
        'win_pct':100*float((x>0).mean())
    }

def one_variant(t,a,b,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    base,early,reason,confirmed=continuation_baseline_and_early(t,a,b,ei,ed,eg)
    split=2*len(t)//3
    disc=ei<split; val=~disc
    return {
        'events':int(len(ei)),
        'events_per_active_day':float(len(ei)/len(np.unique(t[ei]//DAY_MS))),
        'gap_quantiles_usd':np.quantile(eg/PRICE_SCALE,[.1,.25,.5,.75,.9]).tolist(),
        'baseline_full':stats(base), 'early_full':stats(early),
        'baseline_discovery':stats(base[disc]), 'early_discovery':stats(early[disc]),
        'baseline_validation':stats(base[val]), 'early_validation':stats(early[val]),
        'early_failure_count':int(np.sum(reason==1)),
        'early_failure_pct':100*float(np.mean(reason==1)),
        'confirmed_count':int(np.sum(confirmed==1)),
        'confirmed_pct':100*float(np.mean(confirmed==1)),
        'confirmed_tp_count':int(np.sum(reason==2)),
        'confirmed_sl_count':int(np.sum(reason==3)),
        'timeout_count':int(np.sum(reason==4)),
        'gross_loss_reduction_usd':float(abs(stats(base)['gross_loss'])-abs(stats(early)['gross_loss'])),
        'gross_loss_reduction_pct':100*float((abs(stats(base)['gross_loss'])-abs(stats(early)['gross_loss']))/abs(stats(base)['gross_loss'])),
        'net_improvement_usd':float(stats(early)['net']-stats(base)['net'])
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source',type=Path); ap.add_argument('--output',type=Path,required=True); z=ap.parse_args()
    t,sa,sb=load(z.source); a,b,maxe=materialize(t,sa,sb)
    variants={}
    for m,name in [(1.0,'A10'),(1.5,'A15')]:
        variants[name]=one_variant(t,a,b,m)
    out={
        'schema':'delta-a-alpha-grid001-january-early-thesis-failure-v1',
        'unit':'DAA_GRID_001_JANUARY_EARLY_THESIS_FAILURE_001',
        'status':'COMPLETE',
        'surface':'DUKAS_COINEXX_LIKE_P75',
        'ticks':int(len(t)),
        'contract':{
            'direction':'CONTINUATION','proof_favorable_gap':0.25,'provisional_adverse_gap':0.50,
            'confirmed_tp_gap':1.0,'confirmed_sl_gap':1.0,'horizon_seconds':300,'roundtrip_commission_usd':0.02,
            'lot_policy':'0.01 fixed economics proxy; no overlap/margin model in this unit'
        },
        'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE)),
        'variants':variants
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
