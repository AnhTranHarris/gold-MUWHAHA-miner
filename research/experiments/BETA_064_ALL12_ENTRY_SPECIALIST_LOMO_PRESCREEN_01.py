import pandas as pd, numpy as np, json, warnings
from pathlib import Path
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score
warnings.filterwarnings('ignore')
ROOT=Path('/mnt/data'); MONTHS=list(range(1,8))
FEATURES=['spread','atr60','atr300','atr900','tick_z','friction','eff15','eff30','eff60','eff300','eff900','eff3600','eff14400','compression','s_r15','s_r30','s_r60','s_r300','s_r900','s_r3600','s_r14400','s_v1n','s_v3n','s_v12n','s_a1n','s_a3n','s_j1n','s_j3n','s_body','s_qp','s_qv','s_vwap15_z','rel_open']
QS=[.90,.94,.96,.975,.985,.99,.995,.998,.999]

def prepX(d):
 X=d[FEATURES].replace([np.inf,-np.inf],np.nan).fillna(0).astype('float32')
 for s in ['AUSTRALIA','ASIA','MIDEAST','EUROPE','UK','NY','GLOBAL']:X['sess_'+s]=(d.session.values==s).astype('int8')
 return X

def scheduled(z):
 if z.empty:return z
 z=z.sort_values(['time','quality'],ascending=[True,False]).drop_duplicates(['time','side','specialist'])
 keep=[];busy=-10**30
 for i,r in z.iterrows():
  tm=r.time.value//1_000_000
  if tm>=busy:keep.append(i);busy=tm+int(r.horizon)*1000
 return z.loc[keep]

def met(z):
 return (len(z),float(z.survive.mean()) if len(z) else np.nan,float(z.fp_win.mean()) if len(z) else np.nan,float(z.resolved_pnl.sum()) if len(z) else 0.)

def choose(tr):
 vals=np.quantile(tr.quality,QS)
 for th in sorted(np.unique(vals)):
  ok=True; tot=0; nets=0.;mins=1.
  for m in sorted(tr.month.unique()):
   z=scheduled(tr[(tr.month==m)&(tr.quality>=th)])
   if len(z)<3 or z.survive.mean()<.85 or z.resolved_pnl.sum()<=0:ok=False;break
   tot+=len(z);nets+=z.resolved_pnl.sum();mins=min(mins,z.survive.mean())
  if ok:return float(th),tot,mins,nets
 return None

def main():
 df=pd.concat([pd.read_pickle(ROOT/f'beta064_all12_pass1_{m:02d}.pkl') for m in MONTHS],ignore_index=True);df['time']=pd.to_datetime(df.time,utc=True)
 rows=[];sels=[]
 for sp in sorted(df.specialist.unique()):
  ds=df[df.specialist==sp].copy();print('\n'+sp+' raw='+str(len(ds)),flush=True)
  for h in MONTHS:
   tr=ds[ds.month!=h].copy();te=ds[ds.month==h].copy()
   if len(tr)<100 or len(te)<10 or tr.survive.nunique()<2 or tr.fp_win.nunique()<2:
    rows.append({'specialist':sp,'heldout':h,'status':'INSUFFICIENT'});continue
   Xtr=prepX(tr);Xte=prepX(te)
   ms=LGBMClassifier(n_estimators=60,num_leaves=15,learning_rate=.05,subsample=.8,colsample_bytree=.8,reg_lambda=5,min_child_samples=100,verbosity=-1,n_jobs=4)
   mf=LGBMClassifier(n_estimators=60,num_leaves=15,learning_rate=.05,subsample=.8,colsample_bytree=.8,reg_lambda=5,min_child_samples=100,verbosity=-1,n_jobs=4)
   ms.fit(Xtr,tr.survive.astype(int));mf.fit(Xtr,tr.fp_win.astype(int))
   tr['p_surv']=ms.predict_proba(Xtr)[:,1];te['p_surv']=ms.predict_proba(Xte)[:,1]
   tr['p_fp']=mf.predict_proba(Xtr)[:,1];te['p_fp']=mf.predict_proba(Xte)[:,1]
   tr['quality']=tr.p_surv*tr.p_fp;te['quality']=te.p_surv*te.p_fp
   try:auc=float(roc_auc_score(te.survive,te.p_surv))
   except:auc=np.nan
   ch=choose(tr)
   if ch is None:
    rows.append({'specialist':sp,'heldout':h,'status':'NO_6MONTH_GATE','auc':auc});print(' fold',h,'NO GATE auc',round(auc,3),flush=True);continue
   th,tn,tmins,tnet=ch;z=scheduled(te[te.quality>=th]);n,su,fp,net=met(z)
   rows.append({'specialist':sp,'heldout':h,'status':'GATED','auc':auc,'quality_gate':th,'train_n':tn,'train_min_surv':tmins,'train_net':tnet,'test_n':n,'test_surv':su,'test_fp':fp,'test_net':net,'test_pass':bool(n>=3 and su>=.85 and net>0)})
   if len(z): z=z.copy();z['heldout']=h;z['gate']=th;sels.append(z)
   print(' fold',h,'auc',round(auc,3),'train',tn,round(tmins,3),round(tnet,2),'test',n,round(su,3) if n else None,round(net,2),'PASS' if n>=3 and su>=.85 and net>0 else 'FAIL',flush=True)
 out=pd.DataFrame(rows);out.to_csv(ROOT/'BETA064_ALL12_PASS1_FAST_LOMO.csv',index=False)
 sel=pd.concat(sels,ignore_index=True) if sels else pd.DataFrame();sel.to_pickle(ROOT/'BETA064_ALL12_PASS1_FAST_LOMO_SELECTED.pkl')
 print('\nSUMMARY')
 for sp,g in out.groupby('specialist'):
  gg=g[g.status=='GATED'];passes=int(gg.test_pass.fillna(False).sum()) if len(gg) else 0
  print(sp,'gated',len(gg),'passes',passes,'heldout_n',int(gg.test_n.fillna(0).sum()) if len(gg) else 0,'heldout_surv_weighted', (np.average(gg.test_surv.dropna(),weights=gg.loc[gg.test_surv.notna(),'test_n']) if len(gg[gg.test_surv.notna()]) and gg.loc[gg.test_surv.notna(),'test_n'].sum()>0 else np.nan),'net',gg.test_net.sum() if len(gg) else 0)
main()
