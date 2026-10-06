from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import numpy as np
from numba import njit

sys.path.insert(0, '/mnt/data')
from grid001_january_event_label_lab import load_month, materialize_p75, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

COMMISSION=0.02

@njit(cache=True)
def simulate_recovery(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    retire=np.empty(n,np.float64)
    combined=np.empty(n,np.float64)
    rec_leg=np.zeros(n,np.float64)
    eligible=np.zeros(n,np.int8)
    rec_reason=np.zeros(n,np.int8)

    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        entry=a[i] if side>0 else b[i]
        proof=max(1,int(round(0.25*g)))
        early_fail=max(1,int(round(0.50*g)))
        state_confirmed=False
        ex=entry; last=i; reason=4; fail_index=-1
        j=i+1
        while j<t.size and t[j]<=end:
            last=j
            px=b[j] if side>0 else a[j]
            if not state_confirmed:
                if side>0:
                    if px<=entry-early_fail:
                        ex=px; reason=1; fail_index=j; break
                    if px>=entry+proof:
                        state_confirmed=True
                        if px>=entry+g:
                            ex=px; reason=2; break
                else:
                    if px>=entry+early_fail:
                        ex=px; reason=1; fail_index=j; break
                    if px<=entry-proof:
                        state_confirmed=True
                        if px<=entry-g:
                            ex=px; reason=2; break
            else:
                if side>0:
                    if px>=entry+g:
                        ex=px; reason=2; break
                    if px<=entry-g:
                        ex=px; reason=3; break
                else:
                    if px<=entry-g:
                        ex=px; reason=2; break
                    if px>=entry+g:
                        ex=px; reason=3; break
            j+=1
        else:
            ex=b[last] if side>0 else a[last]
            reason=4

        leg1=((ex-entry) if side>0 else (entry-ex))/PRICE_SCALE-COMMISSION
        retire[k]=leg1
        combined[k]=leg1

        if reason!=1:
            continue

        eligible[k]=1
        rside=-side
        rentry=a[fail_index] if rside>0 else b[fail_index]
        rtp=rentry+g if rside>0 else rentry-g
        rsl=rentry-g if rside>0 else rentry+g
        rex=rentry; rlast=fail_index; rr=3
        q=fail_index+1
        while q<t.size and t[q]<=end:
            rlast=q
            if rside>0:
                if b[q]>=rtp:
                    rex=b[q]; rr=1; break
                if b[q]<=rsl:
                    rex=b[q]; rr=2; break
            else:
                if a[q]<=rtp:
                    rex=a[q]; rr=1; break
                if a[q]>=rsl:
                    rex=a[q]; rr=2; break
            q+=1
        else:
            rex=b[rlast] if rside>0 else a[rlast]
            rr=3
        rp=((rex-rentry) if rside>0 else (rentry-rex))/PRICE_SCALE-COMMISSION
        rec_leg[k]=rp
        combined[k]=leg1+rp
        rec_reason[k]=rr

    return retire,combined,rec_leg,eligible,rec_reason

def stats(x):
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {
        'n':int(len(x)), 'net':float(x.sum()), 'gross_profit':gp, 'gross_loss':gl,
        'pf':gp/abs(gl) if gl<0 else None, 'expected':float(x.mean()) if len(x) else None,
        'win_pct':100*float((x>0).mean()) if len(x) else None
    }

def variant(t,a,b,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    retire,combined,rec_leg,eligible,rec_reason=simulate_recovery(t,a,b,ei,ed,eg)
    mask=eligible==1
    split=2*len(t)//3
    disc=ei<split; val=~disc
    oracle=retire.copy()
    oracle[mask]=retire[mask]+np.maximum(rec_leg[mask],0.0)
    rstats=stats(retire); cstats=stats(combined)
    return {
      'events':int(len(ei)),
      'events_per_active_day':float(len(ei)/len(np.unique(t[ei]//DAY_MS))),
      'eligible_early_failure_count':int(mask.sum()),
      'eligible_early_failure_pct':100*float(mask.mean()),
      'recovery_leg':stats(rec_leg[mask]),
      'recovery_tp_count':int(np.sum(rec_reason[mask]==1)),
      'recovery_sl_count':int(np.sum(rec_reason[mask]==2)),
      'recovery_timeout_count':int(np.sum(rec_reason[mask]==3)),
      'recovery_beats_retire_pct':100*float(np.mean(rec_leg[mask]>0)),
      'retire_full':rstats,
      'one_shot_full':cstats,
      'oracle_full':stats(oracle),
      'retire_discovery':stats(retire[disc]),
      'one_shot_discovery':stats(combined[disc]),
      'oracle_discovery':stats(oracle[disc]),
      'retire_validation':stats(retire[val]),
      'one_shot_validation':stats(combined[val]),
      'oracle_validation':stats(oracle[val]),
      'net_change_vs_retire':float(cstats['net']-rstats['net']),
      'gross_loss_change_vs_retire':float(cstats['gross_loss']-rstats['gross_loss']),
      'gross_loss_magnitude_change_pct':100*float((abs(cstats['gross_loss'])-abs(rstats['gross_loss']))/abs(rstats['gross_loss']))
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source',type=Path); ap.add_argument('--output',type=Path,required=True); z=ap.parse_args()
    t,sa,sb=load_month(z.source); a,b,maxe=materialize_p75(t,sa,sb)
    out={
      'schema':'delta-a-alpha-grid001-january-one-shot-recovery-v1',
      'unit':'DAA_GRID_001_JANUARY_ONE_SHOT_RECOVERY_001',
      'status':'COMPLETE',
      'surface':'DUKAS_COINEXX_LIKE_P75',
      'ticks':int(len(t)),
      'contract':{
        'initial_direction':'CONTINUATION','proof_gap':0.25,'early_failure_gap':0.50,
        'initial_confirmed_tp_sl_gap':1.0,'recovery_direction':'OPPOSITE','recovery_tp_sl_gap':1.0,
        'original_event_horizon_seconds':300,'horizon_reset':False,'max_recovery_flips':1,
        'roundtrip_commission_usd_per_leg':0.02,'fixed_lot':0.01,'martingale':False,
        'physical_overlap_model':False
      },
      'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE)),
      'variants':{
        'A10':variant(t,a,b,1.0),
        'A15':variant(t,a,b,1.5)
      }
    }
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
