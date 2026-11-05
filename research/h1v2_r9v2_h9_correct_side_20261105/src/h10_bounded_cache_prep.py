"""H10 preregistered 1-in-16 as-of-only, source ordinal-preserving bounded feature cache.
Original full quote file and H8 futures remain immutable. No model trained here.
"""
from __future__ import annotations
import hashlib,json,time,os,datetime,sys
from pathlib import Path
import numpy as np
import h10_bayesian_np_hawkes_pilot as M
import h9_teacher_january as H

ROOT=H.ROOT; CACHE=ROOT/'h10_atomic_cache';CACHE.mkdir(exist_ok=True)
start=time.monotonic()
t,b,a,signal,fill,ev,stop,censor,ref,q0=H.load()
selection=np.arange(0,len(signal),16,dtype=np.int32)
s=signal[selection]
assert len(selection)==(len(signal)+15)//16
assert s.size>90000 and np.all(s[1:]>s[:-1])
X=M.asof_feature_map(t,b,a,s)
assert X.shape==(len(s),49)
# Independent future-mutation check, input changes strictly after latest tested as-of signal
inds=np.arange(200,310); r=M.asof_feature_map(t,b,a,s[inds]);bp=b.copy();ap=a.copy();cut=int(s[inds[-1]])+1;bp[cut:cut+100]+=10000;ap[cut:cut+100]+=10000
rp=M.asof_feature_map(t,bp,ap,s[inds]);assert np.array_equal(np.nan_to_num(r,nan=-1e9),np.nan_to_num(rp,nan=-1e9))
del bp,ap
Y,stages=M.future_labels(t,fill[selection],ev[selection],stop[selection],censor[selection]);key=M.regime_buckets(X)
day=((t[s]-q0)//86400000).astype(np.int16)
train=(day>=1)&(day<=13);calib=(day>=14)&(day<=21);test=(day>=22)&(day<=30)
assert sum((train&calib)|(train&test)|(calib&test))==0
assert train.sum()>30000 and calib.sum()>15000 and test.sum()>15000
# Atomic .npy write: temp file and rename, sha of actual payload
objs={'feature_X_49':X,'response_Y_2':Y,'regime_key':key,'source_ordinal':s,'utc_day':day,'sample_original_index':selection,'stage_success':stages}
files={}
for k,v in objs.items():
    target=CACHE/(k+'.npy');tmp=CACHE/(k+'.tmp.npy');np.save(tmp,v,allow_pickle=False);os.replace(tmp,target)
    with open(target,'rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    files[k]={'name':target.name,'shape':list(v.shape),'dtype':str(v.dtype),'sha256':sha,'bytes':target.stat().st_size}
receipt={'id':'H10-0002-CACHE','classification':'DETERMINISTIC_1_IN_16_ORIGINAL_SOURCE_SIGNAL_ASOF_PILOT_NOT_FULL_MONTH','source':'DUKASCOPY_RAW','month':'01','original_signal_count':len(signal),'pilot_signal_count':len(s),'source_gz_sha256':H.PIN,'source_h8_zip_sha256':H.sha_file(H.H8ZIP),'sample_mechanism':'exact original signal ordinal indices 0,16,32,...; unchanged underlying quote tick events','feature_schema':M.NAMES,'no_future_leakage':'PASS_110_LABEL_INDEPENDENT_FUTURE_QUOTE_MUTATIONS','first_quote_fill_milliseconds':100,'stage_labels_are_post_entry_futures_response_only':True,'period_split':{'train':'Jan02-14','calib':'Jan15-22','eval':'Jan23-31'},'cohorts':{'train':int(train.sum()),'calib':int(calib.sum()),'eval':int(test.sum()),'buy_hits':[int(Y[m,0].sum()) for m in (train,calib,test)],'sell_hits':[int(Y[m,1].sum()) for m in (train,calib,test)]},'files':files,'elapsed_seconds':round(time.monotonic()-start,3)}
p=CACHE/'H10_0002_ATOMIC_CACHE_RECEIPT.json';p.write_text(json.dumps(receipt,indent=2)+'\n');print('H10_CACHE_VERIFIED',json.dumps(receipt,sort_keys=True),flush=True)
