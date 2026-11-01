"""F401-R150 Stage 1: new R120 regime information, not score retuning.

Research-exposed Dukascopy-only diagnostic. Uses frozen J2/L2/M2 scores,
source-indexed R120 state fit unsupervised on January first 60%, no runtime
truth/teacher. FIT Jan last 40%, CAL February, transfer June/July unchanged.
No independent pending-intent proof in source tapes => NO execution claim.
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score

MONTHS=('01','02','06','07'); HEADS=('guardian','opposite','neutral')

def build_cell(m,stage,atlas,original):
    with np.load(stage/f'dukascopy_{m}.npz',allow_pickle=False) as z:
        d={k:z[k] for k in z.files}
    with zipfile.ZipFile(original) as z:
        with np.load(io.BytesIO(z.read(f'F395_S14_dukascopy_{m}_FROZEN_ORIGINAL_EVENT_MASK.npz'))) as o:
            assert np.array_equal(d['t'],o['t']) and np.array_equal(d['side'],o['side']) and np.array_equal(d['truth'],o['truth'])
            assert np.array_equal(d['ordinal'],o['original_index'])
    with zipfile.ZipFile(atlas) as z:
        phase=np.load(io.BytesIO(z.read(f'R120_{m}_UNSUPERVISED_PHASES.npy')))
        state=np.load(io.BytesIO(z.read(f'R120_{m}_TENSOR_PHASES.npy')))
    n=len(d['t']);assert phase.shape==state.shape==(n,)
    fam=np.column_stack([d[f'{f}_{h}'] for f in ('J2','L2','M2') for h in HEADS]).astype('float32')
    # R120 native geometry state is source-time published at t0; can inform
    # T1 without looking into its future. Do NOT include its retrospective
    # original-label risk census or state risk rates in runtime input.
    hr=((d['t']//3_600_000)%24).astype(np.float32)
    raw=np.column_stack([fam,np.std(fam.reshape(-1,3,3),axis=1),d['side'],
                         np.sin(2*np.pi*hr/24),np.cos(2*np.pi*hr/24)]).astype(np.float32)
    # Category IDs are not ordinal market quantities: pass as categorical.
    advanced=np.column_stack([raw,phase.astype(np.float32),state.astype(np.float32)])
    return d,raw,advanced

def train(x,y,seed,categories):
    params=dict(objective='binary',n_estimators=170,learning_rate=.045,num_leaves=47,
                min_child_samples=180,reg_lambda=14.0,feature_fraction=.85,
                n_jobs=2,verbosity=-1,random_state=seed)
    model=LGBMClassifier(**params)
    model.fit(x,y,categorical_feature=categories if categories else 'auto')
    return model

def cuts(a,s,correct_budget=.006):
    # Empirical February-only calibration; thresholds are frozen for June/July.
    y=a['truth'];valid=a['valid'];side=a['side'];session=(((a['t']//3600000)%24)>=13)&(((a['t']//3600000)%24)<15)
    out={}
    for sd in (-1,1):
      for ss in (False,True):
        q=valid&(side==sd)&(session==ss)&(y==0)
        if q.sum()<100:continue
        co=float(np.quantile(s['opposite'][q],1-correct_budget*.65,method='higher'))
        cn=float(np.quantile(s['neutral'][q],1-correct_budget*.35,method='higher'))
        out[(sd,ss)]=(co,cn)
    return out

def mask(a,s,c):
    valid=a['valid'];session=(((a['t']//3600000)%24)>=13)&(((a['t']//3600000)%24)<15)
    z=np.zeros(len(valid),bool)
    for (sd,ss),(co,cn) in c.items():
      z|=valid&(a['side']==sd)&(session==ss)&(s['guardian']<.80)&((s['opposite']>co)|(s['neutral']>cn))
    return z

def grade(a,s,c):
    v=mask(a,s,c);y=a['truth'];q=a['valid'];return {
        'correct_lost':int((v&(y==0)).sum()),'opposite_veto':int((v&(y==1)).sum()),
        'neutral_veto':int((v&(y==2)).sum()),'bad_veto':int((v&(y!=0)).sum()),
        'abstain':int((~q).sum()),
        'auc_opposite':float(roc_auc_score(y[q]==1,s['opposite'][q])),
        'auc_neutral':float(roc_auc_score(y[q]==2,s['neutral'][q]))}

def run(args):
    data={m:build_cell(m,args.stage,args.atlas,args.original) for m in MONTHS}
    # The unsupervised R120 codebook was trained Jan first 60%, so use
    # only the latter Jan 40% for supervised classhead fitting.
    start=int(.60*len(data['01'][0]['truth']));fits={};summary={}
    for version in ('scores_control','r120_regime'):
        col=1 if version=='scores_control' else 2
        x=data['01'][col]; a=data['01'][0];v=a['valid'].copy();v[:start]=False
        models={}
        for h,yval in [('guardian',0),('opposite',1),('neutral',2)]:
            model=train(x[v],(a['truth'][v]==yval).astype(np.int8),seed=105+len(h),categories=[15,16] if col==2 else [])
            models[h]=model
        ss={m:{h:models[h].predict_proba(data[m][col])[:,1].astype(np.float32) for h in HEADS} for m in MONTHS}
        cal=cuts(data['02'][0],ss['02']);summary[version]={'counts':{m:grade(data[m][0],ss[m],cal) for m in MONTHS},
                'fit_rows':int(v.sum()),'calibration':'February only, 0.6% nominal correct per side/session',
                'cal_groups':len(cal),'features':int(x.shape[1])}
        if args.save_models:
            import joblib
            for h,model in models.items():joblib.dump(model,args.save_models/f'{version}_{h}.joblib',compress=3)
            for m in MONTHS:
                np.savez_compressed(args.save_models/f'{version}_{m}_SCORES.npz',**ss[m])
                np.savez_compressed(args.save_models/f'{version}_{m}_SHADOW.npz',mask=mask(data[m][0],ss[m],cal))
    for m in MONTHS:
        b=summary['scores_control']['counts'][m];c=summary['r120_regime']['counts'][m];summary.setdefault('incremental',{})[m]={
            'bad_delta':c['bad_veto']-b['bad_veto'],
            'correct_lost_delta':c['correct_lost']-b['correct_lost'],
            'neutral_delta':c['neutral_veto']-b['neutral_veto'],
            'opposite_delta':c['opposite_veto']-b['opposite_veto'],
            'neutral_auc_delta':c['auc_neutral']-b['auc_neutral'],
            'opposite_auc_delta':c['auc_opposite']-b['auc_opposite']}
    summary['status']='RESEARCH_ONLY_EXPOSED_NOT_T1_EXECUTION_VERIFIED'
    summary['source']='Dukascopy four original broker-month arrays; frozen F395 event identity'
    summary['strongest_r150q_checkpoint']='234507 BAD / 9639 CORRECT, full 8-cell (not this DK-only experiment)'
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(summary,indent=2))
    print(json.dumps({'incremental':summary['incremental'],'report':str(args.report)},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,default=Path('/mnt/data/r150_lean_candidate/staged'))
 p.add_argument('--atlas',type=Path,default=Path('/mnt/data/XAUUSD_F401_R120_MULTICLOCK_HTF_SESSION_GRID_CAUSAL_RESEARCH_UNAPPROVED_20261028.zip'))
 p.add_argument('--original',type=Path,default=Path('/mnt/data/F395_S14_OWNER_APPROVED_RESEARCH_ONLY_FULL_AUGUST_TRANSFER_UNVERIFIED_20261025.zip'))
 p.add_argument('--save-models',type=Path,default=Path('/mnt/data/r150_repair_advanced/models'))
 p.add_argument('--report',type=Path,default=Path('/mnt/data/r150_repair_advanced/receipts/DK_R120_CONDITIONAL_RESEARCH.json'))
 args=p.parse_args();args.save_models.mkdir(parents=True,exist_ok=True);run(args)
