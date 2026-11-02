"""R5: FITTED mark arrival rates as-of and asymmetric BUY/SELL/WAIT learning.

Two distinct questions:
1. next-second six quote-mark arrival likelihood (NOT trade-direction accuracy)
2. strict 3s trade quality, independent BUY/SELL, judged on a withheld July month

All four-month resubstitution is intentional *in sample* only, never deployment.
"""
from __future__ import annotations
import json,math,hashlib,time
from pathlib import Path
import numpy as np
import lightgbm as lgb
from fitted_quote_excitation import MONTHS,ROOT,predict,diagnostics
from four_month_competing_risks import load,features,labels,wilson,score

def enrich(base,rates):
    b,p,m,k,t=base
    # Rates are a function of PAST quoted mark state. No future 1s arrival Y.
    up=rates[:,[0,2,4]].sum(axis=1)
    down=rates[:,[1,3,5]].sum(axis=1)
    extra=np.column_stack((rates,up-down,np.log1p(up+down),
       (up-down)/(1e-6+up+down))).astype('float32')
    return (b,p,np.column_stack((m,extra)).astype('float32'),k,t)

def ranking(scores,classes,k,month):
    """Scores n x 2; independent side with WAIT if no confident evidence."""
    side=np.argmax(scores,axis=1)
    chosen=scores[np.arange(len(side)),side]
    codes=k[np.arange(len(side)),side]
    records=[]
    for frac in (.005,.01,.025,.05,.10,.25):
        n=max(1,round(len(side)*frac))
        ix=np.argsort(-chosen,kind='stable')[:n]
        h=np.bincount(codes[ix],minlength=4)
        side_oracle_count=int((k[ix]==3).any(axis=1).sum())
        records.append(dict(frac=frac,n=n,strong=int(h[3]),wrong=int(h[0]),neutral=int(h[1]),weak=int(h[2]),
           strict_precision=float(h[3]/n),wilson_95pct_low=float(wilson(int(h[3]),n)),
           oracle_side_potential_at_same_timestamp=side_oracle_count,
           oracle_side_ceiling=float(side_oracle_count/n)))
    return records

def evaluate(data,mode='ordered'):
    fitmonths=('01','02','06')
    xx=np.concatenate([features(*data[m][:3],data[m][4],mode) for m in fitmonths])
    yy=np.concatenate([labels(data[m][3]) for m in fitmonths])
    base=xx.shape[1]
    model=lgb.train({'objective':'multiclass','num_class':4,'learning_rate':.075,'num_leaves':47,
         'max_depth':-1,'min_data_in_leaf':30,'verbosity':-1,'num_threads':4,'seed':20261102,
         'deterministic':True,'force_col_wise':True},lgb.Dataset(xx,label=yy),num_boost_round=140)
    out={'n_features':base,'trained_months':list(fitmonths),'controls':{}}
    for m in MONTHS:
        b,p,mark,k,t=data[m];xx=features(b,p,mark,t,mode)
        pred=model.predict(xx).reshape(2,len(k),4).transpose(1,0,2)
        # Aggressively discourage WRONG (1.5x) and NEUTRAL (0.3x).
        utility=pred[:,:,3]-1.5*pred[:,:,0]-.3*pred[:,:,1]
        out['controls'][m]=ranking(utility,pred,k,m)
    model.save_model(str(ROOT/'R5_ORDERED_INTENSITY_JULY_WITHHELD_model.txt'))
    return out

def train_two_stage(data):
    """Explicitly separate opportunity and direction with independent heads."""
    train=('01','02','06')
    full={m:features(*data[m][:3],data[m][4],'ordered') for m in MONTHS}
    x=[];y=[];xd=[];yd=[]
    for m in train:
        k=data[m][3];n=len(k)
        x.append(full[m][:n,:-1]) # as-of only, no direction indicator
        anystrong=(k==3).any(axis=1).astype(np.int32)
        y.append(anystrong)
        good=np.flatnonzero(anystrong)
        xd.append(full[m][:n,:-1][good])
        yd.append((k[good,1]==3).astype(np.int32))
        if np.any((k[good,0]==3) & (k[good,1]==3)):raise AssertionError('both sides strong')
    x=np.vstack(x);y=np.concatenate(y);xd=np.vstack(xd);yd=np.concatenate(yd)
    args={'objective':'binary','learning_rate':.055,'num_leaves':31,'min_data_in_leaf':25,
          'num_threads':4,'verbosity':-1,'deterministic':True,'force_col_wise':True,'seed':20261102}
    m_op=lgb.train(args,lgb.Dataset(x,label=y),num_boost_round=150)
    m_dir=lgb.train(args,lgb.Dataset(xd,label=yd),num_boost_round=100)
    m_op.save_model(str(ROOT/'R5_OPPORTUNITY_JULY_WITHHELD_model.txt'))
    m_dir.save_model(str(ROOT/'R5_DIRECTION_IF_STRONG_JULY_WITHHELD_model.txt'))
    out={'method':'two-stage causal opportunity -> direction; no future labels in features',
         'train_months':list(train),'train_strong_market_states':int(len(yd)),'eval':{}}
    for m in MONTHS:
        k=data[m][3];n=len(k);x=full[m][:n,:-1];pany=m_op.predict(x);psell=m_dir.predict(x)
        sidescores=np.column_stack((pany*(1-psell),pany*psell))
        out['eval'][m]={'top_rankings':ranking(sidescores,None,k,m),
             'oracle_qualified_any_strong_rate':float((k==3).any(axis=1).mean()),
             'p_any_99pct':float(np.quantile(pany,.99))}
    return out

def _shuffle_control(data,coefs,seed=8804):
    """Within UTC hour shuffle past causal mark states; keep market-season intensity."""
    rng=np.random.default_rng(seed);checks={}
    for m in ('06','07'):
        with np.load(ROOT/f'R5_MARK_1SEC_{m}.npz') as d:
            x=d['X'];y=d['Y'];ts=d['ts']
        group=ts//3600000
        xs=x.copy()
        for hour in np.unique(group):
            ix=np.flatnonzero(group==hour)
            xs[ix]=x[rng.permutation(ix)]
        original=diagnostics(y,predict(x,coefs))
        shuffled=diagnostics(y,predict(xs,coefs))
        checks[m]={'original_poisson_nll':original['mean_poisson_nll'],
                    'hour_preserved_shuffled_nll':shuffled['mean_poisson_nll'],
                    'within_hour_history_value':shuffled['mean_poisson_nll']-original['mean_poisson_nll']}
    return checks

def run():
    from fitted_quote_excitation import fit_poisson
    allfour=load()
    with np.load(ROOT/'R5_MARK_1SEC_01.npz') as a,np.load(ROOT/'R5_MARK_1SEC_02.npz') as b:
        x=np.vstack((a['X'],b['X']));y=np.vstack((a['Y'],b['Y']))
    coeff=fit_poisson(x,y,'cross')
    shuffled=_shuffle_control(allfour,coeff)
    for m in MONTHS:
        rates=predict(np.load(ROOT/f'R5_MARK_1SEC_{m}.npz')['X'],coeff).astype('float32')
        allfour[m]=enrich(allfour[m],rates)
    t0=time.monotonic();a=evaluate(allfour);print('R5 added rates July top 1%',a['controls']['07'][1],flush=True)
    b=train_two_stage(allfour);print('R5 factorized July top 1%',b['eval']['07']['top_rankings'][1],flush=True)
    report={'scope':'H1V2 R5 60k as-of raw quote geometry sampled; Jan Feb June July; no full on-policy',
            'scientific_status':'CAUSAL_JULY_WITHHELD_RESEARCH_ONLY_NO_APPROVED_ENTRY_POLICY',
            'fitted_quote_mark_likelihood_shuffled_control':shuffled,
            'ordered_plus_fitted_intensity':a,'factorized_opportunity_direction':b,
            'elapsed_seconds':round(time.monotonic()-t0,2),
            'warning':'Fitted next-1s quote mark intensity is NOT a correct-trade classifier, and all four months may be trained deliberately only as in-sample teacher, not validated foresight.'}
    (ROOT/'R5_STRICT_ACTION_REJECTION_COMPARISON.json').write_text(json.dumps(report,indent=2))
    return report
if __name__=='__main__':run()
