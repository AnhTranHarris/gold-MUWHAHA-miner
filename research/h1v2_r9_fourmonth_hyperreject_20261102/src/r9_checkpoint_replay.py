"""Bounded-time restartable full-month H1V2 R9 scoring and exact outcome replay.

Multiple invocations share ONLY immutable month-local asof npy and completed
per-chunk scored npz. Full-month replay does not need model inference again.
"""
import argparse,hashlib,json,math,pathlib,time
import numpy as np
import lightgbm as lgb
from r9_side_competing import MONTHS,SYNTH,OUT,R8,R7,H1,sha,augment,admission,_replay_ordinal_selected
BLOCK=500000

def chunk_path(mode,month,index):return OUT/f'R9_{mode}_{month}_BLOCK_{index:02d}.npz'

def score(mode,month,index):
 meta=json.loads((OUT/f'R9_{mode}_FIT.json').read_text())
 src=R8/f'R8_ASOF_{month}.npy';rec=json.loads((R8/f'R8_ASOF_{month}_receipt.json').read_text())
 if sha(src)!=rec['features_sha256']:raise ValueError('R8 full month SHA mismatch')
 regi=R7/f'R7_FULL_REGIME_{month}.npz';ref=json.loads((R7/f'R7_FULL_MONTH_{month}_receipt.json').read_text())
 if sha(regi)!=ref['regime_record_sha256']:raise ValueError('R7 nested regime SHA mismatch')
 X=np.load(src,mmap_mode='r');n=len(X)
 st=index*BLOCK;en=min(n,st+BLOCK)
 if st>=n:raise ValueError('block outside candidate count')
 path=chunk_path(mode,month,index)
 if path.exists():
  with np.load(path) as old:
   if old['start'].item()!=st or old['end'].item()!=en or not np.isfinite(old['score']).all():raise ValueError('existing block invalid')
   print('ALREADY CHECKPOINTED',mode,month,index,st,en,flush=True)
   return
 with np.load(regi) as z:r=z['regime'][st:en]
 arr=augment(X[st:en],r)
 p=[]
 for side in range(2):
  fp=OUT/f'R9_{mode}_{"BUY" if side==0 else "SELL"}_competing.txt'
  if sha(fp)!=meta['model_sha256'][str(side)]:raise ValueError('model SHA drift')
  model=lgb.Booster(model_file=str(fp))
  p.append(model.predict(arr,num_threads=2))
 score,side,margin=admission(np.stack(p,axis=1))
 np.savez_compressed(path,start=np.asarray(st,dtype=np.int64),end=np.asarray(en,dtype=np.int64),
     score=score,side=side,margin=margin)
 print('CHECKPOINTED BLOCK',mode,month,index,st,en,'file_SHA',sha(path),'seconds?',flush=True)

def replay(mode,month):
 meta=json.loads((OUT/f'R9_{mode}_FIT.json').read_text())
 x=np.load(R8/f'R8_ASOF_{month}.npy',mmap_mode='r');n=len(x)
 scores=np.empty(n,dtype=np.float32);sides=np.empty(n,dtype=np.int8)
 blocks=math.ceil(n/BLOCK); hashes={}
 for idx in range(blocks):
  path=chunk_path(mode,month,idx)
  if not path.exists():raise ValueError('missing score block '+str(idx))
  st=idx*BLOCK;en=min(n,st+BLOCK)
  with np.load(path) as z:
   if z['start'].item()!=st or z['end'].item()!=en:raise ValueError('block offset drift')
   if len(z['score'])!=en-st or len(z['side'])!=en-st:raise ValueError('block shape drift')
   scores[st:en]=z['score'];sides[st:en]=z['side']
  hashes[str(idx)]=sha(path)
 if not np.isfinite(scores).all() or not np.isin(sides,[0,1]).all():raise ValueError('bad score stream')
 tpath=H1/f'h1v2_dukascopy_{month}_oracle_labels.npz'
 original_receipt=json.loads((H1/f'h1v2_dukascopy_{month}_receipt.json').read_text())
 if sha(tpath)!=original_receipt['teacher_labels_sha256']:raise ValueError('original H1V2 exhaustive teacher SHA mismatch')
 with np.load(tpath) as z:
  ix=z['tick_index'].copy();code=z['code'].copy();net=z['net'].copy();exit_=z['exit_tick_index'].copy()
 with np.load(R7/f'R7_FULL_REGIME_{month}.npz') as z:
  if not np.array_equal(ix,z['ix']):raise ValueError('original teacher vs R7 ordinal mismatch')
 assert len(ix)==n
 rec={'mode':mode,'month':month,'in_sample_training_month':month in meta['training_months'],
  'candidate_count':n,'R9_SYNTH_reference':SYNTH[month],'score_block_sha256':hashes,
  'score_model_sha256':meta['model_sha256'],'threshold_source':'frozen training only',
  'fractions':{},'status':'HINDSIGHT_MODEL_ASOF_FEATURES_FULL_ORIGINAL_R9_EXIT_REPLAY_NOT_LIVE'}
 for fraction,cut in meta['frozen_thresholds'].items():
  rows=np.flatnonzero(scores>=cut);chosen=sides[rows];classes=code[rows,chosen]
  count,good,neutral,bad,unc,realized=_replay_ordinal_selected(rows,chosen,ix,exit_,net,code)
  assert count==good+neutral+bad
  rec['fractions'][fraction]={'score_cutoff':cut,'candidate_count':len(rows),
   'candidate_strict_good':int((classes==1).sum()),'candidate_bad':int((classes==-1).sum()),
   'candidate_neutral':int((classes==0).sum()),
   'candidate_precision':float((classes==1).mean()) if len(rows) else None,
   'nonoverlapping_count':int(count),'realized_strict_good':int(good),'realized_bad':int(bad),
   'realized_neutral':int(neutral),'unscorable_source_boundary':int(unc),
   'replay_precision':float(good/count) if count else None,'research_modeled_net':round(float(realized),2),
   'count_over_SYNTH':float(count/SYNTH[month]),
   'monthly_eighty_pct_volume_floor':math.ceil(.8*SYNTH[month]),
   'joint_80pct_count_and_correctness':bool(count>=math.ceil(.8*SYNTH[month]) and good/count>=.8) if count else False}
  print('FULLMONTH RESULT',mode,month,fraction,'trades',count,'correct',round(good/count,4) if count else 0,'net',round(realized),flush=True)
 output=OUT/f'R9_{mode}_{month}_FULL_REPLAY.json';output.write_text(json.dumps(rec,indent=2))
 print('COMPLETE REPLAY',mode,month,'SHA',sha(output),flush=True)
 return rec

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['all4','lomo07'],default='all4')
 ap.add_argument('--month',choices=MONTHS,required=True);ap.add_argument('--block',type=int)
 ap.add_argument('--replay',action='store_true')
 args=ap.parse_args()
 if args.block is not None:score(args.mode,args.month,args.block)
 elif args.replay:replay(args.mode,args.month)
 else:ap.error('choose --block or --replay')
