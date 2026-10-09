#!/usr/bin/env python3
"""FEB044 source-model research ONLY. Entry-known gates, first-passage original exits.

Run in a directory beside feb044_screen.py, engine_cohort_caps_044.py, with
root caches/proposals restored from original JAN/FEB raw data and FEB043 lineage.
The FEB044 policy was selected on February outcomes; no full V1 funded genealogy,
MT5 order execution, or month-blind adaptive selection has been certified.
"""
from __future__ import annotations
import sys, json, hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
import feb044_screen as h
import engine_cohort_caps_044 as m
for k in 'EXRDPHSCON':setattr(m,k,getattr(h.m,k).copy())
m.total=h.m.total;m.imp20=h.imp
s=m.S;p=h.phase;r=h.prior
# Fitted February thresholds; *inputs* are known at entry, but selecting these
# thresholds involved retrospective February outcomes. Do not deploy them blindly.
reject = ((s==19)&np.isin(p,[0,1,5])) | ((s==17)&np.isin(p,[1,5])) | ((s==25)&(r>=12)&(r<16)) | ((s==19)&(p==4)) | ((s==21)&(r>=4)&(r<6)) | ((s==23)&(r>=12)&(r<16))
allowed=h.base_allowed.copy()&~reject
allowed|=(s==22)&(r>=24)&(r<48)
allowed|=(s==24)&(r>=0)&(r<12)
allowed|=(s==26)&(r>=8)&(r<16)
m.spread=np.where((s>=17)&~allowed,np.inf,h.spr)
h.exits()
for k in ['X','P']:setattr(m,k,getattr(h.m,k).copy())
keep_sources=[17,19,21,22,23,24,25,26,27]
bit=sum(1<<(src-10) for src in range(17,29) if src not in keep_sources)
params={**h.params,'source22cap':768,'source27cap':64,'phase3cap':448,'phase4cap':448,'phase5cap':128,'l3_excluded_hours':bit}
score,ledger=m.run(**params)
score=m.daily_and_exact(ledger,score)
expected={'net':212710.922,'gl':-23464.931,'trades':30923,'equity_dd':23272.669,'maxopen_full':1536}
for name,target in expected.items():
 assert abs(score[name]-target)<.002,(name,score[name],target)
# Confirm original entry/exit quote side; preserving fully realized-price evidence.
T,A,B=m.t,m.a,m.b
E,X,R,D,P=[ledger[k] for k in 'EXRDP']
assert np.all((E>=0)&(X>E)&(X<len(T)))
assert np.array_equal(R,np.where(D>0,A[E],B[E]))
side_price=np.where(D>0,B[X],A[X])
reconciliation=(side_price-R)*D/1000.-0.02
assert np.max(np.abs(reconciliation-P))<1e-7
# Independent exact floating equity reconstruction on *every* quote (not entry sampling).
N=len(T);lon=D>0;sho=D<0
lc=np.cumsum(np.bincount(E[lon],minlength=N)-np.bincount(X[lon],minlength=N))
sc=np.cumsum(np.bincount(E[sho],minlength=N)-np.bincount(X[sho],minlength=N))
lr=np.cumsum(np.bincount(E[lon],weights=R[lon],minlength=N)-np.bincount(X[lon],weights=R[lon],minlength=N))
sr=np.cumsum(np.bincount(E[sho],weights=R[sho],minlength=N)-np.bincount(X[sho],weights=R[sho],minlength=N))
realized=np.cumsum(np.bincount(X,weights=P,minlength=N))
equity=realized+(lc*B-lr+sr-sc*A)/1000.-0.02*(lc+sc)
dd=float(np.max(np.maximum.accumulate(equity)-equity))
assert abs(dd-score['equity_dd'])<.002
assert int(np.max(lc+sc))==score['maxopen_full']
sec=T[E]//1000;assert np.unique(E).size==len(E)
assert int(np.unique(sec,return_counts=True)[1].max())<=10
start=Path('/mnt/data/feb044_work')
for fname,pin in [("XAUUSD_DUKAS_2026_01_ticks.csv(3).gz",'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5'),("XAUUSD_DUKAS_2026_02_ticks.csv(3).gz",'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d')]:
 with open(Path('/mnt/data')/fname,'rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==pin,(fname,sha)
result={'status':'PASS_RESEARCH_SOURCE_REPLAY_AND_INDEPENDENT_FULL_TICK_EQUITY','model_class':'FEBRUARY_FITTED_FIXED_ORIGINAL_SOURCE_PROPOSAL_TAPE_NOT_FULL_V1_BROKER_FUNDED','metrics':{k:score[k] for k in ['net','gl','gp','pf','trades','equity_dd','bal_dd','maxopen_full','win_pct','daily','weekly']},'raw_feb_sha256':'ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d','jan_warmup_sha256':'d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5','full_quote_count':N,'max_quote_pnl_error':float(np.max(np.abs(P-reconciliation))),'independent_vs_original_dd_diff':dd-score['equity_dd'],'max_entries_per_tick':1,'max_entries_per_second':int(np.unique(sec,return_counts=True)[1].max()),'params':params,'no_production_or_v1_modification':True}
(BASE/'FEB044_SELECTED_EXACT.json').write_text(json.dumps(result,indent=2))
np.savez_compressed(BASE/'FEB044_SELECTED_LEDGER.npz',**ledger)
print('QA_PASS',json.dumps({k:result['metrics'][k] for k in ['net','gl','pf','trades','equity_dd','maxopen_full']},sort_keys=True))