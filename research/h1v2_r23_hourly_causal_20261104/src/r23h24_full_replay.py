"""Causal-score selection, exact observed-quote min-H occupancy, lossless UTC calendars.
This research simulator is not a funded account or live broker execution emulator.
Original R23 R9 SYNTH quota appears ONLY in post-action report joins.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from numba import njit
from r23h24_competing_hazard import BASE,source_arrays,FEEDS
sys.path.insert(0,str(BASE/'r24_source_archive'/'source'))
import r24_firstpass_engine as upstream
H=(15000,30000,60000)
POLICIES=(
 ('E00_VOLUME_FIRST_H15',0,-1.00),
 ('E01_VOLUME_FIRST_H30',1,-1.00),
 ('E02_VOLUME_FIRST_H60',2,-1.00),
 ('E03_MIXED_ANY_H',-1,-1.00),
 ('E04_MIXED_SCORE_FLOOR_M025',-1,-0.25),
 ('E05_MIXED_SCORE_FLOOR_000',-1,0.00),
 ('E06_MIXED_SCORE_FLOOR_P025',-1,0.25),
 ('E07_H15_SCORE_FLOOR_000',0,0.00),
)

@njit(cache=False)
def replay_exact(sig_t,fill,selected_side,selected_h,selected_score,held,stop_ix,end_ix,labels,source_t,censor_resume_ix,cutoff):
 n=len(sig_t)
 out=np.full((n,10),-1,np.int64) # selected signal row, side,H,fill ordinal,exit ordinal,TP,HELD,STOP,CENSOR,score raw
 k=0;last_exit_ms=-9_999_999_999_999_999
 for i in range(n):
  if sig_t[i]<=last_exit_ms:continue
  if selected_score[i]<cutoff:continue
  side=selected_side[i];h=selected_h[i];f=fill[i]
  if side<0:continue
  # Attempted real quote fill is future to signal, and may be rejected.
  if f<0:
   out[k]=np.array((i,side,h,-1,-1,0,0,0,0,int(selected_score[i]*1e6)),np.int64)
   k+=1;continue
  status=held[i,side,h]
  if status==0: exit_ix=stop_ix[i,side,h]
  elif status==1:exit_ix=end_ix[i,h]
  else:
   # GAP/CENSOR is UNKNOWN: assume position externally resolved only after
   # next observed source gap and full 300s fresh re-acquisition.
   # This is an UPPER research continuation assumption, NOT broker execution proof.
   exit_ix=censor_resume_ix[i]
  if exit_ix<f or exit_ix>=len(source_t):
   # Invalid or missing timestamp / failed close receipt => quarantine this event
   out[k]=np.array((i,side,h,f,-1,0,0,0,1,int(selected_score[i]*1e6)),np.int64)
   k+=1;last_exit_ms=source_t[-1];continue
  lab=labels[i,side,h]
  out[k,0]=i;out[k,1]=side;out[k,2]=h;out[k,3]=f;out[k,4]=exit_ix
  out[k,5]=1 if lab==1 else 0
  out[k,6]=1 if status==1 else 0
  out[k,7]=1 if status==0 else 0
  out[k,8]=1 if status==2 else 0
  out[k,9]=int(selected_score[i]*1e6)
  k+=1
  last_exit_ms=source_t[exit_ix]+(300000 if status==2 else 0)
 return out[:k]

def load_all_scores(source,mon,signal_t):
 n=len(signal_t);root=BASE/'score_days'/source/mon
 out=np.zeros((n,2,3,4),np.float32);held=np.zeros((n,2,3),np.float32);wait=np.zeros(n,np.float32)
 cursor=0;sha=[]
 days=(datetime(2026, int(mon)+1,1,tzinfo=timezone.utc)-datetime(2026,int(mon),1,tzinfo=timezone.utc)).days
 for day in range(1,days+1):
  stem=f'R23H24_{source}_{mon}_{day:02d}_CAUSAL_SCORE_DAY.npz';p=root/stem
  d=json.loads((root/(stem+'.receipt.json')).read_text())
  if d['start_row']!=cursor:raise AssertionError('NONCONTIGUOUS_DAY_SCORE')
  if d['sha256']!=hashlib.file_digest(p.open('rb'),'sha256').hexdigest():raise AssertionError('SCORE_SHA_CONFLICT')
  with np.load(p,allow_pickle=False) as z:
   o=z['cause'];h=z['held'];w=z['wait10']
  size=len(w);assert size==d['rows']
  out[cursor:cursor+size]=o;held[cursor:cursor+size]=h;wait[cursor:cursor+size]=w
  cursor+=size;sha.append(d['sha256'])
 if cursor!=n:raise AssertionError('MONTH_SOURCE_SCORE_MISSING')
 return out,held,wait,sha

def policy_scores(cause,held,wait,force_h):
 # First target, first stop, quote-gap, event-free, minimum-H survivability.
 # WAIT is independently scored as the chance of source-level opportunity 10s later.
 utility=(cause[:,:,:,1] + 0.70*held -0.85*cause[:,:,:,0]
          -0.05*cause[:,:,:,3]-0.20*wait[:,None,None])
 # No reference-volume or future label is read by this function.
 if force_h>=0:
  choice=np.argmax(utility[:,:,force_h],axis=1)
  hi=np.full(len(choice),force_h,np.int8);side=choice.astype(np.int8)
  score=utility[np.arange(len(choice)),side,hi].astype(np.float32)
 else:
  choice=np.argmax(utility.reshape(len(utility),6),axis=1)
  side=(choice//3).astype(np.int8);hi=(choice%3).astype(np.int8)
  score=utility[np.arange(len(choice)),side,hi].astype(np.float32)
 return side,hi,score

def write_csv(path,rows):
 if not rows:raise ValueError('NO_CALENDAR_ROWS')
 tmp=path.with_suffix('.tmp')
 with tmp.open('w',newline='',encoding='utf8') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 os.replace(tmp,path)

def run(source,mon,policy_indices=None):
 a=source_arrays(source,mon)
 cause,heldprob,wait,scsha=load_all_scores(source,mon,a['t'])
 ts,b,ask=upstream.raw_month(source,mon,verify=True)
 qtime,qref=upstream.calendar_reference(mon)
 assert len(qref)%96==0 and len(qtime)==len(qref)
 outdir=BASE/'evaluated'/source/mon;outdir.mkdir(parents=True,exist_ok=True)
 # Source quote gaps after a potential fill, never an action feature.
 gi=np.flatnonzero(np.diff(ts)>15000)+1
 fills=np.asarray(a['f']);cursor=np.searchsorted(gi,np.maximum(fills,0),side='right')
 censor_resume_ix=np.where(cursor<len(gi),gi[np.minimum(cursor,len(gi)-1)],len(ts)-1).astype(np.int32) if len(gi) else np.full(len(fills),len(ts)-1,np.int32)
 allmeta=[];digest={};total_good=0
 for policy_index,(name,forced,threshold) in enumerate(POLICIES):
  if policy_indices is not None and policy_index not in policy_indices: continue
  side,hi,score=policy_scores(cause,heldprob,wait,forced)
  # Every censored position has unknown dealer status. Re-entry after source
  # 300s quote readiness is an explicitly optimistic flat-at-reacquisition assumption.
  # Under a strict fail-closed deployment contract, all subsequent actions require
  # actual broker position reconciliation, which is unavailable in the archive.
  trace=replay_exact(a['t'],a['f'],side,hi,score,a['held'],a['stop_ix'],a['end_ix'],a['l'],ts,censor_resume_ix,threshold)
  src_rows=trace[:,0];fill=trace[:,3];valid=fill>=0
  actual_fill_ts=np.where(valid,ts[np.maximum(fill,0)],0)
  q=np.searchsorted(qtime,actual_fill_ts//900000*900000)
  inmonth=valid&(q<len(qref))&(qtime[np.minimum(q,len(qref)-1)]==actual_fill_ts//900000*900000)
  ids=q[inmonth]
  count=np.bincount(ids,minlength=len(qref))
  TP=np.bincount(ids,weights=trace[inmonth,5],minlength=len(qref)).astype(np.int32)
  HOLD=np.bincount(ids,weights=trace[inmonth,6],minlength=len(qref)).astype(np.int32)
  JOIN=np.bincount(ids,weights=trace[inmonth,5]*trace[inmonth,6],minlength=len(qref)).astype(np.int32)
  stop=np.bincount(ids,weights=trace[inmonth,7],minlength=len(qref)).astype(np.int32)
  cens=np.bincount(ids,weights=trace[inmonth,8],minlength=len(qref)).astype(np.int32)
  def rollup(div):
   return [v.reshape(-1,div).sum(axis=1) for v in (qref,count,TP,HOLD,JOIN,stop,cens)]
  qc=[qref,count,TP,HOLD,JOIN,stop,cens]; hc=rollup(4);dc=rollup(96)
  def emit(typ,keys,vals):
   rr=[]
   for j,qt in enumerate(keys):
    orig,ct,tp,safe,joint,st,censor=(int(x[j]) for x in vals)
    rr.append({'source':source,'month':mon,'policy':name,'utc_'+typ:qt,
        'R9_SYNTH_original_exact_UTC_reference':orig,'filled':ct,'target_first':tp,'held_full_H':safe,
        'joint_target_and_full_held':joint,'adverse_stop_by_H':st,'quote_gap_censored':censor,
        'target_first_accuracy':tp/ct if ct else '', 'fullH_survival_fraction':safe/ct if ct else '',
        'volume_meets_reference':int(ct>=orig) if orig else '',
        'target80_and_R9_volume':int(tp>=0.8*ct and ct>=orig) if ct and orig else 0,
        'held80_and_R9_volume':int(safe>=0.8*ct and ct>=orig) if ct and orig else 0,
        'joint80_and_R9_volume':int(joint>=0.8*ct and ct>=orig) if ct and orig else 0,
        'calendar_news_status':'UNKNOWN_NO_VERIFIED_POINT_IN_TIME_MT5_OR_FF',
        'historical_prop_authorization':'UNKNOWN_OWNER_RULES_NOT_SUPPLIED'})
   p=outdir/f'{name}_{typ.upper()}_FULL_UNABRIDGED.csv'
   write_csv(p,rr);digest[p.name]=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
   return rr
  quarters=emit('quarter',[datetime.fromtimestamp(int(qt)/1000,timezone.utc).isoformat() for qt in qtime],qc)
  hours=emit('hour',[datetime.fromtimestamp(int(qt)/1000,timezone.utc).isoformat() for qt in qtime[::4]],hc)
  days=emit('day',[datetime.fromtimestamp(int(qt)/1000,timezone.utc).date().isoformat() for qt in qtime[::96]],dc)
  # preserve *every selected* quote ordinal and direction (positive/negative/censored included)
  full=outdir/f'{name}_ALL_EXACT_SELECTED_QUOTE_ORDINALS.npy'
  with full.with_suffix('.tmp').open('wb') as f:np.save(f,trace,allow_pickle=False)
  os.replace(full.with_suffix('.tmp'),full);digest[full.name]=hashlib.file_digest(full.open('rb'),'sha256').hexdigest()
  cq=int(np.sum((qref>0)&(count>=qref)))
  jointq=int(sum(r['joint80_and_R9_volume'] for r in quarters))
  mh={'source':source,'month':mon,'policy':name,'threshold':threshold,'force_horizon_ms':H[forced] if forced>=0 else 'CAUSAL_MAX',
      'signals_with_action_attempt':len(trace),'filled_in_month':int(inmonth.sum()),'unfilled_attempts':int((fill<0).sum()),
      'outside_month_fills':int(np.sum(valid&~inmonth)),
      'target_first':int(TP.sum()),'fullH_survived':int(HOLD.sum()),'joint_target_and_fullH':int(JOIN.sum()),
      'adverse_stop_by_H':int(stop.sum()),'quote_gap_censored':int(cens.sum()),
      'ref_active_quarters':int(np.sum(qref>0)),'q_volume_quota_met':cq,
      'q_joint80_target_and_volume':int(sum(r['target80_and_R9_volume'] for r in quarters)),
      'q_joint80_fullheld_and_volume':int(sum(r['held80_and_R9_volume'] for r in quarters)),
      'q_joint80_target_fullheld_and_volume':jointq,
      'ref_active_hours':int(np.sum(hc[0]>0)),
      'h_joint80_target_and_volume':int(sum(r['target80_and_R9_volume'] for r in hours)),
      'h_joint80_target_fullheld_and_volume':int(sum(r['joint80_and_R9_volume'] for r in hours)),
      'ref_source_month_total':int(qref.sum()),'complete_quarters':len(quarters), 'complete_hours':len(hours), 'complete_days':len(days)}
  assert count.sum()==inmonth.sum()
  assert TP.sum()<=count.sum() and stop.sum()+HOLD.sum()+cens.sum()==count.sum()
  allmeta.append(mh)
  print('REPLAY_POLICY_COMPLETE',json.dumps(mh),flush=True)
 result={'source':source,'month':mon,'classification':'HEAVILY_INSAMPLE_MODEL_AND_SOURCE_EXACT_OFFLINE_TEST_ONLY',
   'original_raw_SHA':upstream.sha(upstream.source_file(source,mon)),'scored_day_sha256':scsha,
   'source_rows':len(ts),'source_decisions':len(a['t']),
   'policy_metrics':allmeta,'all_files_SHA256':digest,'causal_action_inputs':'historical-prefix price/quote/clock; oracle and R9 quotas excluded',
   'STOP_LABEL_CONTRACT':'full held until minH or actual STOP quote, target before STOP separately recorded; gap/censor unknown, continuation requires explicit broker-flat assumption',
   'censor_reentry_assumption':'OPTIMISTIC_REACQUIRE_300S_AFTER_NEXT_ACTUAL_QUOTE_GAP_FLAT_UNKNOWN_BROKER_POSITION',
   'model_fit_is_in_sample_and_oos_unknown':True, 'cash_profitability_not_tested':True,'news_and_prop_hours_unknown':True}
 tag='ALL' if policy_indices is None else 'POLICY_'+('_'.join(str(x) for x in sorted(policy_indices)))
 p=outdir/f'R23H24_{source}_{mon}_{tag}_ATOMIC_RECEIPT.json'
 p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 return result

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=FEEDS,required=True);ap.add_argument('--month',choices=('01','02','06','07'),required=True)
 ap.add_argument('--policy-indices',nargs='*',type=int,choices=range(len(POLICIES)))
 args=ap.parse_args();run(args.source,args.month,None if args.policy_indices is None else set(args.policy_indices))
