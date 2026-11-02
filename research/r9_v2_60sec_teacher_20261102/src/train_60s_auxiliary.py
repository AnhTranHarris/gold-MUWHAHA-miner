#!/usr/bin/env python3
"""NEW auxiliary 60s future-path teacher: predict deferrable 5s-30s rescue.

This is *not* the same as actionable 250ms-3s WAIT. All three trained
probability heads use identical 19 past-only causal features. Auxiliary future
head is fitted strictly from earlier dates; its predictions, never its labels,
may penalize premature entries. Choose penalty/threshold on calibration only.
"""
from pathlib import Path
import json,argparse,numpy as np,lightgbm as lgb
from sklearn.metrics import roc_auc_score
from train_60s_reachable import MONS,CONFIGS,load,chronological_partition,evaluate_calibration,safeauc,training_arrays
from teacher_60s import hash_file
ROOT=Path('/mnt/data/v2_new_research/sixty')
LATE_PENALTIES=[0.0,.15,.30]

def fit(source,month):
    out=ROOT/'models_60s_aux'/f'{source}_{month}';out.mkdir(parents=True,exist_ok=True)
    receipt=out/'FOLD_60S_AUX.json'
    if receipt.exists():return json.loads(receipt.read_text())
    all_data=training_arrays(source,month,ROOT)
    trains=[]
    for m in MONS[:MONS.index(month)]:trains.append(load(source,m,ROOT))
    cur=load(source,month,ROOT)
    fit_mask,cal_mask,check_mask,dates=chronological_partition(cur['entry_utc_ms'])
    train_late=np.concatenate([z['teacher_60s_later_rescue'] for z in trains]+[cur['teacher_60s_later_rescue'][fit_mask]])
    X=all_data['X'];assert len(X)==len(train_late)
    folds=[]
    best=None
    nowpath=ROOT/'models_reachable_3s'/f'{source}_{month}'
    cal=all_data['cal'];check=all_data['check']
    true_cal=(cal['observed_class']==1).astype(np.uint8)
    cal_late=cur['teacher_60s_later_rescue'][cal_mask]
    check_late=cur['teacher_60s_later_rescue'][check_mask]
    for i,config in enumerate(CONFIGS):
        lgb_params={'objective':'binary','learning_rate':.055,'verbosity':-1,'num_threads':2,'seed':127,**config}
        model=lgb.train(lgb_params,lgb.Dataset(X,label=train_late,free_raw_data=True),num_boost_round=75)
        outfile=out/f'future_60s_{i}.txt';model.save_model(str(outfile))
        pc=lgb.Booster(model_file=str(nowpath/f'three_{i}.txt')).predict(cal['X'])
        pw=lgb.Booster(model_file=str(nowpath/f'wait_{i}.txt')).predict(cal['X'])
        pl=model.predict(cal['X'])
        for lam in LATE_PENALTIES:
            score=pc[:,2]-1.2*pc[:,0]-.45*pc[:,1]-.2*pw-lam*pl
            sweeps=[]
            for q in (.50,.75,.85,.90,.95,.98,.99):
                th=float(np.quantile(score,q));sel=score>th;n=int(sel.sum())
                precision=float(true_cal[sel].mean()) if n else None
                net=float(np.sum(cal['realized_net'][sel]))
                passes=bool(n and precision>=.8 and net>0)
                sweeps.append({'quantile':q,'threshold':th,'selected':n,'precision':precision,'net':net,'passes':passes})
                if passes:
                    candidate={'capacity_idx':i,'late_penalty':lam,'threshold':th,'cal_selected':n,'cal_precision':precision,'cal_net':net}
                    if best is None or candidate['cal_selected']>best['cal_selected']:best=candidate
            folds.append({'capacity_idx':i,'late_penalty':lam,'cal_late_auc':safeauc(cal_late,pl),
                          'cal_late_rate':float(cal_late.mean()),'thresholds':sweeps})
    diagnostic=None
    if best:
        i=best['capacity_idx'];lam=best['late_penalty'];th=best['threshold']
        pc=lgb.Booster(model_file=str(nowpath/f'three_{i}.txt')).predict(check['X'])
        pw=lgb.Booster(model_file=str(nowpath/f'wait_{i}.txt')).predict(check['X'])
        pl=lgb.Booster(model_file=str(out/f'future_60s_{i}.txt')).predict(check['X'])
        score=pc[:,2]-1.2*pc[:,0]-.45*pc[:,1]-.2*pw-lam*pl
        sel=score>th
        diagnostic={'selected':int(sel.sum()),'correct':int(((check['observed_class']==1)&sel).sum()),
                    'precision':float((check['observed_class'][sel]==1).mean()) if sel.any() else None,
                    'net':float(check['realized_net'][sel].sum()),
                    'future_60s_auc':safeauc(check_late,pl)}
    receipt_body={'source':source,'month':month,'training_rows':len(X),
      'future_60s_label':'nonactionable_5_15_30sec_same_side_rescue_teacher_only',
      'entry_features':'19 causal observed quote/HTF/Hawkes bins; no future labels',
      'calibration_trials':folds,'selected_earlier_calibration':best,'heldout_if_approved_calibration':diagnostic,
      'policy_promoted':False,'model_weights_sha256':{p.name:hash_file(p) for p in out.glob('future_60s_*.txt')},
      'status':'NO_APPROVAL_UNLESS_CAL_VALID_AND_COMPLETE_ON_POLICY_VOLUME_80_SURVIVAL_POSITIVE_NET'}
    receipt.write_text(json.dumps(receipt_body,indent=2))
    print(json.dumps({'source':source,'month':month,'training_rows':len(X),'valid_calibration':best is not None,'selected':best,'diagnostic':diagnostic}))
    return receipt_body

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--month',required=True);q=a.parse_args();fit(q.source,q.month)
