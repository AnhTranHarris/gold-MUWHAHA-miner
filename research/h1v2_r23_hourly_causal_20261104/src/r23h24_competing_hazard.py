"""R23H24: month-specific TWO-FEED-POOLED, *in-sample* causal-prefix hazard fit.
This is an ADDITIVE research experiment. Source data/code R9/R11/R23/R24 are NEVER edited.

OBSERVABLE at action: historical quote-prefix features and UTC clock. BROKER ID IS NOT YET A MODEL COLUMN; the same month-specific weights are scored independently on each feed.
OFFLINE TARGETS ONLY: future first TARGET / STOP / GAP-CENSOR / TIMEOUT,
subsequent H=15/30/60s full adverse-survival, and the observed WAIT10 label.
The trained in-sample model is NOT a causal OOS claim nor an approved EA.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from pathlib import Path
import numpy as np
import lightgbm as lgb
BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).expanduser().resolve()
sys.path.insert(0,str(BASE/'r24_source_archive'/'source'))
import r24_firstpass_engine as src
FEEDS=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
H=(15,30,60)
CAUSE=('STOP','TARGET','EVENT_FREE','GAP_CENSORED')
FEATURE_CONTRACT='R23H24_R24_ORIGINAL_PAST_ONLY_45_PLUS_12_PREFIX_RATIOS_AND_CLOCK'

def source_arrays(source,mon):
 d=BASE/'prepared/results'/source/mon
 stem=f'R24_{source}_{mon}_1000MS'
 h=BASE/'held'/source/mon
 return {'x':np.load(d/(stem+'_features.npy'),mmap_mode='r'),
         'l':np.load(d/(stem+'_labels_2SIDE_3HORIZON.npy'),mmap_mode='r'),
         't':np.load(d/(stem+'_signal_utc_ms.npy'),mmap_mode='r'),
         's':np.load(d/(stem+'_source_quote_ordinal.npy'),mmap_mode='r'),
         'f':np.load(d/(stem+'_fill_source_quote_ordinal.npy'),mmap_mode='r'),
         'e':np.load(d/(stem+'_first_event_source_quote_ordinal.npy'),mmap_mode='r'),
         'held':np.load(h/(stem+'_HELD.npy'),mmap_mode='r'),
         'stop_ix':np.load(h/(stem+'_FIRST_STOP_SOURCE_ORDINAL.npy'),mmap_mode='r'),
         'end_ix':np.load(h/(stem+'_FIRST_HORIZON_QUOTE_ORDINAL.npy'),mmap_mode='r')}

def prefix_features(raw, time_ms):
 """Transform already source-verified R24 prefix-only observable vectors.
 No post-action future, R9 quotas, historical oracle membership or news fields.
 """
 z=np.asarray(raw,dtype=np.float32)
 use=np.r_[np.arange(44),[46]]
 x=z[:,use]
 def col(k):return z[:,k]
 def signed_div(n,d):return n/(100.0+np.maximum(np.abs(d),0))
 dayphase=((time_ms//60000)%1440).astype(np.float32)
 quarter=((time_ms//60000)%15).astype(np.float32)
 extras=[
 signed_div(col(5),col(15)),signed_div(col(6),col(15)),
 signed_div(col(7),col(16)),signed_div(col(8),col(16)),
 signed_div(col(9),col(17)),signed_div(col(10),col(17)),
 col(5)*col(6)/(100.0+np.abs(col(5)*col(6))),
 col(7)*col(8)/(100.0+np.abs(col(7)*col(8))),
 np.log1p(np.maximum(0,col(19)))/(1+np.log1p(np.maximum(0,col(20)))),
 np.log1p(np.maximum(0,col(21)))/(1+np.log1p(np.maximum(0,col(22)))),
 np.sin(quarter*np.float32(2*np.pi/15)),
 np.cos(quarter*np.float32(2*np.pi/15)),
 ]
 return np.ascontiguousarray(np.column_stack([x]+extras),dtype=np.float32)

def sampled_indices(n,limit,seed):
 if n<=limit:return np.arange(n,dtype=np.int32)
 rng=np.random.default_rng(seed)
 # Stratified by calendar time, avoids selecting only one source regime.
 edges=np.linspace(0,n,limit+1,dtype=np.int64)
 return np.fromiter((rng.integers(edges[i],edges[i+1]) if edges[i+1]>edges[i] else edges[i] for i in range(limit)),np.int32,count=limit)

def build_cause_training(a,ix):
 fx=prefix_features(a['x'][ix],a['t'][ix])
 label=np.asarray(a['l'][ix])
 rows=[];ys=[]
 for side in range(2):
  for stage in range(3):
   # For subsequent hazard intervals, only still-at-risk paths are included.
   active=(a['f'][ix]>=0) if stage==0 else (label[:,side,stage-1]==2)
   idx=np.flatnonzero(active)
   if not len(idx):continue
   f=np.column_stack((fx[idx],np.full(len(idx),side,np.float32),np.full(len(idx),stage,np.float32)))
   y=label[idx,side,stage]
   keep=(y<=3)
   rows.append(f[keep]);ys.append(y[keep])
 return np.vstack(rows),np.concatenate(ys)

def build_held_training(a,ix):
 fx=prefix_features(a['x'][ix],a['t'][ix]); y=np.asarray(a['held'][ix]);rows=[];ys=[]
 for side in range(2):
  for stage in range(3):
   active=y[:,side,stage]<2
   ind=np.flatnonzero(active)
   if not len(ind):continue
   rows.append(np.column_stack((fx[ind],np.full(len(ind),side,np.float32),np.full(len(ind),stage,np.float32))))
   ys.append(y[ind,side,stage])
 return np.vstack(rows),np.concatenate(ys)

def build_wait_training(a,ix):
 future=np.searchsorted(a['t'],a['t'][ix]+10000,side='left')
 valid=future<len(a['t'])
 ff=np.minimum(future,len(a['t'])-1)
 valid &= (a['t'][ff]-(a['t'][ix]+10000)<=1000)
 # Future side outcomes here are SUPERVISED RESPONSE ONLY, never a decision feature.
 good=np.any(np.asarray(a['l'][ff,:,0])==1,axis=1)
 return prefix_features(a['x'][ix[valid]],a['t'][ix[valid]]),good[valid].astype(np.int8)

def fit_month(mon,limit=25000,rounds=48):
 modeldir=BASE/'models'/mon;modeldir.mkdir(exist_ok=True,parents=True)
 data={s:source_arrays(s,mon) for s in FEEDS}
 train=[];labels=[];ht=[];hy=[];wt=[];wy=[];detail=[]
 for k,(s,a) in enumerate(data.items()):
  ix=sampled_indices(len(a['t']),limit,seed=int(mon)*100+7*k)
  x,y=build_cause_training(a,ix);train.append(x);labels.append(y)
  xx,yy=build_held_training(a,ix);ht.append(xx);hy.append(yy)
  ww,wz=build_wait_training(a,ix);wt.append(ww);wy.append(wz)
  detail.append({'source':s,'sampled_asof_signals':len(ix),'stage_rows':len(y),'held_rows':len(yy),'wait10_rows':len(wz),
                 'stage_counts':np.bincount(y,minlength=4).tolist(),'held_counts':np.bincount(yy,minlength=2).tolist(),'wait_counts':np.bincount(wz,minlength=2).tolist()})
 base={'learning_rate':0.06,'num_leaves':31,'max_depth':7,'min_data_in_leaf':160,'lambda_l2':15.0,
       'feature_fraction':0.85,'bagging_fraction':0.9,'bagging_freq':1,'verbosity':-1,'num_threads':2,
       'seed':int(mon),'feature_pre_filter':False}
 x=np.vstack(train);y=np.concatenate(labels)
 assert x.shape[1]==59 and set(np.unique(y)).issubset({0,1,2,3})
 hazard=lgb.train(base|{'objective':'multiclass','num_class':4},lgb.Dataset(x,label=y),num_boost_round=rounds)
 del x,y,train,labels
 held=lgb.train(base|{'objective':'binary'},lgb.Dataset(np.vstack(ht),label=np.concatenate(hy)),num_boost_round=rounds)
 del ht,hy
 wait=lgb.train(base|{'objective':'binary'},lgb.Dataset(np.vstack(wt),label=np.concatenate(wy)),num_boost_round=rounds)
 models={'hazard':hazard,'held':held,'wait10':wait}
 files={}
 for name,m in models.items():
  f=modeldir/f'R23H24_{mon}_{name.upper()}.txt';m.save_model(str(f));files[name]={'name':f.name,'sha256':hashlib.file_digest(f.open('rb'),'sha256').hexdigest()}
 receipt={'month':mon,'status':'FITTED_INSAMPLE_ONLY','source_signal_limit_PER_BROKER':limit,
          'original_all_inference_rows':{s:len(a['t']) for s,a in data.items()},'rounds':rounds,'class_names':CAUSE,
          'feature_contract':FEATURE_CONTRACT,'feature_count_hazard_hold':59,'feature_count_wait':57,
          'training_rows':detail,'fit_model_files':files,'no_future_quote_or_quota_in_training_features':True,
          'all_original_experiments_preserved':True,'no_OOS_or_real_account_claim':True}
 f=modeldir/f'R23H24_{mon}_MODEL_SHA_RECEIPT.json';f.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'month':mon,'models':files,'training':detail},indent=2),flush=True)
 return receipt

def load_models(mon):
 d=BASE/'models'/mon
 return (lgb.Booster(model_file=str(d/f'R23H24_{mon}_HAZARD.txt')),
         lgb.Booster(model_file=str(d/f'R23H24_{mon}_HELD.txt')),
         lgb.Booster(model_file=str(d/f'R23H24_{mon}_WAIT10.txt')))

def infer_source(s,mon,batch=50000):
 h,held,wait=load_models(mon);a=source_arrays(s,mon);n=len(a['t'])
 out=BASE/'scores'/s/mon;out.mkdir(exist_ok=True,parents=True)
 # stage risk decomposition: target+stop+event_free+gap_censored=1
 target=np.zeros((n,2,3),np.float32);stop=np.zeros_like(target)
 gap=np.zeros_like(target);surv=np.zeros_like(target)
 waitscore=np.zeros(n,np.float32)
 for l in range(0,n,batch):
  r=min(n,l+batch)
  fx=prefix_features(a['x'][l:r],a['t'][l:r]);waitscore[l:r]=wait.predict(fx,num_threads=2)
  for side in range(2):
   pprev=np.ones(r-l,np.float64)
   for stage in range(3):
    X=np.column_stack((fx,np.full(r-l,side,np.float32),np.full(r-l,stage,np.float32)))
    z=h.predict(X,num_threads=2)
    target[l:r,side,stage]=target[l:r,side,stage-1] if stage else 0
    stop[l:r,side,stage]=stop[l:r,side,stage-1] if stage else 0
    gap[l:r,side,stage]=gap[l:r,side,stage-1] if stage else 0
    target[l:r,side,stage]+=pprev*z[:,1]
    stop[l:r,side,stage]+=pprev*z[:,0]
    gap[l:r,side,stage]+=pprev*z[:,3]
    pprev*=z[:,2]
    surv[l:r,side,stage]=held.predict(X,num_threads=2)
   # Full-H survival cannot increase with H; numerical projection prevents contradictions.
   surv[l:r,side,:]=np.minimum.accumulate(surv[l:r,side,:],axis=1)
  if l==0 or r==n:print('INFER_PROGRESS',s,mon,l,r,n,flush=True)
 for name,z in [('target',target),('stop',stop),('gap',gap),('held',surv),('wait10',waitscore)]:
  file=out/f'R23H24_{s}_{mon}_{name}_FULL_ASOF.npy'
  with file.with_suffix('.tmp').open('wb') as f:np.save(f,z,allow_pickle=False)
  os.replace(file.with_suffix('.tmp'),file)
 assert np.all(np.diff(target,axis=2)>=-1.e-6)
 assert np.all(np.diff(stop,axis=2)>=-1.e-6)
 assert np.all(np.diff(gap,axis=2)>=-1.e-6)
 assert np.all(np.diff(surv,axis=2)<=1.e-6)
 receipt={'source':s,'month':mon,'inferred_rows':n,'model_sha_receipt':str(BASE/'models'/mon/f'R23H24_{mon}_MODEL_SHA_RECEIPT.json'),
  'feature_contract':FEATURE_CONTRACT,'full_calendar_inference':True,'oracle_membership_not_input':True,'files':{f.name:hashlib.file_digest(f.open('rb'),'sha256').hexdigest() for f in out.glob('*.npy')},
  'positive_in_sample_NOT_deployable':True}
 (out/f'R23H24_{s}_{mon}_ATOMIC_SCORE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('INFER_COMPLETE',s,mon,n,flush=True)
 return receipt

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--month',choices=('01','02','06','07'),required=True)
 ap.add_argument('--mode',choices=('fit','infer'),required=True)
 ap.add_argument('--source',choices=FEEDS);ap.add_argument('--limit',type=int,default=25000)
 a=ap.parse_args()
 if a.mode=='fit':fit_month(a.month,limit=a.limit)
 else:
  if not a.source:ap.error('infer needs --source')
  infer_source(a.source,a.month)
