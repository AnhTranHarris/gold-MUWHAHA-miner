"""H1V2 R4: strict selective BUY/SELL/WAIT research with 6-mark quote excitation.

No oracle labels are features. July-withheld training and July contaminated
resubstitution are reported distinctly; neither is an on-policy MT5 strategy.
The exponential kernel columns are observed past-event excitation covariates,
not a fitted six-dimensional Hawkes transition matrix. Multi-class predicts
WRONG, NEUTRAL, WEAK_GOOD, STRONG_GOOD, conditional on action side.
"""
from __future__ import annotations
import json,time,os,hashlib,math
from pathlib import Path
import numpy as np
import lightgbm as lgb
from scipy.stats import norm
MONTHS=('01','02','06','07');FILE=Path('/mnt/data/h1v2_r4/results')

def load(root=FILE):
    out={}
    for m in MONTHS:
        with np.load(root/f'H1V2_R4_MARKED_ATLAS_{m}.npz') as v,\
             np.load(f'/mnt/data/h1v2_r2/results/H1V2_R2_{m}_SIDE_INDEPENDENT_HARD_NEGATIVES.npz') as d,\
             np.load(f'/mnt/data/h1v2_r3/results/H1V2_R3_TRUE_PATH_{m}.npz') as z:
            assert np.array_equal(v['ix'],d['ix']) and np.array_equal(v['ts'],z['ts'])
            assert np.array_equal(v['side_class'],d['side_class'])
            basic=d['X'].astype(np.float32)
            path=z['asof_X'].astype(np.float32)
            marked=v['Xmark'].astype(np.float32)
            t=d['ts'].astype(np.int64)
            out[m]=(basic,path,marked,d['side_class'].astype(np.uint8),t)
    return out

def features(basic,path,marked,t,variant):
    # Exactly one side-specific 250ms market decision; create independent action
    # rows with shared as-of observations + explicit direction column.
    minute=(t//60000)%1440
    cyc=np.column_stack((np.sin(2*np.pi*minute/1440),np.cos(2*np.pi*minute/1440))).astype(np.float32)
    if variant=='baseline':parts=[basic,path,cyc]
    elif variant=='counts':parts=[basic,path,marked[:,:30],cyc]
    elif variant=='ordered':parts=[basic,path,marked,cyc]
    else:raise ValueError(variant)
    x=np.column_stack(parts).astype(np.float32)
    # Actual as-of quote displacements (first-to-current across horizons) are
    # side oriented for liquidation; original unsided values retained.
    oriented=path[:,::3]
    signs=np.array([1.,-1.],np.float32)
    return np.concatenate([np.column_stack([x,oriented*s,np.full((len(t),1),s,np.float32)]) for s in signs],axis=0)

def labels(k):
    # X has BUY rows then SELL rows.
    return np.r_[k[:,0],k[:,1]].astype(np.int32)

def wilson(k,n,z=1.96):
    if not n:return 0.
    p=k/n;d=1+z*z/n
    return (p+z*z/(2*n)-z*np.sqrt(p*(1-p)/n+z*z/(4*n*n)))/d

def score(model,dat,variant,month,threshold=None):
    b,p,m,k,t=dat
    xx=features(b,p,m,t,variant)
    pred=np.asarray(model.predict(xx),np.float64).reshape(2,len(k),4).transpose(1,0,2)
    # Asymmetric conservative score: reward strict-positive class, punish
    # WRONG/NEUTRAL; WAIT unless one action dominates and passes gate.
    utility=pred[:,:,3]-1.5*pred[:,:,0]-.3*pred[:,:,1]
    sides=np.argmax(utility,axis=1)
    sel=utility[np.arange(len(k)),sides]
    pred_strong=pred[np.arange(len(k)),sides,3]
    code=k[np.arange(len(k)),sides]
    rows=[]
    for top in (0.005,.01,.025,.05,.10,.25):
        n=max(1,int(len(k)*top));inds=np.argsort(sel,kind='stable')[-n:]
        s=code[inds];a=np.bincount(s,minlength=4)
        rows.append({'frac':top,'admitted':n,'strong':int(a[3]),'wrong':int(a[0]),'neutral':int(a[1]),'weak':int(a[2]),'strict_precision':float(a[3]/n), 'wilson_lower':float(wilson(a[3],n)),'min_score':float(sel[inds].min())})
    admitted=np.flatnonzero((sel>=threshold)) if threshold is not None else np.empty(0,dtype=np.int64)
    a=np.bincount(code[admitted],minlength=4)
    return {'month':month,'total_timestamps':len(k),'features':xx.shape[1],'top_rankings':rows,
        'threshold':threshold,'threshold_admitted':int(len(admitted)), 'threshold_strong':int(a[3]),
        'threshold_wrong':int(a[0]),'threshold_weak':int(a[2]),'threshold_neutral':int(a[1]),
        'threshold_precision':float(a[3]/len(admitted)) if len(admitted) else None}

def fit(data,months,variant,rounds=120,leaves=31,learning=.075):
    X=[];Y=[]
    for m in months:
        b,p,mark,k,t=data[m];X.append(features(b,p,mark,t,variant));Y.append(labels(k))
    X=np.vstack(X);Y=np.concatenate(Y)
    t0=time.monotonic()
    train=lgb.Dataset(X,label=Y,free_raw_data=True)
    cfg={'objective':'multiclass','num_class':4,'learning_rate':learning,'num_leaves':leaves,
        'max_depth':-1,'min_data_in_leaf':20,'feature_fraction':.90,
        'bagging_fraction':1.,'verbosity':-1,'num_threads':4,'seed':20261102,'deterministic':True,'force_col_wise':True}
    model=lgb.train(cfg,train,num_boost_round=rounds)
    return model,round(time.monotonic()-t0,2)

def calibrate_threshold(model,data,variant,month='06',minimum=150):
    b,p,m,k,t=data[month];xx=features(b,p,m,t,variant)
    pred=np.asarray(model.predict(xx),np.float64).reshape(2,len(k),4).transpose(1,0,2)
    utility=pred[:,:,3]-1.5*pred[:,:,0]-.3*pred[:,:,1]
    side=np.argmax(utility,axis=1)
    score=utility[np.arange(len(k)),side];code=k[np.arange(len(k)),side]
    ranks=np.argsort(-score,kind='stable')
    correct=(code[ranks]==3).astype(np.int32);cum=np.cumsum(correct)
    valid=[i for i in range(minimum,len(ranks)+1) if wilson(int(cum[i-1]),i)>=.80]
    if not valid:return None,{'qualified':False,'largest_n':0,'max_top_wilson':float(max(wilson(int(cum[i-1]),i) for i in (150,300,750,1500,3000,7500)))}
    n=max(valid);return float(score[ranks[n-1]]),{'qualified':True,'largest_n':n,'success':int(cum[n-1]),'wilson':float(wilson(int(cum[n-1]),n))}

def run(output=FILE):
    output=Path(output);data=load(output);record={'scope':'H1V2 R4 SOURCE-EXACT RAW QUOTE MARKS; four-month IS intentionally contaminated, July withheld separate','train_classes':'WRONG NEUTRAL WEAK_GOOD STRONG_GOOD','models':{},'status':'NO_MODEL_QUALIFIED_FOR_TRADING'}
    for variant in ('baseline','counts','ordered'):
        model,elapsed=fit(data,('01','02','06'),variant,rounds=120,leaves=31)
        evaluations={m:score(model,data[m],variant,m) for m in MONTHS}
        record['models'][f'{variant}_january_february_june_to_july']={'fit_seconds':elapsed,'train_months':['01','02','06'],'July_unseen':evaluations['07'],'months':evaluations}
        model.save_model(str(output/f'R4_{variant}_JULY_UNSEEN_model.txt'))
        print('JULY OOS',variant,[(x['frac'],round(x['strict_precision'],4)) for x in evaluations['07']['top_rankings'][:4]],flush=True)
    # Strict calibration separate from final July: Jan+Feb train -> June calibrate
    model,elapsed=fit(data,('01','02'),'ordered',rounds=120,leaves=31)
    threshold,cal=calibrate_threshold(model,data,'ordered','06')
    july=score(model,data['07'],'ordered','07',threshold)
    model.save_model(str(output/'R4_ordered_JANFEB_JUNE_CAL_model.txt'))
    record['models']['ordered_janfeb_june_calibration_july_untouched']={'train_months':['01','02'],'calibration_month':'06','calibration':cal,'threshold':threshold,'july':july,'fit_seconds':elapsed}
    print('STRICT GATE',cal,'July',july['threshold_admitted'],flush=True)
    # Intentional overfit: four months labels used in fit, score same four again.
    model,elapsed=fit(data,MONTHS,'ordered',rounds=500,leaves=127,learning=.12)
    insample={m:score(model,data[m],'ordered',m) for m in MONTHS}
    model.save_model(str(output/'R4_ordered_DEL_OPENLY_CONTAMINATED_ALL4_MODEL.txt'))
    record['models']['ordered_all_four_resubstitution_overfit']={'train_months':list(MONTHS),'fit_seconds':elapsed,'months':insample}
    print('OVERFIT training',[(m,round(insample[m]['top_rankings'][1]['strict_precision'],3)) for m in MONTHS],flush=True)
    (output/'H1V2_R4_MARKED_COMPETING_RISK_RESULTS.json').write_text(json.dumps(record,indent=2))
    return record
if __name__=='__main__':run()
