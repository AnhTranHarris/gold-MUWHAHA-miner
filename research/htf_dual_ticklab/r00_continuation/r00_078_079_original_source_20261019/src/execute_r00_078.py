"""R00-078 ABC: frozen multi-oracle same-native-event initial direction research.

Additive source-native experiment only; imports the exact ORIGINAL_067_reader and
native_phase_076d research helpers unchanged, never replaces either broker replay.
Jan fit -> Feb freeze -> June/July historically exposed transfer.
No trade fills, exits, P&L, live claims or unauthorized dataset.
"""
from __future__ import annotations
import os,sys,json,hashlib,io,zipfile,time,gc
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from lightgbm import LGBMClassifier

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ORIGINAL_067_reader import load_raw
from native_phase_076d import extract,FIELDS
ROOTDATA=Path('/mnt/data')
Z=zipfile.ZipFile(ROOTDATA/'R00_065_COMPLETE_NATIVE_QUOTE_RESEARCH_20261018.zip')
REF=ROOTDATA/'xauusd_handoff_bootstrap_20261019/R00_077_PORTABLE/results'
BROKERS=('coinexx','dukascopy')
MONTHS=('01','02','06','07')
POLICIES=['BASE','MICRO_DIRECT','STRUCTURE_DIRECT','COOP_DIRECT','ORACLE_CONSENSUS','ORACLE_GEOMEAN','FLIP_010','FLIP_020','FLIP_STRUCT_010','FLIP_DISAGREE_010','FLIP_EPISODE_010','ORTHOGONAL_EXPERT','NOFEATURE_FLIP_CONTROL']
MODELS=('micro','structure','impulse','exhaustion','reclaim','pullback','cooperative')
for k in ('features','models','results','logs'):(ROOT/k).mkdir(exist_ok=True)

def checksum(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def old(b,m):
 name=f'R00_065_NATIVE_RESEARCH_20261018/native_{b}_{m}.npz'
 with np.load(io.BytesIO(Z.read(name)),allow_pickle=False) as z:
  return {k:z[k].copy() for k in ('ts_ms','quote_index','feature','expert_mask','active_states','expert_votes','active_votes')}

def source_labels(t,bid,ask,ts,j):
 i=np.searchsorted(t,ts+30000,'left');exists=i<len(t)
 ff=i.clip(0,len(t)-1)
 valid=exists&(t[ff]>=ts+30000)&(t[ff]<ts+32000)
 mid=(bid+ask)*.5
 d=mid[ff]-mid[j]
 label=np.where(valid,np.where(d>.10,1,np.where(d<-.10,-1,0)),0).astype(np.int8)
 return label, valid

def last_change_ages(ts, state, k):
 v=state[:,k];n=len(v);change=np.r_[True,v[1:]!=v[:-1]]
 last=np.maximum.accumulate(np.where(change,np.arange(n),0))
 return np.minimum((ts-ts[last]).astype('float32')/1000,3600)

def episode_transition_features(ts, state, oldf):
 # Observed last-event state transitions are causal lower-resolution clocks;
 # full individual state is refreshed from each underlying ORIGINAL tick by extract().
 ix=[16,17,20,21,24,25,28,29,32,33,35,36,38,39]
 ages=np.column_stack([last_change_ages(ts,state,k) for k in ix]).astype('float32')
 current=state[:,ix]
 prev=np.vstack([current[0:1],current[:-1]])
 delta=(current-prev).astype('float32')
 epmask=oldf['expert_mask']
 votes=oldf['expert_votes'].astype('float32')
 active=oldf['active_states'].astype('float32')
 # Deterministic competing expert stages, no event filtering.
 signs=np.column_stack([state[:,16],state[:,20],state[:,32],state[:,35]]).astype('float32')
 stages=np.column_stack([state[:,17],state[:,21],state[:,33],state[:,36]]).astype('float32')
 parts=[ages,delta,
   np.sum(signs>0,axis=1)[:,None].astype('float32'),
   np.sum(signs<0,axis=1)[:,None].astype('float32'),
   np.sum(stages>=2,axis=1)[:,None].astype('float32'),
   np.sum(votes,axis=1)[:,None],
   (state[:,24:26]-state[:,28:30]).astype('float32'),
   ((state[:,38]*state[:,39])>0).astype('float32')[:,None],
   ((state[:,16]*state[:,20])<0).astype('float32')[:,None],
   ((state[:,32]*state[:,35])<0).astype('float32')[:,None],
   np.where(epmask>0,1,0).astype('float32')[:,None],
   (active[:,0]-active[:,1]).astype('float32')[:,None],
 ]
 return np.column_stack(parts).astype('float32')

def derive(b,m):
 start=time.time();o=old(b,m);t,bid,ask,sha=load_raw(b,m)
 ts,j=o['ts_ms'],o['quote_index']
 assert np.array_equal(ts,t[j]),'R00-065 event identity drift'
 if m!='01':
  with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz',allow_pickle=False) as ref:
   assert np.array_equal(ts,ref['ts_ms']) and np.array_equal(j,ref['quote_index']), 'R00-077 event identity drift'
 y,valid=source_labels(t,bid,ask,ts,j)
 if m!='01':
  with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz',allow_pickle=False) as ref:
   assert np.array_equal(y,ref['y']), 'R00-077 label drift'
 state,piv=extract(t,bid,ask,j)
 more=episode_transition_features(ts,state,o)
 x=np.column_stack([o['feature'],o['expert_mask'].astype('float32'),o['active_states'],state,more]).astype('float32')
 assert x.shape[1]==39+1+4+42+more.shape[1]
 assert np.isfinite(x).all()
 outfile=ROOT/'features'/f'R00_078_{b}_{m}_ASOF.npz'
 np.savez_compressed(outfile,ts_ms=ts,quote_index=j,feature=x,y=y,expert_votes=o['expert_votes'],expert_mask=o['expert_mask'],state=state)
 rec={'broker':b,'month':m,'source_sha256':sha,'native_quotes':len(t),'original_events':len(j),'original_index_equal_077':m!='01','thirty_second_077_labels_exact_equal':m!='01','label_corrected_source_native':True,'label_neutral_missing':int(np.count_nonzero(y==0)),'label_up':int(np.count_nonzero(y>0)),'label_down':int(np.count_nonzero(y<0)),'features':x.shape[1],'published_pivots':len(piv[0]),'file_sha256':checksum(outfile),'bytes':outfile.stat().st_size,'duration_s':round(time.time()-start,3)}
 (ROOT/'features'/f'R00_078_{b}_{m}_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
 print('DERIVE',json.dumps(rec),flush=True)
 del t,bid,ask,x,o,state,more;gc.collect()

def data(b,m):
 with np.load(ROOT/'features'/f'R00_078_{b}_{m}_ASOF.npz',allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}

def groups(x):
 # Global: original 39+mask+4active; stage: 42 phase; new: 36 transition/competing expert features
 base=np.arange(44)
 phase=np.arange(44,86)
 meta=np.arange(86,x.shape[1])
 struct=np.r_[np.arange(14,26),np.arange(44+24,44+42),meta]
 impulse=np.r_[np.arange(0,16),np.arange(44,44+20),meta]
 exhaustion=np.r_[np.arange(0,16),np.arange(44+16,44+24),meta]
 reclaim=np.r_[np.arange(0,26),np.arange(44+24,44+32),meta]
 pullback=np.r_[np.arange(0,26),np.arange(44+32,44+42),meta]
 return {'micro':base,'structure':struct,'impulse':impulse,'exhaustion':exhaustion,'reclaim':reclaim,'pullback':pullback,'cooperative':np.arange(x.shape[1])}

def classifier(seed):
 return LGBMClassifier(objective='multiclass',n_estimators=100,num_leaves=19,min_child_samples=170,learning_rate=.05,reg_lambda=14,n_jobs=2,random_state=seed,verbosity=-1)

def fit(b):
 d=data(b,'01');X=d['feature'];y=d['y']
 # Purge 32-second boundary around the training partition; Jan as-of features
 # and 30s forward labels, NO Feb/June/July in fitting.
 j=np.arange(0,len(y),4)
 ix=groups(X);filerec={}
 for k,g in ix.items():
  mod=classifier(20261019+MODELS.index(k));mod.fit(X[j][:,g],y[j])
  p=ROOT/'models'/f'R00_078_{b}_{k}.joblib';joblib.dump(mod,p,compress=3)
  filerec[k]={'sha256':checksum(p),'columns':g.tolist(),'train_rows':len(j),'classes':mod.classes_.tolist()}
 (ROOT/'models'/f'R00_078_{b}_MANIFEST.json').write_text(json.dumps(filerec,indent=2)+'\n')
 print('FIT',b,{k:v['sha256'] for k,v in filerec.items()},flush=True)

def probs(mod,x):
 raw=mod.predict_proba(x);out=np.zeros((len(x),3),np.float32)
 for i,c in enumerate(mod.classes_):out[:,int(c)+1]=raw[:,i]
 return out

def forecast(b,d):
 X=d['feature'];ix=groups(X);p={}
 for k in MODELS:
  mod=joblib.load(ROOT/'models'/f'R00_078_{b}_{k}.joblib');p[k]=probs(mod,X[:,ix[k]])
 return p

def sides(b,m,p,d):
 if m=='01':raise ValueError('Jan base unavailable: do not use invalid in-sample baseline')
 with np.load(REF/f'R00_077_{b}_{m}_EVENTS.npz',allow_pickle=False) as z:
  base=z['base'].copy();assert np.array_equal(d['ts_ms'],z['ts_ms'])
 n=len(base);sgn=lambda arr: np.where(arr[:,2]>=arr[:,0],1,-1).astype('int8')
 pc=p['cooperative'];ps=p['structure'];pm=p['micro']
 expert=np.mean(np.stack([p[k] for k in ['impulse','exhaustion','reclaim','pullback']],axis=0),axis=0)
 consensus=(pc+ps+pm+expert)/4
 geometric=np.exp((np.log(np.maximum(pc,1e-5))+np.log(np.maximum(ps,1e-5))+np.log(np.maximum(pm,1e-5))+np.log(np.maximum(expert,1e-5)))/4)
 geometric/=geometric.sum(axis=1)[:,None]
 advantage=-base*(pc[:,2]-pc[:,0])
 struct_edge=-base*(ps[:,2]-ps[:,0])
 specialist_edge=-base*(expert[:,2]-expert[:,0])
 # episode vector four independently reset at tick-level (IMP/EXH/PULL); only when published.
 st=d['state'];active=np.column_stack([st[:,16],st[:,20],st[:,32],st[:,35]])
 confidence=np.sum(active* (np.column_stack([st[:,17],st[:,21],st[:,33],st[:,36]])>=1),axis=1)
 votes=d['expert_votes'].sum(axis=1)+confidence
 s={
  'BASE':base,'MICRO_DIRECT':sgn(pm),'STRUCTURE_DIRECT':sgn(ps),'COOP_DIRECT':sgn(pc),
  'ORACLE_CONSENSUS':sgn(consensus),'ORACLE_GEOMEAN':sgn(geometric),
  'FLIP_010':np.where(advantage>.10,-base,base),
  'FLIP_020':np.where(advantage>.20,-base,base),
  'FLIP_STRUCT_010':np.where((advantage>.10)&(struct_edge>.10),-base,base),
  'FLIP_DISAGREE_010':np.where((advantage>.10)&(struct_edge>.10)&(specialist_edge>.10),-base,base),
  'FLIP_EPISODE_010':np.where((specialist_edge>.10)&(advantage>.06)&(votes*base<0),-base,base),
  'ORTHOGONAL_EXPERT':np.where(votes>0,1,np.where(votes<0,-1,base)),
  'NOFEATURE_FLIP_CONTROL':np.where(np.arange(n)%97==0,-base,base)
 }
 assert list(s)==POLICIES
 return {k:np.asarray(v,dtype='int8') for k,v in s.items()}, {'advantage':advantage.astype('float32'),'struct_edge':struct_edge.astype('float32'),'specialist_edge':specialist_edge.astype('float32'),'vote':votes.astype('float32')}

def score(b,m):
 d=data(b,m);p=forecast(b,d);s,extras=sides(b,m,p,d);n=len(d['y']);base=s['BASE'];y=d['y'];rows=[]
 for k,pred in s.items():
  change=pred!=base
  rescued=int(np.count_nonzero(change&(pred==y)))
  damaged=int(np.count_nonzero(change&(base==y)))
  total=int(np.count_nonzero(pred==y))
  rows.append({'broker':b,'month':m,'policy':k,'events':n,'correct':total,'accuracy':total/n,'flips':int(change.sum()),'rescued':rescued,'damaged':damaged,'neutral_changed':int(np.count_nonzero(change&(y==0))),'net_rescues':rescued-damaged,'buy':int(np.count_nonzero(pred==1)),'sell':int(np.count_nonzero(pred==-1))})
  assert total==int(np.count_nonzero(base==y))+rescued-damaged
 df=pd.DataFrame(rows);df.to_csv(ROOT/'results'/f'R00_078_{b}_{m}_POLICIES.csv',index=False)
 filename=ROOT/'results'/f'R00_078_{b}_{m}_EVENTS.npz'
 np.savez_compressed(filename,ts_ms=d['ts_ms'],quote_index=d['quote_index'],y=y,**s,**extras)
 print('SCORE',b,m,'base',rows[0]['correct'],'best_descriptive_not_selected',max(rows,key=lambda x:x['correct'])['policy'],flush=True)
 return df

def freeze():
 df=pd.concat([pd.read_csv(ROOT/'results'/f'R00_078_{b}_02_POLICIES.csv') for b in BROKERS])
 agg=df.groupby('policy',sort=False)[['events','correct','flips']].sum()
 winner=min(POLICIES,key=lambda q:(-int(agg.loc[q,'correct']),0 if q=='BASE' else 1,int(agg.loc[q,'flips']),POLICIES.index(q)))
 v={'frozen_winner':winner,'selected_by':'FEB combined correct on all original events','frozen_candidates':POLICIES,'FEB':agg.to_dict(orient='index'),'no_June_July_selection':True,'parent_plan_sha256':checksum(ROOT/'R00_078_PREDECLARED_PLAN.json')}
 (ROOT/'results'/'R00_078_FEB_FROZEN.json').write_text(json.dumps(v,indent=2)+'\n')
 print('FEB FROZEN',winner,agg.loc[winner].to_dict(),flush=True)
 return winner

def interval_benchmark(winner):
 h=pd.read_csv(ROOT/'originals/R00_077_R9_HOUR_DAY_ALL.csv')
 w=pd.read_csv(ROOT/'originals/R00_077_R9_WEEK_MONTH_ALL.csv')
 h=h[h.policy=='BASE'].drop_duplicates(['broker','month','interval','key']).copy()
 w=w[w.policy=='BASE'].drop_duplicates(['broker','interval','UTC_key']).copy()
 rows=[]
 for b in BROKERS:
  for m in ('06','07'):
   with np.load(ROOT/'results'/f'R00_078_{b}_{m}_EVENTS.npz') as z:
    ts=z['ts_ms'];y=z['y'];p=z[winner];ok=p==y
   for inter,unit in [('hour',3600000),('day',86400000)]:
    tkey=ts//unit; z=h[(h.broker==b)&(h.month==int(m))&(h.interval==inter)].copy()
    # all R9 reference keys retained including zero observed native source.
    keys=z.key.to_numpy(np.int64); allct=np.bincount(np.searchsorted(np.unique(np.r_[keys,tkey]),tkey),minlength=len(np.unique(np.r_[keys,tkey])))
    u=np.unique(np.r_[keys,tkey]); vals=allct[np.searchsorted(u,keys)]
    kt=tkey[ok]; corr=np.bincount(np.searchsorted(u,kt),minlength=len(u))[np.searchsorted(u,keys)]
    for row, emitted, correct in zip(z.itertuples(),vals,corr):
     floor=int(row.floor90);rows.append(dict(broker=b,month=m,interval=inter,key=str(row.key),r9=int(row.R9_SYNTH_trades),floor90=floor,emitted=int(emitted),correct=int(correct),volume_pass=int(emitted)>=floor,correct_pass=int(correct)>=floor,both_pass=int(emitted)>=floor and int(correct)>=floor,policy=winner))
   # ISO week/month exact UTC key as original preserved R00-077 ledgers.
   # Report reference keys beyond matched window without rewriting R9.
   dates=pd.to_datetime(ts,unit='ms',utc=True)
   week=dates.isocalendar(); wk=np.array([f'{yy}-W{ww:02d}' for yy,ww in zip(week.year,week.week)],dtype=object)
   month=np.array(dates.strftime('%Y-%m'),dtype=object)
   for inter,keys in [('ISO_week',wk),('month',month)]:
    z=w[(w.broker==b)&(w.interval==inter)].copy()
    for row in z.itertuples():
     key=str(row.UTC_key)
     mask=keys==key
     # original month keys unique per broker; week across June->July spans month boundary
     # do not double count ISO week rows as totals are counted from each b,m source separately.
     if mask.sum()==0 and int(row.R9_SYNTH_trades)==0:continue
     emitted=int(np.count_nonzero(mask)); correct=int(np.count_nonzero(mask&ok));floor=int(row.floor90)
     rows.append(dict(broker=b,month=m,interval=inter,key=key,r9=int(row.R9_SYNTH_trades),floor90=floor,emitted=emitted,correct=correct,volume_pass=emitted>=floor,correct_pass=correct>=floor,both_pass=emitted>=floor and correct>=floor,policy=winner))
 pd.DataFrame(rows).to_csv(ROOT/'results'/'R00_078_R9_INTERVAL_AUDIT.csv',index=False)
 # hourly/day panels here are exact; ISO/week should be interpreted per month key only when original reference similarly scoped.
 return pd.DataFrame(rows)

def finish():
 win=json.loads((ROOT/'results'/'R00_078_FEB_FROZEN.json').read_text())['frozen_winner']
 df=pd.concat([pd.read_csv(ROOT/'results'/f'R00_078_{b}_{m}_POLICIES.csv') for b in BROKERS for m in ('02','06','07')],ignore_index=True)
 df.to_csv(ROOT/'results'/'R00_078_ALL_BROKER_MONTH_POLICIES.csv',index=False)
 trans=df[df.month.isin([6,7])].groupby('policy')[['events','correct','flips','rescued','damaged','neutral_changed','net_rescues','buy','sell']].sum()
 trans['accuracy']=trans.correct/trans.events;trans.to_csv(ROOT/'results'/'R00_078_EXPOSED_ALL_POLICIES.csv')
 bench=interval_benchmark(win)
 h=bench[bench.interval.isin(['hour','day'])].groupby('interval').agg(total=('both_pass','size'),pass_both=('both_pass','sum'),pass_volume=('volume_pass','sum'),pass_correct=('correct_pass','sum'))
 rec={'experiment':'R00-078 ABC','selected_FEB':win,'baseline_June_July':trans.loc['BASE'].to_dict(),'frozen_transfer':trans.loc[win].to_dict(),'FEB_frozen_plan_SHA':checksum(ROOT/'R00_078_PREDECLARED_PLAN.json'),'matched_R9_hour_day':h.to_dict('index'),'no_80_pct_if_accuracy_below':.80,'observed_accuracy':float(trans.loc[win,'accuracy']),'all_original_events':True,'no_exit_profit_blind_certification':True,'exposed_months_only':['2026-06','2026-07'],'unselected_hindsight_best_NOT_PROMOTED':str(trans.correct.idxmax())}
 (ROOT/'results'/'R00_078_COMPLETE_RESULT_RECEIPT.json').write_text(json.dumps(rec,indent=2)+'\n')
 print('COMPLETE',json.dumps(rec),flush=True)

if __name__=='__main__':
 action=sys.argv[1]
 if action=='derive':derive(sys.argv[2],sys.argv[3])
 elif action=='fit':fit(sys.argv[2])
 elif action=='score':score(sys.argv[2],sys.argv[3])
 elif action=='freeze':freeze()
 elif action=='finish':finish()
 else:raise ValueError(action)
