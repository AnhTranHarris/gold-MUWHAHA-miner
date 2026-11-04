"""R24 month-specific broker-conditioned competing-cause and WAIT learner.

Causal refers EXCLUSIVELY to the observed AS-OF input sigma algebra: all
training labels use historical *future* tick outcomes and the fitted same-month
model is severely IN-SAMPLE (cannot certify out-of-sample behavior). Never use
original R9 quota counts, future teacher side or outcome labels as inference
features. Maintains completely independent prospective BUY/SELL/WAIT actions.
"""
from __future__ import annotations
import argparse,gc,hashlib,json,time,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
import lightgbm as lgb
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r24_firstpass_engine as e
MODEL_EXTRA=('side_buy1_sellminus1','horizon_seconds')

def pfx(src,mon):
 return e.R24/'results'/src/mon/f'R24_{src}_{mon}_1000MS'

def load(src,mon):
 p=pfx(src,mon)
 return (np.load(str(p)+'_features.npy',mmap_mode='r'),
         np.load(str(p)+'_labels_2SIDE_3HORIZON.npy',mmap_mode='r'),
         np.load(str(p)+'_signal_utc_ms.npy',mmap_mode='r'))

def future_wait_label(labels,time):
 """Supervised 10s WAIT opportunity label; never available as model input."""
 current=np.any(labels[:,:,0]==1,axis=1)
 hit=np.flatnonzero(current)
 out=np.zeros(len(time),np.uint8)
 if not len(hit):return out
 ix=np.searchsorted(hit,np.arange(len(time),dtype=np.int64)+1)
 good=ix<len(hit)
 next_idx=hit[np.minimum(ix,len(hit)-1)]
 out[good]=((np.asarray(time)[next_idx[good]]-np.asarray(time)[good]<=10000)&(~current[good])).astype(np.uint8)
 return out

def fit_month(mon,per_source=100000,iterations=110):
 start=time.monotonic();mon=f'{int(mon):02d}';dest=e.R24/'models'/mon;dest.mkdir(exist_ok=True,parents=True)
 portions=[];targets=[];waitx=[];waity=[];samples=[];source_pins={}
 nfeatures=len(e.FEATURE_NAMES); nmax=per_source*len(e.SOURCE_NAMES)*6
 tensor=np.empty((nmax,nfeatures+2),np.float32)
 y=np.empty(nmax,np.int32);cursor=0
 wx=np.empty((per_source*len(e.SOURCE_NAMES),nfeatures),np.float32)
 wy=np.empty(per_source*len(e.SOURCE_NAMES),np.int32)
 wcur=0
 print('FIT_STARTED',mon,'train_max_rows',nmax,flush=True)
 for src in e.SOURCE_NAMES:
  X,L,T=load(src,mon)
  k=min(per_source,len(X))
  ix=np.linspace(0,len(X)-1,k,dtype=np.int64)
  samples.append((src,ix))
  source_pins[src]=e.source_pin(src,mon)
  wlabel=future_wait_label(L,T)
  wx[wcur:wcur+k]=X[ix];wy[wcur:wcur+k]=wlabel[ix];wcur+=k
  for side in (0,1):
   for h in range(3):
    stop=cursor+k
    tensor[cursor:stop,:nfeatures]=X[ix]
    tensor[cursor:stop,nfeatures]=1.0 if side==0 else -1.0
    tensor[cursor:stop,nfeatures+1]=float((15,30,60)[h])
    y[cursor:stop]=L[ix,side,h]
    cursor=stop
  print('FIT_TENSOR_POPULATED',src,'rows',len(X),'sample',k,'training_rows',cursor,'elapsed',round(time.monotonic()-start,2),flush=True)
  del X,L,T,wlabel
 if cursor==0:raise RuntimeError('NO_TRAIN_ROWS')
 tensor=tensor[:cursor];y=y[:cursor];wx=wx[:wcur];wy=wy[:wcur]
 if not np.isfinite(tensor).all():raise RuntimeError('NONFINITE_PREFIX_FEATURE')
 classes=np.bincount(y,minlength=5)
 if np.any(classes==0):
  # Refuse to silently merge CENSORED, UNFILLED or STOP into WAIT.
  raise RuntimeError('NONEMPTY_FIVE_CAUSE_CLASSES_REQUIRED '+str(classes))
 print('FIT_CLASSES',classes,'START_LIGHTGBM',flush=True)
 params={'objective':'multiclass','num_class':5,'metric':'multi_logloss','learning_rate':0.07,
  'num_leaves':48,'max_depth':-1,'min_data_in_leaf':180,'lambda_l2':7.0,
  'feature_fraction':0.88,'bagging_fraction':0.85,'bagging_freq':1,
  'max_bin':127,'num_threads':2,'verbosity':-1,'seed':20261104}
 feats=list(e.FEATURE_NAMES)+list(MODEL_EXTRA)
 train=lgb.Dataset(tensor,label=y,feature_name=feats,free_raw_data=True)
 model=lgb.train(params,train,num_boost_round=iterations)
 model_file=dest/'R24_FROZEN_BROKER_CONDITIONED_MULTISCALE_FIRSTPASS_5_CAUSE_LGBM.txt';model.save_model(str(model_file))
 print('FIT_MULTISCALE_CAUSES_COMPLETED',mon,'elapsed',round(time.monotonic()-start,2),flush=True)
 del tensor,y,train;gc.collect()
 if np.unique(wy).size!=2:raise RuntimeError('WAIT_LABEL_SINGLE_CLASS')
 p2={'objective':'binary','metric':'binary_logloss','learning_rate':0.07,'num_leaves':31,
   'min_data_in_leaf':180,'lambda_l2':9.0,'max_bin':127,'num_threads':2,'verbosity':-1,
   'seed':20261104,'feature_fraction':0.88}
 wait=lgb.train(p2,lgb.Dataset(wx,label=wy,feature_name=list(e.FEATURE_NAMES),free_raw_data=True),num_boost_round=max(55,iterations//2))
 wait_file=dest/'R24_FROZEN_OPPORTUNITY_WAIT10S_LGBM.txt';wait.save_model(str(wait_file))
 print('FIT_WAIT_HAZARD_COMPLETED',mon,'elapsed',round(time.monotonic()-start,2),flush=True)
 np.savez_compressed(dest/'R24_FROZEN_FULL_TRAINING_SOURCE_SAMPLE_INDICES_AND_CAUSE_RECEIPT.npz',
     **{k+'_ORIGINAL_ASOF_SIGNAL_TRAINING_ROW_INDEX':v for k,v in samples},
     original_future_cause_training_sample_histogram=classes,wait_label_histogram=np.bincount(wy,minlength=2),
     feature_names=np.asarray(feats))
 rec={'status':'COMPLETE_MONTH_SPECIFIC_SUPERVISED_IN_SAMPLE_HINDSIGHT_DISTILLATION_NOT_OOS',
   'month':mon,'source':list(e.SOURCE_NAMES),'historical_full_raw_tick_source_sha256':source_pins,
   'candidate_training_sample_count_per_broker':per_source,
   'actual_multiclass_rows':int(cursor),'competing_firstpass_causes':e.CLASS_NAMES,
   'side_head_indicator':MODEL_EXTRA[0],'event_risk_horizons_seconds':[15,30,60],
   'full_47_causal_asof_feature_schema':e.FEATURE_NAMES,
   'five_class_training_histogram':classes.tolist(),'wait_future_opportunity_10sec_training_label_histogram':np.bincount(wy,minlength=2).tolist(),
   'future_labels_NEVER_in_inference_features':True,'no_R9_quota_in_model_features':True,
   'monthly_fit_and_monthly_selection_HEAVY_IN_SAMPLE':True,'no_genuine_out_of_sample':True,
   'both_broker_feeds_trained_together_month_conditioned':True,
   'news_impact_unknown_no_MT5_original_export':True,
   'not_MT5_live_broker_order_fill':True,'seconds':round(time.monotonic()-start,3),
   'artifacts':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()} for p in (model_file,wait_file,dest/'R24_FROZEN_FULL_TRAINING_SOURCE_SAMPLE_INDICES_AND_CAUSE_RECEIPT.npz')}}
 (dest/'R24_MONTHLY_HAZARD_FIT_SOURCE_MODEL_SHA_RECEIPT.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 print('FIT_MONTH_RECEIPT',json.dumps({k:v for k,v in rec.items() if k not in ('full_47_causal_asof_feature_schema','artifacts')},indent=2),flush=True)
 return rec

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--month',choices=('01','02','06','07'),required=True);
 p.add_argument('--sample-per-broker',type=int,default=100000);p.add_argument('--iterations',type=int,default=110)
 a=p.parse_args();fit_month(a.month,a.sample_per_broker,a.iterations)
