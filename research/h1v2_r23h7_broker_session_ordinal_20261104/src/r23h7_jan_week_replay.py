"""R23H-0007 PREREGISTERED JANUARY 1–7 2026 pilot, source-exact minimum-H.

Uses separately fitted BROKER-MONTH in-sample models from full January,
but score features at decision time use only true previous quote ordinals.
Original R9/reference calendar used ONLY after actions, to evaluate 15-minute,
hour and day counts. One-position exact quote chronology and modeled stop/fullH
as in parent R23H24, whose optimistic gap-reacquisition is non-deployable.
This IS NOT full-month evaluation or blind OOS; benchmark may be negative.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,os
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
BASE=Path(os.environ.get('R23H24_WORKSPACE','/mnt/data/r23h24_workspace')).resolve()
sys.path.insert(0,str(BASE/'new_source'))
sys.path.insert(0,str(BASE/'r24_source_archive'/'source'))
from r23h24_competing_hazard import source_arrays
from r23h24_full_replay import replay_exact
import r24_firstpass_engine as upstream
from r23h7_clock_news import clock_features
H=(15000,30000,60000)
POLICIES=(
 ('W7_E00_UTILITY_ALL',-1,-1.0),
 ('W7_E01_MIXED_0',-1,0.0),
 ('W7_E02_MIXED_P010',-1,0.10),
 ('W7_E03_H15_0',0,0.0),
 ('W7_E04_H30_0',1,0.0),
 ('W7_E05_H60_0',2,0.0),
)

def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load_scores(source,daymax=7):
 arrays=[];receipts=[];cursor=0
 for day in range(1,daymax+1):
  p=BASE/'r23h7_scores'/source/'01'/f'R23H7_{source}_01_{day:02d}_PREDICTIONS.npz'
  receipt=json.loads(p.with_suffix('.receipt.json').read_text())
  if sha(p)!=receipt['sha256'] or cursor!=receipt['start_row']:
   raise AssertionError(('DAY_SHARD_MISSING_OR_SHA_INVALID',source,day))
  with np.load(p,allow_pickle=False) as z:
   a=z['cause5'];b=z['held'];w=z['wait10']
  assert a.shape==(receipt['rows'],2,3,5) and len(w)==len(a)
  arrays.append((a,b,w));receipts.append(receipt)
  cursor=receipt['end_row']
 return (np.concatenate([a[0] for a in arrays],axis=0),
         np.concatenate([a[1] for a in arrays],axis=0),
         np.concatenate([a[2] for a in arrays],axis=0)),cursor,receipts

def actions(cause,held,wait,force_h):
 # Original R9 SYNTH hour/quarter volume is NEVER consulted in action selection.
 u=cause[:,:,:,1]+0.40*held-0.85*cause[:,:,:,0]-0.20*cause[:,:,:,3]-0.50*cause[:,:,:,4]-0.15*wait[:,None,None]
 u=u-0.025*np.arange(3)[None,None,:]
 n=len(u)
 if force_h>=0:
  which=np.argmax(u[:,:,force_h],axis=1)
  h=np.full(n,force_h,np.int8);side=which.astype(np.int8)
 else:
  which=np.argmax(u.reshape(n,6),axis=1)
  side=(which//3).astype(np.int8);h=(which%3).astype(np.int8)
 score=u[np.arange(n),side,h].astype(np.float32)
 return side,h,score

def write(path,rows):
 path.parent.mkdir(exist_ok=True,parents=True)
 tmp=path.with_suffix('.tmp')
 with tmp.open('w',newline='',encoding='utf8') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 os.replace(tmp,path)

def run(source):
 (cause,heldprob,wait),n,records=load_scores(source)
 a=source_arrays(source,'01')
 if n<=0 or n>=len(a['t']):raise AssertionError('INVALID_WEEK_RANGE')
 ts,b,ask=upstream.raw_month(source,'01',verify=True)
 qtime,qref=upstream.calendar_reference('01')
 # exact source first 7 UTC calendar days, including R9-ref-zero buckets
 cutoff=int(datetime(2026,1,8,tzinfo=timezone.utc).timestamp()*1000)
 qtime=qtime[:7*96];qref=qref[:7*96]
 assert len(qtime)==672 and len(qref)==672
 gap=np.flatnonzero(np.diff(ts)>15000).astype(np.int32)+1
 fill=np.asarray(a['f'][:n]);gp=np.searchsorted(gap,np.maximum(fill,0),side='right')
 gap_resume=np.full(n,len(ts)-1,np.int32)
 good=gp<len(gap)
 gap_resume[good]=gap[gp[good]]
 outroot=Path(__file__).resolve().parents[1]/'results'/'jan_week1_replay'/source
 outroot.mkdir(exist_ok=True,parents=True)
 models_receipt=BASE/'r23h7_models'/source/'01'/'R23H7_FIT_RECEIPT.json'
 outputs=[];allhash={}
 for name,force,threshold in POLICIES:
  side,hi,score=actions(cause,heldprob,wait,force)
  trace=replay_exact(a['t'][:n],fill,side,hi,score,a['held'][:n],a['stop_ix'][:n],a['end_ix'][:n],a['l'][:n],ts,gap_resume,threshold)
  take=trace[:,3]>=0
  true_fill_ts=ts[np.maximum(trace[:,3],0)]
  qt=true_fill_ts//900000*900000
  k=np.searchsorted(qtime,qt)
  valid=take&(true_fill_ts<cutoff)&(k<len(qref))&(qtime[np.minimum(k,len(qref)-1)]==qt)
  k=k[valid];tr=trace[valid]
  outcome={
   'filled':np.bincount(k,minlength=len(qref)),
   'target':np.bincount(k,weights=tr[:,5],minlength=len(qref)).astype(np.int32),
   'held':np.bincount(k,weights=tr[:,6],minlength=len(qref)).astype(np.int32),
   'stop':np.bincount(k,weights=tr[:,7],minlength=len(qref)).astype(np.int32),
   'censor':np.bincount(k,weights=tr[:,8],minlength=len(qref)).astype(np.int32),
   'joint':np.bincount(k,weights=tr[:,5]*tr[:,6],minlength=len(qref)).astype(np.int32)
  }
  ref=np.asarray(qref,dtype=np.int32)
  local={};metrics={}
  for kind,window in (('QUARTER',1),('HOUR',4),('DAY',96)):
   rref=ref.reshape(-1,window).sum(axis=1)
   obs={key:val.reshape(-1,window).sum(axis=1) for key,val in outcome.items()}
   clock=clock_features(np.asarray(qtime[::window],np.int64))
   rows=[]
   for j,orig in enumerate(rref):
    filled=int(obs['filled'][j]);tp=int(obs['target'][j]);h=int(obs['held'][j]);s=int(obs['stop'][j]);ce=int(obs['censor'][j]);joint=int(obs['joint'][j])
    rows.append({'source':source,'model_month':'2026-01','UTC_'+kind:datetime.fromtimestamp(int(qtime[j*window])/1000,timezone.utc).isoformat(),
      'policy':name,'R9_SYNTH_original_source_UTC_reference':int(orig),'filled':filled,
      'target_first':tp,'held_full_H':h,'target_AND_held':joint,'adverse_stop':s,'censored':ce,
      'target_first_precision_completed':tp/filled if filled else '',
      'held_precision_completed':h/filled if filled else '',
      'volume_meets_original_reference':int(filled>=orig) if orig else '',
      'joint80_firstTP_and_R9_original_volume':int(filled>0 and orig>0 and filled>=orig and tp>=0.8*filled),
      'joint80_heldH_and_R9_original_volume':int(filled>0 and orig>0 and filled>=orig and h>=0.8*filled),
      'nominal_london_local_daytime_proxy':int(clock[j,6]),
      'nominal_newyork_local_daytime_proxy':int(clock[j,7]),
      'nominal_sydney_local_daytime_proxy':int(clock[j,4]),
      'nominal_tokyo_local_daytime_proxy':int(clock[j,5]),
      'historic_prop_permission':'UNKNOWN','historic_MT5_FF_highmedium_news':'UNKNOWN',
      'is_full_month':False,'future_privileged_training':'YES_INSAMPLE_MONTH_FIT',
      'action_uses_future_quote':'NO_ASOF_FEATURES_ONLY',
      'source_gap_external_position_reconciliation':'UNKNOWN_OPTIMISTIC_PARENT_R23H24'})
   p=outroot/f'{name}_{kind}_FULL_WEEK.csv';write(p,rows);allhash[p.name]=sha(p)
   local[kind]=rows
   metrics[kind]={'total_bins':len(rows),'active_reference_bins':sum(bool(r['R9_SYNTH_original_source_UTC_reference']) for r in rows),
      'reference_total':int(rref.sum()),'filled':int(obs['filled'].sum()),
      'target_first':int(obs['target'].sum()),'held_H':int(obs['held'].sum()),
      'stop':int(obs['stop'].sum()),'censored':int(obs['censor'].sum()),
      'quota_meet':sum(r['volume_meets_original_reference']==1 for r in rows),
      'joint80_target_R9':sum(r['joint80_firstTP_and_R9_original_volume'] for r in rows),
      'joint80_held_R9':sum(r['joint80_heldH_and_R9_original_volume'] for r in rows)}
  for field in ('reference_total','filled','target_first','held_H','stop','censored'):
   assert len({metrics[k][field] for k in metrics})==1,(name,field)
  traced=outroot/f'{name}_ALL_SOURCE_ORDINALS_ATTEMPTS.npy'
  with traced.open('wb') as f:np.save(f,trace,allow_pickle=False)
  allhash[traced.name]=sha(traced)
  outputs.append({'policy':name,'source':source,'cutoff_UTC':'2026-01-08T00:00:00+00:00',
    'actual_all_policy_attempts':len(trace),'actual_filled_observed_in_week':int(valid.sum()),'calendar':metrics})
 rec={'classification':'R23H7_0007_INSAMPLE_WEEK1_CAUSAL_ASOF_REPLAY_NOT_OOS',
  'source':source,'raw_source_SHA':upstream.sha(upstream.source_file(source,'01')),
  'model_receipt_SHA':sha(models_receipt),'day_score_SHA':[r['sha256'] for r in records],
  'source_signal_rows_through_7d':n,'policies':outputs,'output_member_SHA256':allhash,
  'trade_one_position':'PARENT_R23H24_QUOTE_ORDINAL_MODELED',
  'news':'UNKNOWN','prop_firm_hours':'UNKNOWN','broker_flat_on_gap':'UNKNOWN',
  'not_cashPnL':True,'not_full_month_or_OOS':True}
 p=outroot/'R23H7_JAN_WEEK1_6_CASES_SHA_AND_CALENDAR_RECEIPT.json';p.write_text(json.dumps(rec,indent=2)+'\n')
 print(json.dumps({'source':source,'cases':outputs},indent=2),flush=True)
 return rec
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'),required=True)
 a=ap.parse_args();run(a.source)
