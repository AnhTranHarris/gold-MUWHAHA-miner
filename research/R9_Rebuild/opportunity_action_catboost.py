import pandas as pd, numpy as np, os, json
from catboost import CatBoostRegressor
ROOT='/mnt/data/r9_research_v2'; OUT=f'{ROOT}/screens'; os.makedirs(OUT,exist_ok=True)
actions=['cont_r9','fade_r9','cont_harv','fade_harv']; ycols=[a+'_pnl' for a in actions]
def load(months):
 d=pd.concat([pd.read_pickle(f'{ROOT}/events_{m:02d}.pkl.gz',compression='gzip') for m in months],ignore_index=True)
 ts=pd.to_datetime(d.time_ms,unit='ms',utc=True); mins=ts.dt.hour.to_numpy()*60+ts.dt.minute.to_numpy(); wd=ts.dt.dayofweek.to_numpy()
 d=d.copy(); d['tod_sin']=np.sin(2*np.pi*mins/1440); d['tod_cos']=np.cos(2*np.pi*mins/1440); d['dow_sin']=np.sin(2*np.pi*wd/7); d['dow_cos']=np.cos(2*np.pi*wd/7); return d
def featcols(d):
 bad={'month','time_ms','base_pnl','base_hold','base_mfe','base_mae'}
 for a in actions: bad|={a+'_pnl',a+'_mfe',a+'_mae'}
 return [c for c in d.columns if c not in bad]
def matrix(d,cols):
 X=d[cols].replace([np.inf,-np.inf],np.nan).copy(); med=X.median(numeric_only=True); return X.fillna(med).fillna(0)
def fit_one(X,y,seed=42):
 return CatBoostRegressor(iterations=260,depth=6,learning_rate=.045,l2_leaf_reg=8,loss_function='RMSE',random_seed=seed,verbose=False,thread_count=1,allow_writing_files=False).fit(X,y)
dev=load([1,2,3]); cols=featcols(dev); X=matrix(dev,cols); Y=dev[ycols].to_numpy(); opp=np.maximum(Y.max(axis=1),0).clip(0,3)
po=np.full(len(dev),np.nan); pa=np.full((len(dev),4),np.nan)
for holdm in [1,2,3]:
 tr=dev.month.to_numpy()!=holdm; te=~tr; mo=fit_one(X.loc[tr],opp[tr],100+holdm); po[te]=mo.predict(X.loc[te])
 for j in range(4): pa[te,j]=fit_one(X.loc[tr],np.clip(Y[tr,j],-3,3),200+holdm*10+j).predict(X.loc[te])
rows=[]
for q in [.5,.6,.7,.8,.85,.9,.925,.95,.975]:
 th=np.quantile(po,q); mask=po>=th; best=np.argmax(pa,axis=1); act=Y[np.arange(len(Y)),best]; z=act[mask]; mon=[]
 for m in [1,2,3]:
  mm=mask&(dev.month.to_numpy()==m); zz=Y[np.arange(len(Y))[mm],best[mm]]; mon.append(float(zz.sum()))
 rows.append({'q':q,'opp_thr':float(th),'n':int(mask.sum()),'net':float(z.sum()),'mean':float(z.mean()),'m1':mon[0],'m2':mon[1],'m3':mon[2]})
pd.DataFrame(rows).to_csv(f'{OUT}/catboost_oof_opportunity.csv',index=False); print('OOF OPPORTUNITY\n',pd.DataFrame(rows).to_string(index=False))
mo=fit_one(X,opp,500); mas=[fit_one(X,np.clip(Y[:,j],-3,3),600+j) for j in range(4)]
apr=load([4]); Xa=matrix(apr,cols); opa=mo.predict(Xa); paa=np.column_stack([m.predict(Xa) for m in mas]); Ya=apr[ycols].to_numpy()
qvals=[.5,.6,.7,.75,.8,.85,.875,.9,.925,.95,.96,.97,.98]; ath=[-.10,-.05,0,.025,.05,.075,.10,.15,.20,.25]; gr=[]
for q in qvals:
 ot=float(np.quantile(opa,q))
 for at in ath:
  best=np.argmax(paa,axis=1); mx=paa.max(axis=1); mask=(opa>=ot)&(mx>=at); z=Ya[np.arange(len(Ya))[mask],best[mask]]
  if len(z)<100: continue
  gp=z[z>0].sum(); gl=z[z<0].sum(); gr.append({'q':q,'opp_thr':ot,'act_thr':at,'n':len(z),'net':z.sum(),'mean':z.mean(),'pf':gp/(-gl) if gl<0 else 999,'win':(z>0).mean()})
grid=pd.DataFrame(gr).sort_values('net',ascending=False); grid.to_csv(f'{OUT}/catboost_april_grid.csv',index=False); print('\nAPRIL TOP\n',grid.head(40).to_string(index=False))
cand=None
for _,r in grid.iterrows():
 if r.net<=0 or r.pf<=1 or r.n<300: continue
 near=grid[(abs(grid.q-r.q)<=.0251)&(abs(grid.act_thr-r.act_thr)<=.0501)&(grid.n>=200)]
 if (near.net>0).sum()>=3: cand=r; break
if cand is None: print('NO APRIL ROBUST POSITIVE CANDIDATE'); json.dump({'status':'NO_CANDIDATE'},open(f'{OUT}/catboost_frozen_result.json','w')); raise SystemExit
print('\nSELECTED',cand.to_dict())
fw=load([5,6,7]); Xf=matrix(fw,cols); opf=mo.predict(Xf); paf=np.column_stack([m.predict(Xf) for m in mas]); Yf=fw[ycols].to_numpy(); best=np.argmax(paf,axis=1); mask=(opf>=cand.opp_thr)&(paf.max(axis=1)>=cand.act_thr); act=Yf[np.arange(len(fw)),best]; out=[]
for m in [5,6,7]:
 mm=mask&(fw.month.to_numpy()==m); z=act[mm]; gp=z[z>0].sum(); gl=z[z<0].sum(); out.append({'month':m,'n':int(mm.sum()),'net':float(z.sum()),'mean':float(z.mean()) if len(z) else np.nan,'pf':float(gp/(-gl)) if gl<0 else 999.,'win':float((z>0).mean()) if len(z) else np.nan})
res={'status':'FROZEN_EVAL','selected':cand.to_dict(),'forward':out,'mjj_net':float(sum(x['net'] for x in out)),'mjj_n':int(sum(x['n'] for x in out))}
json.dump(res,open(f'{OUT}/catboost_frozen_result.json','w'),indent=2); pd.DataFrame(out).to_csv(f'{OUT}/catboost_frozen_forward.csv',index=False); print('\nFROZEN FORWARD\n',pd.DataFrame(out).to_string(index=False)); print('MJJ',res['mjj_net'],res['mjj_n'])
imp=pd.DataFrame({'feature':cols,'opp':mo.get_feature_importance()})
for j,a in enumerate(actions): imp[a]=mas[j].get_feature_importance()
imp.to_csv(f'{OUT}/catboost_feature_importance.csv',index=False); print('\nTOP OPP FEATURES\n',imp.sort_values('opp',ascending=False).head(25).to_string(index=False))
