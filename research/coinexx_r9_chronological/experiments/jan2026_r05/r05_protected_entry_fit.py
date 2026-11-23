"""January supervised R05 protected first-leg temporal imitation. Offline labels only.
Target represents original immutable first-leg within +/-2 completed seconds, with protected
cycle controls weighted; runtime scores use only source causal quote features and R03 source scores.
"""
from pathlib import Path
import json,itertools,io,time,sys
import numpy as np,pandas as pd,lightgbm as lgb
ROOT=Path(__file__).parent
OLD=Path('/mnt/data/r9_jan_r03');RAW=OLD/'r03_phase_seconds.csv.gz';PR=OLD/'r03_hazard_predictions.csv.gz'
ORIG=pd.read_csv('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
first=ORIG[ORIG.leg==1].copy();first['minute_id']=first.entry_sec//60
entry=dict(zip(first.minute_id,first.entry_sec));sd=dict(zip(first.minute_id,np.where(first.side=='BUY',1,2)))
prot=dict(zip(first.minute_id,(first.original_booked_net_usd.gt(0)|first.cycle_net_usd.gt(0)).astype(int)))
BASIC=json.loads((OLD/'r03_hazard_fit.json').read_text())['feature_columns']
FEATURE=BASIC+['r03_fb','r03_fs','r03_gap','spread_atr_ratio','v5_atr_ratio','v20_atr_ratio','bid_impact','micro_vs_regime','directional_persistence','phase_sin','phase_cos']
SCORECOL=['sec','ms','bid_c','ask_c','phase','spread_c','f_b','f_s','s_b','s_s']

def derived(df,pr):
 d=df.loc[df.phase<=47,['sec','ms','bid_c','ask_c']+BASIC].copy();assert np.array_equal(d.ms.to_numpy('int64'),pr.ms.to_numpy('int64')) and np.array_equal(d.bid_c.to_numpy(),pr.bid_c.to_numpy())
 d['r03_fb']=pr.f_b.to_numpy();d['r03_fs']=pr.f_s.to_numpy();d['r03_gap']=np.abs(d.r03_fb-d.r03_fs)
 atr=np.maximum(d.m5_atr.to_numpy('float32'),50.)
 d['spread_atr_ratio']=d.spread_c.to_numpy()/atr;d['v5_atr_ratio']=d.ret5.to_numpy()/atr;d['v20_atr_ratio']=d.ret20.to_numpy()/atr
 d['bid_impact']=d.quote_imbalance10*d.eff10
 d['micro_vs_regime']=(d.ret10.to_numpy()/np.maximum(d.m15_atr.to_numpy(),80.))
 d['directional_persistence']=np.sign(d.ret10.to_numpy())*d.eff10
 d['phase_sin']=np.sin(2*np.pi*d.phase/60);d['phase_cos']=np.cos(2*np.pi*d.phase/60)
 return d

def batches():
 with open('/dev/null','w') as _:
  with pd.io.common.get_handle(PR,'r',compression='gzip') as h:
   pin=h.handle;assert pin.readline().strip().split(',')==SCORECOL
   for chunk in pd.read_csv(RAW,chunksize=130000):
    valid=chunk.phase<=47;n=int(valid.sum());
    pr=pd.read_csv(io.StringIO(''.join(itertools.islice(pin,n))),header=None,names=SCORECOL)
    if n!=len(pr):raise RuntimeError('R03 scores truncated')
    yield derived(chunk,pr),pr
   assert not pin.readline(),'unconsumed R03 scores'

def train():
 start=time.time();parts=[]
 for a,pr in batches():
  minute=(a.sec//60).to_numpy('int64');target=pd.Series(minute).map(entry).to_numpy(float);side=pd.Series(minute).map(sd).fillna(0).to_numpy('int8')
  dist=a.sec.to_numpy()-target
  keep=(np.isfinite(target)&(dist<=2)&(a.phase<=35)) | (~np.isfinite(target)&(minute%3==0)&(a.phase<=35))
  z=a.loc[keep,['sec']+FEATURE].copy();zz=(np.isfinite(target)&(np.abs(dist)<=2))
  z['y']=np.where(zz[keep],side[keep],0).astype('int8')
  pp=pd.Series(minute).map(prot).fillna(0).to_numpy('int8')
  z['sample_weight']=np.where(z.y.to_numpy()>0,np.where(pp[keep]>0,3.0,1.5),0.65)
  parts.append(z)
 b=pd.concat(parts,ignore_index=True);b.to_csv(ROOT/'r05_first_train.csv.gz',index=False,compression={'method':'gzip','compresslevel':1});x=b[FEATURE].to_numpy('float32');y=b.y.to_numpy();w=b.sample_weight.to_numpy('float32')
 print(json.dumps({'training_rows':len(b),'positive_side_counts':pd.Series(y).value_counts().to_dict(),'protected_labels':int(((y>0)&(w>2)).sum())}),flush=True)
 model=lgb.LGBMClassifier(objective='multiclass',num_class=3,n_estimators=280,learning_rate=.05,num_leaves=31,max_depth=7,min_child_samples=120,reg_lambda=16,verbosity=-1,n_jobs=4)
 model.fit(x,y,sample_weight=w);model.booster_.save_model(str(ROOT/'r05_first_protected_lgb.txt'))
 pr=model.predict_proba(x,num_threads=4)
 receipt={'model':'first-leg protected ±2sec smooth imitation','all_January_in_sample':True,'rows':len(b),'labels':int((y>0).sum()),'feature_list':FEATURE,'sample_weights':{'protected_original_positive_leg_or_positive_cycle':3,'other_trade':1.5,'wait':0.65},'top_importance':sorted(zip(FEATURE,model.feature_importances_.tolist()),key=lambda x:-x[1])[:16],'train_true_class_top1':round(float((pr.argmax(axis=1)==y).mean()),5),'elapsed_seconds':round(time.time()-start,2),'source_reference_only_used_in_training_labels':True}
 (ROOT/'r05_first_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2),flush=True)

def score():
 start=time.time();model=lgb.Booster(model_file=str(ROOT/'r05_first_protected_lgb.txt'));out=ROOT/'r05_first_protected_predictions.csv.gz';n=0;first=True
 for a,pr in batches():
  p=model.predict(a[FEATURE].to_numpy('float32'),num_threads=4)
  res=pr[SCORECOL].copy();res['f_b']=np.round(p[:,1],5);res['f_s']=np.round(p[:,2],5)
  res.to_csv(out,index=False,header=first,mode='wt' if first else 'at',compression={'method':'gzip','compresslevel':1});first=False;n+=len(res)
 print(json.dumps({'prediction_rows':n,'elapsed_seconds':round(time.time()-start,2),'bytes':out.stat().st_size}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='fit':train()
 else:score()
