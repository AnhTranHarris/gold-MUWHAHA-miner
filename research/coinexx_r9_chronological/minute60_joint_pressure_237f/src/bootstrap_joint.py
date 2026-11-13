"""Efficient exact weighted ROC-AUC paired calendar-day resampling (descriptive).
No future-feature information, no model retraining or threshold search.
"""
import sys,json,io,zipfile
from pathlib import Path
import numpy as np,joblib
from sklearn.metrics import roc_auc_score
sys.path.insert(0,'/mnt/data/r9_m60_joint_20261113/src')
from train_joint import ROOT,read_month

class WeightedAUC:
    def __init__(self,y,p,day_index):
        order=np.argsort(p,kind='mergesort')
        self.y=y[order].astype('f8')
        self.day=day_index[order]
        self.start=np.r_[0,1+np.flatnonzero(np.diff(p[order])!=0)]
    def evaluate(self,daycounts):
        w=daycounts[self.day].astype('f8')
        pos=w*self.y;neg=w*(1.-self.y)
        P=pos.sum();N=neg.sum()
        if P<=0 or N<=0:return np.nan
        pp=np.add.reduceat(pos,self.start)
        nn=np.add.reduceat(neg,self.start)
        return float(np.dot(pp,np.cumsum(nn)-nn+.5*nn)/(P*N))

def sample_scores(mm):
    r=read_month(mm)
    ix=2*np.arange(r['n_entries'])+(r['r9_side']<0)
    good=r['good'][ix];days=r['entry_ms'][good]//86400000;y=r['y'][ix][good]
    unique,ixday=np.unique(days,return_inverse=True)
    with zipfile.ZipFile('/mnt/data/R9_M60_JanSep_FullTraining_155Features_20261113.zip') as z:
        obj=joblib.load(io.BytesIO(z.read(f'models/direct_test_{mm}_shadow.joblib')))
    baseline=obj['model'].predict_proba(r['base'])[:,1][ix][good]
    capacity=np.load(ROOT/'results'/f'pred_{mm}_capacity_182.npy')[ix][good]
    joint=np.load(ROOT/'results'/f'pred_{mm}_synergy_joint.npy')[ix][good]
    specialist=np.load(ROOT/'results'/f'pred_{mm}_original_side_specialist.npy')[ix][good]
    scores={
      'frozen_155':baseline,
      'capacity_182':capacity,
      'joint':joint,
      'specialist':specialist,
      'fixed_joint_specialist':.5*joint+.5*specialist,
      'fixed_frozen_joint':.5*baseline+.5*joint,
    }
    caches={key:WeightedAUC(y,p,ixday) for key,p in scores.items()}
    for name,prep in caches.items():
        a=prep.evaluate(np.ones(len(unique)))
        exact=roc_auc_score(y,scores[name])
        if abs(a-exact)>1e-10:raise RuntimeError(f'Weighted AUC tie handling disagree {mm} {name} {a} {exact}')
    return len(unique),caches

rows=[sample_scores(mm) for mm in ['05','06','07','08','09']]
rng=np.random.default_rng(20261113)
reps=220
pairs=[('joint','frozen_155'),('joint','capacity_182'),('specialist','frozen_155'),('fixed_joint_specialist','frozen_155'),('fixed_frozen_joint','frozen_155')]
deltas={f'{a}_vs_{b}':[] for a,b in pairs}
for rep in range(reps):
    vals={k:[] for k in deltas}
    for ndays,caches in rows:
        daycounts=np.bincount(rng.choice(ndays,size=ndays,replace=True),minlength=ndays)
        aucs={name:cache.evaluate(daycounts) for name,cache in caches.items()}
        if any(not np.isfinite(q) for q in aucs.values()):continue
        for a,b in pairs:vals[f'{a}_vs_{b}'].append(aucs[a]-aucs[b])
    if all(len(z)==5 for z in vals.values()):
        for name,z in vals.items():deltas[name].append(float(np.mean(z)))
report={}
for name,values in deltas.items():
 a=np.array(values)
 report[name]={'mean_delta':float(np.mean(a)),
   'descriptive_95_interval':[float(np.quantile(a,.025)),float(np.quantile(a,.975))],
   'resamples':len(a)}
output={'status':'RETROSPECTIVE_PRIOR_EXPOSED_DAY_CLUSTER_DESCRIPTIVE_NOT_PROSPECTIVE',
        'method':'paired calendar-day block bootstrap; exact weighted AUC with tie groups; five-month mean AUC deltas',
        'pairs':report}
(ROOT/'results'/'DESCRIPTIVE_UNCERTAINTY.json').write_text(json.dumps(output,indent=2)+'\n')
print('DAY_BLOCK_BOOTSTRAP',json.dumps(report,indent=2),flush=True)
