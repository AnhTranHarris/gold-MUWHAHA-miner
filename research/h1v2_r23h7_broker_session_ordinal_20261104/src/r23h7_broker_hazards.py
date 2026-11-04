"""R23H-0007: broker-specific exact quote-ordinal competing hazards.

ADDITIVE INSAMPLE research only: original R23/R24/R23H24 frozen artifacts untouched.
Five distinct first-passage outcomes: STOP, TARGET, EVENT_FREE, OBSERVED_GAP,
SOURCE_END_UNOBSERVED; independent HELD_H and WAIT10 heads. H=15,30,60s.
Predictor features are quoted BID/ASK prefix, exact ordinal micro path, UTC/DST
nominal clock proxies, side/horizon. No future outcomes, quote gaps from future,
or R9 quota/time bucket targets are supplied as model inputs.
Per-source-month fitting remains in-sample: model weights know outcomes of that month.
This is NOT an online deployable policy, blind OOS, prop authorization, or cash PnL.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, sys
from pathlib import Path
import numpy as np
import lightgbm as lgb

BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).resolve()
sys.path.insert(0,str(BASE/'r24_source_archive'/'source'))
sys.path.insert(0,str(BASE/'new_source'))
from r23h24_competing_hazard import source_arrays, prefix_features
import r24_firstpass_engine as original
from r23h7_quote_grammar import quote_path_features,PATH_NAMES
from r23h7_clock_news import clock_features,CLOCK_NAMES
SOURCE=('DUKASCOPY_RAW','MT5_BROKER_EXPORT')
HORIZONS_MS=(15000,30000,60000)
CAUSES=('STOP_FIRST','TARGET_FIRST','EVENT_FREE','OBSERVED_GAP','SOURCE_END_CENSORED')
FEAT_COUNT=57+len(PATH_NAMES)+len(CLOCK_NAMES)


def sha(file):
 with open(file,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def day_balanced_sample(t,cap_per_day=256,seed=20261104):
 """One source-month fit draws deterministic <=cap signals per occupied UTC day."""
 if cap_per_day<=0:raise ValueError('INVALID_DAY_SAMPLE_CAP')
 t=np.asarray(t,dtype=np.int64)
 days=t//86400000
 _,starts=np.unique(days,return_index=True)
 ends=np.r_[starts[1:],len(t)]
 out=[]
 for j,(a,b) in enumerate(zip(starts,ends)):
  take=min(cap_per_day,b-a)
  if take==b-a:out.append(np.arange(a,b,dtype=np.int32));continue
  rng=np.random.default_rng(seed+j)
  # Day-internal time partitions; not only high-volume source regions.
  edges=np.linspace(a,b,take+1,dtype=np.int64)
  out.append(np.asarray([rng.integers(edges[i],edges[i+1]) if edges[i+1]>edges[i] else edges[i] for i in range(take)],dtype=np.int32))
 return np.concatenate(out) if out else np.empty(0,np.int32)


def prefix_matrix(arr,t,b,ask,indices):
 idx=np.asarray(indices,dtype=np.int32)
 x=prefix_features(arr['x'][idx],arr['t'][idx])
 path=quote_path_features(t,b,ask,arr['s'][idx])
 clock=clock_features(arr['t'][idx])
 out=np.ascontiguousarray(np.column_stack((x,path,clock)),dtype=np.float32)
 assert out.shape==(len(idx),FEAT_COUNT)
 assert np.isfinite(out).all()
 return out


def split_censored_gap(label,fill,t):
 """Differentiate original R24 3 = gap OR source-end.

    Only offline target construction may look forward. No result used by runtime features.
    A censored label with a verified post-fill observed 15s quote drought is GAP,
    otherwise SOURCE_END_CENSORED; never silently impute a negative or good trade.
 """
 src=np.asarray(t,dtype=np.int64)
 n=len(fill);f=np.asarray(fill,dtype=np.int32)
 out=np.array(label,dtype=np.int8,copy=True)
 assert out.shape==(n,2,3)
 gap_indexes=np.flatnonzero(np.diff(src)>15000).astype(np.int32)+1
 gpos=np.searchsorted(gap_indexes,np.maximum(f,0)+1,side='left')
 nextgap=np.full(n,len(src),np.int32)
 ok=gpos<len(gap_indexes)
 nextgap[ok]=gap_indexes[gpos[ok]]
 ff=np.maximum(f,0)
 for j,h in enumerate(HORIZONS_MS):
  deadline=src[ff]+h
  horizon_index=np.searchsorted(src,deadline,side='left')
  # In original R24, label 3 can come from a quote gap whose first post-gap
  # quote falls >15s beyond the intended horizon.
  gap_is_within=(nextgap<len(src))&(src[nextgap.clip(max=len(src)-1)]-src[np.maximum(nextgap-1,0)]>15000)&(src[np.maximum(nextgap-1,0)]<deadline)
  for side in range(2):
   cens=out[:,side,j]==3
   out[cens&~gap_is_within,side,j]=4
 # Original unfilled label 4 is still unfilled, and excluded from training by f>=0.
 return out


def train_source_month(source,month,cap_per_day=320,rounds=35,replace=False):
 if source not in SOURCE or month not in ('01','02','06','07'):raise ValueError('INVALID_FROZEN_SOURCE_MONTH')
 modeldir=BASE/'r23h7_models'/source/month
 receiptpath=modeldir/'R23H7_FIT_RECEIPT.json'
 if receiptpath.exists() and not replace:
  info=json.loads(receiptpath.read_text())
  for item in info['models'].values():
   p=modeldir/item['name'];assert p.is_file() and sha(p)==item['sha256'],'FROZEN_MODEL_SHA_CONFLICT'
  assert info['source']==source and info['month']==month
  return info
 modeldir.mkdir(parents=True,exist_ok=True)
 arr=source_arrays(source,month)
 # Original frozen 47-dimensional source feature 0 *already* flags broker.
 broker=int(source=='MT5_BROKER_EXPORT')
 assert arr['x'].shape[1]==47
 assert np.all(np.asarray(arr['x'][::max(len(arr['x'])//1000,1),0])==broker),'PARENT_BROKER_FEATURE_PIN_DRIFT'
 rawpath=original.source_file(source,month)
 t,b,ask=original.raw_month(source,month,verify=True)
 sample=day_balanced_sample(arr['t'],cap_per_day,seed=int(month)*400+(5 if broker else 1))
 if len(sample)<100:raise AssertionError('INSUFFICIENT_MONTH_SAMPLE')
 x=prefix_matrix(arr,t,b,ask,sample)
 f=np.asarray(arr['f'][sample]);labels=split_censored_gap(arr['l'][sample],f,t)
 samples=[];yy=[];srows=[];hy=[]
 held=np.asarray(arr['held'][sample])
 for side in range(2):
  for stage in range(3):
   at_risk=f>=0 if stage==0 else labels[:,side,stage-1]==2
   iii=np.flatnonzero(at_risk)
   if len(iii):
    z=np.column_stack((x[iii],np.full(len(iii),side,np.float32),np.full(len(iii),stage,np.float32)))
    samples.append(z);yy.append(labels[iii,side,stage])
   eligible=np.flatnonzero(held[:,side,stage]<2)
   if len(eligible):
    srows.append(np.column_stack((x[eligible],np.full(len(eligible),side,np.float32),np.full(len(eligible),stage,np.float32))))
    hy.append(held[eligible,side,stage])
 training=np.vstack(samples);y=np.concatenate(yy);htrain=np.vstack(srows);hlabels=np.concatenate(hy)
 assert training.shape[1]==FEAT_COUNT+2 and np.max(y)<5
 # WAIT10 training horizon label is future-only (strict supervised response).
 nextindex=np.searchsorted(arr['t'],arr['t'][sample]+10000,side='left')
 q=np.minimum(nextindex,len(arr['t'])-1)
 eligible=(nextindex<len(arr['t']))&(arr['t'][q]-(arr['t'][sample]+10000)<=1000)
 # Class 1 means there is a first-target action available 10sec later.
 waitlabel=np.any(np.asarray(arr['l'][q[eligible],:,0])==1,axis=1).astype(np.int8)
 assert len(waitlabel)>0
 opts={'learning_rate':0.055,'max_depth':7,'num_leaves':31,'min_data_in_leaf':120,'lambda_l2':14.0,
       'verbosity':-1,'num_threads':2,'feature_pre_filter':False,'seed':int(month)*30+broker}
 booster=lgb.train(opts|{'objective':'multiclass','num_class':5},lgb.Dataset(training,label=y),num_boost_round=rounds)
 hold=lgb.train(opts|{'objective':'binary'},lgb.Dataset(htrain,label=hlabels),num_boost_round=rounds)
 wait=lgb.train(opts|{'objective':'binary'},lgb.Dataset(x[eligible],label=waitlabel),num_boost_round=rounds)
 files={}
 for name,mdl in (('CAUSE5',booster),('HOLD',hold),('WAIT10',wait)):
  p=modeldir/f'R23H7_{source}_{month}_{name}.txt';tmp=p.with_suffix('.tmp');mdl.save_model(str(tmp));os.replace(tmp,p)
  files[name]={'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size}
 weights=booster.predict(training[:min(1000,len(training))],num_threads=2)
 assert np.all(np.isfinite(weights)) and np.max(np.abs(weights.sum(axis=1)-1))<1e-5
 r={'status':'FITTED_SOURCE_SPECIFIC_INSAMPLE_ONLY','source':source,'month':month,'rounds':rounds,
    'sampled_signals':len(sample),'source_signal_population':len(arr['t']),
    'original_source_gz_sha256':sha(rawpath),'original_quote_rows':len(t),
    'broker_column_original_R24_feature0':broker,'source_splits':'INDEPENDENT_BROKER_SPECIALISTS',
    'feature_count_before_side_and_h':FEAT_COUNT,'feature_names_path':list(PATH_NAMES),
    'feature_names_clock':list(CLOCK_NAMES),'five_cause_classes':list(CAUSES),
    'class_count':np.bincount(y,minlength=5).tolist(),'training_cause_rows':len(y),
    'held_count':np.bincount(hlabels,minlength=2).tolist(),'training_held_rows':len(hlabels),
    'wait10_count':np.bincount(waitlabel,minlength=2).tolist(),'training_wait_rows':len(waitlabel),
    'models':files,'future_outcomes_are_OFFLINE_SUPERVISION_ONLY':True,
    'source_end_distinct_from_quote_gap':True,'market_session_proxy_not_broker_permission':True,
    'news_state':'UNKNOWN_UNVERIFIED_ASOF','no_OOS':True,'no_executable_cash_pnl':True}
 tmp=receiptpath.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');os.replace(tmp,receiptpath)
 return r


def evaluate_day(source,month,day,overwrite=False):
 modeldir=BASE/'r23h7_models'/source/month
 info=json.loads((modeldir/'R23H7_FIT_RECEIPT.json').read_text())
 models={key:lgb.Booster(model_file=str(modeldir/rec['name'])) for key,rec in info['models'].items()}
 arr=source_arrays(source,month)
 d=datetime.datetime(2026,int(month),day,tzinfo=datetime.timezone.utc)
 begin=int(d.timestamp()*1000);end=begin+86400000
 lo=int(np.searchsorted(arr['t'],begin));hi=int(np.searchsorted(arr['t'],end));n=hi-lo
 target=BASE/'r23h7_scores'/source/month/f'R23H7_{source}_{month}_{day:02d}_PREDICTIONS.npz'
 recfile=target.with_suffix('.receipt.json')
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and recfile.exists() and not overwrite:
  old=json.loads(recfile.read_text());assert old['sha256']==sha(target) and old['start_row']==lo and old['end_row']==hi
  return old
 if n:
  t,b,a=original.raw_month(source,month,verify=True)
  x=prefix_matrix(arr,t,b,a,np.arange(lo,hi,dtype=np.int32))
  cause=np.zeros((n,2,3,5),np.float32);held=np.zeros((n,2,3),np.float32)
  for side in range(2):
   remaining=np.ones(n,np.float64)
   for stage in range(3):
    pred=np.column_stack((x,np.full(n,side,np.float32),np.full(n,stage,np.float32)))
    cc=models['CAUSE5'].predict(pred,num_threads=2)
    if stage:cause[:,side,stage]=cause[:,side,stage-1]
    for k in (0,1,3,4):cause[:,side,stage,k]+=remaining*cc[:,k]
    remaining=remaining*cc[:,2]
    cause[:,side,stage,2]=remaining
    held[:,side,stage]=models['HOLD'].predict(pred,num_threads=2)
   held[:,side,:]=np.minimum.accumulate(held[:,side,:],axis=1)
  wait=models['WAIT10'].predict(x,num_threads=2).astype(np.float32)
  assert np.max(np.abs(cause.sum(axis=3)-1))<1e-4
  assert np.min(np.diff(cause[:,:,:,1],axis=2))>=-1e-5
 else:
  cause=np.zeros((0,2,3,5),np.float32);held=np.zeros((0,2,3),np.float32);wait=np.zeros(0,np.float32)
 tmp=target.with_suffix('.tmp')
 with tmp.open('wb') as f:np.savez_compressed(f,cause5=cause,held=held,wait10=wait)
 os.replace(tmp,target)
 rec={'source':source,'month':month,'day':day,'rows':n,'start_row':lo,'end_row':hi,
      'sha256':sha(target),'model_receipt_sha256':sha(modeldir/'R23H7_FIT_RECEIPT.json'),
      'market_clock':'IANA_PROXY_ONLY','news':'UNKNOWN_NO_AUTHENTICATED_ASOF_SNAPSHOT',
      'is_full_month_replay':False,'is_in_sample':True,'no_profit_or_accuracy_claim':True}
 tmp=recfile.with_suffix('.tmp');tmp.write_text(json.dumps(rec,indent=2)+'\n');os.replace(tmp,recfile)
 return rec


if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('--source',choices=SOURCE,required=True);ap.add_argument('--month',choices=('01','02','06','07'),required=True)
 ap.add_argument('--mode',choices=('fit','score_day'),required=True);ap.add_argument('--day',type=int,default=2)
 ap.add_argument('--cap-per-day',type=int,default=320);ap.add_argument('--rounds',type=int,default=35)
 a=ap.parse_args()
 if a.mode=='fit':r=train_source_month(a.source,a.month,a.cap_per_day,a.rounds)
 else:r=evaluate_day(a.source,a.month,a.day)
 print(json.dumps(r,indent=2,allow_nan=False),flush=True)
