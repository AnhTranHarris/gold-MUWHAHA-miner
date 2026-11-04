"""R19-S3 new SOURCE-CANDIDATE HINDSIGHT expansion in only failing R19 15m cells.

As-of: first *observed* quote per 25ms bin (new clock), spread<=4 at
original signal, 300s continuous warmup after >15s gap. Actual first
observed >=100ms later with <=1s quote age and <=4 spread. OFFLINE both
BUY and SELL are independently evaluated via future +0.10 executable net
first touch before -0.10 opening-liquidation adverse, within 60s.

NEW successful intervals are retained ONLY if they do not overlap any
preexisting verified R19-S1 selected winning positions; thus no old quota is
sacrificed. New intervals packed earliest-finish among themselves.
HINDSIGHT ONLY; no causal predictive entry, original S1 or actual broker cash.
"""
from __future__ import annotations
import argparse,csv,json,sys,hashlib
from pathlib import Path
import numpy as np
from numba import njit
ROOT=Path('/mnt/data/h1v2_r19_broker_union');sys.path.insert(0,str(ROOT/'src'))
import r19_multi_clock_union as r19
import r18_broker_multihorizon as r18
from r18_frozen_latency_economic_stress import get_frozen
from r18_s2_latency_frontier import pack_future_good
OUT=ROOT/'results_s3_new_admission';OUT.mkdir(exist_ok=True)
FEE=20;TP=100;ADV=100;H=60000;GAP=15000;WARMUP=300000;CAP=4000;LATENCY=100;SLIP=0;BIN=25

@njit(cache=False)
def both_sides_after_observed_fill(t,b,a,signals,fills):
 """Outcome 1=first favorable before adverse, 0=stopped, -1=censored/time, -2=reject;
 earliest actual quote firstTP ordinal; independent two sides, full source.
 """
 n=len(signals); codes=np.full((n,2),-2,np.int8);exits=np.full((n,2),-1,np.int32)
 for k in range(n):
  f=int(fills[k])
  if f<0:continue
  # One new source signal may be future favorable on ONE side only.
  for z in range(2):
   buy=z==0;entry=int(a[f]) if buy else int(b[f]);openliq=int(b[f]) if buy else int(a[f]);prev=t[f]
   for j in range(f+1,len(t)):
    if t[j]==t[f]:continue
    if t[j]-prev>GAP:codes[k,z]=-1;break
    prev=t[j]
    if t[j]>t[f]+H:codes[k,z]=-1;break
    liq=int(b[j]) if buy else int(a[j])
    if (buy and liq<=openliq-ADV) or ((not buy) and liq>=openliq+ADV):codes[k,z]=0;break
    net=liq-entry-FEE if buy else entry-liq-FEE
    if net>=TP:codes[k,z]=1;exits[k,z]=j;break
    # no invented OHLC path; all quotes are original source chronology
 return codes,exits

def source_candidate_ordinals(t,b,a,qkeys,badquarters):
 # Compute actual UTC quote windows of ONLY previously missed original quarter refs.
 ids=[]
 for q in badquarters:
  lo=int(qkeys[q]*900000);hi=lo+900000
  i=np.searchsorted(t,lo,'left');j=np.searchsorted(t,hi,'left')
  if j>i:ids.append(np.arange(i,j,dtype=np.int32))
 if not ids:return np.empty(0,np.int32),{'before_filter':0,'after_25ms':0,'after_300s':0,'after_source_spread':0}
 ix=np.concatenate(ids)
 initial=len(ix)
 isfirst=(ix==0)|(t[ix]//BIN != t[np.maximum(ix-1,0)]//BIN)
 ix=ix[isfirst];postbin=len(ix)
 gaps=np.flatnonzero(np.diff(t)>GAP).astype(np.int32)+1
 pos=np.searchsorted(gaps,ix,side='right')-1
 gap_start=np.where(pos>=0,gaps[np.maximum(pos,0)],0)
 fresh=(t[ix]-t[gap_start]>=WARMUP)
 ix=ix[fresh];postfresh=len(ix)
 spread=(a[ix].astype(np.int64)-b[ix].astype(np.int64))
 ix=ix[(spread>=0)&(spread<=CAP)]
 return ix,{'before_filter':initial,'after_25ms':postbin,'after_300s':postfresh,'after_source_spread':len(ix)}

def run_one(source,mon):
 t,b,a,_,_,_,provenance=get_frozen(source,mon)
 refs=r18.refs_for_month(mon,Path('/mnt/data'));qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 src=ROOT/('results_v2' if (source=='DUKASCOPY_RAW' and mon=='02') or (source=='MT5_BROKER_EXPORT' and mon in ['06','07']) else 'results')
 base=f'R19_{source}_{mon}'
 original=src/f'{base}_EXACT_SELECTED_ORDINAL_TRACES.npz'
 label='lag100_slip0_fillcap4000'
 with np.load(original,allow_pickle=False) as z:
  sig=z[label+'__source_signal_quote_ordinal'].astype(np.int32)
  side=z[label+'__original_future_selected_side'].astype(np.int8)
  fill=z[label+'__actual_observed_fill_quote_ordinal'].astype(np.int32)
  exitidx=z[label+'__first_target_exit_quote_ordinal'].astype(np.int32)
  rawnet=z[label+'__future_selected_nominal_bidask_net_raw'].astype(np.int64)
 old_q=np.bincount(t[fill]//900000-qkeys[0],minlength=len(qref))
 missing=np.flatnonzero((qref>0)&(old_q<qref))
 ix,filters=source_candidate_ordinals(t,b,a,qkeys,missing)
 expected=t[ix]+LATENCY;f=np.searchsorted(t,expected,side='left').astype(np.int32)
 fc=np.minimum(f,len(t)-1)
 start=int(qkeys[0]*900000);end=int((qkeys[-1]+1)*900000)
 valid=(f<len(t))&(fc>ix)&(t[fc]>t[ix])&(t[fc]-expected<=1000)
 valid&=(t[fc]>=start)&(t[fc]<end)
 spread=(a[fc].astype(np.int64)-b[fc].astype(np.int64))
 valid&=(spread>=0)&(spread<=CAP)
 f=np.where(valid,fc,-1).astype(np.int32)
 codes,exits=both_sides_after_observed_fill(t,b,a,ix,f)
 accepted=(codes==1)
 cand_signal=np.repeat(ix,2)[accepted.ravel()]
 cand_side=np.tile(np.array([1,-1],np.int8),len(ix))[accepted.ravel()]
 cand_f=np.repeat(f,2)[accepted.ravel()]
 cand_ex=exits.ravel()[accepted.ravel()]
 # Conservatively never replace a frozen verified older winning source position.
 # Original occupied intervals are disjoint and sorted by actual fill quote time.
 sorted_old_ends=t[exitidx]
 if len(sorted_old_ends)>1 and np.any(np.diff(sorted_old_ends)<=0):raise ValueError('BASE_EXIT_ORDER')
 p=np.searchsorted(sorted_old_ends,t[cand_f],side='left')
 overlap=(p<len(sig))
 validpos=np.minimum(p,len(sig)-1)
 overlap&=(t[fill[validpos]]<=t[cand_ex])
 cand_signal=cand_signal[~overlap];cand_side=cand_side[~overlap];cand_f=cand_f[~overlap];cand_ex=cand_ex[~overlap]
 take=pack_future_good(t,cand_f,cand_ex,np.ones(len(cand_f),np.bool_))
 ns,sd,nf,ne=cand_signal[take],cand_side[take],cand_f[take],cand_ex[take]
 if len(ns)>1 and np.any(t[nf[1:]]<=t[ne[:-1]]):raise ValueError('ADDED_POSITION_CONFLICT')
 allf=np.sort(np.r_[t[fill],t[nf]])
 allend=np.concatenate((t[exitidx],t[ne]));alls=np.concatenate((t[fill],t[nf]))
 order=np.argsort(alls)
 if len(order)>1 and np.any(alls[order][1:]<=allend[order][:-1]):raise ValueError('OLD_NEW_ONE_POSITION_OVERLAP')
 delta=np.bincount(t[nf]//900000-qkeys[0],minlength=len(qref))
 new_q=old_q+delta
 old_h=old_q.reshape(-1,4).sum(axis=1);new_h=new_q.reshape(-1,4).sum(axis=1)
 if np.any(new_q<old_q):raise ValueError('QUARTER_REGRESSION')
 tag=f'R19S3_{source}_{mon}'
 rows=[{'source':source,'month':mon,'utc_quarter':refs['rows'][q]['utc_quarter'],
   'R9_SYNTH_UTC_ref':int(qref[q]),'original_R19_future_winners':int(old_q[q]),
   'new_past_observed_25ms_grid_future_winners':int(delta[q]),'combined_source_future_winners':int(new_q[q]),
   'original_quarter_met':int(old_q[q]>=qref[q]) if qref[q] else '',
   'new_quarter_met':int(new_q[q]>=qref[q]) if qref[q] else '',
   'future_selected_oracle_ONLY':True,'not_predictive':True} for q in range(len(qref))]
 outcsv=OUT/f'{tag}_ALL_SOURCE_UTC_QUARTERS.csv'
 with open(outcsv,'w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 # Complete candidate labels and all selected source quote ordinals saved; do not truncate.
 archive=OUT/f'{tag}_ALL_TARGETED_CANDIDATE_SOURCE_ORDINALS_AND_DUAL_ACTION_LABELS.npz'
 np.savez_compressed(archive,raw_quote_signal_ordinal=ix,actual_fill_ordinal=f,offline_buy_and_sell_code=codes,
   offline_buy_and_sell_firstTP_exit_ordinal=exits,
   added_source_signal_ord=ns,added_future_label_side=sd,added_actual_fill_ord=nf,added_firstTP_exit_ord=ne,
   original_source_missing_quarter_idx=missing)
 result={'source':source,'month':mon,'original_gzip_SHA':r18.PINS[source][mon],
  'source_original_UTC_ref_hash':refs['sha256'],'original_source_missing_quarters':len(missing),
  'pre_admission_counts':filters,'new_100ms_quote_eligible_oracle_actions':len(cand_signal),
  'new_source_25ms_expanded_nonoverlap_winners_not_conflicting_with_original':len(nf),
  'baseline_15m_met':int(((qref>0)&(old_q>=qref)).sum()),
  'expanded_15m_met':int(((qref>0)&(new_q>=qref)).sum()),
  'baseline_hour_met':int(((href>0)&(old_h>=href)).sum()),
  'expanded_hour_met':int(((href>0)&(new_h>=href)).sum()),
  'all_active_quarters':int(np.count_nonzero(qref)),
  'all_active_hours':int(np.count_nonzero(href)),
  'no_prior_source_changed':True,'no_baseline_trade_removed_or_rescheduled':True,
  'still_future_informed_entry_side':True,'source_economic_PNL_not_approved':True}
 result['files']={p.name:{'size':p.stat().st_size,'sha256':r19.sha(p)} for p in (outcsv,archive)}
 receipt=OUT/f'{tag}_SOURCE_AND_OUTPUT_RECEIPT.json';receipt.write_text(json.dumps(result,indent=2)+'\n')
 print('R19S3',source,mon,'new',len(nf),'Q',result['baseline_15m_met'],'->',result['expanded_15m_met'],'H',result['baseline_hour_met'],'->',result['expanded_hour_met'],flush=True)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=r19.SOURCES,required=True);p.add_argument('--month',choices=r19.MONTHS,required=True)
 a=p.parse_args();run_one(a.source,a.month)
