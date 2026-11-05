"""H11 preregistered exclusive-first side causal student, bounded source. Teacher labels future-only.
Important: ex-post source labels NOT features; all January historically research exposed.
"""
import json,hashlib,datetime,time,sys,os
from pathlib import Path
import numpy as np
import h9_teacher_january as H
import h10_bayesian_np_hawkes_pilot as M
import h11_exclusive_direction_teacher as T
ROOT=H.ROOT;CACHE=ROOT/'h10_atomic_cache'

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def freeze_exclusive_labels():
 rec=json.loads((CACHE/'H10_0002_ATOMIC_CACHE_RECEIPT.json').read_text())
 sel=np.load(CACHE/'sample_original_index.npy');Y=np.load(CACHE/'response_Y_2.npy')
 t,b,a,s,fill,ev,stop,censor,ref,q0=H.load()
 EX=T.exclusive(ev[:,:,0],T.stage_at(t,fill,ev,stop,censor,15000))[sel]
 assert not np.any(EX.sum(axis=1)>1)
 # H10 target labels require first +.30 source liquidation before source risk and 30s.
 YC=(Y&EX.astype(np.int8)).astype(np.int8)
 assert np.all(YC<=Y) and not np.any(YC.sum(axis=1)>1)
 p=CACHE/'H11_EXCLUSIVE_FIRST_SIDE_LIQ0300_LABEL.npy';temp=CACHE/'H11_EXCLUSIVE_FIRST_SIDE_LIQ0300_LABEL.tmp.npy';np.save(temp,YC,allow_pickle=False);os.replace(temp,p)
 receipt={'id':'H11-0002-EXCLUSIVE-ORIGINAL-ORDINAL-LABEL','source_signature':rec['source_gz_sha256'],'h8_immutable_source_archive':rec['source_h8_zip_sha256'],'asof_pilot_signal_ordinals':len(YC), 'label_formula':'H10+0.30_exit_lt30_side_label AND original full source first +0.10 midpoint side event before opposing first +0.10 event; side initial marker <=15sec and before own adverse and gap; exclusive by original event ordinal','candidate_ambiguous_initial_both_stage':int(np.count_nonzero(T.stage_at(t,fill,ev,stop,censor,15000)[sel].all(1))), 'candidate_both_h11_success':int(np.count_nonzero(YC.sum(1)>1)), 'label_bytes':p.stat().st_size,'label_sha256':sha(p),'cohort_positive_buy_sell':{},'not_real_trade_pnl':True}
 day=np.load(CACHE/'utc_day.npy');
 for tag,mask in [('TRAIN',(day>=1)&(day<=13)),('CALIB',(day>=14)&(day<=21)),('EVAL',(day>=22)&(day<=30))]:receipt['cohort_positive_buy_sell'][tag]=[int(YC[mask,j].sum()) for j in (0,1)]
 out=CACHE/'H11_0002_EXCLUSIVE_SOURCE_LABEL_RECEIPT.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
 print('H11_FROZEN_EXCLUSIVE_SOURCE_LABEL',json.dumps(receipt),flush=True)
 return YC

def fit(variant):
 if variant not in ('NO_HAWKES','MARKED_HAWKES'):raise ValueError(variant)
 label=CACHE/'H11_EXCLUSIVE_FIRST_SIDE_LIQ0300_LABEL.npy';rc=CACHE/'H11_0002_EXCLUSIVE_SOURCE_LABEL_RECEIPT.json'
 if not rc.exists():freeze_exclusive_labels()
 receipt=json.loads(rc.read_text());assert receipt['label_sha256']==sha(label)
 X=np.load(CACHE/'feature_X_49.npy',mmap_mode='r');Y=np.load(label,mmap_mode='r');keys=np.load(CACHE/'regime_key.npy',mmap_mode='r');day=np.load(CACHE/'utc_day.npy',mmap_mode='r');s=np.load(CACHE/'source_ordinal.npy',mmap_mode='r')
 train=(day>=1)&(day<=13);calib=(day>=14)&(day<=21);test=(day>=22)&(day<=30)
 a=time.monotonic();out=M.fit_models(X,Y,keys,s,variant,train,calib,test)
 data={'classification':'H11_EXCLUSIVE_DIRECTION_CAUSAL_ASOF_SIDE_CHOICE_BOUNDED_IN_SAMPLE_PILOT_NO_REAL_PNL','variant':variant,'source_original_quote_SHA':receipt['source_signature'],'H11_frozen_label_SHA':receipt['label_sha256'],'H10_asof_feature_SHA':json.loads((CACHE/'H10_0002_ATOMIC_CACHE_RECEIPT.json').read_text())['files']['feature_X_49']['sha256'], 'failure_to_meet_NP_reject_remains_failure':True,'no_signal_volume_certification':True,'no_blind_OOS':True,'model':out,'elapsed_s':round(time.monotonic()-a,3),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 path=ROOT/'results'/f'H11_EXCLUSIVE_BOUNDED_{variant}_CAUSAL_PILOT.json';path.write_text(json.dumps(data,indent=2,default=lambda x:float(x) if isinstance(x,np.generic) else str(x))+'\n');print('H11_TRAINED_MODEL',variant,json.dumps({'model':out,'receipt':str(path)},default=str),flush=True)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='FREEZE':freeze_exclusive_labels()
 else:fit(sys.argv[1])
