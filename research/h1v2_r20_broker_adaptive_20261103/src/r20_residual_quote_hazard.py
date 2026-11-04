"""R20 additive fully observed quote-source hindsight capacity falsifier.

Do not confuse source-owned future labels with a causal BUY/SELL/WAIT trader.
The code holds all previously audited R19-S3 winning intervals fixed, and attempts
additional nonoverlapping wins only inside its previously failed UTC quarters.
Both source feed and actual filled quote must pay full spread and nominal fee.
Stop +100 raw adverse versus first +100 raw net before max hold, independent sides.
Source history warmup after >15s raw quote gaps remains 300,000ms.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,time
from pathlib import Path
import numpy as np
from numba import njit
ROOT=Path('/mnt/data')
HERE=ROOT/'h1v2_r20_last46'
R19=ROOT/'h1v2_r19_broker_union'
R18=ROOT/'h1v2_r18_dualbroker'
sys.path[:0]=[str(R19/'src'),str(R18/'src')]
import r19_s3_targeted_source_admission as s3
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen
from r18_s2_latency_frontier import pack_future_good

FEE=20;TP=100;ADVERSE=100;GAP=15000;WARMUP=300000
SCENARIOS=(
 # name, source spread raw, fill spread raw, nominal delay ms, slip/leg raw, horizon ms, stride ms
 ('C1_ASOF_EVERY_DISTINCT_MS_CAP4000_H60_100MS',4000,4000,100,0,60000,1),
 ('C2_ASOF_EVERY_DISTINCT_MS_CAP8000_H60_100MS',8000,8000,100,0,60000,1),
 ('C3_ASOF_EVERY_DISTINCT_MS_CAP8000_H30_100MS',8000,8000,100,0,30000,1),
 ('C4_ASOF_EVERY_DISTINCT_MS_CAP8000_H15_100MS',8000,8000,100,0,15000,1),
 ('C5_ASOF_EVERY_DISTINCT_MS_CAP8000_H60_500MS_SLIP20',8000,8000,500,20,60000,1),
 ('C6_ASOF_FIRST25MS_CAP8000_H60_100MS',8000,8000,100,0,60000,25),
)

@njit(cache=False)
def independent_both_sides(t,b,a,fills,slip,horizon):
 """Outcome:1 good +$0.10 NET; 0 adverse stop;2 timed out;-3 source gap/censor.
 First later *observed* quote; no same-millisecond retro-exit; no OHLC.
 Stop on nominal opening liquidation price at -$0.10, not from entry price.
 On stop or timeout model executable net at respective observed liquidation quote,
 with extra slip per leg on entry/exit. Fee units are quote-price 0.001USD.
 """
 n=len(fills); code=np.full((n,2),-3,np.int8); exits=np.full((n,2),-1,np.int32);net=np.full((n,2),-2147483647,np.int32)
 for k in range(n):
  f=fills[k]
  for side in range(2):
   buy=side==0
   opening=b[f] if buy else a[f]
   entry=(a[f]+slip) if buy else (b[f]-slip)
   prev=t[f];done=False
   for j in range(f+1,len(t)):
    if t[j]==t[f]:continue
    if t[j]-prev>GAP:code[k,side]=-3;done=True;break
    prev=t[j]
    liq=b[j] if buy else a[j]
    # reject post-horizon first quote as potentially stale. It is a timeout ONLY
    # if a proper causal observed time boundary quote exists within 15s.
    if t[j]>t[f]+horizon:
     if t[j]-(t[f]+horizon)<=GAP:
      code[k,side]=2;exits[k,side]=j
      net[k,side]=liq-entry-FEE-slip if buy else entry-liq-FEE-slip
     else:code[k,side]=-3
     done=True;break
    stopped=liq<=opening-ADVERSE if buy else liq>=opening+ADVERSE
    pnl=liq-entry-FEE-slip if buy else entry-liq-FEE-slip
    if stopped:
     code[k,side]=0;exits[k,side]=j;net[k,side]=pnl;done=True;break
    if pnl>=TP:
     code[k,side]=1;exits[k,side]=j;net[k,side]=pnl;done=True;break
   if not done:code[k,side]=-3
 return code,exits,net

def sha(p):
 h=hashlib.sha256();f=open(p,'rb')
 with f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()

def write_csv(path,rows):
 if not rows:raise ValueError('EMPTY_RESULTS')
 with open(path,'w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

def source_candidates(t,b,a,qkeys,failq,stride):
 """Observed first quote in each stride bucket within previously failed quarters.
 All raw quote gaps scanned, not just 25ms candidate-subset gaps.
 """
 seg=[];rawcounts=0
 for q in failq:
  lo=int(qkeys[q])*900000;hi=lo+900000
  i=int(np.searchsorted(t,lo,'left'));j=int(np.searchsorted(t,hi,'left'))
  if j>i:seg.append(np.arange(i,j,dtype=np.int32));rawcounts+=j-i
 if not seg:return np.empty(0,np.int32),{'raw_quotes':0,'sampled':0,'fresh':0}
 ids=np.concatenate(seg)
 first=(ids==0)|(t[ids]//stride!=t[np.maximum(ids-1,0)]//stride)
 ix=ids[first]
 postgrid=len(ix)
 gaps=np.flatnonzero(np.diff(t)>GAP).astype(np.int32)+1
 gp=np.searchsorted(gaps,ix,side='right')-1
 anchor=np.where(gp>=0,gaps[np.maximum(gp,0)],0)
 ix=ix[(t[ix]-t[anchor])>=WARMUP]
 return ix,{'raw_quotes':int(rawcounts),'sampled':int(postgrid),'fresh':int(len(ix))}

def get_old(source,mon,t,refs):
 src=R19/('results_v2' if (source=='DUKASCOPY_RAW' and mon=='02') or (source=='MT5_BROKER_EXPORT' and mon in ('06','07')) else 'results')
 k='lag100_slip0_fillcap4000'
 with np.load(src/f'R19_{source}_{mon}_EXACT_SELECTED_ORDINAL_TRACES.npz',allow_pickle=False) as z:
  of=z[k+'__actual_observed_fill_quote_ordinal'].astype(np.int32)
  oe=z[k+'__first_target_exit_quote_ordinal'].astype(np.int32)
 with np.load(R19/'results_s3_new_admission'/f'R19S3_{source}_{mon}_ALL_TARGETED_CANDIDATE_SOURCE_ORDINALS_AND_DUAL_ACTION_LABELS.npz',allow_pickle=False) as z:
  nf=z['added_actual_fill_ord'].astype(np.int32)
  ne=z['added_firstTP_exit_ord'].astype(np.int32)
 fi=np.r_[of,nf];ex=np.r_[oe,ne]
 o=np.argsort(t[fi],kind='stable');fi=fi[o];ex=ex[o]
 if len(fi)>1 and np.any(t[fi[1:]]<=t[ex[:-1]]):raise ValueError('ORIGINAL_R19S3_POSITION_COLLISION')
 if not np.all(t[ex]>t[fi]):raise ValueError('ORIGINAL_FUTURE_INTERVAL_INVALID')
 qkeys=refs['qkeys'];qref=refs['qref']
 q0=qkeys[0]
 qcounts=np.bincount(t[fi]//900000-q0,minlength=len(qref)).astype(np.int32)
 miss=np.flatnonzero((qref>0)&(qcounts<qref))
 return fi,ex,qcounts,miss

def exclude_occupied(t,candfills,candex,oldf,olde):
 if not len(oldf):return np.ones(len(candfills),bool)
 p=np.searchsorted(t[olde],t[candfills],side='left')
 valid=p<len(oldf)
 q=np.minimum(p,len(oldf)-1)
 valid&=(t[oldf[q]]<=t[candex])
 return ~valid

def run(source,mon,scenario_names=None):
 started=time.monotonic();t,b,a,_,_,_,provenance=get_frozen(source,mon)
 refs=r18.refs_for_month(mon,ROOT);qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 original_f,original_e,baseline_q,miss=get_old(source,mon,t,refs)
 orig_h=baseline_q.reshape(-1,4).sum(axis=1)
 prefix=f'R20_{source}_{mon}'
 scenarios=[x for x in SCENARIOS if scenario_names is None or x[0] in scenario_names]
 allresults=[];allquarter=[];allhour=[];bins={};outcome_summary={}
 for name,source_cap,fill_cap,lag,slip,horizon,stride in scenarios:
  cand,counts=source_candidates(t,b,a,qkeys,miss,stride)
  newspread=a[cand].astype(np.int64)-b[cand].astype(np.int64)
  cand=cand[(newspread>=0)&(newspread<=source_cap)]
  if len(cand):
   target=t[cand]+lag
   fc=np.searchsorted(t,target,side='left')
   j=np.minimum(fc,len(t)-1)
   valid=(fc<len(t))&(j>cand)&(t[j]>t[cand])&(t[j]-target<=1000)
   valid&=(t[j]>=qkeys[0]*900000)&(t[j]<(qkeys[-1]+1)*900000)
   fillspread=(a[j].astype(np.int64)-b[j].astype(np.int64))
   valid&=(fillspread>=0)&(fillspread<=fill_cap)
   accepted_signals=cand[valid];accepted_fills=j[valid]
   # Group equal eventual fill ordinals, preserving deterministic earliest signal
   # from actually observed as-of candidates. Avoid future-informed resampling.
   fillids,indices=np.unique(accepted_fills,return_index=True)
   source_sig=accepted_signals[indices]
   codes,exits,net=independent_both_sides(t,b,a,fillids.astype(np.int32),slip,horizon)
   win=np.argwhere(codes==1)
   trial_fill=fillids[win[:,0]].astype(np.int32)
   trial_exit=exits[win[:,0],win[:,1]].astype(np.int32)
   trial_side=np.where(win[:,1]==0,1,-1).astype(np.int8)
   trial_sig=source_sig[win[:,0]].astype(np.int32)
   trial_net=net[win[:,0],win[:,1]].astype(np.int32)
   nov=exclude_occupied(t,trial_fill,trial_exit,original_f,original_e)
   f=trial_fill[nov]; ex=trial_exit[nov]
   picked=pack_future_good(t,f,ex,np.ones(len(f),dtype=bool))
   addf=f[picked];adde=ex[picked];adds=trial_side[nov][picked];addsig=trial_sig[nov][picked];addnet=trial_net[nov][picked]
   if len(addf)>1 and np.any(t[addf[1:]]<=t[adde[:-1]]):raise ValueError('NEW_ONE_POSITION_CONFLICT')
   fullf=np.r_[original_f,addf];fulle=np.r_[original_e,adde];o=np.argsort(t[fullf],kind='stable')
   if len(fullf)>1 and np.any(t[fullf[o][1:]]<=t[fulle[o][:-1]]):raise ValueError('ADDED_VS_OLD_CONFLICT')
   delta=np.bincount(t[addf]//900000-qkeys[0],minlength=len(qref)).astype(np.int32)
   codes_counts={str(x):int(np.count_nonzero(codes==x)) for x in (-3,0,1,2)}
  else:
   source_sig=np.empty(0,np.int32);fillids=np.empty(0,np.int32)
   codes=np.empty((0,2),np.int8);exits=np.empty((0,2),np.int32);net=np.empty((0,2),np.int32)
   addf=np.empty(0,np.int32);adde=np.empty(0,np.int32);adds=np.empty(0,np.int8);addsig=np.empty(0,np.int32);addnet=np.empty(0,np.int32);delta=np.zeros(len(qref),np.int32)
   codes_counts={'-3':0,'0':0,'1':0,'2':0};accepted_signals=np.empty(0,np.int32)
  nq=baseline_q+delta;nh=nq.reshape(-1,4).sum(axis=1)
  oqa=int(np.count_nonzero((qref>0)&(baseline_q>=qref)));nqa=int(np.count_nonzero((qref>0)&(nq>=qref)))
  oha=int(np.count_nonzero((href>0)&(orig_h>=href)));nha=int(np.count_nonzero((href>0)&(nh>=href)))
  res={'source':source,'month':mon,'scenario':name,'source_cap_raw_0p001':source_cap,'fill_cap_raw_0p001':fill_cap,
   'lag_ms':lag,'extra_slip_per_leg_raw_0p001':slip,'first_touch_horizon_ms':horizon,'sample_stride_ms':stride,
   'base_R19S3_missing_active_quarters':len(miss),'raw_quotes_in_failed_quarters':counts['raw_quotes'],
   'observed_sampled_candidates':counts['sampled'],'after_300s_fresh':counts['fresh'],'after_source_spread_cap':len(cand),
   'valid_first_delayed_fill_signals_before_dedup':len(accepted_signals),'unique_executable_fill_quote_ordinals':len(fillids),
   'independent_buy_and_sell_future_good_actions':codes_counts['1'],'independent_stop_actions':codes_counts['0'],
   'independent_source_censored_actions':codes_counts['-3'],'independent_timeout_actions':codes_counts['2'],
   'additional_packed_future_winning_positions':len(addf),'baseline_R19S3_15m_met':oqa,'new_R20_15m_met':nqa,
   'original_R9_active_15m_quarters':int(np.count_nonzero(qref)),'baseline_R19S3_hours_met':oha,'new_R20_hours_met':nha,
   'original_R9_active_hours':int(np.count_nonzero(href)),'nominal_added_quoted_price_net_raw':int(addnet.astype(np.int64).sum()),
   'future_aware_selected_hindsight_ONLY':True,'full_bidask_cross_and_fee':True,'not_a_causal_entry_predictor':True,
   'not_original_15s_favorable_30s_safe':True,'not_live_broker_or_verified_cash_PNL':True}
  allresults.append(res)
  for q,r in enumerate(refs['rows']):
   allquarter.append({'source':source,'month':mon,'scenario':name,'UTC_quarter':r['utc_quarter'],'R9_SYNTH_ref':int(qref[q]),
    'R19S3_existing_future_winners':int(baseline_q[q]),'R20_added_future_winners':int(delta[q]),
    'R20_total_future_winners':int(nq[q]),'R20_active_quarter_target_met':int(nq[q]>=qref[q]) if qref[q]>0 else '',
    'still_missing_slots':max(0,int(qref[q]-nq[q]))})
  for h in range(len(href)):
   allhour.append({'source':source,'month':mon,'scenario':name,'UTC_hour':refs['rows'][4*h]['utc_hour'],
    'R9_SYNTH_hour_ref':int(href[h]),'R19S3_existing_future_winners':int(orig_h[h]),
    'R20_added_future_winners':int(nh[h]-orig_h[h]),'R20_total_future_winners':int(nh[h]),
    'R20_active_hour_target_met':int(nh[h]>=href[h]) if href[h]>0 else '',
    'still_missing_hour_slots':max(0,int(href[h]-nh[h]))})
  bins[name]={'asof_signal_quote_ordinal':source_sig.astype(np.int32),
    'first_observed_fill_ordinal':fillids.astype(np.int32),'future_buy_sell_codes':codes.astype(np.int8),
    'first_passage_exit_ordinal':exits.astype(np.int32),'first_passage_nominal_net_raw':net.astype(np.int32),
    'added_source_signal_ordinal':addsig,'added_future_selected_side':adds,'added_fill_quote_ordinal':addf,
    'added_firstTP_exit_quote_ordinal':adde,'added_nominal_net_raw':addnet}
  print(source,mon,name,'new',len(addf),'Q',oqa,'->',nqa,'H',oha,'->',nha,'raw',counts['raw_quotes'],'codes',codes_counts,flush=True)
 out=HERE/'results';out.mkdir(parents=True,exist_ok=True)
 result=out/f'{prefix}_ALL_SOURCE_SCENARIOS.csv';quarts=out/f'{prefix}_ALL_UTC_15MIN_SCENARIOS.csv';hours=out/f'{prefix}_ALL_UTC_HOURS_SCENARIOS.csv';npz=out/f'{prefix}_ALL_SOURCE_CANDIDATE_DUAL_ACTION_AND_ADDED_WINNER_ORDINALS.npz'
 write_csv(result,allresults);write_csv(quarts,allquarter);write_csv(hours,allhour)
 arrays={k+'__'+field:val for k,d in bins.items() for field,val in d.items()}
 np.savez_compressed(npz,**arrays)
 rec={'source':source,'mon':mon,'original_r18_sha':r18.PINS[source][mon],'calendar_sha':refs['sha256'],
   'source_halo_provenance':provenance,'scenario_count':len(allresults),'source_records':len(t),
   'all_15min_rows':len(allquarter),'all_hour_rows':len(allhour),
   'scenarios':allresults,'files':{x.name:{'sha256':sha(x),'bytes':x.stat().st_size} for x in (result,quarts,hours,npz)},
   'all_original_winner_intervals_immutable':True,'no_quota_degrading_or_overlap':True,'NO_CASUAL_VALIDATION':True}
 receipt=out/f'{prefix}_EXACT_SOURCE_AND_OUTPUT_SHA_RECEIPT.json';receipt.write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'complete':source+mon,'seconds':round(time.monotonic()-started,3),'result':str(result),'receipt':str(receipt)}),flush=True)
 return rec

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=('DUKASCOPY_RAW','MT5_BROKER_EXPORT'),required=True)
 p.add_argument('--month',choices=('01','02','06','07'),required=True)
 p.add_argument('--scenario',action='append',default=None)
 a=p.parse_args();run(a.source,a.month,a.scenario)
