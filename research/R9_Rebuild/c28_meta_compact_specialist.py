import argparse,json,os,tempfile,hashlib,time,itertools
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.tree import DecisionTreeClassifier
EVROOT=Path('/mnt/data/C28_v2'); REGROOT=Path('/mnt/data/C28_regime_features'); SEEDS={'source_default':(1.05,.78,1.20,.90),'strict':(.90,.75,1.40,.95),'balanced':(1.00,.75,1.30,.93),'loose':(1.10,.82,1.10,.85)}
DEPTHS=[2,3,4]; LEAVES=[300,600,1000]; THRS=[0.,.02,.05,.10]
FC=['side','rearm','atr_m5_ratio50','s2_disp_al','s2_eff','s2_range','s2_turns','s2_ticks','s5_disp_al','s5_eff','s5_range','s5_turns','s5_ticks','s10_disp_al','s10_eff','s10_range','s10_turns','s10_ticks','s10_volimb_al','s30_disp_al','s30_eff','s30_range','s30_turns','s30_ticks','compress5_30','compress15_30','tick5_30','align_pos_count','align_strong_count','align_min','align_mean','align_max']
def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def atomic_json(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=str(p.parent),prefix=p.name+'.tmp.')
 with os.fdopen(fd,'w') as f:json.dump(o,f,indent=2,sort_keys=True,allow_nan=True);f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def load(m):
 e=pd.read_pickle(EVROOT/f'events_{m:02d}_v2_recovery.pkl.gz',compression='gzip').sort_values('time_ms').reset_index(drop=True);r=pd.read_pickle(REGROOT/f'C28_REGIME_FEATURE_M{m:02d}.pkl.gz',compression='gzip').sort_values('time_ms').reset_index(drop=True)
 if len(e)!=len(r) or not np.array_equal(e.time_ms.to_numpy(),r.time_ms.to_numpy()):raise RuntimeError('identity mismatch')
 e=e.copy();e['atr_m5_ratio50']=r.atr_m5_ratio50.to_numpy(float);return e
def mask(d,s,spec):
 a,e,b,f=s; ar=d.atr_m5_ratio50.to_numpy(float);ef=d.s10_eff.to_numpy(float);v=np.isfinite(ar)&np.isfinite(ef);p4=v&(ar<=a)&(ef<=e);p6=v&(~p4)&((ar>=b)|(ef>=f));return p4 if spec=='P4' else p6
def fit(train,test,s,spec,dep,leaf):
 xx=[];yy=[];pp=[]
 for d in train:
  mk=mask(d,s,spec);pnl=(d.fade_harv_pnl if spec=='P4' else d.cont_harv_pnl).to_numpy(float)[mk];x=d.loc[mk,FC].to_numpy(float);ok=np.isfinite(pnl)&np.all(np.isfinite(x),axis=1)
  if ok.any():xx.append(x[ok]);yy.append((pnl[ok]>0).astype(np.int8));pp.append(pnl[ok])
 if not xx:return np.full(len(test),np.nan),0.,0.
 x=np.vstack(xx);y=np.concatenate(yy);p=np.concatenate(pp);xt=test[FC].to_numpy(float);ok=np.all(np.isfinite(xt),axis=1);pr=np.full(len(test),np.nan)
 if len(np.unique(y))<2:pr[ok]=float(y[0])
 else:
  md=DecisionTreeClassifier(max_depth=dep,min_samples_leaf=leaf,random_state=2814).fit(x,y);z=md.predict_proba(xt[ok]);cl=list(md.classes_);pr[ok]=z[:,cl.index(1)] if 1 in cl else 0.
 mw=float(p[p>0].mean()) if (p>0).any() else 0.;ml=float(p[p<=0].mean()) if (p<=0).any() else 0.;return pr,mw,ml
def metric(d,s,spec,pr,mw,ml,th):
 mk=mask(d,s,spec);u=pr*mw+(1-pr)*ml;take=mk&np.isfinite(u)&(u>=th);x=(d.fade_harv_pnl if spec=='P4' else d.cont_harv_pnl).to_numpy(float)[take];gp=float(x[x>0].sum());gl=float(x[x<0].sum());return {'net':float(x.sum()),'trades':int(len(x)),'pf':float(gp/-gl) if gl<0 else (1e9 if gp>0 else 0.),'win':float((x>0).mean()) if len(x) else 0.}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',choices=SEEDS,required=True);ap.add_argument('--spec',choices=['P4','P6'],required=True);ap.add_argument('--out-dir',default='/mnt/data/C28_meta_compact');a=ap.parse_args();t0=time.time();out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);D={m:load(m) for m in range(1,5)};s=SEEDS[a.seed];rows=[]
 for dep,leaf in itertools.product(DEPTHS,LEAVES):
  pred={tm:fit([D[m] for m in [1,2,3] if m!=tm],D[tm],s,a.spec,dep,leaf) for tm in [1,2,3]}
  for th in THRS:
   rec={'seed':a.seed,'spec':a.spec,'depth':dep,'leaf':leaf,'utility_threshold':th};nets=[]
   for tm in [1,2,3]:
    mm=metric(D[tm],s,a.spec,*pred[tm],th);rec.update({f'm{tm:02d}_{k}':v for k,v in mm.items()});nets.append(mm['net'])
   rec['disc_total']=sum(nets);rec['disc_min']=min(nets);rec['disc_all_positive']=all(x>0 for x in nets);rows.append(rec)
 df=pd.DataFrame(rows).sort_values(['disc_all_positive','disc_min','disc_total'],ascending=[False,False,False]);csv=out/f'C28_META_{a.seed}_{a.spec}.csv';df.to_csv(csv,index=False);best=df.iloc[0].to_dict();pr,mw,ml=fit([D[1],D[2],D[3]],D[4],s,a.spec,int(best['depth']),int(best['leaf']));apr=metric(D[4],s,a.spec,pr,mw,ml,float(best['utility_threshold']))
 js={'status':'COMPLETED_LOCAL','seed':a.seed,'spec':a.spec,'seed_values':s,'features':FC,'configs':len(df),'all_positive_count':int(df.disc_all_positive.sum()),'best_discovery':best,'frozen_april':apr,'output_sha256':sha256(csv),'elapsed_seconds':time.time()-t0,'label':'specialist prescribed action pnl>0; utility from training mean win/loss; spread embedded','screen_type':'LOMO Jan-Mar event-independent diagnostic; exact chronology required before promotion'};atomic_json(out/f'C28_META_{a.seed}_{a.spec}.json',js);print(json.dumps(js,indent=2,allow_nan=True))
if __name__=='__main__':main()
