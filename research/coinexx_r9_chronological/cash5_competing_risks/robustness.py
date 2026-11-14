"""Paired source-day uncertainty and economic descriptives for frozen P5 cash-first-cause model.

No order changes; no full tick replayer. Historical days already research exposed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import zipfile
import numpy as np
from sklearn.metrics import roc_auc_score
from competing_cash5 import read_month, SOURCE_RECEIPT, MODEL_ARCHIVE, predictions, brier3

def boot_mean_fold_delta(events, B=200, seed=20261114):
    rng=np.random.default_rng(seed)
    arr=np.zeros((B,3),dtype=float)
    groups=[]
    for v in events:
        d=v['day'];u=np.unique(d)
        groups.append([np.flatnonzero(d==z) for z in u])
    for b in range(B):
        measures=[]
        for v,g in zip(events,groups):
            ii=np.concatenate([g[i] for i in rng.integers(0,len(g),size=len(g))])
            y=v['y'][ii];x=v['base'][ii];x2=v['plus'][ii]
            if len(np.unique(y==1))<2 or len(np.unique(y==2))<2:continue
            measures.append((
                roc_auc_score(y==1,x2[:,1])-roc_auc_score(y==1,x[:,1]),
                roc_auc_score(y==2,x2[:,2])-roc_auc_score(y==2,x[:,2]),
                brier3(y,x2)-brier3(y,x)))
        if not measures:raise ValueError('No valid resampled day risk sets')
        arr[b,:]=np.mean(measures,axis=0)
    return {'resamples':B,'cluster':'SOURCE_ENTRY_DAY_WITHIN_MONTH',
            'interval_type':'PAIRED_95_PERCENTILE',
            'favorable_AUC_delta_CI95':np.quantile(arr[:,0],[.025,.975]).tolist(),
            'adverse_AUC_delta_CI95':np.quantile(arr[:,1],[.025,.975]).tolist(),
            'three_class_Brier_delta_CI95':np.quantile(arr[:,2],[.025,.975]).tolist(),
            'pct_resamples_all_AUC_benefit_favorable':float(np.mean(arr[:,0]>0)),
            'warning':'Historical months previously development-exposed; bootstrap not forward-profit guarantee'}

def run(root:Path,out:Path, B=200):
    with zipfile.ZipFile(root/SOURCE_RECEIPT) as ledger, zipfile.ZipFile(root/MODEL_ARCHIVE) as models:
        receipt=json.loads(ledger.read('source_receipt.json'))
        data={m:read_month(m,root,ledger,receipt,models) for m in range(5,10)}
    events=[];detail=[]
    for m in range(6,10):
        test=data[m];train=[data[k] for k in range(5,m)]
        base=predictions(train,test,'context')
        plus=predictions(train,test,'with_frozen_p5')
        good=test['y']>=0
        events.append({'y':test['y'][good],'base':base[good],
                       'plus':plus[good],'day':test['date'][good]})
        risk=plus[:,1]-plus[:,2];cash=test['cash_orig']
        ranks=np.argsort(risk,kind='mergesort');dec=max(1,int(len(risk)*.1))
        low=ranks[:dec];high=ranks[-dec:];k95=int(np.ceil(len(risk)*.05))
        skip=ranks[:k95]
        detail.append({
          'month':f'{m:02d}', 'n':len(risk),
          'top_10pct_hypothetical_original_exit_net_mean':float(cash[high].mean()),
          'bottom_10pct_hypothetical_original_exit_net_mean':float(cash[low].mean()),
          'top_10pct_original_exit_net_win_fraction':float((cash[high]>0).mean()),
          'bottom_10pct_original_exit_net_win_fraction':float((cash[low]>0).mean()),
          'all_original_exit_net_mean':float(cash.mean()),
          'no_score_based_orders_have_changed':True,
          'low_risk_score_five_percent_drop_original_ledger_noncausal_profit_estimate':float(-cash[skip].sum()),
          'original_trades_removed_in_hypothetical_pnl_only':len(skip),
        })
    boot=boot_mean_fold_delta(events,B=B)
    result={'source':'FROZEN_ORIGINAL_COINEXX_R9_CASH_FIRST_CAUSE',
            'notes':'Original exit cash descriptives only; score thresholds selected with '
                    'test-month distribution, not causal. Never infer changed trading P&L.',
            'bootstrap':boot,'monthly_original_exit_cash_by_risk_score':detail}
    out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--bootstrap',type=int,default=200)
    a=p.parse_args();run(a.root,a.output,B=a.bootstrap)
