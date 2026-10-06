from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from numba import njit
from sklearn.tree import DecisionTreeClassifier, export_text

from grid001_january_event_label_lab import load, materialize, DAY_MS, PRICE_SCALE
from grid001_january_early_thesis_failure import m1_atr_gap, gen_events

COMMISSION=0.02
WINDOWS_MS=np.array([1000,5000,15000,30000,60000],dtype=np.int64)
WINDOW_NAMES=['1s','5s','15s','30s','60s']
PROB_GATES=(0.55,0.60,0.65)

@njit(cache=True)
def simulate_with_failure_index(t,a,b,ei,ed,eg,horizon=300000):
    n=ei.size
    retire=np.empty(n,np.float64)
    rec_leg=np.zeros(n,np.float64)
    fail_idx=np.full(n,-1,np.int64)
    rec_reason=np.zeros(n,np.int8)

    for k in range(n):
        i=int(ei[k]); d=int(ed[k]); g=int(eg[k]); end=t[i]+horizon
        side=-1 if d<0 else 1
        entry=a[i] if side>0 else b[i]
        proof=max(1,int(round(0.25*g)))
        early_fail=max(1,int(round(0.50*g)))
        state_confirmed=False
        ex=entry; last=i; reason=4; fi=-1
        j=i+1
        while j<t.size and t[j]<=end:
            last=j
            px=b[j] if side>0 else a[j]
            if not state_confirmed:
                if side>0:
                    if px<=entry-early_fail:
                        ex=px; reason=1; fi=j; break
                    if px>=entry+proof:
                        state_confirmed=True
                        if px>=entry+g:
                            ex=px; reason=2; break
                else:
                    if px>=entry+early_fail:
                        ex=px; reason=1; fi=j; break
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
        if reason!=1:
            continue

        fail_idx[k]=fi
        rside=-side
        rentry=a[fi] if rside>0 else b[fi]
        rtp=rentry+g if rside>0 else rentry-g
        rsl=rentry-g if rside>0 else rentry+g
        rex=rentry; rlast=fi; rr=3
        q=fi+1
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
        rec_leg[k]=((rex-rentry) if rside>0 else (rentry-rex))/PRICE_SCALE-COMMISSION
        rec_reason[k]=rr
    return retire,rec_leg,fail_idx,rec_reason

def stats(x):
    x=np.asarray(x,float)
    gp=float(x[x>0].sum()); gl=float(x[x<0].sum())
    return {'n':int(len(x)),'net':float(x.sum()),'gross_profit':gp,'gross_loss':gl,
            'pf':gp/abs(gl) if gl<0 else None,'expected':float(x.mean()) if len(x) else None,
            'win_pct':100*float((x>0).mean()) if len(x) else None}

def make_features(t,a,b,ei,ed,eg,fail_idx):
    mask=fail_idx>=0
    eii=ei[mask]; edi=ed[mask].astype(np.int8); egi=eg[mask].astype(np.float64); fii=fail_idx[mask]
    side=np.where(edi<0,-1.0,1.0)
    rside=-side
    entry=np.where(side>0,a[eii],b[eii]).astype(np.float64)
    fail_quote=np.where(side>0,b[fii],a[fii]).astype(np.float64)
    adverse=-side*(fail_quote-entry)
    ttf_s=np.maximum((t[fii]-t[eii])/1000.0,0.001)
    overshoot=(adverse-0.5*egi)/egi
    fail_speed=(adverse/egi)/ttf_s

    mid2=a.astype(np.int64)+b.astype(np.int64)
    dm=np.abs(np.diff(mid2,prepend=mid2[0])).astype(np.int64)
    cum=np.cumsum(dm,dtype=np.int64)

    feats=[ttf_s,fail_speed,overshoot,egi/PRICE_SCALE,edi.astype(np.float64)]
    names=['time_to_failure_s','failure_speed_gap_per_s','failure_overshoot_gap','event_gap_usd','cross_dir']
    tfail=t[fii]
    for w,nm in zip(WINDOWS_MS,WINDOW_NAMES):
        si=np.searchsorted(t,tfail-w,side='left')
        net=(mid2[fii]-mid2[si])/2.0
        aligned=rside*net/egi
        path=(cum[fii]-np.where(si>0,cum[si-1],0))/2.0
        path_gap=path/egi
        eff=np.divide(np.abs(net),path,out=np.zeros_like(net,dtype=float),where=path>0)
        aeff=np.divide(rside*net,path,out=np.zeros_like(net,dtype=float),where=path>0)
        feats.extend([aligned,path_gap,eff,aeff])
        names.extend([f'aligned_disp_{nm}_gap',f'path_len_{nm}_gap',f'eff_{nm}',f'aligned_eff_{nm}'])
    X=np.column_stack(feats).astype(np.float64)
    return mask,X,names

def bin_probe(x,pnl,bins=10):
    qs=np.quantile(x,np.linspace(0,1,bins+1))
    out=[]
    for j in range(bins):
        lo=qs[j]; hi=qs[j+1]
        if j==bins-1: m=(x>=lo)&(x<=hi)
        else: m=(x>=lo)&(x<hi)
        if not np.any(m): continue
        s=stats(pnl[m])
        out.append({'lo':float(lo),'hi':float(hi),'n':int(m.sum()),'recovery_net':s['net'],'pf':s['pf'],'expected':s['expected'],'win_pct':s['win_pct']})
    return out

def eval_selected(retire,rec_leg,all_mask,select):
    combined=retire.copy()
    idx=np.flatnonzero(all_mask)
    combined[idx[select]] += rec_leg[idx[select]]
    return combined

def lattice(t,a,b,mult):
    gaps=m1_atr_gap(t,b,mult)
    ei,ed,eg=gen_events(t,a,b,gaps)
    retire,rec_leg,fail_idx,rec_reason=simulate_with_failure_index(t,a,b,ei,ed,eg)
    eligible,X,names=make_features(t,a,b,ei,ed,eg,fail_idx)
    y=(rec_leg[eligible]>0).astype(np.int8)
    split_tick=2*len(t)//3
    disc_all=ei<split_tick; val_all=~disc_all
    disc=disc_all[eligible]; val=val_all[eligible]
    pnl=rec_leg[eligible]

    probes={}
    for idx in [0,1,2,3,5,9,13,17,21]:
        if idx < X.shape[1]: probes[names[idx]]=bin_probe(X[:,idx],pnl)

    clf=DecisionTreeClassifier(max_depth=3,min_samples_leaf=100,random_state=0)
    clf.fit(X[disc],y[disc])
    p=clf.predict_proba(X)[:,1]
    candidates=[]
    for gate in PROB_GATES:
        sd=p[disc]>=gate; sv=p[val]>=gate
        dleg=stats(pnl[disc][sd]) if np.any(sd) else stats(np.array([],float))
        vleg=stats(pnl[val][sv]) if np.any(sv) else stats(np.array([],float))
        cdisc=eval_selected(retire,rec_leg,eligible,(p>=gate))[disc_all]
        cval=eval_selected(retire,rec_leg,eligible,(p>=gate))[val_all]
        candidates.append({'gate':gate,'selected_discovery':int(sd.sum()),'selected_validation':int(sv.sum()),
                           'recovery_leg_discovery':dleg,'recovery_leg_validation':vleg,
                           'combined_discovery':stats(cdisc),'combined_validation':stats(cval)})
    best=max(candidates,key=lambda z:z['combined_discovery']['net'])
    gate=best['gate']; select=(p>=gate)
    combined=eval_selected(retire,rec_leg,eligible,select)
    oracle=retire.copy(); idx=np.flatnonzero(eligible); oracle[idx]+=np.maximum(rec_leg[idx],0.0)

    return {
      'events':int(len(ei)), 'eligible':int(eligible.sum()), 'eligible_pct':100*float(eligible.mean()),
      'recoverable_pct':100*float(y.mean()),
      'feature_names':names,
      'univariate_probes':probes,
      'tree_rules':export_text(clf,feature_names=names,max_depth=3),
      'tree_feature_importance':{names[i]:float(v) for i,v in enumerate(clf.feature_importances_) if v>0},
      'gate_candidates':candidates,
      'chosen_gate_discovery_only':gate,
      'selected_total':int(select.sum()),
      'selected_pct_of_eligible':100*float(select.mean()),
      'selected_recovery_leg_full':stats(pnl[select]),
      'retire_full':stats(retire), 'selected_full':stats(combined), 'oracle_full':stats(oracle),
      'retire_discovery':stats(retire[disc_all]),'selected_discovery':stats(combined[disc_all]),'oracle_discovery':stats(oracle[disc_all]),
      'retire_validation':stats(retire[val_all]),'selected_validation':stats(combined[val_all]),'oracle_validation':stats(oracle[val_all]),
      'validation_selected_recovery_leg':stats(pnl[val][select[val]]) if np.any(select[val]) else stats(np.array([],float))
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('source',type=Path); ap.add_argument('--output',type=Path,required=True); z=ap.parse_args()
    t,sa,sb=load(z.source); a,b,maxe=materialize(t,sa,sb)
    out={'schema':'delta-a-alpha-grid001-january-recovery-admission-v1','unit':'DAA_GRID_001_JANUARY_RECOVERY_ADMISSION_001',
         'status':'COMPLETE','surface':'DUKAS_COINEXX_LIKE_P75','ticks':int(len(t)),
         'contract':{'tree_max_depth':3,'tree_min_leaf':100,'prob_gates':list(PROB_GATES),'split':'first 2/3 tick index discovery; final 1/3 validation'},
         'max_midpoint_quantization_error_price':float(maxe/(2*PRICE_SCALE)),
         'variants':{'A10':lattice(t,a,b,1.0),'A15':lattice(t,a,b,1.5)}}
    z.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
