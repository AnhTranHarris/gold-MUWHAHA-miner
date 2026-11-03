"""R11 factorized discrete-time cause-specific first-passage model.

The model sees ONLY frozen as-of quote geometry plus the queried future time
interval ID. Future passage labels enter offline fit ONLY; no model may infer
from oracle schedule membership or future price path at runtime. This module
is deliberately research-only, not an approved R9/MT5 entry strategy.
"""
from __future__ import annotations
import numpy as np

CLASSES=('SURVIVE_INTERVAL','FIRST_FAVORABLE','FIRST_ADVERSE')

def person_period_data(X,risks,side,*,max_candidates=None):
    """Generate observed at-risk interval rows without censor-as-survival bias.

    For an interval that is only partially observed and no event occurs, the
    row is right censored and must NOT be trained as SURVIVE_INTERVAL.
    """
    x=np.asarray(X,np.float32)
    if x.ndim!=2 or not np.isfinite(x).all():raise ValueError('invalid asof matrix')
    if side not in (0,1):raise ValueError('side')
    exp=np.asarray(risks['exposure'],np.float32)
    event=np.asarray(risks['event'],np.int8)
    if exp.ndim!=3 or exp.shape[:2]!=(len(x),2) or event.shape!=exp.shape:
        raise ValueError('risk array mismatch')
    idx=np.arange(len(x),dtype=np.int64)
    if max_candidates is not None and len(idx)>max_candidates:
        idx=np.unique(np.linspace(0,len(x)-1,max_candidates,dtype=np.int64))
    observed=exp[idx,side]
    cause=event[idx,side]
    enough=(observed>=1.-1e-7)|(cause!=0)
    i,k=np.nonzero(enough)
    if len(i)==0:raise ValueError('no observed person-period labels')
    XX=np.column_stack((x[idx[i]],k.astype(np.float32))).astype(np.float32)
    yy=np.where(cause[i,k]==1,1,np.where(cause[i,k]==-1,2,0)).astype(np.int8)
    return XX,yy,idx[i],k


def fit_source_only(X,risks,side,*,max_candidates=40000,trees=60,leaves=31):
    """Fit a research candidate only; caller owns chronology and SHA receipts.

    No threshold is qualified here. All model hyperparameters and sampling need
    independent chronological preregistration in R11 Drive ledger before use.
    """
    import lightgbm as lgb
    xx,y,ix,k=person_period_data(X,risks,side,max_candidates=max_candidates)
    if len(np.unique(y))!=3:raise ValueError('insufficient observed competing causes')
    learner=lgb.LGBMClassifier(objective='multiclass',num_class=3,
                               n_estimators=trees,num_leaves=leaves,
                               min_child_samples=40,learning_rate=.05,
                               reg_lambda=12.0,random_state=20261102,
                               n_jobs=2,verbosity=-1)
    learner.fit(xx,y)
    return learner,{'fit_candidates':int(len(np.unique(ix))),
                    'fit_person_periods':int(len(y)),
                    'observed_classes':np.bincount(y,minlength=3).tolist(),
                    'status':'HINDSIGHT_SUPERVISION_TRAIN_ONLY_NOT_A_QUALIFIED_POLICY'}


def integrated_causes(per_interval_prob):
    """Product-integrate conditional competing hazards; conserve probability.

    Input p[n,K,3] ordered SURVIVE,FAV,ADV, all conditionally normalized.
    Output unconditional [BAD,NEUTRAL,GOOD] suitable for separate policy heads
    after a separately validated economic regression and calibration.
    """
    p=np.asarray(per_interval_prob,np.float64)
    if p.ndim!=3 or p.shape[-1]!=3 or not np.isfinite(p).all() or np.any(p<0) or np.any(p>1) or np.any(np.abs(p.sum(axis=2)-1)>1e-5):
        raise ValueError('conditional hazard probabilities invalid')
    survival=np.ones(len(p),np.float64)
    good=np.zeros(len(p),np.float64);bad=np.zeros(len(p),np.float64)
    for k in range(p.shape[1]):
        good+=survival*p[:,k,1]
        bad+=survival*p[:,k,2]
        survival*=p[:,k,0]
    out=np.column_stack((bad,survival,good))
    if not np.allclose(out.sum(axis=1),1.,atol=1e-6):
        raise ValueError('hazard mass not conserved')
    return out


def predict_horizons(model,X,interval_count=6):
    x=np.asarray(X,np.float32)
    if x.ndim!=2 or not np.isfinite(x).all():raise ValueError('invalid asof matrix')
    cond=np.zeros((len(x),interval_count,3),np.float64)
    predictor=model.booster_ if hasattr(model,'booster_') else model
    for k in range(interval_count):
        appended=np.column_stack((x,np.full(len(x),k,dtype=np.float32)))
        cond[:,k,:]=predictor.predict(appended)
    return integrated_causes(cond)
