"""R18 independent frozen-signal latency stress on ORIGINAL full raw BID/ASK quotes.

Source original selected BUY/SELL quote ordinals are FUTURE INFORMED. Their
source-entry decisions are frozen, not reoptimized after latency; no as-of
student learns from them. The experiment replays the first actually observed
fill quote after nominal 0/100/500ms, with no interpolated midprice, realistic
one-position BUY/SELL/WAIT occupancy, 0/0.02/0.05 quoted-price-per-leg slip,
first executable net +0.10 TP or opening-liquidation adverse -0.10 stop,
otherwise first observed quote at/after 60s timeout. The failure and timeout
bid/ask net is recorded, not inventively set to zero. This distinct NEW
FIRST_TOUCH_60_BEFORE_ADVERSE exit is NOT original R9 trail/stop/time-out nor
original full30 adverse-free label. All fills are quote-model simulations,
not actual Coinexx dealer fills nor account-currency PnL.
"""
from __future__ import annotations
import argparse,csv,json,sys,time,hashlib
from pathlib import Path
import numpy as np
from numba import njit
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r18_broker_multihorizon as r18
LAB=Path(__file__).resolve().parents[1]
LANE='R18_ADAPTIVE_UNION_4000'
CONTRACT='NEW_FIRST_TOUCH_60_BEFORE_ADVERSE'
LAGS=(0,100,500)
SLIPS=(0,20,50)
GOOD=1;STOP=0;TIMEOUT=2;REJECT=-1;BUSY=-2;CENSOR=-3
CAP=4000;HORIZON=60000;GAP=15000;FEE=20;TP=100;ADVERSE=100

@njit(cache=False)
def frozen_replay(t,b,a,signals,side,fill_candidates,slip):
 """Point-in-time portfolio state, but input signal/side selected by FUTURE oracle."""
 n=len(signals);out=np.empty(n,np.int8);filled=np.full(n,-1,np.int32)
 exited=np.full(n,-1,np.int32);net=np.full(n,-2147483647,np.int32)
 occupied=np.int64(-9223372036854775807)
 for k in range(n):
  i=signals[k];now=t[i]
  if now<=occupied:
   out[k]=BUSY;continue
  f=int(fill_candidates[k]);target=now # staleness is checked by caller + parameter
  if f<0 or f>=len(t):out[k]=REJECT;continue
  if a[f]<b[f] or a[f]-b[f]>CAP:
   out[k]=REJECT;continue
  # The next source quote is truly observed; limit after nominal target is
  # checked by wrapper, not inferred from future OHLC/last quote.
  filled[k]=f;buy=side[k]==1
  entry=(a[f]+slip) if buy else (b[f]-slip)
  openliq=b[f] if buy else a[f]
  prev=t[f];last=t[f];seen=False;resolved=False
  for j in range(f+1,len(t)):
   if t[j]==t[f]:continue # no invented same-millisecond execution sequence
   if t[j]-prev>GAP:
    out[k]=CENSOR;occupied=t[f]+HORIZON;resolved=True;break
   prev=t[j]
   liq=(b[j]-slip) if buy else (a[j]+slip)
   v=(liq-entry)*side[k]-FEE
   if t[j]>t[f]+HORIZON:
    # At/after 60s; earliest observed source quote is the *possible* timeout
    # liquidation if no stale gap. Never use last quote inside window.
    out[k]=TIMEOUT;exited[k]=j;net[k]=v;occupied=t[j];resolved=True;break
   seen=True
   if (buy and b[j]<=openliq-ADVERSE) or ((not buy) and a[j]>=openliq+ADVERSE):
    out[k]=STOP;exited[k]=j;net[k]=v;occupied=t[j];resolved=True;break
   if v>=TP:
    out[k]=GOOD;exited[k]=j;net[k]=v;occupied=t[j];resolved=True;break
   last=t[j]
  if not resolved:
   out[k]=CENSOR;occupied=t[f]+HORIZON
 return out,filled,exited,net

def get_frozen(source,mon,root=Path('/mnt/data')):
 t,b,a,p=r18.read_raw(source,mon,root)
 tag=f'R18_{source}_{mon}'
 with np.load(LAB/'results'/f'{tag}_LOSSLESS_SELECTED_ORIGINAL_QUOTE_ORDINALS.npz',allow_pickle=False) as d:
  k=LANE+'__'+CONTRACT
  ix=d[k+'_entry_ord'].copy().astype(np.int32)
  side=d[k+'_side_FUTURE_SELECTED'].copy().astype(np.int8)
  ex=d[k+'_firstTP_exit_ord'].copy().astype(np.int32)
 assert np.all(t[ix[1:]]>t[ix[:-1]]) and np.all((side==1)|(side==-1))
 assert len(ix)==len(side)==len(ex) and np.all(ex>ix)
 if source=='MT5_BROKER_EXPORT' and mon=='06':
  # Explicit original adjacent source evidence, no synthetic file extension.
  # June broker-clock data ends before the final two UTC hours; consume
  # the separately hash-pinned July month and tail-only original-quote receipts.
  tj,bj,aj,pj=r18.read_raw(source,'07',root)
  _,end=r18.month_range('06')
  keep=(tj>t[-1])&(tj<end+180000)
  assert np.any(keep)
  fulln=len(t)
  t=np.r_[t,tj[keep]];b=np.r_[b,bj[keep]];a=np.r_[a,aj[keep]]
  with np.load(LAB/'results_r18_JUNE_TAIL_PATCH'/'R18_JUNE_MT5_HALO_FULL_50_SOURCE_QUOTE_ORDINAL_TAIL_SETS.npz',allow_pickle=False) as d:
   k=LANE+'__'+CONTRACT
   extra_ix=d[k+'_stitched_entry_ord'].copy().astype(np.int32)
   extra_side=d[k+'_future_selected_side'].copy().astype(np.int8)
   extra_ex=d[k+'_stitched_exit_ord'].copy().astype(np.int32)
  assert np.all(extra_ix>=fulln) and np.all(extra_ex>=fulln)
  ix=np.r_[ix,extra_ix];side=np.r_[side,extra_side];ex=np.r_[ex,extra_ex]
  assert np.all(np.diff(t[ix])>0)
  # Both SHA independently checked inside read_raw. Return extra provenance.
  return t,b,a,ix,side,ex,{'source_filename':p.name,'source_sha':r18.PINS[source][mon],
   'next_broker_month_sha':r18.PINS[source]['07'],'stitched_actual_JULY_rows':int(keep.sum())}
 return t,b,a,ix,side,ex,{'source_filename':p.name,'source_sha':r18.PINS[source][mon]}

def one(source,mon):
 outdir=LAB/'results_r18_FROZEN_DELAY';outdir.mkdir(exist_ok=True,parents=True)
 start=time.monotonic();t,b,a,ix,side,origex,provenance=get_frozen(source,mon)
 refs=r18.refs_for_month(mon,Path('/mnt/data'));qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 rows=[];allq=[];allh=[];arrays={}
 for lag in LAGS:
  fillidx=ix if lag==0 else np.searchsorted(t,t[ix]+lag,side='left').astype(np.int32)
  # Enforce actual first NEXT observed quote and at most 1s arrival excess.
  safe=np.clip(fillidx,0,len(t)-1)
  ok=(fillidx<len(t))&(t[safe]>t[ix] if lag>0 else True)
  ok&=(t[safe]-(t[ix]+lag)<=1000)
  if lag>0:ok&=safe>ix
  fillidx=np.where(ok,fillidx,-1).astype(np.int32)
  for slip in SLIPS:
   state,filled,exited,net=frozen_replay(t,b,a,ix,side,fillidx,slip)
   if lag==0 and slip==0:
    assert np.all(state==GOOD),f'FROZEN_ZERO_LATENCY_1STTP_PARITY_FAILURE {source} {mon} {np.unique(state,return_counts=True)}'
   assert np.all(np.isin(state,np.array([GOOD,STOP,TIMEOUT,REJECT,BUSY,CENSOR],np.int8)))
   complete=(state==GOOD)|(state==STOP)|(state==TIMEOUT)
   assert int(np.sum(complete| (state==REJECT)|(state==BUSY)|(state==CENSOR)))==len(ix)
   g=int((state==GOOD).sum());bad=int(((state==STOP)|(state==TIMEOUT)).sum());rej=int((state==REJECT).sum());busy=int((state==BUSY).sum());censored=int((state==CENSOR).sum())
   completed_net_raw=int(net[complete].astype(np.int64).sum())
   goodq=np.zeros(len(qref),np.int32);badq=np.zeros(len(qref),np.int32);cenq=np.zeros(len(qref),np.int32)
   rejq=np.zeros(len(qref),np.int32);busyq=np.zeros(len(qref),np.int32)
   for code,dest,usefill in [(GOOD,goodq,True),(STOP,badq,True),(TIMEOUT,badq,True),
                             (CENSOR,cenq,True),(REJECT,rejq,False),(BUSY,busyq,False)]:
    k=np.flatnonzero(state==code)
    if len(k):
     ords=filled[k] if usefill else ix[k]
     # censored filled rows must be tracked at observed quote, not invented exit.
     indices=(t[ords]//900000-qkeys[0]).astype(np.int64)
     assert np.all((indices>=0)&(indices<len(qref))),f'ATTRIBUTION_OUTSIDE_MONTH {source} {mon} {code}'
     dest[:]+=np.bincount(indices,minlength=len(qref))
   assert int(sum(x.sum() for x in (goodq,badq,cenq,rejq,busyq)))==len(ix)
   precision=goodq/(goodq+badq+1e-100)
   qm=(qref>0)&(goodq>=qref)&(precision>=.8)
   hgood=goodq.reshape(-1,4).sum(axis=1);hbad=badq.reshape(-1,4).sum(axis=1)
   hp=hgood/(hgood+hbad+1e-100);hm=(href>0)&(hgood>=href)&(hp>=.8)
   label=f'lag{lag}_slip{slip}'
   rows.append({'source':source,'month':mon,'label':label,'source_selected_oracle_signal_count':len(ix),
    'latency_ms':lag,'per_leg_slippage_raw_0p001':slip,
    'GOOD_60s_firstTP_before_adverse':g,'COMPLETED_FAILED_STOP_OR_TIMEOUT':bad,
    'SOURCE_RIGHT_CENSORED':censored,'QUOTE_OR_SPREAD_REJECTED':rej,'OCCUPIED_SKIPPED':busy,
    'completed_correct_fraction':None if g+bad==0 else g/(g+bad),
    'modeled_all_completed_bidask_net_quote_price_raw_0p001':completed_net_raw,
    'modeled_all_completed_bidask_net_quote_price_usd_per_1oz_not_cash':completed_net_raw/1000,
    'quarter_joint_correct_and_80pct':int(qm.sum()),'active_quarters':int(np.sum(qref>0)),
    'hour_joint_correct_and_80pct':int(hm.sum()),'active_hours':int(np.sum(href>0)),
    'future_selected_original_signal_not_causal':True,'not_actual_broker_fills':True,
    'NOT_ORIGINAL_S1_15F30S':True,'NOT_REAL_R9_DYNAMIC_EXIT':True,
    'cash_per_lot_and_margin_not_modeled':True})
   for q in range(len(qref)):
    n=int(goodq[q]+badq[q]);ref=int(qref[q]);
    allq.append({'source':source,'month':mon,'label':label,
     'quarter_UTC':refs['rows'][q]['utc_quarter'],'original_R9_SYNTH_ref':ref,
     'actual_quote_fill_strictGOOD_60s':int(goodq[q]),'completedBAD':int(badq[q]),
     'rightCENSOR':int(cenq[q]),'reject_original_signal':int(rejq[q]),
     'busy_original_signal':int(busyq[q]),
     'completed_precision':None if n==0 else int(goodq[q])/n,
     'joint_80pct_and_correct_count':int(qm[q]) if ref else '',
     'future_selected_offline_hindsight_only':True})
   for h in range(len(href)):
    n=int(hgood[h]+hbad[h]);ref=int(href[h]);
    allh.append({'source':source,'month':mon,'label':label,
     'hour_UTC':refs['rows'][4*h]['utc_hour'],'original_R9_SYNTH_ref':ref,
     'actual_quote_fill_strictGOOD_60s':int(hgood[h]),'completedBAD':int(hbad[h]),
     'completed_precision':None if n==0 else int(hgood[h])/n,
     'joint_80pct_and_correct_count':int(hm[h]) if ref else '',
     'future_selected_offline_hindsight_only':True})
   arrays[label+'_signal_ord']=ix.copy();arrays[label+'_future_selected_side']=side.copy();
   arrays[label+'_fill_ord']=filled;arrays[label+'_first_observed_exit_ord']=exited;
   arrays[label+'_outcome']=state;arrays[label+'_realized_quote_pnl_raw_or_sentinel']=net
   print(source,mon,label,'good',g,'bad',bad,'reject',rej,'busy',busy,'censor',censored,
       'precision',round(g/(g+bad),5) if g+bad else 'none',
       'Q joint',qm.sum(),'/',int(np.sum(qref>0)),'H joint',hm.sum(),'/',int(np.sum(href>0)),flush=True)
 def writecsv(f,rec):
  with open(f,'w',newline='') as stream:
   writer=csv.DictWriter(stream,fieldnames=list(rec[0]));writer.writeheader();writer.writerows(rec)
 tag=f'R18_LATENCY_{source}_{mon}'
 c=outdir/(tag+'_9_SCENARIO_RESULTS.csv');q=outdir/(tag+'_ALL_UTC_QUARTERS.csv');h=outdir/(tag+'_ALL_UTC_HOURS.csv')
 npz=outdir/(tag+'_ALL_FROZEN_SOURCE_ORDINAL_OUTCOME_TRACES.npz')
 writecsv(c,rows);writecsv(q,allq);writecsv(h,allh);np.savez_compressed(npz,**arrays)
 receipt={'label':'R18_FROZEN_FUTURE_SELECTED_SIGNAL_DELAY_STRESS_NOT_CAUSAL','source':source,'month':mon,
  'source_pin':provenance,'r18_original_quote_signal_count':len(ix),
  'exact_UTC_reference_quarter_sha256':refs['sha256'],'records':rows,
  'member_outputs':{p.name:{'bytes':p.stat().st_size,'sha256':r18.sha(p)} for p in (c,q,h,npz)},
  'not_live_broker_fills':True,'not_training_or_independent_OOS':True,
  'model_60s_firsttarget_before_adverse_not_original_R9_exit':True,
  'zero_delay_noslip_hindsight_is_tautological':True,'elapsed_sec':round(time.monotonic()-start,2)}
 (outdir/(tag+'_SOURCE_SHA_AND_RESULT_RECEIPT.json')).write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 print('COMPLETE',source,mon,'seconds',receipt['elapsed_sec'],flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=tuple(r18.PINS),required=True)
 p.add_argument('--month',choices=tuple(r18.OFFSETS),required=True)
 a=p.parse_args();one(a.source,a.month)
