"""Diagnostic only: test WHETHER original JAN037 50ms source generalizes to archived FEB041 E/S/D.
Do not promote if mismatch; no parameter fitting or calendar switch allowed."""
import sys,zipfile,io,time,json,hashlib
from pathlib import Path
from collections import Counter
import numpy as np,pandas as pd
SRC=Path('/mnt/data/c2d3l_work/032_source');sys.path.insert(0,str(SRC))
import stmr_janjul as j, stmr_base as c, gamma02_campaign_heartbeat_019 as hb
RAW=Path('/mnt/data');SHAS=['d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d']
F='/mnt/data/feb_source_phase/FEB042_ITERATIVE_FEBRUARY_RESEARCH_BUNDLE.zip'
ORIG='FEB042/FEB042_JAN039_PREPARED_PROPOSALS.npz'
start=time.time()
a=[]
for m,sha in zip(['01','02'],SHAS):
 path=RAW/f'XAUUSD_DUKAS_2026_{m}_ticks.csv(3).gz'
 with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==sha
 a.append(pd.read_csv(path,compression='gzip',usecols=['timestamp_ms_utc','ask_raw','bid_raw'],dtype={'timestamp_ms_utc':'i8','ask_raw':'i4','bid_raw':'i4'}))
f=a[0].iloc[-3900880:];g=a[1];d=pd.concat([f,g],ignore_index=True)
t=d.timestamp_ms_utc.to_numpy(np.int64);ask=d.ask_raw.to_numpy(np.int32);bid=d.bid_raw.to_numpy(np.int32);del d,a,f,g
mid=((ask.astype(np.int64)+bid.astype(np.int64))//2).astype(np.int32)
h4,h1,m15,m5=j.make_states(t,bid,((8,21),(8,21),(8,21),(8,21)))
print('loaded',len(t),'elapsed',round(time.time()-start,2),flush=True)
idx,dr,src,hh,tt,ss=hb.heartbeat_candidates(t,mid,h4,h1,m15,m5,50,4)
mask=idx>=3900880
ref=np.stack([idx[mask],src[mask]+10,dr[mask]],axis=1).astype(np.int64)
with zipfile.ZipFile(F) as z:raw=z.read(ORIG)
with np.load(io.BytesIO(raw),allow_pickle=False) as z:
 emask=z['S']>=17; orig=np.stack([z['E'][emask],z['S'][emask],z['D'][emask]],axis=1).astype(np.int64)
produced=Counter(map(tuple,ref.tolist()));original=Counter(map(tuple,orig.tolist()))
extra=produced-original;missing=original-produced
print('FROM_JAN037_GENERIC',len(ref),'FEB041_FROZEN',len(orig),'extra',sum(extra.values()),'missing',sum(missing.values()),'seconds',round(time.time()-start,2),flush=True)
print('first extra',list(extra.items())[:8], 'missing',list(missing.items())[:8],flush=True)
out={'genuine_11_439_219_ticks':len(t),'frozen_feb042_L3_s17_s28':len(orig),'JAN037_original_heartbeat_crossmonth_generated':len(ref),'generated_not_FEB041':sum(extra.values()),'FEB041_not_generated':sum(missing.values()),'first_extra':[(list(k),v) for k,v in list(extra.items())[:10]],'first_missing':[(list(k),v) for k,v in list(missing.items())[:10]],'original_source_generalization_exact':extra==missing==Counter(),'elapsed':round(time.time()-start,2)}
Path('/mnt/data/c2d3l_work/JAN037_TO_FEB041_NATIVE_MECHANISM_ABLATION.json').write_text(json.dumps(out,indent=2)+'\n')
