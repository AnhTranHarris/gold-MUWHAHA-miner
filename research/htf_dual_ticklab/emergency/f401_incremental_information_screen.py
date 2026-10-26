"""F401 STAGE 1 — predeclared incremental information screen, UNSCORED until run.

Frozen F398 model + F395 survivors are controls. Native marked L1 features must
already have been extracted with original eight source-tape SHA checks. Only
Jan early70% / Feb early60% FIT; FEB 60-80 CAL / 80-100 VAL, 40s embargo.
VAL is never used to fit or select hyperparameters. Only diagnostics, no veto.
"""
import argparse, io, json, math, pathlib, zipfile
import numpy as np
from lightgbm import Booster
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import log_loss, roc_auc_score
from f398_residual_eventflow import build_features


def model_and_events(f395_zip, f398_zip, broker, month, npz_path):
    key=f'{broker}_{month}'
    with zipfile.ZipFile(f395_zip) as z:
        with np.load(io.BytesIO(z.read(f'F395_S14_{key}_FROZEN_ORIGINAL_EVENT_MASK.npz'))) as d:
            D={k:d[k].copy() for k in d.files}
    with np.load(npz_path) as d:
        # Reject missing/misaligned rows, timestamps, source event indices or sides.
        for k,ref in [('t','t'),('side','side'),('truth','truth'),('original_index','original_index'),
                      ('f395_parent_veto','final_source_shadow_veto')]:
            if not np.array_equal(d[k],D[ref]):raise ValueError(f'{key}: {k} source-event mismatch')
        quote=d['X'].copy();names=d['feature_names'].tolist()
        hash_used=str(d['source_sha256'].item())
    with zipfile.ZipFile(f395_zip) as z:
        pins=json.loads(z.read('F386_S04_S05_SOURCE_DEPENDENCY_PINS.json'))['original_quote_files']
    filename=(f'XAUUSD_MT5_BROKER_2026_{month}_ticks_ALL.csv.gz'
              if broker=='coinexx' else f'XAUUSD_DUKAS_2026_{month}_ticks.csv.gz')
    if hash_used!=pins[filename]['registered_sha256']:
        raise ValueError(f'{key}: prior quote-source SHA receipt mismatch')
    Xparent,parent_names=build_features(D)
    with zipfile.ZipFile(f398_zip) as z:
        w=z.read(f'H1023_WRONG_{broker}.txt').decode('utf8')
    booster=Booster(model_str=w)
    if booster.num_feature()!=Xparent.shape[1]:raise ValueError('F398 frozen head feature contract mismatch')
    frozen=booster.predict(Xparent,num_threads=3).astype(np.float64)
    # Parent veto remains frozen. Restrict study to source-indexed survivors.
    daysec=(D['t']//1000)%86400;phase=2*np.pi*daysec/86400
    controls=np.column_stack((frozen,D['side'],np.sin(phase),np.cos(phase)))
    return {'t':D['t'],'y':(D['truth']!=0).astype('int8'),'truth':D['truth'],
            'survivor':~D['final_source_shadow_veto'],'controls':controls,'quote':quote,
            'features':names,'src_sha':hash_used,'f398_model_features':parent_names}


def chronological_splits(J,F):
    def bound(t,fraction):return int(len(t)*fraction)
    jcut=bound(J['t'],.70); f60=bound(F['t'],.60);f80=bound(F['t'],.80)
    # Exclude 40 seconds around every FIT/CAL/VAL cut. Diagnostic label t+32
    # matures strictly before the next fold begins.
    jfit=J['survivor']&(np.arange(len(J['t']))<jcut)&(J['t']<=J['t'][jcut-1]-40_000)
    ffit=F['survivor']&(np.arange(len(F['t']))<f60)&(F['t']<=F['t'][f60-1]-40_000)
    fcal=F['survivor']&(np.arange(len(F['t']))>=f60)&(np.arange(len(F['t']))<f80)&(F['t']>=F['t'][f60]+40_000)&(F['t']<=F['t'][f80-1]-40_000)
    fval=F['survivor']&(np.arange(len(F['t']))>=f80)&(F['t']>=F['t'][f80]+40_000)
    if not (jfit.any() and ffit.any() and fcal.any() and fval.any()):raise ValueError('empty source fold')
    return (jfit,ffit,fcal,fval)


def native_matched_permutation(x,t,side,rng):
    """Shuffle novel source features only within same UTC hour-of-day and side.
    Preserve all control predictors/labels, fold boundaries and source population.
    Jointly permute feature row to preserve internal native quote correlations.
    """
    # Exact UTC hour, not merely hour-of-day: preserve date-specific regime.
    hours=t//3_600_000
    group=hours*2+(np.asarray(side)>0)
    out=x.copy()
    for g in np.unique(group):
        idx=np.flatnonzero(group==g)
        if len(idx)>1:out[idx]=x[idx[rng.permutation(len(idx))]]
    return out


def fit_logit(X,y):
    sc=StandardScaler();T=sc.fit_transform(X)
    mdl=LogisticRegression(C=.3,max_iter=250,solver='lbfgs',random_state=401)
    mdl.fit(T,y)
    return sc,mdl


def metrics(sc,mdl,X,y):
    pr=np.clip(mdl.predict_proba(sc.transform(X))[:,1],1e-6,1-1e-6)
    return {'n':int(len(y)),'source_bad_fraction':float(y.mean()),
            'logloss':float(log_loss(y,pr,labels=[0,1])),
            'auc':float(roc_auc_score(y,pr)) if len(np.unique(y))==2 else None}


def test_one_broker(J,F,permutations=199,fit_cap=150_000):
    jfit,ffit,fcal,fval=chronological_splits(J,F)
    if J['features']!=F['features']:raise ValueError('native feature schema changed Jan/Feb')
    def part(D,mask):
        C=D['controls'][mask];Q=D['quote'][mask];y=D['y'][mask];t=D['t'][mask]
        side=C[:,1].astype('int8')
        return C,Q,y,t,side
    j=part(J,jfit);f=part(F,ffit);cal=part(F,fcal);val=part(F,fval)
    Xbase=np.concatenate((j[0],f[0]),axis=0)
    Xnew=np.concatenate((j[1],f[1]),axis=0)
    y=np.r_[j[2],f[2]]
    if fit_cap and len(y)>fit_cap:
        rng=np.random.default_rng(401)
        # Deterministic row subsample; selection is independent of outcome.
        choose=np.sort(rng.choice(len(y),size=fit_cap,replace=False))
        Xbase=Xbase[choose];Xnew=Xnew[choose];y=y[choose]
    bs,bm=fit_logit(Xbase,y)
    fs,fm=fit_logit(np.column_stack([Xbase,Xnew]),y)
    res={'fit_n':int(len(y)),'features_native':J['features'],'cal':{},'val':{}}
    for name,fold in [('cal',cal),('val',val)]:
        C,Q,Y,T,S=fold
        b=metrics(bs,bm,C,Y);u=metrics(fs,fm,np.column_stack([C,Q]),Y)
        gain=b['logloss']-u['logloss']
        null=[]
        for seed in range(permutations):
            rng=np.random.default_rng(401000+seed)
            q=native_matched_permutation(Q,T,S,rng)
            p=metrics(fs,fm,np.column_stack([C,q]),Y)
            null.append(b['logloss']-p['logloss'])
        res[name]={'baseline':b,'native_extended':u,'native_delta_logloss':float(gain),
                   'matched_placebo_99pct':float(np.quantile(null,.99)),
                   'permutation_p_upper':(1+int(np.sum(np.asarray(null)>=gain)))/(permutations+1)}
    res['novelty_qualified']=(res['cal']['native_delta_logloss']>0 and res['val']['native_delta_logloss']>0
       and res['cal']['permutation_p_upper']<=.01 and res['val']['permutation_p_upper']<=.01)
    res['qualification']='conditional-information screen ONLY; no 20:1 veto or portfolio-profit gate tested'
    return res


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--f395-archive',required=True);ap.add_argument('--f398-archive',required=True)
    ap.add_argument('--features-dir',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--permutations',type=int,default=199)
    args=ap.parse_args()
    if args.permutations<199:raise ValueError('predeclared stage-1 null requires >=199 permutations')
    report={'id':'F401-STAGE1','state':'UNAPPROVED','broker':{},'fit_split':'Jan first70% + Feb first60%, 40s embargo',
            'tested_months':'Jan/Feb only until novel information qualified',
            'no_trading_claim':True,'f400_scores':'unavailable; frozen F398+F395 are controls'}
    for broker in ('coinexx','dukascopy'):
        data={}
        for m in ('01','02'):
            p=pathlib.Path(args.features_dir)/f'F401_{broker}_{m}.npz'
            if not p.is_file():raise FileNotFoundError(f'original marked quote features missing: {p}')
            data[m]=model_and_events(args.f395_archive,args.f398_archive,broker,m,p)
        report['broker'][broker]=test_one_broker(data['01'],data['02'],args.permutations)
    out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2));print(json.dumps({'result':str(out),
              'qualified':{b:r['novelty_qualified'] for b,r in report['broker'].items()}}))
if __name__=='__main__':main()
