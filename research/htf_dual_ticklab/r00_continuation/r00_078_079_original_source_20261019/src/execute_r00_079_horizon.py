"""R00-079: Source-native Jan-only 5s/15s horizon oracles for original 30s initial direction.
Continuity-preserving use of existing R00-078 as-of feature arrays, R00-077 incumbent,
source-normalized ORIGINAL_067_reader, and original R00-065 indexed events.
Never uses training future labels as live features. No fills/exits/PnL.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd,joblib
from lightgbm import LGBMClassifier
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ORIGINAL_067_reader import load_raw
REF=Path('/mnt/data/xauusd_handoff_bootstrap_20261019/R00_077_PORTABLE/results')
PREV=ROOT/'results'
BROKERS=('coinexx','dukascopy')
POLICIES=['INCUMBENT_077','PREVIOUS_FUSION_SELECTED','5S_DIRECT','15S_DIRECT','HORIZON_AVG_DIRECT','HORIZON_GEOMETRIC_DIRECT','ALL_3_ORACLE_DIRECT','SHORT_LONG_AGREE_FLIP','TRIPLE_AGREE_FLIP','5_15_CONVEXITY_FLIP','077_PLUS_NEW_HORIZON','077_VETO_HORIZON','077_PLUS_FAST_SPECIALIST']

def checksum(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load(b,m):
 with np.load(ROOT/'features'/f'R00_078_{b}_{m}_ASOF.npz',allow_pickle=False) as z:return {k:z[k].copy() for k in ('ts_ms','quote_index','feature','y')}

def jan_labels(b):
 a=load(b,'01');ts,j=a['ts_ms'],a['quote_index'];t,bid,ask,h=load_raw(b,'01')
 assert np.array_equal(ts,t[j]);mid=(bid+ask)*.5
 res={}
 for sec in (5,15):
  ind=np.searchsorted(t,ts+sec*1000,side='left');good=ind<len(t)
  ind=np.clip(ind,0,len(t)-1)
  valid=good&(t[ind]>=ts+sec*1000)&(t[ind]<ts+(sec+2)*1000)
  d=mid[ind]-mid[j]
  res[str(sec)]=np.where(valid,np.where(d>.10,1,np.where(d<-.10,-1,0)),0).astype(np.int8)
  res[str(sec)+'_valid']=valid
 p=ROOT/'features'/f'R00_079_{b}_JAN_MULTI_HORIZON_TRAIN_LABELS.npz';np.savez_compressed(p,ts_ms=ts,quote_index=j,y30=a['y'],source_sha256=np.array(h),**res)
 print('LABELS',b,{'source_sha':h,'n':len(j),'y5':np.bincount(res['5']+1,minlength=3).tolist(),'y15':np.bincount(res['15']+1,minlength=3).tolist()},flush=True)
 return res

def fit(b):
 d=load(b,'01');a=jan_labels(b);X=d['feature'];ii=np.arange(0,len(X),4)
 for sec in (5,15):
  mdl=LGBMClassifier(objective='multiclass',n_estimators=130,num_leaves=19,min_child_samples=165,learning_rate=.045,reg_lambda=16,n_jobs=2,random_state=20261024+sec,verbosity=-1)
  mdl.fit(X[ii],a[str(sec)][ii]);p=ROOT/'models'/f'R00_079_{b}_{sec}S_ORACLE.joblib';joblib.dump(mdl,p,compress=3)
  print('FIT',b,sec,'SHA',checksum(p),flush=True)

def trivalent_proba(m,x):
 p=m.predict_proba(x);out=np.zeros((len(x),3),np.float32)
 for i,c in enumerate(m.classes_):out[:,int(c)+1]=p[:,i]
 return out

def score(b,m):
 a=load(b,m);X=a['feature'];y=a['y'];n=len(y)
 with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz',allow_pickle=False) as old, np.load(PREV/f'R00_078B_{b}_{m}_EVENTS.npz',allow_pickle=False) as new:
  assert np.array_equal(a['ts_ms'],old['ts_ms']) and np.array_equal(a['ts_ms'],new['ts_ms'])
  base=old['BASE'].copy();inc=old['AGREE_005'].copy();old078=new['078_PRIO_STRONG'].copy()
 p5=trivalent_proba(joblib.load(ROOT/'models'/f'R00_079_{b}_5S_ORACLE.joblib'),X)
 p15=trivalent_proba(joblib.load(ROOT/'models'/f'R00_079_{b}_15S_ORACLE.joblib'),X)
 # Existing Jan 30s cooperative oracle: no change to original model.
 m30=joblib.load(ROOT/'models'/f'R00_078_{b}_cooperative.joblib')
 p30=trivalent_proba(m30,X)
 sign=lambda p:np.where(p[:,2]>=p[:,0],1,-1).astype('int8')
 sm5,sm15,sm30=sign(p5),sign(p15),sign(p30)
 avg=.35*p5+.35*p15+.30*p30
 geo=(np.maximum(p5,1e-4)*np.maximum(p15,1e-4)*np.maximum(p30,1e-4))**(1/3)
 geo/=geo.sum(axis=1)[:,None]
 agree=(sm5==sm15)
 trip=agree&(sm15==sm30)
 agreement_bad=agree&(sm5==-base)
 maturity=(sm15==-base)&(((p15[:,2]-p15[:,0])*sm15)>.07)
 fast_bias=-base*(p5[:,2]-p5[:,0]);slow_bias=-base*(p15[:,2]-p15[:,0]);long_bias=-base*(p30[:,2]-p30[:,0])
 # Learned 5/15s predictions reference only January labels, not target-month future labels.
 panel={
  'INCUMBENT_077':inc,
  'PREVIOUS_FUSION_SELECTED':old078,
  '5S_DIRECT':sm5,'15S_DIRECT':sm15,
  'HORIZON_AVG_DIRECT':sign(avg),'HORIZON_GEOMETRIC_DIRECT':sign(geo),
  'ALL_3_ORACLE_DIRECT':np.where(trip,sm15,inc),
  'SHORT_LONG_AGREE_FLIP':np.where(agreement_bad&(fast_bias>.05)&(slow_bias>.05),-base,inc),
  'TRIPLE_AGREE_FLIP':np.where(trip&(sm15==-base)&(slow_bias>.04),-base,inc),
  '5_15_CONVEXITY_FLIP':np.where(maturity&(slow_bias>fast_bias+.03)&(long_bias>.03),-base,inc),
  '077_PLUS_NEW_HORIZON':np.where(agreement_bad&(slow_bias>.1),-base,inc),
  '077_VETO_HORIZON':np.where((inc!=base)&(sm5==-base)&(sm15==-base),inc,base),
  '077_PLUS_FAST_SPECIALIST':np.where((sm5==-base)&(fast_bias>.15)&(long_bias>.04),-base,inc)
 }
 assert list(panel)==POLICIES
 rows=[]
 for name,p in panel.items():
  flip=p!=base;rescue=int(np.count_nonzero(flip&(p==y)));damage=int(np.count_nonzero(flip&(base==y)))
  rows.append({'broker':b,'month':m,'policy':name,'events':n,'correct':int(np.count_nonzero(p==y)),'accuracy':float(np.mean(p==y)),'flips':int(np.count_nonzero(flip)),'rescued':rescue,'damaged':damage,'net':rescue-damage,'BUY':int(np.count_nonzero(p==1)),'SELL':int(np.count_nonzero(p==-1))})
 pd.DataFrame(rows).to_csv(PREV/f'R00_079_{b}_{m}_POLICIES.csv',index=False)
 np.savez_compressed(PREV/f'R00_079_{b}_{m}_EVENTS.npz',ts_ms=a['ts_ms'],quote_index=a['quote_index'],y=y,base=base,**panel,fast_bias=fast_bias.astype('float32'),slow_bias=slow_bias.astype('float32'),long_bias=long_bias.astype('float32'))
 print('SCORE',b,m,'incumbent',rows[0]['correct'],'descriptive_best',max(rows,key=lambda x:x['correct'])['policy'],flush=True)

def freeze():
 x=pd.concat([pd.read_csv(PREV/f'R00_079_{b}_02_POLICIES.csv') for b in BROKERS])
 z=x.groupby('policy')[['events','correct','flips']].sum()
 winner=min(POLICIES,key=lambda k:(-int(z.loc[k,'correct']),0 if k=='INCUMBENT_077' else 1,int(z.loc[k,'flips']),POLICIES.index(k)))
 obj={'selected_Feb':winner,'scores_Feb':z.to_dict('index'),'selection_on_Feb_only':True,'plan_sha256':checksum(ROOT/'R00_079_PREDECLARED_MULTIHORIZON_PLAN.json')}
 (PREV/'R00_079_FEB_FROZEN.json').write_text(json.dumps(obj,indent=2)+'\n');print('FEB_FROZEN',winner,z.loc[winner].to_dict(),flush=True)

def finish():
 ob=json.loads((PREV/'R00_079_FEB_FROZEN.json').read_text());win=ob['selected_Feb']
 x=pd.concat([pd.read_csv(PREV/f'R00_079_{b}_{m}_POLICIES.csv') for b in BROKERS for m in ('02','06','07')]);x.to_csv(PREV/'R00_079_ALL_POLICY_BROKER_MONTH.csv',index=False)
 z=x[x.month.isin((6,7))].groupby('policy')[['events','correct','flips','rescued','damaged','net','BUY','SELL']].sum();z['accuracy']=z.correct/z.events
 z.to_csv(PREV/'R00_079_EXPOSED_ALL_POLICIES.csv')
 obj={'FEB_frozen':win,'baseline_077_JunJul':z.loc['INCUMBENT_077'].to_dict(),'selected_JunJul':z.loc[win].to_dict(),'delta_correct_vs_incumbent':int(z.loc[win,'correct']-z.loc['INCUMBENT_077','correct']),'descriptive_hindsight_best_NOT_SELECTED':str(z.correct.idxmax()),'original_event_population':814244,'no_new_events_or_skips':True,'no_exit_profit_blind':True}
 (PREV/'R00_079_COMPLETE_RESEARCH_RECEIPT.json').write_text(json.dumps(obj,indent=2)+'\n');print('COMPLETE',json.dumps(obj),flush=True)
if __name__=='__main__':
 action=sys.argv[1]
 if action=='fit':fit(sys.argv[2])
 elif action=='score':score(sys.argv[2],sys.argv[3])
 elif action=='freeze':freeze()
 elif action=='finish':finish()
 else:raise ValueError(action)
