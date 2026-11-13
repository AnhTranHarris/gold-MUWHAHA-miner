"""Frozen, chronological 60-second tick-pattern model research, no EA mutation.

Five validation passes: Jan-Apr -> May; Jan-May -> June; ... Jan-Aug -> Sep.
Prediction target is strictly 15-second +50 / -30 price-cent first passage.
All-model heldout months are identical WITHIN each pass; score thresholds from
training predictions only. DO NOT equate shadow filtered paths with on-policy PnL.
"""
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score,average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeClassifier
from sklearn.feature_selection import SelectKBest,f_classif
from lightgbm import LGBMClassifier
from rocket_fallback import FixedKernelPPV
from hft import hft_features

MONTHS=[f'{m:02}' for m in range(1,10)]
BASE_COLS=['side','spread_u','session','r9_atr_u','r9_disp_signed_u','r9_eff',
           'r9_range_u','r9_turns','rearm','minute_second','entry_overshoot_u',
           'w10000_signed_mid_disp','w10000_eff','w10000_events']
HORIZON_INDEX=1 # 15s, preregistered and never tuned on holdout
TARG=50;STOP=30;FEE=20

def load(directory):
    arrays=[]
    for m in MONTHS:
        f=Path(directory)/f'multiscale_2026_{m}.npz'
        if not f.exists():raise FileNotFoundError(f)
        dat=np.load(f,allow_pickle=False)
        yall=dat['labels'][:,HORIZON_INDEX]
        ok=yall!=-1
        cols=list(dat['columns'].astype(str))
        base=dat['base'][:,[cols.index(s) for s in BASE_COLS]]
        z=dict(month=m,x=dat['X'][ok],base=base[ok],
               y=(yall[ok]==1).astype(np.int8),labels=yall[ok],
               real_return=dat['ret'][ok,HORIZON_INDEX].astype(np.int32),
               times=dat['entry_times'][ok],ordinals=dat['ordinals'][ok])
        arrays.append(z)
    return arrays

def model():
    return LGBMClassifier(n_estimators=160,learning_rate=.045,num_leaves=9,
        max_depth=-1,min_child_samples=65,reg_alpha=1.0,reg_lambda=12.0,
        colsample_bytree=.9,subsample=.85,subsample_freq=1,random_state=20261113,
        n_jobs=4,verbosity=-1)

def evaluate(scores,train_scores,y,real_return):
    # 15-sec outcome; priced in integer 0.01 XAUUSD units. Quote proxy only.
    if len(np.unique(y))<2:raise RuntimeError('single-class heldout month')
    auc=float(roc_auc_score(y,scores))
    ap=float(average_precision_score(y,scores))
    result={'samples':len(y),'positive_rate':float(np.mean(y)),
      'auc':auc,'average_precision':ap,'all_quote_ev_usd_price':float(np.mean(real_return-FEE)/100)}
    for q in (0.50,0.80,0.95):
        threshold=float(np.quantile(train_scores,q))
        use=scores>=threshold
        key=f'train_quantile_{int(q*100)}'
        result[key]={'threshold':threshold,'kept':int(use.sum()),'coverage':float(np.mean(use)),
            'hit_rate':float(np.mean(y[use])) if np.any(use) else None,
            'quote_ev_usd_price':float(np.mean((real_return[use]-FEE))/100) if np.any(use) else None}
    result['status']='FAIL' if auc<.75 else ('TARGET_MET_RESEARCH_ONLY' if auc>.80 else 'RESEARCH_ONLY')
    return result

def _matrix(z,key):
    if key=='base':return z['base']
    if key=='hft':return np.concatenate((z['base'],z['hft']),axis=1)
    if key=='rocket':return z['rocket']
    if key=='fusion':return np.concatenate((z['base'],z['hft'],z['rocket']),axis=1)
    raise ValueError(key)

def run(root,out,through='09'):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=load(root)
    # Force an immutable January-April-only transform fit; its parameters are
    # fixed for all folds, and all later monthly labels are kept sealed until eval.
    pre=np.concatenate([z['x'] for z in rows[:4]])
    transform=FixedKernelPPV(train_bias_cases=64).fit(pre)
    for z in rows:
        z['hft']=hft_features(z['x'])
        z['rocket']=transform.transform(z['x'])
        print('FEATURES',z['month'],'n',len(z['y']),'positive',z['y'].mean(),flush=True)
    results=[]
    for n in range(4,9):
        if int(rows[n]['month'])>int(through):break
        train=rows[:n];test=rows[n]
        ytr=np.concatenate([x['y'] for x in train])
        yte=test['y']; rr=test['real_return']
        r={'pass':n-3,'train_months':[x['month'] for x in train],
           'check_month':test['month'],'families':{},'sample_count_train':len(ytr),
           'train_positive_rate':float(np.mean(ytr))}
        for family in ['base','hft','rocket','fusion']:
            tic=time.monotonic()
            Xtr=np.concatenate([_matrix(x,family) for x in train],axis=0)
            Xte=_matrix(test,family)
            if family=='rocket':
                est=make_pipeline(StandardScaler(),RidgeClassifier(alpha=350.,solver='lsqr'))
                est.fit(Xtr,ytr)
                pred=est.decision_function(Xte)
                trscores=est.decision_function(Xtr)
            elif family=='fusion':
                # Select Rocket kernels using TRAINING outcomes only; HFT + BASE
                # kept by explicit index; K-best trained on all train features.
                normal_count=train[0]['base'].shape[1]+train[0]['hft'].shape[1]
                rf=Xtr[:,normal_count:];test_rf=Xte[:,normal_count:]
                select=SelectKBest(score_func=f_classif,k=96)
                select.fit(rf,ytr)
                Xtr=np.concatenate([Xtr[:,:normal_count],select.transform(rf)],axis=1)
                Xte=np.concatenate([Xte[:,:normal_count],select.transform(test_rf)],axis=1)
                est=model();est.fit(Xtr,ytr)
                pred=est.predict_proba(Xte)[:,1];trscores=est.predict_proba(Xtr)[:,1]
            else:
                est=model();est.fit(Xtr,ytr)
                pred=est.predict_proba(Xte)[:,1];trscores=est.predict_proba(Xtr)[:,1]
            stats=evaluate(pred,trscores,yte,rr)
            stats['training_seconds']=round(time.monotonic()-tic,2)
            stats['train_auc']=float(roc_auc_score(ytr,trscores))
            r['families'][family]=stats
            print('FOLD',r['pass'],test['month'],family,'AUC',round(stats['auc'],5),
                  'TRAIN',round(stats['train_auc'],5),'N',len(yte),
                  'KEPT80',stats['train_quantile_80']['kept'],
                  'selectedEV80',stats['train_quantile_80']['quote_ev_usd_price'],flush=True)
        results.append(r)
        (out/f'pass_{r["pass"]}_2026_{test["month"]}.json').write_text(json.dumps(r,indent=2)+'\n')
        (out/'results.json').write_text(json.dumps({'classification':'RESEARCH_SHADOW_NOT_ON_POLICY',
          'barriers':{'gross_target_cents':TARG,'gross_stop_cents':STOP,'cost_price_cents':FEE,
          'horizon_seconds':15},'rocket_family':'custom_fixed_kernel_PPV_not_aeon_MiniRocket',
          'validation':'five expanding chronological monthly checks; January-April bias fit only',
          'passes':results},indent=2)+'\n')
    return results

if __name__=='__main__':
    arg=argparse.ArgumentParser()
    arg.add_argument('--input-dir',default='/mnt/data/r9_minute_rocket/output')
    arg.add_argument('--output-dir',default='/mnt/data/r9_minute_rocket/models')
    arg.add_argument('--through',default='09')
    a=arg.parse_args();run(a.input_dir,a.output_dir,a.through)
