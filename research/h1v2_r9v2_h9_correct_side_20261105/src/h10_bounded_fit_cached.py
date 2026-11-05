"""H10-0003: fit preregistered, side-specific Bayesian+NP models on frozen 1-in-16 original signal cache.
Train, calibrate and chronological-evaluate distinct Jan calendar days. Research-exposed month, NOT OOS.
"""
import json,hashlib,sys,time,datetime
from pathlib import Path
import numpy as np
import h10_bayesian_np_hawkes_pilot as M
from h9_teacher_january import ROOT

def main(variant):
 if variant not in ('NO_HAWKES','MARKED_HAWKES'):raise ValueError(variant)
 root=ROOT/'h10_atomic_cache';rc=json.loads((root/'H10_0002_ATOMIC_CACHE_RECEIPT.json').read_text())
 data={}
 for key,v in rc['files'].items():
  p=root/v['name'];with_open=open(p,'rb'); sha=hashlib.file_digest(with_open,'sha256').hexdigest();with_open.close()
  assert sha==v['sha256'],('SOURCE_CACHE_SHA_DRIFT',key)
  data[key]=np.load(p,mmap_mode='r',allow_pickle=False)
 X=data['feature_X_49'];y=data['response_Y_2'];keys=data['regime_key'];days=data['utc_day']
 train=(days>=1)&(days<=13);calib=(days>=14)&(days<=21);test=(days>=22)&(days<=30)
 assert train.sum()>30000 and calib.sum()>15000 and test.sum()>15000
 start=time.monotonic();out=M.fit_models(X,y,keys,np.asarray(data['source_ordinal']),variant,train,calib,test)
 report={'classification':'H10_BOUNDED_ORIGINAL_1_IN_16_ASOF_CHRONOLOGICAL_INSAMPLE_PILOT_NOT_BLIND_OOS_NOT_CASH_PNL',
 'research_only':True,'variant':variant,'original_cache_receipt_sha':hashlib.sha256((root/'H10_0002_ATOMIC_CACHE_RECEIPT.json').read_bytes()).hexdigest(),
 'entire_original_tick_source_sha':rc['source_gz_sha256'],'h8_frozen_label_source_sha':rc['source_h8_zip_sha256'],
 'eval_cohort_is_original_research_exposed_January':True,'future_label_access_during_action_selection':False,
 'buyer_and_seller_NP_gate_before_argmax':True,'model':out,'elapsed_fit_seconds':round(time.monotonic()-start,3),
 'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 path=ROOT/'results'/('H10_BOUNDED_'+variant+'_ATOMIC_RESEARCH_RECEIPT.json');path.write_text(json.dumps(report,indent=2,default=lambda a:float(a) if isinstance(a,np.generic) else str(a))+'\n')
 print('COMPLETE_H10_MODEL',variant,json.dumps({'model':out,'elapsed':report['elapsed_fit_seconds'],'receipt':str(path)},default=str),flush=True)
if __name__=='__main__':main(sys.argv[1])
