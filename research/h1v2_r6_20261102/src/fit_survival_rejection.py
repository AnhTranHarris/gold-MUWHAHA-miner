"""R6: isolate quote-arrival survival innovation from R5 fitted marked intensity.

DIAGNOSTIC: original independent BUY/SELL R2 action classes and R4/R5 as-of states.
Never label future historical state as an input. Only 15,000 250ms candidate
observations per month (not full 15.4m on-policy replay). Intentionally
all-four resubstitution in a separate experiment. July withheld models explicit.
"""
from __future__ import annotations
import json,hashlib,os,time
from pathlib import Path
import numpy as np
import lightgbm as lgb
from h1v2_teacher import read_ticks
from h1v2_freeze import PINNED
from quote_survival import extract,NAMES
from four_month_competing_risks import load,features,wilson
from fitted_quote_excitation import fit_poisson,predict

MONTHS=('01','02','06','07');ROOT=Path('/mnt/data/h1v2_r6/results')
R5=Path('/mnt/data/h1v2_r5/results')

def load_raw_asof():
    out={};pins={}
    for m in MONTHS:
        raw=Path('/mnt/data')/f'XAUUSD_DUKAS_2026_{m}_ticks.csv.gz'
        digest=hashlib.sha256(raw.read_bytes()).hexdigest()
        if digest!=PINNED[m]:raise ValueError(f'bad original tick hash {m}')
        with np.load(R5/f'R5_MARK_1SEC_{m}.npz') as q:
            ix=q['ix'].copy();st=q['ts'].copy()
        file=ROOT/f'R6_SURVIVAL_ASOF_{m}.npz'
        if file.exists():
            with np.load(file) as prior:
                if not np.array_equal(prior['ix'],ix) or not np.array_equal(prior['ts'],st):
                    raise ValueError('stored as-of provenance mismatch')
                z=prior['X'].copy()
        else:
            t,b,a=read_ticks(raw)
            if not np.array_equal(st,t[ix]):raise ValueError('ordinal and timestamp mismatch')
            z=extract(t,b,a,ix)
            np.savez_compressed(file,X=z,ix=ix,ts=st)
        out[m]=z
        pins[m]={'raw_sha256':digest,'quote_rows':{'01':9135062,'02':7538339,'06':8201406,'07':7415841}[m],'sample_rows':len(ix),
                 'feature_count':z.shape[1],'stored_asof_sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    return out,pins

def train_heads(dat,months,name,rounds=(115,95),leaves=(23,15)):
    op_path=ROOT/f'R6_{name}_opportunity_model.txt';dir_path=ROOT/f'R6_{name}_direction_model.txt'
    if op_path.exists() and dir_path.exists():
        return lgb.Booster(model_file=str(op_path)),lgb.Booster(model_file=str(dir_path))
    xs=[dat[m]['x'] for m in months];ys=[dat[m]['k'] for m in months]
    X=np.vstack(xs);K=np.vstack(ys)
    anygood=(K==3).any(axis=1).astype(np.int32)
    good=np.flatnonzero(anygood)
    opp={'objective':'binary','learning_rate':.06,'num_leaves':leaves[0],
         'min_data_in_leaf':60,'verbosity':-1,'num_threads':4,
         'deterministic':True,'force_col_wise':True,'seed':62411}
    direction={**opp,'num_leaves':leaves[1],'min_data_in_leaf':35}
    m_op=lgb.train(opp,lgb.Dataset(X,label=anygood),num_boost_round=rounds[0])
    m_dir=lgb.train(direction,lgb.Dataset(X[good],label=(K[good,1]==3).astype(np.int32)),num_boost_round=rounds[1])
    m_op.save_model(str(ROOT/f'R6_{name}_opportunity_model.txt'))
    m_dir.save_model(str(ROOT/f'R6_{name}_direction_model.txt'))
    return m_op,m_dir

def precision_report(scores,classes):
    side=np.argmax(scores,axis=1)
    ts=np.max(scores,axis=1)
    outcome=classes[np.arange(len(side)),side]
    ranked=np.argsort(-ts,kind='stable');top=[]
    for pct in (.005,.01,.025,.05,.10,.25):
        n=max(1,int(round(len(side)*pct)));ii=ranked[:n]
        h=np.bincount(outcome[ii],minlength=4)
        possible=np.any(classes[ii]==3,axis=1)
        top.append({'top_frac':pct,'count':n,'strong':int(h[3]),'wrong':int(h[0]),
           'neutral':int(h[1]),'weak':int(h[2]),'strict_selected_precision':float(h[3]/n),
           'oracle_any_side_strong':int(possible.sum()),'opportunity_oracle_ceiling':float(possible.mean()),
           'wilson_lower':float(wilson(int(h[3]),n))})
    return {'top':top,'max_prob':float(ts.max()),'scores_mean':float(ts.mean()),'side_buy_rate':float((side==0).mean())}

def score(m_op,m_dir,data):
    x=data['x'];opp=m_op.predict(x);sell=m_dir.predict(x)
    q=np.stack([opp*(1.-sell),opp*sell],axis=1)
    return q,opp,sell

def fit_and_eval(dataset,train,name):
    op,dr=train_heads(dataset,train,name,rounds=(45,35) if name.startswith('r6_gap_surprise') else (115,95))
    evaluation={}
    for mon in MONTHS:
        sc,prob,_=score(op,dr,dataset[mon]);k=dataset[mon]['k']
        pr=precision_report(sc,k)
        pr['opportunity_log_loss']=float(-np.mean(np.any(k==3,axis=1)*np.log(np.maximum(prob,1e-7))+(~np.any(k==3,axis=1))*np.log(np.maximum(1-prob,1e-7))))
        pr['opportunity_brier']=float(np.mean((prob-np.any(k==3,axis=1))**2))
        evaluation[mon]=pr
    return {'train_months':list(train),'feature_count':dataset['01']['x'].shape[1], 'evaluations':evaluation}

def calibrate_one(models,data):
    """Train Jan/Feb, calibrate June; never choose July labels or July threshold."""
    m_op,m_dir=models
    sc,_,_=score(m_op,m_dir,data['06'])
    row=precision_report(sc,data['06']['k'])
    n=len(sc);p=np.max(sc,axis=1);side=np.argmax(sc,axis=1)
    selected=np.argsort(-p,kind='stable');s=(data['06']['k'][np.arange(n),side]==3)[selected]
    cumul=np.cumsum(s)
    # Scan all nested prefix sizes; samples strongly time clustered, conservative rule.
    valid=[i for i in range(150,n+1) if wilson(int(cumul[i-1]),i)>=.80]
    if not valid:return {'passed':False,'calibration_max_wilson_at_top150':float(wilson(int(cumul[149]),150)), 'july_qualified_entries':0}
    threshold=float(p[selected[max(valid)-1]])
    july,_,_=score(m_op,m_dir,data['07'])
    accept=np.max(july,axis=1)>=threshold
    k=data['07']['k'][np.arange(len(july)),np.argmax(july,axis=1)]
    return {'passed':True,'threshold':threshold,'july_qualified_entries':int(accept.sum()),
      'july_strong':int((k[accept]==3).sum()),'july_wrong':int((k[accept]==0).sum())}

def run():
    ROOT.mkdir(parents=True,exist_ok=True)
    t0=time.monotonic();raw,pins=load_raw_asof();existing=load()
    with np.load(R5/'R5_MARK_1SEC_01.npz') as a,np.load(R5/'R5_MARK_1SEC_02.npz') as b:
        ex=np.vstack([a['X'],b['X']]);future=np.vstack([a['Y'],b['Y']]);
    coeff=fit_poisson(ex,future,'cross')
    datasets={'r5_intensity_only':{},'r6_quote_survival':{},'r6_gap_surprise_and_survival':{}}
    for m in MONTHS:
        b,p,mark,k,t=existing[m]
        with np.load(R5/f'R5_MARK_1SEC_{m}.npz') as q:
            xx=q['X'];ifutures=q['Y'];assert_same=np.array_equal(q['ts'],t)
            if not assert_same:raise ValueError('bad source join')
        rate=predict(xx,coeff).astype(np.float32)
        up=rate[:,[0,2,4]].sum(axis=1);down=rate[:,[1,3,5]].sum(axis=1)
        extra=np.column_stack([rate,up-down,np.log1p(up+down),(up-down)/(up+down+1e-6)]).astype('float32')
        base=np.concatenate([b,p,mark,extra],axis=1)
        # Gap surprise is observed past 8/32/128 ordinal-quote age compression
        # relative to already fitted next-1s quote mark intensity, not future Y.
        r=raw[m];age=np.log1p(np.maximum(r[:,0],0))
        intensity=rate.sum(axis=1)
        inv_speed=np.log1p(np.maximum(r[:,11],0))
        surprise=np.column_stack([age,age-np.log1p(1000./np.maximum(intensity,1e-6)),
                                   np.log1p(np.abs(r[:,1])),r[:,2],
                                   inv_speed-np.log1p(intensity)]).astype('float32')
        for variant,additional in [('r5_intensity_only',None),('r6_quote_survival',r),('r6_gap_surprise_and_survival',np.column_stack((r,surprise)) )]:
            matrix=base if additional is None else np.column_stack((base,additional)).astype('float32')
            # Fill all previous source structural NaNs in the exact same way in each variant.
            matrix=np.nan_to_num(matrix,nan=-999.0,posinf=-999.0,neginf=-999.0)
            datasets[variant][m]={'x':matrix,'k':k,'ts':t,'ix':np.load(R5/f'R5_MARK_1SEC_{m}.npz')['ix']}
    reports={}
    for variant,data in datasets.items():
        # Same Jan/Feb/June fit, July genuinely withheld, constant hyperparams.
        reports[variant]=fit_and_eval(data,('01','02','06'),f'{variant}_july_withheld')
        models=train_heads(data,('01','02'),f'{variant}_june_cal',rounds=(45,35) if variant=='r6_gap_surprise_and_survival' else (115,95))
        reports[variant]['june_calibration_july_untouched']=calibrate_one(models,data)
        print('R6',variant,'July 150',reports[variant]['evaluations']['07']['top'][1],flush=True)
        (ROOT/'R6_COMPLETED_TWO_ARMS_INTERIM.json').write_text(json.dumps(reports,indent=2))
    receipt={'method':'strict source-exact raw quote ordinal survival event-time features and R5 marked six-mark intensity',
     'scientific_status':'RESEARCH_HINDSIGHT_GEO_CAUSAL_FALSIFICATION_ONLY',
     'scope':'60k sampled as-of candidate quote events / 120k independent side labels; not full 15.4m on-policy',
     'original_source_sha256':pins,'months':list(MONTHS),
     'teacher':'independent side labels R2: WRONG/NEUTRAL/WEAK_GOOD/STRONG_GOOD; strong first 3s +0.10 before -0.10 and original exit net >=.10 and spread<=1.00',
     'feature_names':list(NAMES), 'comparisons':reports,
     'runtime_s':round(time.monotonic()-t0,2),
     'caveat':'train JanFebJune, evaluate July without July labels; strict sampled decision ranking (NOT tradable nonoverlapping PNL), no strategy promoted'}
    (ROOT/'R6_OPPORTUNITY_SURVIVAL_FALSIFICATION.json').write_text(json.dumps(receipt,indent=2))
    return receipt
if __name__=='__main__':run()
