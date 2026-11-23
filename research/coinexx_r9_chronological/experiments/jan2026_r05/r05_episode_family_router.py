"""January fitted family router. The first observable quote of the minute is the ONLY
runtime information for family prediction; original R9 family labels never enter replay.
Family choices: no original first, early 0..10, late 18..28, other.
"""
from pathlib import Path
import pandas as pd,numpy as np,lightgbm as lgb,json,time,sys
R=Path(__file__).parent;OLD=Path('/mnt/data/r9_jan_r03');ROOT=OLD/'r03_phase_seconds.csv.gz';H=OLD/'r03_hazard_predictions.csv.gz'
BASE=['phase','minute','hour','spread_c','gap_ms','m1_disp','m5_disp','m15_disp','h1_disp','m5_atr','m15_atr','h1_atr','ret1','ret5','ret10','ret20','ret30','ret60','ret300','eff10','eff30','eff60','range10','range60','quotes10','quotes60','quote_imbalance10','m5_position','m15_position','h1_position']

def build():
 # Synthetic R9 labels are accessed only during deliberate January OFFLINE FIT.
 original=pd.read_csv('/mnt/data/jan2026_forensic_metrics/2026-01_ALL_27980_TRADES_manifest.csv')
 first=original[original.leg==1].copy()
 first['minute_id']=first.entry_sec//60
 first['family']=np.select([first.entry_sec%60<=10,(first.entry_sec%60).between(18,28)], [1,2],default=3)
 family=dict(zip(first.minute_id,first.family))
 a=[];seen=-1
 for ch in pd.read_csv(ROOT,chunksize=150000):
  minutes=ch.sec.to_numpy('int64')//60;mark=np.r_[minutes[0]!=seen,minutes[1:]!=minutes[:-1]];pick=ch.loc[mark,['sec','ms','bid_c','ask_c']+BASE];seen=int(minutes[-1]);a.append(pick)
 df=pd.concat(a,ignore_index=True);df['minute_id']=df.sec//60;df['family']=df.minute_id.map(family).fillna(0).astype('int8');df.to_csv(R/'r05_episode_firstquote.csv.gz',compression={'method':'gzip','compresslevel':1},index=False)
 return df

def fit():
 start=time.time();df=build();X=df[BASE].to_numpy('float32');y=df.family.to_numpy();model=lgb.LGBMClassifier(objective='multiclass',num_class=4,n_estimators=210,learning_rate=.07,num_leaves=23,max_depth=6,min_child_samples=65,reg_lambda=30,n_jobs=4,verbosity=-1)
 model.fit(X,y);model.booster_.save_model(str(R/'r05_episode_family_lgb.txt'));pr=model.predict_proba(X,num_threads=4)
 counts=np.bincount(y,minlength=4)
 rec={'model':'first source quote of each minute to original January 4-way R9 episode family','observed_minute_count':len(df),'family_counts':counts.tolist(),'training_accuracy_in_sample':round(float((pr.argmax(1)==y).mean()),5),'pretrade_available_Coinexx_completed_context_only':True,'training_labels_original_R9_fixed_only':True,'features':BASE,'top_importance':sorted(zip(BASE,model.feature_importances_.tolist()),key=lambda x:-x[1])[:10],'elapsed_s':round(time.time()-start,2)}
 (R/'r05_episode_receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec,indent=2),flush=True)

def score():
 start=time.time();df=pd.read_csv(R/'r05_episode_firstquote.csv.gz');model=lgb.Booster(model_file=str(R/'r05_episode_family_lgb.txt'));p=model.predict(df[BASE].to_numpy('float32'),num_threads=4);assert p.shape[1]==4
 d=df[['minute_id']].copy();d['none']=p[:,0];d['early']=p[:,1];d['late']=p[:,2];d['other']=p[:,3];d.to_csv(R/'r05_episode_family_scores.csv.gz',compression={'method':'gzip','compresslevel':1},index=False)
 # Keep original R03 model source BID/ASK parity. Stream scores only; no label/time/target file is read.
 scores=[]
 for ch in pd.read_csv(H,chunksize=150000):
  c=ch[['sec','ms','bid_c','ask_c','phase','spread_c','f_b','f_s','s_b','s_s']].copy();m=c.sec//60
  jj=np.searchsorted(d.minute_id.to_numpy(),m.to_numpy());jj=np.minimum(jj,len(d)-1)
  assert np.array_equal(d.minute_id.to_numpy()[jj],m.to_numpy())
  early=d.early.to_numpy()[jj];late=d.late.to_numpy()[jj];other=d.other.to_numpy()[jj]
  ph=c.phase.to_numpy();weight=np.where(ph<=10,np.clip(early*2.,.08,1.5),np.where((ph>=18)&(ph<=28),np.clip(late*2.,.08,1.5),np.clip(other*2.,.08,1.5)))
  c['f_b']=np.round(c.f_b.to_numpy()*weight,5);c['f_s']=np.round(c.f_s.to_numpy()*weight,5)
  scores.append(c)
 del c
 z=pd.concat(scores,ignore_index=True);z.to_csv(R/'r05_episode_predictions.csv.gz',compression={'method':'gzip','compresslevel':1},index=False)
 print(json.dumps({'predictions':len(z),'bytes':(R/'r05_episode_predictions.csv.gz').stat().st_size,'elapsed_s':round(time.time()-start,2)}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='fit':fit()
 else:score()
