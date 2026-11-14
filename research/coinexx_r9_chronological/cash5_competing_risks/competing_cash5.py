"""R9 Coinexx frozen P5 -> mutually exclusive 5s cash first-causes.

No raw ticks, feature reconstruction, live EA change or high-AUC retraining.
Train ONLY on previously held-out May..prior-month frozen P5 predictions.
Cash causes are original as-of source-ordinal tick labels: +0.10 cash first,
-0.65 cash first, or neither within five seconds, with >2.5s quote gap censored.
Prices and fees use previously disclosed HYPOTHETICAL 0.01-lot K=1/C=.20.
The label tracks hypothetical entry-to-5s quote paths, not realized strategy.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, log_loss

CODES = (0,1,2)  # no observed event, positive first, adverse first
CONTEXT = ('spread_u','r9_atr_u','r9_disp_signed_u','r9_eff','r9_range_u',
           'quote_gap_ms','minute_second','rearm','side')
SOURCE_RECEIPT = 'R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip'
MODEL_ARCHIVE = 'R9_M60_JanSep_FullTraining_155Features_20261113.zip'
PINS = {
  5:'48c3e3898aab1a78cc5f3b0fec45137af23f2267a4ef665a73eb1e1c431ed661',
  6:'bdeb8c4ccc8b6523c3c2cf1185104162c5bf2e3f45271c42c521e50e660ec121',
  7:'bd4c886a470cecac663f5cb71889f195148fa2ef3da932cfce02c361c873e1c5',
  8:'b23e84ed6d9d34b68e5496c71304b76c5db8be8b81be85975ea5dcd1f4df830f',
  9:'8d6bb3c41741a2223494a8ec87314e9e8d7ea93634ab83498dd133fe7a187d06',
}

def auc_safe(y, p):
    return float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None

def brier3(y, probs):
    targets=(y[:,None]==np.array(CODES)).astype(float)
    return float(np.mean(np.sum((targets-probs)**2,axis=1)))

def sanitize(z):
    z=np.asarray(z,dtype=np.float64)
    if not np.isfinite(z).all():raise ValueError('Non-finite predictors')
    return z

def logit(z):
    z=np.clip(np.asarray(z,dtype=float),1e-5,1-1e-5)
    return np.log(z/(1-z))

def encode_features(d, mode):
    """All fields existed at original R9 entry. No current/future cash info."""
    x=np.asarray(d['context'],dtype=float)
    ses=d['session'].astype(int)
    if not np.all(np.isin(ses,[0,1,2,3])):raise ValueError('Unknown session code')
    oh=np.eye(4)[ses][:,1:]  # session 0 as reference
    z=np.column_stack((x,oh))
    if mode=='with_frozen_p5':z=np.column_stack((z,logit(d['p5'])))
    return sanitize(z)

def normalize_fit(x):
    """Training-only winsorization / standardization; no test labels involved."""
    lo,hi=np.percentile(x,[1.,99.],axis=0)
    t=np.clip(x,lo,hi)
    mu=np.mean(t,axis=0);std=np.std(t,axis=0)
    std=np.where(std<1e-7,1.,std)
    return lo,hi,mu,std

def normalize_apply(x, norm):
    lo,hi,mu,std=norm
    return (np.clip(x,lo,hi)-mu)/std

def read_month(m,root,archive,receipt,models):
    mm=f'{m:02d}';pred=np.load(root/f'r9_auc_strength_work/pred_fold_{mm}.npz',allow_pickle=False)
    micro=np.load(root/f'r9_auc_strength_work/cache/micro_2026_{mm}.npz',allow_pickle=False)
    ledger=pd.read_csv(io.BytesIO(archive.read(f'candidate_closes_2026_{mm}.csv.gz')),
         compression='gzip',usecols=['entry_ordinal','entry_time_msc','side', 'session','entry_price_u',
          'spread_u','r9_atr_u','r9_disp_signed_u','r9_eff','r9_range_u','quote_gap_ms',
          'minute_second','rearm'])
    n=len(ledger);assert n==len(pred['p_frozen'])==len(micro['cash_label'])
    if n!=receipt['source_months'][mm]['entries']:raise ValueError('Original completed trade count changed')
    if str(micro['source_sha256'])!=receipt['source_months'][mm]['source_sha256']:
        raise ValueError('Raw Coinexx frozen SHA receipt mismatch')
    if not np.all(np.diff(ledger['entry_ordinal'])>0):raise ValueError('Ordinal disorder')
    if not np.array_equal(ledger['session'].to_numpy('i1'),pred['session']):
        raise ValueError('Source session mismatch')
    cause=micro['cash_label'].astype('i1')
    if not np.array_equal(pred['cash_good'],cause!=-1):
        raise ValueError('Source censor label mismatch')
    if not np.array_equal(pred['cash_label'],(cause==1).astype('i1')):
        raise ValueError('Source favorable-event label mismatch')
    hit=micro['cash_hit_ms'].astype(int)
    if np.any((cause==0)&(hit!=-1)) or np.any((cause>=1)&((hit<0)|(hit>5000))):
        raise ValueError('Future first-cause time invalid')
    sha=hashlib.sha256(models.read(f'models/direct_test_{mm}_shadow.joblib')).hexdigest()
    if sha!=PINS[m]:raise ValueError('Original 155-model weights replaced')
    orig_auc=auc_safe(pred['y_original'][pred['good_original']],pred['p_frozen'][pred['good_original']])
    original_report=json.loads(models.read(f'outputs/fold_{mm}.json'))['models']['direct_5sec']['r9_direction_auc5']
    if abs(orig_auc-original_report)>1e-6:raise ValueError('Original approved P5 AUC failed reproduction')
    x=ledger[list(CONTEXT)].to_numpy('f8')
    return {'month':m,'n':n,'y':cause,'hit':hit,'context':x,'p5':pred['p_frozen'].copy(),
        'session':pred['session'].copy(), 'cash_orig':pred['net_cash'].copy(),
        'date':(ledger['entry_time_msc'].to_numpy('i8')//86_400_000),
        'p5_orig_auc':orig_auc,'source_sha256':str(micro['source_sha256'])}

def predictions(train,test,mode):
    a=np.concatenate([encode_features(x,mode)[x['y']!=-1] for x in train])
    y=np.concatenate([x['y'][x['y']!=-1] for x in train])
    if not np.array_equal(np.unique(y),np.array(CODES)):raise ValueError('Missing competing cause')
    norm=normalize_fit(a)
    model=LogisticRegression(C=0.3,max_iter=350,solver='lbfgs',random_state=20261114)
    model.fit(normalize_apply(a,norm),y)
    if not np.array_equal(model.classes_,np.array(CODES)):raise ValueError('Unexpected class order')
    z=normalize_apply(encode_features(test,mode),norm)
    p=model.predict_proba(z)
    if not np.allclose(np.sum(p,axis=1),1.,atol=1e-9):raise ValueError('Probabilities do not sum to one')
    return p

def evaluate(test,p,contextp):
    y=test['y'];good=y>=0
    if not np.array_equal(np.unique(y[good]),np.array(CODES)):raise ValueError('Missing test cause')
    b={}
    for name,pred in [('context',contextp),('context_plus_frozen_p5',p)]:
        yp=y[good]; pp=pred[good]
        b[name]={
            'n_uncensored':int(good.sum()),
            'log_loss_three_class':float(log_loss(yp,pp,labels=list(CODES))),
            'brier_three_class':brier3(yp,pp),
            'favorable_first_auc':auc_safe((yp==1).astype(int),pp[:,1]),
            'adverse_first_auc':auc_safe((yp==2).astype(int),pp[:,2]),
            'expected_favorable_rate':float(pp[:,1].mean()),
            'observed_favorable_rate':float((yp==1).mean()),
            'expected_adverse_rate':float(pp[:,2].mean()),
            'observed_adverse_rate':float((yp==2).mean()),
        }
    raw_auc={name:auc_safe((y[good]==cause).astype(int),test['p5'][good])
             for name,cause in [('favorable_first',1),('adverse_first',2)]}
    b['unchanged_155_p5_raw_cash_ranking_auc']=raw_auc
    b['deltas_after_adding_p5']={
        'three_class_log_loss': b['context_plus_frozen_p5']['log_loss_three_class']-b['context']['log_loss_three_class'],
        'three_class_brier': b['context_plus_frozen_p5']['brier_three_class']-b['context']['brier_three_class'],
        'favorable_auc': b['context_plus_frozen_p5']['favorable_first_auc']-b['context']['favorable_first_auc'],
        'adverse_auc': b['context_plus_frozen_p5']['adverse_first_auc']-b['context']['adverse_first_auc'],
    }
    return b

def empirical_landmarks(d):
    out={}; y=d['y']; h=d['hit']
    good=y>=0
    for seconds in [1,3,5]:
        t=seconds*1000
        out[str(seconds)]={
            'pct_favorable_first_by_t_over_uncensored':float(np.mean((y[good]==1)&(h[good]<=t))),
            'pct_adverse_first_by_t_over_uncensored':float(np.mean((y[good]==2)&(h[good]<=t))),
            'pct_no_observed_event_by_t_over_uncensored':float(np.mean(~((h[good]>=0)&(h[good]<=t))))}
    return out

def run(root:Path,out:Path):
    with zipfile.ZipFile(root/SOURCE_RECEIPT) as ledger, zipfile.ZipFile(root/MODEL_ARCHIVE) as models:
        receipt=json.loads(ledger.read('source_receipt.json'))
        fold={m:read_month(m,root,ledger,receipt,models) for m in range(5,10)}
    results=[]
    for m in range(6,10):
        train=[fold[i] for i in range(5,m)]
        test=fold[m]
        pred0=predictions(train,test,'context')
        pred1=predictions(train,test,'with_frozen_p5')
        scores=evaluate(test,pred1,pred0)
        scores.update({'evaluation_month':f'{m:02d}','training_months': [f'{i:02d}' for i in range(5,m)],
         'n_original_r9_entries':test['n'], 'n_gap_censored':int(np.sum(test['y']==-1)),
         'cause_counts':{str(c):int(np.sum(test['y']==c)) for c in (-1,0,1,2)},
         'p5_original_five_second_auc_same_label':test['p5_orig_auc'],
         'first_cause_empirical_by_seconds':empirical_landmarks(test),
         'source_sha256':test['source_sha256']})
        results.append(scores)
        print(f"EVAL {m:02d}: favorable AUC context {scores['context']['favorable_first_auc']:.5f}, "
              f"+p5 {scores['context_plus_frozen_p5']['favorable_first_auc']:.5f}; "
              f"adverse AUC context {scores['context']['adverse_first_auc']:.5f}, "
              f"+p5 {scores['context_plus_frozen_p5']['adverse_first_auc']:.5f}; "
              f"3class delta brier {scores['deltas_after_adding_p5']['three_class_brier']:+.6f}",flush=True)
    a=lambda func:float(np.mean([func(x) for x in results]))
    summary={
      'n_original_r9_eval_positions':int(sum(x['n_original_r9_entries'] for x in results)),
      'n_censored_eval_positions':int(sum(x['n_gap_censored'] for x in results)),
      'mean_original_p5_auc_for_its_OWN_label':a(lambda x:x['p5_original_five_second_auc_same_label']),
      'mean_context_favorable_auc':a(lambda x:x['context']['favorable_first_auc']),
      'mean_context_plus_p5_favorable_auc':a(lambda x:x['context_plus_frozen_p5']['favorable_first_auc']),
      'mean_context_adverse_auc':a(lambda x:x['context']['adverse_first_auc']),
      'mean_context_plus_p5_adverse_auc':a(lambda x:x['context_plus_frozen_p5']['adverse_first_auc']),
      'mean_favorable_auc_increment':a(lambda x:x['deltas_after_adding_p5']['favorable_auc']),
      'mean_adverse_auc_increment':a(lambda x:x['deltas_after_adding_p5']['adverse_auc']),
      'mean_threeclass_brier_delta':a(lambda x:x['deltas_after_adding_p5']['three_class_brier']),
      'mean_threeclass_logloss_delta':a(lambda x:x['deltas_after_adding_p5']['three_class_log_loss']),
      'folds_p5_lower_threeclass_brier':int(sum(x['deltas_after_adding_p5']['three_class_brier']<0 for x in results)),
    }
    report={
      'classification':'RETROSPECTIVE_FROZEN_R9_ENTRY_COMPETING_CASH_FIRST_CAUSE_NOT_TRADING_PERFORMANCE',
      'method':'STRICT_PRIOR_HELDOUT_P5_CALIBRATOR_TRAINED_MAY_TO_PREVIOUS_MONTH_TEST_JUNE_TO_SEPT',
      'labels':{'0':'neither cash threshold hit within 5 seconds','1':'+0.10 account cash first',
                '2':'-0.65 account cash first','-1':'right-censored quote gap >2500ms'},
      'unverified_broker_assumptions':{'account_cash_per_one_XAU_quote_dollar_at_0p01_lot':1.0,
                'extra_roundtrip_cash_cost_beyond_bidask_spread':.20},
      'warning':'All Jan-Sep already research exposed. Entry p5 model target != cash first cause; '
           'this fits probabilities under source-quote paths only; actual modified R9 stops, account governor, '
           'broker fills, rearm and profit/hour not tested. Right-censored cases excluded from predictive metrics.',
      'unchanged_original_high_auc_model':True,'no_ea_changes':True,'no_tick_rebuild':True,
      'no_production_signals':True,'five_fold_original_p5_scores_reused':True,
      'may_initial_oos_score_month_training_only':True,
      'summary':summary,'evaluation_months':results,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();run(args.root,args.output)
if __name__=='__main__':main()
