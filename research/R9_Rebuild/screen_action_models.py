import pandas as pd, numpy as np, json, os, itertools
from sklearn.tree import DecisionTreeRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import ExtraTreesRegressor

ROOT='/mnt/data/r9_research_v2'; OUT=f'{ROOT}/screens'; os.makedirs(OUT,exist_ok=True)
months={m:pd.read_pickle(f'{ROOT}/events_{m:02d}.pkl.gz',compression='gzip') for m in [1,2,3]}
df=pd.concat(months.values(),ignore_index=True)
actions=['cont_r9','fade_r9','cont_harv','fade_harv']; ycols=[a+'_pnl' for a in actions]
meta={'month','time_ms','side','rearm','base_pnl','base_hold','base_mfe','base_mae'}
future=set(ycols)
for a in actions: future|={a+'_mfe',a+'_mae'}
allfeat=[c for c in df.columns if c not in meta and c not in future]
fixed=[c for c in allfeat if c.startswith('s') or c in ['atr_m5','compress5_30','compress15_30','tick5_30','rearm']]
mult=[c for c in allfeat if c.startswith('tf') or c.startswith('align_')]
dc=[c for c in allfeat if c.startswith('dc')]
groups={'FIXED':fixed,'MULTI':mult,'DC':dc,'FIXED_MULTI':list(dict.fromkeys(fixed+mult)),'FIXED_DC':list(dict.fromkeys(fixed+dc)),'MULTI_DC':list(dict.fromkeys(mult+dc)),'ALL':allfeat}
thresholds=[-0.05,0.0,0.025,0.05,0.075,0.10,0.15,0.20]
rows=[]
for gname,features in groups.items():
  X=df[features].replace([np.inf,-np.inf],np.nan)
  for depth in [3,4,5,6]:
    for leaf in [250,500,1000,2000]:
      preds=np.full((len(df),4),np.nan)
      for holdm in [1,2,3]:
        tr=df.month!=holdm; te=~tr
        for j,yc in enumerate(ycols):
          model=make_pipeline(SimpleImputer(strategy='median'),DecisionTreeRegressor(max_depth=depth,min_samples_leaf=leaf,random_state=42))
          model.fit(X.loc[tr],df.loc[tr,yc].clip(-3,3)); preds[te,j]=model.predict(X.loc[te])
      for th in thresholds:
        choice=np.argmax(preds,axis=1); mx=np.max(preds,axis=1); take=mx>=th
        actual=np.zeros(len(df)); Y=df[ycols].to_numpy(); actual[take]=Y[np.arange(len(df))[take],choice[take]]
        monthly=[float(actual[df.month.to_numpy()==m].sum()) for m in [1,2,3]]
        gp=float(actual[actual>0].sum()); gl=float(actual[actual<0].sum())
        rows.append({'group':gname,'depth':depth,'leaf':leaf,'thr':th,'net':float(actual.sum()),'trades':int(take.sum()),'mean':float(actual.sum()/max(take.sum(),1)),'gp':gp,'gl':gl,'pf':gp/(-gl) if gl<0 else 999.,'m1':monthly[0],'m2':monthly[1],'m3':monthly[2],'allpos':all(x>0 for x in monthly)})
res=pd.DataFrame(rows).sort_values(['allpos','net'],ascending=[False,False]); res.to_csv(f'{OUT}/dt_oof_grid.csv',index=False); print(res.head(30).to_string(index=False))
features=allfeat; X=df[features].replace([np.inf,-np.inf],np.nan); preds=np.full((len(df),4),np.nan)
for holdm in [1,2,3]:
 tr=df.month!=holdm; te=~tr
 for j,yc in enumerate(ycols):
  model=make_pipeline(SimpleImputer(strategy='median'),ExtraTreesRegressor(n_estimators=120,max_depth=10,min_samples_leaf=100,n_jobs=2,random_state=43,max_features=.6))
  model.fit(X.loc[tr],df.loc[tr,yc].clip(-3,3)); preds[te,j]=model.predict(X.loc[te])
ceil=[]
for th in thresholds:
 choice=np.argmax(preds,axis=1); mx=np.max(preds,axis=1); take=mx>=th; Y=df[ycols].to_numpy(); act=np.zeros(len(df)); act[take]=Y[np.arange(len(df))[take],choice[take]]
 mon=[float(act[df.month.to_numpy()==m].sum()) for m in [1,2,3]]; gp=float(act[act>0].sum()); gl=float(act[act<0].sum())
 ceil.append({'thr':th,'net':float(act.sum()),'trades':int(take.sum()),'mean':float(act.sum()/max(take.sum(),1)),'pf':gp/(-gl) if gl<0 else 999,'m1':mon[0],'m2':mon[1],'m3':mon[2]})
pd.DataFrame(ceil).to_csv(f'{OUT}/extratrees_oof_ceiling.csv',index=False); print('\nEXTRA TREES CEILING'); print(pd.DataFrame(ceil).to_string(index=False))
