"""R9 M60 controlled incremental training; historic development evaluation only.

Every input is a previously frozen Coinexx source-derived as-of feature. No new
labels, stop geometry, R9 decision times or production EA changes. Retains QRB,
QAF, event trend, segmented CUSUM, signed intensity and analytic BM features.
"""
import os,sys,json,time,hashlib,zipfile,argparse
from pathlib import Path
import numpy as np, joblib
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score,average_precision_score

ROOT=Path('/mnt/data/r9_m60_training_20261113')
DATA=ROOT/'input';OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
BASE=ROOT/'source_hazard/r9_m60_competing/src'
PRIORITY=ROOT/'source_priority/src'
sys.path.insert(0,str(BASE));sys.path.insert(0,str(PRIORITY))
import train as earlier
from signal_features import action_barrier_features,FEATURE_NAMES,ACTION_NAMES

FROZEN_OLD={'05':.7080347600118277,'06':.7208719243129638,'07':.7407110057824265,'08':.7391913168155045,'09':.7276386251157598}
BASE_ARTIFACTS=ROOT/'source_priority/models'
RNG_SEED=20261113


def read_month(mm):
    with np.load(DATA/'full_derived'/f'full_month_2026_{mm}.npz',allow_pickle=False) as old, \
         np.load(DATA/'event'/f'event_2026_{mm}.npz',allow_pickle=False) as ev, \
         np.load(DATA/'derived'/f'priority_2026_{mm}.npz',allow_pickle=False) as new:
        assert np.array_equal(old['entry_times'],ev['entry']) and np.array_equal(ev['entry'],new['entry'])
        assert np.array_equal(old['entry_ordinals'],ev['ordinal']) and np.array_equal(ev['ordinal'],new['ordinal'])
        assert np.array_equal(old['side'],ev['r9_side'])
        base=np.hstack([old['features'],ev['features']]).astype('f4')
        # Same frozen feature selection as preceding 5-fold studies.
        col=list(range(14))+earlier.OLD_HFT_IDX.tolist()+list(range(145,145+len(ev['feature_names'])))
        b=base[:,col]
        side=np.tile(np.array([1.,-1.],dtype='f4'),len(ev['entry']))
        side0=np.repeat(ev['r9_side'].astype('f4'),2)
        E=np.repeat(ev['features'],2,axis=0)
        meta=np.stack([side,(side==side0).astype('f4'),np.repeat(ev['stop'].astype('f4'),2),np.repeat(ev['target'].astype('f4'),2),np.repeat(ev['spread'].astype('f4'),2)],axis=1)
        analytical=action_barrier_features(E,meta[:,4],meta[:,2],meta[:,3],side)
        X=np.concatenate([np.repeat(b,2,axis=0),np.repeat(new['features'],2,axis=0),analytical,meta],axis=1).astype('f4')
        assert np.all(np.isfinite(analytical))
        time_ms=np.repeat(ev['entry'].astype('i8'),2)
        kind=ev['cause'].reshape(-1).astype('i1')
        hit=ev['hit_ms'].reshape(-1).astype('i4')
        return dict(mm=mm,X=X,kind=kind,hit=hit,time_ms=time_ms,sp=meta[:,4],stop=meta[:,2],target=meta[:,3],r9=side0, n=len(ev['entry']))


def hazard_params():
    return dict(objective='multiclass',num_class=3,n_estimators=75,learning_rate=.055,
       num_leaves=15,min_child_samples=180,reg_alpha=2.,reg_lambda=23.,
       colsample_bytree=.87,subsample=.85,subsample_freq=1,random_state=RNG_SEED,
       n_jobs=2,verbosity=-1,max_bin=31,force_row_wise=True)


def direct_params():
    return dict(objective='binary',n_estimators=95,learning_rate=.05,
        num_leaves=19,min_child_samples=160,reg_alpha=2.,reg_lambda=22.,
        colsample_bytree=.85,subsample=.85,subsample_freq=1,random_state=RNG_SEED,
        n_jobs=2,verbosity=-1,max_bin=31,force_row_wise=True)


def area_metrics(r,scores):
    y=(r['kind']==1)&(r['hit']>=0)&(r['hit']<=5000)
    good=r['kind']!=-1
    original_side_ix=2*np.arange(r['n'])+(r['r9'][::2]<0).astype(np.int32)
    r9good=good[original_side_ix]
    s=scores
    return {
        'pooled_auc5':float(roc_auc_score(y[good],s[good])),
        'r9_direction_auc5':float(roc_auc_score(y[original_side_ix][r9good],s[original_side_ix][r9good])),
        'average_precision5':float(average_precision_score(y[good],s[good])),
        'positive_rate5':float(np.mean(y[good])),
        'n_censored':int((~good).sum()),
        'n_original_decisions':int(r['n']),
        'n_actions':int(len(s)),
        'mean_pred':float(np.mean(s[good]))
    }


def predict_hazard(model, X):
    return earlier.cumulative_incidence(model,X)


def train_fold(ix,verify_prior=True):
    mm=f'{ix+1:02d}'
    train=[read_month(f'{k:02d}') for k in range(1,ix+1)]
    test=read_month(mm)
    assert max(t['time_ms'][-1] for t in train)+60000<test['time_ms'][0]
    X=np.concatenate([r['X'] for r in train]);kind=np.concatenate([r['kind'] for r in train]);hit=np.concatenate([r['hit'] for r in train]);
    assert X.shape[1]==len(train[0]['X'][0])
    result={'test_month':mm,'train_months':[r['mm'] for r in train],
            'train_entries':sum(r['n'] for r in train),'test_entries':test['n'],
            'train_actions':len(X),'feature_count':X.shape[1],
            'labels':'UNCHANGED_FROZEN_FIRST_PASSAGE',
            'status':'EXPOSED_MONTH_RETROSPECTIVE_NOT_PRISTINE_OOS',
            'models':{}}
    # Ground comparison: the previous published model and identical features must reproduce.
    if verify_prior:
        artifact=joblib.load(BASE_ARTIFACTS/f'all_three_test_{mm}_FAILED_UNTIL_CERTIFIED.joblib')
        oldpred=predict_hazard(artifact['model'],test['X'])[5000]['p_fav']
        val=area_metrics(test,oldpred)
        if abs(val['pooled_auc5']-FROZEN_OLD[mm])>1.e-8:
            raise RuntimeError(f'Frozen hazard baseline did not reproduce: {mm} {val}')
        result['models']['frozen_baseline']=val
        del artifact,oldpred
    print('DATA',mm,'n_features',X.shape[1],'n_train_actions',len(X),'begin fit',flush=True)
    tic=time.monotonic()
    hx,hy=earlier.expanded_at_risk(X,kind,hit,max_per_bin=55000)
    H=LGBMClassifier(**hazard_params())
    H.fit(hx,hy);del hx,hy
    prediction=predict_hazard(H,test['X'])
    h5=prediction[5000]['p_fav'];h15=prediction[15000]['p_fav']
    result['models']['expanded_hazard']=area_metrics(test,h5)
    result['models']['expanded_hazard']['pooled_auc15']=float(roc_auc_score(((test['kind']==1)&(test['hit']>=0)&(test['hit']<=15000))[test['kind']!=-1],h15[test['kind']!=-1]))
    u=h5*(test['target']-earlier.FEE)-prediction[5000]['p_adv']*(test['stop']+earlier.FEE)-prediction[5000]['p_alive']*earlier.FEE
    best=np.maximum(u[::2],u[1::2]);result['models']['expanded_hazard']['utility_positive_decisions']=int((best>0).sum());
    result['models']['expanded_hazard']['utility_positive_fraction']=float(np.mean(best>0))
    model_dir=OUT/'models';model_dir.mkdir(exist_ok=True)
    hf=model_dir/f'hazard_test_{mm}_shadow.joblib';joblib.dump({'model':H,'config':hazard_params(),'status':'SHADOW_FAIL_UNLESS_CERTIFIED'},hf,compress=3)
    result['models']['expanded_hazard']['model_sha256']=hashlib.sha256(hf.read_bytes()).hexdigest()
    print('HAZARD',mm,round(result['models']['expanded_hazard']['pooled_auc5'],6),round(result['models']['expanded_hazard']['r9_direction_auc5'],6),'seconds',round(time.monotonic()-tic,1),flush=True)
    # direct binary classifier: alternative loss, identical frozen 5-second labels
    tic=time.monotonic();good=kind!=-1;y=(kind==1)&(hit>=0)&(hit<=5000)
    D=LGBMClassifier(**direct_params());D.fit(X[good],y[good].astype('i1'))
    d5=D.predict_proba(test['X'])[:,1]
    result['models']['direct_5sec']=area_metrics(test,d5)
    result['models']['fixed_half_ensemble']=area_metrics(test,.5*h5+.5*d5)
    df=model_dir/f'direct_test_{mm}_shadow.joblib';joblib.dump({'model':D,'config':direct_params(),'status':'SHADOW_FAIL_UNLESS_CERTIFIED'},df,compress=3)
    result['models']['direct_5sec']['model_sha256']=hashlib.sha256(df.read_bytes()).hexdigest()
    print('DIRECT',mm,round(result['models']['direct_5sec']['pooled_auc5'],6),'ENS',round(result['models']['fixed_half_ensemble']['pooled_auc5'],6),'seconds',round(time.monotonic()-tic,1),flush=True)
    # Training AUC is for overfit diagnosis only, never eligibility.
    # Avoid huge all-train prediction duplicate memory: score last 100k training samples.
    idx=np.arange(min(100000,len(X)))
    result['training_fit_diagnostics']={'direct_5sec_first_100k_auc':float(roc_auc_score(y[idx][good[idx]],D.predict_proba(X[idx][good[idx]])[:,1]))}
    del D,H,X,kind,hit,train,test
    outfile=OUT/f'fold_{mm}.json';outfile.write_text(json.dumps(result,indent=2)+'\n')
    return result


def fit_full():
    train=[read_month(f'{i:02d}') for i in range(1,10)]
    X=np.concatenate([r['X'] for r in train]);kind=np.concatenate([r['kind'] for r in train]);hit=np.concatenate([r['hit'] for r in train]);
    n=sum(x['n'] for x in train)
    assert n==303934 and len(X)==607868 and X.shape[1]>=150
    print('FINAL ALL NINE',n,'opportunities',len(X),'actions',X.shape[1],'features',flush=True)
    hx,hy=earlier.expanded_at_risk(X,kind,hit,max_per_bin=55000)
    H=LGBMClassifier(**hazard_params());H.fit(hx,hy);del hx,hy
    good=kind!=-1;y=(kind==1)&(hit>=0)&(hit<=5000)
    D=LGBMClassifier(**direct_params());D.fit(X[good],y[good].astype('i1'))
    model_dir=OUT/'models';model_dir.mkdir(exist_ok=True)
    paths={}
    for key,obj,config in [('hazard_all_JanSep_IS_ONLY',H,hazard_params()),('direct_all_JanSep_IS_ONLY',D,direct_params())]:
        f=model_dir/f'{key}.joblib';joblib.dump({'model':obj,'config':config,'feature_count':X.shape[1],'trained_months':'2026-01..2026-09','status':'IN_SAMPLE_RESEARCH_ONLY_NOT_CERTIFIED'},f,compress=3)
        paths[key]={'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
    state={'train_months':[x['mm'] for x in train],'n_entries':n,'n_actions':len(X),'n_features':X.shape[1], 'positive_rate':float(y[good].mean()),
           'n_censored':int((~good).sum()),'models':paths,
           'notice':'NO OOS METRIC FROM ALL_NINE_MONTH_TRAINING - future data required for certification'}
    (OUT/'all_nine_training_receipt.json').write_text(json.dumps(state,indent=2)+'\n')
    return state

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--fold',type=int);parser.add_argument('--full',action='store_true');args=parser.parse_args()
    if args.full:print(json.dumps(fit_full(),indent=2))
    else:
        assert args.fold in [4,5,6,7,8]
        print(json.dumps(train_fold(args.fold),indent=2)[:1500])
