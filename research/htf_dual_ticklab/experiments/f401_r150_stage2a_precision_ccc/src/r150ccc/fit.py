"""Offline-only: FIT original classes; teacher available to *audit* but NEVER T0 inputs.

No fit from a Q approximate mask. This requires the exact original R150Q
vetoed event population plus independent full source/emitter certification.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class AuditPopulation:
    broker:str
    month:str
    original_ordinal:np.ndarray
    original_t0_ms:np.ndarray
    truth:np.ndarray  # offline ONLY: 0 CORRECT, 1 OPPOSITE, 2 NEUTRAL
    exact_q_mask:np.ndarray
    original_q_mask_sha256:str
    market:np.ndarray
    source_root_attested:bool
    t1_valid:np.ndarray


def validate_population(p:AuditPopulation):
    import hashlib
    n=len(p.truth)
    if not p.source_root_attested or len(p.original_q_mask_sha256)!=64:
        raise ValueError('stage2A blocked: original root or Q mask unverified')
    if hashlib.sha256(np.packbits(p.exact_q_mask).tobytes()).hexdigest()!=p.original_q_mask_sha256:
        raise ValueError('Q mask byte proof failed')
    if p.market.ndim!=2 or p.market.shape[0]!=n or not all(len(x)==n for x in
       (p.original_ordinal,p.original_t0_ms,p.exact_q_mask,p.t1_valid)):
        raise ValueError('original population identity/feature length mismatch')
    if not np.isin(p.truth,[0,1,2]).all():raise ValueError('invalid original class')
    if np.any(p.exact_q_mask&~p.t1_valid):raise ValueError('Q veto on ineligible event')
    if not np.isfinite(p.market).all():raise ValueError('nonfinite causal market data')
    if len(np.unique(p.original_ordinal))!=n:raise ValueError('duplicate original event')


def build_training_slice(p:AuditPopulation):
    validate_population(p)
    i=np.flatnonzero(p.exact_q_mask)
    return p.market[i],(p.truth[i]==0).astype(np.int8),p.original_t0_ms[i],p.original_ordinal[i]


def hard_negative_weights(x:np.ndarray,y:np.ndarray,*,n_neighbors:int=6):
    """Local class-neighborhood hard negatives without teacher or fitted parent labels.

    Uniformly sample source-only CORRECT prototypes; score BAD by proximity
    within a normalized market-state geometry. Weights are TRAIN-time only.
    """
    from sklearn.neighbors import NearestNeighbors
    x=np.asarray(x,dtype=np.float32);y=np.asarray(y,dtype=np.int8)
    good=np.flatnonzero(y==1)
    bad=np.flatnonzero(y==0)
    if len(good)<50 or len(bad)<100:return np.ones(len(y),dtype=np.float32)
    # robust scaling FIT only; weights emphasize confusing BAD neighbors
    med=np.median(x,axis=0);scale=np.maximum(np.subtract(*np.percentile(x,[75,25],axis=0)),1e-3)
    z=np.clip((x-med)/scale,-8,8)
    # Bounded prototype bank: no quadratic all-positive x all-negative lookup.
    # Repeatable selection across chronological sampling, target-free within class.
    proto=good[np.linspace(0,len(good)-1,min(1024,len(good)),dtype=np.int64)]
    basis=np.arange(min(16,z.shape[1]),dtype=np.int64)
    model=NearestNeighbors(n_neighbors=min(n_neighbors,len(proto)),algorithm='auto',n_jobs=1)
    model.fit(z[proto][:,basis]); dist=model.kneighbors(z[bad][:,basis],return_distance=True)[0].mean(axis=1)
    cut=np.quantile(dist,.25);w=np.ones(len(y),dtype=np.float32)
    w[bad]=1.+2.*np.exp(-dist/float(max(cut,1e-3)))
    w[good]=2.0
    return w


class CalibratedHead:
    """Frozen, out-of-fit isotonic reliability map for one independent expert."""
    def __init__(self,model,columns,calibrator):
        self.model=model;self.columns=np.asarray(columns,dtype=np.int64);self.calibrator=calibrator
    def predict_proba(self,x):
        z=np.asarray(x,dtype=np.float32)[:,self.columns]
        p=np.clip(self.model.predict_proba(z)[:,1],1.e-6,1-1.e-6)
        pc=np.clip(self.calibrator.predict(p),0,1)
        return np.column_stack((1-pc,pc))


def fit_three_experts(x:np.ndarray,y:np.ndarray, *, feature_groups:dict,
                      seed:int=1502):
    """FIT-only complementary high-capacity T0 experts; no teacher targets.

    Require three DIFFERENT predeclared source families: continuation path,
    Bayesian/reliability, and hard-negative local topology. Avoid three clones
    fitted to the same feature matrix.
    """
    from lightgbm import LGBMClassifier
    x=np.asarray(x,dtype=np.float32);y=np.asarray(y,dtype=np.int8)
    names=('continuation','reliability','hard_negative')
    if set(feature_groups)!=set(names):raise ValueError('three distinct source blocks required')
    cols={k:np.asarray(feature_groups[k],dtype=np.int64) for k in names}
    if (any(len(v)==0 or np.any(v<0) or np.any(v>=x.shape[1]) or len(np.unique(v))!=len(v)
            for v in cols.values()) or len({tuple(x) for x in cols.values()})!=3):
        raise ValueError('invalid/identical source feature groups')
    if x.ndim!=2 or len(x)!=len(y) or len(x)<5000 or y.sum()<150:
        raise ValueError('insufficient Q-veto source-only fitting evidence')
    w=hard_negative_weights(x[:,cols['hard_negative']],y)
    configs={
        'continuation':dict(num_leaves=63,max_depth=9,n_estimators=180,min_child_samples=90),
        'reliability':dict(num_leaves=47,max_depth=8,n_estimators=240,min_child_samples=125),
        'hard_negative':dict(num_leaves=95,max_depth=10,n_estimators=200,min_child_samples=140)
    }
    out={}
    for j,(name,params) in enumerate(configs.items()):
        m=LGBMClassifier(objective='binary',learning_rate=.04,reg_lambda=15.,
             colsample_bytree=.82,subsample=.9,subsample_freq=1,
             random_state=seed+j,n_jobs=2,verbosity=-1,**params)
        m.fit(x[:,cols[name]],y,sample_weight=w if name=='hard_negative' else None)
        out[name]=(m,cols[name])
    return out


def calibrate_three_experts(fitted,cal_x,cal_y):
    """Use a disjoint chronological CAL subset, never the FIT or July rows."""
    from sklearn.isotonic import IsotonicRegression
    x=np.asarray(cal_x,dtype=np.float32);y=np.asarray(cal_y,dtype=int)
    if len(x)<1000 or np.sum(y==1)<100 or np.sum(y==0)<100:
        raise ValueError('insufficient disjoint reliability calibration')
    out={}
    for name,(model,cols) in fitted.items():
        uncal=np.asarray(model.predict_proba(x[:,cols])[:,1],dtype=float)
        iso=IsotonicRegression(y_min=0,y_max=1,out_of_bounds='clip')
        iso.fit(uncal,y)
        out[name]=CalibratedHead(model,cols,iso)
    return out


def explain_teacher_residual_offline(*,teacher_rank,truth,market):
    """Offline microscope: measure within-class continuous teacher margins.

    The returned object MUST NEVER be exported into scorer configuration,
    feature statistics, model weights, calibration or runtime serialization.
    """
    teacher_rank=np.asarray(teacher_rank,dtype=float)
    truth=np.asarray(truth,dtype=int)
    if len(teacher_rank)!=len(truth) or market.shape[0]!=len(truth):raise ValueError('offline alignment')
    out={}
    for cls in (0,1,2):
        r=teacher_rank[truth==cls]
        out[str(cls)]={'count':int(len(r)),'q10':float(np.quantile(r,.10)) if len(r) else None,
                       'q50':float(np.median(r)) if len(r) else None,'q90':float(np.quantile(r,.90)) if len(r) else None}
    return out
