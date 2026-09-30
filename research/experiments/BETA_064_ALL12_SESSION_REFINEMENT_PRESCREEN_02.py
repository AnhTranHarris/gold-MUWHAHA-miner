import pandas as pd, numpy as np, warnings
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')
ROOT=Path('/mnt/data'); MONTHS=list(range(1,8))
TARGETS=['E5_VWAP_RECLAIM','E7_SWEEP_RECLAIM','E10_COMPRESSION_RELEASE','E12_FAILED_EXPANSION']
FEATURES=['spread','atr60','atr300','atr900','tick_z','friction','eff15','eff30','eff60','eff300','eff900','eff3600','eff14400','compression','s_r15','s_r30','s_r60','s_r300','s_r900','s_r3600','s_r14400','s_v1n','s_v3n','s_v12n','s_a1n','s_a3n','s_j1n','s_j3n','s_body','s_qp','s_qv','s_vwap15_z','rel_open']
QS=[.90,.93,.95,.97,.98,.985,.99,.993,.995,.997,.998,.999,.9995]

def Xof(d): return d[FEATURES].replace([np.inf,-np.inf],np.nan).fillna(0).astype('float32')
def sched(z):
 if z.empty:return z
 z=z.sort_values(['time','quality'],ascending=[True,False]).drop_duplicates(['time','side','specialist','session'])
 keep=[];busy=-10**30
 for i,r in z.iterrows():
  tm=r.time.value//1_000_000
  if tm>=busy:keep.append(i);busy=tm+int(r.horizon)*1000
 return z.loc[keep]
def choose(tr):
 for th in sorted(np.unique(np.quantile(tr.quality,QS))):
  ok=True; total=0; mn=1; net=0
  for m in sorted(tr.month.unique()):
   z=sched(tr[(tr.month==m)&(tr.quality>=th)])
   if len(z)<3 or z.survive.mean()<.85 or z.resolved_pnl.sum()<=0: ok=False; break
   total+=len(z);mn=min(mn,z.survive.mean());net+=z.resolved_pnl.sum()
  if ok:return th,total,mn,net
 return None

df=pd.concat([pd.read_pickle(ROOT/f'beta064_all12_pass1_{m:02d}.pkl') for m in MONTHS],ignore_index=True);df['time']=pd.to_datetime(df.time,utc=True)
rows=[]
for sp in TARGETS:
 for sess in ['AUSTRALIA','ASIA','MIDEAST','EUROPE','UK','NY']:
  ds=df[(df.specialist==sp)&(df.session==sess)].copy()
  if len(ds)<150: continue
  print('\n',sp,sess,'raw',len(ds),'surv',round(ds.survive.mean(),3),flush=True)
  for h in MONTHS:
   tr=ds[ds.month!=h].copy();te=ds[ds.month==h].copy()
   if len(te)<10 or min(tr.survive.nunique(),tr.fp_win.nunique())<2:
    rows.append(dict(specialist=sp,session=sess,heldout=h,status='INSUFFICIENT'));continue
   ms=LGBMClassifier(n_estimators=80,num_leaves=12,learning_rate=.04,subsample=.8,colsample_bytree=.8,reg_lambda=8,min_child_samples=60,verbosity=-1,n_jobs=4)
   mf=LGBMClassifier(n_estimators=80,num_leaves=12,learning_rate=.04,subsample=.8,colsample_bytree=.8,reg_lambda=8,min_child_samples=60,verbosity=-1,n_jobs=4)
   ms.fit(Xof(tr),tr.survive.astype(int));mf.fit(Xof(tr),tr.fp_win.astype(int))
   tr['ps']=ms.predict_proba(Xof(tr))[:,1];tr['pf']=mf.predict_proba(Xof(tr))[:,1];tr['quality']=tr.ps*tr.pf
   te['ps']=ms.predict_proba(Xof(te))[:,1];te['pf']=mf.predict_proba(Xof(te))[:,1];te['quality']=te.ps*te.pf
   auc=roc_auc_score(te.survive,te.ps) if te.survive.nunique()>1 else np.nan
   ch=choose(tr)
   if ch is None:
    rows.append(dict(specialist=sp,session=sess,heldout=h,status='NO_6MONTH_GATE',auc=auc));continue
   th,tn,tmin,tnet=ch;z=sched(te[te.quality>=th]);n=len(z);sv=z.survive.mean() if n else np.nan;fp=z.fp_win.mean() if n else np.nan;net=z.resolved_pnl.sum() if n else 0
   pas=bool(n>=3 and sv>=.85 and net>0)
   rows.append(dict(specialist=sp,session=sess,heldout=h,status='GATED',auc=auc,quality_gate=th,train_n=tn,train_min_surv=tmin,train_net=tnet,test_n=n,test_surv=sv,test_fp=fp,test_net=net,test_pass=pas))
   print(' fold',h,'train',tn,round(tmin,3),'test',n,round(sv,3) if n else None,round(net,2),'PASS' if pas else 'FAIL',flush=True)
out=pd.DataFrame(rows);out.to_csv(ROOT/'BETA064_SESSION_REFINEMENT_PASS2_LOMO.csv',index=False)
s=[]
for (sp,se),g in out.groupby(['specialist','session']):
 gg=g[g.status=='GATED']; n=int(gg.test_n.fillna(0).sum()) if len(gg) else 0
 sv=(np.average(gg.test_surv.dropna(),weights=gg.loc[gg.test_surv.notna(),'test_n']) if len(gg) and gg.loc[gg.test_surv.notna(),'test_n'].sum()>0 else np.nan)
 s.append(dict(specialist=sp,session=se,folds_gated=len(gg),heldout_passes=int(gg.test_pass.fillna(False).sum()) if len(gg) else 0,heldout_n=n,heldout_weighted_surv=sv,heldout_net=gg.test_net.sum() if len(gg) else 0))
sm=pd.DataFrame(s).sort_values(['heldout_passes','heldout_n'],ascending=False);sm.to_csv(ROOT/'BETA064_SESSION_REFINEMENT_PASS2_SUMMARY.csv',index=False);print('\n',sm.to_string(index=False))
