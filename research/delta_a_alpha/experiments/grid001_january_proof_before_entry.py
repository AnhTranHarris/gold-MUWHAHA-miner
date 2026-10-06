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
def simulate(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    baseline=np.empty(n,np.float64)
    pbe=np.zeros(n,np.float64)
    opened=np.zeros(n,np.int8)
    status=np.zeros(n,np.int8)  # 1 fail before proof, 2 TP, 3 SL, 4 timeout, 5 no decision

    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        event_entry=a[i] if side>0 else b[i]

        # Immediate-continuation baseline.
        tp=event_entry+g if side>0 else event_entry-g
        sl=event_entry-g if side>0 else event_entry+g
        ex=event_entry; last=i; j=i+1
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
        baseline[k]=((ex-event_entry) if side>0 else (event_entry-ex))/PRICE_SCALE-COMMISSION

        # Proof-before-entry gate.
        proof=max(1,int(round(0.25*g)))
        fail=max(1,int(round(0.50*g)))
        proof_idx=-1; decided=False; j=i+1

        while j<t.size and t[j]<=end:
            px=b[j] if side>0 else a[j]
            if side>0:
                if px<=event_entry-fail:
                    status[k]=1; decided=True; break
                if px>=event_entry+proof:
                    proof_idx=j; decided=True; break
            else:
                if px>=event_entry+fail:
                    status[k]=1; decided=True; break
                if px<=event_entry-proof:
                    proof_idx=j; decided=True; break
            j+=1

        if not decided or proof_idx<0:
            if not decided:
                status[k]=5
            continue

        opened[k]=1
        entry=a[proof_idx] if side>0 else b[proof_idx]
        tp2=entry+g if side>0 else entry-g
        sl2=entry-g if side>0 else entry+g
        ex2=entry; last2=proof_idx; rr=4; q=proof_idx+1

        while q<t.size and t[q]<=end:
            last2=q
            if side>0:
                if b[q]>=tp2:
                    ex2=b[q]; rr=2; break
                if b[q]<=sl2:
                    ex2=b[q]; rr=3; break
            else:
                if a[q]<=tp2:
                    ex2=a[q]; rr=2; break
                if a[q]>=sl2:
                    ex2=a[q]; rr=3; break
            q+=1
        else:
            ex2=b[last2] if side>0 else a[last2]
            rr=4

        status[k]=rr
        pbe[k]=((ex2-entry) if side>0 else (entry-ex2))/PRICE_SCALE-COMMISSION

    return baseline,pbe,opened,status

def stats(x):
    x=np.asarray(x,float)
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {
        'n':int(len(x)),
        'net':float(x.sum()),
        'gross_profit':gp,
        'gross_loss':gl,
        'pf':gp/abs(gl) if gl<0 else None,
        'expected':float(x.mean()) if len(x) else None,
        'win_pct':100*float((x>0).mean()) if len(x) else None,
    }

def variant(t,a,b,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    baseline,pbe,opened,status=simulate(t,a,b,ei,ed,eg)
    op=opened==1
    split=2*len(t)//3
    disc=ei<split
    val=~disc
    active_days=len(np.unique(t[ei]//DAY_MS))

    def segment(mask):
        sm=mask & op
        return {
            'events':int(mask.sum()),
            'opened':int(sm.sum()),
            'opened_pct':100*float(sm.sum()/max(1,mask.sum())),
            'baseline':stats(baseline[mask]),
            'physical':stats(pbe[sm]),
            'system_event_net':float(pbe[mask].sum()),
            'expected_per_event':float(pbe[mask].mean()) if mask.sum() else None,
            'fail_before_proof':int(np.sum(mask & (status==1))),
            'no_decision':int(np.sum(mask & (status==5))),
        }

    physical=stats(pbe[op])
    baseline_stats=stats(baseline)
    return {
        'events':int(len(ei)),
        'events_per_active_day':float(len(ei)/active_days),
        'opened':int(op.sum()),
        'opened_pct':100*float(op.mean()),
        'opened_per_active_day':float(op.sum()/active_days),
        'failed_before_proof':int(np.sum(status==1)),
        'failed_before_proof_pct':100*float(np.mean(status==1)),
        'no_decision_timeout':int(np.sum(status==5)),
        'physical_tp':int(np.sum(status==2)),
        'physical_sl':int(np.sum(status==3)),
        'physical_timeout':int(np.sum(status==4)),
        'baseline_full':baseline_stats,
        'physical_full':physical,
        'system_event_net':float(pbe.sum()),
        'expected_per_lattice_event':float(pbe.mean()),
        'gross_loss_reduction_vs_baseline_usd':float(abs(baseline_stats['gross_loss'])-abs(physical['gross_loss'])),
        'gross_loss_reduction_vs_baseline_pct':100*float((abs(baseline_stats['gross_loss'])-abs(physical['gross_loss']))/abs(baseline_stats['gross_loss'])),
        'discovery':segment(disc),
        'validation':segment(val),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    z=ap.parse_args()

    t,sa,sb=load(z.source)
    a,b,maxe=materialize(t,sa,sb)

    out={
        'schema':'delta-a-alpha-grid001-january-proof-before-entry-v1',
        'unit':'DAA_GRID_001_JANUARY_PROOF_BEFORE_ENTRY_001',
        'status':'COMPLETE',
        'surface':'DUKAS_COINEXX_LIKE_P75',
        'ticks':int(len(t)),
        'contract':{
            'proof_gap':0.25,
            'failure_gap':0.50,
            'post_proof_tp_sl_gap':1.0,
            'horizon_seconds':300,
            'horizon_reset':False,
            'fixed_lot':0.01,
            'roundtrip_commission_usd':0.02,
            'martingale':False,
            'physical_overlap_model':False,
        },
        'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE)),
        'variants':{name:variant(t,a,b,m) for m,name in MULTS},
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__':
    main()
