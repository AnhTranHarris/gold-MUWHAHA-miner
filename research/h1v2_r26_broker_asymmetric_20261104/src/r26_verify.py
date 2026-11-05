"""R26 independent read-only all-evidence verifier; no model execution.

Runs source-month in atomic order. Each accepted source quote ordinal gets
independent actual bid/ask fill, time, and economic trace parity validation.
"""
from __future__ import annotations
import hashlib,json,sys,csv
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

@njit(cache=False)
def position_nonoverlap(ts, signals, fills, exits, statuses):
 prev=-9_999_999_999_999_999
 for i in range(len(signals)):
  if ts[signals[i]]<=prev:return i
  if fills[i]<0:continue
  if statuses[i]==3:
   prev=int(ts[exits[i]]+300000) if exits[i]>=0 else int(ts[-1])
  else:prev=int(ts[exits[i]])
 return -1

from source import source_month,PINS
from r26_mechanisms import NAME
from r26_replay import R,calendar

SHA=lambda p:hashlib.file_digest(open(p,'rb'),'sha256').hexdigest()

def verify(source,month):
 t,b,a=source_month(source,month,verify_sha=True)
 q,reference=calendar(month)
 checks=[]
 for policy in NAME:
  root=R/'results'/source/month/policy
  recpath=root/f'R26_{source}_{month}_{policy}_SOURCE_SHA_AND_SCIENCE_RECEIPT.json'
  receipt=json.loads(recpath.read_text())
  assert receipt['source_raw_sha256']==PINS[(source,month)]
  assert receipt['original_R9_SYNTH_corrected_month_reference']==int(reference.sum())
  for file,meta in receipt['files'].items():
   p=root/file
   assert p.stat().st_size==meta['bytes'] and SHA(p)==meta['sha256'],('OUTPUT_SHA_MISMATCH',file)
  tr=root/f'R26_{source}_{month}_{policy}_ALL_ACCEPTED_AND_UNFILLED_EXACT_SOURCE_QUOTE_ORDINALS.npz'
  with np.load(tr,allow_pickle=False) as z:
   signal=z['signal_ordinal'];fill=z['fill_ordinal'];exit_=z['exit_ordinal'];side=z['buy1_sellminus1'];status=z['outcome_code_1TARGET_0STOP_2TIMEOUT_3UNKNOWN_4UNFILLED'];
   ftime=z['fill_utc_ms'];net=z['known_net_quote_raw_unknown_minus2147483647'];s=z['fill_source_spread_raw'];tp=z['target_net_raw'];stop=z['stop_adverse_from_open_liq_raw'];h=z['horizon_ms']
  n=len(signal)
  assert n==receipt['replay_attempts_including_unfilled']
  assert len(np.unique(signal))==n and np.all(np.diff(signal)>0)
  assert set(np.unique(status)).issubset({0,1,2,3,4}) and set(np.unique(side)).issubset({-1,1})
  actual=fill>=0;completed=actual&(status!=3);unknown=actual&(status==3);unfilled=~actual
  assert np.count_nonzero(actual)==receipt['true_actual_quote_fills']
  assert np.count_nonzero(status==1)==receipt['TARGET_FIRST']
  assert np.count_nonzero(status==0)==receipt['STOP_FIRST']
  assert np.count_nonzero(status==2)==receipt['TIMEOUT']
  assert np.count_nonzero(status==3)==receipt['GAP_CENSORED_UNKNOWN_PNL']
  assert np.count_nonzero(status==4)==receipt['UNFILLED']
  assert np.all(status[unfilled]==4) and np.all(net[unfilled]==-2147483647)
  assert np.all((signal>=0)&(signal<len(t)))
  f=fill[actual];ff=ftime[actual]
  assert np.all((f>signal[actual])&(f<len(t)))
  assert np.all(ff==t[f])
  assert np.all(ff>=t[signal[actual]]+100) and np.all(ff-t[signal[actual]]<=1100)
  assert np.all(np.searchsorted(t,t[signal[actual]]+100,side='left')==f)
  assert np.all(s[actual]==a[f]-b[f])
  assert np.all((s[actual]>=0)&(s[actual]<=4000))
  if np.any(completed):
   fi=fill[completed];ei=exit_[completed];ss=side[completed];nn=net[completed]
   assert np.all((ei>fi)&(ei<len(t)))
   calc=np.where(ss==1,b[ei].astype(np.int64)-a[fi].astype(np.int64)-20,b[fi].astype(np.int64)-a[ei].astype(np.int64)-20)
   assert np.array_equal(calc,nn)
   assert int(nn.sum())==receipt['known_quote_price_net_raw_excluding_censored']
   hit=(status[completed]==1);bad=(status[completed]==0);timeout=(status[completed]==2)
   assert np.all(calc[hit]>=tp[completed][hit])
   if np.any(hit):assert np.all(t[ei[hit]]<=t[fi[hit]]+h[completed][hit])
   assert np.all(np.where(ss[bad]==1,b[ei[bad]]<=b[fi[bad]]-stop[completed][bad],a[ei[bad]]>=a[fi[bad]]+stop[completed][bad]))
   assert np.all(t[ei[timeout]]>=t[fi[timeout]]+h[completed][timeout])
  if np.any(unknown):assert np.all(net[unknown]==-2147483647)
  # Quote-level position overlap including previous UTC calendar boundaries, compiled.
  bad_ix=position_nonoverlap(t,signal,fill,exit_,status)
  assert bad_ix<0,('SOURCE_SIGNAL_OPEN_POSITION',source,month,policy,int(bad_ix))
  # Source calendar all four-month quarter/hour/day full rows, including zero reference.
  for typ,rowspan in [('QUARTER',1),('HOUR',4),('DAY',96)]:
   p=root/f'R26_{source}_{month}_{policy}_ALL_{len(reference)//rowspan}_UTC_{typ}_SOURCE_OUTCOMES.csv'
   d=pd.read_csv(p)
   assert len(d)==len(reference)//rowspan
   r=reference.reshape(-1,rowspan).sum(axis=1)
   assert np.array_equal(d.original_R9_SYNTH_UTC_reference.to_numpy(),r)
   assert int(d.actually_filled.sum())==receipt['true_actual_quote_fills']
   assert int(d.completed_eligible_excluding_gap_and_unfilled.sum())==int(completed.sum())
   assert int(d.TARGET_FIRST.sum())==receipt['TARGET_FIRST']
   assert int(d.STOP_FIRST.sum())==receipt['STOP_FIRST']
   assert int(d.TIMEOUT.sum())==receipt['TIMEOUT']
   assert int(d.GAP_CENSORED.sum())==receipt['GAP_CENSORED_UNKNOWN_PNL']
   assert int(d.known_net_quoted_price_raw_NOT_ACCOUNT_CASH.sum())==receipt['known_quote_price_net_raw_excluding_censored']
   if typ=='QUARTER':key='strict_quarters'
   elif typ=='HOUR':key='strict_hours'
   else:key='strict_days'
   assert int((r>0).sum())==receipt[key]['active']
   assert int(d.original_quota_count_pass.sum())==receipt[key]['volume']
   assert int(d.strict_80pct_precision_pass.sum())==receipt[key]['precision']
   assert int(d.joint_80pct_AND_original_R9_quota_pass.sum())==receipt[key]['joint']
  checks.append({'source':source,'month':month,'policy':policy,'full_quote_trace_count':n,'filled':int(actual.sum()),'completed':int(completed.sum()),'target':int((status==1).sum()),'stop':int((status==0).sum()),'net_known':int(net[completed].sum()),'parity':'PASS'})
 return checks

if __name__=='__main__':
 s,m=sys.argv[1:3];ret=verify(s,m)
 print('SOURCE_MONTH_VERIFY_ALL_6_PASSED',s,m,'ALL_ORIGINAL_QUOTES_AUTHENTICATED',len(ret),flush=True)
 path=R/'verification'/f'R26_VERIFY_{s}_{m}_ORIGINAL_QUOTE_TRADE_CALENDAR_SHA_RECEIPT.json'
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(ret,indent=2)+'\n')
