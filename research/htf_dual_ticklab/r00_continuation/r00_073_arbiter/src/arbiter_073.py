"""R00-073 original-source conditioned initial entry-direction arbiter.

Reuses ORIGINAL signed-as-of native quote caches and broker-specific R00-068
February-frozen candidate. May not replace or rewrite R00-067 loader or baseline.
All nonneutral labels used for fitting only AFTER month January finishes.
"""
from __future__ import annotations
import sys, json, hashlib, time
from pathlib import Path
import numpy as np, pandas as pd, joblib
from lightgbm import LGBMClassifier
from importlib.machinery import SourceFileLoader
ROOT=Path(__file__).resolve().parents[2];HOME=ROOT/'r00_073_arbiter'
M=HOME/'models';O=HOME/'results';R70=ROOT/'r00_070_experiment';R69=ROOT/'r00_069'
R72=SourceFileLoader('original_r00_072',str(ROOT/'r00_072_episode/src/episode_072.py')).load_module()
R68=SourceFileLoader('original_r00_068',str(ROOT/'r00_068/src/entry_orchestra_068.py')).load_module()
BROKERS=('coinexx','dukascopy')


def dataset(b,m):
    if m=='01':
        with np.load(ROOT/f'r00_072_episode/results/EPISODES_{b}_01.npz') as z:
            t=z['ts_ms'].copy();j=z['quote_index'].copy();y=z['y'].copy();base=z['reference_side'].copy();emit=z['emitted_side'].copy();stage=z['expert_stage'].copy()
    else:
        with np.load(R70/f'results/score_{m}_{b}_R00_068_FEB_protected_reference.npz') as z:
            t=z['ts_ms'].copy();j=z['quote_index'].copy();y=z['y'].copy();base=z['side'].copy()
        with np.load(R70/f'features/structural_{b}_{m}.npz') as z:
            assert np.array_equal(t,z['ts_ms']) and np.array_equal(j,z['quote_index'])
            observed=z['expert_observed'].copy()
        emit,stage,_=R72.episodes(t,observed,R72.AGE,R72.COOL)
    # Unmodified R00-067 original event cache: all 95 features available at source quote-index.
    with np.load(ROOT/f'runs/native_relabel/corrected_{b}_{m}.npz') as z:
        assert np.array_equal(t,z['ts_ms']) and np.array_equal(j,z['quote_index'])
        orig=z['feature'].astype(np.float32)
    with np.load(R69/f'features/path_{b}_{m}.npz') as z:
        assert np.array_equal(t,z['ts_ms']) and np.array_equal(j,z['quote_index'])
        q=z['feature'].astype(np.float32)
    with np.load(R70/f'features/structural_{b}_{m}.npz') as z:
        assert np.array_equal(t,z['ts_ms']) and np.array_equal(j,z['quote_index'])
        struct=z['structure'].copy().astype(np.float32);expert=z['expert_observed'].copy()
    second=(t//1000)%86400
    phase=(second/86400)*2*np.pi
    age=np.diff(t,prepend=t[0]).astype(np.float32);age=np.minimum(age,60000)/1000
    # No use of future observations; no label values or y passed as features.
    X=np.column_stack([orig,q,struct,expert.astype(np.float32),emit.astype(np.float32),stage.astype(np.float32),base.astype(np.float32),np.sin(phase),np.cos(phase),np.clip(age,0,60)]).astype(np.float32)
    assert X.shape[0]==len(t) and len(t)==len(y) and np.all(np.diff(j)>=0)
    # Account for inherently missing pivot fields without inventing completion.
    X[np.isinf(X)]=np.nan
    return {'X':X,'t':t,'j':j,'y':y,'base':base,'emit':emit,'stage':stage,'expert':expert,'struct':struct,'q':q}


def clf(seed,nleaf=15,ntrees=32,tri=False):
    return LGBMClassifier(n_estimators=ntrees,num_leaves=nleaf,min_child_samples=180,
     learning_rate=.045,reg_alpha=.5,reg_lambda=10.,colsample_bytree=.8,
     subsample=.85,subsample_freq=2,max_bin=63,n_jobs=2,verbosity=-1,random_state=seed)


def train(b):
    D=dataset(b,'01');X,y,base=D['X'],D['y'],D['base']; valid=y!=0
    models={};train_counts={'events':len(y),'nonneutral':int(valid.sum()),'shape':list(X.shape)}
    # Fixed stratified-on-time index sample in January, avoids unbounded model fit.
    # Evaluation remains on ALL original events in every test month.
    rng=np.random.default_rng(20261018)
    for name,seed,fit_y,sel,leaves in [
      ('binary',7301,(y[valid]==1).astype(np.uint8),valid,15),
      ('binary_deep',7302,(y[valid]==1).astype(np.uint8),valid,23),
      ('ternary',7303,(y+1).astype(np.uint8),np.ones(len(y),dtype=bool),15),
      ('flip',7304,((y[valid]==base[valid])).astype(np.uint8),valid,15),
    ]:
        c=clf(seed,nleaf=leaves,tri=name=='ternary')
        idx=np.flatnonzero(sel)
        if len(idx)>35000: idx=np.sort(rng.choice(idx,35000,replace=False))
        # original fit_y is aligned to every sel-true row, not full original.
        orig_sel=np.flatnonzero(sel)
        pos=np.searchsorted(orig_sel,idx)
        c.fit(X[idx],fit_y[pos])
        models[name]=c
        ck=M/f'R00_073_PARTIAL_{b}.joblib';joblib.dump(models,ck,compress=3)
        print('trained',b,name,'examples',len(idx),flush=True)
    model_file=M/f'R00_073_JAN_{b}_FOUR_MODELS.joblib';joblib.dump(models,model_file,compress=3)
    digest=hashlib.sha256(model_file.read_bytes()).hexdigest();train_counts['sha256']=digest
    (M/f'R00_073_JAN_{b}_RECEIPT.json').write_text(json.dumps(train_counts,indent=2))
    return models


def infer(b,m):
    D=dataset(b,m);X=D['X'];models=joblib.load(M/f'R00_073_JAN_{b}_FOUR_MODELS.joblib')
    binary=2*models['binary'].predict_proba(X)[:,1]-1
    deep=2*models['binary_deep'].predict_proba(X)[:,1]-1
    tprob=models['ternary'].predict_proba(X)
    ci={int(c):i for i,c in enumerate(models['ternary'].classes_)}
    ternary=tprob[:,ci[2]]-tprob[:,ci[0]]
    flip=models['flip'].predict_proba(X)[:,1]
    base=D['base'];e=D['emit'];stage=D['stage'];expert=D['expert'];struct=D['struct']
    # likelihood of present base direction conditional on nonneutral 30s outcome; 50% neutral irreducible.
    residual=np.where(flip>=.5,base,-base)
    # noncausal label-free inputs: expert evidence, observed topology and own independent lifecycle.
    obs=np.sum(expert,axis=1); emits=np.sum(e,axis=1)
    # selectively trust an expert only when all observed expert signs AND 30s forecaster agree.
    same=np.sign(emits)==np.sign(binary)
    sig_strength=np.abs(emits)
    tri_sign=np.where(ternary>=0,1,-1)
    native_conf=np.abs(binary)
    # all policies return -1/+1; never remove an event, even if neutral.
    sign=lambda s: np.where(s>=0,1,-1).astype(np.int8)
    preds={
      'A_protected_068':base,
      'B_binary_Jan_native':sign(binary),
      'C_binary_deep':sign(deep),
      'D_ternary':sign(ternary),
      'E_base_flip_metaclass':residual.astype(np.int8),
      'F_blend_binary_ternary':sign(.5*binary+.5*ternary),
      'G_binary_deep_blend':sign(.5*binary+.5*deep),
      'H_3model_ensemble':sign(.40*binary+.30*deep+.30*ternary),
      'I_base_protected_75':np.where(np.abs(binary)>.75,sign(binary),base),
      'J_base_protected_60':np.where(np.abs(binary)>.60,sign(binary),base),
      'K_base_protected_45':np.where(np.abs(binary)>.45,sign(binary),base),
      'L_residual_reliability_60':np.where(flip<.40,-base,base).astype(np.int8),
      'M_residual_reliability_75':np.where(flip<.25,-base,base).astype(np.int8),
      'N_ensemble_specialist_confirmation':np.where((sig_strength>=1)&same&(native_conf>.25),sign(binary),base),
      'O_ensemble_expert_conflict':np.where((sig_strength==0)&(np.abs(obs)<=1),sign(.5*binary+.5*ternary),base),
      'P_ensemble_structural_pivot_50':np.where((np.abs(struct[:,7])+np.abs(struct[:,24])>0)&(native_conf>.5),sign(binary),base),
      'Q_protected_deep_conf_30':np.where((np.sign(deep)==np.sign(binary))&(np.abs(binary)>.30),sign(.5*binary+.5*deep),base),
      'R_4head_disagreement_base':np.where((np.sign(binary)==np.sign(ternary))&(np.sign(deep)==np.sign(binary))&(np.sign(binary)!=np.sign(base)),sign(binary),base),
    }
    assert all(np.isin(v,[-1,1]).all() and len(v)==len(base) for v in preds.values())
    score={n:int(((p==D['y'])&(D['y']!=0)).sum()) for n,p in preds.items()}
    O.mkdir(exist_ok=True,parents=True)
    rows=[{'broker':b,'month':m,'policy':n,'events':len(D['y']),'correct':s,'BUY':int((preds[n]==1).sum()),'SELL':int((preds[n]==-1).sum())} for n,s in score.items()]
    pd.DataFrame(rows).to_csv(O/f'ALL_POLICIES_{b}_{m}.csv',index=False)
    # Save all event-level outputs for COMPLETE reproducibility and later paired analysis.
    np.savez_compressed(O/f'ALL_DIRECTIONS_{b}_{m}.npz',ts_ms=D['t'],quote_index=D['j'],y=D['y'],reference_side=base,
     **{k:preds[k] for k in preds},binary_score=binary.astype(np.float32),deep_score=deep.astype(np.float32),ternary_score=ternary.astype(np.float32),
     predicted_base_reliability=flip.astype(np.float32),expert_emissions=e,expert_stage=stage)
    print('SCORED',b,m,'control',score['A_protected_068'],'best',sorted(score.items(),key=lambda x:-x[1])[:3],flush=True)


def freeze():
    rows=pd.concat([pd.read_csv(O/f'ALL_POLICIES_{b}_02.csv') for b in BROKERS]); s=rows.groupby('policy').agg(correct=('correct','sum'),events=('events','sum')).sort_values(['correct','policy'],ascending=[False,True]);
    w=str(s.index[0]);q={'policy':w,'correct':int(s.iloc[0].correct),'events':int(s.iloc[0].events),'frozen_on':'2026-02','evaluation':'strict R00-067 original +30s labels, 2s max freshness, neutral wrong','transfer_not_used_for_choice':True}
    (O/'FROZEN_FEB_073.json').write_text(json.dumps(q,indent=2));s.to_csv(O/'FEB_COMBINED_ALL_POLICIES.csv');print('FROZEN FEB',q,flush=True)


def transfer():
    w=json.loads((O/'FROZEN_FEB_073.json').read_text())['policy']
    df=pd.concat([pd.read_csv(O/f'ALL_POLICIES_{b}_{m}.csv') for b in BROKERS for m in ['06','07']]); group=df.groupby('policy').agg(correct=('correct','sum'),events=('events','sum'));group['accuracy']=group.correct/group.events;group.sort_values('correct',ascending=False).to_csv(O/'TRANSFER_ALL_POLICIES_AGGREGATE_073.csv')
    old=group.loc['A_protected_068'];new=group.loc[w];
    print('FROZEN TRANSFER',w,new.to_dict(),'CONTROL',old.to_dict(),flush=True)
    (O/'TRANSFER_FROZEN_RECEIPT.json').write_text(json.dumps({'selection':'FEB_FROZEN_073.json','winner':w,'correct':int(new.correct),'events':int(new.events),'accuracy':float(new.accuracy),'protected_068_correct':int(old.correct),'delta_correct':int(new.correct-old.correct),'test_period':'2026-06/07 historically exposed; not blind'},indent=2))

if __name__=='__main__':
    action=sys.argv[1];
    if action=='train':train(sys.argv[2])
    elif action=='score':infer(sys.argv[2],sys.argv[3])
    elif action=='freeze':freeze()
    elif action=='transfer':transfer()
