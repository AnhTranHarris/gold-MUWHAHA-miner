"""R24S3 resumable, source-hash-bound as-of multihorizon hazard inference.

Only observed feature matrix and frozen LightGBM models enter prediction. Labels,
original R9 volume quotas, and future-selected oracle ordinals are never read.
Each full chunk is written atomically with SHA-256 before marking complete. A
crash can never certify a partial .npy. This code is ADDITIVE to R24/R24S2.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time
from pathlib import Path
import numpy as np
import lightgbm as lgb

ROOT=Path('/mnt/data'); R24=ROOT/'h1v2_r24_asof'; LAB=ROOT/'h1v2_r24_s3'
sys.path.insert(0,str(R24/'source'))
import r24_firstpass_engine as source


def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()


def atomic_text(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_name(path.name+'.tmp')
 tmp.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')
 os.replace(tmp,path)


def run(src,month,chunk=32768,threads=4):
 mon=f'{int(month):02d}';pref=f'R24_{src}_{mon}_1000MS'
 srcdir=R24/'results'/src/mon
 base=srcdir/(pref+'_features.npy')
 raw=source.source_file(src,mon)
 model_path=R24/'models'/mon/'R24_FROZEN_BROKER_CONDITIONED_MULTISCALE_FIRSTPASS_5_CAUSE_LGBM.txt'
 wait_path=R24/'models'/mon/'R24_FROZEN_OPPORTUNITY_WAIT10S_LGBM.txt'
 if not all(p.is_file() for p in (base,raw,model_path,wait_path)):raise FileNotFoundError('MISSING_PINNED_SOURCE_FEATURE_OR_MODEL')
 source_sha=sha(raw);expect=source.source_pin(src,mon)
 if source_sha!=expect:raise RuntimeError('RAW_GZIP_SHA_MISMATCH')
 M=lgb.Booster(model_file=str(model_path));W=lgb.Booster(model_file=str(wait_path))
 features=np.load(base,mmap_mode='r',allow_pickle=False)
 if features.ndim!=2 or features.shape[1]!=len(source.FEATURE_NAMES):raise ValueError('FEATURE_SCHEMA_SIZE_MISMATCH')
 n=features.shape[0];if_matrix=M.num_feature()!=features.shape[1]+2
 if if_matrix or W.num_feature()!=features.shape[1]:raise RuntimeError('MODEL_FEATURE_SCHEMA_MISMATCH')
 digest={'source':src,'month':mon,'raw_source_sha256':source_sha,'source_rows':n,
         'features_sha256':sha(base),'feature_names':list(source.FEATURE_NAMES),
         'firstpass_model_sha256':sha(model_path),'wait_model_sha256':sha(wait_path),
         'chunk_size':chunk,'source_prefix_only':True,'no_future_labels_or_R9_quotas_in_prediction':True}
 blocks=LAB/'resumable_blocks'/src/mon
 blocks.mkdir(parents=True,exist_ok=True)
 base_record=blocks/'R24S3_FIXED_MODEL_INPUT_SHA_GUARD.json'
 if base_record.exists():
  if json.loads(base_record.read_text())!=digest:raise RuntimeError('FROZEN_INPUT_SCHEMA_SHA_DRIFT_ABORT')
 else:atomic_text(base_record,digest)
 nblocks=(n+chunk-1)//chunk
 for blk in range(nblocks):
  lo=blk*chunk;hi=min(n,lo+chunk)
  filename=f'R24S3_{src}_{mon}_PREDICTION_BLOCK_{blk:04d}.npz'
  target=blocks/filename;receipt=blocks/(filename+'.sha.json')
  if target.is_file() and receipt.is_file():
   rec=json.loads(receipt.read_text())
   if rec.get('input_sha_guard')==sha(base_record) and rec.get('sha256')==sha(target) and rec.get('lo')==lo and rec.get('hi')==hi:
    continue
   raise RuntimeError('STORED_BLOCK_SHA_MISMATCH_STOP')
  X=np.ascontiguousarray(features[lo:hi],dtype=np.float32)
  pp=np.empty((hi-lo,2,3,5),dtype=np.float32)
  ww=np.asarray(W.predict(X,num_threads=threads),dtype=np.float32)
  xx=np.empty((hi-lo,X.shape[1]+2),np.float32);xx[:,:-2]=X
  for s in range(2):
   xx[:,-2]=1 if s==0 else -1
   for hh,h in enumerate((15,30,60)):
    xx[:,-1]=h
    y=np.asarray(M.predict(xx,num_threads=threads),dtype=np.float32)
    if y.shape!=(hi-lo,5):raise AssertionError('PROB_5_CAUSE_SHAPE')
    pp[:,s,hh,:]=y
  if not (np.isfinite(pp).all() and np.isfinite(ww).all()):raise ValueError('NAN_INF_PREDICTION')
  if not np.allclose(pp.sum(-1),1.,atol=2e-4):raise ValueError('HAZARD_CLASS_PROB_NOT_SUM_ONE')
  if np.any((ww<0)|(ww>1)):raise ValueError('WAIT_PROBABILITY_NOT_IN_RANGE')
  tmp=target.with_name(target.name+'.tmp.npz')
  np.savez_compressed(tmp,probabilities=pp,wait=ww,lo=np.int64(lo),hi=np.int64(hi))
  os.replace(tmp,target)
  atomic_text(receipt,{'lo':lo,'hi':hi,'source':src,'month':mon,'input_sha_guard':sha(base_record),
                       'shape':list(pp.shape),'sha256':sha(target),'status':'COMPLETE_SHA_VERIFIED'})
  if blk%8==0:print('ATOMIC_CHUNK',src,mon,blk+1,nblocks,'decisions_through',hi,flush=True)
 # Merge only after verifying every block: no model leakage and no partial matrix reuse.
 outp=srcdir/f'R24_{src}_{mon}_FROZEN_ASOF_FIVE_CAUSE_PROBABILITIES.npy'
 outw=srcdir/f'R24_{src}_{mon}_FROZEN_ASOF_WAIT10S_PROBABILITY.npy'
 pout=outp.with_name(outp.name+'.R24S3.partial.npy');wout=outw.with_name(outw.name+'.R24S3.partial.npy')
 for old in (pout,wout):
  if old.exists():old.unlink()
 p=np.lib.format.open_memmap(pout,mode='w+',dtype=np.float32,shape=(n,2,3,5))
 w=np.lib.format.open_memmap(wout,mode='w+',dtype=np.float32,shape=(n,))
 for blk in range(nblocks):
  lo=blk*chunk;hi=min(n,lo+chunk)
  target=blocks/f'R24S3_{src}_{mon}_PREDICTION_BLOCK_{blk:04d}.npz'; receipt=blocks/(target.name+'.sha.json')
  rec=json.loads(receipt.read_text())
  if rec['sha256']!=sha(target) or rec['input_sha_guard']!=sha(base_record):raise RuntimeError('MODEL_BLOCK_SHA_INVALID_ON_MERGE')
  with np.load(target,allow_pickle=False) as z:
   if int(z['lo'])!=lo or int(z['hi'])!=hi:raise RuntimeError('CHUNK_ORDER_GAP')
   p[lo:hi]=z['probabilities'];w[lo:hi]=z['wait']
 p.flush();w.flush();del p,w
 # Original outputs must never be silently overwritten if already certified.
 original_marker=srcdir/f'R24_{src}_{mon}_FROZEN_ASOF_INFERENCE_ATOMIC_COMPLETION.json'
 if original_marker.exists():
  original=json.loads(original_marker.read_text())
  if original.get('status')=='ATOMIC_FROZEN_PROBABILITIES_COMPLETE':
   raise RuntimeError('ORIGINAL_FROZEN_INFERENCE_ALREADY_CERTIFIED_NO_OVERWRITE')
 for old in (outp,outw):
  if old.exists():
   if old.name.endswith('.npy'):
    q=old.with_name(old.name+'.INCOMPLETE_PRIOR_QUARANTINED')
    if q.exists():raise RuntimeError('AMBIGUOUS_QUARANTINE_NAME')
    os.replace(old,q)
 os.replace(pout,outp);os.replace(wout,outw)
 receipt={'status':'ATOMIC_FROZEN_PROBABILITIES_COMPLETE','source':src,'month':mon,'n_asof_decisions':n,
          'source_sha':source_sha,'hazard_model_sha':digest['firstpass_model_sha256'],
          'wait_model_sha':digest['wait_model_sha256'], 'probabilities_sha':sha(outp),
          'wait_probabilities_sha':sha(outw),'features_sha256':digest['features_sha256'],
          'input_sha_guard':sha(base_record),'completed_blocks':nblocks,'R24S3_additive_resumable_inference':True,
          'in_sample_exposed_labels':True,'not_trading_performance':True}
 atomic_text(original_marker,receipt)
 atomic_text(LAB/f'R24S3_{src}_{mon}_PREDICTION_SOURCE_FULL_SHA_RECEIPT.json',receipt)
 print('FROZEN_COMPLETE',src,mon,receipt,flush=True)
 return receipt

if __name__=='__main__':
 pa=argparse.ArgumentParser();pa.add_argument('--source',choices=source.SOURCE_NAMES,required=True);pa.add_argument('--month',choices=['01','02','06','07'],required=True)
 pa.add_argument('--chunk',type=int,default=32768);pa.add_argument('--threads',type=int,default=4)
 a=pa.parse_args();run(a.source,a.month,a.chunk,a.threads)
