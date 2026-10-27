#!/usr/bin/env python3
"""R34 research-only: SOURCE-BROKER fit Jan/Feb, Jun calibration, OTHER broker Jul report.
EXPERIMENTAL right-rescue guardian on original R24 would-veto signals.
Even a withheld target broker here is NOT a fully blind broker: R24/R17 upstream
scorers already consumed BOTH brokers and ALL four months historically.
No current event truth is in X; labels used only for precommitted FIT/CAL scores.
"""
from __future__ import annotations
import pathlib,os,hashlib,json,math,time
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='2'
import numpy as np, lightgbm as lgb
from r34_eightcell_source_audit import load
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES={'COINEXX':'coinexx','DUKASCOPY':'dukascopy'}
RECIPES=[('G34_31_85',31,85,.060),('G34_63_105',63,105,.045),('G34_127_125',127,125,.040),('G34_255_95',255,95,.045)]
FEATURES=['original_r24_score','r17_opposite','r17_neutral','r17_right_guard',
 'direction_buy','delay_ms_15','hour_sin','hour_cos','week_sin','week_cos']

def load_features(broker,month,original):
    f=ROOT/f'F401_R17_{SOURCES[broker]}_{month}_NOVEL_COMPLETED_HTF_FROZEN_SCORES.npz'
    with np.load(f,allow_pickle=False) as z:
        assert np.array_equal(z['t'],original['t'])
        assert np.array_equal(z['side'],original['side'])
        assert np.array_equal(z['truth'],original['original_truth'])
        assert np.array_equal(z['valid'],original['valid'])
        t=original['t']; d=original['decision_t'];sec=t/1000.0;h=2*np.pi*(sec%86400)/86400.;w=2*np.pi*(sec%604800)/604800.
        x=np.column_stack([original['frozen_r24_score'],z['r17_opposite'],z['r17_neutral'],z['r17_right_guard'],
            (original['side']>0).astype(np.float32),(d-t-15000).clip(0,999),np.sin(h),np.cos(h),np.sin(w),np.cos(w)]).astype('float32')
        assert np.isfinite(x).all()
    return x

def fit_rows(cells,broker,months):
    xs=[];ys=[]
    for m in months:
        z=cells[(broker,m)];n=z['frozen_r24_veto'];X=load_features(broker,m,z)
        xs.append(X[n]);ys.append((z['original_truth'][n]==0).astype('int8'))
    return np.concatenate(xs),np.concatenate(ys)

def evaluate(mdl,threshold,cells,broker,month):
    c=cells[(broker,month)];p=c['frozen_r24_veto']; x=load_features(broker,month,c)
    idx=np.flatnonzero(p);ys=(c['original_truth'][idx]==0)
    scores=np.asarray(mdl.predict(x[idx],num_threads=2),dtype='float32')
    r=scores>=np.float32(threshold)
    right_rescue=int(np.sum(r&ys));bad_rescue=int(np.sum(r&~ys))
    return {'veto_candidate_bad':int(np.sum(~ys)),'veto_candidate_right':int(np.sum(ys)),
            'rescued_right':right_rescue,'rescued_bad':bad_rescue,
            'new_bad_veto':int(np.sum(~ys))-bad_rescue,'new_right_lost':int(np.sum(ys))-right_rescue,
            'rescue_precision':round(right_rescue/max(1,right_rescue+bad_rescue),6)}

def select_cut(model,cells,broker,month='06'):
    z=cells[(broker,month)];p=z['frozen_r24_veto'];x=load_features(broker,month,z);idx=np.flatnonzero(p);y=z['original_truth'][idx]==0
    ps=np.asarray(model.predict(x[idx],num_threads=2),dtype='float32')
    # fixed guardian cap: rescue no more than 2% of existing bad veto on
    # SOURCE-BROKER June calibration; maximize right rescue within this budget.
    bad_allow=int(np.floor(np.sum(~y)*.02))
    cuts=np.unique(np.r_[np.float32(1.000001),np.quantile(ps,np.linspace(.20,1.0,161)).astype('float32')])
    best=None
    for cut in cuts:
        s=ps>=cut;bad=int(np.count_nonzero(s&~y));right=int(np.count_nonzero(s&y))
        if bad>bad_allow:continue
        cand=(right,-bad,float(cut))
        if best is None or cand>best:best=cand
    assert best is not None
    return best[2],{'right_rescued':best[0],'bad_rescued':-best[1], 'bad_rescue_limit':bad_allow}

def run():
    cells=load(ROOT);out={'research_only':True,'month_fit':['01','02'],'month_cal':'06','month_transfer':'07',
      'upstream_fitted_both_brokers_and_all_four_months':True,'true_broker_blind':False,
      'data':'original frozen tick-derived R24 and R17 score/event arrays, NOT new full raw tick replay',
      'features':FEATURES,'fits':[]}
    for source in SOURCES:
        target=next(x for x in SOURCES if x!=source)
        X,Y=fit_rows(cells,source,('01','02'))
        print('ORIGINAL FIT SOURCE',source,'rows',len(Y),'right',int(Y.sum()),flush=True)
        candidates=[]
        for name,leaves,rounds,rate in RECIPES:
            params=dict(objective='binary',num_leaves=leaves,learning_rate=rate,min_data_in_leaf=40,
              lambda_l2=7,feature_fraction=.93,bagging_fraction=.9,bagging_freq=1,
              is_unbalance=True,max_bin=127,num_threads=2,verbosity=-1,seed=3400+leaves)
            t=time.monotonic()
            model=lgb.train(params,lgb.Dataset(X,label=Y,feature_name=FEATURES),num_boost_round=rounds)
            threshold,cal=select_cut(model,cells,source)
            candidates.append((cal['right_rescued'],-cal['bad_rescued'],name,threshold,cal,model))
            print('TRAIN',source,name,'threshold',round(threshold,6),'cal_rescue',cal,'time',round(time.monotonic()-t,1),flush=True)
        # Recipe picked STRICTLY on SOURCE June CAL, never target-broker July.
        winner=max(candidates,key=lambda a:(a[0],a[1],-a[3]))
        _,_,name,cut,cal,model=winner
        path=ROOT/f'R34_GUARD_{source}_FIT_JANFEB_CAL_JUN.txt';model.save_model(str(path))
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        result={'fit_broker':source,'excluded_target_broker':target,'selected_recipe':name,
          'weights_sha256':sha,'weight_file':path.name,'cal_cut':cut,'source_june_cal':cal,
          'source_july_recheck':evaluate(model,cut,cells,source,'07'),
          'other_broker_july_scored_without_target_model_fit_or_cut_selection':evaluate(model,cut,cells,target,'07')}
        out['fits'].append(result)
        print('FROZEN',json.dumps(result),flush=True)
    (ROOT/'R34_AUX_GUARD_CROSSBROKER_TRANSFER_PILOT.json').write_text(json.dumps(out,indent=2))
    return out
if __name__=='__main__':run()
