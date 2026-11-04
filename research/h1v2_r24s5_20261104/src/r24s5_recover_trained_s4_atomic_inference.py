"""Additive R24S5 restart-safe, SHA-guarded chunked inference of an ALREADY-FITTED R24S4 model.

This replays exactly R24S4's model/feature/side/horizon predictor on genuinely past-only 47+17
feature rows. Labels are NEVER loaded. No future-selected side is present, no R9 quota input.
Complete score .npy path is only promoted after all block checks and original-row coverage.
Do not use this output for live execution or claim performance validation without full replay.
"""
from __future__ import annotations
import sys,os,json,hashlib,argparse,datetime
from pathlib import Path
import numpy as np
import lightgbm as lgb
sys.path[:0]=['/mnt/data/h1v2_r24s4_entry_specialists/src','/mnt/data/h1v2_r24_asof/source']
import r24s4_broker_hazard_specialist as sp
import r24_firstpass_engine as e
ROOT=Path('/mnt/data/h1v2_r24s4_entry_specialists')
RESEARCH=Path('/mnt/data/h1v2_r24s5')
BLOCK=32768

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()

def run(source,mon,max_blocks=8,verify_only=False):
 d=ROOT/'results'/source/mon;d.mkdir(parents=True,exist_ok=True)
 src=e.source_file(source,mon)
 if sha(src)!=e.source_pin(source,mon):raise ValueError('RAW_SHA_MISMATCH')
 p=sp.inputpaths(source,mon);x=np.load(str(p)+'_features.npy',mmap_mode='r')
 n=len(x);shape=(n,2,3,5)
 model=d/f'R24S4_{source}_{mon}_BROKER_ONLY_MULTISCALE_CROSS_PRODUCT_5_CAUSE_LGBM.txt'
 waitmodel=d/f'R24S4_{source}_{mon}_BROKER_ONLY_WAIT10_HAZARD.txt'
 trainidx=d/f'R24S4_{source}_{mon}_TRAINING_ROW_INDICES.npy'
 for q in (model,waitmodel,trainidx):
  if not q.is_file():raise ValueError('TRAINING_ARTIFACT_MISSING '+str(q))
 stamp={'raw_sha':e.source_pin(source,mon),'features_sha':sha(str(p)+'_features.npy'),
  'model_sha':sha(model),'waitmodel_sha':sha(waitmodel),'train_indices_sha':sha(trainidx),
  'source':source,'month':mon,'size':n,'block_size':BLOCK,
  'feature_schema_names':list(e.FEATURE_NAMES)+list(sp.EXTRA_NAMES)}
 target=d/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_HAZARD_PROBABILITIES.npy'
 wtarget=d/f'R24S4_{source}_{mon}_FROZEN_IN_SAMPLE_WAIT_PROBABILITIES.npy'
 ppartial=Path(str(target)+'.PARTIAL');wpartial=Path(str(wtarget)+'.PARTIAL')
 checkpoint=d/f'R24S5_{source}_{mon}_ATOMIC_CHUNK_INFERENCE_PROGRESS.json'
 state=json.loads(checkpoint.read_text()) if checkpoint.exists() else {'stamp':stamp,'completed_blocks':{}}
 if state['stamp']!=stamp:raise ValueError('CHECKPOINT_SOURCE_MODEL_SCHEMA_DRIFT')
 total=(n+BLOCK-1)//BLOCK
 P=np.lib.format.open_memmap(ppartial,mode='r+' if ppartial.exists() else 'w+',dtype=np.float32,shape=shape)
 W=np.lib.format.open_memmap(wpartial,mode='r+' if wpartial.exists() else 'w+',dtype=np.float32,shape=(n,))
 m=lgb.Booster(model_file=str(model));w=lgb.Booster(model_file=str(waitmodel))
 jobs=0
 for bi in range(total):
  l=bi*BLOCK;r=min(n,(bi+1)*BLOCK)
  key=str(bi)
  if key in state['completed_blocks']:
   a=state['completed_blocks'][key]
   if a['start']!=l or a['stop']!=r:raise ValueError('CHECKPOINT_PARTITION_DRIFT')
   # No reusing a checkpoint if locally stored chunk changed, even when overall .npy is unfinished.
   ph=hashlib.sha256(P[l:r].tobytes()).hexdigest();wh=hashlib.sha256(W[l:r].tobytes()).hexdigest()
   if (a['P_sha256'],a['W_sha256'])!=(ph,wh):raise ValueError('CHECKPOINT_BLOCK_BYTE_MISMATCH '+key)
   continue
  if verify_only:continue
  X=np.concatenate([np.asarray(x[l:r],np.float32),sp.enhanced_prefix(x[l:r])],axis=1)
  if X.shape[1]!=len(e.FEATURE_NAMES)+len(sp.EXTRA_NAMES):raise AssertionError('FEATURE_DIM')
  W[l:r]=w.predict(X,num_threads=3).astype(np.float32)
  xx=np.empty((len(X),X.shape[1]+2),np.float32)
  xx[:,:-2]=X
  for side in range(2):
   xx[:,-2]=1 if side==0 else -1
   for hi,h in enumerate((15,30,60)):
    xx[:,-1]=h
    P[l:r,side,hi,:]=m.predict(xx,num_threads=3).astype(np.float32)
  if not np.isfinite(P[l:r]).all() or not np.isfinite(W[l:r]).all():raise RuntimeError('NONFINITE_PREDICTION')
  if not np.allclose(P[l:r].sum(axis=-1),1,atol=1e-4):raise RuntimeError('NON_NORMALIZED_COMPETING_HAZARD')
  P.flush();W.flush()
  a={'start':l,'stop':r,'P_sha256':hashlib.sha256(P[l:r].tobytes()).hexdigest(),
     'W_sha256':hashlib.sha256(W[l:r].tobytes()).hexdigest()}
  state['completed_blocks'][key]=a
  tmp=Path(str(checkpoint)+'.TMP');tmp.write_text(json.dumps(state,indent=2));os.replace(tmp,checkpoint)
  jobs+=1
  print('R24S5_COMPLETE_CHECKPOINT_BLOCK',source,mon,bi+1,'/',total,flush=True)
  if jobs>=max_blocks:break
 done=len(state['completed_blocks'])==total
 if done:
  if not np.isfinite(P).all() or not np.isfinite(W).all():raise RuntimeError('NONFINITE_FULL_FROZEN_PROBA')
  if not np.allclose(P[::max(1,n//3000)].sum(axis=-1),1,atol=1e-4):raise RuntimeError('NONNORMALIZED_FULL_P')
  del P,W
  os.replace(ppartial,target);os.replace(wpartial,wtarget)
  receipt={'status':'COMPLETE_SOURCE_EXACT_ADD_ONLY_RESUMABLE_INFERENCE','source':source,'month':mon,
    'model_and_source_stamps':stamp,'blocks_verified':total,
    'probability_file_sha':sha(target),'WAIT_probability_sha':sha(wtarget),
    'no_target_or_R9_feature_or_future_side_used_in_inference':True,
    'in_sample_training_month_exposed':True}
  dest=d/f'R24S5_{source}_{mon}_RESUMABLE_INFERENCE_ATOMIC_FINAL_RECEIPT.json';dest.write_text(json.dumps(receipt,indent=2)+'\n')
  print('R24S5_FROZEN_INFERENCE_COMPLETE',json.dumps(receipt),flush=True)
 else:
  print('R24S5_INFERENCE_PARTIAL',source,mon,'completed',len(state['completed_blocks']),'of',total,flush=True)
 return done

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--source',default='DUKASCOPY_RAW');parser.add_argument('--month',default='06');parser.add_argument('--blocks',type=int,default=8);parser.add_argument('--verify-only',action='store_true');a=parser.parse_args();run(a.source,a.month,a.blocks,a.verify_only)
