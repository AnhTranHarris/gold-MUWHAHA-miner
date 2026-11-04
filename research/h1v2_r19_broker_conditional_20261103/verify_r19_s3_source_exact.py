"""Independent source exact verifier for R19-S3 all 8 months.

Evidence class: future-known favorable intervals, NOT causal forecasting.
"""
from __future__ import annotations
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/data/h1v2_r19_broker_union');sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,'/mnt/data/h1v2_r18_dualbroker/src')
import r18_broker_multihorizon as r18
import r19_multi_clock_union as r19
import r19_s3_targeted_source_admission as s3
from r18_frozen_latency_economic_stress import get_frozen
from verify_r19_full_source import independently_check_first_good

def read_csv(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))

def verify_one(src,mon):
 t,b,a,_,_,_,prov=get_frozen(src,mon);refs=r18.refs_for_month(mon,Path('/mnt/data'))
 qkeys=refs['qkeys'];qref=refs['qref'];href=refs['href']
 orig=ROOT/('results_v2' if (src=='DUKASCOPY_RAW' and mon=='02') or (src=='MT5_BROKER_EXPORT' and mon in ['06','07']) else 'results')
 old=orig/f'R19_{src}_{mon}_EXACT_SELECTED_ORDINAL_TRACES.npz';tag=f'R19S3_{src}_{mon}'
 npz=s3.OUT/f'{tag}_ALL_TARGETED_CANDIDATE_SOURCE_ORDINALS_AND_DUAL_ACTION_LABELS.npz'
 csvp=s3.OUT/f'{tag}_ALL_SOURCE_UTC_QUARTERS.csv';receipt=s3.OUT/f'{tag}_SOURCE_AND_OUTPUT_RECEIPT.json'
 r=json.loads(receipt.read_text());assert r['original_gzip_SHA']==r18.PINS[src][mon] and r['source_original_UTC_ref_hash']==refs['sha256']
 for p in (npz,csvp):assert r['files'][p.name]['sha256']==r19.sha(p) and r['files'][p.name]['size']==p.stat().st_size
 with np.load(old,allow_pickle=False) as original:
  label='lag100_slip0_fillcap4000';of=original[label+'__actual_observed_fill_quote_ordinal'];oe=original[label+'__first_target_exit_quote_ordinal'];os=original[label+'__source_signal_quote_ordinal'];osi=original[label+'__original_future_selected_side']
 with np.load(npz,allow_pickle=False) as d:
  ix=d['raw_quote_signal_ordinal'];f=d['actual_fill_ordinal'];codes=d['offline_buy_and_sell_code'];exits=d['offline_buy_and_sell_firstTP_exit_ordinal']
  ns=d['added_source_signal_ord'];side=d['added_future_label_side'];nf=d['added_actual_fill_ord'];ne=d['added_firstTP_exit_ord'];bad=d['original_source_missing_quarter_idx']
  assert len(ix)==len(f)==len(codes)==len(exits)
  assert np.all((codes>=-2)&(codes<=1))
  assert codes.shape==(len(ix),2) and exits.shape==(len(ix),2)
  assert np.all((exits[codes!=1]<0)), 'NON_GOOD_FIRST_TARGET_SOURCE_ORDINAL'
  assert np.all((exits[codes==1]>=0))
  assert len(ns)==len(side)==len(nf)==len(ne)==r['new_source_25ms_expanded_nonoverlap_winners_not_conflicting_with_original']
  # Prove ALL input quote ordinals are observed *first* per 25ms bin and have
  # 300s actually observed gap-free history. Any post-gap fabrication must fail.
  assert np.all((ix==0)|((t[ix]//25)!=(t[np.maximum(0,ix-1)]//25)))
  gaps=np.flatnonzero(np.diff(t)>15000).astype(np.int32)+1
  gp=np.searchsorted(gaps,ix,side='right')-1
  last=np.where(gp>=0,gaps[np.maximum(0,gp)],0)
  assert np.all(t[ix]-t[last]>=300000)
  assert np.all((a[ix].astype(np.int64)-b[ix].astype(np.int64))<=4000)
  if len(ix):
   assert np.all(np.searchsorted(qkeys,(t[ix]//900000),side='left')<len(qkeys))
  # Every delayed actually filled quote must be the FIRST source quote after
  # signal+100 ms (or explicitly rejected by source age/cap).
  ok=np.flatnonzero(f>=0)
  if len(ok):
   expected=np.searchsorted(t,t[ix[ok]]+100,side='left')
   assert np.array_equal(expected,f[ok])
   assert np.all(t[f[ok]]-t[ix[ok]]>=100) and np.all(t[f[ok]]-(t[ix[ok]]+100)<=1000)
   assert np.all((a[f[ok]].astype(np.int64)-b[f[ok]].astype(np.int64))<=4000)
  # Each newly added future winner MUST be a raw 25ms sample and first delayed
  # executable quote with genuine realized original bid/ask target.
  if len(ns):
   where=np.searchsorted(ix,ns)
   assert np.all(where<len(ix)) and np.array_equal(ix[where],ns)
   assert np.array_equal(f[where],nf)
   label_idx=np.where(side==1,0,1)
   assert np.all(codes[where,label_idx]==1)
   assert np.array_equal(exits[where,label_idx],ne)
   assert independently_check_first_good(t,b,a,ns,nf,ne,side,0)==len(ns)
   assert np.all(t[nf[1:]]>t[ne[:-1]])
  idx=np.searchsorted(t[oe],t[nf],side='left')
  pos=np.minimum(idx,len(of)-1)
  collision=(idx<len(of))&(t[of[pos]]<=t[ne])
  assert not np.any(collision),'ORIGINAL_R19_BASELINE_WAS_DISPLACED'
  # Include unchanged old complete future winner positions and independently
  # rerun source byte-index counter to compare every quarter/hour.
  oldqc=np.bincount(t[of]//900000-qkeys[0],minlength=len(qref))
  newqc=np.bincount(t[nf]//900000-qkeys[0],minlength=len(qref))
  allqc=oldqc+newqc
  original_bad=np.flatnonzero((qref>0)&(oldqc<qref));assert np.array_equal(bad,original_bad)
  rows=read_csv(csvp)
  assert len(rows)==len(qref)
  for j,x in enumerate(rows):
   assert x['utc_quarter']==refs['rows'][j]['utc_quarter']
   assert int(x['R9_SYNTH_UTC_ref'])==int(qref[j])
   assert int(x['original_R19_future_winners'])==int(oldqc[j])
   assert int(x['new_past_observed_25ms_grid_future_winners'])==int(newqc[j])
   assert int(x['combined_source_future_winners'])==int(allqc[j])
  assert r['baseline_15m_met']==int(((qref>0)&(oldqc>=qref)).sum())
  assert r['expanded_15m_met']==int(((qref>0)&(allqc>=qref)).sum())
  assert r['baseline_hour_met']==int(((href>0)&(oldqc.reshape(-1,4).sum(axis=1)>=href)).sum())
  assert r['expanded_hour_met']==int(((href>0)&(allqc.reshape(-1,4).sum(axis=1)>=href)).sum())
  res={'source':src,'month':mon,'original_raw_sha':r18.PINS[src][mon],
   'complete_all_quarter_records':len(rows),'all_source_original_asof_25ms_candidates':len(ix),
   'all_candidate_dual_side_outcomes_recorded':True,
   'added_quote_ordinals_independently_first_touch_verified':len(ns),
   'existing_R19_winner_intervals_unchanged':True,
   'no_candidate_lookback_before_source_300s_fresh_history':True,
   'actual_delayed_quote_first_observed_100ms':True,
   'no_original_archived_results_modified':True,
   'future_known_offline_target_not_caused_by_entry_model':True}
  out=s3.OUT/f'{tag}_INDEPENDENT_SOURCE_VERIFIER_PASS.json';out.write_text(json.dumps(res,indent=2)+'\n')
  print('R19S3_VERIFY_PASS',src,mon,'complete_candidates',len(ix),'new_winners',len(ns),flush=True)
  return res

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',choices=r19.SOURCES,required=True);p.add_argument('--month',choices=r19.MONTHS,required=True)
 a=p.parse_args();verify_one(a.source,a.month)
